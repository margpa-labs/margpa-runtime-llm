# Phase 8 P8-MR7 — Codex Controller Single Independent Review

```yaml
document_type: controller_independent_review
document_state: final
phase: phase_8
review_target: P8-MR7-0_through_P8-MR7-6
review_result: ADJUST
reviewed_at: 2026-08-31 14:44:55 JST
reviewer_role: project_controller_and_design_governor
product_quality_target: poc_mvp
review_cycle: single_bounded_cycle
```

## 1. 結論

P8-MR7で対象としたP8-CODEX-013〜018は、Source・Focused Test・Digest・Format Checkの範囲でそれぞれ有効に是正された。特に次はPreserved Baselineとする。

```text
ResolverのConstructor InjectionとDNS Hermetic Test
ERROR-terminal Web Evidenceの永続化
Web Citation Schema 1／2のReader-side Upgrade
CJK／History／Max New Tokensを考慮したWeb Evidence Budgetの基盤
User実構成に合わせたRecheck Sheet
P8-ACC-001〜040の38 PASS／1 PARTIAL／1 USER MANUAL GATE集計
```

ただし、「Testした局所経路では成立するが、実際のProduction Compositionでは同じFailureが再現する」2件をController Probeで確認した。いずれもEnterprise Hardeningではなく、Userがすでに実画面で再現したManual URL取得安定性／Context上限Failureに直結する。この2件だけをMicro Rework対象とし、判定は`ADJUST`とする。

## 2. Review Evidence

### 2.1 Return Digest

```text
Expected: 74568e75a968d115046785cfc0ea1ecbe56672940d4bdfee45b5e97ca8c7addf3ee65460d9cfab3aba097f41878de95c850c041008f0be31cf520f083eabb624
Observed: 74568e75a968d115046785cfc0ea1ecbe56672940d4bdfee45b5e97ca8c7addf3ee65460d9cfab3aba097f41878de95c850c041008f0be31cf520f083eabb624
Result: MATCH
```

### 2.2 Focused Verification

MR7のContext Budget 4経路、Httpx ProviderのTransient DNS Retry、Service Resolver Injectionを実行し、6 Testは全件PASSした。

```text
6 passed in 0.28s
557 files already formatted
```

これによりMR7の局所実装を無効とはしない。次の2件は、その局所Test間のComposition Gapである。

## 3. Open Findings

### P8-CODEX-019 — Web Evidence Budget後のSystem NoticeでOpaque Context Failureが再発する

```yaml
severity: major_mvp_blocker
impact: user_reproduced_context_limit_failure, P8-CODEX-016
disposition: micro_rework_required
```

`ConversationGenerationService._build_request()`は、先に`_inject_web_evidence()`で残りToken Budgetを計算した後で、`expressive_style_notice`と`context_usage_notice`を追加する。そのためWeb Evidenceが当時の残りBudgetを使い切ると、後置NoticeによってFinal Promptが上限を超え、再び汎用`context_limit_exceeded`へ落ちる。

ControllerがMR7と同じLong CJK／8192 ContextにExpressiveとContext Usageだけを有効化した実測：

```text
terminal: error
code: context_limit_exceeded
model_calls: 0
```

Reference：

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  _build_request(): Web Evidence -> Expressive Notice -> Context Usage Notice -> Final Token Check
tests/unit/conversation/test_conversation_generation.py
  P8-MR7 Context Budget Testに上記2 Mode併用Caseなし
```

今回のRequirementは「Web本文を固定文字数で切る」ではなく、「実際にModelへ渡すFinal Prompt全体が収まる」である。したがってClosure前の最小修正対象とする。

### P8-CODEX-020 — Service Preflightの一時DNS FailureがProvider Retryへ到達しない

```yaml
severity: major_mvp_blocker
impact: manual_url_fetch_reliability, P8-MANUAL-001
disposition: micro_rework_required
```

`HttpxWebFetchProvider`にはTransient DNS FailureのRetryがあり、そのUnit TestもPASSする。しかしProductionのManual URL経路は、その手前で`WebKnowledgeService.fetch_direct_url()`が別のDNS Validationを1回行う。この最初の1回がTransient Failureだと、Serviceが直ちに`url_rejected`を返し、ProviderのRetryに到達しない。

Controller Probe実測：

```text
failure: url_rejected
resolver_calls: 1
fetch_calls: 0
citations: 0
```

MR7のTransient DNS Retry Testは`HttpxWebFetchProvider.fetch()`を直接呼び、Service経由のEnd-to-End Caseではない。実画面Manual URL取得の安定性はService Compositionで決まるため、これもClosure前の最小修正対象とする。

## 4. Preserved／Stop Line

P8-CODEX-013〜018、P8-MANUAL-002〜006、Archive、Citation、Constitution Preview、Dev Agent Foundationを再実装しない。次Reworkは019／020のSource・Test・Recovery／Returnだけに限定する。

次は今回のClosure Blockerにしない。

```text
Token Counter自体が存在しない別Runtimeの将来Policy
Production-grade DNS Pinning／Rebinding完全耐性
Charset／JavaScript Rendering／Readability完成
General Search Provider／Automatic Search
Phase 6 Semantic／Selene／Qwen3Guard残件
```

## 5. Controller Disposition

```yaml
current_claim: ADJUST_REQUIRED
ready_for_user_manual_recheck: false
phase_8_closure_ready: false
next_exact_work_unit: P8-MR8-0
maximum_next_return_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
required_review_cycles_in_next_task: 1
```
