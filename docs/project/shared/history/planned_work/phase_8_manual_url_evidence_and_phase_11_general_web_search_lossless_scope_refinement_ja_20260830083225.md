---
document_id: phase_8_manual_url_evidence_and_phase_11_general_web_search_lossless_scope_refinement_20260830083225
document_type: append_only_lossless_scope_refinement_and_user_decision
document_state: current_decision_reserved_not_started
language: ja
recorded_at: 2026-08-30 08:32:25 JST
decision_authority: user
authority_owner: Nazuna Research
maintainer_role: プロジェクト責任者兼設計統括者役
amends_by_reference:
  - docs/project/phases/phase_7/history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md
  - docs/project/shared/history/planned_work/phase_11_plus_governed_external_web_knowledge_runtime_reservation_ja_20260829222647.md
implementation_authorized: false
network_authorized: false
---

# Phase 8 Manual URL Evidence／Phase 11 General Web Search — Lossless Scope Refinement

## 1. 結論

Web Knowledge機能を、次の2段階へ分離する。

```text
Phase 8冒頭:
  1. Userが貼ったURLを明示操作で取得し、画面へ表示する。
  2. Userが貼ったURLのContentを、Untrusted External Evidenceとして
     LLMへ渡し、URL／Digest付きCitationを出す。

Phase 11以降:
  3. Search Providerを使った一般Web検索。
  4. LLMが必要性を判断して自動検索する。
  5. Provider／Account／Credential／Cost／Privacy／Public Demo／
     Hostile-site／Data Qualityを含むGoverned External Web Runtime。
```

Phase 7時点の「一般URL Fetchを含む実External Web Runtime全体をPhase 11以降へ延期」という判断を隠さず保持する。その後のUser Decisionにより、**Userが明示的に貼ったURLを読む限定機能だけをPhase 8冒頭へ前倒し**する。General Web SearchおよびAutomatic SearchはPhase 11以降のままである。

## 2. 起点となった問題認識

Userは、一般的なSite検索だけであっても、現在の個人PoC／MVP条件で適した方式が本当に存在しないのかを再確認した。

検討済みの方式には次のTrade-offがある。

### 2.1 Hosted Search API

Brave、Tavily、Exa、SerpAPI等はGeneral Web Indexを利用しやすい一方、Account、API Token、料金、Quota、Rate Limit、Query Privacy、Terms、Credential保管および失効対応が必要である。

Account登録自体はUserが将来許容し得るが、Token一個だけの問題ではない。外部へ何を送り、誰がCostとPrivacyを負い、公開Demo利用者のQuotaをどう分離するかという運用契約が付随する。

### 2.2 SearXNG

Private SearXNGはVendor Account／Card／API Tokenを避けられる有力候補だが、Docker／Podman、設定、Engine選定、更新、Rate Limit、Log、Privacy、障害対応および公開時の濫用対策が必要になる。当面Server／Lightning／Home Serverを常用しない状況では、Web検索のためだけに運用対象を増やすCostがある。

Public Instanceは登録不要で使える場合があるが、JSON APIの有無、Availability、Rate Limit、Privacy、運営主体、Engine構成および結果品質をProject側で保証できない。公開OSS／Demoの既定EndpointへHard-codeしない。

### 2.3 Search Engine HTML Scraping／Browser Automation

Account不要で動く場合があっても、HTML変更、CAPTCHA、Bot対策、地域差、Rate Limit、TermsおよびParser破損に弱い。安定したProduction既定方式にしない。

### 2.4 Domain限定API／RSS

Wikipedia／MediaWiki、RSS、個別公式APIは限定Sourceとして有用だが、General Web Searchの代替ではない。

### 2.5 General Search Engine自作

単なるHTTP Clientでは成立しない。

```text
Crawler
  -> Robots／Rate Limit／取得Policy
  -> Storage／更新Scheduler
  -> Duplicate／Near-duplicate処理
  -> Index／Ranking／Freshness
  -> Delete／Correction対応
  -> Search API／運用監視
```

これはPhase内の小機能ではなく、単独System／Project級である。現在のPoCで自作General Web Indexへ進まない。

## 3. 「自己責任」方式で軽くできる範囲

Userは、Provider登録や全機能の保証を必須とせず、Local利用者の自己責任、既定OFF、明示操作という形式なら成立範囲を縮小できないかを確認した。

結論として、Local／User明示URLに限定すれば、Public Demo、Multi-user Abuse、Search Provider Account、Automatic Query、General Discoveryおよび高度なData Quality GovernanceをPhase 8の必須Scopeから外せる。

ただし「自己責任」という表示はSecurity Controlの代替ではない。最低限、次を保持する。

- 許可SchemeはPublic `http`／`https`だけ。
- `file:`、`data:`、`javascript:`、`ftp:`、`git:`、`ssh:`等をGeneric URL Readerで扱わない。
- localhost、Private／Loopback／Link-local、Cloud Metadata相当を拒否する。
- Redirect先も再検査する。
- Timeout、Response Size、Redirect Count、Content-Typeを有界化する。
- JavaScriptを実行しない。
- Cookie、User Credential、Authorization Headerを自動付与しない。
- 取得ContentをSystem／Developer Instruction Authorityへ昇格しない。
- Sourceが正しい、Clean、安全、最新またはTraining EligibleだとはClaimしない。

高度な汚染Data対策、攻撃Site Sandbox、PDF／Archive／Media Parser Isolation、Data Poisoning研究および企業級HardeningはPhase 8の限定機能へ含めない。

## 4. Capability別の規模判断

| Capability | 規模判断 | Current Decision |
|---|---:|---|
| 貼ったURLを取得してPanelへ表示 | 小 | Phase 8冒頭へ前倒し |
| 貼ったURLをLLM Evidenceとして読む | 小〜中 | Phase 8冒頭へ前倒し |
| LLMが一般Webを手動検索する | 中 | Phase 11以降 |
| LLMが必要時に自動検索する | 中〜大 | Phase 11以降、Manual成立後の別Gate |
| Search Engine／Crawler／Index自作 | 特大 | 現在不採用 |

現在のRepositoryには、Phase 7で次のScaffoldがある。

- Provider-neutral Search／Fetch Port。
- `HttpxWebFetchProvider`。
- Public `http`／`https`、DNS／Private IP／Metadata、RedirectのMVP Security Boundary。
- Timeout、Response Size、Content-Type制限。
- Prompt Injection Pattern Detector。
- Web Evidence、URL、Digest、Provider、CitationのContract。
- Fixture ProviderとTest。

したがってManual URL Readerをゼロから作る必要はない。Production Binding、URL入力Contract、本文抽出／Normalization、External Untrusted EvidenceとしてのChat接続、Citation Persistence、Consent／Failure表示およびUser Manual Gateが主な残作業である。

## 5. Development Agentとの関係

Userは、URL Readerが`http/https`以外を拒否した場合、将来のMARGPA Development Agentが技術選定できるのかを質問した。初回回答ではFilesystem／MCP等のTool Protocol分離を中心に説明し、質問の主旨を取り違えた。その後、次のように訂正した。

### 5.1 Protocol制限は技術選定を妨げない

技術選定に使う一般的な公開Evidenceは、ほぼHTTPSで取得できる。

- 公式Documentation。
- GitHub／Hugging Face。
- Package Registry／Release Notes。
- Issues／Discussions。
- 論文、Benchmark、公式Blog。

実Clone、Package取得、Shell、MCPまたはLocal Previewは、Generic External URL Readerではなく専用Tool／Authorityで扱う。したがってExternal URL ReaderをPublic HTTP(S)へ限定しても、将来の自動検索や技術選定の本質的障害にはならない。

### 5.2 Phase 8とPhase 11の能力差

```text
Phase 8:
  UserがURLを提供
    -> Agent／通常ChatがContentを読む
    -> 比較・分析・技術選定を補助

Phase 11以降:
  Agent自身が候補を発見
    -> Search Queryを反復
    -> 複数Sourceを収集・比較
    -> 自律的な技術選定へ進む
```

Phase 8時点でも、Local CorpusおよびUser提供URLを根拠にした技術選定は可能である。候補発見を含む自律ResearchにはPhase 11以降のSearch Provider／Automatic Searchが必要である。問題は`http/https`制限ではなく、Search Capabilityの有無である。

## 6. Public／Private境界

Phase 8のManual URL Readerは、Local Loopback／User明示操作／自己責任のResearch Previewとする。Public Demoで自動有効化しない。

```text
Default Activation       : OFF
Automatic Fetch          : FORBIDDEN
Automatic Search         : NOT IMPLEMENTED
External Query Provider  : NONE
User URL                 : EXPLICIT ONLY
External Transmission    : EXPLICIT CONSENT／ACTION
Content Authority        : UNTRUSTED EXTERNAL EVIDENCE
Public Demo Default      : DISABLED
```

URLがPromptへ含まれているだけで暗黙Fetchしない。Network ActionとLLM Evidence採用はUserが区別できるUI／Statusで扱う。

## 7. Phase 11へ残すもの

- General Web Search Provider選定。
- Hosted API／Private SearXNG／限定API比較。
- Account、Credential、Secret、Cost、Quota、Privacy、Terms。
- Server Canonical `disabled／manual／automatic`。
- LLMによるSearch Need判定、Query生成、反復検索。
- Search Result Ranking、Source Selection、Contradiction処理。
- Provider CallとOutbound Network Callの正確なObservability。
- Secret／PII Query GateとExternal Transmission Enforcement。
- Prompt Injection／Data Poisoning／Spam／Duplicate／Source Quality。
- Hostile-site Sandbox、Parser Isolation、PDF／Archive／Media Tier。
- Public OSS／Demo Deployment Operator Contract。

## 8. Current Decision

```text
Phase 8 Entry:
  Manual pasted-URL fetch and display             : RESERVED
  Manual pasted-URL LLM Evidence／Citation         : RESERVED

Phase 11 Plus:
  General Web Search Provider                     : DEFERRED
  LLM-triggered automatic search                  : DEFERRED
  Self-host／Hosted Provider operational contract : DEFERRED

General Search Engine from scratch                : REJECTED CURRENTLY
Implementation Authority                         : FALSE
Network Authority                                : FALSE
```

本書は予約とScope再分類であり、実装、Network、Provider Account、Credential、Git、Phase ClosureまたはPhase移行Authorityを与えない。

