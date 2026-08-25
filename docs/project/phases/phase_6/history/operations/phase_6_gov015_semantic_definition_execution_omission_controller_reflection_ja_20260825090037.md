# Phase 6 Semantic Definition実行脱落に関するController反省・是正記録（Append-only、P6-GOV-015）

```yaml
document_id: phase_6_gov015_semantic_definition_execution_omission_controller_reflection
status: append_only_governance_correction_and_controller_reflection
phase: phase_6
finding_id: P6-GOV-015
owner: プロジェクト責任者兼設計統括者役
recorded_at: 2026-08-25 09:00:37 JST
trigger: user_mac_manual_acceptance_and_requirement_lineage_recheck
finding_class: controller_design_scope_review_and_closure_failure
severity: major
phase_6_closure: blocked
supersedes_nothing: true
```

## 1. 結論

Phase 4／5でPhase 6の責務として明示していたARGD／DAGD Semantic Ruleの実行接続を、Phase 6のExact
Design、実装、Independent Reviewおよび複数回のReworkで完了させなかった。Userの明示的な延期承認、
技術的不可能性または外部Blockerは存在しない。

これはExecutorだけの実装漏れではない。Codex ControllerがPhase間RequirementをPhase 6 Freezeへ正しく
継承せず、Infrastructureの完成、Deferred表示の正確さおよび大量Test Passを、MARGPAの中心機能が
実行可能になったことと混同した設計・Review・Closure判断の失敗である。

```text
P6-GOV-015: OPEN FOR REWORK
Classification: DESIGN / SCOPE / REVIEW / FALSE-CLOSURE-PROXIMITY FAILURE
User-authorized Deferral: NO
Phase 6 Closure Blocker: YES
```

## 2. 履行すべきだった約束

既存の正本には次が残っている。

- Public RoadmapはPhase 4 Semantic Ruleを`Deferred to Phase 6`とした。
- Phase 4 Manual Acceptanceは109件の意味Ruleを不実なPassへせずDeferred表示し、意味的Judge／Repairを
  Phase 6の責務とした。
- Phase 5はHallucination、知ったかぶり、根拠なき断定、意味的品質Judgeおよび反復RepairをPhase 6へ
  明示的に送った。
- Projectの中心Conceptは、MARGPA Governance DefinitionsをRuntimeで選択、評価、判断、Actionおよび
  Evidenceへ接続することである。

したがってPhase 6は、汎用Judge Portを置くだけでなく、少なくとも次を成立させる必要があった。

```text
Governance Definition
→ Semantic Descriptor
→ Evaluator／Judge Criteria
→ Request Evaluation
→ Deviation／Unknown／Pass
→ Action Resolver
→ Repair／Final
→ Evidence
```

## 3. 実際に行った誤ったScope縮小

Phase 6では、Evaluation Identity、Criteria、Result、LLM Judge Port、Repair、Cancellation、Recording、
Runtime Status等の広い基盤を実装した。一方、Live Judgeは固定Criteria
`correctness／safety／coherence`を使用し、ARGD／DAGD Semantic DescriptorをCriteriaへ変換しなかった。

その結果、実画面では各Turnで109件が次のまま残った。

```text
Selected Rule数: 109
Deferred（意味評価待ち）: 109
```

後続Reworkでは、この未接続を直す代わりに「別ComponentのJudgeはDeferred Ruleを実行可能へ昇格しない」
というCurrent LimitをUIへ正確に表示した。これはFalse Claimを防いだ点では正しいが、元のPhase 6責務を
満たしたことにはならない。

## 4. なぜ見逃したか

### 4.1 Requirement LineageをFreezeへ継承しなかった

Phase 6 Requirements／Architectureを作る際、Phase 4／5から送られた明示的なDeferred項目を、Acceptance
IDへ一対一で継承しなかった。新しいFrozen Packageが上位Roadmapの未完了Requirementを暗黙に消せるかの
ように扱った。

Frozen Scopeは変更防止の手段であり、User承認なしに上位Requirementを削除する権限ではない。

### 4.2 Infrastructure CompletionをOutcome Completionと混同した

次の成立を過大評価した。

- Judge／Repair Portが存在する。
- Structured ResultとFailure Contractが存在する。
- Cancellation／Deadline／RecordingがTestされている。
- Main-self Judgeが実Model Callできる。
- 109件をDeferredとして正直に表示できる。

これらは必要な基盤であるが、MARGPA Definitionが実際に回答を評価・修復したEvidenceではない。

### 4.3 大量Test Passを核心Acceptanceの代理にした

Backend／Frontend Test、Ruff、Mypy、BuildおよびReal Model Smokeが多数PASSしても、Testが核心の欠落を
表現していなければFailureは検出されない。Userが実画面で「天音かなた」の明白な誤答を確認するまで、
`accept／0.95`の自己承認と109件Deferredの組合せをClosure Blockerとして扱えなかった。

### 4.4 Reworkの局所最適化

複数Reworkでは、Concurrency、Cancellation、TOCTOU、Recording Exactly-once、Path、Evidence Grade等の
実在する重要問題を直した。しかし局所Findingを閉じることへ集中し、Project名と中心目的に直結する
「MARGPAのGDが実際に効くか」を毎回の最上位Gateへ戻さなかった。

### 4.5 Honest UnsupportedをCompletionと取り違えた

未実装をPassへ捏造せずDeferred／Unavailableと表示することはGovernance上必要である。しかし、正確な
未実装表示は未実装そのものを解消しない。Controllerは「虚偽表示を直した」と「機能を完成させた」を
分けるべきだった。

## 5. 責任区分

ClaudeまたはCodexの実装Executorは、Frozen Handoffに従って大量の基盤実装とReworkを行った。Executorの
局所的な逸脱やFalse Claimとは別に、今回のSemantic Definition脱落については次をFreezeし、Reviewし、
Closure候補へ近づけたControllerが主たる責任を持つ。

```text
Requirement継承: Controller責任
Exact Design Scope: Controller責任
Acceptance Matrix: Controller責任
Independent Review: Controller責任
Closure判定: Controller責任
User実画面での最終発見: Controller事前検出失敗のEvidence
```

Executorへ責任を転嫁せず、Cross-provider／Agent Automationの成功評価と今回のController Failureを分離する。

## 6. 影響

1. `ENFORCE`表示があるのにMARGPA Semantic Ruleが回答品質へ介入せず、False Assuranceを生んだ。
2. Qwenの誤答を同じQwenが`accept／0.95`と自己承認した。
3. 追加Model CallによりLatencyとResourceを増やしながら、独立Judgeとしての価値を得られなかった。
4. Userは何度も同じ明白な誤答を使って実画面検証する必要が生じた。
5. Phase 6 Closureが繰り返し遠のき、利用可能量を大きく消費した。
6. MARGPA-RUNTIME-LLMの中心機能が成立したかについて、Docsと実装の意味が乖離した。

## 7. 是正措置

### 7.1 Phase 6 Rework

- ARGD／DAGD Semantic DescriptorをNormalized Evaluation Criteriaへ接続する。
- Definition／Rule／Point／Plan／Request／Judge／Action／Repair／Evidence Identityを相関する。
- SeleneをDedicated Judge Providerとして実接続する。
- Qwen3GuardをGuardrail Providerとして実接続する。
- Main／Guardrail／Judge Providerの明示選択と`None`／Built-inを実装する。
- Main-selfは明示選択時だけ許可し、暗黙Fallbackを禁止する。
- Known ContradictionからRepair Acceptedまでの再現可能なGolden Pathを実Browserで確認する。
- 固定30秒Policy、Generic Safe FallbackおよびRecording相関不足を修正する。

### 7.2 Review Rule

今後、前PhaseからDeferredされたRequirementには次を必須とする。

1. Receiving PhaseのRequirements／Acceptance Matrixへ元文書と元記述をLinkする。
2. `Implemented／Explicitly Deferred by User／Rejected with Reason`のいずれかを付す。
3. New Frozen Scopeに存在しないDeferred Requirementを自動的に消滅させない。
4. UIがUnsupportedを正確に表示するだけではCompletionとしない。
5. Core Milestoneは、Infrastructure TestとOutcome Acceptanceを別Gateにする。
6. COMPLETE_CANDIDATE前に、Projectの中心価値を一文で問い直す。

```text
このPhaseの完成によって、Userが期待する核心能力は実際に動くか。
```

### 7.3 Manual Acceptance Rule

- 実Model、実Browser、明白な既知正解、User CorrectionおよびEvidence contradictionを早期に使う。
- Modelが偶然`needs_repair`を返すことへ依存せず、再現可能Fixtureを用意する。
- `Pass Test数`ではなく、Raw Candidate、Judge、Action、Repair、Finalの因果Chainを確認する。
- Current／Last Historical／Different Requestの状態を混同しない。

## 8. 再発防止のClosure Gate

Phase 6 Closureは次を満たすまで許可しない。

```text
Semantic Rules all blindly Deferred: NO
Dedicated Judge usable: YES
Guardrail Model usable: YES
Explicit Provider selection: YES
Implicit main_self fallback: NO
Known contradiction detected: YES
Repair golden path reproducible: YES
Reason-specific failure presentation: YES
Request-correlated recording summary: YES
User Mac manual acceptance: PASS or explicitly bounded User Gate
```

## 9. Controller Reflection

今回の最も大きな誤りは、未実装を正確に`Deferred`と表示した時点でGovernance上十分に安全になったと考え、
「なぜPhase 6でまだDeferredなのか」を最上位Requirementへ戻して問わなかったことである。

MARGPA-RUNTIME-LLMでMARGPA Governance Definitionsが意味評価へ接続されない状態は、周辺基盤がどれだけ
堅牢でも中心Milestoneの完成ではない。Userが実画面で指摘する前にControllerが検出すべきだった。

今後は、正確なFailure表示、堅牢なInfrastructureおよび大量のTestを評価しつつ、それらを核心Outcomeの
代替にしない。Phase間で送った約束はUserの明示承認なしに縮小せず、Closure判定では実際の製品挙動を
最終正本として扱う。

## 10. Current Disposition

```text
P6-GOV-015: RECORDED／OPEN FOR TECHNICAL REWORK
Phase 6: ADJUST
Phase 6 Closure: BLOCKED
Phase 7 READY: NOT STARTED
Historical Evidence Mutation: 0
Source／Test／Config Mutation by this correction: 0
Git Mutation by this correction: 0
```
