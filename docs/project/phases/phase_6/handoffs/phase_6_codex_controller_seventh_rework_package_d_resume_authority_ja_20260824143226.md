# Phase 6 Seventh Rework — Package D差分再開Authority

```yaml
document_id: phase_6_codex_controller_seventh_rework_package_d_resume_authority
status: exact_resume_authority_active
phase: phase_6
rework: seventh_rework_user_ui_runtime_model_semantic_enforcement
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-24 14:32:26 JST
resume_from: package_d_current_partial
completed_packages_reuse: [package_a, package_b, package_c]
continue_packages: [package_d, package_e, package_f, package_g]
phase_closure_authority: false
git_mutation_authority: false
```

## 1. Controller Decision

P6-RW7-INC-001として、Frontend検証Commandの誤ったWorkdirによりnpmがAuthorized Root外の
`/Users/Nazuna Research/.npm/_logs`へError Logを書こうとした事実を受理する。

```text
Root-outside Write Attempt : 1
Persistent Write           : Tool出力上は不成立
Root-outside Inspection    : 0
Irreversible Mutation      : 0 known
Secret／Privacy Contact    : 0 known
Product Source Impact      : 0
Disposition                : RECORDED／STOPPED_SAFE／NON-BLOCKING FOR RESUME
```

Incidentを無かったことにせず、Current Cycleの`P6-RW7-REG-004`は「Root外Action 0」ではなく
`historical_nonconformance_recorded`として扱う。Root外を追加調査、削除、修復してはならない。

Product実装を巻き戻す理由はない。Package A〜CおよびPackage DのBackend focused 63 PASS／Targeted
Mypy 14 files PASSを保持し、Package D Current Partialから差分再開する。

## 2. Mandatory Resume Reading

1. `docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_d_root_outside_npm_log_attempt_stopped_safe_ja_20260824143020.md`
2. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_seventh_rework_stopped_safe_return_ja_20260824143020.md`
3. 本Authority。
4. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_seventh_rework_exact_handoff_ja_20260824134921.md`の§3〜8。

## 3. Exact Resume Boundary

1. Package A〜Cを再実装しない。
2. Package D Current Partialを直接照合し、Latest Frontend Validationから再開する。
3. Package D完了Recoveryを作成後、停止せずPackage E〜Gへ連結する。
4. 元HandoffのAcceptance／Boundary／True Stop Contractは、本書で訂正したIncident分類以外すべて維持する。

## 4. Frontend Command Safety

Frontend Commandは必ず次の条件で実行する。

```text
workdir:
  <Authorized Root>/frontend

NPM_CONFIG_CACHE:
  <Authorized Root>/.venv/.t/phase_6_seventh_rework_20260824135445/npm_cache

TMPDIR:
  <Authorized Root>/.venv/.t/phase_6_seventh_rework_20260824135445/tmp
```

必要DirectoryはProject内に作成する。`~/.npm`、User Home、`/dev/null`、Root外Temporaryを参照先／
書込先に使わない。Command前に`pwd`をExact Frontend Pathと比較する。

## 5. Required Evidence Correction

Package D RecoveryおよびFinal Returnでは、次を正確に記録する。

```text
Seventh Rework cumulative Root-outside Attempt: 1（P6-RW7-INC-001）
Resume Cycle Root-outside Action: 実測値
Persistent Root-outside Artifact: Tool出力上0、外部Inspection未実施
P6-RW7-REG-004: HISTORICAL_NONCONFORMANCE_RECORDED、0 Claim禁止
```

このProcess Incidentだけを理由にProduct Acceptance IDを捏造してFAIL/PASSへ変えず、Product実装と
Process Evidenceを分離する。

## 6. Execution Order

1. Package D Latest Frontend Typecheck／Test／Lint。
2. Package D Backend／Frontend差分を照合し、必要な修正とPackage D Recovery。
3. Package E Judge／Repair／Semantic ENFORCE。
4. Package F Qwen／DeepSeek Real Runtime。
5. Package G Integrated Verification／Direct Return。

真のStop Condition以外で進捗報告を理由に停止しない。Phase 6 Closure、Phase 7、Roadmap、Git、Networkへ
進まない。
