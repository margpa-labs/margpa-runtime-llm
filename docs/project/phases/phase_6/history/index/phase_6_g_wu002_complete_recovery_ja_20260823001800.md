# Phase 6-G-WU-002 完了 Recovery Entry（Main／Judge／Guard／Governance Layer Identity）

```yaml
document_id: phase_6_g_wu002_complete_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu002_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 00:18:00 JST
```

## 調査結果（Explore Agent、Read-only）

```text
Guard Model     : 実Model Identity Contract（SafetyModelResponse／RawSafetyModelObservation、
                  model_id／exact_revision／artifact_digest_sha512）は存在するが、Production
                  既定AdapterはUnavailableSafetyModelAdapter（Phase 5でArtifact未選択）。
                  実検出は100% Deterministic／Pattern-based（MarkerDetector等）。
                  → Guard Model = None が現在の誠実な既定値。
Guardrail Mode  : 専用Snapshot Classなし、GovernanceModeSnapshot（governance_definitions）を
                  再利用。GuardrailModeController._current_modeがcurrent_modeを保持。
Governance Layer: GovernanceModeSnapshot.digest_sha512はMode State専用（revision+current_modeのみ）
                  であり、Corpus/Manifest Identityではない。真のLayer Identityは
                  governance_definitions.domain.manifest.PackageManifestのpackage_id／
                  manifest_digest_sha512（definitions/manifest.jsonから解決）。
```

## Exact Mutation

```text
Modified:
  src/margpa_runtime_llm/modules/runtime_observability/projection/component_identity_projection.py
    （GuardModelIdentity／GovernanceLayerIdentity、project_guard_model_identity()、
      project_governance_layer_identity() 追加）
  tests/unit/runtime_observability/test_component_identity_projection.py（4 Test追加）
```

## 設計判断

```text
両関数とも「既に解決済みの値」を引数で受け取る設計とし、guardrail_governance／
governance_definitions Moduleへ直接依存しない（Import Cycle回避、および実際の
Provider呼び出しパターンを断定せず、実配線は別WUとする）。
model_id=None／package_id=None を明示的にNONE Stateとして扱い、Unavailableや
Active相当の値を捏造しない（P6-ACC-024A、P6-ACC-054）。
```

## Validation

```text
New Unit Test  : 4 passed（Guard Model 2、Governance Layer 2）
Full Backend   : 1378 passed／3 deselected（回帰0）
Frontend       : 175 passed／20 files（回帰0）
Ruff／Mypy      : Clean（405 source files）
```

## Phase 6-G 残WU（未実施、UI層のためBrowser検証が必要）

```text
P6-G-WU-001 Sidebar Current Model     : 未実施（実API Route + Frontend）
P6-G-WU-002 Advanced Component Identity: Domain層完了。実API Route + Frontend表示は未実施。
P6-G-WU-003 Context／Token Control UI  : 未実施
P6-G-WU-004 Judge／Repair／Recording UI: 未実施
P6-G-WU-005 UI Naming／Legacy Cleanup  : 未実施
P6-G-WU-006 Browser Sync／Accessibility: 未実施
```

## Next Exact Route

Phase 6-G残りはAPI Route配線とFrontend実装＋Real Browser検証を要するため、次Batchで
Backend Route（web/app.py類似Pattern）から着手する。並行してPhase 6-H（Comparative
Experiment）はReal Model Executionを要するため、Route配線後にまとめて実施する方が
Context効率が良いと判断。
