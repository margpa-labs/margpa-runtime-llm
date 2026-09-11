# Phase 9-2 Whole Scope Review 3 残差 — Evidence Truth Rework Handoff

```yaml
document_type: exact_rework_handoff
document_state: active
created_at: 2026-09-09 12:22:44 JST
from_role: project_controller_design_governor
to_role: designer_implementer
base_return: phase_9_codex_phase_9_2_whole_scope_r3_acceptance_truth_rework_exact_return_ja_20260909075520.md
review_result: changes_required
append_only: true
```

<intent>

Review 3のR3-01〜03は大部分が成立したが、Controller再Reviewで、比較Artifactの真実性を壊す残差3件を実行Probeにより確認した。既存66件のFocused Testが全PASSしても再現するため、Test成功数ではClosureできない。

本Reworkは、Freshnessの否定文False PASS、宣言Config外のHidden Variant挙動、およびRepair起点の虚偽記録だけを局所修正する。Phase 9-2の既成立範囲はRollbackしない。

</intent>

<confirmed_findings>

## IR-P9-2-WHOLE-R4-01 — BLOCKER: Current Valueの否定的言及がPASSする

`classify_freshness_answer()`は、Current Valueが回答内へ部分文字列として現れただけで`CURRENT_FACT_USED`を返す。

Controller Probe:

```text
current_source_value = "000"
answer = "000 is not the current value; 765 is current."
actual = current_fact_used
```

これはCurrent Sourceを採用していない明示的な否定回答をPASSにするため、R3-01のAcceptance Truthは未完了である。

要求:

- Current Valueの単なる出現、引用、否定、訂正文中の旧値を`CURRENT_FACT_USED`にしない。
- Current Valueを回答のCurrent Factとして採用したことが確認できるEvidenceだけをPASSにする。
- 無関係、空、曖昧、否定、Evidence不足はPASSにしない。
- Updated／Deleted、Historical Citation改変最優先、Production未観測`None`の既存境界を維持する。
- UnitだけでなくPlan→Run→Raw Evidence→Comparison→Restart Readで、肯定、無関係、否定の3経路をHard Assertする。

Evidence: `freshness.py:62`、`test_experiment_routes.py:1768`。

## IR-P9-2-WHOLE-R4-02 — MAJOR: 同一ConfigがVariant名だけで別挙動になる

`fixture-main-active`と`fixture-manual-url-fail-closed`はComponent設定が完全一致する。しかしAdapterが`variant_id`文字列を分岐条件にし、前者ではMain Call 1、後者ではMain Call 0となる。さらに後者を`baseline-all-off`からMainだけを変えたRegressionとして永続化している。

Controller Probe:

```text
identical_components = true
fixture-main-active.main.called = true
fixture-manual-url-fail-closed.main.called = false
```

同じCase、同じ宣言Component Configで異なる結果が出るHidden Factorであり、単一要因比較のClaimを成立させない。

要求:

- Manual URL Fail-closed条件を、Variant名ではなくPlan Digestへ入る明示的なCase／Component Selection／Scenario Contractとして表現する。
- 同一Config＋同一Caseは、Variant IDだけでInvocation／Trace／Dispositionを変えない。
- Manual URLの比較関係は実際の宣言差を再計算できる形にする。Hidden FactorをMainの効果として表示しない。
- Guard short-circuitもVariant ID分岐を廃し、明示Guard条件からCall 0を導出する。Main-active対Guard-enforceの真の単一要因差を比較Artifactへ記録するか、単一要因Claimをしない理由を構造化して残す。
- Raw InvocationとTraceは、同じ実行判断から導出し、片方だけ手作りしない。

Evidence: `semantic_fixture_adapter.py:84-115,171-204,207-250`、`experiment_routes.py:84-99,119,167付近`、`test_experiment_routes.py:1991-1998,2052-2088`。

## IR-P9-2-WHOLE-R4-03 — MAJOR: Repair起点とRepair実行を捏造できる

`_governance_for()`はRepairがCalledなら、実際のRequesterを見ず常に`judge_and_main`を記録する。現`fixture-definition-manual-with-repair`はJudge、Definition、RepairだけがCalledでMain GovernanceはCall 0だが、保存Evidenceは`repair_propagation=judge_and_main`である。

Controller Probe:

```text
called = [judge, definition_set, repair]
main_governance.called = false
actual repair_propagation = judge_and_main
```

また`fixture-repair-enforce`はRequesterなしでRepairをCallし、その事実だけから`repair_adopted=True`、Belief Revision／False Improvement結果を作る。Repair ModeだけではRepair要求は発生しないというRuntime契約と一致しない。

要求:

- `repair_requested_by`／`repair_propagation`を実際にCalledかつRequestを発したActorから導出する。
- Judgeのみなら`judge`、Main Governanceのみなら`main_governance`、両方なら`judge_and_main`。存在しないRequesterを記録しない。
- RepairはMode ENFORCEだけで起動・採用扱いにせず、明示Requesterと適格性があるFixture経路だけでCalled／Adoptedとする。
- Belief Revision／False Improvement比較は、Requesterを持つBaselineとRepair差だけのVariantなど、宣言と実行が一致する構成へ直す。
- Top-level ComparisonとRestart Readで、Requester、Repair Call、Adoption、Component Invocationの保存整合をHard Assertする。

Evidence: `semantic_fixture_adapter.py:316-321`、`experiment_routes.py:138-145,1109-1137`、`test_experiment_routes.py:1851-1859,1912-1924,2021-2033`。

</confirmed_findings>

<execution_contract>

```json
{
  "schema_version": "development_agent_handoff_v1",
  "message_type": "rework",
  "from_role": "project_controller_design_governor",
  "to_role": "designer_implementer",
  "task_identity": "01a03b6c-2a68-7881-99bc-c788a600f632",
  "objective": "Phase 9-2 Review 3残差3件を局所修正し、Top-level EvidenceとComparisonの真実性を成立させる",
  "scope": {
    "in_scope": [
      "IR-P9-2-WHOLE-R4-01",
      "IR-P9-2-WHOLE-R4-02",
      "IR-P9-2-WHOLE-R4-03",
      "直接必要なFixture Adapter、Case/Variant Contract、Evaluator、Comparison、回帰Test"
    ],
    "out_of_scope": [
      "Real Model",
      "Browser/User Manual",
      "Phase 9-3",
      "Phase 10",
      "Data Controls",
      "既成立範囲の再設計",
      "軽微な非Blocker"
    ]
  },
  "authority": {
    "read": ["repository root以下"],
    "write": ["in_scope source/tests", "新規Exact Return", "新規Recovery"],
    "git": "deny",
    "external": "deny"
  },
  "required_actions": [
    "3 Controller Probeを修正前再現として固定する",
    "R4-01からR4-03の順で修正する",
    "Plan→Run→Raw Evidence→Comparison→Restart ReadをHard Assertする",
    "各主要OracleをSabotageして検出力を確認後に完全復元する",
    "Phase 9-2 Backend範囲とFrontend影響範囲を検証する",
    "Append-onlyでExact ReturnとRecoveryを新規作成する"
  ],
  "forbidden_actions": [
    "既存Handoff/Return/Recoveryの上書き",
    "Fixture結果をProduction/Real Model結果として表示",
    "未観測をFalse/0/PASSへ変換",
    "Variant IDだけをHidden Scenario Flagとして使用",
    "存在しないRepair Requesterの記録",
    "git add/commit/push/stash/clean",
    "Phase 9-2 Complete/Closureの自己承認",
    "中間報告"
  ],
  "acceptance_criteria": [
    "否定文Probeが非PASSで肯定Current FactだけがPASS",
    "同一Case/ConfigはVariant IDだけで実行結果が変わらない",
    "Manual URL/Guard Call 0条件が宣言済み要因から導出される",
    "Repair Requester/Call/Adoptionが実Componentと一致",
    "単一要因DeclarationがPlan内の実差とHidden Factorなしで一致",
    "既存66件を含む関連TestがPASSし新規False-success Oracleが追加される"
  ],
  "stop_conditions": [
    "Blockerまたは設計Authority拡張が必要",
    "指示間Conflict",
    "Resource Pressure",
    "対象外の大規模再設計が必要"
  ],
  "reporting": {
    "intermediate": "forbidden_except_user_interrupt_response",
    "final": "required",
    "destination": "project_controller_design_governor task 019f739b-8a21-7592-95cc-c83c9c08e5f6"
  },
  "resource_policy": {
    "real_model_runs": 0,
    "browser_runs": 0,
    "prioritize_blocker_major_only": true
  },
  "maximum_claim": "P9_2_WHOLE_SCOPE_R4_EVIDENCE_TRUTH_REWORK_CANDIDATE_FOR_CONTROLLER_REREVIEW",
  "artifacts": [
    "new exact return handoff",
    "new recovery index"
  ]
}
```

</execution_contract>

<return_contract>

返却時は3 Findingごとに、Before／After、変更File、Top-level Evidence、Sabotage結果、未解決境界を分離する。既存PASS数だけを修正根拠にせず、上記Controller Probeが修正後にどう変わったかを生値で示す。完了報告をControllerへ一度だけ送り、その後停止する。

</return_contract>
