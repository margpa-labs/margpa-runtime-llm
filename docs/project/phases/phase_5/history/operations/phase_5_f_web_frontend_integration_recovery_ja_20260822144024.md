# Phase 5-F Web/Frontend Integration Recovery

```yaml
document_id: phase_5_f_web_frontend_integration_recovery_20260822144024
status: append_only_evidence
phase: phase_5
subphase: phase_5_f
recorded_at: 2026-08-22 14:40:24 JST
git_mutation: not_performed
```

Recovery Entry：前Entryは`phase_5_a_to_e_backend_core_recovery_ja_20260822111500.md`。

## 1. Completed（Work Unit別）

### P5-F-WU-001: Bootstrap／Generation Composition統合

- `conversation_generation.py`（`ConversationGenerationSession`/`ConversationGenerationService`）に`guardrail_pre_hook`/`guardrail_post_hook`/`guardrail_stream_guard_factory`をOptional Constructor Paramとして追加（Phase 4 `governance_pre_hook`/`governance_post_hook`と同一Pattern、P5-0-WU-002 Additive方針）。
- Ordering：Guardrail Pre-check→Governance Pre-check（`_guardrail_pre_check() or _governance_pre_check()`）、Governance Post-check→Guardrail Post-check（Security最終Gate、ADR-5-001）。
- `_run_stage()`を全面改修し、`emit_deltas=True`のPathでのみ`IncrementalStreamGuard`をRequest-local Factory経由で挿入。`guardrail_stream_guard_factory`未指定時はByte-identical（P5-ACC-004）。
- `bootstrap/guardrail_governance.py`：`GuardrailGovernanceComposition`（Policy/Authority/Approval/Action Registry/Input・Output Point Runtime/Mode Controller/Last-Result保持）と`build_guardrail_hooks()`。
- `bootstrap/web_application.py`：`guardrail_governance_enabled`Flag、Composition構築、Hook/Stream Guard Factory配線、`WebRuntime.guardrail_governance_composition`公開。
- `entrypoints/web/main.py`：`--phase-5-guardrail-governance` CLI Flag、`_guardrail_governance_enabled()`（Local Loopback＋明示Opt-in必須、Phase 4 `_runtime_governance_enabled`と同一Gate）。
- `web/app.py`：Lifespan Defense-in-depth Loopback Re-check（`guardrail_governance_composition`版）。

自己検出Bug修正：`_StreamGuardDecisionLike` Protocolが素のMutable Attributeを宣言していたためmypyがInvariantとして扱い、Frozen `StreamGuardDecision`が構造的にProtocolを満たさない（Return-type Mismatch）と判定——`@property`によるRead-only Protocolへ修正（本Cycle唯一の新規Type Bug、Test作成中にmypyが検出）。

### P5-F-WU-002: Configuration Control CAS Field

- `GuardrailGovernanceControlMode`（off/observe/enforce）、`GuardrailGovernanceHookDescriptor`を`contracts.py`に追加。`ConfigurationPatch.guardrail_governance_mode`、`EffectiveConfigurationSnapshot.guardrail_governance_hooks`、`configuration_digest()`拡張。
- `ports.py`：`GuardrailGovernanceModeApplierPort`（Main Governanceと同一Applier-may-raise契約）。
- `application.py`：Constructor Param追加、`_validated_guardrail_governance_hooks()`、`_changes()`/`apply()`へのGuardrail分岐。`_EXTERNAL_APPLIER_KEYS`を`{governance_mode, main_governance_mode, guardrail_governance_mode}`へ一般化し、P4-CODEX-009由来の「複数External Applier同時変更禁止」Ruleを3方向へ拡張（元は2方向Pair限定Check）。
- `bootstrap/configuration_control.py`：`_GuardrailGovernanceModeApplierAdapter`、`build_configuration_control()`への配線。
- `web/configuration_contracts.py`：`GuardrailGovernanceHookResponse`、Patch Request/Effective Responseへの反映。

### P5-F-WU-003: Web Route

- `web/guardrail_governance_routes.py`（新規）：`GET /api/v3/guardrail-governance/status`。Read-only専用（Mutation Canonical PathはConfiguration Control CASのみ、Phase 4 `runtime_governance_routes.py`のRationaleと同一）。Detection/Match CountのみをSafe Count-only Projection（Raw Content/Category詳細/Typed Span Offsetは一切露出しない）。
- `web/app.py`：Router登録、`guardrail-bootstrap` HTML Marker（Disabled/Enabled）追加。
- `frontend/index.html`/`web/static/index.html`：`<script id="guardrail-bootstrap">`Marker追加。

### P5-F-WU-004: Frontend Settings UI Panel

- `lib/guardrailGovernanceBootstrap.ts`（Bootstrap Marker Reader、Fail-closed）。
- `components/GuardrailGovernancePanel.tsx`（`RuntimeGovernancePanel.tsx`Pattern踏襲、Lazy Initializer＋Revision Re-sync、Mode Radio Group、Point別Detection/Match/Executed Count表示）。
- `types.ts`：`GuardrailGovernanceMode`/`GuardrailModeDescriptor`/`GuardrailPointStatus`/`GuardrailGovernanceStatus`。
- `api/client.ts`：`fetchGuardrailGovernanceStatus()`。
- `i18n/translations.ts`：ja/en両方に`guardrailGovernance*` Key群（Safety Model Unavailable／Phase 6接続予定Noticeを含む）。
- `App.tsx`：Bootstrap State、Load/Apply Handler、3箇所のGeneration完了Refresh Call、SettingsModalへのProps配線。
- `SettingsModal.tsx`：Props追加、Advanced Tab可視性への算入、Panel描画。
- Production Build（`vite build`）実行——`web/static/{index.html,app.js,app.css}`を実Build成果物で更新（手動Marker編集から実Bundle反映へ切替）。

### P5-F-WU-005: Public/Basic Compatibility Call-0

- `test_guardrail_governance_public_basic_call0.py`（新規）：Public/Basic Exposureで`guardrail_governance_composition`がBindされている場合はApp起動自体を拒否、Call-0状態（未配線）ではChat Behavior完全不変・Status Routeが安全なUnavailable Responseに縮退・index.html Bootstrap Markerが自動的にEnabledへ変わらないことを確認。Phase 4 `test_runtime_governance_public_basic_call0.py`と同一Invariantの鏡写し。

## 2. Test（実測）

```text
Backend Full Suite : 1110 → 1151 passed, 3 deselected（5-F区間で+41、Phase 5-A〜E完了時点1110が起点）
  内訳（新規/拡張ファイル）
    tests/unit/conversation/test_conversation_generation_guardrail_hooks.py         : 13
    tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py : 3
    tests/unit/web/test_web_cli.py（追加分）                                        : 4
    tests/unit/configuration_control/test_configuration_control_service.py（追加分） : 7
    tests/integration/web/test_guardrail_governance_web_app.py                      : 9
    tests/integration/web/test_guardrail_governance_public_basic_call0.py           : 8
  Phase 5-A時点で作成した3件のTest Fixture Bug（test_domain_contracts.py Execution
  State文字列直渡し、test_policy_authority_approval_adapters.py冗長Identity比較、
  test_point_runtime.py型注釈欠如＋Protocol非準拠Fixture）を本Cycleのmypy Strict実行
  （`mypy`単体、Project設定`files=["src","scripts","tests"]`準拠の網羅実行）で新規検出
  し修正——個別File単位のmypy実行では検出されていなかった、Package全体解決時のみ顕在化
  するGapだった。

Frontend Full Suite : 155 → 175 passed, 20 test files
  lib/guardrailGovernanceBootstrap.test.ts        : 5
  components/GuardrailGovernancePanel.test.tsx    : 14
  components/SettingsModal/SettingsModal.test.tsx : 既存Test 2件をFour-bootstrap前提へ修正
                                                     ＋新規1件（Guardrail単独Enabled）

Static：
  Backend  ruff check / ruff format --check / mypy（bare、Project設定準拠）：Phase 5関連
           File全てPASS。mypy残存99件はPhase 1〜4既存File 9件に限定される既知債務
           （本Cycle新規混入0件、逐次確認済み）。
  Frontend tsc --noEmit / eslint . / vite build：全てPASS。Build成果物
           `web/static/{index.html,app.js,app.css}`は実Compileで再生成し、
           Guardrail Bootstrap Markerおよび新Panel Codeの反映を確認。
```

`.p5t/`配下のPytest Basetemp Scratchは各Checkpoint後に削除済み（Project Root直下の使い捨てTest Temp、Phase 4 P4-GOV-002 Correction discipline踏襲）。

## 3. 設計判断・Note

- Guardrail用`_EXTERNAL_APPLIER_KEYS`一般化：Phase 4 P4-CODEX-009/010の「2 External Applier同時Apply禁止」を字面通り2値Setとして実装していた既存Codeを、3値Frozensetへの一般化＋`len(...) > 1`判定へ書き換え。Governance/Main-Governance間の既存Pair Rejection Testは無改変のまま踏襲されることを`test_mixed_governance_patch_is_rejected_before_calling_either_applier`のRe-run（無変更）で確認、加えてMain/Guardrail新PairのRejection Testを新規追加して一般化の正当性を実証した。
- Stream Guard Factory配線：`GuardrailGovernanceComposition.new_stream_guard()`はRequest-local Fresh Instance（Session/Tab間で共有しない、architecture §10 P5-ACC-022）。`conversation_generation.py`は依然として`guardrail_governance`をImportしない——Protocol経由の構造的満足のみ。
- Web Status Routeは`guardrail.context_source`/`guardrail.stream_candidate`のPoint別Statusを対象外とした（前者はPhase 5-Fで未接続、後者はStream Guardが専用Terminal判定を持ち`GuardrailPointRuntime`を経由しないため`last_result_for()`にResultが存在しない設計）——Frontend/Web Routeとも`guardrail.input`/`guardrail.output_candidate`の2 Pointのみ表示する現状の実装Scopeを本Documentで明示する。
- Frontend Safety Model Noticeは翻訳Key`guardrailGovernanceSafetyModelNotice`としてja/en両方に配置し、Runtime Governance Panelの`runtimeGovernanceSemanticBoundaryNotice`と同じ役割（現状の限界とPhase 6接続予定の明示）を果たす。

## 4. Remaining（Phase 5-G）

Phase 5-Fの5 Work Unit（WU-001〜005）は全て完了・検証済み。Phase 5-Gで残る作業：

```text
- Golden Mode/Adversarial Matrix（Definition-0/Guard-Model-0/Valid/Invalid/Stale ×
  OFF/OBSERVE/ENFORCE × Input/Context/Stream/Output × False-Positive/Negative）
- Security/Privacy/Concurrency/Recovery Adversarial検証
- Full Regression/Performance計測
- 最終Completion Handoff（phase_5_claude_complete_candidate_handoff_ja.md）作成
```

## 5. Subphase Recommendation

```text
P5-F-WU-001 : CLOSED（Session/Service/Bootstrap/CLI/Lifespan配線、mypy Protocol Bug自己修正済み）
P5-F-WU-002 : CLOSED（CAS Field、3-way External Applier一般化）
P5-F-WU-003 : CLOSED（Status Route、Safe Count-only Projection）
P5-F-WU-004 : CLOSED（Frontend Panel、実Build確認済み）
P5-F-WU-005 : CLOSED（Public/Basic Call-0、Phase 4鏡写しInvariant確認）
Next         : Phase 5-G（Adversarial Verification／COMPLETE_CANDIDATE）
Recommendation : GO
```
