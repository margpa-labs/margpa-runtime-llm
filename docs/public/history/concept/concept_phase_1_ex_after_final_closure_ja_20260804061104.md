# MARGPA Runtime LLM コンセプト

```yaml
document_id: public_concept
status: current
language: ja
created_at: 2026-07-27 10:49:00 JST
updated_at: 2026-08-04 06:11:04 JST
owner: Nazuna Research
active_phase: phase_2_ready_to_start
```

## 1. モデルそのものではなく、モデルを統治するRuntimeを作る

MARGPA Runtime LLMの中心は、独自の巨大モデルを事前学習することではない。既存の事前学習済みモデルを交換可能な実行部品として扱い、その直外側に、入力、前提、文脈、生成条件、監査、評価、修復、状態および証跡を扱うRuntime Governance Layerを置く。

モデルが変わってもGovernance Coreを作り直さず、Governance Definitionが変わってもModel Adapterを作り直さない。現在の軽量モデルはRuntime骨格を成立させるためのBaselineであり、最終性能Targetではない。

より長期的には、AIの認知、評価、修復、実行、権限、証跡および学習に関係する構成要素を、分解、交換、比較、監査およびRollback可能にするGovernance実行・実験Kernelを志向する。「AI GovernanceのHypervisor」または「実験OS」という比喩で説明できるが、実際のVirtual Machine MonitorやOperating Systemを実装済みだと主張するものではない。

## 2. 徹底した疎結合

設計上の中心価値は、可能な限り徹底した疎結合である。

- ModelとBackendを分離する。
- Application CoreとUIを分離する。
- Configurationの共通値とDeployment固有値を分離する。
- Governance DefinitionとGovernance実行機構を分離する。
- Guardrail、Judge、Repair、RAG、AgentおよびStatus Reportingを独立Componentとする。
- 各機能本体と、その手前で働く専用Governance Pointを分離する。
- Storage、External ServiceおよびCloud SDKをAdapter境界へ閉じ込める。

ただ分割数を増やすことが目的ではない。機能を個別にON／OFFし、構成差による品質、Cost、Latency、監査結果およびFailure Modeを再現可能に比較できる研究装置へ発展させるための分離である。

## 3. 共有Control Planeと分散Governance Point

一つの巨大なGovernance Promptですべてを管理すると、毎Turnの負荷、規則衝突、状態不整合および不要なModel Callが増える。そのため、中央にはDefinition Registry、Compiler、Shared State、Rule Selection、Audit EvidenceおよびAction Resolutionを持つGovernance Control Planeを置き、各機能の手前には必要なRuleだけを受け取る軽量なGovernance Pointを置く。

```text
Governance Control Plane
  ├─ Definition Registry
  ├─ Compiler／Validation
  ├─ Shared Governance State
  ├─ Rule Selection
  ├─ Audit／Evidence
  └─ Action Resolution

Execution Pipeline
  ├─ Input Governance Point
  ├─ RAG Governance Point
  ├─ Guardrail Governance Point
  ├─ Agent／Tool Governance Point
  ├─ Judge Governance Point
  ├─ Model Governance Point
  └─ Output／Repair Governance Point
```

決定論で処理できるものはRuntime側で処理し、意味評価が必要な場合だけModelまたはJudgeを呼ぶ。定義全体を毎回Promptへ投入しない。

## 4. Governance Definitionを名前でハードコードしない

ARGDとDAGDは中核の初期Definitionだが、Runtimeはそれらが存在しない状態でも起動可能とする。Definition Directoryが空、未知のGDが一件だけ存在する、既知系列と無関係なDefinitionが混在する、といった状態を最初から許容する。

DefinitionはID、Version、Hash、Domain、Activation Condition、Capability、Dependency、Conflict、Priority、Input／Output ScopeおよびResult Contractを通じて解決する。将来のCDOGD、AISGD、AAGD、MPGD、DAAGDその他のGDも、名前をApplication Coreへ埋め込まず追加できる構造を目指す。

## 5. OFF／Observe／Enforce

Governanceを含む各Componentは、研究のため個別に切り替えられる構造を目指す。

```text
off      : 完全無効
observe  : 判定と記録だけを行い、出力へ介入しない
enforce  : 停止、修復、再生成または拒否まで実行する
```

自由な切替は、無効な組合せを黙って受理することを意味しない。依存関係、排他関係、Degraded Mode、Runtime変更可否およびRestart要否をSchemaで検証する。

この自由度は研究価値を高める一方、安全機能を無効化した構成も作れる。そのため、本Projectは一切の動作・安全保証を行わず、利用条件と留意事項を明示する。

## 6. 証跡と復元可能性

本Projectは、良い回答だけでなく「どの構成、Model、Definition、Rule、ContextおよびActionからその結果が生じたか」を後から検証できることを重視する。

生のChain of Thoughtを正本として保存するのではなく、System Trace、Input、Output、Generation Config、Model Provenance、Definition Hash、適用Rule、評価、修復、高水準の説明概要およびIntegrity情報を分離して記録する。

Project運用自体も同じ考え方で管理する。Current Canonical、Shared Rule、Phase Index、Append-only History、Before／After Snapshot、SHA-512、Phase Lossless CompilationおよびBackupを組み合わせ、担当Taskを作り直してもDocsだけから続きを復元できる状態を目指す。

## 7. 現在のRuntimeと将来の性能

現在はApple M2 Pro／16GBで継続開発できることを優先し、Qwen3-4B GGUF Q4_K_MをMain Modelとして使用する。環境制約により、現時点では高性能Model、大規模Context、複数Model常駐および高負荷なFull Governanceを前提にしていない。

Model Port、Capability Contract、Deployment ProfileおよびStorage Adapterを維持し、将来のHome Server、GPU Server、Cloud、Remote InferenceまたはvLLM系Backendへ移行したとき、ModelまたはBackendの交換を中心に性能を引き上げられる構造を作る。

## 8. 外部R&D Hook

MARGPA Runtime LLM完成後の独立R&D連携として、次のGeneric Hookを予約する。公開するのは名称、研究領域、方向性および接続原則であり、核心Algorithmや内部Protocolをここでは開示しない。

### EASA

**Exception Aware Safety Architecture**  
**例外認識型安全統治機構**

研究領域：AI Safety Governance

モデル内部に形成された安全傾向、周辺の安全制御および入力文脈・生成過程の相互作用から現れるComposite Safety Behaviorを、単一の物理層と断定せず扱う。

### DLAGSA

**Distributed LEA Agentic Governance & Safety Architecture**  
**分散証跡型例外認識エージェント統治安全機構**

研究領域：Multi-Agent Governance, Distributed Accountability, and Safety Assurance

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う。

### OCILNS

**Open Cognitive Interaction Ledger Network System**  
**認知対話証跡台帳網**

研究領域：Cognitive Interaction Provenance, Tamper-resistant Ledger Architecture, and Cross-system Continuity

人、AI、Toolおよび外部System間の対話を、後から検証・参照・継承・監査できる改竄耐性付き証跡単位として扱い、Model、Thread、ProviderおよびStorageを横断する継続性を支える。

3機構はMARGPA Runtime LLMの必須Coreに埋め込まず、後からAdapter／Event／Evidence Contractで接続し、Configから個別にON／OFFできる方向で設計する。

## 9. このProjectが目指すもの

最終的に目指すのは、単に「ローカルでLLMが動く」状態ではない。

```text
構成を交換できる
構成を無効化できる
構成差を比較できる
判断と副作用を統治できる
結果とCostを再現できる
証跡から検証できる
失敗から修復できる
長期化してもProjectを復元できる
```

現在の実装範囲と今後の順序は、[Roadmap](roadmap_ja.md)を正本として参照する。

## 10. Governanceを実行可能な第一級Componentとして扱う

一般的なAI Governanceは、Policy文書、System Prompt、Guardrail、評価Checklistまたは人間向けReportとして表現されることが多い。MARGPA Runtime LLMでは、Governance Definitionを参照用文書だけで終わらせず、将来的にRuntimeが検証、正規化、Compile、Bindingおよび実行できる第一級Componentとして扱う。

概念上の処理経路は次のとおりである。

```text
Provider
  → Manifest
  → Descriptor
  → Trusted Adapter
  → Normalized Intermediate Representation
  → Governance Compiler
  → Compiled Plan
  → Runtime Binding
  → Governance Pointでの実行
```

各段階の責務を分けることで、Definitionの原文、出所、信頼境界、正規化結果、Compile結果、実行Bindingおよび実行Evidenceを混同しない。Definitionを読み込んだだけで有効化されたとは扱わず、検証、Capability、Activation Condition、Dependency、ConflictおよびBinding結果を通じて実行状態を決める。

ARGDやDAGDも特権的なHardcode対象にはしない。既知のDefinitionが一件も存在しない状態、未知の名前やSchemaを持つDefinitionだけが存在する状態、Custom ProviderからDefinitionが供給される状態を正式な入力状態として扱う。対応不能なDefinitionを黙って実行せず、Inactive、Unsupported、DegradedまたはRefusedとして識別し、理由をEvidenceへ残す。

したがって、本Projectは特定の統治思想だけを実装するAIではない。異なる統治思想を読み込み、変換し、実行し、比較し、必要に応じて無効化できる基盤を目指す。

## 11. AI System内部の遷移点を統治する

統治対象はMain Modelの最終出力だけではない。

```text
Input
  → Context／RAG
  → Guardrail
  → Policy／Authority
  → Agent
  → Tool
  → Judge
  → Main Model
  → Output
  → Repair
```

各遷移点には異なる前提、Capability、Authority、Failure ModeおよびEvidenceがある。そのため、全Layerを一つの巨大Promptで処理せず、共有Control Planeから各Governance Pointへ必要なDefinition、Rule、BudgetおよびStateだけを配布する。

この構造は、中央集権的な一枚岩Guardrailと、各Layerへ完全なGovernance機構を複製する構造の中間に位置する。Definition Registry、State Namespace、Evidence、Budget、Conflict ResolutionおよびAction Resolutionは共有し、Enforcementは対象Layerの境界で行う。

決定論的に判断できる項目はRule Engineで処理し、意味的評価が必要な項目だけModelまたはJudgeへ渡す。これは安全性だけでなく、Cost、Latency、再現性およびFailure Isolationを維持するための設計でもある。

## 12. Governanceを反証可能な実験対象にする

MARGPA Runtime LLMでは、Governanceを「有効だと考えられる思想」として採用するだけでなく、構成差による効果と副作用を検証可能な実験対象として扱う。

同じInput、Model、Seed、Config、DefinitionおよびArtifactに対して、例えば次を比較する。

- Governanceなし
- `observe`による観測のみ
- `enforce`による介入あり
- Guardrailのみ
- Judgeのみ
- Repairあり／なし
- RAGあり／なし
- Agentあり／なし
- 単一Definition／複数Definition

将来的なExperiment Recordには、少なくとも次を関連付ける。

```text
experiment_id／run_id
Input／Output
Model／Artifact／Revision／Digest
Config Snapshot／Source／Digest
Definition／Compiled Plan／Binding Digest
Seed
Enabled Layer／Mode
Baseline
Latency／Token／Resource Cost
Evaluation／Deviation／Severity
Repair Count／Failure
Repeat Run／Variance
Human Review
LLM-as-a-Judge
Known Limitation
```

目的は、単一の総合Scoreだけで優劣を断定することではない。ある構成がどの能力を改善または悪化させたか、追加Token、Latency、Failureおよび運用Costをどれだけ生じさせたかを、再現可能なEvidenceとともに比較することである。

定量計算と定性計算は分離して保持する。異質な結果を無理に一つのScoreへ圧縮せず、評価軸、前提、測定限界および判断主体を残す。これにより、AI Governanceを工学的かつ実験科学的に扱える基盤へ発展させる。

## 13. 存在、評価、権限および実行を混同しない

本Projectを貫く重要な不変条件は、何かが存在、登録または評価された事実だけでは、真実性、権限または実行許可を獲得しないことである。

```text
存在
≠ 登録
≠ 検証
≠ 有効化
≠ 評価
≠ 判断
≠ 権限
≠ 承認
≠ 実行
≠ 責任
```

この分離から、次の原則が導かれる。

- Governance Definitionが読み込まれてもActiveとは限らない。
- Governanceは外部に存在しないPolicy、権限または委譲を生成しない。
- Judgeは評価を行うが、存在するだけで最終Authorityにはならない。
- Agent Governanceは実行過程を統治するが、新しい実行許可を発行しない。
- Tool PermissionはModelの印象や自然言語上の自称権限だけで決めない。
- Research／Developer Modeは表示範囲や設定範囲を広げても、権限昇格を意味しない。
- UI上の非表示はSecurity Boundaryではない。
- Candidate ModelはEvaluationとApprovalを通過するまでCurrent Modelを上書きしない。
- Conversation RuntimeとTraining Runtimeを分離する。
- 評価結果を、承認、実行または責任の確定と同一視しない。

これは単なるModule分割ではない。認知、評価、権限、実行および責任が一つのModelやComponentへ集中し、境界が消失することを防ぐためのArchitectureである。

## 14. InferenceからAI Lifecycle全体へ

初期実装はInference Runtimeから開始するが、長期的な統治対象は回答生成時だけに限定しない。

```text
Data
  → Training
  → Candidate Model
  → Evaluation
  → Approval／Promotion
  → Inference
  → RAG
  → Agent／Tool Execution
  → Judge
  → Repair
  → Audit
  → Rollback
```

将来的には、Dataset Provenance、Training Run、Candidate Artifact、Evaluation、Promotion、Rollback、DriftおよびRegressionを、Inference Runtimeと同じEvidence／Authority原則へ接続する。

RAGではSource、Document、Chunk、Digest、Scoreおよび採用理由を扱う。Agent／ToolではAction Scope、Side Effect、Approval、Budget、MemoryおよびHandoff Integrityを扱う。Judgeでは評価基準、独立性、Bias、CalibrationおよびConflictを扱う。Repairでは修復前後の出力、発火理由、試行回数、成功条件およびFailureを扱う。

各領域は独立Componentとして実装し、同じDatabase、ModelまたはFrameworkへの直接依存をCoreへ持ち込まない。共通化するのは、Evidence、Authority、Identity、Integrity、State TransitionおよびPort Contractである。

## 15. 外部研究群を受け入れるRuntime Kernel

MARGPA Runtime LLMは、EASA、DLAGSAまたはOCILNSそのものではない。これらの独立R&D機構を将来接続、切断、比較、組合せ、隔離および評価するための汎用実装母体として位置付ける。

```text
EASA／DLAGSA
  → Generic External Governance Provider Port

OCILNS
  → Generic Evidence Ledger Port
```

外部機構はDefault OFFとし、存在や接続だけでAuthorityを得ない。External ProviderのFailureがCore Runtime全体を破壊しないよう、Timeout、Capability、Trust、Version、Error、FallbackおよびIsolation境界を持たせる。

この接続原則により、将来的なAI Safety、Multi-Agent Governance、Distributed Accountability、長期認知証跡、Multi-Model／Multi-Thread Continuityおよび改竄耐性付きEvidenceを、Coreへ密結合せず検証できる構造を維持する。

## 16. Project運用自体をGovernanceの実験対象とする

Phase 1-exにおけるDocs再編、Authority分離およびRecovery運用は、単なる文書整理ではない。将来Runtimeへ実装する予定の原則を、Project開発工程そのものへ先行適用している。

```text
担当境界
Write／Read-only Authority
Current／Phase／Shared／Public
Stable／History
Source Freeze
Manifest
SHA-512
Lossless Compilation
Handoff
Review
Cutover
Rollback
Recovery
```

設計、実装および公開文書の担当境界を分け、正本と履歴を区別し、変更前後SnapshotとAppend-only Indexを保持する。Taskが長期化、停止または再作成されても、Docsから現在状態、判断、未解決事項および次の安全な作業を復元できる状態を作る。

この運用は、将来のRuntime Governanceが扱うAuthority、Evidence、Handoff、Fail-closed、ReviewおよびRecoveryの実運用上の検証でもある。ただし、現在のProject運用が将来Runtime Governanceの完成または有効性を証明したとは扱わない。得られたFailureと改善点を、後続設計へ戻すための先行運用である。

## 17. Phase 1の意味

Phase 1で成立させたのは、完成したAI Governance Platformではない。Mac MetalとLightning Linux Pure CPUで同じLogical Contractを通し、Model Adapter、Capability、Config Trace、Streaming、Cancel、Thinking生成／表示分離、Markdown、Copy、Lifecycle、認証およびBackupの最初のCross-environment Runtime契約を成立させた段階である。

現在のWeb画面は完成像ではなく、交換可能なMain Model Runtimeが複数環境で動作することを確認する最初の実行面である。Phase 1の価値は機能数ではなく、Phase 10までの追加機能を既存Coreへ密結合させず、AuthorityとEvidenceを崩さず積み上げるための不変条件を、最初の実装段階から守ることにある。

したがって、MARGPA Runtime LLMの現在地は、次の長期構想に対する最初の動作確認である。

> 複数のGovernance体系を任意のModel、Guardrail、Judge、RAG、Agent、ToolおよびTraining Pipelineへ接続し、その介入効果、Cost、Authority、Responsibility、Evidence、FailureおよびRepairを再現可能に扱う、汎用AI Governance実行・実験基盤。

## 18. 表現上の境界

本書で用いる「Kernel」「Hypervisor」「実験OS」は、責務分離、接続境界および実験基盤としての位置付けを説明する概念的比喩である。現在、Operating System、Hardware Hypervisorまたは完成済みの汎用AI Governance製品を提供しているという意味ではない。

また、Roadmap上の将来機能を現在の実装済み機能として扱わない。現在の実装、Accepted済みの設計、未実装の将来構想、外部R&D Hookおよび再評価中の事項を区別する。実装状態と順序の正本は[Roadmap](roadmap_ja.md)である。
