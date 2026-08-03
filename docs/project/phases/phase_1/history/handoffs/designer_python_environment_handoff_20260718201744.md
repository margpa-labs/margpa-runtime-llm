# Python環境設計から実装担当への引き継ぎ

- 文書ID: `designer_python_environment_handoff`
- 状態: `waiting_for_implementation_unlock`
- 作成日時: `2026-07-18 20:17:44 JST`
- 更新日時: `2026-07-18 20:17:44 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Architecture正本: [python_environment_and_dependency_strategy_20260718201744.md](../architecture/python_environment_and_dependency_strategy_20260718201744.md)
- ADR: [adr_0005_python_environment_and_dependency_management_20260718201744.md](../adr/adr_0005_python_environment_and_dependency_management_20260718201744.md)
- 共通実装引き継ぎ: [implementer_handoff_20260718193435.md](implementer_handoff_20260718193435.md)
- supersedes: なし（新規Handoff系列）

## 1. 最重要指示

現在は要件定義・技術選定・Architecture設計Phaseである。

このHandoffは、実装開始後に使用するEnvironment仕様を伝えるものであり、実装解禁ではない。

ユーザーから明示的な実装解禁を受けるまで、次を行わない。

- Python Install
- `.venv/`作成
- `uv` Install
- Package Install
- `pyproject.toml`作成・変更
- `uv.lock`作成・変更
- `.python-version`作成
- `.gitignore`変更
- `llama-cpp-python` Build
- Model Load Test

## 2. 確定したEnvironment基準

```text
Python          : CPython 3.13.14
Python Build    : ARM64／通常GIL
Python Fallback : CPython 3.12.13
Package Manager : uv 0.11.29
Virtual Env     : margpa-runtime-llm/.venv/
Install Policy  : Phase単位
Lock Policy     : uv.lockでExact Lock
```

Python 3.11.9は正式基準にしない。

## 3. Venv配置

Primary：

```text
margpa-runtime-llm/.venv/
```

`.venv/`はGit管理外とする。

深い日本語Pathを原因とするNative Build、Shebang、Toolchain問題が確認された場合のFallback：

```text
<USER_HOME>/.venvs/margpa-runtime-llm/
```

必要な場合のみ、Project Rootの`.venv`をExternal VenvへのPOSIX Symbolic Linkとする。

## 4. Phase 1で導入するDirect Dependency

### Core

```text
pydantic==2.13.4
pydantic-settings==2.14.2
psutil==7.2.2
```

### llama.cpp Backend

```text
llama-cpp-python==0.3.34
```

### Development

```text
pytest==9.1.1
pytest-asyncio==1.4.0
pytest-cov==7.1.0
ruff==0.15.22
mypy==2.3.0
```

### Notebook

```text
jupyterlab==4.6.1
notebook==7.6.0
ipykernel==7.3.0
```

実際のInstall直前に、同一Versionの公開状態、Security情報、Python 3.13対応、ARM64対応を再確認する。再確認なしにVersionを勝手に最新へ変更しない。

## 5. Dependency Group方針

初期有効化：

```text
core
inference-llama
dev
notebook
```

後続：

```text
Phase 2 : api
Phase 3 : governance
Phase 5 : rag
Phase 6 : agent
Optional: transformers
Optional: mlx
Cloud   : Localとは別Environment
```

将来利用しそうなPackageを最初に全部Installしない。

## 6. 後続Phaseの参考Version

以下は`2026-07-18`時点の参考であり、今はLockしない。

```text
Phase 2:
  fastapi==0.139.2
  uvicorn[standard]==0.51.0
  httpx==0.28.1

Phase 3:
  jsonschema==4.26.0

Phase 5 Candidate:
  langchain==1.3.14
  sentence-transformers==5.6.0
  transformers==5.14.1
  torch==2.13.0
  Vector Storeは未決定

Phase 6 Candidate:
  langgraph==1.2.9

Optional MLX Candidate:
  mlx==0.32.0
  mlx-lm==0.31.3
```

Guard／Judgeの初期GGUF構成は`llama-cpp-python`を共用するため、Phase 4で別の推論Libraryを追加することは必須ではない。

## 7. Python Fallback判定

Python 3.13から3.12へ落とす前に、次を順に確認する。

1. PythonがARM64通常GIL Buildか
2. Rosetta／x86_64 Toolが混入していないか
3. Xcode Command Line Toolsが利用可能か
4. Metal Build設定が正しいか
5. Projectの深い日本語Pathが原因でないか
6. External Venvで再現するか
7. CleanなEnvironmentとLock条件で再現するか

これらを確認してもMetal Buildが再現可能に成立しない場合のみ、Python 3.12.13を検討する。

Fallbackを行う場合は、設計者とユーザーへ次を報告する。

- Error内容
- 再現手順
- Python、OS、Architecture
- Xcode／Compiler情報
- 試したBuild条件
- External Venvでの結果
- 3.12へ落とす理由
- 影響範囲

## 8. Phase 1 Setup Acceptance Criteria

Environment Setup完了報告には、少なくとも次を含める。

- Python Version／Architecture／GIL種別
- Venv実体PathとProject側の見え方
- `uv` Version
- Direct Dependency Version一覧
- `uv.lock`再現確認
- Metal Backend有効性
- Qwen3-4B GGUF Load結果
- Minimal Generation結果
- Streaming／Stop結果
- Model Load／Unload結果
- Peak Memory
- Token生成速度
- Test結果
- Ruff結果
- mypy結果
- Jupyter KernelからのProject Import結果
- FallbackやDeviationの有無

## 9. 実装境界

- Backend固有のBuild／Import／Chat Template処理は`adapters/model_backends/llama_cpp/`へ閉じ込める
- Coreから`llama_cpp`を直接Importしない
- User固有のAbsolute PathをCoreへ入れない
- Venv PathをApplication Domainへ露出しない
- NotebookをApplication Runtime Dependencyにしない
- Jupyter上だけで成立するLogicを正本実装にしない
- `uv.lock`を無断で一括Updateしない
- Install済みTransitive DependencyをDirect Dependencyとして無目的に列挙しない
- RAG、Agent、Transformers、MLXをPhase 1へ前倒ししない

## 10. 読む順序

1. [documentation_index_20260718201744.md](../documentation_index_20260718201744.md)
2. [documentation_rules_20260718193435.md](../requirements/documentation_rules_20260718193435.md)
3. [implementer_handoff_20260718193435.md](implementer_handoff_20260718193435.md)
4. [python_environment_and_dependency_strategy_20260718201744.md](../architecture/python_environment_and_dependency_strategy_20260718201744.md)
5. [adr_0005_python_environment_and_dependency_management_20260718201744.md](../adr/adr_0005_python_environment_and_dependency_management_20260718201744.md)
6. [project_directory_structure_20260718192110.md](../architecture/project_directory_structure_20260718192110.md)

