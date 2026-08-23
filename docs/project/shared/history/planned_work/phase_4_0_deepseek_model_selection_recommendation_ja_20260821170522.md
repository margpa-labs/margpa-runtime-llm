# Phase 4-0 DeepSeek Model Selection Recommendation

Document Status: `COMPLETE_CANDIDATE`
Document Type: `APPEND_ONLY_HISTORY_ARTIFACT`
Phase: `Phase 4-0 Preselection`
Created At: `2026-08-21T17:05:22+09:00`
From: `設計者兼実装者役`
To: `Codex Controller Review`
Input Evidence:

- `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_preselection_design_ja_20260821152518.md`
- `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_preselection_handoff_ja_20260821152518.md`
- `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_candidate_inventory_ja_20260821170522.md`

## 1. Executive Decision

Phase 4 Entryに向けた事前選定を次で`COMPLETE_CANDIDATE`とする。

| Decision | Selection | Meaning |
|---|---|---|
| Main Primary Candidate | `deepseek-ai/DeepSeek-V4-Flash-0731` | 最新公式Open Weightの高性能Main候補。Phase 4 EntryのFreeze／Download／Benchmark前はCurrentへ昇格しない |
| Practical Fallback Candidate | `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` | 低CostでDeepSeek系Reasoning／Chat／Function Callingを検証する実用Fallback |
| Mid-scale Comparison | `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` | 8BとV4 Flash間の品質／Resource比較用。初期Fallbackの第一順位にはしない |
| Highest-capacity Future Candidate | `deepseek-ai/DeepSeek-V4-Pro-0813` | `RESEARCH_ONLY`。初期導入対象にしない |
| Low-resource／Mac Baseline | Current Qwen3-4B GGUF | `COMPARISON_BASELINE`として保持し、Mac pathを失わせない |
| Preview V4 | Flash Preview／Pro Preview | `REJECT_CURRENTLY`。最新公式Releaseに置換済み |
| V3.2 | `deepseek-ai/DeepSeek-V3.2` | `REJECT_CURRENTLY`。Resource負担とV4との重複が大きい |

この選定はCandidateの順位であり、Model Identity、Artifact、Revision、Backend、Platform、Current StateまたはDeployment Profileの最終決定ではない。

## 2. Primary Candidateの理由

`DeepSeek-V4-Flash-0731`をPrimary Candidateとする理由は次である。

1. DeepSeek公式がPreviewを置換するFlash公式Releaseと位置付けている。
2. 公式BenchmarkではAgentic／Coding／Tool利用でPreviewおよびPro Previewを大きく上回るEvidenceがある。
3. 304B total／13B active級として、Pro-0813の約1.65T～1.7T total／49B activeよりWeight、HBM、起動、転送、課金および障害切分けが現実的である。
4. SGLang公式に8×B200、4×GB300、4×H200のVerified構成があり、単一高性能Nodeでの開始候補を持てる。
5. `low`／`high`／`max` Reasoning、Thinking分離、Streaming、DSML Tool Callingを、公式EncodingおよびServing Engineが明示的に扱う。
6. MIT Licenseの公式Canonical Weightが存在する。
7. 高性能ModelとQwen Baselineを分離するProject Strategyに合致する。

ただし、Activated 13Bを一般的なDense 13Bと同じResource classとして扱わない。Canonical Repositoryは約167 GBであり、Model全Weight、KV Cache、Kernelおよび分散実行を必要とする。

## 3. Fallback構造

### 3.1 Practical Fallback: R1-0528-Qwen3-8B

第一Fallbackは`DeepSeek-R1-0528-Qwen3-8B`とする。

理由:

- 公式Canonical Repositoryが約16.4 GBで、V4に比べDownload、Storage、Load、BenchmarkおよびIteration Costが小さい。
- Qwen3 Architecture由来で、現行Qwen系知見を活用しやすい。
- System PromptをSupportし、旧R1 Distillの強制`<think>`運用より現在のChat Contractへ合わせやすい。
- 公式にFunction Calling強化が記載され、Governance／Tool Experimentの低Cost入口になる。
- Local／Mac向けDerived Artifactを将来検討できる。ただし公式SafetensorsをCanonicalのまま保持し、GGUF等はDerivedとして分離する。

FallbackはFlashの完全互換ではない。V4専用Encoding、DSML、DSpark、1M ContextまたはMoE Backendの検証を代替しない。

### 3.2 Mid-scale Comparison: R1-Distill-Qwen-32B

32Bは比較価値を保持するが、初期Fallbackの第一順位にはしない。

- 8Bより品質上限を期待でき、V4よりResource負担が小さい。
- 一方、旧R1 Prompt semanticsとQwen2.5由来条件があり、新規Main Contractに追加分岐を持ち込む。
- 8Bが品質不足、FlashがCost／Capacity不足の場合に限り、第二Fallback Freezeを検討する。

### 3.3 Qwen3-4B Baseline

現行Qwen3-4B GGUFは退役させない。

- Mac ARM64 Metal、低資源、Offline、Fast StartupおよびRegression Comparisonの正本である。
- DeepSeek MainがAWS／高性能Serverを必要としても、Local Mac routeを独立維持する。
- DeepSeek障害、Quota不足、Cost Gate不成立、Network断またはSecurity Review中のFallbackとして残す。
- Primary Promotion後も`Model Identity != Deployment Profile != Current Selection`を維持し、同一ApplicationからProfileで選択可能にする。

## 4. V4-Pro-0813をResearch-onlyとする理由

`DeepSeek-V4-Pro-0813`は品質上限候補として残すが、Phase 4初回Integrationへ投入しない。

1. Canonical Repositoryが約893 GBで、Flashの約5倍を超える。
2. 単一NodeであってもGB300／B200／B300／H200上位構成を要求し、Storage、Transfer、起動時間、HBM、KVおよび課金Riskが極めて大きい。
3. 初回IntegrationではV4 Encoding、Tool Parser、Reasoning、Streaming、Cancel、Adapter、Audit Evidenceという共通RiskをFlashで先に解消できる。
4. Flash 0731の公式Agentic BenchmarkはPro Previewを上回っており、Proを先に選ぶ必然性がない。
5. Flash Acceptance後に同一Harnessで品質差とTotal Costを測らなければ、Proの追加Costを正当化できない。

Pro Promotionを検討する条件:

- FlashがMust-have品質Gateを満たさない。
- Pro-0813が同一Dataset／Prompt／Tool／Governance Harnessで有意に改善するEvidenceがある。
- Exact AWS Capacity、Quota、Budget CeilingおよびShutdown Controlが承認される。
- Weight、Container、Custom Code、License、DigestおよびRecovery TransactionがFreezeされる。

## 5. Canonical WeightとDerived Artifact Route

### 5.1 Canonical Route

全候補のCanonical Sourceは`deepseek-ai`公式Hugging Face Repositoryとする。

Hugging FaceはAcquisition SourceおよびRevision／Manifest Provenanceであり、Runtime Dependencyではない。承認済みArtifactをProject管理下の許可されたModel Storageへ取得し、Offline Integrity Checkを通過した後は、推論の成立をmutable `main`、Hugging Face API、Network可用性または自動更新へ依存させない。

Final Freeze Recordには少なくとも次を含める。

```text
model_identity
official_repository_url
full_commit_sha
release_name
config_digest
tokenizer_digest
encoding_code_digest
license_digest
weight_file_manifest
per_file_size
per_file_sha512
total_size
download_timestamp
download_tool_and_version
source_authentication_result
```

Mutable `main`、短縮Commit、Model名だけ、Cacheの存在だけ、またはServing Engineの自動Download完了だけをEvidenceにしてはならない。

### 5.2 Derived Route

GGUF、AWQ、GPTQ、NVFP4、W4A16、FP8 conversion等はCanonical Weightとは別のDerived Artifactとして扱う。

必要Record:

```text
upstream_canonical_identity_and_revision
derivation_owner
conversion_tool_repository_and_revision
conversion_command_or_reproducible_recipe
source_and_output_format
quantization_scheme
hardware_target
output_manifest_and_sha512
license_and_distribution_review
correctness_and_quality_delta
backend_version_and_container_digest
```

Community Quantizationを採る場合、Browse一覧やPopularityだけで承認しない。公式WeightからのSelf-conversionとCommunity ArtifactのどちらがRecovery、Time、Disk、Security、Correctnessで優れるかを比較し、人間がArtifact取得を承認する。

推奨順:

1. V4 Flash: 公式Mixed-precision Canonical Weightを公式Engineで検証。
2. R1-0528-Qwen3-8B: 公式Safetensorsを先に検証し、Macが必要なら別GateでDerived GGUFを作成または採用。
3. Qwen3-4B: 現行GGUFを変更せずBaseline維持。
4. V4 Pro: Flash完了後のResearch-only GateまでArtifactを取得しない。

## 6. Backend Recommendation

### 6.1 Primary Backend Candidate: SGLang

初回V4 Flash Backend CandidateはSGLangとする。

根拠:

- 最新0731／0813のHardware別Verified Matrixが公式Cookbookにある。
- `deepseek-v4` Reasoning Parser、`deepseekv4` Tool Call Parser、ThinkingとContentを分けたStreaming例がある。
- DSpark、MoE、KV、Concurrency、Hopper／Blackwell差異の運用条件が明示される。
- OpenAI-compatible APIを提供し、MARGPA側をRemote Backend Adapterとして隔離できる。

### 6.2 Alternative Backend Candidate: vLLM

vLLMをAlternativeとする。

- DeepSeek V4専用Model、Tokenizer／Renderer、Reasoning／Tool ParserおよびDSparkを公式に実装する。
- OpenAI-compatible APIと分散Servingの既存Architectureがある。
- vLLM公式Recipeは0731をDefault Official ReleaseとしてHardware別構成を提供する。

### 6.3 Backend Freeze原則

Engine名だけをFreezeしない。次を一体でFreezeする。

```text
engine_name
engine_exact_version_or_commit
container_image_digest
python_version
torch_version
cuda_or_rocm_version
driver_minimum
flashinfer_or_custom_kernel_revision
gpu_architecture
parallelism_topology
parser_and_tokenizer_mode
speculative_decoding_mode
context_and_concurrency_limits
security_isolation
```

`latest` Image、Nightly Packageまたはmutable DependencyをProduction Candidate正本にしない。検証のためNightlyが必要な場合は、Digestを固定したResearch Profileへ隔離する。

## 7. MARGPA Integration Boundary

### 7.1 推奨形

```text
MARGPA Application／Governance
  -> Model Port
  -> DeepSeek Remote Backend Adapter
  -> OpenAI-compatible Client Contract
  -> SGLang Primary／vLLM Alternative
  -> Exact DeepSeek V4 Codec／Parser
  -> Canonical Weight Artifact
```

現行Qwen route:

```text
MARGPA Application／Governance
  -> Model Port
  -> llama.cpp Adapter
  -> Current Qwen3-4B GGUF
```

両Routeを並存させ、Qwen AdapterをV4都合で破壊しない。

### 7.2 新規Contractで分離すべき項目

- `model_identity_key`
- `artifact_identity_key`
- `backend_key`
- `backend_endpoint_profile`
- `backend_exact_version`
- `codec_key`
- `reasoning_mode`と`reasoning_effort`
- `reasoning_content`とFinal `content`
- `tool_calls`とTool Result message
- `stream_chunk_kind`
- `cancel_capability`
- `usage_source`とAccuracy
- `context_limit`、`max_output_tokens`、`concurrency_limit`
- `trust_remote_code_required`
- `platform_profile`
- `current／candidate／research_only` State

### 7.3 Acceptance対象

少なくとも次をBackend共通Contract Testへ落とす。

1. Non-thinking Chat。
2. `low`／`high`／`max` Reasoning mapping。
3. ReasoningとFinal Answerの非混線。
4. Streaming chunk order、UTF-8境界、Terminal chunk。
5. Client disconnect／Cancel伝播とResource解放。
6. Tool Call single／multiple／parallel／invalid argument。
7. System／Developer／User／Assistant／Tool historyのEncode順序。
8. Stop、Max Tokens、Finish Reason、Usage Accounting。
9. Timeout、OOM、Engine crash、Parser error、Partial streamのError Mapping。
10. Japanese、English、混在入力。
11. Governance observe／enforce seamとAudit EventのModel／Artifact／Backend identity。
12. Qwen BaselineとのRegression隔離。

## 8. AWS Feasibility Recommendation

### 8.1 No-account Phase

Phase 4-0の事前選定、Architecture、Harness設計、Cost Formula、Freeze ChecklistはAWS Accountなしで完了できる。本書作成時にAccount作成やAWS Mutationは不要であり、実施していない。

### 8.2 Flash Feasible Scenarios

| Scenario | Preselection Decision | Conditions |
|---|---|---|
| AWS `p6-b200.48xlarge`、8×B200、single node | `supported_with_condition` | SGLang 8×B200 verified evidenceとMemory classが整合。Exact AWS image／driver／container／quota未検証 |
| AWS `p5e.48xlarge`、8×H200、single node | `supported_with_condition` | SGLang 4×H200 evidenceあり。AWS上のKernel、Throughput、Context、Conversion／precisionを検証 |
| AWS H100 class | `supported_with_condition` | SGLangはH100 routeを持つが、0731、Kernel、TP、Context、CostをExact Freeze |
| Multi-node | `supported_with_condition`、初期非推奨 | Network、NCCL、Failure domain、Startup、CostおよびRecovery複雑性が増える |
| AWS Managed V4 | `unknown` | 公式提供、Revision、Data boundary、Audit、CostをPhase 4 Entryで再検索 |

初回はsingle-node、短時間、ephemeral、低Context、低Concurrencyから始める。1M ContextやDSparkはBase Correctness成立後に段階的に追加する。

### 8.3 Pro Feasible Scenarios

P6 B200／B300、GB300 classまたはH200 FP4の公式Engine例からTechnical Feasibilityは`supported_with_condition`と推定できる。しかしCost、Storage、Transfer、Startupおよび余剰HBMを含むOperational Feasibilityは未確認である。

Proは次を満たすまでAWS起動しない。

- FlashのProject Acceptance完了。
- Pro固有の評価仮説と停止条件。
- Hourly、Storage、Transfer、Snapshotを含むCost Ceiling。
- Auto-stop、TTL、Idle shutdown、Tagging、Budget Alarm。
- Quota／Capacity確認。
- Exact Artifactを再DownloadしないCache／Volume Strategy。

### 8.4 Cost Control

Capacity Blocks表示例ではB200 classが約USD 98.84／hour、H200 classが約USD 47.76／hourである。価格は変動し、Pricing model／Regionで異なるため、これを予算正本にしない。

実行前に次を人間が承認する。

```text
region
purchase_model
instance_type
requested_duration
maximum_total_cost
storage_size_and_lifetime
data_transfer_estimate
quota_status
shutdown_deadline
cleanup_owner
```

## 9. Stale Check at Phase 4 Entry

Preselectionは時間依存である。Phase 4開始承認後、Download前に次を再確認する。

1. DeepSeek公式Collectionに0731／0813より新しいReleaseがないか。
2. Model Card、Config、Encoding、License、Files、Commit Historyが変更されていないか。
3. Full Commit SHAとLFS Manifest。
4. SGLang／vLLMのStable Release、DeepSeek V4 Support Matrix、Known Issue、Security Advisory。
5. Reasoning／Tool／Streaming Parserの名称とAPI Contract。
6. DSpark既知Issueと推奨設定。
7. NVIDIA Driver、CUDA、PyTorch、FlashInfer、DeepGEMM、Container互換性。
8. AWS Instance availability、Region、Quota、Capacity、Pricing、Managed V4 availability。
9. Community／Official Derived Artifactの新規公開とProvenance。
10. MIT License Fileの内容、依存Code／Base Model／Distribution条件。
11. Project側Model Port、Governance Seam、Audit Schema、Config ContractのPhase 3 Closure後差分。
12. Qwen3-4B Baselineが引き続き正常であること。

新Releaseが出ていても自動的にPrimaryを置換しない。同一Vectorで比較し、変更理由とMigration CostをEventとして記録する。

## 10. Human Freeze Gates

### Gate H-01: Candidate Approval

- Primary／Fallback／Baseline／Research-only分類をユーザーが承認する。
- Status: `PENDING`

### Gate H-02: License and Security Acceptance

- Exact License、Custom Code、`trust_remote_code`、Container、Kernel、Distribution条件をReviewする。
- Status: `PENDING`

### Gate H-03: Model Download

- Exact Repository、Full Revision、Expected Size、Destination、Disk余裕、Network、SHA-512 Procedureを提示する。
- ユーザーの明示許可なしにDownloadしない。
- Status: `PENDING`

### Gate H-04: Derived Artifact

- ConversionかCommunity Artifactか、Provenance、Tool Revision、Quantization、Quality Loss、Digestを承認する。
- Status: `PENDING`

### Gate H-05: AWS Account／Quota

- Account、Region、IAM、Quota request、Secret handlingを個別に承認する。
- Status: `PENDING`

### Gate H-06: AWS Cost／Resource Mutation

- Instance、Duration、Maximum Cost、Storage、Auto-stop、Cleanupを承認する。
- Status: `PENDING`

### Gate H-07: Benchmark Acceptance

- Dataset、Japanese／Governance／Tool／Long Context、Pass Criteria、Cost Stop条件を承認する。
- Status: `PENDING`

### Gate H-08: Current Promotion

- DeepSeekをCurrent MainへPromotionするかを、Qwen Baseline保持を含めてユーザーが最終承認する。
- Status: `PENDING`

## 11. Proposed Phase 4 Execution Order

Phase 4開始が別途承認された場合の推奨順は次である。

1. Stale CheckとExact Revision Candidate Freeze。
2. Security／License Review。
3. Backend Stable Version候補のSGLang／vLLM比較。
4. Contract Test／Evaluation HarnessをModel Download前に実装。
5. R1-0528-Qwen3-8Bの低Cost Integration Smoke。
6. Qwen3-4B Regression確認。
7. Flash-0731 Canonical Download承認。
8. Ephemeral high-end single-nodeで最低Context／ConcurrencyのLoad／Chat／Stream／Cancel／Tool試験。
9. Reasoning effort、日本語、Governance、Audit試験。
10. ContextとConcurrencyを段階的に拡大。
11. vLLM Alternativeの必要性判定。
12. Cost／品質／運用Evidenceに基づくPromotion Candidate Review。
13. ProはFlash不足がEvidence化された場合だけ別Gateで評価。

この順序は、FallbackをPrimaryと誤認するものではない。低CostでAdapter／Harness不備を先に排除し、高価なFlash GPU時間をModel固有課題へ集中させるためである。

## 12. Stop Conditions

次のいずれかで作業を止め、上位ReviewへEscalateする。

- Canonical Repository／Revision／License／Weight Manifestが一意に確定しない。
- `trust_remote_code`またはContainer内CodeをDigest Freeze／Reviewできない。
- Required GPU、Quota、CapacityまたはCost Ceilingが成立しない。
- EngineのExact VersionにCritical Correctness Issueがあり、安全な固定版またはWorkaroundがない。
- ReasoningとFinal Answer、Tool CallまたはStreamingを監査可能に分離できない。
- Cancel／Timeout／OOMでResource LeakまたはUnbounded課金Riskが残る。
- Japanese／Governance Must-have GateがQwen Baselineを下回る。
- Model採用がMac Qwen routeの削除または不可逆変更を要求する。
- Scope外Mutation、Secret、External Account、Git、Phase 3またはStable Docs変更が必要になる。

## 13. Final Recommendation

```text
Primary Candidate       : deepseek-ai/DeepSeek-V4-Flash-0731
Fallback Candidate      : deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Mid-scale Comparison    : deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
Research-only Ceiling   : deepseek-ai/DeepSeek-V4-Pro-0813
Comparison Baseline     : Current Qwen3-4B GGUF
Primary Backend Candidate: SGLang
Alternative Backend     : vLLM
Canonical Source        : official deepseek-ai Hugging Face repository
Derived Artifact        : optional, separately governed
AWS Account Now         : NOT REQUIRED
Phase 4 Final Freeze     : REQUIRED／NOT PERFORMED
Current Promotion       : NOT PERFORMED
```

Major Unknownsは非BlockingなPreselection Unknownとして明示した。Download、AWS課金、License Risk受容、Phase 4開始およびCurrent PromotionはすべてHuman Gateに残る。

Model Download: `NOT PERFORMED`
AWS Mutation: `NOT PERFORMED`
Source／Stable／Phase 3／Git Mutation: `0`
Root-outside Filesystem Access: `0`

## 14. Source Basis

Web Source、URL、Access Dateおよび現行Repository Evidenceの完全なRegisterは、同TimestampのCandidate Inventoryを正本とする。

- `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_candidate_inventory_ja_20260821170522.md`
- Web `accessed_at`: `2026-08-21T17:05:22+09:00`
