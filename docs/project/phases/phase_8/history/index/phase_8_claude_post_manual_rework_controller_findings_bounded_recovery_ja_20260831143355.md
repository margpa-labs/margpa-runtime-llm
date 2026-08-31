# Phase 8 P8-MR7 Post-User-Manual Rework Controller Findings — Recovery Index

```yaml
document_id: phase_8_claude_post_manual_rework_controller_findings_bounded_recovery_20260831143355
document_type: recovery_index
document_state: frozen
language: ja
created_at: 2026-08-31 14:33 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_8
execution_scope: P8-MR7-0_through_P8-MR7-6
入力Controller_Review: phase_8_post_user_manual_rework_controller_independent_review_adjust_ja_20260831134826.md
入力Controller_Review_sha512: d00f8f9e27bae53dcb60ebc9eff2131a973a839c4dcc13aa312952d8602801bca8cf009998239cfdbb05830d8a6dfd5d895a80b2d3093dbdc8219659df5b221d
入力Handoff: phase_8_claude_post_user_manual_rework_controller_findings_bounded_exact_handoff_ja_20260831134826.md
入力Handoff_sha512: 2fe2c909f8b72f9a7156bbf1bb7a97f183bdde9bb086ed32da8924b380378d2697a5abd3ab7faa86a5dca9f2607a7e4cf504c406015fcbab07b1e393f9db9759
対象Finding: P8-CODEX-013_through_018
```

## 1. 完了状態サマリ

```yaml
p8_codex_013_disposition: RESOLVED
p8_codex_014_disposition: RESOLVED
p8_codex_015_disposition: RESOLVED
p8_codex_016_disposition: RESOLVED
p8_codex_017_disposition: RESOLVED
p8_codex_018_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
major_open: 0
internal_review_rework_performed: 2
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
```

## 2. Finding別詳細

### 2.1 P8-CODEX-013 — Resolver Injection／Test Hermeticity（P8-MR7-1）

根本原因：`WebKnowledgeService.fetch_direct_url()`と`HttpxWebFetchProvider._attempt_one_hop()`はどちらも
`url_security.validate_url_before_connect()`を直接呼び、DNS解決に実`socket.getaddrinfo()`しか使えなかった。
`tests/unit/web_knowledge/`には`conftest.py`のAutouse Fixtureで実DNSを遮断する既存の仕組みがあったが、
`tests/unit/conversation/test_conversation_generation.py`にはこの仕組みが無く、Manual Web Evidence Test 4件が
実DNSに依存していた。

実装：

- `url_security.py`へ`Resolver`型（`Callable[[str, int], Sequence[GetAddrInfoResult]]`）と`default_resolver()`
  （実`socket.getaddrinfo`への薄いWrapper）を追加し、`validate_url_before_connect(url, resolver=default_resolver)`
  とした。既存の`monkeypatch.setattr(socket, "getaddrinfo", ...)`ベースのTestは`default_resolver`が同じSymbolを
  経由するため無変更で動作し続ける。
- `WebKnowledgeService.__init__`／`HttpxWebFetchProvider.__init__`の両方へ`resolver: Resolver = default_resolver`を
  追加し、両Boundaryの`validate_url_before_connect()`呼び出しへ伝播した——一方だけFakeでもう一方が実DNSを呼ぶ
  状態を作らない設計。
- `test_conversation_generation.py`の`_web_knowledge_service()`Helperへ`resolver=_fake_public_resolver`を注入し、
  Controllerが実失敗させた4 Testを含む全Manual Web Evidence TestをNetwork 0にした。
- 新規Determinism Test 10件を追加：`test_url_security.py`3件（Resolver Parameter自体の直接検証、実`socket.
  getaddrinfo`をAssertion Errorへ差し替えてFakeが確実に使われることを証明）、`test_web_knowledge_service.py`3件
  （Service Boundaryでの同様の証明、Permanent Rejection含む）、`test_httpx_fetch_provider.py`4件（Hop Boundary、
  Public IPv4／IPv6、Transient DNS Failure→Retry成功、Permanent Rejection）。

Regression Guard：Controller指定4 Testを`./.venv/bin/pytest`で実行し`4 passed in 0.21s`を確認。

### 2.2 P8-CODEX-014 — ERROR-terminal Web Evidence Persistence（P8-MR7-2）

根本原因：`fail_generation()`（`persistent_conversation_service.py`）は`complete_generation()`と異なり
`web_search_result`を一切受け取らず、`_transition_terminal_or_generating()`も`web_citation_evidence`を
`_commit()`へ渡していなかった。Fail-closed Grounding（P8-MR1）でERROR終了したTurnはWeb Citation Evidenceを
一切永続化できなかった。

実装：

- `fail_generation()`／`_transition_terminal_or_generating()`へ`web_search_result: WebSearchAndFetchResult | None`
  を追加し、`complete_generation()`と同じ`build_turn_web_citation_evidence()`を使って`web_citation_evidence`を
  構築、`_commit()`へ渡すようにした。
- ERROR Event経路の呼び出し元（`_generate_pending_turn()`のERROR分岐）で`web_search_result=session.
  web_search_result`を明示的に渡した。
- 実装中に発見した真の欠陥：`CommitConversation`（`conversation_store.py`）の`model_validator`が
  「`web_citation_evidence`はCOMPLETED状態のTurnにしか付けられない」というInvariantを持っており、私の配線だけでは
  `pydantic_core.ValidationError`（"web citation evidence must reference a completed turn in the commit"）で
  実際にFailした。この検証は`_persist_terminal()`が例外を`PersistentConversationError`へ包むため、Live SSEでは
  「保存できませんでした」という不透明な失敗になっていたはずである。Invariantを「COMPLETED**または**FAILED」へ
  限定的に緩和し、Documentation RAGの`citation_evidence`側のInvariant（COMPLETED限定）は無変更のまま維持した。
- 新規Test：`test_persistent_citation_evidence.py`に`WebEvidenceErrorSession`（実際にWEB_EVIDENCE→ERRORの順で
  Eventを発火する、既存の`WebCitingSession`のようにCOMPLETEDを偽造しない）を追加し、実ERROR経路→Restart相当の
  再Openで、Aggregate Reasonと具体的なRejection Reason（`dns_resolution_failed`）の両方が復元されることを
  証明した。

Regression Guard：`CommitConversation`のInvariant緩和前に一度実際に上記ValidationErrorを再現してから修正、
Test再実行で成功を確認した（原因調査自体がRevert-and-reproduceを兼ねている）。

### 2.3 P8-CODEX-015 — Web Citation Schema 1／2 Backward Compatibility（P8-MR7-3）

根本原因：`WebCitation.transformation`（Schema 2→3で必須化）と`requested_url`（Schema 1→2で必須化）は、
`_decode_web_citation_evidence()`が`PersistedTurnWebCitationEvidence.model_validate()`へ生のPayloadをそのまま
渡すため、旧Schema Recordでは`ValidationError`となり`WebCitationUnavailable(reason="corrupt_record")`へ
Fail-closed退行していた。「安全なDegrade」であって「Backward Compatibility」ではないというController指摘どおり。

実装：

- `sqlite_conversation_store.py`へ`_upgrade_web_citation_payload(payload, schema_version)`（純粋関数、Diskの
  Historical Recordは書き換えない）を追加。Schema 1では`requested_url`が無ければ`canonical_url`と同値を補い
  （「当時Redirect前URLを別途保存していた」と虚偽主張しない、正直なCompatibility Projection）、Schema 2では
  `transformation`が無ければ既存の`classify_content_transformation(content_type)`で導出する。
- `_decode_web_citation_evidence()`が`model_validate()`の直前でこのUpgradeを適用するよう変更。
- 新規Test File `test_web_citation_evidence_sqlite_store.py`（3 Test）：実際にSchema 3のRecordをCommitしてから、
  実Encoded SQLite Row（`citations_json`／`citations_sha512`／`citation_schema_version`列）を直接改変してSchema
  1／2相当を再現し、正しく復元されることを証明した。

Regression Guard：Upgrade呼び出しを一時的に無効化し、新規2 Test（Schema 1／2）が実際に`corrupt_record`へ
Failすることを確認してから復元、Diff一致を確認した。

### 2.4 P8-CODEX-016 — Context-aware Evidence Budget／Raw Content Contract（P8-MR7-4）

2つの独立した欠陥を修正した。

**Raw Fetch Contract**：`WebEvidence.fetched_content`の`MAX_FETCHED_CONTENT_CHARACTERS`が固定200,000文字で
あった一方、`WebSearchFeatureConfig.max_response_bytes`は既定1,500,000／最大10,000,000 Byteを許容していた。
Byte Cap内で正常に取得できたContentが`WebEvidence`構築時に未分類の`ValidationError`でCrashし得た。
`MAX_FETCHED_CONTENT_CHARACTERS`を`max_response_bytes`の上限（10,000,000）へ引き上げた——UTF-8のDecoded文字数は
元のByte数を超えないため、Byte Cap自体（Security Boundary）を弱めることなく数学的に安全である。実際に
`MAX_FETCHED_CONTENT_CHARACTERS`を200,000へ戻すと新規Testが`string_too_long`で実Failすることを確認した。

**Model Injection Budget**：`_inject_web_evidence()`が`@staticmethod`のまま固定12,000文字Capだけで
Model注入Contentを決めており、実際のEffective Context／Conversation History／RAG／Max New Tokens予約を
一切参照しなかった。CJK ContentのToken／Character比は英文より高く、固定Character Capは「8192 Contextを
超えない」というClaimを数学的に保証しなかった。

- `_inject_web_evidence()`をInstance Methodへ変更し、`chat_prompt_token_counter`／`effective_context_size`／
  `requested_max_new_tokens`を受け取るようにした。
- `_bounded_truncate_web_evidence_to_token_budget()`（新規）：実Token Counterへの二分探索で、Turnの実際の
  残Budgetに収まる最大Prefixを求める——概算のChars/Token比ではなく、実測値そのものが根拠。
- Web Evidence追加前のBase Conversation自体が既にBudget超過の場合と、Web Evidence追加（1文字＋固定Untrusted
  Instructionの分）だけで超過する場合を、`InferenceErrorCode.CONTENT_BUDGET_EXCEEDED`（新規）＋
  `caused_by_base_conversation`フラグ付きMessageで区別した。いずれもMain Model Call 0（`_web_evidence_request_
  factory`内で発火、Modelを呼ぶ前に確実にReturnする既存の`try/except InferenceError`経路を再利用）。
- `error_mapping.py`へ`CONTENT_BUDGET_EXCEEDED`を`CONTEXT_LIMIT_EXCEEDED`と同じ400番台へ追加。
- 新規Test 5件：CJK長文＋8192 Effective Contextで正常完了（Opaque `context_limit_exceeded`にならない）、
  History増加とMax New Tokens予約でBudgetが実際に縮小すること、Base Conversation単独超過時の`caused_by_base_
  conversation=True`分岐、Web Evidence自体だけが超過する場合の同`False`分岐、200,000文字超え・Byte Cap内
  Contentの正常成立。

**Internal Review Rework（この段階で発見・修正）**：`_bounded_truncate_web_evidence_to_token_budget()`の
二分探索は、`fits(char_count)`が`TRUNCATION_NOTICE`を含めずにToken数を測定していた一方、最終的な戻り値は
`text[:low] + TRUNCATION_NOTICE`——つまり実際に返す内容と二分探索が検証した内容が食い違い、`TRUNCATION_NOTICE`
自体のTokenコスト分だけBudgetを超過し得た（まさにこの修正が防ごうとしていたOpaque `context_limit_exceeded`を
別の形で再発させかねないBug）。新規CJK Testを最初に実行した際に実際にこの形でFailし、それを追跡して発見・
修正した——`fits_truncated_to()`を`TRUNCATION_NOTICE`込みで測定するよう修正し、以後全Test成功を確認した。

### 2.5 P8-CODEX-017 — User Manual Recheck Sheet Reproducibility（P8-MR7-5）

`phase_8_claude_post_manual_rework_controller_findings_corrected_user_manual_recheck_sheet_ja_20260831143355.md`
を新規作成し、前回Sheetを差分是正した：

- `uv run margpa-web`単独起動を撤回し、前回正本（`phase_8_user_mac_manual_acceptance_test_sheet_ja_
  20260831072507.md`）のFull Flag Commandを、初回Migration付き起動／以後の通常起動の2種類に分けて明記した。
- Conversation／Local Corpus／Data ControlsのRuntime RootとScope IDを、User実構成（`$PWD/runtime_data`／
  `mac-local-primary`）へ統一した。
- Dev Agent任意確認Pathを`runtime_data/persistent/default/...`から`runtime_data/persistent/mac-local-primary/
  ...`へ修正した（`FixtureWorkspaceToolPort`はScope IDをHash化せずDirectory名としてそのまま使うことを
  `fixture_workspace_tool_adapter.py`のSource Codeで確認して裏付けた）。
- 「Loopback外へ一切出ない」という虚偽記載を撤回し、Public URL FetchはUser MacからのRealネットワークOutbound
  であることを明記した。
- P8-CODEX-014／016の是正結果を確認できる新規手順（Reload後のFailed Turn Evidence確認、Context Budget確認）を
  追加した。

### 2.6 P8-CODEX-018 — Acceptance Disposition Count／Claim Correction（P8-MR7-5）

`phase_8_post_manual_rework_controller_findings_acceptance_correction_addendum_ja_20260831143355.md`を新規作成し、
前回Addendumを差分是正・Supersedeした：

- Frozen Matrix（`phase_8_acceptance_matrix_ja.md`、40件）は無変更のまま、P8-ACC-001〜040の全40件を個別に
  再導出した（旧Addendumは33行のTableに対し集計36という矛盾があった）。
- 集計は`PASS 38 + PARTIAL 1（P8-ACC-038）+ USER MANUAL GATE 1（P8-ACC-040）= 40`であり、Table行数（40）・
  Frozen Matrix行数（40）と機械的に一致することを`grep`で確認した。
- P8-ACC-039は、Controllerが実測した4 Test Failureを本Package全体で解消し、Backend Full／Ruff／Mypy／
  Frontend全てClean化したことを根拠に、「条件付きPASS」からPASSへ更新した。
- P8-ACC-038（GD相関PARTIAL）とP8-ACC-040（User Manual Gate）は根拠なくPASSへ昇格させていない。

## 3. Changed Paths

```text
# Backend Source
src/margpa_runtime_llm/modules/web_knowledge/domain/url_security.py
src/margpa_runtime_llm/modules/web_knowledge/domain/__init__.py
src/margpa_runtime_llm/modules/web_knowledge/__init__.py
src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py
src/margpa_runtime_llm/adapters/web_knowledge/httpx_fetch_provider.py
src/margpa_runtime_llm/modules/web_knowledge/contracts.py
src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
src/margpa_runtime_llm/modules/conversation/ports/conversation_store.py
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/modules/inference/domain/errors.py
src/margpa_runtime_llm/web/error_mapping.py
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py（Ruff Format限定、機械的）

# Backend Test
tests/unit/web_knowledge/test_url_security.py
tests/unit/web_knowledge/test_httpx_fetch_provider.py
tests/unit/web_knowledge/test_web_knowledge_service.py
tests/unit/conversation/test_conversation_generation.py
tests/integration/conversation/test_persistent_citation_evidence.py
tests/unit/conversation/test_web_citation_evidence_sqlite_store.py（新規）
tests/integration/web/test_constitution_web_app.py（Ruff Format限定、機械的）
tests/unit/constitution/test_constitution_contracts.py（Ruff Format限定、機械的）
tests/unit/dev_agent/test_dev_agent_contracts.py（Ruff Format限定、機械的）
tests/unit/dev_agent/test_run_service.py（Ruff Format限定、機械的）

# Docs
docs/project/shared/未解決/current_unresolved_findings_registry_ja.md（UF-P8-002へ状況Note追記、statusは未変更）
docs/project/phases/phase_8/operations/phase_8_post_manual_rework_controller_findings_acceptance_correction_addendum_ja_20260831143355.md（新規）
docs/project/phases/phase_8/history/index/phase_8_claude_post_manual_rework_controller_findings_corrected_user_manual_recheck_sheet_ja_20260831143355.md（新規）

# Frontend
変更なし（Source Diff 0）。npm run buildは実行し、Static配信物（app.js／app.css／index.html）を再生成したが、
出力Sizeは前Package終了時と完全一致（app.js 366.62 kB／app.css 22.31 kB／index.html 1.14 kB）——実質無変更。
```

明示的に変更していないもの：P8-MANUAL-001〜006（P8-MR1〜6）で確立したUI／Archive同期／Constitution Layout／
Dev Agent Fixture Workspace／Button Contrastの実装本体、P8-CR系Concurrency／Authorization Envelope／Approval
Evidence／Budget／Completion Gate、P8-RW6／RW7のRedirect Evidence Truthfulness／Constitution Preview 3-axis
Semantics——いずれもRollback・再実装していない。

## 4. Focused／Canonical Verification

```yaml
controller_4_focused_tests:
  command: >-
    ./.venv/bin/pytest -q --tb=short
    tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_is_injected_as_an_untrusted_tool_message
    tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_html_noise_is_stripped_and_budgeted_before_injection
    tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn
    tests/unit/conversation/test_conversation_generation.py::test_guardrail_context_source_hook_also_governs_manual_web_evidence
  result: "4 passed in 0.21s"
backend_full_suite:
  command: "uv run pytest -q"
  result: "2186 passed, 7 deselected"
  deselected_reason: "model_smoke marker, addopts -m 'not model_smoke' — intentional, unrelated to this Package"
  baseline_before_this_package: "2167 passed, 7 deselected"
ruff_check:
  result: "All checks passed"
ruff_format_check:
  result: "563 files already formatted — full repository clean, including the 5 Controller-flagged files"
mypy:
  result: "Success: no issues found in 346 source files"
frontend_typecheck:
  command: "npx tsc --noEmit"
  result: clean
frontend_full_suite:
  command: "npm test -- --run"
  result: "315 passed (33 files)"
frontend_lint:
  command: "npx eslint ."
  result: clean
frontend_build:
  command: "npm run build"
  result: "succeeded — app.js 366.62 kB, app.css 22.31 kB, index.html 1.14 kB (byte-identical to prior Package)"
regression_guard_verification:
  method: >-
    各中心修正（Resolver Injection、CommitConversation Invariant緩和、Schema 1/2 Upgrade、Token Budget
    Truncation）について、実際にFail-fastする状態（旧Resolver呼び出し、旧Invariant、旧Schema、旧Truncation
    Logic）を一時的に再現し、新規Testが実際にFailすることを確認してから修正・復元し、diffで完全一致を
    確認した。CommitConversationとTruncation Notice Bugの2件は、意図的なRevert実験ではなく実装直後の通常
    Test実行で偶然発見した——いずれも根本原因を追跡して修正し、専用Regression Testを追加した。
```

## 5. Internal Review Finding Ledger

Requirement／Negative Path／Persistence／Backward Compatibility／Context Budget／Acceptance Claimの6観点で
1 Cycle実施。

```yaml
requirement:
  finding: none
  note: "P8-CODEX-013〜018の全6件をP8-MR7-1〜5で個別に解消したことを本Index §2で確認した。"
negative_path:
  finding: 1
  severity: major
  summary: "_bounded_truncate_web_evidence_to_token_budget()の二分探索がTRUNCATION_NOTICEのTokenコストを
    含めずに候補をFitさせ、実際に返す内容（Notice付き）が探索時に検証した内容（Notice無し）と食い違い、
    Budgetを超過し得た。"
  disposition: fixed_in_this_package
  fix: "fits_truncated_to()がTRUNCATION_NOTICEを含めて測定するよう修正し、新規CJK/History Testで再現・確認した。"
security_boundary:
  finding: none
  note: "Resolver Injectionのproduction既定値は実DNSのまま無変更。MAX_FETCHED_CONTENT_CHARACTERSの引き上げは
    max_response_bytesという既存Byte Cap（Security Boundary）に対する整合であり、Cap自体を弱めていない。"
persistence:
  finding: 1
  severity: major
  summary: "CommitConversationのweb_citation_evidence Invariantが「COMPLETEDのTurnにしか付けられない」ため、
    fail_generation()への配線だけではpydantic ValidationErrorで実際にFailした。"
  disposition: fixed_in_this_package
  fix: "InvariantをCOMPLETEDまたはFAILEDへ限定的に緩和し、Documentation RAGのcitation_evidence側は無変更のまま
    維持した。実際に例外を再現してから修正し、専用Integration Testを追加した。"
backward_compatibility:
  finding: none
  note: "Schema 1/2 Upgradeは実Encoded SQLite Recordを直接改変したRegression Testで検証済み。旧Recordを
    書き換えず、Reader側の純粋関数としてのみ動作することをコードレビューで確認した。"
context_budget:
  finding: none
  note: "実Token Counterによる二分探索を採用し、CJK/English密度に依存しない正確な判定を実現した。Base
    Conversation単独超過とWeb Evidence単独超過を区別するTest 2件を追加した。"
acceptance_claim:
  finding: none
  note: "P8-ACC-001〜040全件を個別に再導出し、Table行数40・集計40・Frozen Matrix行数40の3点一致をgrepで
    機械検証した（Acceptance Correction Addendum §1参照）。"
critical_or_major_found_and_reworked: 2
rework_performed_in_this_cycle: "CommitConversationのFAILED Turn許可、TRUNCATION_NOTICE込みの二分探索修正"
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
archive_full_delete_or_bulk_or_export_implemented: false
real_dev_agent_project_file_tool_implemented: false
general_search_provider_implemented: false
production_constitution_activation_touched: false
```

すべての新規Web関連Testは`httpx.MockTransport`／Injected `resolver`／Monkeypatch経由の`socket.getaddrinfo`
Assertion Errorガードで完結し、実Networkに一切到達していない。Dev Agent関連の既存Test（本Packageで変更なし）は
引き続き`tmp_path`を使用する。Persistence関連の全新規Testは`tmp_path`ベースのTemp SQLiteを使用し、Userの実際の
`runtime_data/`には一切触れていない。

## 7. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK。
Final Acceptance、Phase 8 Closure、Phase 9開始のいずれもClaimしていない。
P8-ACC-040（User Manual Gate）自体もClaimしていない——User実画面再確認が必須。
```
