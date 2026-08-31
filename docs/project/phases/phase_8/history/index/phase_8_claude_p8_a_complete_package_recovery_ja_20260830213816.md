# Phase 8 Claude P8-A Manual URL Fetch/Evidence — Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-A
state: complete
provider: Claude
created_at: 2026-08-30 21:38 JST
supersedes: phase_8_claude_p8_a_manual_url_fetch_evidence_package_recovery_ja_20260830203026
```

## 結論

```yaml
p8_a_established: true
mvp_blocker_open: 0
critical_open: 0
major_open: 0
```

前Recovery（20260830203026）で未着手として記録したP8-A-WU-004（Main Model Evidence注入）とP8-A-WU-005（Persistence）を実装した。これによりP8-A-WU-001〜006が全てCompleteとなり、P8-Aが成立した。

## Work Unit別Status（最終）

| Work Unit | Status |
|---|---|
| P8-A-WU-001〜003 | COMPLETE（前Recovery記載どおり、無変更） |
| P8-A-WU-004 | **COMPLETE**（本Package内で新規実装） |
| P8-A-WU-005 | **COMPLETE**（本Package内で新規実装） |
| P8-A-WU-006 | **COMPLETE**（Standalone Panel＋Chat Compose添付導線の両方完成） |

## WU-004: Main Model Evidence注入（実装概要）

`conversation_generation.py`を直接読み込み、Documentation RAGの既存Injection機構（`_inject_documentation_reference()`、Guardrail Context Source Check、Live SSE、Terminal Event）と構造的に並行する新規Pipelineを追加した。

- `ConversationSettings.manual_web_evidence_url`（一Turn限定のOptional Field、既定None）。
- `ConversationGenerationService`／`ConversationGenerationSession`へ`web_knowledge_service`／`web_search_governance_mode`を追加。`.start()`でRAGと同型のFail-closed Availability Checkを実装。
- `events()`へDocumentation Retrieval Phaseと並行するWeb Evidence Fetch Phaseを追加（`fetch_direct_url()`呼び出し、Cancellation確認、Guardrail Context Source Check再利用）。
- `_inject_web_evidence()`：`WEB_EVIDENCE_UNTRUSTED_INSTRUCTION`（Documentation RAGの Authority文言とは別の、Untrusted性を明示する専用Instruction）とともに`TOOL` Roleで Splice。Documentation RAGと同一Turnで共存可能（Session未確定時点のClosureが`self`経由で遅延評価される設計、両者が独立に注入される）。
- Guardrail再利用：`_guardrail_web_evidence_source_check()`が既存`self._guardrail_context_source_hook`をWeb Evidence用に再利用（新規Guardrail概念を作らない）。
- 新規`ConversationEventType.WEB_EVIDENCE`SSE Event。**Persistent SSE Bridge（`persistent_streaming.py`）のEvent Type別Dispatchが未知TypeでRuntimeErrorを投げる構造だったため、対応Branchを追加**（見落とせばPersistent Chatが即座に500になる差分だった）。
- `_completed_event()`へ`data["web_evidence"]`を追加（Documentationの`documentation_retrieval`と対称）。

## WU-005: Persistence（実装概要）

`documentation_rag`の`turn_citations`永続化Pipelineと完全に並行する新規Pipelineを追加した。

- `web_knowledge/contracts.py`：`WEB_CITATION_EVIDENCE_SCHEMA_VERSION`（Documentation側と独立）、`PersistedTurnWebCitationEvidence`、`WebCitationUnavailable`、`build_turn_web_citation_evidence()`。
- `web_knowledge/ports.py`：`WebCitationEvidenceStorePort`（`@runtime_checkable`）。
- `CommitConversation.web_citation_evidence`（`citation_evidence`と独立、同一Turnへ両方・片方・どちらも無し全て許容）。
- `sqlite_conversation_store.py`：新規`turn_web_citations` Table（`turn_citations`と同型のColumn構成）、`STORAGE_SCHEMA_VERSION`を`sqlite-3`→`sqlite-4`へBump、encode/decode/get系Method一式。
- `sqlite_migration.py`：**既存`CONVERSATION_TITLE_MIGRATION_STEP`が生Import`STORAGE_SCHEMA_VERSION`を`target_version`に使っており、Bump後に意味が変わってしまう不整合を検出・修正**（新規`LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_3`定数を導入し、旧Stepを固定Pinさせた上で新規`TURN_WEB_CITATIONS_MIGRATION_STEP`を追加）。`persistence_factory.py`のMigration Step登録・`known_legacy_versions`も更新。
- `persistent_conversation_service.py`：`complete_generation(web_search_result=...)`、`get_conversation_web_citations()`。
- `web/persistent_contracts.py`・`persistent_routes.py`：`PersistentTurnResponse.web_citations`、`_project_turn_web_citations()`、REST Detail応答への配線。

## WU-006: Frontend（完成分）

- Standalone `WebSearchPanel`：Direct URL入力＋Untrusted Label（前Package実施済み、無変更）。
- **Chat Compose「次のTurnへURL添付」入力**（`Composer.tsx`）：Web Search機能がManual ON時のみ表示。送信時だけ`manual_web_evidence_url`をSettingsへ含め（Retry／Regenerateには含めない設計）、送信後に自動Clear。
- `WebCitationsSection.tsx`：Assistant吹き出し内にWeb Evidenceを表示（URL・Title・Digest・Untrusted Label、失敗時はFailure Reason表示）。
- `persistentDetailProjection.ts`：`PersistentTurn.web_citations`からの再構成、`DisplayMessage.webCitations`。

## Changed Paths（本Package、34ファイル）

Backend（10）：
```text
src/margpa_runtime_llm/modules/conversation/contracts.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
src/margpa_runtime_llm/modules/conversation/ports/conversation_store.py
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_migration.py
src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py
src/margpa_runtime_llm/web/persistent_contracts.py
src/margpa_runtime_llm/web/persistent_routes.py
src/margpa_runtime_llm/web/persistent_streaming.py
src/margpa_runtime_llm/bootstrap/web_application.py
```
（`web_knowledge/contracts.py`・`ports.py`・`__init__.py`はP8-A-WU-001〜003の前Recoveryで既に列挙済みのため再掲しない — 本Package内でも追加変更している）

Backend Test（10）：
```text
tests/unit/conversation/test_conversation_generation.py
tests/unit/conversation/test_persistent_conversation_service.py
tests/unit/conversation/test_persistent_conversation_actions.py
tests/unit/conversation/test_persistent_attempt_provenance.py
tests/unit/conversation/test_sqlite_migration.py
tests/unit/bootstrap/test_repair_live_integration.py
tests/unit/web/test_persistent_streaming_web_evidence.py（新規）
tests/integration/conversation/test_persistent_citation_evidence.py
tests/integration/conversation/test_local_conversation_persistence.py
tests/integration/web/test_persistent_web_app.py
```

Frontend Source（8）：
```text
frontend/src/App.tsx
frontend/src/types.ts
frontend/src/i18n/translations.ts
frontend/src/lib/persistentDetailProjection.ts
frontend/src/components/Composer.tsx
frontend/src/components/MessageBubble.tsx
frontend/src/components/WebCitationsSection.tsx（新規）
src/margpa_runtime_llm/web/static/app.js（Build Artifact）
```

Frontend Test（6）：
```text
frontend/src/lib/persistentDetailProjection.test.ts
frontend/src/components/Composer.test.tsx（新規）
frontend/src/components/MessageBubble.test.tsx
frontend/src/components/MessageList.test.tsx
frontend/src/components/WebCitationsSection.test.tsx（新規）
```

## Canonical Verification（本Package完了時点）

```text
Backend: .venv/bin/pytest -q            -> 1984 passed, 7 deselected
         .venv/bin/mypy src/            -> Success (323 files)
         .venv/bin/ruff check .         -> All checks passed
         .venv/bin/ruff format --check . -> 527 files already formatted

Frontend: npx tsc --noEmit              -> clean
          npm test                     -> 280 passed (31 files)
          npm run lint                 -> clean
          npm run build                -> succeeded, app.js再生成済み
```

Entry Baseline（Backend 64／Frontend 6）およびP8-A-WU-001〜003完了時点（Backend 1972／Frontend 273）からの純増：Backend +12、Frontend +7、Regression 0（一貫して確認済み）。

## Internal Review（1 Cycle、本Package分）

1. **Controller Issue解消**: P7-CODEX-017型（配信Artifact未反映）の再発防止として`npm run build`実行・Static Artifact更新を確認 — 適合。
2. **Backward Compatibility**: 新規Field・新規Parameterは全てOptional／デフォルト値付きで追加。既存呼出元（Fake Session double 6ファイル、`CommitConversation`構築箇所、`ConversationSettings`構築箇所）は無変更のまま動作することを1984件のFull Suiteで確認。
3. **Security**: Web EvidenceはGuardrail Context Source Checkを通過しない限りModelへ届かない（既存Hookを再利用、新規Bypass経路を作っていない）。Untrusted Instructionを明示しSystem／User Authorityと分離。
4. **Historical Immutability**: 既存`turn_citations`のSchema・Behavior・Migration Chainを変更していない（新Tableの追加のみ）。
5. **Scope遵守**: Backend/Frontend Source・Test・Static Artifactのみ変更。Git Mutation 0、Network 0、Real Browser 0、Real Model 0。
6. **Claim精度**: P8-A全体を成立としてClaimする根拠（WU-001〜006全Complete、ACC-001〜012個別検証、Regression 0）を本Documentへ記録。

Critical／Major：0件。Minor：2件（非Blocking、Stable未解決へ記録）：
- **P8-RW-A-IR-001**: `WebCitationsSection`のLive SSE表示（Persistent Chat中の`web_evidence`Event受信→即時Bubble反映）は未実装。現状はTurn完了後のDetail Projectionからの再構成のみで表示される。Documentation RAGの`RETRIEVAL`同様のLive反映は将来のUI改善として残す（Persistence自体は正しく動作しており、Citation Identityの欠落や不整合はない）。
- **P8-RW-A-IR-002**: `WebCitationsSection`のFailure表示（`webSearchPanelRejected: <raw code>`）はraw Failure Reason Codeをそのまま連結表示しており、Documentation RAG側の`knownServerMessages`翻訳Tableのような per-code 翻訳文言を持たない。機能的には正しいが、User向け文言の洗練は将来のHardening項目とする。

## P8-ACC-001〜012 最終Disposition

| ID | Disposition |
|---|---|
| P8-ACC-001 | PASS |
| P8-ACC-002 | PASS |
| P8-ACC-003 | PASS |
| P8-ACC-004 | PASS |
| P8-ACC-005 | PASS |
| P8-ACC-006 | PASS |
| P8-ACC-007 | PASS |
| P8-ACC-008 | PASS |
| P8-ACC-009 | **PASS**（前Recovery: NOT MET → 本Packageで実装・Test済み） |
| P8-ACC-010 | PASS |
| P8-ACC-011 | **PASS**（前Recovery: NOT MET → 本Packageで実装・Test済み） |
| P8-ACC-012 | PASS |

**P8-ACC-001〜012 全12件PASS。P8-A成立。**

## Action Inventory

```yaml
network_actions: 0
npm_install_or_download: 0
node_runtime_switch: 0
git_mutation_actions: 0
git_read_only_actions: 1
backup_actions: 0
user_runtime_data_access: 0
real_model_access: 0
real_browser_access: 0
provider_memory_used: false
project_root_外_access_executed: 0
```

## Exact Next Work Unit

```text
Next: P8-B Entry UI Simplification／Archive Management
  P8-A成立に伴い、Execution Plan自身の順序に従い開始する。
  Do Not Repeat: P8-A-WU-001〜006（本Recoveryで完成済み）。
```
