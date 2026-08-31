# Phase 8 Manual URL Final Two Blockers — Claude Micro Rework Exact Handoff

```yaml
document_type: exact_handoff
document_state: final
provider: Claude
role: designer_and_implementer
task_identity: current_continued_claude_task
task_state: continued_not_fresh
phase: phase_8
package: P8-MR8-0_through_P8-MR8-3
implementation_authority: true
independent_review_authority: false
phase_8_closure_authority: false
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
created_at: 2026-08-31 14:44:55 JST
```

## 1. Objective

Codex Controller Single ReviewでProduction Composition上の実再現を確認したP8-CODEX-019／020だけをMicro Reworkし、Phase 8をUser Mac Manual Recheckへ渡せるCandidateへ収束させる。

これはCurrent Claude Taskの継続である。Fresh Task化、Bootstrap、Role Reading、Phase 8 Mandatory Reading全件のやり直しは行わない。

## 2. Differential Reading

次の4文書だけを差分正本とし、Current Working TreeをCanonical Baselineとする。

```text
docs/project/phases/phase_8/history/operations/phase_8_post_mr7_controller_single_review_adjust_ja_20260831144455.md
docs/project/phases/phase_8/handoffs/phase_8_claude_manual_url_final_two_blockers_micro_rework_exact_handoff_ja_20260831144455.md
docs/project/phases/phase_8/handoffs/phase_8_claude_post_manual_rework_controller_findings_bounded_exact_return_handoff_ja_20260831143355.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_manual_rework_controller_findings_bounded_recovery_ja_20260831143355.md
```

## 3. Preserved Baseline

```text
P8-CODEX-013〜018 = Fixedのまま保持
P8-MANUAL-002〜006 = 再実装しない
Archive／Citation／Constitution Preview／Dev Agent Foundation = 非変更
Acceptance 38 PASS／1 PARTIAL／1 USER MANUAL GATE = 根拠なく再集計しない
```

## 4. Open Findings

```text
P8-CODEX-019 Final Prompt全体でのWeb Evidence Token Budget未成立
P8-CODEX-020 Service PreflightのTransient DNS FailureがRetryへ到達しない
```

## 5. P8-MR8-0 — Entry Freeze

- Differential Readingを行う。
- P8-CODEX-019／020の2件だけをOpenにする。
- 既存MR7実装をRollbackしない。
- Recovery Indexを作り、True StopがなければP8-MR8-3まで連結実行する。

## 6. P8-MR8-1 — Final Prompt-aware Web Evidence Budget

### Required Runtime Behavior

- Web EvidenceのBudgetは、最終的にModelへ渡すMessage全体で決定する。
- 少なくともBase Policy、Conversation History、Documentation RAG、Expressive Style Notice、Context Usage Notice、Web Evidence、予約Max New Tokensを同じFinal Fitで考慮する。
- 実装はMessage組み立て順の調整、Final Candidateの再計測、必要時の有界Re-budgetなど最小差分でよい。新しいChunking基盤を作らない。
- Web Evidenceを安全に追加できない場合は、汎用`context_limit_exceeded`ではなくTyped `content_budget_exceeded`、Main Model Call 0へ収束させる。
- Context Usage Noticeの表示値の正直さを不必要に悪化させない。

### Mandatory Regression

MR7のLong CJK Testと同じ条件に次を追加する。

```text
effective_context_size = 8192
max_new_tokens = 128
long CJK Web Content
ExpressiveMode = ENABLED
ContextUsagePromptInjectionMode = ENABLED
```

次をAssertする。

```text
Terminal = COMPLETED（Truncateで収まる場合）
Final Prompt Tokens + Max New Tokens <= Effective Context
context_limit_exceeded = 0
入る余地0のCaseはcontent_budget_exceeded
そのCaseのModel Call = 0
```

## 7. P8-MR8-2 — End-to-End Transient DNS Retry

### Required Runtime Behavior

- Manual Direct URLのProduction経路全体で、最初のService Security PreflightがTransient `DNS_RESOLUTION_FAILED`となっても、既存の有界Retry Policyの範囲内で再試行できるようにする。
- Private／Loopback／Dangerous Port／Credential／Unsupported Scheme等のPermanent RejectionはRetry 0、Fetch Provider Call 0のまま保つ。
- Redirect HopごとのSecurity RevalidationとHostname Rebinding Rejectionは弱めない。
- ServiceとProviderの二重Validationを無理に重複Retryさせない。最小で有界なCompositionにする。
- Resolver・Transport・SleepはFake／Mockとし、実DNS／実Network 0で証明する。

### Mandatory End-to-End Regression

`WebKnowledgeService.fetch_direct_url()`を直接通し、次を証明する。

```text
Resolver 1回目 = socket.gaierror
Resolver後続Call = Public IP
Result = Citationありの成功
Real socket.getaddrinfo = 呼ばれない
Permanent Private／Loopback = Provider Call 0
```

Provider単体のRetry Testだけで代用しない。

## 8. P8-MR8-3 — Verification／Review／Return

1. P8-CODEX-019／020を個別にFixedへ再導出する。
2. 上記2つのMandatory Regressionを実行する。
3. MR7のFocused Test 6件をRegressionとして保つ。
4. Conversation Generation／Web KnowledgeのFocused Suite、Backend Full、Mypy、Ruff Check／Format Checkを実行する。
5. Frontend Source変更0ならFrontend Fullの再実行は不要。変更がある場合だけTypecheck／Test／Lint／Buildを行う。
6. Requirement／Negative Path／Composition／Regressionの4観点でInternal Reviewを1 Cycleだけ行う。
7. Critical／Major／MVP BlockerだけをReworkし、Minor／HardeningでReviewを無限化しない。
8. Recovery IndexとExact Return Handoffを作る。他のDocsを増やさない。

## 9. Authority／Prohibitions

### 許可

- Project Root内のP8-CODEX-019／020に必要なSource／Test／Phase 8 Recovery／Return Mutation。
- Project Root内のTest／Mypy／Ruff。
- Testが使うSystem Temp内の限定Temporary Data。

### 禁止

- Git Read／Write／Commit／Push。
- Network／Install／Download。
- Real Browser／Real Model／Real MCP。
- User `runtime_data/`へのRead／Write。
- Project Root外への任意Read／Write／Redirect。
- P8-CODEX-013〜018、Archive、Citation UI、Constitution Preview、Dev Agent Foundationの再実装。
- General Search／Automatic Search／SearXNG／Readability／Charset／Production DNS PinningへのScope拡張。
- Roadmap／Phase 8 Closure／Backup／Phase 9開始。

実装難度、Core File変更、Diff量、Pending Controller Review、Minor Findingだけで停止しない。True StopがなければP8-MR8-3まで連結実行する。

## 10. Return Condition

```text
P8-CODEX-019／020 Individual Disposition
Changed Paths
Mandatory Regression Result
MR7 Focused Regression Result
Backend Full／Mypy／Ruff Result
Network／User runtime_data／Browser／Model Action Count
Internal Review Result
Recovery Index
Exact Return Handoff
```

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK`。Phase 8 Closure／P8-ACC-040 PASS／Phase 9 READYは主張しない。
