# Phase 6 DeepSeek Quantization Completion Evidence

```yaml
document_id: phase_6_deepseek_quantization_completion_evidence_20260823141827
status: complete_candidate
result: PASS
phase: phase_6
workstream: deepseek_local_quantization_only
from_role: 設計者兼実装者役
to_role: プロジェクト責任者兼設計統括者役
recorded_at: 2026-08-23 14:18:27 JST
authority_handoff: phase_6_deepseek_quantization_codex_designer_implementer_exact_handoff_ja_20260823135123.md
authority_handoff_sha512: bb8f39057c600b35ceefd6c676cfb697f5a0e050a680a07014a88b48b10db2bd202b46b268b0bc1aa2d4d8689ae2a7ca2007518e0fc2adb406d03781c754b2d9
```

## 1. Outcome

`deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` Exact Commit `6e8885a6ff5c1dc5201574c8fd700323f23c25fa`から、指定されたQ8_0 Intermediateを経由してQ4_K_M Derived Artifactを作成した。Q8_0／Q4_K_MのProcess Exit、Size、SHA-512およびGGUF構造検証はPASSである。Q8_0 Intermediateは保存し、Canonical Snapshotを変更していない。

Runtime Load、Inference、Benchmark、品質評価、Model Definition登録、PromotionはAuthority外のため実施していない。本EvidenceのPASSは量子化Artifactの作成と構造的Integrityだけを意味する。

## 2. Canonical Input／Evidence Grade

```text
Repository              : deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Exact Commit            : 6e8885a6ff5c1dc5201574c8fd700323f23c25fa
Canonical Root          : models/main/deepseek-r1-0528-qwen3-8b/huggingface/
Allowed Root Files      : 9
Allowed Root Size       : 16,388,605,270 bytes
Safetensors Index Total : 16,381,470,720 bytes
Evidence Grade          : EXACT_COMMIT_PLUS_ACCEPTED_SNAPSHOT_INVENTORY_PLUS_SUCCESSFUL_FULL_CONVERSION_READ
Full Weight SHA-512     : NOT RECOMPUTED IN THIS TASK
Excluded                : .cache/／figures/
Canonical Mutation      : 0
```

全Weightの連結SHA-512は再計算していない。Exact Commit、既存Accepted Download Evidence、Inventory、および全Safetensorsを読み切ったExit 0変換を根拠にした。未計算を計算済みとは扱わない。

## 3. Toolchain／Compatibility

```text
Converter Repository : ggml-org/llama.cpp
Official Tag         : b10516
Exact Commit         : b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9
Commit Verification  : GitHub API verified=true／valid signature
Archive SHA-512      : eb24feb381d5989768c44727bf1bea0683a207e337c7f62a55c78d88b0bb84d7960618211ba625e65df8c51fc1bb1fb8b20b932661524473077f6d81b80fe6fa
Converter SHA-512    : 861074ac8f3c5a087eecb58347f3ed29b43493576c33aa0d38f106d301de386f472e1550cea9649cbc37d682c06be3508e94f8828c836e7c3d626efd821cff06
Quantizer            : Homebrew llama.cpp 7970／build revision eb449cdfa
Quantizer SHA-512    : 3cc649f4cc382f63a8bbd76479bcaffb45b8c71eb9acb7b22c47193afb82d08de2453eb3cd319f922d7fb29f0e0ec0048b741442b98235d8925cf967f133e70d
Platform             : macOS 15.4.1／Darwin 24.4.0／arm64
Python               : CPython 3.13.14
Dependencies         : transformers 5.15.1／gguf 0.19.0／torch 2.13.0／sentencepiece 0.2.2
```

b10516でも対象Tokenizer Hash `0d75215efe33c49084836cb245f2fa78de4b3858f5a3e54d5e1fd27f4ce33b05`は未登録だった。Exact Modelの公式Metadataから再導出し、Project-local Toolchain Copy内の`conversion/base.py`と`convert_hf_to_gguf_update.py`だけへ`deepseek-r1-qwen`対応を追加した。Patch根拠、Canonical Metadata Digest、Before／After DigestおよびVocab-only検証はQuantization Manifestと先行Recovery Evidenceへ固定した。Canonical Model、Homebrew Binary、Project SourceへのPatchは0である。

## 4. Q8_0 Intermediate

```text
Path        : models/main/deepseek-r1-0528-qwen3-8b/conversion_work/deepseek-r1-0528-qwen3-8b-Q8_0-intermediate.gguf
Size        : 8,709,517,376 bytes
SHA-512     : b2fbf5b16c2be0d96d659d8ea39073dd120c017da8216671f6657730c2c43d3fdf447496dfe729a4aca6305eac703580e925811b11565350323f214333c3b68a
Exit Code   : 0
Preserved   : YES
GGUF        : v3／LITTLE／qwen3／file_type 7
Tensors     : 399 = F32 145 + Q8_0 254
Blocks      : 36
Context     : 131,072
Tokenizer   : gpt2／deepseek-r1-qwen
Validation  : PASS
```

## 5. Q4_K_M Final Artifact

```text
Path        : models/main/deepseek-r1-0528-qwen3-8b/gguf/DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf
Size        : 5,027,782,720 bytes
SHA-512     : b32af428f1e44c8f4f19b4069b5bc56042ecdb58b18cfb604ee17f33897863986987e731ec4cd28929b72af4b845ac99d7b5f405d97c56bbec40db437518e786
Scheme      : Q4_K_M mixed／F32 145 + Q4_K 217 + Q6_K 37
Source      : Preserved Q8_0 Intermediate
Exit Code   : 0
GGUF        : v3／LITTLE／qwen3／file_type 15
Tensors     : 399
Blocks      : 36
Context     : 131,072
Tokenizer   : gpt2／deepseek-r1-qwen
Validation  : PASS
```

## 6. Retry／Preserved Partial／Open Finding

最初のQ4_K_M試行は、QuantizerがQ8_0からの再量子化を既定で拒否し、Exit 1となった。生成済みPartialは削除・上書きせず保存した。

```text
Partial Path    : models/main/deepseek-r1-0528-qwen3-8b/gguf/DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf
Partial Size    : 5,955,648 bytes
Partial SHA-512 : b583d69cc976a1a66f44706002d524d5e7090507aa28aea571623a54c19a8c4035e177225251803f6582b9aafbca979d4132b9237d0342b6f2a971d0cb864704
Failure         : requantizing from type q8_0 is disabled
Retry           : --allow-requantizeを付加、新規Exact Pathへ出力、Exit 0
Resume Required : NO
```

Open Non-critical Findingは1件である。`llama-quantize`は、既量子化Tensorの再量子化が16-bit／32-bit入力からの量子化より品質を大幅に低下させ得ると警告している。Exact HandoffはQ8_0→Q4_K_Mを指定しており、本TaskではそのRecipeに従った。Runtime Load／Inference／Benchmarkが禁止されているため品質は未評価であり、後続Acceptanceで別途確認が必要である。構造的Integrityを否定するCritical Findingではない。

## 7. Disk Gate

```text
Minimum Floor       : 67,108,864 KiB（64 GiB）
Preflight Available : 86,817,520 KiB
Post-Q8 Available   : 77,983,412 KiB
Pre-Q4 Retry        : 77,976,292 KiB
Final Available     : 73,071,572 KiB（約69.7 GiB）
Final Headroom      : 5,962,708 KiB（約5.69 GiB）
Result              : PASS
```

既存Artifactの削除、移動、上書き、容量確保Cleanupは行っていない。

## 8. Manifest／Logs

```text
Manifest:
  models/main/deepseek-r1-0528-qwen3-8b/manifests/deepseek-r1-0528-qwen3-8b-Q4_K_M-quantization-manifest-20260823141827.json

Q8 Log:
  models/main/deepseek-r1-0528-qwen3-8b/conversion_work/logs/deepseek-r1-0528-qwen3-8b-Q8_0-conversion-b10516.log
  SHA-512: ee844dc0fb5b57281e14fbb0c6cb6872d0d59fd05fadcfa39f9064789c408714d02dab0fb3eab501f9f65ecc0be6bd10180981efc6f1af67cbcbe9d856fa7419

Q4 First-attempt Log:
  models/main/deepseek-r1-0528-qwen3-8b/conversion_work/logs/deepseek-r1-0528-qwen3-8b-Q4_K_M-quantization-homebrew-b7970.log
  SHA-512: 3f1330c3671e64f62441b49c4c9d08adab686268ffd827b2aeee9b206388ed5143e3d3133b0bf6b65ebca44745b14c93c7eeb50723d687c69b04ff79ea251df2

Q4 Successful-retry Log:
  models/main/deepseek-r1-0528-qwen3-8b/conversion_work/logs/deepseek-r1-0528-qwen3-8b-Q4_K_M-requantization-homebrew-b7970.log
  SHA-512: 9a6b60424584248a8b1585abfc56d4574d7d9dedb6fa99b7d408106d973a52e2b165ddc9b0b06d6549b8f4079385f880cf20fcd10efc43d197f1c4408bbc1a5b
```

## 9. Mutation Boundary

```text
Canonical Model Mutation      : 0
Qwen／V4／Sibling Mutation      : 0
Project Source／Test／Config    : 0
Stable Docs／Index／Roadmap     : 0
Git Mutation                   : 0
User runtime_data Contact      : 0
Runtime Load／Inference        : 0
Benchmark／Promotion           : 0
Existing Artifact Delete／Move : 0
```

Authorized新規Writeは、対象Modelの`conversion_work/`、`gguf/`、`manifests/`およびPhase 6 Append-only Evidence／Handoffだけである。

## 10. Completion Contract

```text
Q4_K_M Artifact              : CREATED
Q4_K_M Structural Validation : PASS
Q4_K_M SHA-512／Size         : RECORDED
Q8 Intermediate Status       : RECORDED／PRESERVED
Canonical Mutation           : 0
Qwen／V4／Sibling Mutation    : 0
Source／Test／Config Mutation : 0
Git Mutation                 : 0
User runtime_data Contact    : 0
Manifest                     : CREATED
Disk Floor                   : PASS
Runtime Load／Benchmark      : NOT PERFORMED
Open Critical Finding        : 0
Result                       : PASS／COMPLETE CANDIDATE
```

次Actionは、プロジェクト責任者兼設計統括者役によるEvidence Reviewである。後続のRuntime Acceptance、Benchmark、Promotionは本Taskでは開始しない。
