# Phase 9-2 — Real Multi-Variant / Truthful Evidence R3 Exact Handoff

```yaml
document_id: phase_9_controller_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_handoff_20260907090620
document_type: exact_rework_handoff
document_state: ready
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-07 09:06:20 JST
language: ja
from: codex_controller
to: claude_designer_implementer
authority_owner: Nazuna Research
decision_authority: user
in_response_to: phase_9_claude_phase_9_2_experiment_truthful_variant_execution_and_evidence_r2_exact_return_ja_20260907084839.md
controller_review: phase_9_2_controller_r2_return_independent_review_and_r3_rework_decision_ja_20260907090620.md
maximum_claim: P9_2_R3_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
network_authorized: false
append_only: true
```

## 1. Objective

R2の有効な成果を保持し、Phase 9-2を「Direct Adapter SmokeとFixture型がある状態」から、次の実行可能なMVPへ収束させる。

```text
同一Case / 同一Experiment
  -> 異なるFrozen Production Variant
  -> 明示的かつ非破壊なConfig境界
  -> Top-level Experiment Run
  -> Actual / Unknownを混同しないEvidence
  -> Evaluation / Comparison / Restart Read
```

## 2. Primary Inputs

1. Controller Review: `docs/project/phases/phase_9/history/operations/phase_9_2_controller_r2_return_independent_review_and_r3_rework_decision_ja_20260907090620.md`
2. R2 Return / Recovery。
3. R2 Exact Handoff。
4. `phase_9_2_experiment_multi_governance_execution_design_and_work_breakdown_ja.md`
5. `phase_9_requirements_ja.md`のP9-REQ-201〜209。
6. `phase_9_acceptance_matrix_ja.md`のP9-ACC-039〜045。
7. 現行Experiment Source / Test / UI。

全Historyの無差別再読はしない。

## 3. Non-negotiable Boundary

- 通常ChatのGlobal設定をExperimentが無言変更して戻す方式は禁止。
- Userが明示的にSettingsを変更するWorkflowは可。ただし必要ConfigをUIへ表示し、Run中の関連設定変更を防ぐLeaseを持つこと。
- 代替としてExperiment-scoped Controller / Compositionを構成してもよい。
- 同一Live Snapshot Digestを相互排他的Variant全件へ複製して解決扱いにしない。
- Existing Main／Judge／Guard／Main Governance／Repairの疎結合契約を弱めない。
- R2で成立したCase Oracle、Persistence、Async API、Stale UIをRollbackしない。
- 未観測をFalse／0／PASSへ変換しない。
- FixtureとProductionを同じEvidence Identityにしない。
- Phase 9-3、Phase 10、Provider固有Reworkへ進まない。

## 4. R3-WU-01 — Production Plan / Variant Configuration成立

### 4.1 Plan契約

1. Plan作成時に`execution_mode`をFreezeする。Run開始時にFixture／Productionを自由に後変更させない。
2. Production PlanはVariantごとに別のFull Effective Configuration Snapshotを保存し、Digestだけで内容を消失させない。
3. Snapshotは最低限次を分離する。

```text
Main configured / active / artifact
Judge mode / configured / active / expected executed / artifact when available
Guard mode / configured / active / expected executed / artifact when available
Main Governance mode
Repair mode
Recording mode
RAG / Presentation / Definition Set: observed value or explicit unavailable
snapshot digest / case digest / plan digest
```

4. Variant宣言を現在Live SnapshotへOverlayして「必要Config」を構成してよい。ただしDesired／Frozen／Actualを別Fieldとし、同じIdentityへ潰さない。
5. Restart後もSnapshot内容とDigestを読み直せる。

### 4.2 実行方式

次のいずれかを選ぶ。

**Option A: Explicit User-Gated Live Match + Lease（MVP優先候補）**

- UIがVariantごとの必要設定を表示する。
- Userが通常Settingsで明示的に設定する。
- Run開始前にFrozen VariantとLive Configを完全照合する。
- 一致後、実行中は関連Settings／Provider変更をLeaseで409拒否する。
- Terminal／Cancel／Deadline後にLeaseをExactly-once解放する。

**Option B: Experiment-scoped Controller / Composition**

- 通常WebRuntimeとは別のMode Controller / Request-local Snapshotを使う。
- 通常Chat SettingsをMutationしない。
- Model Resourceは逐次Leaseし、Variant間へResult／Contextを共有しない。

どちらを選んでも、同一Production Plan内で少なくとも次の2 Variantを同じCaseに対して順番に実行しComparisonへ並べられること。

```text
production-main-only-baseline
production-judge-repair-baseline
```

可能ならGuardも同じPlanへ含める。16GB Macのため実Modelは必ず逐次。

### 4.3 Hard Assert

- 同一Planの相互に異なる2 Variantが両方Run可能。
- Variant AのFrozen ConfigとVariant BのFrozen Config Digestが異なる。
- Plan作成後のPreset変更はRunへ混入しない。
- Run前Live mismatchはCall 0 Typed Reject。
- Run中Settings変更はLeaseで拒否され、ABA変更も通らない。
- Lease解放後は通常Settings変更が復旧する。
- 二つのRunをほぼ同時に要求してもConfig／Resultが交差しない。

## 5. R3-WU-02 — Tri-state Evidence / Identity

### 5.1 Contract

`ActorInvocationRecord`およびAPI DTOを、少なくとも次の三状態を表せる形へする。

```text
observed_called
observed_not_called
not_observed / unavailable_correlation
```

未観測時は`called`、Mutation Count、Evidence Count、Authorityを`None`またはField不在にし、False／0へ固定しない。Fixtureの確定Call 0は従来どおりFalse／0でよい。

Metricの総Call CountはUnknownを0として足さない。全対象が確定していない場合は、既知Call CountとCompleteness／Unknown Countを分離するか、総数自体を`None`にする。

### 5.2 Actual Identity

Raw Evidenceへ、取得できる範囲で同一Requestの次を保存する。

- Main Attempt Provenance / Model Identity。
- Judge Configured / Active / Executed / Evaluated / Artifact / Backend Pointer。
- GuardはRequest相関がない間、`unavailable_correlation`のままでよい。実行をFalseとは記録しない。
- Repair called / outcome / adopted / requested_by。
- Final disposition。
- unmodeled Componentは`not_observed`。

Guard相関そのものを今RoundでPhase 9-1へ追加する場合は、Optional・Request-local・Default no-opとし、通常Chat Regression Testを必須とする。過大なら相関不能の正直な非主張を保持する。

### 5.3 Hard Assert

- Guard不明が`called=False`／Call 0にならない。
- Main Governance／RAG／Recording等の未観測がAuthority Falseにならない。
- Repair Called but Not AdoptedとNot Calledを区別する。
- Judge safe fallbackをcandidate acceptedにしない。
- Comparison UIはUnknownを`0`ではなく`—`／Unavailableで表示する。

## 6. R3-WU-03 — Queue Cancel / Deadline Call 0

Workerで、Queue中にTerminalへ到達したRunのActorを後から実行しない。

最低限次をTestする。

1. Run AがWorkerを占有中、Run BをQueue。
2. Run BをUser Cancel。
3. Run A解放後もRun B Actor Call 0。
4. 同じScheduleでRun B Deadline超過後もActor Call 0。
5. Queue Futureを取り消すか、Task開始直前のAuthoritative Terminal Checkで必ず短絡する。
6. Cancel／Deadline／Worker完了のTerminalはExactly-once。
7. Shutdown時にQueue済みRunを不用意に実行せず、Model Unload前Drain契約を維持する。

## 7. R3-WU-04 — Top-level Real Experiment Gate

Direct `LiveProductionTurnAdapter.run_turn()` Testは残してよいが、それをTop-level Experiment Gateとは数えない。

Fixture／Integration収束後のみ、実Modelを最大3 Top-level Runで実行する。各Runは実際に次を通す。

```text
Plan creation
-> Frozen full Variant Config
-> Experiment Run API / Service
-> ExperimentRunWorker
-> Production Adapter
-> persisted Raw Evidence
-> Evaluation
-> Comparison
-> restart/rebuild後のread
```

Scenario:

1. Main Qwen only。
2. Main Qwen + Gemma Judge / Repair ENFORCE。
3. Main Qwen + Qwen3Guard ENFORCE。

Rules:

- Selene／DeepSeek Judgeは実行しない。
- 事前後にMemory Pressure、Swap、Process、Port、Model Unloadを確認する。
- Scenario 2でRepairが発火しなければ`not_called`として正直に記録し、成功を捏造しない。Phase 9-1 Repair Golden Pathの再証明目的で入力を歪めない。
- Model品質FAILは許容するが、`pytest.skip()`でGate成功にしない。Typed FAILED／INCONCLUSIVE Rowとして同じIdentity Chainへ保存する。
- Memory Pressureが危険なら強行せずPartial Returnにする。
- Direct Adapter Smokeの再実行は不要。今回必要なのはTop-level経路だけ。

最低1つの実Model Experimentについて、Process再構成後もPlan／Snapshot／Run／Raw Evidence／Comparisonが読めることを確認する。

## 8. R3-WU-05 — UI / Acceptance Truthfulness

1. Plan作成前にFixture／Productionを選び、Plan作成後は固定する。
2. Preset宣言を「Frozen Config」と呼ばない。Frozen Snapshotと必要Live設定を別表示する。
3. Production Planで複数Variantを選択した場合、各VariantのReady／Mismatch／Running／Terminalを区別する。
4. Live mismatchはBackend Typed Codeを表示する。
5. Unknown EvidenceはFalse／0ではなく`—`またはUnavailable。
6. Comparisonは同一Case、Variant差、Execution Mode、Frozen Config Digest、Actual Evidence Pointerを表示する。
7. P9-REQ-201〜209／P9-ACC-039〜045を再Mappingし、Fixture-only／Production-fixture／実Model／Human未実施を別列にする。

現行Minimal UIで到達不能なRAG／Main Governance／Routing／Strict-Progressiveの比較は、Source存在だけでUser機能成立としない。今RoundでPreset／APIへ到達可能にするか、明確にPartialとして残す。Phase 9-2 User Manual Candidateを主張する場合は、少なくともDeterministic Fixture経路としてUI/APIから到達可能であること。

## 9. Verification

順序:

1. Focused Unit。
2. Experiment Integration / Web。
3. Queue Cancel / Deadline deterministic tests。
4. Frontend Test / Typecheck / Lint / Build。
5. Backend Non-model Full Suite。
6. Ruff / Canonical Mypy Baseline差分。
7. 条件成立後のみTop-level Real Experiment Gate。
8. Internal Review A / B。

Critical境界のSabotage-regressionは重複を避け、少なくとも次を含める。

- 全Variantへ同一Digestを戻すとMulti-Variant Testが落ちる。
- UnknownをFalseへ戻すとEvidence Testが落ちる。
- Queue Terminal Checkを外すとCancelled RunのActor Call 0 Testが落ちる。

## 10. Review A / B

Review A:

- 同一Caseの異なるProduction Variantが本当に実行されたか。
- Frozen／Desired／Actual ConfigとProvider／Artifact／Requestが分離されたか。
- 通常Chat Global設定をExperimentが無言Mutationしていないか。
- Restart後のIdentity Chain。

Review B:

- Unknown→False／0、Completed→PASS、Called→AdoptedのFalse Valueがないか。
- Queue Cancel／Deadline／Late Result／Shutdown。
- Direct Adapter SmokeをTop-level Runと誤表現していないか。
- UIがPreset宣言とFrozen Snapshotを混同していないか。

Confirmed Critical／Major／MVP Blockerだけを修正し、同一観点Reviewを無限反復しない。

## 11. Scope / Authority

- Phase 9-1 Provider品質、Gemma Schema／Sampling／Retry、Selene、DeepSeekは変更しない。
- Main／Judge／Guard／Repairの内部評価Logicを作り直さない。
- Phase 9-3／Phase 10へ進まない。
- Settings／Sidebar／Main Chat／右Panelの大改造をしない。
- Network、Download、Install、Root外Mutationをしない。
- Git `add`／`commit`／`push`／`stash`／`reset`／`clean`をしない。
- Phase Index、Roadmap、Technology Selection、Current Unresolved Registryを編集しない。
- Existing Handoff／Return／Historyを上書きしない。
- Existing Dirty Treeを保持する。

## 12. Exact Return / Recovery

新規Pathへ分けて作る。

```text
docs/project/phases/phase_9/handoffs/
  phase_9_claude_phase_9_2_real_multi_variant_and_truthful_evidence_r3_exact_return_ja_<timestamp>.md

docs/project/phases/phase_9/history/index/
  phase_9_2_real_multi_variant_and_truthful_evidence_r3_recovery_ja_<timestamp>.md
```

Returnには次を含める。

- WU-01〜05の個別状態。
- Controller Finding対応表。
- 選んだConfig実行方式と理由。
- 同一Planで異なるVariantを実行したEvidence。
- Full Snapshot / Actual Evidence / Provider / Artifact / Request Identity Chain。
- Queue Cancel／Deadline Call 0。
- Top-level実Modelの正確な回数と経路。
- Fixture／Production-fixture／Direct Adapter Smoke／Top-level Real Experimentの区別。
- P9-REQ／ACC Mapping。
- Focused／Full／Frontend／Static結果。
- Review A／B。
- Open Findings。
- Git／Network／Root外Mutation／Process／Port／Model状態。

最大Claim:

- 全必須項目と安全なTop-level Real Gate成立: `P9_2_R3_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`
- 実ModelのみResource Gate: `P9_2_R3_PARTIAL_READY_FOR_USER_REAL_GATE`
- Blocker残存: `P9_2_R3_INCOMPLETE_FOR_CONTROLLER_REVIEW`

Phase 9-2 Complete、Phase 9-3開始、Phase 9 Closureを自己承認しない。

## 13. True Stop

次だけをTrue Stopとする。

- Multi-Variant成立に通常Chat Global設定の無言Mutationが不可避。
- LeaseまたはExperiment-scoped境界を局所的に成立できず、Phase 9-1疎結合Invariant破壊が必要。
- Existing Dirty Treeを保持できない。
- 新Authority、Network、Cost、Model取得またはGit Writeが必要。
- 実Modelを安全にUnload／Stopできない。

難しい、時間がかかる、追加設計が必要という理由だけで、必須項目を独断でScope外へ移さない。方式選択で要件が変わる場合は実装前にUserへ確認する。
