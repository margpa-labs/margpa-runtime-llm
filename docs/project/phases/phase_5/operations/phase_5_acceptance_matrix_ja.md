# Phase 5 Acceptance Matrix

```yaml
document_id: phase_5_acceptance_matrix
status: accepted_frozen_ready_for_backup
phase: phase_5
recorded_at: 2026-08-22 09:57:48 JST
implementation_authorized: false
```

## 1. Technical Acceptance

| ID | Contract | Required Evidence |
|---|---|---|
| `P5-ACC-001` | Guardrail ResultとPhase 4 Resultが別Identity | Contract／Projection Test |
| `P5-ACC-002` | Detector→Policy→Authority→Approval→Actionが分離 | Domain／Resolver Matrix |
| `P5-ACC-003` | Unknown／Unsupported／TimeoutをSafe Allowにしない | Negative／Fault Matrix |
| `P5-ACC-004` | Guardrail OFFで既存Runtime同値／Call 0 | v1／v2／RAG／Phase 4 Spy |
| `P5-ACC-005` | OBSERVEはInput／Output／Stream／Persistence Mutation 0 | Byte／Event／Store Spy |
| `P5-ACC-006` | ENFORCEはApplicable Policy／Authority／Approval／Registry内だけ | Full Decision Matrix |
| `P5-ACC-007` | RAG／External ContextがInstruction Authorityを獲得しない | Indirect Injection Test |
| `P5-ACC-008` | Encoded／Unicode／Multilingual／Fragmented Attackを有界処理 | Adversarial Fixtures |
| `P5-ACC-009` | Stream Chunk境界のHitがClientへ漏れない | Chunk Split／Holdback Test |
| `P5-ACC-010` | Reject／Cancel／FailureでGhost Completion／未承認Commit 0 | SSE／Store／Receipt Test |
| `P5-ACC-011` | Typed Redaction以外の捛造書替え0 | Span／Overlap／Integrity Test |
| `P5-ACC-012` | Secret／PII実値がEvidence／Status／Raw Errorへ0 | Projection／Log Security Test |
| `P5-ACC-013` | Model／Definition／DetectorがAuthority／Approvalを生成しない | Provider／Schema Negative Test |
| `P5-ACC-014` | Stale Policy／Authority／Approval／Registryを再利用しない | Revision／Cache Matrix |
| `P5-ACC-015` | Main Governance AllowでSafety Denyが解除されない | Conflict Matrix |
| `P5-ACC-016` | Safety Model 0件／UnavailableでDeterministic Baseline成立 | No-provider Integration |
| `P5-ACC-017` | Unknown Model Label／Low ConfidenceをPassにしない | Fake Adapter Matrix |
| `P5-ACC-018` | Public／BasicでPrivate Control／Evidence非露出 | Route／DOM／Call Spy |
| `P5-ACC-019` | Phase 3／4 ModeとGuardrail Modeが独立 | Configuration CAS Matrix |
| `P5-ACC-020` | Mode再OpenでServer Current Stateを表示 | Component／Browser Test |
| `P5-ACC-021` | Persistent／RAG／Retry／Regenerate／Branch／Resume回帰 | Web Integration |
| `P5-ACC-022` | Concurrent Turn／TabのScanner／Result混同0 | Concurrency Test |
| `P5-ACC-023` | Repair／Regenerate／Phase 6 Judge追加Call 0 | Call Spy |
| `P5-ACC-024` | AWS／Lightning／Safety Model LoadがCompletion Dependencyでない | Bootstrap／Config Test |

## 2. Mode Matrix

| Guard Source | Policy／Authority | Mode | Expected |
|---|---|---|---|
| none | none | off | Existing Runtime／Guard Call 0 |
| none | none | observe | inactive／Output unchanged |
| none | none | enforce | unavailable／mutation 0／no silent observe |
| valid | valid | off | Existing Runtime／Detector／Action Call 0 |
| valid | valid | observe | Detection／Evidence only／Output unchanged |
| valid | valid | enforce | Registered／Authorized Exact Action |
| valid | missing approval | enforce | pending／action 0 |
| valid | stale authority | enforce | fail-closed／action 0 |
| invalid | any | observe | isolated degraded／Runtime unchanged |
| invalid | any | enforce | unavailable／no allow fabrication |

## 3. Point／Action Matrix

| Point | Observe | Enforce |
|---|---|---|
| input | detection only | warn／reject／stop if authorized |
| context_source | source-risk evidence | exclude／reject only if explicit policy／authority |
| stream_candidate | no output mutation | safe-prefix／suppress／typed terminal |
| output_candidate | result only | reject or verified typed redaction |

| Action | Initial Phase 5 | Rule |
|---|---|---|
| allow | executable | no mutation |
| warn | candidate | safe metadata only |
| reject_input／stop_before_generation | candidate | Model Call 0／typed terminal |
| suppress_stream_candidate | candidate | matched content release 0 |
| reject_output | candidate | no replacement fabrication |
| redact_typed_secret／pii | candidate | validated span／policy／authority only |
| require_approval | status only | AI approval issuance 0 |
| repair／regenerate | not executable | Phase 6 |
| tool／external action | prohibited | capability absent／user authority required |

## 4. Adversarial Security

- Direct／Indirect Prompt Injection、Jailbreak、RAG Source内Instruction。
- Unicode Confusable／Invisible／Normalization／Base64等Encoded Candidate／Fragmented Multi-turn／Chunk Split。
- Synthetic Secret／PII Fixtureと実値非露出。実User Dataは使わない。
- Tool／Agent／System／Authority／Approval Spoofing。
- Detector False Positive／False Negative、Model False Allow／False Deny、Unknown Label。
- Stale Policy／Authority／Approval／Cache、Double Execute／Partial Action／Timeout／Crash／Race。
- Stream／Terminal／Commit／SSE／Citation／Retry／Branchの順序。

## 5. Privacy／Evidence

- Raw Content、Secret／PII実値／Hash／Prefix／Suffix、System Prompt、Thinking、Absolute Path、Raw Exceptionの通常Evidence 0。
- Count／Category ID／Severity／Digest／Action State／Safe Reasonのみ。
- Observer FailureとStore Failureを分離し、FailureをEvidence Successにしない。
- False Positive／NegativeはGround Truthがない場合`unavailable`とし、0で捛造しない。

## 6. Performance／Automation

- Mode別Detector／Safety Model／Policy／Authority／Action Call、Latency、Buffer Byte、Evidence Byte。
- OFF追加Call 0、OBSERVE Output Mutation 0、Production Safety Model Call 0、Repair Call 0。
- Human Clarification／Intervention、False Completion、Self-detected／Codex-detected Finding、Compaction／Quota Recoveryを分離記録する。
- Root／Git／Stable／User Data／Provider Memory違反目標0。

## 7. Closure

Technical／Security Matrix PASS、Open Major Finding 0、Codex Independent Review、User Mac AcceptanceおよびMinimal Closureが成立した場合だけPhase 5をAcceptedとする。
