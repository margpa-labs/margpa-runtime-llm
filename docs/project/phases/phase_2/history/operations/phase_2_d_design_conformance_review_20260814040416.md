# Phase 2-D Design Conformance Review

```yaml
review_id: phase_2_d_design_conformance_review_20260814040416
status: partial_rework_required
phase: phase_2
subphase: phase_2_d
created_at: 2026-08-14 04:04:16 JST
from_role: Phase 2設計担当者役
to_role: プロジェクト責任者兼設計統括者役
rework_to_role: Phase 2実装者役
result: PARTIAL
closure_recommendation: REWORK
```

## 1. Review Scope

次を独立Reviewした。

- Phase 2-D Requirements／Architecture／ADR／Handoff／Acceptance Matrix。
- Design Freeze ReceiptおよびTest Module Identity Correction Receipt。
- `implementer_status_phase_2_d_20260814035807.md`。
- Frozen Handoff Section 3の全Allowed Source／TestとCorrection Package Marker。
- Forbidden Path、Existing v1／Persistent Conversation／Public／Basic／TOML Profile、Browser Storage、Runtime Data Boundary。

Source／Test／Stable Docs／Configの変更は行っていない。

## 2. Finding

### P2D-REV-001 — Major／Required Hook Availability Contract Incomplete

対象：

```text
src/margpa_runtime_llm/bootstrap/configuration_control.py
src/margpa_runtime_llm/modules/configuration_control/application.py
tests/unit/configuration_control/test_effective_config_sources.py
tests/unit/configuration_control/test_configuration_control_service.py
```

現状のBootstrapは、`DocumentationRagEffectiveState.ENABLED`の場合だけ`FeatureHookDescriptor.available=True`とする。

```text
effective state = DISABLED
adapter state   = availableだがfeature profileでdisabled
current output  = current_mode=disabled, available=false
```

`DISABLED`はAdapter unavailableではないため、これはSafe Effective Hook Projectionとして不正確である。さらにServiceは、`available=false`でも`enabled`へのRestart-required Previewを許し、`current_mode`が`allowed_modes`に含まれない矛盾DescriptorもConstructorで受理する。

影響はConfiguration HookのAvailability／Preview結果に限定される。Authority昇格、Public／Basic露出、Secret／Path露出、Runtime Apply、Persistence、Recorder／Protected Capture／Agent／Tool Callは発生しない。ただしP2D-HOK-001とTyped Hook ValidationをRequired Acceptanceとして閉じることはできない。

## 3. Exact Rework Route

ImplementerはFrozen Write Lease内の次の4 Pathだけを変更する。

```text
src/margpa_runtime_llm/bootstrap/configuration_control.py                 MODIFY
src/margpa_runtime_llm/modules/configuration_control/application.py       MODIFY
tests/unit/configuration_control/test_effective_config_sources.py         MODIFY
tests/unit/configuration_control/test_configuration_control_service.py    MODIFY
```

Required Correction：

1. `DocumentationRagEffectiveState.DISABLED`と`ENABLED`を`available=true`へ写像し、`UNAVAILABLE`と`DENIED`だけを`available=false`へ写像する。
2. Feature Hook Constructor Validationで、Component Key、Component-specific Allowed Modes、Current Mode membership、Restart-required Dispositionおよび`enabled + unavailable`矛盾をFail-closedする。
3. `available=false`のHookに対するMode変更Preview／ApplyをUnsupported／Mutation 0にする。Current Modeと同一のNo-opはState不変を維持する。
4. DISABLED／ENABLED／UNAVAILABLE／DENIEDのProjection Matrix、矛盾Descriptor拒否、Unavailable Enable拒否／Mutation 0をTestする。

新Path、Web Contract、Static UI、Config Loader、Conversation、Public／Basic、Frozen Docsを変更しない。

Rework Statusは次の1 Fileだけを新規作成する。

```text
docs/project/phases/phase_2/history/handoffs/
  implementer_rework_status_phase_2_d_<timestamp>.md
```

```text
From   : Phase 2実装者役
To     : Phase 2設計担当者役
Finding: P2D-REV-001
Result : PASS | PARTIAL | BLOCKED
```

## 4. Acceptance Result

```text
FAIL / REWORK:
  P2D-HOK-001

PARTIAL pending P2D-REV-001:
  P2D-SCH-002

PASS:
  P2D-EXP-001..003
  P2D-CMP-001..003
  P2D-SEP-001..003
  P2D-SCH-001,003
  P2D-EFF-001..005
  P2D-APL-001..008
  P2D-HOK-002..003
  P2D-PRV-001..005
  P2D-UX-001..003 (automated/static scope)
  P2D-QA-001..005
```

実Browser Manual MatrixはController／User Acceptance Gateとして残るが、P2D-REV-001とは別であり、Technical Reworkの自動Blockerを追加しない。

## 5. Independent Validation

```text
Target:
  96 passed in 0.60s

Config／Conversation／Web Regression:
  392 passed in 4.06s

Ruff check (Phase 2-D exact source/test scope):
  PASS

Mypy:
  PASS, 165 source files

Correction Package Marker:
  0 bytes, production semantics 0

Forbidden files newer than Frozen Handoff:
  0

Persistent Web forbidden files newer than Frozen Handoff:
  0

Config／Script／Access／Auth／Streaming／Persistent Path diff:
  0

Project Root runtime_data:
  ABSENT

Configuration Browser Storage sensitive writes:
  0
```

Adversarial Inspectionでは、Allowed Modesが`disabled`だけでCurrent Modeが`enabled`の矛盾Feature DescriptorをServiceが受理することを確認した。これがP2D-REV-001の再現Evidenceである。

## 6. Boundary Review

- Typed Field Projectionは8 Field Allowlistで、Raw Object Dump／Generic Recursive Redactionを使用していない。
- Field Source Traceは値と分離され、Environment Variable名／値を返さない。
- DigestはSafe ProjectionのCanonical Sorted JSONをSHA-512化し、Revisionは成功Live Mutationだけ増加する。
- CAS、Applied Operation Replay、Mixed Patch、Unsupported Patch、No-opはMutation 0を維持する。
- Research ModeはProcess-localで、Authority／Policy／Permission／Protected Captureを追加しない。
- Restart ProposalのTracked File／Browser／Runtime Data／Conversation Store Stageは0。
- Public／Basic通常経路のConfiguration Control Build／Read／Write／Apply／Browser Route Callは0。Accidental BindingはLifespanでもFail-closedする。
- Existing v1／Persistent Conversation／Config Profile、Recorder／Protected Capture／Agent／Tool／SwitchboardはPhase 2-Dで変更されていない。
- Test Module Identity Correctionは空Package Marker 1件だけで、追加Production Semantics 0。

## 7. Closure Recommendation

```text
Technical result      : PARTIAL
Required local rework : P2D-REV-001 only
Controller closure    : DO NOT CLOSE YET
Rework route          : Implementer -> Designer -> Controller
Scope expansion       : NOT REQUIRED
```

P2D-REV-001修正とFocused Regression PASS後、DesignerがFinal Conformance Reviewを行う。他のDeferred事項を再活性化しない。
