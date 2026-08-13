# Phase 2-B Design Conformance Review

```yaml
review_id: phase_2_b_design_conformance_review_20260814020244
status: rework_required
phase: phase_2
subphase: phase_2_b
created_at: 2026-08-14 02:02:44 JST
from_role: Phase 2設計担当者役
to_role: プロジェクト責任者兼設計統括者役
reviewed_result: implementer_status_phase_2_b_20260814015827
result: PARTIAL
closure_recommendation: ADJUST
```

## 1. Conclusion

実装はPackage分離、SQLite CAS、Canonical Serialization、Lifecycle、Context Mapper、Crash Recovery、Default Recording OFFおよび既存v1／Public／Basic Zero-bindingの大部分でFrozen Designに適合する。Target Testは独立再実行でも`35 passed`、対象RuffもPASSした。

ただし、Migrationの排他／Path境界とApplication層のUnknown Outcome／失敗後LifecycleにRequired Defectがある。Phase 2-Bは現時点でClosure不可とし、Phase 2実装者役へ局所Reworkを返す。Domain、Port、既存v1、Web、ConfigまたはPublic／Basicを変更する必要はない。

## 2. Required Findings

### P2B-RW-001 — CRITICAL — Migration中のConcurrent WriteがCutoverで消失し得る

対象：`P2B-MIG-002`、`P2B-MIG-003`、CAS／Migration整合

`sqlite_migration.py`はSource DBへ`BEGIN EXCLUSIVE`した後、Checkpoint／Staging／Markerを作ってTransactionをCommitし、Lockを解放してからTransformと`os.replace`を行う。一方、Repository Writeは`_require_ready()`をTransaction取得前に確認するだけで、Write Transaction取得後にMigration Stateを再確認しない。

したがって、次のRaceが成立する。

```text
Migration: marker作成 -> Source EXCLUSIVE解放 -> staging変換
Writer   : 事前Readiness通過 -> SourceへCommit
Migration: stale stagingをos.replace
Result   : WriterのAccepted Commitが消失
```

これはAtomic CAS成功を後続Migrationが消すためRequired Failureである。

Rework対象：

- `src/margpa_runtime_llm/modules/conversation/adapters/sqlite_migration.py`
- `src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py`
- `tests/unit/conversation/test_sqlite_migration.py`
- `tests/unit/conversation/test_sqlite_conversation_store.py`または`tests/integration/conversation/test_local_conversation_persistence.py`

Required Result：Migration GateをDB／Adapter双方で原子的に成立させ、Marker／Migration State確定後に開始しようとしたWriterと、Readiness確認後に待機していたWriterの双方をFail-closedにする。CheckpointからCutoverまでのConcurrent Writeが成功・消失しないTestを追加する。

### P2B-RW-002 — CRITICAL — Migration IdentityとSymlinkからRecovery Root外へWrite可能

対象：`P2B-MIG-002`、Filesystem Boundary

`checkpoint_id`と`migration_id`をそのままFilenameへ連結しており、Port ContractはSlash／`..`を禁止していない。またMigration側`_make_private_directory()`は、既存DirectoryのOwner／Mode／Symlink／Containmentを検証しない。通常Maintenance経路でも、攻撃的または誤ったCheckpoint IDや、後置SymlinkによりCheckpoint／Marker／Staging Writeが予約Root外へ逸脱し得る。

Rework対象：

- `src/margpa_runtime_llm/modules/conversation/adapters/sqlite_migration.py`
- `tests/unit/conversation/test_sqlite_migration.py`

Required Result：External IdentityをPath Segmentとして使わずDomain-separated Digest Keyへ変換するか、等価なStrict Mappingを行う。Active、Checkpoint、Marker、Staging、Restoreの全PathについてResolved Containment、Owner、Mode、Symlink／Regular Fileを検証し、既存対象を自動修正しない。Traversal、Absolute-like値、Symlink、Unsafe ModeのTestを追加する。

### P2B-RW-003 — HIGH — Application CommitがUnknown OutcomeをReceiptで収束しない

対象：`P2B-CAS-003`、`P2B-LIF-003`、`P2B-REC-002`

Store単体はResponse Loss後のReceipt照合をTestしているが、`PersistentConversationService._commit()`は`unknown`をそのまま上位へ送る。特にTerminal Commitが実際には成功してResponseだけ失われた場合、`_persist_terminal()`は`terminal_persistence_failed`へ変換し、保存済みCanonical ResultをClientへ成功通知しない。Frozen Requirementsの「完全な同一Operationの適用が証明できた場合だけ継続」に不適合である。

RecoveryもReceiptの存在だけを見ており、Scope、Conversation、Operation、Previous／Committed Revisionの完全一致を検証していない。

Rework対象：

- `src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py`
- `tests/unit/conversation/test_persistent_conversation_service.py`

Required Result：全Application Commitで`unknown`時に同一Operation Receiptを照合し、期待するScope／Conversation／Operation／Revision Stepが完全一致する場合だけ成功へ収束する。Terminal Response LossではTerminal Eventを一度だけ公開し、不一致／ReceiptなしはFail-closedとする。Recovery Receiptも同じ完全一致を要求する。

### P2B-RW-004 — HIGH — Generation開始前後の失敗がConversation／Ephemeral SessionをStuckさせる

対象：`P2B-LIF-001`、`P2B-MAP-002`、Storage Failure Boundary

`generate_turn()`はPending Commit後のContext Mapping失敗をTerminal化しないため、Context Limit Error後にPending Turnが残り、同じProcessでは次Turnを開始できない。また既存Generation Serviceの`start()`成功後、Generating Commitが失敗した場合、登録済みEphemeral SessionをReleaseする処理がなく、既存Generation RuntimeをBusyのまま残し得る。

Rework対象：

- `src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py`
- `tests/unit/conversation/test_persistent_conversation_service.py`

Required Result：Mapping／Generation Start／Generating Commitの各失敗点で、Persistent Turnと既存Generation Sessionを決定的かつ有界に終了させる。Context LimitはGeneration Call 0を維持しつつTurnをFailedまたはInterruptedへ収束させる。Start後のPersistence失敗ではEphemeral SessionをCancel／Releaseし、次RequestをBusyにしない。Cleanup自体が証明できない場合はServiceをFAILEDへ落とし、元ErrorとCleanup Failureを混同しない。

## 3. Acceptance Matrix Review

```text
PASS:
  P2B-STO-001..005
  P2B-CAS-001..002, P2B-CAS-004..005
  P2B-MIG-001, P2B-MIG-004
  P2B-FAL-001..002
  P2B-LIF-002, P2B-LIF-004
  P2B-MAP-001
  P2B-REC-001
  P2B-PRV-001..002
  P2B-REC-003
  P2B-CMP-001..003
  P2B-QA-001..005

FAIL／REWORK:
  P2B-CAS-003
  P2B-MIG-002..003
  P2B-LIF-001, P2B-LIF-003
  P2B-MAP-002
  P2B-REC-002
```

`P2B-MAP-002`のGeneration Call 0自体はPASSしているが、失敗後Lifecycleを含むEnd-to-end AcceptanceとしてReworkへ分類した。

## 4. Forbidden Path／Compatibility Review

```text
Phase 2-A domain mutation evidence       : 0
Phase 2-A ports mutation evidence        : 0
Existing conversation contracts/public  : 0
Existing conversation_generation.py     : 0
Web／entrypoints／config binding         : 0
Public Demo／Shared Basic Preview binding: 0
Project Root runtime_data/               : absent
Concrete Recorder                        : 0
Git／Network／External                   : 0
```

Phase 2-Bの既存File変更は許可された`application/__init__.py`の新Exportだけである。新Source／Test／StatusはFrozen HandoffのAllowed Paths内に収まる。

## 5. Independent Validation

```text
.venv/bin/pytest -q <Phase 2-B six target files>
35 passed in 0.48s

.venv/bin/ruff check \
  src/margpa_runtime_llm/modules/conversation/adapters \
  src/margpa_runtime_llm/modules/conversation/application \
  tests/unit/conversation tests/integration/conversation
All checks passed
```

既存Implementer EvidenceのConversation／Web Regression、MypyおよびFull Suite合格も確認対象に含めた。上記Findingは既存Test未包含のFailure Interleaving／Lifecycle Cleanupであり、Green Testを否定せずAcceptance Coverage不足を示す。

## 6. Exact Rework Route

```text
From : Phase 2設計担当者役
To   : Phase 2実装者役
Task : P2B-RW-001..004だけを修正し、該当Testを追加する
Do not modify:
  Phase 2-A domain／ports
  Existing v1 contracts／public／conversation_generation
  Web／entrypoints／config
  Stable Docs／Frozen Design Docs
Return:
  New implementer rework status -> Phase 2設計担当者役
```

## 7. Closure Recommendation

```text
Recommendation : ADJUST
Current closure: NOT ACCEPTED
Required action : Implementer rework P2B-RW-001..004
After rework    : Designer re-review -> Controller closure review
Human decision  : none required for this in-scope rework
```
