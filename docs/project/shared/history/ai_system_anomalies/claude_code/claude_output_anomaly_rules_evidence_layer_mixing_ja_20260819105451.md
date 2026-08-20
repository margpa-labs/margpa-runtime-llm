# 観測記録 — 新規Rule追加時に、Evidence層の内容をRule本文へ混入させた誤り

```yaml
document_id: claude_output_anomaly_rules_evidence_layer_mixing_20260819105451
status: observation_record
category: failure
phase: cross_phase
subphase: none
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 10:54:51 JST
language: ja
authorization: |
  ユーザー指示（2026-08-19）：「あと、これら完全にFailureだから、
  そっちにもdocs作っとけ」。
  [claude_output_anomaly_instruction_referent_misreading_ja_20260818192108.md]
  第5節「同種の事象がさらに観測された場合、本Docへの追記ではなく、
  新規File（Append-only）として記録する」に基づき、新規本Docを作成する。
created: Claude Code
```

## 0. 位置づけ

本Docは、[claude_output_anomaly_unverified_interpretation_candidate_ja_20260819105409.md](claude_output_anomaly_unverified_interpretation_candidate_ja_20260819105409.md)（以下「関連Doc」）と同一のUser Feedback Cycleの中で発生した、しかし**別種のFailure**を記録する。関連Docは指示解釈の誤りを扱ったが、本件は、その誤りを踏まえて運用メモへRuleを新設する際に、**運用メモ自身が定めるDocs層分離の原則（第3.3節・第3.5節）を、その場で自分自身が破った**事例である。

## 1. 事象

関連Docの事象を受け、ユーザーから「じゃそれ上位ルールに追加しろ」と指示され、運用メモ第3.14節「不明瞭判定前の候補整合性Check」を新設した。その際、Rule本文の後に、次のような長い「契機」段落を追記した。

> （本節の直接の契機：ユーザー指示「入力ログの位置、もうちょっと下げて」に対し、「下げる」を①位置を実際に下へ動かす（Gap値を増やす）と、②口語的にGap値そのものを小さくする、の2通りで曖昧と判断し確認質問を行った。しかし②はGap値を減らすと位置が実際には上へ動く（Topbarに近づく）ため、「下げて」という明示的な言葉と論理的に矛盾しており、最初から候補になり得なかった。（後略）

ユーザーから、「それはEvidenceだろう。それを付けてRuleの適用精度が上がるのか。上がらないなら余計な文章を入れるな」という趣旨の指摘を受けた。指摘の通り、この段落はIncidentの経緯そのもの（Evidence層の内容）であり、Rule適用時の判断精度には寄与しない。該当段落を削除し、Rule本文（2段落）のみを残した。

## 2. パターンとしての特徴

運用メモ自身が、第3.3節（Docs Layer分離の3層モデル）・第3.5節（Operating Notesの保持範囲限定：「作業状態・予約事項・実験結果・Incident履歴・変更履歴は一切保持しない」）で明確に定めている原則に、Rule新設という同一の作業の中で自分自身が違反した。しかも、直前の第3.13節（Compaction Recovery Hash記録の分離）では、同種の背景説明を「4回目のDrillで実際に発生。詳細は…Evidence Doc参照」という**1文の参照Pointerのみ**に留める、正しい書き方を既に実践していたにもかかわらず、直後の第3.14節で同じ判断ができなかった。

## 3. 原因についての評価

- Rule単体を読んだ第三者が背景を理解しやすいようにという意図が先行し、「Rule本文に何を書くべきか」という判断基準（適用精度に寄与するか）ではなく、「読み手の理解を助けるか」という別の基準で内容を選んでしまった。
- 直前の第3.13節で自分自身が使った、Evidence参照は最小限のPointerに留めるという書き方を、直後の第3.14節作成時に踏襲しなかった——同一Session・同一File内での自己の直近の実例からも学習できていなかった。

## 4. 対応

- 運用メモ第3.14節から該当段落を削除した（Snapshot退避→編集→Diff照合・Link／文字化けCheck、いずれも完了）。
- 教訓として、Ruleを新設・改訂する際は、追記しようとしている一文一文について「これはRule適用時の判断精度に寄与するか、それとも単なる経緯説明（Evidence層の内容）か」を都度自問し、後者であれば、Rule本文には書かず、最小限の参照Pointer（第3.13節のような1文）に留めるか、Rule本文には一切含めない。

## 5. Status

```text
Current Point            : Rule新設時にEvidence層の内容を混入させた事例
                            を記録。運用メモ第3.14節から該当段落を削除
                            済み。
Files Created／Modified   : 本Fileのみ（新規作成）。運用メモ第3.14節の
                            修正は別途完了済み（本Docの前提事実）。
Validation                : N/A（観測記録）
Open Current Blocker      : NONE
Controller-owned Next Work: NONE。
Exact Next Route          : 同種の事象がさらに観測された場合、本Docへの
                            追記ではなく、新規File（Append-only）として
                            `shared/history/ai_system_anomalies/
                            claude_code/`配下へ記録する。
```
