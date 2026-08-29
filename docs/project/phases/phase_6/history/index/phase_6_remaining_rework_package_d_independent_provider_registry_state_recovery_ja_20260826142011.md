# Phase 6 Remaining Rework — Package D Recovery

```yaml
document_id: phase_6_remaining_rework_package_d_independent_provider_registry_state_recovery_20260826142011
status: package_complete_next_active
package: P6-RR-D
completed_wus: [P6-RR-D-WU-001, P6-RR-D-WU-002, P6-RR-D-WU-003, P6-RR-D-WU-004, P6-RR-D-WU-005, P6-RR-D-WU-006, P6-RR-D-WU-007]
created_at: 2026-08-26 14:20:11 JST
next_exact_work_unit: P6-RR-E-WU-001
```

## Result

- Main／Guard／Judgeを独立Roleとして扱うProvider Option、Selection、Runtime State、Independence Contractを実装した。
- Global Revision＋Digest CASを実装し、Stale Revision、Unknown Provider、Role Mismatch、Disabled ProviderをTyped ErrorとしてRejectする。
- Option RegistryはMain `Qwen／DeepSeek`、Guard `none／built_in.rule_pattern／Qwen3Guard`、Judge `none／built_in.deterministic／Selene／Qwen／DeepSeek`を持つ。
- Default ConfiguredはMain Qwen、Guard Qwen3Guard、Judge Selene。Startup ActiveはMainだけで、Dedicated Guard／Judge Activeは`none`。SelectionだけではLoad／Fallbackしない。
- Configured／Active／State／Failure／Independenceを別Fieldで保持し、明示選択したSame Main Judgeだけを`self`とする。
- Selene／Qwen3GuardのModel Definitionを追加し、Frozen DesignのArtifact Relative Path／Size／SHA-512／Roleを保持した。Model Artifact本体はTraverse／Loadしていない。

## Changed Source／Test／Config

- `src/margpa_runtime_llm/modules/runtime_model_control/domain/provider_selection.py`
- `src/margpa_runtime_llm/modules/runtime_model_control/domain/__init__.py`
- `src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py`
- `src/margpa_runtime_llm/modules/runtime_model_control/application/__init__.py`
- `config/models/selene_1_mini_llama_3_1_8b_q5_k_m.toml`
- `config/models/qwen3guard_gen_0_6b_q8_0.toml`
- `tests/unit/runtime_model_control/test_provider_selection_controller.py`

P6-RR-EのLifecycle Source／TestおよびWeb Composition Current Diffは本Packageの完了根拠へ混入しない。

## Validation

```text
Provider Registry/CAS Focused: 6 passed / exit 0
Model Definition parse/identity: 上記6件中2 parameter cases PASS
Package D current Mypy/Ruff: NOT RUN（P6-RR-E統合後のScoped Staticで実施）
Integrated Backend Full: NOT RUN in Package D
Frontend: NOT RUN in Package D
Real Model: NOT RUN / Project Root外symlink target不接触
Browser: NOT RUN
```

Artifact SHA-512:

```text
provider_selection domain:
f7dae17922f871505e00701e962f6d7d7433ab8f6ab950fa12e42640958f0acff4e45d5e1d13ee38e19d5a2d257e69a155c394419c61050f0e2fd008ac4fd228
provider_selection controller:
16a3d60de7bf35a26300dfe92ab0911a144a5ff1f80aa6b52b3144d6ebcbf608e46d5b66407725107fe2a03453faaedc881476f24ee843dcd3e03c64a587872a
Selene definition file:
74384b58f56b8ff9b44b53ed0a62aab2eeb76a0056fe5145fa7a6f38accf9bb79360d920999d8d706e0bdce2c62941149dc1f0595cdc5fc017e69da7ea790b3c
Qwen3Guard definition file:
4e654240d58b357c123879d2ce557e6f026c75efef68f2ea12adc8e130ef27b589c6184a7692065f634b5f6e076831243a155319c054961a76bc17d5cf788f60
```

Frozen Artifact Identity copied into validated Config:

```text
Selene size 5732992896 / artifact SHA-512 6d547291...b6c50d
Qwen3Guard size 804753472 / artifact SHA-512 0b8d213f...6c19cb
```

## Acceptance／Finding

```text
P6-RR-ACC-009〜011: Domain Option Registry PASS; API/UI remains Package I
P6-RR-ACC-012: CURRENT PASS for Configured defaults and Dedicated Active none
P6-RR-ACC-013: CURRENT PASS by construction/test; no startup dedicated Load
P6-RR-ACC-014〜017: NOT RUN / Package E
P6-RR-ACC-018: CURRENT PASS at Independence Domain; UI remains Package I
open_critical: 0
open_major: Dedicated lifecycle/runtime binding pending E/F/G
open_non_critical: Upstream exact revision/prompt provenance pending F/G; Network prohibited by Resume Authority
```

## Authority／Incident Inventory

```text
current package root_outside/provider_memory/runtime_data/git/network/model_mutation: 0/0/0/0/0/0
historical P6-RR-INC-001 root-outside action: 1 retained
P6-RR-ACC-039: FAIL retained
active_process: 0
loaded_model_by_this_task: none
task_owned_temp: .venv/.t/phase_6_remaining_rework_claude_20260826093407/
claims_not_made: Dedicated Active/Usable, Real Model PASS, Browser PASS, Phase 6 Closure, Phase 7 Ready
```

`next_exact_work_unit: P6-RR-E-WU-001`
