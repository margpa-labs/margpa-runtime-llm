# Codex Desktop Documentation I/O Provider Adapter

```yaml
document_id: codex_desktop_documentation_io_adapter
revision: semantic-mapping-1
status: design_review_passed_not_activated
provider_specific: true
normative_core: false
language: ja
created_at: 2026-08-11 23:13:32 JST
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
default_state: disabled
mapping_policy: semantic_mapping
mechanical_enforcement: unavailable
```

## 1. Purpose

本書は、Provider-neutralな`bounded_documentation_read`および`bounded_documentation_create`をCodex Desktopの現在CapabilityへMappingする。

旧[Bounded Read Adapter](codex_desktop_bounded_read_adapter_ja.md)はP2-0-WU-002のStrict Read試験Evidenceとして保持し、遡及変更しない。本AdapterはP2-0-WU-003で得たCommand Grammar／Capability Semantics分離知見を後続Work Unitへ適用する。

## 2. Provider Capability Mapping

| Core Capability | Current Mapping | State |
|---|---|---|
| Exact regular-file existence／identity check | Local read-only command or equivalent provider inspection | available |
| Exact line count／digest | Local read-only command or equivalent deterministic calculation | available |
| Exact content read | Provider text read or local stdout-only read | available with coverage evidence |
| Exact new Markdown create | `apply_patch` Add File equivalent | available with one-target limit |
| Existing File mutation | none | denied for bounded create |
| Bounded batch read | no accepted mapping | unavailable |
| Mechanical command allowlist | none | unavailable |

## 3. Mapping Invariants

Provider固有手段の選択に関係なく、次を満たす。

- `workdir`またはProvider Root BindingはControllerが与えたExact Authorized Root。
- TargetはManifest／Envelopeに列挙されたExact Relative Pathだけ。
- 一回のInvocationは一つのTargetを基本とする。
- Directory探索、Search、Glob、Recursive Traversalまたは類似Path推測を行わない。
- Readはstdout／conversation equivalentだけとし、Artifact、CacheまたはLogを意図的に作成しない。
- WriteはExact Result Pathへの一回の新規作成だけ。
- 実行したInvocation Class、Target、Coverage、ResultおよびDeviationを報告する。

## 4. Read Mapping Selection

Providerは、対象Size、Output Limit、Coverage要件および現在Tool Capabilityから、Exact Single-target Read方式を選ぶ。

```text
whole_text_read
  Exact Target全文を一回で取得し、Truncationなしを確認できる場合。

ranged_text_read
  Exact Targetを連続Rangeで取得し、Gap／Overlapなしを確認する場合。

provider_native_text_read
  Provider固有ReaderがExact TargetとCoverage Evidenceを返せる場合。
```

Command名はCore Contractへ固定しない。`cat`、`sed`その他の差は、Exact Target、Coverage、Truncation、ArtifactおよびMutationのEvidenceにより判定する。

## 5. Strict Grammar Boundary

現在のCodex Desktop Mappingには、Raw Command Grammarを実行前に機械的拒否する専用Wrapperがない。このため、本Adapterは`semantic_mapping`を使用し、特定Command列をEnforced Allowlistとは表示しない。

Strict Grammarが必要な将来Work Unitでは、次のいずれかを先に成立させる。

- 検証済みWrapper
- Tool Parameter Schemaによる固定
- Provider-native Allowlist
- 実行前Validatorと拒否Evidence

Promptだけで特定Commandを列挙する場合は`strict_prompt_only`と表示し、機械的強制済みと扱わない。

## 6. Batch Boundary

Loop、複数引数、複数Target Pipelineまたは複数FileをまとめたShell処理は、本Adapterの`exact_single_target_read`へ含まれない。

複数Target処理が必要な場合は、別の`bounded_batch_read` Capability、Exact Target Set、個別Output Separation、Partial Failure ContractおよびユーザーがAcceptedしたAdapter Revisionを必要とする。現在Stateは`unavailable`である。

## 7. Create Mapping

```text
Precondition : Exact Result Path absent／non-symlink parent already exists
Action       : one Add File operation
Encoding     : UTF-8 Markdown
Postflight   : exact readback／line count／SHA-512
Mutation     : created 1／modified 0／deleted 0／additional 0
```

作成後に不一致を検出しても、削除、上書き、二回目のPatchまたは自動Rollbackを行わない。

## 8. Evidence／Failure

Taskは次を返す。

```yaml
mapping_policy: semantic_mapping
invocation_class: list
exact_targets: list
coverage: mapping
result: mapping
mutation: mapping
provider_trace_available: boolean
deviation: list
self_reported: list
unverified: list
stop_state: string
```

次で停止する。

- Exact Target、Root、EnvelopeまたはManifest不一致。
- Output Truncation、Coverage GapまたはTarget混在を解消できない。
- Batch処理、探索または追加Mutationが必要になる。
- ProviderがUnexpected Artifactを生成した疑い。
- Result Pathが存在する、Symlinkである、または一回のAddで完了できない。

Stop後は代替Command、Cleanup、Scope拡張または自動Retryを行わない。

## 9. Current State

```text
Design Review          : PASS
Mechanical Enforcement : UNAVAILABLE
Mapping Policy         : SEMANTIC
Bounded Batch Read     : UNAVAILABLE
Activated Work Unit    : NONE
P2-0-WU-003            : NOT RETROACTIVELY CHANGED
Next Gate              : exact package／user acceptance／two-key start
```

## 10. Related Documents

- [Documentation Capability Contract](../documentation_capability_contract_ja.md)
- [Legacy Bounded Read Adapter](codex_desktop_bounded_read_adapter_ja.md)
- [Automation Governance Index](../automation_governance_index_ja.md)
- [P2-0-WU-003 Controller Review](../../../phases/phase_2/history/operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
