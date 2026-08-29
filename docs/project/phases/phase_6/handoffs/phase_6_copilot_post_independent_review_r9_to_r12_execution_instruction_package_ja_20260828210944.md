# Phase 6 Copilot Post-Independent-Review R9〜R12 Execution Instruction Package

```yaml
document_id: phase_6_copilot_post_independent_review_r9_to_r12_execution_instruction_package_20260828210944
document_type: user_copy_paste_execution_instruction
document_state: ready
language: ja
created_at: 2026-08-28 21:09:44 JST
target_provider: GitHub Copilot app
target_role: 設計者兼実装者役
implementation_authority: false_until_step_3
```

## 1. 送信順

同じCopilot Taskを継続する場合も、新規Taskへ切り替える場合も、次の1→2→3を順に送る。

### Step 1 — Role／Review Correction Bootstrap

```text
【Copilot Phase 6 Post-Review Role／Authority Correction Bootstrap】

Provider: GitHub Copilot app
Role: 設計者兼実装者役
Task Identity: Copilot Phase 6 Post-Review Rework Task

旧Conversation、内部Memory、以前のComplete Candidate Claim、以前の実装Authorityまたは自己解釈したScopeを正本として継承しないでください。

現在許可するのは、指定文書のReadとReceipt返却だけです。
まだSource／Test／Config／Frontend／Docs Mutation、Command、Network、Git、Model Loadを開始しないでください。

次の4文書を全文読んでください。

1.
<PROJECT_ROOT>/docs/project/shared/task_roles/copilot_side_designer_implementer_operating_notes_ja.md

2.
<PROJECT_ROOT>/docs/project/shared/task_roles/copilot_side_long_running_automation_companion_ja.md

3.
<PROJECT_ROOT>/docs/project/shared/task_roles/copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md

4.
<PROJECT_ROOT>/docs/project/shared/history/automation/copilot_first_long_run_pilot_empirical_automation_and_resource_evidence_ja_20260828210944.md

読了後、次だけを返してください。

Provider: GitHub Copilot app
Role: 設計者兼実装者役
Task Identity: Copilot Phase 6 Post-Review Rework Task
Mandatory Role Reading: COMPLETE
Previous Complete Candidate Claim: SUPERSEDED_PENDING_CONTROLLER_REWORK
Old Authority Inheritance: NONE
Implementation Authority: FALSE
State: WAITING_FOR_EXACT_HANDOFF

返却後は停止してください。
```

### Step 2 — Exact Handoff Read／Receipt

```text
【Phase 6 Copilot Post-Independent-Review R9〜R12 Exact Handoff Bootstrap】

次のController ReviewとExact Rework Handoffを全文読んでください。

Controller Review:
<PROJECT_ROOT>/docs/project/phases/phase_6/history/operations/phase_6_gov020_copilot_r3_to_r8_controller_independent_review_ja_20260828210944.md

Controller Review SHA-512:
9d77e21bd58a8fb704075e5744df214c4d42efb58d144561befc5f26c56f9ac0c28c9b495d29a2040d617c81e84f8a2de41b10fac0469b011e91106804e1d13f

Exact Rework Handoff:
<PROJECT_ROOT>/docs/project/phases/phase_6/handoffs/phase_6_copilot_post_independent_review_r9_to_r12_exact_rework_handoff_ja_20260828210944.md

Exact Rework Handoff SHA-512:
720a30f93479f388ea0454c7dbb84a4e4f6bcfb6ff3bda52d9f5aca53bcbc90eae159c692ba39c443bc8d317c49e296562d73b65a8d25dc10abf9c3f8b3db007

Exact Handoff §3のMandatory Reading全39件を指定順で全文読んでください。
この段階ではまだ実装を開始しないでください。

DigestとActive Contractを確認後、次だけを返してください。

Mandatory Reading: COMPLETE
Controller Review Digest: MATCH / MISMATCH
Exact Handoff Digest: MATCH / MISMATCH
Preserved Packages: P6-RR-R0_TO_R8_CURRENT_SOURCE
Superseded Claim: COPILOT_R3_TO_R8_COMPLETE_CANDIDATE
Open Findings: P6-CODEX-069_TO_073
Next Exact Work Unit: P6-RR-R9-WU-001
Implementation Authority: FALSE
State: WAITING_FOR_EXACT_USER_START

Mismatch時はPathとObserved Digestを正確に返してください。
返却後は停止してください。
```

### Step 3 — Exact Start

```text
Phase 6 Copilot Post-Review R9〜R12 Reworkを開始する。

P6-GOV-020とR9〜R12 Exact Rework HandoffをActive Execution Contractとして、P6-RR-R9-WU-001からP6-RR-R12-WU-010まで差分連結実行してください。

R0〜R8の成立部分を再実装、Rollbackまたは無駄に再実行しないでください。
P6-CODEX-069〜073の残件だけを修正してください。

各Work UnitでCheckpoint、各Package Entry／FinalでRecovery Indexを必ず残してください。Long Command、Canonical Verification、CompactionまたはPlatform Resource Stop前にもCurrent Recoveryを確定してください。

Progress報告、Test Failure、内部Review Finding、実装難度、Real Model Authority不足または長時間は停止理由ではありません。報告後もTrue Stop Conditionがなければ自動継続してください。

Copilot UIにOS Temporary Pathが表示されたことだけを、Copilot自身のRoot外Actionと推測しないでください。Command／Toolとの因果を確認してください。

Real Selene／Qwen3Guard、Official Provenance、Real BrowserはAuthorityがなければNOT RUN／AUTHORITY REQUIREDへ限定し、Authority不要のR9〜R12を継続してください。

R12ではS1〜S17、Original Acceptance 40＋Delta Acceptance 26、Exact Changed File SHA-512、Identity／Budget／109 Criterion／Failure Language／Recording Correlation Matrixを省略しないでください。

最大ClaimはComplete Candidateまでです。Phase 6 Closure、Git、Backup、Roadmap、Stable Shared Rule、Public Docs、ConstitutionまたはPhase 7へ進まないでください。

完了後はExact Return Handoffを作り、Codexプロジェクト責任者兼設計統括者役によるIndependent Review待ちで停止してください。
```

## 2. Package State

Controller ReviewとExact HandoffのDigestは確定済みであり、Placeholderは残っていない。
