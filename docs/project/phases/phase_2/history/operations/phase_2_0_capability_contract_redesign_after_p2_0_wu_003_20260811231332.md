# Phase 2-0 Capability Contract Redesign after P2-0-WU-003

```yaml
document_id: phase_2_0_capability_contract_redesign_after_p2_0_wu_003_20260811231332
status: redesign_complete_next_exact_package_not_authorized
phase: phase_2
subphase: phase_2_0
work_unit_source: P2-0-WU-003
created_at: 2026-08-11 23:13:32 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role: user
control_state: PAUSED_CAPABILITY_CONTRACT_REDESIGN
```

## 1. Trigger

P2-0-WU-003は、正しい成果物をExact Pathへ一件作成し、追加Mutationを発生させなかった。一方、子Taskは`cat`使用と複数対象Shell処理がAccepted HandoffのProvider Grammarに違反したと自己申告し、安全停止した。

この事象は、実害の大きさと統治上の重要性が一致しない例である。

```text
Immediate Artifact／Security Impact : low
Literal Contract Impact             : material
Long-term Repetition Risk            : high if normalized
Evidence Value                       : high
```

## 2. Design Decision

Raw Command列をNormative Safety Contractへ直接Hard-codeせず、次へ分離した。

```text
Provider-neutral Capability Semantics
  → Provider-specific Mapping Policy
     → Actual Invocation Evidence
        → Dimension-separated Review
```

Provider固有Grammarが不可欠なら、Promptで命令するだけでなく機械的強制を必要とする。機械的強制がない状態は`strict_prompt_only`と明示し、保証済みと扱わない。

## 3. Preserved Boundaries

再設計は次を弱めない。

- Human-defined Supreme Rules
- Exact Authorized Root／Allowed Path
- Role／Docs Authority
- Exact Manifest／Envelope／Human Gate
- Directory探索、Glob、External、Secret、Gitおよび無許可Mutation禁止
- One-target／One-createのCardinality
- Digest／Coverage／Result Evidence
- Incident後No-cleanup

Command選択の抽象化はShell一般許可、任意Command許可またはBatch許可を意味しない。

## 4. New Review Model

```text
Authority
Scope
Capability Semantics
Provider Mapping
Result
Evidence
Stop／Recovery
```

各Dimensionを独立判定する。P2-0-WU-003は、Result／Mutation Safety／StopはPASS、Literal Provider GrammarはFAIL、Overallは`ADJUST_REQUIRED`のまま保持する。

## 5. New Stable Design Sources

- [Documentation Capability Contract](../../../../shared/automation/documentation_capability_contract_ja.md)
- [Codex Desktop Documentation I/O Adapter](../../../../shared/automation/provider_adapters/codex_desktop_documentation_io_adapter_ja.md)

旧Bounded Read Adapter、P2-0-WU-003 Handoff、ResultおよびReviewはHistory Evidenceとして遡及変更しない。

## 6. Next Minimal Retest Candidate

```text
Candidate ID        : P2-0-WU-004
Purpose             : capability-semantics-based bounded documentation create retest
Task Role           : Phase 2設計担当者役
Automation Level    : bounded_unit
Read Capability     : exact_single_target_read only
Write Capability    : one exact create only
Batch Capability    : unavailable／deny
Provider Policy     : semantic_mapping
Mechanical Grammar  : unavailable／not claimed
Existing Mutation   : zero
Git／External／Secret: zero
Acceptance          : dimension-separated review + user decision
```

P2-0-WU-004では、成果物内容を再利用して同じFileを上書きしない。新しい小さなEvidence ArtifactとExact Packageを別途設計し、Command名ではなくCapability Semantics、Target Cardinality、Coverage、MutationおよびStopを検証する。

## 7. Current Gate

```text
P2-0-WU-003 Artifact       : retained／content verified
P2-0-WU-003 Acceptance     : ADJUST_REQUIRED／not accepted
Capability Redesign        : complete／design review passed
P2-0-WU-004 Exact Package  : not created
P2-0-WU-004 Task           : not created／not authorized
Automation State           : PAUSED
Phase 2-A                  : not started
Git／External              : no action
```

次の安全なActionは、P2-0-WU-004のExact Envelope／Manifest／Handoff／Receipt候補を作る範囲について、ユーザー判断を得ることである。本再設計だけでTask作成、READY、StartまたはPhase 2-Aへ移行しない。

## 8. Evidence

- [P2-0-WU-003 Controller Review](phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md)
- [P2-0-WU-003 Result](phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md)
- [Shared Automation Evidence](../../../../shared/history/automation/automation_governance_evidence_phase_2_write_success_command_grammar_failure_ja_20260811225656.md)
