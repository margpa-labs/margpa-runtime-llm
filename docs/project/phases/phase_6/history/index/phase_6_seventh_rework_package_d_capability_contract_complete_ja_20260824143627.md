# Phase 6 Seventh Rework — Package D Capability Contract完了Recovery Entry

```yaml
document_id: phase_6_seventh_rework_package_d_capability_contract_complete_20260824143627
status: recovery_entry_complete
phase: phase_6
rework: seventh_rework_user_ui_runtime_model_semantic_enforcement
package: package_d
owner_role: 設計者兼実装者役
created_at: 2026-08-24 14:36:27 JST
authority: phase_6_codex_controller_seventh_rework_package_d_resume_authority_ja_20260824143226.md
previous_entry: phase_6_seventh_rework_package_d_root_outside_npm_log_attempt_stopped_safe_ja_20260824143020.md
next_package: package_e
```

## Completed

- `Context Size (Current / Native)`を廃止し、Model Native／Backend／Deployment-Hardware Verified／Effective Maximumを独立したTyped Capabilityとして投影した。
- Local ProfileのDeployment-Hardware Verified 8192をQwen Native 32768／DeepSeek Native 131072と分離し、Context Inputの`max`は実行可能性を保証できるEffective Maximumのみに固定した。
- Current AllocationをBackend MaximumやDeployment Verificationに昇格しない。これによりContext縮小後もVerified Maximumへ再拡張可能にした。
- ContextはMinimum 512／Effective Maximum／Maximum-1／範囲外をUnload前に検証し、Typed Reasonと共に拒否する。Target Model Switchにも同一Preflightを適用した。
- Max New TokensのConfigured Default 2048と、Model／Deployment／Current Loaded Contextから決まるUpper Limitを分離した。Context 8192でのRuntime Upper Limitは8191。
- Model Switch先でCurrent Max New TokensがUpper Limitを超える場合は、可能な限りDefault 2048へ収束し、それも不可能な場合はTarget Upper Limitへ収束する。
- Turn RequestがFrozen Runtime Limitを超える場合のSilent Clampを廃止し、Typed Rejectionに変更した。ProductionのExact Chat Prompt Token Counterで`prompt + requested output <= effective context`を検証する。
- UIはLimit／CAS Conflict／BusyをTyped Resultとして表示し、Failure後はInput／SelectorをCanonical SnapshotへRollbackしてからRefreshする。
- Ephemeral／Persistentの両Requestは、固定2048ではなくCurrent Runtime Snapshotの`current_max_new_tokens`をClient-side Upper Limitに使う。

## Verification

```text
Backend Package D Focused : 63 tests PASS／Exit 0
Targeted Mypy             : 14 source files／0 issues／Exit 0
Targeted Ruff Check       : PASS／Exit 0
Frontend Typecheck        : PASS／Exit 0
Frontend Full Test        : 24 files／220 tests PASS／Exit 0
Frontend Lint             : PASS／Exit 0
```

Boundary TestはContext Maximum／Maximum-1／Minimum／範囲外、Max New Tokens Maximum／Minimum／範囲外、
Busy／CAS Conflict／Load Failure／Rollback／Target Switch Default収束／Bootstrap Default／Exact Remaining
Contextを含む。Qwen／DeepSeek実ArtifactのLoad／Metal実測はPackage Fで別途実施する。

## Acceptance Delta

```text
P6-RW7-MDL-002 : IMPLEMENTED_AND_DETERMINISTIC_TEST_PASS（Real Model confirmation pending Package F）
P6-RW7-MDL-003 : PASS for deterministic Controller/API boundaries
P6-RW7-MDL-004 : PASS for Default/Upper/Remaining-Context/Switch Contract
P6-RW7-REG-003 : Package D focused validation PASS; integrated validation pending Package G
```

## Incident／Action Inventory

```text
Seventh Rework cumulative Root-outside Attempt : 1（P6-RW7-INC-001）
Resume Cycle Root-outside Action               : 0（本Resume実行Log）
Persistent Root-outside Artifact               : Tool出力上0／外部Inspection未実施
P6-RW7-REG-004                                 : HISTORICAL_NONCONFORMANCE_RECORDED
Provider Memory Internal Contact               : 0（本Resume実行Log）
User runtime_data Contact                      : 0（本Resume実行Log）
Git Action                                     : 0（本Resume実行Log）
Network Action                                 : 0（本Resume実行Log）
Model Artifact Mutation                        : 0（本Resume実行Log）
```

Frontend CommandはExact `frontend/` WorkdirとAuthority指定のProject内NPM Cache／TMPDIRを使用した。

## Exact Next Action

Package EでJudge Prompt／Output Decoder／Evaluation Orchestrator／Repair Router／Presented Final境界を修正し、
Semantic ENFORCEのKnown Failed CandidateがFinalへ通過しないBounded Contractを実装する。
