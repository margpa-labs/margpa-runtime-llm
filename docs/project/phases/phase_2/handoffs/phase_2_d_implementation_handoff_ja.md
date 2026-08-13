# Phase 2-D Configuration Control Implementation Handoff

```yaml
handoff_id: phase_2_d_configuration_control_implementation
status: accepted_and_frozen_for_implementer
phase: phase_2
subphase: phase_2_d
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
review_return_to: Phase 2設計担当者役
final_review: プロジェクト責任者兼設計統括者役
```

## 1. Objective

Local Private専用のNon-persistent Configuration Controlを実装する。Safe Effective Projection、Per-field Source、SHA-512 Digest、Revision CAS、Redacted Preview／Apply、Research／Developer ModeおよびFeature／Recording Hookを提供し、Existing v1／Persistent Conversation／Public／Basic／TOML Profileを変更しない。

## 2. Mandatory Inputs

- [Requirements](../requirements/phase_2_d_configuration_control_requirements_ja.md)
- [Architecture](../architecture/phase_2_d_configuration_control_architecture_ja.md)
- [ADR](../adr/phase_2_d_configuration_control_adr_ja.md)
- [Acceptance Matrix](../operations/phase_2_d_acceptance_matrix_ja.md)
- Existing Config Loader／Effective Config／CLI／Web Runtime Contracts and Tests
- Phase 2-B／2-C Frozen Packages、Source、Tests、Final Reviews、Controller Closure
- [Runtime Data／Recording Architecture](../architecture/phase_2_runtime_data_root_and_recording_architecture_ja.md)

局所矛盾は実装前にDesignerへ返す。Config永続化、Public／Basic Control、Agent／Tool／Switchboard追加で回避しない。

## 3. Write Lease／Allowed Paths

Implementation Source：

```text
src/margpa_runtime_llm/modules/configuration_control/__init__.py        NEW
src/margpa_runtime_llm/modules/configuration_control/contracts.py       NEW
src/margpa_runtime_llm/modules/configuration_control/ports.py           NEW
src/margpa_runtime_llm/modules/configuration_control/application.py     NEW
src/margpa_runtime_llm/bootstrap/configuration_control.py               NEW
src/margpa_runtime_llm/bootstrap/config_loader.py                       MODIFY field source trace only
src/margpa_runtime_llm/bootstrap/web_application.py                     MODIFY optional local composition only
src/margpa_runtime_llm/entrypoints/web/main.py                          MODIFY minimal opt-in only
src/margpa_runtime_llm/web/configuration_contracts.py                   NEW
src/margpa_runtime_llm/web/configuration_routes.py                      NEW
src/margpa_runtime_llm/web/contracts.py                                 MODIFY optional service field only
src/margpa_runtime_llm/web/app.py                                       MODIFY v2 router/local page bootstrap only
src/margpa_runtime_llm/web/static/index.html                            MODIFY hidden control panel/bootstrap placeholder
src/margpa_runtime_llm/web/static/app.js                                MODIFY local capability/control UI only
src/margpa_runtime_llm/web/static/app.css                               MODIFY control UI styling only
```

Tests：

```text
tests/unit/configuration_control/test_configuration_control_contracts.py NEW
tests/unit/configuration_control/test_configuration_control_service.py   NEW
tests/unit/configuration_control/test_effective_config_sources.py        NEW
tests/unit/web/test_configuration_control_contracts.py                   NEW
tests/unit/web/test_configuration_control_static_contract.py             NEW
tests/integration/web/test_configuration_control_web_app.py              NEW
tests/unit/inference/test_config_and_registry.py                          MODIFY source trace regression only
tests/unit/web/test_web_cli.py                                            MODIFY local opt-in matrix only
```

Evidence：

```text
docs/project/phases/phase_2/history/handoffs/
  implementer_status_phase_2_d_<timestamp>.md                 NEW exactly one
```

追加Pathが必要なら無断拡張せず、Exact Path、理由、代替案をDesignerへ返す。

## 4. Forbidden Paths／Actions

```text
config/**
scripts/**
runtime_data/**
src/margpa_runtime_llm/entrypoints/cli/**
src/margpa_runtime_llm/web/access_profiles.py
src/margpa_runtime_llm/web/auth.py
src/margpa_runtime_llm/web/streaming.py
src/margpa_runtime_llm/web/persistent_*.py
src/margpa_runtime_llm/modules/conversation/**
tests/unit/conversation/**
tests/integration/conversation/**
Existing Stable／Frozen Docs／History
pyproject.toml
uv.lock
.gitignore
Repository外Path
```

Existing `/api/v1/**`、`/api/v2/conversations/**`、TOML Profile／Backend Contractを変更しない。Git Mutation、Network、Package Install、External Service、Permission変更、Existing File削除、Production Runtime起動を行わない。

## 5. Implementation Sequence

### D1. Contracts／Service

1. Typed Field、Source、Disposition、Snapshot、Patch、Preview、Apply Result、Safe Errorを作る。
2. Allowlist ProjectorとCanonical SHA-512 Digestを作る。
3. Process-local Revision／Operation Receipt、CAS、Atomic Applyを実装する。
4. `research_developer_mode`だけをLive Fieldにする。

### D2. Source Trace／Hooks

1. Existing LoaderへKnown Field単位のSafe Source Traceを追加する。
2. Existing Constructor互換のDefaultを保つ。
3. Documentation RAGの`disabled／enabled` DescriptorをRestart-required Projectionする。
4. Recording `off` DescriptorをRead-onlyでProjectionし、Metadata／Full／Protected Captureを拒否する。

### D3. Composition／Web API

1. `--configuration-control` Opt-inを追加する。
2. Local／Loopback／Auth disabledをFactory Build前に検証する。
3. Optional ServiceをWeb Runtimeへ追加する。
4. `/api/v2/configuration/**`をTyped Contractへ接続する。
5. Unbound SurfaceはSafe 404、Factory／Projection／Apply Call 0とする。

### D4. Browser UI

1. Root HTMLの固定Boolean BootstrapでLocal Bindingだけを通知する。
2. Enabled時だけConfiguration Runtime／Effectiveを取得する。
3. Effective／Source／Digest／Revision／Disposition、Preview／Apply Resultを表示する。
4. Research Mode ToggleだけLive Applyし、Restart-required FieldはPreview-onlyにする。
5. Browser StorageへConfig Dataを保存しない。

## 6. Required Technical Rules

- ProjectionはExplicit Typed Allowlistのみ。Raw Object dump／Generic recursive redaction禁止。
- Environment Variable名／値、Raw CLI、Raw TOML、Path、CredentialをResponse／HTML／Logへ出さない。
- DigestはCanonical Safe ProjectionだけをSHA-512化し、Volatile Fieldを除外する。
- PreviewはMutation 0。ApplyはOperation ID＋Expected Revision＋Expected Digest必須。
- Duplicate／Stale／Invalid／Restart-required／Mixed PatchはMutation 0。Partial Apply禁止。
- Restart-required ProposalをFile／Browser／Runtime Data／Conversation Storeへ保存しない。
- Research／Developer ModeはAuthority／Policy／Permission／Tool／Agent／Protected Captureを変更しない。
- HookはTyped Component-specific Modeを使い、Opaque Dictionaryや強制`off／observe／enforce`を使わない。
- Recorder Build／Bind／Call 0。Agent／Tool／Switchboard実装 0。
- Public／BasicはControl Service Build／Read／Write／Apply 0、UI非表示、Route Call 0。
- Existing v1／Persistent Conversationを変更またはControl Stateへ結合しない。

## 7. Required Tests

- Schema：Unknown／Duplicate／Invalid／Oversize／Protected Field拒否。
- Source：各Precedence、Environment値非露出、Existing Resolution Regression。
- Digest：Order independent、Same State same Digest、Mutation changes Digest。
- Service：Preview Read-only、CAS Conflict、Duplicate Operation、No-op、Atomic Mixed Patch、Restart-required Mutation 0。
- Authority：Research Mode onでもPolicy／Permission／Protected Capture／Recorder Call 0。
- Hook：RAG Descriptor、Recording OFF、Metadata／Full拒否、Unknown Component拒否。
- Exposure：Local opt-in PASS、Public／Basic／Non-loopback／Auth enabledはBuild前Failure、通常Public／Basic Call 0。
- Web：Safe Projection／Error、404 Unbound、No Secret／Path、Bootstrap／UI Capability。
- Static：Public／Basic Configuration Fetch 0、Browser Storage 0、ja／en、Existing Chat／Persistence UX不変。
- Test ArtifactはMemory／`tmp_path`だけでProject Root `runtime_data/` 0。

## 8. Validation Commands

```bash
.venv/bin/pytest -q \
  tests/unit/configuration_control \
  tests/unit/web/test_configuration_control_contracts.py \
  tests/unit/web/test_configuration_control_static_contract.py \
  tests/integration/web/test_configuration_control_web_app.py \
  tests/unit/inference/test_config_and_registry.py \
  tests/unit/web/test_web_cli.py

.venv/bin/pytest -q \
  tests/unit/inference \
  tests/unit/conversation \
  tests/integration/conversation \
  tests/unit/web \
  tests/integration/web

.venv/bin/ruff format --check src tests
.venv/bin/ruff check src tests
.venv/bin/mypy
node --check src/margpa_runtime_llm/web/static/app.js
node --test tests/unit/web/safe_markdown.test.mjs
.venv/bin/pytest -q
```

Node不在のSkipは既存Contractに従うが、Python Static ContractでConfiguration UI／Storage／Secret Boundaryを必ず検証する。

## 9. Boundary Evidence

Implementer Statusへ次を記録する。

```text
Changed paths: exact list
Acceptance IDs: PASS / FAIL
Target / Regression / Static / Full results
Existing v1 mutation/call: 0 / exact finding
Persistent Conversation mutation/call: 0 / exact finding
Public / Basic control build/read/write/apply/route-call: 0 / exact finding
Tracked config / environment / CLI write: 0 / exact finding
Secret / path / raw config projection: 0 / exact finding
Restart proposal persistence: 0 / exact finding
Recorder / protected capture / agent / tool call: 0 / exact finding
Project Root runtime_data artifact: absent / exact finding
Known limitations / rollback
```

## 10. Return Route

```text
From   : Phase 2実装者役
To     : Phase 2設計担当者役
Result : PASS | PARTIAL | BLOCKED
File   : implementer_status_phase_2_d_<timestamp>.md
```

DesignerがSource／Test／Statusを独立Reviewし、局所FindingをImplementerへ返す。Designer PASS後だけControllerがClosure Reviewを行う。ImplementerはUserへ直接Completionを返さない。

## 11. Rollback

Rollback UnitはSection 3のAllowed Source／TestとImplementer Statusだけである。Existing Config Input、TOML Profile、Conversation Domain／Persistence、v1 Contract、Access ProfileをRollback対象へ含めない。

TestはMemory／`tmp_path`だけを使う。Project RootまたはRepository外にArtifactを誤作成した場合は削除せず停止し、Controller／Userへ報告する。

## 12. Completion

- Acceptance Matrix全Required PASS。
- Target／Regression／Static／Ruff／Mypy／Full PASS。
- Public／Basic Control 0、Existing v1／Persistent Conversation不変。
- Secret／Path Projection 0、Config Persistence 0、Recorder／Protected Capture／Agent／Tool 0。
- Designer Design Conformance PASS。
