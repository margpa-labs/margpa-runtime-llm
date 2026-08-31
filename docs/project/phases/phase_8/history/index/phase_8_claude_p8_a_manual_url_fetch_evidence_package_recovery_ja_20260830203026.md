# Phase 8 Claude P8-A Manual URL Fetch/Evidence — Package Recovery Index

```yaml
document_type: recovery_index
phase: phase_8
package: P8-A
completed_cp: CP8-04 (WU-001–003), CP8-05 (WU-006 partial)
provider: Claude
state: package_partial_open_mvp_blocker
created_at: 2026-08-30 20:30 JST
```

## Continuity

継続元：`docs/project/phases/phase_8/history/index/phase_8_claude_cp8_04_wu_001_002_003_recovery_index_ja_20260830201912.md`（本Documentが上位のPackage境界Recoveryであり、CP8-04の内容を差し替えるものではなく統合する）。CP8-01〜03／Mandatory Reading Digest確認／Entry Baselineは再実行していない。

## Package全体の結論

```yaml
p8_a_established: false
mvp_blocker_open: 1
critical_open: 0
major_open: 0
next_provider_authority: implementation_authority_required
```

P8-A（Manual URL Fetch／Evidence）は**未成立**。理由はP8-ACC-009／011（Main Model Evidence注入・Persistence）が未着手のため。下記Work Unit別Statusと§4「Open MVP Blocker」を参照。

## Work Unit別Status

| Work Unit | 内容 | Status |
|---|---|---|
| P8-A-WU-001 | Direct URL Request／Status／Evidence Contract | **COMPLETE** |
| P8-A-WU-002 | Public http/https Validation、SSRF／Redirect Revalidation | **COMPLETE**（危険Port拒否を含め完成） |
| P8-A-WU-003 | Bounded Fetch、Size／Timeout／Content Type、Text Normalizer | **COMPLETE**（Phase 7から再利用、Direct URL Fetch用のProduction配線を追加） |
| P8-A-WU-004 | Untrusted EvidenceをMain Model Contextへ明示接続 | **NOT_STARTED**（設計調査済み、§5参照） |
| P8-A-WU-005 | Citation PersistenceとReload／Restart復元 | **NOT_STARTED**（WU-004に従属、設計調査済み、§5参照） |
| P8-A-WU-006 | Settings Toggle／Manual URL入力UI／Untrusted Label／Failure Presentation | **PARTIAL**（Standalone Panelでの入力・表示・失敗提示は完成。Main Model Evidence注入と連動する「次の送信へ添付」導線はWU-004に従属のため未着手） |

## §1 CP8-04（WU-001〜003）— 完了済み

`docs/project/phases/phase_8/history/index/phase_8_claude_cp8_04_wu_001_002_003_recovery_index_ja_20260830201912.md`に記載済みのため詳細はここに繰り返さない。要旨：

- Copilot Partial差分の`IndentationError`（`search_and_fetch()`途中への`fetch_direct_url()`誤挿入）を修復し、後者を独立Methodへ再配置。
- Controller Recovery §6の7項目Auditのうち1〜6を成立させた（Production Httpx配線分離、Redirect後Canonical URL、Citation Content Type／Source Class、危険Port拒否、OFF/Rejected時Network 0の確認、既存Fixture後方互換確認）。7項目目（Main Model Evidence注入／Persistence／UI）が本Recoveryの対象。

## §2 CP8-05（WU-006 Partial）— 本Package内で追加実施

Standalone `WebSearchPanel`（Settings内、既存のSearch Query Boxと並置）へ、Direct URL Fetchの入力・表示・失敗提示を追加した。Main Model Contextへの接続はWU-004が前提のため、本UIは「取得して画面で確認する」までのScopeに限定している（Handoff §6「取得Contentを画面表示し...」は満たすが、「Main Modelへ明示的に渡せる」はWU-004待ち）。

### Changed Paths（Frontend、6）

- `frontend/src/components/WebSearchPanel.tsx`（Direct URL Form、`EvidenceList`共通化、Untrusted Label追加）
- `frontend/src/components/WebSearchPanel.test.tsx`（新規5 Test）
- `frontend/src/components/SettingsModal/SettingsModal.tsx`（`onWebSearchDirectUrl` Prop中継）
- `frontend/src/api/client.ts`（`fetchDirectUrl()`追加）
- `frontend/src/types.ts`（`WebCitationItem`へ`content_type`／`content_sha512`／`source_class`追加）
- `frontend/src/i18n/translations.ts`（ja/en 11 Key追加：Direct URL Title/Note/Label/Fetch/Idle/Loading/Ready/Failed、Untrusted Label）
- `frontend/src/App.tsx`（`webSearchState.directUrl`初期化、`handleFetchDirectUrl()`追加、Prop配線）

### Changed Paths（Static Artifact、Build実行のEvidence）

- `src/margpa_runtime_llm/web/static/app.js`（`npm run build`で現行Sourceから再生成。P7-RW5-Eの教訓— Build未実行のまま配信Artifactが古いままになる失敗——を踏まえ、本Package内でBuildまで実行し確認した）

### Focused Verification

```text
NODE_OPTIONS=--no-webstorage vitest run（該当3 File）
  57 passed

npm test（Full Canonical、29 files）
  273 passed（Entry/前回Baseline 268から+5、Regression 0）

npx tsc --noEmit
  Errors: 0

npm run lint
  Errors: 0

npm run build
  tsc --noEmit && vite build succeeded
  app.js 337.33 kB (was 333.72 kB before this Package)
```

## §3 Backend Full Canonical（Package全体、WU-001〜003＋006共通）

```text
.venv/bin/pytest（Full Suite、Deselect込み）
  1972 passed, 7 deselected（Entry/直近Baseline 1952から+20、Regression 0）

.venv/bin/mypy src/
  Success: no issues found in 323 source files

.venv/bin/ruff check .
  All checks passed

.venv/bin/ruff format --check .
  526 files already formatted（1件Auto-fix適用済み、再検証済み）
```

## §4 Open MVP Blocker — P8-A-WU-004／005（Main Model Evidence注入／Persistence）

### 4.1 現状

`fetch_direct_url()`（Standalone `/api/v2/web-search/direct` Route経由）で取得したContentは、User画面へのPreview表示までは成立しているが、**Conversation Turnの生成へは一切接続されていない**。既存のDocumentation RAG（`documentation_rag`）は同種の機能を持つが、Web Evidenceは構造的に独立したまま — `WebCitation`／`WebSearchAndFetchResult`はこの意図（両契約のDocstringが明示的に"Web analogue of DocumentationAugmentation"と記述）で先行実装されていたが、実際の接続Layer（Injection／Persistence）は本Packageまで誰も着手していなかった（Copilot PartialもClaudeもこのLayerには触れていない）。

### 4.2 なぜ本Package内で実装しなかったか

`ConversationGenerationSession`／`ConversationGenerationService`（`src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`）を直接読み、正しい接続点を特定した（下記4.3）。この File は:

- Constructor Parameterが20件超、Guardrail Pre/Post Check、Judge Enforce/Observe、Recording Hook、Request Correlation、Cancellation、Context Usage Token会計等が緻密に絡み合う、Repository内で最もHardeningされたCore Fileである（`P6-RR-R18/R19`、`P6-CODEX-010/012/025/082/083`等、複数回のIndependent Review Reworkを経た履歴Commentが随所にある）。
- Documentation RAG Evidenceは、Guardrail Context Source Check（`_guardrail_context_source_check()`、`_context_source_items()`共有）、Token会計（`_context_usage()`のRAG分離集計）、Live SSE（`_retrieval_event()`）、Terminal Event（`_completed_event()`の`documentation_retrieval`Key）、そして別途Persistence Layer（`turn_citations` SQLite Table、`build_turn_citation_evidence()`）の**5レイヤー全てに同じ厳密さで統合されている**。Web Evidenceを同格に扱うには、この5レイヤー全てを、既存Testを一切壊さずに複製する必要がある。
- 全Chat（ephemeral・persistent双方）が共有するCore Pipelineであり、誤りは「既存Chat／RAG／Citation／Persistenceに重大Regressionがない」というHandoff自身のMVP停止線要件に直接抵触するRisk Surfaceを持つ。
- Independent Reviewを経ない状態でこのFileへの複数File・大規模Diffを「完成」とSelf-certifyすることは、Proportional Autonomy Addendum §9「自己ReviewはIndependent Reviewではない」およびPoC/MVP Policy「品質を捏造せず」に反すると判断した。

これはRoutine ConfirmationでもMinor FindingでもReal Network未許可でもなく、Blast RadiusとVerifiability上の設計判断であり、Claudeの実装Authority内で下したScoping Decisionである（Addendum §8のUser Escalation対象には該当しない）。ただし、この判断自体と、それによりP8-A全体が「成立」に至っていないという事実は、次のReturn Handoffで正直に報告する。

### 4.3 実装設計（次Providerへの正確な引き継ぎ — Read-onlyの直接Source確認済み）

```text
WU-004 Main Model Evidence注入:

1. Contract:
   `ConversationSettings`（modules/conversation/contracts.py 47行目〜）へ
   `manual_web_evidence_url: str | None = Field(default=None, max_length=2048)`
   を追加（既定None、既存構築コード全件が無変更のまま動作）。

2. `ConversationGenerationService.__init__`
   （conversation_generation.py 1936行目〜）へ
   `web_knowledge_service: WebKnowledgeService | None = None`
   `web_search_governance_mode: WebEvidenceGovernanceMode = OFF`
   を追加。

3. `.start()`（2012行目〜）:
   `documentation_rag_mode`と同型のAvailability Check
   （2021〜2034行目のPatternを複製）。
   `manual_web_evidence_url`が設定されているのに
   `web_knowledge_service`がNoneならfail-closed
   （`InferenceError(UNSUPPORTED_CAPABILITY)`）。

4. `ConversationGenerationSession.__init__`
   （576行目〜）へ`web_knowledge_service`／
   `web_search_governance_mode`／`manual_web_evidence_url`／
   `web_evidence_request_factory`
   （`documentation_request_factory`と同型のClosure、2110〜2121行目参照）
   を追加。

5. `events()`（696行目〜）の`if self._documentation_rag is not None:`
   ブロック（709〜745行目）と並列に、Web Evidence Fetch Phaseを追加:
   `yield self._start_event(state="fetching_web_evidence")`
   → `self._web_knowledge_service.fetch_direct_url(...)`
   → Cancellation Check
   → **Guardrail Context Source Check**: `_context_source_items()`は
     Documentation固有のため、新規`_web_evidence_context_source_items()`
     （同じ`_ContextSourceItem`型を返す）を追加し、既存の
     `self._guardrail_context_source_hook`をそのまま再利用
     （1856行目`_guardrail_context_source_check()`と同型のWeb版を追加）。
   → `self._web_search_result = result`
   → `self._request = self._web_evidence_request_factory(result)`

6. `_inject_web_evidence()`静的Method
   （`_inject_documentation_reference()`2371行目〜と同型）を追加し、
   `_build_request()`（2234行目）から
   `_inject_documentation_reference()`の直後に呼ぶ。
   Roleは`MessageRole.TOOL`固定でよい（Web Evidenceは単一Source Classの
   ため`_PROMPT_ROLE_BY_SOURCE_CLASS`相当の分岐は不要）。Instructionは
   `CURRENT_EVIDENCE_AUTHORITY_INSTRUCTION`とは別に、Untrusted性を明示する
   新規`WEB_EVIDENCE_UNTRUSTED_INSTRUCTION`を用意する
   （P8-REQ-006の「Untrusted」区別をModelへ明示するため）。

7. `_completed_event()`（1363行目〜）の
   `if self._documentation_augmentation is not None:` ブロック
   （1473〜1482行目）と並列に`data["web_evidence"]`を追加。
   `_retrieval_event()`（1600行目）と同型の`_web_evidence_event()`を
   `events()`のFetch Phaseで`yield`し、Live SSEでも同じEvidenceを
   即時表示できるようにする（P7-RW5-A同様、Live SSEとPersistent Detail
   の非対称を最初から作らないこと）。
   `_context_usage()`（1538行目）へWeb Evidenceの Token寄与も
   `rag_context_tokens`と並ぶ新規`web_evidence_context_tokens`として
   分離集計することが望ましい（必須ではない）。

8. `ConversationGenerationSession.web_search_result`Property
   （`documentation_augmentation`Property 674行目と同型）を追加し、
   `PersistentConversationService`から読み出せるようにする。

WU-005 Persistence（WU-004完了後に着手）:

1. `web_knowledge/contracts.py`へ`PersistedTurnWebCitationEvidence`
   （`PersistedTurnCitationEvidence`と同型）と
   `WEB_CITATION_EVIDENCE_SCHEMA_VERSION`、
   `build_turn_web_citation_evidence(result, *, conversation_id, turn_id)`
   を追加（`build_turn_citation_evidence()`と同型、
   documentation_rag/contracts.py 561〜604行目参照）。

2. `conversation/ports/conversation_store.py`の`CommitConversation`
   （41〜65行目）へ`web_citation_evidence`Fieldを追加し、
   `validate_scope()`を複製。

3. `sqlite_conversation_store.py`へ`turn_web_citations` Table
   （`turn_citations`のDDLを複製、276〜286行目参照）と対応する
   Migration Step（`sqlite_migration.py` 514〜544行目のPatternを複製）、
   `commit()`内のINSERT分岐（463〜479行目相当）、
   `get_turn_web_citations()`／`get_conversation_web_citations()`
   （871行目・891行目相当）を追加。

4. `web_knowledge/ports.py`へ`WebCitationEvidenceStorePort`
   （documentation_rag/ports.py 156〜174行目と同型）を追加。

5. `persistent_conversation_service.py`の`complete_generation()`
   （393〜450行目）へ`web_search_result`引数を追加し、
   `build_turn_web_citation_evidence()`を呼んで`_commit()`へ渡す。
   `get_conversation_web_citations()`
   （142〜155行目のisinstance Duck-check Patternを複製）も追加。

6. `web/persistent_contracts.py`へ`_project_turn_web_citations()`
   （`_project_turn_citations()` 205〜232行目と同型）と
   `PersistentTurnResponse.web_citations`Fieldを追加。

7. Frontend: `types.ts`の`PersistentTurn`へ`web_citations?`、
   `persistentDetailProjection.ts`の`detailToMessages()`へ
   もう一つの`webCitations`構築ブロック、
   新規`WebCitationsSection.tsx`（`CitationsSection.tsx`はDocumentation
   固有Shapeのため転用不可、`WebCitationItem`の実Fieldに対して
   新規Componentが必要）。

各StepでBackend Full Canonical Suite（現在1972 passed基準）を都度
再実行し、0 Regressionを確認しながら進めること。Guardrail関連の
既存Test（`test_context_source_*`系）は特に注意深く確認すること。
```

## §5 Internal Review（1 Cycle、本Package自己実施分）

WU-001/002/003/006(partial)について6角Reviewを実施。

1. **Controller Issue解消確認**: P7-CODEX-017型の再発防止として本Package内で`npm run build`を実行しStatic Artifactを確認 — 適合。
2. **Backward Compatibility**: `direct_fetch_provider`省略時Fallback、`WebSearchPanelState.directUrl`省略時Default — 両方Test済み、適合。
3. **Security**: 危険Port拒否、Redirect再検証（既存）、Untrusted Label（新規、Search／Direct URL両方に適用）— 適合。React JSX Interpolationによる自動Escapeを確認（Fetched ContentのXSS Risk 0）。
4. **Scope遵守**: Backend/Frontend Source・Test・Config・Static Artifactのみ変更。Git Mutation 0、Network 0、Real Browser 0、Real Model 0。
5. **Historical Immutability**: 新規機能のため該当なし（既存Citation Persistenceへの影響なし、Web CitationはまだPersistenceされていないため）。
6. **Claim精度**: P8-A自体を「成立」とはClaimしていない。§4のOpen MVP Blockerを明示。

Critical／Major：0件。Minor：1件（`_DANGEROUS_PORTS`Denylistは手動選定のMVP-tier Listであり、既存`_METADATA_HOSTNAME_DENYLIST`と同じ「網羅ではない」性質を持つ — Code Comment内で開示済み、Non-blocking）。

## §6 Action Inventory

```yaml
network_actions: 0
npm_install_or_download: 0
node_runtime_switch: 0
git_mutation_actions: 0
git_read_only_actions: 1  # git status のみ、Changed Paths確認目的
backup_actions: 0
user_runtime_data_access: 0
real_model_access: 0
real_browser_access: 0
provider_memory_used: false
project_root_外_access_executed: 0
```

Incident（Level 1、既にUserへ開示済み・記録目的で再掲）：`npm run build`のExit確認目的で再実行しようとした際、Log Redirect先を誤ってFilesystem Root直下（`/tmp_build_rerun.log`）と指定するCommandを提案したが、User承認前にRejectされ未実行。実File・実Writeは発生していない。

## §7 Active Process／Temporary Artifact

- `frontend/.build_tmp/`（Node compile cache、Project内・空Content相当、副作用のみ）
- `pytest --basetemp`各種（Session Scratchpad配下、Project外への影響なし）

いずれもClaudeが本Session中に生成したものであり、いずれもUser Runtime Data・Git管理対象外。

## §8 Exact Next Work Unit

```text
Next: P8-A-WU-004（Main Model Evidence注入）
  §4.3の設計を、Backend Full Canonical Suite（1972 passed基準）を
  都度再実行しながら慎重に実装する。完了後WU-005（Persistence）へ。
  WU-004/005完了後、WU-006の残り（「次の送信へ添付」導線、
  Frontend側のManual URL→次Turn Evidence連携UI）を完成させる。
  この3 WUが揃った時点でP8-Aが初めて「成立」し、P8-B以降への
  連結Long-runを開始できる。
```

Do Not Repeat：CP8-01〜03、Mandatory Reading Digest確認、Entry Baseline、CP8-04（WU-001〜003の再実装）、CP8-05（WU-006 partialの再実装、Standalone Panel部分は完成済み）。
