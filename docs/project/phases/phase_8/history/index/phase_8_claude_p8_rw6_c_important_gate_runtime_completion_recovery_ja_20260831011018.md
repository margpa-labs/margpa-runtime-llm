# P8-RW6-C — Important Gate Runtime Completion — Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-RW6-C
finding: P8-CODEX-007
state: complete
provider: Claude
created_at: 2026-08-31 01:10 JST
```

## 結論

`RunState.AWAITING_COMPLETION_APPROVAL`（新設）、`CompletionApprovalEvidence`（`ApprovalEvidence`とは構造的に別Type、`step_id`／`tool_id`を持たない）、`submit_completion_approval()`を実装。`important_gate_only`では全Step成功後もRun-level Completion Gateで停止し、明示Approvalなしに`completed`へ自動収束しない。Generic Gate Engineが8 Reason全てを扱えることをParametrized Fixture Testで証明（6 Non-Completion Reason個別）。Step ApprovalとCompletion Approvalの相互不流用をTestで実証。FrontendのDevAgentPanel／DevAgentPanel.testも実Flowに合わせて更新（新規UI追加なしではUser実画面Demo Runが行き詰まるため必須対応）。

Completion Gate分岐を一時的に無効化しRegression 4件が実際に失敗することを確認した上で復元（diff上Fix版と完全一致）。

## Changed Paths

```text
src/margpa_runtime_llm/modules/dev_agent/contracts.py（AWAITING_COMPLETION_APPROVAL、CompletionApprovalEvidence、completion_approvals、Validator拡張）
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py（_has_completion_evidence()、Gate分岐、submit_completion_approval()）
src/margpa_runtime_llm/modules/dev_agent/__init__.py
src/margpa_runtime_llm/web/dev_agent_contracts.py（CompletionApprovalRequest/Response、completion_approvals Field）
src/margpa_runtime_llm/web/dev_agent_routes.py（POST /runs/{id}/completion-approval）
tests/unit/dev_agent/test_run_service.py（新規14件：6 Reason Parametrize + Pending/Denied/Approved/Rejects/Cancel/Restart/Cross-Scope/Cross-Run）
tests/integration/dev_agent/test_dev_agent_web_app.py（既存4件Update：Golden Path REST／Restart／Concurrency）
frontend/src/components/DevAgentPanel.tsx（Completion Gate UI追加）
frontend/src/components/DevAgentPanel.test.tsx（実Flowに合わせ更新）
frontend/src/api/client.ts（submitDevAgentCompletionApproval）
frontend/src/types.ts（DevAgentRunState拡張）
frontend/src/i18n/translations.ts
```

## Focused Verification

```yaml
dev_agent_unit_and_integration: 105 passed
regression_before_fix_reproduction: confirmed_fails_without_the_gate_branch（4 Test）
backend_full_suite_after: 2113 passed, 7 deselected
frontend_full_suite: 296 passed
frontend_typecheck_lint_build: clean
```

Acceptance Target `P8-ACC-034`: PASS（Completionを含む8 Reason全てがGeneric Gate Engineで扱えることを実証、Completion自体がRun-level Important Gateとして実配線）。既存P8-CODEX-009（Manual SheetとClick数の不一致）はHandoff §4の指示どおり本Packageでは修正していない（別課題として保持）。
