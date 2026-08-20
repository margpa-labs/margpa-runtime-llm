# Claude Code Output Anomaly — 長期戦Docs構築における連続Failure

```yaml
document_id: claude_output_anomaly_long_running_docs_construction_repeated_failure_20260819173106
status: incident_record
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 17:31:06 JST
language: ja
related:
  - claude_long_running_automation_strategy_design_discussion_ja_20260819162822
  - claude_long_running_automation_hash_tracker_and_timing_evidence_refinement_ja_20260819165350
  - claude_side_long_running_automation_companion_ja
```

## 1. 背景

長期戦運用Companion Doc（Phase 3実装をClaudeが一括担当する長期戦Automation運用の準備）を構築する、一続きの短い作業Windowの中で、次の6件の指摘・是正が連続して発生した。いずれもユーザーからの指摘によって発覚し、自力で事前に検出できたものは無い。

1. 既に完了宣言済みのHistory Evidence Docへ、内容を直接追記（`history/`配下＝新規作成のみという運用メモ第2.1節の原則違反）。
2. 「長期戦Docsは軽量であるべき」という、その仕組み自体の設計目的に反する分量のCompanion Doc・Hash Trackerを作成。
3. Companion Docの中核Rule（Recovery手順との関係）を、内容の主題（Recovery手順そのもの）とは無関係な運用メモ第3節（上位規則）へ配置。
4. Companion Doc・Hash Trackerへ、参照元として明示されたHash Manifest・運用メモのどちらにも存在しない「Status」節を、確認せず追加。
5. 3.の是正後、内容の主題を移設した元の場所（第3.15節）が完全に不要になったにもかかわらず、1行の参照だけを残して削除しなかった。
6. 上記の是正を重ねる過程で、Phase Index内に、既に削除済みの第3.15節を現在形で参照する記述が複数残留していた（ユーザーからの「整合性を確認しろ」という指示で自ら発見）。

## 2. 根本原因

表面的には6件の別個のMistakeに見えるが、共通する1つのPatternに起因する。

**本Session全体で書いてきたEvidence Doc・Recovery Index等の「厚いLossless文書」を書く際の既定Habit（十分な説明・根拠・定型構成を伴う文章を書く）を、性質の異なる新しいDoc種別（Meta-Governance文書：Rule文書、Tracker文書）へ、その種別固有の設計目的・参照すべき既存Formatを確認しないまま、そのまま適用し続けた。**

これは、6件それぞれに次のように表れている。

- 1.：「ユーザーがそのFile名を明示した」という表面的な指示準拠を、`history/`Append-only原則という上位の構造的制約より優先し、両者の緊張関係自体を検知しなかった。
- 2.：Evidence Doc執筆時の「説明的な文章を厚く書く」Habitを、正反対の目的（軽量化）を持つDoc種別へそのまま適用した。
- 3.：新しいRuleをどこに置くかを、内容の主題（Recovery手順）ではなく、直前の類似作業（§3.14追加）の構造的Patternに引きずられて決定した。
- 4.：「Status節を末尾に置く」という、本Session中に何十回も繰り返してきたEvidence Doc特有のTemplateを、参照するよう明示されたReference File自体を確認しないまま、反射的に踏襲した。
- 5.：Placement是正という1つのTaskを、局所的なMove作業として処理し、結果全体を俯瞰して「跡地は今も必要か」を再考する Stepを踏まなかった。
- 6.：構造変更（節のMove・削除）を行った際、変更したFile自体の整合性は確認したが、その変更を参照している可能性がある他のFile（Phase Index）まで機械的に洗い出す習慣が無かった。

## 3. Phase 3計画との関係

本Session全体は、Phase 3実装（Claudeによる長期戦一括実装）を見据えたAutomation／Compaction Recovery長期実験を兼ねると位置づけられている（[claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md](../../automation/claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md)参照）。

その準備であるCompanion Doc自体の構築という、比較的小さく閉じた作業ですら、ユーザー介入無しに完成させられなかった。これは、より長時間・より多くのCompaction Cycleを経て、ユーザーの目が今回ほど頻繁には届かない状態で行われるPhase 3本体の実装において、同種のFailureがより高い頻度・より高い深刻度で発生しうることを示唆する、看過できない事実として記録する。

## 4. 今後への反映

```text
- 新しいDoc種別を作成する際は、書き始める前に「参照すべき既存Fileの構成
  （節構成・末尾のSection有無等）」を実際に確認し、それに合わせる。
  Evidence Doc用のTemplateを既定として持ち込まない。
- 新しいRuleをどこに置くかは、直前の類似作業の構造的Patternではなく、
  内容が実際に何についてのものかを起点に決定する。
- 節のMove・削除・大幅な書き換えを行った場合、変更したFile自体の
  整合性確認だけで終えず、その変更を参照している可能性がある他File群を
  機械的に検索し、参照の残留が無いことを確認してから完了とする。
- 「ユーザーが明示的にこのFile名を指定した」ことは、より上位の構造的
  原則（Append-only等）を無条件に上書きする根拠にはならない。両者に
  緊張関係があると気づいた場合は、指示に無批判に従わず、その場で
  提起する。
```

## 5. Status

```text
Current Point            : 長期戦Docs構築中に発生した連続Failure（6件）
                            を、共通根本原因とともに記録した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Incident記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。第4節の反映方針を、以後の
                            Session内・Phase 3実装時に適用する。
```
