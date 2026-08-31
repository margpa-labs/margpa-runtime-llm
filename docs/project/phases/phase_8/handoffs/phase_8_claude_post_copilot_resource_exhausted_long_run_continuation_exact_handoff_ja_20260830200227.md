# Phase 8 Claude Post-Copilot Resource-exhausted Long-run Continuation Exact Handoff

```yaml
document_id: phase_8_claude_post_copilot_resource_exhausted_long_run_continuation_exact_handoff_20260830200227
document_type: exact_continuation_handoff
document_state: frozen_ready_not_started
language: ja
created_at: 2026-08-30 20:02:27 JST
phase: phase_8
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_continuity: continued_not_fresh
start_boundary: CP8-04
implementation_authority: true_after_exact_user_start
network_authority: false
git_authority: false
backup_authority: false
phase_8_closure_authority: false
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
```

## 1. Objective

CopilotがResource Exhaustedで停止したPhase 8 Current Working TreeをRollbackせず、`CP8-04`のPartial Direct URL実装を修復・監査し、P8-Aを完成させた後、P8-B〜P8-Fを連結Long-run実行する。

## 2. Continuity／Priority

このClaude TaskはFresh Taskではない。Phase 7を担当したCurrent Claude設計者兼実装者役Taskを継続使用する。Role Bootstrap、旧Authority全消去または三段階Receiptをやり直さない。

```text
Userの最新明示指示
→ 本Exact Continuation Handoff
→ Controller Recovery 20260830200227
→ Phase 8 Base Exact Handoff
→ Phase 8 Requirements／Architecture／Execution／Acceptance
→ 比例的Autonomy Addendum
→ Claude Long-running／Internal Review Rule
```

Current Working Treeは、Copilotによる正当な途中Mutationを含むCanonical Baselineである。Claudeの過去ContextへRollbackしない。

## 3. Minimum Mandatory Reading

1. `docs/project/phases/phase_8/handoffs/phase_8_claude_post_copilot_resource_exhausted_long_run_continuation_exact_handoff_ja_20260830200227.md`
2. `docs/project/phases/phase_8/history/index/phase_8_copilot_resource_exhausted_controller_recovery_ja_20260830200227.md`
3. `docs/project/phases/phase_8/handoffs/phase_8_implementation_exact_handoff_ja_20260830191806.md`
4. `docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md`
5. `docs/project/phases/phase_8/architecture/phase_8_architecture_ja.md`
6. `docs/project/phases/phase_8/operations/phase_8_execution_plan_ja.md`
7. `docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md`
8. `docs/project/phases/phase_8/history/index/phase_8_copilot_p8_0_wu_003_recovery_index_ja_20260830.md`
9. `docs/project/shared/task_roles/codex_controller_and_delegated_agent_proportional_autonomy_append_only_correction_addendum_ja_20260828223445.md`

上記の後、Recoveryに列挙した6 Changed Filesと隣接Production Composition／Testsを直接読む。Phase 3〜7全Historyまたは旧Handoffを機械的に全走査しない。

## 4. Preserved／Partial State

### Preserved COMPLETE

- CP8-01〜03／P8-0-WU-001〜003。
- Phase 7 Closure Baseline。
- Entry Focused Backend 64 passed／Frontend 6 passed。
- Root／Network／Git／User Data Action 0。

### Current PARTIAL

- CP8-04／P8-A-WU-001／002。
- Direct URL Contract、Route、Service、Testの途中差分。
- `web_knowledge_service.py:223`で`IndentationError`。

CP8-01〜03を再実行しない。CP8-04 RecoveryはSyntaxとFocused Testが成立するまで作成済み扱いにしない。

## 5. First Exact Action

1. Current DiffをRollbackせず読み取る。
2. `search_and_fetch()`を元の完全なMethod Boundaryへ復元する。
3. `fetch_direct_url()`を独立Methodとして正しく配置する。
4. `py_compile`と最小Unit Test Collectionを通す。
5. Controller Recovery §6の7観点をAuditし、必要な設計補正を行う。

単なるIndent修正だけでP8-AをPASSにしない。

## 6. P8-A Required Completion

- Direct URL用Production Fetchは既存Search Fixtureと分離し、`HttpxWebFetchProvider`を実配線する。
- Real Networkは実行しない。Mock Transport／FixtureでContractを検証し、User Manualへ残す。
- Public `http／https`、Credential、Private／Loopback／Link-local／Metadata／危険Port、Redirect再検証。
- Timeout、Size、Content Type、Text Normalization、JavaScript／Cookie／Login／Form／Download 0。
- Current TurnだけへのUntrusted Evidence注入。OFF／Failure時注入0。
- CitationにCanonical URL、Fetched At、Content Type、Digest、Source Class。
- Live／Persistent／ReloadでIdentity保持、Historical Turn不変。
- 設定のOFF／ON、Manual URL入力、Content表示、Untrusted Label、原因別Failure。
- Existing Search Fixture、Local RAG、Citation、Conversation、Data Controls Regression 0。

## 7. Remaining Long-run Scope

P8-A成立後、Base Execution Planに従い次を連結する。

```text
P8-B Entry UI Simplification／Archive Management
P8-C Provisional Runtime Constitution
P8-D Dev Agent／Tool／Approval Harness Foundation
P8-E Integration／Lifecycle／Evidence／Persistence
P8-F Review／Verification／User Manual Candidate
```

General Web Search、Automatic Search、Full Constitution、正式Agent Level 1、Remote MCPまたはPhase 6／9 Semantic Debtを混入させない。

## 8. Recovery／Long-run

- P8-A、P8-B、P8-C、P8-D、P8-E、P8-FのPackage BoundaryでRecovery Indexを作る。
- ClaudeのCompaction／Resource Stopが近い場合、Package途中でもExact WU Recoveryを作る。
- Progress Report後もTrue Stopがなければ自走する。
- Routine Confirmation、Minor FindingまたはReal Network未許可だけで全体停止しない。
- Current Sourceを別Providerによる競合と誤認しない。

## 9. Authority

### Allowed

- Project Root内のPhase 8 Source／Test／Frontend／Config／Static Artifact。
- Phase 8 Recovery、Implementation Freeze、Finding Ledger、Return Handoff。
- 既存`.venv`と既存`frontend/node_modules`を使うTest／Static／Build。

### Forbidden

- Project Root外Action、Git、Network、Install／Download、Provider Memory、User `runtime_data/`、Real Browser、Model Load。
- Phase 8 Closure、Phase 9、Roadmap、Backup、Commit／Push。
- General Web Search、Credential／Account、Remote MCP、External Side Effect。

Node v25のFrontend環境差が出ても、Node／nvmを新規Installしない。環境Failureを正確に分離して独立Scopeを継続する。

## 10. Review／Stop Line

Internal ReviewはFrozen ScopeのProduction Wiring、Failure、Persistence、UIおよびAcceptanceを確認する。Critical／Major／MVP BlockerはReworkし、Minor／Hardening／将来改善は未解決へ送る。

Enterprise Hardening、未解決0件または一発完全合格を目的にしない。User Manualへ渡せるPoC／MVP停止線でCandidate Returnする。

## 11. Return

Exact Return Handoffへ次を含める。

- P8-ACC-001〜040の個別DispositionとEvidence Pointer。
- Copilot PartialのDisposition。
- Package／WU Completion、Changed Paths、Canonical Verification。
- Internal Review／Rework、Open Finding、PARTIAL／NOT RUN／USER GATE。
- Root／Git／Network／Provider Memory／User Data／Model Action Inventory。
- Active Process／Temporary Artifact／Compaction／Resource Recovery。
- User Manual Test Sheet。

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL`。Return後はCodex Controller Independent Review待ちで停止する。

## 12. Exact Start

```text
Phase 8 Post-Copilot Long-run ContinuationをCP8-04から開始する。
```
