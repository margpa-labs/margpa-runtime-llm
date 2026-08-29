# Phase 6 Remaining Rework — Package B Recovery

```yaml
document_id: phase_6_remaining_rework_package_b_semantic_criterion_compiler_20260826094401
status: package_complete_next_active
package: P6-RR-B
completed_wus: [P6-RR-B-WU-001, P6-RR-B-WU-002, P6-RR-B-WU-003, P6-RR-B-WU-004, P6-RR-B-WU-005]
created_at: 2026-08-26 09:44:01 JST
next_exact_work_unit: P6-RR-C-WU-001
```

## Result

- Provider-neutral `SemanticCriterion`、Stage／Method、Result、Typed Deferred Reason、Compile Finding、Batch Planを実装した。
- Trusted ARGD／DAGD Compilerは109 Descriptorを109 Criterionへ変換し、Unsupported 0。Source ID／Digest／Pointer／Text Digest／Instruction／Governance Point／Stage／Method／Severity／Action／Evidence Requirementを保持する。
- Compiler Outputは入力順序に依存しないCanonical順序とSHA-512 Digestを持つ。
- Batch PlannerはStage ApplicabilityとBudgetを分離し、選択外CriterionをCriterion単位の`budget_exhausted`として復元可能にする。Unknown Mapping／Digest欠落はPassにしない。

## Validation／Inventory

```text
Focused Pytest: 8 passed
Focused Mypy : PASS / 25 source files
Focused Ruff : PASS
Compiler output: 109 criteria / 0 unsupported
open_critical: 0
open_major: P6-GOV-015（Runtime Wiring未完、次Package対象）
root_outside/provider_memory/runtime_data/git/network/model_mutation: 0/0/0/0/0/0
active_process: 0
loaded_model: none
task_owned_temp: .venv/.t/phase_6_remaining_rework_claude_20260826093407/
claims_not_made: Runtime semantic evaluation、Phase 6 Closure、Real Model PASS
```

Changed PathsはPackage A記載の6 Source／Test群。ArtifactはCanonical Definitionを変更せずRead-only。Recovery DocsはAppend-only新規作成。

`next_exact_work_unit: P6-RR-C-WU-001`
