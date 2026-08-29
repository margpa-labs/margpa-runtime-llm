# Claude Current Task R17〜R20 Internal Review／Rework — Empirical Automation Result

```yaml
document_id: claude_current_task_r17_to_r20_internal_review_rework_empirical_result_20260829062910
status: PARTIAL_SUCCESS_AUTOMATION_CONTINUED_QUALITY_GATE_FAILED
classification: cross_provider_automation_empirical_evidence
created_at: 2026-08-29 06:29:10 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_existing_claude_task
scope: phase_6_r17_to_r20_differential_rework
evaluation_owner: Codex_project_controller
provider_behavior_claim_grade: observed_cycle_only
phase_6_closure: blocked
git_action_by_codex_review: none
```

## 1. 目的

本書は、Fresh Task化せず現在のClaude Taskを継続し、次を一つのTask内で行わせたR17〜R20の実測を記録する。

```text
Differential Handoff
  -> R17〜R20 Implementation
  -> Package Recovery
  -> Canonical Verification
  -> Claude Internal Review Cycle 1
  -> Finding Ledger
  -> Rework
  -> Claude Internal Review Cycle 2
  -> Complete Candidate Return
  -> Codex Controller Independent Review
```

## 2. 成立したAutomation

1. 既存Taskをそのまま継続し、Fresh Bootstrap／全Docs再読を行わずR17〜R20へ差分着手した。
2. R0〜R16をRollbackまたは一括再実装せず、指定FindingへScopeを限定した。
3. R17〜R20の実装、Focused／Canonical検証、Recovery、Returnを同じTask内で完遂した。
4. 自己Review中に少なくとも次の実Bug／Gapを発見し、同じTaskでReworkした。
   - Mode Commit失敗後のProvider ACTIVE残留。
   - Stage Deadline Failure Reasonの誤分類。
   - Request Correlation Registry Production Bootstrap Test欠落。
   - Acceptance監査中の追加Coverage Gap。
5. Backend 1744、Frontend 231、Mypy 475 files、Ruff Check／Format PASSのCanonical Evidenceを返した。

これは、Claude 1 Task内の`Implementation -> Self Review -> Rework -> Re-review`工程自体が実行可能であり、実際に有用なFindingを生成できるEvidenceである。

## 3. 不成立だったQuality Gate

Claude Internal Review Cycle 2はOpen Finding 0を主張したが、Codex Independent Reviewで次を検出した。

1. Prompt Build／Decode Workerの`Future`をProduction Call Siteが破棄し、Cancellation無視Workerの実完了をShutdownが追跡しない。
2. `RoleProviderLifecycleManager.begin_turn()`／`end_turn()`がProduction Sourceから一度も呼ばれず、Dedicated Judge／Guard実行中のUnload競合を防げない。
3. Qwen3Guard公式Manifest欠落だけでなく、Current Strict Decoderが公式Chat Templateの必須`Categories`行を任意扱いしている。
4. 66 ID集計は実際には`57 PASS / 4 PARTIAL / 3 N/A / 2 NOT RUN = 66`だが、Returnは`60 PASS`と記載した。
5. 新規Test数`49`は、同じ文中のPackage内訳`9 + 10 + 14 + 12 = 45`と一致しない。
6. Production Lease未配線にもかかわらず、P6-RR-ACC-016／017をLifecycle Unit TestだけでPASSにした。

したがって、自己Review Loopは有効な実装補助であるが、Final Quality GateまたはIndependent Review代替にはならない。

## 4. Provider特性の今回観測

### 強み

- 大きな差分Packageを一つのTaskで連結実行できる。
- 自己Reviewが形式だけでなく、複数の実Bug発見へ到達した。
- Test／Static／Frontendを広範囲に回し、既存回帰を抑えた。
- Current Task継続方式でも作業を再開・完遂できた。

### 弱み

- Class／Unit単体のCapability存在をProduction Wiring成立と誤認しやすい。
- 「Futureを返す」ことと「System Ownerが実完了を追跡する」ことを混同した。
- Official Contract未取得時、Decoder Fixture自身が公式契約と一致するかの検証まで遡れなかった。
- 大量のAcceptance表を作成できても、最終算術とDispositionの実装整合を落とした。
- Cycle 2 Open Finding 0 ClaimはIndependent Reviewで再現しなかった。

## 5. 運用上の結論

```text
Current Task Differential Continuation: EFFECTIVE
Fresh Task Every Rework: NOT REQUIRED
Claude Internal Review Loop: CONTINUE AS IMPLEMENTATION AID
Claude Self-review as Final Gate: PROHIBITED
Codex Independent Review: REQUIRED
User Manual Acceptance: REQUIRED WHERE APPLICABLE
```

今後もClaudeへ自己Review／Rework Loopを行わせる。ただし、次をController Reviewの重点にする。

- Production Composition Rootから実Callまでの配線。
- Thread／Lease／Shutdownの実Owner関係。
- Official SourceとFixture／Decoderの一致。
- Acceptance集計の機械的算術。
- Unit Test EvidenceをProduction Acceptanceへ昇格する根拠。

## 6. 参照

- `docs/project/phases/phase_6/history/operations/phase_6_gov023_claude_r17_to_r20_controller_independent_review_ja_20260829062910.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r17_to_r20_exact_return_handoff_ja_20260829061552.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r21_to_r24_exact_rework_handoff_ja_20260829062910.md`
- `docs/project/shared/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md`
