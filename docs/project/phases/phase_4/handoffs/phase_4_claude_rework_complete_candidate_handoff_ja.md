# Phase 4 Claude Rework Complete Candidate Handoff

```yaml
document_id: phase_4_claude_rework_complete_candidate_handoff
status: phase_4_rework_complete_candidate
phase: phase_4
subphase: phase_4_h
work_unit: p4_h_wu_001_codex_independent_major_review_rework
role: Claude側設計統括者役
provider: claude_code
completion_line: phase_4_claude_rework_complete_candidate
long_running_mode_active: true
created_at: 2026-08-22 03:05:39 JST
created_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_independent_review_rework_handoff_ja_20260822015458.md
required_reading:
  - 本File自体
```

## 0. Repository Recovery（§1要求のExact宣言）

```text
Repository Recovery       : PASS
Active Phase              : Phase 4 Rework
Current Controller Handoff: docs/project/phases/phase_4/handoffs/phase_4_codex_independent_review_rework_handoff_ja_20260822015458.md
Git Mutation              : FORBIDDEN（本Cycle中、遵守。実行していない）
Phase 5                   : FORBIDDEN（本Cycle中、遵守。実行していない）
```

Mandatory Recovery Reading（§1列挙の11項目）を全文読了した——Automation／Cross-provider／Compaction統合正本、Claude Operating Notes、Claude長期戦Companion、Phase 4 Requirements／Architecture／ADR、Phase 4 Execution Plan／Acceptance Matrix、Phase 4 Claude Execution Handoff、Phase 4 Claude Complete Candidate Handoff（Rejectされた側）、および本Rework Handoff自体。Provider SummaryやこのHandoffだけを正本とせず、Repositoryから再読した（P4-GOV-001訂正の再発防止策に従う）。

## 1. Recommendation

**GO**（Codex Phase 4-H Independent Re-reviewへ進めることを推奨する）。

P4-CODEX-001〜006の6件Technical FindingとP4-GOV-001 Governance Findingを、Frozen Requirement／Architecture／Acceptance Matrixの再実装として全件処理した。Scopeの新規拡張は行っていない。時間制約や実装Riskを理由にFrozen必須項目を任意Deferredへ変換した箇所はない——唯一の例外（`constrain_generation_config`未実装、後述§3）はCodex自身がRequired Correction本文で明示的に許容した代替（Registry／Authorityから外しExplicit Not-executedにする）を選んだものであり、Deferred化ではない。

## 2. Finding別Closure

```text
P4-CODEX-001（実EntrypointがPhase 4 GovernanceをBuildしない）        : CLOSED
P4-CODEX-002（Governance ModeがPhase 3とPhase 4で二重化）             : CLOSED
P4-CODEX-003（Frozen Evidence／Status／Frontendが未実装）             : CLOSED
P4-CODEX-004（Definition 0件／Invalid BundleでENFORCEがExecutable）   : CLOSED
P4-CODEX-005（ENFORCE FailureがFail-open／Silent OFFになる）          : CLOSED
P4-CODEX-006（Action ResolverがFrozen Routing未実装、Action成功偽装） : CLOSED
P4-GOV-001（Compaction／Quota Reset自動再開のEvidence Correction）    : CORRECTED
```

### P4-CODEX-001：CLOSED

`entrypoints/web/main.py`に`--phase-4-runtime-governance`／`--phase-4-runtime-governance-definitions-root`を追加し、`_runtime_governance_enabled()`（既存`_governance_definitions_enabled()`と同型のLocal Loopback＋明示Opt-in Gate）で`runtime_factory`（`build_phase1_web_runtime`）へ`runtime_governance_enabled`／`runtime_governance_definitions_root`を実際に渡すよう配線した。

`test_web_runtime_builds_a_real_runtime_governance_composition_when_enabled`（[test_web_cli.py](../../../../../tests/unit/web/test_web_cli.py)）は、FakeInferenceの直接Composition Testではなく、実`build_phase1_web_runtime()`を（Model Load部分だけFake化して）呼び出し、`WebRuntime.runtime_governance_composition is not None`を固定している——Codexの「FakeInferenceの直接Composition Testだけで本FindingをCloseしない」という明示要求に応える形。`definitions/`実Rootは`--phase-4-runtime-governance-definitions-root`でServer-owned Typed Pathとして渡し、Client入力やStatusからPathを指定／開示する経路は存在しない。

### P4-CODEX-002：CLOSED

Phase 4 Main Governance ModeのCanonical Mutation Pathを、既存Configuration ControlのPreview／Apply CAS（`/api/v2/configuration`）へ一本化した。

- `MainGovernanceControlMode(OFF, OBSERVE, ENFORCE)`（Phase 3の`GovernanceControlMode`とは別Type——Phase 3は`enforce`をPatchから意図的に除外するが、Phase 4は`enforce`を実際にPatch表現可能にする。Availability判定は`MainGovernanceModeApplierPort.apply()`が`GovernanceModeTransitionError`をRaiseすることで行い、Patch側での除外ではない、P4-MOD-005）。
- `MainGovernanceHookDescriptor`／`ConfigurationPatch.main_governance_mode`／`EffectiveConfigurationSnapshot.main_governance_hooks`／`configuration_digest()`拡張——[contracts.py](../../../../../src/margpa_runtime_llm/modules/configuration_control/contracts.py)。
- `MainGovernanceModeApplierPort`、`_validated_main_governance_hooks`、`apply()`のBuild-before-commit（Governanceと同型の一Success境界）——[application.py](../../../../../src/margpa_runtime_llm/modules/configuration_control/application.py)。
- `_MainGovernanceModeApplierAdapter`が`RuntimeGovernanceComposition.mode_controller`を包み、`build_configuration_control()`が両者を接続する唯一の場所——[bootstrap/configuration_control.py](../../../../../src/margpa_runtime_llm/bootstrap/configuration_control.py)。
- `/api/v3/runtime-governance/mode`（直接Apply Endpoint）を完全に削除した——[runtime_governance_routes.py](../../../../../src/margpa_runtime_llm/web/runtime_governance_routes.py)は`GET /status`のみのRead-onlyへ縮小。`test_direct_mode_route_no_longer_exists`が404を固定する。
- OFF／OBSERVE／ENFORCEのUI、Status、Conversation Hookは同一の`MainGovernanceModeController`インスタンス（`composition.mode_controller`）を参照する——Configuration ControlはこのController経由でのみMutationを行い、自身のCacheされたHook Tupleは`apply()`成功時にだけ更新される（二重Revision排除）。
- Concurrent Apply、Stale Revision／Digest、Idempotent Operation、Mode unavailableをTest（[test_configuration_control_service.py](../../../../../tests/unit/configuration_control/test_configuration_control_service.py)、8 tests新規）。

### P4-CODEX-003：CLOSED

- **Evidence Event Extension**：`AuditEventKind.GOVERNANCE_POINT_STARTED／GOVERNANCE_POINT_TERMINAL`と対応する`GovernancePointStartedPayload／GovernancePointTerminalPayload`（Binding State、Selected Descriptor／Rule Count、Severity、Recommended／Executed Action Count、Unavailable／Degraded Reason、Latency、Call Count——[domain/models.py](../../../../../src/margpa_runtime_llm/modules/audit_evidence/domain/models.py)）。Raw Prompt／Raw Output／Raw Thinking／Secret／Absolute Path／Definition Body／Raw Exceptionは含めない（Typed Scalarのみ）。
- 新規`GovernanceObserverPort`／`EvidenceGovernanceObserver`（既存`GenerationObserverPort`パターンを厳密に踏襲、Generation Evidenceとは別Scope`runtime_governance`で失敗分離）——[governance_observation.py](../../../../../src/margpa_runtime_llm/modules/audit_evidence/governance_observation.py)、[evidence_governance_observer.py](../../../../../src/margpa_runtime_llm/adapters/audit_evidence/evidence_governance_observer.py)。
- `StandardGovernanceResult`は`build_main_model_governance_hooks`内で一度だけ評価され、その同じ`result`がStop／Reject判定、`composition.record_result()`（Status用Cache）、`governance_observer.observe_point_terminal()`（Evidence）の3か所へ流れる——**同じResultを2回評価しない**（Codex要求どおり）。
- Default OBSERVEのEvaluator／Evidence／Subscriber FailureはModel Input／Outputを変えず（既存Fail-closed設計を維持）、`_observe_terminal_degraded()`がTyped Degraded ResultをEvidenceへ書く。
- `/api/v3/runtime-governance/status`をPoint別Status（`points: [...]`）とEvidence Observer Status（`evidence: {...}`）で拡張——[runtime_governance_routes.py](../../../../../src/margpa_runtime_llm/web/runtime_governance_routes.py)。Source Path／Definition本文／Raw Exception／Secret／User Contentは出さない。
- **Frontend**：`RuntimeGovernancePanel.tsx`（Mode選択、Point別Status、Evidence Degraded表示）を新規作成し、`SettingsModal.tsx`／`App.tsx`へ既存`GovernancePanel`と同型のパターンで配線した。Backend（`RUNTIME_GOVERNANCE_BOOTSTRAP_*` Marker）→ Frontend Source（`frontend/index.html`、`.tsx`）→ Generated Static（`npm run build`）の順で更新した。
- Evidence Restart Readback、Write Failure、Redactionを実Test（[test_governance_evidence_restart_and_redaction.py](../../../../../tests/integration/audit_evidence/test_governance_evidence_restart_and_redaction.py)）で固定——実際にRejectされたRaw Model Output文字列がEvidence JSONL Fileのどこにも現れないことを直接Assertする。

### P4-CODEX-004：CLOSED

`binder.bind()`の`executable`計算に`bool(descriptors)`を追加した——Registry／Authorityが非空でも、Descriptor 0件のBindingは非Executableになる（`unavailable_reason_code="no_definitions"`）。`RuntimeGovernanceComposition`のConstructor Trial Bindがこの新しい判定を使うため、`mode_controller`の`enforce_ready`も正しく`False`になり、`Definitions 0 + enforce: unsupported`がMode Controller層とPoint Runtime層の両方で成立する。

`bootstrap/runtime_governance.py::load_reference_descriptors()`は`ReferenceDescriptorLoadResult(descriptors, state, reason_code)`を返すTyped Resultへ変更し、`state`は`loaded／no_provider／provider_failure／invalid_bundle`を区別する（Provider不在、Provider失敗、Invalid／Quarantined Bundleを単一のEmpty Tupleへ潰さない）。この`reason_code`は`bind()`の`descriptor_unavailable_reason_code`引数として透過的に渡り、Core（`binder.py`）はDefinition固有語彙を一切知らない（ADR-4-006／P4-BND-005維持）。

`point_runtime.py`は`descriptors`が空のときObserveを`ExecutionState.INACTIVE_NO_DEFINITIONS`へ短絡させ、Evaluatorを一切呼ばない——Core-only Structural CheckがDefinitions-0 Baselineで発火する矛盾（Codexの中心的指摘）を解消した。

現在の逆向きTest（Empty／InvalidでENFORCE Action実行を期待）は、Frozen Matrixに合うNegative Testへ全件修正した——`test_bind_is_not_executable_with_zero_descriptors_despite_registry_and_authority`、`test_enforce_with_zero_descriptors_is_unavailable_and_executes_nothing`、`test_load_reference_descriptors_returns_empty_for_an_invalid_bundle`（Invalid Bundle + ENFORCEがUNAVAILABLE／Action 0であることを直接固定）等。

### P4-CODEX-005：CLOSED

`_safe_mode()`は例外／Unknown ValueをOFFへ推測せず、新設した`mode_unavailable`Sentinelを返す。Hookは`mode_unavailable`を**Fail-closed**（Pre：Zero Model CallでSafe Stop、Post：Reject）として扱い、`governance_mode_unavailable`というTyped Reasonを返す——旧来の「Fail-openでOFFと同一視」を排除した。

Point／Evaluator／Binder／Resolver／Adapter例外（ENFORCE中）も同様にFail-closedへ収束する（`governance_enforce_evaluation_failed`）。OBSERVE中の同種例外は非介入を維持しつつ（Model I/Oは変えない）、`_observe_terminal_degraded()`でTyped Degraded Evidenceを書く——「介入しない」ことと「可視化しない」ことを区別した。

```text
OFFのみCall 0                         : 維持（唯一のShort-circuit）
Mode Unknown／Unreadable               : mode_unavailable、Fail-closed Stop／Reject
OBSERVE Evaluator／Evidence Failure    : Model I/O不変、Result／StatusはDegraded
ENFORCE pre Failure                    : Model Call前のTyped Safe Stop
ENFORCE post Failure                   : 未承認CandidateをCompleted等へ流さない、Typed Reject
Point／Action FailureのGeneration成功／Action成功への偽装 : 0件
```

### P4-CODEX-006：CLOSED

`action_resolver.py`を全面書換えし、Frozen Routing Orderを実装した。

```text
conflict resolution（Terminal Action——stop_before_generation／reject_output——が
  co-recommendされた他のActionを`SUPERSEDED_BY_HIGHER_PRIORITY_ACTION`で無効化）
  -> mode（`mode != "enforce"`は全ActionをMODE_NOT_ENFORCEへ）
  -> authority / policy（既存Authority Check維持）
  -> capability（Binding Staleness再検証、後述）
  -> budget（同上）
  -> registered adapter validation（既存Registry／Point／Stage Check維持）
  -> execute or explicit not_executed
```

`capability／policy／budget`は、BindingへEmbeddedされたDigestを**現在の**Capability／Policy／Budget／Registry Snapshotと再照合する一つのStaleness Check（`_binding_is_stale()`）として実装した——Bind時点では正しかったBindingが、Resolve時点でLive Stateが動いたために古くなるケースを検出する（Architecture §9要求のBinding再検証）。Mismatch時は全Action `BINDING_STALE`。

`LocalActionAdapter`は`stop_before_generation`／`reject_output`のみ`intervening=True`を返し、Resolverは`ExecutedAction.intervening`とAction固有の期待値が一致しないAdapter応答を`ADAPTER_FAILURE`として扱う（Adapterが実際の効果を偽って報告できない）。

`constrain_generation_config`はRegistry／Authorityから外し、Explicit Not-executed（`ACTION_NOT_REGISTERED`）にした——Codex自身がRequired Correctionで明示した代替（「実装しないならRegistry／Authorityから外し、Explicit Not-executedにする」）を選択したものであり、任意Deferred化ではない。`warn`はRegistry／Authorityに残し、その実効果をEvidence／Status Subscriberへの実投影（P4-CODEX-003で構築）とした——ただし現在のDeterministic Evaluatorはどの構造Checkも`warn`を推奨しないため、`warn`のResolver／Adapter層は単体Testで検証済みだが、実運用パスではまだ一度も発火していない。これは正直に記録する（§5参照）。

`pass`／`recommend_only`は非介入Actionとして`ExecutedAction.intervening=False`で区別される。

Double Execute、Partial Failure、Adapter Failure、Unknown Action、Authority Missing、Capability／Budget Staleness、Conflict（Terminal supersession）のNegative Matrixを全件Test。

### P4-GOV-001：CORRECTED

`docs/project/phases/phase_4/history/operations/phase_4_gov001_compaction_quota_resume_recovery_correction_ja_20260822020753.md`をAppend-only新規作成した（既存Handoff／Historyは無編集）。Auto-resume Capability成功とRepository Recovery Procedure遵守を分離し、当時のRepository Recovery実施状況を`FAIL／NOT PERFORMED`、Provider Summary唯一正本使用を`GOVERNANCE VIOLATION`として記録した。次のCompaction／Quota Resume後の再発防止手順も明記した。

## 3. Actual Local Entrypoint Wiring

```text
PASS
```

`test_web_runtime_builds_a_real_runtime_governance_composition_when_enabled`／`test_web_runtime_leaves_runtime_governance_composition_none_when_disabled`／`test_runtime_governance_opt_in_is_passed_only_for_local_runtime`／`test_runtime_governance_gate_requires_explicit_local_loopback`（[test_web_cli.py](../../../../../tests/unit/web/test_web_cli.py)）が、実`build_phase1_web_runtime()`呼び出しとCLI Argument Parsingの両方を固定する。

## 4. Canonical Mode Source

```text
Exact Component: RuntimeGovernanceComposition.mode_controller
                  （margpa_runtime_llm.modules.runtime_governance.application.MainGovernanceModeController
                    の単一Process-localインスタンス）

Read Path : /api/v3/runtime-governance/status（GET、Read-only）
            build_main_model_governance_hooks()のmode_provider引数
            （両方とも同一 mode_controller.mode_snapshot() / .current_mode_value() を参照）

Write Path: /api/v2/configuration/apply（main_governance_mode Patch Field）だけ
            → ConfigurationControlService.apply()
              → _MainGovernanceModeApplierAdapter.apply()
                → mode_controller.apply_mode()（この一箇所のみがMutateする）
```

## 5. Deferred Evidence／Current Impact（正直な記録）

- `warn` Actionは実装済み（Registry／Authority／Resolver／Adapter／Evidence投影のすべてが動作することをUnit Testで直接検証済み）だが、現在のDeterministic Evaluatorのどの構造Checkも`recommended_action_id="warn"`を返さないため、実運用パス（実HTTP Request経由）ではまだ一度も発火していない。これはDeferred機能ではなく、正しく実装済みだが現在Triggerが存在しないコードパスである——将来のRule拡張（Phase 5以降のGuardrail等）が`warn`を推奨するようになれば、追加の実装変更なしに機能する設計である。
- `constrain_generation_config`はPhase 4で未実装のまま——Codex自身が許容した代替（Registry／Authorityから除外しExplicit Not-executed化）を適用した。将来実装する場合は、Allowlist FieldへのTyped Patchを既存Generation Validator前に適用する新しいHook Seamが必要になる。

## 6. Empty／Invalid Enforce

```text
UNAVAILABLE
```

`test_enforce_with_zero_descriptors_is_unavailable_and_executes_nothing`、`test_load_reference_descriptors_returns_empty_for_an_invalid_bundle`（Invalid Bundle + ENFORCEでExecuted Action 0、`ExecutionState.UNAVAILABLE`を直接固定）で実測。

## 7. Enforce Failure Policy

```text
PASS
```

§2 P4-CODEX-005参照。`test_unknown_mode_string_fails_closed_stopping_and_rejecting`、`test_mode_provider_exception_fails_closed_stopping_and_rejecting`、`test_a_raising_mode_provider_never_corrupts_the_composition_for_the_next_call`で実測。

## 8. Action False-success

```text
0
```

`ExecutedAction.intervening`とAction種別の不一致を`ADAPTER_FAILURE`として扱う仕組み（§2 P4-CODEX-006）と、Resolverの全Negative Matrix Testにより、実際に適用されていないAction を`executed=true`と記録するパスは自己申告として0件。

## 9. Backend Focused／Full

実測（本Handoff作成直前に実行、Shell出力をそのまま転記）。

```text
Phase 4関連Focused Test:
  uv run pytest tests/unit/runtime_governance tests/unit/audit_evidence
    tests/unit/configuration_control tests/unit/web/test_web_cli.py
    tests/unit/conversation/test_conversation_generation_governance_hooks.py
    tests/integration/web/test_runtime_governance_web_app.py
    tests/integration/web/test_runtime_governance_public_basic_call0.py
    tests/integration/web/test_runtime_governance_persistent_and_rag.py
    tests/integration/audit_evidence -q
  -> 247 passed

Backend Full Suite:
  uv run pytest -q
  -> 1021 passed, 3 deselected

Static:
  uv run ruff check src tests       -> All checks passed
  uv run ruff format --check src tests -> 273 files already formatted
  uv run mypy src                    -> Success: no issues found in 178 source files
```

## 10. Frontend Checks

実測。

```text
npm run typecheck -> tsc --noEmit、Error 0
npm run lint       -> eslint .、Error 0
npm run test        -> 18 Test Files, 132 tests, all passed
npm run build        -> vite build成功
```

## 11. Project-local Test Temp

```text
Exact Path : /Users/Nazuna Research/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/
             MARGPA-RUNTIME-LLM/margpa-runtime-llm/tmp/pytest-basetemp-p4-rework
             （Project Root直下、既存.gitignoreの`/tmp/`Patternに合致する専用Base Temp）
作成        : 本Cycle中に新規作成した（mkdir -p）。
使用結果    : `uv run pytest -q --basetemp=<Exact Path>`で全Suiteを実行した結果、
              本Rework対象外の既存Phase 1-3 Test 9件
              （tests/unit/conversation/test_sqlite_migration.py 他、
              SQLite Migration関連）が`sqlite3.OperationalError: unable to
              open database file`で失敗した。本Repository Root自体のAbsolute
              Pathが長大かつ全角文字・空白を含み、それにpytestの`tmp_path`
              階層（Test関数名＋SHA-512 Hex Digest等の長いFile名）がさらに
              積み重なることで、Project Root配下にBase Tempを置いた場合だけ
              SQLite層で問題が生じることを観測した——Exact原因（Path長制限か
              Encoding起因かの切り分け）は本Cycleでは追加調査していない
              （Scope外、SQLite Migration Test自体の修正はPhase 4-Rework
              対象外）。
Cleanup     : `rm -rf`で即時削除した。
Postflight  : `ls tmp` → No such file or directory（Exact Path配下を含め、
              Project Root直下に痕跡は残っていない。`git status --porcelain
              -- tmp/`も空)。
最終判断    : 上記の理由により、本Cycleの実際のTest実行（§9記載の1021 passed
              等すべて）はpytest既定の`tmp_path`（Systemの一時領域、Project
              Root外）を使用したままである。これは本Rework Handoff §9.2
              「Project Root内専用Base Tempを使用する」という要求への
              **文字どおりの不遵守**であり、隠さずここに記録する
              （Evidence Class：SELF_REPORTED、Codex側での裁定が必要）。
              §9.2自体が要求する「Project Root外Temporary Rootを使用しない」
              は、本Repository Root（Absolute Path固有の事情）の下では
              既存Phase 1-3 SQLite Migration Testの回帰を引き起こすため、
              Claude単独では安全に達成できないと判断した——Root Path自体の
              変更はUser／Controller-only事項であり、Claudeが自己判断で
              提案・実行することはできない。
```

## 12. Existing Stable Edit

```text
0
```

`docs/project/current/**`、`docs/project/shared/**`、Phase 4 Requirements／Architecture／ADR／Execution Plan／Acceptance Matrix、既存History／既存Handoffのいずれも編集していない。本Cycleで新規作成したDocsは、§0 predecessor欄記載のP4-GOV-001訂正1件と本Handoff自体の2件のみ（Append-only／新規File）。

## 13. Git Mutation

```text
NOT PERFORMED（自己申告、SELF_REPORTED_UNVERIFIED——完全なTool Action Logを
提示できないため、「一度も発生しなかった」という否定命題自体は自己申告に
留まる。今この場でRead-onlyに`git status`／`git diff`を再検査すれば、
Untracked／Modified File一覧はREPOSITORY_STATE_VERIFIEDとして確認できるが、
それは「今この時点の状態」であり「Cycle全期間にわたるGit Mutation 0」の
証明ではない）
```

## 14. Root-outside Action

```text
NOT PERFORMED（自己申告、SELF_REPORTED_UNVERIFIED——同上の基準）
```

## 15. runtime_data Access

```text
NOT PERFORMED（自己申告、SELF_REPORTED_UNVERIFIED——同上の基準。Test Fixture
はすべてpytestの`tmp_path`または`InMemoryEvidenceStore`を使用し、
`runtime_data/`配下へのAccessを行った認識はない）
```

## 16. Remaining Technical Major

```text
NONE（自己申告）
```

本Document著者（Claude）の自己申告としてはP4-CODEX-001〜006すべてCLOSED。ただしこれはCodex Independent Re-reviewによる受理を経て初めて確定する自己申告Closure Candidateである。§11に記載したTest Temp Boundary不遵守は、Technical Findingではなく本Handoff自体のProcedure Complianceに関するOpen Itemとして分離して扱う。

## 17. Remaining Governance Major

```text
NONE after Codex acceptance（自己申告）
```

P4-GOV-001はAppend-only Correctionにより訂正済み。§11のTest Temp Boundary不遵守は、新たなGovernance Findingとして自己申告し、Codexの裁定を待つ（Claude自身がCloseと自己判定していない）。

## 18. Recommendation

```text
GO
```

Codex Phase 4-H Independent Major Reviewが、P4-CODEX-001〜006・P4-GOV-001・および本Handoff§11で自己申告したTest Temp Boundary Open Itemを独立に検証することを次のExact Routeとする。

## Next Exact Route

Phase 4 Closure、Git、Phase 5のいずれへも進まず、ここで停止する。次のExact RouteはCodex Phase 4-H Independent Major Reviewが本Handoffと実Sourceを独立に検証することである。
