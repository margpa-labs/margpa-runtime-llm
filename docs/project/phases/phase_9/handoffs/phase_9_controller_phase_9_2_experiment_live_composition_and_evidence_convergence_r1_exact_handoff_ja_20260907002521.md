# Phase 9-2 — Experiment Live Composition／Evidence Convergence R1 Exact Handoff

```yaml
document_id: phase_9_controller_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_handoff_20260907002521
document_type: exact_rework_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 00:25:21 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_20260906225104.md
controller_review: phase_9_2_controller_long_run_return_independent_review_and_r1_rework_decision_ja_20260907002521.md
maximum_claim: P9_2_R1_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 1. Objective

Phase 9-2 Long Runで作成したFixture／Domain基盤を保持し、現行のFixture-only Demoを次へ収束させる。

```text
Frozen Case／Variant／Effective Config
  -> Experiment-scoped execution
  -> Existing Production Turn／Component composition
  -> Actual stage evidence
  -> Metric／Evaluation／Comparison
  -> Restart-readable result
  -> Minimal UIで事実どおり表示
```

新しい中央Runtimeを作らず、Phase 9-1で成立したMain／Judge／Guard／Main Governance／RAG／Repair／Recordingの疎結合性を維持する。

## 2. Primary Inputs

1. `docs/project/phases/phase_9/history/operations/phase_9_2_controller_long_run_return_independent_review_and_r1_rework_decision_ja_20260907002521.md`
2. `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_20260906225104.md`
3. `docs/project/phases/phase_9/operations/phase_9_2_experiment_multi_governance_execution_design_and_work_breakdown_ja.md`
4. 現行`modules/experiment/`、`adapters/experiment/`、Web Route／Frontend／Test。
5. Phase 9-1 Production Compositionと実機Golden PathのAs-built Source／Test。

全Historyの無差別再読は行わない。

## 3. Non-negotiable Architecture

- Experimentは既存Componentの上位Research Adapterであり、既存ComponentからExperimentへ逆依存させない。
- Component OFF／不在／Unsupportedの場合、当該ComponentだけCall／Mutation／Evidence／Authority 0とし、他Componentを止めない。
- Fixture MatrixとProduction Turn Adapterを別Adapterとして分離する。Fixtureの部品呼出しを実Turn成立と呼ばない。
- Production実行でMain／Judge／Guard／Repairを無理に個別Model Callとして再実装しない。既存の実Turn Compositionを「1 Variant Run」として包む。
- Experiment RunのためにUserの通常Chat設定、Conversation、Current Result、Local Corpusまたは既存Evidenceを無言Mutationしない。
- 実行前にCase／Variant／Config／Provider Identity／BudgetをFreezeし、実行中のUI設定変更をRunへ混入させない。
- 個人名をCanonical Caseに入れない。

## 4. R1-WU-01 — Identity／Case／Config Correlation

### 4.1 Plan／Run契約

- `ExperimentPlan`に少なくとも`case_id`、`case_revision`、Case DigestおよびVariantごとのFrozen Effective Configuration参照／Digestを保持する。
- `VariantRun.request_id`を実行Runで必須とし、APIは生成または受理した値をResponse／Persistence／Traceに返す。
- `VariantRun`かRaw Evidenceから、Experiment／Plan／Case／Variant／Run／Request／Config Snapshot／Artifact／Definition／Provider Evidenceを一意に相関できるようにする。
- Provider／Artifact Identityを単1 Fieldに潰さず、実行したComponent／StageごとのConfigured／Active／Executed／Evaluated／Artifact／Backend／VersionをEvidence参照で分離する。
- Unknown／Unavailableは`None`の成功値ではなく、意味あるTyped Stateとする。

### 4.2 Persistence

Plan、Case ManifestまたはCase Digest、Config Snapshot、Run、Raw Evidence、Evaluation、ComparisonがRestart後も同じIdentity Chainで読めること。

## 5. R1-WU-02 — Frozen Plan Execution／Invariant修正

- Runは必ずPersistenceから読んだ`ExperimentPlan.variant(variant_id)`を実行する。Module Global Presetの再検索を実行正本にしない。
- PresetはPlan作成時のInputに限定し、実行時はFrozen Planからのみ読む。
- Duplicate Variant ID、未知Case／Variant、Case Digest不一致、Config Digest不一致を呼出し前Typed Rejectにする。
- `ComponentSelection.mode is None`は、現行Contractの説明どおりOFF／AbsentとしてCall 0にする。別の意味に変える場合はContract／UI／Testを一括で明示的に変えるが、黙ってCall 1にしない。
- `ExperimentPlanBudget` fieldsに正の境界を設け、`max_variant_runs`、Deadline、Stop Policy、Execution OrderをRuntimeで強制する。

## 6. R1-WU-03 — Production Turn Variant Adapter

### 6.1 二層Adapter

```text
Fixture Component Runner
  -> 疎結合Matrix／Failure Injection／Call 0の機械検証

Production Turn Variant Adapter
  -> Existing Production Compositionの1 Turnを一つのVariant Runとして実行
  -> 既存Stage EvidenceからComponent別Call／Action／FailureをProjection
```

Production AdapterはMain／Judge／Guard／Repairの内部実装を再実装せず、Phase 9-1のComposition／Correlation／Recording／Cancellationを再利用する。

### 6.2 Config Isolation

実Sourceを調査し、次を満たす最小方式を選ぶ。

- Experiment-scoped Controller／Runtimeを構成できるなら、通常WebRuntimeと別Instanceにする。
- 別Instanceが過大で、既存のRequest-local Frozen Snapshotを注入できるなら、専用Adapter境界だけで使う。
- Global Modeの一時切替→実行→復元で実装する場合は、無言変更、並行Chat混入、復元失敗のRiskがあるため、原則不採用とする。

どの方式も成立しない場合、Fixtureのみで完了を主張せず、正確なAs-built BlockerをTrue Stopで返す。

## 7. R1-WU-04 — Case Evaluation／Comparison結線

- Actor／Turn ExecutorへFrozen Case Input／Evidence／Expected Observationを渡す。
- Freshness、RAG Grounding、Strict NO_HIT、Belief Revision、False Improvementの分類を実行RunのRaw Evidence／Metric／Evaluation Observationへ収束させる。
- `build_comparison_report()`をExperiment Service／APIへ結線し、Run追加後に同じCase RevisionのReportを生成／再生成／保存できるようにする。
- Evaluation Observationが別のRun／Caseを参照する場合はTyped Rejectにする。
- FrontendのComparisonはRun State一覧だけではなく、Case、Frozen Variant差、Runtime State、Metric、Human／LLM／Deterministicの未実施を含む別Identity、Failure、Raw Evidence Pointerを表示する。
- Human Review未実施をPASSにしない。

## 8. R1-WU-05 — Async Lifecycle／Cancel／Failure

- Run開始APIは`running`を返し、実行をTracked Workerへ渡す。FrontendがIn-flight Runを一覧し、Cancelで実際のCancellation Tokenへ到達できるようにする。
- Actor／Turn例外、Timeout、Unavailable、CancelをTyped Terminal State／Reasonへ収束させ、`running`のまま放置しない。
- Terminal二重Publish、Cancel後Late Result、Restart後の不正Publisherを拒否する。
- Worker／Model Lease／Experiment-scoped RuntimeはTerminal／Shutdown後に解放する。
- Async化が今Roundで過大となる場合、Cancelを実装済みと主張せず、Exact Blockerとして返す。

## 9. R1-WU-06 — Verification／Real Model Gate

### 9.1 Fixture／Integration

少なくとも次をHard Assertする。

1. 同じRevisionを持つ異なるCaseが混同されない。
2. Plan作成後にPresetが変わってもFrozen Variantを実行する。
3. `mode=None`／OFF／Absent／Unsupportedは当該Actor Call 0。
4. Case／Config／Plan Digest不一致はActor Call 0。
5. `max_variant_runs`／Deadline／Stop Policy／Execution Order違反はActor Call 0。
6. Actor例外はRun FAILED、CancelはCANCELLED、Late Publishは拒否。
7. ComparisonがRun／Case／Observationの不一致を拒否する。
8. FixtureとProductionのEvidenceに`fixture_only`／`production`の実Identityが正しく残る。
9. Experiment OFF／不在時に通常Chat／Judge／Guard／RAG／Repairへ影響0。
10. UIはFixture Resultを実Model Resultと表示しない。

Sabotage-regressionは上記のCritical Boundaryに限定し、同じ観点を過剰反復しない。

### 9.2 Real Model — Candidate前必須

Fixture／Static／Production-fixture Composition完了後、次の代表Variant Runを逐次で最大3回実行する。User Manual Candidateには必須である。

```text
1. Main Qwen only baseline
2. Main Qwen + Gemma Judge／Repair representative path
3. Main Qwen + Qwen3Guard representative path
```

実際のCase／Config／Provider／Stage／Call／Output／Evaluation／Comparison Evidenceが一つのExperiment Identity Chainで保存されること。実機で一部Provider品質がFAILしても、Typed Failureと比較行が正しければ事実どおり記録する。

Selene／DeepSeek Judgeは実行しない。Memory Pressure、Swap急増、Unload失敗またはProcess残存があれば追加Runを止め、Partial／True Stopで返す。

### 9.3 Canonical Verification

- Focused Unit／Integration。
- Backend Non-model Full Suite 1回。
- Ruff。
- Canonical Mypyと既存43 errors／4 files Baseline差分。
- Frontend Test／Typecheck／Lint／Build。
- 実Model最大3 Run。
- 実行前後のProject所有Process／Port／Unload状態。

## 10. Internal Review

Review AはIdentity、Frozen Plan、Authority、Component Independence、Variant Isolation、Production Composition、Persistenceを見る。

Review BはMetric Oracle、Case参照整合、False Success、Call 0、Cancel／Late Result、Strict／Progressive、Comparison UIの真実性を見る。

同一観点の無限Reviewは行わず、Confirmed Critical／Major／MVP Blockerだけを有界修正する。

## 11. Scope／Authority Boundary

- Phase 9-1のProvider固有問題を修正しない。
- Selene／DeepSeek Judgeを実行しない。
- Phase 9-3／Phase 10へ進まない。
- 右Panel／Settings／Sidebar／Main Chatの大改造をしない。
- Network、Model Download、Package Install、Project Root外Mutationを行わない。
- Git `add`／`commit`／`push`／`stash`／`reset`／`clean`を行わない。
- Phase Index、Current未解決Registry、Roadmap、Technology Selectionを編集しない。
- Existing Handoff／Return／Historyを上書きしない。
- Existing Dirty Working Treeを保持する。

## 12. Exact Return／Recovery

必ず別々の新規Pathへ両方作成する。

```text
docs/project/phases/phase_9/handoffs/
  phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_ja_<timestamp>.md

docs/project/phases/phase_9/history/index/
  phase_9_2_experiment_live_composition_and_evidence_convergence_r1_recovery_ja_<timestamp>.md
```

ReturnにはR1-WU-01〜06の個別状態、Before／After、Files Changed／Not Changed、Acceptance Mapping、Fixture／Production-fixture／実Model Evidence、Review A／B、Open Findings、完全なGit／Network／Root外Mutation状態を含める。

最大Claimは`P9_2_R1_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`まで。Phase 9-2 Complete／Phase 9-3開始／Phase 9 Closureを自己承認しない。

## 13. True Stop

次の場合だけ、到達点とBlockerをExact Partial Returnに書いて停止する。

- 実TurnをExperiment-scopedに実行するために、最上位疎結合Invariantの破壊が必要。
- User Data／Existing Dirty Treeを安全に保持できない。
- 新Network／Cost／License／Model取得／Root外Mutation Authorityが必要。
- 実Modelを安全にUnload／停止できない。
- Phase 9-1 Golden Pathが壊れ、局所修復で回復できない。

単一Fixture Failure、Minor UI、既知Mypy Baseline、Provider固有回答品質はTrue Stopではない。
