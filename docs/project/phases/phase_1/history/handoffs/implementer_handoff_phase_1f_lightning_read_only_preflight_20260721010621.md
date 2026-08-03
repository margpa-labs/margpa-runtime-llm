# 実装担当向け Phase 1-F Lightning Read-only Preflight Handoff

- 文書ID: `implementer_handoff_phase_1f_lightning_read_only_preflight`
- 状態: `accepted_ready_for_external_preflight`
- 作成日時: `2026-07-21 01:06:21 JST`
- 更新日時: `2026-07-21 01:06:21 JST`
- Snapshot: `20260721010621`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- Repository Accepted Review: [designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md](designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md)
- 最新Index: [documentation_index_20260721010621.md](../documentation_index_20260721010621.md)
- supersedes: なし（Lightning Read-only Preflight専用Handoffの初回）

## 1. Objective

Project本体、Model Artifact、Mac `.venv`をLightningへ搬入する前に、小型のPreflight Scriptだけを対象Lightning AI Studioで実行する。

次をRead-onlyに確認し、Full UploadとDependency Syncへ進める前提を確定する。

```text
Host OS               : Linux
Architecture          : x86_64
Distribution          : Ubuntu
Execution Environment : Container
Environment Mode      : studio-active または project-venv
Python                : 3.12.11
uv                    : 0.11.29
GPU Mandatory Path    : NVIDIA GPU割当をnvidia-smiで確認
nvcc                  : 有無のみ参考記録
```

## 2. Authorized External Action

Lightning Targetへ配置してよいProject Fileは、次の1ファイルだけである。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

次を許可する。

- 上記Script 1ファイルのLightning Targetへの配置
- Scriptの`--help`実行
- GPU用Read-only Preflight実行
- CPU候補用Read-only Preflight実行
- Command、Exit Code、標準出力、Safeな標準エラーの記録
- Local Repository側でのImplementer Status新規作成

## 3. Prohibited Actions

Preflight中は次を行わない。

- Project本体のFull Upload
- GGUF ModelのUpload／Download／Copy
- `.venv`のUpload／Copy／作成
- `uv sync`
- `pip install`
- Package Upgrade／Downgrade
- `llama-cpp-python`のBuild／Rebuild
- `nvcc`によるCompile
- Config／Source／Test／Scriptの変更
- Lightning Environment／GPU設定の変更
- Credential、Token、Cookie、Secretの表示または記録
- Git／GitHub操作

Preflightが失敗した場合も、その場で環境を修復しない。Failure Evidenceを保存して設計者Reviewへ戻す。

## 4. Transfer Boundary

Local MacのProject Tree全体をまだUploadしない。Preflight Script 1ファイルだけを、Lightning側の任意の作業Directoryまたは既存Project Treeの同一相対Pathへ配置する。

Mac `.venv`、`models` Symbolic Link、GGUF本体、Cache、Log、Credentialを一緒に転送しない。

Scriptは`bash`で直接実行できるため、Executable Bit変更は必須ではない。

## 5. Execution Procedure

### 5.1 Help確認

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --help
```

期待：

- Exit Code 0
- `auto`、`studio-active`、`project-venv`が表示される。
- `--cpu-only`が表示される。
- Environment作成、Package Install、`nvcc`要求を行わない旨が表示される。

### 5.2 GPU Mandatory Preflight

Tesla T4等のNVIDIA GPUがLightning Studioへ割り当てられている状態で実行する。

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto
```

合格条件：

- Exit Code 0
- `Phase 1-F Lightning preflight passed.`
- `Environment mode`が`studio-active`または`project-venv`
- Python 3.12.11
- uv 0.11.29
- `GPU required : 1`
- `nvidia-smi -L`によりAllocated NVIDIA GPUを確認できる。
- `nvcc available`は`yes／no`のどちらでもPreflight合格可

`nvcc`は後続のNative Rebuild要否を決める参考値であり、本Preflightでは必須にしない。

### 5.3 CPU Candidate Preflight

GPU割当がない場合、またはCPU候補の環境前提だけを確認する場合に実行する。

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto \
  --cpu-only
```

合格条件：

- Exit Code 0
- GPU割当や`nvidia-smi`を必須としない。
- Host／Container／Python／uv／Environment Mode条件がGPU Pathと同様に成立する。
- `GPU required : 0`

この合格は、GPUのない環境でllama.cpp Import／Model Load／Generateが成立した証明ではない。CPU Native GateはFull Upload後に別途実行する。

GPU割当中のStudioで`--cpu-only`を実行しても、GPU不在を証明したことにはならない。GPU Requirementを外したEnvironment Candidate確認としてのみ記録する。

## 6. Environment Mode Interpretation

```text
auto
  ├─ VIRTUAL_ENV／CONDA_PREFIXあり
  │    → studio-active
  └─ Active Prefixなし
       → project-venv
```

- `studio-active`の場合、Active Prefix配下の`bin/python`が3.12.11であることを確認する。
- `project-venv`の場合、本PreflightではVenvを作成せず、現在の`python3`が3.12.11であることだけを確認する。
- Auto Resolution結果をStatusへ記録し、後続Full Setupでは確定したModeを明示する。

## 7. Failure Handling

次のいずれかが発生した場合はPreflight不合格とする。

- Linux／x86_64／Ubuntu／Containerの不一致
- Pythonが3.12.11ではない。
- uvが存在しない、または0.11.29ではない。
- `studio-active`選択時にActive Prefixまたは`bin/python`がない。
- GPU Mandatory Pathで`nvidia-smi`またはAllocated GPUを確認できない。
- Scriptが非0で終了する。

不合格時は次を守る。

1. Exit CodeとSafeなError Messageを記録する。
2. Package Install、Version変更、Environment作成を行わない。
3. Model／Project Full Uploadへ進まない。
4. Failure原因と候補Follow-upをStatusへ記録する。
5. 設計者Reviewとユーザー判断へ戻す。

## 8. Evidence／Status Requirement

Preflight完了後、Local Repositoryへ新Timestampで次を作成する。

```text
docs/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_YYYYMMDDHHMMSS.md
```

最低限、次を含める。

```text
Execution Date／Timezone
Lightning Environmentの一般的な識別名
GPU割当有無
GPU Name／Memory（取得できる場合）
Host OS／Architecture／Distribution／Container
Selected Environment Mode
Active Prefixの有無
Python Pathの種別／Version
uv Pathの種別／Version
nvcc Available yes／no
GPU Preflight Command／Exit Code／Output
CPU Candidate Command／Exit Code／Output
Pass／Fail／Not Runの区別
Failure時の未変更確認
Full Uploadへ進めるかの実装担当自己評価
```

公開やTask引き継ぎに不要な次の情報は記録しないか匿名化する。

- Credential／Token／Cookie／Secret
- LightningのPrivate Access URL
- Session ID
- Machine ID／Boot ID
- 個人名を含むPath
- 不要なIP Address／Hostname

実行していない項目をPass扱いしない。

## 9. Review Gate

Preflight Status作成後、設計者役へReviewを依頼する。

設計者ReviewがAcceptedになるまで、次へ進まない。

```text
Project Full Upload
Model Upload
Dependency Sync
Native Build／Reuse
CUDA／CPU Acceptance
```

## 10. Start Condition

本HandoffはAcceptedであり、ユーザーの本Turnにおける「次はLightning Read-only Preflightへ進めます。よろしく。」を開始指示として扱う。

実装担当は本Handoff、最新Index、Repository Accepted Reviewを読んだ後、Section 2の範囲でPreflightへ着手できる。
