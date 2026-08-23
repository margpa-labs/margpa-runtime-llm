# P6-CODEX-005 Four Component Identities — Rework Complete

```yaml
document_id: phase_6_codex_p6_codex_005_four_component_identities
status: current_recovery_entry
phase: phase_6
work_unit: p6_codex_005_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 05:55:00 JST
```

## 発見

```text
Domain層のproject_guard_model_identity()／project_governance_layer_identity()
はPhase 6-G-WU-002で実装・Unit Test済みだったが、Web Route
（runtime_model_control_routes.py `/status`）とFrontend
（RuntimeModelStatusPanel.tsx）はMain／Judgeの2 Rowしか実際には配線して
いなかった。Governance Layer Identityの真の材料
（governance_definitions.domain.manifest.PackageManifestのpackage_id／
manifest_digest_sha512）も、GovernanceObserveSummary自体に一度も
含まれていなかった（Compiled Plan Digestのみ）。
```

## Exact Mutation

```text
Backend:
  Modified:
    src/margpa_runtime_llm/modules/governance_definitions/runtime.py
      + GovernanceObserveSummary.package_id／manifest_digest_sha512
      + _run_observe_pipeline()で実Manifestからこれらを実際に設定
        （新規Provider呼び出し無し、既にLoad済みのmanifestから抽出するだけ）
    src/margpa_runtime_llm/web/runtime_model_control_routes.py
      + GuardModelIdentityResponse／GovernanceLayerIdentityResponse追加
      + RuntimeModelStatusResponseへguard_model／governance_layer追加
      + _project_status()がrequest.app.stateのgovernance_definitions_runtime
        （Optional）からGovernance Layer Identityを実際に投影、Guard Modelは
        model_id=Noneを明示（Phase 5の誠実な既定値）
  Created:
    tests/integration/governance_definitions/test_observe_summary_governance_layer_identity.py
      （2 Test、実Repository Bundle使用）

Frontend:
  Modified:
    frontend/src/types.ts（RuntimeModelGuardIdentity／
      RuntimeModelGovernanceLayerIdentity追加）
    frontend/src/components/RuntimeModelStatusPanel.tsx
      （Guard Model／Governance Layerの2 Row追加）
    frontend/src/i18n/translations.ts（JA／EN、4 Key追加）
    frontend/src/components/RuntimeModelStatusPanel.test.tsx
      （既存Fixture更新、新規Test1件追加）
```

## 設計判断

```text
Guard Model model_id=None固定: bootstrap/guardrail_governance.pyには
Safety Model Artifact識別Logicが一切存在しない（Phase 5の既定Adapterは
UnavailableSafetyModelAdapter）。実配線コストとRisk（guardrail_governance
Compositionへの新規依存追加）に見合う実Value（常にNoneを返すだけ）が
無いため、Web Route側でNoneを明示的にHard-codeする——これは"捏造"では
なく、実際に存在しないものを実際に存在しないと申告する誠実な実装である。
Governance Layerは実Wiring: GovernanceDefinitionsRuntimeは既にapp.state
に条件付きBind済み（--phase-3-governance-definitions）のため、
getattr(request.app.state, "governance_definitions_runtime", None)で
安全に参照し、OBSERVE以降実行済みなら実Package Identityを、そうでなければ
Noneを返す——Fake値へのFallbackは一切行わない。
```

## Validation

```text
Backend Full: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider --basetemp=.venv/.t/f
  1410 passed, 5 deselected in 62.82s（新規2 Test含む、回帰0。既存の
  test_status_degrades_safely_when_not_bound の完全一致AssertionをGuard/
  Governance追加分だけ更新）
Ruff: All checks passed!
Mypy: Success: no issues found in 424 source files
Frontend: typecheck PASS／lint PASS（Warning 0）／
  Test Files 23 passed (23) / Tests 191 passed (191)（新規1 Test含む）／
  build PASS
```

## Acceptance Cross-check

```text
P6-ACC-053（Main／Guard／Judge／Governance Layerを別Row表示）: PASS
P6-ACC-054（Guard Model NoneとGuardrail Modeを混同0）: PASS（既存Domain
  層のTestに加え、Web Route側もGuardrail Mode Stateとは完全に独立した
  guard_model.model_id=Noneを返す——Guardrail Mode Enforceの状態に一切
  依存しない）
P6-ACC-055（Governance LayerはManifest／Digest／Bindingから導出）: PASS
  （実Repository Bundleを使ったIntegration Testで直接検証）
P6-ACC-024A（Requested CandidateをCurrentへ昇格0、None／Unavailable捏造0）:
  PASS（Guard Model／Governance LayerともにNoneをそのままNoneとして返す
  経路をTestで確認、代替値へのFallback無し）
```

## Next Exact Route

P6-CODEX-001／002（Live Judge／Repair Integration、最大規模のRework）へ
進む。
