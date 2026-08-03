# 実装担当向け Phase 1-ex Lightning Lifecycle Safety Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_lifecycle_safety_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-26 20:20:36 JST
owner: 設計統括者役
target_role: 実装者役
source_review: designer_review_phase_1_ex_lightning_auto_start_and_lifecycle_scripts_20260726202036.md
supersedes: null
```

## 1. Objective

Auto-start Read-only PreflightのAccepted部分を維持したまま、Lightning Basic Preview Lifecycle Scriptsに残るFile／Process安全性のBlockerだけを修正する。

## 2. Authorized Files

```text
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
docs/project/phases/phase_1_ex/history/handoffs/
```

`auto_start_preflight.sh`は、共通Helper変更への追随が必要な最小差分だけ許可する。

`src／config／pyproject.toml／uv.lock`、Requirements、Architecture、ADR、Shared Policy、CurrentおよびPublic Docsは変更しない。

## 3. Required Changes

### 3.1 Dedicated Runtime State Safety

- 広い既存DirectoryをRuntime State Rootとして受理しない。
- `/`、Home、Workspace、Project、Model、Environmentおよび重要な親Directoryを拒否する。
- Mutation前に対象を検証する。
- 既存Directoryへ無条件`chmod 700`しない。
- PID／Log／LockのSymlinkと非通常Fileを拒否する。
- 専用Directoryと内部Fileだけを安全に作成する。

### 3.2 Atomic Lifecycle Lock

- `start／stop／restart`およびPID更新をAtomic Lockで直列化する。
- 正常終了、Error、Signal時のLock解放を定義する。
- Stale Lockを無関係Processへ影響させず処理する。
- 同時StartでProcessが最大1件になるTestを追加する。

### 3.3 Spawned Child Cleanup

- Identity確認失敗時に、Script自身が起動したAlive Childを安全にCleanupする。
- 無関係ProcessへSignalを送らない。
- Cleanup不能時はPID Evidenceを保持し、Recovery可能なErrorを返す。
- Health FailureとCleanup Failureを区別する。

### 3.4 Credential Validation

- 空白だけのUsername／Passwordを拒否する。
- Usernameの`:`、CRおよびLFを拒否する。
- Secret値をOutputへ出さない。
- Application起動前にFail Closedする。

## 4. Required Tests

- Workspace Root等の広いDirectory指定時にMutation前拒否
- Runtime State Root／PID／Log／LockのSymlink拒否
- 同時`start`の排他
- Stale Lock
- Identity確認失敗中のAlive Child Cleanup
- Cleanup不能時のEvidence保持
- 空白Credential
- `:`を含むUsername
- CR／LF Credential
- 既存9 Testの維持
- 関連TestとRepository Full Suite
- Shell Syntax、Ruff、Mypy、Lock Check

Test用Credentialは固定の実Credentialに見える値をRepositoryへ追加せず、動的に生成する。

## 5. Prohibited

- Lightning外部状態の変更
- File Upload
- Managed Secrets、Hook、PortまたはURL設定
- Public Demo／匿名Access
- RAG
- Dependency変更
- Git操作
- 要件拡張

## 6. Status

完了後、次を新Timestampで作成する。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up_YYYYMMDDHHMMSS.md
```

変更File、各Findingへの対応、Test、未実行項目および既知制限を記載する。

## 7. Acceptance

- Review F1～F4がすべて解消される。
- Read-only PreflightのAccepted性を壊さない。
- Lifecycle操作が広いDirectory、無関係Processまたは秘密値へ影響しない。
- Concurrent Startで追跡対象が1 Processを超えない。
- Failure時に孤児Processまたは回復不能なEvidence欠落を生じさせない。
- 全自動検証が合格する。

実装者Status作成後、設計統括者役へ再Reviewを依頼する。
