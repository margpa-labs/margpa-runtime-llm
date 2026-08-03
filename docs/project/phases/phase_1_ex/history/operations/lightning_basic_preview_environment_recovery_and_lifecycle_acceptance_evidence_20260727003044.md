# Lightning Basic Preview Environment Recovery／Lifecycle Acceptance Evidence

```yaml
document_id: lightning_basic_preview_environment_recovery_and_lifecycle_acceptance_evidence
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-27 00:30:44 JST
owner: 設計統括者役
executor: user
environment: lightning_ai_studio
runtime_target: lightning-cpu-native
credential_values_recorded: false
git_operation_performed: false
supersedes: null
extends:
  - lightning_manual_environment_and_preflight_evidence_20260726233910.md
```

## 1. 目的

[Lightning Manual Environment／Preflight Evidence](lightning_manual_environment_and_preflight_evidence_20260726233910.md)以後に発生した、Project `.venv`のEnvironment Variable復旧、Linux Lifecycle Test再実行、Runtime State起動失敗の原因確認、Start／Status／Health／External Authentication／Restart／Stopの手動Acceptanceまでを、一つの時系列EvidenceとしてAppend-onlyで保存する。

本EvidenceはCredential実値、Private URL、Prompt本文またはGit状態を保存しない。

## 2. 更新Test File配置後の`pytest`起動失敗

更新済みTest FileをLightningへ配置した後、次を実行した。

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py
```

結果：

```text
zsh: no such file or directory: /bin/pytest
```

### 2.1 原因

新しいTerminalでは`MARGPA_ENV_PREFIX`が未設定だった。

空のEnvironment Variableを含む次の式は、

```text
"$MARGPA_ENV_PREFIX/bin/pytest"
```

実質的に次へ解決される。

```text
/bin/pytest
```

したがって、`.venv`消失やTest File不良ではなく、Terminal SessionごとのEnvironment Variable再設定不足が原因である。

### 2.2 復旧

次を設定した。

```bash
export MARGPA_PROJECT_ROOT=/teamspace/studios/this_studio/margpa-runtime-llm
export MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"

cd "$MARGPA_PROJECT_ROOT"
```

確認：

```bash
test -x "$MARGPA_ENV_PREFIX/bin/pytest"
printf 'PYTEST_AVAILABLE=%s\n' "$?"
```

結果：

```text
ENV_PREFIX=/teamspace/studios/this_studio/margpa-runtime-llm/.venv
PYTEST_AVAILABLE=0
```

`0`はExecutableが存在することを示す。

## 3. Linux Lifecycle Unit Test

Environment復旧後に再実行した。

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py
```

結果：

```text
30 passed in 18.70s
```

これによりLinux `/proc` Test Fixture Follow-upのLightning実環境Gateは合格した。

## 4. Basic Preview Preflight

Managed Secretsが新しいTerminalへ注入され、`MARGPA_WEB_AUTH_MODE=basic`を設定した状態でPreflightを実行した。

結果：

```text
check.credentials=pass source=environment values=redacted
```

Credential値そのものは表示・保存されていない。

## 5. 最初のStart失敗

次を実行したが、起動しなかった。

```text
START_EXIT=1
status=stopped
STATUS_EXIT=3

Runtime State Directory:
  does not exist

Basic Preview Log:
  does not exist

PID Evidence:
  does not exist
```

Health CheckとWeb Rootも接続失敗だった。

```text
curl: (7) Failed to connect to 127.0.0.1 port 8000
```

## 6. Runtime State Rootの原因

Terminalで次を明示設定していた。

```bash
export MARGPA_RUNTIME_STATE_ROOT="$MARGPA_WORKSPACE_ROOT/.runtime-state/margpa-runtime-llm/basic-preview"
```

このPathはScriptの組み込みDefaultと文字列上は同じである。しかし、Environment Variableとして明示した場合はOverrideとして扱われる。

安全設計上、明示Overrideは既存の安全な親Directoryを要求する。親Directoryが存在しない状態では、Scriptは無断作成せずMutation前にFail Closedした。

したがって、失敗原因は次である。

```text
Runtime State Default:
  safe automatic creation

Explicit Override:
  caller-managed existing parent required

Observed Failure:
  explicit override selected while parent was absent
```

## 7. Default Runtime Stateへの復旧

通常運用ではOverrideを使わず、Scriptの組み込みDefaultへ戻した。

```bash
unset MARGPA_RUNTIME_STATE_ROOT

test -z "${MARGPA_RUNTIME_STATE_ROOT:-}"
printf 'RUNTIME_STATE_OVERRIDE_UNSET=%s\n' "$?"
```

結果：

```text
RUNTIME_STATE_OVERRIDE_UNSET=0
```

通常のLightning Basic Previewでは、今後も`MARGPA_RUNTIME_STATE_ROOT`を明示設定しない。

明示Overrideを採用する場合は、別の設計判断として親Directory、Ownership、Marker、PermissionおよびRecoveryを確認する。

## 8. Start／Status／Health Acceptance

Default Runtime Stateへ戻して起動した。

結果：

```text
Start:
  status=running pid=466377 health=healthy
  START_EXIT=0

Status:
  status=running pid=466377 health=healthy

Health:
  HTTP/1.1 200 OK
  {"status":"ok"}

Web Root without Credential:
  HTTP/1.1 401 Unauthorized
```

`{"status":"ok"}HTTP/1.1 401 Unauthorized`と同一行に続いて見える場合があるが、これはHealth JSON末尾に改行がない表示上の連結であり、二つのHTTP結果自体は正常である。

## 9. External Browser Acceptance

Lightning外部公開URLで次を確認した。

- Credentialなしでは開けない。
- 誤ったCredentialでは開けない。
- Lightning Managed Secretsに設定したCredentialで開ける。
- 認証後にMARGPA画面を表示できる。
- MARGPA画面からModel生成を実行できる。

Credential実値とPrivate URLは本Evidenceへ保存しない。

## 10. Restart Acceptance

結果：

```text
state_cleanup=stale_pid_file_removed
status=stopped
status=running pid=488529 health=healthy
RESTART_EXIT=0

Status after Restart:
  status=running pid=488529 health=healthy

Health after Restart:
  HTTP/1.1 200 OK
  {"status":"ok"}

Web Root without Credential:
  HTTP/1.1 401 Unauthorized
```

Restart前後でPIDが変化し、新ProcessでHealthとBasic認証境界が成立した。

## 11. Stop Acceptance

結果：

```text
state_cleanup=stale_pid_file_removed
status=stopped
STOP_EXIT=0

Status after Stop:
  status=stopped
  STATUS_EXIT=3

Health after Stop:
  curl: (7) Failed to connect to 127.0.0.1 port 8000
```

`STATUS_EXIT=3`はLifecycle Scriptの正常な停止状態Contractである。停止後にPortが閉じたことも確認した。

## 12. `stale_pid_file_removed`表示

Repository確認により、`state_cleanup=stale_pid_file_removed`は異常なPID Fileだけでなく、正常Stop完了後のPID File削除にも共通して使用される表示である。

今回のRestart／Stopにおける同表示は機能異常ではない。

ただし正常Cleanupでも`stale`と表示されるため、将来のObservability改善候補として次を検討できる。

```text
state_cleanup=pid_file_removed
```

本件は低優先度であり、Acceptanceを妨げない。

## 13. 最終判定

```text
Environment Prefix Recovery:
  PASS

Lightning Lifecycle Unit Test:
  PASS／30

Basic Preview Preflight:
  PASS

Start／Status／Health:
  PASS

External Authentication／Model Generation:
  PASS

Restart:
  PASS

Stop／Port Close:
  PASS

Lightning Basic Preview Manual Lifecycle:
  ACCEPTED
```

Traffic-aware Auto-start、Sleeping Studio Wake-up、匿名Public Demo、RAGおよびGitは本EvidenceのAccepted範囲に含めない。

## 14. 関連Review

- [Linux `/proc` Test Fixture Follow-up Accepted Review](../handoffs/designer_review_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235422.md)
- [Lightning Basic Preview Manual Lifecycle Accepted Review](../handoffs/designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
