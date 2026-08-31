# Phase 8 Execution Plan — Bounded Research Foundation

```yaml
document_id: phase_8_execution_plan
document_state: complete_accepted_closed
phase: phase_8
language: ja
created_at: 2026-08-30 19:18:06 JST
executor_candidate: Claude_or_Copilot_or_Codex_sequential
reviewer: Codex project responsible and design governor role
```

## 1. Execution Policy

- Phase 7成立範囲を再実装しない。
- Phase 6／9 Semantic DebtをPhase 8へ混入させない。
- Packageを連結実行し、Routine報告だけで停止しない。
- Package BoundaryでRecovery Indexを残す。
- 実装中、Controllerは完全待機を基本とし、Return後にBounded Independent Reviewする。
- Critical／Major／MVP Blockerだけを即Reworkし、P2以下はStable未解決Registryへ送る。
- Real Network／MCP／External Side Effectは明示Authorityなしに実行しない。
- 最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL`。

## 2. Packages／Work Units

### P8-0 Entry／As-built／Authority Freeze

- P8-0-WU-001: Phase 7 Local RAG／Web Port／Data Controls／PersistenceのAs-built Map。
- P8-0-WU-002: Phase 2 Branch／Archive／ResumeとPhase 3〜5 Governance Portの再利用境界。
- P8-0-WU-003: Authority、Network、Temp、Model、Git、User runtime_data、Test Matrixの固定。

### P8-A Manual URL Fetch／Evidence

- P8-A-WU-001: Manual URL Request／Status／Evidence Contract。
- P8-A-WU-002: Public `http／https` URL ValidationとSSRF／Redirect Revalidation。
- P8-A-WU-003: Bounded Fetch、Size／Timeout／Content Type、Text Normalizer。
- P8-A-WU-004: Untrusted EvidenceをMain Model Contextへ明示接続。
- P8-A-WU-005: URL／Fetched At／Digest／Source Class CitationとPersistence。
- P8-A-WU-006: Settings Toggle／Consent／Failure Presentation／Fixture Test。

### P8-B Entry UI Simplification／Archive Management

- P8-B-WU-001: Branch UIをFeature Flag／Presentation Boundaryで既定非表示。
- P8-B-WU-002: Archive Lazy List API／Projection。
- P8-B-WU-003: Data Controls一覧、Title／Timestamp、Open、Unarchive。
- P8-B-WU-004: Unarchive後Immediate Send、Restart／Two-tab Regression。

### P8-C Provisional Runtime Constitution

- P8-C-WU-001: `constitution/` Directory／Manifest／Rule／View Schema。
- P8-C-WU-002: Provider Port、Revision／Digest Validation、Capability View。
- P8-C-WU-003: OFF／OBSERVE／ENFORCEとTyped Decision Envelope。
- P8-C-WU-004: Generic Resolver／Conflict／Unsupported／Authority非生成境界。
- P8-C-WU-005: 通常Chat／Agent／Tool HookのFixture／Evidence。

### P8-D Dev Agent／Tool／Approval Harness Foundation

- P8-D-WU-001: Stable Capability IDとChat／Dev Agent UI切替。
- P8-D-WU-002: Run／Step／State／Plan／Completion Contract。
- P8-D-WU-003: Tool Port／Registry／Descriptor／Capability Metadata。
- P8-D-WU-004: Fake／Deterministic Tool Adapterと複数Step Golden Path。
- P8-D-WU-005: MCP Client Adapter Port／Fixture。Generic Remote接続はしない。
- P8-D-WU-006: Approval ProfilesとFrozen Authorization Envelope。
- P8-D-WU-007: Important-gate-only Golden Path／Gate Wait／Resume。
- P8-D-WU-008: Max Step／Deadline／Retry／Stop／Cancel／Late Result拒否。

### P8-E Integration／Lifecycle／Evidence／Persistence

- P8-E-WU-001: Constitution／GD／Policy／Approval／Tool Decision相関。
- P8-E-WU-002: Run／Step／Request Evidence PersistenceとCurrent／Historical Projection。
- P8-E-WU-003: Restart／Reload／Two-tab／Shutdown Recovery。
- P8-E-WU-004: Normal Chat／Local RAG／Citation／Data Controls Regression。
- P8-E-WU-005: Failure Language／Provider／Stage／Reasonの正直な表示。

### P8-F Review／Verification／User Manual Candidate

- P8-F-WU-001: Requirement／Acceptance／Source／Test Traceability。
- P8-F-WU-002: Internal Review Cycle 1、必要なP0／P1 Rework、Cycle 2。
- P8-F-WU-003: Canonical Backend／Static／Frontend Verification。
- P8-F-WU-004: User Manual Sheet、Exact Return Handoff、Complete Candidate。

## 3. Acceptance停止線

Package完成数やTest総数だけで完成を主張しない。Manual URLの実NetworkはUser Authorityがない場合Fixture／NOT RUNへ分離できるが、URL Fetchを完成Claimするには最終的にUser Mac Manual Gateを必要とする。Dev Agentは限定ToolのResearch Previewとして評価し、実案件完成を要求しない。

## 4. Recovery Index

各Package Recoveryへ次を記録する。

```text
Completed Work Units
Changed Paths
Focused Verification
Open Findings／Deferrals
Network／Git／User Data／Model／External Action Inventory
Active Process／Loaded Resource
Next Exact Work Unit
```

## 5. Controller Review上限

```text
Independent Review 1回
Critical／Major／MVP BlockerのBounded Rework 1回
Targeted Re-review 1回
User Manual
```

新しいEnterprise HardeningやPhase 10／11機能をReview Loopへ追加しない。
