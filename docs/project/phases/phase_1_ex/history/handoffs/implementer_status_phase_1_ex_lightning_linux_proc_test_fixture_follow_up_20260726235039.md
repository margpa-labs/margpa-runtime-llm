# Phase 1-ex Lightning Linux `/proc` Test Fixture Follow-up 実装Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_linux_proc_test_fixture_follow_up
phase: phase_1_ex
status: implementation_complete_review_pending
language: ja
created_at: 2026-07-26 23:50:39 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md
source_review: designer_review_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726213429.md
source_external_evidence: lightning_manual_environment_and_preflight_evidence_20260726233910.md
supersedes: null
```

## 1. Result

Lightning Linuxで無効だったIdentity Failure Injectionを、Production Safetyを変更せずTest FixtureだけでCross-platform化した。

```text
Implementation:
  COMPLETE

Local Mac Verification:
  PASS

Lightning Linux Verification:
  NOT_RUN／USER RE-EXECUTION REQUIRED

Designer Review:
  PENDING
```

## 2. Root Cause Reconfirmation

旧Fixtureは`MARGPA_TEST_IDENTITY=invalid`時にFake Process Registry内のCommandだけを書き換えていた。

LinuxではProductionが`/proc/<pid>/cmdline`を優先するため、実Processに残る`margpa-web` Path、Profile、Model Root、HostおよびPortを観測してIdentityをValidと判断した。ProductionのLinux `/proc` Observationは設計どおりであり、Test Fixture側のFailure Injectionだけが不十分だった。

## 3. Fixture Changes

変更File：

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
```

変更後SHA-512：

```text
df7998b9b7c2dbb537abc9a5c81bcb2c53f60df8afd949e6f46662efd13c161032dc1ff8bfce02568ac084029ec845c79a49400deb95f46000efbda7f5b9fbe5
```

変更内容：

- Invalid Identity時、Fake `margpa-web`を専用の`unexpected-lifecycle-child`へ`exec`する。
- 専用Childへ元のHost、Port、Profile、Model Root Argumentを渡さず、Linuxの実`/proc/<pid>/cmdline`でもExpected Identityと一致しないProcessへ切り替える。
- `exec`によりPIDとProcess Start Tokenを維持する。
- Identity遷移完了MarkerをTest専用`mv` Wrapperで待ち、PID Evidence確定後のProduction Identity確認より前に不一致Processへの遷移を確定する。
- Spawn Historyを追加し、Cleanup後に実PIDが停止していることをFake `ps`に依存せず確認する。
- Cleanup成功時の空Registry、PID Evidence削除、Lifecycle Lock削除およびChild停止を確認する。
- Cleanup失敗時はPID／Start Token Evidence保持後、`stop --force`でRecoveryし、Child、PID EvidenceおよびLifecycle Lockが残らないことを確認する。

Test専用Helper、Marker、WrapperおよびHistoryは`tmp_path`配下だけで生成され、実Credential、外部Process、実PortまたはRepository Runtime Stateへ影響しない。

## 4. Production File Changes

```text
scripts/runtime/lightning/basic_preview_common.sh : NOT CHANGED
scripts/runtime/lightning/basic_preview_service.sh: NOT CHANGED
scripts/runtime/lightning/auto_start_preflight.sh : NOT CHANGED
src/                                               : NOT CHANGED
config/                                            : NOT CHANGED
pyproject.toml                                     : NOT CHANGED
uv.lock                                            : NOT CHANGED
```

Linuxの`/proc/<pid>/cmdline`優先、PID／Start Token照合、Process Signal条件およびCredential処理は変更していない。

## 5. Verification

対象2 Test：

```text
test_identity_failure_cleans_the_spawned_alive_child
test_identity_cleanup_failure_retains_evidence_for_forced_recovery

Result: 2 passed
```

Lifecycle Test：

```text
30 passed
```

Repository Full Suite：

```text
297 passed
3 deselected
```

静的確認：

```text
Ruff Check        : PASS
Ruff Format Check : PASS／96 files
Mypy Strict       : PASS／91 source files
```

通常SuiteではModel Smokeを実行していない。`3 deselected`をPassとして扱わない。

## 6. Residual State Confirmation

対象2 Test内で次を確認した。

```text
Cleanup Success:
  Child Process              : STOPPED
  PID Evidence               : REMOVED
  Lifecycle Lock             : REMOVED
  Fake Active Process Entry  : REMOVED

Cleanup Failure／Force Recovery:
  PID／Start Token Evidence  : RETAINED BEFORE RECOVERY
  stop --force               : PASS
  Child Process              : STOPPED AFTER RECOVERY
  PID Evidence               : REMOVED AFTER RECOVERY
  Lifecycle Lock             : REMOVED
```

## 7. Not Run／Known Limitation

- Lightning Linux上の更新File再配置およびLifecycle Test再実行は行っていない。
- Linux `/proc`経路の最終Acceptanceは、ユーザーがLightningへTest Fileを再配置して`30 passed`を確認するまでPendingである。
- Lightning `start／restart／stop` Manual Acceptance、Public URL、Sleep／WakeおよびAuto-start Platform判定は行っていない。
- Lightning外部操作、Managed Secrets変更、Port／Hook変更、Public Demo、匿名Access、RAG、Dependency変更およびGit操作は行っていない。

## 8. Review Gate

設計統括者役のReview Acceptance前に、Lightning `start／restart／stop` Manual Acceptanceまたは後続Phase 1-ex Scopeへ進まない。
