# DeepSeek Local Artifact保持／V4 Flash実行可能性 予約事項

```yaml
document_id: deepseek_local_artifact_retention_and_v4_flash_feasibility_reservation_20260823145813
status: planned_work_retention_decision_deferred
recorded_at: 2026-08-23 14:58:13 JST
scope: deepseek_local_model_artifacts
decision_authority: user
model_mutation: none
deletion_authority: not_granted
```

## 1. 目的

DeepSeek-R1-0528-Qwen3-8Bの量子化完了後に残ったCanonical Source、Q8_0 IntermediateおよびQ4_K_M Artifactの保持方針と、DeepSeek-V4-Flash-0731を現Macで量子化・実行できるかの現時点判断を、将来忘れないための予約事項として残す。

本書は削除、移動、追加量子化、Model Load、BenchmarkまたはPromotionの実行指示ではない。Model FileへのMutationは0である。

## 2. DeepSeek 8Bの現状

```text
Official Repository:
deepseek-ai/DeepSeek-R1-0528-Qwen3-8B

Exact Commit:
6e8885a6ff5c1dc5201574c8fd700323f23c25fa

Hugging Face Canonical Root:
約16.4 GB

Q8_0 Intermediate:
8,709,517,376 bytes

Q4_K_M Final Artifact:
5,027,782,720 bytes

Preserved Failed Partial:
5,955,648 bytes

Controller Review時の空き容量:
73,072,708 KiB（約69.7 GiB）
```

RuntimeでQ4_K_Mだけを使用する場合、Hugging Face Canonical SourceとQ8_0 Intermediateは実行時に必須ではない。

ただし、現Q4_K_MはQ8_0 Intermediateから`--allow-requantize`で作成されており、実用品質は未確認である。F16／BF16等からの直接量子化より品質が低下する可能性があるため、少なくともMac上のLoad、Inference、日本語、Governance／Judge用途およびQwen比較が終わるまでは、Canonical SourceとQ8_0 Intermediateを保持する。

## 3. 当面の保持判断

```text
Immediate Cleanup             : NOT REQUIRED
Canonical HF Source           : RETAIN FOR NOW
Q8_0 Intermediate             : RETAIN FOR NOW
Q4_K_M Final                  : RETAIN
Failed Partial                : RETAIN UNTIL USER DECISION
Toolchain／Manifest／Logs      : RETAIN AS REPRODUCIBILITY EVIDENCE
Automatic Cleanup             : PROHIBITED
```

Userは、現時点では約60GB以上の空きが残っていれば当面の作業に支障はないと判断し、急いで削除しない方針を選択した。

量子化Taskで用いた64 GiB Floorは、そのTaskのMaterial Write開始可否を決めるためのContractである。今後の全作業へ自動的に同じFloorを転用せず、実作業ごとに必要容量を再計算する。

## 4. 将来の削除候補と順序

容量整理が必要になった場合も、自動削除せず、Userの明示判断後に次の順序で検討する。

1. 失敗Partial：約6MB。Evidenceとして不要とUserが判断した場合の最初の候補。ただし容量効果は小さい。
2. Q8_0 Intermediate：約8.7GB。Q4_K_MのRuntime／品質Acceptance後、Exact Current Recipeの即時再現を不要と判断した場合の候補。
3. Hugging Face Canonical Source：約16.4GB。Direct Quantizationや別Schemeを行わないと判断した後の候補。Exact CommitとManifestを保持すれば再Download可能だが、Network時間とRemote Availability Riskが戻る。
4. Q4_K_M Final：約5.0GB。Modelを使用しない、または別Artifactへ正式に置換した場合だけ候補。

Toolchain、Manifest、Digest、Completion EvidenceおよびController Acceptanceは、Artifact再取得／再生成の入口として小容量のため原則保持する。

削除前には、Exact Target、保持するEvidence、復旧方法、必要ならBackup／Digestを確認する。Directory単位の推測削除は行わない。

## 5. DeepSeek-V4-Flash-0731の現状

```text
Official Repository:
deepseek-ai/DeepSeek-V4-Flash-0731

Exact Commit:
7872f01b1d1fe23eabc4c98b48bffcef5a386062

Downloaded Payload:
166,898,661,074 bytes

Model Files:
74

Safetensors Shards:
48
```

V4 FlashはActivated Parameterだけを見て小型Modelとして扱ってはならない。RuntimeにはModel全体のWeight保持とKV Cache等の追加Resourceが必要である。

Q4相当のDerived Artifact Sizeは、総Parameter、Quantization Scheme、Tensor Type内訳およびConverter対応に依存するため未実測である。単純理論値でも100GBを大きく超える可能性があり、現在の約69.7 GiB空き容量では、元データを保持したまま量子化Artifactを新規作成する容量条件を満たさない。

Memoryについても、現MacでV4 Flashの全WeightとRuntime Overheadを安全に保持・実行できるEvidenceはない。Activated Parameterが小さいことは、全Weightを小容量Memoryで保持できることを意味しない。

したがって現時点の判断は次である。

```text
V4 Flash Canonical Download : PRESERVED
Local Quantization          : NOT CURRENTLY FEASIBLE
Local Runtime Load          : NOT CURRENTLY FEASIBLE／NOT VERIFIED
Current Mac Acceptance      : NOT PLANNED NOW
Cloud／Large-memory Host     : FUTURE CANDIDATE
Immediate Deletion          : NOT REQUESTED
```

## 6. V4 Flashの将来Route

V4 Flashを扱う場合は、次のいずれかを別Gateで設計する。

1. 十分なStorageとMemoryを持つ別Machineで量子化・Loadする。
2. Cloud GPU／Large-memory Instanceで短時間のLoad／Inference／Benchmarkを行う。
3. 公式または信頼できるDerived Artifactを、License、Provenance、Digest、Engine Compatibility確認後に使用する。
4. Local保持をやめ、Exact Commit／Manifestを残して必要時に再Downloadする。

Cloud利用はCost、Quota、Region、Engine、Container、Securityおよび停止忘れRiskを伴うため、Modelが既にDownload済みであることから自動開始しない。

## 7. 再判断Trigger

次のいずれかが発生した場合、本予約事項を再Openする。

- DeepSeek 8B Q4_K_MのRuntime／品質Acceptanceが完了した。
- Direct F16／BF16→Q4等の再量子化が必要になった。
- Project Disk空き容量が今後の作業Gateを満たさなくなった。
- V4 Flash用のCloud／Large-memory Hostを用意する具体計画が成立した。
- Model ArtifactsのBackup／Archive Policyを正式化した。
- Exact Modelを今後使用しないとUserが明示判断した。

## 8. Current Decision

```text
DeepSeek 8B Source Cleanup : DEFERRED
DeepSeek 8B Q8 Cleanup     : DEFERRED
DeepSeek 8B Q4 Runtime Test: FUTURE REQUIRED
DeepSeek V4 Local Test     : DEFERRED／CURRENTLY INFEASIBLE
Current Disk Policy        : OBSERVE／NO URGENT CLEANUP
User Action Required Now   : NONE
Model Mutation             : 0
```
