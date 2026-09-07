# Phase 9-2 — Truthful Variant Execution / Evidence R2 Exact Handoff

```yaml
document_id: phase_9_controller_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_handoff_20260907071729
document_type: exact_rework_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 07:17:29 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_ja_20260907032749.md
controller_review: phase_9_2_controller_r1_return_independent_review_and_r2_rework_decision_ja_20260907071729.md
maximum_claim: P9_2_R2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 1. Objective

R1で追加したIdentity、Persistence、Fixture Composition、Async API、Comparison UIを保持しつつ、Production経路を次の状態へ収束させる。

```text
Frozen Case / Variant / Effective Config
  -> 実際に同じVariantを実行
  -> Request相関されたActual Evidenceのみを投影
  -> Case期待によるEvaluation
  -> Restart-readable Comparison
  -> UIでFixture / Running / Production / Unknownを事実どおり表示
```

Runが終了したこと、Componentが呼ばれたこと、MutationやRepair採用が起きたこと、CaseがPASSしたことを混同しない。

## 2. Primary Inputs

1. `docs/project/phases/phase_9/history/operations/phase_9_2_controller_r1_return_independent_review_and_r2_rework_decision_ja_20260907071729.md`
2. `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_ja_20260907032749.md`
3. `docs/project/phases/phase_9/handoffs/phase_9_controller_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_handoff_ja_20260907002521.md`
4. 現行`modules/experiment/`、`adapters/experiment/`、`bootstrap/experiment_production_turn_adapter.py`、Web Route、Frontend、Test。
5. Phase 9-1のRequest-local Mode Snapshot、Judge Result、Guard Result、Runtime Governance Evidence、Recording、PresentationのAs-built Source。

全Historyの無差別再読は行わない。

## 3. Non-negotiable Architecture

- Experimentから既存Componentを上位Adapterとして利用し、既存ComponentからExperimentへ逆依存させない。
- Production RunはFrozen Variantと同じ設定を実行する。Live Runtimeの偶然の現在値をVariant名だけ変えて実行しない。
- 通常ChatのGlobal設定を無言変更→復元する方式は採用しない。
- Request-localまたはExperiment-scopedの設定境界を優先する。それが過大なら、Frozen ConfigとLive Configの完全一致をCall前に検証し、一致しないRunはTyped Call 0にする有界Fallbackを選んでもよい。ただし実行中の設定固定まで保証する。
- 実際に観測できない値は`unknown`、`unavailable`、`not_observed`または`None`にする。0、1、False、True、PASSへ変換しない。
- FixtureとProductionは別Execution Identityのまま保持する。
- Phase 9-1のMain、Judge、Guard、Governance、Repair、Recordingの疎結合契約を弱めない。

## 4. R2-WU-01 — Frozen Effective Configuration / Production Variant成立

### 4.1 Plan Identity

- Production用PlanはPlan作成時にExecution ModeとVariantごとの`EffectiveConfigurationSnapshot`を生成・保存する。
- `variant_configuration_digests` をProduction Planで空にしない。
- SnapshotにはMain、Judge、Guard、Main Governance、Definition Set、RAG、Repair、Recording、PresentationのMode / Selectorと、取得可能なProvider / Artifact / Definition Digestを分離して保存する。
- Fixture用PresetとProductionで実行不可能なPresetを混同しない。例えばMainまでOFFのFixture Matrixを、通常Conversationを使うProduction Main-only Baselineと同じ意味で表示しない。

### 4.2 Execution

- Runは保存PlanのFrozen ConfigurationをProduction Adapterへ渡す。
- 次のいずれかで、実行したMode / ProviderがFrozen Variantと一致することを保証する。
  1. Request-local Frozen Snapshotを既存Production Turn境界へ注入する。
  2. Experiment-scoped Controller / Runtimeを構成する。
  3. Frozen ConfigとLive ConfigをCall前に完全比較し、実行中の関連設定変更を拒否するLeaseの下だけで実行する。
- 不一致、Unsupported、Lease取得失敗はActor Call 0のTyped Failureにする。
- 通常ChatのConversation、Current Result、Settings、Local Corpusを無言Mutationしない。

### 4.3 Hard Assertions

- `judge-observe`を選びLive JudgeがOFF / ENFORCEなら、そのまま偽OBSERVE成功にせずTyped Call 0またはRequest-local OBSERVEで実行する。
- Plan作成後のUI Mode / Provider変更をRunへ混入させない。
- Frozen Config Digestの1 byte改変、Live Config不一致およびProvider Identity不一致をCall 0で検出する。
- 二つのVariantを同時に開始してもConfigが交差しない。

## 5. R2-WU-02 — Actual Component Evidence / Identity

- `ProductionTurnObservation`とRaw Evidenceを「呼ばれたら一律1 / True」から実Evidence投影へ変える。
- Main Model Call、Judge、Guard、Main Governance、Definition Set、RAG、Repair、Recording、Presentationごとに、実際に得られるCall / Action / Mutation / Evidence / Authority / Outcome / Failure / Identity Pointerを参照する。
- 未観測Componentは`not_observed`または`unavailable`にし、`called=False`、Count 0、Authority Falseの機械的証明と混同しない。Contract上必要ならOptional FieldまたはEvidence Stateを追加する。
- `main_called`は実Main Callから導出する。Guard Pre-block等のMain Call 0をTrueにしない。
- `repair_adopted`は`repair_called`ではなく、同一Requestの`repair_accepted`から導出する。
- `final_disposition`は同一RequestのPresented Final / Judge Resultが持つ`presentation_outcome`または同等の実値を使う。
- Guard EvidenceはRequest IDまたは同等の不変Correlation IDで相関させる。Last Resultの前後差分のみを確定証拠にしない。今Roundで相関を追加できない場合はGuard Evidenceを`unavailable_correlation`と事実どおり表示し、呼出しまたはOutcomeを推定しない。
- Configured / Active / Executed / Evaluated / Artifact / Backend / VersionはStageごとに分離し、取得できない値は`unavailable`にする。

Hard Assertに少なくとも次を含める。

1. Guard Pre-blockでMain Call 0。
2. Repair Called / Not Adoptedで`repair_adopted=False`。
3. Repair Called / Adoptedで`repair_adopted=True`。
4. Judge safe fallbackが`candidate_accepted`へ変換されない。
5. 未観測ComponentがCount 0 / Authority Falseの確定値に化けない。
6. 並行する通常ChatのGuard / Judge ResultがExperiment Runへ混入しない。

## 6. R2-WU-03 — Case Evaluation / Comparison Persistence

- `completed => PASS`のOracleを削除する。
- Frozen Caseの`expected_observations`、Actual OutputおよびActual Evidenceから判定できるCaseだけをDeterministicに評価する。
- Freshness、RAG Grounding / Strict NO_HIT、Belief Revision、False Improvementを、作成済みDomain Classifierまたは明示的なEvaluator Adapterへ結線する。
- 評価に必要なEvidenceがない場合は`INCONCLUSIVE`、`NOT_RUN`または`UNAVAILABLE`であり、PASSではない。
- Human Review必須Caseは引き続きHuman未実施をPASSにしない。
- Metricは実測可能な値だけを記録する。Call Count、Deviation、Repair Adoption、False Positive、False Grounding、Correction Acceptanceを別Fieldのまま保持する。
- Evaluation ObservationをComparison生成前に保存または同一Comparison Artifactへ組み込み、Disk上のComparisonとAPI Responseを同一内容にする。
- Restart後にPlan、Case、Config、Run、Raw Evidence、Evaluation、ComparisonのIdentity Chainを復元する。
- ComparisonRowはMetricの有無にかかわらず、ObservationのRun ID / Case ID / Rubric Revision不一致をTyped Rejectする。

## 7. R2-WU-04 — Async Worker / Deadline / Cancel収束

- RunのExecution ModeをRun開始時に保存し、Raw Evidence未保存のRunning Production RunをFixtureと表示しない。
- DeadlineをActor Call前だけでなく、呼出し中も含むRun全体の上限として強制する。Deadline時は実Cancel Hookへ到達し、Typed `deadline_exceeded`に収束する。
- Worker shutdown / submit Raceで、保存Runを`running`のまま残さない。
- Future完了が`_in_flight`登録より先行しても、終了済みEntryを残さない。
- User Cancel、Worker Terminal、Deadlineの競合はExactly-once Terminalに収束し、Cancel成功を偽409にしない。
- Restart時に前Process由来の`running`がある場合、無限にRunning表示し続けず、復旧不可ならTyped `interrupted_by_restart`等へ収束する。
- Shutdown後にModel Unloadする前、Experiment Workerの実Drain完了を保証する。

Testには少なくとも次を含める。

1. Actor呼出し開始後にDeadline超過。
2. shutdownとsubmitの競合。
3. 即時完了TaskのIn-flight登録Race。
4. Cancel Hook側TerminalがPersisted Cancelより先に完了。
5. Cancel後Late Result。
6. Restart後の孤立Running Run。

## 8. R2-WU-05 — Frontend Truthfulness

- Plan作成前にFixture / Productionの意味と、Production VariantのFrozen Configを確認できるようにする。
- Running RunをFixtureとProductionのどちらか不明な状態に戻さない。
- Variant表示とActual Effective Configが不一致なRunは、成功RowではなくTyped Failureとして表示する。
- Metric / Evaluation / Failure / Raw Evidence Pointerを表示し、未計測値は`—`または明示的Unknownとする。
- `completed`と`pass`、`repair_called`と`repair_adopted`を同じ表示にしない。
- Comparison取得失敗を無言で握りつぶし、古いComparisonを最新に見せない。少なくともFailureまたはStale状態を表示する。

## 9. R2-WU-06 — Verification / Bounded Real Model Gate

### 9.1 Fixture / Production-fixture

- R2-WU-01〜05のHard Assert。
- Existing Experiment Suite。
- Backend Non-model Full Suite、Ruff、Canonical Mypy Baseline差分。
- Frontend Test、Typecheck、Lint、Build。
- Critical境界のSabotage-regressionは観点重複を避けて有界に行う。

### 9.2 Real Model

Production VariantのConfig一致とEvidenceの真実性がFixture / Integrationで成立するまで実Modelを回さない。成立後のみ、次を逐次で最大3 Run実行する。

```text
1. Main Qwen only Production baseline
2. Main Qwen + Gemma Judge / Repair
3. Main Qwen + Qwen3Guard
```

- SeleneとDeepSeek Judgeは実行しない。
- 事前にProject所有Process / Port、macOS Memory Pressure、Swapおよび残存Modelを確認する。
- `PhysMem used`またはFree容量だけでPressureを確定しない。
- Memory Pressureが高い、Swapが急増している、Unloadできない、またはUserの通常作業を妨げると判断した場合は強行しない。`partial_ready_for_user_real_gate`として返し、実行したと主張しない。
- 実Model品質がFAILでも、Frozen Variant、Typed Failure、Actual Evidence、Comparisonが正しければ事実どおり記録する。
- 実行前後にProcess / Port / Worker / Model Unloadを確認する。

## 10. Independent Internal Review

Review Aは次のみを見る。

- Frozen Variantが実行Variantと一致する。
- 通常Chat設定とExperiment設定が混線しない。
- Provider / Artifact / Definition / Request Identityが相関する。
- Restart後もIdentity ChainとComparisonが読める。

Review Bは次のみを見る。

- Call / Mutation / Evidence / Authority / Repair AdoptionのFalse Valueがない。
- CompletedをCase PASSと混同しない。
- Deadline / Cancel / Late Result / Worker DrainがExactly-onceに収束する。
- UIがFixture、Production、Running、Unknown、Failureを混同しない。

同一観点の無限Reviewは行わない。Confirmed Critical / Major / MVP Blockerだけを修正する。

## 11. Scope / Authority Boundary

- R1で成立したFixture、Identity、Persistence、API、UIを全Rollbackしない。
- Phase 9-1のProvider固有問題を修正しない。
- Phase 9-1へ必要な追加境界を入れる場合は、Optional / Request-local / Default no-opに限定し、通常Chatの不変をTestする。
- JSON Retry、Judge Decoder緩和、Model Sampling、Context / Token Budget、Selene、DeepSeekに触れない。
- Phase 9-3 / Phase 10へ進まない。
- 右Panel、Settings、Sidebar、Main Chatの大改造を行わない。
- Network、Model Download、Package Install、Project Root外Mutationを行わない。
- Git `add` / `commit` / `push` / `stash` / `reset` / `clean`を行わない。
- Phase Index、Current Unresolved Registry、Roadmap、Technology Selectionを編集しない。
- Existing Handoff / Return / Historyを上書きしない。
- Existing Dirty Working Treeを保持する。

## 12. Exact Return / Recovery

必ず別々の新規Pathへ作成する。

```text
docs/project/phases/phase_9/handoffs/
  phase_9_claude_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_return_ja_<timestamp>.md

docs/project/phases/phase_9/history/index/
  phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_recovery_ja_<timestamp>.md
```

Returnには次を含める。

- R2-WU-01〜06の個別状態。
- Before / After。
- Files Changed / Deliberately Not Changed。
- Frozen Config / Actual Config / Provider / Request / EvidenceのIdentity Chain。
- Metric / Evaluation / Comparisonの根拠。
- Fixture / Production-fixture / 実Modelの区別。
- Focused / Full / Frontend / Static Verification。
- Review A / B。
- Open Findings。
- Git / Network / Root外Mutation / Process / Port / Model状態。

最大Claimは、全必須項目と実Model Gateを満たした場合のみ`P9_2_R2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`とする。実Modelを安全上見送った場合は`P9_2_R2_PARTIAL_READY_FOR_USER_REAL_GATE`まで。Blockerが残る場合は`P9_2_R2_INCOMPLETE_FOR_CONTROLLER_REVIEW`までとする。

Phase 9-2 Complete、Phase 9-3開始およびPhase 9 Closureを自己承認しない。

## 13. True Stop

次の場合だけ、到達点と機械的BlockerをPartial Returnへ記録して停止する。

- Frozen Variantを実行するために通常ChatのGlobal設定Mutationまたは最上位疎結合Invariant破壊が不可避。
- Actual Evidenceを得るために秘密情報、User Dataまたは未許可のRoot外データへの接触が必要。
- Existing Dirty Treeを保持できない。
- 新Network、Cost、License、Model取得またはGit Write Authorityが必要。
- 実Modelを安全にUnload / Stopできない。
- Phase 9-1 Golden Pathが壊れ、局所修復で回復できない。

実Modelをその時点のMemory Pressureで回さない場合は、コード修正のTrue Stopと混同せず`partial_ready_for_user_real_gate`で返す。

