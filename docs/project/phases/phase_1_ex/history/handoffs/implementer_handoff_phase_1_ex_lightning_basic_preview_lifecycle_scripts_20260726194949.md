# 実装担当向け Phase 1-ex Lightning Basic Preview Lifecycle Scripts Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_basic_preview_lifecycle_scripts
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-26 19:49:49 JST
owner: 設計統括者役
target_role: 実装者役
supersedes: null
```

## 1. Objective

Lightning Basic認証Previewの起動前確認、起動、停止、再起動および状態確認を、秘密値をRepositoryへ保存せず、少数の安全なScript操作へ統合する。

Lightning側へのFile配置、Managed Secrets設定、API Builder／Port Viewer／`on_start.sh`設定および実行はユーザーが行う。実装担当はRepository内のScriptとTestだけを作る。

## 2. Authoritative References

- [ADR-0026](../../adr/adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets_ja.md)
- [ADR-0025](../../adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [Auto-start Read-only Preflight Handoff](implementer_handoff_phase_1_ex_lightning_auto_start_read_only_preflight_20260726192912.md)
- [Public Demo／Auto-start要件](../../requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](../../architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Phase 1-ex Index](../../phase_index_ja.md)

## 3. Authorized Deliverables

推奨する主入口：

```text
scripts/runtime/lightning/basic_preview_service.sh
```

最低限、次の操作を提供する。

```text
preflight
run
start
stop
status
restart
--help
```

必要であれば責務別の内部Scriptへ分割してよい。ただし、利用者が覚える主入口は一つにする。

### 3.1 `preflight`

- Project Root、Model Root、`.venv`、`uv`、`margpa-web`、ProfileおよびModel Artifactを確認する。
- `MARGPA_WEB_AUTH_MODE`、`MARGPA_WEB_AUTH_USERNAME`、`MARGPA_WEB_AUTH_PASSWORD`の存在だけを確認する。
- Credential値を表示しない。
- File、Environment、Dependency、ProcessまたはPlatform状態を変更しない。

### 3.2 `run`

- Foregroundで`margpa-web`を実行する。
- Host、Port、Profile、Model Rootを明示する。
- CredentialをArgumentへ渡さず、Environmentから子Processへ継承する。
- API Builder／`on_start.sh`／手動Terminalで共通利用できる。

### 3.3 `start`

- Manual Background起動を行う。
- 二重起動を拒否する。
- PID／Log／StateをConfigurable Runtime State Directoryへ置く。
- PID／LogへCredentialを保存しない。
- 起動後にBounded Health Checkを行い、失敗時は安全に終了状態を報告する。

### 3.4 `stop`

- PID FileのProcessが本ProjectのWeb Processであることを確認する。
- Graceful停止を行う。
- 無関係なProcessを停止しない。
- Stale PIDを安全に処理する。
- 強制終了が必要な場合は既定動作にせず、明示Optionとする。

### 3.5 `status`

- Running／Stopped／Stale／Unhealthyを区別する。
- PID、Healthおよび安全な非秘密情報だけを表示する。
- Credential、Private URLまたは内部Tokenを表示しない。

### 3.6 `restart`

- `stop`と`start`の安全規則を再利用する。
- Lightning Secrets変更後、新しいCredentialを読み込むために使用できる。

## 4. Configuration Contract

Scriptは次を環境変数または明示Optionから解決する。

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
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

Lightning固有Defaultを持つ場合も上書き可能にする。MacまたはApplication CoreへLightning Pathを混入させない。

PasswordとUsernameの実値をScript、Test Fixture、Docs、LogまたはStatusへ記載しない。

## 5. Write Authority

実装担当が書き込める場所：

```text
scripts/
tests/
docs/project/phases/phase_1_ex/history/handoffs/
```

`src/`変更は、Shell Scriptだけでは安全に実現できない場合に限定し、Statusへ理由を記録する。

`config/`、`pyproject.toml`、`uv.lock`、Current Canonical、Public Docs、Requirements、Architecture、ADRおよびShared Policyは変更しない。

## 6. Explicitly Prohibited

- Lightning StudioへのFile Upload
- Managed Secretsの作成、変更または削除
- Username／Passwordの決定
- `.lightning_studio/on_start.sh`の作成または変更
- API Builder／Public App／Port Viewer設定
- Public URL発行または匿名公開
- SecretをScript、Config、`.env`、Log、StatusまたはTestへ埋め込むこと
- Secret値の標準出力、Debug出力またはCommand Argument化
- Package Install／Build／Dependency変更
- Model、`.venv`またはRepositoryのUpload
- Public Demo、RAG、Tool、AgentまたはGit操作

## 7. Tests

最低限次を自動Testする。

- `--help`と各SubcommandのArgument処理
- `preflight`のRead-only性
- Credential不足時のFail Closed
- Credential値がOutput／Logへ出ないこと
- 二重起動拒否
- Stale PID処理
- 無関係Processを停止しないこと
- Graceful Stop
- Health成功／失敗／Timeout
- Path Override
- Spaceを含むPathの安全な処理
- Shell Syntax
- Existing Phase 1 TestへのRegressionがないこと

Model本体を必要とするTestはMarkerで分離し、通常Unit Testで不必要にModelをLoadしない。

## 8. Status

完了後、次へ新Timestampで作成する。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_basic_preview_lifecycle_scripts_YYYYMMDDHHMMSS.md
```

Statusへ記載するもの：

- 変更File
- Subcommand一覧
- Default／Override一覧
- Test Command／Result
- Secret非露出確認
- 未実行のLightning Manual項目
- Known Limitation
- ユーザーがLightning側で行う残作業

## 9. Acceptance Conditions

1. 主入口一つでPreflight、Foreground Run、Start、Stop、StatusおよびRestartを実行できる。
2. Credential値がRepository、Argument、LogまたはStatusへ保存・表示されない。
3. Username／PasswordをLightning Secrets側で変更し、Process再起動だけで反映できる。
4. Scriptが外部Platform設定を変更しない。
5. Stopが無関係ProcessへSignalを送らない。
6. Failure時に安全な非0終了と原因を返す。
7. Unit Testと関連既存Testが合格する。
8. 実装者Statusが新Docs構造へ作成される。

## 10. Execution／Review Gate

Repository側Script実装は着手可能である。

Lightning側への配置、Secret設定、Hook設定および実行はユーザーが行うため、実装担当は実施しない。

実装者Status作成後、設計統括者役のReview Acceptedを得るまで、Auto-start Go／No-Go、Public Demo、匿名Access、RAGまたはGitへ進まない。
