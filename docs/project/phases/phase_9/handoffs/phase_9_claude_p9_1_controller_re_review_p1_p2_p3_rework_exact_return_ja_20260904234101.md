# Phase 9-1 Judge／Governance — Controller再Review(22:41版)対応 Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../history/operations/phase_9_1_judge_governance_controller_re_review_ja_20260904224150.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-04 23:41:01 JST
```

## 1. Maximum Claim

`P9_1_CONTROLLER_RE_REVIEW_P1_P2_REWORK_COMPLETE_P3_PARTIAL_EVIDENCE_ONLY`

**主張しないこと(明示的除外)**:
- Gemmaが実機ENFORCE Golden Path(ACCEPT／Repair→Rejudge→改善回答採用)で成立したとは主張しない。今回の実機Evidenceは「Main+Gemma同時LoadはSelene同様のNative Crashを起こさない(有界条件)」および「Gemma自身にevidence_refs JSON閉じ括弧欠落という別の再現性ある欠陥がある」ことのみを示す。
- Seleneの延期(先送り)は成立していない。User承認済みの延期条件(「Gemmaが正常に使え、後工程に支障がなければ」)は今回も未成立。
- Phase Closureは主張しない。次Phaseへも進まない。
- 上書きされた旧Handoff(`..._20260904221547.md`)の復旧、phase_index_ja.md直接編集の訂正は、User「放置でいい」指示によりいずれも実施していない(今回のTaskとは別の既決事項として維持)。

## 2. 対象

[Controller再Review(2026-09-04 22:41:50 JST)](../history/operations/phase_9_1_judge_governance_controller_re_review_ja_20260904224150.md)のP1(§2)／P2(§3)／P3(§4)、3項目。

## 3. Files Changed

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/bootstrap/repair_live_integration.py` | P1修正。新規`_RejudgePlan`/`_plan_rejudge()`を追加し、Rejudgeの`max_new_tokens`計画をCancellation有無で単一化。Cancellation分岐・非Cancellation分岐の両方が同じ`rejudge_plan.max_new_tokens`を参照するよう書き換え。計画が成立しない場合(残Token不足、または入力Context不足)は新規Typed Reason `repair_rejudge_budget_insufficient`で呼出し前に返す。`ThinkingMode`の新規Import。 |
| `tests/unit/bootstrap/test_repair_live_integration.py` | P1 Test。新規Fixture `_UsageScriptedRepairService`(段階別Completion Tokens指定可)、`_criterion()`Helper追加。既存Test `test_budget_exhausted_by_rejudge_tokens_blocks_persistence_after_the_second_call`を`test_budget_too_tight_for_the_rejudge_plan_is_rejected_before_the_call_is_ever_made`へ書き換え(新挙動に合わせ、呼出し前Rejectを検証)。新規Test 9件追加(`_plan_rejudge`直接Test 5件、`attempt_live_repair`経由End-to-End Test 3件、AFTER-call Overspend残存確認Test 1件)。 |
| `tests/unit/bootstrap/test_judge_repair_rejudge_normal_enforce_save_path.py`(新規) | P2 Test。実Production `ConversationGenerationService`+`PersistentConversationService`+実`build_judge_completion_hook`をFixture Modelで結合し、通常ENFORCE経路(Conversation→Hook→Main起点Repair→同条件Rejudge→同一Turn保存)を検証。2 Test(成功時同一Turn保存、失敗時旧回答非保存)。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py`(新規) | P3実機Test。Main(Qwen, context=16384)+Gemma(context=8192)同時Load下で有界1 Criterionの実Dispatchを行い、Native Crash非再現を検証。1 Test(現在1 Skipped、理由は下記実Evidence参照)。 |
| `docs/project/shared/history/unresolved_work/phase_9_1_gemma_concurrent_load_no_crash_and_evidence_refs_json_defect_snapshot_ja_20260904233724.md`(新規) | P3実機Evidence記録。UF-P9-010提案(Gemma `evidence_refs` JSON欠落)、Selene延期条件未成立の確認。 |

Scratchpad(Repository外、Task所有隔離Process、Git対象外):
`wu03_gemma_repro/repro1_main_gemma_concurrent_bounded.py`、`repro2_raw_content_diagnostic.py`、`repro3_raw_content_accept_case.py`、`run1.log`、`run2.log`、`run_diagnostic.log`、`run_accept_case.log`。

## 4. Files Deliberately Not Changed

- `src/margpa_runtime_llm/bootstrap/judge_live_integration.py` — 精読したが未編集。IR-02修正済みの`rejudge_criteria`/`persist_accepted_attempt`貫通配線は既に正しく、P1/P2いずれもこのFileへの変更を要さなかった(P1はRepair内部のPlanning、P2は既存配線の未Test状態が欠陥だった)。
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py` — 精読したが未編集。P2で新規結合Testを追加した結果、既存の同一Turn保存経路(`_completed_event()`)自体は正しく機能していることを確認した(欠陥はTest不在であり、実装ではなかった)。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md` — Stable文書のため直接編集していない。UF-P9-010提案は新規History Snapshotへ記録した。
- `docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない(User訂正済みRuleに従う)。
- `config/profiles/local_macos_arm64.toml` — 今回未編集(WU-01訂正は前Round既済み、今回変更なし)。
- Frontend一式(`frontend/`) — 今回未編集。前Round(WU-05)からの変更なし。
- `git diff --stat`確認: 上記Filesおよび前Round以前からの既存未commit差分(104件、内訳は前Round Returnと同一Baseline)以外に、新規のUnintended変更は発生していない。

## 5. Real Evidence

### 5.1 P1 — Rejudge予算整合(§6詳細検証と併読)

Controllerの合成Case(32 Criteria、候補Usage 5、Cancellation有無で400/4800 vs 400/200)は、修正後は次のとおり解消する:
- Cancellation有無に関わらず、`_plan_rejudge()`が同一Planを1回だけ計算し、両分岐が同じ値を参照する(構造上、`_plan_rejudge()`自体がCancellation引数を持たないため、両分岐が異なる値を送ることは設計上不可能)。実機End-to-Endでも確認: `test_rejudge_max_new_tokens_requested_is_identical_with_and_without_a_cancellation_token`が両ケースで`max_new_tokens=750`(5 Criteria)の一致を実測。
- 32 Criteria(Controller合成Caseと同数)では、`desired=4800`が`remaining`(候補Usage差引後の残Token)を超えるため、Rejudge呼出し**前**に`repair_rejudge_budget_insufficient`でTyped Reject。実際にRejudge Call自体が発生しないことを`len(service.calls) == 1`で実測確認(`test_a_large_criterion_count_never_reaches_the_rejudge_call_end_to_end`)。
- 通常件数(5 Criteria)では、`LIVE_REPAIR_BUDGET`(2000 Token)内で計画どおり`750 Token`(150×5)のRejudgeが成立し、Repair成立まで到達することを実機的な擬似End-to-Endで確認(`test_a_normal_criterion_count_rejudge_succeeds_end_to_end_within_the_default_live_budget`)。
- 入力Context制約: Model側`loaded_context_size`とPrompt Token数からの残余がPlanを下回る場合も呼出し前Rejectとなることを`test_plan_rejudge_is_bounded_by_the_models_own_input_context`で確認。`runtime_info`/`count_chat_prompt_tokens`未提供のFixture(既存の`_FakeRepairService`)ではこのBoundが安全にSkipされることも確認(`test_plan_rejudge_skips_the_context_bound_when_the_service_exposes_no_runtime_info`)。
- 予算の無断拡大・Criterion脱落による成功化がないことの直接検証: `test_plan_rejudge_never_returns_a_plan_smaller_than_the_full_calibrated_allowance`(残余が必要量の1 Token不足の場合でもPlanはNoneであり、縮小Planでの成功化はしない)。

### 5.2 P2 — 通常ENFORCE経路の保存Test(Fixture Model)

`test_judge_repair_rejudge_normal_enforce_save_path.py`の2 Testとも実Production Composition(`ConversationGenerationService`→`PersistentConversationService.generate_turn()`→実`judge_completion_hook`→実`attempt_live_repair()`)をFixture Modelで駆動し、Executor直接呼出しを代用していない。

- 成功時: 誤答Candidate("Tenon")がRepairされ、Rejudgeで同一Frozen Criterion(`semantic.argd.evidence.1`)がPassし、`PersistentConversationService`が保存した**唯一のTurn**(`origin=NORMAL`、新規REPAIR Turnではない)のAssistant Messageが修復後回答("Paris")と一致することを実測。旧回答("Tenon")が含まれないことも確認。
- 失敗時: RejudgeでもDeviationが残る(修復失敗)Caseでは、同じ唯一のTurnに旧回答("Tenon")が保存されないことを確認(Safe Fallbackへ収束)。重複Turnも発生しない。

### 5.3 P3 — Gemma実機成立とSelene先送り条件

Task所有隔離Process、4回の有界実機実行(`wu03_gemma_repro/`配下、Logは前掲):

- **Main+Gemma同時Load、Native Crash非再現**(2回連続実行、有界1 Criterion): `RuntimeError: llama_decode returned -3`等の未捕捉例外は一度も発生せず、毎回1.8〜1.9秒で正常にTyped Responseが返った。Seleneの同型構成(ただし32 Criteria Batch)で確定しているNative Crashとは異なる結果。ただし本条件はCriterion数がSeleneのCrash確認時(32件)と異なるため、「GemmaはCrashしない」という一般化はしない(有界条件限定の結果として記録)。
- **Gemma自身のJSON整形欠陥、3/3再現**: `evidence_refs`配列に非空の引用文字列を含めると、Gemmaは一貫して閉じ`]`を欠落させる(誤答Case・正答Case両方で同一Pattern)。`finish_reason=stop`でありToken Truncationではない。IR-01修正により正しくTyped Failure(`malformed_output`)へFail-closedされ、誤った回答が表示されることはない(安全側の挙動)。
- 上記2点により、pytestとして書いた`test_real_local_main_gemma_concurrent_dispatch_smoke.py`は「Crash非再現」をHard Assertし、「JSON欠陥によるprovider_state非ACTIVE」を既知の再現性あるOpen Findingとして明示的な理由付きでSkipする(汎用的な「実Model非決定性」Skipとは区別し、追跡可能な理由文言にした)。実行結果: 1 Skipped(意図どおり)。
- 結論: **Gemma正常に使えるの条件は今回も未成立**。Seleneの延期条件(User承認済み)を満たさないため、Seleneは延期せず現状維持する。詳細は[新規History Snapshot](../../shared/history/unresolved_work/phase_9_1_gemma_concurrent_load_no_crash_and_evidence_refs_json_defect_snapshot_ja_20260904233724.md)。
- 後工程がSelene固有機能に依存しないことの照合(Static、必要箇所のみ): `dedicated_role_adapters.py`の`SeleneRoleAdapter`はDocstringで明示的に「Gemmaへ`provider_label`のみ変えて無変更で再利用」と規定されており、`judge_live_integration.py`の`_run_selene_dispatch`はDuck Typing(`.semantic_evaluator`属性の有無)でDispatchするためProvider非依存。Source Readで確認済み、追加の新規実機実行はしていない(有界化のため)。

## 6. Focused／Static Verification

- Backend Full Suite: `uv run pytest -q` → **2298 passed, 25 deselected (76.84s)**。model_smoke含む全体で新規12件Test追加(P1 9件 + P2 2件 + P3 1件)。model_smoke除外時のCollect数増加分。
- Backend Ruff: `uv run ruff check .` → **All checks passed**。
- Backend Mypy: `uv run mypy src` → **1 error, 1 file**(`judge_live_integration.py:622`、`"None" not callable`)。このFileは今回未編集。この1件は今回のP1/P2/P3変更前から存在する既存State(前回Return記載の「43 errors/4 files」Baselineとは差異があるが、その差分の原因調査は今回のScope外であり、今回新規に発生したErrorではないことのみ確認した——今回変更した3 Files(`repair_live_integration.py`及び新規2 Test Files)は`uv run mypy`個別実行で**Success: no issues found**)。
- Frontend: 今回未変更のため再実行していない(前Round Return記載: npm test 327 passed / typecheck・lint clean / buildは前Round時点の結果のまま、今回のRe-runなし)。
- 実機Model Smoke(P3新規File): `uv run pytest tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py -m model_smoke` → **1 skipped**(上記5.3参照、意図どおりの安全側挙動)。既存の他Model Smoke Testは今回再実行していない(前Round WU-03成立分は変更なし、再実行不要と判断)。

## 7. Internal Review(2回、観点の異なる完全別Pass)

### Review A — Correctness／Contract適合(実装内容そのもの)

- [OK] P1: `_plan_rejudge()`は同一関数がCancellation有無双方から呼ばれる構造であり、「同じ計画を使う」がTest上の確認だけでなく構造的に保証されている(関数SignatureにCancellation引数が存在しない)。
- [OK] P1: 予算超過時は呼出し前Reject、既存の`_budget_overspent_after_call`(呼出し後Check)は温存し、実際にPlanを超えてModelがToken消費した場合(実Model異常)への防御は別のTestで確認済み(`test_a_rejudge_that_overruns_its_own_affordable_plan_is_still_rejected_after_the_call`)。
- [OK] P2: 実装側の変更なし、既存の同一Turn保存経路が正しく機能していたことをTest追加のみで実証。IR-R2-02の指摘は「Test不在」であり、実装欠陥ではなかったという理解で相違ないことをSourceの`_completed_event()`/`_generate_pending_turn()`の実装で確認済み。
- [PARTIAL] P3: Native Crash非再現はHard Evidence(4回実測)。ただし「Gemma正常に使える」の完全立証には至っていない(evidence_refs欠陥)——この限界を最大Claim・実機Evidence双方で明示しており、過大表記はしていない。
- [OK] 既存Test 30件(`test_repair_live_integration.py`)+96件(`test_judge_live_integration*.py`)が全PASSし、既存Regressionなし。

### Review B — Process／Handoff適合(手続き面)

- [OK] Git: `git status`/`git diff --stat`のRead-only確認のみ。Add/Commit/Push等の変更操作は一切実行していない。
- [OK] Append-only: 新規File 3件(P2 Test、P3 Test、P3 History Snapshot)はいずれも未使用のPathへの新規作成。既存Handoff/Return/History Fileの上書きはしていない。
- [OK] Stable文書境界: `current_unresolved_findings_registry_ja.md`(Stable)は編集せず、新規UF-P9-010提案は`history/unresolved_work/`配下の新規Snapshotへ記録。
- [OK] phase_index_ja.md: 直接編集していない(前Round訂正済みRuleに従う)。
- [FIXED-DURING-REVIEW] `tests/unit/bootstrap/test_repair_live_integration.py`の新規Test構築中に`GenerationResult.runtime_info`必須Field欠落によるPydantic ValidationErrorを発見・修正(P2側Fixtureの実装ミス、本番Code欠陥ではない)。診断Scriptで根本原因(`None`不可Field)を特定し、Fixtureへ実`ModelRuntimeReference`を設定して解消。
- [OK] Internal Review 2回のみ実施(本節)。3回目以降は実施していない。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **Selene**: 依然未解決。今回のTaskでは新規実機実行を行っていない(User承認の「最大3試行」は前Round(WU-01)で既に使用済みであり、今回はGemma側の有界実機実行(4回)のみを新規に実施した)。登録・再調査入口は前Round時点のまま維持する。
2. **Gemma**: 新規UF-P9-010(提案)——`evidence_refs`配列のJSON閉じ括弧欠落、3/3再現。本Task範囲外のため修正は行っていない。Registry本体への反映はCodex/User判断待ち。
3. **Mypy 1 error**(`judge_live_integration.py:622`): 今回未編集のFile。前回Return記載の「43 errors/4 files」Baselineとの差異理由は未調査(本Taskの直接Scope外)。
4. **Frontend再検証**: 今回変更なしのため未実施。次回Frontend変更を伴うTaskで再実行が必要。
5. **上書き旧Handoff・phase_index_ja.md直接編集の訂正**: User「放置でいい」により既決。今回のTaskでも変更していない。

## 9. Action Inventory

**実行した**:
- `repair_live_integration.py`のP1修正実装、関連Test 30件(既存21件+新規9件、1件書換え)の追加・実行・全PASS確認。
- P2新規結合Test File作成(2 Test、全PASS)。
- P3実機実行4回(Task所有隔離Process、Scratchpad)、実機pytest 1回(1 skipped)。
- P3新規History Snapshot 1件作成(UF-P9-010提案)。
- Backend Full Suite・Ruff・Mypy(src全体)の最終実行。
- 本Return Handoffの新規File作成。

**実行しなかった**:
- Frontend再検証(変更なしのため)。
- Selene側の新規実機実行(前Round予算を使い切っており、今回は対象外)。
- `current_unresolved_findings_registry_ja.md`本体への直接反映(Stable文書のため)。
- Mypy 1 errorの調査・修正(今回未編集Fileであり、Scope外と判断)。
- 上書き旧Handoff・phase_index_ja.mdの訂正(User既決事項)。
- Git Add/Commit/Push等の変更操作。

**Temporary Artifact／Active Process／Model Load**: 全実機Trial(4回)で都度`unload()`を確認し、Process終了時に残存Model Loadはない。Scratchpad配下のScript/Logはそのまま保持(User所有隔離Processの記録として)。稼働中のBackground Process・Server起動は行っていない。

## 10. Exact Next Action for Codex Controller

1. P1(`_plan_rejudge()`)の実装・Test(§3, §5.1, §7 Review A)を、Controller自身の合成Case(32 Criteria、候補Usage 5)で独立再現し、`repair_rejudge_budget_insufficient`が呼出し前に返ることを確認する。
2. P2の新規結合Test(`test_judge_repair_rejudge_normal_enforce_save_path.py`)を、ControllerがFixture ModelをMock差し替えするなどして、同一Turn保存経路が本当にExecutor直接呼出しの代用になっていないことを検証する。
3. P3のGemma実機Evidence(§5.3、`wu03_gemma_repro/`Log)を確認し、「Gemma正常に使える」は今回も未成立であること、Seleneの延期条件が満たされていないことに同意するか判断する。UF-P9-010提案のRegistry反映可否を判断する。
4. Mypy 1 error(`judge_live_integration.py:622`)の扱い(前回43件Baselineとの差異調査を別Taskとするか)を指示する。
5. 上記1-4を踏まえ、本Rework全体をACCEPTするか、追加のCHANGES REQUIREDを発行するか判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作は行わない。Codex Controller Independent Reviewを待つ。
