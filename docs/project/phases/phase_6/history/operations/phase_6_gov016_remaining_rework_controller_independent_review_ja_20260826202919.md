# Phase 6 Remaining Rework Controller Independent Review（Append-only、P6-GOV-016）

```yaml
document_id: phase_6_gov016_remaining_rework_controller_independent_review_20260826202919
governance_id: P6-GOV-016
status: ADJUST_REWORK_REQUIRED
review_target: phase_6_remaining_rework_bounded_complete_candidate_handoff_ja_20260826202200.md
reviewer_role: project_owner_and_design_controller
provider: Codex
created_at: 2026-08-26 20:29:19 JST
phase_6_closure: BLOCKED
phase_7: NOT_STARTED
```

## 1. 結論

`Phase 6 Remaining Rework`のPackage 0〜Jは、Domain、Adapter、State、CAS、Failure、UI部品および
静的／自動Testの大部分を成立させた。しかし、Frozen Designが要求するProduction Web Turnへの
Provider実接続は成立していない。

したがって、返送Status
`COMPLETE_CANDIDATE_WITH_PARTIAL_NOT_RUN_AND_USER_GATES`はPackage Jの有界な返送状態として
受理するが、Phase 6 AcceptanceまたはClosure Candidateとしては受理しない。判定は
`ADJUST／Rework required`である。

## 2. Resource Signal訂正

Package JのResource停止およびBounded Completion文書は、Userの一時的な誤報
`Codex週間利用可能量 9%`を前提にしている。Userは直後に、正しくは`残り69%`であると訂正した。

この訂正は、当時のSafe StopおよびAppend-only Evidenceを削除しない。ただし、現在のResource
判定、次作業のAuthorityおよび残量見積りへ`9%`を再利用してはならない。

```text
current user-observed weekly availability: 69%
superseded mistaken signal: 9%
```

## 3. 成立した範囲

- ARGD 53件＋DAGD 56件から109 Semantic Criterionを再導出するCompiler／Domain。
- Structural／Semantic ResultのIdentity付きMerge、Typed Deferred／Unknown、False ENFORCE Gate。
- Main／Guard／Judge Provider Registry、Revision＋Digest CAS、Configured／Active分離のDomain。
- Role Lifecycle ManagerのLoad／Unload／Drain／Rollback契約。
- Selene Prompt／Decoder AdapterとQwen3Guard Gen Decoder／Adapterの隔離された実装。
- Stage別Budget Contract、理由別／言語別Failure Contract、Judge／Repair／Recording相関Field。
- Advanced Settingsの3 Provider DropdownとFeature Mode UI部品。
- Executor Canonical Evidence：Backend `1656 passed, 7 deselected`、Mypy `465 source files / 0 issues`、
  Ruff PASS、Frontend typecheck／lint／test／build Exit 0。
- Controller focused revalidation：次の6 Test File、`52 passed / exit 0`。

```text
tests/unit/runtime_governance/test_semantic_runtime.py
tests/unit/runtime_model_control/test_provider_selection_controller.py
tests/unit/runtime_model_control/test_role_lifecycle_manager.py
tests/unit/evaluation/test_selene_adapter.py
tests/unit/guardrail_governance/test_qwen3guard_adapter.py
tests/integration/web/test_feature_modes_routes.py
```

この52件は部品とFake Lifecycleの成立Evidenceであり、Production Compositionの実接続Evidenceではない。

## 4. Independent Findings

### P6-CODEX-046 — Dedicated Provider Production Factory未接続（Major）

`bootstrap/web_application.py`は、Productionの`RoleProviderLifecycleManager`へ
`UnavailableRoleAdapterFactory`を固定している。したがって、Configured Selene／Qwen3Guardを
OBSERVE／ENFORCEでActivationしても、Preflightは常に
`dedicated_provider_artifact_unavailable`となる。

Selene／Qwen3GuardのAdapter ClassとModel Definitionが存在することは、Production TurnでLoad／Use
できることを意味しない。P6-RR-ACC-014／021およびFrozen Design §7〜10は未成立である。

### P6-CODEX-047 — Selected Judgeと実行Judgeが一致しない（Critical）

`build_judge_completion_hook()`はProductionでMain `InferenceService`だけを受け取り、Judge Callは
常に`context.model_key`を使う。結果の`judge_role`およびDecoderも
`JudgeIndependenceClass.MAIN_SELF`固定である。

一方、Semantic Snapshot／UIはProvider Selection ControllerのConfigured／Active Judgeを表示する。
Built-in Deterministicを選択してActiveにした場合でも、実際にはMain ModelがLLM Judgeとして呼ばれる。
つまり、表示されたActive Providerと実行Provider／Evidence Identityが一致しない。これは単なる未実装
ではなく、研究EvidenceとENFORCE判断を誤認させるFalse Identityである。

P6-RR-ACC-008／014／018／021／031／032は未成立である。

### P6-CODEX-048 — Qwen3Guard ResultがGuardrail実行経路へ入らない（Major）

`GuardrailGovernanceComposition`は現在もRule／Pattern Detectorだけで構築される。
`Qwen3GuardGenAdapter`をInput／Output／Context Sourceへ加算的に接続するProduction Compositionはない。
Role LifecycleのGuard Activation Stateが作られても、Guardrail HookはそのAdapterを参照しない。

P6-RR-ACC-014／022／025と、Frozen Design §6／§10は未成立である。

### P6-CODEX-049 — Main Provider DropdownがRuntime Main Switchへ未接続（Major）

`PUT /api/v6/provider-selection/main`はProvider Selection ControllerのConfigured Stateだけを変更する。
既存`RuntimeModelController`のSwitch Transactionを呼ばず、実際のMain Model、Sidebar、
`/api/v4/runtime-model/status`を切り替えない。逆方向に、既存Runtime Model Switch Commit後にProvider
SelectionのMain Configured／Activeを同期する配線もない。

3 Dropdownを同一Model切替面として扱うUser要件とP6-RR-ACC-009は、UI要素の存在だけでは成立しない。

### P6-CODEX-050 — Model Statusが新Provider Stateを投影しない（Major）

`runtime_model_control_routes.py`はJudgeを旧`RuntimeModelSnapshot`＋
`main_self_available`から投影し、Guardは常に`model_id=None`で投影する。新しいProvider Selection
Controller／Role LifecycleのConfigured／Active Stateを参照しない。

そのためProvider Selection PanelとModel StatusでJudge／Guard Identityが矛盾する。Userが以前検出した
「Current LLM-as-a-Judge Model／Current Guardrail Modelの表示と実処理が一致しない」問題は未解決である。

### P6-CODEX-051 — Stage BudgetとRepair RejudgeがSelected Providerへ未接続（Major）

Live Judgeの実Budgetは`LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET`固定である。Provider Selection APIがSelene／
Qwen3Guard用Budgetを表示しても、Judge Hookの実Deadline／Inference Budgetは選択Providerへ追随しない。

Repair後Rejudgeも、Production Wrapperから`rejudge_service`／`rejudge_model_key`／`rejudge_role`を渡して
いないためMain Model／MAIN_SELFへ戻る。Frozen Design §11および§13の「選択Judgeで再評価」は未成立。

### P6-CODEX-052 — Official Contract Provenance未成立（Major）

Selene Manifestは`verified_official_copy: false`、Upstream Revision／Template File／Digestが`null`である。
Qwen3Guard Adapterもverified official contractとExact Revisionを要求するが、Productionで供給する
Manifest／Category Allow-list配線がない。Network禁止下で未取得と正直に記録した点は正しいが、
Frozen Acceptance P6-RR-ACC-019／022を満たしたことにはならない。

### P6-CODEX-053 — Observability／説明の残件（Non-criticalだがAcceptance Blockerを含む）

- `frozen_guard_mode`は`null`固定で、Turn相関へGuard ModeがFreezeされない。
- Recording UIはTurn／Judge Evidenceの成否だけが残り、Recording Summary自身のRequest ID／時刻／
  Provider／Outcome／Reason表示は未完了。
- CLI Helpの`--phase-6-feature-modes`説明は「no live Generation-path effect」のままで、現実のJudge／
  Repair／Recording経路と一致しない。
- Real Qwen／DeepSeek／Selene／Qwen3GuardおよびReal Browserは未実施であり、PASSへ昇格できない。

## 5. Acceptance再分類

Executorの`PASS 27 / PARTIAL 10 / NOT RUN 1 / USER MANUAL 1 / FAIL 1`を、Phase 6 Acceptanceの
最終値として採用しない。特に、APIやDropdownの存在だけを根拠としたP6-RR-ACC-009、およびFake Adapter
だけを根拠とするLifecycle系PASSはProduction Wiringの成立を意味しない。

Controller判定は次の通りである。

```text
Phase 6 Remaining Rework Package completion: PARTIAL ACCEPT
Phase 6 Technical Acceptance: FAIL / ADJUST
Phase 6 Closure: BLOCKED
Open Critical: 1 (P6-CODEX-047)
Open Major: 6 (P6-CODEX-046, 048-052)
Real Browser Gate: OPEN
Real Model Gate: OPEN
```

## 6. 次の順序

1. User Macで、現状をAcceptance PASSへ昇格させない限定Manual Checkを行う。
2. Manual ResultをAppend-onlyで記録する。
3. Claude復帰後、P6-CODEX-046〜053とManual Resultだけを対象にした差分Exact Handoffを発行する。
4. Production Factory／Execution Router／Main Switch同期／Status／Budget／Rejudge／Guard加算配線を修正する。
5. Selene／Qwen3Guardの公式ContractをNetwork Authority下で取得・Digest Freezeする。
6. Real Model／Real Browser Matrixを再実行し、40 Acceptanceを全件再導出する。

既存Package 0〜Iの成立済みDomain実装を最初からやり直してはならない。
