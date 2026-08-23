# Phase 3-F Complete／Recovery Entry

```yaml
document_id: phase_3_f_complete_recovery
status: current_recovery_entry
phase: phase_3
subphase: phase_3_f
work_unit: p3_f_wu_006_complete
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_g_wu_004_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 21:00:00 JST
predecessor: phase_3_e_complete_recovery_ja_20260821203000
```

Lightweight Recovery Entry。Phase 3-F全体（WU-001〜006）を1件に統合。

## Current State

```text
Accepted Predecessor : Phase 3-E（完了）
Current WU            : Phase 3-F 完了（WU-001〜006）
Next WU                : P3-G-WU-001（Integrated Technical Validation）
```

## Phase 3-F Summary（Runtime／Web／UI／Observation統合）

```text
P3-F-WU-001 Governance Mode Contract              : ACCEPTED_LOCAL
P3-F-WU-002 Runtime Composition／Bootstrap         : ACCEPTED_LOCAL
P3-F-WU-003 Governance Status API                 : ACCEPTED_LOCAL
P3-F-WU-004 React Settings UI                     : ACCEPTED_LOCAL
P3-F-WU-005 Non-intervening Generation Observation Hook : ACCEPTED_LOCAL
P3-F-WU-006 Mode／Access／Compatibility Matrix     : ACCEPTED_LOCAL
```

`GovernanceMode`（off／observe／enforce）はPydantic `Literal`＋固定Descriptor Table（`PHASE_3_MODE_DESCRIPTORS`）で構成し、`enforce`は`unavailable`のまま構造的に固定——`apply_mode()`はEnforce Requestを常にRejectし、無効Modeへの静かなDowngradeを行わない。`GovernanceDefinitionsRuntime`は`off`の間Provider Callを一切行わず（`_run_observe_pipeline`は`apply_mode(OBSERVE)`経由でのみ実行）、Bootstrapは`entrypoints/web/main.py`の既存Gate Function Pattern（`_configuration_control_enabled`と同形）を`_governance_definitions_enabled`として複製し、Local／Loopback／Auth-disabledかつ明示Flagのみで有効化した。

Status API（`web/governance_routes.py`、`GET /api/v3/governance/runtime`・`POST /api/v3/governance/mode`）は既存Route Patternを踏襲し、絶対Path／Source本文／Raw Exceptionを一切返さない。設計書§9.2はMode MutationをConfiguration ControlのPreview/Applyへ統合することを提案しているが、本Phaseでは専用Endpointとして実装し、Module Docstringおよび本Entryへ Deferred Evidence として明記した（Scope逸脱として隠さない）。

React Advanced Settingsへ`GovernancePanel`を追加：`governance-bootstrap` Bootstrap Marker（`web/app.py`のCONFIGURATION_BOOTSTRAP同型）で存在をGate、初期`OFF`・`OBSERVE`選択可・`ENFORCE`はDisabled＋理由表示、Revision／Digest／Observe Summary（Provider State・Package・Definition数・有効／無効／未対応Adapter数・Compiled Plan ID）を表示。実Serverでの手動End-to-end確認（Browser Pane）で、OFF→OBSERVE→OFF往復・Revision増分・実18件Definition検出を確認済み。

Non-intervening Generation Observation Hook（P3-F-WU-005）は、v1（`web/streaming.py`の`produce()`）／v2（`web/persistent_streaming.py`の`PersistentSseBridge._produce`）双方の既存SSE Producer Loopに、`GenerationObservationTracker`（`web/generation_observation.py`）による純粋な副作用専用Watchを追加——`ConversationEvent`のYield順序・内容は一切変更しない。`EvidenceGenerationObserver`（`adapters/audit_evidence/`）はGovernance Mode（`mode_provider`経由でLive参照）が`observe`の時のみEvidence Store（`LocalJsonlEvidenceStore`、`runtime_data/audit_evidence/web_preview/`）へ`generation_started`／`generation_terminal`をAppendし、`off`／`enforce`では0 Call。Store書込失敗・不正Payload・Observer自身の例外は全経路でTry/Except Swallowにより非介入を保証。実Server＋実Modelで1往復手動確認済み（Mode=observeで2件正しくAppend、Mode=offへ戻すと以降0件）。

P3-F-WU-006（横断Test）は、Governance Mode（off／observe／enforce-rejected）・Definition Provider（empty／reference／invalid、既存Phase 3-C〜E Matrixを継承）・Access Profile（Public／Basic時はCLI Gate Functionが起動前にRejectするため構造的にDefinition／Evidence Call不可能——`_governance_definitions_enabled`のUnit Testで確認）・Conversation Mode（Persistent／Ephemeral、両方でSSE非改変とMode Gatingを確認）の四軸をカバーするTestを追加・統合した。

## Exact Mutation（Phase 3-F）

```text
Created:
  src/margpa_runtime_llm/modules/governance_definitions/domain/mode.py
  src/margpa_runtime_llm/modules/governance_definitions/runtime.py
  src/margpa_runtime_llm/bootstrap/governance_definitions.py
  src/margpa_runtime_llm/web/governance_routes.py
  src/margpa_runtime_llm/modules/audit_evidence/generation_observation.py
  src/margpa_runtime_llm/adapters/audit_evidence/evidence_generation_observer.py
  src/margpa_runtime_llm/bootstrap/audit_evidence.py
  src/margpa_runtime_llm/web/generation_observation.py
  frontend/src/lib/governanceBootstrap.ts（＋.test.ts）
  frontend/src/components/GovernancePanel.tsx（＋.test.tsx）
  tests/unit/governance_definitions/test_governance_mode.py
  tests/unit/governance_definitions/test_runtime.py
  tests/integration/governance_definitions/test_runtime_with_real_bundle.py
  tests/integration/web/test_governance_definitions_web_app.py
  tests/unit/audit_evidence/test_evidence_generation_observer.py
  tests/unit/web/test_generation_observation.py
  docs/project/phases/phase_3/history/index/phase_3_f_complete_recovery_ja_20260821210000.md（本File）
Modified:
  src/margpa_runtime_llm/modules/governance_definitions/domain/__init__.py（累積Export追加）
  src/margpa_runtime_llm/entrypoints/web/main.py（--phase-3-governance-definitions系Flag、_governance_definitions_enabled、_current_governance_mode_value、app.state.governance_definitions_runtime／generation_observer配線）
  src/margpa_runtime_llm/web/app.py（GOVERNANCE_BOOTSTRAP_*定数、index()へのMarker置換、chat_streamでのObservationTracker生成、governance router登録、GovernanceWebError Handler）
  src/margpa_runtime_llm/web/streaming.py（stream_session_as_sseへobservation_tracker引数追加）
  src/margpa_runtime_llm/web/persistent_streaming.py（PersistentSseBridgeへobservation_tracker引数追加）
  src/margpa_runtime_llm/web/persistent_routes.py（_stream_responseでのObservationTracker生成）
  src/margpa_runtime_llm/modules/audit_evidence/public.py（GenerationObserverPort Export追加）
  frontend/index.html／src/margpa_runtime_llm/web/static/index.html（governance-bootstrap Marker追加）
  frontend/src/App.tsx／App.test.tsx（Governance State／Load／Apply配線）
  frontend/src/components/SettingsModal/SettingsModal.tsx／.test.tsx（Governance Panel統合）
  frontend/src/types.ts／api/client.ts／i18n/translations.ts（Governance型・API・文言追加）
  tests/integration/web/test_web_app.py（Generation Observer統合Test追加）
  tests/integration/web/test_persistent_web_app.py（Generation Observer統合Test追加）
  tests/unit/web/test_web_cli.py（Governance Gate Function／Mode Value Reader Test追加）
  src/margpa_runtime_llm/web/static/app.js／app.css（Frontend Build成果物、npm run build再生成）
  .claude/launch.json（開発用Preview Server起動設定、新規・非Git管理File）
Deleted: NONE
Git Mutation: 0　Root外Action: 0　User実Data接触: 0（実Model生成確認は開発Serverのtmp的Evidence Storeのみ、確認後rm -rf runtime_data/audit_evidenceで削除済み）
```

## Tests Run／Results

```text
Full Suite（Backend）: 848 passed／3 deselected（Baseline 823 + 25 new、Regression 0）
  内訳: WU-003 API Test +6、WU-005 Adapter/Tracker/Integration Test +17、WU-006 Gate Test +2
Frontend Test        : 116 passed（Baseline 108 + 8 new：GovernancePanel 6、governanceBootstrap 5、App.tsx 2、SettingsModal 3 ― 実数は各ファイル差分参照）
Ruff／Mypy（src）     : PASS — 152 source files
Frontend Typecheck／Lint／Build : PASS（tsc --noEmit、eslint、vite build）
実Server手動確認      : OFF→OBSERVE→OFF往復（Browser Pane、Revision増分・18件Definition検出）、実Model 1往復生成でEvidence Append 2件（started／terminal）確認、OFFへ戻し後0件追加を確認
```

## Open Findings

継続：Mypy bare（tests/全体）既存11件Error（Phase 2由来、Deferred、`mypy src`のみが宣言Scope）。設計書§9.2の「Mode MutationをConfiguration Control Preview/Applyへ統合」提案は本Phaseでは専用Endpointのまま——Phase 4以降のDeferred Evidenceとして記録。Evidence Store Root（`runtime_data/audit_evidence/web_preview/`）は固定Scope ID一つのみ（複数Worker／複数Scope分離は将来Phase）。

## Next Exact Route

P3-G-WU-001（Integrated Technical Validation）へ進む。
