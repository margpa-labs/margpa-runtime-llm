# Phase 4 Exact Design Freeze

```yaml
document_id: phase_4_exact_design_freeze_ja_20260821232056
status: accepted_frozen
phase: phase_4
subphase: phase_4_0
recorded_at: 2026-08-21 23:20:56 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
automation_control_state: OFF
git_mutation: not_performed
```

## 1. Freeze Decision

Phase 3 As-built ReconciliationをPASSとし、Phase 4 Design PackageをAccepted／Frozenとする。Phase 4-0～4-GのClaude長期実行Packageは設計上成立しているが、ユーザーBackup、Activation Preflight、Codex `ARMED`および後続User Startまで実行してはならない。

## 2. Frozen Package SHA-512

```text
fb350a7959966ec5a9bf3599cffaea2c787c04ced60bb0e3011f6c25ac44f2b1628c7e196765a1730fc9c9e87a784e7662672910eccd48c4c05e921402a15dd8  docs/project/phases/phase_4/requirements/phase_4_requirements_ja.md
8c06b87108577e400bd454981fde6de1b76806dbccb1b6db2e4223e94e6f6336ff2ea3657cbabc27e23a8384fe04d96e96efddeb3fc27f36deac425b5b37fcd4  docs/project/phases/phase_4/architecture/phase_4_architecture_ja.md
e9778af1dc948121f0f7edf212b9457e4080f982c4e4c1ce3e34af8f23ac91fe907423c9596cf9b86c7e5ae270269552264ec84bf25ac27d00c36a1549529350  docs/project/phases/phase_4/adr/phase_4_adr_ja.md
7b608a706b1c3e1e28624624bb5a0319bca344f6e07047564b211989bb02b9d9fd14e8eaf03147de2047c3eee86ff5b4e083ee9d7393fedeb8d6392badf21fb1  docs/project/phases/phase_4/governance/phase_4_claude_execution_governance_ja.md
3074c36fbc8cea53cc04ba77464729b720bcd0e854df95fb8843ec7ef2a8da6b00256cf4b460b11367be268bc664d6cc0b15e0f163312af6633a39518b2d406f  docs/project/phases/phase_4/operations/phase_4_execution_plan_ja.md
c702f6694f2a05175f1e6ab92b14a49bc8405f375ecb16b42acfd691dc28ea407dc4fa3e05c6f323d76f749e2ce49ffecd829f6d6e5c64250d8fb3734457e2aa  docs/project/phases/phase_4/operations/phase_4_acceptance_matrix_ja.md
50ffc73c77083a01d317c0ef98bab7dab75de7c42747d852514b1498af19e9936863b296c7e1f47aa60cebe604535dd89ded5bd6bca5e44983eaf913601ee160  docs/project/phases/phase_4/handoffs/phase_4_claude_execution_handoff_ja.md
cc64d63acf88d3a29a07a5e1a45e6de50f4c98a65b72f61549e92f903f86ee6231588ccefdef160a6ae1d284cac5fca30af4211aa9bcaa8dbe71c1c67445ec2c  docs/project/phases/phase_4/phase_index_ja.md
9c0a579384d58095b8f994ab7e27f38be50fad15da5d61707e5b23d5f166b665c595816fbdf09229abed7d24bc610204f4d84c1f5e986058d7d1270ffa165990  docs/project/phases/phase_4/history/operations/phase_4_as_built_reconciliation_ja_20260821232056.md
```

DigestはFreeze時点のFile bytesに対する実測値である。Freeze後にStable Packageを変更する場合は、理由、影響、Before／After、Reviewおよび新しいFreeze Receiptを必要とする。

## 3. Frozen Execution Boundary

```text
Claude Minimum Start : P4-0-WU-001
Claude Maximum End   : P4-G-WU-003／COMPLETE_CANDIDATE
Codex／User Boundary : Phase 4-H
Phase 5／6           : NOT AUTHORIZED
Git／External        : NOT AUTHORIZED
Model                : Qwen Current Route only
DeepSeek             : Candidate Artifact only／Load・Promotion 0
Automation           : OFF until two-key activation
```

Exact MutationはWork UnitごとにFrozen要件とAs-builtからRole-localに動的決定する。必要なものだけを作り、固定Packageを機械的に量産しない。

## 4. Material Recovery Boundary

Recoveryは毎小修正ではなく、Phase 4-0、4-A、4-B、4-C、4-D、4-E、4-Fおよび4-GのMaterial Boundary単位で作る。利用可能量／Provider Limitで中断した場合は、Current WU、Exact Mutation、Last Validated State、Open Major Finding、Next Semantic ActionをPhase 4 HistoryへAppend-onlyで残す。

## 5. Activation Gate

```text
Design Accepted／Frozen : PASS
Phase 3 Closure         : PASS
As-built Reconciliation: PASS
User Backup             : PENDING
Codex ARMED             : PENDING AFTER BACKUP
User Start              : PENDING AFTER ARMED
Implementation          : NOT AUTHORIZED
```
