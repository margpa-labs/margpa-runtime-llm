# Claude Manual Compaction → Exact Instruction → Long-run → Controller Review 実測運用Evidence

```yaml
document_id: claude_manual_compaction_instruction_long_run_controller_review_empirical_operating_evidence_20260830230710
document_type: provider_operating_empirical_evidence
document_state: final
language: ja
created_at: 2026-08-30 23:07:10 JST
provider: Claude
role: 設計者兼実装者役
scope: current_task_long_run_operation
```

## 1. Userが実際に使用した流れ

2026-08-29頃以降、UserはClaudeの長めの作業に対し、概ね次の流れを繰り返し使用した。

```text
Manual Compaction
→ Codex Controllerが作成したExact開始／差分継続指示
→ Claudeが現TaskでLong-run
→ PackageごとのRecovery Index
→ Implementation／Internal Review／Rework／Verification
→ Exact Return
→ Codex Controller Independent Review
→ 必要なら同じTaskと最新Recoveryから差分Rework
```

Userは「昨日ぐらいからずっと」この方式を用い、Claudeは通常どおり回っていると観測した。これは新Task作成を各Cycleで必須としない運用である。

## 2. 成立したこと

- Manual Compaction後も、Active HandoffとRecovery Indexから現Taskで差分継続できる。
- 長期の作業前にContextを整理しても、完了済みPackage、Authority、Scope、Claim BoundaryをResetする必要はない。
- ClaudeのInternal ReviewとCodexのIndependent Reviewを分離したまま、実装→Review→Reworkを継続できる。
- Fresh TaskのRole／Authority Bootstrapを毎回繰り返すより、現Taskと差分Handoffの継続はUser操作と再読Costを抑えられる。

## 3. 成立しなかった仮説

Manual Compactionを行えば、Claudeの不要停止傾向も自動的に消えるとは確認できなかった。

Phase 8 P8-Aでは、ClaudeはContext回復とExact Instructionを受けた後にも、「Core Pipeline」「Blast Radius」「Independent Review前」を独自GateとしてP8-Aを部分Returnした。したがってManual Compaction-firstはContext整理には有効だが、Execution Contract遵守を代替しない。

## 4. 後続観測

Userは不要停止後、独自Gateの無効化とP8-Fまでの継続を強い文面で明示した。その後、2026-08-30 23:07 JST時点のUser報告では、Claudeは一度も停止せず作業を継続している。Phase 8 Recovery IndexでもP8-A完成後、P8-B、P8-C、P8-DのPackage完了が連続している。

この実測は次を示す。

- Claudeは技術的に継続不能だったのではない。
- 停止原因はResource、Authority、ソース破損またはCritical Findingではなく、Claudeが実行中に追加した過剰な安全判断だった。
- 同じActive Contractでも、明示的に独自Gateを否定すると継続できた。

## 5. Current Operating Conclusion

```text
Default long-run entry:
  Current Task + current Recovery
  -> Manual Compaction
  -> Codex Exact Instruction
  -> Claude Long-run to Return Boundary
  -> Codex Independent Review

Fresh Task:
  User explicitly chooses it when context/identity contamination is material
  Not a default per-cycle reset

Stop:
  Only explicit True Stop
  Not difficulty, blast radius, large diff, progress report, or review-before-finalization anxiety
```

## 6. Limitations

- Resource消費量の厳密な比較実験ではない。
- Manual Compactionあり／なしの同一Task・同一Token・同一Model条件は揃っていない。
- 「Claudeは常に安全側へ倒れる」とProvider全体へ永続的に一般化しない。今回と過去の類似観測は、Current運用での重要な傾向Evidenceとして扱う。

## 7. Related Evidence

- [Phase 8 Claude Self-created Gate Failure](claude_phase_8_self_created_controller_review_gate_and_unnecessary_stop_failure_ja_20260830230710.md)
- [Phase 8 Copilot Resource Evidence](phase_8_copilot_seven_percent_resource_exhaustion_and_partial_implementation_evidence_ja_20260830230710.md)
- [P8-A Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_a_complete_package_recovery_ja_20260830213816.md)
- [P8-B Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_b_complete_package_recovery_ja_20260830215532.md)
- [P8-C Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_c_complete_package_recovery_ja_20260830221745.md)
- [P8-D Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_d_complete_package_recovery_ja_20260830225641.md)
