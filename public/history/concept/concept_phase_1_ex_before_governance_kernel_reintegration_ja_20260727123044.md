# MARGPA Runtime LLM コンセプト

```yaml
document_id: public_concept
status: current
language: ja
created_at: 2026-07-27 10:49:00 JST
updated_at: 2026-07-27 10:49:00 JST
owner: Nazuna Research
active_phase: phase_1_ex
```

## 1. モデルそのものではなく、モデルを統治するRuntimeを作る

MARGPA Runtime LLMの中心は、独自の巨大モデルを事前学習することではない。既存の事前学習済みモデルを交換可能な実行部品として扱い、その直外側に、入力、前提、文脈、生成条件、監査、評価、修復、状態および証跡を扱うRuntime Governance Layerを置く。

モデルが変わってもGovernance Coreを作り直さず、Governance Definitionが変わってもModel Adapterを作り直さない。現在の軽量モデルはRuntime骨格を成立させるためのBaselineであり、最終性能Targetではない。

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
