# Phase 9-1 Real Selene／Qwen3Guard Mandatory Closure Correction

```yaml
document_id: phase_9_1_real_selene_qwen3guard_mandatory_closure_correction_20260901001700
document_state: final_append_only_correction
language: ja
created_at: 2026-09-01T00:17:00+09:00
phase: phase_9
program: phase_9_1
authority: user_explicit_correction
current_state: real_dedicated_activation_required
phase_9_1_closure: blocked_by_mandatory_real_artifact_execution
```

## 1. User Correction

Userは2026-09-01、Phase 9-1の最低成立条件について次を明示した。

```text
Real Selene／Qwen3Guardを「今回実行するか」の任意選択としない。
Phase 9-1はSelene／Qwen3Guardを実際に使用可能な状態へすることが最低条件である。
```

## 2. Corrected Meaning of RESOURCE_GATED／FAILED

`RESOURCE_GATED／FAILED`は、Preflight／Load／Inferenceの途中失敗を虚偽PASSにしないためのTyped Intermediate Stateである。Phase 9-1の最終成立条件、PASS、ClosureまたはPhase 9-2への自動移行代替ではない。

Current User-authorized Mac Baselineでは、次の両方が必須である。

```text
Selene:
  Real Artifact Preflight
  Real Candidate Load
  Real Inference
  Configured = Active = Executed Identityの整合
  Judge Evidence
  OFF／Stop後の安全なUnload

Qwen3Guard:
  Real Artifact Preflight
  Real Candidate Load
  Real Inference
  Target／Category／Line Protocol／Evidence Identityの整合
  Configured = Active = Executed Identityの整合
  OFF／Stop後の安全なUnload
```

必須Artifactが未配置、互換性不明、またはCurrent Hardware上で失敗した場合は、原因をStage別Evidence化した上で解消作業を続ける。新しいNetwork／License／Cost／Root外Mutationが必要になった場合だけ、その具体的GateをUserへ戻す。

## 3. Superseded Statements

次のHistorical StatementはEvidenceとして改変しないが、Current Phase 9-1 Closure Semanticsとしては本CorrectionがSupersedeする。

- `docs/project/phases/phase_9/history/operations/phase_9_1_corrected_user_manual_recheck_sheet_ja_20260831234930.md`の「Authorityがない場合はDedicated Smokeを実施せずRESOURCE_GATEDを保持」。
- `docs/project/phases/phase_9/history/operations/phase_9_1_post_claude_quota_acceptance_disposition_addendum_ja_20260831234930.md`のP9-ACC-008／011を残したままのComplete Candidate表現。
- `docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_final_re_review_acceptance_receipt_ja_20260901001158.md`の「Real Artifact Disposition」を任意選択と読める表現。

P9-CODEX-001〜005のSource／Test／Docs Finding解消自体は無効化しない。ただし、Phase 9-1全体はReal Dedicated Artifactの両方がPASSするまでComplete Candidateではない。

## 4. Controller Failure Correction

Controllerは`RESOURCE_GATED`を「今回実行するかUserが選べる状態」と説明し、Phase 9-1の中心目的を任意化した。これはScope／Closure Stop Lineの判定Failureである。

今後のExact Next Actionは「実行するか選ぶ」ではなく、「Selene／Qwen3Guardを実Artifactで成立させ、User Macで確認する」である。

## 5. Claims Not Made

```text
Real Selene PASS: NOT YET
Real Qwen3Guard PASS: NOT YET
Phase 9-1 Complete Candidate: NOT CURRENTLY CLAIMED
Phase 9-1 Closure: NOT CLAIMED
Phase 9-2 Start: NOT AUTHORIZED
```
