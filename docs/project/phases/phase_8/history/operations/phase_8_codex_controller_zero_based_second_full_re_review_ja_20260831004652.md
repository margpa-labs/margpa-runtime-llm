# Phase 8 Codex Controllerゼロベース第2回全体再Review

```yaml
document_id: phase_8_codex_controller_zero_based_second_full_re_review_20260831004652
document_type: controller_zero_based_full_re_review
document_state: final
language: ja
created_at: 2026-08-31 00:46:52 JST
provider: Codex
role: プロジェクト責任者兼設計統括者役
trigger: UserからPhase 8が数時間でUser Manual Readyまで到達したClaimへの再確認要求
review_scope: phase_8_requirements_and_acceptance_001_through_040_zero_based
supersedes_controller_disposition:
  - phase_8_codex_controller_final_re_review_and_user_manual_ready_20260831003518
controller_disposition: REWORK_REQUIRED_BOUNDED
phase_8_closure: not_claimed
```

## 1. 結論

前回の`USER_MANUAL_READY`判定を撤回する。

前回ReviewはP8-CODEX-004のApproval Evidence Scope修正を正しく確認したが、Review Scopeを`P8-CODEX-004_only_plus_preserved_findings`へ限定したまま、Phase 8 Requirements／Architecture／40 Acceptanceへ戻るゼロベース全体再導出を行わず、P8-A〜P8-F全体へ`USER_MANUAL_READY`を拡張した。この拡張は不適切だった。

```text
P8-CODEX-001〜004: RESOLVEDのまま維持
New Critical: 0
New Major / MVP Blocker: 4
New Verification / Manual-Sheet Finding: 2
Controller Disposition: REWORK_REQUIRED_BOUNDED
User Manual: HOLD
Phase 8 Closure: NOT CLAIMED
```

Phase 8全体の再実装、正式Level 1 Agent、Real MCP、General Web Search、Dynamic Sub-Agent、Enterprise Hardeningは不要である。以下の明示要件Gapだけを限定是正する。

## 2. Review方法

正本：

- `docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md`
- `docs/project/phases/phase_8/architecture/phase_8_architecture_ja.md`
- `docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md`
- `docs/project/phases/phase_8/operations/phase_8_execution_plan_ja.md`
- `docs/project/phases/phase_8/phase_index_ja.md`

Source直接確認：

- Manual URL Security／Fetch／Evidence／Citation／Conversation Injection／Persistence
- Archive Lazy List／Open／UnarchiveおよびBranch Presentation Boundary
- Constitution Manifest／Provider／Resolver／Production Composition／UI
- Dev Agent Contract／Run Service／Tool Registry／Approval／Envelope／Persistence／REST／UI
- P8-F Traceability Matrix／User Manual Test Sheet／CR1〜CR5 Return群

Codex Focused Verification：

```text
Dev Agent + Constitution Backend: 106 passed
Web Knowledge + Constitution + Dev Agent Backend: 190 passed
Archive／Unarchive Focused: 3 passed
Dev Agent REST／Limits Focused: 21 passed
Frontend Dev Agent／Constitution／Archive／Branch: 36 passed

Manual URL Conversation Focused under network-restricted environment:
89 passed / 3 failed / 45 deselected
```

最後の3 FailureはProduct Fetch Adapterの実Network失敗ではなく、`tests/unit/conversation/test_conversation_generation.py`だけがSafe DNS Stubを持たず、`validate_url_before_connect()`から実`socket.getaddrinfo()`へ到達する非Hermetic Test構成による。

## 3. New Findings

### P8-CODEX-005 — Redirect後Canonical URLとSource Authorityが不一致

```yaml
severity: major
priority: P0
classification: evidence_truthfulness_and_mvp_blocker
affected_requirements:
  - P8-REQ-007
  - P8-REQ-008
affected_acceptance:
  - P8-ACC-012
```

`fetch_direct_url()`は`source_authority`をRedirect前のUser入力URL Hostから算出し、`_build_fetched_evidence()`はCanonical URLだけをRedirect後の最終URLへ差し替える。

Codex非Network Probe：

```yaml
requested_url: https://agency.gov/start
final_canonical_url: https://example.org/final
reported_source_authority: official
expected_final_host_authority: general
```

最終的に読んだContentが`example.org`由来であるのに、Citationは`official`と表示し得る。これは取得成功と内容信頼を分離する要件に反する。さらに`WebCitation`はOriginal／Requested URL Fieldを持たず、P8-REQ-007の「URL、Canonical URL」双方保持も成立していない。

限定是正：

- Source Authorityを最終Canonical URL Hostから再計算する。
- Requested URLとCanonical URLを別FieldでEvidence／Citation／Persistence／UIへ保持する。
- 別Authority ClassへのRedirect Regression Testを追加する。
- Redirect Chain全履歴、Browser SandboxまたはHostile-site解析までは要求しない。

### P8-CODEX-006 — Budget未実装をMax Stepで代替してPASS Claim

```yaml
severity: major
priority: P0
classification: missing_explicit_requirement_and_false_acceptance_claim
affected_requirements:
  - P8-REQ-029
affected_acceptance:
  - P8-ACC-036
```

`RunSnapshot`、Start Request、Tool Descriptor、Run Service、REST ResponseおよびFrontendにDev Agent Budget Field／Usage／Limit／Exceeded Dispositionが存在しない。Traceability Matrixは「Fake Toolに実Costが無いためBudgetはMax Stepで代替」としてP8-ACC-036をPASSにしたが、Step数制限とBudgetは同義ではない。

```text
RunSnapshot Fields:
approval_profile, approvals, capability_id, completion,
constitution_mode, constitution_rule_ids, created_at,
deadline_at, envelope, max_steps, plan, retry_policy,
run_id, schema_version, state, steps

Budget Field: NONE
Budget Usage: NONE
budget_exceeded Disposition: NONE
```

限定是正はFake Tool Foundationに比例したDeterministic Budgetでよい。実料金、Token BillingまたはProvider Cost APIは不要だが、少なくともFrozen Limit、消費単位、実行前Check、Exceeded時のTyped Stop、PersistenceおよびTestが必要である。

### P8-CODEX-007 — Completion Gate未配線／重要Gate分類の実動Evidence不足

```yaml
severity: major
priority: P0
classification: approval_harness_mvp_blocker
affected_requirements:
  - P8-REQ-027
affected_acceptance:
  - P8-ACC-034
```

`ImportantGateReason`には8 Categoryが列挙されるが、Production Registryで実際に使うのは`external_write`だけである。`network／cost／irreversible／secret_or_privacy／scope_expansion／critical_incident／completion`は列挙以外の実配線またはCategory別Testがない。

特にCompletionはTool DescriptorではなくRun Lifecycle Gateである。しかし現Run Serviceは最後のPending Stepが無くなるとApprovalなしで自動`completed`へ収束する。Architectureが定めるImportant-gate-onlyのCompletion User Gateは成立していない。

```yaml
enum_categories: 8
production_gated_tools:
  - write_note: external_write
completion_gate_runtime: absent
```

限定是正：

- Generic Gate EngineがCompletionを含む8 Reasonを扱えることを実Testで証明する。
- Important-gate-onlyのCompletion GateをRun-level Typed Evidenceとして実配線する。
- Completion ApprovalはStep ApprovalとIdentity／Scopeを混同しない。
- Real Network／Cost Toolは追加せず、Fixture Descriptor／Lifecycle Testだけでよい。

### P8-CODEX-008 — Constitution Mode比較がProductionではOFF固定

```yaml
severity: major
priority: P0
classification: mvp_stop_line_blocker_and_false_acceptance_claim
affected_requirements:
  - P8-REQ-016
affected_acceptance:
  - P8-ACC-021
```

Contract／Resolver Unit TestはOFF／OBSERVE／ENFORCEの差を表現できる。一方、Production Compositionは`constitution_mode=OFF`固定でCLI／API／UIに比較経路がない。User Manual Test Sheetも「必ずOFF」としており、正本MVP停止線の「OFF／OBSERVE／ENFORCEの差が虚偽なく表示される」を確認できない。

正式Runtime EnforcementをPhase 8へ前倒しする必要はない。限定是正は、実Active ModeがOFF固定であることを維持したまま、同一ManifestをOFF／OBSERVE／ENFORCEへPure Preview Evaluationし、3 ModeのResult差を非Authority・非Activationの比較Evidenceとして表示する方式でよい。

### P8-CODEX-009 — User Manual SheetとRun Completion Transitionの不一致

```yaml
severity: medium
priority: P1
classification: user_manual_and_ui_flow_mismatch
affected_acceptance:
  - P8-ACC-030
  - P8-ACC-040
```

User Manual Test Sheetは、write Approval後に「次のStepへ進める」を1回押すとwrite成功とRun Completedが同時成立すると記載する。実装は最後のTool成功時点ではRunが`running`のままで、さらにもう1回AdvanceしてPending Stepなしを検知して初めて`completed`になる。

Codex Probe：

```yaml
after_last_tool:
  run_state: running
  step_state: succeeded
  completion: null
after_extra_advance:
  run_state: completed
  completion: completed
```

Engineの1 Call 1 Transition方針自体は成立し得るため、単独MVP Blockerとはしない。ただしManual Sheetと実画面期待値は一致させる。自動Finalizeへ変更するか、明示Finalize TransitionとしてUI／文言を区別するかを選び、曖昧な追加Clickを残さない。

### P8-CODEX-010 — Manual URL Conversation Testが実DNSへ依存

```yaml
severity: medium
priority: P1
classification: canonical_verification_reproducibility_blocker
affected_acceptance:
  - P8-ACC-039
```

`tests/unit/web_knowledge/conftest.py`と`tests/integration/web/test_web_search_web_app.py`は`socket.getaddrinfo()`をSafe Public IPへ置換する。しかしManual URLのMain Model注入を検証する`tests/unit/conversation/test_conversation_generation.py`には同等Fixtureがなく、Network-restricted環境で次の3 TestがFailする。

```text
test_manual_web_evidence_is_injected_as_an_untrusted_tool_message
test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn
test_guardrail_context_source_hook_also_governs_manual_web_evidence
```

これはSource Runtime RegressionではなくTest Isolation Gapだが、Network Authority 0で再現可能としたCanonical Verification Claimと両立しない。Test側へLocal Safe DNS Stubを明示し、実Resolverへ接触せず同じProduction Validation Pathを通す。

## 4. Acceptance再導出

前回の`38 PASS / 1 PARTIAL / 1 USER MANUAL GATE`は維持できない。

```text
PASS              33
PARTIAL            3
  P8-ACC-021  Constitution 3 ModeはContract／Unitのみ、Production比較経路なし
  P8-ACC-034  重要GateはExternal Writeのみ実動、Completion等は未配線
  P8-ACC-038  GD相関未実装（既知Foundation Boundary）
FAIL                3
  P8-ACC-012  Redirect後Trust／Authority表示が最終Sourceと不一致になり得る
  P8-ACC-036  Budget実装なし
  P8-ACC-039  Phase 8 Manual URL Conversation TestがNetwork-restricted環境で3 Fail
USER MANUAL GATE   1
  P8-ACC-040
TOTAL              40
```

P8-ACC-026はPhase 8が正式Level 1ではなくResearch Previewであること、Acceptance本文も`Dev Agent Preview`と明示するため、Settings内Preview SwitchでもPASSを維持する。Main Surface全体切替はLevel 1以降のUI発展課題であり、このReworkへ拡張しない。

P8-ACC-038も既知PARTIALのまま保持し、Phase 6／9 Semantic Governance DebtをPhase 8へ逆流させない。

## 5. 前回Controller ReviewのFailure

前回の最終再ReviewはCR5修正の対象範囲では正しかったが、次の推論を誤った。

```text
P8-CODEX-004 Targeted Re-reviewでOpen Findingなし
→ P8-A〜P8-F全体にもOpen Findingなし
→ USER_MANUAL_READY
```

Targeted Re-reviewの成立は、未検査領域の成立を生成しない。特に、Traceability Matrix内の「BudgetをMax Stepで代替」という非同義Claim、Constitution Production OFF固定、Gate Reason EnumだけのCompletion未配線を再検証しなかった。

再発防止：

- 最終`USER_MANUAL_READY`前は、直前ReworkのTargeted Reviewとは別に、正本40 Acceptanceをゼロベースで一度再導出する。
- Test総数、Internal Review回数またはExecutorの`Finding 0`をAcceptance成立の代替にしない。
- 「型／Enumが存在する」「Unitで比較できる」「代替概念がある」を、実Composition／実Lifecycle／明示要件の成立と混同しない。
- PoC／MVP停止線を守る一方、Frozen Requirementを別機能で代替してPASSにしない。実装しない場合はPARTIAL／Deferredへ落とす。

## 6. Exact Next Action

User Manualを開始しない。Current Working Treeを維持し、P8-A〜P8-F、P8-CODEX-001〜004を再実装しない。

限定Rework対象：

```text
1. Redirect最終Source Authority＋Requested/Canonical URL分離
2. Deterministic Dev Agent Budget
3. Completionを含むImportant Gate実配線／Evidence
4. Constitution 3 Modeの非Activation Preview比較
5. Completion UI／Manual Sheet整合
6. Manual URL Conversation TestのNo-real-DNS化
```

Rework後、Codex Controllerが6 FindingだけをTargeted Re-reviewし、40 Acceptanceを再集計する。成立後に初めてP8-ACC-040 User Manualへ進む。
