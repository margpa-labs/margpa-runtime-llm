# Phase 8 P8-MR8 Manual URL Final Two Blockers Micro Rework — Recovery Index

```yaml
document_id: phase_8_claude_manual_url_final_two_blockers_micro_rework_recovery_20260831150330
document_type: recovery_index
document_state: frozen
language: ja
created_at: 2026-08-31 15:03 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_8
execution_scope: P8-MR8-0_through_P8-MR8-3
入力Controller_Single_Review: phase_8_post_mr7_controller_single_review_adjust_ja_20260831144455.md
入力Controller_Single_Review_sha512: 24ef29271a91193e1570ded7635bb18c06a91f5d86f2431796c589bb98d779eac9bc6961e46b367b1eb5a125b71ec3a75186c298a44d21c27a041892bc39bf01
入力Handoff: phase_8_claude_manual_url_final_two_blockers_micro_rework_exact_handoff_ja_20260831144455.md
入力Handoff_sha512: 1a684c5d3df63f7df5b0a841533ea6d043def9fae9bd25c29c9d1fd5158afad53789964b7d7a6b72ed33123f6ab7abcd23671f71d18b42af5c50b45d51d96cfa
対象Finding: P8-CODEX-019_and_020
```

## 1. 完了状態サマリ

```yaml
p8_codex_019_disposition: RESOLVED
p8_codex_020_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
major_open: 0
internal_review_rework_performed: 0
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
```

## 2. Finding別詳細

### 2.1 P8-CODEX-019 — Final Prompt-aware Web Evidence Budget（P8-MR8-1）

根本原因：`_inject_web_evidence()`（P8-MR7-4）はWeb Evidenceを注入する時点の`messages`だけを基準に
Token Budgetを計算していたが、`_build_request()`はその**後で**`expressive_style_notice`と
`context_usage_notice`を追加する。Web Evidenceが当時の残りBudgetを使い切ると、後置Noticeの分だけ
Final Promptが上限を超え、既存の汎用Final Token Check（`_build_request()`末尾）が`context_limit_exceeded`
を再度Raiseしていた。Controllerが同じLong CJK／8192 ContextにExpressiveとContext Usageだけを有効化して
実測し、`terminal: error, code: context_limit_exceeded, model_calls: 0`を確認していた。

実装：

- `_reserved_tokens_for_post_evidence_notices()`（新規）：Web Evidence注入**前**の`messages`に対し、
  Expressive Style Notice（固定文字列、決定的）とContext Usage Notice（`effective_context_size`自体を
  Worst-case Placeholderとして使い、実際にあり得る最大桁数で計測——安全な上限であり過小Reserveにならない）
  を仮に追加した場合の追加Token数を実Token Counterで計測し、その差分を返す。
- `_inject_web_evidence()`へ`reserved_tokens_for_notices: int = 0`引数を追加し、
  `available_tokens = effective_context_size - requested_max_new_tokens - base_tokens -
  reserved_tokens_for_notices`という形でBudget計算へ組み込んだ。既存の`content_budget_exceeded`
  （Base Conversation単独超過／Web Evidence自体が入らない場合の2分岐）はこの拡張後もそのまま機能する
  ——新しいRaise分岐を追加する必要はなかった。
- `_build_request()`で、Web Evidence注入の直前にこのReservationを計算し、Web Evidence注入時にだけ渡すよう
  配線した。Web Evidenceが要求されていないTurn（`manual_web_evidence_url`未指定）では、このReservation計算
  自体をSkipする最適化も併せて行った（`_inject_web_evidence()`がどのみち値を使わずEarly Returnするため、
  無駄なToken Counter呼び出しを避けた）。

Mandatory Regression：Handoff §6の完全な条件（`effective_context_size=8192`、`max_new_tokens=128`、
Long CJK Web Content、`ExpressiveMode=ENABLED`、`ContextUsagePromptInjectionMode=ENABLED`）で新規Test
`test_manual_web_evidence_cjk_content_fits_8192_with_notices_enabled`を追加し、Terminal=COMPLETED、
Final Prompt Tokens + Max New Tokens <= 8192、`context_limit_exceeded`のERROR Event 0件を確認した。
入る余地が全く無いCase用に`test_manual_web_evidence_content_budget_exceeded_when_notices_leave_zero_room`
も追加し、`content_budget_exceeded`とModel Call 0を確認した。

Regression Guard：`reserved_tokens_for_notices`の計算・伝播を一時的に無効化（`= 0`固定）し、新規Testが
実際にController Probeと全く同じ`context_limit_exceeded`でFailすることを確認してから復元、diff一致を
確認した。

### 2.2 P8-CODEX-020 — End-to-End Transient DNS Retry（P8-MR8-2）

根本原因：`HttpxWebFetchProvider`自体のTransient DNS Retryは正しく機能し、そのUnit Testも通過していたが、
Production経路では`WebKnowledgeService.fetch_direct_url()`／`search_and_fetch()`が**その手前で**独立した
`validate_url_before_connect()`呼び出し（Preflight Validation）を1回だけ行っていた。この最初の1回が
Transient `DNS_RESOLUTION_FAILED`だと、ServiceはRetryなしで直ちに`url_rejected`（`network_calls_made=0`）
を返し、Fetch ProviderのRetry Budgetへは一度も到達しなかった。Controller Probe実測：
`failure: url_rejected, resolver_calls: 1, fetch_calls: 0, citations: 0`。

実装：

- `web_knowledge_service.py`へ`DEFAULT_PREFLIGHT_MAX_RETRIES=2`（`HttpxWebFetchProvider.DEFAULT_MAX_RETRIES`
  と同じ値だが、Application層がAdapter層のConstantに依存しないよう独立定義）、
  `DEFAULT_PREFLIGHT_RETRY_BACKOFF_SECONDS=0.2`、`_PREFLIGHT_RETRYABLE_REASONS = {DNS_RESOLUTION_FAILED}`
  （Preflight ValidationはDNS解決しか行わないため、Retry対象になり得るReasonはこれだけ）を追加した。
- `WebKnowledgeService.__init__`へ`preflight_max_retries`／`preflight_retry_backoff_seconds`／`sleep_fn`
  を追加（Production既定はTop-levelの`time.sleep`、Testは`sleep_fn=lambda seconds: None`で実待機なしに
  検証可能）。
- 新規`_validate_url_with_retry(url)`Method：`HttpxWebFetchProvider.fetch()`と対称的な、固定Budget内での
  Retry Loop。`search_and_fetch()`と`fetch_direct_url()`の両方の呼び出し箇所を、直接の
  `validate_url_before_connect(url, resolver=self._resolver)`からこのMethod経由へ置き換えた——両経路が
  同じPreflight Validation Patternを共有しているため、片方だけ直すと非対称になる。
- Permanent Rejection（Private／Loopback／Credentials／Dangerous Port／Unsupported Scheme等）は
  `_PREFLIGHT_RETRYABLE_REASONS`に含まれないため、Retryなしで初回失敗のまま——`network_calls_made`の
  既存Semantics（Provider呼出数に近い、既存Observability Debtとして保留中）も無変更。

Mandatory End-to-End Regression：`WebKnowledgeService.fetch_direct_url()`を直接通す新規Test 3件：
`test_fetch_direct_url_retries_a_transient_preflight_dns_failure_end_to_end`（Resolver 1回目
`socket.gaierror`→後続Call Public IP→Citationありの成功、実`socket.getaddrinfo`は呼ばれない）、
`test_fetch_direct_url_permanent_dns_failure_still_fails_on_the_first_attempt`（恒久的Failureは3回で
確実に打ち切り、無限Retryにならない）、
`test_fetch_direct_url_permanent_private_address_rejection_makes_zero_provider_calls`（Permanent
Rejectionは1回で確定、Provider Call 0）。

Regression Guard：`_validate_url_with_retry()`を一時的に単純な1回呼び出しへ差し替え、新規Testが実際に
Controller Probeと全く同じ`url_rejected`／`network_calls_made=0`でFailすることを確認してから復元、
diff一致を確認した。

## 3. Changed Paths

```text
# Backend Source
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py

# Backend Test
tests/unit/conversation/test_conversation_generation.py
tests/unit/web_knowledge/test_web_knowledge_service.py
```

明示的に変更していないもの：P8-CODEX-013〜018の実装本体（Resolver Injection、ERROR-terminal Persistence、
Schema 1/2 Upgrade、Raw Fetch Contract）、P8-MANUAL-002〜006（Web Citation Metadata、Archive同期、
Constitution Layout、Dev Agent Fixture／Approval、Button Contrast）、P8-CR系、P8-RW6／7——いずれも
Rollback・再実装していない。`HttpxWebFetchProvider`自体（Hop-level Retry）も無変更——今回のGapは
その手前のService-level Preflightだった。

## 4. Focused／Canonical Verification

```yaml
p8_codex_019_regression:
  test: test_manual_web_evidence_cjk_content_fits_8192_with_notices_enabled
  test_2: test_manual_web_evidence_content_budget_exceeded_when_notices_leave_zero_room
  result: both pass
p8_codex_020_regression:
  test: test_fetch_direct_url_retries_a_transient_preflight_dns_failure_end_to_end
  test_2: test_fetch_direct_url_permanent_dns_failure_still_fails_on_the_first_attempt
  test_3: test_fetch_direct_url_permanent_private_address_rejection_makes_zero_provider_calls
  result: all 3 pass
mr7_focused_regression:
  note: >-
    Controllerの6 Test（MR7 Context Budget 4経路、Httpx Provider Transient DNS Retry、Service Resolver
    Injection）はBackend Full Suiteに含まれ、全通過を確認した——個別の再実行は行わず、Full Suite結果を
    根拠とした。
backend_full_suite:
  command: "uv run pytest -q"
  result: "2191 passed, 7 deselected"
  deselected_reason: "model_smoke marker, addopts -m 'not model_smoke' — intentional, unrelated to this Package"
  baseline_before_this_package: "2186 passed, 7 deselected"
ruff_check:
  result: "All checks passed"
ruff_format_check:
  result: "563 files already formatted"
mypy:
  result: "Success: no issues found in 346 source files"
frontend:
  note: "Frontend Source変更0のため、Handoff §8.5の指示どおりFrontend Full再実行は行っていない。"
regression_guard_verification:
  method: >-
    P8-CODEX-019／020の両修正について、実際にFail-fastする状態（Reservation計算無効化、Retry Loop単純化）
    を一時的に再現し、新規TestがController Probeと全く同じ失敗Shapeで実際にFailすることを確認してから
    修正・復元し、diffで完全一致を確認した。
```

## 5. Internal Review Finding Ledger

Requirement／Negative Path／Composition／Regressionの4観点で1 Cycle実施。

```yaml
requirement:
  finding: none
  note: "P8-CODEX-019／020の両方をHandoff §6／§7の Required Runtime Behavior／Mandatory Regressionどおりに
    解消したことを本Index §2で確認した。"
negative_path:
  finding: none
  note: "Permanent Rejection（Private／Loopback／Dangerous Port等）はRetry対象Setに含まれないため初回で
    確定することを新規Testで確認した。恒久的Transient風Failure（毎回gaierror）も固定Budget（3試行）で
    確実に打ち切られ、無限Retryにならないことを確認した。"
composition:
  finding: none
  note: "ServiceのPreflight Retry（最大3試行）とProviderのHop-level Retry（最大3試行、Redirect全体で共有）
    は独立しており、両方が同時にTransientな場合の理論上限は有界（最大9回のResolver呼び出し）——Handoffが
    禁止する『無理な重複Retry』（片方の失敗をもう片方が無限に補償する設計）ではなく、それぞれが独立して
    有界であることを確認した。"
regression:
  finding: none
  note: "Backend Full Suite 2191 passed（Baseline 2186から純増5件、既存Testの結果反転なし）、Mypy／Ruff
    Check／Ruff Format Check全てClean。P8-MR7の全実装（Resolver Injection、ERROR-terminal Persistence、
    Schema 1/2 Upgrade、Raw Fetch Contract、元のCJK/History Budget Test）は無変更のまま全通過を確認した。"
critical_or_major_found_and_reworked: 0
minor_optimization_applied: >-
  Web Evidence未使用のTurnで`_reserved_tokens_for_post_evidence_notices()`の計算自体をSkipするGuardを
  実装時に追加した（Correctnessには影響しない、無駄なToken Counter呼び出しを避けるだけの最適化）。
```

## 6. Process Action Inventory

```yaml
git_read_or_write_executed: false
network_used: false
install_used: false
real_browser_used: false
real_model_used: false
real_mcp_used: false
backup_used: false
project_root_外_access_executed: 0
runtime_data_read_or_written: false
phase_8_closure_claimed: false
roadmap_touched: false
phase_9_entered: false
p8_codex_013_through_018_reimplemented: false
p8_manual_002_through_006_reimplemented: false
acceptance_recount_performed: false
```

全新規Testは`httpx.MockTransport`不要（`WebKnowledgeService`単体経由）で、Injected `resolver`／
`socket.getaddrinfo`をAssertion Errorへ差し替えるMonkeypatch Guardのいずれかで完結し、実Networkに
一切到達していない。`sleep_fn`をInjectableにしたことで、Retry Testも実待機なしで即座に完了する。

## 7. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK。
Phase 8 Closure、P8-ACC-040 PASS、Phase 9開始のいずれもClaimしていない。
Acceptance集計（38 PASS／1 PARTIAL／1 USER MANUAL GATE = 40）は根拠なく再集計していない——Handoff §3の
指示どおり据え置いた。
```
