# MARGPA Runtime LLM 技術選定書

```yaml
document_id: technology_selection
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 15:16:24 JST
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

