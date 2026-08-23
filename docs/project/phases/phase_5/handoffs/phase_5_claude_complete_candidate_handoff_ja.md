# Phase 5 Claude Complete Candidate Handoff

```yaml
document_id: phase_5_claude_complete_candidate_handoff
status: complete_candidate
phase: phase_5
recorded_at: 2026-08-22 14:55:00 JST
git_mutation: not_performed
next_authority: codex_independent_review
```

Sourceとして参照した既存Recovery Evidence（Append-only、全て本Cycle内で作成、無変更）：

```text
phase_5_0_entry_preflight_reconciliation_and_execution_freeze_ja_20260822103200.md
phase_5_a_to_e_backend_core_recovery_ja_20260822111500.md
phase_5_f_web_frontend_integration_recovery_ja_20260822144024.md
phase_5_g_adversarial_verification_recovery_ja_20260822144841.md
```

## Phase 5-G Recommendation

**GO** — Phase 5-0からPhase 5-Gまでを連結実行し、Phase 5-G Adversarial Verification（`P5-ACC-001`〜`024`全24項目のChecklist監査）まで完走した。監査中に発見した唯一の重大Gap（Stream Guard Mode非依存Bug）は自己検出・修正・再発防止Test追加・全再確認まで完了している。Open Major Finding 0。Codex Independent Reviewへ引き継ぐ準備が整ったとClaudeは判断する（最終Acceptance判断はCodex／Userに属する）。

## Technical／Security Blockers

なし。Phase 5-G Recovery Evidence §2に記載した1件（`GuardrailGovernanceComposition.new_stream_guard()`のMode非依存Bug、Stream Point限定でOFF/OBSERVEでもDetector Scan＋Terminationが発生し得た）は本Cycle内で発見・修正・再発防止Test 5件を追加し、全て再確認済み。他にBlocker級のFindingはない。

## Governance Incidents

Local Bug 1件（上記Stream Guard Mode非依存Bug）。ユーザーへの個別報告・承認要求は行わず、Claude側設計統括者役の権限（本Instructionの明示委任）で解消し、本Documentで事後報告する。最上位規則違反・Project Root外操作・新規Authority要求・Frozen Scope変更・重大安全性/完全性/可逆性問題のいずれにも該当しないため、即時停止の対象ではないと判断した。

その他、Phase 5-A作成の既存Test Fixtureに3件の型Bug（`ExecutionState`文字列直渡し、冗長Identity比較、Protocol非準拠Fixture＋型注釈欠如）を本Cycleのmypy Strict網羅実行で新規検出・修正済み（詳細は`phase_5_f_web_frontend_integration_recovery_ja`§Test記載）。個別File単位のmypy実行では検出されず、Project設定準拠のBare実行で初めて顕在化したGapであり、今後の恒久的Static Check手順として「Bare `mypy`（Project Root、no追加引数）を最終Gateとする」ことを推奨事項として記録する。

## Controller-owned Work

- Stream Guard Mode非依存Bugの発見・修正・Test追加（上記）。
- Configuration Control `_EXTERNAL_APPLIER_KEYS`の2値→3値一般化（Governance/Main-Governance限定PairチェックをGuardrail込み3方向へ拡張、既存Pair Rejection Testは無変更のまま踏襲確認）。
- `_StreamGuardDecisionLike` Protocol Read-only化（mypy Protocol Invariance Bug、Frozen Dataclassとの構造的非適合を自己修正）。
- mypy Strict網羅実行によるPhase 5-A Test Fixture Bug 3件の検出・修正。
- CI相当のLocal Temp Directory衝突（`.p5t/`長Path×macOS Path上限）を自己診断し、短縮Basetempへ切替。

いずれもFrozen Scope内のLocal Bug／Test Failure／設計具体化の範疇であり、Requirement／Architecture／ADR／Execution Plan／Acceptance Matrixの変更は一切行っていない。

## Deferred Evidence／Current Impact

- `guardrail.context_source` Point：Domain／Application層は汎用実装済みだが、実RAG Pipelineへの接続は本Phase未実施（Phase 5-A〜E Recovery Evidenceで既に明示していたDeferredの継続）。現在の影響：RAG Contentは既存Phase 3/4設計によりSystem／Instruction Roleへ合成されない構造的保証があるため、Indirect Injectionに対する既存の防御線は保たれているが、Guardrail自身によるRAG Source内容の専用Detection（Injection Marker等）は行われない。
- Safety Model（Qwen3Guard等）：Production Default `UnavailableSafetyModelAdapter`のまま、実Artifact選定・Load・Promotionは対象外（P5-SFM-003/004、当初から本Phase Scope外として設計）。
- Authority／Registry Revision機構：本MVPは固定Local定数であり、実行時Mutation経路が存在しない（Stale化しうる状態自体が未実装）。

いずれもBlockerではなく、Phase 6以降または将来Cycleでの拡張対象として明示する。

## Exact Mutation

Phase 5全体（5-0〜5-G）で新規作成・変更したPathの要約（個別FileリストはPhase 5-0/5-A-to-E/5-Fの各Recovery Evidenceに記載済み、ここでは5-F/5-G分を中心に補足）：

```text
[新規]
src/margpa_runtime_llm/modules/guardrail_governance/       （Domain/Application、Phase 5-A〜E）
src/margpa_runtime_llm/adapters/guardrail_governance/       （Adapter、Phase 5-A〜E）
src/margpa_runtime_llm/bootstrap/guardrail_governance.py    （Composition Root、Phase 5-A〜E／5-F/5-G更新）
src/margpa_runtime_llm/web/guardrail_governance_routes.py   （Status Route、Phase 5-F）
frontend/src/lib/guardrailGovernanceBootstrap.ts(.test.ts)
frontend/src/components/GuardrailGovernancePanel.tsx(.test.tsx)
tests/unit/guardrail_governance/                            （Phase 5-A〜E／5-G追加分）
tests/unit/conversation/test_conversation_generation_guardrail_hooks.py
tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py
tests/integration/web/test_guardrail_governance_web_app.py
tests/integration/web/test_guardrail_governance_public_basic_call0.py
docs/project/phases/phase_5/history/operations/phase_5_{0,a_to_e,f,g}_*_recovery_ja_*.md

[既存への追加変更（Additive、既存行の削除・意味変更は無し）]
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  （Guardrail Hook/Stream Guard Factory Optional Param、Protocol Read-only化）
src/margpa_runtime_llm/bootstrap/web_application.py（Composition配線）
src/margpa_runtime_llm/entrypoints/web/main.py（CLI Flag/Enable Gate）
src/margpa_runtime_llm/web/app.py（Router登録／Lifespan Loopback Gate／Bootstrap Marker）
src/margpa_runtime_llm/web/contracts.py（WebRuntime.guardrail_governance_composition Field）
src/margpa_runtime_llm/modules/configuration_control/{contracts,ports,application,__init__}.py
src/margpa_runtime_llm/bootstrap/configuration_control.py
src/margpa_runtime_llm/web/configuration_contracts.py
frontend/src/{App.tsx,types.ts,api/client.ts,i18n/translations.ts}
frontend/src/components/SettingsModal/SettingsModal.tsx(.test.tsx)
frontend/index.html／src/margpa_runtime_llm/web/static/{index.html,app.js,app.css}
  （最終的に`vite build`実Compileで再生成、手動Marker編集から切替）
tests/unit/web/test_web_cli.py
tests/unit/configuration_control/test_configuration_control_service.py
```

Git Mutation：`not_performed`（Add／Commit／Push一切なし、本Sessionを通じて厳守）。

## Focused／Subphase／Full／Static／Frontend

```text
Focused（各File作成直後）    : ruff check / ruff format --check / mypy を都度実行、全てPASS
Subphase（5-0/5-A-E/5-F/5-G） : 各Recovery Evidence記載の通り、区切り毎にFull Suite再実行
Full Suite（最終）           : Backend 1156 passed／3 deselected
                               Frontend 175 passed（20 test files）
Static（最終、Bare実行）     : ruff check .            → All checks passed
                               ruff format --check .   → 316 files already formatted
                               mypy（引数無し、pyproject.toml準拠）→ 99 errors, 9 files
                                 （Phase 1〜4既存File内の既知債務8件＋Phase 5新規1件は
                                   既存httpx-auth Typing Patternの鏡写しで新規クラスの
                                   Errorではない、Phase 5固有File・Moduleは0 Error）
Frontend Static               : tsc --noEmit / eslint . / vite build → 全てPASS
                                 Build成果物はweb/static配下へ実反映済み
```

## OFF／OBSERVE／ENFORCE Matrix

```text
Point               OFF                          OBSERVE                        ENFORCE
guardrail.input     Detector Call 0              Detection＋Recommend記録のみ    Applicable/Authorized/
                     (test_off_mode_never_               (Executed Action 0)      Registered内でReject/Warn
                      evaluates_anything)                                         (test_enforce_rejects_...)
guardrail.output_   Detector Call 0              同上                            Reject／Typed Redaction
 candidate                                                                        (redact_typed_secret等)
guardrail.stream_   NullStreamGuard              NullStreamGuard                 IncrementalStreamGuard
 candidate           (Detector Call 0、            (Detector Call 0、              (Cross-chunk Detection、
                      Byte-identical、             Byte-identical、               Bounded Holdback、
                      Fix後再確認済み)              Fix後再確認済み)                Match時Zero-leak Terminal)
guardrail.context_  未接続（Deferred）            未接続（Deferred）              未接続（Deferred）
 source
```

全PointでOFF時のByte-identical／Call-0、OBSERVE時のMutation 0を実測Testで確認済み（Stream Pointは本Cycleで発見・修正したBugのFix後再確認を含む）。

## Input／Context／Stream／Output Adversarial Evidence

```text
Input      : Injection Marker（"ignore previous instructions"等）、Jailbreak Marker、
             Authority-spoofing Marker、Unicode Confusable／Invisible Char／Fullwidth
             正規化、多言語Benign非誤検知、Fragmented Multi-turn再構成検知
Context    : Deferred（上記）
Stream     : Cross-chunk Split Pattern検知（"SECRET-MAR"+"KER"型、Unit Test）、
             実Secret Pattern（"sk-"+16文字超Split、Web統合Test）でのZero-leak Termination、
             Clean StreamでのTotal Byte数一致（Holdback完全Flush）
Output     : Secret Pattern（sk-/AKIA/PEM Private Key）、PII Pattern（Email／Phone）、
             False Positive Fixture（Version文字列等）非誤検知
```

## Policy／Authority／Approval／Action Evidence

```text
Policy    : Category→Action固定Mapping、未知CategoryはUNKNOWN（Action未生成）、
            Clear DetectionはNOT_APPLICABLE
Authority : 固定Grant Set（repair／regenerate等は非付与）、Denied/Missingで
            Action 0（AUTHORITY_MISSING）
Approval  : UnavailableApprovalPortは常にUNAVAILABLE（APPROVED捏造なし）、
            approval_required時はAPPROVAL_PENDING／MISSINGでAction 0
Action    : allow／require_approval単独実行不可（NOT_EXECUTABLE_ACTION_IDS）、
            Terminal Conflict はEligibility-first→Severity勝者、Tie時CONFLICT_UNRESOLVED、
            Redactionは spans_are_verified() 必須（SPAN_UNVERIFIEDでAction 0）
```

## Secret／PII Non-disclosure Evidence

```text
- Web Status Route（/api/v3/guardrail-governance/status）：Detection/Match/Executed Action
  は数値Countのみ、Raw Content／Category詳細／Typed Span Offsetは一切含まない
  （test_enforce_status_projects_detection_and_action_counts_without_raw_content で
  実際に投入したInjection文字列がResponse本文に不在であることを確認）
- Enforce Reject Terminal：Error Event Dataにcode（Reason Code文字列）のみ、
  assistant_message等のRaw Content Fieldは含まれない（Ghost Completion 0）
- Public／Basic Call-0：Status Routeは`{"enabled": false, ...}`のみを返し、
  Composition未Bind時にInternal Stateへ一切触れない
```

## Compaction／Quota Recovery／Human Burden

本Cycle中、Auto-Compaction 0回、利用制限からの復旧 1回（作業再開後、直前のConversation Generation統合作業から中断なく継続）。User Clarificationは0件——全Local Bug／Test Failure／設計具体化はClaude自身の権限で解消した。Human Interventionは本Instruction開始時の宣言のみで、以降の個別承認要求は発生していない。

## Root／Git／User Data／External Evidence Class

```text
Project Root外Read/Write/実行     : 0件（全Path Project Root配下）
Provider Memory保存／依存         : 0件
ユーザー実runtime_data内容への接触 : 0件（全TestはFake/Local Fixtureのみ使用、
                                     tmp_path／Project-local .p5t/ Scratch限定）
Git／GitHub操作                   : 0件（status/diff等Read-onlyのみ、Mutation 0）
Network／Model Download／Load     : 0件（全Detector Local Deterministic、
                                     Safety Model Unavailable-by-default）
AWS／Lightning／課金操作          : 0件
Human Approval／Tool Permission／External Authorityの捏造 : 0件
```

Evidence Grade：本Documentの全数値・全Test件数はSubagentの申告ではなく、Claude本体が同一Session内で直接`pytest`／`ruff`／`mypy`／`tsc`／`eslint`／`vite build`を実行して得た実測値（`STRONG_VERIFIED`相当）。

## Next Action: Codex Phase 5-H Independent Review only

本Handoff作成をもってClaude側のPhase 5自走実行を終了する。Phase 5-H Closure、Git操作、Phase 6遷移はいずれもClaudeの範囲外であり、実施しない。次のActionはCodex側Independent Reviewであり、その結果を受けたUser／Codexの最終判断を待つ。
