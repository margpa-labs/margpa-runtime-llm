# Phase 6 Current Claude Task — Package R19 Final Recovery（Shared Request Correlation Registry）

```yaml
document_id: phase_6_current_claude_task_r19_final_recovery_20260829041908
package: P6-RR-R19
status: PACKAGE_COMPLETE
created_at: 2026-08-29 04:19:08 JST
active_contract: phase_6_claude_current_task_r17_to_r20_exact_rework_handoff_ja_20260829032604.md
predecessor: phase_6_current_claude_task_r18_final_recovery_ja_20260829040404.md
git_action: 0
network_action: 0
root_outside_action: 0 known
```

## 対象Finding

```text
P6-CODEX-082: Request-ID Correlation Registry／Server-side Join未成立 -> RESOLVED（本Package）
```

## 調査（実装前）

R15の修正（Recording自身のLast Outcomeを起点とするCurrent識別）はJudge OFF Turnにおける「完了後の
誤Join」を正しく除去したが、その起点自体が「Turn RecordingがWriteされた後」にしか成立しない
Completion-only Proxyであることを確認した。新しいTurnが開始し、Main生成が進行中で、Judge／
Recordingがまだ一度も走っていない間、`recording_composition.last_outcome()`は依然として
「一つ前のTurn」を指したままであり、Current Requestが新Turnへ切り替わらない。これがUser Macで
実証された「送信後に設定を開くと一つ前、開き直すと最新」というObservability Lagの根本原因である
ことを、Codexの指摘通り確認した。

## 実装

### 新設: Shared Request Correlation Registry

Judge CompositionやRecording Last Outcomeを起点にするのではなく、`ConversationGenerationSession`
がTurn開始時（`request_id`確定直後、Judge／Repair／Recordingのいずれも走る前）に自分自身を
登録する、独立したRegistryを新設した。既存のField保有者（`JudgeGovernanceComposition`の
Judge Result、`RecordingCompositionState`×2のRecording Outcome、`LiveJudgeResult`自身の
Frozen Mode／Provider／Budget Field）は重複させず、Server-side Summary構築時にこのRegistryの
`current_request_id()`を起点としてJoinする設計とした。

```text
[新規]
src/margpa_runtime_llm/bootstrap/request_correlation_registry.py
  RequestCorrelationEntry（request_id, generation, status, started_at, completed_at）、
  RequestCorrelationRegistry（begin, mark_terminal, current_request_id, entry_for, entries）
  を新設。Thread-safe、Retention Bound付き（Default 8件）。

[変更]
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  Layering維持のため、bootstrap/からConcrete Registry型を直接Importしない
  （既存のJudgeCompletionHook／RecordingCompletionHookと同じ、Plain Callable Hook Pattern）。
  - RequestCorrelationBeginHook = Callable[[str, str], None]（request_id, started_at）
  - RequestCorrelationTerminalHook = Callable[[str, str, str], None]（request_id, status,
    completed_at）を新設。
  - ConversationGenerationService.start()内、request_id確定直後（Judge Mode解決・Runtime
    Snapshot解決よりも前）にrequest_correlation_beginを呼ぶ。start()自体が後続で失敗した場合
    （except BaseException:）もrequest_correlation_terminal(status="failed")で確実にClose。
  - ConversationGenerationSession: self._terminal_statusを新設（Default "failed"）。
    _completed_event／_cancelled_event／_error_eventそれぞれの成立点で正確に設定。
    events()自身のfinally（唯一保証されたTerminal境界）でrequest_correlation_terminalを
    exactly onceで呼ぶ。

src/margpa_runtime_llm/web/contracts.py
  WebRuntimeへrequest_correlation_registry: "RequestCorrelationRegistry | None"を追加
  （TYPE_CHECKING限定Import、既存のjudge_governance_composition等と同じPattern）。

src/margpa_runtime_llm/bootstrap/web_application.py
  feature_modes_enabled時にRequestCorrelationRegistry()を1つ構築し、
  ConversationGenerationService（request_correlation_begin／terminal Hook経由）と
  WebRuntime双方へ配線。

src/margpa_runtime_llm/web/feature_modes_routes.py
  RequestCorrelationSummaryResponse（request_id, status, started_at, completed_at,
  judge_result, turn_recording, judge_evidence_recording）を新設。
  RecordingCorrelationResponseへcurrent: RequestCorrelationSummaryResponse | Noneを追加
  （既存のrequest_id／current_turn／current_judge_evidence／historical_or_unmatchedは
  後方互換のため維持、値もRegistry起点へ更新）。
  _recording_snapshot()：current_request_idをregistry.current_request_id()から取得
  （Registry未配線時は旧Recording-outcome起点へFallback、既存Test互換）。
  judge_governance_composition.last_result()をcurrent_request_idと突き合わせてJudge Resultを
  Join。Turn Recording／Judge Evidence Recordingも同一Request IDのみCurrentへ。

frontend/src/types.ts
  RequestCorrelationSummary Interfaceを新設、RecordingModeSnapshot.correlation.currentへ追加。

frontend/src/components/FeatureModesPanel.tsx
  renderRecordingCorrelation()へcurrent.status／started_at／completed_atの表示を追加
  （#feature-modes-recording-correlation-status）。既存のcurrent_turn／current_judge_evidence
  消費Logicは無変更（Server供給値がRegistry起点へ更新されたことで自動的に正しくなる）。

[新規Test]
tests/unit/bootstrap/test_request_correlation_registry.py（6 tests）
  Registry単体：begin直後のCurrent正当性、新Turn開始による旧Turn自動供出、Terminal更新、
  未知Request ID黙殺、Retention Eviction、Generation単調増加。

tests/unit/conversation/test_conversation_generation_judge_hook.py（4 tests追加）
  - test_request_correlation_begin_fires_before_judge_hook_with_the_turn_request_id
  - test_request_correlation_terminal_fires_once_completed_for_a_normal_turn
  - test_request_correlation_terminal_fires_failed_when_guardrail_rejects
  - test_request_correlation_terminal_fires_cancelled_when_the_user_cancels

tests/integration/web/test_feature_modes_routes.py（4 tests追加、R19-A〜D）
  - test_r19_a_current_turn_is_correct_before_recording_hook_ever_fires
  - test_r19_b_observe_background_pending_current_request
  - test_r19_c_completed_turn_joins_judge_result_and_both_recordings
  - test_r19_d_out_of_order_late_evidence_for_a_superseded_request_stays_historical

frontend/src/components/FeatureModesPanel.test.tsx（既存Test1件へStatus表示Assertion追加）
```

## Focused／Full Evidence

```text
Command: ./.venv/bin/pytest tests/unit/bootstrap/test_request_correlation_registry.py \
         tests/unit/conversation/ tests/integration/web/test_feature_modes_routes.py -q
Result : 全件PASS（新規14 tests含む）

Command: ./.venv/bin/pytest tests/unit/ tests/integration/ -q
Result : 1732 passed, 7 deselected（R18終了時1718 + 新規14 tests = 1732、Regression 0）

Command: ./.venv/bin/mypy src tests
Result : Success: no issues found in 475 source files

Command: ./.venv/bin/ruff check <本Package変更File>
Result : All checks passed!

Command（Frontend）: npm test / npm run typecheck / npm run lint / npm run build
Result : Test Files 25 passed (25) / Tests 231 passed (231) / typecheck・lint・build全PASS
         （Static Build出力3 Fileのうちapp.jsのみ実際に変更、app.css／index.htmlは無変更のまま
         一致を確認）
```

## Required Regression Scenarios（本Package分）

```text
R19-A: Judge OFF＋Recording FULLのCurrent Turn
  -> test_r19_a_current_turn_is_correct_before_recording_hook_ever_fires PASS
R19-B: OBSERVE Pending中のCurrent Request
  -> test_r19_b_observe_background_pending_current_request PASS
R19-C: Completed TurnのJudge／Recording Single Join
  -> test_r19_c_completed_turn_joins_judge_result_and_both_recordings PASS
R19-D: Out-of-order旧RequestのHistorical分離
  -> test_r19_d_out_of_order_late_evidence_for_a_superseded_request_stays_historical PASS
```

## Scope Boundary（意図的に対象外とした部分、理由付き）

```text
historical_or_unmatched自体のRegistry Metadata拡張: 現状はRecording Outcome（request_id／ok／
  degraded_reason）のみのまま維持した。Handoffが明示的に要求したのはCurrentのFull Joinであり、
  Historical一覧までRegistry Metadataで拡張することは指示範囲を超えるScope Creepと判断し、
  対象外とした。

Judge Result・Recording以外のTurn Metadata（例: Documentation RAG使用有無等）のCurrent
  Summaryへの追加: Handoffが明示した対象（Turn Metadata、Judge Result、Final Disposition、
  Failure、Configured／Active／Executed Provider、Budget、Frozen Modes、開始／完了時刻、
  Turn Recording、Judge Evidence Recording）は全てJudgeLastResultResponse
  （既存、Frozen Modes／Provider／Budget／Final Disposition／Failureを包含）とRegistry Entry
  （status／started_at／completed_at）の組み合わせで充足されるため、追加Fieldは不要と判断した。
```

## Open Critical／Major

```text
Open Critical: 0
Open Major: 0（P6-CODEX-082はRESOLVED。084・085は引き続きOpen、R20で対応）
```

## Action Inventory（累積）

```text
Git Read Action: 1（P6-RR-R-INC-001、既存記録のまま。本Package中の新規発生 0）
Git Mutation      : 0
Network Action     : 0
Root外Persistent Write: 0 known
```

## Changed File SHA-512（本Package）

```text
410f4b932034b12a9626a9c2b70bb4bd02ad28456bd5d4008343d72410767146d6042fbfbdc25356b8fb276493a9720221ff81b7d368e4cbc0e6994df4e11cf4 request_correlation_registry.py
13539d9b19505591c458e6013c101594a733af615e9f02223531b1baa59448216e1e108a3b609f5c5c5d71cc1bc972c76dbbe7afbee5ed596046b281bd0335da conversation_generation.py
6847ec258223554fc9fa325eecdb99773b6a778a54fc79200957f567d45ea7f92a1d92974f6697bc87ee166bd3da2db2e0213a7f1e82052fde0e1f6b8958b5d4 contracts.py
ead9a47efc9a24faf8a6d366e34aaeb3ae4704db1795c71ad5610b06dd4f95ff5b5e63f9b04ae85f44bb8765a1e532a0fa60c7642df8cc80acfa5601fa4c8961 web_application.py
468270fbff228c66f3e24ccf270beb21912214bf3d932adca4b26a6d694d5d653d53452ca850eb27fd7970ee400ff0e5663673daa773fbf902503793e8894fe2 feature_modes_routes.py
91becaca688b813733eb57fd9e7a33ad439aff9e57581d192f1e590c546d11280868455159131f168f66ea5a95b50802a7dd5ec0cbda699c000d2a836a494ddf web/static/app.js
1487a8f4b8ae9f24b7de3ff1b7ef6e0b3db0974b20ff538f23522e70709e913944dcf675a6173fcbb273f34e6f191dfb6767a26881efc899f6edabca8eb0e597 web/static/app.css
0164475a2143041d53cebf2d43b61f9ccf9ab1bdf9c1b49a9efe5cee8176caaa2b5b9bee34116d7a782ddc71df451f825059dabb44bfeeef744aaf8a43b759bb web/static/index.html
3050f5b7e5a6ab7f26c0d3809f058099998a33876ca7d307259aa4be98ed90ef7577b16876f5f07da7c9425f6f03577c98fc6734e9baab2df5a47a8561775224 frontend/src/types.ts
dbba7cd59d578614818cfcc5a286985e7b3ddcc3dbdfe8e6060dabaa3cf96c6119b08375c19b0c2c52c2e80d9a2a1db00ccc1a89d007bb25fff08985ba268051 FeatureModesPanel.tsx
947451a6525379dfbd8e2f81722bebe014ad44628359cf6435dd5343a29201c207c9acd3bf0ffdb9303bbf78328b45b3b9528ec8f7f651cce295875308f99f1f test_request_correlation_registry.py
5dbb0a20741420ef0fd35b0dc8b0ee4680bc3808e8138f99ef4be54ef3ef177ae623645344a3dcc2107a3b2a2b4ee6492e2f25638a5d03e55262e57a1a04e9ed test_conversation_generation_judge_hook.py
e930b5a1c269d694734b4ff31c8d3a16bfe59600e9d9e9848f9e9ef6a001a63243de58436b3f2a70f0a426caefae3f20ed8ac5bc65a6f38153354e08ac4801e6 test_feature_modes_routes.py
7a6e12e7dc6c6484bfebf94ad707207f8ba4fbc18ce209863027595faa74b582837e0458afe4c3831e02b7a638178b9c840a578921b2c647adaee95cd31b1bcd FeatureModesPanel.test.tsx
```

## Exact Next Action

```text
next_exact_action: P6-RR-R20-WU-001（Contract-complete QA／Claim Audit／Return）
```
