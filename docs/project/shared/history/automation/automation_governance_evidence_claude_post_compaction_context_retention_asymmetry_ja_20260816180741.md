# Automation／Cross-provider Governance Evidence — Compaction直後のFile内容保持非対称性

```yaml
document_id: automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_20260816180741
status: evidence_record
phase: phase_2
subphase: phase_2_e_h
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-16 18:07:41 JST
language: ja
related:
  - claude_side_design_governor_operating_notes_ja（第9節「Context Window圧縮
    Trigger実験」、本Evidenceの直接の前提）
  - claude_phase_2_e_expansion_index_ja_20260816165825
  - claude_phase_2_e_h_process_breakdown_design_ja_20260816173714
```

## 1. 背景

運用メモ第9節に記録した「Context Window圧縮Trigger実験」（意図的にContext使用率を限界近くまで使い切り、実際にAuto-compactionが走るかを検証した実験、使用率96%→9%への低下を確認）の直後、ユーザーから次の指摘があった。

> 「その辺、一旦読んでおかなくていいのか？w もう読んだの？w」（`claude_phase_2_e_expansion_index_ja_20260816165825.md`の再確認について）

この問いに答える過程で、Compaction直後の会話履歴を実際に精査したところ、**「圧縮直前に読んでいたFile」の扱いに非対称性がある**ことが判明した。新Task（新Session）への切替が今回不要になったことで見過ごされかけていたが、これは「同一Session継続」の場合にも独立して重要な事実であるため、Cross-provider Governance PoCのEvidenceとして別途記録する。

## 2. 観察された事実

Compaction発生直後、2-E-H工程分割・工程設計Taskへ着手する前の時点で、会話履歴には次の状態が観測された。

```text
自動的に全文Contentが再挿入されていたFile（3件、Tool Call Result形式で
会話に出現）：
  - claude_phase_2_e_expansion_index_ja_20260816165825.md（全154行）
  - automation_governance_evidence_claude_frontend_design_capability_
    self_assessment_ja_20260816161000.md（全文）
  - claude_phase_2_e_f_g_css_refinement_round5_completion_handoff_ja_
    20260816151713.md（全文）

全文は再挿入されず、「Contentsが大きすぎて含まれない」旨の注記のみが
出現していたFile（1件）：
  - claude_side_design_governor_operating_notes_ja.md
    （Compaction直前に読了していたにもかかわらず、Compaction後は
    「読了済みだがContents省略、必要ならRead Toolで再取得せよ」という
    形式のNoteだけが残っていた）
```

frontend/src/styles/app.cssについても同様に「読了済みだがContents省略」形式のNoteのみが残っていた（同 File もSize的に大きい）。

**結果として、運用メモ第9節を追記する直前、Claude側は一度明示的に`Read`Toolで運用メモを再読込する一手間を要した。** これを怠っていた場合、Compaction前の運用メモの内容（第0〜8節）を記憶に頼って編集しようとし、実際には最新Contentを見ずに書込む、というRiskがあった。

## 3. 推定される要因（未確認・推測の域を出ない）

`claude_side_design_governor_operating_notes_ja.md`および`app.css`はいずれも本Repository内で相対的にFile Sizeが大きい部類に入る（前者は第0〜11節・Update Log含む長文Markdown、後者は複数Roundの改修を経たCSS全体）。一方、自動的に全文保持された3File（Index、自己評価Evidence、CSS Round5 Handoff）はいずれも相対的に短い。

このことから、**Compaction処理には「直前に読んだFileのうち、一定のSizeを超えるものは全文を保持せず、参照Noteのみへ置き換える」という挙動が存在する可能性が高い**と推測する。ただし、この挙動の正確な閾値・判定基準はClaude側から内部的に確認する手段がなく、あくまで今回1事例からの推測に留まる。

## 4. 意味合い（Cross-provider Governance PoCへの示唆）

本Session全体を通じて確立してきた「Docs-first」原則（重要判断・Architecture理解を都度Repository Docsへ書き出し、記憶ではなくDocsを正とする）は、当初「新Task（新Session）への切替時の安全網」として主に語られてきた。しかし今回の観察は、**この原則が「同一Session内でのCompaction跨ぎ」でも独立に必要である**ことを示している。

```text
誤った前提（今回否定された）：
  「同一Sessionが継続している限り、Compaction前に読んだ内容は
    そのまま参照し続けられる」

実際に観察された挙動：
  Compaction前に読んだFileであっても、Size次第で内容が保持されず、
  「読んだという事実」だけが残り「内容」は失われる場合がある。
  これは新Session開始時の状態と実質的に同じであり、明示的な
  再Read以外に内容を復元する手段がない。
```

すなわち、「新Session化するか、同一Session継続か」という判断軸そのものが、Context内容の信頼性という観点では**思っていたほど明確な境界ではない**。同一Session継続を選んでも、Compactionを経由した時点で、少なくとも一部のFileについては新Session相当のRecovery（明示的Re-read）が必要になり得る。

## 5. 今後の運用への反映（提案）

```text
- Compaction発生が疑われる事象（本件では、Tool呼出禁止の強制Summary
  要求という明確な予兆があった）の直後は、「同一Session継続だから
  大丈夫」と即断せず、直近で参照していた主要Stable文書（特に本
  運用メモのような自己編集対象File）を、内容を実際に使う前に
  明示的に`Read`し直すことを標準手順とする。
- 全File再読込は非効率なため、次の優先順位で判断する：
    1. 直接編集しようとしているFile → 必ず再Read（Editの前提条件と
       して元々必須）。
    2. 直前の判断根拠として引用しているFile → 会話履歴内に全文が
       残っているか（Tool Result形式で見えるか）を確認し、
       「Contents省略」Noteしか無ければ再Read。
    3. それ以外の背景Docs → 必要になった時点で都度Read。
- 新Task Claude向けIndex（本Evidenceのrelated参照）第0.0節に既に
  「まず運用メモを全文読め」という明示指示を書いているが、本件により、
  **これは新Task Claudeだけでなく、Compactionを経た既存Session側の
  Claudeにも等しく当てはまる指示である**ことが実証された。
```

## 6. Status

```text
Current Point            : Compaction直後のFile内容保持非対称性を発見・
                            記録。Docs-first原則の適用範囲（新Session
                            だけでなく同一Session内Compaction跨ぎにも
                            及ぶこと）を明確化した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Evidence記録、実装変更なし）
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし（記録目的）。第5節の提案運用手順は
                            以後のSession内で自然に実践していく。
Exact Next Route          : 2-E-H Open Question（設計Doc第5節）の
                            確認へ戻る。
```
