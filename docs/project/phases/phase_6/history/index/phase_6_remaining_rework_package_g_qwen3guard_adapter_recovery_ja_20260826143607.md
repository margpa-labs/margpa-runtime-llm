# Phase 6 Remaining Rework — Package G Recovery

```yaml
document_id: phase_6_remaining_rework_package_g_qwen3guard_adapter_recovery_20260826143607
status: package_complete_with_partial_acceptance_next_active
package: P6-RR-G
completed_wus: [P6-RR-G-WU-001, P6-RR-G-WU-002, P6-RR-G-WU-003, P6-RR-G-WU-004, P6-RR-G-WU-005, P6-RR-G-WU-006, P6-RR-G-WU-007]
created_at: 2026-08-26 14:36:07 JST
next_exact_work_unit: P6-RR-H-WU-001
```

## Result

- Qwen3Guard-Gen専用のTyped ContractとExact Line Decoderを追加し、`Safety: Safe|Controversial|Unsafe`、Optional `Categories`、Output Candidateで必須の`Refusal: Yes|No`を分離保持した。Token-level Stream Variantは実装していない。
- `guardrail.input / guardrail.output_candidate / guardrail.context_source`をTyped Targetとして分離し、Output CandidateはUser Query→Assistant CandidateのMessage PairでBindingする。
- Field順序、Duplicate Field、Unknown Safety、Unknown Refusal、Duplicate Category、SafeとRisk Categoryの矛盾をRejectする。MalformedとTimeoutはTyped Unknownとし、Safeに変換しない。
- Resume AuthorityのNetwork禁止によりOfficial Category Allow-listのImmutable Revisionを取得できない。記憶で代用せず、Category Mappingは検証済みMappingの明示Injectionとし、未確認Categoryは`UNKNOWN_LABEL`にFail Closedする。
- Dedicated AdapterはModel ID、Exact Revision、Artifact SHA-512、Schema ID、Target、Safety、Categories、Refusal、Detection、Failure、Latency、Token Countを保持する。Official Contract未検証時はModel Call前にTyped Unavailableとする。
- Existing `SafetyModelDetectorAdapter`を介してRule／Pattern Detectionと加算的に共存し、ModelのClearがDeterministic Matchを消さないことをRegressionで確認した。

## Changed Source／Test

- `src/margpa_runtime_llm/modules/guardrail_governance/domain/qwen3guard.py`
- `src/margpa_runtime_llm/modules/guardrail_governance/domain/__init__.py`
- `src/margpa_runtime_llm/adapters/guardrail_governance/qwen3guard_adapter.py`
- `src/margpa_runtime_llm/adapters/guardrail_governance/__init__.py`
- `tests/unit/guardrail_governance/test_qwen3guard_adapter.py`

## Validation

```text
Qwen3Guard Adapter + existing Safety Model Seam Focused: 28 passed / exit 0
Scoped Mypy: 3 source files PASS / exit 0
Scoped Ruff: PASS / exit 0
Decoder matrix: Safe/Controversial/Unsafe/Categories/Refusal PASS
Negative matrix: Unknown Safety/Refusal/Category, Malformed, Partial, Duplicate, Contradiction, Timeout -> Reject/Typed Unknown PASS
Additive Merge: Deterministic Match retained with Model Clear PASS
Official Category Contract Revision: UNAVAILABLE / Network prohibited
Real Qwen3Guard GGUF: NOT RUN / Project Root外Artifact target不接触
Integrated Backend Full: NOT RUN in Package G
Frontend: NOT RUN in Package G
Browser: NOT RUN
```

Key SHA-512:

```text
Qwen3Guard typed contract/decoder:
b601252f261de0c563a7eed84501a7dfbc9c93bc3de2d2f062e1bf2f8dbf3236ea17daff12f1edbac5478528a868b80c3b6c2ae8c16c2e009a3937e8fc5af03d
Qwen3Guard adapter:
edbb066c4dba71aee554fd64ba2bef861bfd6f0a2bc19c41f5aa81fa9512e06d2dd090d1951bc8b42cb6ceb2ff328c1ecd9cb89a53060fa9b9075986a9201670
Qwen3Guard model definition:
4e654240d58b357c123879d2ce557e6f026c75efef68f2ea12adc8e130ef27b589c6184a7692065f634b5f6e076831243a155319c054961a76bc17d5cf788f60
Frozen Qwen3Guard artifact identity:
size=804753472
sha512=0b8d213fd487980ce2667acaaf042d228486d9b467cd90ab6bfbe490527fa1b51d7a318af593bc920d59f5b22759196c09eaf8cba1974766ab170e6d6f6c19cb
```

## Acceptance／Finding

```text
P6-RR-ACC-022: PASS / Frozen Safety・Optional Categories・Response RefusalのExact Parser
P6-RR-ACC-023: PASS / Unknown Category・Malformed・TimeoutをSafeにせずTyped Unknown化
P6-RR-ACC-024: CURRENT PASS / Additive MergeとDedicated Identity; Real Turn NOT RUN
P6-RR-ACC-037 Qwen3Guard row: UNAVAILABLE / Real Artifact NOT RUN
open_critical: 0
open_major: Official Category Allow-list and immutable upstream revision unavailable under Network prohibition
open_non_critical: Real Dedicated Load and Web Turn remain unavailable in current environment
```

## Authority／Incident Inventory

```text
current package root_outside/provider_memory/runtime_data/git/network/model_mutation: 0/0/0/0/0/0
historical P6-RR-INC-001 root-outside action: 1 retained
P6-RR-ACC-039: FAIL retained
active_process: 0
loaded_model_by_this_task: none
task_owned_temp: .venv/.t/phase_6_remaining_rework_claude_20260826093407/
claims_not_made: Official Category Mapping PASS, Real Model PASS, Integrated Full PASS, Browser PASS, Phase 6 Closure, Phase 7 Ready
```

`next_exact_work_unit: P6-RR-H-WU-001`
