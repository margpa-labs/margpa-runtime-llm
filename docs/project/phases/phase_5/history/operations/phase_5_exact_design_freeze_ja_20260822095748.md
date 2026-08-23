# Phase 5 Exact Design Freeze

```yaml
document_id: phase_5_exact_design_freeze_20260822095748
status: accepted_frozen
phase: phase_5
recorded_at: 2026-08-22 09:57:48 JST
implementation_authorized: false
```

## 1. Frozen Package

```text
docs/project/phases/phase_5/phase_index_ja.md
docs/project/phases/phase_5/requirements/phase_5_requirements_ja.md
docs/project/phases/phase_5/architecture/phase_5_architecture_ja.md
docs/project/phases/phase_5/adr/phase_5_adr_ja.md
docs/project/phases/phase_5/governance/phase_5_claude_execution_governance_ja.md
docs/project/phases/phase_5/operations/phase_5_execution_plan_ja.md
docs/project/phases/phase_5/operations/phase_5_acceptance_matrix_ja.md
docs/project/phases/phase_5/handoffs/phase_5_claude_execution_handoff_ja.md
```

## 2. Exact Responsibility

```text
Claude : Phase 5-0～5-G／32 Work Units／COMPLETE_CANDIDATEで停止
Codex  : Phase 5-H Independent Major Review／Rework Routing／Closure Proposal
User   : Backup／Start／Mac Acceptance／Final Acceptance／External／Git Authority
```

## 3. Frozen Invariants

- Guardrail ModeはPhase 3／4 Modeと独立し、Default OFF。
- Detection／Policy／Authority／Approval／Actionを分離。
- Safety Model 0件でDeterministic Baselineが成立。
- OBSERVEは非介入、ENFORCEはRegistered／Authorized／Approved Actionのみ。
- Unknown／Unsupported／Timeout／Low ConfidenceからAllowを捛造しない。
- Secret／PII実値をEvidence／Status／Raw Errorへ出さない。
- Enforce Streamで未検査ContentをClientへ先送しない。
- Main Governance AllowまたはPhase 6 JudgeはSafety／Authority Denyを上書きしない。
- Phase 5-G後にPhase 5-H／5-EX／6／Git／Externalへ自動進行しない。

## 4. Dynamic Exact Mutation

実File Packageを固定量産しない。ClaudeはPhase 5-0でAs-builtとFrozen Contractを照合し、Work Unit毎に必要なSource／Test／UI／Historyだけを動的に解決する。Stable Existing Docs／Existing HistoryはRead-onlyとする。

## 5. Activation

```text
Design       : ACCEPTED／FROZEN
Backup       : PENDING
Codex ARMED  : PENDING AFTER BACKUP
User Start   : PENDING AFTER ARMED
Automation   : OFF
Implementation: NOT AUTHORIZED
```
