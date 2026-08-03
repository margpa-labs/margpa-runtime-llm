# ADR-0005 Python実行環境とDependency管理

- 文書ID: `adr_0005_python_environment_and_dependency_management`
- 状態: `accepted`
- 作成日時: `2026-07-18 20:17:44 JST`
- 更新日時: `2026-07-18 20:17:44 JST`
- 対象: 全担当Task
- 正本言語: 日本語
- Decision Owner: 設計者役担当Task、ユーザー承認済み
- 関連Architecture: [python_environment_and_dependency_strategy_20260718201744.md](../architecture/python_environment_and_dependency_strategy_20260718201744.md)
- supersedes: なし（新規ADR）

## Context

MARGPA Runtime LLMは、Apple M2 Pro／16GB／ARM64のMacBook Proで初期開発・実行する。

初期ModelはGGUFであり、Local Backendとして`llama-cpp-python`／Metalを有力候補とする。

将来は次を追加・交換する可能性がある。

- FastAPI
- Jupyter
- Governance／Audit
- Guard Model
- LLM-as-a-Judge
- RAG
- LangChain
- LangGraph
- Transformers／PyTorch
- MLX
- Cloud／vLLM

そのためPython Version、Virtual Environment、Dependencyの追加時期、Lock方式を先に定める必要がある。

## Decision

### Python

Primary：

```text
CPython 3.13.14 / ARM64 / 通常GIL Build
```

Fallback：

```text
CPython 3.12.13
```

Python 3.13で`llama-cpp-python`のMetal Source Buildが再現可能に成立しない場合のみ、3.12へFallbackする。

Python 3.11.9は正式基準にしない。

### Virtual Environment

Primary：

```text
margpa-runtime-llm/.venv/
```

Path起因のNative Build問題が確認された場合：

```text
<USER_HOME>/.venvs/margpa-runtime-llm/
```

Project側の`.venv`からExternal VenvへのPOSIX Symbolic Linkを候補とする。

### Package Manager

```text
uv 0.11.29
```

Dependencyは`pyproject.toml`で宣言し、解決済みVersionを`uv.lock`で固定する。

### Install Policy

将来使用する可能性があるPackageを先に全部Installしない。

Phase単位で必要なDependency Groupだけを追加する。

初期対象：

```text
core + inference-llama + dev + notebook
```

## Reasons

### Python 3.13をPrimaryとする理由

- Python 3.11より長い公式Support期間を確保できる
- Python 3.12よりBugfix Support期間とEOLが長い
- Python 3.14よりLLM／Native Package互換性を保守的に扱える
- 主要候補PackageがPython 3.13をSupportしている
- 2026年開始の新規Projectに適した寿命がある

### Python 3.11.9を正式基準にしない理由

- Python 3.11系列はSecurity Fix Onlyである
- 公式Support終了予定が2027年10月である
- 3.11.9は最新Security Patchではない
- 将来Network公開する可能性がある新規Projectの基準として残存期間が短い

Python 3.11.9が「動かない」または「使用禁止」という意味ではない。Localの短期ExperimentやEmergency Fallbackとしては利用可能である。

### Phase単位Installとする理由

- GGUF推論にPyTorch／Transformersは不要である
- 未使用PackageのVersion競合を避けられる
- 問題発生時の原因範囲を小さくできる
- RAG／Agent実装時点のCompatibilityを改めて評価できる
- Install済みPackageとAttack Surfaceを最小化できる
- Modular ArchitectureのOptional Capabilityと対応づけられる

## Alternatives Considered

### Python 3.11.9

長所：

- 非常に広いPackage互換性
- Metal Prebuilt Wheelの利用が容易
- 既存ML Toolとの相性がよい

不採用理由：

- 新規Projectの正式基準としてSupport残存期間が短い
- 最新Security Patchではない

### Python 3.12.13

長所：

- Python 3.13よりPrebuilt Wheel対応が広い可能性がある
- ML Package互換性が成熟している

Primaryにしない理由：

- すでにSecurity Fix Onlyである
- Python 3.13よりEOLが早い

Fallbackとして保持する。

### Python 3.14

長所：

- 最も長いSupport期間
- 新しいPython機能

不採用理由：

- Native ExtensionとML Ecosystemの追随Riskを増やす
- MVPの目的に新機能が必要ない

### 将来Packageの一括Install

不採用理由：

- 未使用の大規模Dependencyが増える
- Phase開始前にVersionが古くなる
- 競合とBuild問題の切り分けが難しくなる

## Consequences

### Positive

- Python環境の再現性が高くなる
- Local／Cloud Dependencyを分離しやすい
- Phase単位で影響範囲を制御できる
- Model BackendをOptional Capabilityとして扱える
- 開発担当がInstall対象を判断しやすい

### Negative／Risk

- Python 3.13では`llama-cpp-python` Metal版のSource Buildが必要になる可能性が高い
- Xcode Command Line Tools等のNative Build前提が増える
- 深い日本語PathがBuild Toolへ影響する可能性がある
- 将来Package追加時に都度Compatibility確認が必要になる

## Implementation Constraint

このADRはEnvironment作成やInstallの許可ではない。

ユーザーから実装解禁を受けるまで、Python、Venv、Package、Build、Lock Fileを変更しない。

