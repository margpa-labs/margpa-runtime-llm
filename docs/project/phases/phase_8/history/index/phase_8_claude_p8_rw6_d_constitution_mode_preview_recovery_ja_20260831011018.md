# P8-RW6-D — Constitution Three-mode Non-activation Preview — Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-RW6-D
finding: P8-CODEX-008
state: complete
provider: Claude
created_at: 2026-08-31 01:10 JST
```

## 結論

`resolve_constitution_mode_preview()`（同一ManifestをOFF／OBSERVE／ENFORCE全てへPure Evaluationする新関数）と`GET /api/v2/constitution/preview`（新規Read-only Route）を実装。Production Active Mode（`WebRuntime.constitution_mode`）はP8 Boundaryどおり触れず、Responseへ`active_production_mode`（常にoff）を明示的に含める。FrontendのConstitutionPanelへ3-Mode比較表示を追加し、「PreviewでありActive Runtime Modeではない」旨を明示するDisclaimerを表示。

OBSERVE／ENFORCEが実Ruleに対して虚偽の差を捏造しないよう、`supported_rule_ids`未指定時は現状の正直な`unsupported_action`を両Modeとも返す（Ruleが`supported`として与えられた場合にのみOBSERVE=`observed`／ENFORCE=`enforced`と分岐することをTestで実証）。

## Changed Paths

```text
src/margpa_runtime_llm/modules/constitution/contracts.py（ConstitutionModePreview系Contract、resolve_constitution_mode_preview()）
src/margpa_runtime_llm/modules/constitution/__init__.py
src/margpa_runtime_llm/web/constitution_contracts.py（Preview Response Contract、project_mode_previews()）
src/margpa_runtime_llm/web/constitution_routes.py（GET /preview）
tests/unit/constitution/test_constitution_contracts.py（新規5件）
tests/integration/web/test_constitution_web_app.py（新規5件）
frontend/src/components/ConstitutionPanel.tsx（Preview比較UI追加）
frontend/src/components/ConstitutionPanel.test.tsx（URL別Mock化、新規2件）
frontend/src/api/client.ts（fetchConstitutionModePreview）
frontend/src/types.ts（ConstitutionModePreview系Type）
frontend/src/i18n/translations.ts
frontend/src/styles/app.css
```

## Focused Verification

```yaml
constitution_unit_and_integration: 42 passed (17+10+新規15内訳含む合算)
backend_full_suite_after: 2123 passed, 7 deselected
frontend_full_suite: 298 passed
frontend_typecheck_lint_build: clean
real_browser_used: false（前Package Incident同様の境界曖昧を回避するため、本Rework全体でReal Browserは使用していない。Backend/Frontend Test Suite＋Typecheck／Build／Code Reviewで代替）
```

Acceptance Target `P8-ACC-021`: PASS（OFF／OBSERVE／ENFORCEの差がProduction経路（REST／UI）でEvidenceとして確認可能になった。Production Active ModeはOFF固定のまま、Runtime Activationは一切発生しない）。
