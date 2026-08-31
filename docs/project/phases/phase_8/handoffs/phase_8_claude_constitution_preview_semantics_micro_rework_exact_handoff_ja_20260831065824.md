# Phase 8 Claude Constitution Preview Semantics Micro Rework — Exact Handoff

```yaml
document_id: phase_8_claude_constitution_preview_semantics_micro_rework_exact_handoff_20260831065824
document_type: exact_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 06:58:24 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-RW7-0_through_C
implementation_authority: true
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
phase_8_closure_authority: false
git_authority: false
network_authority: false
real_browser_authority: false
real_model_authority: false
real_mcp_authority: false
```

## 1. Objective

P8-RW6後のCodex Controller二段階Reviewで残った、次の1件だけを限定是正する。

```text
P8-CODEX-012
Constitution PreviewがDecision Outcomeだけを表示し、
Exact Handoff指定のAction Permission／Violation Presentation比較を欠く。
```

P8-CODEX-005／006は解消済みBaseline、P8-CODEX-007は中心Runtime上解消済みである。
P8-CODEX-011は非BlockingのFrozen Envelope Observability差として未解決Registryへ送ったため、本Taskでは修正しない。

## 2. Mandatory Reading

Current Claude Taskを継続し、Fresh BootstrapまたはRole文書の再読を行わない。次だけを指定順で全文読む。

1. 本Exact Handoff
2. `docs/project/phases/phase_8/history/operations/phase_8_codex_controller_rw6_two_cycle_targeted_re_review_ja_20260831065406.md`
3. `docs/project/phases/phase_8/handoffs/phase_8_claude_zero_based_controller_blockers_bounded_exact_return_handoff_ja_20260831035609.md`
4. `docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md`
5. `docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md`

Digest：

```text
Controller Review
124db30e3185e8c1d550b7063263b21760b97aa805f20d1b2434977cf71bfe19920d0b05486a81c5ec67123dd647ae22c0dff9f01570837ac725187c21925c60

P8-RW6 Return
3f3f8ceb204e1cc6ecb226df2b04a546cc1e78bd6ccbbca9977e925ad86310bd2de54f74fff2db088e32561702b9bb74cd0804b35c43ca9743f6623c769f750b

Phase 8 Requirements
e658a5f5fda55590e3875987f1622be3e91c415a8c881dc4f1c5266f53aee7017973669dd3b3a6e0305766238566b297d76c56adf444301e78334aadbea0a1ca

Phase 8 Acceptance Matrix
40ebe8449d880fd00f98b3633825756a4e23d1edea8efbdac437be0ad718e6b6a0c04776f1907089cde23b057087ba3c3275ba68727d116bec2baee682bd1a34
```

## 3. Preserved Baseline／Forbidden Scope

次を再実装、Rollbackまたは便乗修正しない。

- P8-A〜F、P8-CR0〜5、P8-RW6-A〜C。
- Manual URL、Archive管理、Branch非表示、Dev Agent Run／Budget／Completion Gate。
- Production Constitution Active ModeのOFF固定。
- P8-CODEX-009／010／011、P8-ACC-038。
- Phase 6／7の既知Debt。
- General Web Search、Production Enforcement Engine、GD接続、Semantic Runtime、Level 1完成、Real MCP。
- Phase 8 Closure、Roadmap、Git、Backup、Phase 9。

## 4. Frozen Preview Semantics

同一Manifest／同一Capability Viewを、Production Activationなしで3 Mode比較する現在構造を維持する。
Current ManifestのRuleを虚偽に`observed`／`enforced`へ昇格させない。現在未対応のRuleは引き続き
`unsupported_action`でよい。

その上で、各`ConstitutionModePreviewEntry`へ少なくとも次の3軸を明示する。

```text
evaluation_disposition
action_permission
violation_presentation
```

最低限の意味を次で固定する。Field名またはEnum名は既存命名へ合わせてよいが、意味を変えない。

```text
OFF
  evaluation_disposition: not_evaluated
  action_permission: no_constitution_action
  violation_presentation: not_evaluated

OBSERVE
  evaluation_disposition: evaluate_record_only
  action_permission: no_block_no_authority_change
  violation_presentation: observation_only_or_typed_unsupported

ENFORCE
  evaluation_disposition: evaluate_and_apply_supported_action
  action_permission: supported_actions_only_no_authority_expansion
  violation_presentation: enforced_or_typed_unsupported
```

重要事項：

- `action_permission`はProvider／Platform／User Authorityを追加しない。
- Previewは実Action、Tool実行、Model Injection、NetworkまたはMode変更を起こさない。
- 未対応Ruleに対し、ENFORCEだから実際にBlockしたというClaimを作らない。
- Rule別`ConstitutionDecision.reason`を保持する。
- Frontendでは3軸のLabel／Valueを日本語／英語で読める形にし、Outcomeだけの列挙で終わらせない。
- Preview Disclaimerと`active_production_mode=off`を維持する。

## 5. Work Packages

### P8-RW7-0 — Entry／Scope Freeze

- Mandatory Reading Digestを照合する。
- Current Working Treeを正本とし、Fresh Bootstrapしない。
- P8-CODEX-012だけをOpen Findingとして固定する。

### P8-RW7-A — Backend Preview Contract／Projection

- Preview専用Contractへ3軸を追加する。
- OFF／OBSERVE／ENFORCEのMode SemanticsをPure／Deterministicに解決する。
- Existing Rule Decision、Revision、Digest、Viewを保持する。
- `/api/v2/constitution/preview`へ損失なくProjectionする。
- Production Active Modeを変更しない。

### P8-RW7-B — Frontend Presentation／Regression

- 各View／ModeについてDecision、Action Permission、Violation Presentationを表示する。
- Label／Valueは日本語／英語に対応する。
- Current ManifestのOBSERVE／ENFORCEが`unsupported_action`である事実を隠さない。
- Preview／Active Runtimeの区別を維持する。
- Focused Backend／Frontend Testを追加する。

### P8-RW7-C — Verification／Internal Review／Return

- Focused Testを実行する。
- Backend Full、Mypy、Ruffを実行する。
- Frontend Test、Typecheck、Lint、Buildを実行する。
- P8-ACC-021をSource／Test／UI Evidenceから再導出する。
- Requirement、Negative Path、Composition、Persistence非影響、UI Claim、Acceptanceの6観点でInternal Reviewを1 Cycle行う。
- Critical／Major／MVP Blockerが出た場合だけ本Scope内でReworkする。
- Minor／Hardening／別Phase事項は未解決へ送り、全体停止しない。
- Recovery IndexとExact Return Handoffを作る。

## 6. Required Tests

少なくとも次を実証する。

1. Actual Manifestの全ViewにOFF／OBSERVE／ENFORCEがある。
2. 3 Modeそれぞれが3軸を持ち、Mode Semanticsが指定値へ収束する。
3. Current unsupported RuleはOBSERVE／ENFORCEとも`unsupported_action`のままである。
4. Preview前後でProduction Active ModeはOFFのままである。
5. Preview呼出しによるTool、Network、Model、External Actionは0。
6. Frontendに3軸とPreview Disclaimerが表示される。
7. 日本語／英語Presentationが成立する。
8. Existing Constitution Runtime／Manifest／Digest TestにRegression 0。

## 7. Verification Interpretation

Codex Network制限環境では、既知P8-CODEX-010によりBackend Fullが次の3件だけFailする。

```text
tests/unit/conversation/test_conversation_generation.py
  test_manual_web_evidence_is_injected_as_an_untrusted_tool_message
  test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn
  test_guardrail_context_source_hook_also_governs_manual_web_evidence
```

Claude環境で2124件が通る場合はその事実を記録してよいが、非Hermetic Debtが消えたとはClaimしない。
この3件だけを理由にP8-RW7を停止しない。本Taskで修正もしない。

## 8. Authority／Continuation

許可：

- Project Root内の必要なSource／Test／Frontend／Docs Mutation。
- Project Root内のTest／Typecheck／Lint／Build Command。
- Recovery Index／Exact Return Handoff作成。

禁止：

- Git Read／Write、Commit、Push。
- Network、Install、Real Browser、Real Model、Real MCP。
- User `runtime_data/`へのAction。
- Project Root外へのRead／Write／Redirect。
- Phase 8 Closure、Roadmap、Backup、Phase 9。

実装規模、Frontend変更、Pending Controller Review、Known P8-CODEX-010またはMinor Findingを理由に停止しない。
Resource Hard Stop、Project Root境界違反、Canonical Stateの回復不能な競合など既存True Stop Conditionだけで停止する。

## 9. Return Condition

次を満たしたら停止する。

```text
P8-CODEX-012 disposition
P8-ACC-021 disposition and exact evidence
Changed Paths
Focused／Canonical Verification
Known P8-CODEX-010 separation
Internal Review Finding Ledger
Recovery Index Path
Exact Return Handoff Path
Maximum Claim
```

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL`である。Final Acceptance、Phase 8 ClosureまたはPhase 9開始をClaimしない。
