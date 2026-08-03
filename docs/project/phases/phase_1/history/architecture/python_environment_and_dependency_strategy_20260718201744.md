# Python実行環境・仮想環境・Dependency設計

- 文書ID: `python_environment_and_dependency_strategy`
- 状態: `current`
- 作成日時: `2026-07-18 20:17:44 JST`
- 更新日時: `2026-07-18 20:17:44 JST`
- 対象: Python、Virtual Environment、Package Manager、Dependency Group、Version固定
- 正本言語: 日本語
- 上位Architecture: [system_architecture_20260718193435.md](system_architecture_20260718193435.md)
- 関連Directory設計: [project_directory_structure_20260718192110.md](project_directory_structure_20260718192110.md)
- 関連ADR: [adr_0005_python_environment_and_dependency_management_20260718201744.md](../adr/adr_0005_python_environment_and_dependency_management_20260718201744.md)
- supersedes: なし（新規文書系列）

## 1. Decision Summary

初期Local Development Profileは、次を基準とする。

```text
Python          : CPython 3.13.14
Architecture    : ARM64
Interpreter     : 通常GIL Build
Python Fallback : CPython 3.12.13
Package Manager : uv 0.11.29
Virtual Env     : margpa-runtime-llm/.venv/
Install Policy  : Phase単位
Version Policy  : Exact Lock、無断自動Update禁止
Initial Groups  : core + inference-llama + dev + notebook
```

実験的なFree-threaded Buildは初期版で使用しない。

Python 3.11.9は動作可能性とPackage互換性が高いが、2026年から開始する新規Projectの正式な基準Versionにはしない。

## 2. Python Version

### 2.1 Primary

```text
CPython 3.13.14 / ARM64 / 通常GIL Build
```

Project MetadataのPython制約候補：

```toml
requires-python = ">=3.13,<3.14"
```

Project Rootへ将来作成する`.python-version`候補：

```text
3.13.14
```

`.python-version`は実行Interpreterを再現するためPatch Versionまで固定する。

### 2.2 Python 3.13を選ぶ理由

- 2026年7月時点でBugfix Support中である
- 公式Support終了予定が2029年10月である
- Python 3.12より公式Support期間を長く確保できる
- `llama-cpp-python`、PyTorch、Transformers、Jupyter等がPython 3.13をSupportしている
- Python 3.14よりApple Silicon向けNative Packageの互換性Riskが低い
- 新規Projectの基準として、互換性と残存Support期間の均衡がよい

### 2.3 Python 3.12 Fallback

Primary構成で`llama-cpp-python`のMetal Buildが成立しない場合のみ、次へFallbackする。

```text
CPython 3.12.13
```

Fallbackの検討条件：

- Python 3.13向け`llama-cpp-python` Source Buildが再現可能に成功しない
- Metal Backendを有効化できない
- ARM64とx86_64のArchitecture混在を解消できない
- Project Pathを原因とするNative Build問題を外部Venvで回避できない
- Build成功後も再現性または安定性に重大な問題がある

単にWarningがある、Buildに時間がかかる、Prebuilt Wheelがないという理由だけではFallbackしない。

### 2.4 Python 3.11.9の位置づけ

Python 3.11.9は、次の意味では現在も利用可能である。

- LLM／ML関連Packageとの互換性が広い
- `llama-cpp-python`のMetal Prebuilt Wheel対象に含まれる
- Jupyter、PyTorch、Transformers、LangChain系を利用可能である
- Localの短期Experimentには十分使用できる

一方、正式基準にしない理由は次である。

- Python 3.11系列の公式Support終了予定は2027年10月である
- 現在はSecurity Fix Onlyである
- `3.11.9`は最新Security Patchではなく、`3.11.15`に置換されている
- 将来FastAPIでNetwork公開する可能性があるProjectの新規基準としては残存期間が短い

例外的にPython 3.11系列を使用する必要が生じた場合は、`3.11.9`を正式固定せず、その時点の最新Security Patchを再確認する。

## 3. Virtual Environment

### 3.1 Primary配置

Virtual EnvironmentはProject Root直下へ作成する。

```text
margpa-runtime-llm/.venv/
```

論理構成：

```text
margpa-runtime-llm/
├─ .venv/             # Local Virtual Environment、Git管理外
├─ pyproject.toml      # Dependency宣言
├─ uv.lock             # 解決済みVersionのLock
└─ .python-version     # Python 3.13.14
```

`.venv/`はSource、Config、Runtime Data、Model、Docsのいずれでもない。再生成可能なLocal Development Environmentとして扱う。

### 3.2 Git方針

将来`.gitignore`を作成する際、少なくとも次をGit管理外とする。

```gitignore
.venv/
```

GitHubへ含めるもの：

- `pyproject.toml`
- `uv.lock`
- `.python-version`
- Setup手順
- Build前提条件

GitHubへ含めないもの：

- `.venv/`本体
- Install済みPackage本体
- Machine固有Cache
- Model File本体

### 3.3 External Venv Fallback

Project Rootの実体Pathは深く、日本語文字を含む。そのためNative Extension、Build Tool、Shebang等でPath由来の問題が発生する可能性がある。

Path問題が確認された場合のFallback候補：

```text
<USER_HOME>/.venvs/margpa-runtime-llm/
```

その場合もProject側からの論理入口を統一するため、次の形を候補とする。

```text
margpa-runtime-llm/.venv
  → <USER_HOME>/.venvs/margpa-runtime-llm/
```

External Venvへ移行するのは、実際にPath起因の問題を確認した後とする。最初からLocal固有PathをApplication ConfigやCore Logicへ埋め込まない。

## 4. Package Manager

### 4.1 採用

```text
uv 0.11.29
```

`uv`はProjectの`.venv`へ入れるRuntime Libraryではなく、Python、Virtual Environment、Dependency、Lockを扱うDevelopment Toolとして外側で管理する。

採用目的：

- Python Version管理
- `.venv`作成・同期
- `pyproject.toml`管理
- `uv.lock`による再現性
- Dependency Group
- Optional Dependency／Extra
- Platform条件
- Phase単位の追加と更新

### 4.2 Version固定

直接利用するTop-Level Dependencyは、初期検証時にVersionを明示する。

全Transitive Dependencyの正確なVersionは`uv.lock`で固定する。

```text
pyproject.toml : 意図したDirect Dependencyと利用条件
uv.lock        : 実際に解決・検証した全Dependency
```

`uv.lock`はGit管理対象とする。

### 4.3 Update Policy

- 無条件の一括Updateを行わない
- Phase開始時に、そのPhaseで追加するPackageだけを再確認する
- Native Backendは特にVersionを明示して固定する
- Update前後でUnit、Integration、Contract、Smoke Testを行う
- Model出力、Chat Template、Tokenization、Streaming挙動の変化を確認する
- Lock更新とSource変更を混同せず、変更理由を記録する
- Security UpdateもTestなしで即時一括反映しない
- ただし既知の重大Security問題は優先的に評価する

## 5. Dependency分類

Dependencyは、次の二種類に分ける。

### 5.1 Runtime Optional Dependencies

実行Capabilityを追加するPackageは、Optional Dependency／Extraとして分離する。

候補：

```text
inference-llama
api
governance
rag
agent
transformers
mlx
```

### 5.2 Local Dependency Groups

Application配布に不要な開発用PackageはDependency Groupへ分離する。

```text
dev
notebook
```

Jupyterはユーザーの研究・検証用途であり、Application Runtimeから依存しない。

## 6. Phase 1 Initial Dependencies

以下は`2026-07-18`時点の初期固定候補である。実際のInstall直前に公開状態、Security情報、Wheel／Build対応を再確認する。

### 6.1 Core Runtime

| Package | Version | Purpose | 初期導入 |
|---|---:|---|---|
| `pydantic` | `2.13.4` | DTO、Contract、Capability、設定値のValidation | Yes |
| `pydantic-settings` | `2.14.2` | Environment Variable、Path、Deployment Profile | Yes |
| `psutil` | `7.2.2` | Memory、CPU、Process、Runtime Metric | Yes |

Python標準Libraryを優先して使用する領域：

- `json`
- `hashlib`
- `logging`
- `pathlib`
- `asyncio`
- `dataclasses`
- `typing`
- `uuid`
- `datetime`
- `sqlite3`（将来検討時）
- `tomllib`（読取のみ）

標準Libraryで足りる領域へ、目的の重複するPackageを先に追加しない。

### 6.2 llama.cpp Backend

| Package | Version | Purpose | 初期導入 |
|---|---:|---|---|
| `llama-cpp-python` | `0.3.34` | GGUF Model、Streaming、Generation、Metal Backend | Yes |

対象Model：

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Python 3.13ではMetal Prebuilt Wheelに依存せず、Source Buildを前提とする。

Build候補設定の概念：

```text
GGML_METAL=on
```

実装時の事前条件：

- Apple Silicon／ARM64で実行している
- Xcode Command Line Toolsが利用可能である
- C／C++ Build Toolchainが利用可能である
- x86_64 PythonやRosetta環境を混在させない

Install成功判定は`import`成功だけにしない。次を確認する。

- Package Version
- Python Version／Architecture
- Metal Backend有効性
- Main Model Load
- 一問一答Generation
- Streaming
- Stop
- Load／Unload
- Peak Memory
- Token生成速度
- Process終了後のResource解放

### 6.3 Development Group

| Package | Version | Purpose | 初期導入 |
|---|---:|---|---|
| `pytest` | `9.1.1` | Test Runner | Yes |
| `pytest-asyncio` | `1.4.0` | Async／Streaming Test | Yes |
| `pytest-cov` | `7.1.0` | Coverage | Yes |
| `ruff` | `0.15.22` | Lint、Format、Import整理 | Yes |
| `mypy` | `2.3.0` | Static Type Check | Yes |

初期版では、役割が重複するため次を追加しない。

- Black
- Flake8
- isort

### 6.4 Notebook Group

| Package | Version | Purpose | 初期導入 |
|---|---:|---|---|
| `jupyterlab` | `4.6.1` | Main Notebook Environment | Yes |
| `notebook` | `7.6.0` | `jupyter notebook`形式のUI | Yes |
| `ipykernel` | `7.3.0` | Project EnvironmentのPython Kernel | Yes |

NotebookからProject Packageを呼び出す。Application RuntimeからNotebookをImportしない。

Notebookへ次を保存しない。

- Secret
- Credential
- 実会話Audit Logの無加工Copy
- 個人情報
- Model File本体
- 生のChain of Thought

## 7. Phase別追加候補

### 7.1 Phase 2: API／Web UI

| Package | 2026-07-18時点の暫定Version | Purpose | 今すぐ導入 |
|---|---:|---|---|
| `fastapi` | `0.139.2` | Application API | No |
| `uvicorn[standard]` | `0.51.0` | ASGI Server、WebSocket、Development Reload | No |
| `httpx` | `0.28.1` | API／ASGI Test、HTTP Client | No |

UI方式が未確定の間、StreamlitとFastAPI系を両方Installしない。

FastAPI＋Vanilla JavaScriptを採用した場合、Frontendの大規模なPython Frameworkは不要である。

### 7.2 Phase 3: Governance／Audit

| Package | 2026-07-18時点の暫定Version | Purpose | 今すぐ導入 |
|---|---:|---|---|
| `jsonschema` | `4.26.0` | ARGD／DAGD、Audit、Config Schema Validation | No |

SHA-512はPython標準Libraryの`hashlib`を使用する。

JSON Canonicalization方式は未決定である。RFC 8785／JCS対応Package等を先にInstallせず、Canonicalization仕様を確定してから選ぶ。

### 7.3 Phase 4: Guard／Judge

初期のMain、Guard、JudgeはすべてGGUFであり、同じ`llama-cpp-python` Backendを利用できる。

```text
Main Model  ─┐
Guard Model ─┼─ llama-cpp-python Adapter
Judge Model ─┘
```

そのためPhase 4で推論Libraryを必ず追加する必要はない。

16GB Memory制約のため、複数Modelの同時常駐は前提にしない。必要時Load／Unloadまたは別Process化を検討する。

Qwen3GuardまたはSeleneの非GGUF版が必要になった場合のみ、`transformers` Groupを有効化する。

### 7.4 Phase 5: RAG

現在の候補：

| Package | 2026-07-18時点の参考Version | Status |
|---|---:|---|
| `langchain` | `1.3.14` | Candidate |
| `sentence-transformers` | `5.6.0` | Candidate |
| `transformers` | `5.14.1` | Candidate |
| `torch` | `2.13.0` | Candidate |
| Vector Store | 未決定 | Undecided |

Embedding Model、Vector Store、Document形式、Index更新方式を確定してから必要なPackageだけを固定する。

### 7.5 Phase 6: Agent

| Package | 2026-07-18時点の参考Version | Status |
|---|---:|---|
| `langgraph` | `1.2.9` | Candidate |

LangGraphはPhase 6開始時に必要性と代替を再評価する。

### 7.6 Optional MLX Backend

| Package | 2026-07-18時点の参考Version | Status |
|---|---:|---|
| `mlx` | `0.32.0` | Candidate |
| `mlx-lm` | `0.31.3` | Candidate |

GGUFのみを使用するPhase 1では導入しない。

MLX Model形式を採用し、`adapters/model_backends/mlx/`を実装する段階で追加する。

### 7.7 Cloud Backend

vLLM、CUDA、Cloud SDK等はMac用`.venv`へ入れない。

Cloud Deployment Profileは、Local Profileと同じApplication Coreを使いつつ、OS、GPU、Backend、Dependencyが異なる別Environmentとして管理する。

## 8. Install Timing

先に将来PackageをすべてInstallする方式は採用しない。

初期Install対象：

```text
core
inference-llama
dev
notebook
```

追加時期：

```text
Phase 2 → api
Phase 3 → governance
Phase 5 → rag
Phase 6 → agent
必要時  → transformers / mlx
Cloud   → Localとは別Environment
```

Phase単位とする理由：

- 未使用Packageが使用前に古くなることを防ぐ
- Dependency競合範囲を限定する
- Disk使用量を抑える
- Install／Build失敗の原因を限定する
- Runtime Attack Surfaceを抑える
- Package追加による挙動変化を追跡しやすくする
- GGUF推論に不要なPyTorch／Transformersを初期導入しない

## 9. Versionの意味

この文書のVersion表は、次の二種類を区別する。

```text
Initial Fixed Candidate:
  Phase 1開始時に検証し、問題なければLockするVersion

Reference Version:
  将来候補の2026-07-18時点の情報であり、今はLockしないVersion
```

将来Phaseの参考Versionは、そのPhase開始時に最新Compatibility、License、Security、Apple Silicon対応を再調査する。

## 10. Implementation Acceptance Criteria

実装担当はDependency Setup完了を、次で判定する。

- Pythonが`3.13.14`である
- ARM64通常GIL Buildである
- `.venv/`がProject Environmentとして機能する
- `.venv/`がGit管理外である
- `uv`のVersionが記録される
- `uv.lock`からEnvironmentを再現できる
- 初期Direct DependencyのVersionが意図どおりである
- `llama-cpp-python`でMetalを利用できる
- Qwen3-4B GGUFをLoadできる
- 最小Generation、Streaming、Stopが動作する
- Test、Ruff、mypyが実行可能である
- JupyterからProject PackageをImportできる
- Runtime環境がJupyterへ依存していない
- 未使用のRAG、Agent、Transformers、MLX Packageが入っていない

## 11. 実装前の禁止事項

ユーザーから実装解禁を受けるまで、次を行わない。

- Python Install
- `.venv/`作成
- `uv` Install
- Package Install
- `pyproject.toml`作成・変更
- `uv.lock`作成・変更
- `.python-version`作成
- `.gitignore`変更
- Native Build
- Model Load Test

この文書は設計判断であり、実装開始の許可ではない。

## 12. External References

- Python Support Status: <https://devguide.python.org/versions/>
- Python 3.13.14: <https://www.python.org/downloads/release/python-31314/>
- Python 3.11.9: <https://www.python.org/downloads/release/python-3119/>
- uv: <https://pypi.org/project/uv/>
- uv Dependency Management: <https://docs.astral.sh/uv/concepts/projects/dependencies/>
- llama-cpp-python: <https://pypi.org/project/llama-cpp-python/>
- JupyterLab: <https://pypi.org/project/jupyterlab/>
- Jupyter Notebook: <https://pypi.org/project/notebook/>
- MLX: <https://pypi.org/project/mlx/>
- PyTorch: <https://pypi.org/project/torch/>
- Transformers: <https://pypi.org/project/transformers/>

