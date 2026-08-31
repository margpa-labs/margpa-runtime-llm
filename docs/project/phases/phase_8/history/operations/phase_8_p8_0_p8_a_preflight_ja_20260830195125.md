# Phase 8 P8-0／P8-A Preflight

```yaml
document_id: phase_8_p8_0_p8_a_preflight_20260830195125
document_type: bounded_implementation_preflight
document_state: final
language: ja
created_at: 2026-08-30 19:51:25 JST
phase: phase_8
scope: P8-0_and_P8-A_only
executor_candidate: GitHub Copilot app
decision: GO
```

## 1. 結論

Phase 8全体ではなく、GitHub Copilot appへ`P8-0 Entry／As-built／Authority Freeze`と`P8-A Manual URL Fetch／Evidence`だけをBounded Scopeとして渡せる。

Copilot週間利用可能量はUser報告で残り7%であるため、P8-B以降へ進めない。各Work Unit完了時に短いRecovery Indexを作り、Resource Stopが来ても成立済み境界からClaudeが差分再開できる状態を優先する。

## 2. Entry State

```text
Backup                         : USER CONFIRMED COMPLETE
Baseline Commit                : 99c7395c027f1d5e5d038b7f453f53b4b2c0cdb0
Branch                         : main
Local／origin                  : 同期済み（Phase 7 Closure時点）
Phase 7                       : COMPLETE／ACCEPTED／CLOSED
Phase 8                       : READY／NOT STARTED／NOT ARMED
Phase 8 Source Mutation        : 0
Real Network Action            : 0
Git Mutation after Phase 7     : 0
User runtime_data Action       : 0
```

Backupの内容または保存先は本PreflightでInspectionしておらず、Userの完了報告を正本とする。

## 3. Environment／Focused Baseline

```text
Python                         : 3.13.14
Node                           : v25.8.1
npm                            : 11.11.0
Backend Web Knowledge Focused  : 64 passed
Frontend WebSearchPanel        : 1 file／6 passed
Network                        : 0
Install／Download              : 0
```

Node v25.8.1では過去にFull Frontendのjsdom環境差が観測されている。ただし今回の`WebSearchPanel` Focused TestはPASSした。CopilotはNode／Packageを新規Installせず、環境起因Failureが出た場合はSource Failureと混同せずRecoveryへ記録し、独立して進められるBackend／Contract作業を継続する。

## 4. Reusable As-built

Phase 7で次が成立済みであり、再実装しない。

- `modules/web_knowledge/`のSearch／Fetch／Evidence／Citation Contract。
- `url_security.py`のPublic `http／https`、Credential、Private／Loopback／Link-local／Metadata拒否。
- Redirectごとの再検証、Timeout、Response Size、Content Typeを持つ`HttpxWebFetchProvider`。
- Prompt Injection／Secret Candidate Detector。
- Fixture Search／Fetch Providerと実HTTP Semantics用`httpx.MockTransport` Test。
- `/api/v2/web-search` Route、Frontend `WebSearchPanel`、設定FormのWeb Mode。
- Phase 7 Local RAG／Citation／Conversation Persistence／Data Controls。

## 5. Exact Missing Surface

P8-Aで新しく成立させるのは次だけである。

1. Search Queryを経由しない、User明示URL用のDirect Fetch Request／Result Contract。
2. OFF時Network Call 0と、明示操作時だけDirect FetchするComposition。
3. Fetch Contentを`Untrusted External Evidence`として画面へ表示し、明示的にMain Model Contextへ渡す経路。
4. Canonical URL、Fetched At、Content Type、SHA-512 Digest、Source Classを持つCitation。
5. Conversation Turn／Persistent DetailへWeb CitationをCurrent／Historicalの意味を壊さず保存・再投影する経路。
6. URL入力、OFF／ON、Consent、Failure ReasonおよびUntrusted表示のUI。
7. Fixture／Mock Transport、Failure、Reload／Restart相当および既存RAG Regression Test。

## 6. Boundary

### Allowed

- Project Root内のP8-0／P8-Aに必要なSource／Test／Config／Frontend／Static Artifact／Phase 8 Recovery／Return Docs。
- 既存`.venv`と既存`frontend/node_modules`を使うTest／Static／Build。
- Fixture、Mock TransportおよびNetwork Call 0の検証。

### Forbidden

- Real Network、General／Automatic Web Search、Search Provider Account、Credential、Cost、Remote MCP。
- Project Root外Read／Write／Temp／Cache／Install、Git、Provider Memory、User `runtime_data/`、Real Browser、Model Load。
- P8-B以降、Phase 8 Closure、Phase 9、Roadmap、Backup、Commit／Push。
- Phase 6／9 Semantic Governance Debt、Full Constitution、正式Agent Level 1。

## 7. Preflight Decision

```text
P8-0／P8-A Implementation Entry : GO
P8-B〜P8-F                     : NOT AUTHORIZED FOR COPILOT
Real URL Fetch Validation       : USER MANUAL GATE／NOT RUN
Maximum Copilot Claim           : P8-A BOUNDED COMPLETE CANDIDATE
```
