# MARGPA Runtime LLM 技術選定書

```yaml
document_id: technology_selection
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 10:01:20 JST
owner: Nazuna Research
active_phase: phase_1_ex
rag_default: true
```

## 1. 選定方針

- 現在のMacで動作すること
- 長期安定性と再現性
- Local／Server／Cloud間の交換性
- Framework固有依存の局所化
- 小型Modelでも全機能の骨格を検証できること

## 2. 採用済み

| 分類 | 技術／Version | 用途 |
|---|---|---|
| Language | Python `>=3.12,<3.14` | Application／Runtime |
| Local Default | CPython 3.13.14 | macOS開発 |
| Lightning | CPython 3.12.11 | Linux Pure CPU実証 |
| Package Manager | uv 0.11.29 | Lock／Environment／Build |
| Validation | Pydantic 2.13.4 | Typed Config／Contract |
| Settings | pydantic-settings 2.14.2 | Environment設定 |
| System Info | psutil 7.2.2 | Runtime Observation |
| Inference | llama-cpp-python 0.3.34 | GGUF／Metal／CPU |
| Web API | FastAPI 0.139.2 | Minimal Web Boundary |
| ASGI | Uvicorn 0.51.0 | Web Runtime |
| Test | pytest 9.1.1 | Unit／Integration |
| Async Test | pytest-asyncio 1.4.0 | Async Boundary |
| Coverage | pytest-cov 7.1.0 | Test計測 |
| Type Check | mypy 2.3.0 | Strict Type Check |
| Lint／Format | Ruff 0.15.22 | Static Quality |
| Notebook | JupyterLab 4.6.1等 | User研究環境 |

Version正本はProject Rootの`pyproject.toml`と`uv.lock`である。

## 3. Model

### Main

```text
Repository   : Qwen/Qwen3-4B-GGUF
Upstream     : Qwen/Qwen3-4B
Artifact     : Qwen3-4B-Q4_K_M.gguf
Quantization : Q4_K_M
Backend      : llama.cpp
```

M2 Pro／16GBでRuntime全体を構築するBalanced候補として採用した。Model性能より交換可能な骨格成立を優先する。

### Guard候補

```text
Qwen3Guard-Gen-0.6B
GGUF Q8_0または通常版
```

### Judge候補

```text
AtlaAI/Selene-1-Mini-Llama-3.1-8B
GGUF Q5_K_Mまたは通常版
```

Guard／Judgeは未統合であり、通常版Transformers Artifactは必要性が生じた時点で再評価する。

## 4. UI／API

Phase 1ではFastAPIとRepository内の軽量Web Assetを採用した。理由：

- ApplicationとUIの境界が明確
- Streaming／Cancel／Health Checkを直接制御可能
- React等への交換余地を維持
- Lightning Port公開に適合

Streamlitは短期試作候補だったが、長期的なBoundary、State、Cancel、Access Controlを優先し不採用とした。React／Next.jsはPhase 4以降のUI再評価候補である。

## 5. Storage

Current：

- Browser Memoryの一時Conversation
- Config TOML
- Model Registry TOML
- Documentation Markdown／JSON

Future：

- Audit原本：JSON／JSONL Append-only
- Index／検索：SQLite候補
- Cloud：PostgreSQL／Object Storage候補

SQLを初期必須にしない。

## 6. Deployment

| Profile | Backend | Acceleration | 状態 |
|---|---|---|---|
| macOS ARM64 | llama.cpp | Metal | 実機Accepted |
| Lightning Linux x86_64 | llama.cpp | Pure CPU | 実機Accepted |
| Linux NVIDIA | llama.cpp／将来vLLM | CUDA | Hook／一部Profile |
| Windows | llama.cpp | CPU／CUDA等 | Hook |
| Cloud／Hybrid | vLLM／Remote API | GPU Server | 将来 |

DockerはLocal Metal初期開発では不採用。LightningはPlatform側Containerを利用するが、Application CoreはContainer前提にしない。

## 7. 保留技術

- MLX／mlx-lm
- Transformers／PyTorch
- vLLM
- LangChain／LangGraph
- Vector Store
- SQLite／PostgreSQL
- React／Next.js
- Docker
- AWS／Azure

機能Phaseと必要性を確認して導入する。将来候補であることを理由に先行Installしない。

## 8. 再評価条件

- M2 Pro／16GBでMemoryまたはLatencyが許容不能
- Home Server／CUDA GPU導入
- Tool CallingまたはStructured Output Capabilityが必要
- Guard／Judgeの通常版Modelが必要
- Multi-user／永続Conversation／検索が必要
- Public DemoのCost／Auto-start要件が変化
- UIのMobile／Accessibility／大規模State管理が必要

## 9. Traceability

- [System Architecture](system_architecture_ja.md)
- [Phase 1 Architecture Compilation](../../phases/phase_1/architecture/phase_1_architecture_ja.md)
- [Phase 1 ADR Compilation](../../phases/phase_1/adr/phase_1_adr_ja.md)

## 10. Python／Environment選定

### 10.1 Version Range

```text
Project Support Range : >=3.12,<3.14
Local Default         : CPython 3.13.14
Lightning Verified    : CPython 3.12.11
Fallback              : Python 3.12系
```

Python 3.13.14をLocal本命とし、`llama-cpp-python` Metal Buildまたは将来Dependencyで問題が生じた場合だけ3.12へFallbackする方針で開始した。Phase 1ではPython 3.13.14でMetal Build、CLI、Web、Testが成立し、Lightningでは既存環境との適合を優先して3.12.11を採用した。

Python 3.11.9は動作不能と断定しないが、本ProjectのSupport Rangeから除外する。新規機能は3.12／3.13 Contractで検証する。

### 10.2 Virtual Environment

- Project Root直下の`.venv/`を使用する。
- `.venv/`はGit、Backup Source Archiveおよび公開Uploadへ含めない。
- Lightning既定Conda PrefixをProject Environmentとして再利用しない。
- Native Backend BuildはTarget Environmentごとに明示的に再構築する。
- Environment同期とNative Backend再Buildを将来分離する。

通常Setup Recipeが毎回`--reinstall-package llama-cpp-python`を使用する場合、Native Packageを毎回再Buildするため重い。再現性重視としては妥当だが、日常同期用Commandと明示Native Rebuild用Commandを分離する候補を維持する。

## 11. Package Management選定

### 11.1 uv

`uv 0.11.29`を採用する。

- Python Environment作成
- Lock
- Dependency Sync
- Build Backend
- Reproducible Setup

Lightning標準の`uv 0.11.18`はProject Pinと一致しないため使用せず、Project Workspace配下の固定Tool Pathへ`0.11.29`を配置してPATH先頭に追加する。

### 11.2 Install Strategy

Phaseごとに必要なDependencyだけを追加する。

理由：

- M2 Pro／16GBで不要なRuntime負荷を避ける。
- Dependency Conflictの原因範囲を限定する。
- 未実装FrameworkをArchitecture前提にしない。
- Lock差分と導入理由をPhase単位で追跡する。

LangChain、LangGraph、Transformers、Torch、MLX等を将来使用する可能性があっても、必要Phase前に一括導入しない。

## 12. Inference Backend選定

### 12.1 llama.cpp／llama-cpp-python

初期Backendとして採用した理由：

- GGUF Artifactを直接扱える。
- Apple Metalを利用できる。
- Linux Pure CPUを同じLogical Contractで扱える。
- Quantized ModelのMemory効率が高い。
- Streaming、Stop、Seed、Chat Template、Metadataを提供できる。
- 将来Backend Adapter交換のBaselineになる。

Backend固有処理はAdapterへ閉じ込め、Application Coreから直接`llama_cpp` APIを呼ばない。

### 12.2 Build Variant

```text
macOS:
  llama.cpp Metal Build

Lightning Pure CPU:
  llama.cpp CPU Build

Lightning CUDA CPU Execution:
  CUDA Build + gpu_layers=0
  Pure CPU Buildとは別Profile

Future CUDA:
  llama.cpp CUDAまたはvLLM
```

`compute_kind=cpu`と`build_variant=cuda`は矛盾ではなく、CUDA BuildをCPU実行する構成であり得る。Pure CPU Buildと明示的に区別する。

### 12.3 Backend候補

| Backend | 初期判断 | 再評価理由 |
|---|---|---|
| llama.cpp | 採用 | Local GGUF／Metal／CPU |
| MLX／mlx-lm | 保留 | Apple Silicon最適化、Model形式追加 |
| Transformers／PyTorch | 保留 | Canonical Weight、Guard／Judge、ZeroGPU |
| vLLM | 将来 | Cloud GPU、高Throughput |
| Remote Inference API | 将来 | Hybrid／External Provider |

## 13. Model選定詳細

### 13.1 Main Model

Qwen3-4B Q4_K_Mは最終品質ではなく、M2 Pro／16GB上でRuntime全体を成立させるBalanced Baselineとして採用した。

選定軸：

- 日本語／英語
- 開発・設計・Code支援
- 雑談
- 指示追従
- Thinking Control
- GGUF／llama.cpp
- Memory
- Metal速度
- License／配布再現性
- 将来Cloud移行

DeepSeek、Llama、Mistral等は将来交換候補であり、特定FamilyをCoreへ固定しない。

### 13.2 Guard Model

```text
Candidate:
  Qwen3Guard-Gen-0.6B

Local Artifact:
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf

Canonical Candidate:
  Standard Weight／Transformers
```

Prompt InjectionはRule-based中心とし、専用Classifierは後から追加する。Tool PermissionはGuard Modelではなく決定論的Policyが正本である。

### 13.3 Judge Model

```text
Candidate:
  AtlaAI/Selene-1-Mini-Llama-3.1-8B

Local Artifact:
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf

Canonical Candidate:
  Standard Weight／Transformers
```

LLM-as-a-Judgeは将来機能であり、Main／Guardと独立Adapter、Prompt、Criteria、ThresholdおよびEvidenceを持つ。GGUFでCapabilityが不足する場合はCanonical Weightへ切り替える。

### 13.4 Model File Naming

取得済みArtifactのFile名は配布元の名称を保持する。

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
models/guard/qwen3guard-gen-0.6b/gguf/Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
models/judge/selene-1-mini-llama-3.1-8b/gguf/Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
```

命名規則の差はRegistry Key、Role、Upstream、Digestで吸収する。File Rename履歴管理のためだけにArtifact名を変更しない。

## 14. Web Technology選定

### 14.1 FastAPI／Uvicorn

FastAPI＋Repository内の軽量HTML／CSS／JavaScriptを採用した。

- API Boundaryが明確
- SSE Streamingを直接制御
- Cooperative Cancel
- Health Check
- Basic認証
- Lightning Port公開
- React等への将来交換
- Server-side Policyを適用可能

### 14.2 Streamlit不採用理由

最短Prototypeには適するが、次を優先して初期採用しなかった。

- UIとApplication Stateの分離
- Cancel／Busy／Streaming Lifecycle
- Access Profile
- API再利用
- 将来React／Mobile Clientへの交換

### 14.3 React／Next.js

Phase 4以降の候補とする。

- 複数Chat
- 複雑な研究設定
- Responsive UI
- Component別Status
- Advanced Markdown／Code Block
- Accessibility

採用時もFastAPI Boundaryを維持し、UI FrameworkをCoreへ入れない。Next.jsは必要性が生じた時点で再評価し、現在の必須技術にしない。

## 15. Configuration Technology

TOML＋Pydanticを採用する。

- Human-readable Config
- Typed Validation
- Source Precedence
- Invalid Combination拒否
- Effective Config生成
- Schema-driven UIへの拡張

UIからTOMLを直接書き換えず、Typed Schema Validation、Diff、Effective Config生成および保存Adapterを経由する。

## 16. Storage選定詳細

### 16.1 Current

- TOML：Application／Profile／Model Registry
- Markdown：Canonical／History／Public Docs
- JSON：Migration Manifest／Inventory
- Browser Memory：一時Conversation
- Filesystem Runtime State：Lightning Lifecycle

### 16.2 Audit

初期候補はJSON／JSONL Append-onlyである。

理由：

- 人が検査できる。
- Phase初期のSchema変更へ追従しやすい。
- SHA-512とCanonicalizationを適用しやすい。
- Databaseへ依存せず原本を保持できる。

SQLiteは検索Index、Projection、履歴UIの補助候補とし、Audit原本の唯一の保存先にしない。

### 16.3 RAG

Vector Storeは未選定である。Mac限定簡易Documentation RAGでは、Dependency、Index Size、再構築時間および公開性を確認して最小構成を選ぶ。LangChainはOrchestration候補だが、Core Contractとしない。LlamaIndexは初期優先候補ではない。

## 17. Platform／Hosting選定

### 17.1 macOS Native

Dockerを使わずNative Metalを採用した。Docker DesktopはLinux VMであり、Apple GPU利用、File Pathおよび初期学習Costを増やすためである。

### 17.2 Lightning AI Studio

Hugging Face ZeroGPUよりLightningを優先した理由：

- 現行GGUF／llama.cpp Repositoryを比較的小変更で実行できる。
- 通常Linux開発環境として扱える。
- SSH／Editor／Persistent Storage／Port公開がある。
- PyTorch／Gradio専用Adapterを初期必須にしない。

Pure CPUはCredit消費を抑えられるがGenerationが遅い。GPUは将来の短時間検証に限定して再評価する。

Traffic-aware Auto-startはRepository側Preparationだけでなく、Platform上のWake、URL維持、Cold Start、Credit条件の実測が必要である。

### 17.3 Hugging Face ZeroGPU

将来Backend交換性の実証候補である。ただし通常はPyTorch／Transformers／Gradio Adapterが必要であり、現行GGUF Runtimeへ追加工事が発生するため初期採用しない。

### 17.4 Cloud／Home Server

高性能GPU付きHome ServerまたはAWS／Azure等へ移行する場合、Deployment Profile、Backend Adapter、Storage AdapterおよびSecret Providerを交換する。Application Coreの変更を最小化する。

## 18. Test／Quality Tool選定

```text
pytest          : Unit／Integration／Native Gate
pytest-asyncio  : Async Web／Lifecycle
pytest-cov      : Coverage
mypy strict     : Static Type
Ruff            : Lint／Format
httpx           : Web Test Client
```

Testを次に分ける。

- Static
- Unit
- Integration
- Model Smoke
- Native Environment Acceptance
- Manual Web Acceptance
- External Browser Acceptance

Mac専用Metal TestをLinuxでFailさせずSkipし、Platform-independent Testは全環境でGreenにする。Test FixtureがHost `/proc`やExecutable Permissionへ不必要に依存しないようにする。

## 19. Documentation Technology

- Markdownを日本語正本の主形式とする。
- JSON Manifestで機械可読Inventory／Migration／Hashを保持する。
- SHA-512でSnapshot Integrityを確認する。
- Mermaid等の図は必要箇所だけで使用する。
- Public画像はRepository相対Pathで参照する。
- Canonical／Phase／History／Shared／PublicをDirectoryで分離する。

Git導入後もAppend-only Historyを削除しない。Git Commit／Tagは追加のEvidenceであり、Documentation Historyの代替ではない。

## 20. License／Distribution Technology Boundary

Model Weightは配布しない。Model取得元、License、Revision、Digestおよび配置方法を記録する。

ARGD／DAGD原本を配布する場合はCC-BY-SA-4.0のAttributionとShareAlike条件を確認する。Project Sourceの初期利用条件は閲覧・評価のみを想定し、将来OSS化時に再選定する。

License、Terms、Notice、Citationは別Artifactとして整合させる。技術選定書は法的解釈の正本にしない。

## 21. Current Decision Status

| 項目 | 状態 |
|---|---|
| Python 3.12／3.13 | Accepted |
| uv 0.11.29 | Accepted |
| llama.cpp／GGUF | Accepted for Initial Runtime |
| macOS Metal | Native Accepted |
| Lightning Pure CPU | Native Accepted |
| FastAPI／Uvicorn | Accepted for Preview |
| Browser Memory | Accepted for Phase 1 only |
| JSON／JSONL Audit | Planned |
| SQLite | Deferred |
| LangChain／LangGraph | Deferred |
| MLX／Transformers | Deferred／Adapter Candidate |
| React／Next.js | Deferred |
| vLLM | Future Cloud |
| Docker | Deferred |
| Traffic-aware Wake | Manual Validation Waiting |
| Anonymous Public Demo | Not Implemented |
| Git Workflow | Not Selected／Not Started |
