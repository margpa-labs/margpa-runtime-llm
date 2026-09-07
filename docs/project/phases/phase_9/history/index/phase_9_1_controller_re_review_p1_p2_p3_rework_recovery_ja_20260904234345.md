# Phase 9-1 Controller再Review(22:41版) P1／P2／P3 Rework Recovery

```yaml
document_id: phase_9_1_controller_re_review_p1_p2_p3_rework_recovery_20260904234345
document_state: complete_recovery
language: ja
created_at: 2026-09-04T23:43:45+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-04 22:41:50 JST再Review(CHANGES REQUIRED)への対応として、P1(Rejudge予算整合)／P2(通常ENFORCE保存経路結合Test)／P3(Gemma実機確認とSelene先送り条件)の3項目に着手・完了した。Exact Return Handoffを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- P1: `src/margpa_runtime_llm/bootstrap/repair_live_integration.py`に`_plan_rejudge()`を新設し、RejudgeのToken計画をCancellation有無で単一化。予算不足時は呼出し前Typed Reject(`repair_rejudge_budget_insufficient`)。Test 9件追加・1件書換え、全PASS。
- P2: `tests/unit/bootstrap/test_judge_repair_rejudge_normal_enforce_save_path.py`新規作成。実Production Composition(Conversation→Hook→Repair→Rejudge→同一Turn保存)をFixture Modelで結合検証。2 Test、全PASS。
- P3: Main+Gemma同時Load実機確認(4回)。Native Crash非再現を確認したが、Gemma自身の`evidence_refs` JSON整形欠陥(3/3再現)により「Gemma正常に使える」条件は今回も未成立。Selene延期は不成立のまま。新規実機Test 1件(1 skipped、意図どおり)、新規Unresolved Snapshot 1件(UF-P9-010提案)作成。

## 3. Files Created This Round

- `tests/unit/bootstrap/test_judge_repair_rejudge_normal_enforce_save_path.py`
- `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py`
- `docs/project/shared/history/unresolved_work/phase_9_1_gemma_concurrent_load_no_crash_and_evidence_refs_json_defect_snapshot_ja_20260904233724.md`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_p9_1_controller_re_review_p1_p2_p3_rework_exact_return_ja_20260904234101.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_p9_1_controller_re_review_p1_p2_p3_rework_exact_return_ja_20260904234101.md](../../handoffs/phase_9_claude_p9_1_controller_re_review_p1_p2_p3_rework_exact_return_ja_20260904234101.md)

Maximum Claim: `P9_1_CONTROLLER_RE_REVIEW_P1_P2_REWORK_COMPLETE_P3_PARTIAL_EVIDENCE_ONLY`

## 5. Open Items at This Point

- Selene: 未解決のまま継続(今回新規実機実行なし)。
- Gemma: 新規UF-P9-010提案(`evidence_refs` JSON欠落)、Registry本体未反映(Codex/User判断待ち)。
- Mypy 1 error(`judge_live_integration.py:622`、今回未編集File)、原因未調査。
- Frontend再検証未実施(今回変更なし)。
- 上書き旧Handoff・phase_index_ja.md直接編集の訂正はUser「放置でいい」により既決、変更なし。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手は行わない。
