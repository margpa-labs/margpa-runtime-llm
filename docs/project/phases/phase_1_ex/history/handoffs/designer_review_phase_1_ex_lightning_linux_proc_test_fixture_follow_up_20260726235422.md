# Phase 1-ex Lightning Linux `/proc` Test Fixture Follow-up Review

```yaml
document_id: designer_review_phase_1_ex_lightning_linux_proc_test_fixture_follow_up
phase: phase_1_ex
status: accepted_repository_linux_reexecution_pending
language: ja
created_at: 2026-07-26 23:54:22 JST
owner: 設計統括者役
source_handoff: implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md
reviewed_status: implementer_status_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235039.md
supersedes_review: null
```

## 1. Result

```text
Test Fixture Follow-up:
  ACCEPTED_REPOSITORY

Production Runtime Changes:
  NONE

Local Mac Verification:
  PASS

Lightning Linux Re-execution:
  PENDING

Web Lifecycle Manual Acceptance:
  NOT_RUN
```

Linux `/proc/<pid>/cmdline`を優先するProduction Identity Observationを変更せず、Test FixtureだけでIdentity Failureを実Processへ反映する実装になっている。

Repository側Follow-upをAcceptedとする。Lightning Linuxで更新Test Fileを再配置し、Lifecycle Test `30 passed`を確認した時点でCross-platform Test Acceptanceを確定できる。

## 2. Reviewed Files

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md
implementer_status_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235039.md
```

変更後Test File SHA-512：

```text
df7998b9b7c2dbb537abc9a5c81bcb2c53f60df8afd949e6f46662efd13c161032dc1ff8bfce02568ac084029ec845c79a49400deb95f46000efbda7f5b9fbe5
```

## 3. Scope Verification

Production Script Hashは前回Accepted時と一致した。

```text
1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58  scripts/runtime/lightning/basic_preview_common.sh
7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac  scripts/runtime/lightning/basic_preview_service.sh
bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d  scripts/runtime/lightning/auto_start_preflight.sh
```

次は変更されていない。

```text
Production Runtime Scripts
src/
config/
pyproject.toml
uv.lock
Managed Secrets
Lightning Platform State
Git
```

## 4. Fixture Design Review

### 4.1 Actual Process Identity

Invalid Identity時、Fake `margpa-web`は専用`unexpected-lifecycle-child`へ`exec`する。

- `exec`によりPIDを維持する。
- Process Start Tokenを維持する。
- Expected Host、Port、ProfileおよびModel Root ArgumentをChildへ渡さない。
- Linuxの実`/proc/<pid>/cmdline`でもExpected Identityと一致しない。
- 非LinuxではFake Process Registry／Fake `ps`から同じFailureを観測できる。

### 4.2 Race Control

Test専用`mv` WrapperはPID EvidenceのAtomic Move前にIdentity Transition Markerを待つ。これにより、ProductionがIdentity確認を開始する前にChildの`exec`完了を確定する。

Wrapper、Marker、ChildおよびProcess Historyは`tmp_path`配下のFixtureだけであり、Production Fileまたは外部状態へ影響しない。

### 4.3 Cleanup／Recovery

Cleanup成功Scenario：

```text
returncode:
  1

error:
  process_identity_not_verified_child_cleaned

Child:
  STOPPED

PID Evidence:
  REMOVED

Lifecycle Lock:
  REMOVED
```

Cleanup失敗Scenario：

```text
returncode:
  1

error:
  process_identity_not_verified_cleanup_incomplete_pid_evidence_retained

PID／Start Token Evidence:
  RETAINED_BEFORE_RECOVERY

stop --force:
  PASS

Child／PID／Lock:
  REMOVED_AFTER_RECOVERY
```

## 5. Independent Verification

設計統括者Reviewで再実行した。

```text
Target 2 Tests:
  2 passed

Lifecycle Tests:
  30 passed

Repository Full Suite:
  297 passed
  3 deselected

Ruff Check:
  PASS

Ruff Format:
  PASS／96 files

Mypy:
  PASS／96 source files

uv lock --check:
  PASS／122 packages
```

Test自身がChild停止、PID Evidence削除、Lock削除およびForce Recoveryを確認している。

Sandboxからの独立したOS全体Process List取得は利用できなかったため、Process残留判定はTest内の実PID確認をEvidenceとする。

Model SmokeおよびLightning External Lifecycleは実行していない。

## 6. Findings

Blocker、Major Findingおよび追加修正要求はない。

## 7. Lightning Re-execution Gate

Lightningへ再配置するのは次の1 Fileだけでよい。

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
```

期待SHA-512：

```text
df7998b9b7c2dbb537abc9a5c81bcb2c53f60df8afd949e6f46662efd13c161032dc1ff8bfce02568ac084029ec845c79a49400deb95f46000efbda7f5b9fbe5
```

Lightningで次を実行する。

```bash
"$MARGPA_ENV_PREFIX/bin/pytest" -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py
```

期待値：

```text
30 passed
```

`30 passed`確認後、`start／status／healthz／restart／stop` Manual Acceptanceへ進める。

`28 passed／2 failed`が継続する場合は、File Hashと配置Pathを再確認し、Web Lifecycle起動へ進まない。

