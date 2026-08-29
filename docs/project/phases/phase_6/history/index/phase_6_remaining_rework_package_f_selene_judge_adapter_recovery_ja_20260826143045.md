# Phase 6 Remaining Rework — Package F Recovery

```yaml
document_id: phase_6_remaining_rework_package_f_selene_judge_adapter_recovery_20260826143045
status: package_complete_with_partial_acceptance_next_active
package: P6-RR-F
completed_wus: [P6-RR-F-WU-001, P6-RR-F-WU-002, P6-RR-F-WU-003, P6-RR-F-WU-004, P6-RR-F-WU-005, P6-RR-F-WU-006]
created_at: 2026-08-26 14:30:45 JST
next_exact_work_unit: P6-RR-G-WU-001
```

## Result

- Selene Dedicated JudgeのArtifact IdentityはFrozen DefinitionのRelative Path、Size、SHA-512、Roleとして保持した。
- Exact Resume AuthorityがNetworkを禁止しているため、Official Promptを記憶から作成せず、Repository URLと未取得状態のみをManifest化した。Upstream Revision、Template File、Template SHA-512は`null`、`verified_official_copy=false`である。
- Production ManifestはOfficial Revision・Template・Digestが揃わない限り`SelenePromptUnavailable`としてFail Closedする。
- Criterion→Prompt AdapterはQuery、Candidate、Reference、Criterion ID・Method・Instruction・Source Pointer、Strict Response Schemaを明示Bindingする。Template SHA-512と必須Placeholderも検証する。
- Structured DecoderはValid結果をTyped Semantic Resultへ変換し、Malformed、Partial、Contradictory OutputはAcceptせずTyped Unavailableとする。
- Dedicated Runtime AdapterはConfigured Selene Model KeyをGeneration RequestとSemantic Evidence Provider Identityの両方に保持し、`independent_artifact`のDecoder Contractを使用する。Main-selfへのFallbackは0。

## Changed Source／Test／Config

- `config/judge_templates/selene/manifest.json`
- `src/margpa_runtime_llm/adapters/evaluation/selene.py`
- `src/margpa_runtime_llm/adapters/evaluation/__init__.py`
- `tests/unit/evaluation/test_selene_adapter.py`

## Validation

```text
Selene Adapter + Judge Prompt/Decoder Focused: 29 passed / exit 0
Scoped Mypy: 2 source files PASS / exit 0
Scoped Ruff: PASS / exit 0
Fixture Prompt coverage: Query/Candidate/Reference/Criterion/Method/Schema PASS
Decoder matrix: Valid PASS; Malformed/Partial/Contradictory -> Typed Unavailable PASS
Production Official Prompt: UNAVAILABLE / Network prohibited, immutable revision not obtained
Real Selene GGUF: NOT RUN / Project Root外Artifact target不接触
Integrated Backend Full: NOT RUN in Package F
Frontend: NOT RUN in Package F
Browser: NOT RUN
```

Key SHA-512:

```text
Selene model definition:
74384b58f56b8ff9b44b53ed0a62aab2eeb76a0056fe5145fa7a6f38accf9bb79360d920999d8d706e0bdce2c62941149dc1f0595cdc5fc017e69da7ea790b3c
Selene prompt manifest:
5e7776276396db28c83c1945df45d2c889a4a2058198df241ec658463837e1ba7e55ea28e479e4c33fa32ca929ba6dddc4e160ba9383e937c80b10e48997efbb
Selene adapter:
a0cf79965f76a6cd9e853afba3987439f803e2ffbbc5d18d8621cdb5e8944c4fd1b211d24f6de40447de1548d267ec709e8aa8ae6e4d3aa2f363bbabf2206a50
Frozen Selene artifact identity:
size=5732992896
sha512=6d5472911fc347d51a73e57077dd34353c3e134a0af67b0dbe4e4df7d980e3246f0253ee16e5a241a41904d37e73ab3ba11ce5d800de37b9adddb2ada9b6c50d
```

## Acceptance／Finding

```text
P6-RR-ACC-019: PARTIAL / Artifact Identity PASS; Official Prompt immutable revision/template/digest UNAVAILABLE
P6-RR-ACC-020: PASS / Valid・Malformed・Partial・ContradictoryをFocused Testで分離
P6-RR-ACC-021: CURRENT PASS / Selene IdentityをAdapter Request/Responseに保持; Real Turn NOT RUN
P6-RR-ACC-037 Selene row: UNAVAILABLE / Real Artifact NOT RUN
open_critical: 0
open_major: Official Prompt Template provenance cannot be completed under current Network prohibition
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
claims_not_made: Official Prompt PASS, Real Model PASS, Integrated Full PASS, Browser PASS, Phase 6 Closure, Phase 7 Ready
```

`next_exact_work_unit: P6-RR-G-WU-001`
