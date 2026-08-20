# Claude Phase 2-E Architecture

```yaml
document_id: claude_phase_2_e_architecture_20260815004739
status: frozen
phase: phase_2
subphase: phase_2_e
from_role: Claude Phase 2-E設計担当者役
to_role: Claude設計統括者役
role: phase_designer
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 00:47:39 JST
language: ja
source_requirements: claude_phase_2_e_requirements_20260815004739
```

## 1. 既存Codebaseとの関係（実証済み事実）

実Source Tree調査により次を確認済み（詳細File:Line根拠は調査Agent Reportに記録）。

- Component選択は`entrypoints/web/main.py`／`bootstrap/web_application.py`／`bootstrap/documentation_rag.py`の個別`if/elif`分岐であり、共通Registryは存在しない。`modules/configuration_control/application.py`の`_validated_feature_hooks`は`len(hooks) != 1`かつ`component_key != "documentation_rag"`をHard-codeしており、単一Component決め打ちである。
- 既存の再利用可能Stateパターン：`web/access_profiles.py`の`resolve_documentation_rag_state()`が`(capability, feature_profile, adapter_available) → DENIED／UNAVAILABLE／DISABLED／ENABLED`を計算する。
- 既存のTyped Descriptorパターン：`modules/configuration_control/contracts.py`の`FeatureHookDescriptor`／`RecordingHookDescriptor`（`component_key, allowed_modes, current_mode, available, apply_disposition`）。
- Citationは`modules/conversation/application/conversation_generation.py`のSSE `retrieval`／`completed`イベントにのみ存在し、`PersistedConversationMessage`・SQLite Schema（`store_metadata／conversations／commit_operations`の3 Table）のいずれにもCitation Fieldは存在しない。
- Conversation Domainは`modules/conversation/domain/**`でPhase 2-A以降Frozen。`project_generation_history()`が`head_turn_id`から`parent_turn_id`を辿り、Completed Turnのみを収集する。
- SQLite Adapter（`modules/conversation/adapters/sqlite_conversation_store.py`）はCanonical JSON＋SHA-512 Envelope、`commit_operations`経由のOperation-id Idempotency、`BEGIN IMMEDIATE`によるCAS Transactionを持つ。Migrationは`ConversationStorageMaintenancePort`（`inspect_schema／plan_migration／migrate／rollback`）経由。
- Configuration Controlの実行時State自体はProcess再起動で永続化されず、信頼済み起動InputからRebuildされる（`web/configuration_routes.py`／`modules/configuration_control/*`）。

## 2. 設計方針（ADRで詳細化する主要判断の要約）

1. Switchboardは**既存Gateの置き換えではなく観測・記述層**として追加する。Security-criticalな既存Local／Loopback／認証チェックは変更しない。
2. Citation Evidenceは**Conversation永続化と同一DB・同一Transaction**に格納し、既存のCAS／Idempotency／Crash Recovery機構をそのまま再利用する（新しいTransaction機構・新しいRecovery経路を作らない）。
3. 新規Contract型は既存Enum（`ApplyDisposition`等）を再利用し、意味の重複する型を増やさない。
4. Component Keyは閉じたEnumにせず、既存の`_OpaqueIdentifier`パターンに準じたValidated Opaque Stringとする（Hard-code回避）。

## 3. Module A: Runtime Composition Switchboard Foundation

### 3.1 新規Module

```text
src/margpa_runtime_llm/modules/runtime_composition/
├─ __init__.py
├─ contracts.py
├─ ports.py
├─ application.py
└─ public.py
```

### 3.2 contracts.py

- `ComponentKey`: `_OpaqueIdentifier`類似のValidated str型（Pattern `^[a-z][a-z0-9_]{0,63}$`）。
- `ComponentState` Enum: `ENABLED, DISABLED, UNAVAILABLE, DENIED`。
- `ComponentSideEffectLevel` Enum: `NONE, READ_ONLY, LOCAL_WRITE, EXTERNAL`。
- `ComponentDescriptor`（Frozen Pydantic Model）:
  ```text
  component_key: ComponentKey
  kind: str                      # 例: "feature" / "persistence" / "control-surface"
  version: str
  state: ComponentState
  capabilities: tuple[str, ...]
  required_dependencies: tuple[ComponentKey, ...]
  optional_dependencies: tuple[ComponentKey, ...]
  conflicts_with: tuple[ComponentKey, ...]
  degraded_reasons: tuple[str, ...]
  side_effect_level: ComponentSideEffectLevel
  apply_disposition: ApplyDisposition        # modules.configuration_control.contracts を再利用
  restart_required: bool
  effective_source: ConfigurationSource      # modules.configuration_control.contracts を再利用
  revision: int
  canonical_digest: str                      # sha512 hex、既存 configuration_digest() と同じ正規化手順
  governance_seam_mode: Literal["off"]       # Phase 2-E では "off" 固定、他値は構築不能
  ```
  Model Validatorで次を強制する：`state in (UNAVAILABLE, DENIED)` の場合 `capabilities` は空、`degraded_reasons` は非空必須。`state == ENABLED` かつ `required_dependencies` に未解決Keyがある組み合わせは構築不能。
- `ComponentRegistrationError`（重複Key、Conflict宣言同士の同時ENABLE等、登録時Fail-closed）。

### 3.3 ports.py

```text
class ComponentRegistryPort(Protocol):
    def register(self, descriptor: ComponentDescriptor) -> None: ...
    def resolve(self, component_key: ComponentKey) -> ComponentDescriptor | None: ...
    def list_components(self) -> tuple[ComponentDescriptor, ...]: ...
```

### 3.4 application.py

`ComponentRegistryService`：Process内Memory Dict実装（Non-persistent、Process起動ごとに再構築——Configuration Controlの既存方針と同じ）。`register()`はDuplicate KeyまたはConflict宣言済みComponent同士が同時に`ENABLED`で登録されようとした場合、`ComponentRegistrationError`を送出しFail-closedとする（黙って上書き・無視しない）。

### 3.5 Wiring（既存コードへの最小侵襲）

`bootstrap/web_application.py`の`build_phase1_web_runtime()`内、既存3 Component（Documentation RAG／Conversation Persistence／Configuration Control）が実際に構築・State解決された**直後**に、その解決済みStateをそのまま`ComponentDescriptor`へ写像してRegistryへ登録する。既存の`if/elif`分岐・既存Gate判定ロジック自体は一切変更しない（Additiveな観測登録のみ）。

### 3.6 新規Endpoint

`src/margpa_runtime_llm/web/runtime_composition_routes.py`：
```text
GET /api/v2/runtime/components
```
既存`configuration_routes.py`と同型のGate（Local／Loopback／未認証必須／明示CLI Opt-in `--runtime-composition-inspection`）。未Bind時は`configuration_control_unavailable`と同型の`404 runtime_composition_unavailable`を返し、Path／Source情報を漏らさない。Public／Basic Previewでは常に未Bind。

## 4. Module B: Documentation RAG Multi-turn Follow-up

既存`modules/documentation_rag/application/documentation_rag.py`の`augment_with_context()`、および`modules/conversation/domain/models.py`の`project_generation_history()`は要件を満たす形で既に実装されている（調査Agentにより確認済み）。本Phaseでの追加作業は次の2点のみ。

1. **統合Test**：Multi-turn（3ターン以上）＋Branch分岐＋Retry／Regenerateを組み合わせた条件下で、各TurnのCitationが他Turnと混線しないこと、Context AssemblyがSelected BranchのCompleted Turnのみを使うことをEnd-to-Endで証明する（既存実装への変更なし、Test新設のみ）。
2. **Persistence連携Hook**：`augment_with_context()`の戻り値（`DocumentationAugmentation`）を、Turn Commit時にModule C（Persistent Citation Evidence）へ引き渡す新しい呼び出し経路を`modules/conversation/application/conversation_generation.py`（または`persistent_conversation_service.py`のTurn完了経路）に追加する。RAGロジック自体は変更しない。

## 5. Module C: Persistent Citation Evidence

### 5.1 Contract拡張（`modules/documentation_rag/contracts.py`）

**実装調査による設計補正**：既存`contracts.py`には既にAllowlist型`DocumentationCitation`（`citation_id, project_relative_path, heading_breadcrumb, chunk_id, document_sha512, retrieval_score, selected_order, truncated`、`project_relative_path`はField Validator `_validate_project_relative_path`で絶対Path・Path Traversalを拒否済み）が存在する。これはFrontend `renderCitations()`（`web/static/app.js:600`）およびSSE `retrieval`イベント（`web/persistent_streaming.py:79-80`）が既に消費している`project_relative_path`／`heading_breadcrumb`と同じField名である。新規に類似Fieldを再発明せず、この既存型をそのまま再利用する。

```text
class PersistedTurnCitationEvidence(FrozenModel):
    conversation_id: str
    turn_id: str
    schema_version: int
    corpus_revision: str                      # corpus_manifest_digest を転記
    retrieval_state: DocumentationRetrievalState
    grounding_state: DocumentationGroundingState
    warning_codes: tuple[str, ...]
    citations: tuple[DocumentationCitation, ...]   # 既存型を再利用（新規Field追加なし）

class CitationUnavailable(FrozenModel):
    turn_id: str
    reason: Literal["unsupported_schema_version", "corrupt_record", "not_present"]
```

`conversation_scope_id`は独立Fieldとして持たず、永続化Layer（SQLite Adapter）側でScope Keyから解決する（既存`StoredConversation`が同様にScope非保持であることと整合）。`DocumentationCitation`はAllowlist Fieldのみで構成され、自由記述の生Content Fieldを持たない。これにより、Absolute Path／Secret／Raw Thinking／System Prompt／Tool内部情報／Hidden Original／未確定Partial Output／Raw Exception／無制限Raw Chunkは型として構築不能とする（Field自体が存在しない）。`project_relative_path`は既存Validatorにより絶対Path・Path Traversalを拒否済み。

### 5.2 Port拡張（`modules/documentation_rag/ports.py`）

```text
class CitationEvidenceStorePort(Protocol):
    def get_turn_citations(
        self, scope_id: str, conversation_id: str, turn_id: str,
    ) -> PersistedTurnCitationEvidence | CitationUnavailable: ...

    def get_conversation_citations(
        self, scope_id: str, conversation_id: str,
    ) -> Mapping[str, PersistedTurnCitationEvidence | CitationUnavailable]: ...
```

書き込みは独立Portを新設せず、Module 5.3のとおり`ConversationRepositoryPort.commit()`のCommit対象へCitation Recordsを含める形で拡張する（Atomicity確保のため、別Portでの独立書込にしない）。

### 5.3 永続化（`modules/conversation/ports/conversation_store.py` ／ `modules/conversation/adapters/sqlite_conversation_store.py`）

`CommitConversation`（Port側）へOptional Field `citation_records: tuple[PersistableCitationRecord, ...] | None`を追加する（`None`＝この Commit ではCitation書込を伴わない＝既存Commit呼び出しは無変更で動作）。

SQLite Adapter側：新規Table
```sql
CREATE TABLE turn_citations (
    conversation_id TEXT NOT NULL,
    turn_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    citations_json TEXT NOT NULL,
    citations_sha512 TEXT NOT NULL,
    operation_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (conversation_id, turn_id)
);
```
既存`commit()`メソッドの同一`BEGIN IMMEDIATE`Transaction内で、Turn Commit（`conversations`Table更新）と同時に`turn_citations`へInsertする。`citations_json`は既存Snapshotと同じ正規化（UTF-8、Sorted Keys、Compact Separator、`allow_nan=false`）＋SHA-512。`operation_id`により既存の再送Idempotency（同一Operation Idは同一結果を返す）に自然に乗る。RAG OFF／Citation 0件の場合は行を作らない（FR-3.9）。

### 5.4 Migration

`ConversationStorageMaintenancePort`の既存Migration機構でStorage Schema Versionを`sqlite-1 → sqlite-2`へ進める。Migrationは`CREATE TABLE IF NOT EXISTS turn_citations (...)`のみ（既存データの変換不要、Additive-onlyのため低Risk）。既存のCheckpoint（`0600`権限＋Digest／件数記録）→Staging変換→再検証→`fsync`＋`os.replace`Cutoverの手順をそのまま適用する。Rollbackも既存Port経由。

### 5.5 Fail-closed読み取り

`get_turn_citations()`実装：
- 行が存在しない → `CitationUnavailable(reason="not_present")`（＝Citationなし、RAG OFF等の正常状態）。
- `schema_version`が実装の認識するVersionより新しい → `CitationUnavailable(reason="unsupported_schema_version")`。
- JSON Parse失敗またはSHA-512不一致 → `CitationUnavailable(reason="corrupt_record")`（例外を上位へ伝播させない）。
- 正常時 → `PersistedTurnCitationEvidence`。

いずれの`CitationUnavailable`も、Conversation本体（Message本文）の取得・表示を妨げない。

### 5.6 Commit経路への統合

`modules/conversation/application/persistent_conversation_service.py`のTurn完了経路（`complete_generation`相当）で、Module Bが引き渡した`DocumentationAugmentation`から`PersistableCitationRecord`Tupleを構築し（`retrieval_state == ENABLED`かつCitation非空の場合のみ）、`CommitConversation.citation_records`へ設定して既存のCommit呼び出しに渡す。

### 5.7 API拡張（`web/persistent_routes.py`）

`GET /api/v2/conversations/{conversation_id}`（Detail）のResponseへ、既存Message／Turn Projectionと並べてTurnごとの`citations`Fieldを追加する。値は次のいずれか：Safe Citation Projection一覧（既存のLive SSE `retrieval`イベントで使っているものと同じProjection型を再利用）／`null`（Citationなし）／Unavailable Marker（`{"unavailable": true, "reason": ...}`）。既存Responseへの**追加**Fieldであり、既存Fieldの削除・型変更は行わない（NFR-3準拠）。

### 5.8 Retry／Regenerate／Branch Selectとの整合

- Retry／Regenerate：新しいDerived Turnが独自の`turn_id`で完了時にCitationを書き込む。Source Turnの`turn_citations`行は一切触れない（FR-3.11）。
- Branch Select：`head_turn_id`Pointerの変更のみ。Citation取得はTurn単位（`get_conversation_citations`が現在のBranchのCompleted Turn集合に対してKeyで引くだけ）のため、Branch Select自体はCitation Tableに触れない（FR-3.12）。

### 5.9 Crash Recovery

Citation書込がTurn CommitとSame Transactionのため、既存`recover_incomplete_conversations()`のCAS再確認ロジックがそのままCitation込みの原子性を保証する。新しいRecovery経路の追加は不要。

## 6. Frontend（Browser）反映

**実装調査により確定**：`src/margpa_runtime_llm/web/static/app.js`に既に次の配線が存在する。

- `state.persistentCitationEvidence`（`app.js:329`）：`turn_id → {citations, warnings}`のClient-side Map。
- `handlePersistentEvent()`（`app.js:1533-1547`）：SSE `retrieval`イベント受信時のみ、このMapへ`state.activePersistentTurnId`をKeyとして書き込む（＝Page Memory限定、既存の既知の境界）。
- `renderCitations(assistantView, data)`（`app.js:600-628`）：`data.citations`配列を描画。各要素は`project_relative_path`／`heading_breadcrumb`を参照（§5.1で確認した`DocumentationCitation`と同じField名）。
- `loadPersistentDetail()`（`app.js:1301-1315`）：`GET /api/v2/conversations/{id}`をFetchし`state.persistentDetail`へ格納、`renderPersistentDetail()`を呼ぶ。
- `renderPersistentDetail()`（`app.js:1317-1369`）：Turnごとに`state.persistentCitationEvidence.get(turn.turn_id)`を参照して`renderCitations()`を呼ぶ（`app.js:1335-1338`）——**Detail Fetchからこの値を埋める経路が現在存在しない**ため、Reload／Resume／再Open時は常に`undefined`となりCitationが表示されない。これが本Phaseで埋めるべき唯一のGapである。

**変更内容**：`loadPersistentDetail()`内、`state.persistentDetail = await response.json();`の直後に、Response JSONの新設`turns[].citations`Field（§5.7）を読み取り、`state.persistentCitationEvidence`へ`turn_id`をKeyとして書き込む処理を追加する（`{citations: [...], warnings: [...]}`の既存Shapeへ正規化）。`renderCitations()`・`renderPersistentDetail()`・SSE経路（`handlePersistentEvent()`）は無変更で動作する——Data Sourceを1つ追加するだけであり、既存の描画Contractを変えない。

## 7. Public/Basic Preview非Binding（設計による自動満足）

Citation Store・Runtime Composition Endpointは、いずれも既存のLocal専用構築経路（`LocalConversationPersistenceSettings`、`--configuration-control`同型のOpt-inフラグ）の内側にのみ配線される。Public／Basic Previewの起動経路はこれらのSettingsを構築しないため、Persistent Build／Read／Write／Route Call 0はコード構造上自動的に満たされる（個別の追加ガード実装ではなく、配線Scopeの限定による）。

## 8. Status

```text
Current Point            : Architecture Frozen
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（設計段階）
Open Current Blocker      : NONE
Controller-owned Next Work: ADR／Mutation Manifest／Acceptance Matrix／Implementer Handoff作成
Deferred Evidence         : Frontend Exact File Pathは実装時Grepで確定（§6）
Exact Next Route          : ADR作成へ進む
```
