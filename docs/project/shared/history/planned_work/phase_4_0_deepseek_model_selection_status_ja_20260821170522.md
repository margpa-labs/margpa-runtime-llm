# Phase 4-0 DeepSeek Model Selection Status

Document Status: `STOPPED`
Document Type: `APPEND_ONLY_HISTORY_ARTIFACT`
Phase: `Phase 4-0 Preselection`
Created At: `2026-08-21T17:05:22+09:00`
From: `設計者兼実装者役`
To: `Codex Controller Review`

## 1. Completion State

```text
Status                     : STOPPED
Primary Candidate          : deepseek-ai/DeepSeek-V4-Flash-0731
Fallback Candidate         : deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Mid-scale Comparison       : deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
Research-only Candidate    : deepseek-ai/DeepSeek-V4-Pro-0813
Qwen Baseline              : RETAINED
Primary Backend Candidate  : SGLang
Alternative Backend        : vLLM
Canonical Source           : Official deepseek-ai Hugging Face Repository
Final Revision Freeze      : NOT PERFORMED
Current Promotion          : NOT PERFORMED
Next Action                : Codex Controller Review／Boundary Incident Decision
```

Phase 4-0 PreselectionのCandidate Inventory、Selection Recommendation、Major Unknowns、AWS Feasibility、Stale CheckおよびHuman Freeze Gatesは作成した。事前設計時点のV4 Previewではなく、実行時点の最新公式0731／0813 Releaseを中心に再分類した。

ただし、Completion Validation中のUTF-8確認Commandで、Project Root外の`/dev/null`をwrite-only discard sinkとして1回指定した。外部Dataの読取、永続化、内容変更、Metadata取得またはArtifact作成はないが、Root外Filesystem Access `0`のAcceptance Criteriaを満たさない。Stop Conditionに従い、本Work Unitを`STOPPED`とし、以後の調査、修正、検証、Download、実装または外部操作へ進まない。

## 2. Created Files

1. `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_candidate_inventory_ja_20260821170522.md`
2. `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_selection_recommendation_ja_20260821170522.md`
3. `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_selection_status_ja_20260821170522.md`

本Work UnitのWrite Leaseは上記3件の新規Append-only Artifactだけに使用した。既存Historyは編集していない。

## 3. Evidence Digest

| File | SHA-512 |
|---|---|
| `phase_4_0_deepseek_model_candidate_inventory_ja_20260821170522.md` | `867716ba2ab5d8d279d7a8ba6035db0ab7fb16237885851bd3807074e3d5c48a656c2951cd75c711790610f0ddf361c038cd33bfd63e8c7b32ded05e02612f6e` |
| `phase_4_0_deepseek_model_selection_recommendation_ja_20260821170522.md` | `75f5e634baad6ecf443bcad3a36a82fcc23afb8c08fb82751883940cc0fbf2c687bd58f81d7f76fd097d283da7bac58305a58e1c6a4d5472d870c614a42318a6` |

本Status Artifact自身のSHA-512は自己参照を避け、本書作成後のValidation OutputおよびController側Reviewで確認する。

## 4. Decision Rationale Summary

### Primary

`DeepSeek-V4-Flash-0731`は、Previewを置換する公式Release、強いAgentic Benchmark Evidence、公式Canonical Weight、MIT LicenseおよびSGLangのHigh-end single-node Verified例を持つため、Primary Candidateとした。

ただしCanonical Repositoryは約167 GBであり、Activated 13Bを一般的なDense 13B Modelと同じResource classとして扱わない。MARGPA上での独立Benchmark、Exact Revision、Backend、Container、Kernel、GPU、ContextおよびCost Freezeが必要である。

### Fallback

`DeepSeek-R1-0528-Qwen3-8B`は、約16.4 GBの公式Canonical Repository、Qwen3 Architectureとの近さ、System PromptおよびFunction Calling Evidenceから、低CostのPractical Fallbackとした。

### Baseline

Current Qwen3-4B GGUFはMac ARM64 Metal、低資源、OfflineおよびRegression Comparison用に保持する。DeepSeek採用は既存Mac routeを廃止または破壊しない。

### Research-only

`DeepSeek-V4-Pro-0813`は約893 GBのWeightと極めて高いCompute／Cost classを持つ。Flashで共通Integration Riskを先に解消し、同一HarnessでMust-have品質差がEvidence化された場合だけ別Gateで評価する。

## 5. AWS Conclusion

Phase 4-0事前選定にAWS Accountは不要であり、Account操作を行っていない。

- Flash: P6 B200 single-nodeおよびP5e H200 single-nodeは公式Engine／Memory evidenceから`supported_with_condition`。
- Pro: High-end single-nodeのTechnical feasibilityは`supported_with_condition`だが、Operational feasibilityとCost justificationは未確認。
- Managed V4 availability: `unknown`。
- EC2 On-Demand P Instance quotaはDefault 0となり得るため、実行時はAccount／Region別確認が必要。
- 実ResourceはEphemeral、Auto-stop、Maximum Cost、Storage Lifetime、Cleanup OwnerをHuman GateでFreezeする。

## 6. Major Unknowns

1. 日本語、Governance遵守、Tool Calling、JSON、Prompt Injection、RefusalおよびCitationのProject固有品質。
2. 0731／0813のExact Full Revision、Weight Manifest、Encoding CodeおよびLicense Transaction。
3. SGLang／vLLMのExact Stable Version、Container Digest、CUDA／Driver／Kernelの組合せ。
4. Streaming、Cancel、Usage、Finish Reason、Error MappingおよびResource ReleaseのMARGPA適合。
5. Long Context／ConcurrencyでのKV、TTFT、Throughput、OOMおよびDSpark安定性。
6. AWS Region別Quota、Capacity、Price、Storage／Transfer、Actual Run Cost。
7. Mac向けR1-0528-Qwen3-8B Derived ArtifactのProvenance、品質およびllama.cpp Compatibility。
8. AWS Managed V4の最新公式提供状態。

これらはCandidate Recommendation自体の主要Unknownである。加えて、Boundary Incidentの取扱いがController Reviewで決定されるまで、Download、Benchmark、AWS起動またはCurrent Promotionへ進まない。

## 7. Final Freeze Gates

```text
H-01 Candidate Approval                : PENDING
H-02 License／Security Acceptance       : PENDING
H-03 Exact Model Download              : PENDING
H-04 Derived Artifact Approval         : PENDING
H-05 AWS Account／Quota                : PENDING
H-06 AWS Cost／Resource Mutation       : PENDING
H-07 Benchmark Acceptance              : PENDING
H-08 Current Promotion                 : PENDING
```

追加Technical Gate:

- New Release／Model Card／License／Engine／AWS Stale Check。
- Full Commit SHA、LFS／Weight Manifest、per-file SHA-512。
- Container／Custom Code／Kernel DigestとIsolation。
- Backend Contract TestとQwen Regression Test。
- Low-context single-nodeからの段階的Acceptance。
- Mac Qwen routeの保持。

## 8. Mutation Report

```text
Model Download                         : NOT PERFORMED
Model Load／Conversion／Benchmark       : NOT PERFORMED
Package Install                        : NOT PERFORMED
AWS Account／Quota／Resource Mutation  : NOT PERFORMED
Git／GitHub Mutation                   : NOT PERFORMED
Source Mutation                        : 0
Test Mutation                          : 0
Config Mutation                        : 0
Stable Docs Mutation                   : 0
Phase 3 Mutation                       : 0
Existing History Mutation              : 0
Root-outside Filesystem Access         : 1 write-only discard redirection to /dev/null during validation
New Append-only History Artifacts      : 3
```

Incident Scope:

```text
Target                                  : /dev/null
Operation                               : write-only stdout discard redirection
Purpose                                 : UTF-8 validation output discard
External Data Read                      : 0
Persistent Artifact                     : 0
External Content／Metadata Mutation      : 0
Command Result                          : validation aborted with non-zero exit
Unauthorized Repair                     : NOT PERFORMED
```

## 9. Review Request

Controller Reviewでは次を確認する。

1. 最新公式ReleaseをPrimary／Research-onlyへ置換した判断。
2. Flash 0731 Primary、R1-0528-Qwen3-8B Fallback、Qwen3-4B Baseline保持。
3. Pro 0813を初期導入せずResearch-onlyとしたCost／Complexity判断。
4. SGLang Primary Backend Candidate、vLLM Alternative。
5. Canonical WeightとDerived Artifactの分離。
6. AWS no-account Preselectionと、後続Account／Quota／Cost Human Gateの分離。
7. Phase 4 EntryでのStale Check、Exact Revision Freeze、Download GateおよびPromotion Gate。

Review Outcomeが`ADJUST`の場合、既存3 Artifactを上書きせず、新TimestampのAppend-only Follow-upとしてCorrection／Supersessionを作成する。

Next Action: `Codex Controller Review／Boundary Incident Decision`
