# Phase 9-1 Claude Package 1 Integrated Instruction

```yaml
document_id: phase_9_1_claude_package_1_lightweight_independent_judge_integrated_instruction_20260902121740
document_type: executable_integrated_instruction
document_state: ready_not_started
language: ja
created_at: 2026-09-02 12:17:40 JST
provider: Claude
package: P9-1-JUDGE-PACKAGE-1
```

あなたはMARGPA Runtime LLMの設計者兼実装者役である。

全体計画は二つの連続Packageから成る。Package 1で軽量な独立Judgeを選定・取得し、Package 2で4方式の比較、Judge基盤修復、Judge→Repair→Rejudge、Semantic 109、ARGD／DAGDを含むMain Runtime Governance ENFORCEまで進める。

このTurnではPackage 1だけを実行する。次のExact Handoffを正本として開始する。

`docs/project/phases/phase_9/handoffs/phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_handoff_ja_20260902121740.md`

重要事項：

- Current Working TreeをCanonicalとし、過去Taskを勝手に再開しない。
- Shortlistを比較し、License／公式Source／Local Mac適合性を確認して一つだけ取得する。
- Artifact Rootは既存設定から解決する。既存Modelを削除・上書きしない。
- 軽量JudgeでSeleneを置換・廃止しない。
- Package 2へ入らず、Runtime Load／Inference／Judge修復を行わない。
- Routine Progress、Minor Finding、不確実性または後続Reviewを理由に停止しない。
- Git、Backup、Phase Closure、Phase 9-2、User runtime_dataには触れない。
- 完了時はRecoveryとExact Returnを作り、Artifact Identity、SHA-512、License、Source、Path、未実行事項およびPackage 2 Exact First Actionを返す。

最大Claimは`P9_1_LIGHTWEIGHT_INDEPENDENT_JUDGE_ARTIFACT_ACQUIRED_CANDIDATE_FOR_PACKAGE_2`である。True Stopがない限り、Package 1のReturn条件まで自走すること。

