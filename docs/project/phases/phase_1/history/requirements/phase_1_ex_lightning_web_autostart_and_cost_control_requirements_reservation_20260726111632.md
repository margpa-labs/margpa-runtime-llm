# Phase 1-ex Lightning Web Auto-start／Cost Control 要件予約

- 文書ID: `phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation`
- 状態: `accepted_reservation_not_implemented`
- 作成日時: `2026-07-26 11:16:32 JST`
- 更新日時: `2026-07-26 11:16:32 JST`
- Snapshot: `20260726111632`
- 作成担当: 設計者役担当Task
- 対象Phase: Phase 1-ex「運用再整備」
- Acceptance Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- 正本言語: 日本語
- supersedes: なし

## 1. 背景

Lightning Web Previewは、Pure CPU Profile、Basic認証、外部Browserおよび主要Web機能についてAcceptanceを通過した。

一方、StudioのSleep／Restartごとに次をTerminalへ手入力する運用は負担が大きい。

- Workspace／Project／Model／uv／`.venv` Path
- `PATH`
- Basic認証Mode、Username、Password
- Profile
- Host／Port
- `margpa-web`起動
- Health Check

Phase 1実装のCorrectness問題ではなく、公開Previewを継続運用するためのOperations問題としてPhase 1-exへ予約する。

## 2. Goal

利用者がPublic LinkへAccessしたとき、必要に応じてLightning環境とMARGPA Webが起動し、Idle時には安全にSleepできる構成を目指す。

```text
Traffic／Studio Wake
  → Runtime Start
  → Model Load
  → Health Ready
  → Basic Authentication
  → Web Available

Idle
  → Web／Studio Sleep
  → Compute Cost停止
  → Persistent Artifact維持
```

## 3. Two-stage Automation

### 3.1 Studio起動後の自動Web起動

LightningのStudio Launch ActionからProject-owned Launcherを呼ぶ。

候補：

```text
~/.lightning_studio/on_start.sh
  → margpa-runtime-llm/scripts/run/start_lightning_pure_cpu_web.sh
```

`on_start.sh`へ長いApplication起動手順を直接埋め込まず、Repository管理可能なLauncherへ責務を寄せる。

### 3.2 URL AccessによるTraffic-aware Auto-start

StudioがSleep中でもPublic URLへのAccessを契機に起動できるLightningのAuto-start／Hosted App機能を利用可能か確認する。

Current Port Viewerによる手動Port公開だけで、URLからStudio Wakeまで成立すると仮定しない。

実装前に次をRead-only Preflightする。

- Current Lightning PlanでAuto-startを利用できるか
- Custom Port Appで利用できるか
- Public LinkがSleep／Wake後も維持されるか
- CPU StudioをTargetに固定できるか
- Cold Start中の表示
- Health CheckとReady判定
- Auto-startとBasic認証の順序
- Credit／無料CPU枠への影響

## 4. Project-owned Launcher

候補File：

```text
scripts/run/start_lightning_pure_cpu_web.sh
```

最低責務：

- Workspace Root、Project Root、Model Root、Project-local uv、Project `.venv`を決定する。
- Pure CPU Profileを明示する。
- GPUへ黙って切り替えない。
- Model ArtifactとExecutableを確認する。
- Basic認証が有効であることを確認する。
- Secret不足時にFail Closedする。
- 同一Port／同一Processの重複起動を防止する。
- `margpa-web`を起動する。
- `/healthz`がReadyになるまでBounded Waitする。
- Startup FailureをCredentialなしのLogへ記録する。
- Stop／Restart／Stale PIDを安全に扱う。

Launcherの実装方式は、Lightning On-start Process Lifecycleを確認してから決定する。`nohup`、Background Job、PID FileまたはProcess Supervisorを根拠なく固定しない。

## 5. Persistent Configuration

### 5.1 Non-secret

次はLightning Studio EnvironmentまたはProject-owned Launcherの既定値候補とする。

```text
MARGPA_WORKSPACE_ROOT
MARGPA_PROJECT_ROOT
MARGPA_MODEL_ROOT
MARGPA_UV_BIN
MARGPA_ENV_PREFIX
MARGPA_WEB_AUTH_MODE
```

PathはCurrent Lightning Environmentに固有であるため、Application Coreへハードコードしない。

### 5.2 Secret

次はLightning Managed Secretsまたは同等のSecret Storeで管理する。

```text
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

PasswordをRepository、Config、Docs、Command Example、Screenshot、Process Argument、公開Logへ保存しない。

外部Preview利用者へ毎回Credentialを再通知しないため、Auto-start時にRandom Passwordを毎回再生成しない。安定したPreview CredentialをSecret Storeへ登録し、必要時に明示Rotateする。

## 6. Cost／Performance Policy

```text
Default Lightning Runtime : Pure CPU
GPU Runtime               : Explicit opt-in only
Silent GPU Selection      : Forbidden
Summary Mode              : User opt-in
Thinking Generation       : User opt-in
Max New Tokens            : User configurable
```

Pure CPUの遅さは利用者へ明示する。Summary Modeは通常回答後に同じModelを再度呼ぶため、Pure CPUでは特にLatencyが増える。

GPUは短時間のBenchmark、Compatibility Testまたは明示Demo時だけ選択し、終了後にCPUへ戻す。

## 7. Sleep Semantics

Lightningの通常Auto-sleepと、Traffic-aware Hosted App Auto-startを区別する。

- 通常のStudio Auto-sleepでは、実行中のAPI ServerがActive WorkとしてSleepを妨げる場合がある。
- Traffic-aware Auto-startは、User Trafficを監視し、未使用時にApp／Studioを停止する別のHosting動作である。
- Browserを閉じただけで直ちにProcess停止またはCost停止したと推測しない。
- Lightning DashboardのMachine StateとCredit Consumptionを実測する。

Manual Sleepは、Auto-start Acceptance完了までの安全なCost Control手段として維持する。

## 8. Cold Start

URL Accessから利用可能になるまで、Model LoadおよびSHA-512検証を含むCold Startが発生する。

要件：

- Cold StartはFailure表示と区別する。
- 起動中Statusを可能な範囲で表示する。
- 無期限に待たない。
- Ready前にModel Requestを受け付けない。
- Cold Start時間を計測する。
- Public Preview利用者へ数分待つ可能性を案内する。

## 9. Acceptance Conditions

### 9.1 Functional

1. StudioまたはHosted AppをSleepさせる。
2. Public Linkへ外部BrowserからAccessする。
3. Manual Terminal入力なしに起動が開始される。
4. Cold Start後にBasic認証画面が表示される。
5. 正しいCredentialでMARGPA Webを開ける。
6. `/healthz`がReadyを返す。
7. 短い日本語生成が成立する。
8. 二重Processが起動しない。
9. Idle後にPlatform定義どおりSleepする。
10. 次回Accessで再度起動できる。

### 9.2 Security

1. Credential未設定時はPublic Bindを拒否する。
2. SecretがLog、Docs、Git、Process Argumentへ出ない。
3. `/healthz`は最小情報だけを返す。
4. Public RootはBasic認証を維持する。
5. Auto-start ScriptはModel／Project以外を変更しない。

### 9.3 Cost

1. Default MachineはCPUである。
2. Auto-startがGPUへ切り替えない。
3. Sleep中のCompute StateをDashboardで確認する。
4. User Trafficがない状態で無期限実行しない。

## 10. Fallback

Current Lightning Plan、Custom Port AppまたはPublic LinkでTraffic-aware Auto-startが利用できない場合：

```text
Fallback A:
  Studioを手動Wake
  → on_start.shでWebを自動起動

Fallback B:
  Current Manual手順
  → Pure CPU Webを手動起動
  → 使用後にManual Sleep
```

Platform制約を回避するためにCredentialを外す、GPUを常時起動する、非公開APIへ依存する等の変更を行わない。

## 11. iOS／Responsive UI

iPhone／iOSは本Auto-start要件の対象外とする。

Mobile Browser対応はPhase 4または後続UI PhaseのResponsive Designとして扱う。Public Linkへ到達できることと、Mobile UX Acceptanceを同一視しない。

## 12. Authorization Boundary

本書はPhase 1-exの要件予約であり、次を自動許可しない。

- `on_start.sh`の変更
- Lightning Environment Variable／Secretの追加
- Source／Script変更
- Auto-start有効化
- Machine Type変更
- Public Link変更
- Git／GitHub操作

実装前にCurrent Lightning UI／PlanのRead-only Preflightと、実装担当向けAccepted Handoffを作成する。
