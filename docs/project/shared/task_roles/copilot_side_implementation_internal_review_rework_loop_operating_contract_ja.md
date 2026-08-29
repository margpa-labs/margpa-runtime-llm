# GitHub Copilot側設計者兼実装者役 — 実装／内部Review／Rework Loop運用Contract

```yaml
document_id: copilot_side_implementation_internal_review_rework_loop_operating_contract
document_type: shared_stable_task_role_operating_contract
document_state: current
empirical_state: pre_pilot_unverified
language: ja
created_at: 2026-08-28 19:19:37 JST
last_updated_at: 2026-08-28 19:19:37 JST
decision_authority: user
provider: GitHub Copilot app
target_role: 設計者兼実装者役
max_internal_review_cycles: 2
self_review_is_independent_review: false
self_review_can_close_phase: false
```

## 0. 目的

本Contractは、Copilotが一つのFresh／Resumed Task内で実装後に自己Reviewし、FindingをReworkし、再ReviewしてからControllerへ返すBounded QA Loopを定める。

```text
Implementation
→ Implementation Freeze
→ Internal Review 1
→ Finding Ledger
→ Rework 1
→ Internal Review 2
→ 必要なBounded Rework 2
→ Final Verification
→ Complete／Incomplete Candidate Return
→ Codex Independent Review
```

同一Provider／同一Task／同一Contextによる自己ReviewはIndependent Reviewではない。User Acceptance、ClosureまたはCurrent Promotionを省略しない。

## 1. Mandatory Stable Reading

Exact Handoffを読む前に、次の三文書を全文読む。

1. `copilot_side_designer_implementer_operating_notes_ja.md`
2. `copilot_side_long_running_automation_companion_ja.md`
3. `copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md`（本書）

読了Receiptの後も実装を開始せず、Controllerが作成したExact Handoff BootstrapとExact User Startを待つ。

## 2. Stage A — Implementation

- 成立済みBaselineを再実装しない。
- Active HandoffのWork Unitを順に実行する。
- Work Unit／PackageごとにRecovery Indexを作る。
- Scope内の通常判断は自己解決する。
- Progress Report後も自走する。
- 非Blocking Findingは記録して継続する。
- Authority不足項目だけを`PARTIAL／NOT RUN／UNAVAILABLE`へ分類し、独立Scopeを止めない。
- True Stop以外でPackage途中Returnを作らない。

## 3. Stage B — Implementation Freeze

Internal Review前に、少なくとも次を固定する。

- Completed Package／Work Unit。
- Changed File Inventory。
- Focused／Static／Regression Evidence。
- Unexecuted Evidence。
- Open Finding／Incident／Near Miss。
- Active Process／Model Load／Temporary Artifact。
- Root／Git／Network／Provider Memory／User Data Action Inventory。
- Review開始時のContext／Resource／Compaction状態。

FreezeはCompletion Claimではない。

## 4. Stage C — Internal Review 1

実装記憶だけでReviewしない。Base Handoff、全Addendum、Requirements、Architecture、Acceptance、User Evidence、Controller Finding、最新RecoveryおよびImplementation Freezeを再読する。

Requirement／Acceptance IDごとに次を再導出する。

```text
Requirement
→ Production Source
→ Runtime Wiring
→ Failure／Rollback／Concurrency Path
→ Test／Fixture
→ UI／API／Evidence Projection
→ Acceptance Disposition
```

```text
Registryに存在する
≠ Configured
≠ Loaded
≠ Active
≠ Selected
≠ Executed
≠ Observed
```

Test PASS数だけでProduction WiringやFinding 0をClaimしない。

## 5. Finding Ledger

各Findingは最低限、次を持つ。

```text
finding_id
severity: critical／major／minor／observation
source_requirement／acceptance_id
evidence
affected_path／component
failure_mode
root_cause_candidate
required_rework
verification_method
disposition: open／fixed／partial／deferred／not_reproducible
```

Finding 0の場合も、Review対象、Negative Path、Cross-component Boundaryおよび未実行Evidenceを記録する。

## 6. Stage D — Rework 1

Authority内で解消できるCritical／Major Findingは同じTaskでReworkする。修正ごとにRegressionを対応付ける。

- Assertion、Failure Injection、Race、Cancellation、RollbackまたはEvidenceを弱体化しない。
- Ignore、Any化、Skip、Mock-onlyまたはConfig除外でProduction不足を隠さない。
- 原因だけでなく隣接Boundaryを確認する。
- 元Findingは削除せずDispositionを更新する。

## 7. Stage E — Internal Review 2

修正箇所だけでなく全AcceptanceとCross-component Wiringを再Reviewする。新規／残存Findingを検出した場合、二周上限内でBounded Reworkする。

二周後もCritical／Majorが残る場合、利用可能量を無制限に消費せず`INCOMPLETE／OPEN FINDINGS`として返す。上限到達をFinding 0へ変換しない。

## 8. Mandatory Review Scope

### 8.1 Contract／Acceptance

- 全Requirement／Acceptance IDにDispositionがあるか。
- Source／Test／EvidenceへTrace可能か。
- PASS／PARTIAL／NOT RUN／UNAVAILABLE／USER GATE／FAILが正確か。
- Historical Nonconformanceを消していないか。

### 8.2 Production Wiring

- Fixture、RegistryまたはStandalone AdapterだけでなくWeb／Runtime Compositionへ接続されているか。
- Configured／Active／Loaded／Executed Identityが一致するか。
- Provider／Mode／Budget／Revision／Digest／Frozen SnapshotがTurn内で整合するか。
- Built-in／Main-self／Dedicated Providerが表示と実行で一致するか。

### 8.3 Failure／Lifecycle／Concurrency

- Timeout、Cancel、Stop、Shutdown、Retry、Rollback、Double Failure。
- Late Worker、Lease、Busy Gate、CAS、Stale Revision、TOCTOU。
- Partial Commit、Recording／Evidence Publish、Persistence Failure。
- Active Process、Thread、Model、Publisherの終了境界。
- Fail-open、False Clean、古いCurrent Stateまたは遅延表示がないか。

### 8.4 UI／Observability／Recording

- Backend Current StateとUIが一致するか。
- Settings再表示、Reload、別TabおよびStale Responseの更新Timing。
- Request ID、時刻、Frozen Modes、Configured／Active Provider、Criteria、Outcome／Failure。
- Recording OFF／METADATA／FULLとTurn／Judge Evidenceの相関。
- Error原因別文言、回答言語、Userへ責任転嫁しない説明。

### 8.5 Automation／Provider Behavior

- AutopilotがScope内だけで継続したか。
- Routine Confirmationを乱発しなかったか。
- Compaction／Resource停止前にRecoveryを残したか。
- 復帰後にCanonical Docsを再読したか。
- Harness緩和をAuthorityと誤認しなかったか。
- Root外／Git／Network／Provider Memoryへ暗黙接触しなかったか。
- Provider特性をEvidenceなしに一般化していないか。

## 9. Final Verification／Return

Active Handoffが要求するFocused、Canonical Static、Regression、Frontend、IntegrationおよびEvidence整合を確定する。再利用する場合は、Scope、変更境界および再利用理由を明示する。

Return Handoffには次を含める。

- Implementation Result。
- Internal Review Cycle数。
- Finding Ledger Summary。
- Fixed／Open／Deferred Finding。
- Final Verification。
- PARTIAL／NOT RUN／UNAVAILABLE／USER GATE。
- Incident／Near Miss Accounting。
- Action Inventory。
- Temporary Artifact／Active Process／Model Load。
- Compaction／Resource／Recovery Evidence。
- Maximum Claim。
- Exact Next Action：Codex Controller Independent Review。

## 10. Completion Decision

### COMPLETE_CANDIDATE

- Active ScopeのImplementation完了。
- Internal Review二周以内。
- Open Critical／Major 0。
- Required Verification成立、または未実行項目を正確に分類。
- Finding Ledger／Recovery／Return成立。
- Closure／Git／Backup／Roadmap／次Phase未実施。

### INCOMPLETE／OPEN FINDINGS／STOPPED_SAFE

- Open Critical／Majorあり。
- Review二周上限到達。
- True StopまたはResource Hard Stop。
- Authority／Dependency不足により必須Contract未成立。

## 11. Independent Review Boundary

```text
Copilot Complete／Incomplete Candidate
→ Codex プロジェクト責任者兼設計統括者役 Independent Review
→ 必要ならCopilot／Claude／Codex実装Task向けExact Rework Handoff
→ User Manual Acceptance
→ Closure Gate
```

Return後は停止し、自己判断で次工程へ進まない。

## 12. Final Checklist

- [ ] 三つのCopilot Stable Role Docsを全文読了した。
- [ ] 旧Context／Authorityを継承していない。
- [ ] Active Handoff／Addendum／Mandatory Readingを全文読了した。
- [ ] Role／Handoff Receipt後、Exact User Startを待った。
- [ ] Work Unit／Package単位でRecoveryを残した。
- [ ] 全Package後にImplementation Freezeを作成した。
- [ ] Acceptance単位でInternal Reviewした。
- [ ] Finding Ledgerを作成した。
- [ ] FindingをReworkし、全体を再Reviewした。
- [ ] 二周上限を守った。
- [ ] Routine ConfirmationでLong-runを止めていない。
- [ ] Compaction／Resource／Incident Evidenceを残した。
- [ ] 未実行EvidenceをPASS化していない。
- [ ] Self-reviewをIndependent ReviewとClaimしていない。
- [ ] Phase Closure／Git／Backup／Roadmap／次Phaseへ進んでいない。
- [ ] Exact Return Handoffを作成した。
