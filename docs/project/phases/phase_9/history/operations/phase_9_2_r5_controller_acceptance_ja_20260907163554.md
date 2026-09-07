# Phase 9-2 R5 — Codex Controller受理

```yaml
document_id: phase_9_2_r5_controller_acceptance_20260907163554
document_type: controller_independent_review
document_state: implementation_accepted_pending_user_manual_recheck
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 16:35:54 JST
language: ja
authority_owner: Nazuna Research
reviewer: codex_controller
review_target: ../../handoffs/phase_9_claude_phase_9_2_evidence_oracle_and_claim_truthfulness_r5_exact_return_ja_20260907135139.md
maximum_claim: P9_2_R5_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
decision: accepted_pending_user_manual_recheck
phase_9_2_complete: false
phase_9_3_authorized: false
real_model_action_by_controller: none
controller_focused_verification: 44_passed_3_deselected
git_mutation: none
append_only: true
```

## 1. 判定

```text
ACCEPTED
internal implementation complete
User実画面Recheck pending
```

R5 Maximum Claimを受理する。R4 Controller Reviewの5 Findingは、R5の局所的なTest／Evidence／Claim訂正により閉じた。追加Claude Reworkは要求しない。

Phase 9-2 CompleteとPhase 9-3開始は、Nazuna Researchの実画面確認後に判定する。

## 2. 受理Evidence

- Restart ReadはFresh StoreからPlan、Variant Desired、Run、Frozen Configuration、Raw Evidence、Comparison Row、Metric、Evaluation Observationを読み、IdentityとDigestを相互照合する。
- Scenario 2／3は`completed`だけをPASSとし、Main／Judge InvocationとFrozen Provider IdentityをHard Assertする。
- R5実機実行でScenario 2は13.31秒、Scenario 3は7.49秒でどちらも`completed`。
- Expected ExecutedとActual Executed Providerの意味を分離し、Actual Providerが取得不能な経路はUnavailableと記録した。
- Guardは`called=None / unavailable_correlation`を維持し、Actual Dispatchを捐造していない。
- Queue中Cancel／Deadline後のShutdownでActor Call 0、Terminal State、`request_cancel()==False`を機械検証した。
- Claude報告はBackend非Model Full Suite `2665 passed / 43 deselected`、Ruff Clean、Mypy既存Baseline 43 errors / 4 files。
- Controller側Focused Verificationは`44 passed / 3 deselected`。Controllerは実Modelを追加実行していない。

## 3. R4運用違反の訂正

R4の`git stash` / `git stash pop`は、正味の差分が残らなかったこととは無関係に、明示されたGit Write禁止への違反だった。R5 Returnはこれを正確に訂正した。R5中のGit操作はRead-onlyに限定され、現時点のStashは空である。

## 4. 非Blockerの残存境界

- Main／Judge／GuardのActual Executed ProviderはExperiment Adapter上でrequest-correlatedではなくUnavailable。Configured／Active／Expectedと混同しない現状を受理する。
- Guard Invocationはrequest-correlatedでないためUnknown。Phase 9-2で追加相関機構は作らない。
- Definition Set／RAG／PresentationはProduction Adapterで未観測。Fixture比較基盤とUnavailable表示を維持する。
- 実Model Scenarioは各1 Trialであり、長期反復の安定性は保証しない。
- False-success単体Testは実Scenarioと共通Helperを使わない。現行実Scenario自体の`state == "completed"` Hard Assertは正しいため、Phase 9-2 Blockerにはしない。

## 5. 次Action

Nazuna Researchによる最小の実画面Recheckへ進む。実画面でFixture比較、同一Production Plan内の異なるVariant、Wrong Live ConfigurationのTyped Rejectが成立した後に、Phase 9-2 CompleteとPhase 9-3開始を判定する。

