# Phase 1-ex Lightning Lifecycle Safety Follow-up 実装Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up
phase: phase_1_ex
status: implementation_complete_review_pending
language: ja
created_at: 2026-07-26 21:16:53 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726202036.md
source_review: designer_review_phase_1_ex_lightning_auto_start_and_lifecycle_scripts_20260726202036.md
supersedes: null
```

## 1. Result

設計Review F1～F4へ対応した。

Auto-start Project-side Read-only PreflightのAccepted境界を維持し、Lightning外部状態、Dependency、Config、Application Core、Model、Public AccessおよびGit状態を変更していない。

## 2. Changed Files

```text
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/auto_start_preflight.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
```

`auto_start_preflight.sh`は、専用Runtime State Directory制約をHelpへ追記する最小追随だけを行った。

変更していないもの：

```text
src/
config/
pyproject.toml
uv.lock
Requirements
Architecture
ADR
Shared Policy
Current
Public Docs
```

## 3. F1：Dedicated Runtime State Safety

次を実装した。

- Runtime State Rootの最終Directory名を`basic-preview`へ限定
- `/`、Home、Workspace、Project、Model、Environmentおよび重要な親Directoryを拒否
- Project／Model／Environment Tree内を拒否
- Runtime State Path内のSymlink Componentを拒否
- 既存Directoryは正本Marker、Directory Mode `0700`、Marker Mode `0600`を要求
- Markerのない既存Directoryを所有済みとみなさない
- 既存Directoryへ無条件`chmod`しない
- 既存Logを切り詰めず追記
- PID／Log／Lock／Lock OwnerのSymlinkおよび非通常Fileを拒否
- PID／Log／Marker／Lock Owner Modeを`0600`として検証
- Atomic Temporary File＋RenameによるPID Evidence更新
- Mutation前のPath／Artifact検証

広い既存Directoryまたは不正Artifactを指定した場合、Permission、内容、Symlink Targetおよび外部Processを変更せずFail Closedする。

## 4. F2：Atomic Lifecycle Lock

Workspace直下の専用Lock DirectoryをAtomic `mkdir`で取得する。

```text
.margpa-runtime-llm-basic-preview.lifecycle.lock/
└─ owner.pid
```

Lock Owner Fileは専用MarkerとOwner PIDを保持する。

- `start／stop／restart`全体をLockで直列化
- PID確認、Process Spawn、PID Evidence更新およびStopを同じCritical Sectionへ包含
- Lock Directory `0700`、Owner File `0600`
- Symlink、非Directory、非通常Owner、Marker不一致および予期しない内容を拒否
- Owner PIDがAliveの場合は`busy`でFail Closed
- Marker一致、Owner死亡、予期しない内容なしの場合だけStale Lockを回収
- 正常終了、ErrorおよびSignal時のLock解放
- Lock解放時もOwner Marker／PIDを再照合

Concurrent Start Testを5回連続で実行し、毎回Web Process最大1件を確認した。

## 5. F3：Spawned Child Cleanup／Recovery Evidence

Process PIDだけでなくProcess Start Tokenを取得し、PID Evidenceへ保存する。

```text
Line 1: PID
Line 2: Process Start Token
```

Linuxでは`/proc/<pid>/stat`のStart Timeを使用し、Fallbackでは`ps lstart`を使用する。

- Command IdentityまたはStart Token一致時だけSpawned ChildへSignalを送る。
- Identity確認失敗時、Script自身のChildをGraceful Cleanupする。
- Health Timeout時も同じOwnership確認後にCleanupする。
- Cleanup成功時はPID Evidenceを除去する。
- Cleanup不能時はPID Evidenceを保持し、`cleanup_incomplete_pid_evidence_retained`を返す。
- Health FailureとCleanup Failureを別Errorへ分類する。
- 後続`stop --force`はStart Token Evidenceを再照合し、安全にRecoveryできる。
- PID Evidence書込失敗時もChild Cleanupを試行し、Cleanup不能時はRecovery PIDを出力する。
- Signal受信中のStartは、Child Cleanupを試行してからLockを解放する。

無関係ProcessまたはPID再利用後のProcessへSignalを送らない。

## 6. F4：Credential Validation

Applicationと同じPython `str.strip()`条件をModel Load前に適用した。

- 未設定Username／Passwordを拒否
- 空文字を拒否
- 空白だけのUsername／Passwordを拒否
- Usernameの`:`、CRおよびLFを拒否
- PasswordのCRおよびLFを拒否
- Credential値をArgument、Output、Log、PID、LockまたはStatusへ出さない
- Validation PythonへはEnvironmentとしてのみ継承

Test Credentialは実行時に動的生成し、固定Credential値をRepositoryへ追加していない。

## 7. Tests

Required Safety Test：

```text
Lifecycle Safety Unit Test : 30 passed
Concurrent Start Stability : 1 passed × 5 consecutive runs
Related Lightning／Web     : 100 passed
Repository Full Suite      : 297 passed／3 deselected
```

含む確認：

- 広い／保護対象State RootのMutation前拒否
- Markerのない既存DirectoryのMode／内容維持
- Owned Logの非切り詰め
- State Root／PID／Log／Lock／Lock Owner Symlink拒否
- PID／Log非通常File拒否
- Concurrent Start最大1 Process
- Stale Lock回収
- Identity失敗Child Cleanup
- Cleanup不能時のPID Evidence保持と強制Recovery
- Health Cleanup Failureの独立分類
- 空白Credential
- `:` Username
- CR／LF Credential
- Secret非露出
- Spaceを含むPath
- 既存Lifecycle／Read-only Preflight回帰

## 8. Static／Repository Verification

```text
Shell Syntax       : PASS
Ruff Check         : PASS
Ruff Format        : PASS／96 files
Mypy Strict        : PASS／96 source files
uv lock --check    : PASS／122 packages
Fake Process残留  : 0
```

通常SuiteではModel Smokeを実行していない。`deselected`をPassとして扱わない。

## 9. Not Run

- LightningへのFile配置
- Managed Secrets／Hook／Port／Public URL設定
- Lightning Lifecycle実行
- Model Load／SHA-512再計算
- Auto-start Go／No-Go
- Public Demo／匿名Access
- RAG
- Git操作

## 10. Known Limitations

- Lockは単一Workspace内の単一Filesystemを前提とする。
- Lock Owner PIDが無関係Processへ再利用された場合、安全側で`busy`を維持し、手動確認を必要とする。
- Linux Production Process Identityは`/proc`を使用し、非Linux Fallbackは`ps`可用性に依存する。
- Cleanup不能時はProcessを追跡不能にせずPID／Start Token Evidenceを保持するため、後続の明示Recoveryが必要である。
- Local Health CheckはLightning Public URLの外部到達性を保証しない。

## 11. Review Gate

設計統括者役の再Review Accepted前に、Lightning配置／実行、Secret／Hook／Port変更、Auto-start Go／No-Go、Public Demo、匿名Access、RAGまたはGitへ進まない。
