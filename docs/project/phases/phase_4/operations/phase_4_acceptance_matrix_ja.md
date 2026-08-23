# Phase 4 Acceptance Matrix

```yaml
document_id: phase_4_acceptance_matrix
status: accepted_frozen_ready_for_backup
phase: phase_4
recorded_at: 2026-08-21 22:04:22 JST
implementation_authorized: false
frozen_at: 2026-08-21 23:20:56 JST
```

## 1. Technical Acceptance

| ID | Contract | Required Evidence |
|---|---|---|
| `P4-ACC-001` | Definition 0件＋OFFで既存Runtime同値 | v1／v2／Persistent／RAG Regression |
| `P4-ACC-002` | PlanとBindingが別Immutable Artifact | Domain／Digest Test |
| `P4-ACC-003` | Binding Keyが全Integrity Inputを含む | Stale Cache／Digest Matrix |
| `P4-ACC-004` | Unknown／Conflict／Authority不足はExecutableでない | Negative Matrix |
| `P4-ACC-005` | Standard ResultのFact／Evaluation／Action分離 | Contract Test |
| `P4-ACC-006` | ObserveはModel Input／Output Mutation 0 | Byte／Semantic／Spy Regression |
| `P4-ACC-007` | EnforceはRegistered Actionだけ | Registry／Authority／Mode Matrix |
| `P4-ACC-008` | Silent Downgrade 0 | Mode Transition Test |
| `P4-ACC-009` | Repair／Regenerate自動Call 0 | Call Spy |
| `P4-ACC-010` | ARGD／DAGD不在でもRuntime正常 | Empty Provider Integration |
| `P4-ACC-011` | Typed AdapterがSource不在Semanticsを補完しない | Loss／Ambiguity Fixtures |
| `P4-ACC-012` | EvidenceがRecommendation／Executionを分離 | Event Contract／Restart Test |
| `P4-ACC-013` | StatusにPath／Secret／本文／Raw Error 0 | Projection Security Test |
| `P4-ACC-014` | Public／Basic Private Governance Call 0 | App Build／Route／Spy Test |
| `P4-ACC-015` | Cancel／Terminal／Retry／Branch互換 | Web Integration |
| `P4-ACC-016` | Concurrent InvocationのCross-turn混同0 | Concurrency Test |
| `P4-ACC-017` | Qwen Current Routeが三Modeで動作 | Local Browser／Runtime Test |
| `P4-ACC-018` | DeepSeek／AWSがCompletion Dependencyでない | Config／Bootstrap Test |
| `P4-ACC-019` | post判定→Atomic Commit→completedの順序を維持 | Fault Injection／SSE／Persistence Test |
| `P4-ACC-020` | Reject／Stop／失敗時にGhost Completionと未承認Content永続化0 | Store／Receipt／Terminal Spy Test |

## 2. Mode Matrix

| Definitions | Binding | Mode | Expected |
|---|---|---|---|
| 0 | none | off | Existing Runtime、Governance Call 0 |
| 0 | none | observe | inactive_no_definitions、Output unchanged |
| 0 | none | enforce | unsupported／mutation 0 |
| valid | valid | off | Existing Runtime、Point／Action Call 0 |
| valid | valid | observe | Result／Evidence only、Output unchanged |
| valid | valid | enforce | Registered／Authorized Action only |
| valid | stale | observe | Rebind or explicit unavailable、stale reuse 0 |
| valid | stale | enforce | fail-closed、action 0 |
| invalid | none | observe | isolated invalid、Main Runtime pass |
| invalid | none | enforce | unavailable、no silent observe |

## 3. Action Matrix

| Action | Phase 4 | Rule |
|---|---|---|
| pass | executable | no mutation |
| recommend_only | executable | evidence only |
| warn | candidate | safe projection only |
| stop_before_generation | candidate | explicit terminal、Model Call 0 |
| reject_output | candidate | no replacement content fabrication |
| constrain_generation_config | candidate | allowlist＋existing validation |
| repair／regenerate | not executable | Phase 6 recommendation only |
| redact secret／PII | not executable | Phase 5 responsibility |
| tool／external action | prohibited | Authority not present |

## 4. Security／Failure

- Definition／Manifest／Binding／CacheのPath、Digest、Size、Schema、SymlinkおよびRace境界。
- Unknown／Malformed／Unsupported／Ambiguous／Quarantinedの分離。
- Action Adapter allowlist、Double Execute、Partial Failure、Timeout、Conflict。
- Evidence Write Failure、Status Subscriber FailureおよびRaw Error Redaction。
- Model Busy、Cancel、Client Disconnect、Persistence Conflict、Server Restart。
- Collection／String／Rule／Result／Event／Cache／Budget上限。

## 5. Performance／Cost

各Modeで次を計測する。

- Main Model Call Count／Token。
- Governance Deterministic Call Count。
- Additional Semantic Model Call Count（Phase 4は0）。
- Point／Binding／Evaluation／Action／Evidence Latency。
- Cache Hit／Miss。
- Result／Evidence Byte Size。

OFF追加Call 0、Observe追加Model Call 0、Repair Call 0を必須とする。

## 6. Automation／Recovery

- Human Clarification、Intervention、False Completion、Claude Self-detected／Codex-detected Findingを分離記録。
- Auto-compaction CycleはBefore／After Hash、Semantic RecoveryおよびLanguage Fidelityを別軸にする。
- Root／Git／Stable／User Data／Provider Memory違反目標0。
- Phase 4-G後にPhase 5へ自動移行しない。

## 7. Closure

Technical Matrix PASS、Open Major Finding 0、Codex Independent Review、User Mac AcceptanceおよびMinimal Closureが成立した場合だけPhase 4をAcceptedとする。
