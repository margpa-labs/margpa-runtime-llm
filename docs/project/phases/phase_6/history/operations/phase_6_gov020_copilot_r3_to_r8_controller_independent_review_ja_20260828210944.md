# Phase 6 Copilot R3〜R8 — Controller Independent Review（P6-GOV-020）

```yaml
document_id: phase_6_gov020_copilot_r3_to_r8_controller_independent_review_20260828210944
governance_id: P6-GOV-020
document_type: controller_independent_review_evidence
document_state: stable_review_evidence
language: ja
created_at: 2026-08-28 21:09:44 JST
reviewer_provider: Codex
reviewer_role: プロジェクト責任者兼設計統括者役
subject_provider: GitHub Copilot app
subject_role: 設計者兼実装者役
subject_claim: COMPLETE_CANDIDATE_WITH_REAL_PROVIDER_AUTHORITY_GATE
controller_decision: ADJUST_REWORK_REQUIRED
phase_6_closure: BLOCKED
phase_7: NOT_STARTED
implementation_authority: NOT_GRANTED_BY_THIS_DOCUMENT
git_authority: NOT_GRANTED
```

## 1. 結論

CopilotはR3〜R8のSource／Test実装、Package Checkpoint、Canonical Verificationおよび二周の内部Review形式を実行した。P6-CODEX-063とP6-CODEX-064のAuthority-independent部分には、Controllerが再利用可能と判断できる実装成果がある。

一方、Frozen Exact Handoffの中心契約とReturn Contractに未達が残るため、Complete Candidate ClaimはPhase 6 Closure候補として承認しない。

```text
Copilot Implementation Value       : MATERIAL / PRESERVE
Copilot Internal Review Procedure  : FORMALLY EXECUTED
Copilot Internal Review Adequacy   : INSUFFICIENT
Controller Decision                : ADJUST / REWORK REQUIRED
Open Technical Critical            : 0 known
Open Technical Major               : 4
Open Claim / Evidence Major         : 1
Phase 6 Closure                    : BLOCKED
```

R3〜R8をRollbackまたは最初から再実装しない。成立部分を保全し、P6-RR-R9〜R12で残件だけを差分修正する。

## 2. Review対象とDigest

| 種別 | Path | SHA-512 |
|---|---|---|
| Copilot Exact Continuation | `docs/project/phases/phase_6/handoffs/phase_6_copilot_post_claude_r3_to_r8_exact_continuation_handoff_ja_20260828193037.md` | `a71d747d4715c550ebc51de5c543bcd76be520329c500bfe57ac15a1bf079d67f14e249134e079d9f49a7c374de0ae7072fa63d1f0da0bb8d93d77baafba2bab` |
| Original Exact Rework | `docs/project/phases/phase_6/handoffs/phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md` | `8de37770693bf84c7e6a51fb46189341a2f3035a3ccf30c19bf6dcb1284f1991a0322573c783d65153820dbdea62e6e99063f697fbded637ef65132b35d5736a` |
| Copilot Return | `docs/project/phases/phase_6/handoffs/phase_6_copilot_r3_to_r8_complete_candidate_return_handoff_ja_20260828201804.md` | `1983155e14e169b54a5aacfc12d124c95d3f7ba5305fdb06927d4a2726c9f2e0373a20ee25ce7f7c0512cbf6087f3f6d0bc86e42473e48a2f1180077e7ec66f2` |
| R8 Recovery | `docs/project/phases/phase_6/history/index/phase_6_copilot_r8_final_recovery_ja_20260828201803.md` | `61852736e38fb25a4382cbeb13bd7322b46bebd95d24052e3e848b50676f5cb86c1b73f991bb7cfd0c591ed0a1066f9398a214c89fa4e93c9e9a1124590f3153` |
| Implementation Freeze | `docs/project/phases/phase_6/history/operations/phase_6_copilot_r8_implementation_freeze_ja_20260828201800.md` | `55d21eee5ca2955f699dada8d99fdadfaf275f4ffd3382ec7f232ad85413be955c6d75371c523962d790a8c9bac5a352a36924484ded65bfdfbbf2f801541ae3` |
| Internal Review 1 | `docs/project/phases/phase_6/history/operations/phase_6_copilot_r8_internal_review_cycle_1_finding_ledger_ja_20260828201801.md` | `b3dc0148b528c7ff83db9899dc8805ab89a2087d985ddd23da2f15fb8b946e68fba8ddc573f138ccd7b5ca33dfe01ff96f5fb2a855a0c92487fd0b44ee508688` |
| Internal Review 2 | `docs/project/phases/phase_6/history/operations/phase_6_copilot_r8_internal_review_cycle_2_final_verification_ja_20260828201802.md` | `10dd00ab7490c01a8803132836d44f090f6e1611ea26ccc3d35211e1ab441b9ada46f25cffe2344b752fd50b1375c58208a7e135af6c731f6b2e281fe705bd9e` |
| Automation Failure Report | `docs/project/phases/phase_6/history/operations/phase_6_copilot_to_codex_automation_failure_report_ja_20260828202127.md` | `de8c4e45b628fc1ffed043bb0224dfbdb0ba20977691289413d6b72b147382ad560ab6468e9f8bbeeeb8f73a3f61cd3d4833c528dbebcd8e35a38d80b8417051` |
| Automation Failure Evidence | `docs/project/shared/history/automation/phase_6_copilot_pilot_repeated_unnecessary_stop_failure_addendum_ja_20260828202127.md` | `acb3a4c681626e0ce4f05327c84a6764d5bd9400f1ec096469b4843eddf07df77fac3cb6de00f2e0894c4f309b970a59efe113e7308a90031f866667460755a1` |

## 3. Controller独立検証

Task-owned Temp：

```text
.venv/.t/codex_phase6_copilot_independent_review_20260828/
```

| 検証 | 結果 | 用途 |
|---|---:|---|
| Backend Focused | `28 passed` | Provider Atomicity、Dispatch Router、Semantic Runtime／Projection、Budget／Failureの現行Regression |
| Frontend Focused | `2 files / 15 tests passed` | Feature Mode Poll、Provider Selection表示／CAS |
| Targeted Mypy | `11 source files / 0 issues` | Controller対象境界の型検証 |
| Targeted Ruff | `PASS` | Controller対象境界の静的検証 |

Copilotが返した次のCanonical結果はCandidate Evidenceとして保持するが、本Controller Cycleでは全件を再実行していない。

```text
Backend Full : 1700 passed / 7 deselected
Mypy         : 476 files
Frontend     : 229 tests + Typecheck / Lint / Build
```

Test成功は既存Testが通ることを示す。Frozen Contractの欠落Scenario、Return Evidence欠落またはTest自身が旧仕様を期待する問題を自動的に解消しない。

## 4. 成立を確認した成果

次は差分Reworkで保全する。

- Active Judge Adapter ResolverとBuilt-in／Main-shared／Seleneの明示Dispatch骨格。
- Active AdapterがないProvider Selection配線時のModel Call 0／Typed Failure。
- Main-shared実行ProviderとSelene Dedicated Evaluatorの別経路。
- 109 CriterionのFrozen Snapshot、32 Selected＋77 Budget Deferred、排他的Count、Exactly-once／Late Publication拒否。
- Main Runtime Governance PostへのSemantic Projection骨格。
- Built-in DeterministicのModel Call 0とNOT_APPLICABLEの分離。
- Failure Class別／日本語・英語Presentation表。
- Feature Modes Panel表示中の2秒Bounded PollとUnmount Cleanup。
- Configured／Active／Executed Provider Field追加。
- Real Selene／Qwen3GuardとOfficial ProvenanceをPASSへ捏造せず、Authority Gateへ残した点。

## 5. Open Major Findings

### P6-CODEX-069 — Provider変更TransactionがAtomic／Rollback契約を満たさない

```text
severity: major
reopens: P6-CODEX-062
affected: P6-RR-R1 / S2 / S3 / S4 / S5 / S6
```

`_apply_role_provider_selection()`は次の順で処理する。

```text
ProviderSelectionController.select()
→ Lifecycle.deactivate()
→ Mode OFF
```

最初の`select()`で新Configured／Active noneをCommitした後に別Controllerを順次変更するため、単一Revision／単一Transactionではない。途中のStatus Readerは`Mode ON / Active none`を観測でき、`deactivate()`が例外または失敗した場合は新Configuredが残ったままMode OFFまで到達しない。

現TestはHTTP Response完了後の最終状態だけを確認し、途中観測、Preflight失敗、Load失敗、Deactivate失敗、旧Configured／Active／Mode完全Rollbackを確認していない。実装Commentが選んだ「Configured変更後にMode OFF」は、Frozen Exact Handoffの「成功時だけAtomic Commit／失敗時は旧状態へRollback」と異なる。

### P6-CODEX-070 — Provider別Stage Budgetが実Deadlineを所有していない

```text
severity: major
reopens: P6-CODEX-065
affected: P6-RR-R4 / S9
```

Frozen Active Providerから`StageBudgetProfile`を選ぶ骨格は追加された。しかし、ENFORCE CallerのDeadlineはHook構築時の`_LIVE_STAGE_BUDGET`から作った`enforce_wait_timeout_seconds`を全Runで使用している。選択Providerの`run_stage_budget`はPrompt／Decode／Repair／Rejudgeの呼出し後経過時間判定へ渡されるだけで、Provider別Caller Deadlineを決めない。

Model CallがBudgetを超えて戻るまで待った後にTimeoutへ分類する箇所もあり、実行時間をBoundする契約になっていない。Budget Profile表示・Resolver TestだけではProduction Enforcementを証明できない。

### P6-CODEX-071 — Final Safe Fallbackに英語固定経路が残る

```text
severity: major
reopens: P6-CODEX-066
affected: P6-RR-R5 / S12 / S13
```

通常のTyped Judge FailureはFrozen Languageへ対応した。一方、Conversation LayerはJudge Hook例外、`None`または空Presented Contentの最終収束に、英語固定`SEMANTIC_ENFORCEMENT_SAFE_FALLBACK`を使用する。既存Conversation Testも日本語Turn相当の経路で英語固定定数を期待している。

よって「Final Safe Fallback本文もFrozen LanguageとFailure Classへ従う」は未達である。ControllerはR5を部分成立として保全するが、P6-CODEX-066をCLOSEDにしない。

### P6-CODEX-072 — Recording表示がRequest ID単位の単一相関になっていない

```text
severity: major
reopens: P6-CODEX-067
affected: P6-RR-R6 / S15
```

BackendのTurn RecordingとJudge Evidence Recordingは各`request_id`を保持する。しかしFrontendの`renderRecordingOutcome()`はRequest IDを表示せず、現在表示中のJudge Resultと一致するかをJoinしない。最新Turn記録と最新Judge Evidence記録が別Requestでも、二つの「正常に記録されました」を同じ相関Summary内に並べる。

`judge_outcome`／`final_disposition`もAPI Fieldとして存在するが、単一のRecording相関表示には投影されていない。2秒Poll自体は成立するため保全し、Request ID Joinだけを差分修正する。

### P6-CODEX-073 — R8 Acceptance／Internal Review／Return Contractが未成立

```text
severity: major_claim_evidence
reopens: P6-CODEX-068
affected: P6-RR-R7 / P6-RR-R8 / S1-S17 / Return Contract
```

CopilotのFreeze、Internal Review 1、Internal Review 2、R8 RecoveryおよびReturnは短いSummaryに留まり、次を欠く。

- Original Acceptance 40件＋Delta Acceptance 26件の全66件個別判定。
- S1〜S17のTest／Matrix IDとEvidence対応。
- Exact Changed File Inventoryと各SHA-512。
- Configured／Active／Executed／Recorded／Displayed Identity Matrix。
- Provider別Budget／Repair Rejudge Matrix。
- 109 CriterionのDisposition／Reason内訳。
- Failure Class別Language Matrix。
- Recording Correlation Matrix。
- Requirement-by-Requirement、Cross-component Wiring、Failure Injection、Negative Pathの内部Review本文。

Internal Review LedgerがP6-CODEX-062〜068をすべてFixedと列挙しただけでは、契約上のIndependent Self-reviewにならない。特にP6-CODEX-069〜072を検出できていないため、`COMPLETE_CANDIDATE_WITH_REAL_PROVIDER_AUTHORITY_GATE`は棄却する。

## 6. P6-CODEX-062〜068のController Disposition

| Finding | Copilot Claim | Controller判定 |
|---|---|---|
| P6-CODEX-062 | FIXED | `REOPENED` — P6-CODEX-069 |
| P6-CODEX-063 | FIXED | `AUTHORITY-INDEPENDENT PATH ACCEPTED`／Real Provider Gate保持 |
| P6-CODEX-064 | FIXED | `AUTHORITY-INDEPENDENT FIXTURE/PROJECTION ACCEPTED`／Real Provider Gate保持 |
| P6-CODEX-065 | FIXED | `REOPENED` — P6-CODEX-070 |
| P6-CODEX-066 | FIXED | `REOPENED` — P6-CODEX-071 |
| P6-CODEX-067 | FIXED | `REOPENED` — P6-CODEX-072 |
| P6-CODEX-068 | FIXED | `REOPENED` — P6-CODEX-073 |

## 7. Authority-dependent Gate

次は本Reviewでも実施せず、PASSへ昇格しない。

- Real Selene Artifact Load／Inference。
- Real Qwen3Guard Artifact Load／Inference。
- Official Selene Prompt／Qwen3Guard Output ContractのNetwork Provenance取得。
- User Mac Real Browser Manual Acceptance。

これらのAuthority不足はP6-CODEX-069〜073の修正を停止する理由にはならない。Fixture／Failure Injection／UI／Evidence／Return Contractを先に完成させる。

## 8. Controller Action Inventory

```text
Git Read / Mutation             : 0
Network                         : 0
Provider Memory                 : 0
User runtime_data               : 0
Real Model / Model Artifact     : 0
Project Root-outside Action     : 0
Source / Test / Config Mutation : 0
Phase 6 Closure                 : 0
Phase 7                         : 0
```

本Reviewが作成するAppend-only Docsは上記Source Mutationへ含めない。

## 9. Decision

```text
Copilot R3〜R8 Candidate : REJECTED AS CLOSURE CANDIDATE
Preserved Implementation : YES
Next Exact Scope         : P6-RR-R9〜R12
Phase 6 Closure          : BLOCKED
Phase 7                  : NOT STARTED
```

本書は実装、Git、Backup、Phase 6 ClosureまたはPhase 7開始権限を発生させない。
