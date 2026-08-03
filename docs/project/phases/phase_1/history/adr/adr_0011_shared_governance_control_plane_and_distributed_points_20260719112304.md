# ADR-0011: 共有Governance Control Planeと分散Enforcement Point

- 文書ID: `adr_0011_shared_governance_control_plane_and_distributed_points`
- 状態: `accepted`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- 関連Architecture: [governance_control_plane_architecture_20260719112304.md](../architecture/governance_control_plane_architecture_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし

## Context

将来のMain Model、Guard、Judge、Repair、Agent、Tool、RAG、Policy等にそれぞれ専用Governanceを配置したい。

一方で、全層を1つの巨大Governance Layerが毎回一括管理すると、無関係なRule、Prompt、Model Callが増える。逆に各Layerへ完全なMARGPA一式を複製すると、Definition、State、Audit、Actionの重複と矛盾が発生する。

## Decision

次の3要素に分離する。

1. 共有Governance Control Plane／Kernel
2. Functional Component境界の軽量Governance Enforcement Point
3. Definition／Profile／Mode／BudgetをPointへ接続するGovernance Binding

決定論的Ruleを優先し、必要なときだけSemantic Evaluatorを呼ぶ。すべてのPointがARGD／DAGD全体を毎回再評価する構成にしない。

## Rationale

- Definition／Compiler／Audit／Action Resolverを共通化できる。
- PointはそのComponentに必要なRuleだけを使える。
- Functional ComponentとGovernanceを個別に無効化・交換できる。
- 複数ActionとAuthorityを中央Resolverで整合できる。
- Definitionの内容とPipeline上の配置をBindingで分離できる。

## Detailed Constraints

- StateはShared Turn／Session Context、Point-local Namespace、Append-Only Evidenceに分ける。
- `off／observe／enforce`をBindingのModeとする。
- Pointが呼ばれない場合、そのGovernanceも実行しない。
- Lazy Load、Rule Selection、Plan Cache、Call／Token／Latency／Repair Budgetを必須とする。
- Unknown ActionをJSONの指示だけで実行しない。
- Governance-on-governanceの無限再帰を禁止する。Meta Reviewは将来、原則OFF／非同期／Max Depth 1とする。

## Consequences

### Positive

- Governanceの共通部とDomain固有部が分離される。
- Guard／Judge／Agent等を追加するたびに統治基盤を複製せずに済む。
- Pointごとの負荷、効果、Errorを計測できる。
- ComponentとGovernanceの組み合わせ実験が容易になる。

### Negative

- Point Contract、Binding Resolver、State Namespace、Action Resolverが必要になる。
- 単純な直列Middlewareより概念数が増える。
- 複数PointのOrdering、Conflict、Failure Policyを設計する必要がある。

## Alternatives Considered

### Alternative A: 中央の単一巨大Governance Layer

却下。すべてのDomain Ruleを毎ターン評価しやすく、負荷、Scope、障害範囲が大きい。

### Alternative B: 各Layerへ完全なGovernance基盤を複製

却下。Registry、Definition、State、Evidence、Action Resolutionが重複し、不整合と保守負荷を増やす。

### Alternative C: Functional Component内へGovernanceを直書き

却下。Guard、Judge、Agent、Model Adapterの交換性を損ねる。

## Authorization Boundary

本ADRはArchitecture DecisionをAcceptedとする。Implementationは個別Phaseの解禁後に行う。
