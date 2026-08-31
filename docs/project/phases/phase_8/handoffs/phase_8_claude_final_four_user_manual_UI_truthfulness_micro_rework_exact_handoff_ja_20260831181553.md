# Phase 8 Final Four User Manual UI／Truthfulness — Claude Micro Rework Exact Handoff

```yaml
document_type: exact_differential_execution_handoff
document_state: final
provider: Claude
role: designer_and_implementer
task_identity: current_continued_claude_task
task_state: continued_not_fresh
phase: phase_8
package: P8-MR9-0_through_P8-MR9-4
implementation_authority: true
independent_review_authority: false
phase_8_closure_authority: false
maximum_claim: COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK
created_at: 2026-08-31 18:15:53 JST
```

## 1. Objective

P8-MR8後のUser Mac実画面で残った4件だけをMicro Reworkし、Phase 8を最終User Recheckへ返す。

これはCurrent Claude Taskの継続である。Fresh Task化、Bootstrap、Role Reading、Phase 8全Mandatory Readingまたは
過去Packageの再実行は行わない。

## 2. Mandatory Differential Reading

次の4文書だけを指定順で全文読む。Current Working TreeをCanonical Baselineとする。

### 2.1 User Mac Post-MR8 Evidence

```text
docs/project/phases/phase_8/history/operations/phase_8_user_mac_post_mr8_full_manual_acceptance_and_behavior_evidence_ja_20260831181553.md
SHA-512:
16a57365699e915d18a49ffd8e8a06cc5d67901c2a54bf33fdf2302b7019d38c76c2cd9d526556c8ff86c912e2d7ea6760355ca0aa7fa04e9d59aac6ca778ac8
```

### 2.2 Latest Exact Return

```text
docs/project/phases/phase_8/handoffs/phase_8_claude_manual_url_final_two_blockers_micro_rework_exact_return_handoff_ja_20260831150330.md
SHA-512:
5676881c8d8121eaa8ad1b30593dc8e27ecbfa2667275fb6cf68be407cb4e7d209793c4bd3bc34b97f0ceae7a837b1307ac345f7408cdaa31b13828b60494b3e
```

### 2.3 Latest Recovery

```text
docs/project/phases/phase_8/history/index/phase_8_claude_manual_url_final_two_blockers_micro_rework_recovery_ja_20260831150330.md
SHA-512:
75dd5f816b4a760fa0f2154ee686564cec5dd6053c05cbb19be22ccc6e14f17e9102bf822d56200487b7ecb79644e71cad42af8e6147fc3c6d29e81a6dc7c80e
```

### 2.4 Current Unresolved Registry

```text
docs/project/shared/未解決/current_unresolved_findings_registry_ja.md
SHA-512:
30b4f8eb42dfb9835156f02da8a3899e13c440a56390c32d3e8fa23ece799777cf182a1b986faadadc2329121031073f511f03e30bcfc9473bd2f4851fd58f10
```

Digest不一致がある場合はPath／Expected／ObservedをReturnへ記録する。User／Codexによる本Handoff後のDocs追記だけで
停止せず、4件の実装Scopeが変わっていなければCurrent Working Treeを優先して継続する。

## 3. Preserved Baseline

次は成立済みであり、再実装、Rollbackまたは追加Hardeningを行わない。

```text
P8-MR0〜MR8 Source／Test／Persistence
Manual URL UTF-8 Public Fetch／Retry／Fail-closed Grounding
HTML本文抽出／Final Prompt-aware Budget／Typed Failure
Web Citation Metadata／Reload／Restart
Archive／Unarchive／Sidebar／Panel同期
Constitution 3-Mode Semantics／Production OFF
Dev Agent Run／Step／Budget／Envelope／Approval Evidence／実File Fixture
Local Corpus削除／Current Citation Freshness
General Keyword Search Fixture境界
```

## 4. Open Findings — 4件限定

```text
P8-MANUAL-FINAL-001 Completion Gateでcompletionを表示
P8-MANUAL-FINAL-002 Chat切替／新規Chat／成功した次Turnで過去Web Failure警告をCurrent Composerから消す
P8-MANUAL-FINAL-003 Untrusted External Contentの文字色不統一
P8-MANUAL-FINAL-004 新しいDemo Runを開始Buttonの色不統一
```

## 5. P8-MR9-0 — Entry Freeze

- Mandatory Differential Readingを行う。
- Open Findingを4件に固定する。
- Current Working TreeをCanonicalとする。
- 新Bootstrap、新Task、全Phase Readingまたは全Reviewを開始しない。
- Recovery Indexを作り、True StopがなければP8-MR9-4まで連結実行する。

## 6. P8-MR9-1 — Completion Gate Truthfulness

### 6.1 Required Behavior

Dev Agentが`awaiting_approval`のTool Gateにいる時は、Current Tool Descriptor／Gateから次を表示する。

```text
Gate Reason: external_write
```

Dev Agentが`awaiting_completion_approval`にいる時は、Current Completion Gateを表示する。

```text
Gate Reason: completion
```

Completion Gateで`run.envelope.gate_reasons`のTool Reasonを流用しない。Runtime Contract上の
`CompletionApprovalEvidence.gate_reason = completion`、Current Run Stateまたは既存Typed Contractを正本にする。

### 6.2 Non-goal

- Approval Engine、Authorization Envelope、Completion TransitionまたはPersistence Schemaの作り直し。
- `external_write` Tool Gateの削除。
- Level 1実Project Tool Authorityの追加。

### 6.3 Test

同一Frontend Testまたは分離Testで次をAssertする。

```text
awaiting_approval -> external_write
awaiting_completion_approval -> completion
completed -> Completion Gate表示なし
```

Backend変更が不要ならFrontendだけで完結してよい。

## 7. P8-MR9-2 — Current Composer Web Failure Lifecycle

### 7.1 Required Behavior

Manual URL Failure警告は、Current Live Attempt／Current Composer Stateへだけ属する。

次で消す。

```text
Chat AでFailure -> Chat Bへ切替
Chat AでFailure -> 新規Chat
Chat AでFailure -> 次Turnが成功Terminalへ到達
```

次を保つ。

```text
同じCurrent AttemptがFailureへ到達した直後は警告を表示
別の新しいFailureが起きれば新しい警告を表示
Historical Failure Turn／Stored Failure Reason／Evidenceを変更しない
Chat切替後に戻っても、過去FailureをCurrent Composer警告として復活させない
```

Global／Application-wideなStale StatusをConversation Current Stateとして再利用しない。必要ならConversation ID、Attempt ID、
Generation Lifecycleまたは選択Chat変更EventへBoundする。固定Timeoutで消す方式にしない。

### 7.2 Test

Frontend Testで少なくとも次を証明する。

```text
failure warning appears on current failure
select another chat -> warning absent
create new chat -> warning absent
successful next turn -> old warning absent
historical failure bubble／detail remains
```

Persistence／Backend Error Contractを変更する必要がない限り触らない。

## 8. P8-MR9-3 — Two Style Corrections

### 8.1 Untrusted Label

`Untrusted External Content（信頼できない外部Content）`の意味、文言および表示は保持する。
周囲のWeb Citation Metadataと調和し、Light／Dark Themeで読める既存Semantic Token／Classへ統一する。
Labelを薄くして意味を弱めたり、Trusted表示へ変えたりしない。

### 8.2 New Demo Run Button

Completed Runの`新しいDemo Runを開始`へ、既存の同等Primary Actionと同じButton Class／Tokenを適用する。
新しいButton Design Systemまたは専用Hard-code Colorを作らない。

### 8.3 Test

- Untrusted LabelのClass／Semantic StyleをFrontend Testで確認する。
- Completed状態のNew Demo Run Buttonが既存Primary Classを使うことを確認する。
- Light／Darkの既存Button／Citation Regressionを保つ。

## 9. P8-MR9-4 — Verification／Internal Review／Return

1. 4 Findingを1件ずつFixed／Not Fixedへ再導出する。
2. 変更ComponentのFocused Frontend Testを行う。
3. Frontend Typecheck、Full Test、Lint、Buildを行い、配信用Static Artifactを更新する。
4. Backend Sourceを変更しない場合、Backend Full／Mypy／Ruffの再実行は不要。変更した場合だけ変更範囲のFocused Testと必要なCanonical Checkを行う。
5. Requirement／State Lifecycle／UI Truthfulness／Regressionの4観点でInternal Reviewを1 Cycleだけ行う。
6. Critical／Major／MVP BlockerだけをInline Reworkする。Minor／Hardening／今回Deferred項目で追加Cycleを開始しない。
7. Recovery IndexとExact Return Handoffを作る。Acceptance Matrix、Roadmap、Closure Docsを変更しない。

## 10. Explicit Deferred／Prohibited Scope

今回直さない。

```text
Model Call 0 Live Observability
Shift_JIS／x-sjis／Charset Detection
Settings Manual URL結果Close／Reopen Lifecycle
Manual URL成功／失敗Card Redesign
通常Composer本文URLの自動抽出
Archive Dedicated Manage Modal
False-positive RAG Retrieval／Semantic Judge／Strict NO_HIT
過去Context Fact Freshness Governance
General Search Provider／Automatic Search
Full Readability／Chunking／Hostile Content Hardening
実Project File Tool／Real MCP／Level 1完成
```

## 11. Authority／Prohibitions

### 許可

- Project Root内で4件に必要なFrontend Source／Test／Static Artifact。
- Backendの既存Typed ContractをFrontendへ正しく投影するために不可避な最小Source／Test。ただし先にFrontendだけで解決可能か確認する。
- Phase 8 Recovery Index／Exact Return Handoff。
- Project Root内のTest／Typecheck／Lint／Build。

### 禁止

- Git Read／Write／Commit／Push。
- Network／Install／Download。
- Real Browser／Real Model／Real MCP。
- User `runtime_data/`へのRead／Write。
- Project Root外への任意Read／Write。
- Roadmap／Phase 8 Closure／Backup／Phase 9開始。
- 4件以外の未解決を便乗実装すること。
- Minor Findingを理由に追加Review Cycleまたは停止を作ること。

実装難度、既存Dirty Working Tree、Pending Controller Reviewまたは小さなUI判断だけを理由に停止しない。
既存変更はCopilot／Claude／Codex／Userの成立済みPhase 8 Baselineであり、Rollbackしない。

## 12. Return Condition

```text
P8-MANUAL-FINAL-001〜004 Individual Disposition
Changed Paths
Focused Frontend Test Result
Frontend Typecheck／Full Test／Lint／Build Result
Backend変更有無と、変更した場合のVerification Result
Static Artifact更新
Internal Review Result
Network／Install／Git／Browser／Model／User runtime_data Action Count
Recovery Index Path
Exact Return Handoff Path／SHA-512
```

最大Claimは`COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK`。Phase 8 Closure、P8-ACC-040 PASS、Roadmap、Git、Backupまたは
Phase 9 READYを主張しない。
