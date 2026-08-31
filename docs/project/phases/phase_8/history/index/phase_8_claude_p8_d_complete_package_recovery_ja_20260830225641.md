# Phase 8 Claude P8-D Dev Agent／Tool／Approval Harness Foundation — Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-D
state: complete
provider: Claude
created_at: 2026-08-30 22:56 JST
```

## 結論

```yaml
p8_d_established: true
mvp_blocker_open: 0
critical_open: 0
major_open: 0
```

新規Module `modules/dev_agent`（Stable Capability ID、Run/Step/Plan/Completion Contract、Tool Port/Registry/Descriptor、Approval Gate、Frozen Authorization Envelope）を実装し、Fake／Deterministic Tool Adapterのみを本番Composition（`bootstrap/dev_agent.py`）へ配線した。MCP Client Adapterは`McpClientPort`のPort定義とFixture実装（`FixtureMcpClient`）のみをShip、Real MCP ServerへのProduction配線は行っていない（Bootstrap未許可のRemote MCP／Real Networkを一切実行しないため）。Max Step／Deadline／Retry／Approval-Gate／Cancel／Late-Result-rejectionの全項目をUnit Testで個別に、important-gate-only Golden PathをUnit TestとREST統合Testの両方で確認した。

## Work Unit別Status

| Work Unit | Status | 備考 |
|---|---|---|
| P8-D-WU-001（Stable Capability ID／Contracts） | COMPLETE | `CapabilityId`（chat/dev_agent）、`RunState`/`StepState`/`RunCompletionOutcome`（全て明示的Outcome） |
| P8-D-WU-002（Tool Port／Registry／Descriptor） | COMPLETE | `ToolPort` Protocol、`ToolRegistry`（in-memory）、`ToolDescriptor`（`important`フラグ） |
| P8-D-WU-003（Fake／Deterministic Tool Adapter＋多段Golden Path） | COMPLETE | `FakeToolPort`（list_files/read_file/write_note）、4段Planの多段Golden Path Test |
| P8-D-WU-004（MCP Client Adapter：Port／Fixtureのみ） | COMPLETE | `McpClientPort`、`FixtureMcpClient`。**本番Registryへ非配線**（意図的） |
| P8-D-WU-005（Approval Profile＋Frozen Authorization Envelope） | COMPLETE | `ApprovalProfile`（AUTO/GATE_IMPORTANT_ONLY/GATE_ALL）、`AuthorizationEnvelope`（`ImmutableContract`＝Frozen） |
| P8-D-WU-006（important-gate-only Golden Path） | COMPLETE | Unit Test＋REST統合Testの二重確認 |
| P8-D-WU-007（Max Step／Deadline／Retry／Stop／Cancel／Late-Result） | COMPLETE | 全項目個別Unit Test（9件） |
| P8-D-WU-008（Production Wiring：REST／Bootstrap／Frontend Switch） | COMPLETE | `/api/v2/dev-agent/*`、`DevAgentPanel.tsx` |

## 実装概要

### P8-D-WU-001/002: Contracts／Ports／Registry

- `modules/dev_agent/contracts.py`：`CapabilityId`（`chat`/`dev_agent`、Constitutionの`ConstitutionView`とは別概念 — UI最上位Surfaceの選択であり、Rule/Authority評価Surfaceではない）、`RunState`/`StepState`（`LATE_REJECTED`を含む）、`RunCompletionOutcome`（`completed`/`max_steps_exceeded`/`deadline_exceeded`/`cancelled`/`approval_denied`/`tool_failure` — Constitutionの`ConstitutionDecisionOutcome`と同じ「握り潰さず全て明示」規律）、`ApprovalProfile`、`RetryPolicy`、`ToolDescriptor`（`important`）、`Plan`/`PlanStep`（Step ID重複拒否）、`StepRecord`、`RunCompletion`、`AuthorizationEnvelope`（Frozen、単一Step Scope）、`RunSnapshot`（Immutable Point-in-time Projection、`model_copy(update=...)`でのみ遷移）。
- `modules/dev_agent/ports.py`：`ToolExecutionOutcome`（`ToolExecutionSucceeded | ToolExecutionFailed`、`web_knowledge`の`FetchedContent | FetchRejected`パターンと同型）、`ToolPort`、`McpClientPort`（両方が同じOutcome型を共有）。
- `modules/dev_agent/application/tool_registry.py`：`ToolRegistry`（in-memory、`register`/`get_descriptor`/`get_port`/`list_descriptors`、重複ID拒否）。

### P8-D-WU-003/004: Tool Adapters

- `adapters/dev_agent/fake_tool_adapter.py`：`FakeToolPort`が`list_files`/`read_file`/`write_note`の3 Toolを内部Dispatchで提供。実FileSystem・実Networkには一切触れない固定Fixture。`write_note`のみ`important=True`。
- `adapters/dev_agent/mcp_fixture_adapter.py`：`FixtureMcpClient`（`McpClientPort`実装、固定Response Table）。**Bootstrap未配線** — Remote MCPはこのTaskのAuthority外であるため、Portの形と単体Testの成立のみを示す。

### P8-D-WU-005/006: Approval Gate

- `modules/dev_agent/application/run_service.py`の`_requires_approval()`：`ApprovalProfile`（AUTO/GATE_IMPORTANT_ONLY/GATE_ALL）と`ToolDescriptor.important`の組合せでStep単位のApproval要否を決定。
- `AuthorizationEnvelope`はConstructorがRun Service内の`submit_approval()`にのみ存在し、外部からCaller-supplied Inputとして受理されることは一切ない（Web層の`DevAgentApprovalRequest`は`step_id`/`decision`のみを受け取り、Envelope自体は絶対に外部Inputとして構築されない）。承認済みStepは`self._approved_steps: set[(run_id, step_id)]`で厳密にScopeされ、別Stepや別Runへの転用は構造的に不可能（Test: `test_submit_approval_rejects_wrong_step_id`）。
- important-gate-only Golden Path：`list_files`→`read_file`（非important、自動実行）→`write_note`（important、Approval待機→承認→実行）の3段Planで、Unit Test（`test_important_gate_only_golden_path_blocks_then_completes`）とREST統合Test（`test_important_gate_only_golden_path_via_rest`）の両方で成立を確認。

### P8-D-WU-007: Max Step／Deadline／Retry／Stop／Cancel／Late-Result

- Max Step：`started_count`（Attempt済みまたはPENDING以外のStep数）が`max_steps`に達した時点で`max_steps_exceeded`へ収束、未到達のStepはPENDINGのまま保持（正直な部分状態）。
- Deadline：`FakeClock`によるDeterministic Time制御Testで、`deadline_seconds`経過後の`advance()`が`deadline_exceeded`へ収束することを確認。
- Retry：`RetryPolicy.max_attempts`回まで同一StepをRetry、成功でRecover／枯渇で`tool_failure`へ収束する両方をTest。
- Cancel：実行中／未着手の全StepをCANCELLEDへ、既に成立済み（SUCCEEDED）のStepは不可侵のまま維持。
- Late-Result-rejection：`record_late_result()`はRun確定後にのみ受理可能（確定前に呼ぶとエラー）、渡された`ToolExecutionOutcome`は絶対に`StepRecord.output`へ書き込まれず、対象StepはCANCELLED→LATE_REJECTEDへ遷移するのみ（Test: `test_late_result_after_cancel_is_rejected_and_never_merged`でOutputが`None`のままであることを確認）。

### P8-D-WU-008: Production Wiring

- `web/dev_agent_contracts.py`／`web/dev_agent_routes.py`：`GET /api/v2/dev-agent/capabilities`、`GET /api/v2/dev-agent/tools`、`POST /api/v2/dev-agent/runs`、`GET /api/v2/dev-agent/runs/{run_id}`、`POST /api/v2/dev-agent/runs/{run_id}/advance`、`POST /api/v2/dev-agent/runs/{run_id}/approvals`、`POST /api/v2/dev-agent/runs/{run_id}/cancel`。未Bind時404、Run未発見404、不正Transition409 — 全て安全なJSON Errorへ収束し500は0件。
- `bootstrap/dev_agent.py`：`build_dev_agent_run_service()`がFake Tool Adapterのみを登録したRegistryでService合成。
- `entrypoints/web/main.py`：Constitutionと同じ理由（純Local・外部依存0のFoundation）で無条件Compose。
- `frontend/src/components/DevAgentPanel.tsx`：Stable Capability ID（chat/dev_agent）のSwitch（`usePreference`、`margpa.dev_agent_capability.v1`）。Dev Agent選択時は実際に`GET /api/v2/dev-agent/tools`をFetchしてTool一覧（Important flagを含む）を表示 — Switchが実際に何かを動かすことをTestで保証しているが、この画面からRunを開始するUIはまだ実装していない（Minor Finding、下記）。

## Changed Paths

Backend Source（14）：
```text
src/margpa_runtime_llm/modules/dev_agent/__init__.py
src/margpa_runtime_llm/modules/dev_agent/contracts.py
src/margpa_runtime_llm/modules/dev_agent/ports.py
src/margpa_runtime_llm/modules/dev_agent/application/__init__.py
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py
src/margpa_runtime_llm/modules/dev_agent/application/tool_registry.py
src/margpa_runtime_llm/adapters/dev_agent/__init__.py
src/margpa_runtime_llm/adapters/dev_agent/fake_tool_adapter.py
src/margpa_runtime_llm/adapters/dev_agent/mcp_fixture_adapter.py
src/margpa_runtime_llm/bootstrap/dev_agent.py
src/margpa_runtime_llm/web/dev_agent_contracts.py
src/margpa_runtime_llm/web/dev_agent_routes.py
src/margpa_runtime_llm/web/app.py（既存Fileへ追記）
src/margpa_runtime_llm/web/contracts.py（既存Fileへ追記）
src/margpa_runtime_llm/bootstrap/web_application.py（既存Fileへ追記）
src/margpa_runtime_llm/entrypoints/web/main.py（既存Fileへ追記）
```

Backend Test（6）：
```text
tests/unit/dev_agent/test_dev_agent_contracts.py
tests/unit/dev_agent/test_tool_registry.py
tests/unit/dev_agent/test_fake_tool_adapter.py
tests/unit/dev_agent/test_mcp_fixture_adapter.py
tests/unit/dev_agent/test_run_service.py
tests/integration/dev_agent/test_dev_agent_web_app.py
```

Frontend Source（5）：
```text
frontend/src/components/DevAgentPanel.tsx
frontend/src/components/SettingsModal/SettingsModal.tsx
frontend/src/api/client.ts
frontend/src/types.ts
frontend/src/i18n/translations.ts
frontend/src/styles/app.css
```

Frontend Test（1）：
```text
frontend/src/components/DevAgentPanel.test.tsx
```

Static Artifact（1）：
```text
src/margpa_runtime_llm/web/static/app.js（Build Artifact、npm run build実行済み、app.cssも再生成済み）
```

## Canonical Verification

```text
Backend: uv run pytest -q  -> 2044 passed, 7 deselected
         （内訳: P8-C完了時点2006 + Dev Agent Unit 30 + Dev Agent Integration 8 = 2044、Regression 0）
         uv run mypy src tests -> Success: no issues found in 550 source files
         uv run ruff check .   -> All checks passed
         uv run ruff format .  -> 適用済み（Diff無し確認済み）

Frontend: npx tsc --noEmit -> clean
          npm test         -> 292 passed（33 files）（P8-C完了時点288 + DevAgentPanel新規4 = 292、Regression 0）
          npm run lint     -> clean
          npm run build    -> succeeded、app.js/app.css再生成済み
```

## Internal Review（1 Cycle）

1. **Controller Issue解消**：該当なし（新規Controller Issue報告はまだない）。
2. **Authority非付与の構造保証**：`RunSnapshot.model_fields`をScanし、`authority`/`permission`/`grant_all`を含むFieldが存在しないことを検証するStructural Unit Test（`test_run_snapshot_has_no_authority_shaped_field`）で確認。`ToolDescriptor`自体もAuthority判定を持たず、実際の要否は`ApprovalProfile`との組合せでRun Service側が決定する設計（Descriptor単体が「常に信頼してよい」と主張しない）。
3. **Frozen Authorization Envelopeの単一Scope保証**：`AuthorizationEnvelope`は`ImmutableContract`（`frozen=True`/`extra="forbid"`）であり、Fieldへの再代入は`ValidationError`（Test確認済み）。Envelopeが外部からCaller-supplied Inputとして受理される経路は皆無（`DevAgentApprovalRequest`はDecisionのみを運ぶ）。
4. **Fail-closed一貫性**：未知Tool ID・Provider未Bind・Run未発見・不正Transitionの全パターンが、Backend側は同一の安全なJSON Error（404／409）、決して500にならないことを統合Testで確認。
5. **Late-Result-rejectionの正確性**：Late Resultの`output`が絶対に`StepRecord.output`へ混入しないことを、渡した具体的なDummy値（`"should_never_appear.md"`）がResponseに一切現れないことまで確認するTestで保証（曖昧な「たぶん無視される」ではなく、具体的な非混入をAssert）。
6. **Scope遵守**：Real MCP・Real Network・Real Filesystem・Remote MCP・Persistence(Restart/Reload) は一切実装していない（次PackageのP8-Eへ明示的に委譲）。Root外0、Git Mutation 0、Install 0、Provider Memory 0、Real Browser/Model 0。

Critical／Major：0件。Minor：1件（非Blocking、Stable未解決へ記録）：
- **P8-RW-D-IR-001**: `DevAgentPanel`はTool一覧の閲覧のみで、実際にRunを開始・進行・承認するInteractive UIはまだ実装していない（REST APIは完全に機能するが、そのUIはまだ無い）。P8-D自体は「Foundation」（Engine＋Production配線＋Stable Capability ID Switch）の成立が目的であり要件上の欠落ではないが、P8-E以降でRun/Step/Evidence Persistenceと統合する際に、実際にUserがRunを起動できるUIが必要になる。

## P8-ACC-026〜033 Disposition

| ID | Disposition | 根拠 |
|---|---|---|
| P8-ACC-026 | PASS | `CapabilityId`（chat/dev_agent）が安定した閉じた集合として存在し、`GET /api/v2/dev-agent/capabilities`とFrontend Switchの両方から参照可能（`DevAgentPanel.test.tsx`） |
| P8-ACC-027 | PASS | `Plan`/`PlanStep`/`RunState`/`StepState`/`RunCompletion`/`RunCompletionOutcome`が全て型付きContractとして存在し、握り潰されるOutcomeが無い（`test_dev_agent_contracts.py`） |
| P8-ACC-028 | PASS | `ToolPort`/`ToolRegistry`/`ToolDescriptor`が存在し、重複ID登録は拒否される（`test_tool_registry.py`） |
| P8-ACC-029 | PASS | `FakeToolPort`による3段Plan Golden Pathが Unit・REST統合両方で成立（`test_golden_path_multi_step_auto_profile_completes`／`test_golden_path_via_rest_completes`） |
| P8-ACC-030 | PASS | `McpClientPort`＋`FixtureMcpClient`が存在しTest済みだが本番Registryには非配線（`test_mcp_fixture_adapter.py`、`bootstrap/dev_agent.py`のコメントで明記） |
| P8-ACC-031 | PASS | `ApprovalProfile`3種＋Frozen `AuthorizationEnvelope`、important-gate-only Golden PathがUnit・REST統合両方で成立 |
| P8-ACC-032 | PASS | Max Step／Deadline／Retry（成功・枯渇双方）／Cancel／Late-Result-rejectionの個別Testが全て成立（9 Test） |
| P8-ACC-033 | PASS | REST APIがBootstrap経由で実際に配線され、未Bind・未発見・不正Transitionが全て安全に404/409へ収束（500は0件） |

**P8-ACC-026〜033 全8件PASS。P8-D成立。**

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
real_mcp_server_access: 0
provider_memory_used: false
project_root_外_access_executed: 0
```

## Exact Next Work Unit

```text
Next: P8-E Integration／Lifecycle／Evidence／Persistence
  Do Not Repeat: P8-A（WU-001〜006）、P8-B（WU-001〜004）、P8-C（WU-001〜005）、
                 P8-D（WU-001〜008）は本Recoveryで完成済み。
```
