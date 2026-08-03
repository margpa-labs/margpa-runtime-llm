# ADR-0010: AI実験・統治Platform向けPhase再編

- 文書ID: `adr_0010_research_runtime_phase_reorganization`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連要件: [post_phase_1e_research_platform_requirements_20260719112304.md](../requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
- 後継Roadmap: [implementation_roadmap_20260719112304.md](../architecture/implementation_roadmap_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし

## Context

旧Roadmapは、Phase 2をConversation Application、Phase 3をAudit／Core Governanceとし、後半にRAG、Agent、複数GDを置いていた。

その後、次の要件が優先化された。

- ARGD／DAGDを含むGovernance実行基盤
- 各Functional Layerと専用Governanceの疎結合なON／OFF
- `off／observe／enforce`の比較
- Experiment Profile、Run Identity、Config／Artifact／Definition Digest
- Event-driven Runtime Status
- Macと外部Linux／CUDA環境での並行検証
- UIからのTyped Config調整
- 特定GDをハードコードしない汎用Definition Platform

これらは単なる後付けFeatureではなく、後続するGuard、Judge、Repair、RAG、Agentの基盤である。UIを先に固定すると、その後にComponent Switch、Status、Experiment、Governance Bindingを追加する際の手戻りが大きい。

## Decision

Phase 1-E完了後のRoadmapを再編する。

```text
Phase 0   Project Definition／Technology Selection
Phase 1   Portable Model Runtime Foundation
Phase 2   Experimental Runtime Control Plane
Phase 3   Generic Governance Definition Platform + MARGPA Main Governance
Phase 4   Conversation Application／Web UI
Phase 5   Guardrail／Security／Policy
Phase 6   Judge／Evaluation／Repair
Phase 7   RAG／Data Governance
Phase 8   Agent／Tool／Memory
Phase 9   Multi-Governance Orchestration
Phase 10  Hardening／Public Release／Expansion
```

UIの前にPhase 2として、Component Registry、Experiment Runtime、Event／Status／Minimal Audit、Lightning AI Studio対応を置く。

## Rationale

1. UIの前にTyped Runtime Contractを作ると、CLI、API、UI、Experiment Runnerが同じContractを使える。
2. Governance実装前にBaseline、Mode、Run Recordを持つことで、Governanceの効果と負荷を比較できる。
3. MacだけでArchitectureを固める前にLinux／CUDAでPortabilityを検証できる。
4. Main Governanceで汎用Definition Platformを実証した後、Guard／Judge／Agentへ同じPoint／Binding Contractを展開できる。
5. 全当初Scopeを失わず、中間Milestoneを明確にできる。

## Consequences

### Positive

- Phase 2完了時点で、外部環境と実験に耐えるRuntime骨格ができる。
- UIがSource／Config固有のロジックを持たなくなる。
- 後続Layerの実験構成を比較できる。
- 複数GDとDynamic RoutingをMVP中核から切り離し、Phase 9へ延期できる。

### Negative

- Web UIの着手は旧Roadmapより後ろになる。
- Phase 2で直接ユーザーに見えにくいControl Plane実装が増える。
- Phase数とPhase Gateが増える。

### Mitigation

- Phase 1のCLIで各Phaseの受入確認を継続する。
- Phase 2は最小ContractとBaselineを優先し、実装前のFunctional Layerを作り込まない。
- 各PhaseのMilestoneと実装境界をRoadmapで固定する。

## Alternatives Considered

### Alternative A: 旧RoadmapのままUIを先行

却下。後からComponent Registry、Status Event、Experiment、Typed Config ServiceをUIの下に入れる手戻りが大きい。

### Alternative B: 全機能を同時に実装

却下。M2 Pro／16GBと試作品の優先順位に合わず、受入条件と問題範囲が不明確になる。

### Alternative C: GovernanceをGuard／Judge後に一括実装

却下。各LayerのContractがGovernanceとExperimentを考慮しないまま固定される。

## Authorization Boundary

本ADRはPhase再編のDecisionをAcceptedとする。個別Phaseの実装解禁を意味しない。
