# Lightning Manual Environment／Preflight Evidence

```yaml
document_id: lightning_manual_environment_and_preflight_evidence
phase: phase_1_ex
status: partial_acceptance_test_follow_up_required
language: ja
created_at: 2026-07-26 23:39:10 JST
owner: 設計統括者役
executor: user
environment: lightning_ai_studio
runtime_target: lightning-cpu-native
credential_values_recorded: false
git_operation_performed: false
```

## 1. 目的

Phase 1-ex Lightning Basic Preview LifecycleのRepository Acceptance後、ユーザーがLightning AI Studio上で実施したFile配置、Managed Secrets、Environment、Permission、Hash、Unit Test、Read-only PreflightおよびBasic Preview Preflightの結果をAppend-only Evidenceとして保存する。

本Evidenceは、Basic Preview Web Processの起動、再起動、停止、External URL、Sleep／WakeまたはAuto-startをAcceptedとするものではない。

## 2. Environment

```text
Workspace Root:
  /teamspace/studios/this_studio

Project Root:
  /teamspace/studios/this_studio/margpa-runtime-llm

Model Root:
  /teamspace/studios/this_studio/models

uv:
  /teamspace/studios/this_studio/.runtime-tools/uv/0.11.29/bin/uv

Environment Prefix:
  /teamspace/studios/this_studio/margpa-runtime-llm/.venv

Python:
  3.12.11

Profile:
  config/profiles/lightning_linux_x86_64_cpu_native.toml

Runtime State:
  /teamspace/studios/this_studio/.runtime-state/margpa-runtime-llm/basic-preview

Host／Port:
  0.0.0.0:8000
```

## 3. 配置File

Lightning側へ次を同一相対Pathで配置した。

```text
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/auto_start_preflight.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
```

SHA-512：

```text
1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58  scripts/runtime/lightning/basic_preview_common.sh
7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac  scripts/runtime/lightning/basic_preview_service.sh
bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d  scripts/runtime/lightning/auto_start_preflight.sh
fb78b50f90db29571853f1696fe3a4e0311a8671b9f2765b3c53e5c4234e5e20f53fe6b5ca24f188638096e049b6cea4f6b35342040dd7618cd8370754aefdf0  tests/unit/runtime/test_lightning_basic_preview_service.py
```

結果：

```text
File Placement:
  PASS

PLACEMENT_CHECK_EXIT:
  0

SHA-512:
  PASS／4 files
```

## 4. Permission

実施内容：

```bash
chmod 644 scripts/runtime/lightning/basic_preview_common.sh
chmod 755 scripts/runtime/lightning/basic_preview_service.sh
chmod 755 scripts/runtime/lightning/auto_start_preflight.sh
chmod 644 tests/unit/runtime/test_lightning_basic_preview_service.py
```

Permission設定はManaged Secrets再設定後にも再実行した。

## 5. Managed Secrets

### 5.1 Current Lightning UI

Lightningの現行UIでは`New secret` Dialogに次のTabが表示された。

```text
Secret
Credential
```

本Projectが使用するのは`Secret` Tabである。

`Credential` TabはDocker Registry等の認証情報向けであり、本Projectの環境変数注入には使用しない。

### 5.2 Secret Name

`Secret` Tabで次の2件を別々に登録した。

```text
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

Username／Passwordの実値は、本Evidence、Docs、Code、Config、Screenshot、LogまたはGitへ記録しない。

`MARGPA_WEB_AUTH_MODE`はSecretではなく、Terminalで次を設定する。

```bash
export MARGPA_WEB_AUTH_MODE=basic
```

### 5.3 Injection Result

最初の確認ではUsername／PasswordがEnvironmentへ注入されず、両方`1`だった。

```text
USERNAME_AVAILABLE=1
PASSWORD_AVAILABLE=1
```

`Secret` Tabで正しいName／Value Pairを作成し、新しいTerminalを開いた後は次となった。

```text
USERNAME_AVAILABLE=0
PASSWORD_AVAILABLE=0
AUTH_MODE_EXIT=0
```

Environment Variable Name確認：

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_PASSWORD
MARGPA_WEB_AUTH_USERNAME
```

Secret値は表示していない。

## 6. Terminal Environment

新しいTerminalで次を設定した。

```bash
export MARGPA_WORKSPACE_ROOT=/teamspace/studios/this_studio
export MARGPA_PROJECT_ROOT="$MARGPA_WORKSPACE_ROOT/margpa-runtime-llm"
export MARGPA_MODEL_ROOT="$MARGPA_WORKSPACE_ROOT/models"
export MARGPA_UV_BIN="$MARGPA_WORKSPACE_ROOT/.runtime-tools/uv/0.11.29/bin"
export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
export MARGPA_WEB_HOST=0.0.0.0
export MARGPA_WEB_PORT=8000
export MARGPA_WEB_PROFILE="$MARGPA_PROJECT_ROOT/config/profiles/lightning_linux_x86_64_cpu_native.toml"
export MARGPA_RUNTIME_STATE_ROOT="$MARGPA_WORKSPACE_ROOT/.runtime-state/margpa-runtime-llm/basic-preview"
export MARGPA_WEB_AUTH_MODE=basic
export PATH="$MARGPA_UV_BIN:$PATH"

cd "$MARGPA_PROJECT_ROOT"
```

## 7. Unit Test

実行：

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py
```

結果：

```text
28 passed
2 failed
```

失敗Test：

```text
test_identity_failure_cleans_the_spawned_alive_child
test_identity_cleanup_failure_retains_evidence_for_forced_recovery
```

双方で期待値`returncode == 1`に対し、実値は`0`だった。

### 7.1 Cause Assessment

LinuxではProduction処理が`/proc/<pid>/cmdline`を優先してProcess Identityを確認する。

現行Test Fixtureの`MARGPA_TEST_IDENTITY=invalid`はFake Process Registry／Fake `ps`のIdentityだけを変更する。一方、Lightning Linuxでは実`/proc`に正しいFixture Script PathとArgumentが見えるため、Production処理はIdentityをValidと判定する。

したがって、現時点のEvidenceは次を示す。

```text
Production Linux /proc Observation:
  OPERATING_AS_DESIGNED

Linux Test Fixture Identity Failure Injection:
  INEFFECTIVE

Runtime Defect:
  NOT_ESTABLISHED

Test-only Cross-platform Follow-up:
  REQUIRED
```

## 8. Port／Existing Process

Port `8000`の既存Listener確認では出力がなく、旧Web Processは検出されなかった。

```text
Port 8000:
  FREE
```

## 9. Read-only Auto-start Preflight

実行：

```bash
bash scripts/runtime/lightning/auto_start_preflight.sh
```

自動確認結果：

```text
Host Platform:
  PASS／linux_x86_64_container

Distribution:
  PASS／ubuntu

Project Root:
  PASS

Model Root:
  PASS

Environment Prefix:
  PASS

Python:
  PASS／3.12.11

uv:
  PASS／0.11.29

margpa-web:
  PASS

Pure CPU Profile:
  PASS

Model Artifact:
  PASS

Health Contract:
  PASS

Web Bind:
  PASS／0.0.0.0:8000

Access Boundary:
  PASS／basic_preview／public_demo=false

Credential Launch Contract:
  PASS／environment_only

Runtime State Root:
  PASS

Health Client:
  PASS／curl
```

Lightning Platform側の次の項目は、設計どおり`manual_required`または`not_run`であり、Pass扱いしていない。

```text
platform_validation
api_builder_availability
traffic_aware_auto_start
machine_and_credit
public_url_issuance
sleeping_studio_wake_up
startup_command_execution
model_load_and_artifact_hash
healthz_reachability
cold_start_time
idle_sleep_and_wake
restart_url_persistence
log_secret_and_path_exposure
```

## 10. Basic Preview Preflight

Managed Secrets修正前：

```text
check.credentials=fail reason=username_required
```

Managed Secrets修正後：

```text
check.credentials=pass source=environment values=redacted
```

Credential値は出力されなかった。

## 11. Not Run

Test SuiteがGreenになるまで、次は実行していない。

```text
basic_preview_service.sh start
basic_preview_service.sh restart
basic_preview_service.sh stop
Background Web Process
Model Load
Local /healthz
Port Viewer
External Basic Authentication
Public URL
Sleep／Wake
Auto-start Go／No-Go
Anonymous Public Demo
RAG
Git
```

## 12. Current Acceptance State

```text
File／Environment／Managed Secrets:
  PASS

Read-only Auto-start Preflight:
  PASS_REPOSITORY_AND_LIGHTNING_ENVIRONMENT

Basic Preview Preflight:
  PASS

Lightning Lifecycle Unit Test:
  FOLLOW_UP_REQUIRED／28_PASS_2_FAIL

Web Lifecycle Manual Acceptance:
  NOT_RUN

External Acceptance:
  PARTIAL
```

## 13. Next Gate

1. LinuxでIdentity Failureを再現できるTest Fixtureへ修正する。
2. Productionの`/proc`優先Identity確認を弱化しない。
3. LightningでLifecycle Test `30 passed`を確認する。
4. その後に限り`start／status／healthz／restart／stop`へ進む。

実装指示は[Linux `/proc` Test Fixture Follow-up Handoff](../handoffs/implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md)を正本とする。

