# Lightning Stage B Unattended Wake Failure／Private Bootstrap Preparation

```yaml
document_id: lightning_stage_b_unattended_wake_failure_and_private_bootstrap_preparation
status: private_bootstrap_prepared_user_validation_pending
phase: phase_1_ex
created_at: 2026-07-27 18:27:36 JST
owner: 設計統括者役
platform_operator: user
continues_from: lightning_stage_b_manual_trial_preparation_and_port_7860_20260727171551.md
first_unattended_wake: failed
second_unattended_wake: not_run
traffic_aware_auto_start: unconfirmed
private_bootstrap_source_recorded: false
exact_start_command_recorded: false
public_url_recorded: false
credential_values_recorded: false
```

## 1. Purpose

本Recordは、Lightning Stage BのFirst Unattended Wake試験が成立しなかった事実、Studio Sleep／Restart後に確認された状態、原因分析の訂正、Repository外Private Bootstrapの作成方針および設計統括者役による内部Review結果を記録する。

Private BootstrapのSource Code、正確な起動Command、Public URLおよびCredential実値は、本Projectの公開候補DocsまたはRepositoryへ保存しない。

## 2. First Unattended Wake Failure

StudioをSleep状態にした後、OwnerのBrowser TabやTerminal操作に依存せず、別BrowserからAPI Builder発行URLへAccessした。

結果：

```text
API Builder URL Access:
  APPLICATION DID NOT OPEN

First Unattended Wake:
  FAILED

Traffic-aware Auto-start:
  NOT PROVEN
```

Studio稼働中に同じPortとPublic URLでMARGPAを利用できていたため、本FailureはWeb UI、Model RuntimeまたはBasic Previewの通常起動そのもののFailureではない。Sleep状態から必要なRuntime条件を再構築してApplicationを起動する経路が成立していないことを示す。

## 3. Sleep／Restart後の観測

Studio再起動直後、以前のTerminalで設定したShell Environmentは保持されていなかった。

主な観測：

- Project Root用Environmentが未設定のため、Projectへ移動する意図のCommandを実行してもWorkspace Rootに留まった。
- Environment Prefixが未設定のため、Test Commandが`/bin/pytest`を参照しようとして失敗した。
- Read-only PreflightとBasic Preview Preflightは、Runtime State DirectoryのMode不一致をFail Closedで検出した。
- Runtime State PathをEnvironment変数から組み立てる確認では、変数未設定によりFilesystem Root起点の誤ったPathとなった。
- Port Listenerは存在しなかった。
- Terminalへ手動設定したWorkspace、Project、Model、Environment、Port等の値は、Sleep／Restart後の新しいProcessへ自動継承されなかった。
- Managed Secretsの存在確認CommandはExit Code `0`を返した。Unix系Commandでは`0`が成功を意味するため、Username／Passwordは利用可能であった。Credential実値は表示・記録していない。

Project、Model、Project-local EnvironmentおよびRepository Artifactが残っていることと、Terminalの一時EnvironmentやRuntime State Permissionが保持されることは別である。

したがって、以前の「Lightning環境は永続である」という表現は広すぎた。今回のEvidenceから確定できるのは、少なくとも次の区別である。

```text
Project／Model／Environment Artifact:
  PERSISTED

Terminal Export:
  NOT PERSISTED

Process State:
  NOT PERSISTED

Runtime State Permission:
  REVALIDATION／REPAIR REQUIRED

Managed Secrets:
  AVAILABLE TO THE NEW PROCESS
```

## 4. Cause Analysis

当初のAPI Builder On-start設定は、既存のForeground Service Entrypointを呼び出すだけであり、その前提となる全Environment、Port、Path、Permissionおよび安全確認を再構築する責務を持っていなかった。

問題は、Foreground `run`を使用したこと自体ではない。API BuilderのProcess Lifecycleへ所有権を渡すため、Foreground実行は引き続き正しい。

不足していたのは、Foreground Serviceを呼び出す前段の再構築処理である。

```text
API Builder Wake／Start
  ↓
Private Bootstrap
  ├─ 固定Workspace Contractの再構築
  ├─ Project／Model／Environment Pathの検証
  ├─ Port 7860の適用
  ├─ Managed Secrets存在確認
  ├─ Runtime State Permissionの安全な限定修復
  ├─ Symlink／Owner／Mode検査
  └─ Credential値非表示
  ↓
Repository-side Foreground Service
  ↓
MARGPA Web Runtime
```

## 5. Private Bootstrap Decision

Private Bootstrapは、公開Repository内部ではなく、Lightning Workspace上のRepository外Private Artifactとして扱う。

この分離の目的：

- GitHubまたは公開Docsへ運用内部情報を含めない。
- Project Source ArchiveへPrivate Startup設定を混入させない。
- Credential値をCodeへ埋め込まない。
- Managed Secretsを唯一のCredential Sourceとする。
- Lightning固有の再構築処理をApplication Coreから分離する。
- 必要時だけユーザーが原本を管理し、変更時に設計・Review対象として提示できるようにする。

Repository外へ置くことだけでSecurity Boundaryが成立するわけではない。Owner、File Mode、Managed Secrets、公開対象からの除外およびFail-closed Validationを組み合わせて扱う。

## 6. Bootstrap Safety Contract

作成したPrivate Bootstrapは、次のContractを持つ。

- Credential値をSource Codeへ保持しない。
- Managed Secrets由来のUsername／Passwordが空の場合は起動しない。
- Credential値を標準出力、標準Error、StatusまたはFileへ出さない。
- Linux x86_64 Container以外では起動しない。
- Workspace、Project、Model、Project-local Environment、Pure CPU Profile、Model ArtifactおよびService Entrypointを検証する。
- PortはStage Bで確定した`7860`へ統一する。
- 不要なRuntime State Root Overrideを子Processへ継承しない。
- Bootstrap自身、Runtime State、Marker、Log、PID EvidenceおよびLifecycle Lockを限定対象として扱う。
- Symbolic Link、Owner不一致、Group／World Writable等の危険状態では自動修復せずFail Closedする。
- Sleep等でRead／Execute Modeだけが変化したOwner所有Artifactは、必要最小限のPermissionへ限定修復する。
- Foreground Processを`exec`で置換し、API BuilderがProcess Lifecycleを所有できるようにする。
- Runtime起動時にTest-only Artifactを必須にしない。
- Test Commandを明示した場合だけ、限定Unit Test Artifactを要求する。

## 7. Internal Review／Verification

Private Bootstrapは公開Repositoryへ追加せず、設計統括者役の一時検証領域で作成・Reviewした。

内部検証結果：

```text
Ruff:
  PASS

Mypy strict:
  PASS

Python Syntax:
  PASS

Simulated Bootstrap Safety／Environment Tests:
  3 PASS

Existing Lightning Basic Preview Lifecycle Unit Tests:
  32 PASS
```

疑似試験では、Bootstrap File Mode修復、危険なWritable Mode拒否、Virtual EnvironmentのPython Symlink許容、Executable Permission修復、Runtime State `700`／Evidence `600`修復、危険なRuntime Evidence拒否、Symlink拒否、Managed Secrets継承、Runtime State Override除去、Port適用、Test-only依存分離およびForeground `exec`契約を確認した。

この結果はRepository-side Reviewと疑似環境試験の合格であり、Lightning Sleep／Wake実機合格ではない。

## 8. Public Documentation Boundary

公開候補Docsへ記録してよい範囲：

- Repository外Private Bootstrapが存在すること。
- Sleep後の一時EnvironmentとPermissionを安全に再構築する役割。
- CredentialをManaged Secretsから受け取り、値を記録しないこと。
- Fail-closed ValidationとForeground Service委譲。
- 実機試験の合否と制約。

公開候補へ記録しない範囲：

- Private BootstrapのSource Code全文。
- 正確なPrivate Startup Command。
- Credential実値。
- Public URL実値。
- Secret設定値。
- Private Artifactの配布物。

## 9. Current State／Next Gate

```text
Running-Studio Public URL Smoke:
  PASS

First Unattended Wake:
  FAILED

Private Bootstrap:
  PREPARED／INTERNALLY REVIEWED

Private Bootstrap Lightning Placement:
  USER ACTION PENDING

Private Bootstrap Preflight／Test:
  USER VALIDATION PENDING

First Unattended Wake Retest:
  NOT RUN

Second Unattended Wake:
  NOT RUN

Traffic-aware Auto-start:
  UNCONFIRMED
```

次の作業はユーザーがLightning上で行う。

1. Repository外の所定位置へPrivate Bootstrapを配置する。
2. Private File Modeを設定する。
3. Managed Secretsを利用できるProcessでPreflightを実施する。
4. 限定Unit Testを実施する。
5. Manual Foreground起動を確認する。
6. API BuilderのOn-startをPrivate Bootstrap経由へ変更する。
7. StudioをSleepさせ、Owner Session不在の別BrowserからFirst Unattended Wakeを再試験する。
8. First合格後にSecond Unattended WakeとURL持続性を確認する。

実機Evidenceが返るまで、Traffic-aware Auto-startを合格扱いにしない。
