---
document_id: phase_7_codex_controller_bounded_independent_review_adjust_20260829215534
document_type: controller_independent_review
document_state: frozen
language: ja
created_at: 2026-08-29 21:55:34 JST
review_owner: Codex_プロジェクト責任者兼設計統括者役
review_target_provider: Claude
review_target_role: 設計者兼実装者役
review_target_return: phase_7_claude_bounded_mvp_implementation_exact_return_handoff_ja_20260829191047.md
review_policy: poc_mvp_portfolio_resource_constrained_bounded_review
verdict: ADJUST_BOUNDED_WEB_REWORK_REQUIRED
phase_7_closure: false
phase_8: not_started
git_action: none
---

# Phase 7 — Codex Controller Bounded Independent Review

## 1. 結論

ClaudeのP7-0〜P7-I成果は、Local Corpus、Data Controlsの基礎、Web Search／FetchのPort、SSRF／Prompt Injection／Secret検査およびFrontend Panelについて有効な実装を含む。ただし、現在のWeb機能は実Web検索としてUser主経路へ届かず、Web検索OFFおよび外部送信ConsentもServer正本として強制されていない。

したがって、現在の`COMPLETE_CANDIDATE`は受理しない。

```text
Controller Verdict: ADJUST / BOUNDED WEB REWORK REQUIRED
Local Corpus: ACCEPTED BASELINE
Data Controls Schema／Persistence／UI: ACCEPTED BASELINE
Web Security Port／Fixture Tests: ACCEPTED BASELINE
Phase 7 Closure: NOT ALLOWED
Phase 8: NOT STARTED
```

ReworkはWebの実利用経路に限定する。Local Corpusを再実装せず、Enterprise HardeningやAutomatic Trigger Heuristicsへ拡大しない。

## 2. Review Boundary

次だけを確認した。

- Frozen Requirements／Architecture／Acceptance／Exact Handoff。
- Claude Exact Return HandoffおよびP7-I Final Recovery。
- Local Corpus、Web Search／Fetch、Data ControlsのProduction Composition、Route、Service、Frontend状態。
- User主経路、虚偽表示、外部送信、次Phase土台へ直接影響する事項。
- 変更範囲に直結するController Focused Test。

次は行っていない。

- Canonical Full Suiteの再実行。
- Real Public WebへのSearch／Fetch。
- Real Browser操作。
- Git操作。
- Phase 6 Known Debtの再調査。
- 理論Edge CaseまたはEnterprise級Hardeningの追加探索。

## 3. 成立を確認した範囲

### 3.1 Local Corpus

- Local Documentの登録、更新、削除、検索。
- Existing Documentation RAGへのComposite Source合成。
- Selected EvidenceのContext Injection。
- CitationおよびConversation Persistence経路。
- Source Class、Revision、DigestのContract。

Local CorpusはPhase 7の成立済みBaselineとして保持し、Web Reworkで再実装しない。

### 3.2 Web／Data Controlsの土台

- Provider非依存Search／Fetch Port。
- URL Security、Redirect、Private／Loopback／Metadata Endpoint、Response Size、Timeoutの境界。
- Prompt Injection DetectionおよびSecret様QueryのFail-closed検査。
- SnippetとFetched Contentの構造的分離。
- Data ControlsのRetention FactとPurpose Consentの分離。
- Settings内Web検索Toggle、Local Corpus／Web／Data Controls Panel。

### 3.3 Controller Focused Verification

```text
Backend Focused: 111 passed
Frontend Focused: 4 files / 39 tests passed
Exit Code: 0
```

Project内Task Tempだけを使用した。ClaudeのCanonical Full Evidenceは再利用し、無意味な再実行を行っていない。

## 4. Open Finding

### P7-CODEX-001 — Production Web SearchがFixture固定

```yaml
severity: major
priority: P0
closure_blocker: true
impact_scope: user_web_search_primary_path
ownership: controller_contract_gap_and_implementation_gap
```

`bootstrap/web_knowledge.py`は`FixtureWebSearchProvider`と`FixtureWebFetchProvider`をProduction Compositionへ固定している。現在の検索結果はPython、FastAPI、Wikipedia等の固定Sampleであり、Public WebのCurrent情報を検索しない。

これはClaudeだけの逸脱ではない。Controller Exact Handoff §4がFixture／FakeによるManual Golden Pathを許可し、Real Public Webを条件付きにしたため、Contract自体がUserの「古いModel知識をWebで補う」という目的をClosure条件へ十分固定できていなかった。

Phase 7 Closureには、少なくとも次のいずれかを正本として選ぶ必要がある。

1. User指定SearXNG EndpointによるCredential-free General Search。
2. User提供Credentialを使うGeneral Search API Adapter。
3. Direct URL Fetch＋限定Search Providerを明示した縮小MVP。

FixtureはTest Providerとして残せるが、実Web検索として表示しない。

### P7-CODEX-002 — Manual Web EvidenceがChat回答へ接続されない

```yaml
severity: major
priority: P0
closure_blocker: true
impact_scope: web_grounded_answer_and_citation
```

現在のWeb検索はSettings内の独立Utilityであり、検索／取得したEvidenceをMain Modelへ渡せず、Web CitationをConversationへ保存できない。Architectureの中心経路`Web Search／Fetch -> Evidence Assembler -> Context Injection -> Main Model -> Citation Persistence`が未成立である。

`manual`はUserが検索を明示起動する方式であり、Evidenceを回答へ使用しないことを意味しない。Automatic Trigger Heuristicsを実装しなくても、Userが選択した検索結果を「次の回答で使用」するOne-shot Manual Bindingは成立できる。

Bounded ReworkではAutomaticを延期したまま、Manual Evidenceだけを次Turnへ有界注入し、Citation／Request ID／Conversationへ相関する。

### P7-CODEX-003 — Web検索OFFがFrontend Local StateでServer正本ではない

```yaml
severity: major
priority: P0
closure_blocker: true
impact_scope: network_zero_call_contract
```

Settingsの`webSearchMode`はReact Local Stateで初期化・切替されるだけで、Server Runtime状態として保存／照合されない。Search実行時は常にClientから`activation=manual`を送る。Server RouteはClient値を受理するため、画面がOFFでもAPI直接呼出しによりSearch Providerを実行できる。

現TestはRequest Bodyへ`activation=disabled`を送った場合の0 Callだけを証明しており、Userが設定したOFF状態の強制を証明していない。

Server Canonical Snapshotへ`disabled／manual`を置き、OFF時はClient Requestに関係なくSearch／Fetch Adapter Call 0へ収束させる。

### P7-CODEX-004 — 外部送信ConsentとPII GateがWeb実行経路へ未接続

```yaml
severity: major
priority: P0_before_real_provider
closure_blocker: true_for_real_network
impact_scope: external_query_transmission_and_privacy
```

`external_query_transmission_consent`は保存・表示されるが、Web Route／ServiceはData Controls Storeを参照しない。このままReal Providerへ差し替えると、Consent既定OFFでもQueryを外部送信できる。

Secret様Pattern検査は成立しているが、P7-REQ-015／P7-ACC-022が求めるPII候補の無断送信まで満たしていない。General PIIを無制限に推測する必要はないが、明白なEmail／Phone等の有界検査または送信前確認が必要である。

Real Provider接続前に、Consent=falseでOutbound Call 0、明白なSecret／PII候補でFail-closedまたは明示確認、送信Query最小化をTestする。

### P7-CODEX-005 — `network_calls_made`がFixture Callを実Networkと表示

```yaml
severity: moderate
priority: P1
closure_blocker: false_if_P7_CODEX_001_rework_corrects_projection
impact_scope: observability_truthfulness
```

現在の`network_calls_made`はProvider Port Attempt数であり、Fixture Providerでも2以上になる。実Socket／Outbound Networkは0であるため名称がUserへ誤解を与える。

`provider_calls_attempted`と`outbound_network_calls_attempted`を分離するか、少なくともFixture／Network Provider種別と表示文言を一致させる。本Findingだけで追加Rework Loopを作らず、P7-CODEX-001のProvider修正時に同時是正する。

## 5. Deferred／Non-blocking

次はPhase 7 Closureを止めない。

- Automatic Web Search Trigger Heuristics。
- Embedding Adapterの実使用。Current BM25 Baselineを維持する。
- Chat Composer汎用File Attachment。
- Data Controlsの全Project横断Export／一括Delete。
- DNS Rebinding等の追加Hardening。
- Local Corpus Title変更時のIdentity改善。
- Web Search Progressive Streaming等のUI Polish。

## 6. Provider Decision Gate

2026-08-29時点のOfficial Contract確認では、次の差がある。

- SearXNGは`/search?q=...&format=json`のHTTP APIを提供する。ただしJSON形式はInstance設定依存で、多くのPublic Instanceでは無効になり得る。Self-hostまたはUser指定Endpointが必要。
- Brave Web Search APIはGeneral Web IndexとFreshnessを提供するが、`X-Subscription-Token`が必要であり、Credential／Account Authorityなしに実接続できない。
- MediaWiki APIはCredential-free検索が可能だが、対象はWikiでありGeneral Web Searchではない。

したがって、Controllerが勝手にProvider、課金、AccountまたはSecret運用を決めない。User Decision後にExact Differential Rework Handoffを固定する。

## 7. Acceptance Correction

Claude Returnの集計は、実装したFixture／Local範囲のTest結果として保持する。ただしPhase 7 Product Acceptanceとしては次を訂正する。

```text
P7-ACC-003: FAIL — Server Canonical OFF未成立
P7-ACC-011: PASS Local / FAIL Web
P7-ACC-013〜015: PASS Local / NOT IMPLEMENTED Web
P7-ACC-016: PARTIAL — Provider Port Golden Pathのみ、Real Web Searchなし
P7-ACC-022: PARTIAL — Secret成立、PII／Consent Enforcement未成立
P7-ACC-025: PARTIAL — Data Control保存／表示成立、Web実行Enforcement未成立
P7-ACC-028: PARTIAL — Fixture CallとOutbound Networkの区別不足
P7-ACC-032: NOT RUN — User Manual Gate
```

## 8. Final Ruling

```text
Phase 7 Candidate: ADJUST
Rework Scope: Web実利用経路だけ
Preserve: Local Corpus / Data Controls Foundation / Security Ports / Existing Tests
Do Not Add: Automatic Trigger / Enterprise Hardening / Phase 6 Rework
Next Action: User Provider Decision -> Exact Differential Handoff -> Current Claude Task
```

P7-CODEX-001〜004を成立させた後、Controller Focused ReviewとUser Real Browser Manual Gateへ進む。理論上の完全性や追加Edge Caseを理由にPhase 7を無限Reworkしない。
