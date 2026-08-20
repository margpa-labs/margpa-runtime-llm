# Claude Phase 2-E-I I-6：Context Usage Gauge Follow-up（実Browser確認指摘の対応）

```yaml
document_id: claude_phase_2_e_i_i6_context_usage_gauge_followup_design_20260818223456
status: design_confirmed
phase: phase_2
subphase: phase_2_e_i
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-18 22:34:56 JST
language: ja
authorization: |
  2-E-I（I-1〜I-5）完了後、ユーザーによる実Browser確認で5件の指摘が
  あった。その後のChatでの遣り取りにより、対応方針・Scopeが確定した。
  ユーザー指示：「まず docs/ 3つ作って。1: 今の要件とかの話しをdocに。
  I-6か？」。番号は、2-E-I内の工程（I-1〜I-5）に続く形で「I-6」とする。
  実装は未着手——本Docは要件記録のみ。
created: Claude Code
```

## 0. 位置づけ

2-E-I（I-1〜I-5）は完了済みだが、実Browser・実Model確認の後に、ユーザーから5件の指摘があった。Chatでの遣り取りを通じ、5件それぞれの対応方針（今回実装する／保留にする／別件として調査する）が確定した。本Docは、その確定した要件を記録する。実装は本Doc作成時点で未着手。

## 1. 実Browser確認で見つかった指摘（5件、原文の番号のまま）

1. 別Chatを選択すると、右下のGaugeが「未取得」表示に戻る（初期化される）。
2. Panelを閉じる際、Hover Messageが出ない。
3. Panel外をClickしても閉じない（現状、Icon自体をClickするしか閉じる方法がない）。
4. Context使用率Injection Toggleが**OFF**の状態で「今コンテキストどれぐらい？」と尋ねたところ、LLM内部の思考過程・メタ会話のような、通常このModelでは見たことのない出力が返ってきた。
5. （別件）Chat Optionの「再開」が、再開済み状態でも表示され続けるようになっている。以前は消えていた。

## 2. 各指摘への対応方針（確定）

```text
#1 別Chat選択でGauge初期化
   【方針】I-6のScopeには含めない（保留）。
   【理由】現在の設計（Turn完了時のSSEのみでClient State更新、DB保存
   ・専用取得API無し）のもとでは、会話を開き直した瞬間に数値を出す
   には、①オンデマンドで使用率を再計算する新規Endpoint追加（中規模）
   か、②Turnごとに使用率をDB永続化（Migration込みでさらに大きい）の
   いずれかが必要——ユーザー評価「けっこう戦いそうだな」。
   【代替対応】第2.2節「新規Toggle追加」を参照。

#2 Panel閉じる時にHover Messageが出ない
   【方針】I-6のScopeに含める。修正する。
   【原因】ContextUsageGauge.tsx実装時、Panel展開中はTooltip自体を
   意図的に非表示にしていた（Panel見出しとの重複を避ける意図）。
   これにより、Hoverで常に「表示／非表示」切替文言が出る、という
   本来の設計（2-E-I Mission第1節）を満たせていなかった。

#3 Panel外Clickで閉じない
   【方針】I-6のScopeに含める。実装する。
   【方式】SettingsModalのBackdrop Click Pattern（
   `.settings-modal-backdrop`のonClickでevent.target ===
   event.currentTargetを確認して閉じる）を踏襲する。

#4 Toggle OFF状態での思考過程混入
   【方針】I-6のScopeには含めない。原因未特定のまま、別件Trackとして
   保留する。
   【経緯】Claude側は当初「Model自体の応答Style（Qwenが長めの前置きを
   しがち）」という仮説を提示したが、ユーザーから明確に否定された
   （「よくどこの会社もあるLLM内部のやつをログっぽくしたこんな思考
   過程みたいな、メタ会話みたいなん見た事ないわ。このLLMでは。」）。
   Context使用率Injection機能（本Sub-phaseの対象機能）とは無関係な
   はずである（Toggle OFF時はInjection Logic自体が発火しない）。原因は
   完全に未特定であり、本Docの実装Scopeには含めない。

#5 「再開」Optionの表示不具合
   【方針】I-6のScopeに含める。原因調査・修正する。
   【経緯】2-E-Iの変更範囲（Composer・ContextUsageGauge・Settings
   Panel・関連App.tsx State）とは無関係な箇所（Sidebar／ChatListItemの
   表示制御）と推定される。ユーザー推測：「reactに使ってUI変えた
   あたり」（2-E-E〜G、React／Vite移行期）が原因の可能性——ただし
   未確認。

## 3. 新規機能：Context表示 ON/OFF Toggle

#1の保留に伴う代替対応として、新規Toggleを追加する。

```text
配置        : 基本設定（Settings ModalのAdvancedではない方、
              SettingsPanel）の末尾。
Label       : 「コンテキスト表示」ON/OFF。
既定値      : OFF。
効果        : ONの時のみ、ComposerにContextUsageGauge（丸Icon＋
              Breakdown Panel）を表示する。OFFの時はGauge自体を
              Composerから完全に非表示にする（既存の「LLMへContext
              使用率を伝える」Toggle＝Prompt Injection制御とは別の、
              独立したFrontend表示専用Toggleである）。
既定OFFの理由: #1（会話切替でGaugeがリセットされる挙動）が未解決の
              まま残るため、既定では機能自体を見せない状態で提供し、
              希望するユーザーだけが有効化できるようにする。
```

## 4. Status

```text
Current Point            : 実Browser確認で見つかった5件の指摘のうち、
                            #2・#3・#5を修正対象、新規Toggle追加を
                            機能追加対象として確定。#1は保留（代替
                            Toggleで緩和）、#4は原因未特定のため
                            Scope外として、要件を確定した。実装は
                            本Doc作成時点で未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。実装Fileは無変更。
Validation                : N/A（要件記録Doc）
Open Current Blocker      : NONE（技術的Blockerではない）。
Controller-owned Next Work: ユーザーからの実装開始指示を待って、#2・
                            #3の修正、新規Toggle追加、#5の原因調査・
                            修正に着手する。
Exact Next Route          : 本Session内、Manual Compaction実施後、
                            ユーザーの実装開始指示を待つ。
```
