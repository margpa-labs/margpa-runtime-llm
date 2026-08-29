# Phase 6 Remaining Rework — Package 0 Entry／Baseline Recovery

```yaml
document_id: phase_6_remaining_rework_package_0_entry_baseline_recovery_20260826093853
status: package_complete_next_active
phase: phase_6
package: P6-RR-0
completed_wus:
  - P6-RR-0-WU-001
  - P6-RR-0-WU-002
  - P6-RR-0-WU-003
  - P6-RR-0-WU-004
created_at: 2026-08-26 09:38:53 JST
next_exact_work_unit: P6-RR-A-WU-001
```

## 1. Authority／Freeze

- User Exact Start受領済み。Phase 6 Remaining Rework Authorityは`ACTIVATED`。
- Mandatory Reading 16件を指定順で全文再読した。
- Design Freeze SHA-512：`3489ad52522bd19c75d47f186d21ef9f82c289da4b11b8315387a54e7ea6a3fc559afc8edb899678cb6a321037e30de767b7618c6eb819d80e6a8bda4c44b89e`、指定値と一致。
- Execution Plan SHA-512：`6d66367e88ddd33d85979837871a2e4028bf9c8efd72df69cb237fc286e78a781ed098bd585966db23702d91044f46ceca55c92e1bc7ded7c768c8da01c021cc`、指定値と一致。
- Git Commandは使用していない。Preparation Baselineとの差分はGitで再構成せず、許可対象File本文とKnown Controller-owned Artifactから扱う。
- Controller-owned Concurrent Artifact `docs/project/shared/history/automation/codex_task_recreation_identity_routing_authority_delivery_and_resource_preservation_evidence_ja_20260826092621.md` はExpected Dirty／不触対象。

## 2. Baseline Validation

Task-owned Temp：`.venv/.t/phase_6_remaining_rework_claude_20260826093407/`

| Class | Command要旨 | Result |
|---|---|---|
| Backend Full | Project内TempをCWD、`pytest --basetemp=<task-temp>/pytest` | exit 0、1602 passed／7 deselected |
| Mypy | `mypy --cache-dir=<task-temp>/mypy_cache` | exit 0、443 source files |
| Ruff | `ruff check .`、CacheはTask Temp | exit 0 |
| Frontend Typecheck | `npm run typecheck` | exit 0 |
| Frontend Lint | `npm run lint` | exit 0 |
| Frontend Test | `npm test` | exit 0、24 files／221 tests |
| Frontend Build | `npm run build -- --outDir <task-temp>/frontend-dist` | exit 0 |

Backend FullはProject Root直下のUser `runtime_data/`を参照しないようTask TempをCWDにした。初回の相対Python Path指定は実行前に`no such file or directory`でexit 127となり、Project内`.venv/bin/python`の絶対Path指定へ訂正した。

## 3. As-built Reconciliation

- Canonical Definition PackageはProject内`definitions/`からRead-onlyで検証可能。
- Current ARGD／DAGD DescriptorはARGD 53、DAGD 56、合計109。
- Current Descriptor Canonical Digest SHA-512：`dfbbf441df50bd3a97b1a053b9eb59554d879667cccd428c7aedc734faa57462f7f3093e9939f90bf86e13fa4611691586f35ab33a0b2727e00a9351e6d99361`。
- Current実装は全109件を`requires_semantic_evaluator`としてDeterministic Evaluatorで一律Deferredにする。
- JudgeはMain Runtimeを`main_self`として再利用し、GuardrailはRule／Pattern Baseのみ。Dedicated Selene／Qwen3Guard Production Bindingは未実装。
- `models`は`<MODEL_ROOT>`へのSymbolic Link。Resolved TargetはProject Root外のため、本TaskではTarget内容をTraverse／Loadしない。Real Model Acceptanceは権限上Unavailableとして分類し、Fake／Fixture／Contractを継続する。

## 4. Exact Mutation Freeze

MutationはExact Handoffの許可範囲内に限定する。予定差分は次である。

- Runtime Governance：Semantic Criterion Domain、ARGD／DAGD Trusted Compiler、Composite Evaluation、Mode Matrix／False ENFORCE防止、Criterion Evidence。
- Evaluation／Runtime Model Control／Inference／Bootstrap：Role Provider Registry、Configured／Active State、Stage Budget、Selene Runtime／Prompt／Decoder、Repair Rejudge接続。
- Guardrail Governance／Bootstrap：Qwen3Guard Prompt／Decoder、Deterministic Additive Merge、Role Binding。
- Web／Frontend：Provider Selection API、3 Dropdown、Configured／Active／Failure／Recording相関の最小表示。
- Config：Selene／Qwen3Guard Role Definition、Selene Official Prompt Copy／Manifest、Stage Budget Profile。
- Tests：上記各Contract、Regression、Failure／Race／UI。
- Docs：Package Recovery、Append-only Evidence、Complete Candidate Return Handoff。

Canonical `definitions/`、Model Artifact、Stable／Frozen Docs、Roadmap、Phase Index、Closure／Phase 7、Git、User `runtime_data/`、Provider Memoryは変更しない。

## 5. Finding／Inventory

```text
open_critical: 0
open_major:
  - P6-GOV-015 semantic execution omission（本Reworkの対象）
open_non_critical:
  - Real Model／BrowserはProject Root外Model Target不接触契約により現時点でUnavailable候補
root_outside_action: 0
provider_memory_action: 0
runtime_data_action: 0
git_action: 0
network_action: 0
model_mutation: 0
active_process: 0
loaded_model: none
task_owned_temp: .venv/.t/phase_6_remaining_rework_claude_20260826093407/
claims_not_made:
  - Phase 6 Closure
  - Real Model Acceptance PASS
  - Phase 7 Ready
```

`next_exact_work_unit: P6-RR-A-WU-001`
