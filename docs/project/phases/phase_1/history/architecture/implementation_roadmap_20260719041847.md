# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: Phase構成、Configuration Layer、現在地点、次段階
- 正本言語: 日本語
- 最新Index: [documentation_index_20260719041847.md](../documentation_index_20260719041847.md)
- supersedes: `implementation_roadmap_20260719040237.md`

## 1. Current Position

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Phase 1-D Configuration／Response Language    : Designed／Accepted／Implementation Not Authorized
Phase 1-E Thinking Presentation Policy        : Planned／Not Designed／Not Authorized
Phase 2 Conversation Application              : Not Started
```

## 2. Phase 1-D Scope Update

Phase 1-D実装前に、Current Deployment ProfileがApplication共通設定を含む問題を発見した。

Phase 1-Dを次の二段階とする。

```text
Phase 1-D Step A
  Application Config／Deployment Profile分離

Phase 1-D Step B
  Response Language Policy
```

新規共通Config：

```text
config/application.toml
```

共通Owner：

- Selected Model
- Model Root
- Common Load Default
- Generation
- Response Language

Deployment Owner：

- Host／Compute／Backend
- Runtime Requirements
- Hardware Load Override

## 3. Phase 1-A：Environment

状態：Complete／Accepted

- Python 3.13.14／`.venv`／uv
- llama-cpp-python Metal Build
- Environment Verification
- Native Metal Smoke

## 4. Phase 1-B：Model Runtime

状態：Complete／Accepted

- Model Port／llama.cpp Adapter
- Model Registry／Profile Config
- Load／Generate／Streaming／Cancel
- Generation Config／Thinking実行制御
- CLI／Artifact SHA-512

## 5. Phase 1-C：Deployment／Platform／Acceleration

状態：Complete／Accepted

- Deployment Contract
- Platform Registry／Profile Resolver
- Platform Normalization
- Capability／Requirement分離
- Pre-load／Post-load Validation
- Runtime Observation
- Cross-platform Hook

## 6. Phase 1-D：Configuration／Response Language

状態：Designed／Accepted／Implementation Not Authorized

### Step A

- `config/application.toml`
- Application Config Schema `1`
- Deployment Profile Schema `3`
- Typed Config Composer
- Generic Deep Merge禁止
- Common Field／Hardware Field分離

### Step B

- `ja／en／auto`
- Default `ja`
- Environment／CLI Override
- Effective Policy／Source
- System Message Composer
- `model-info`

正本：

- [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
- [configuration_layer_architecture_20260719041847.md](configuration_layer_architecture_20260719041847.md)
- [phase_1d_response_language_requirements_20260719041847.md](../requirements/phase_1d_response_language_requirements_20260719041847.md)
- [phase_1d_response_language_architecture_20260719041847.md](phase_1d_response_language_architecture_20260719041847.md)
- [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- [designer_handoff_phase_1d_response_language_20260719041847.md](../handoffs/designer_handoff_phase_1d_response_language_20260719041847.md)

## 7. Phase 1-E：Thinking Presentation

状態：Planned／Not Designed／Not Authorized

- Thinking実行と表示の分離
- 表示／非表示
- Display Label
- Model Protocol Parser
- Streaming Filter
- Raw／Display Output分離
- Raw Thinking保存方針
- Thinking Sampling Profile

## 8. Phase 2以降

### Phase 2 Conversation Application

- API／Web UI
- Multi-turn／History／Resume
- Stop／Regenerate
- Model／Config／Governance State表示

### Phase 3 Audit／Core Governance

- JSON／JSONL Turn Log
- Canonicalization／SHA-512
- Definition Loader
- ARGD／DAGD Core
- High-Level Explanation

### Phase 4 Evaluation／Repair／Guard

- Rating／Deviation／Severity
- Repair／Re-fix／Rebind
- Guard Model
- Rule Based Injection Guard
- Deterministic Tool Permission

### Phase 5 RAG

- Document／Chunk／Embedding／Index／Retrieval／Citation

### Phase 6 Agent

- Tool／Planning／State／Memory／Handoff／Approval／Audit

### Phase 7 Extensions

- Database／Multiple Model／Multiple GD
- Image／Docker／Home Server
- Windows／Linux／CUDA／ROCm／Vulkan／MLX
- Cloud／vLLM／Remote
- LLM-as-a-Judge
- AISGD／AAGD／MPGD／DAAGD／CDOGD

## 9. Future Config Hook

複数Presetが必要になった場合のみ次を追加する。

```text
config/presets/generation/
config/presets/response/
```

Phase 1-Dでは`config/application.toml`一つを共通正本とする。

## 10. Current Deferred Items

- Response Languageは設計済み、未実装
- Configuration Layer分離は設計済み、未実装
- Thinking PresentationはPhase 1-E
- Native Package通常再Buildは重い
- Runtime Device判定はMetal／CPU中心
- Windows／Linux Native Verification未実施
- `.DS_Store`再生成はRepository Hygiene課題

## 11. Phase Gate

```text
Requirements
  ↓
Architecture
  ↓
Accepted ADR
  ↓
Designer Handoff
  ↓
User Implementation Authorization
  ↓
Implementation
  ↓
Implementer Status
  ↓
Designer Review＋Documentation Index
```

## 12. Authorization Boundary

Phase 1-Dの改訂Requirements、Architecture、ADRおよびHandoffはAcceptedである。

Source／Config／Test実装は未解禁である。
