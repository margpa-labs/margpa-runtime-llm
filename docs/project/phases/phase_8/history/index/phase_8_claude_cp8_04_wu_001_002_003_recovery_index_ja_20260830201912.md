# Phase 8 Claude CP8-04 / P8-A-WU-001–003 Recovery Index

```yaml
document_type: recovery_index
phase: phase_8
package: P8-A
work_units: P8-A-WU-001, P8-A-WU-002, P8-A-WU-003
completed_cp: CP8-04
provider: Claude
state: complete
created_at: 2026-08-30 20:19 JST
```

## Continuity

継続元：`docs/project/phases/phase_8/history/index/phase_8_copilot_resource_exhausted_controller_recovery_ja_20260830200227.md`（CP8-01〜03／Mandatory Reading Digest確認／Entry Baselineは再実行していない）。

## Fixed: IndentationError (Controller Recovery §5)

`fetch_direct_url()`がCopilotにより`search_and_fetch()`の途中へ誤挿入され、後者の本体（`search_run`以降）が孤立していた問題を修復した。

- `search_and_fetch()`を単一の完全なMethodへ復元（`try/except`直後から`search_run`以降の本体まで連続）。
- `fetch_direct_url()`を独立Methodとして`search_and_fetch()`の直後・`_build_fetched_evidence()`の前へ再配置し、Indentを標準8-spaceへ修正（Copilotの元差分は12-space・不整合だった）。
- `py_compile`成功、`.venv/bin/pytest tests/unit/web_knowledge/`成功を確認済み。

## Completed: Mandatory Audit after Syntax Repair (Controller Recovery §6, 7項目)

| # | 項目 | Disposition | Evidence |
|---|---|---|---|
| 1 | Production CompositionがFixture Fetch固定 | **FIXED** | `WebKnowledgeService.__init__`に`direct_fetch_provider`を追加（省略時は既存`fetch_provider`にFallbackし、既存Testと完全後方互換）。`bootstrap/web_knowledge.py`が`direct_fetch_provider=HttpxWebFetchProvider(transport=direct_fetch_transport)`を実配線。Search Golden Path（`FixtureWebFetchProvider`）は無変更。 |
| 2 | Redirect後Canonical URL未保持 | **FIXED** | `FetchedContent`に`canonical_url`Fieldを追加。`HttpxWebFetchProvider`が最終Hop後のURLを設定。`WebEvidence.canonical_url`／`WebCitation.canonical_url`は`fetched.canonical_url`から構築（元Requestの`url`ではない）。 |
| 3 | CitationのContent Type／Digest／Source Class | **FIXED** | `WebCitation`に`content_type`・`source_class`（固定値`"public_web"`）Fieldを追加し、Search／Direct URL双方のCitation構築箇所へ配線。`content_sha512`はP7時点で既存。REST Response（`WebCitationResponse`）も追従。 |
| 4 | P8-REQ-003危険Port拒否が未成立 | **FIXED** | `url_security.py`へ`_DANGEROUS_PORTS`Denylist（SSH/SMTP/RDP/DB/Redis/Docker等20件、MVP-tier）と`UrlRejectionReason.DANGEROUS_PORT`を追加。DNS解決前に判定するためDNS 0回で拒否できる。副次的に`urlsplit(...).port`が不正Port文字列で例外を投げるPre-existing Gapも同時に修正（Typed Rejectionへ収束）。 |
| 5 | OFF時Network 0、Rejected時Fetch 0、Typed Failure | **CONFIRMED既存** | `WebSearchAndFetchResult.validate_disabled_means_zero_calls`（Pydantic Validator）が構造的に保証。`fetch_direct_url()`のDISABLED分岐・Rejection分岐は共にFetch Provider呼び出し前にReturn。新規Testで再確認。 |
| 6 | Existing Search／Fixture／Citation後方互換 | **CONFIRMED** | `test_web_knowledge_service.py`の既存Test（Direct URLが単一`fetch_provider`を共有する前提で書かれていたもの）は無変更のまま全Green（Fallback設計のため）。Search Golden Path Testも無変更・全Green。 |
| 7 | CP8-06以降のMain Model Evidence注入／Persistence／UI | **未着手（次WU）** | 下記「未着手範囲」参照。 |

## Changed Paths

Backend Source（8）：
- `src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py`（IndentationError修復＋`direct_fetch_provider`追加＋Citation Field拡張）
- `src/margpa_runtime_llm/modules/web_knowledge/contracts.py`（`WebCitation.content_type`／`source_class`、`UrlRejectionReason.DANGEROUS_PORT`、`PUBLIC_WEB_SOURCE_CLASS`定義位置整理）
- `src/margpa_runtime_llm/modules/web_knowledge/ports.py`（`FetchedContent.canonical_url`）
- `src/margpa_runtime_llm/modules/web_knowledge/domain/url_security.py`（危険Port Denylist、Port解析の例外安全化）
- `src/margpa_runtime_llm/adapters/web_knowledge/httpx_fetch_provider.py`（`canonical_url`設定）
- `src/margpa_runtime_llm/adapters/web_knowledge/fixture_providers.py`（`canonical_url`設定）
- `src/margpa_runtime_llm/bootstrap/web_knowledge.py`（`direct_fetch_provider`実配線、`direct_fetch_transport`Test Seam）
- `src/margpa_runtime_llm/web/web_search_contracts.py`（`WebCitationResponse`へField追加）

Backend Source（Copilot Partial・無変更で維持）：
- `src/margpa_runtime_llm/web/web_search_routes.py`（Ruff Import順のみ自動整形、Route本体は無変更）

Backend Test（4）：
- `tests/unit/web_knowledge/test_web_knowledge_service.py`（既存Stub`canonical_url`対応＋新規4 Test：direct_fetch_provider分離、Fallback、Citationのcontent_type/source_class×2）
- `tests/unit/web_knowledge/test_url_security.py`（新規4 Test：危険Port拒否×1 parametrize、標準Port非該当、不正Port範囲）
- `tests/unit/web_knowledge/test_httpx_fetch_provider.py`（新規2 Test：Redirect後canonical_url、非Redirect時canonical_url）
- `tests/integration/web/test_web_search_web_app.py`（`runtime()`へ`direct_fetch_transport`追加、既存Fixture前提Testを実Httpx MockTransport前提へ書換え、新規3 Test：Fixtureから独立したFetch、Redirect後Citation canonical_url、危険Port拒否）

## Focused Verification

```text
.venv/bin/pytest tests/unit/web_knowledge/ tests/integration/web/test_web_search_web_app.py
  84 passed

.venv/bin/mypy （変更Source全件）
  Success: no issues found in 15 source files

.venv/bin/ruff check （変更Source＋Test全件）
  All checks passed（Copilot由来のImport順Issue 1件を含め解消）
```

Entry Baseline（Backend 64 passed／Frontend 6 passed）からの純増：Backend Web Knowledge Unit 59（既存45＋新規10、内訳は上記）／Integration 13（既存10＋新規3）で計84、Regressionなし。Frontend `WebSearchPanel.test.tsx` 6 passed（無変更で再確認のみ、Sourceを触っていないため）。

## Open Findings／Deferrals

Critical／Major／MVP Blocker：0件。

未着手範囲（Controller Recovery §6項目7、Handoff §6の一部）：

```text
P8-A-WU-004: Untrusted EvidenceをMain Model Contextへ明示接続
P8-A-WU-005: Citation Persistence（Reload／Restart後の復元）
P8-A-WU-006: Settings Toggle／Manual URL入力UI／Untrusted Label／Failure Presentation
```

Research（本Package内で実施、Read-onlyでSource変更なし）により、既存`documentation_rag` Citation Persistence Pipeline（`SQLiteConversationStore`の`turn_citations`Table、`build_turn_citation_evidence()`、`_project_turn_citations()`、`conversation_generation.py`の`_inject_documentation_reference()`）の正確な設計を把握済み。WU-004/005は、これと**構造的に並行な**新規Pipeline（`turn_web_citations`Table、`build_turn_web_citation_evidence()`、`_inject_web_evidence()`等）として設計する方針を確認した——単一の巨大な`ConversationGenerationSession`（Constructor Param 20件超、Phase 6 Hardening Comment多数を含むCore Pipeline）へ新規Field／新規SQLite Table／新規Migration Stepを追加する、既存Chatに対するRegression Risk管理が必要な変更であるため、CP8-04とは別のCP境界（CP8-05／CP8-06相当）として切り出して実装する。

WebSearch/Direct URLの標準UIは現状Search専用（`WebSearchPanel.tsx`）で、Direct URL入力欄・Untrusted Label・Persistent Turnへの統合表示は未着手（`frontend/src/types.ts`の`WebCitationItem`/`WebSearchResult`は既存だが`PersistentTurn`と未接続）。

## Action Inventory

```yaml
network_actions: 0
npm_install_or_download: 0
node_runtime_switch: 0
git_mutation_actions: 0
git_read_only_actions: 0
backup_actions: 0
user_runtime_data_access: 0
real_model_access: 0
real_browser_access: 0
provider_memory_used: false
project_root_外_access: 0
```

## Next Exact Work Unit

```text
P8-A-WU-004: Main Model Evidence注入
  - ConversationGenerationSession / ConversationGenerationServiceへ
    Web Evidence（Direct URL Fetch結果）を Current Turn 限定で
    Threadする。documentation_rag の _inject_documentation_reference()
    と並行する _inject_web_evidence() を conversation_generation.py に追加。
  - Client→Serverの明示Trigger（Send Message Requestへの
    Optional Direct URL Field追加）を設計。
  - 既存Chat／RAG Citation Injectionへの Regression Test必須。
```
