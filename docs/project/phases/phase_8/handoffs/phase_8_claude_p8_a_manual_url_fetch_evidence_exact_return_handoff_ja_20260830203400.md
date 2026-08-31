# Phase 8 Claude P8-A Manual URL Fetch/Evidence — Exact Return Handoff

```yaml
document_id: phase_8_claude_p8_a_manual_url_fetch_evidence_exact_return_handoff_20260830203400
document_type: exact_differential_execution_return_handoff
document_state: frozen
language: ja
created_at: 2026-08-30 20:34 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
phase: phase_8
execution_scope: P8-A（P8-B〜P8-Fは本Return対象外・未着手）
maximum_claim: PARTIAL_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_8_closure_authority: false
phase_9_authority: false
git_authority: false
network_authority: false
active_contract: phase_8_claude_post_copilot_resource_exhausted_long_run_continuation_exact_handoff_20260830200227
```

## 1. Digest照合

```text
Exact Continuation Handoff: 8f0ef3635cb748edc452c9cad7406e2df744a88512c9ae3812a9a0b97b4b33b64673ddcc180c2429bb5f898a71390c4e8ceb632e4e1025949fc32ea30985434c  一致
Controller Recovery:        521328143fb8e271692d2919d5721d06bd3ca6f985d0d5e33e97a85b6cda8c4d7fac2fdd41685224f8aa3861c34cd1867e2c04f3e72ee0667ed31b3b1393d87b  一致
```

## 2. Package Recovery Index Path

```text
docs/project/phases/phase_8/history/index/phase_8_claude_p8_a_manual_url_fetch_evidence_package_recovery_ja_20260830203026.md
SHA-512: cfaf93f549a98f79de3a2c866b503c75d64ed2439c6b105d1ebcfa36083d746011c52c53117f74c93233f261f0e2fea4da3805be7e6822fdff9181e4b8d53731

中間Recovery（統合済み）:
docs/project/phases/phase_8/history/index/phase_8_claude_cp8_04_wu_001_002_003_recovery_index_ja_20260830201912.md
```

## 3. Maximum Claimの根拠（`PARTIAL_CANDIDATE_FOR_CONTROLLER_REVIEW`）

Exact Continuation Handoffの`COMPLETE_CANDIDATE_FOR_USER_MANUAL`は、P8-A〜P8-F全体の完成を前提とした上限Claimである。本Returnは**P8-Aのみ**を対象とし、P8-A自体もWU-004／005（Main Model Evidence注入・Persistence）が未着手のため「成立」に至っていない。したがって`COMPLETE_CANDIDATE_FOR_USER_MANUAL`をP8-A全体にも、まして未着手のP8-B〜P8-Fにも適用しない。P8-B以降への連結Long-runは、Handoff§7自身が「P8-A成立後」を条件としているため、本Returnでは開始していない。

これはRoutine Confirmation・Minor Finding・Real Network未許可のいずれでもなく、Blast Radius（全Chat共有Core Pipelineへの複数File・大規模Diff）とVerifiability（Independent Review前の自己Certify回避）を理由とする、実装Authority内でのScoping Decisionである。詳細な理由と正確な次Work Unit設計はPackage Recovery Index §4に記載した。

## 4. P8-ACC-001〜012 個別Disposition（P8-A対象）

| ID | Disposition | Evidence |
|---|---|---|
| P8-ACC-001 | **PASS** | Backend Full Canonical 1972 passed（Entry Baseline 1952から+20、Regression 0）。Frontend Full Canonical 273 passed（Baseline 268から+5、Regression 0）。 |
| P8-ACC-002 | **PASS** | `WebSearchAndFetchResult.validate_disabled_means_zero_calls`（Pydantic Validator）が構造的に保証。`fetch_direct_url()`のDISABLED分岐はFetch Provider呼び出し前にReturn。`test_direct_url_disabled_makes_zero_fetch_calls`等で確認。 |
| P8-ACC-003 | **PASS** | `url_security.py`の`ALLOWED_SCHEMES = {"http", "https"}`。`test_unsupported_scheme_is_rejected`で確認（既存）。 |
| P8-ACC-004 | **PASS** | Credential／Private／Loopback／Link-local／Metadata（既存）＋危険Port（本Package新規、`_DANGEROUS_PORTS`）。`test_dangerous_port_is_rejected_before_dns_resolution`等で確認。 |
| P8-ACC-005 | **PASS** | `HttpxWebFetchProvider.fetch()`のRedirect Loopが毎Hop`validate_url_before_connect()`を呼ぶ（既存、Phase 7実装）。`test_redirect_to_a_private_address_is_rejected_by_the_security_boundary`で確認。 |
| P8-ACC-006 | **PASS** | Timeout／Response Size／Content Type Allowlist（既存、Phase 7実装、無変更）。 |
| P8-ACC-007 | **PASS** | `httpx.Client`はJavaScript実行系を持たず、Formや任意Downloadを行う経路が存在しない（構造的に不可能、Architecture上のInvariant）。 |
| P8-ACC-008 | **PASS**（Standalone Panel限定） | `WebSearchPanel`の`EvidenceList`が、Search・Direct URL双方のFetched Contentへ`webSearchPanelUntrustedLabel`（"Untrusted External Content"）を明示表示。ただしChat本体への表示ではなくSettings内のStandalone Previewに限定（Main Model連携はP8-ACC-009参照）。 |
| P8-ACC-009 | **NOT MET** | Main Model Evidence注入は未着手（WU-004）。Package Recovery Index §4.3に設計を記録。 |
| P8-ACC-010 | **PASS**（Contract Level） | `WebCitation`が`canonical_url`／`fetched_at`／`content_sha512`／`source_class`（新規）を保持。`/api/v2/web-search/direct`のResponseで確認可能。ただしConversation Turnへの永続化はP8-ACC-011参照。 |
| P8-ACC-011 | **NOT MET** | Turn Persistenceは未着手（WU-005）。Package Recovery Index §4.3に設計を記録。 |
| P8-ACC-012 | **PASS** | `rejected`／`rejection_reason`／`withheld_by_governance`が個別に表示され、Fetch成功と信頼を同一視しない。Untrusted Labelで明示。 |

**P8-ACC-001〜012 集計：PASS 10／NOT MET 2（009, 011）／全12件査定済み。**

## 5. P8-ACC-013〜040（P8-B〜P8-F対象）

```yaml
P8-ACC-013..018: NOT_STARTED  # P8-B（Entry UI Simplification／Archive Management）未着手
P8-ACC-019..025: NOT_STARTED  # P8-C（Provisional Runtime Constitution）未着手
P8-ACC-026..038: NOT_STARTED  # P8-D/E（Dev Agent／Tool／Approval Harness、Integration／Lifecycle）未着手
P8-ACC-039..040: NOT_STARTED  # P8-F（Review／Verification／User Manual Candidate）未着手
```

P8-A未成立のため、Execution Plan自身の順序（P8-A→B→C→D→E→F）に従い着手していない。虚偽のPASS・Partial表示は行わない。

## 6. Copilot Partial Disposition

```yaml
P8-CODEX-Copilot-Partial: RESOLVED_AND_EXTENDED
```

Copilotが追加した`URL_FETCH_DISABLED`／`URL_REJECTED` Failure Reason、`WebCitation.content_sha512`、`DirectUrlFetchRequest`、`/api/v2/web-search/direct` Route、`WebKnowledgeService.fetch_direct_url()`、関連Testは、`IndentationError`修復後すべてCurrent Sourceとして保持し、そのまま完成させた（Rollbackなし）。Copilot由来のImport順Issue（`web_search_routes.py`）は本Package内でRuff Auto-fixにより解消した。

## 7. Package／Work Unit Completion、Changed Paths

Package Recovery Index §Work Unit別Status、§1、§2に記載済み。要約：

```text
COMPLETE: P8-A-WU-001, WU-002, WU-003
PARTIAL:  P8-A-WU-006（Standalone Panel部分のみ）
NOT_STARTED: P8-A-WU-004, WU-005
```

Changed Paths（Backend 10、Frontend 7、Static Artifact 1、Test 4、計22）はPackage Recovery Index §1・§2に列挙済み。

## 8. Canonical Verification

Package Recovery Index §2・§3に記載済み。要約：

```text
Backend: 1972 passed, 7 deselected / mypy clean (323 files) / ruff check clean / ruff format clean
Frontend: 273 passed (29 files) / tsc clean / eslint clean / vite build succeeded
```

## 9. Internal Review

Package Recovery Index §5に記載済み。6角Review実施、Critical/Major 0件、Minor 1件（危険Port Denylistの非網羅性、既存Metadata Denylistと同じ開示済みの性質、Non-blocking）。

## 10. Incident（Level 1、開示済み・再掲）

`npm run build`のExit確認目的での再実行提案時、Log Redirect先をFilesystem Root直下（`/tmp_build_rerun.log`）と誤指定したが、User承認前にRejectされ未実行。実File・実Writeは発生していない。

## 11. PARTIAL／NOT RUN／USER GATE

```yaml
Real Network (実URL Fetch): NOT_RUN_USER_MANUAL_GATE  # 従来どおり、Mock/Fixture PASSをReal URL PASSへ昇格していない
Real Browser: NOT_RUN  # 本Package全体でBrowser Toolを使用していない
Real Model: NOT_RUN
P8-A-WU-004 (Main Model Evidence注入): NOT_STARTED
P8-A-WU-005 (Persistence): NOT_STARTED
P8-B..P8-F: NOT_STARTED
```

## 12. Root／Git／Network／Provider Memory／User Data／Model Action Inventory

Package Recovery Index §6に記載済み。全項目0（Git Read-only 1件のみ、Changed Paths確認目的）。

## 13. Active Process／Temporary Artifact／Compaction／Resource Recovery

Package Recovery Index §7に記載済み。`frontend/.build_tmp/`（Node Compile Cache）、`pytest --basetemp`各種（Session Scratchpad配下）のみ、いずれも無害。本Return作成時点でCompaction／Resource Stopの兆候はない。

## 14. User Manual Test Sheet（P8-A完成部分のみ、実施可能な範囲）

```text
1. Settings → Web Search Panel（既存）を開く。
2. 「URL Fetch (Manual)」セクションに Public URL を入力し「Fetch」を押す。
   期待：Untrusted Labelとともに取得Contentが表示される
   （Real Network User Authorityが必要 — 本Package内ではFixture/
   MockTransportのみ検証済み）。
3. Web Search機能をOFFに設定し、同じ操作を行う。
   期待：「Web search is OFF in Settings...」Note表示、入力欄・Fetch
   Buttonが無効化される。
4. 危険Port（例: https://example.org:6379/）を入力し取得を試みる。
   期待：Rejectedとして表示され、実際のFetchは発生しない
   （dangerous_port Reason）。
```

Main Model Evidence注入・Reload後Citation復元はWU-004/005未着手のため、本Sheetには含めていない。

## 15. Exact Next Action

```text
Next Provider: Claude（継続）またはController指定の別Provider
Next Work Unit: P8-A-WU-004（Main Model Evidence注入）
  Package Recovery Index §4.3の設計に従い、
  Backend Full Canonical Suite（1972 passed基準）を都度再実行しながら
  慎重に実装する。
Do Not Repeat: CP8-01〜03、Mandatory Reading Digest確認、Entry Baseline、
  CP8-04（WU-001〜003）、CP8-05（WU-006 partial、Standalone Panel部分）。
P8-A-WU-004/005/006完了後、初めてP8-A成立とみなし、P8-B以降への
  連結Long-runを開始する。
```

Return後はCodex Controller Independent Review待ちで停止する。Phase 8 Closure、Phase 9、Roadmap、Backup、Git Mutationのいずれへも進んでいない。
