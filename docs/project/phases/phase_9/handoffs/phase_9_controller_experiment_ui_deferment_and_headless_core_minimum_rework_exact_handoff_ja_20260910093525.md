# Phase 9-2 Experiment UI延期／Headless Core維持 最小Rework Exact Handoff

```yaml
document_id: phase_9_controller_experiment_ui_deferment_and_headless_core_minimum_rework_exact_handoff_20260910093525
document_type: exact_rework_handoff
document_state: active
phase: phase_9
program: phase_9_2
created_at: 2026-09-10 09:35:25 JST
from_role: project_controller_design_governor
to_role: claude_designer_implementer
decision_authority: user
priority: quota_bounded_minimum
claude_weekly_quota_observed_by_user: approximately_3_percent_remaining
intermediate_reporting: forbidden_except_direct_user_interruption_response
new_subtask_or_delegation: forbidden
real_model_runs: 0
browser_runs: 0
git_authority: deny
append_only: true
```

<intent>

User Mac実画面テストで、現行Minimal Experiment UIのCancel導線、Plan Reset、Details表示およびState明示が通常利用に十分でないことが確認された。

ユーザーは、現Experiment UIをMVP必須機能とせず、Phase 11以降または優先度を上げた時点まで延期する方針を承認した。一方、Phase 9-2のHeadless Experiment CoreはPhase 9-3のCompaction前後比較および後続研究に再利用できるため維持する。

本Reworkは、現Experiment UIの修復ではない。通常UIからの入口だけを最小変更で外し、Backend Core／API／Evidence／Test AssetをRollbackしないことが目的である。

</intent>

<required_sources>

1. `docs/project/shared/conventions/documentation_rules_ja.md`
2. `docs/project/phases/phase_9/history/operations/phase_9_2_user_mac_original_manual_checklist_partial_result_and_strategy_change_input_ja_20260910093525.md`
3. `docs/project/shared/planned_work/phase_11_plus_experiment_workspace_ui_deferment_and_headless_core_preservation_reservation_ja_20260910093525.md`
4. `docs/project/phases/phase_9/handoffs/phase_9_controller_phase_9_2_whole_scope_independent_review_3_r4_acceptance_result_ja_20260909130912.md`
5. 現行`frontend/src/App.tsx`、`frontend/src/components/TopBar.tsx`、関連Frontend Test。

</required_sources>

<work_units>

## WU-01 — 通常UIからExperiment入口を非表示化

次のProduct Behaviorにする。

- 通常起動したAppのTop Barに「実験（Phase 9-2）」Buttonを表示しない。
- 通常UI操作から`ExperimentPanel`をOpenできない。
- テーマ／言語／Settings／Chatその他のTop Bar／App機能は維持する。
- `ExperimentPanel.tsx`とその専用Testは削除しない。将来Workspace設計のSourceとして保持する。

実装は、例えばTopBarからExperiment Button／Callbackを外し、Appの通常CompositionからPanelを開くState／Mountを外する最小変更でよい。使われないimport／propは正直に除去する。

## WU-02 — Headless Coreの非変更を証明

今回は次を変更しない。

- `src/margpa_runtime_llm/modules/experiment/`
- `src/margpa_runtime_llm/adapters/experiment/`
- `src/margpa_runtime_llm/web/experiment_routes.py`
- `src/margpa_runtime_llm/bootstrap/experiment_*`
- Experiment Store／API／Worker／Lease／Identity／Trace／Comparison／Case／Evidence契約。
- `frontend/src/components/ExperimentPanel.tsx`のCancel／Reset／Details／Polling内部。

現Working Treeに存在するPhase 9-2 R1〜R4の既存Dirty Diffはユーザー／先行Taskの作業として保存し、Rollback、Clean、Formatによる広範囲書換えまたは意味変更を行わない。

## WU-03 — Focused Verification

最小限、次を機械確認する。

1. Top Barに`experiment-toggle`が表示されない。
2. Appの通常RenderからExperiment Panelを開くActionがない。
3. Theme／Language／Settings／Chatの関連する既存Focused Testが維持される。
4. TypeScript TypecheckがPASSする。

利用可能量が残る場合のみ、Frontend Lint、Frontend Full Test、Buildの順で追加する。Backend Full Suite、Real Model、BrowserおよびManual UI Testは実行しない。

## WU-04 — Append-only Return／Recovery

実施結果を新規PathのExact ReturnとRecoveryへ記録する。既存Handoff／Return／Recoveryは上書きしない。

可能なMaximum Claimは次以下とする。

```text
P9_2_EXPERIMENT_UI_ENTRY_HIDDEN_HEADLESS_CORE_PRESERVED_CANDIDATE_FOR_CONTROLLER_REVIEW
```

</work_units>

<execution_contract>

```json
{
  "schema_version": "development_agent_handoff_v1",
  "message_type": "bounded_rework",
  "from_role": "project_controller_design_governor",
  "to_role": "claude_designer_implementer",
  "objective": "Hide the current Phase 9-2 Experiment entry from the normal UI while preserving the accepted headless Experiment Core without modification.",
  "priority_order": [
    "read required sources and inspect only the directly affected frontend composition",
    "remove the normal UI entry and open path",
    "add or update focused frontend regression tests",
    "run focused tests and TypeScript typecheck",
    "write a new append-only Exact Return and Recovery",
    "only if quota remains, run lint, frontend full tests, and build"
  ],
  "scope": {
    "in_scope": [
      "frontend/src/App.tsx",
      "frontend/src/components/TopBar.tsx",
      "directly corresponding frontend tests",
      "new append-only Exact Return",
      "new append-only Recovery"
    ],
    "out_of_scope": [
      "ExperimentPanel internal UI repair",
      "Experiment backend core, API, store, worker, lease, identity, trace, comparison, case, and evidence",
      "new CLI or backend feature gate",
      "Phase 9-3 or Phase 10",
      "Data Controls",
      "Roadmap, Phase Index, Registry, and Stable documentation",
      "unrelated dirty working-tree changes"
    ]
  },
  "authority": {
    "read": "project_root_only",
    "write": "listed_in_scope_paths_only",
    "git": "deny",
    "external": "deny",
    "real_model": "deny",
    "browser": "deny",
    "delegation": "deny"
  },
  "required_invariants": [
    "The experiment toggle is absent from the normal UI.",
    "The normal App composition cannot open ExperimentPanel.",
    "ExperimentPanel source and dedicated tests remain in the repository.",
    "No file under src/margpa_runtime_llm/modules/experiment or adapters/experiment is changed.",
    "No Experiment API, persistence, worker, lease, trace, comparison, case, or evidence contract is changed.",
    "Existing dirty changes are preserved and never rolled back or reformatted wholesale."
  ],
  "forbidden_actions": [
    "fixing cancel, reset, details, polling, or comparison UI",
    "deleting ExperimentPanel or backend Experiment code",
    "adding a new runtime or CLI feature flag in this round",
    "git add, commit, push, stash, clean, reset, checkout, or branch changes",
    "backend full suite, real model run, browser run, or user manual run",
    "Phase 9-2 Complete, Phase 9 Closure, Phase 9-3 start, or Phase 10 start claims",
    "creating a new task, subtask, subagent, or delegated review",
    "intermediate progress reports unless directly responding to a user interruption"
  ],
  "verification": {
    "mandatory": [
      "focused TopBar/App frontend tests",
      "frontend typecheck"
    ],
    "optional_if_quota_remains": [
      "frontend lint",
      "frontend full tests",
      "frontend build"
    ],
    "forbidden": [
      "backend full suite",
      "real model",
      "browser/manual UI"
    ]
  },
  "quota_stop_policy": {
    "remaining_weekly_quota_observed": "approximately_3_percent",
    "on_limit_warning": "stop immediately without broadening scope; report completed edits, completed verification, and exact unverified items",
    "partial_claim_required": true,
    "no_recovery_by_git_stash": true
  },
  "reporting": {
    "intermediate": "forbidden_except_direct_user_interruption_response",
    "final": "one_exact_return_to_controller_then_stop",
    "append_only": true
  }
}
```

</execution_contract>

<acceptance>

Minimum Acceptance:

- 通常UIにExperiment Buttonがない。
- 通常AppのState／Callback／MountからExperiment Panelを開く経路がない。
- Experiment Panel本体とBackend Coreは保持される。
- Focused TestとTypecheckがPASSする。
- 実施済みと未検証を分けたAppend-only Return／Recoveryが新規作成される。

利用可能量不足でMinimum Acceptanceへ到達できない場合は、失敗や未完了を隠さずPartial Returnで停止する。

</acceptance>

<stop_boundary>

Exact ReturnをControllerへ一度だけ返却した後、追加Rework、Independent Review、User Manual、Phase Completion、Git操作または次Phaseへ進まず停止する。

</stop_boundary>

