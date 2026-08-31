# Phase 8 Post-User-Manual Rework Controller Findings — Acceptance Correction Addendum

```yaml
document_id: phase_8_post_manual_rework_controller_findings_acceptance_correction_addendum_20260831143355
document_type: acceptance_correction_addendum
document_state: frozen
language: ja
created_at: 2026-08-31 14:33 JST
provider: Claude
phase: phase_8
package: P8-MR7-0_through_P8-MR7-6
frozen_acceptance_matrix: phase_8_acceptance_matrix_ja.md（本Addendumは書き換えない）
supersedes: phase_8_post_manual_acceptance_bounded_rework_acceptance_disposition_addendum_ja_20260831132631.md
supersede_reason: >-
  P8-CODEX-018（Controller Review 2026-08-31 13:48:26 JST）が、旧AddendumのTable行数（33）と集計式
  （PASS 34 + PARTIAL 1 + USER MANUAL GATE 1 = 36）が数学的に矛盾し、かつP8-ACC-039を「条件付きPASS」と
  計上した根拠（Controller自身が実測した4 Test Failure）と矛盾すると指摘した。本Addendumは
  Frozen Matrixの40件全件を個別に再導出し、合計が必ず40になるよう機械検証する。
```

## 1. 集計（機械検証）

```text
PASS               38
PARTIAL             1  (P8-ACC-038)
FAIL                0
USER MANUAL GATE    1  (P8-ACC-040)
NOT RUN             0
--------------------------------
TOTAL              40  (= Frozen Matrixの行数と一致)
```

検算：`38 + 1 + 0 + 1 + 0 = 40`。Frozen Matrix（`phase_8_acceptance_matrix_ja.md`）の行数は40であり、
本Table行数も40（下記§2）——ID数・Table行数・集計式の3つが相互に一致することを目視でも確認できる。

## 2. P8-ACC-001〜040 個別再導出

| ID | Disposition | Evidence |
|---|---|---|
| P8-ACC-001 | PASS | Phase 7 Local RAG／Citation／Data Controls／Persistenceの既存Testが本Packageでも全通過（Backend Full Suite内）。Regressionなし。 |
| P8-ACC-002 | PASS | Manual URL OFF時`network_calls_made=0`。`fetch_direct_url()`のDISABLED分岐は本Package無変更。 |
| P8-ACC-003 | PASS | `ALLOWED_SCHEMES = {"http", "https"}`無変更。 |
| P8-ACC-004 | PASS | `url_security.py`の拒否ロジック本体は無変更。P8-MR7-1で追加した`resolver`パラメータはDNS解決の呼び出し先を差し替える注入点であり、判定ロジック自体（Private／Loopback／Link-local／Metadata／危険Port／Credentials）には触れていない。 |
| P8-ACC-005 | PASS | `HttpxWebFetchProvider._attempt_one_hop()`はRedirect Hopごとに`validate_url_before_connect()`を呼ぶ既存構造を維持（`resolver`引数を追加で伝播するのみ）。 |
| P8-ACC-006 | PASS（強化） | Timeout／Content Type有界化は無変更。P8-MR7-4で`MAX_FETCHED_CONTENT_CHARACTERS`を`max_response_bytes`の上限（10,000,000）に整合させ、Byte Cap内で正常取得したContentが`WebEvidence`構築時に未分類Crashする欠陥を解消——Size有界化の実効性が強化された。 |
| P8-ACC-007 | PASS | JavaScript／Cookie／Login／Form／Download実行なし。無変更。 |
| P8-ACC-008 | PASS | Untrusted Label表示。無変更。 |
| P8-ACC-009 | PASS（強化） | 明示操作時だけEvidenceをMain Modelへ渡す。P8-MR7-4で、Web Evidence自体がTurnの実際のToken Budgetに収まらない場合もMain Model Call 0のTyped `content_budget_exceeded`へ収束するようになり、Fail-closed Groundingの適用範囲がFetch失敗時だけでなくBudget超過時にも及ぶよう強化された。 |
| P8-ACC-010 | PASS | Canonical URL／取得時刻／Digest／Source Class／Transformationは無変更で維持。P8-MR7-3でSchema 1／2の旧Recordからもこれらが正しく復元されるようになった（下記P8-ACC-011と表裏一体）。 |
| P8-ACC-011 | PASS | Reload／Restart後もURL Evidence／Citationを復元する。本Packageで2件の実欠陥を解消：(1) P8-CODEX-014 — ERROR-terminal（Fail-closed Grounding発火時）のTurnがWeb Citation Evidenceを一切永続化していなかった問題を`fail_generation()`への`web_search_result`伝播と`CommitConversation`のTurn State制約緩和で解消。(2) P8-CODEX-015 — Schema 1／2の旧Recordが`corrupt_record`へFail-closed退行していた問題を`_upgrade_web_citation_payload()`のReader側Upgradeで解消。いずれも実Encoded SQLite Record／実ERROR Event経路でRegression Test済み（Revert→Fail確認→復元）。 |
| P8-ACC-012 | PASS | Fetch成功とContent信頼を同一視しない。Aggregate＋Specific Reasonの両方を保持。無変更。 |
| P8-ACC-013 | PASS | Branch操作UI既定非表示。本Reworkの変更対象外、既存Testで維持を確認。 |
| P8-ACC-014 | PASS | Branch Data／API／履歴保持。本Reworkの変更対象外、既存Testで維持を確認。 |
| P8-ACC-015 | PASS | Data ControlsからArchive済みChatをLazy一覧表示。P8-MR3実装（Preserved Baseline）、本Packageで再実装・Rollbackなし。 |
| P8-ACC-016 | PASS | Archive済みChatのTitle／Timestamp表示、開ける。Preserved Baseline。 |
| P8-ACC-017 | PASS | Archive解除後、手動Resumeなしで送信可能。Preserved Baseline。 |
| P8-ACC-018 | PASS | 完全削除／一括Delete／Exportの虚偽表示なし。本Reworkで追加していない。 |
| P8-ACC-019 | PASS | `constitution/` Manifest／Rule／ViewのRevisionとDigest検証。本Reworkの変更対象外、既存Testで維持を確認。 |
| P8-ACC-020 | PASS | ConstitutionとGD Providerの疎結合並列Result。本Reworkの変更対象外。 |
| P8-ACC-021 | PASS | OFF／OBSERVE／ENFORCEの差がEvidenceで確認できる（P8-RW7で確立）。本Packageで無変更、Preserved Baseline。 |
| P8-ACC-022 | PASS | Constitution OFFでもPlatform Security解除せず。本Reworkの変更対象外。 |
| P8-ACC-023 | PASS | Constitution ViewはAuthority追加不可。本Reworkの変更対象外。 |
| P8-ACC-024 | PASS | 不明Rule／Conflict／Digest不一致を黙ってPassにしない。本Reworkの変更対象外。 |
| P8-ACC-025 | PASS | Agent CoreへGD名／Provider／User PathをHard-codeしない。本Reworkの変更対象外。 |
| P8-ACC-026 | PASS | 通常ChatとDev Agent PreviewをUIで切替可能。Preserved Baseline（P8-MR5／6、本Packageで無変更）。 |
| P8-ACC-027 | PASS | Stable Capability IDとDisplay Name分離。Preserved Baseline。 |
| P8-ACC-028 | PASS | Run／Step／State／Tool Request／Result／Dispositionを追跡可能（P8-MR5のStep Input REST投影で確立）。Preserved Baseline。 |
| P8-ACC-029 | PASS | Tool Port／RegistryとAdapterが交換可能（`FakeToolPort`／`FixtureWorkspaceToolPort`）。Preserved Baseline。 |
| P8-ACC-030 | PASS | Fake／Deterministic Toolの複数Step Golden Pathが完了。Preserved Baseline。 |
| P8-ACC-031 | PASS | MCP Client Adapter Portを持つがRemote MCP完成を主張しない。本Reworkの変更対象外。 |
| P8-ACC-032 | PASS | Plan-only／Manual／Risk-based／Important-gate-onlyを区別する。本Reworkの変更対象外。 |
| P8-ACC-033 | PASS | Important-gate-onlyはFrozen Envelope内だけ逐次確認なしで進む。Preserved Baseline。 |
| P8-ACC-034 | PASS | External Write等でGate待機。Preserved Baseline。 |
| P8-ACC-035 | PASS | HarnessがProvider／Platform強制Gateを迂回しない。Preserved Baseline。 |
| P8-ACC-036 | PASS | Max Step／Deadline／Retry／Budget／Loop防止が作用する。Dev Agent側Preserved Baseline。Web Fetch層のBounded Retry（P8-MR1由来、本Packageで無変更）も同じ規律の別実装として維持。 |
| P8-ACC-037 | PASS | Stop／Cancel後のLate ResultがCurrentへ追加されない。Preserved Baseline（Dev Agent、本Packageで無変更）。 |
| P8-ACC-038 | PARTIAL | Run／Step／Tool／Approval／Constitution／GDのID相関永続化はFoundation BoundaryとしてPARTIALのまま——本Packageのスコープ外（P8-CODEX-013〜018はGD相関に触れない）、根拠なくPASSへ昇格させない。 |
| P8-ACC-039 | PASS | 本Package完了時点のCanonical Verificationが全てClean：Backend Full Suite `2186 passed, 7 deselected`（Deselectedは`model_smoke`のみ、意図的除外）／Ruff Check `All checks passed`／Ruff Format Check `563 files already formatted`（Controller指摘の5 File含め全てClean化）／Mypy `Success: no issues found in 346 source files`／Frontend Typecheck・Test（315 passed, 33 files）・Lint・Buildも全てClean。Controllerが実測した4 Test Failureは本Packageで解消し、再実測でPASSを確認した（§4）。 |
| P8-ACC-040 | USER MANUAL GATE | User実画面でManual URL、Archive管理、Chat／Agent切替、Gate／Stopを確認できる。本Reworkの直接対象だが、Codex ControllerとUser自身の実画面再確認が別途必要——本Addendumはこの項目のPASSを主張しない。 |

## 3. 前回Addendumとの差分

```text
旧: PASS 34, PARTIAL 1, USER MANUAL GATE 1, 未再導出 4 -> 記載Table行数33、集計式が36（矛盾）
新: PASS 38, PARTIAL 1, USER MANUAL GATE 1 -> Table行数40、集計式が40（一致）
```

差分の内訳：

```text
P8-ACC-013／014／019／020／024／025／031／032：
  旧Addendumで「未再導出（Handoff指定Scope外）」として省略していた8件を、今回は個別に再導出しPASSとして明記した
  （実質的なDisposition変更ではなく、集計の完全性を回復する再導出）。
P8-ACC-009／010／011／028／029／036／039：
  旧「PASS(強化)」「PARTIAL->PASS」等の注記付きDispositionを、今回は無印PASSへ整理した
  （Frozen Matrix自体にDisposition強調のColumnは無く、注記は本文Evidence欄に統一した）。
P8-ACC-039：
  旧「条件付きPASS」からPASSへ更新。Controllerが実測した4 Test Failureを本Packageで解消し、
  Canonical Verification全体を再実測してClean化を確認したため。
```

## 4. Controller 4 Failure再実測結果

```yaml
command: >-
  ./.venv/bin/pytest -q --tb=short
  tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_is_injected_as_an_untrusted_tool_message
  tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_html_noise_is_stripped_and_budgeted_before_injection
  tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn
  tests/unit/conversation/test_conversation_generation.py::test_guardrail_context_source_hook_also_governs_manual_web_evidence
result: "4 passed in 0.21s"
network_used: false
resolver_injected: true
```

## 5. Honesty Note

- P8-ACC-038は根拠なくPASSへ昇格させていない——本Packageの変更範囲（P8-CODEX-013〜018）はGD相関永続化に触れていない。
- P8-ACC-040はUser Manual Gateのままであり、本Addendumのいかなる記述もUser自身による実画面再確認を代替しない。
- P8-ACC-039のPASSは「本Session環境でのCanonical Verificationが実際にCleanになった」ことに基づく——Codex Controller自身の
  環境での再実行が別途必要であり、本Addendumはその結果を先取りしていない。
