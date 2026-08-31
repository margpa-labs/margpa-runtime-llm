# Phase 8 Claude P8-C Provisional Runtime Constitution — Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-C
state: complete
provider: Claude
created_at: 2026-08-30 22:17 JST
```

## 結論

```yaml
p8_c_established: true
mvp_blocker_open: 0
critical_open: 0
major_open: 0
```

新規Module `modules/constitution`（Manifest／Rule／CapabilityView／Generic Resolver）を、既存GD（Guardrail／Governance）Conceptと独立に実装した。P8-REQ-015「Constitution/GD Providerを並列独立に扱う」方針に従い、既存`GovernanceMode`／`GuardrailGovernanceMode`とは型を共有せず、`resolve_decisions()`は`rule_id`のOpaque Setのみを受け取るGeneric Resolverとして設計している（P8-REQ-019）。`ConstitutionMode.OFF`は常に「未評価」を意味し、Rule／Manifestが実在してもEnforced/Observedを偽装しない（P8-REQ-016）ことを構造Testと統合Testの両方で確認済み。

## Work Unit別Status

| Work Unit | Status | 備考 |
|---|---|---|
| P8-C-WU-001（Constitution Contracts／Ports） | COMPLETE | `ConstitutionMode`/`ConstitutionRule`/`ConstitutionManifest`/`CapabilityView`/`ConstitutionDecision`、Generic `resolve_decisions()` |
| P8-C-WU-002（JSON File Provider・Digest自己検証） | COMPLETE | `JsonFileConstitutionProvider`、Fail-closed（not_present/corrupt/digest_mismatch/missing_field/malformed_rule） |
| P8-C-WU-003（実Manifest Artifact作成） | COMPLETE | `constitution/manifest.json` + 3 Rule Markdown、Digest実測・検証済み |
| P8-C-WU-004（REST Route・Bootstrap配線） | COMPLETE | `GET /api/v2/constitution/runtime`、`entrypoints/web/main.py`で無条件Compose |
| P8-C-WU-005（Frontend表示：ConstitutionPanel） | COMPLETE | `ConstitutionPanel.tsx`新規、`SettingsModal`のAdvanced Categoryへ配線 |

## 実装概要

### P8-C-WU-001/002: Contracts / Ports / Provider

- `modules/constitution/contracts.py`：`ConstitutionMode`（`off`/`observe`/`enforce`のStrEnum）、`ConstitutionRule`（`rule_id`はPattern`^[a-z][a-z0-9-]{2,63}$`で制約）、`ConstitutionManifest`（`revision`/`digest_sha512`/`rules`）、`ConstitutionManifestUnavailable`（型付きUnavailable、例外ではなく戻り値として使う設計）、`CapabilityView`（`view`/`mode`/`rule_ids`のみ — Authority形状のFieldは構造的に存在しない）、`ConstitutionDecision`、`compute_manifest_digest()`（Canonical JSON Digest、ProviderとTest/Toolingが同一関数を共有）、`resolve_capability_view()`、`resolve_decisions()`。
- `modules/constitution/ports.py`：`ConstitutionProviderPort` Protocol。
- `adapters/constitution/json_file_provider.py`：`JsonFileConstitutionProvider(project_root: Path)`。ファイル不在・JSON破損・Digest不一致・必須Field欠落・個別Rule不正の全てをFail-closedで`ConstitutionManifestUnavailable`へ収束（例外を投げない）。**Digestは常にProvider側で再計算し、On-disk側の自己申告Digestは信用しない**（P8-REQ-018）。

### P8-C-WU-003: 実Manifest Artifact

- `constitution/manifest.json`（Project Root、実File）：Digest `a10bbc7dd74ce02a33eb4f64413599f84bd044c2a93a299b4a3471d1d2699d3e7420c5cc7eb44345998aba0974a154626b3401f7f8b396a967235fb72d1aab29`（`tests/unit/constitution/test_json_file_provider.py::test_real_repository_manifest_loads_and_verifies`で実File読込・検証を実施）。
- `constitution/rules/{no-secrets-in-external-evidence,untrusted-content-never-instruction-authority,external-write-requires-human-gate}.md`：3件。いずれもP8-A（Web Evidence Untrusted Framing）／既存Guardrail Conceptと矛盾しない内容として起票。

### P8-C-WU-004: REST Route / Bootstrap配線

- `web/constitution_contracts.py`：`ConstitutionCapabilityViewResponse`/`ConstitutionRuntimeResponse`/`project_capability_views()`。
- `web/constitution_routes.py`：`create_constitution_router()`（`GET /api/v2/constitution/runtime`）、`ConstitutionWebError`、`constitution_error_response()`。Provider未Bind・Manifest不在・Digest不一致の全てが同一の安全な404（`constitution_unavailable`）へ収束し、500を返さない（統合Testで確認）。
- `web/contracts.py`：`WebRuntime`へ`constitution_provider: ConstitutionProviderPort | None = None`/`constitution_mode: ConstitutionMode = ConstitutionMode.OFF`を追加。
- `bootstrap/constitution.py`：`build_constitution_provider(*, project_root: Path)`。
- `bootstrap/web_application.py`：`constitution_provider`/`constitution_mode`をParamとして受け`WebRuntime`へ配線。
- `entrypoints/web/main.py`：`build_constitution_provider(project_root=PROJECT_ROOT)`を無条件Compose（CLI Flag／Mode昇格は本Packageの対象外、Comment付きで明記）。
- `web/app.py`：`create_constitution_router()`をRegister、`ConstitutionWebError`用Exception Handlerを追加。

### P8-C-WU-005: Frontend表示

- `frontend/src/api/client.ts`：`fetchConstitutionRuntime()`（`GET /api/v2/constitution/runtime`）。
- `frontend/src/types.ts`：`ConstitutionView`/`ConstitutionMode`/`ConstitutionCapabilityView`/`ConstitutionRuntime`。
- `frontend/src/components/ConstitutionPanel.tsx`（新規）：`FeatureModesPanel.tsx`の自己完結Fetch-on-visible Patternに倣うが、Constitution ManifestはStatic Local Fileであり動的に変化しないため、Polling（`setInterval`）は追加していない。Revision／Digest（短縮表示、Full値は`title`属性）／Rule数、View別（chat/agent/tool）のMode（OFF/OBSERVE/ENFORCE — 常に明示的な値として表示、`active`/`inactive`のような曖昧な二値化はしない、P8-REQ-016に対応）とRule件数を表示する。Fetch失敗時はErrorを表示せずSilentlyに非表示（他のOptional Panelと同じ「静かなDegrade」規約、P8-REQ-013）。
- `frontend/src/components/SettingsModal/SettingsModal.tsx`：`<ConstitutionPanel>`を`<FeatureModesPanel>`直後、Advanced Category内へ配線。
- `frontend/src/i18n/translations.ts`：`constitutionTitle`/`constitutionNote`/`constitutionLoading`/`constitutionRevisionLabel`/`constitutionDigestLabel`/`constitutionRuleCountLabel`/`constitutionModeOff`/`constitutionModeObserve`/`constitutionModeEnforce`をja/en両方へ追加。
- `frontend/src/styles/app.css`：`.constitution-view-row`/`.constitution-view-name`/`.constitution-view-mode`/`.constitution-view-rule-count`（既存の`--border-surface`Variableを使用、新規Variable追加なし）。

## Changed Paths

Backend Source（10）：
```text
src/margpa_runtime_llm/modules/constitution/__init__.py
src/margpa_runtime_llm/modules/constitution/contracts.py
src/margpa_runtime_llm/modules/constitution/ports.py
src/margpa_runtime_llm/adapters/constitution/__init__.py
src/margpa_runtime_llm/adapters/constitution/json_file_provider.py
src/margpa_runtime_llm/web/constitution_contracts.py
src/margpa_runtime_llm/web/constitution_routes.py
src/margpa_runtime_llm/bootstrap/constitution.py
src/margpa_runtime_llm/bootstrap/web_application.py（既存Fileへ追記）
src/margpa_runtime_llm/entrypoints/web/main.py（既存Fileへ追記）
src/margpa_runtime_llm/web/app.py（既存Fileへ追記）
src/margpa_runtime_llm/web/contracts.py（既存Fileへ追記）
```

Backend Test（3）：
```text
tests/unit/constitution/test_constitution_contracts.py
tests/unit/constitution/test_json_file_provider.py
tests/integration/web/test_constitution_web_app.py
```

実Artifact（4）：
```text
constitution/manifest.json
constitution/rules/no-secrets-in-external-evidence.md
constitution/rules/untrusted-content-never-instruction-authority.md
constitution/rules/external-write-requires-human-gate.md
```

Frontend Source（6）：
```text
frontend/src/components/ConstitutionPanel.tsx
frontend/src/components/SettingsModal/SettingsModal.tsx
frontend/src/api/client.ts
frontend/src/types.ts
frontend/src/i18n/translations.ts
frontend/src/styles/app.css
```

Frontend Test（1）：
```text
frontend/src/components/ConstitutionPanel.test.tsx
```

Static Artifact（1）：
```text
src/margpa_runtime_llm/web/static/app.js（Build Artifact、npm run build実行済み、app.cssも再生成済み）
```

## Canonical Verification

```text
Backend: uv run pytest -q  -> 2006 passed, 7 deselected（Regression 0、前Package終了時点と同数）
         uv run mypy src   -> Success: no issues found in 331 source files
         uv run ruff check . -> All checks passed

Frontend: npx tsc --noEmit -> clean
          npm test         -> 288 passed（32 files）（P8-B完了時点285 + ConstitutionPanel新規3 = 288、Regression 0）
          npm run lint     -> clean
          npm run build    -> succeeded、app.js/app.css再生成済み
```

## Internal Review（1 Cycle）

1. **Controller Issue解消**：該当なし（新規Controller Issue報告はまだない）。
2. **GD Conceptとの非混同**：`ConstitutionMode`は既存`GovernanceMode`/`GuardrailGovernanceMode`と型を共有せず、`resolve_decisions()`はOpaque `rule_id` Setのみを受け取る（GD固有型を一切import/参照しない）ことをGrepで確認済み。P8-REQ-015/019準拠。
3. **OFF＝allow all禁止**：`test_off_mode_never_reports_enforced_or_observed_even_when_bound`（Backend統合Test）と、`ConstitutionPanel.tsx`のMode表示（OFF/OBSERVE/ENFORCEを常に明示的な別Labelとして表示）の両方で二重に保証。P8-REQ-016準拠。
4. **Authority非付与の構造保証**：`CapabilityView.model_fields`をScanし、禁止語（`authority`等）を含むFieldが存在しないことを検証するStructural Unit Testが既に存在（Backend）。Frontend側`ConstitutionCapabilityView`型もBackend Responseの型をそのまま反映しており、独自のAuthority-shaped Fieldを追加していない。
5. **Fail-closed一貫性**：Provider未Bind・Manifest不在・JSON破損・Digest不一致・必須Field欠落・個別Rule不正の全パターンが、Backend側は同一の404（`constitution_unavailable`）、Frontend側は同一のSilent-absence（Panel非表示、Error Banner無し）へ収束することを確認。
6. **Scope遵守**：Root外0、Git Mutation 0（`git status`/確認のみ）、Real Network 0、Install 0、Provider Memory 0、Real Browser/Model 0、Phase 8 Closure/Phase 9/Roadmap 0。

Critical／Major：0件。Minor：1件（非Blocking、Stable未解決へ記録）：
- **P8-RW-C-IR-001**: `ConstitutionMode`の`observe`/`enforce`への昇格経路（CLI Flag等）は本Packageの対象外のまま未実装（`entrypoints/web/main.py`は`ConstitutionMode.OFF`固定でCompose）。P8-C自体はManifest Provider＋Read-only表示の基盤成立が目的であり、要件上の欠落ではないが、P8-D以降でApproval/Tool Harnessと接続する際に昇格経路の設計が必要になる。

## P8-ACC-019〜025 Disposition

| ID | Disposition | 根拠 |
|---|---|---|
| P8-ACC-019 | PASS | `ConstitutionMode`OFF/OBSERVE/ENFORCEが常に明示的な値として存在し、OFFは`resolve_decisions()`内で常に`not_evaluated`系Outcomeへ収束（`test_off_mode_never_reports_enforced_or_observed_even_when_bound`） |
| P8-ACC-020 | PASS | `compute_manifest_digest()`をProvider側で再計算しOn-disk自己申告Digestと比較、不一致は`digest_mismatch`Unavailableへ収束（`test_json_file_provider.py`のDigest系5 Test） |
| P8-ACC-021 | PASS | `CapabilityView`構造Testで禁止語Scanを実施、Authority形状のFieldが存在しないことを確認 |
| P8-ACC-022 | PASS | `resolve_decisions()`はOpaque `rule_id` Setのみを受け取るGeneric Resolver、GD固有型のImport 0（Grep確認） |
| P8-ACC-023 | PASS | Provider未Bind／Manifest不在／Digest不一致の全てがWeb層で同一の安全な404へ収束、500 0件（`test_constitution_web_app.py`5 Test） |
| P8-ACC-024 | PASS | 実`constitution/manifest.json`をProjectへ配置し、実File経由でDigest検証が成立することを`test_real_repository_manifest_loads_and_verifies`で確認 |
| P8-ACC-025 | PASS | Frontend `ConstitutionPanel`がRevision/Digest/Rule数/View別Mode+Rule件数を表示し、取得失敗時はErrorを出さず静かに非表示（`ConstitutionPanel.test.tsx`3 Test） |

**P8-ACC-019〜025 全7件PASS。P8-C成立。**

## Action Inventory

```yaml
network_actions: 0
npm_install_or_download: 0
node_runtime_switch: 0
git_mutation_actions: 0
git_read_only_actions: 0
backup_actions: 0
user_runtime_data_access: 0
real_model_access: 0
real_browser_access: 0
provider_memory_used: false
project_root_外_access_executed: 0
```

## Exact Next Work Unit

```text
Next: P8-D Dev Agent／Tool／Approval Harness Foundation
  Do Not Repeat: P8-A（WU-001〜006）、P8-B（WU-001〜004）、P8-C（WU-001〜005）は本Recoveryで完成済み。
```
