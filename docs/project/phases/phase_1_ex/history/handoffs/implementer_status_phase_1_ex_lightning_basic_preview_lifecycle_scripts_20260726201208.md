# Phase 1-ex Lightning Basic Preview Lifecycle Scripts 実装Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_basic_preview_lifecycle_scripts
phase: phase_1_ex
status: implementation_complete_review_pending
language: ja
created_at: 2026-07-26 20:12:08 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_basic_preview_lifecycle_scripts_20260726194949.md
related_status: implementer_status_phase_1_ex_lightning_auto_start_read_only_preflight_20260726201208.md
supersedes: null
```

## 1. Result

Lightning Basic認証PreviewのRepository側Lifecycleを、単一主入口へ統合した。

```text
scripts/runtime/lightning/basic_preview_service.sh
```

Lightning Managed Secrets、Hook、Port、URLおよびPlatform設定は変更していない。

## 2. Changed Files

```text
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/auto_start_preflight.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
```

`src/`、`config/`、`pyproject.toml`および`uv.lock`は変更していない。

## 3. Subcommands

```text
preflight       Read-only Project／Environment／Credential／Manual検査
run             Foreground margpa-web
start           Background起動＋Bounded Health Check
stop            Graceful Stop
stop --force    Graceful Timeout後だけ明示的SIGKILL
status          Running／Stopped／Stale／Unhealthy
restart         Stop＋Start
restart --force Explicit Force OptionをStopへ適用
--help          操作／設定／安全境界
```

## 4. Default／Override

次を環境変数で上書き可能にした。

```text
MARGPA_WORKSPACE_ROOT
MARGPA_PROJECT_ROOT
MARGPA_MODEL_ROOT
MARGPA_UV_BIN
MARGPA_ENV_PREFIX
MARGPA_WEB_HOST
MARGPA_WEB_PORT
MARGPA_WEB_PROFILE
MARGPA_RUNTIME_STATE_ROOT
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

DefaultはScript配置からProject Rootを解決し、Workspace／Model／`.venv`／Pure CPU Profile／Runtime Stateを相対関係から導出する。Lightning PathをApplication Coreへ追加していない。

Runtime State Rootは正規化し、Project Root内、Dot Segment、不正Pathまたは書込不能AncestorをFail Closedで拒否する。

## 5. Lifecycle Safety

- CredentialはEnvironmentから子Processへ継承し、Command Argumentへ渡さない。
- Credential値を標準出力、標準エラー、PID、LogまたはStatusへ書かない。
- Runtime State Directoryは`0700`、PID／Logは`0600`とする。
- 二重起動を拒否する。
- PIDだけでなく、Executable、ProfileおよびModel RootをProcess Command Lineと照合する。
- Linuxでは`/proc/<pid>/cmdline`、Fallbackでは`ps`を用いる。
- Stale PIDまたはIdentity不一致時に対象ProcessへSignalを送らない。
- Graceful Stopを既定とし、SIGKILLは`--force`指定時だけ許可する。
- Signal直前にProcess Identityを再照合する。
- Health CheckはLoopbackの`/healthz`だけを使用し、HTTP 200と`{"status":"ok"}`を要求する。
- Start時のHealth FailureはBounded Timeoutで失敗する。

## 6. Secret Non-exposure Verification

Test Credentialは実行時に動的生成し、固定値をRepositoryへ保存していない。

自動Testで次を確認した。

- Credential不足時のFail Closed
- Credential値がPreflight／Run／PID／Log／Statusへ出ない
- CredentialがCommand Argumentへ入らない
- 子Processへは値ではなくEnvironmentとして継承される

## 7. Verification

```text
Shell Syntax                         : PASS
New Lifecycle／Preflight Unit Test   : 9 passed
Stability Repeat                     : 9 passed × 3 consecutive runs
Related Lightning／Web Test          : 43 passed
Repository Full Suite                : 276 passed／3 deselected
Ruff Check                           : PASS
Ruff Format                          : PASS／96 files
Mypy Strict                          : PASS／96 source files
uv lock --check                      : PASS／122 packages
```

Unit TestはSpaceを含むPath、Path Override、二重起動、Stale PID、無関係Process保護、Graceful Stop、Restart、Health成功／失敗／Timeout、Shell SyntaxおよびRead-only Preflightを含む。

## 8. Lightning-side Remaining Work

ユーザーがLightning側で行う。

- Managed Secretsの作成／変更
- Username／Passwordの決定
- Lifecycle Scriptの配置確認
- API Builder／Public App／Port Viewer設定
- `on_start.sh`設定
- Basic Preview起動
- Public URL／`/healthz`
- Cold Start／Sleep／Wake／Restart
- Log／Secret／内部Path露出確認

## 9. Known Limitations

- Basic認証は共有Credentialであり、個別User識別には使えない。
- Credential変更後はProcess Restartが必要である。
- Linux Production Process Identityは`/proc`を前提とし、非Linux Fallbackは`ps`可用性に依存する。
- Health CheckはLocal Processの起動確認であり、Lightning Public URLの外部到達性を保証しない。
- Start Process Identityを確認できない場合はSignalを送らずFail Closedとし、PID Evidenceを保持する。
- 本実装はBasic Preview用であり、Public Demoまたは匿名Accessを有効化しない。

## 10. Review Gate

設計統括者役のReview Accepted前に、Lightning配置／実行、Secret／Hook／Port変更、Auto-start Go／No-Go、Public Demo、匿名Access、RAGまたはGitへ進まない。
