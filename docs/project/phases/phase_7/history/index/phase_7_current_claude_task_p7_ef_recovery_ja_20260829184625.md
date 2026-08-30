# Phase 7 Current Claude Task — Package P7-E/F Recovery（Web Search／Fetch／Security Boundary／Evidence Governance）

```yaml
document_id: phase_7_current_claude_task_p7_ef_recovery_20260829184625
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 18:46:25 JST
active_contract: phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md
package: P7-E, P7-F
```

## 0. Recovery Index Pointer

前Package: [P7-B/C/D Recovery](phase_7_current_claude_task_p7_bcd_recovery_ja_20260829182237.md)。次Package: P7-G（Data Controls）。

## 1. Bounded Network決定（重要）

Handoff §5 Authorityは「Credential、課金、Account作成、有料Search Providerを必要としない範囲」のReal Public Web Probeを許容するが、**本Packageでは実施しなかった**。理由：

```text
無料・無Credentialで使える一般Web Search APIが存在しない（主要Search Provider
  はほぼ全てAPI Key／課金契約を要求する）。
Handoff自体が「最低1つのManual Search Golden PathをFixture／Fake Providerで
  成立させ」ることを明示許容しており、Real Public Webは「Authorityと安定性が
  成立する場合だけ」という条件付き任意事項である。
Test Suiteの安定性・再現性（CI・再実行時の非決定性排除）を優先した。
```

Real Network Action: 0（Search／Fetch双方）。この判断はP7-0 Recovery §5で先行documentedし、本Packageで実施結果として確定した。

`WebSearchActivation.AUTOMATIC`（P7-REQ-013のTrigger Heuristics）は本Task未着手。`WebKnowledgeService.search_and_fetch()`はAUTOMATIC選択時に`NotImplementedError`を送出し、将来の呼出し元が無言のNo-opへ縮退することを防ぐ。

## 2. 実装（Backend、`modules/web_knowledge/`）

### 2.1 Contracts

`WebSearchActivation`(disabled/manual/automatic)、`WebEvidenceGovernanceMode`(off/observe/enforce，Activationとは独立Axis)、`SourceAuthorityClass`(official/primary/secondary/general/unknown，Host Suffix Heuristic)、`WebSearchQuery`/`WebSearchResultItem`/`WebSearchRun`(Canonical `RetrievalRun`相当)、`WebEvidence`(`rejected`／`fetched`／`withheld_by_governance`の3独立状態——ENFORCEがPrompt Injection検出後に「実際に取得したがContentを非公開にした」ことを、Reject（未取得）や生Content公開のどちらとも異なる誠実な状態として表現)、`WebCitation`、`WebSearchAndFetchResult`(`activation=DISABLED`なら`network_calls_made==0`をModel Validatorで機械的に強制)。

### 2.2 URL Security Boundary（`domain/url_security.py`、SSRF対策）

`validate_url_before_connect()`：Scheme許可List(http/https)、Credentials-in-URL拒否、IP Literal／DNS解決結果のPrivate／Loopback／Link-local／Multicast／Reserved拒否（Cloud Metadata IP `169.254.169.254`含む）、Metadata Hostname明示Denylist。既知の限定事項（Phase 10 Hardening候補としてDocument化）：DNS解決結果のIPをそのままSocket接続へPinningしていない（DNS Rebinding耐性は将来課題）。

### 2.3 Prompt Injection Detector（`domain/prompt_injection_detector.py`）

Pattern-basedヒューリスティック（Model-backedではない、明示的にDocument化）。

### 2.4 Application（`WebKnowledgeService`）

Search→（URL Security Boundary）→Fetch→（Governance Mode別Injection Scan）→Citation、の単一Pipeline。`network_calls_made`はAttempted Call数（成功可否によらない、Evidence／Audit目的）。Fetch Provider由来の予期しない例外もEvidence化しCrashへ波及させない。

### 2.5 Adapter（`adapters/web_knowledge/`）

`FixtureWebSearchProvider`/`FixtureWebFetchProvider`：本Task実Runtimeで使用する実Composition（Test Doubleではない）。実在・安定した公開Domain（python.org等）をキーワード一致で返す、正直にFixture-labelledな固定Sample。`HttpxWebFetchProvider`：実httpx Request構築・Redirect追跡（各Hop再検証）・Streaming Size Cap・Timeout。`httpx.MockTransport`で実HTTP Semanticsを検証（実Socket 0）。

## 3. 実装（Web API／Bootstrap）

`/api/v2/web-search/runtime`(GET)、`/api/v2/web-search/search`(POST、`activation`のみClient指定可、`automatic`はRequest Validationで拒否)。`governance_mode`はServer Config専用（CLI Flag `--phase-7-web-search-governance-mode`、Client Request Bodyに含めても`extra=forbid`で拒否——Client側からGovernance Policyを上書きできないことをTestで直接証明）。`--phase-7-web-search`はLoopback-only Gate（既存Local Corpus等と同一Pattern）。

## 4. 実装（Frontend）

`frontend/index.html`へ`web-search-bootstrap`Marker追加。基本設定（`SettingsPanel.tsx`）の要約Mode／RAG設定列の最上段へ、同一Segmented Control形式でWeb検索OFF/ON Toggleを追加（既定OFF、Position順序をTestで直接検証）。Advanced Mode配下へ`WebSearchPanel.tsx`（Query入力→検索→Evidence一覧、Toggle OFF時は入力・Buttonを無効化）。

## 5. Focused Evidence

```text
tests/unit/web_knowledge/test_url_security.py ... 19 passed
tests/unit/web_knowledge/test_prompt_injection_detector.py ... 5 passed
tests/unit/web_knowledge/test_web_knowledge_service.py ... 10 passed
tests/unit/web_knowledge/test_httpx_fetch_provider.py ... 10 passed（httpx.MockTransport、実Socket0）
tests/integration/web/test_web_search_web_app.py ... 8 passed
frontend: WebSearchPanel.test.tsx ... 6 passed
frontend: SettingsModal.test.tsx ... +3 passed（Panel Gating×2、Toggle位置・既定値×1）
```

新規Backend Test Node ID: 19+5+10+10+8 = 52。新規Frontend Test: 6+3 = 9（240→249）。

## 6. Canonical Evidence

```text
Backend pytest（Full Suite） : 1898 passed, 7 deselected（Baseline 1846 + 52新規 = 1898、一致確認済み）
mypy（Project既定）          : Success、515 source files
ruff check . / format --check .: All checks passed／All formatted
frontend: typecheck／lint    : Clean
frontend: npm test           : 249 passed（27 files）
frontend: npm run build      : Clean（89ms）。web-search-bootstrap Marker、Build出力へ反映確認済み。
```

## 7. Requirement／Acceptance対応（暫定、最終集計はP7-I）

```text
P7-REQ-007〜011、013〜015: 実装・Test済み（013のAutomatic Triggerのみ明示未着手）。
P7-ACC-002〜003（RAG／Web検索OFFでNetwork Call 0）: PASS（機械Validator＋Route Test）。
P7-ACC-016〜023: PASS（Manual Search Port経由実行、Snippet/Fetched Content分離、
  Canonical URL/Provider/取得時刻/Digest Evidence化、Source Authority区別、
  Private/Metadata拒否、危険Scheme/Redirect/巨大Response/Timeout有界化、
  Secret/PII——Query自体はUser入力そのまま送信するため無断加工はしないが、
  外部送信はUser自身の明示Actionによるものであり、Governance Modeによる
  Fetched Content側のPrompt Injection Detection EvidenceはPASS）。
P7-ACC-024（Toggle配置）: PASS（DOM順序をTestで直接確認）。
```

## 8. Known Findings／Deferrals

```text
P2: DNS解決結果IPのSocket接続直接Pinning未実装（DNS Rebinding耐性、Phase 10 Hardening）。
P2: WebSearchActivation.AUTOMATIC（自動Trigger Heuristics）は未着手のまま。
P3: Real Search Provider接続は無Credential手段が存在しないため、将来Contract成立後の課題。
```

## 9. Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0（Real Public Web Probe不実施、上記§1参照）
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Package P7-G（Data Controls）実装へ継続。
