# Phase 4 MARGPA Main Runtime Governance 要件

```yaml
document_id: phase_4_requirements
status: accepted_frozen_ready_for_backup
phase: phase_4
language: ja
recorded_at: 2026-08-21 22:04:22 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
frozen_at: 2026-08-21 23:20:56 JST
```

## 1. Purpose

Phase 3で成立したDefinition／Normalized IR／Unbound Compiled Plan／Evidenceを、Main Model直前・直後のGovernance Pointへ安全にBindingし、Qwen Baselineで`off／observe／enforce`を比較可能にする。

Phase 4はMain Runtime Governance MVPである。Guardrail／Security／Policy／AuthorityはPhase 5、LLM-as-a-Judge／反復RepairはPhase 6の責務とする。

## 2. Requirements

### 2.1 Standard Result／Identity

- `P4-RES-001`：Point Invocation、Binding、Evaluation、Recommendation、Executed ActionおよびResultを別Identityにする。
- `P4-RES-002`：Fact、Observation、Inference、Assumption、EvaluationおよびActionを区別する。
- `P4-RES-003`：Standard ResultはDefinition／Rule／Plan／Binding／Capability／Authority／Budget Digestへ追跡可能とする。
- `P4-RES-004`：`recommended_actions`と`executed_actions`を別Fieldにする。
- `P4-RES-005`：取得不能なMetricを0で捏造せずUnavailable Reasonを持つ。

### 2.2 Binding

- `P4-BND-001`：Phase 3のPlanはUnboundのまま保存し、Bindingは新しいImmutable Artifactとして作る。
- `P4-BND-002`：Binding InputにPoint、Stage、Profile、Plan Digest、Runtime Capability、Authority、Policy、BudgetおよびAction Registry Digestを含める。
- `P4-BND-003`：Digest／Compiler／Capability／Authority／Registryの変化で旧Bindingを黙って再利用しない。
- `P4-BND-004`：Unknown Rule／Evaluator／Action、Dependency不足またはConflict未解決をExecutable扱いしない。
- `P4-BND-005`：Definition名をCore Routing条件にしない。Manifest CapabilityとTrusted Adapterで接続する。

### 2.3 Main Governance Point

- `P4-PNT-001`：初期Pointは`main_model.pre`と`main_model.post`とする。
- `P4-PNT-002`：Pointは必要な最小Scopeだけを受け、Secret、Raw Thinkingおよび無関係な全Conversationを受け取らない。
- `P4-PNT-003`：`pre`はPremise、Scope、Constraint、ContextおよびGeneration Configを扱える。
- `P4-PNT-004`：`post`はCanonical Final Output、形式、根拠不足、矛盾、逸脱およびRecommendationを扱える。
- `P4-PNT-005`：Streaming中の介入はPhase 4必須にせず、Start／Canonical Terminal境界を優先する。
- `P4-PNT-006`：Point FailureをGeneration成功またはAction成功へ偽装しない。

### 2.4 Evaluation

- `P4-EVL-001`：決定論的Evaluatorを最初に実装する。
- `P4-EVL-002`：Semantic Evaluator Portは予約できるが、Phase 4 CompletionにModel Callを必須としない。
- `P4-EVL-003`：同じSnapshot、Definition、ProfileおよびConfigから同じDeterministic Resultを得る。
- `P4-EVL-004`：Total ScoreだけでCritical Violationを隠さない。
- `P4-EVL-005`：Unsupported／Ambiguous RuleをPassへ変換しない。

### 2.5 Mode

- `P4-MOD-001`：Defaultは`off`。
- `P4-MOD-002`：`off`はProvider／Evaluator／Point／Action Call 0、Input／Output Mutation 0、追加Model Call 0。
- `P4-MOD-003`：`observe`はResult／Recommendation／Evidenceを生成できるが、Main Model Input／Output／Stopを変更しない。
- `P4-MOD-004`：`enforce`はValid Binding、登録済みAction、AuthorityおよびBudgetが揃う場合だけ利用可能。
- `P4-MOD-005`：Unavailableな`enforce`要求を`observe`へSilent Downgradeしない。
- `P4-MOD-006`：Mode変更はLocal／Loopback／Auth-disabled／Explicit Configuration Controlへ限定する。

### 2.6 Action Resolver

- `P4-ACT-001`：Phase 4 Action Allowlistは`pass／recommend_only／warn／stop_before_generation／reject_output／constrain_generation_config`のうち実装・Authorityが成立したものだけとする。
- `P4-ACT-002`：`repair／regenerate／rebind／reinitialize`はRecommendationとして予約し、Phase 6前に自動反復実行しない。
- `P4-ACT-003`：Unknown Action、Side Effect不明、Authority不足、Budget不足またはConflict未解決時は実行0。
- `P4-ACT-004`：Action ResultはMode、Authority、Capability、Budget、ConflictおよびFailure理由を持つ。
- `P4-ACT-005`：Action ResolverはTool Permission、External AuthorityまたはHuman Approvalを生成しない。

### 2.7 ARGD／DAGD Reference Binding

- `P4-GD-001`：ARGD／DAGDは最初のReference Bundleであり、Core必須Dependencyにしない。
- `P4-GD-002`：Source JSONを黙って修正、独自再定義または巨大System Prompt化しない。
- `P4-GD-003`：構造Passthrough IRだけで実行意味が不足する場合、Trusted Typed Adapter Extensionで補い、推測実行しない。
- `P4-GD-004`：DAGD Experimental State、命名矛盾、欠落ActionおよびAmbiguityをEvidenceへ保持する。
- `P4-GD-005`：Reference Bundle不在でもQwen Runtimeは動作する。

### 2.8 Evidence／Privacy／Status

- `P4-EVD-001`：Point開始／完了、Binding、Rule、Evaluation、Recommendation、Executed Action、CostおよびFailureをTyped Evidence化する。
- `P4-EVD-002`：Raw Prompt／Output全文を通常Evidenceへ複製しない。
- `P4-EVD-003`：Evidence Failure PolicyはProfileで明示し、Default ObserveではModel出力を壊さずDegradedを可視化する。
- `P4-STS-001`：UI／APIはMode、Binding State、Selected Definition／Rule Count、Last Result、Action CountおよびDegraded Reasonを安全に表示する。
- `P4-STS-002`：Source絶対Path、Definition本文、Raw Exception、SecretまたはUser ContentをStatusへ出さない。

### 2.9 Compatibility／Model Strategy

- `P4-COM-001`：既存v1／v2、Persistent Chat、RAG Citation、Stop、Retry／Regenerate、Branch、Public／Basicを壊さない。
- `P4-COM-002`：Qwen3-4BをCurrent／低資源Baselineとして維持する。
- `P4-COM-003`：DeepSeek追加、Load、BenchmarkまたはCurrent PromotionをPhase 4 Main Governanceの必須条件にしない。
- `P4-COM-004`：Model／Backend固有差をCapability SnapshotとAdapterへ隔離する。
- `P4-COM-005`：Public／BasicはLocal Governance Control、Private DefinitionおよびPrivate Evidence Call 0を維持する。
- `P4-COM-006`：Persistent経路では`post` GovernanceのCanonical Terminal判定をAssistant Message永続Commitより前に完了し、永続Commit成功後だけ`completed`を通知する。Reject／Stop／Governance Failureを、未承認Contentの永続化済みCompletionへ変換しない。
- `P4-COM-007`：Ephemeral経路のStop／Rejectは既存SSE Contract内の明示Terminalへ写像し、新しい未定義Event ShapeまたはGhost Completionを生成しない。

## 3. Non-scope

- Phase 5専用Guardrail、Prompt Injection、PII、Policy／Authority本実装。
- Phase 6 LLM-as-a-Judge、自動Repair Loop、User Evaluation本実装。
- Phase 5-EX AWS Resource作成／公開。
- DeepSeekのLoad／Benchmark／Quantization／Promotion。
- Agent／Tool／Memory、本格RAG、Protected Full Capture。

## 4. Completion Condition

- QwenでOFF／OBSERVE／ENFORCEの三経路を再現できる。
- OFFは回帰0、OBSERVEは非介入、ENFORCEは登録済みActionだけを正確に実行する。
- Invalid／Unknown／Ambiguous Definition、Binding不成立およびAuthority不足がFail-closedとなる。
- ARGD／DAGD Reference BundleとDefinition 0件Baselineの両方が成立する。
- Open Major Finding 0、Codex Independent ReviewおよびUser Acceptanceを経る。
