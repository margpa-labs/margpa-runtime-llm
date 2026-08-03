# Phase 1-ex Lightning Lifecycle Safety Follow-up Review

```yaml
document_id: designer_review_phase_1_ex_lightning_lifecycle_safety_follow_up
phase: phase_1_ex
status: accepted_with_non_blocking_observations
language: ja
created_at: 2026-07-26 21:34:29 JST
owner: 設計統括者役
source_handoff: implementer_handoff_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726202036.md
reviewed_status:
  - implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726211653.md
  - implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726212010.md
supersedes_review: designer_review_phase_1_ex_lightning_auto_start_and_lifecycle_scripts_20260726202036.md
```

## 1. Result

```text
Auto-start Project-side Read-only Preflight:
  ACCEPTED_REPOSITORY_ONLY

Lightning Basic Preview Lifecycle Scripts:
  ACCEPTED_REPOSITORY_ONLY

Lifecycle Safety Follow-up F1–F4:
  RESOLVED

Combined Repository Acceptance:
  ACCEPTED

Lightning External Acceptance:
  NOT_RUN
```

前ReviewのHigh／Moderate Finding F1～F4は解消された。Repository内実装としてLightning Auto-start Read-only PreflightとBasic Preview Lifecycle ScriptsをAcceptedとする。

本判定はLightning上のFile配置、Managed Secrets、Hook、Port、Public URL、Traffic-aware Auto-start、Sleep／Wake、Model Loadまたは外部到達性をAcceptedとするものではない。

## 2. Reviewed Files

```text
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/auto_start_preflight.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
implementer_handoff_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726202036.md
implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726211653.md
implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726212010.md
```

## 3. Finding Resolution

### F1. Dedicated Runtime State Safety

Status：`RESOLVED`

- Final Directory名を`basic-preview`へ限定している。
- `/`、Home、Workspace、Project、Model、Environmentおよび重要な親DirectoryをMutation前に拒否する。
- Project／Model／Environment Tree内を拒否する。
- 既存Directoryは専用Marker、ModeおよびAccess条件を満たす場合だけOwned Stateとして扱う。
- 既存Directoryへ無条件`chmod`しない。
- PID、Log、State Root、LockおよびLock OwnerのSymlink／非通常Fileを拒否する。
- Logを切り詰めず、PID EvidenceをAtomic更新する。

### F2. Atomic Lifecycle Lock

Status：`RESOLVED`

- Atomic `mkdir` Lockで`start／stop／restart`とPID更新を直列化する。
- Lock Marker、Owner PID、Mode、ContentおよびAccess条件を確認する。
- Alive Ownerは`busy`、死亡Ownerかつ正しいMarkerだけStale回収する。
- 正常、ErrorおよびSignal経路でLock解放を処理する。
- Concurrent Startを5回再実行し、毎回1 Processだけが追跡された。

### F3. Spawned Child Cleanup／Recovery Evidence

Status：`RESOLVED`

- PIDとProcess Start TokenをEvidenceとして保持する。
- Command IdentityまたはStart Token一致時だけSignalを送る。
- Identity FailureおよびHealth Timeout時にOwned Child Cleanupを試みる。
- Cleanup不能時はPID／Start Token Evidenceを保持し、Errorを区別する。
- 無関係ProcessとPID再利用後のProcessを保護する。

### F4. Credential Validation

Status：`RESOLVED`

- 未設定、空文字および空白だけのUsername／Passwordを拒否する。
- Usernameの`:`、CRおよびLFを拒否する。
- PasswordのCRおよびLFを拒否する。
- SecretをArgument、Log、PID、Lock、StatusまたはErrorへ表示しない。
- Application起動前にFail Closedする。

## 4. Independent Verification

設計統括者Reviewで再実行した結果：

```text
Lifecycle Safety Unit Test:
  30 passed

Repository Full Suite:
  297 passed
  3 deselected

Concurrent Start Stability:
  1 passed × 5 consecutive runs

Shell Syntax:
  PASS

Ruff Check:
  PASS

Ruff Format:
  PASS／96 files

Mypy:
  PASS／96 source files

uv lock --check:
  PASS／122 packages
```

`uv lock --check`はSandbox外CacheへのWriteを避けるため、`UV_CACHE_DIR=/private/tmp/margpa-uv-cache`で実行した。Lock内容は変更していない。

Model Smoke、Lightning Lifecycle実行、External URLおよびAuto-start Platform Acceptanceは実行していない。

## 5. Secret／Repository Hygiene

- 固定Credentialは検出されなかった。
- User Manual／Requirements内のCredential表記はPlaceholderまたは実行時Random生成例である。
- Test Credentialは実行時生成される。
- Test後のFake Process残留は確認されなかった。
- Review中に再生成された`.DS_Store` 6件を、既存除外方針に従って削除した。
- Git操作は行っていない。

## 6. Non-blocking Observations

### O1. Runtime State Help表現

`basic_preview_service.sh`のHelpは、Runtime Stateを「Workspace外」と読める表現である。一方、既定PathはWorkspace配下の専用`.runtime-state/.../basic-preview`であり、実際の禁止境界はWorkspace Rootそのもの、広いRootおよび保護Treeである。

Runtime Safety動作には影響しない。次回User Manual／Help Refreshで、既定Pathと禁止境界が一致する表現へ正規化する候補とする。

### O2. Final Accessibility Hardeningの専用Regression Test

最終Statusで追加されたState／Lock DirectoryのRead／Write／Execute検査はCode上確認できるが、この最終Delta専用のTest Case追加はなく、Test数は前Statusと同じ30件である。

F1～F4の必須AcceptanceとFail-closed動作は既存TestおよびCode Reviewで確認できるためBlockerにはしない。将来Test更新時に、Access不能なOwned State／Lockを明示Fixtureで固定する候補とする。

## 7. Scope／Next Gate

Repository側Safety Follow-upは完了した。

次に進められるのは、ユーザー管理下のLightning環境における次の作業である。

```text
Read-only Preflight
Basic Preview Lifecycle Preflight
Managed Secrets設定
Foreground／Background Lifecycle確認
Local Health Check
Public URL／Sleep／Wake／Auto-start Manual Checklist
```

ただし、匿名Public Demo、Public Demo Guard、RAG、Dependency変更、Git操作またはAuto-start Go判定を、本Reviewだけで自動許可しない。各作業は既存Phase 1-ex要件とユーザーの明示許可に従う。

