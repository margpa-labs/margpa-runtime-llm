# Phase 7 External Web Runtime — Phase 11以降への延期Decision

```yaml
document_id: phase_7_external_web_runtime_phase_11_plus_deferral_decision_20260829222647
document_type: user_decision_scope_reclassification_and_lossless_discussion_record
document_state: current_decision
language: ja
created_at: 2026-08-29 22:26:47 JST
decision_authority: user
authority_owner: Nazuna Research
maintainer_role: プロジェクト責任者兼設計統括者役
source_return: phase_7_claude_bounded_mvp_implementation_exact_return_handoff_ja_20260829191047.md
source_controller_review: phase_7_codex_controller_bounded_independent_review_adjust_ja_20260829215534.md
phase_7_external_web_claim: not_implemented
phase_7_preserved_scope: local_corpus_data_controls_web_ports_and_security_scaffolding
external_web_reopen_target: phase_11_or_later
network_authority: false
provider_contract_authority: false
credential_creation_authority: false
```

## 1. 本書の結論

2026-08-29、Userは、Phase 7で実Web検索・一般URL取得・Web EvidenceのChat Groundingを完成させる案を撤回し、**Phase 11以降へ延期**することを明示決定した。

```text
Phase 7で成立済みとして保持:
  Local Corpus登録／更新／削除／検索
  Existing RAGへのLocal Corpus合成
  Local EvidenceのContext Injection／Citation／Conversation Persistence
  Data Controlsの基礎
  Provider非依存Web Search／Fetch Port
  Fixture ProviderとTest
  URL Security／SSRF／Redirect／Size／Timeout／Content Type境界
  Prompt Injection／Secret様Query検査の基礎

Phase 7で完成を主張しない:
  実General Web Search Provider
  外部NetworkへのSearch／Fetch
  Web EvidenceのMain Model回答への注入
  Web CitationのConversation保存
  Server正本によるWeb OFF／ON Enforcement
  外部送信Consent／PII Enforcement
  未知・攻撃的Siteを安全に扱うSandbox

再開先:
  Phase 11以降のGoverned External Web Knowledge Runtime
```

これは問題の不存在、解決済みまたはWeb検索の不要化を意味しない。現在の個人PoC／MVP、資金、AI利用可能量、時間、Hardware、Account／Credentialおよび運用責任では、安全で公開可能な実Web機能をPhase 7内に成立させるCostとRiskを受け止めきれないため、Scopeを明示的に縮小した判断である。

## 2. 起点 — Claude Phase 7 Complete Candidate

ClaudeはP7-0〜P7-Iを実装し、次をComplete Candidateとして返却した。

- Local Corpusを既存Documentation RAGへ合成し、Document登録・更新・削除・検索・Context Injection・Citation・永続化を実装。
- Web Search／Fetch Port、Fixture Provider、実`httpx` Fetch Adapter、SSRF対策、Prompt Injection Detector、Secret様Query検査を実装。
- Retention事実とPurpose別Consentを分離したData Controlsを実装。
- Internal Review 2 Cycleを実施。
- Backend Full `1924 passed`、Mypy `526 files clean`、Ruff clean。
- Frontend `256 passed`、Typecheck／Lint／Build clean。

ただしClaude自身がReturn冒頭で、Web Search／FetchはSettings内の**独立Manual Utility**であり、検索結果はConversation Generation／Main Modelへ注入されないと開示した。Production CompositionもFixture Providerを使用し、Real Public Webは実行していなかった。

このReturnとEvidenceは破棄しない。成立したLocal Corpus、Data ControlsおよびWeb安全境界の基礎は、Phase 11以降で再利用する。

## 3. Controller Independent Reviewで確認した事実

Codex Controllerは、Closureに直接関係するSource／TestをBounded Reviewし、Backend Focused `111 passed`、Frontend Focused `4 files／39 tests passed`を確認した。その上で、次のFindingを記録した。

| Finding | 確認内容 | 技術状態 |
|---|---|---|
| P7-CODEX-001 | Production Web SearchがFixture固定 | 実Web検索ではない |
| P7-CODEX-002 | Manual Web EvidenceがChat回答／Citationへ接続されない | Grounded Answer未成立 |
| P7-CODEX-003 | Web検索OFFがFrontend Local State | Server Canonical Enforcement未成立 |
| P7-CODEX-004 | 外部送信Consent／PII GateがWeb実行経路へ未接続 | Real Provider接続前に必須 |
| P7-CODEX-005 | `network_calls_made`がFixture Port Callも実Networkのように数える | Observability不正確 |

Controller Review時点では、P7-CODEX-001〜004をPhase 7 Closure Blockerとして`ADJUST／BOUNDED WEB REWORK REQUIRED`とした。ただし、この判定は「Phase 7で実Webを完成させる」Scopeを前提とする。

本書のUser Decisionは、その前提自体を変更する。Reviewで確認した技術事実は維持する一方、実Web完成をPhase 11以降へ移したため、P7-CODEX-001〜005をPhase 7の即時Closure Blockerから、Phase 11以降で再開する既知Debtへ再分類する。

## 4. 「後工程への影響」と方式選択で重視した条件

Userは、単に最短で接続できる方式ではなく、次を総合して方式を選ぶよう求めた。

- 後からProviderを変更する際にCoreを作り直さないこと。
- 公開Repository／Demo利用者へ危険な既定値を配布しないこと。
- Account、API Token、課金、Rate Limit、Privacy、Termsの運用負債。
- Local Mac中心で、当面Server／Lightningを使わない現状。
- Modelへ「URLを渡しただけ」でNetwork Authorityを与えたと誤認しないこと。
- 汚染Data、Prompt Injection、攻撃Site、SSRF、巨大ResponseおよびParser脆弱性を過小評価しないこと。
- PoC／MVPとして今成立させる価値と、個人開発者が負うRisk／Costの釣り合い。

General Web Searchは、単にModelへ検索欄を追加するだけではない。

```text
User Request
  -> Search Activation／Consent
  -> Query最小化／Secret・PII検査
  -> Provider Adapter／Credential／Cost Budget
  -> Search Result
  -> URL Fetch／Redirect／DNS／SSRF境界
  -> Parser／Content Normalization
  -> Prompt Injection／Poisoning／Source Quality
  -> Evidence Selection／Provenance
  -> Main Model Context Injection
  -> Citation／Recording／Audit
  -> Error／Fallback／User表示
```

どれか一つを省略すると、動作しないだけでなく、Privacy、Security、虚偽のGroundingまたは公開Demo利用者への危険につながり得る。

## 5. 検討した実Web検索方式

### 5.1 Brave Search API

General Web Index、Freshnessおよび比較的安定したAPI Contractを持つ候補として検討した。技術的にはProvider Adapterを作りやすく、将来の安定運用候補になり得る。

一方、Account、Subscription Token、Plan／Rate Limit、課金、Credential保管、Query送信先、Privacyおよび利用条件の管理が必要になる。2026-08-29時点で確認した公開情報では、従量単価とMonthly Creditを伴うPlanが案内されていたが、価格・条件は将来変更され得るため、実装時に再確認が必要である。

結論：将来候補。UserのAccount／Credential／Cost AuthorityなしにPhase 7で選ばない。

### 5.2 SearXNG Self-host／Private Instance

OSSであり、Vendor Account、CardおよびAPI Tokenを必須としない。Provider非依存のPortとも相性がよい。

ただし、Private Instanceを使うには、Docker／Podman等の実行環境、Instance設定、Search Engine設定、更新、障害対応、Rate Limit、TLS、Log／Privacy、Network Boundaryおよび継続運用が必要になる。当面Server／Lightningを使わずLocal Mac中心で進める現状では、Web検索のためだけに運用対象を増やすCostが大きい。

結論：将来のPrivate／Self-host候補。現在はInstanceを立てない。

### 5.3 Public SearXNG Instance

登録なしで試せる場合がある一方、次の問題がある。

- JSON APIがInstance側設定で無効な場合がある。
- Rate Limit、停止、設定変更および検索品質をProject側で保証できない。
- 運営主体がQuery、IP、User-Agentその他のMetadataを観測・保存する可能性を排除できない。
- InstanceごとのTerms、Privacy、Engine構成および結果差を追跡しづらい。
- 公開OSS／Demoへ特定のPublic InstanceをHard-codeすると、その運営者と利用者の双方へ予期しない負荷とPrivacy Riskを移す。

User入力によるBring Your Own Provider Endpointも、一般利用者が信頼できないEndpointを設定し、Query／Conversation Context／PIIを送信する危険がある。FrontendへTokenを置く設計、暗黙Fallbackまたは「Endpointを選べば安全」というUIは不可である。

結論：公開製品／Demoの既定Providerにはしない。将来導入する場合も`none`既定、Deployment Operator管理、Server-side Secret、Allowlist／Trust Metadata、明示Consent、No Silent Fallbackが必要。

### 5.4 MediaWiki／Wikipedia等のDomain限定API

Credential-freeで比較的扱いやすいが、一般Web検索ではない。百科事典領域の検索やFixture／限定Providerとして有用でも、「今日の公式発表」「任意Site」「一般Web Evidence」を満たさない。

結論：限定Provider候補。General Web Search完成の代替とは主張しない。

### 5.5 その他のHosted Search API

Tavily、Exa、SerpAPIその他のHosted APIは、Account、API Key、課金、Query送信、Data利用条件およびProvider Lock-inを伴う。OpenAI等のWeb Search Toolも、外部API Account、Cost、Model／Tool Contractへ依存する。

結論：Adapter候補として将来比較する。Phase 7でAccount作成やProvider決定をしない。

### 5.6 Search Engine HTML Scraping／Browser Automation

Accountなしで動く場合があるが、HTML変更、Bot対策、CAPTCHA、Rate Limit、Terms、地域差およびParser破損に弱い。PoCの一時実験には使えても、公開Runtimeの安定した正本にしづらい。

結論：Production既定方式にしない。

### 5.7 Specialized API／RSS／自前Crawler

RSSや個別公式APIは安全性とAuthorityを限定しやすいが、対象範囲も限定される。自前Crawler／Indexは取得Policy、Robots、Storage、更新、重複除去、検索品質、削除対応および運用基盤が必要で、Phase級の別Systemになる。

結論：Domain限定Sourceは将来のProvider候補。自前General Web Indexは現在対象外。

## 6. 方式比較から得た結論

次をすべて同時に満たす一般Web検索方式は確認できなかった。

```text
無料
Account不要
Credential不要
Server不要
安定
Privacy責任が軽い
General Web
公開OSS／Demoの既定値として安全
```

「API Tokenは後で何とかする」だけでは足りない。Provider Accountには、課金、Rate Limit、Credential Rotation、漏洩時対応、Query Privacy、利用条件変更、Result保存権、Account停止および公開利用者のQuota分離が付随する。

一方、Accountを避けてPublic InstanceやScrapingへ寄せると、安定性、Privacy、Terms、品質および運営主体への依存が増える。問題はToken一個ではなく、External Knowledge Runtime全体の運用契約である。

## 7. URLを貼り付ける方式の実態

URL文字列をPromptへ入れても、Local Model自身はURLを開けない。BackendのFetch Adapter、Network Authorityおよび取得ContentのContext Injectionが必要である。

Direct URL FetchはSearch Provider Accountを不要にできるが、安全性が自動的に高くなるわけではない。

- `localhost`、Private Network、Cloud Metadata Endpoint等へのSSRF。
- Redirect Chain、DNS RebindingおよびHost検証後の接続先変化。
- 巨大Response、Compression Bomb、無限Stream、TimeoutおよびMemory／Disk枯渇。
- HTML／PDF／Archive／Media Parserの脆弱性。
- Web本文に埋め込まれたIndirect Prompt Injection。
- SEO Spam、転載Loop、AI生成汚染Data、虚偽の公式らしさ、Data Poisoning。
- Cookie、認証Header、Referer、Query String等を介したSecret／PII漏洩。
- Citationが存在することと、Sourceが正しいことを誤って同一視する問題。

Phase 7実装にはSSRF、Redirect、Size、Timeout、Content Type、Prompt Injection等の安全境界が一部ある。しかしこれは、未知・悪性・攻撃目的Siteを安全に解析できるBrowser Sandboxではない。

将来の縮小案として、Userが明示した公式／一般Public URLを、一回限り、Allowlist／Confirmation付きで取得するManual Fetchは検討できる。ただし、汚染Dataが多いSite、攻撃Site、認証領域、File Download、Archive／Media解析は、Network／Parser Isolationを持つ別Tierへ分離する。

## 8. Public OSS／Demo利用者への安全判断

User自身だけでなく、将来Repositoryを利用する第三者を考えると、次は危険である。

- Public SearXNG EndpointをProject既定値へHard-codeする。
- Userが任意Endpointを入力すれば安全に使えると案内する。
- Browser側へProvider Tokenを保存する。
- Consent OFFでもAPI直接呼出しで外部送信できる。
- FixtureまたはPort Callを「Web検索成功」と表示する。
- 検索／Fetch結果を無検証でModelへ注入する。
- General Web、公式Source、User提供Source、未知Sourceを同一Authorityとして扱う。

Public機能として成立させる場合、少なくとも次が必要である。

```text
default provider: none
default activation: disabled
external query consent: false
credential location: server side only
provider configuration: deployment operator controlled
silent fallback: forbidden
provider identity／endpoint／privacy／cost: visible
outbound query minimization: enforced
secret／PII gate: enforced
SSRF／redirect／DNS／size／timeout: enforced
source provenance／trust class: recorded
network calls／provider calls: separately observed
```

一般利用者へ公開するには、単に検索結果が返ることより、危険な既定値を持たないことを優先する。

## 9. Phase 7の最終Scope Correction

Phase 7の公開・内部Claimを次へ修正する。

```text
誤ったClaim:
  Phase 7でGeneral Web SearchとWeb-grounded Chatが完成した。

許されるClaim:
  Phase 7でLocal Corpus／Citation／Data ControlsのMVPと、
  将来のExternal Web Runtimeへ接続可能なProvider Port／Fixture／Security Scaffoldを実装した。
  実External Provider、Network CallおよびWeb-grounded Chatは未実装であり、Phase 11以降へ延期した。
```

Phase 7では次を既定にする。

- External Providerは`none`相当。
- Web Searchは`disabled／OFF`相当。
- External Network Callは0。
- FixtureはTest／Research Scaffoldであり、実Web検索と表記しない。
- Local CorpusだけをGrounded Chatの成立済み経路として扱う。
- Data Controlsは基礎であり、外部送信Consent Enforcementが成立したとは主張しない。

既存実装を即座に削除・再実装するAuthorityは本Decisionに含まない。Phase 7 Closure前には、少なくともDocs、UI Claim、Acceptance Dispositionおよび未解決Registryが上記と矛盾しないことを確認する。

## 10. Phase 11以降で再開するFull Scope

Phase 11以降の`Governed External Web Knowledge Runtime`では、最低限次を一つのProgramとして扱う。

1. Provider-neutral Search／Fetch Contractの再監査。
2. `none`、限定API、Private SearXNG、Hosted API等のProvider比較。
3. Account／Credential／Secret Vault／Rotation／Revocation。
4. Cost、Quota、Rate Limit、TimeoutおよびCircuit Breaker。
5. Server Canonical `disabled／manual／automatic`。
6. Purpose別Consent、Query最小化、Secret／PII検査。
7. Manual Evidence SelectionとOne-shot Chat Binding。
8. Automatic Search TriggerはManual Grounding成立後の別Gate。
9. URL Fetch、Redirect、DNS、SSRF、Response Size、Content Type。
10. Parser Isolation、Archive／PDF／Media Tier、Hostile-site Sandbox。
11. Prompt Injection、Data Poisoning、Spam、Duplicate、Source Authority。
12. Provenance、Canonical URL、Digest、取得時刻、Citation、Contradiction Evidence。
13. Provider Callと実Outbound Network CallのObservability分離。
14. Error／Fallbackの言語、責任主体およびUser検証可能性。
15. Public OSS／Demo向けDeployment Operator Contractと安全な既定値。
16. Real Browser、Real Provider、Privacy、FailureおよびUser Acceptance。

「検索できた」だけで完成とせず、取得Evidenceが正しく選ばれ、Model回答とCitationへ追跡可能に結びつき、外部送信とFailureがUserへ正直に表示されることをAcceptanceにする。

## 11. Reopen／Stop条件

次のいずれかが成立した時に再開する。

- Phase 11以降のExact Design開始Authority。
- UserがProvider、Account、Credential、EndpointまたはSelf-host運用を明示決定した時。
- Private／Trusted Search Backendが利用可能になった時。
- URL Fetchを限定Source Tierとして先行させる明示Authorityが出た時。

次だけでは再開しない。

- 「Web検索は便利そう」という一般的期待。
- Public Instanceが偶然応答したこと。
- Fixture TestがPASSしたこと。
- ModelがURLを知っているように回答したこと。
- Provider Accountを作れそうという推測。

## 12. Source Register

2026-08-29の方式比較で参照した主な一次資料候補を記録する。実装再開時は契約、価格、APIおよびPrivacyを再確認する。

- Brave Search API: <https://brave.com/search/api/>
- Brave Search API Privacy Policy: <https://api-dashboard.search.brave.com/privacy-policy>
- SearXNG Search API: <https://docs.searxng.org/dev/search_api.html>
- SearXNG Own Instance: <https://docs.searxng.org/own-instance.html>
- SearXNG Container Installation: <https://docs.searxng.org/admin/installation-docker.html>
- Google Custom Search JSON API Overview: <https://developers.google.com/custom-search/v1/overview>
- OWASP SSRF Prevention Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html>
- OWASP LLM Prompt Injection: <https://genai.owasp.org/llmrisk/llm01-prompt-injection/>

## 13. Action Boundary

本Decisionの記録によって、次は許可されない。

- External Network Call。
- Provider Account／Credential／Subscription作成。
- SearXNG Instance起動。
- Public Instanceへの接続。
- Production Provider Binding。
- User DataまたはQueryの外部送信。
- Phase 7 Closure、Git、BackupまたはPhase 8開始。

本書はScope／Claim／延期先の正本であり、実装Authorityではない。
