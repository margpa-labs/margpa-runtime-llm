# Phase 9-2 Long Run Return — Codex Controller独立ReviewとR1 Rework判断

```yaml
document_id: phase_9_2_controller_long_run_return_independent_review_and_r1_rework_decision_20260907002521
document_type: controller_independent_review_and_rework_decision
document_state: accepted_changes_required
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 00:25:21 JST
language: ja
decision_authority: user
authority_owner: Nazuna Research
controller: codex
review_target: phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_20260906225104.md
controller_disposition: changes_required
phase_9_2_complete: false
phase_9_3_authorized: false
git_write_authorized: false
append_only: true
```

## 1. 結論

Claude Returnの最大Claim `P9_2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`は受理したが、Phase 9-2 User Manual Candidateとしては不成立である。Controller判定は`CHANGES_REQUIRED`とする。

P9-2-A〜F向けのDomain Contract、Fixture Matrix、Persistence、Semantic Case分類、Trace、PresentationおよびFrontend基盤は有意な実装成果である。Controller再実行でも次は成立した。

```text
tests/unit/experiment + tests/integration/web/test_experiment_routes.py
154 passed in 0.71s
```

ただし、現行Web経路はFixture Actor固定であり、選択Caseの入力やFrozen ConfigをActor実行へ渡さず、実Main／Judge／Guard／Repairとも結線されていない。よって、現時点の製品挙動は「Experiment Platform」ではなく「Fixture Contract／UI Demo」である。

## 2. Confirmed Findings

### IR-P9-2-01 — Experiment RunがFixture固定で実Runtimeへ未結線 [BLOCKER]

`/api/v7/experiment/runs`は常に`_build_fixture_actor_registry()`を構築し、`FixtureActor`だけを呼ぶ。Production Adapterは存在せず、F3実Model Evidenceは0回である。

Fixture Matrixが成立していることと、Main／Judge／Guard／GD／RAG／Repairの構成差を実Turnで比較できることは別である。P9-REQ-202／P9-ACC-040の製品経路Evidenceは未成立である。

### IR-P9-2-02 — Case／Config／Run／Digest相関が実行経路にない [BLOCKER]

- `ExperimentPlan`は`case_revision`だけを持ち、`case_id`やCase Digestを持たない。
- 現Case Packの3 Manifestはすべて同じRevisionを使うため、保存PlanからどのCaseを選んだか復元できない。
- Web `StartRunRequest`は`request_id`を受けず、実際のRunで`request_id=None`となる。
- `EffectiveConfigurationSnapshot`は単体ContractとTestには存在するが、Plan／Run／Web Route／Persistenceに結線されていない。
- Acceptance TestはSnapshotをRunと無関係に同一Test内で構築し、Plan Digestの値を比較しているだけである。Artifact／Definition／Case Digestは`None`のままである。

P9-REQ-201／P9-ACC-039を「相関可能」とするEvidenceにはなっていない。

### IR-P9-2-03 — Frozen PlanではなくLiveのGlobal Presetを実行 [MAJOR]

Plan作成時にVariantを保存しているにもかかわらず、Run Routeは保存Planの`plan.variant()`を使わず、Module Globalの`_PRESET_VARIANTS`を再検索して実行する。Preset定義がPlan作成後に変わると、Plan Digestが示すVariantと実行Variantが乖離する。

### IR-P9-2-04 — Comparison ReportとUIが未結線 [MAJOR]

`build_comparison_report()`とComparison Persistenceは存在するが、Web Route／Frontendから一度も呼ばれない。現UIの「比較表」はVariant ID、Run State、詳細Buttonの一覧であり、Metric、Human／LLM Evaluation、Failure、Raw／Final Output、Applied ActionまたはCase差を比較しない。P9-ACC-045の実利用経路は未成立である。

### IR-P9-2-05 — 選択CaseがExperiment Runで使われない [MAJOR]

CaseはPlan作成時にRevisionを取るためだけに使われ、`run_variant()`やActorにCase Input／Evidence／Expected Observationは渡されない。Freshness、Strict NO_HIT、False ImprovementのどのCaseを選んでも、Web実行は同じFixture Invocation Countを返す。Dの分類関数は単体的には成立するが、Experiment Runとしては未結線である。

### IR-P9-2-06 — Budget／Deadline／Stop Policy／Cancelが実行Contractになっていない [MAJOR]

- `ExperimentPlanBudget` fieldsはDigestに入るだけで、値制約もRuntime強制もない。
- `max_variant_runs`は`start_run()`で参照されず、上限を超えても実行できる。
- `execution_order`も実行時に参照されない。
- Actor呼出し例外時にRunを`failed`へ収束させるBoundaryがなく、`running`のまま残り得る。
- Web Runは同期的に即Terminalまで進む。FrontendはResponse後にしかRunを一覧へ載せないため、現在のCancel ButtonでIn-flight Runを停止できない。

### IR-P9-2-07 — `mode=None`がOFF契約に反しActor Call 1 [MAJOR]

`ComponentSelection`の契約は`mode=None`をOFF／Absentと説明するが、Runnerは`"off"`だけをSkipし、`None`の場合はActorを呼ぶ。Controller実行Probeでも`calls=[(judge, None)]`、`called=True`を再現した。

これは「Component OFF／不在 => 当該Call／Mutation／Evidence／Authority 0」という最上位Invariantへの直接違反であり、Returnの「具体的Failure Scenarioなし」「Blockerではない」という判定は受理しない。

## 3. F3見送り判断

HandoffのF3文言に「実行してもよい」と読める余地があったことはController側の曖昧さであり、ClaudeがRiskを避けて0回としたこと単体を違反とは判定しない。

一方で、Execution DesignのFinal Verificationは「実Model代表Run」を含み、User Candidateには全Acceptance行のEvidenceを要求している。Production Adapterが無いままA〜Eを`resolved`としたことは過大Claimである。

R1では文言を明確化し、Fixture／Productionの両経路を分離したうえで、実Model代表RunをUser Manual Candidate前の必須Gateとする。安全に実行できない場合はTrue Stop／Partialであり、Fixture PASSで代替しない。

## 4. 保持する成果

R1はRollbackではない。次は保持し、実行経路だけを収束させる。

- `modules/experiment/`の純粋Domain Contract。
- FixtureによるComponent Independence Matrix。
- Human／Self Judge／Independent Judge／DeterministicのIdentity分離。
- Semantic Caseの中立名称と分類Contract。
- Call 0、Strict／Progressive、False Success拒否のContract。
- Filesystem PersistenceとAppend-only Return／Recovery。
- Phase 9-1のMain／Judge／Guard／Repairの完全疎結合基盤。

## 5. Disposition

```text
P9-2-A: partial
P9-2-B: partial
P9-2-C: partial
P9-2-D: partial
P9-2-E: partial
P9-2-F: partial
Phase 9-2 User Manual Candidate: not accepted
Next: R1 bounded convergence rework
```

Phase 9-3とPhase 10は未許可のままとする。
