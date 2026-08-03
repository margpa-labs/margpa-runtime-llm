# Phase 1-ex Lightning Auto-start Read-only Preflight 実装Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_auto_start_read_only_preflight
phase: phase_1_ex
status: implementation_complete_review_pending
language: ja
created_at: 2026-07-26 20:12:08 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_auto_start_read_only_preflight_20260726192912.md
supersedes: null
```

## 1. Result

Project側Read-only Preflightと、Platform側Manual Checklistの機械可読出力を実装した。

本実装からLightning外部状態、Platform設定、Public Access、Dependency、Model、ProcessおよびGit状態を変更していない。

## 2. Changed Files

```text
scripts/runtime/lightning/auto_start_preflight.sh
scripts/runtime/lightning/basic_preview_common.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
```

Lifecycle Handoffと共通する検査Contractは`basic_preview_common.sh`へ集約した。Auto-start Preflight入口はRead-only検査とManual Checklist出力だけを呼び出す。

## 3. Automated Project Checks

```text
Host Candidate            : Linux／x86_64／Container
Distribution              : Ubuntu
Project Root              : Readable／Configurable
Model Root                : Present／Configurable
Project Environment       : Python 3.12または3.13
Project-local uv          : 0.11.29／Configurable Path
margpa-web                : Executable
Pure CPU Profile          : Contract Valid
Model Registry／Artifact  : Relative Layout Valid／Artifact Present
/healthz                  : HTTP 200／{"status":"ok"} Contract Present
Web Bind                  : Host／Port Explicit
Access Boundary           : basic_preview／public_demo=false
Credential Launch Contract: Environment Only
Runtime State Root        : Project Root外／Writable Ancestor
Health Client             : curl Present
```

Python Probeは`PYTHONDONTWRITEBYTECODE=1`で実行する。PreflightはRuntime State Directoryを作成せず、`curl`による通信、Server起動、Package Install、BuildまたはPlatform操作を行わない。

## 4. Manual Checklist

次を自動Passにせず、`not_run`または`manual_required`として出力する。

- API Builder可用性
- Traffic-aware Auto-start可用性
- Machine／Credit条件
- Public URL発行
- Sleeping Studio Wake-up
- Startup Command実行
- Model Load／Artifact Hash
- `/healthz`外部到達
- Cold Start時間
- Idle Sleep／Wake
- Restart後URL維持
- Log／Secret／内部Path露出

出力Status Vocabulary：

```text
pass
fail
not_run
manual_required
unknown
```

## 5. Verification

```text
Shell Syntax                         : PASS
New Lifecycle／Preflight Unit Test   : 9 passed
Related Lightning／Web Test          : 43 passed
Repository Full Suite                : 276 passed／3 deselected
Ruff Check                           : PASS
Ruff Format                          : PASS／96 files
Mypy Strict                          : PASS／96 source files
uv lock --check                      : PASS／122 packages
```

通常SuiteではModel Smokeを実行していない。`deselected`をPassとして扱わない。

## 6. Not Run

- Lightning Account／Studio上の機能確認
- API Builder／Public App／Port設定
- Traffic-aware Wake-up
- Public URL
- Cold Start／Sleep／Restart
- Model Load／SHA-512再計算
- Lightning外部Runtime Test

## 7. Known Limitations

- 本StatusはProject側Preflight実装完了候補であり、Auto-start Go／No-Goではない。
- Account、Credit、URL、Sleep／Wakeおよび外部到達性はRepository単独では判定できない。
- Model Artifactの存在とRegistry Layoutは自動確認するが、実Model LoadとSHA-512はManual項目として保持する。
- Public Demo、匿名Access、RAG、GitおよびPlatform変更は未実装・未実行である。

## 8. Review Gate

設計統括者役のReview Accepted前に、Lightning Platform操作、Auto-start Go／No-Go、Public Demo、匿名Access、RAGまたはGitへ進まない。
