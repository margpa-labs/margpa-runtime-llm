# Phase 10予約 — 右側検証パネルのUIイメージ・修正方針

```yaml
document_id: phase_10_right_panel_ui_concept_consolidation_reservation_20260904190434
document_type: planned_work_ui_concept_reservation
document_state: concept_recorded_requirements_pending
language: ja
recorded_at: 2026-09-04 19:04:34 JST
decision_authority: user
authority_owner: Nazuna Research
target_phase: phase_10_late_ui_consolidation
project_stage: individual_r_and_d_mvp_portfolio
implementation_authorized: false
append_only: true
```

## 1. 位置付けと参考画像

中央を会話、右側を「選択した回答の処理・根拠・出力を確認する場所」に分ける。提示画像の方向性を採り、下記の修正点をPhase 10の再要件定義へ引き継ぐ。画像そのものを仕様・実装済み機能の証明にはしない。

- [イメージ1：Trace](../../../../../assets/images/margpa_runtime_llm_mvp_ui_concept_1.png)
- [イメージ2：Evidence](../../../../../assets/images/margpa_runtime_llm_mvp_ui_concept_2.png)
- [イメージ3：Outputs](../../../../../assets/images/margpa_runtime_llm_mvp_ui_concept_3.png)

対象は右パネル。画像内のSidebar、Account、添付、評価ボタン等を今回まとめて実装する決定ではない。サンプルのModel名、日時、件数、Phase名、本文も実績・固定値として採用しない。画像ファイルと既存Historyは変更せず、本書を補足として追加する。

## 2. 基本構成

| 場所 | 役割 |
|---|---|
| 中央の回答 | 読む・会話を続ける。短い参照Chipや検証パネルへの入口を置く |
| 右パネル共通部 | 対象の回答／Turnと、その実行時の構成・状態を示す |
| Trace | 何が実行され、どこで判定・修復・停止したかを確認する |
| Evidence | どの資料を参照したか、その出所と回答との対応を確認する |
| Outputs | 初回候補、修復候補、最終的に提示された回答を比較する |

`Trace / Evidence / Outputs`の3タブを基本案とする。日本語の補助ラベル、詳細な配置・表示項目は着手時に決める。

## 3. 共通部 — 「いまの設定」と「この回答の実行」を混ぜない

- 画像の`Main Governance`カードは、案として「このTurnの実行構成」へ変更する。
- Main Model、Main Runtime Governance、Judge、Guard、Runtime Constitution、Repair等を別の役割として並べる。Judge／Guard／ConstitutionがMain Governanceの配下にあるように見せない。
- Main Runtime GovernanceのModeとConstitutionのModeを一つの`Constitution Mode`で代用しない。表示するModel／Modeは実際の構成から取得し、Selene固定などにしない。
- パネルは選択した回答に紐付ける。過去回答には当時の設定・記録を表示し、後から変えた現在設定で上書きしない。
- `Live`は対象が実行中の時だけ使用する。完了・過去・失敗・停止済みを区別し、別Turnの進行状況を混在させない。
- 設定されたProvider、利用可能なProvider、実際に処理したProviderは意味が違う。表示元がある範囲で区別し、単なる`active`から推論成功を導かない。
- 記録なし・取得失敗・未実装と、実行なし・成功を区別する。値がない時に成功やゼロを補完しない。

## 4. Trace — 固定の「全段階Passed」をやめる

- 画像の一直線の処理順は説明用イメージ。実際のイベント順・分岐・繰り返しを表示する。RAGやJudgeの省略、複数地点のGuard、Repair→Rejudgeも扱える構成を候補とする。
- 「処理が完了した」と「評価に合格した」は別表示にする。RAGの取得完了を資料の正しさ、Judgeの処理完了を回答の合格として扱わない。
- 実行中／完了／失敗／停止／未実行と、合格／逸脱／不明／未評価などの評価結果を混同しない。名称とBackend状態の対応は再要件定義で確認する。
- 通常は短い要約を見せ、展開すると既存記録の理由・時刻・件数等を確認できる形にする。数値・所要時間は取得できる記録だけを表示する。
- Raw／Final本文をTrace内で重複展開しない。ここには結果の要約とOutputsへの入口を置く。

## 5. Evidence — 出所と信頼度を取り違えない

- RAG専用にせず、Project Docs、Local Corpus、Web等の対応済みSourceを共通の枠組みで整理する。未対応Sourceの実装を画像から追加しない。
- 画像の`Primary / Secondary`は意味が曖昧なため、そのまま採用しない。検索順位、参照順、一次資料かどうか、Source Authorityは別概念として扱う。
- 一覧はTitle・Source種別・短い抜粋を中心にし、Path／URL、Heading、Revision、Digest等の詳細は展開する。保有していない項目は作らない。
- 回答の参照Chipから該当資料を選択できる構成とし、検索で取得した資料と回答との対応は記録で裏付けられる範囲だけ示す。
- 過去回答の参照は当時のRevision／Digestを保持する。外部ContentがInstruction Authorityを持つかのような表示にしない。
- パネルへ移動しても、既存のCitation、Copy、Sourceへの導線、保存済みEvidenceを失わない。

## 6. Outputs — 重複表示より比較を中心にする

- 「初回候補」「修復候補（存在する時）」「最終提示結果」を区別する。元の候補とFallbackを同じ成功回答として扱わない。
- 全文を小さい文字で縦に重ねず、切替・差分・個別展開を候補にする。同一内容なら「変更なし」と分かる形にする。
- `Structured Output`は実際の出力形式と単なるメタ情報を区別する。画像の分類・Token数などを推測で埋めない。
- `Applied Transformations`は実行記録がある処理だけを表示する。文章が整っていることから「正規化済み」「冗長表現を削除済み」等を逆算しない。Guardの評価と文章の変換も区別する。
- 拒否・非提示となった候補の閲覧可否は既存の権限・提示方針と照合する。Outputsタブを追加するだけで非提示方針を迂回する許可にはしない。

## 7. 読みやすさとMVP境界

右パネルの幅調整、折り畳み、長文の拡大表示を候補とする。狭い画面でも会話本文を潰さず、通常は要約、必要時だけ詳細を開く。実際の文量・失敗例・長い日本語でも確認する。

着手時は、①既存の表示・記録を整理する項目、②既存データのUIへの接続が必要な項目、③新たな内部計測が必要な項目に分け、工程・工数を決める。①ですべて作れると決め付けず、③を一括でPhase 10の必須条件にも追加しない。

[内部Observability予約](phase_9_1_post_manual_internal_observability_judge_lifecycle_selene_and_lightweight_judge_reservation_ja_20260901180418.md)のCall 0、Worker Drain、Late Publish、Exactly-once、詳細Artifact Identity等は、実装時期未定のまま保持する。必要な一部を採用する場合は再要件定義で合意する。画面・手順が用意されていない内部項目を実画面テストとして要求しない。

本書は[Phase 10後半UI／Citation再編予約 §5.7–5.8](phase_9_10_11_docs_constitution_padg_ui_web_and_no_hit_lossless_restructure_reservation_ja_20260830170415.md)の具体化メモ。既定のPhase順序、技術Contract、MVP優先方針を変更しない。[Governance／Constitutionの構造制御・意味評価分離](phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_ja_20260904172003.md)はPhase 11以降のままとする。

## 8. Advanced Judge／Repair Budget設定の追加予約 — 2026-09-05

[Advanced Judge／Repair Budget設定予約](phase_10_plus_advanced_judge_repair_budget_controls_reservation_ja_20260905092958.md)を追加する。SettingsのAdvanced側でToken／Criterionと総Repair Budgetを扱い、右側検証パネルには対象TurnのFrozen実効値をRead-only表示する案。既存設定系の再利用で軽く済む場合だけPhase 10へ含め、Runtime Contract・保存・Evidenceへ広い変更が必要なら後続へ送る。Phase 10のMVP UIを遅らせる必須条件にはしない。
