# P8-RW6-A — Redirect Evidence Truthfulness — Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-RW6-A
finding: P8-CODEX-005
state: complete
provider: Claude
created_at: 2026-08-31 01:10 JST
```

## 結論

`fetch_direct_url()`／`search_and_fetch()`共通の`_build_fetched_evidence()`が`source_authority`をRedirect前の`url`から計算していた実Bugを修正。今後は必ず`fetched.canonical_url`（実際に読んだ最終Host）から再計算する。`WebEvidence`／`WebCitation`へ`requested_url`Fieldを新設し、Requested／Canonical両URLをEvidence／Citation／Persistence／REST／SSE／UIで損失なく保持する。

Fix前のSourceへ一時的に差し戻し、新規Regression Testが実際に`OFFICIAL`誤判定で失敗することを確認した上で復元（diff上Fix版と完全一致を確認済み）。

## Changed Paths

```text
src/margpa_runtime_llm/modules/web_knowledge/contracts.py（requested_url追加、SCHEMA_VERSION 1->2）
src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py（authority再計算、requested_url配線）
src/margpa_runtime_llm/web/web_search_contracts.py
src/margpa_runtime_llm/web/persistent_contracts.py
src/margpa_runtime_llm/web/persistent_streaming.py
frontend/src/types.ts
frontend/src/components/WebSearchPanel.tsx
frontend/src/components/WebCitationsSection.tsx
frontend/src/i18n/translations.ts
tests/unit/web_knowledge/test_web_knowledge_service.py（新規Regression Test 2件）
tests/integration/web/test_persistent_web_app.py（requested_url追記）
tests/integration/conversation/test_persistent_citation_evidence.py（requested_url追記）
```

## Focused Verification

```yaml
tests/unit/web_knowledge/ + tests/integration/web/ + persistent_citation_evidence: 289 passed
regression_before_fix_reproduction: confirmed_fails_as_OFFICIAL_instead_of_GENERAL
backend_full_suite_after: 2092 passed, 7 deselected
ruff: All checks passed
mypy: Success (344 source files)
```

Acceptance Target `P8-ACC-012`: PASS（別Authority ClassへのRedirectで最終Hostから再判定されることを実Testで確認）。Frontend Test/Build検証はP8-RW6-Eでまとめて実施。
