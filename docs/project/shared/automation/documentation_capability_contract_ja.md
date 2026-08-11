# Documentation Capability Contract

```yaml
document_id: documentation_capability_contract
revision: capability-semantics-1
status: design_review_passed_not_activated
language: ja
created_at: 2026-08-11 23:13:32 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral: true
normative_scope: automation_pilot_design
```

## 1. Purpose

本書は、Documentationを読む・新規作成するCapabilityを、特定Provider、Command、Tool、Project PathまたはUIへ固定せずに定義する。

P2-0-WU-003では、成果物、Path、CoverageおよびMutation境界が正しくても、HandoffへHard-codeしたProvider Grammarに違反した。この結果から、統治対象を次の独立層へ分ける。

```text
Authority
  → Capability Semantics
     → Provider Mapping
        → Invocation Evidence
           → Result／Mutation Review
```

成果物の成功は契約遵守を証明せず、Provider Grammar違反も直ちにAuthority／Scope逸脱を証明しない。各層を独立判定し、未知または不一致を推測で相互補完しない。

## 2. Capability Classes

### 2.1 `bounded_documentation_read`

```yaml
inputs:
  authorized_root: exact_runtime_binding
  targets: exact_manifest_entries
  expected_identity: regular_file_non_symlink
  expected_digest: optional_or_required_by_envelope
  required_coverage: complete_or_exact_range
authority:
  mode: read_only
  discovery: deny_unless_separately_authorized
outputs:
  content: conversation_or_stdout_equivalent
  evidence: target_identity_coverage_digest
mutation:
  filesystem: zero
  git: zero
  external: zero
failure: fail_closed
```

### 2.2 `bounded_documentation_create`

```yaml
inputs:
  authorized_root: exact_runtime_binding
  exact_target: envelope_bound_path
  expected_absence: required
  content_contract: handoff_bound
authority:
  mode: create_new_only
  existing_mutation: deny
  creation_cardinality: envelope_bound
outputs:
  regular_utf8_document: required
  evidence: path_line_count_digest_readback
mutation:
  additional_artifact: zero
  permission_acl: zero
  git: zero
  external: zero
failure: stop_without_cleanup
```

## 3. Normative Capability Invariants

Providerおよび実行方法に関係なく、次をCapability-levelの必須条件とする。

1. Authorized Root、Allowed Path、Role、Work UnitおよびOperationがAccepted Authorityと一致する。
2. Read TargetまたはWrite TargetをExact Manifest／Envelopeから解決し、類似Pathを推測しない。
3. Symlink、Directory、Secret、Git Metadata、External Mountまたは許可外Targetへ暗黙拡張しない。
4. Readは要求されたCoverageを満たし、Truncation、Gapまたは未読を完全読取として報告しない。
5. Writeは許可されたOperationと件数だけを実行し、既存File変更または追加Artifactを生成しない。
6. 実行後にResult、Mutation、Evidenceおよび未確認事項を分離して報告する。
7. 不一致検知後にCleanup、Rollback、代替実行またはScope拡張を行わない。

## 4. Provider Mapping Policy

Provider Adapterは、Capability Semanticsを現在ProviderのTool／Command／APIへ変換する。Mappingは次のModeを明示する。

```text
semantic_mapping
  Capability Invariantを満たす任意のProvider-native手段を許容する。
  実際に使ったInvocation ClassとEvidenceを報告する。

strict_enforced_mapping
  特定Grammar自体がSafety上必要で、Wrapper／Validator／Provider制約により
  機械的に拒否できる場合だけ使用する。

strict_prompt_only
  特定GrammarをPromptだけで必須化する状態。
  Enforcement済みと扱わず、Pilot Evidence対象とする。
```

`strict_prompt_only`は、特定Grammarに違反しない保証を提供しない。不可避な理由がない限り、Normative CoreへCommand名を固定しない。

## 5. Invocation Cardinality／Batch Boundary

一件のInvocationで複数Targetを処理することは、単一Target Readと別Capabilityとして扱う。

```text
exact_single_target_read : 基本Capability
bounded_batch_read       : 別Capability／Default DENY
```

Batchを許可するには、Target SetがExact Freeze済みであり、各TargetのOutput、Failure、CoverageおよびDigestを分離でき、途中失敗時のPartial Stateを再現できなければならない。Loop、Glob、Directory探索またはShell展開が存在するだけで許可済みと解釈しない。

## 6. Command Choice／Content Coverage

特定のText Read Command名だけを正しさの証明にしない。全文を一括取得する方式、Range取得またはProvider-native Readerのいずれでも、次が証明できる場合だけCapability Pass候補となる。

- Exact Targetだけを処理した。
- Output Truncationがない、または検知・補完された。
- Required CoverageにGap／Overlapがない。
- Digest／Identity要件が満たされた。
- Artifact、Cache、Logまたは別Mutationを生成していない。

Command選択がAccess Scope、副作用、Evidence分離またはRecoveryへ影響する場合は、Provider Adapterがその差を明示し、より制限の強いMappingを採用する。

## 7. Independent Review Dimensions

Work UnitのReviewでは次を独立判定する。

| Dimension | Question |
|---|---|
| Authority | Role／Envelope／Human Gate内だったか |
| Scope | Exact Root／Target／Operation内だったか |
| Capability Semantics | Coverage、Cardinality、Mutation契約を満たしたか |
| Provider Mapping | Accepted Mapping Modeに従ったか |
| Result | 内容、Path、Line Count、Digestが正しいか |
| Evidence | Self-reportと独立確認を区別できるか |
| Stop／Recovery | 不一致後に安全停止し、証跡を保持したか |

一つのPASSまたはFAILだけで他Dimensionを上書きしない。

## 8. Severity／Continuation Rule

```text
Authority／Authorized Root／無許可Mutation違反
  → EMERGENCY_STOP候補

Capability Semantics違反
  → STOPPED／Result未Accepted

strict_enforced_mapping違反
  → Provider Adapter FAIL／Resultと分離Review

strict_prompt_only違反かつCapability Semantics維持
  → ADJUST_REQUIRED／Evidence保持／再設計Gate

Result Contentだけの不一致
  → Functional FAIL／Safety結果と分離
```

小さな逸脱が将来の不可逆な副作用へ発展する可能性を過小評価しない。同時に、実害のないProvider差を最上位Safety Incidentへ自動昇格せず、影響DimensionをEvidenceで分離する。

## 9. Evidence Contract

```yaml
capability_id: string
capability_revision: string
authority_revision: string
provider_adapter_id: string
provider_mapping_mode: semantic_mapping | strict_enforced_mapping | strict_prompt_only
requested_targets: list
observed_target_evidence: list
invocation_class: list
provider_trace_available: boolean
coverage: mapping
result: mapping
mutation: mapping
deviation: list
self_reported: list
independently_verified: list
unverified: list
stop_state: string
```

Provider Traceが取得できない場合は`unverified`として残し、Child Self-reportをController独立確認へ読み替えない。

## 10. Activation Boundary

本書は設計正本であり、既存P2-0-WU-003の結果、HandoffまたはAcceptanceを遡及変更しない。次Work Unitで使用するには、Exact Envelope、Provider Adapter Revision、Manifest、Handoff、Freeze Receipt、Controller READYおよびユーザーStartを別途必要とする。

## 11. Related Documents

- [Automation Governance Index](automation_governance_index_ja.md)
- [Codex Desktop Documentation I/O Adapter](provider_adapters/codex_desktop_documentation_io_adapter_ja.md)
- [P2-0-WU-003 Controller Review](../../phases/phase_2/history/operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
- [P2-0-WU-003 Automation Evidence](../history/automation/automation_governance_evidence_phase_2_write_success_command_grammar_failure_ja_20260811225656.md)
