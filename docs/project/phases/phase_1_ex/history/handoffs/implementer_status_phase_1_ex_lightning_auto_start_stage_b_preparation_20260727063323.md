# Phase 1-ex Lightning Auto-start Stage B Preparation 実装Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation
phase: phase_1_ex
status: repository_preparation_complete_review_pending
language: ja
created_at: 2026-07-27 06:33:23 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md
supersedes: null
```

## 1. Result

Lightning API Builderを候補経路とするStage B Unattended External Wake Trialについて、Repository側Preparationを完了した。

採用Entrypoint：

```bash
bash scripts/runtime/lightning/basic_preview_service.sh run
```

既存`run`が必要なForeground Process Contractを満たすため、Thin Entrypointは追加しなかった。

Lightning UI、Plugin、API Builder、Startup Command、Port、Health、Managed Secrets、Public URLおよびStudio状態は変更していない。Stage B実試験も実施していない。

## 2. Scope

実施：

- Existing `run` Compatibility Assessment
- API Builder相当の外部Working DirectoryからのForeground起動Test
- Platform指定Portの`MARGPA_WEB_PORT`経由伝達Test
- Default Runtime State非生成Test
- Foreground Process Identity／TERM Signal Test
- Command Template
- User Manual Stage B手順
- Evidence Template
- Rollback
- Stop Conditions

未実施：

- Lightning UI操作
- Plugin Install／Remove
- API Builder作成
- Public URL発行
- Studio Sleep／Wake
- Managed Secrets変更
- Dependency Install／Build
- Model Download／変更
- `src/`、`config/`、`pyproject.toml`または`uv.lock`変更
- Git操作

## 3. Existing `run` Compatibility Assessment

| Contract | Assessment | Evidence／扱い |
|---|---|---|
| Foreground Process | PASS | `run_foreground`が最後に`exec "${margpa_web_bin}"`する。Background化しない。 |
| Platform Signal | PASS | Shell Processを`margpa-web`へ置換し、Process IDを維持する。TERM実Test合格。 |
| Project Root | PASS | `MARGPA_PROJECT_ROOT`を優先し、未指定時はScript配置から解決する。 |
| External Working Directory | PASS | Scriptを解決可能なPathで呼び、Root環境変数を設定すればProject外から起動可能。Unit Test合格。 |
| Workspace Root | PASS | `MARGPA_WORKSPACE_ROOT`を優先し、未指定時はProject Rootの親を使用する。 |
| Model Root | PASS | `MARGPA_MODEL_ROOT`を優先し、未指定時はWorkspace配下`models`を使用する。 |
| Environment Prefix | PASS | `MARGPA_ENV_PREFIX`を優先し、未指定時はProject配下`.venv`を使用する。 |
| Project-scoped `uv` | PASS | `MARGPA_UV_BIN`を優先し、未指定時はWorkspace配下`.runtime-tools/uv/0.11.29/bin`を検査する。Installは行わない。 |
| Pure CPU Profile | PASS | `MARGPA_WEB_PROFILE`を受け、CPU／No Acceleration／Fallback Denyを起動前検査する。 |
| Host | PASS | `MARGPA_WEB_HOST`を受け、既定は`0.0.0.0`。 |
| Port | PASS WITH PLATFORM CONTRACT | `MARGPA_WEB_PORT`を`margpa-web --port`へ渡す。API Builder側の公開／Application Portを同じ値にする。 |
| Basic Authentication | PASS | Mode、Username、PasswordをEnvironmentから受け、値をArgumentへ渡さない。 |
| Missing／Invalid Credential | PASS | 不足、空白、Usernameの`:`／改行、Passwordの改行をModel Load前に非0終了で拒否する。 |
| Runtime State | PASS | `run`はPID、Log、Lockを作らない。`MARGPA_RUNTIME_STATE_ROOT`未指定でもDefault Pathを検査するだけで生成しない。 |
| Health Contract | PASS | Repository側契約は`/healthz`、HTTP `200`、`{"status":"ok"}`。 |
| Install／Build／Network | PASS | Preparation CommandはInstall、BuildおよびNetwork Accessを行わない。`uv --version`とLocal File Contractだけを検査する。 |
| Existing Manual Lifecycle | PASS | 同じService Scriptの既存`start／stop／restart`回帰Testを含む対象32件が合格。 |

## 4. Entrypoint Decision

Thin Entrypointを追加しない。

理由：

1. `basic_preview_service.sh`自身がScript配置からProject Rootを解決できる。
2. Root、Model、Environment、`uv`、Profile、HostおよびPortは既存環境変数で明示できる。
3. `run`はCredentialとPure CPU Runtime前提を検査後、`exec margpa-web`する。
4. API Builder向けにModel Load、認証またはWeb Server処理を重複実装する必要がない。
5. 未確認のPlatform固有環境変数をProduction Scriptへ推測で追加せずに済む。

API Builder起動Commandに次は使用しない。

```bash
bash scripts/runtime/lightning/basic_preview_service.sh start
```

`start`はManual Terminal用Background Lifecycleであり、Platform Process Manager用の主Process Contractを満たさない。

## 5. API Builder Command Template

### 5.1 Target

```text
Organization : Nazuna-Research-Org
Teamspace    : general
Studio       : margpa-runtime-llm
Machine      : existing Free Pure CPU Studio
```

### 5.2 Working Directory／Command

API BuilderのWorking DirectoryをRepository Rootへ設定する。

```text
<STUDIO_WORKSPACE_ROOT>/margpa-runtime-llm
```

Startup Command：

```bash
bash scripts/runtime/lightning/basic_preview_service.sh run
```

Working DirectoryをRepository Rootへ設定できない場合は、次の形式でScriptを解決し、Root環境変数も明示する。

```bash
bash <PROJECT_ROOT>/scripts/runtime/lightning/basic_preview_service.sh run
```

`<PROJECT_ROOT>`等のPlaceholderはUI上の実Pathへ置換するが、Credential、Public URLまたは個人識別情報をCommandへ追加しない。

### 5.3 Non-secret Environment

API BuilderのEnvironment設定で次を指定する。標準配置と一致する場合も、UI上で解決値を確認する。

```text
MARGPA_WORKSPACE_ROOT = <STUDIO_WORKSPACE_ROOT>
MARGPA_PROJECT_ROOT   = <STUDIO_WORKSPACE_ROOT>/margpa-runtime-llm
MARGPA_MODEL_ROOT     = <STUDIO_WORKSPACE_ROOT>/models
MARGPA_UV_BIN         = <STUDIO_WORKSPACE_ROOT>/.runtime-tools/uv/0.11.29/bin
MARGPA_ENV_PREFIX     = <STUDIO_WORKSPACE_ROOT>/margpa-runtime-llm/.venv
MARGPA_WEB_HOST       = 0.0.0.0
MARGPA_WEB_PORT       = 8000
MARGPA_WEB_PROFILE    = config/profiles/lightning_linux_x86_64_cpu_native.toml
MARGPA_WEB_AUTH_MODE  = basic
```

通常運用では次を設定しない。

```text
MARGPA_RUNTIME_STATE_ROOT
```

### 5.4 Managed Secrets

既存Lightning Managed SecretsからProcess Environmentへ次を継承する。

```text
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

値をStartup Command、通常Environment欄、Docs、Log、ScreenshotまたはStatusへ転記しない。

### 5.5 Port／Health

```text
Application／API Builder Port : 8000
MARGPA_WEB_PORT                : 8000
Health Path                    : /healthz
Expected Health                : HTTP 200
Expected Body                  : {"status":"ok"}
```

API Builderが任意Portを割り当てる場合は、その確定値を`MARGPA_WEB_PORT`とAPI Builder側Portの両方へ同じ値で設定する。

`PORT`等のPlatform環境変数名は未確認である。UIが`PORT`だけを提供し、Application Portまたは`MARGPA_WEB_PORT`を設定できない場合は、推測でScriptへMappingを追加せず停止する。

## 6. User Manual Stage B Procedure

本Statusが設計統括者ReviewでAcceptedされた後に限り、ユーザーがLightning上で実施する。

### 6.1 Installation／Configuration

1. Targetが`Nazuna-Research-Org／general／margpa-runtime-llm`であることを再確認する。
2. 既存Manual Basic Previewを停止する。
3. 採用Portに既存Listenerがないことを確認する。
4. API Builder PluginをInstallする。
5. APIを新規作成する。
6. Working DirectoryをRepository Rootへ設定する。
7. Section 5のNon-secret Environmentを設定する。
8. Managed Secrets二項目がProcess Environmentへ継承されることを確認する。
9. Startup CommandへForeground `run`を設定する。
10. Application Portを`MARGPA_WEB_PORT`と同じ値に設定する。
11. 設定可能ならHealth Pathを`/healthz`にする。
12. Basic Authentication Modeが`basic`であることを確認する。
13. Public URLを発行するが、URL自体をDocsまたはStatusへ記録しない。

UI Label、設定項目、Port ContractまたはSecret継承方法が想定と異なる場合は、推測で進めず停止する。

### 6.2 First Unattended Wake Trial

1. Manual Basic Preview Processが停止していることを確認する。
2. StudioをSleepさせる。
3. Owner Browser、Studio Tab、TerminalおよびSSH Sessionをすべて閉じる。
4. Owner操作なしの別Accountまたは第三者相当Private BrowserからPublic URLを開く。
5. Public URL Access開始時刻を記録する。
6. URL AccessだけでStudioがWakeし、Foreground Entrypointが起動することを確認する。
7. Login PromptまたはApplication表示までのCold Start秒数を記録する。
8. Credentialなしと誤Credentialが拒否されることを確認する。
9. 正しいCredentialでApplicationを開く。
10. `/healthz`がHTTP `200`を返すことを確認する。
11. 短いModel Generationを一回実行する。
12. `margpa-web`が単一Processであることを確認する。
13. Secret、Credential、不要な内部PathまたはStack Traceが外部Responseへ露出していないことを確認する。

OwnerがStudioを別操作でWakeする、Browser Tabを維持する、Terminalを開く、またはAccess時に手動対応した場合は合格にしない。

### 6.3 Second Unattended Wake Trial

1. Applicationを未使用状態にする。
2. Studioが再度Sleepしたことを確認する。
3. Owner Sessionを開かない。
4. 同じPublic URLを別Sessionから開く。
5. URL Accessだけで二回目のWakeが成立することを確認する。
6. 二回目のCold Start秒数を記録する。
7. 同じURLが維持されていることを確認する。
8. Basic認証、`/healthz`、単一ProcessおよびModel Generationを再確認する。
9. Trial前後のCredit表示を記録する。

## 7. Evidence Template

未実施項目をPassにしない。Credential実値、Public URL、Prompt本文、回答本文、Account IDおよび個人Pathを記録しない。

```text
checked_at_jst:
correct_target_confirmed:
api_builder_installed:
api_created:
foreground_entrypoint:
platform_port:
health_path:
studio_sleep_confirmed:
owner_sessions_closed:
third_party_url_trigger_only:
first_wake_pass:
first_cold_start_seconds:
healthz_200_after_first_wake:
basic_auth_after_first_wake:
model_generation_after_first_wake:
second_sleep_confirmed:
second_wake_pass:
second_cold_start_seconds:
same_url_preserved:
single_process_confirmed:
credit_before:
credit_after:
secret_exposure_found:
internal_path_exposure_found:
rollback_required:
notes_without_private_identifiers:
```

## 8. Rollback

Rollback操作はユーザーだけがLightning上で行う。

1. API BuilderのAPIを停止または無効化する。
2. Public URLの公開を停止する。
3. Startup Commandを削除または無効化する。
4. 必要ならAPI Builder PluginをRemoveする。
5. Foreground Processが停止したことを確認する。
6. Port Listenerが残っていないことを確認する。
7. 既存Manual Basic Previewの`start／status／restart／stop`が引き続き利用できることを確認する。
8. Managed Secretsは自動削除せず、保持または削除をユーザーが判断する。

## 9. Stop Conditions

次の場合は推測で続行せず、Platform状態をむやみに変更しない。

- Correct Targetを確認できない。
- API Builder UIがStage A Evidenceと大きく異なる。
- Foreground Commandを設定できない。
- Working DirectoryをRepository Rootまたは明示Root Contractへ固定できない。
- Managed SecretsをProcess Environmentへ継承できない。
- Basic認証を維持できない。
- API Builderが独自Framework、別ArtifactまたはBuildを必須とする。
- Port Contractを`MARGPA_WEB_PORT`へ確定できない。
- Public URL AccessだけではStudioがWakeしない。
- Owner SessionまたはManual Wakeが必要になる。
- Secret、Credential、不要な内部PathまたはStack Traceが外部へ露出する。
- 予期しない課金、Credit消費またはMachine変更が発生する。
- 複数Web Processが残る。
- Public URLが二回目のWakeで維持されない。
- Rollback方法または停止対象が不明である。

## 10. Repository Verification

```text
Shell Syntax:
  PASS

Target Runtime Test:
  32 passed

Repository Full Suite:
  299 passed
  3 model_smoke tests deselected

Ruff Check:
  PASS

Ruff Format Check:
  PASS

Mypy Strict:
  PASS
  96 source files
```

追加回帰Test：

- Project外Working DirectoryからのForeground起動
- `MARGPA_WEB_PORT`の`margpa-web`への伝達
- `MARGPA_RUNTIME_STATE_ROOT`未指定時のPID／Log／Lock非生成
- `run`がInstall、BuildまたはHealth Network Callを行わないこと
- `exec`後のProcess ID維持
- TERM SignalによるForeground Process停止
- Credential値のStdout／Stderr非露出

## 11. Files／SHA-512

変更File：

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
SHA-512:
2413cd6ca9a953d2829e676aac209e6b4781b0fe6ce3befaa0d7d934ca9cdff82cb8556ac8399c0a166c650084c9ff3443d4f64efbe76dbca080f3b6389eb88e
```

採用済みEntrypoint Evidence（内容変更なし）：

```text
scripts/runtime/lightning/basic_preview_common.sh
1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58

scripts/runtime/lightning/basic_preview_service.sh
7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac

scripts/runtime/lightning/auto_start_preflight.sh
bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d
```

本Statusは自己参照Hashを記録しない。

## 12. Unconfirmed Platform Items

次はRepositoryから確認できず、ユーザーのStage B手動操作で確認する。

- API Builder Install後の正確なUI Label
- Working Directory設定可否
- Startup Command設定可否
- Platform Portの設定方式
- `PORT`等のPlatform自動注入変数の有無
- Managed SecretsのProcess Environment継承方式
- Health Check設定可否とTimeout
- Public URL発行方式
- Public URL AccessによるSleeping Studio Wake
- Owner Session完全不在での起動
- First／Second Cold Start
- 二回目WakeでのURL維持
- Trial前後のCredit
- Platform Restart Policy
- API Builder Stop／Disable／Remove手順
- 外部ResponseのSecret／内部Path非露出

## 13. Review／Execution Gate

Repository Preparationは完了し、設計統括者Review待ちである。

Review Accepted前に、ユーザーはAPI Builder Install、設定、Public URL発行、Studio Sleep／Wakeまたは実Trialへ進まない。

Review Accepted後もLightning上の全操作はユーザーが手動実施し、実装者役はPlatform Mutationを行わない。
