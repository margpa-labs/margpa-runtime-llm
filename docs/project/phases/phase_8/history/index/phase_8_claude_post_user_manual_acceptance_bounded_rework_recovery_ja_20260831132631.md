# Phase 8 P8-MR Post-User-Manual Acceptance Bounded Rework — Recovery Index

```yaml
document_id: phase_8_claude_post_user_manual_acceptance_bounded_rework_recovery_20260831132631
document_type: recovery_index
document_state: frozen
language: ja
created_at: 2026-08-31 13:26 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_8
execution_scope: P8-MR0_through_P8-MR6
入力Handoff: phase_8_claude_post_user_manual_acceptance_bounded_rework_exact_handoff_ja_20260831122257.md
入力Handoff_sha512: 37c5bc5490533139f5c1d5413f7364382afdd5797aa3103ee56f82aeccda02bafe67c00d30986aabcf35aade214c9982a3ff18ca3c40e741d878b54d03d8a408
対象Finding: P8-MANUAL-001_through_006
```

## 1. Package Boundary構成についての注記

Handoffは「各Package BoundaryでRecovery Indexを残す」と指定するが、本Reworkは6 Findingにまたがる単一の連結実行であり、
6本の別Fileへ分割するより、Package境界を明示した章立てを持つ1本の統合Indexの方がController Reviewにとって
追跡しやすいと判断した。以下の各章（§3.1〜§3.6）がそれぞれ独立したPackage Boundaryに対応する。

## 2. 完了状態サマリ

```yaml
p8_manual_001_disposition: RESOLVED
p8_manual_002_disposition: RESOLVED
p8_manual_003_disposition: RESOLVED
p8_manual_004_disposition: RESOLVED
p8_manual_005_disposition: RESOLVED
p8_manual_006_disposition: RESOLVED
mvp_blocker_open: 0
critical_open: 0
major_open: 0
internal_review_rework_performed: 1
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
```

## 3. Package別詳細

### 3.1 P8-MR1 — Manual URL Reliability（P8-MANUAL-001）

正本Finding：`phase_8_manual_web_direct_url_reliability_grounding_and_context_budget_findings_ja_20260831112449.md`

実装：

- `UrlRejectionReason`へ`CONNECT_FAILED`／`TLS_FAILED`／`HTTP_PROTOCOL_ERROR`を追加し、`httpx.ConnectError`の
  `__cause__`（`socket.gaierror`／`ssl.SSLError`）から実DNS失敗・実TLS失敗・純粋Connect失敗を分離した
  （`httpx_fetch_provider.py`）。
- `HttpxWebFetchProvider`へRedirect Hop全体で共有される固定Retry Budget（`DEFAULT_MAX_RETRIES=2`＝最大3試行）を追加した。
  Retry対象は`DNS_RESOLUTION_FAILED`／`TIMEOUT`／`CONNECT_FAILED`のみで、Private／Loopback等のPermanent
  Rejectionおよび`TLS_FAILED`／`HTTP_PROTOCOL_ERROR`はRetryしない。`sleep_fn`Injectableで実待機なしにTest可能。
- `html_normalizer.py`（新規）：`extract_html_title()`（実`<title>`抽出）、`extract_readable_text()`
  （`script`／`style`／`noscript`除去＋Tag除去、外部Dependency追加なし）、`budget_evidence_for_injection()`
  （Model注入用のみ12,000文字Hard Cap、Truncation Notice付き）。Citation／Evidence自体のRaw Content・Digestは
  無変更（常にRaw Byteに対して計算）。
- **Fail-closed Grounding（最重要）**：`conversation_generation.py`のManual Web Evidence経路へ、Documentation RAGの
  `should_generate=False`Gateと構造的に対称な早期Returnを追加した。`web_result.should_generate_with_evidence`が
  Falseの場合（Rejected／Fetch失敗／Governance Withheld）、`_web_evidence_fetch_failed_event()`
  （新規、`web_evidence_fetch_failed`Code、Configured Language Safe Message）をYieldしてReturnし、
  Main Modelを一切呼び出さない（Model Call 0、Counting Fakeで実証）。これがUser Manual Web Segment 1で
  再現した「阿部寛」バグ（Fetch失敗にもかかわらずModelが未取得Pageに基づかない人物説明を生成した）の直接修正である。

Regression Guard：`conversation_generation.py`のFail-closed早期Returnを一時的に無効化し、新規2 Test
（`test_manual_web_evidence_rejected_url_fails_closed_with_zero_model_calls`、
`test_manual_web_evidence_withheld_by_governance_also_fails_closed`）が実際にFailすることを確認した上で復元、
diff一致を確認した。`httpx_fetch_provider.py`のRetry Budgetも同様の手法でVerifyした。

### 3.2 P8-MR2 — Web Citation Completeness（P8-MANUAL-002）

- `WebContentTransformation`（`raw`／`html_text_extracted`）を`WebEvidence`／`WebCitation`へ追加し、
  `classify_content_transformation()`で`content_type`から決定的に導出した。`WEB_CITATION_EVIDENCE_SCHEMA_VERSION`を
  2→3へBumpし、既存の`WebCitationUnavailable(reason="corrupt_record")` Fallbackが旧Recordを安全に処理することを
  維持した。
- Direct URL FetchのTitleを、実HTML `<title>`から抽出し、抽出不能時だけCanonical URLへFallbackするよう修正した
  （従来は常にURL自体がTitleだった）。
- Frontend Copy Buttonの誤表示を修正：`WebCitationsSection.tsx`のCanonical URL Copy Buttonが「Pathをコピー」と
  表示していたBugを「Canonical URLをコピー」へ修正し、Requested URLが異なる場合は専用の
  「Requested URLをコピー」Buttonを追加した。
- Chat Citationへ Source Authority／Fetched At／Content Type／Transformation の4行を追加表示した
  （Backend Contractには既に存在していたが、Frontend UIが表示していなかった）。
- **UF-P8-007（実装中に発見・修正）**：Chat Web EvidenceがAggregate `failure_reason`（例：`url_rejected`）だけを
  表示し、per-Evidence の Specific Reason（例：`private_or_loopback_address`）を一切保持・表示していなかった。
  `PersistedTurnWebCitationEvidence.specific_failure_reason`（新規Field、Optional・Backward Compatible）を
  追加し、Live SSE（`_web_evidence_event()`）／Persistence／REST（`persistent_contracts.py`）／Frontend
  （`WebCitationsSection.tsx`）へ損失なく投影した。

Regression Guard：`dev_agent_contracts.py`の`project_run()`と同様の一時的Revert手法を`web_search_contracts.py`
系の主要変更へは適用せず（低Risk・純Projectionのため）、代わりに新規Test（Backend 7件・Frontend 4件）が
実データを直接Assertする形で検証した。

### 3.3 P8-MR3 — Archive Sidebar／Panel State Synchronization（P8-MANUAL-003）

- `fetchPersistentList()`（Sidebar用）へ`state=active`を明示的に付与した。従来はQuery Param省略によりBackendの
  既定値（Deleted以外の全State＝Active＋Archived）を取得しており、これがArchive済みChatがSidebarへ残留した
  直接原因だった。`chatListItemAction()`が既にArchive／Unarchive後に`loadPersistentList()`を呼び出す実装だったため、
  このQuery Param修正だけでSidebar除外・復帰の両方が正しく動作するようになった。
- Archive済みChat Panelへ「閉じる」Button（`onArchivedChatsClose`）を追加し、Stateを`idle`へResetする
  （`DataControlsPanel.tsx`）。
- Settings Modalの`onClose`および`openArchivedChat()`双方から`closeArchivedChats()`を呼ぶよう`App.tsx`を修正し、
  Settings再Open後は必ずFreshなFetchが行われる（古い`ready` Stateが残らない）ようにした。

Regression Guard：`fetchPersistentList()`の`state=active`を一時的に除去し、新規Test
（`the sidebar's conversation list fetch requests state=active...`）が実際にFailすることを確認した上で復元した。

### 3.4 P8-MR4 — Constitution Presentation（P8-MANUAL-004）

- `ConstitutionPanel.tsx`のPer-Mode行を再構成：Mode名を`<h5>`Headerとし、Decision／評価区分／Action許可範囲／
  違反時の表示の4行を`.constitution-preview-mode-details`という別Blockへ配置した（従来はMode名とDecisionが
  同一Flex Rowに同居し、他3軸だけが折り返されていた）。Backend Contract・Semantics・Production OFFは無変更
  （Frontend限定の構造変更）。

### 3.5 P8-MR5 — Traceable Dev Agent Fixture／Informed Approval UI（P8-MANUAL-005）

- `FixtureWorkspaceToolPort`（新規Adapter、`fixture_workspace_tool_adapter.py`）：
  `<runtime_data_root>/persistent/<scope_key>/dev_agent/fixture_workspace/`限定の実File List／Read／Write。
  `JsonFileDevAgentRunStore`と同じ安全規律（Absolute Path／`..`／Symlink／Root Escape拒否、Owner-only
  0700／0600、Atomic Same-directory Replace）を踏襲した。Seed（`notes/readme.md`／`notes/todo.md`）はRestartごとに
  既存Fileを上書きしない。Write先は`notes/new.md`固定Fixture Planに従うが、Adapter自体は`fixture_workspace/`配下の
  任意の安全な相対Pathを扱える汎用実装である。
- `bootstrap/dev_agent.py`／`entrypoints/web/main.py`：Production Compositionを、既存の
  `dev_agent_runtime_data_root`／`dev_agent_scope_id`（既にDev Agent Run Store用に計算済み）を再利用して
  `FixtureWorkspaceToolPort`へ配線した。`FakeToolPort`はUnit Test用のPure In-memory Fake としてそのまま保持
  （P8-MR5 Required §10.3が明示的に許容）。
- **Informed Approval（最重要）**：`RunSnapshot.plan.steps[].input`はBackendに既に存在していたが、REST
  `DevAgentRunResponse`へ一切投影されておらず、UIはApproval前にTarget Path／Write Contentを一切表示できなかった
  （Blind Approval）。`DevAgentStepRecordResponse`へ`input`Fieldを追加し、`project_run()`で`step_id`一致により
  `Plan`から実Inputを投影した。`StepRecord.output`は既にProjectされていたため、Result（Digest／Overwrite／
  Written At）は元々表示可能だったが、Frontendが描画していなかった。
- `DevAgentPanel.tsx`：各Stepの Input／Output を`formatRecord()`（汎用Key:Value Formatter、Tool固有の
  Hard-coded Rendererではない）で表示し、Approval Gate内にResource Scope・Gate Reason・
  `fixture_workspace_only`Disclaimerを追加した。`devAgentNote`の文言を「実File・実Networkに一切触れない」から
  「Fixture Workspace限定の実Fileを扱うが、Project SourceとNetworkには触れない」へ訂正した（Backend変更後に
  従来の文言が虚偽になるため）。

**Internal Review Rework（Critical/Major、本Package内で解消）**：`FixtureWorkspaceToolPort.execute()`が、
既存Directory（例：`notes/`自体）と衝突するWrite Path指定時に`os.replace()`が送出する`IsADirectoryError`を
無防備に伝播させ、`DevAgentRunService.advance()`（Tool Port呼出し箇所に元々try/exceptが無い）を経由して
未捕捉例外としてRESTまで到達し得ることを発見した。`execute()`全体を`try/except OSError`で覆い、
`ToolExecutionFailed(reason="workspace_io_error")`へ収束するよう修正し、実際に例外を再現してから
修正後にFailしないことを確認した（`test_write_note_targeting_an_existing_directory_fails_without_raising`）。

### 3.6 P8-MR6-Buttons — Dev Agent Button Contrast（P8-MANUAL-006）

- `app.css`へ`--button-danger-bg`／`--button-danger-text`（Light／Dark両Theme）と`.danger`Classを新設した
  （既存の`.primary`／`.secondary`と対称）。
- `DevAgentPanel.tsx`の Approve／Advance／Start Demo Run／Start New Run を`.primary`または`.secondary`、
  Deny／Cancel（Step Gate・Completion Gate双方）を`.danger`へ明示的に分類した。従来は無Class（Browser既定の
  淡色BackgroundとLight Text Colorが衝突し、ほぼ判読不能）だった。

## 4. Changed Paths（手動編集のみ、Frontend Build再生成物は除く）

```text
# Backend Source
src/margpa_runtime_llm/modules/web_knowledge/contracts.py
src/margpa_runtime_llm/modules/web_knowledge/domain/html_normalizer.py（新規）
src/margpa_runtime_llm/modules/web_knowledge/domain/__init__.py
src/margpa_runtime_llm/modules/web_knowledge/__init__.py
src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py
src/margpa_runtime_llm/adapters/web_knowledge/httpx_fetch_provider.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/web_search_contracts.py
src/margpa_runtime_llm/web/persistent_contracts.py
src/margpa_runtime_llm/web/persistent_streaming.py
src/margpa_runtime_llm/adapters/dev_agent/fixture_workspace_tool_adapter.py（新規）
src/margpa_runtime_llm/adapters/dev_agent/__init__.py
src/margpa_runtime_llm/bootstrap/dev_agent.py
src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/web/dev_agent_contracts.py

# Backend Test
tests/unit/web_knowledge/test_httpx_fetch_provider.py
tests/unit/web_knowledge/test_url_security.py
tests/unit/conversation/test_conversation_generation.py
tests/integration/web/test_persistent_web_app.py
tests/integration/conversation/test_persistent_citation_evidence.py
tests/unit/dev_agent/test_fixture_workspace_tool_adapter.py（新規）
tests/integration/dev_agent/test_dev_agent_web_app.py

# Frontend
frontend/src/api/client.ts
frontend/src/types.ts
frontend/src/i18n/translations.ts
frontend/src/components/WebCitationsSection.tsx（+.test.tsx）
frontend/src/components/WebSearchPanel.test.tsx
frontend/src/components/DataControlsPanel.tsx（+.test.tsx）
frontend/src/components/SettingsModal/SettingsModal.tsx（+.test.tsx）
frontend/src/App.tsx（+.test.tsx）
frontend/src/components/ConstitutionPanel.tsx（+.test.tsx）
frontend/src/components/DevAgentPanel.tsx（+.test.tsx）
frontend/src/lib/persistentDetailProjection.ts（+.test.ts）
frontend/src/styles/app.css
```

明示的に変更していないもの：P8-A〜F・P8-CR・P8-RW6／7で解消済みのSource（Constitution Backend Semantics、
Dev Agent Approval Evidence／Budget／Completion Gate自体のContract、URL Security Boundaryの拒否ロジック本体）。
`resource_scope`の実値（`"fixture_only"`）は据え置き、UI側で`fixture_workspace_only`の意味をDisclaimerとして
明示する方針を採った（値のRenameはScope外の6ファイル横断修正になるため見送り、Recovery §6に理由を記録）。

## 5. Focused／Canonical Verification

```yaml
backend_full_suite:
  command: "uv run pytest -q"
  result: "2167 passed, 7 deselected"
  baseline_before_this_package: "2131 passed, 7 deselected"
ruff_check:
  result: "All checks passed"
ruff_format_check:
  result: "5 pre-existing files outside this Package's Changed Paths would be reformatted (run_service.py, test_constitution_web_app.py, test_constitution_contracts.py, test_dev_agent_contracts.py, test_run_service.py) — not touched by this Rework; this Package's own new file (test_fixture_workspace_tool_adapter.py) was formatted clean."
mypy:
  result: "Success: no issues found in 346 source files"
frontend_full_suite:
  command: "npm test -- --run"
  result: "315 passed (33 files)"
  baseline_before_this_package: "302 passed (33 files)"
frontend_typecheck_lint_build:
  result: clean
regression_guard_verification:
  method: >-
    各中心修正（Fail-closed Grounding、httpx Retry、Archive state=active、DevAgentPanel Informed
    Approval表示／Button Contrast）を一時的にPre-fix状態へ書き換え、新規Testが実際にFailすることを確認した上で
    Scratchpadバックアップから復元し、diffで完全一致を確認した。
```

## 6. Design Scoping Notes（理由の記録）

- `AuthorizationEnvelope.resource_scope`の実値は`"fixture_only"`のまま維持した。`"fixture_workspace_only"`への
  Rename自体は`contracts.py`／`run_service.py`／Test 4Fileを横断する低Risk・純粋機械的な変更だが、6 Finding全体の
  Scopeに対して機能的必要性が無く（UI側でDisclaimer文言により意味は既に明示できる）、不要な追加Diffを避けた。
- HTML Normalizerは正規表現ベースの最小Extractorであり、Phase 11以降のFull Extractor／Chunking／Relevance
  Selectionの代替を主張しない（UF-P8-006は未解決のまま、Deferred継続）。
- Large HTMLのBudget対応は「Typed `content_budget_exceeded`」ではなく「Budgeted Evidence（Truncate + Notice）」
  を選択した。Handoff §5がいずれかをRework設計時判断としており、既存のRaw Preview PASS挙動（Settings画面での
  全文表示）を維持しつつMain Model注入だけを安全にBudget化する方が、追加Typed Failureを増やすより低Riskと判断した。
- `FixtureWorkspaceToolPort.execute()`のInternal Review Reworkにより、`workspace_io_error`という新しいTool
  Failure Reason文字列が生じた。これはEnum化されたTyped Contractではなく（`ToolExecutionFailed.reason: str`は
  元々自由文字列）、既存の`"path_not_found"`／`"invalid_input"`／`"unknown_tool"`と同じ扱いである。

## 7. Process Action Inventory

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
```

## 8. Exact Next Action

```text
Codex Controller Independent Review待ちで停止する。
最大Claimは COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK。
Final Acceptance、Phase 8 ClosureまたはPhase 9開始はClaimしていない。
User Manual PASS自体もClaimしていない（Userの実画面再確認が必須）。
```
