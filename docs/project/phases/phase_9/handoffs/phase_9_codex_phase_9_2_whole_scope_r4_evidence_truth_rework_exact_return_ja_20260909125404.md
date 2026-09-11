# Phase 9-2 Whole Scope R4 Evidence Truth Rework Exact Return

作成時刻: 2026-09-09 12:54:04 JST  
From: 設計者兼実装者役（Task `01a03b6c-2a68-7881-99bc-c788a600f632`）  
To: プロジェクト責任者兼設計統括者役（Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`）

## 1. Return Claim

`P9_2_WHOLE_SCOPE_R4_EVIDENCE_TRUTH_REWORK_CANDIDATE_FOR_CONTROLLER_REREVIEW`

これは`IR-P9-2-WHOLE-R4-01`〜`03`のBounded Rework完了候補であり、Phase 9-2 Complete／Closure、Real Model／Browser／User Manual成立、Phase 9-3／10、Git Authorityを意味しない。

## 2. Finding Disposition and Raw Probe

| Finding | Before raw | After raw | Disposition |
|---|---|---|---|
| R4-01 | negative answer=`current_fact_used` | direct=`insufficient_evidence`; Top-level affirmative=`pass`, unrelated=`inconclusive`, negative=`inconclusive`; Restartもnegative=`inconclusive` | FIXED CANDIDATE |
| R4-02 | identical config=`true`; main-active Main Call=`true`; manual-url Main Call=`false` | 宣言Config差=`main`; manual Main Call=`false`; Guard差=`guard`; identical-config replicaはInvocation／Trace／Disposition一致 | FIXED CANDIDATE |
| R4-03 | called=`judge,definition_set,repair`; main-governance=`false`; propagation=`judge_and_main` | 同Run requester=`judge`; Repair-only requester=`None`／Call=`false`／Adopted=`false`; Main Governance=`main_governance`; both=`judge_and_main` | FIXED CANDIDATE |

## 3. Implementation Summary

- Freshness PASSを明示Adoption Evidence必須へ変更し、否定／引用／無関係／空を非PASS化。Case Packをrev-3へ更新。
- Manual URL／Guard short-circuit／Freshness negative／Repair requestをPlan Digestへ入る明示Component modeとして表現し、BehaviorのVariant ID分岐を除去。
- 同一Config replication controlでVariant名だけでは結果が変わらないことをTop-level確認。
- RepairをRequester Actor実行後にだけ起動する二段階Fixture実行へ変更。Judge／Main Governance／Both／Noneを実Called Actorから導出。
- Raw Invocation、Trace、Semantic Evidence、Metric、Governance propagationの矛盾をTyped reject。
- Belief Revision／False ImprovementはRequesterあり・Repairだけ差分のVariant pairへ変更。

## 4. Sabotage-regression

- R4-01: Adoption guard除去で否定文が`current_fact_used`へ戻りFAIL。
- R4-02: Manual URL modeをMain activeへ戻すと実差0をComparison verifierが検出し、HTTP 409／Top-level FAIL。
- R4-03: Judge-only originを`judge_and_main`へ戻すとRequester Top-level AssertでFAIL。
- 3件とも直後に完全復元し、最終Phase scopeでPASSを確認した。

## 5. Validation

- Phase 9-2 Backend scope: `283 passed in 4.45s`
- Frontend Full: `34 files / 339 tests` PASS
- Frontend typecheck／lint／build: PASS、60 modules transformed
- Changed Python: Ruff PASS、Mypy `8 source files / 0 issues`
- `git diff --check`: PASS
- Real Model／Browser／User Manual: NOT RUN
- 非Model Backend Full全体: 本Bounded R4ではNOT RUN

詳細なBefore／After、Evidence Pointer、Changed Paths、Restart Read、Self Review、Open Boundary:

- `docs/project/phases/phase_9/history/index/phase_9_2_whole_scope_r4_evidence_truth_rework_recovery_ja_20260909125404.md`

## 6. Exact Next Action

Controller Task `019f739b-8a21-7592-95cc-c83c9c08e5f6`が`IR-P9-2-WHOLE-R4-01`〜`03`のみをIndependent Re-reviewする。本TaskはDirect Return後に停止し、追加修正、Phase 9-2完了承認、User Manual、Phase 9-3／10、Closure、Gitへ進まない。
