# Phase 9-2 R1 Return — Codex Controller Independent Review / R2 Rework Decision

```yaml
document_id: phase_9_2_controller_r1_return_independent_review_and_r2_rework_decision_20260907071729
document_type: controller_independent_review
document_state: current
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 07:17:29 JST
language: ja
from: codex_controller
to: nazuna_research
decision_authority: user
authority_owner: Nazuna Research
review_target: phase_9_claude_phase_9_2_experiment_live_composition_and_evidence_convergence_r1_exact_return_ja_20260907032749.md
review_target_sha512: 63a94d0414c29ea7ee73a1c6356575eb18b044d8b5de77ed022d8ca60cd5851c60a7496a7591c138e851ff37ceb1f305e46284530cae93140d1b7dcdc49f8b8d
decision: changes_required
phase_9_2_complete: false
user_manual_candidate: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
append_only: true
```

## 1. 結論

R1によるIdentity追加、Frozen Planの再読込み、Case Digest検証、非同期Run、Comparison API/UI結線は前進である。ただし、最大Claimの`P9_2_R1_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`は承認しない。

Production経路は、選択したFrozen Variantを実行せず、通常Web Runtimeでその瞬間に有効なGlobal設定をそのまま実行する。その上で、実際に観測していないCall、Mutation、Evidence、Authority、Repair採用およびCase PASSを比較結果へ生成している。この状態ではExperimentのVariant差と比較値を信頼できない。

## 2. 確認した前進

- `ExperimentPlan`がCase ID、Case Digest、Run Request IDを持つ。
- Run実行時のVariant参照先がModule Global Presetから保存Planへ変わった。
- `mode=None`、Run数、Execution Order、開始前Deadlineの一部Gateが実装された。
- Run開始APIが202を返し、Workerに実行を渡す。
- Comparison RouteとFrontend表示経路が追加された。
- FixtureとProductionを区別する入口が追加された。

## 3. Confirmed Findings

### IR-P9-2-R1-01 — Frozen VariantがProduction実行に反映されない [BLOCKER]

`start_run()`は保存PlanからVariantを読むが、Production Adapterへ渡すのはCase Inputだけである。`LiveProductionTurnAdapter`はMain、Judge、Guard、Repairの選択・Modeを決めず、通常RuntimeのLive設定を読んで実Turnを開始する。

従って、例えば`judge-observe`と表示したRunが、実際にはJudge OFF、ENFORCE、別ProviderまたはGuard ONのLive Runtimeで動き得る。`baseline-all-off`も実際のAll OFFを保証しない。これではVariant Comparisonは成立しない。

R1 Return自身も、`variant_configuration_digests`が常に空、Effective Configuration Snapshot未配線、Live ConfigとFrozen Configの再検証なしと明記している。これを`Config Isolation Option 2 resolved`とするのは、R1 Handoffの「どの方式も成立しない場合はTrue Stop」と矛盾する。

### IR-P9-2-R1-02 — Production Evidenceに未観測の成功値を生成する [BLOCKER]

Production AdapterとProjectionに次のFalse Evidenceがある。

- ConversationがGuard等でMain Call 0になった可能性を確認せず、`main_called=True`に固定する。
- Componentが呼ばれただけで`mutation_count=1`、`evidence_count=1`、`authority_exercised=True`とする。
- Main Governance、Definition Set、RAG、Recording、Presentationを常に`called=False / not_applicable`とし、実行有無を観測しない。
- Repairが呼ばれただけでMetricの`repair_adopted=True`とする。不採用Repairを採用済みと記録し得る。
- Conversation `COMPLETED`を一律`candidate_accepted`とし、Judgeの`repair_accepted`、`safe_fallback`、withhold等のPresented Finalを反映しない。
- Guardは実Outcomeを保存せず、呼出しを推定すると一律`observed`にする。

Unknownまたは未計測値は`unknown` / `unavailable` / `not_observed`のまま保存し、0、1、Trueまたは成功Dispositionに変換してはならない。

### IR-P9-2-R1-03 — 「Run completed」をCase PASSにするFalse Success Oracle [BLOCKER]

`_observation_for_row()`は、Human Review不要CaseでRun Stateが`completed`なら、Caseの入力、出力、Evidence、`expected_observations`、Freshness、GroundingまたはStrict NO_HITを確認せず`PASS`を作る。

Phase 9-2で作成済みの`classify_freshness_answer()`、`classify_grounding()`、`classify_belief_revision()`、`classify_repair_semantic_outcome()`はWeb実行・Comparison経路で使われない。Runが例外なく終わったことと、Caseの期待を満たしたことは別である。R1-WU-04は`resolved`ではない。

### IR-P9-2-R1-04 — Evaluation付きComparisonがRestart-readableでない [MAJOR]

`build_comparison_report()`はEvaluation ObservationのないComparisonをPersistenceへ保存する。Web Routeはその後に一時的なObservationを生成しResponseにだけ追加する。そのため、Disk上のComparisonとUI Responseが同じArtifactではなく、再起動後にEvaluation Identity Chainを再生できない。

### IR-P9-2-R1-05 — Guard EvidenceがRequest単位に相関していない [MAJOR]

Guardの前後Last Invocation ID差分は、Experiment Worker内の逐次実行だけでなく、通常Chat等も含めて同一Runtimeに他Turnが入らない場合に限って成立する。Experiment Workerは通常Chatまで排他しないため、現行利用規律だけでは他RequestのGuard Resultを誤帰属し得る。R1 Returnの「近似Signal」という申告は正直だが、Actual Stage Evidenceの完了には数えない。

### IR-P9-2-R1-06 — DeadlineとWorker Lifecycleが実行全体を束縛しない [MAJOR]

- `deadline_ms`はActor呼出し前に一度確認されるだけで、呼出しがDeadlineを超えても`COMPLETED`になる。
- `submit()`は「Never raises」と説明するが、shutdown後は`RuntimeError`を送出する。Routeは先にRunを`running`で保存し、この例外をTerminalへ収束しないため、RUNNING残留の経路がある。
- FutureをExecutorへSubmitした後に`_in_flight`へ登録するため、高速なTaskが登録前に終了・popし、終了済みEntryが後から残るRaceがある。
- Cancel HookとPersisted CANCELLEDの二つのPublisher順序により、実CancelのTerminal Publishが先に完了した場合の409 Raceが未検証である。

Asyncにしたことだけで、Deadline、Cancel、Exactly-once Terminal、Shutdown Drainが成立したことにはならない。

### IR-P9-2-R1-07 — Running Production RunのIdentityがFixtureへ変わる [MINOR]

Run本体が`execution_mode`を保持せず、Raw Evidenceのない実行中Runを`fixture_only=True`と推定する。POST直後はRequest値で正しく表示しても、ListまたはGETでEvidence保存前のProduction RunがFixtureと表示され得る。Execution ModeはRun開始時にFreezeすべきIdentityであり、Evidenceから後付け推定しない。

## 4. 実Model Gateの判定

他Applicationを無言で終了せず、実Model読込みを強行しなかった安全判断は受け入れる。ただし、`PhysMem used`と名目上のFree容量だけでmacOSの実Memory Pressureを確定はできない。実際のPressure State、Compressedの推移、Swap増加、Model Load後の実測はない。

よって、これは「今Roundで実行しない安全上のPartial判断」としては妥当だが、User Manual Candidateの必須Gate成立や、実Modelを実行不可とするTrue Stopの機械的証明ではない。また、上記Blockerがあるため、現在のProduction Adapterで実Model Gateを追加実行しても採用証拠にはならない。先にR2を修正する。

## 5. Controller Decision

```text
R1 Identity / Async / UI 基盤       : 部分採用
R1-WU-01 Config Correlation          : 未成立
R1-WU-02 Frozen Fixture Variant      : 成立
R1-WU-03 Production Variant Adapter  : 未成立
R1-WU-04 Evaluation / Comparison     : 未成立
R1-WU-05 Async Lifecycle             : 部分成立
R1-WU-06 Real Model Gate             : 未実行
User Manual Candidate                : 不承認
Phase 9-2 Complete                   : 不承認
Next                                 : R2局所Rework
```

R1全体をRollbackしない。成立したIdentity、Persistence、Fixture Composition、Web API、Frontendは保持し、Production Variant実行、Actual Evidence、Evaluation OracleおよびWorker境界に限ってR2で収束させる。

