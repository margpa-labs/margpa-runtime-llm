# Phase 6 Governance Semantic Runtime難度回顧／新Phase 10移管

```yaml
document_id: phase_6_governance_semantic_runtime_difficulty_retrospective_and_phase_10_transfer_20260829175551
document_state: final
language: ja
created_at: 2026-08-29 17:55:51 JST
authority_owner: Nazuna Research
phase: phase_6
decision: incomplete_semantic_and_dedicated_provider_scope_transferred_to_new_phase_10
```

## 1. 結論

Phase 6は旧Phase 6〜9の中でも本質的に難度が高いPhaseだった。ただし長期化の全てを技術難度へ帰属させない。MARGPA固有のGD Semantic Runtime、独立Judge／Guard Model、Lifecycle／Budget／Evidence／Repairの同時整合は研究開発級だった一方、PoC／MVP停止線を越えたHardening、実画面確認前の理論完全性追求、Provider間Rework反復およびControllerの優先度判断失敗が、Cost、時間、AI利用可能量およびUser負担を増幅した。

## 2. 本質的に難しかった部分

GD Semantic接続は、109件をJudgeへ単純転送する作業ではない。

```text
Declarative GD Rule
→ Turn時点のDefinition／Rule Selection
→ Evaluation CriterionへのCompile
→ Deterministic／Model Evaluator Dispatch
→ Pass／Deviation／Unknown／Deferred分類
→ Criterion Evidence
→ Conflict／Priority／Budget解決
→ OBSERVE／ENFORCE／Repair判断
→ Recording／Audit／Presentation
```

この経路には、Frozen Turn Snapshot、Provider Identity、Configured／Active／Executed分離、Timeout、Cancel、Late Result拒否、Repair／Rejudge、Request CorrelationおよびRole別Lifecycleも必要になる。一般的なPrompt Guardまたは単体LLM-as-a-Judge接続より、宣言的Governanceを実行可能にするCompiler／Runtimeを新規に構成する仕事に近い。

MARGPAはARGD、DAGDその他の複数GD系を、Coreへ特別扱いせず交換可能なGovernance Pointへ接続する。GD定義群と通常Chat、RAG、Agent、Tool、Constitutionの疎結合な同時実行を前提とする類似実装は少なく、既製の正解や定番Architectureをそのまま採用できない。

Selene／Qwen3GuardもGGUF Loadだけでは成立しない。Main Modelと独立したProvider、Model固有Prompt／Output Contract、Mac Local資源制約、Mode Activation、Atomic Provider Switch、Drain／Unload、Timeout／CancelおよびEvidence Identityを整合させる必要があった。

## 3. 難度を不必要に増幅した進行Failure

- 個人PoC／MVP／Portfolioであるのに、Enterprise／Product-gradeの完全性へ停止線をずらした。
- User実画面Acceptance前に、Testと内部Reviewだけで一発完全合格を狙った。
- Closure BlockerではないTOCTOU、Manifest、Lifecycle Hardening等までCurrent Reworkへ繰り返し昇格した。
- Provider間の実装、Review、Reworkを過度に反復し、同じFinding数のままCostを消費した。
- 大量Test Pass、正確なFailure表示または基盤成立と、中心機能の実用成立を混同した。
- Controllerが技術重大度、現在優先度、Closure Blockerおよび延期可能性を十分に分離しなかった。

したがってPhase 6の長期化は、`研究対象としての高難度`と`進め方の失敗`の複合結果である。

## 4. Phase 6で成立した再利用基盤

Phase 6は無成果ではない。次は新Phase 10で再利用する。

- Judge／Guard Provider RegistryとConfigured／Active／Executed状態Contract。
- Role Lifecycle、Load／Drain／Unload、Budget、Deadline、Cancel、Tracked Worker。
- Judge／Repair／RecordingのRequest相関とFailure Presentation。
- Rule／Pattern Base Guardrail。
- Built-in Deterministic JudgeのPort／Baseline。
- GD Definition Selection、Compiler入口、Semantic Criterion／Evidence型。
- Mode OFF／OBSERVE／ENFORCE、Provider選択およびUI／API基盤。

これらは完成したDedicated Model／Semantic Governanceを意味しないが、Phase 10でゼロから作り直す対象でもない。

## 5. Phase 7〜9の暫定運用

新Phase 10まで、次をPoC Baselineとして使用する。

```text
Guardrail:
  Default = Built-in Rule／Pattern Base
  Dedicated Qwen3Guard = 未使用／未完成

Judge:
  Default = Built-in Deterministic、または不要時None／OFF
  Dedicated Selene = 未使用／未完成

GD Semantic:
  未評価CriterionをPassへ捏造しない
  Deferred／Not Applicable／Unknownを正確に保持する
```

Built-inやRule-basedがDedicated Modelと同等であるとは主張しない。不要な推論Costを避けるため、Mode既定値とRuntime Defaultは各Phaseの実験目的に応じてOFF／Noneを選択できる。

## 6. 新Phase 10への正式移管

次を新Phase 10の`Governance Semantic Runtime Completion Program`へ移管する。

1. Selene Dedicated Judgeの実Artifact Load／Inference／Prompt／Strict Output Contract。
2. Qwen3Guard Dedicated Guardの実Artifact Load／Inference／Target別Output Contract。
3. ARGD／DAGDを含むGD Semantic RuleのLive Criterion評価。
4. Built-in Evaluatorの適用可能Criterionと限界の再定義。
5. Independent JudgeによるJudge／Repair／Rejudge Golden Path。
6. Main Governance Semantic ENFORCEとConflict／Priority／Budget。
7. Dedicated Model、Built-in、Noneを比較できるProvider構成実験。
8. Real Hardware／Latency／Memory／Model同時常駐のProfile検証。
9. User実画面AcceptanceによるConfigured／Active／Executed／Evidence一致確認。

Phase 10着手時は、Phase 6 Sourceと未解決RegistryをAs-built Baselineとして読み、成立済み基盤を再実装しない。

## 7. Constitution層への教訓

ConstitutionはGDと同様に、単なるPrompt追加ではなく、Revision、View、Authority、Priority、Conflict、EvidenceおよびEnforcementを持つため高難度になる可能性が高い。

Phase 8では疎結合なConstitution Port／View／OFF・OBSERVE・限定ENFORCEのResearch Previewに留める。Phase 10 READYの全Docs統合とPADG Package後に本格Constitutionを編纂し、GD群とのConflict／Priority／Enforcementを段階的に検証する。18系統GDとConstitutionを最初から全てENFORCEせず、基盤、OBSERVE、限定ENFORCEの順に進める。

ハードコードは可能な範囲で回避し、安定ID、Versioned Definition、Registry、Port／AdapterおよびCapability Metadataによる疎結合を維持する。

## 8. Closure／Claim境界

- Phase 6は特殊最小Closureのままであり、技術的完全合格へ変更しない。
- 新Phase 10移管は未解決の隠蔽または解決済み主張ではない。
- Phase 7〜9は暫定Baselineで進め、Dedicated Provider／Semantic Enforcementを依存条件にしない。
- 実画面Test前に理論完全性を追わず、中心経路が動き、Data破損や虚偽表示がなく、次Phaseへ渡せるPoC／MVP停止線で止める。
