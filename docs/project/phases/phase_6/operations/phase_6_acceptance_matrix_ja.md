# Phase 6 Acceptance Matrix

    document_id: phase_6_acceptance_matrix
    status: accepted_frozen_not_activated
    phase: phase_6
    recorded_at: 2026-08-22 21:13:08 JST
    implementation_authorized: false

## 1. Model／Runtime Control

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-001 | Startup Default Qwen | Startup／Runtime Snapshot |
| P6-ACC-002 | DeepSeek Canonical／Derived Provenance | Manifest／Digest／Recipe |
| P6-ACC-003 | V4 Flash Local Call 0 | Config／Backend Spy |
| P6-ACC-004 | Qwen→DeepSeek→Qwen、Server再起動0 | Real Local Round-trip |
| P6-ACC-005 | Active Generation中Switch拒否 | Concurrency Test |
| P6-ACC-006 | Load失敗Rollback／二重失敗Fail-closed | Fault Injection |
| P6-ACC-007 | Switch後もConversation／Citation／Branch維持 | Web Integration |
| P6-ACC-008 | TurnへExact Model／Artifact／Backend／Config | Persistence Projection |
| P6-ACC-009 | Context Size Dynamic Limit／Internal Reload | Capability／Reload Test |
| P6-ACC-010 | Context変更失敗でRequestedをCurrent化0 | Rollback／UI Test |
| P6-ACC-011 | Max New Tokens変更はReload 0／次Generation反映 | Generation Spy |
| P6-ACC-012 | Prompt込み上限超過をSilent Clamp 0 | Token Boundary Test |
| P6-ACC-012A | models SymlinkのLogical／Resolved ScopeとCurrent Authorization一致 | Path／Receipt Test |
| P6-ACC-012B | Symlink TargetのSibling Model／未指定Subtree Mutation 0 | Inventory／Containment Test |

## 2. Evaluation／Judge

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-013 | Dataset／Case／Criteria／Ground Truth／Run／Result分離 | Domain Contract |
| P6-ACC-014 | Ground Truth Revision／Digest／Source追跡 | Manifest Test |
| P6-ACC-015 | Deterministic JudgeはModel 0件で成立 | No-provider Test |
| P6-ACC-016 | Judge OFFで追加Call／Mutation 0 | Call Spy |
| P6-ACC-017 | Judge OBSERVEでCanonical Answer不変 | Byte／SSE／Store Spy |
| P6-ACC-018 | Judge ENFORCEがAuthorityを直接生成0 | Resolver Matrix |
| P6-ACC-019 | LLM Judge Typed Decode／Unknown Fail-closed | Malformed／Timeout Matrix |
| P6-ACC-020 | Same Artifact JudgeをIndependentと表示0 | Role Identity Test |
| P6-ACC-021 | Prompt／Rubric／Model／Seed／Config Digest追跡 | Run Evidence |
| P6-ACC-022 | Position／Verbosity／Language／Self Bias比較 | Calibration Matrix |
| P6-ACC-023 | 少なくとも一つの実Local LLM Judge Run | Real Model Evidence |
| P6-ACC-024 | Judge ResultでSafety／Authority Deny解除0 | Cross-phase Conflict |
| P6-ACC-024A | Selene候補未Load時にCurrent／Available捏造0 | Registry／Projection Test |

## 3. Repair

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-025 | Judge ModeとRepair Mode独立／Default OFF | Configuration Matrix |
| P6-ACC-026 | Repair OBSERVEで追加Generation 0 | Model Call Spy |
| P6-ACC-027 | Repair ENFORCEはRegistry／Authority／Budget内だけ | Resolver Matrix |
| P6-ACC-028 | OriginalとRepair Attemptを別Identity | Domain／Persistence Test |
| P6-ACC-029 | Repair CandidateがPhase 4／5全Point再通過 | Hook Spy |
| P6-ACC-030 | Max Attempt／Time／Token／Call／Depth有界 | Exhaustion Matrix |
| P6-ACC-031 | Before／Afterを同Criteriaで再評価 | Comparison Test |
| P6-ACC-032 | Worse／Unknown／FailureをSuccess化0 | Negative Matrix |
| P6-ACC-033 | Ghost Completion／Double Terminal／Uncommitted Completed 0 | SSE／Store Test |
| P6-ACC-034 | Hidden Original通常保存0 | Storage Security Test |

## 4. Observability／Presentation

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-035 | Request／Turn／Generation／Judge／Repair相関 | Event／API Test |
| P6-ACC-036 | Current Requestへ過去Point結果混在0 | Sequential Request Test |
| P6-ACC-037 | 未実行PointをTyped not-invoked表示 | Reject-before-model Test |
| P6-ACC-038 | State遷移とTerminal一意 | State／Concurrency Matrix |
| P6-ACC-039 | Subscriber Failureで成功捏造0 | Fault Injection |
| P6-ACC-040 | Guardrail RejectでModel Call 0 | Inference Spy |
| P6-ACC-041 | Raw Error CodeでなくJA／EN Safe Refusal | Frontend／Browser Test |
| P6-ACC-042 | Safe RefusalをAssistant Authority／次Context化0 | Projection Test |
| P6-ACC-043 | Reload／Resumeで安全表示再構築 | Persistent Browser Test |

## 5. Feedback／Recording

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-044 | FeedbackとPolicy／Authority／Training分離 | Domain／Call Spy |
| P6-ACC-044A | RatingだけでRetry／Regenerate／Repair自動実行0 | Action Spy |
| P6-ACC-045 | Recording OFFでBuild／Call／Write 0 | Filesystem Spy |
| P6-ACC-046 | METADATAがAllowlist Fieldだけを保存 | Schema／Storage Test |
| P6-ACC-047 | FULLがCanonical Input／Presented Answerだけを許可 | Positive／Negative Matrix |
| P6-ACC-048 | Thinking／System／Secret／Tool／RAG Internal／Hidden／Partial保存0 | Security Scan |
| P6-ACC-049 | Atomic Write／Quota／Failure／Degraded | Fault／Recovery Test |
| P6-ACC-050 | TestがUser実runtime_dataへRead／Write 0 | Path／Inventory Evidence |
| P6-ACC-051 | Private Evaluation／FeedbackがGit Stage対象外 | Gitignore／git check-ignore／ls-files |

## 6. UI／Identity

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-052 | Sidebar Current Main Modelが実Runtime一致 | API／Browser |
| P6-ACC-053 | Main／Guard／Judge／Governance Layerを別Row表示 | Component Test |
| P6-ACC-054 | Guard Model NoneとGuardrail Modeを混同0 | State Matrix |
| P6-ACC-055 | Governance LayerはManifest／Digest／Bindingから導出 | Valid／Invalid Matrix |
| P6-ACC-056 | None／Unavailable／Invalid／Loading／Degraded／Active区別 | Projection Matrix |
| P6-ACC-057 | Context／Max Tokens Current／Limit／Source表示 | API／Browser |
| P6-ACC-058 | Settings再Open／Reload／別Tab同期 | Real Browser |
| P6-ACC-059 | Main Runtime Governance／Guardrail GovernanceからPhase Suffix除去 | DOM／Translation Test |
| P6-ACC-060 | 将来の利用者向けLabelへPhase Suffix 0 | String／Review |
| P6-ACC-061 | Phase 3 Panel整理、内部Definition基盤回帰0 | UI／Backend Regression |
| P6-ACC-062 | Current Constitution LayerをPhase 6で捏造0 | DOM／API Call Spy |
| P6-ACC-063 | Path／Secret／Raw Definition／Prompt露出0 | Projection Security |

## 7. Compatibility／Experiment

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-064 | v1／v2／Persistent／Ephemeral回帰 | Full Web Integration |
| P6-ACC-065 | RAG TOOL Role／Citation／Restart互換 | Functional Smoke |
| P6-ACC-066 | RAG最終品質判定をPhase 7前に完了主張0 | Docs／Experiment Review |
| P6-ACC-067 | Stop／Retry／Regenerate／Branch／Resume回帰 | Integration Matrix |
| P6-ACC-068 | Public／BasicでControl／Judge／Repair／Record Call 0 | Route／DOM／Spy |
| P6-ACC-069 | Qwen Mode比較が再現可能 | Experiment Manifest |
| P6-ACC-070 | DeepSeek Supported／Unsupportedを正確に分岐 | Capability Evidence |
| P6-ACC-071 | Token／Latency／Call／Repair／Byteを分離計測 | Metrics |
| P6-ACC-072 | False Positive／Negative不明値を0で捏造0 | Result Schema |

## 8. Automation／Governance

| ID | Contract | Required Evidence |
|---|---|---|
| P6-ACC-073 | Compaction後Recovery Fidelity | Tracker／Recovery Entry |
| P6-ACC-074 | 5時間Quota後の自動再開Fidelity | Provider Event Evidence |
| P6-ACC-075 | Subphase報告による不要停止0 | Timeline |
| P6-ACC-076 | False Completion／Rework／Human介入を正確分類 | Completion Handoff |
| P6-ACC-077 | 未許可Root外／Provider Memory／Git Mutation／Network／User Data違反0 | Mutation Evidence／Authorized Exception Inventory |
| P6-ACC-077A | 過去Download例外をPhase 6 Authorityへ再利用0 | Activation／Audit Review |
| P6-ACC-078 | Stable直書き0、Correction Append-only | Diff／History Review |
| P6-ACC-079 | Per-WU Evidence濫造0、Material Boundary Recovery | File Inventory |

## 9. Manual Acceptance

User Macで最低限次を確認する。

1. Qwen Default起動。
2. DeepSeek Supported時のQwen→DeepSeek→Qwen切替。
3. Context Size変更とServer継続。
4. Max New Tokens変更と次Generation反映。
5. Main／Guard／Judge／Governance Layer表示。
6. Phase番号なしのUI Label。
7. Guardrail Safe Refusal。
8. Request単位Statusで未実行Pointが混在しない。
9. Judge OBSERVEとRepair ENFORCEの有界Golden Path。
10. Mode OFF復帰、再Open、Browser Reload、Conversation／Citation維持。

## 10. Closure

全Technical／Security／Compatibility Matrix、Open Major Finding 0、Claude COMPLETE_CANDIDATE、Codex Independent Review、User Mac Acceptance、Phase 4〜6 Lossless Compilation、BackupおよびPhase 7 READYが成立した場合だけPhase 6をAcceptedとする。
