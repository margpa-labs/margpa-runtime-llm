# Phase 8 Copilot P8-0／P8-A Resource-bounded Execution Plan

```yaml
document_id: phase_8_copilot_p8_0_p8_a_resource_bounded_execution_plan_20260830195125
document_type: provider_specific_differential_execution_plan
document_state: frozen_ready
language: ja
created_at: 2026-08-30 19:51:25 JST
provider: GitHub Copilot app
role: 設計者兼実装者役
user_reported_weekly_availability: 7_percent_remaining
reserve_floor: none_user_intends_to_use_remaining_copilot_budget
```

## 1. 目的

Copilotの残り7%をPhase 8全体へ拡散せず、Phase 8先頭のManual URL Evidenceへ集中する。Resource停止またはSession停止時に、Claudeが会話ContextなしでExact差分再開できるRecoveryを最優先する。

## 2. Execution Boundary

```text
Authorized Packages : P8-0、P8-A
Forbidden Next       : P8-B以降
Start                : P8-0-WU-001
Normal End           : P8-A-WU-006 Return
Resource End         : Current WUを安全収束しStopped-safe Return
```

## 3. Work Unit／Recovery Boundary

### CP8-01 — P8-0-WU-001 As-built Map

- Phase 7 Web Knowledge、Citation、Persistence、UI、BootstrapのProduction WiringをSourceから確定。
- 再利用対象と変更禁止Baselineを列挙。
- Recovery Index 1を作成。

### CP8-02 — P8-0-WU-002 Adjacent Boundary

- Local RAG、Citation、Conversation、Data Controlsとの接続点を確定。
- Branch／Archive、Constitution、Agent Scopeへ越境しないことを固定。
- Recovery Index 2を作成。

### CP8-03 — P8-0-WU-003 Authority／Test Freeze

- Network、Git、Root、Temp、User Data、Node環境およびTest Matrixを固定。
- Source Mutation前のEntry Inventoryを記録。
- Recovery Index 3を作成。

### CP8-04 — P8-A-WU-001／002 Direct URL Contract／Security

- Direct URL Request／Status／Evidence／Failure Contract。
- OFF時Network Call 0。
- Public `http／https`、Credential、Loopback、Private、Link-local、Metadata、危険Port／Scheme拒否。
- Redirect再検証契約。
- Focused Test後にRecovery Index 4を作成。

### CP8-05 — P8-A-WU-003 Bounded Direct Fetch

- 既存`WebFetchProviderPort`／`HttpxWebFetchProvider`を再利用。
- Timeout、Size、Redirect、Content Type、UTF-8 Text Normalization。
- JavaScript、Cookie、Login、Form、File／Archive／Media解析0。
- Mock Transport Test後にRecovery Index 5を作成。

### CP8-06 — P8-A-WU-004 Main Model Evidence Wiring

- Userの明示操作で取得したContentだけをUntrusted EvidenceとしてCurrent Turnへ渡す。
- Search Result Snippet、Past Turn、取得前URL、Fetch失敗をEvidence本文と混同しない。
- OFF／Failure時はMain Model注入0。
- Integration Test後にRecovery Index 6を作成。

### CP8-07 — P8-A-WU-005 Citation／Persistence

- Canonical URL、Fetched At、Content Type、Digest、Source ClassをCitationへ投影。
- Live SSE／Persistent Detail／Reload相当で同一Identityを保持。
- Historical Turnを書き換えず、Current Resultと分離。
- Integration Test後にRecovery Index 7を作成。

### CP8-08 — P8-A-WU-006 Toggle／UI／Failure

- 設定のWeb取得OFF／ON、Manual URL入力、取得Content、Untrusted Label、Failure Reason。
- OFF既定、取得成功と信頼済みを同一表示しない。
- Real Network成功をFixtureでClaimしない。
- Frontend Focused Test後にRecovery Index 8を作成。

### CP8-09 — Bounded Integration／Review／Return

- P8-ACC-001〜012、039のうち変更範囲を個別Disposition。
- Internal Review Cycle 1。Resourceが残り、Critical／Major／MVP BlockerがAuthority内で直せる場合だけBounded Rework。
- Canonical Full SuiteはResourceが足りる場合だけ実行し、不足時は成立済みFocused Evidenceを保持してClaudeへ渡す。
- Final Recovery、Copilot Automation Evidence、Exact Return Handoffを作成。
- P8-Bへ進まない。

## 4. Recovery Minimum

各Recoveryは短くても次を欠かさない。

```text
Completed CP／P8 Work Unit
Changed Paths
Focused Test結果
成立したAcceptance／未成立Acceptance
Open Finding／Incident
Root／Git／Network／Provider Memory／User Data Action Inventory
Active Process／Temporary Artifact
Resource／Compaction／Session Signal
Do Not Repeat
Exact Next CP／Work Unit
```

## 5. Resource Stop

Copilot利用可能量、SessionまたはPlatform上限が接近した場合、新しいWUへ入らない。現在のCommandを収束し、未確定Claimを`PARTIAL`へ戻し、最新RecoveryとStopped-safe Returnを作る。Platformによる自動再開を前提にしない。

残7%を使い切る方針は、途中File、実行中Processまたは虚偽PASSを残す許可ではない。
