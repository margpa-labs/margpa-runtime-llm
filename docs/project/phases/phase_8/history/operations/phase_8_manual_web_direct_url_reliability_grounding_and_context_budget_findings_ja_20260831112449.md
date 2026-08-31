# Phase 8 Manual Web — Direct URL Reliability／Grounding／Context Budget Findings

```yaml
document_id: phase_8_manual_web_direct_url_reliability_grounding_and_context_budget_findings_20260831112449
document_type: controller_finding_and_bounded_rework_scope
document_state: open
language: ja
recorded_at: 2026-08-31 11:24:49 JST
source_evidence: phase_8_user_mac_manual_acceptance_web_segment_1_evidence_ja_20260831112449.md
decision_authority: user
controller: Codex_project_controller
phase_8_closure: blocked_by_manual_url_mvp_reliability_candidate
implementation_authority: false
```

## 1. Controller結論

今回の中心問題は`url_rejected`という表示だけではない。

```text
Userが明示した普通のPublic URLを安定して取得できない
  +
取得できなかった時にModelが未取得Contentを読んだかのように回答し得る
```

これはDirect URL Readerの中心Purposeへ影響するため、単なるUI Polishではない。Phase 8の限定Manual URL MVPについては
Major／MVP Blocker候補として扱い、Userの明示的な再分類がない限り最小修正または正確なScope縮小が必要である。

## 2. Current Sourceで確認した構造

### 2.1 DNS／SSRF Preflight

`url_security.py`は接続前に`socket.getaddrinfo()`を1回実行する。例外または空結果は即
`dns_resolution_failed`へ収束する。Source自身も、検証時のResolved IPを後続ConnectionへPinせず、
実Connectionで再解決されることを明記している。

```text
Preflight DNS Resolution
  -> Public／Private Address判定
  -> httpx request
       -> Transport側で別のDNS Resolution
```

したがってCurrent実装には、少なくとも次の安定性／整合性Gapがある。

- DNS PreflightがSingle Attemptである。
- Retryable FailureとPermanent Rejectionを分離しない。
- IPv4／IPv6 Candidateごとの接続FallbackをProject Contractとして制御しない。
- Validation時AddressとConnect時Addressを結び付けない。
- Redirect Hopごとに同じSingle-shot Preflightを繰り返す。

### 2.2 HTTP Fetch

`HttpxWebFetchProvider`はRedirect、Timeout、Response SizeおよびContent Typeを有界化するが、`httpx.HTTPError`を
Generic `fetch_rejected`へ集約する。HTTP Status、TLS、Connect、Read、Protocol等の具体原因をEvidenceへ残さない。

### 2.3 Chat Evidence Projection

Conversation SSE、Completed Event、PersistenceおよびFrontendのWeb Citation表示は、失敗時に
`WebSearchAndFetchResult.failure_reason`のAggregateだけを投影する。Per-Evidenceの`rejection_reason`をLive／Persisted Chatへ
運ばないため、User画面は`url_rejected`しか復元できない。

### 2.4 Grounding Boundary

Manual URL Fetchが失敗してCitation 0でも、Main Model生成自体は継続し得る。今回、Qwenが未取得Pageに基づかない内容を
断定した。これはModel品質だけでなく、External Evidenceを明示要求したTurnのFailure ContractがFail-closedでないことを示す。

## 3. Bounded MVP修正Scope

Phase 8で必要な最小範囲は次とする。

```text
1. 普通の静的Public HTTP(S) URL
   -> 一時的な名前解決／接続失敗を恒久的なUnsafe URLと同一視しない。

2. Bounded Retry
   -> Retry回数、DeadlineおよびBackoffを固定する。
   -> User Cancel／Turn Deadlineを超えない。

3. Address Family／Connection
   -> IPv4／IPv6 Candidateを安全に分類し、到達可能なPublic Candidateへ有界Fallbackする。
   -> Private／Loopback／Link-local／MetadataへFallbackしない。

4. Exact Failure Evidence
   -> aggregate_reasonとspecific_reasonをLive SSE、Persistence、Reload／RestartおよびUIへ保持する。

5. Fail-closed Grounding
   -> Userが当該URLだけをEvidenceとして要求し、Fetchが0件の場合、未取得Pageの要約・人物説明・事実回答を生成しない。
   -> Typed Safe Failureへ収束する。
```

これはWeb Search Engine、Browser Automation、JavaScript RendererまたはHostile-site Sandboxの新設ではない。
既存Port／Provider／Evidence Contractを限定的に補正する小〜中規模Reworkである。

## 4. Phase 8へ含めない完全Hardening

次は一般Siteを高確率で読めるようにする中〜大規模Scopeであり、Phase 11以降へ維持する。

- 検証済みIPを実TCP ConnectionへPinするCustom Transport。
- DNS Rebinding耐性の完成。
- Browser／JavaScript Rendering。
- Login／Cookie／Credential Site。
- CAPTCHA、Anti-bot、WAF／403回避。
- PDF、Archive、Mediaおよび任意Binary Parser。
- 多言語／Legacy Encodingの網羅。
- Content Quality、Poisoning、ContradictionおよびSource Ranking。
- General Search ProviderおよびAutomatic Search。

## 5. Raw HTML／Context Budget

Hololive公式PageではFetch自体が成功したが、Raw WordPress HTML全体の注入により8192 Contextを超過した。
この問題への設計候補は次である。

```text
Fetch
  -> Content-Type aware Decoder
  -> HTML Normalizer
  -> script/style/nav/footer/boilerplate除去
  -> Readable Text／Metadata抽出
  -> Chunking
  -> Relevance Selection
  -> Evidence Token Budget
  -> Main Model Injection
```

UserはこのEvidenceを保留設計として記録し、今回直ちに大規模Web Ingestion Pipelineへ拡張しないことを選択した。
Phase 8のBounded Fixで簡易本文抽出／Hard Capを同時に行うか、Typed `content_budget_exceeded`で安全に失敗させるかは
Rework設計時に決める。General Web品質はPhase 11以降で扱う。

## 6. Acceptance再確認

最低Regression Scenario：

1. `example.org`成功、Citation／Digest／Restart保持。
2. Loopback拒否、Network 0。
3. Public static URLでTransient Failureを注入し、Bounded Retry後に成功。
4. Permanent DNS Failureは具体理由付きで終了。
5. TLS／Timeout／Content-Type／Response Too Largeを別Reasonで表示。
6. Fetch 0のEvidence-only TurnではModelを呼ばない、またはGrounded Factを生成せずTyped Safe Failure。
7. Large Raw HTMLはContext超過でChat全体を不透明にFailさせず、Budgeted Evidenceまたは明示Failureへ収束。
8. Live、Reload、Server Restartで同じFailure Reason／Citationを保持。

## 7. Controller自身の診断Failure

ControllerはNetwork制限されたCodex実行環境のDNS失敗を、User RuntimeのExact原因と誤って断定した。
これはEnvironment BoundaryとEvidence Strengthを分離しなかった診断Failureである。

今後、Controller-side restricted environmentのNetwork Failureは次のように扱う。

```text
Reproduction in restricted controller environment
  !=
Exact reproduction in user runtime
```

User RuntimeのSpecific ReasonがProject Evidenceへ保存されていない場合は、推測で確定せず`unobservable_due_to_projection_gap`とする。

## 8. Stop Line

```text
Phase 8 Manual URL MVP:
  ordinary_public_URL_stable_fetch        = required_bounded
  fetch_failure_exact_reason              = required
  evidence_only_turn_fail_closed          = required

Phase 11 Plus:
  general_web_reliability                 = deferred
  full_extraction_and_ranking             = deferred
  anti_bot_browser_hostile_site_hardening = deferred
```

本書はFindingと最小Rework Scopeであり、実装、Network、Git、ClosureまたはPhase移行Authorityを与えない。
