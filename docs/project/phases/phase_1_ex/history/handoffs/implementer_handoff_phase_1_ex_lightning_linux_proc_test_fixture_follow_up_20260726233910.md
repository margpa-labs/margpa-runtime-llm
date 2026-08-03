# 実装担当向け Phase 1-ex Lightning Linux `/proc` Test Fixture Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-26 23:39:10 JST
owner: 設計統括者役
target_role: 実装者役
source_review: designer_review_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726213429.md
source_external_evidence: lightning_manual_environment_and_preflight_evidence_20260726233910.md
supersedes: null
```

## 1. Objective

Macでは合格するがLightning Linuxでは失敗する、Process Identity Failure Cleanupの2 Testを、Production Safetyを弱化せずCross-platform化する。

本Follow-upはTest Fixtureの修正であり、Accepted済みLightning Lifecycle Runtimeの仕様変更ではない。

## 2. External Evidence

Lightning Linux x86_64 Pure CPU環境：

```text
File／SHA-512:
  PASS

Managed Secrets:
  PASS

Read-only Auto-start Preflight:
  PASS

Basic Preview Preflight:
  PASS

Lifecycle Test:
  28 passed
  2 failed
```

失敗：

```text
test_identity_failure_cleans_the_spawned_alive_child
test_identity_cleanup_failure_retains_evidence_for_forced_recovery
```

詳細は[Lightning Manual Environment／Preflight Evidence](../operations/lightning_manual_environment_and_preflight_evidence_20260726233910.md)を参照する。

## 3. Root Cause

ProductionのProcess Identity Observationは、Linuxで`/proc/<pid>/cmdline`が読める場合にこれを優先する。

現行Test FixtureのFake `margpa-web`は、`MARGPA_TEST_IDENTITY=invalid`時にFake Process Registryへだけ`/unexpected/lifecycle-child`を記録する。

Macでは`/proc`がないためFake `ps`が使われ、Identity Failureを再現できる。Linuxでは実`/proc/<pid>/cmdline`に正しいFixture Script Pathと起動Argumentが残るため、IdentityがValidになり、`start`がReturn Code `0`で完了する。

## 4. Authorized Files

Primary：

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
```

Status：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_YYYYMMDDHHMMSS.md
```

Production Fileは原則Read-onlyとする。

```text
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/auto_start_preflight.sh
src/
config/
pyproject.toml
uv.lock
```

Test Fixtureだけでは安全に解決できずProduction変更が必要と判断した場合は、変更前に停止し、理由、影響、安全性および代替案を設計統括者役へEscalateする。無断でProduction Identity判定を変更しない。

## 5. Required Implementation

### 5.1 Linux Identity Failure Injection

Linux上でもProduction Codeが観測する実際のProcess Identityを不一致にするFixtureを作る。

許容する方向：

- Fake Child自身の実`argv／cmdline`を、期待する`margpa-web` Identityと一致しない状態へ切り替える。
- Test Process構造を変更し、Productionの通常Observation経路から不一致を観測できるようにする。
- Test専用Wrapper／Childを使い、Linuxと非Linuxの両方で同じFailure Contractを再現する。

### 5.2 Production Safety Preservation

- Linuxの`/proc/<pid>/cmdline`優先を削除または弱化しない。
- PIDとProcess Start Tokenの照合を弱化しない。
- Fake `ps`だけをProduction上で強制する一般利用可能なUnsafe Switchを追加しない。
- 無関係ProcessへSignalを送れるTest Hookを追加しない。
- Test用挙動が実Credential、外部Processまたは実Portへ影響しないようにする。

### 5.3 Required Scenarios

#### Identity Failure／Cleanup Success

```text
Expected:
  returncode == 1
  process_identity_not_verified_child_cleaned
  PID Evidence removed
  Child Process terminated
  Lifecycle Lock removed
```

#### Identity Failure／Cleanup Failure

```text
Expected:
  returncode == 1
  process_identity_not_verified_cleanup_incomplete_pid_evidence_retained
  PID／Start Token Evidence retained
  stop --forceでRecovery可能
  Recovery後にChild／PID／Lock残留なし
```

## 6. Required Tests

Local Mac：

```bash
./.venv/bin/pytest -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py
```

期待値：

```text
30 passed
```

対象2 Testの個別実行：

```bash
./.venv/bin/pytest -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py::test_identity_failure_cleans_the_spawned_alive_child \
  tests/unit/runtime/test_lightning_basic_preview_service.py::test_identity_cleanup_failure_retains_evidence_for_forced_recovery
```

Repository Full Suite：

```bash
./.venv/bin/pytest -q
```

静的確認：

```text
Ruff Check
Ruff Format Check
Mypy
```

Linuxでの最終Acceptanceは、実装Status Review後にユーザーがLightningへ更新Fileを再配置し、同じLifecycle Testを実行して`30 passed`を確認する。

## 7. Prohibited

- Production `/proc` Identity Observationの弱化
- Process Signal条件の緩和
- Managed Secretsの値追加
- 固定Test Credentialの追加
- Lightning外部操作
- Port／Hook／Public URL変更
- Auto-start Go／No-Go
- Public Demo／匿名Access
- RAG
- Dependency変更
- Git操作
- 要件拡張

## 8. Status Requirements

完了後、次を新Timestampで作成する。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_YYYYMMDDHHMMSS.md
```

記載事項：

- Root Cause再確認
- Fixture変更内容
- Production File変更有無
- 対象2 Test結果
- Lifecycle 30 Test結果
- Full Suite
- Ruff／Mypy
- Child／PID／Lock残留確認
- Lightningで未実行の項目
- 既知制限

## 9. Acceptance

- MacでLifecycle Testが全件合格する。
- LinuxでIdentity Failureを実際に再現できる設計である。
- Production Identity／Signal Safetyを弱化しない。
- Test終了後にFake Child、PID EvidenceまたはLockを残さない。
- Repository Full Suiteを維持する。
- 実装Statusを作成し、設計統括者役のReviewを受ける。

本HandoffのReview Acceptance前に、Lightning `start／restart／stop` Manual Acceptanceへ進まない。

