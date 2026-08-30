---
document_id: phase_11_plus_governed_external_web_knowledge_runtime_reservation_20260829222647
document_type: append_only_planned_work_scope_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-08-29 22:26:47 JST
decision_authority: user
authority_owner: Nazuna Research
target: phase_11_or_later
implementation_authorized: false
network_authorized: false
provider_contract_authorized: false
credential_authorized: false
---

# Phase 11以降 — Governed External Web Knowledge Runtime予約

## 1. Reservation

Phase 7で予定していた実General Web Search、一般URL Fetch、Web EvidenceのChat Grounding、Web Citationおよび外部送信Enforcementを、Phase 11以降へ延期する。

Phase 7は次の基礎だけを保持する。

- Local Corpus／Local RAG／Citation／Persistence。
- Data Controlsの基礎。
- Provider非依存Web Search／Fetch Port。
- Fixture Provider／Test。
- SSRF、Redirect、Size、Timeout、Content Type、Prompt InjectionおよびSecret様Query検査のScaffold。

実Provider、実Network、Web-grounded Chat、外部送信Consent、一般URL FetchおよびHostile-site処理は未実装と表示する。

## 2. Phase 11以降の必須Scope

- Provider比較：`none`、限定API、Private SearXNG、Hosted General Search API。
- Account／Credential／Cost／Quota／Privacy／Terms。
- Deployment Operator管理、Server-side Secret、安全な既定値。
- Server Canonical `disabled／manual／automatic`。
- Consent、Query最小化、Secret／PII Gate。
- Search／Fetch／Normalize／Evidence Selection／Chat Injection／Citation。
- SSRF、Redirect、DNS Rebinding、Response Bomb、Parser Isolation。
- Prompt Injection、Data Poisoning、Source Authority／Provenance。
- Provider CallとOutbound Network Callの観測分離。
- Manual Groundingを先に成立させ、Automatic Triggerは別Gateにする。
- Real Provider／Real Browser／Failure／Privacy／Public Demo Acceptance。

## 3. Provider Decision

2026-08-29時点では特定Providerを正本へ固定しない。

- Brave等のHosted APIは安定候補だが、Account／Token／Cost／Privacy運用が必要。
- Private SearXNGはAccount不要だが、Instance運用が必要。
- Public SearXNGはPrivacy、Rate Limit、Availabilityおよび運営主体の不確実性から公開Demo既定にしない。
- MediaWiki等はCredential-freeでもDomain限定であり、General Webの代替と主張しない。
- HTML Scraping／Browser Automationは脆弱で、Production既定にしない。

既定Providerは`none`、Activationは`disabled`、ConsentはOFF、External Networkは0から開始する。

## 4. Canonical Decision

詳細な経緯、方式比較、安全上の判断、Phase 7 Claim CorrectionおよびReopen条件は次を正本とする。

`docs/project/phases/phase_7/history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md`

本Reservationは実装、Network、Account、Credential、Git、Phase ClosureまたはPhase移行Authorityを与えない。
