# ADR-0013: 第一外部開発・検証環境にLightning AI Studioを採用

- 文書ID: `adr_0013_lightning_ai_studio_external_development`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連Architecture: [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし

## Context

現行の開発・検証環境はmacOS／Apple Silicon／Metalである。将来のCloud／Home Server／GPU Serverへの移行を考慮し、Macと並行してLinux／CUDA環境でも同じRepositoryを開発・検証したい。

候補はHugging Face ZeroGPUとLightning AI Studioであった。

現行RuntimeはPython 3.13、GGUF、llama.cpp／llama-cpp-pythonを中心とする。ZeroGPUは公開DemoとGPU費用の面で魅力があるが、公式仕様上Gradio／PyTorch中心で、GPU Lifecycle、Python Version、Quotaに対する追加Adapterが必要になる。

## Decision

- Phase 2-Dの第一外部開発／検証環境にLightning AI Studioを採用する。
- 同一Repository、GGUF、Model Port、Config Contract、Test Contractを使用する。
- Linux x86_64／NVIDIA CUDA／llama.cppのDeployment ProfileとSetup Recipeを追加する。
- ModelはGitに含めず、Persistent Storageへ配置しDigestを検証する。
- Hugging Face ZeroGPUはPhase 10の公開Demo／PyTorch Backend交換性実証に延期する。

## Rationale

1. Lightning AI Studioは通常のLinux開発環境としてRepositoryを実行できる。
2. SSH、VS Code、永続Storage、GPU、Port公開を利用できる。
3. llama.cppのMetal BuildからCUDA Buildへの差分はDeployment／Acceleration Adapterで吸収しやすい。
4. ZeroGPU向けのTransformers／PyTorch／Gradio Adapterを現時点で先行実装するより、CoreのPortability検証を早く行える。
5. ZeroGPUを後で追加すること自体がBackend交換性の別の実証になる。

## Consequences

### Positive

- Mac MetalとLinux CUDAの2環境でPortabilityを検証できる。
- 現行GGUF Modelとllama.cpp Adapterを再利用できる。
- 将来のHome Server／Cloud GPU移行の学習と検証になる。

### Negative

- LightningのAccount、Cost、Persistence、GPU割当を管理する必要がある。
- CUDA Native BuildとLinux固有検証が追加される。
- 無料公開Demoはすぐには得られない。

## Alternatives Considered

### Alternative A: Hugging Face ZeroGPUを先に採用

今回は却下。現行Runtimeとは別のPyTorch／Transformers／Gradio Adapter、GPU Decorator／Lifecycle対応が必要で、目的に対する追加工事が大きい。Phase 10の候補として保持する。

### Alternative B: Macのみで後回し

却下。Platform／Acceleration Abstractionの問題を後半まで発見できない可能性がある。

### Alternative C: AWS／Azureを直接採用

現時点では延期。Infrastructure、Credential、Cost、DeploymentのScopeが広がる。

## Official References

- [Hugging Face ZeroGPU documentation](https://huggingface.co/docs/hub/main/en/spaces-zerogpu)
- [Lightning AI Studio overview](https://lightning.ai/docs/overview/ai-studio/)
- [Connect a local IDE to Lightning Studio](https://lightning.ai/docs/platform/build/ai-studio/connect-local-ide)
- [Lightning SDK Studio documentation](https://lightning.ai/docs/overview/sdk/studio)

## Authorization Boundary

本ADRは技術選定をAcceptedとする。Lightning Studio作成、GPU利用、課金、Upload／Download、Repository変更は別途の実装／外部操作許可が必要である。
