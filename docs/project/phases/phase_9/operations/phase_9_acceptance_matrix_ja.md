# Phase 9 Acceptance Matrix

```yaml
document_id: phase_9_acceptance_matrix
document_state: accepted_frozen_ready_not_started
phase: phase_9
language: ja
created_at: 2026-08-31 21:02:44 JST
acceptance_count: 50
phase_9_1_acceptance: P9-ACC-001_to_P9-ACC-038
phase_9_2_acceptance: P9-ACC-039_to_P9-ACC-045
phase_9_3_acceptance: P9-ACC-046_to_P9-ACC-050
```

## 1. Phase 9-1 Acceptance — Current Detailed Freeze

| ID | Acceptance |
|---|---|
| P9-ACC-001 | Phase 6〜8の成立済みSource、Contract、PersistenceおよびUser Dataを再実装・Rollbackしない。 |
| P9-ACC-002 | 2026-08-30以降の再編をCurrent Source Priorityとし、Phase 9とPhase 10のScopeを混同しない。 |
| P9-ACC-003 | OFF／Unavailable／Unsupported／Deferred／Unknown／FailedをPASSまたは実行済みと表示しない。 |
| P9-ACC-004 | Provider／Model Path／User Path／GD名／Hardware値をCoreへHard-codeしない。 |
| P9-ACC-005 | Phase 9-1完了候補Return前にPhase 9-2／9-3を実装しない。 |
| P9-ACC-006 | Selene／Qwen3GuardのArtifact、Manifest、Digest、Backend、HardwareおよびAuthority PreflightをEvidence化する。 |
| P9-ACC-007 | SeleneをConfiguredだけでなくCandidate Load／Strict Contract／Executed ProviderへProduction配線する。 |
| P9-ACC-008 | Seleneが成立する環境では実Artifact Inferenceを行い、成立しない場合はStage別`RESOURCE_GATED／FAILED`を返す。 |
| P9-ACC-009 | Selene OutputのMalformed／Timeout／Cancel／UnavailableをStrict DecodeしたTyped Failureへ収束する。 |
| P9-ACC-010 | Qwen3GuardをConfiguredだけでなくCandidate Load／Target別Contract／Executed ProviderへProduction配線する。 |
| P9-ACC-011 | Qwen3Guardが成立する環境では実Artifact Inferenceを行い、成立しない場合はStage別`RESOURCE_GATED／FAILED`を返す。 |
| P9-ACC-012 | Qwen3GuardのInput／Output Target、Category Set、Line ProtocolおよびEvidence Identityが一致する。 |
| P9-ACC-013 | Startup全Mode OFFでDedicated Model Call 0、不要なDedicated Role常駐Load 0を維持する。 |
| P9-ACC-014 | Mode ONはPreflight／Load成功後にAtomic Commitし、OFF／ShutdownはLease終了後にUnloadする。 |
| P9-ACC-015 | Configured／Active／Executed Provider、Artifact IdentityおよびEvidence Providerが一致する。 |
| P9-ACC-016 | Real Model Call 0／1以上、Stage、Latency、BudgetおよびFailure ReasonをTestまたはUser-facing Technical Traceで確認できる。 |
| P9-ACC-017 | Semantic 109 RuleをDefinition／Point／Capability／Criterion Type別に機械集計できる。 |
| P9-ACC-018 | Normalized IRから対応Semantic Criterionへ変換し、実評価入力へ渡せる。 |
| P9-ACC-019 | Semantic 109件が一律Deferredではなく、evaluated／not_applicable／unsupported／unknown／deferredへRule単位で分かれる。 |
| P9-ACC-020 | Built-in Evaluatorは対応Criterionだけを評価し、意味評価不能なCriterionをPASSへ捏造しない。 |
| P9-ACC-021 | selected／evaluated／passed／deviated／unknown／not_applicable／deferredの件数が全対象数と整合する。 |
| P9-ACC-022 | Criterion ID、Rule Revision、Point、Outcome、ReasonおよびEvidence Pointerを追跡できる。 |
| P9-ACC-023 | Independent JudgeとMain Self JudgeをProvider／Artifact／Evidence上で区別できる。 |
| P9-ACC-024 | Judge Outputのaccept／deviation／unsupported／malformed／timeout／cancelledをStrict Decodeできる。 |
| P9-ACC-025 | Material DeviationからRepair Eligibility／Plan／Budget／Candidate生成へ進める。 |
| P9-ACC-026 | Repair CandidateをRejudgeし、原Candidateと別Identityで評価できる。 |
| P9-ACC-027 | Adopt／Reject／Safe Fallback／FailureのFinal DispositionとUser Presentationが一致する。 |
| P9-ACC-028 | Semantic ENFORCEは対応済みActionだけを実行し、Authorityを追加しない。 |
| P9-ACC-029 | Conflict／Priority／Budget／Max Repair／Deadlineを有界化し、無限Loopしない。 |
| P9-ACC-030 | Cancel／Deadline／OFF／Shutdown後のLate Judge／Repair ResultがCurrentへ追加されない。 |
| P9-ACC-031 | Request IDでCriterion、Judge、Repair、Rejudge、FinalおよびRecordingを相関できる。 |
| P9-ACC-032 | OFF TurnはCurrent実行なしと表示し、前回ResultをHistoricalとして分離する。 |
| P9-ACC-033 | 通常Chat、Conversation Persistence、Reload／Restart／別TabをMaterial Regressionさせない。 |
| P9-ACC-034 | Local RAG／Citation／Manual URL／Dev Agent FoundationをMaterial Regressionさせない。 |
| P9-ACC-035 | 変更範囲に比例したBackend／Mypy／Ruff／Frontend／BuildのCanonical VerificationがPASSする。 |
| P9-ACC-036 | 観点変更二段階Internal ReviewでCritical／Major／MVP BlockerをReworkし、Minorを無限追加しない。 |
| P9-ACC-037 | User Mac Manual SheetでDedicated Role、Semantic Criterion、Judge／Repair／Rejudge、ENFORCE、OFF／Stopを確認できる。 |
| P9-ACC-038 | 最大Claimを`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`に制限し、Phase 9 ClosureまたはP9-2開始を自己承認しない。 |

## 2. Phase 9-2 Acceptance — Reserved Boundary

| ID | Acceptance |
|---|---|
| P9-ACC-039 | Experiment、Run、Request、Config SnapshotおよびArtifact／Definition Digestを相関できる。 |
| P9-ACC-040 | Main／Judge／Guard／GD／RAG／Repair／ModeのVariantを同一Caseで比較できる。 |
| P9-ACC-041 | Multiple Definition、Conflict、Suppression、Repair PropagationおよびRouting差を比較できる。 |
| P9-ACC-042 | Historical Fact／Current Source、False-positive RetrievalおよびStrict NO_HITをVersion付きCaseで評価できる。 |
| P9-ACC-043 | Source Authority／ProvenanceとCorrection Acceptance／Belief Revision Successを観測できる。 |
| P9-ACC-044 | Manual URL Fail-closed時のModel Call 0、Strict BufferおよびProgressive Presentationを比較できる。 |
| P9-ACC-045 | Baseline／Regression／Ablation、定量／定性、Human／Judgeを混同しないComparison Reportを作れる。 |

## 3. Phase 9-3 Acceptance — Conditional Reserved Boundary

| ID | Acceptance |
|---|---|
| P9-ACC-046 | Context Capacity／Usage／Effective Budget／Reserve／Safety Margin／Pressure Stateを分離できる。 |
| P9-ACC-047 | Default OFF、OBSERVE Mutation 0、ENFORCE／ManualのPre-Snapshot／Atomic Swap／Rollbackが成立する。 |
| P9-ACC-048 | Original Chat／Structured Context／Snapshot／Recovery Index／Selective Rehydrationを分離し、原Chatを自動削除しない。 |
| P9-ACC-049 | Handoff／Manual Compaction／Recovery／Governance TraceのUI-independent API／Event／Identity Contractが成立する。 |
| P9-ACC-050 | 9-3を実装しない場合も、未実装理由、再開条件およびPhase 10／11境界を正直にDispositionできる。 |

## 4. Disposition Rules

```text
PASS:
  Source／Test／Evidence／User ManualでAcceptanceが成立。

RESOURCE_GATED:
  Artifact／Hardware／Authority等の物理条件で実経路を成立できず、
  Stage別Evidenceと正直なFallbackがある。PASSではない。

PARTIAL:
  中心Contractの一部が成立するが、Acceptance全体は未成立。

DEFERRED:
  後続Program／PhaseへUser Decisionで延期。

NOT RUN:
  必要AuthorityまたはUser Manualが未実施。
```

Test総数、Fixture PASS、Manifest存在またはUI表示だけでReal Dedicated Provider、Semantic Evaluation、Judge／Repair Golden PathをPASSへ格上げしない。
