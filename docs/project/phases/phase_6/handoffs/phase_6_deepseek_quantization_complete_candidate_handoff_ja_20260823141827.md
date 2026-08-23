# Phase 6 DeepSeek Quantization Complete Candidate Handoff

```yaml
document_id: phase_6_deepseek_quantization_complete_candidate_handoff_20260823141827
status: complete_candidate
result: PASS
phase: phase_6
from_role: 設計者兼実装者役
to_role: プロジェクト責任者兼設計統括者役
recorded_at: 2026-08-23 14:18:27 JST
authority: phase_6_deepseek_quantization_codex_designer_implementer_exact_handoff_ja_20260823135123.md
authority_sha512: bb8f39057c600b35ceefd6c676cfb697f5a0e050a680a07014a88b48b10db2bd202b46b268b0bc1aa2d4d8689ae2a7ca2007518e0fc2adb406d03781c754b2d9
```

## 1. Handoff Result

指定ScopeのDeepSeek-R1-0528-Qwen3-8B量子化を完了した。Q8_0 Intermediateを保存したままQ4_K_M Derived Artifactを作成し、GGUF構造、Size、SHA-512、64 GiB Disk FloorおよびMutation境界を検証した。Resultは`PASS／COMPLETE CANDIDATE`である。

## 2. Primary Artifact

```text
Repository   : deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Exact Commit : 6e8885a6ff5c1dc5201574c8fd700323f23c25fa
Path         : models/main/deepseek-r1-0528-qwen3-8b/gguf/DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf
Size         : 5,027,782,720 bytes
SHA-512      : b32af428f1e44c8f4f19b4069b5bc56042ecdb58b18cfb604ee17f33897863986987e731ec4cd28929b72af4b845ac99d7b5f405d97c56bbec40db437518e786
Structure    : GGUF v3／LITTLE／qwen3／file_type 15／399 Tensor
Tensor Types : F32 145／Q4_K 217／Q6_K 37
Validation   : PASS
```

## 3. Preserved Intermediate

```text
Path       : models/main/deepseek-r1-0528-qwen3-8b/conversion_work/deepseek-r1-0528-qwen3-8b-Q8_0-intermediate.gguf
Size       : 8,709,517,376 bytes
SHA-512    : b2fbf5b16c2be0d96d659d8ea39073dd120c017da8216671f6657730c2c43d3fdf447496dfe729a4aca6305eac703580e925811b11565350323f214333c3b68a
Structure  : GGUF v3／LITTLE／qwen3／file_type 7／399 Tensor
Preserved  : YES
Validation : PASS
```

## 4. Evidence

- Completion Evidence: `docs/project/phases/phase_6/history/operations/phase_6_deepseek_quantization_completion_evidence_ja_20260823141827.md`
- DQ-001／DQ-002 Recovery Evidence: `docs/project/phases/phase_6/history/operations/phase_6_deepseek_quantization_dq001_dq002_recovery_ja_20260823140759.md`
- Canonical Manifest: `models/main/deepseek-r1-0528-qwen3-8b/manifests/deepseek-r1-0528-qwen3-8b-Q4_K_M-quantization-manifest-20260823141827.json`

## 5. Disk／Mutation Boundary

```text
Final Available               : 73,071,572 KiB（約69.7 GiB）
64 GiB Floor                  : PASS
Canonical Mutation            : 0
Qwen／V4／Sibling Mutation     : 0
Source／Test／Config Mutation  : 0
Stable Docs／Index／Roadmap    : 0
Git Mutation                  : 0
User runtime_data Contact     : 0
Runtime／Inference／Benchmark  : NOT PERFORMED
Resume Required               : NO
```

## 6. Open Finding

Open Critical Findingは0件。Open Non-critical Findingは1件である。

Exact Handoff指定のQ8_0→Q4_K_MにはQuantizerの`--allow-requantize`が必要だった。Quantizerは、16-bit／32-bit入力から直接量子化する場合に比べ、再量子化が品質を大幅に低下させ得ると警告している。今回はRuntime Load／Inference／Benchmark／品質AcceptanceがAuthority外であり未実施である。したがって、本PASSはArtifact作成と構造的Integrityに限定し、実用品質は後続Acceptanceへ送る。

最初の失敗試行による5,955,648-byte Partial ArtifactはAuthorityどおり削除・上書きせず保存した。成功Artifactは別Exact Pathへ作成済みであり、再開は不要である。

## 7. Next Action／Stop Condition

次Actionはプロジェクト責任者兼設計統括者役によるCompletion Evidence Reviewである。このTaskはここで停止し、Runtime Load、Benchmark、Model Definition登録、Promotion、Stable Docs／Index／Roadmap更新、Git操作または別Model作業へ進まない。
