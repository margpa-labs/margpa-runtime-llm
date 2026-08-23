# Phase 4-0 DeepSeek Model事前選定設計

```yaml
document_id: phase_4_0_deepseek_model_preselection_design_20260821152518
status: designed_not_started
phase: phase_4_pre_entry
subphase: phase_4_0_preselection
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-21 15:25:18 JST
language: ja
document_class: append_only_planned_work_design
authorization: ユーザーによる2026-08-21の設計・Handoff作成指示
activation: 別途の明示的な開始指示が必要
supersedes: null
```

## 1. Purpose

本設計は、Claude側設計統括者役がPhase 3を実行している期間を利用し、Phase 4 Entry Candidateである高性能DeepSeek系Main Modelの事前選定を、Phase 3から分離して行うためのものである。

本Work Unitの到達点は、Phase 4開始時にゼロから選定をやり直さず、最新条件の再確認とExact Revision Freezeへ直ちに進める状態である。

本設計は次を意味しない。

- Phase 4の開始。
- Phase 3の変更、中断、完了またはScope拡張。
- DeepSeekのCurrent Model昇格。
- Model Weight、Tokenizer、ConfigまたはRepository SnapshotのDownload。
- Hugging Face AccountへのLogin、Token利用、License同意操作またはGated Access申請。
- AWS Account、Quota、Billing、IAM、Network、Storage、ComputeまたはEndpointの作成・変更。
- Bedrockその他Managed Model APIの採用。
- Source、Config、Stable Docs、Roadmap、Gitまたは外部Repositoryの変更。

## 2. User Direction Preserved

本設計は次のユーザー方針を保持する。

1. 高性能Main Model候補としてDeepSeek系を追加する。
2. 現行Qwen3-4Bは低資源環境とGovernance差分研究用のBaselineとして保持する。
3. 将来は複数Open Modelを自由に切り替えられる構造を目指す。
4. DeepSeekは公式Hugging Face Repositoryから取得するOpen Weightを正本Sourceとする。
5. Bedrock等の特定Platform Managed ModelをMain Routeへ固定しない。
6. Mac、Home Server、AWSおよび将来の他Cloud間で、Model ArtifactとBackend Adapterを交換可能にする。
7. Platform移行時にModel Contract、Governance Core、Evidence、UIまたはExperiment Contractを作り直さない。
8. 追加の日数、Storage、Download、変換およびInfrastructure Costが生じても、Platform非依存性を優先する。

## 3. Position and Two-stage Decision

Model選定は次の二段階とする。

### 3.1 Preselection Now

本Work Unitで行う。

- 実行時点の公式DeepSeek Model群をInventory化する。
- Main、Fallback、Research-onlyおよびCurrent Rejectionの候補を分類する。
- Model、Artifact、Backend、Hardware、CloudおよびLicenseを分離して比較する。
- Phase 4開始時に必要な最終Freeze Gateを設計する。

### 3.2 Final Freeze at Phase 4 Entry

Phase 3 Closure後、ユーザーのPhase 4開始承認を得て行う。

- 公式Repositoryの最新状態を再確認する。
- Exact Repository ID、Commit Revision、File Set、License、Tokenizer、Config、Weight Formatおよび推論Engine Versionを固定する。
- Download容量、配置先、AWS Region／Instance／Quota／Budget、取得CommandおよびRollbackを確定する。
- ユーザーのModel Download、課金および外部操作に対する明示承認を得る。
- Canonical Snapshot取得後にSHA-512 Manifestを生成する。

Preselection結果はFinal Freezeの有力Inputであるが、Current Model昇格またはDownload Authorityではない。

## 4. Non-negotiable Architecture

```text
Official DeepSeek Hugging Face Repository
  -> Exact Revision Snapshot
  -> Canonical Model Artifact Manifest
  -> Optional Internal Conversion／Quantization
  -> Derived Artifact Manifest
  -> Model Artifact Store
  -> Backend Adapter
  -> MARGPA Model Port
  -> Mac／Home Server／AWS／Future Cloud
```

### 4.1 Acquisition Source and Runtime Dependency

- Hugging FaceはCanonical Artifactの取得元であり、実行時必須Serviceにしない。
- Import完了後は、外部NetworkまたはHugging Face APIなしで起動可能な設計を必須とする。
- Runtime中にHugging Face Endpointへ暗黙接続しない。
- `trust_remote_code`、Custom KernelまたはModel固有Python Codeが必要な場合、Requirement、Digest、Version、IsolationおよびRiskを明示する。
- Canonical SourceはDeepSeek公式Organization配下のRepositoryとする。Community QuantizationをCanonical Sourceへ昇格させない。

### 4.2 Canonical and Derived Artifacts

次を混同しない。

```text
Upstream Model Identity
Official Repository Identity
Exact Repository Revision
Canonical Weight Artifact
Tokenizer／Config／Chat Template
Derived Converted Artifact
Derived Quantized Artifact
Backend-specific Cache／Engine
Deployment Copy
Current Model Promotion State
```

公式Weightから内部変換または量子化する場合、Derived Artifactとして次を記録する。

- Source Artifact Digest。
- Conversion Tool／Version／Commit。
- Exact Command／Parameters。
- Output Format／Quantization／Shard構成。
- Output SHA-512。
- Capability差分とQuality Risk。
- ReproductionとRollback手順。

### 4.3 Platform Neutrality

- AWS S3、EBS、Instance Store等はArtifact Store／Deployment Adapter候補であり、Model Domain ContractへAWS固有APIを持ち込まない。
- vLLM、SGLang、llama.cpp、Transformers、TensorRT-LLM等はBackend候補であり、Model Identityと同一視しない。
- Bedrock等のManaged Modelは、将来のOptional Provider Adapter候補として独立比較できるが、本Work UnitのMain Routeではない。
- Model追加だけでCurrent Modelを上書きしない。
- CandidateはEvaluation／Approval／Promotionを経るまでCandidateのままとする。

## 5. Candidate Discovery Rule

候補一覧を固定的なHard-codeへしない。実行時点でDeepSeek公式Hugging Face Organizationを確認し、一般Chat、Reasoning、Tool CallingおよびSelf-hostingに関係する最新公開Modelを動的にInventory化する。

設計日時点のSeed候補は次であるが、閉集合ではない。

- DeepSeek-V4-Flash family。
- DeepSeek-V4-Pro family。
- DeepSeek-V3.2 family。
- DeepSeek-R1 Distill 32B class。
- DeepSeek-R1 Qwen3 8B class。
- 実行時点で公式Organizationに追加された、上記を置換し得る新しい一般用途Model。

候補追加または除外は、名前の新しさではなくEvidenceにより行う。Activated Parameter数をWeight Memory、QualityまたはCostと同一視しない。

## 6. Work Unit Decomposition

### P4-0-SEL-001 — Current Contract Recovery

Read-onlyで次を確認する。

- Current Qwen Model Definition。
- Model PortとCapability Contract。
- llama.cpp Backend境界。
- Registry LoaderとDeployment Profile。
- Phase 3からPhase 4へのDefinition／Evidence／Binding Seam。
- RoadmapのMulti-model／Cloud Backend予約。

Outputは、DeepSeek候補が満たすべき既存Logical Contract一覧である。

### P4-0-SEL-002 — Official Candidate Inventory

各候補について次を記録する。

- Official Organization／Repository ID／URL。
- Model family／release／base／instruct／reasoning区分。
- Release／Update時点と確認日時。
- Total Parameter／Activated Parameter。公表なしは`unknown`。
- Context Length。
- Canonical Weight Format／Precision／Shard／Repository総容量。
- License名称、License File URLおよび主要な配布条件。法的断定はしない。
- Tokenizer、Chat Template、System／Developer Role、Thinking、Tool Calling、Structured OutputおよびStreaming Capability。
- 公式Local Deployment手順と推奨Engine。
- Known Limitation。

### P4-0-SEL-003 — Artifact and Backend Feasibility

次を分離して評価する。

- Canonical Weightをそのまま実行するRoute。
- 公式Weightから内部変換するRoute。
- Backendごとの対応精度、Kernel、Parallelism、Offline起動、Streaming、Cancel、Thinking分離およびTool Calling。
- Single-node、Multi-GPU、Multi-nodeの成立条件。
- Macで実行可能か、Artifact管理／Config編集／Remote Clientだけ可能か。
- Existing MARGPA Model PortへAdapter追加だけで接続できるか。
- Backend固有ResponseをCanonical Responseへ正規化できるか。

実行していないBenchmark、未確認Hardwareおよび推測値を実測値として扱わない。

### P4-0-SEL-004 — Hardware／AWS Feasibility

外部Resourceを作成せず、公式公開情報だけで次を調査する。

- CandidateごとのWeight Storage、Host RAM、GPU VRAM、GPU数、InterconnectおよびLocal DiskのRequirementまたはEvidence-based Estimate。
- Estimateは計算式、Precision、Overhead、KV Cache前提およびSourceを明記する。
- AWSで成立し得るInstance Family／GPU Class／Single-nodeまたはMulti-node構成。
- Quota、Region Availability、On-demand／Spot、Startup／Shutdown、StorageおよびData TransferのCost要因。
- Exact CostはRegion、購入方式、稼働時間およびContext条件なしに断定しない。
- Region未決のため、比較値はAssumption付きScenarioまたはCost Classとして記録する。
- 一般公開SurfaceはEphemeral Defaultとし、Persistent Conversation／Citation DBを自動Bindingしない。

### P4-0-SEL-005 — Vector Evaluation

全要素を一つの総合点へ潰さず、次のVectorで比較する。

```text
quality_evidence
reasoning_capability
general_chat_quality
japanese_capability_evidence
tool_calling
thinking_separation
streaming_and_cancel_fit
context_and_kv_cost
canonical_artifact_portability
backend_maturity
single_node_feasibility
multi_node_complexity
aws_cost_class
home_server_future_fit
license_and_distribution
security_and_custom_code
offline_reproducibility
margpa_adapter_fit
governance_experiment_value
```

各項目は`confirmed／supported_with_condition／unknown／unsupported`とEvidence Sourceで表現する。Vendor BenchmarkだけでMARGPAへの適合を確定しない。

### P4-0-SEL-006 — Recommendation and Freeze Gate

候補を次へ分類する。

```text
PRIMARY_CANDIDATE
FALLBACK_CANDIDATE
COMPARISON_BASELINE
RESEARCH_ONLY
REJECT_CURRENTLY
```

少なくとも次を出す。

- Primary Candidate 1件。
- Fallback Candidate 1件以上。
- Qwen Current Baselineの保持理由。
- Pro級Modelを採用または延期する理由。
- Phase 4開始時に再確認すべきStale可能性のある事実。
- Final Freezeに必要なHuman Gate。
- 最初のDownload／Conversion／AWS Provisioningを分離した実行順序。

## 7. Mandatory Decision Gates

Primary Candidateは少なくとも次を満たす必要がある。

1. DeepSeek公式Hugging Face RepositoryにCanonical Weightが存在する。
2. Exact RevisionでSnapshot固定可能である。
3. Licenseと配布条件をRepository Sourceから記録できる。
4. Offline Self-host Routeを構成できる。
5. 必要なBackendまたは実装可能なAdapter Routeが説明できる。
6. MARGPAのStreaming、Cancel、Thinking Presentation、Model CapabilityおよびEvidence境界を壊さない。
7. Artifact容量とHardware Requirementを、未知のまま「実行可能」と断定しない。
8. AWSまたは将来Home Serverで成立し得る現実的Routeが一つ以上ある。
9. Current Qwenを削除または黙って置換しない。
10. Provider固有ServiceをGovernance Coreへ埋め込まない。

いずれかを満たさない場合も、調査を停止してUserへ丸投げせず、Condition、代替候補、追加確認Triggerおよび推奨判断を提示する。

## 8. Exact Read Scope

### Repository

```text
docs/project/shared/conventions/documentation_rules_ja.md
docs/project/shared/operations/research_asset_mutation_control_ja.md
docs/project/shared/task_roles/role_authority_matrix_ja.md
docs/project/shared/task_roles/task_role_write_authority_policy_ja.md
docs/project/current/architecture/technology_selection_ja.md
docs/project/current/architecture/system_architecture_ja.md
docs/project/current/architecture/basic_design_ja.md
docs/project/current/requirements/requirements_specification_ja.md
docs/project/current/governance/runtime_governance_specification_ja.md
docs/project/phases/phase_3/phase_index_ja.md
docs/project/phases/phase_3/architecture/phase_3_architecture_ja.md
docs/project/phases/phase_3/requirements/phase_3_requirements_ja.md
docs/project/shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md
docs/public/roadmap_ja.md
config/models/qwen3_4b_q4_k_m.toml
config/platforms/platform_registry.toml
src/margpa_runtime_llm/modules/inference/
src/margpa_runtime_llm/adapters/model_backends/
src/margpa_runtime_llm/bootstrap/model_registry_loader.py
tests/contract/model_port/
tests/integration/llama_cpp/
```

上記以外のProject Root内Fileは、候補評価に必要な場合だけRead-onlyで追加確認し、Statusに理由とPathを記録する。Symbolic LinkのProject Root外追跡は禁止する。

### External Read-only Primary Sources

```text
https://huggingface.co/deepseek-ai/models
https://github.com/deepseek-ai
https://huggingface.co/docs/huggingface_hub/
```

候補ごとの公式Model Card、Files、Commit HistoryおよびLicenseを確認する。加えて、採用候補EngineとAWSの公式DocumentationだけをPrimary Sourceとして使用する。第三者Benchmark、Blog、IssueまたはCommunity Quantizationは補助Evidenceとし、公式事実と分離する。

## 9. Write Scope for the Future Execution Task

実行Taskへ別途開始許可が与えられた場合、次の新規Append-only Fileだけを作成できる。

```text
docs/project/shared/history/planned_work/
  phase_4_0_deepseek_model_candidate_inventory_ja_<timestamp>.md
  phase_4_0_deepseek_model_selection_recommendation_ja_<timestamp>.md
  phase_4_0_deepseek_model_selection_status_ja_<timestamp>.md
```

既存Fileの変更、同名Fileの上書き、Stable Docs更新、Roadmap更新、Phase Index更新およびSource／Test／Config変更は禁止する。追加設計Evidenceが必要な場合は、上記3文書のいずれかへLosslessに含める。Task単位で不要なFileを増やさない。

## 10. Explicit Prohibitions

- Project Root外Filesystemの読取、書込、Hash取得、Metadata操作またはTemporary Artifact作成。第8節で許可された公開Web Primary SourceのRead-only参照は除く。
- `other/`、別Project、Public Repository Copy、Provider Memory、`.claude`、`.codex`またはHome DirectoryへのAccess。
- Model Download、Git LFS、`hf download`、`git clone`、`wget`、`curl -O`またはWeight File取得。
- Login、Credential、Secret、Cookie、Token、Account、OrganizationまたはBilling操作。
- AWS CLI、Console Mutation、Terraform、CloudFormation、SDKまたはResource Provisioning。
- Package Install、Environment変更、Model Load、GPU実行、Benchmark実行またはCost発生。
- Git Add／Commit／Push／Pull／Fetch／Branch／Tag／Remote操作。
- Phase 3 File、Stable File、Roadmap、Source、Test、ConfigまたはCurrent Model Stateの変更。
- BedrockをMain Routeへ変更する判断。
- 不明値の捏造、Activated Parameterと必要Memoryの同一視、Community Artifactの公式扱い。

## 11. Acceptance Criteria

```text
AC-001 Official Candidate Inventory is current as of execution time.
AC-002 Every material claim has a URL and access timestamp.
AC-003 Official, engine-vendor, AWS, and third-party evidence are separated.
AC-004 Exact unknowns remain unknown; estimates expose assumptions and formulae.
AC-005 Canonical and derived artifacts are separated.
AC-006 HF is acquisition source, not runtime dependency.
AC-007 Model, backend, artifact, platform, current/candidate state are separated.
AC-008 One Primary and at least one Fallback recommendation are produced.
AC-009 Qwen low-resource baseline retention is preserved.
AC-010 Phase 4 Final Freeze and Human Gates are explicit.
AC-011 Project Root outside filesystem mutation/read is zero; authorized public Web primary-source reading is excluded.
AC-012 Model download, AWS mutation, source mutation, stable docs mutation, and Git mutation are zero.
AC-013 Exactly three result/status files or fewer are created; unnecessary file proliferation is zero.
AC-014 Phase 3 state and files are unchanged by this Work Unit.
AC-015 No secret, personal information, local user path, account identifier, or credential value is recorded.
```

## 12. Completion Contract

実行Taskは次の形式で終了する。

```text
Recommendation           : PRIMARY／ADJUST／NO_GO
Primary Candidate        : <exact family/repository candidate>
Fallback Candidate       : <candidate(s)>
Current Qwen Baseline    : RETAINED
Phase 4 Final Freeze     : REQUIRED／NOT PERFORMED
Model Download           : NOT PERFORMED
AWS Mutation             : NOT PERFORMED
Repository Source Change : 0
Stable Docs Change       : 0
Phase 3 Change           : 0
Git Mutation             : 0
Root-outside Filesystem Access : 0
Created Files            : <exact list>
Major Unknowns           : <exact list>
Next Human Gates         : <exact list>
```

Technical比較、Routineな候補分類および推奨判断は設計者兼実装者役が行う。ユーザーへ返すのは、課金、Download、外部Account操作、License Risk受容、Phase 4開始、Current Promotionおよび最終候補承認等のHuman-only Gateだけとする。
