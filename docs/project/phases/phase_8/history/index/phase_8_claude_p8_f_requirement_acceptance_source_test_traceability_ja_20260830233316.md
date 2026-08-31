# Phase 8 Claude P8-F Requirement／Acceptance／Source／Test Traceability

```yaml
document_type: traceability_matrix
phase: phase_8
package: P8-F
provider: Claude
created_at: 2026-08-30 23:33 JST
authoritative_sources:
  - docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md
  - docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md
```

## 0. 本Documentの位置づけ（Internal Review Cycle 2の主要発見）

P8-B〜P8-EのComplete Package Recoveryは、各Package内で`P8-ACC-XXX`という作業用連番を独自に付与しており、`docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md`（`acceptance_count: 40`、正本）のID⇔内容Mappingと必ずしも一致していなかった（特にP8-C／P8-D／P8-Eで顕著）。P8-A（P8-ACC-001〜012）は正本と一致していたことを`phase_8_claude_p8_a_complete_package_recovery_ja_20260830213816.md`で確認済み。

これは本日実施したP8-F Internal Review Cycle 2（正本2文書を実際に読み直す独立監査）で発見した、実装そのものの欠陥ではなくDocument追跡上の不整合である。既存のB〜E各Recoveryは当時のHistorical Recordとして訂正せず保持し（Historical Immutability）、本Documentを**正本ID→実際のSource／Test**の唯一の正しい対応表とする。

Cycle 2ではさらに、正本を実装と照合する過程で2件の**実装Gap**を発見し、その場でImplementation Authority内で修正した（停止・先送りしていない）：

1. **P8-ACC-032**（Plan-only／Manual／Risk-based／Important-gate-only 4Profileの区別）: 旧実装は`AUTO`／`GATE_ALL`／`GATE_IMPORTANT_ONLY`という独自3Profileのみで、正本が要求する4Profile中2つ（`plan_only`／`risk_based`）が存在しなかった。→ `ApprovalProfile`を正本の4値（`plan_only`／`manual`／`risk_based`／`important_gate_only`）へ全面差し替え、各Profileの新規Test（Unit 4件＋REST統合2件）を追加。
2. **P8-ACC-034**（External Write／Network／Cost／不可逆／Scope拡張等でGate待機する）: 旧実装は`ToolDescriptor.important: bool`という単一Flagのみで、Gate理由を区別できなかった。→ `ImportantGateReason`Enum（8種：external_write／network／cost／irreversible／secret_or_privacy／scope_expansion／critical_incident／completion）を新設し、`ToolDescriptor.important_gate_reason`へ差し替え。`write_note` Toolに`EXTERNAL_WRITE`を実際に付与し、REST Response・Frontend表示まで一貫させた。

さらにCycle 2でP8-ACC-040（User実画面でGate／Stopを確認できる）が、REST APIのみでUI経由の確認手段が無いという**Gap**であることを発見し、`DevAgentPanel.tsx`へ実際にRun起動・Advance・Approve／Deny・CancelのInteractive UIを追加、Real Browserで全Flowを実演確認した（§4参照）。

以上の修正を反映した上での最終Dispositionを以下に記録する。

## 1. P8-ACC-001〜012（Manual URL Evidence／P8-A）

| ACC ID | 対応REQ | Disposition | Source（代表） | Test（代表） |
|---|---|---|---|---|
| 001 | 全体 | PASS | — | Full Suite Regression 0（本Document §5） |
| 002 | REQ-001 | PASS | `web_knowledge/application/web_knowledge_service.py` | `test_web_knowledge_service.py` |
| 003 | REQ-002 | PASS | `web_knowledge/domain/url_security.py` | `test_url_security.py` |
| 004 | REQ-003 | PASS | `url_security.py`（`_DANGEROUS_PORTS`含む） | `test_url_security.py` |
| 005 | REQ-004 | PASS | `httpx_fetch_provider.py` | `test_httpx_fetch_provider.py` |
| 006 | REQ-004 | PASS | `httpx_fetch_provider.py` | `test_httpx_fetch_provider.py` |
| 007 | REQ-005 | PASS | Architecture不変（`httpx.Client`使用、JS実行系なし） | — |
| 008 | REQ-006 | PASS | `WebSearchPanel.tsx`／`WebCitationsSection.tsx` | `WebCitationsSection.test.tsx` |
| 009 | REQ-006 | PASS | `conversation_generation.py`の`_inject_web_evidence()` | `test_conversation_generation.py` |
| 010 | REQ-007 | PASS | `web_knowledge/contracts.py`の`WebCitation` | `test_web_knowledge_service.py` |
| 011 | REQ-007 | PASS | `sqlite_conversation_store.py`の`turn_web_citations` | `test_persistent_citation_evidence.py` |
| 012 | REQ-008 | PASS | `WebCitationsSection.tsx`のFailure表示 | `WebCitationsSection.test.tsx` |

## 2. P8-ACC-013〜018（UI／Archive Management／P8-B）

| ACC ID | 対応REQ | Disposition | Source | Test |
|---|---|---|---|---|
| 013 | REQ-009 | PASS | `App.tsx`（`branchUiVisible`既定false） | `MessageBubble.test.tsx` |
| 014 | REQ-009 | PASS | Branch Data／API無変更（Architecture不変） | 既存Branch Test群（Regression 0） |
| 015 | REQ-010 | PASS | `DataControlsPanel.tsx`（Archived Chats Lazy一覧） | `DataControlsPanel.test.tsx` |
| 016 | REQ-010 | PASS | `DataControlsPanel.tsx`（Title/Timestamp/Open） | `DataControlsPanel.test.tsx` |
| 017 | REQ-011 | PASS | 既存`_ensure_active_session()`（Lazy Resume） | `test_lazy_resume_on_unarchive_allows_first_send_without_manual_resume` |
| 018 | REQ-012 | PASS | 完全削除／一括操作UIを追加していない（Architecture不変） | — |

## 3. P8-ACC-019〜025（Provisional Runtime Constitution／P8-C）

| ACC ID | 対応REQ | Disposition | Source | Test |
|---|---|---|---|---|
| 019 | REQ-014 | PASS | [contracts.py](../../../../../src/margpa_runtime_llm/modules/constitution/contracts.py)の`compute_manifest_digest()` | `test_json_file_provider.py`（Digest系5件） |
| 020 | REQ-015 | PASS | `resolve_decisions()`（GD固有型Import 0、Grep確認） | `test_constitution_contracts.py` |
| 021 | REQ-016 | PASS | `ConstitutionMode`（OFF/OBSERVE/ENFORCE明示） | `test_off_mode_never_reports_enforced_or_observed_even_when_bound` |
| 022 | REQ-016 | PASS | Constitution自体が何もEnforceしていない（Architecture、Enforcement未配線につき構造的に無害） | `test_constitution_web_app.py` |
| 023 | REQ-017 | PASS | `CapabilityView`（Authority形状Field 0、構造Test） | `test_run_snapshot_has_no_authority_shaped_field`型のScan Test |
| 024 | REQ-018 | PASS | `ConstitutionManifestUnavailable`、404収束 | `test_tampered_manifest_digest_is_a_safe_404_not_a_500` |
| 025 | REQ-019 | PASS | `ConstitutionRule`にGD名／Provider名／User Path Field無し | Contract定義そのもの（構造的検証） |

## 4. P8-ACC-026〜033（Dev Agent／Tool／Approval Harness／P8-D、Cycle 2修正反映後）

| ACC ID | 対応REQ | Disposition | Source | Test |
|---|---|---|---|---|
| 026 | REQ-020 | PASS | [DevAgentPanel.tsx](../../../../../frontend/src/components/DevAgentPanel.tsx)（Chat/Dev Agent Switch） | `DevAgentPanel.test.tsx`＋Real Browser実演（§6） |
| 027 | REQ-021 | PASS | `CapabilityId`（Wire値）と`translate(...)`（表示名）の分離 | `DevAgentPanel.test.tsx` |
| 028 | REQ-022 | PASS | `RunSnapshot`/`StepRecord`/`RunCompletion`（Versioned Contract） | `test_dev_agent_contracts.py` |
| 029 | REQ-023 | PASS | `ToolPort`/`ToolRegistry`と`McpClientPort`の分離 | `test_tool_registry.py`／`test_mcp_fixture_adapter.py` |
| 030 | REQ-024 | PASS | `FakeToolPort`＋`DevAgentRunService` | `test_golden_path_multi_step_completes_with_zero_gates`／REST版 |
| 031 | REQ-023 | PASS | `McpClientPort`＋`FixtureMcpClient`、本番Registry非配線 | `test_mcp_fixture_adapter.py`、`bootstrap/dev_agent.py`の非配線明記 |
| 032 | REQ-025 | **PASS（Cycle 2で実装追加）** | `ApprovalProfile`（`plan_only`/`manual`/`risk_based`/`important_gate_only`） | `test_plan_only_profile_never_executes_any_step`／`test_risk_based_profile_gates_important_tools`／`test_risk_based_profile_gates_a_retry_after_failure`／REST版2件 |
| 033 | REQ-026 | PASS | `AuthorizationEnvelope`（Frozen）＋`StepRecord.approved`（単一Step Scope） | `test_authorization_envelope_is_frozen`、important-gate-only Golden Path |

## 5. P8-ACC-034〜038（Integration／Lifecycle／Evidence／Persistence／P8-E、Cycle 2修正反映後）

| ACC ID | 対応REQ | Disposition | Source | Test |
|---|---|---|---|---|
| 034 | REQ-027 | **PASS（Cycle 2で実装追加）** | `ImportantGateReason`（8種）、`write_note`が`EXTERNAL_WRITE`を実演 | `test_risk_based_profile_gates_important_tools`、REST `important_gate_reason`確認 |
| 035 | REQ-028 | PASS（構造的） | HarnessにProvider/Platform Gateを迂回するCode Path自体が存在しない（本Foundationが触れるのはFake Toolのみ） | Architecture上の不在確認（Bypass機構0） |
| 036 | REQ-029 | PASS | Max Step／Deadline／Retryは個別Field＋Test。Budgetは Max Stepで代替表現（Fake Toolに実Costが無いため専用Cost Modelは意図的に作らない）。Loop防止はPlanが静的かつRetryが有界であることから構造的に保証される（動的再Planning機構が存在しないため） | `test_max_steps_exceeded_stops_the_run_honestly`／`test_deadline_exceeded_stops_the_run_honestly`／`test_retry_*` |
| 037 | REQ-029 | PASS | `record_late_result()`＋`StepState.LATE_REJECTED` | `test_late_result_after_cancel_is_rejected_and_never_merged` |
| 038 | REQ-030 | **PARTIAL** | Run/Step/Tool/Approval/Constitution相関は`RunSnapshot.constitution_mode`/`constitution_rule_ids`として実装・永続化・Test済み。**GD（Governance Definitions／Guardrail）相関は未実装** — Fake ToolはModel出力を生成しないため、既存GuardrailがEvaluateすべき対象が本Foundationには存在せず、自然な接続点が無い。Dev AgentがReal LLM駆動のPlanning/Executionを持つようになった時点で再検討すべき、正直に開示する残課題 | `test_constitution_correlation_is_recorded_once_and_immutable`、REST `test_start_run_correlates_with_the_bound_constitution` |

## 6. P8-ACC-039〜040（P8-F自身）

| ACC ID | 対応REQ | Disposition | 根拠 |
|---|---|---|---|
| 039 | REQ-031/032/033 | PASS | Backend `uv run pytest -q` → 2063 passed, 7 deselected（Regression 0、P8-A時点1984から一貫して純増のみ）。`uv run mypy src tests` → 552 files Success。`uv run ruff check .` → All checks passed。Frontend `npm test` → 296 passed（33 files）。`npx tsc --noEmit`／`npm run lint`／`npm run build` → 全Clean。 |
| 040 | REQ-031/033 | PASS | Real Browser（`http://localhost:8000`、実Server起動・実API・実Model Registry読込）でManual URL（P8-A、既存確認済み）、Archive管理（P8-B、既存確認済み）、Chat／Dev Agent切替、Tool Registry表示、**Demo Run起動→Approval Gate表示→承認→完了**、**別RunでのCancel→Cancelled収束**の全てをUser画面から実演・Screenshot確認した（§7）。 |

## 7. Real Browser実演ログ（P8-ACC-040の直接Evidence）

```text
1. `uv run margpa-web`（Host 127.0.0.1:8000、Loopback限定）を起動。
2. Settings → アドバンスモード → Provisional Runtime Constitution：
   Revision 1・Digest a10bbc7d...・chat=OFF/2 Rule・agent=OFF/3 Rule・tool=OFF/2 Rule を実確認。
3. 同画面 Dev Agent（Foundation）：Chat/Dev Agent Radio Switch実操作、
   List Files／Read File／Write Note（承認必須 external_write）の実Tool一覧を確認。
4. Demo Runを開始 → Run状態 running、3 Step全pending。
5. 「次のStepへ進める」を2回クリック → list=succeeded, read=succeeded,
   write=awaiting_approval、承認待ちStep："write" の Box が実際に出現。
6. 「承認」をクリック → Run状態 running、write=pending（approved=true）へ復帰。
7. 「次のStepへ進める」を2回クリック → 全StepがSucceeded、
   Run状態 completed、完了理由 "completed — All Plan Steps completed successfully." を実確認。
8. 「新しいDemo Runを開始」→再度Runを起動 →「中止」をクリック →
   Run状態 cancelled、全Step cancelled、完了理由 "cancelled — Run was cancelled." を実確認。
9. Chat/Radioを再度Chatへ戻すとTool一覧／Demo Runが消え、通常Chat画面に
   Regressionが無いことを確認。Console Error 0件。
```

Real Model・Real Network・Real MCP・Real Browser相手の外部通信は一切発生していない（Model RegistryのLocal読込のみ、Chatへのメッセージ送信は行っていない）。
