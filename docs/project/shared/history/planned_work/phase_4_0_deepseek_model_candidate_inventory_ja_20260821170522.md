# Phase 4-0 DeepSeek Model Candidate Inventory

Document Status: `COMPLETE_CANDIDATE`
Document Type: `APPEND_ONLY_HISTORY_ARTIFACT`
Phase: `Phase 4-0 Preselection`
Created At: `2026-08-21T17:05:22+09:00`
From: `設計者兼実装者役`
To: `Codex Controller Review`
Authority Source:

- `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_preselection_design_ja_20260821152518.md`
- `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_preselection_handoff_ja_20260821152518.md`

## 1. 目的と非目的

本書は、Phase 4 Entry時のMain Model選定をゼロからやり直さないため、2026-08-21時点のDeepSeek公式Open Weight、公式Serving Engine資料、AWS公式情報および現行MARGPA ContractをInventory化した事前選定Evidenceである。

本書は次を意味しない。

- Phase 4開始、Current Model昇格または現行Qwen3-4Bの退役。
- Model Download、Weight変換、Load、BenchmarkまたはAWS Resource作成。
- Exact Revision、Derived Artifact、Backend Version、Instance Typeまたは予算の最終Freeze。
- `trust_remote_code`、Custom Kernel、Community QuantizationまたはExternal EndpointのRisk受容。

## 2. 調査方法と判定語彙

調査優先順位は、DeepSeek公式Hugging Face、DeepSeek公式Repository、Serving Engine公式Documentation／Repository、AWS公式Documentation、論文の順とした。第三者配布ArtifactはCanonical Sourceとして扱っていない。

Evidence区分:

- DeepSeek Model事実: DeepSeek公式Hugging Faceだけを採用。
- Backend事実: SGLang／vLLM各公式Documentation／Repositoryを採用。
- AWS事実: AWS公式Documentation／Pricingだけを採用。
- Third-party Benchmark／Blog／Quantization: 最終判断の根拠には`NOT USED`。Hugging Face上のCommunity Quantization件数は存在確認だけで、Identity、品質または推奨根拠に使用しない。

各評価値は次の4値に限定する。

| 値 | 意味 |
|---|---|
| `confirmed` | 公式資料と現行Repository Evidenceの双方、または現行Projectでの実測により確認済み |
| `supported_with_condition` | 公式資料にSupport／検証例があるが、本ProjectのExact Revision・Hardware・Workloadでは未検証 |
| `unknown` | 判断に足る公式Evidenceまたは本Project Evidenceがない |
| `unsupported` | 現行Contract、Hardwareまたは公式Support条件と明確に不整合 |

Model CardのBenchmark値はUpstream自己申告Evidenceであり、本Projectの独立再現結果ではない。GitHub IssueはEngine成熟度のWatch Evidenceであり、一般的な再現性や不具合確定を単独で意味しない。

## 3. 現行MARGPA Model Contract

### 3.1 現行Baseline

| 項目 | 現行値 |
|---|---|
| Model | Qwen3-4B |
| Artifact | GGUF Q4_K_M |
| Artifact Size | 2,497,280,256 bytes |
| Backend | `llama-cpp-python 0.3.34` |
| Platform | macOS ARM64 Metalおよび既存Lightning Profile |
| Context Contract | Native 32,768 tokens |
| Chat Template | GGUF Metadata内Jinja Template |
| Runtime Features | Chat、Streaming、Cancel、Seed、Stop、Token Usage、Thinking分離 |
| Integrity | Exact relative path、size、SHA-512、format、quantization、backend/versionを検証 |

Source:

- `config/models/qwen3_4b_q4_k_m.toml`
- `config/profiles/local_macos_arm64.toml`
- `config/profiles/lightning_linux_x86_64_cuda.toml`
- `src/margpa_runtime_llm/modules/inference/`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/`
- `src/margpa_runtime_llm/bootstrap/model_registry_loader.py`

### 3.2 DeepSeek系を接続する際の既存Seam

現行Model PortはLoad／Unload、Chat、Streaming、Cancel、Context、Seed、Stop、Token Usage、Metadata、CapabilityおよびDevice観測をModel Backendから分離している。したがって、DeepSeek V4の採用に伴いDomain Contract全体をBackend固有化する必要はない。

一方、現行Model Definition Loaderとllama.cpp Adapterは単一Local Artifact、GGUF Metadata内Jinja Chat TemplateおよびExact `llama-cpp-python` Versionを前提とする。DeepSeek-V4-Flash-0731とPro-0813はJinja Chat Templateを同梱せず、専用`encoding` Python実装とDSML Tool Call形式を使用する。このため、現行llama.cpp Adapterへの直接差し替えは`unsupported`であり、Remote OpenAI-compatible AdapterまたはDeepSeek V4専用Codecを持つ新Backend Adapterが必要である。

## 4. Dynamic Official Inventory

### 4.1 Inventory結果

| Candidate | Official State | Approx. Canonical Repository Size | Parameter Evidence | Context Evidence | License | Initial Class |
|---|---|---:|---|---|---|---|
| `deepseek-ai/DeepSeek-V4-Flash-0731` | Flash公式Release、Previewを置換 | 167 GB | HFは304B、SGLangは13B activeを記載 | 1M family、High／Maxは最大384K output推奨 | MIT | `PRIMARY_CANDIDATE` |
| `deepseek-ai/DeepSeek-V4-Pro-0813` | Pro公式Release、Previewを置換 | 893 GB | 約1.65T～1.7T、49B active | 1M family | MIT | `RESEARCH_ONLY` |
| `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` | 公式Distill Release | 16.4 GB | 8B Dense | Qwen3系Config依存、Exact Freeze時再確認 | MIT | `FALLBACK_CANDIDATE` |
| `deepseek-ai/DeepSeek-R1-Distill-Qwen-32B` | 公式Distill Release | 65.5 GB | 33B Dense | 32K launch例、Base R1は128K | MIT、Qwen2.5由来条件も確認対象 | `RESEARCH_ONLY` |
| Current Qwen3-4B GGUF | Project Current | 2.50 GB | 4B class | 32,768 Project Contract | 現行記録を維持 | `COMPARISON_BASELINE` |
| `deepseek-ai/DeepSeek-V3.2` | 公式Release | Large | 約685B class | Long-context family | MIT | `REJECT_CURRENTLY` |
| `DeepSeek-V4-Flash` Preview | Preview、0731に置換 | 約160 GB | 284B／13B active | 1M | MIT | `REJECT_CURRENTLY` |
| `DeepSeek-V4-Pro` Preview | Preview、0813に置換 | Large | 1.6T／49B active | 1M | MIT | `REJECT_CURRENTLY` |

Repository SizeはHugging Face Files表示の概数であり、実Download Size、Local Cache Size、Conversion一時容量、Runtime HBMまたはKV Cache容量と同義ではない。

### 4.2 Revision観測

2026-08-21のRead-only観測では、次のHugging Face `main`短縮Commit IDが表示された。これはPreselection時点の観測値であり、Final Freezeではない。

| Repository | Observed `main` Short Commit | Freeze State |
|---|---|---|
| `DeepSeek-V4-Flash-0731` | `7872f01` | `NOT_FROZEN` |
| `DeepSeek-V4-Pro-0813` | `72e1d32` | `NOT_FROZEN` |
| `DeepSeek-R1-0528-Qwen3-8B` | `6e8885a` | `NOT_FROZEN` |
| `DeepSeek-R1-Distill-Qwen-32B` | `711ad2e` | `NOT_FROZEN` |

Phase 4 EntryではFull Commit SHA、LFS Object／File Manifest、Config、Tokenizer、Encoding Code、Licenseおよび全取得Artifact SHA-512を同一TransactionでFreezeする。短縮Commitやmutable `main`を実行正本にしてはならない。

## 5. Candidate Facts

### 5.1 DeepSeek-V4-Flash-0731

確認できた事実:

- DeepSeek公式は0731をFlash Previewの後継となる公式Releaseと明記する。
- 公式Repositoryは約167 GB、48 Safetensors shardを持ち、Model Cardは304B parameterを表示する。
- SGLang公式Cookbookは304B total／13B active、1M-context familyと記載し、8×B200、4×GB300、4×H200での検証済み構成を掲示する。
- 公式Model CardはPreviewおよびPro Previewを上回る複数のAgentic Benchmark値を掲示する。ただし一部は内部Datasetであり、DeepSeek Harness条件を含む。
- `reasoning_effort`は`low`／`high`／`max`。High／Maxでは最大384K output tokenを許容する設定が推奨される。
- Jinja Chat Templateはない。公式`encoding` codeでOpenAI-compatible messageをPromptへEncodeし、出力をParseする。
- DSML Tool Call、ThinkingとFinal Contentの分離、StreamingはSGLang公式CookbookおよびvLLM公式Parserに明示的なSupportがある。
- 公式vLLM／SGLang起動例は`trust_remote_code`とModel固有Kernel／Parserを伴う。自動実行は許容できず、Exact Code Revision、Container DigestおよびIsolation Reviewが必要である。
- Bundled DSpark draft headを持つ。Preview向けMTP／EAGLE設定をそのまま適用してはならない。

未確認または条件付き:

- 日本語品質の公式独立評価、本Project Governance Promptでの遵守性、JSON／Tool引数の安定性。
- 1M ContextはArchitecture Capabilityであり、全Hardware／Engine／Concurrencyで実用可能とは確認されていない。
- Exact AWS Image、Driver、CUDA、Engine、Kernelの組合せ。
- Cancel伝播、Error Mapping、Usage Accounting、Deterministic SeedのMARGPA Port適合。

Evidence URLs: `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/tree/main`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/commits/main`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/encoding/README.md`、`https://docs.sglang.io/cookbook/autoregressive/DeepSeek/DeepSeek-V4`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 5.2 DeepSeek-V4-Pro-0813

確認できた事実:

- 0813はPro公式Releaseで、DSpark draft headを含む。
- 公式Repositoryは約893 GB、66 Safetensors shard。Hugging Face表示は約1.7T、SGLangは1.65T total／49B activeと記載する。
- SGLang公式Cookbookは4×GB300、8×B200／B300、8×H200 FP4等の検証済み構成を掲示する。
- MIT Licenseである。

選定上の意味:

- Weight Size、HBM、起動時間、Storage、Data Transfer、障害切分けおよび時間課金がFlashより一段大きい。
- 本Projectの最初のDeepSeek IntegrationでPro固有の複雑性を同時導入する合理性は薄い。
- 将来の最高性能比較およびFlashの品質上限検証には価値があるため、除外ではなく`RESEARCH_ONLY`とする。

Evidence URLs: `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/tree/main`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/commits/main`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/blob/main/LICENSE`、`https://docs.sglang.io/cookbook/autoregressive/DeepSeek/DeepSeek-V4`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 5.3 DeepSeek-R1-0528-Qwen3-8B

確認できた事実:

- DeepSeek公式の8B Dense Distillで、Repositoryは約16.4 GB、2 Safetensors shard。
- Qwen3-8Bと同じArchitectureだが、公式RepositoryのConfig／Tokenizerを使用するようModel Cardが要求する。
- 0528版はSystem PromptをSupportし、強制的な`<think>` prefixが不要で、公式Model CardはFunction Calling強化を記載する。
- Canonical WeightとLicenseはDeepSeek公式Repositoryから取得できる。

選定上の意味:

- 現行Qwen系Contractに最も近く、DeepSeek固有Reasoning／Tool挙動を低いCompute Costで先に検証できる。
- Mac／小規模GPU向けDerived GGUFの候補になり得るが、Hugging FaceのCommunity Quantization一覧はCanonicalではない。変換または第三者Artifactの採用には別途Provenance、Conversion Tool、Quantization、SHA-512および回帰試験が必要である。
- V4 Codec／DSML／DSparkの代替ではないため、Flash Compatibility Proofにはならない。

Evidence URLs: `https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`、`https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B/tree/main`、`https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B/blob/main/LICENSE`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 5.4 DeepSeek-R1-Distill-Qwen-32B

確認できた事実:

- DeepSeek公式の33B Dense Distillで、Repositoryは約65.5 GB、8 Safetensors shard。
- 公式Model CardはvLLM／SGLang起動例を持つ。
- 初期R1系列のPrompt運用はSystem Prompt非使用、`<think>`誘導等の固有条件を含む。

選定上の意味:

- 8BとV4-Flashの間の品質／Resource比較には有用である。
- 2025世代のPrompt semanticsを新規Main Adapterの中心へ据えるより、最新0528 8Bを実用Fallback、32Bを比較研究に置く方がContractの分岐を抑えられる。

Evidence URLs: `https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B`、`https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B/tree/main`、`https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B/blob/main/LICENSE`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 5.5 DeepSeek-V3.2およびPreview V4

- V3.2は高性能研究Evidenceとして参照可能だが、685B classで、最新V4 Flash／Pro選定と重複する。初回候補からは`REJECT_CURRENTLY`とする。
- V4 Previewは再現研究には必要だが、公式0731／0813が明示的に置換している。新規Primary／Fallbackにはしない。

Evidence URLs: `https://huggingface.co/deepseek-ai/DeepSeek-V3.2`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash`、`https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro`、`https://huggingface.co/collections/deepseek-ai/deepseek-v4`。Accessed at: `2026-08-21T17:05:22+09:00`。

## 6. Evaluation Vector Matrix

略号:

- `F0731`: DeepSeek-V4-Flash-0731
- `P0813`: DeepSeek-V4-Pro-0813
- `R8`: DeepSeek-R1-0528-Qwen3-8B
- `R32`: DeepSeek-R1-Distill-Qwen-32B
- `Q4`: Current Qwen3-4B GGUF

| Vector | F0731 | P0813 | R8 | R32 | Q4 |
|---|---|---|---|---|---|
| `quality_evidence` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `reasoning` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `chat` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `japanese_evidence` | `unknown` | `unknown` | `unknown` | `unknown` | `supported_with_condition` |
| `tool_calling` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `unknown` | `unsupported` |
| `thinking_separation` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `streaming_cancel` | Streaming `supported_with_condition`、Cancel `unknown` | 同左 | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `context_kv_cost` | 1M capability、実効値 `supported_with_condition` | 1M capability、Cost大 | `unknown` | `supported_with_condition` | `confirmed` at 32K |
| `artifact_portability` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `backend_maturity` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `single_node_feasibility` | `supported_with_condition` on high-end GPU | `supported_with_condition` on highest-end GPU | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `multi_node_complexity` | `supported_with_condition`、High | `supported_with_condition`、Very High | `unknown`／通常不要 | `unknown`／通常不要 | `unsupported`／不要 |
| `aws_cost_class` | Very High | Extreme | Low～Moderate | Moderate～High | Local baseline |
| `home_server_fit` | `unsupported` | `unsupported` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `license_distribution` | `confirmed` MIT | `confirmed` MIT | `confirmed` MIT | `supported_with_condition` | `confirmed` in Current record |
| `security_custom_code` | `supported_with_condition`、要Review | `supported_with_condition`、要Review | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `offline_reproducibility` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `adapter_fit` | `unsupported` for current llama.cpp direct replacement | 同左 | `supported_with_condition` | `supported_with_condition` | `confirmed` |
| `governance_experiment_value` | `supported_with_condition`、High | `supported_with_condition`、比較上限 | `supported_with_condition`、Low-cost | `supported_with_condition` | `confirmed` baseline |

`Q4.japanese_evidence`は現行Runtimeで日本語Policyを扱えることに対するProject Evidenceであり、標準化された日本語Benchmarkの完了を意味しない。

## 7. Serving Engine Inventory

### 7.1 SGLang

公式Cookbookは0731／0813、Hardware別Verified Matrix、Reasoning Parser、Tool Call Parser、Streaming、DSpark、Context／Concurrency tuningを同一資料で扱う。0731では8×B200、4×GB300、4×H200の検証済み条件が明示される。

判定:

- Backend Candidate: `PRIMARY_BACKEND_CANDIDATE`
- Maturity: `supported_with_condition`
- 理由: 最新公式Checkpointの検証情報が具体的で、Thinking／Tool／StreamingをOpenAI-compatible surfaceへ分離するEvidenceが最も揃う。
- 留保: `latest` Image、Custom KernelおよびHardware別分岐をmutableなまま使わず、Exact Image Digest／SGLang Commit／Dependency LockをFreezeする必要がある。

Evidence URL: `https://docs.sglang.io/cookbook/autoregressive/DeepSeek/DeepSeek-V4`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 7.2 vLLM

vLLM公式Recipeは0731をDefault Official Releaseとし、DeepSeek V4専用Tokenizer／Reasoning／Tool Parser、DSpark、Hardware別Recipeを提供する。OpenAI-compatible APIを既存ArchitectureのRemote Adapterへ接続しやすい。

判定:

- Backend Candidate: `ALTERNATIVE_BACKEND_CANDIDATE`
- Maturity: `supported_with_condition`
- 理由: MARGPA Adapter境界との親和性、公式Parser／Recipeおよび広いServing Ecosystem。
- 留保: vLLM／SGLang双方に、0731のKV Cache、長Context、DSpark、Ampere等に関するOpen Issueがある。Issueは環境依存だが、Version／GPU／Contextを固定したAcceptanceなしにProduction-readyとしない。

Evidence URLs: `https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4-Flash.yaml`、`https://docs.vllm.ai/en/latest/api/vllm/models/deepseek_v4/`、`https://docs.vllm.ai/en/latest/api/vllm/parser/deepseek_v4/`。Maturity Watch: `https://github.com/vllm-project/vllm/issues/51041`、`https://github.com/vllm-project/vllm/issues/50576`、`https://github.com/sgl-project/sglang/issues/33549`、`https://github.com/sgl-project/sglang/issues/34155`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 7.3 llama.cpp／Transformers

- 現行llama.cpp AdapterはQwen3-4B Baselineに維持する。V4-0731／0813のCanonical Serving Primaryにはしない。
- Community GGUF表示は存在するが、Canonical Sourceではない。V4専用Encoding、DSML、Kernel、極大WeightおよびLong ContextのCompatibilityが未証明である。
- Transformers単体はReference／Conversion検証候補であり、V4の初期Production Serving Primaryにはしない。

## 8. AWS Inventory

### 8.1 Instance Capability

AWS公式Instance資料では、代表的な単一Instanceの総GPU Memoryは次の通りである。

| Instance | GPU | Total GPU Memory | Preselection Interpretation |
|---|---|---:|---|
| `p5.48xlarge` | 8×H100 | 640 GiB | FlashはEngine条件次第、Pro canonical 893 GBはraw sizeだけで不足 |
| `p5e.48xlarge`／`p5en.48xlarge` | 8×H200 | 1,128 GiB | Flashは有力、ProはSGLang FP4例があるが余裕・KV・Kernelを要検証 |
| `p6-b200.48xlarge` | 8×B200 | 1,432 GiB | Flash／Proともraw size上は収容、SGLang B200例と整合 |
| `p6-b300.48xlarge` | 8×B300 | 2,144 GiB | Pro含む最有力Memory class、Availability／Costは最重 |

これはMemory CapacityからのPreselection推論であり、AWS上でのLoad／Correctness／Throughput検証ではない。WeightだけでなくEngine、CUDA Graph、KV Cache、Activation、Communication Buffer、Context長およびConcurrencyの余裕が必要である。

Memory一次Screeningの式は次だけに限定する。

```text
raw_headroom = instance_total_gpu_memory - canonical_repository_size
```

この`raw_headroom`は、Repository fileの格納量とRuntime配置量が同一という仮定を含む粗い上限Screeningである。正の値でもLoad可能性を確定せず、負の値の場合だけ少なくとも同一形式の単純全Weight常駐が成立しないと判定する。Runtime Feasibilityは実際のWeight layout、replication／sharding、KV、workspace、context、concurrencyおよびEngine telemetryで再計算する。

Evidence URLs: `https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html`、`https://aws.amazon.com/ec2/instance-types/p6/`、`https://aws.amazon.com/ec2/instance-types/accelerated-computing/`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 8.2 CostとQuota

- AWS Capacity Blocks公式Pricingの2026-08-21表示例では、`p6-b200.48xlarge`は約USD 98.84／hour、`p5e.48xlarge`は約USD 47.76／hourのRegion例がある。これはCapacity Blocksの例であり、一般On-Demand価格または将来価格ではない。
- EC2 On-Demand P InstanceのDefault vCPU Quotaは0とAWS公式資料に記載され、Account／Regionごとの引上げが必要になり得る。
- Actual Quota、Capacity、Region、Storage、Data Transfer、AMI／Container CompatibilityはAWS Accountなしには確定できない。
- Phase 4-0 Preselection自体にAWS Accountは不要である。Account作成、Quota申請、課金Resource作成はHuman Gate後の別Work Unitとする。

実行前Cost上限は次の式で再見積する。

```text
maximum_run_cost = instance_effective_hourly_price * approved_hours
                 + storage_cost_for_approved_lifetime
                 + expected_data_transfer_cost
                 + approved_contingency
```

Capacity Blocks表示価格を`instance_effective_hourly_price`へ自動転記せず、購入方式、Regionおよび実行時刻のAWS公式見積をHuman Gateで固定する。

Evidence URLs: `https://aws.amazon.com/ec2/capacityblocks/pricing/`、`https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-quotas.html`、`https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html`。Accessed at: `2026-08-21T17:05:22+09:00`。

### 8.3 Managed Availability

AWS公式はDeepSeek-R1およびDistillをBedrock Marketplace／SageMaker JumpStartで案内している。一方、今回調査範囲ではV4-0731／0813のAWS Managed提供を確定できなかった。したがって`unknown`とし、「提供なし」と断定しない。

Evidence URL: `https://aws.amazon.com/blogs/machine-learning/deepseek-r1-model-now-available-in-amazon-bedrock-marketplace-and-amazon-sagemaker-jumpstart/`。Accessed at: `2026-08-21T17:05:22+09:00`。V4 Managed Availabilityは公式Source検索で確証なしのため`unknown`。

本ProjectのMain RouteはOpen Weight Self-hosted Candidateであり、Managed ModelはIdentity、Provider Policy、Data Boundary、Audit EvidenceおよびCost Modelを分離したAlternativeである。

## 9. Source Register

全Web Sourceの`accessed_at`は、特記がない限り`2026-08-21T17:05:22+09:00`である。

### 9.1 DeepSeek Official

| Subject | URL |
|---|---|
| V4 Collection | https://huggingface.co/collections/deepseek-ai/deepseek-v4 |
| V4 Flash 0731 Model Card | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731 |
| V4 Flash 0731 Files | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/tree/main |
| V4 Flash 0731 Commits | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/commits/main |
| V4 Flash 0731 License | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/LICENSE |
| V4 Flash Encoding | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/encoding/README.md |
| V4 Flash Inference | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/blob/main/inference/README.md |
| V4 Pro 0813 Model Card | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813 |
| V4 Pro 0813 Files | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/tree/main |
| V4 Pro 0813 Commits | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/commits/main |
| V4 Pro 0813 License | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/blob/main/LICENSE |
| V4 Flash Preview | https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash |
| V4 Pro Preview | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro |
| V3.2 Model Card | https://huggingface.co/deepseek-ai/DeepSeek-V3.2 |
| R1 0528 Qwen3 8B | https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B |
| R1 0528 Qwen3 8B Files | https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B/tree/main |
| R1 0528 Qwen3 8B License | https://huggingface.co/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B/blob/main/LICENSE |
| R1 Distill Qwen 32B | https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B |
| R1 Distill Qwen 32B Files | https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B/tree/main |
| R1 Distill Qwen 32B License | https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-32B/blob/main/LICENSE |

### 9.2 Engine Official

| Subject | URL |
|---|---|
| SGLang DeepSeek V4 Cookbook | https://docs.sglang.io/cookbook/autoregressive/DeepSeek/DeepSeek-V4 |
| SGLang DeepSeek V4 Notebook | https://github.com/sgl-project/sglang/blob/main/docs/demo/deepseek_v4_flash.ipynb |
| vLLM DeepSeek V4 Recipe | https://github.com/vllm-project/recipes/blob/main/models/deepseek-ai/DeepSeek-V4-Flash.yaml |
| vLLM DeepSeek V4 Model Implementation | https://docs.vllm.ai/en/latest/api/vllm/models/deepseek_v4/ |
| vLLM DeepSeek V4 Parser | https://docs.vllm.ai/en/latest/api/vllm/parser/deepseek_v4/ |
| vLLM Parallelism | https://docs.vllm.ai/en/latest/serving/parallelism_scaling/ |
| vLLM 0731 KV Watch Issue | https://github.com/vllm-project/vllm/issues/51041 |
| vLLM Ampere Watch Issue | https://github.com/vllm-project/vllm/issues/50576 |
| SGLang Long-context Watch Issue | https://github.com/sgl-project/sglang/issues/33549 |
| SGLang 1M OOM Watch Issue | https://github.com/sgl-project/sglang/issues/34155 |

### 9.3 AWS Official

| Subject | URL |
|---|---|
| EC2 Accelerated Computing Instance Types | https://docs.aws.amazon.com/ec2/latest/instancetypes/ac.html |
| EC2 P6 Instances | https://aws.amazon.com/ec2/instance-types/p6/ |
| Accelerated Computing Specs | https://aws.amazon.com/ec2/instance-types/accelerated-computing/ |
| EC2 Capacity Blocks Pricing | https://aws.amazon.com/ec2/capacityblocks/pricing/ |
| EC2 Instance Quotas | https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-quotas.html |
| EC2 Resource Limits | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-resource-limits.html |
| DeepSeek R1 in AWS Managed Services | https://aws.amazon.com/blogs/machine-learning/deepseek-r1-model-now-available-in-amazon-bedrock-marketplace-and-amazon-sagemaker-jumpstart/ |

## 10. Major Unknowns

1. 日本語、Governance遵守、JSON、Citation、Tool Call、Prompt InjectionおよびRefusalのProject固有評価。
2. Exact Revision時点の304B／13B active表記、Config、Encoding Code、DSpark、License FileおよびWeight Manifestの一貫性。
3. SGLang対vLLMのExact Version／Container Digest別のCorrectness、Streaming、Cancel、Usage、Seed、Error Mapping。
4. 32K、128K、384Kおよび1M ContextでのKV、TTFT、Throughput、Concurrency、OOM境界。
5. AWS Region別のP6／P5e Capacity、Quota、Price、Storage／Transfer費用およびImage互換性。
6. Community／Self-converted GGUF等Derived ArtifactのProvenance、品質、Backend SupportおよびMac実用性。
7. V4 Managed EndpointのAWS公式提供状態。

## 11. Inventory Conclusion

公式Releaseの更新を反映すると、事前設計時のPreview名をそのまま選ぶのは不適切である。最新公式`DeepSeek-V4-Flash-0731`を高性能Main Primary Candidate、`DeepSeek-R1-0528-Qwen3-8B`を実用Fallback Candidate、現行Qwen3-4BをMac／低資源Comparison Baseline、`DeepSeek-V4-Pro-0813`をResearch-only品質上限候補として次段のRecommendationへ渡す。

Current Promotion: `NOT PERFORMED`
Model Download: `NOT PERFORMED`
AWS Mutation: `NOT PERFORMED`
Source／Stable／Phase 3／Git Mutation: `0`
Root-outside Filesystem Access: `0`
