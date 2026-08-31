# Phase 8 Copilot Resource-exhausted Controller Recovery

```yaml
document_id: phase_8_copilot_resource_exhausted_controller_recovery_20260830200227
document_type: controller_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 20:02:27 JST
phase: phase_8
provider: GitHub Copilot app
state: RESOURCE_EXHAUSTED_PARTIAL
next_provider: Claude
```

## 1. Stop Signal

UserからCopilotが利用可能量を使い切った旨が報告された。Copilot自身のStopped-safe Returnは作成されていないため、ControllerがCurrent Source、Recovery Indexおよび失敗出力から再開境界を固定する。

## 2. Completed Boundary

次は成立済みとして保持し、再実行しない。

- `CP8-01／P8-0-WU-001` As-built Map。
- `CP8-02／P8-0-WU-002` Adjacent Boundary。
- `CP8-03／P8-0-WU-003` Authority／Test Freeze。
- Mandatory Reading 10文書と指定Digest 4件の一致確認。
- Entry時Focused Baseline：Backend 64 passed、Frontend 6 passed。

Recovery：

1. `docs/project/phases/phase_8/history/index/phase_8_copilot_p8_0_wu_001_recovery_index_ja_20260830.md`
2. `docs/project/phases/phase_8/history/index/phase_8_copilot_p8_0_wu_002_recovery_index_ja_20260830.md`
3. `docs/project/phases/phase_8/history/index/phase_8_copilot_p8_0_wu_003_recovery_index_ja_20260830.md`

## 3. Current Partial Boundary

```text
Current CP／WU       : CP8-04／P8-A-WU-001／002
State                 : PARTIAL／NOT VERIFIED
Source Files Changed  : 4
Test Files Changed    : 2
Focused Test           : Collection failed
Failure                : IndentationError
Failure Path           : src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py:223
Active Process         : 0 known
Real Network           : 0
Git                    : 0
User runtime_data      : 0
```

Changed Files：

- `src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py`
- `src/margpa_runtime_llm/modules/web_knowledge/contracts.py`
- `src/margpa_runtime_llm/web/web_search_contracts.py`
- `src/margpa_runtime_llm/web/web_search_routes.py`
- `tests/integration/web/test_web_search_web_app.py`
- `tests/unit/web_knowledge/test_web_knowledge_service.py`

## 4. Partial Implementation

Copilotは次を途中まで追加した。

- `URL_FETCH_DISABLED`／`URL_REJECTED` Failure Reason。
- `WebCitation.content_sha512`。
- `DirectUrlFetchRequest`。
- `/api/v2/web-search/direct` Route。
- `WebKnowledgeService.fetch_direct_url()`。
- Disabled、Explicit URL、Rejected URL用Test。

この差分はCurrent Sourceとして保持するが、成立済みとはClaimしない。

## 5. Exact Technical Failure

`fetch_direct_url()`が既存`search_and_fetch()`の途中へ挿入され、元の`search_run`以降の本体が不正なIndentへ分断された。そのためTest Collection前のImportで次へ失敗する。

```text
IndentationError: unindent does not match any outer indentation level
src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py:223
```

最初の修復は、既存`search_and_fetch()`を完全なMethodとして復元し、`fetch_direct_url()`を独立Method Boundaryへ移すことである。全Copilot差分のRollbackはしない。

## 6. Mandatory Audit after Syntax Repair

Syntaxだけを直してCP8-04完了としない。少なくとも次を確認する。

1. Production Compositionは現在Fixture Fetch固定であり、任意User URLを実際に取得できない。既存Search Fixtureを壊さず、Direct URLだけを`HttpxWebFetchProvider`へ配線する境界が必要。
2. Redirect後の最終Canonical URLを`FetchedContent`／Evidence／Citationへ保持できるか。
3. CitationにContent Type、Digest、Source Class、Fetched Atが揃うか。
4. P8-REQ-003の危険Port拒否が既存`url_security.py`で未成立ではないか。
5. OFF時Network 0、Rejected時Fetch 0、Exception／Timeout／Unsupported ContentのTyped Failure。
6. Existing Search／Fixture／Phase 7 Citationの後方互換。
7. CP8-06以降のMain Model Evidence注入、Persistence、UIは未着手。

## 7. Exact Resume

```text
Next Provider : Claude
Next CP       : CP8-04
Next Action   : Current Partial Diffを保持してSyntax／Method Boundaryを修復し、Contract全体をAudit
Do Not Repeat : CP8-01〜03、Mandatory Reading Digest確認、Entry Focused Baseline
```
