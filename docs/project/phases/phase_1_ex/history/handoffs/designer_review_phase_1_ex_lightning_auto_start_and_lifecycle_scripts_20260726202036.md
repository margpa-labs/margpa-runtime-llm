# Phase 1-ex Lightning Auto-start／Basic Preview Lifecycle Scripts Review

```yaml
document_id: designer_review_phase_1_ex_lightning_auto_start_and_lifecycle_scripts
phase: phase_1_ex
status: changes_required
language: ja
created_at: 2026-07-26 20:20:36 JST
owner: 設計統括者役
reviewed_status:
  - implementer_status_phase_1_ex_lightning_auto_start_read_only_preflight_20260726201208.md
  - implementer_status_phase_1_ex_lightning_basic_preview_lifecycle_scripts_20260726201208.md
```

## 1. Result

判定を分離する。

```text
Auto-start Project-side Read-only Preflight:
  ACCEPTED_REPOSITORY_ONLY

Lightning Basic Preview Lifecycle Scripts:
  CHANGES_REQUIRED

Combined Acceptance:
  NOT_ACCEPTED
```

Read-only Preflightは、Project側自動確認とPlatform側Manual Checklistを分離し、外部状態を変更せず、未実行項目をPass扱いしないため、Repository実装としてAcceptedとする。

Lifecycle Scriptは主要構造、Secret非露出、Process Identity確認、Graceful StopおよびTest分離がHandoffに沿っている。一方、実運用時のFile／Process安全性に関するBlockerが残るため、2本まとめてのAcceptanceにはしない。

## 2. Reviewed Files

```text
scripts/runtime/lightning/auto_start_preflight.sh
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
implementer_status_phase_1_ex_lightning_auto_start_read_only_preflight_20260726201208.md
implementer_status_phase_1_ex_lightning_basic_preview_lifecycle_scripts_20260726201208.md
```

## 3. Accepted Points

- Auto-start PreflightはFile、Dependency、Process、NetworkおよびPlatformを変更しない。
- Platform固有項目を`manual_required／not_run`として保持する。
- Basic Preview CredentialはEnvironmentからのみ受け取る。
- Secret値をArgument、PID、LogまたはStatusへ明示的に書かない。
- `run／start／stop／status／restart`を単一主入口へ統合している。
- Model Registry／Artifact、Pure CPU Profile、Python、uvおよびHealth Contractを検査する。
- PIDだけでなくProcess Command Lineを確認する。
- 通常StopはGracefulであり、SIGKILLは`--force`時だけである。
- Model不要のUnit Testとして分離している。
- `src／config／pyproject／uv.lock`を変更していない。
- Lightning外部状態を変更していない。

## 4. Required Findings

### F1. Runtime State Rootが広い既存Directoryを変更できる

Severity: High

`MARGPA_RUNTIME_STATE_ROOT`はProject Root内だけを拒否しているため、Workspace Root、Home、Model Rootまたは別の広い既存Directoryを指定できる。

`start`は指定Directoryそのものへ`chmod 700`を行い、その直下の固定名PID／Log Fileを作成・切り詰めする。誤設定により既存DirectoryのPermission変更または既存Fileの上書きが起こり得る。

Required：

- Runtime State Rootを専用の狭いDirectoryとして検証する。
- `/`、Home、Workspace Root、Project Root、Model Root、Environment Rootおよびそれらの重要な親Directoryを拒否する。
- 既存の広いDirectoryへ`chmod`しない。
- PID／Log／LockのSymlinkまたは非通常Fileを拒否する。
- 安全な専用Directoryだけを作成し、Permissionを設定する。
- 誤設定時にMutation前にFail ClosedするTestを追加する。

### F2. 同時`start`をAtomicに排他していない

Severity: High

現在の二重起動判定はPID確認から新Process起動・PID保存までAtomicではない。Auto-start、Manual Startまたは再試行が重なると、複数Processが起動し、最後に書いたPID以外が追跡不能になる可能性がある。

Required：

- `start／stop／restart`とPID更新をProcess間Lockで直列化する。
- LockはAtomicに取得し、正常／異常終了時に安全に解放する。
- Stale Lockを安全に扱う。
- 同時Start Testを追加し、Web Processが最大1件であることを確認する。

### F3. 起動後Identity確認失敗時に子Processが残り得る

Severity: Moderate

`start`後のIdentity確認が失敗し、Process自体がAliveの場合、現在はErrorを返すだけで子ProcessとPID Evidenceを残す。後続`stop`でもIdentity不一致としてPID Fileを削除すると、Processが追跡不能になる可能性がある。

Required：

- Script自身が起動した子Processを、PID再利用や無関係ProcessへのSignalを避けつつ安全にCleanupする。
- Cleanup不能時はPID Evidenceを削除せず、明確なRecovery情報を返す。
- Identity確認失敗時のAlive Child Testを追加する。
- Health Timeout後にProcessが終了しない場合も、単なる`health_check_timeout`と区別する。

### F4. Credential PreflightがApplicationの有効値条件と一致しない

Severity: Moderate

Shell側は空文字だけを拒否するため、空白だけのUsername／PasswordをPassにする。一方、Application側は空白だけの値を無効として起動拒否する。

Usernameに`:`が含まれる場合もBasic認証形式上Login不能になるが、PreflightはPassにする。

Required：

- 空白だけのUsername／Passwordを拒否する。
- Usernameの`:`、CRおよびLFを拒否する。
- Credential値をErrorへ表示しない。
- Application起動前に同条件でFail ClosedするTestを追加する。

## 5. Verification Performed

```text
Lifecycle／Preflight Unit Test:
  9 passed

Related Lightning／Deployment／Web Test:
  70 passed

Repository Full Suite:
  276 passed
  3 deselected

Ruff Check:
  PASS

Ruff Format Check:
  PASS／96 files

Mypy:
  PASS／96 source files

uv lock --check:
  PASS／122 packages

Shell Syntax:
  PASS
```

Model SmokeおよびLightning External Acceptanceは実行していない。未実行項目をPassとして扱わない。

## 6. Repository Hygiene

Review時にProject内で検出した`.DS_Store`は全件削除した。

`__pycache__`はTest実行で生成され得るため、Phase Backup／Git公開Allowlist確認時に改めて除外・清掃する。

## 7. Scope／Gate

Follow-upはRepository内ScriptとUnit Testに限定する。

次はまだ許可しない。

- Lightningへの配置または実行
- Managed Secrets／Hook／Port／Public URL設定
- Auto-start Go／No-Go確定
- Public Demo
- 匿名Access
- RAG
- Git操作

Follow-up Status作成後、再Reviewを行う。
