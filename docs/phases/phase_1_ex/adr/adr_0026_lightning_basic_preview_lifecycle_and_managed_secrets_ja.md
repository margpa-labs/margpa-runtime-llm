# ADR-0026: Lightning Basic Preview Lifecycle／Managed Secrets

```yaml
document_id: adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets
status: accepted
language: ja
created_at: 2026-07-26 19:49:49 JST
updated_at: 2026-07-26 19:49:49 JST
owner: 設計統括者役
phase: phase_1_ex
```

## 1. Context

Lightning Pure CPU上でBasic認証Previewを起動する際、Workspace、Project、Model、`uv`、`.venv`、認証、Profile、HostおよびPortをTerminalで毎回個別設定している。

また、Basic認証のUsername／Passwordを固定しつつ、Repository、Config、Docs、Screenshot、Shell ScriptまたはGitへ秘密値を保存しない必要がある。

## 2. Decision

Basic認証の固定CredentialはLightning Managed Secretsから環境変数として受け取る。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

Username／Passwordはどちらも後から変更可能とする。Secret値の変更後、Web Processを再起動した時点で新しいCredentialを読み込む。

RepositoryにはCredential値を保存しない。Secret名、必要な環境変数名および設定手順だけを管理する。

## 3. Responsibility Boundary

### 3.1 Repository

Repository内には、Lightning Basic Previewを起動、停止、状態確認および事前検査するLifecycle Scriptを置く。

推奨配置：

```text
scripts/runtime/lightning/
└─ basic_preview_service.sh
```

Subcommand候補：

```text
preflight
run
start
stop
status
restart
```

`run`はForeground実行とし、Lightning API Builder、`on_start.sh`または手動Terminalから呼べるようにする。

`start／stop／status`は手動Background運用を補助する。PID、Logおよび一時状態はRepository Source Tree外または明示的に除外されたRuntime State Directoryへ置き、Credentialを保存しない。

### 3.2 User／Lightning Platform

次はユーザーがLightning側で行う。

- Managed Secretsの作成、変更、削除
- Username／Passwordの決定
- API Builder／Public App／Port Viewer設定
- `~/.lightning_studio/on_start.sh`の設置または変更
- Public URLの確認
- Studioの起動、停止およびSleep
- Repository／Modelの配置

実装担当はLightning外部状態を変更しない。

## 4. Secret Storage

Passwordを次へ保存しない。

- Repository
- Tracked Config
- `.env`の公開対象
- `.studiorc`
- `on_start.sh`
- Shell Script
- Command Line Argument
- PID File
- Log
- Status／Review／Handoff
- Screenshot

RuntimeではLightning Managed Secretsから環境変数へ注入され、現行Web ApplicationがProcess起動時に読み込む。

Managed SecretsのScopeがUser全StudioまたはTeamspace全Studioへ及ぶ場合があるため、専用のSecret名を使用し、不要なStudioへ秘密値を転用しない。

## 5. Non-secret Configuration

次はScript引数または環境変数で指定可能とする。

```text
MARGPA_WORKSPACE_ROOT
MARGPA_PROJECT_ROOT
MARGPA_MODEL_ROOT
MARGPA_UV_BIN
MARGPA_ENV_PREFIX
MARGPA_WEB_HOST
MARGPA_WEB_PORT
MARGPA_WEB_PROFILE
MARGPA_RUNTIME_STATE_ROOT
```

Lightning固有Scriptでは`/teamspace/studios/this_studio`を明示的なPlatform Default候補にできるが、上書き可能とし、Application CoreへHard-codeしない。

## 6. Lifecycle Safety

- Credentialが不足している場合はModel Load前にFail Closedする。
- Credential値を標準出力、標準エラーまたはLogへ出さない。
- CredentialをCommand Line Argumentへ渡さない。
- `status`はSecret値を表示しない。
- `stop`はPID Fileだけを信用せず、対象Processが本ProjectのWeb Processであることを確認する。
- Stale PIDを安全に検出する。
- `stop`はGraceful Signalを優先する。
- `/healthz`は最小情報だけを返し、Credential不要の現行契約を維持する。
- Public HTTPS URLを使用し、平文HTTPを外部共有しない。

## 7. URL

Lightning Public URLはPlatform側のPropertyとして扱い、Credential Storeへ入れない。

URLの固定性、Studio Restart後の維持およびTraffic-aware Wake-upはAuto-start Preflightで確認する。確認前にRepositoryへ固定URLを埋め込まない。

## 8. Execution Order

```text
Repository Lifecycle Script実装
  → Local Test／Review
  → Auto-start Read-only Preflight
  → ユーザーがLightning Managed Secretsを設定
  → ユーザーがLifecycle Script／Hookを配置・指定
  → Basic Preview Manual Acceptance
  → Auto-start Go／No-Go
```

Repository側Scriptは先に実装してよいが、Lightning Platformへの配置、Secret設定および実行はユーザーが行う。

## 9. Out of Scope

- Anonymous Public Demo
- Public Rate Limit／Budget
- Per-user Account
- Password Reset UI
- Secret Rotation Automation
- Secret Manager Adapterの追加
- Tool／RAG／Agent
- Git操作

## 10. Consequences

### Positive

- 毎回の長いTerminal操作を短縮できる。
- Username／Passwordを固定しながらRepositoryから秘密値を分離できる。
- Credential変更にCode変更を必要としない。
- Manual Terminal、API Builderおよび`on_start.sh`から同じ起動経路を利用できる。

### Limitation

- Basic認証は共有Credentialであり、個別Userの識別や監査には使えない。
- Credential変更後はWeb Process再起動が必要である。
- Managed Secretsの利用可能ScopeはLightningのUser／Teamspace設定に依存する。
- URLの永続性はPlatform Preflight完了まで未確認である。
