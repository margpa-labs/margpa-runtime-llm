# Phase 8 P8-MR8 — Codex Controller Targeted Review

```yaml
document_type: controller_targeted_review
document_state: final
phase: phase_8
review_target: P8-MR8-0_through_P8-MR8-3
review_result: PASS
reviewed_at: 2026-08-31 15:12:08 JST
reviewer_role: project_controller_and_design_governor
product_quality_target: poc_mvp
review_cycle: single_bounded_cycle
ready_for_user_manual_recheck: true
phase_8_closure_ready: false_pending_user_manual_recheck
```

## 1. 結論

P8-CODEX-019／020は対象としたProduction Compositionで是正された。P8-MR7以前のPreserved BaselineへのRegressionは検出されず、User Mac Manual Recheckへ進める。追加Reworkは不要。

```text
P8-CODEX-019: PASS
P8-CODEX-020: PASS
Open Critical／Major／MVP Blocker: 0
Next Gate: User Mac Manual Recheck
```

## 2. Review Evidence

### 2.1 Return Digest

```text
Expected: 5676881c8d8121eaa8ad1b30593dc8e27ecbfa2667275fb6cf68be407cb4e7d209793c4bd3bc34b97f0ceae7a837b1307ac345f7408cdaa31b13828b60494b3e
Observed: 5676881c8d8121eaa8ad1b30593dc8e27ecbfa2667275fb6cf68be407cb4e7d209793c4bd3bc34b97f0ceae7a837b1307ac345f7408cdaa31b13828b60494b3e
Result: MATCH
```

### 2.2 Mandatory Regression

```text
Long CJK／8192／Expressive ON／Context Usage ON: PASS
Notice予約後のZero-room -> content_budget_exceeded／Model Call 0: PASS
Service Preflight Transient DNS -> Retry -> Citation: PASS
Permanent DNS Failure -> 有界3 Attempts: PASS
Private Address -> Retry 0／Provider Call 0: PASS

5 passed in 0.21s
```

### 2.3 Focused／Canonical

```text
Conversation Generation／WebKnowledge Focused: 111 passed
Backend Full: 2191 passed, 7 deselected
Mypy Source: Success, 346 source files
Ruff Check: All checks passed
Ruff Format: 557 files already formatted
Frontend: Source変更0のため再実行不要
```

## 3. Finding Disposition

### P8-CODEX-019 — PASS

Web EvidenceをTruncateする前に、後置されるExpressive Style Notice／Context Usage NoticeのTokenを同じCounterでReserveする。Controllerが再現したLong CJK／8192条件でFinal Promptが上限内へ収まり、汎用`context_limit_exceeded`は再現しなかった。

### P8-CODEX-020 — PASS

`WebKnowledgeService` Preflight自身にDNS Failureだけを対象とする有界Retryが入り、Direct URLとSearch Resultの両方が同じHelperを通る。Private／Loopback等のPermanent Rejectionは従来どおり1回目で拒否し、Provider Call 0を保つ。

## 4. Non-blocking Observation

```yaml
id: P8-OBS-001
severity: trivial_test_hygiene
priority: P3
closure_blocker: false
```

`tests/unit/web_knowledge/test_web_knowledge_service.py`のRedirect Authority Testに、`GENERAL`をAssertした直後に`OFFICIALでない`をAssertする同義の2行がある。RuntimeやTest結果に影響はないが、`mypy src tests`で後者が`comparison-overlap`となる。

Current Canonical Claimの`mypy src`はCleanであり、Backend 2191 TestもPASSしている。PoC／MVPのUser主経路、Data、Safety、UIに影響しないため、この冗長Assertの1行整理だけでManual Recheckを止めない。次回同Test Fileを変更する際のMechanical Cleanup対象とする。

## 5. Controller Disposition

```yaml
current_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
ready_for_user_manual_recheck: true
additional_rework_required: false
phase_8_closure_ready: false
phase_8_closure_blocker: user_manual_recheck_only
```

User Manual Recheckの対象は、変更されたManual URL／Evidence／Archive／Constitution Layout／Dev Agent Fixture／Button Contrastの差分に限定する。Phase 8 Acceptance 40件を最初から再実施しない。
