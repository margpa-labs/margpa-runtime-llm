# Phase 2-D Test Module Identity Correction Receipt

```yaml
receipt_id: phase_2_d_test_module_identity_correction_20260814035021
status: accepted_correction_lease
phase: phase_2
subphase: phase_2_d
created_at: 2026-08-14 03:50:21 JST
from_role: Phase 2設計担当者役
to_roles:
  - Phase 2実装者役
  - プロジェクト責任者兼設計統括者役
correction_scope: test_package_identity_only
```

## 1. Original Defect

Frozen Handoffで次の2 Test Fileを同時に新設したが、両DirectoryをPython Packageとして識別するMarkerをWrite Leaseへ含めていなかった。

```text
tests/unit/configuration_control/test_configuration_control_contracts.py
tests/unit/web/test_configuration_control_contracts.py
```

PytestのDefault Import Modeでは、Package Boundaryのない同名Fileが共にTop-level Module `test_configuration_control_contracts`としてImportされる。そのため、先に収集されたModuleと後続FileのPathが一致せず、Import File MismatchでCollectionが停止する。

これはProduction Contract／Test Assertionの不具合ではなく、Phase 2-D Frozen HandoffのTest Module Identity Lease不足である。Implementerが停止してDesignerへ返した判断は正しい。

## 2. Accepted Minimal Correction

Phase 2-D Implementerへ、次のFileを**新規作成する権限だけ**を追加する。

```text
tests/unit/configuration_control/__init__.py    NEW, empty package marker only
```

Fileは空のPackage Markerとし、Import、Fixture、Constant、Side Effect、Production Semanticsを持たせない。

## 3. Rationale

Package Marker追加後、Configuration Control側のTestは`configuration_control.test_configuration_control_contracts`として識別される。Package Markerを持たないWeb側は従来どおり`test_configuration_control_contracts`として識別されるため、Module Identityが分離される。

Production Packageは`margpa_runtime_llm.modules.configuration_control`であり、Top-level Test Package `configuration_control`と異なる。したがってProduction Import Contractを変更しない。

Test File Rename、Test内容変更、Pytest Import Mode変更、`pyproject.toml`変更、Production Source変更は不要である。

## 4. Exact Lease

```text
Allowed:
  tests/unit/configuration_control/__init__.py    NEW empty file only

Not allowed by this correction:
  Existing Test File rename / edit
  Other __init__.py creation
  Production Source modification
  Frozen Design Document modification
  pyproject.toml / pytest configuration modification
  Config / Script / runtime_data modification
  Repository外Path
  Git / Network / External action
```

本ReceiptはFrozen Handoff Section 3のTest Write Leaseへ上記1 Pathだけを追加する。その他のAllowed／Forbidden Boundary、Rollback、Report Routeは変更しない。

## 5. Required Validation

Marker作成後、Implementerは次を実行する。

```bash
.venv/bin/pytest --collect-only -q \
  tests/unit/configuration_control/test_configuration_control_contracts.py \
  tests/unit/web/test_configuration_control_contracts.py

.venv/bin/pytest -q \
  tests/unit/configuration_control \
  tests/unit/web/test_configuration_control_contracts.py \
  tests/unit/web/test_configuration_control_static_contract.py \
  tests/integration/web/test_configuration_control_web_app.py \
  tests/unit/inference/test_config_and_registry.py \
  tests/unit/web/test_web_cli.py
```

Validation EvidenceはPhase 2-D Implementer Statusへ追記し、少なくとも次を記録する。

```text
Package marker path: exact
Package marker content: empty
Collection result: PASS / FAIL
Target result: PASS / FAIL
Additional production semantics: 0
Other path expansion: 0
```

MarkerだけでCollection Conflictが解消しない場合は、Test Renameや追加変更を行わず再停止し、Exact ErrorをDesignerへ返す。

## 6. Unchanged Boundaries

- Existing Frozen Requirements／Architecture／ADR／Handoff／Acceptance Matrixは変更しない。
- Existing Source／Test／Configは変更しない。
- Public／Basic、Existing v1、Persistent Conversation、Secret／Path、Recorder、Protected Capture、Agent／Tool／Switchboard境界は不変である。
- Project Root `runtime_data/` Artifact 0を維持する。
- Implementer → Designer → ControllerのReview Routeは不変である。

## 7. Correction Decision

```text
Decision: GO_WITH_MINIMAL_TEST_PACKAGE_MARKER
Added lease: tests/unit/configuration_control/__init__.py only
Rename required: NO
Production impact: NONE
Frozen design semantic change: NONE
```
