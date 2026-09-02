# Phase 9-1 Codex Controller Independent Review／Bounded Rework Finding Ledger

```yaml
document_id: phase_9_1_codex_controller_independent_review_and_bounded_rework_finding_ledger_20260831231243
document_type: controller_independent_review_finding_ledger
document_state: final_rework_required
language: ja
created_at: 2026-08-31 23:12:43 JST
phase: phase_9
program: phase_9_1
review_target: phase_9_claude_p9_1_four_percent_resource_bounded_long_run_exact_return_handoff_ja_20260901033000.md
review_disposition: REWORK_REQUIRED
phase_9_2_authority: false
```

## 1. 結論

Claude Returnの中心Finding、すなわちCanonical Semantic 109が全件質的判断であり、Built-in Deterministic Judgeが`evaluated 0`となること自体は設計上正しく、Authority非依存の実評価経路としてMain-shared self-judgeが存在するという判断はSourceと一致する。

一方、Phase 9-1の中心目的であるDedicated Selene／Qwen3Guard Production Activationは、Composition Rootが`dedicated_model_authority_granted=False`へ固定されたままであり、明示的なUser AuthorityをRuntimeへ渡す入口が存在しない。この状態ではArtifactが存在しても実画面Activationは必ず失敗する。さらにMain-shared Repair／Rejudgeの新規`e2e` Testは実Rejudgeを実行しておらず、Return ClaimがEvidenceより広い。

したがって`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`は受理せず、4件だけのBounded Reworkへ戻す。Phase 9-1全体を再実装しない。

## 2. Independent Verification

```text
Return Handoff SHA-512:
3640f42d548afd8e969622af4ddb97aec2630adf3848194784c3323312d2991bb03a5fc82a388632287441bd0b9176b580e334178231081fa4df9999c75fe48a

Controller Focused Test:
48 passed in 2.00s

Controller git diff --check:
CLEAN
```

Source照合で確認した成立事項：

- Canonical 109 Descriptorは既存Testで109／109 Compile、Unsupported 0。
- Mappingは`CLASSIFICATION_WITH_REFERENCE`／`ABSOLUTE_SCORING`／`CLASSIFICATION`だけである。
- Built-inは全Criterionを`NOT_APPLICABLE／UNSUPPORTED_MAPPING`として扱い、Model Call 0／虚偽PASS 0。
- Main-shared Judge OptionとDispatch、Provider Identity、Semantic Result Decode経路は存在する。
- Dedicated Adapterの共通Preflight Refactorは既存挙動を維持し、Focused TestはPASSする。

## 3. Findings

### P9-CODEX-001 — Dedicated Production Authority入口が存在しない

```yaml
severity: major
priority: P0_MVP_BLOCKER
scope: production_composition_and_startup_contract
```

`src/margpa_runtime_llm/bootstrap/web_application.py`は`ProductionRoleAdapterFactory`へ常に次を渡す。

```python
dedicated_model_authority_granted=False
```

Repository全体を検索しても、CLI／Config／Environment／Runtime Receiptからこの値を明示的に`True`へ渡す経路は存在しない。これは「Real Artifactを今回Loadしなかった」こととは別である。Default Falseは正しいが、Userが後でExact Authorityを与えてもProductionが受領できないため、Selene／Qwen3Guardは現在も必ず`dedicated_model_authority_unavailable`へ収束する。

**Required Rework**：Default Falseの明示的Startup Opt-inを追加し、Entry Pointから`build_phase1_web_runtime()`、Composition Root、FactoryへLosslessに配線する。Opt-inだけで自動Loadせず、Mode OFF中はDedicated Model Call／Load 0を維持する。Real Artifact Loadは本ReworkでもNOT RUNとする。

### P9-CODEX-002 — Main-shared Repair／Rejudge E2E Claimが実Rejudgeを実行していない

```yaml
severity: major
priority: P0_EVIDENCE_BLOCKER
scope: judge_repair_rejudge_production_composition
```

新規`test_main_shared_judge_needs_repair_and_rejudge_reuses_the_same_main_service_single_turn_e2e`は、Fake Repair Executorへ`rejudge_service`、`rejudge_model_key`、`rejudge_role`が渡されたことを確認する。しかしFake ExecutorはRepair GenerationもRejudge Model Callも実行せず、即座に`accepted=True`を返す。

`attempt_live_repair()`単体には実Rejudge Testが存在するため、Source機構が不存在というFindingではない。問題はMain-shared Judge Hookから実Repair Executorまでの合成を一本で実行したというReturn Claimが未証明である点である。

**Required Rework**：Productionと同じRepair実装をFixture Inference Serviceへ接続し、Initial Judge → Repair Generation → Rejudge Call → Adopt／Rejectまで実行するDeterministic Testを追加する。Fake Executorが即Acceptedを返すTestだけでE2E PASSを主張しない。

### P9-CODEX-003 — Canonical Phase State／Acceptance DispositionがReturnと矛盾する

```yaml
severity: major
priority: P0_RECOVERY_TRUTHFULNESS
scope: current_phase_state_and_traceability
```

`phase_9/phase_index_ja.md`はまだ`handoff_ready_implementation_not_started／implementation_started: false`である。Return HandoffはP9-1完了を主張しながら、P9-ACC-001〜038の個別Dispositionを持たず、Acceptance Matrix／Unresolved RegistryをControllerへ委ねている。

**Required Rework**：Phase Indexを`controller_rework_in_progress`から最終Candidate Stateへ更新し、38 AcceptanceをPASS／PARTIAL／RESOURCE_GATED／NOT RUN／USER MANUAL GATEへ個別Dispositionする。Fixture PASSをReal Dedicated PASSへ昇格しない。

### P9-CODEX-004 — User Mac Manual手順がMode Lifecycleを欠く

```yaml
severity: moderate
priority: P0_USER_GATE_ACCURACY
scope: user_manual_gate
```

Provider変更時はModeが安全のためOFFへ戻る。Return §11はMain-shared Provider選択後、Judge OBSERVE／ENFORCEおよび必要なRepair Modeを再適用する手順を明記していない。そのままではUserがTurnを実行してもJudgeが動かず、誤ってFailure判定する可能性がある。

**Required Rework**：Main Providerと一致するself-judgeを選ぶ、Judge Modeを再適用する、Repair／Recording Modeを目的に応じて設定する、Semantic CountsとExecuted Providerを確認する、という正確な順序へManualを修正する。Dedicated Smoke用Startup FlagはReal Artifact Authority付与時だけ使うものとして分離する。

## 4. Rework Stop Line

本Reworkは上記4件だけを対象とする。

- Semantic Compiler／Built-in Judge／Lifecycleの全面再設計をしない。
- Real Artifact、Network、Official Selene Prompt取得を実行しない。
- UI Polish、Phase 9-2／9-3、Roadmap、Closureを混入させない。
- P1以下を新しいRework Loopへ追加しない。

## 5. Maximum Claim

```text
Current: P9_1_CONTROLLER_REWORK_REQUIRED
After Rework: P9_1_COMPLETE_CANDIDATE_FOR_USER_MANUAL_AND_REAL_ARTIFACT_DISPOSITION
Final Acceptance／Phase 9-1 User Checkpoint: User Authority
```
