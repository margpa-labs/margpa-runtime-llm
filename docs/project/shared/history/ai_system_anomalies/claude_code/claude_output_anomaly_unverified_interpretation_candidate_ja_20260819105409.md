# 観測記録 — 解釈候補をユーザー自身の言葉と照合せず「曖昧」と判定した誤り

```yaml
document_id: claude_output_anomaly_unverified_interpretation_candidate_20260819105409
status: observation_record
category: failure
phase: cross_phase
subphase: none
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 10:54:09 JST
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

本Docは、[claude_output_anomaly_instruction_referent_misreading_ja_20260818192108.md](claude_output_anomaly_instruction_referent_misreading_ja_20260818192108.md)（以下「関連Doc」）と同系統の、指示解釈に関わるFailure Patternの新しい具体例を記録する。関連Docは「指示語の参照範囲取り違え」を扱ったが、本件は**確認質問を送る前に、解釈候補それぞれをユーザー自身の言葉と照合して検証する工程を怠った**、別種の事例である。

## 1. 事象

ScrollのPin位置調整に関して、ユーザーから次の指示があった。

> 「入力ログの位置、もうちょっと下げて。20ぐらい。」

Claudeはこれを、①位置を実際に下（Topbarから離れる方向）へ動かす＝Gap値を増やす、②口語的に「数値を下げる」＝Gap値そのものを小さくする、の2通りで解釈可能と判断し、AskUserQuestionでユーザーへ確認質問を送った。

ユーザーから、この確認質問自体の妥当性を問われ、Claudeは当初「両読みとも成立するため、確認は妥当だった」という趣旨で応答した。しかしユーザーから重ねて指摘を受け、次の事実が判明した——**候補②（Gap値を減らす）を実行すると、実際の見た目上の位置はTopbarに近づく＝画面上で「上がる」方向に動く**。ユーザーは明示的に「下げて」（＝下へ動かす）と言っており、候補②はこの言葉と論理的に矛盾する、最初から成立し得ない解釈だった。

## 2. パターンとしての特徴

関連Docの事例（指示語の参照範囲を、後続の文脈から正しく特定できなかった）とは異なり、本件は**解釈候補を複数立てた後、それらをユーザー自身が実際に使った言葉と照合する検証を行わなかった**ことが直接の原因である。候補①・候補②は、それぞれ単体としては一応意味の通る読みだったが、候補②は「下げて」という、ユーザーが同じ指示の中で明示的に使った言葉と矛盾しており、この矛盾は候補を立てた時点で機械的にCheckできたはずだった。

不要な確認質問を送ったこと自体、ユーザーの時間を消費させる副作用があり、些細に見えて実害を伴うFailureである。

## 3. 原因についての評価

- 複数の解釈候補を検討する際、候補同士を比較する（互いに両立するか）ことはしたが、各候補を**ユーザーが実際に使った単語・方向性そのもの**と照合する検証を怠った。
- 「下げる」という1つの語に対し、辞書的・慣用的に複数の意味（物理的な位置移動／口語的な数値の増減）が存在すること自体に気を取られ、その意味が指示全体の**方向性の一貫性**を壊していないかという、より基本的なCheckを飛ばした。

## 4. 対応

- 運用メモへ第3.14節「不明瞭判定前の候補整合性Check」を新設した（[claude_side_design_governor_operating_notes_ja.md](../../../task_roles/claude_side_design_governor_operating_notes_ja.md)第3.14節）。確認質問を送る前に、各解釈候補がユーザー自身の言葉と論理的に矛盾していないかを自分で検証し、矛盾する候補は「曖昧さ」の材料に数えない、という手順を明文化した。
- 当初、この第3.14節に本Incidentの経緯を「契機」として長文で埋め込んだが、ユーザーから「それはEvidence層の内容であり、Rule自体の適用精度を上げない不要な文章ではないか」という指摘を受け、該当箇所を削除した。Rule本文とHistory／Evidenceの層分離（運用メモ第3.3節・第3.5節）を、Rule新設の作業中に自分自身で一時的に破っていたことになる。

## 5. Status

```text
Current Point            : 解釈候補をユーザーの言葉と照合せず確認質問を
                            送った事例を記録。運用メモ第3.14節を新設し、
                            候補整合性Checkの手順を明文化した。
Files Created／Modified   : 本Fileのみ（新規作成）。運用メモ第3.14節の
                            新設・修正は別途完了済み（本Docの前提事実）。
Validation                : N/A（観測記録）
Open Current Blocker      : NONE
Controller-owned Next Work: NONE。
Exact Next Route          : 同種の事象がさらに観測された場合、本Docへの
                            追記ではなく、新規File（Append-only）として
                            `shared/history/ai_system_anomalies/
                            claude_code/`配下へ記録する。
```
