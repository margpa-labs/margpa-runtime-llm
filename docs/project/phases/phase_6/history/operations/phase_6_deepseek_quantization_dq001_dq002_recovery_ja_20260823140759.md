# Phase 6 DeepSeek Quantization DQ-001／DQ-002 Recovery Evidence

```yaml
document_id: phase_6_deepseek_quantization_dq001_dq002_recovery_20260823140759
status: checkpoint_ready
phase: phase_6
workstream: deepseek_local_quantization_only
from_role: 設計者兼実装者役
to_role: プロジェクト責任者兼設計統括者役
recorded_at: 2026-08-23 14:07:59 JST
authority_handoff: phase_6_deepseek_quantization_codex_designer_implementer_exact_handoff_ja_20260823135123.md
authority_handoff_sha512: bb8f39057c600b35ceefd6c676cfb697f5a0e050a680a07014a88b48b10db2bd202b46b268b0bc1aa2d4d8689ae2a7ca2007518e0fc2adb406d03781c754b2d9
recovery_state: CHECKPOINT_READY
```

## 1. Current State

DQ-001 Read-only PreflightとDQ-002 Compatible Converter Freezeを完了した。次ActionはDQ-003 HF Safetensors→Q8_0 Intermediateである。Q8_0、Q4_K_M、Quantization ManifestおよびCompletion Handoffは未作成である。

## 2. DQ-001 Result

```text
Logical Model Root : margpa-runtime-llm/models
Resolved Target    : /Users/Nazuna Research/models/margpa-runtime-llm/models
Target Model       : deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Exact Commit       : 6e8885a6ff5c1dc5201574c8fd700323f23c25fa
Allowed Root Files : 9
Allowed Root Size  : 16,388,605,270 bytes
Full Snapshot Size : 16,388,927,770 bytes（Accepted Download Evidence）
Excluded Difference: 322,500 bytes（figures/。本TaskではRead／Conversion対象外）
Destination State : conversion_work／gguf／manifestsはDirectory存在、Entry 0、Collision 0
Disk Before       : 86,817,520 KiB available（約82.8 GiB）
Disk Floor        : 64 GiB
Result            : PASS
```

Canonical Root Fileは`LICENSE`、`README.md`、`.gitattributes`、`config.json`、`tokenizer.json`、`tokenizer_config.json`、`model.safetensors.index.json`および2 Safetensors Shardである。`.cache/`と`figures/`へは接触していない。

## 3. Official Toolchain Freeze

```text
Repository          : ggml-org/llama.cpp
Official Tag        : b10516
Exact Commit        : b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9
Commit Verification : GitHub API verified=true／valid signature
Archive             : conversion_work/toolchain/llama.cpp-b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9.tar.gz
Archive Size        : 36,880,066 bytes
Archive SHA-512     : eb24feb381d5989768c44727bf1bea0683a207e337c7f62a55c78d88b0bb84d7960618211ba625e65df8c51fc1bb1fb8b20b932661524473077f6d81b80fe6fa
Archive Validation  : gzip PASS／3,815 Entry／Unsafe Entry 0
Source Root         : conversion_work/toolchain/llama.cpp-b95502ba9aa0eb73a2f4fc8878d7fbe6a847a0b9/
Converter SHA-512   : 861074ac8f3c5a087eecb58347f3ed29b43493576c33aa0d38f106d301de386f472e1550cea9649cbc37d682c06be3508e94f8828c836e7c3d626efd821cff06（unpatched）
```

Mutable `main`、Git clone、Homebrew変更、System／Global Package変更は使用していない。

## 4. Compatibility Finding／Local Patch

b10516の公式Converterでも対象Tokenizer Hashは未登録だった。Patch前`--vocab-only`は次を再現し、Outputを作成せず停止した。

```text
chkhsh             : 0d75215efe33c49084836cb245f2fa78de4b3858f5a3e54d5e1fd27f4ce33b05
Failure            : BPE pre-tokenizer was not recognized
Log                : conversion_work/logs/compatibility-vocab-only-b10516.log
Log SHA-512        : 4e409bbd0fed7bd3970f282412180a3eb681bf160bb4c445af44038c7ee378edd56c3a16fd7a0f19037ed7717dae57c57337b111f206c70d33d9baead5247751
```

対象Exact Commitの公式Metadataから再導出したHashを、Project-local Source Copy内で`deepseek-r1-qwen`へ結ぶ最小Patchを適用した。根拠は、`tokenizer.json`がBPE、NFC、Qwen2-compatible Split＋ByteLevelを示し、llama.cpp Runtimeで`qwen2`と`deepseek-r1-qwen`が同じ`LLAMA_VOCAB_PRE_TYPE_QWEN2`へ解決されることである。

```text
Patched Files:
  conversion/base.py
  convert_hf_to_gguf_update.py

Canonical Metadata SHA-512:
  tokenizer.json        : 33e0abac75a49a17a1d5ddd325bf3c06f4087a8f53ac59eff1dd38a5f7ed8acf058a6790d443bf5c8e2638a774fa9366f5b97e77913e568f8afb42fc70e78402
  tokenizer_config.json : ca0de5f48cad30594e1fcf7f967a61faf60679d7818fba7a2b87660710593908643a96032e153d006ab796e673f3cac220c85e978a286fccc65e62865c2ed398
  config.json           : bcef8548cd948b0fb1400944d2695ac146b7ae45cc6cf8a65cb481f76999563345ff4c89b41be383f81502ea844d901ea33a196b1008160d76f0e483652ca180

Before／After SHA-512:
  conversion/base.py
    before: 3d44d872f4304577254c8504c76b2c367ce78d183b97ab0363c737e5cac3abf55c3aa1c1e2ae8317012bf96cbd31e94c69a0beed5154b383f0b210d9157976c7
    after : 0198983fb5a3386942e0eee2090c96464029ec843e1273f7ca388b0034927948069c6a4a7ae8f26045c2e79da7db7c6bdb89cb82fc5d1d415b8b572c08834781
  convert_hf_to_gguf_update.py
    before: dfffe58efd2981a8e3483952361000a718a626be6fc12c7c8737bd7aa1c30bb01c4c68ffb3df66ee435129cf1d74373dc27ca9d30305f954e64ed2fc21c923b5
    after : fc910eb5caa8355e2858548d1d4b08d8c9c062f492f76247f49f89b650c456f0b97fa963ad343e3a43a52b08970f0e1fe311ecb7cb2149706c5d0f216dadbeb3
```

Patch後の`--vocab-only`はExit 0で成功した。

```text
Tokenizer Pre      : deepseek-r1-qwen
Compatibility GGUF: conversion_work/compatibility-vocab-only-b10516-patched.gguf
Size               : 5,932,066 bytes
SHA-512            : ba2785c6e9a6e8ad5129813ea8713afa04732992d75b89e4d2447279e050536b066d6ad8caea66469b5dd7d979b2e98266bc50e84dbc3bb99389deacd90ccad3
Log                : conversion_work/logs/compatibility-vocab-only-b10516-patched.log
Log SHA-512        : d6d86981ad3699d1a47cce979e0cec9bb0fb0e5e12a3243e96ef79a735737367d3e6a79726a192582eb32776ba28ef80df34a079396cf120fc02714447e2cf9a
```

## 5. Resource／Mutation Boundary

```text
Disk At Checkpoint            : 86,493,772 KiB available（約82.5 GiB）
Projected Q8_0＋Q4_K_M        : 約12.5 GiB
Projected Post-artifact Free  : 約70 GiB before minor logs／metadata
64 GiB Floor                  : PASS／material-step recheck required
Canonical Model Mutation      : 0
Qwen／V4／Sibling Contact      : 0
Project Source／Test／Config   : 0
Stable／Phase Index／Roadmap   : 0
Git Mutation                  : 0
Runtime Load／Benchmark       : 0
Provider Memory／runtime_data : 0
```

## 6. Resume Contract

DQ-003開始直前にOutput／Log collisionとCurrent Diskを再確認する。Q8_0変換成功後、Size、SHA-512、GGUF StructureおよびDiskを検証し、DQ-004へ進む。64 GiB Floorを維持できない場合、既存Artifactを削除せず停止する。
