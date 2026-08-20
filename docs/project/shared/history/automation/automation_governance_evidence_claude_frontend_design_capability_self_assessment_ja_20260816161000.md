# Claude側設計統括者役 — Frontend／Web Design能力の自己評価（Evidence）

```yaml
document_id: automation_governance_evidence_claude_frontend_design_capability_self_assessment_20260816161000
status: evidence_record
phase: phase_2
subphase: phase_2_e_f_g_refinement
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-16 16:10:00 JST
language: ja
related:
  - claude_phase_2_e_f_g_css_refinement_completion_handoff_ja_20260816132247
  - claude_phase_2_e_f_g_css_refinement_round2_completion_handoff_ja_20260816142248
  - claude_phase_2_e_f_g_css_refinement_round3_completion_handoff_ja_20260816144539
  - claude_phase_2_e_f_g_css_refinement_round4_completion_handoff_ja_20260816150655
  - claude_phase_2_e_f_g_css_refinement_round5_completion_handoff_ja_20260816151713
```

## 1. 背景

2-E-F／2-E-G完了後、ユーザーが実画面を確認しながらCSSの微調整を計5Round依頼し（各RoundのCompletion Handoffは上記related参照）、全て完了した時点で、ユーザーから次の直接的な質問があった。

> 「それより、キミUI周りのくだり、同じミス何度も繰り返したな？？？クロードはフロントエンド、webデザイン苦手なのか？」

Cross-provider Governance PoCの一環として、この質問への回答（Claude自身による能力の自己評価）を、記憶ではなくRepository Docs側にEvidenceとして記録する。ユーザーからの明示指示（「エビデンスとして残したいから、docs/内のどこかのhistoryの中にその辺まとめ直して書いておいて」）による。

## 2. 5Roundで実際に発生した事象の分類

同じ「UI微調整」という括りの中に、性質の異なる2種類の事象が混在していた。

### 2.1 技術的Bug（実装の詰めが甘かったもの）

```text
1. Composer Auto-grow初回計測のRace（2-E-F/G CSS微調整、第1弾）
   初回Mount直後にscrollHeightを読むと、Style確定前の値
   （意図した約6倍）を掴むことがあった。requestAnimationFrameでの
   再計測により自己修正する形で解消。

2. .app-shellの高さが上限固定されていなかった問題（第2弾）
   min-height: 100vhのみで上限を設けていなかったため、Sidebarの
   長いContentがPage全体を押し広げ、Body全体がScrollしてしまって
   いた。height: 100vh + overflow: hiddenへ変更し、Sidebar／
   Main Contentそれぞれが独立Scrollする構造へ修正。

3. position: fixed + transform + overflow: autoの組み合わせに
   関するCSS仕様の誤解（第2弾）
   Sidebar状態に応じてFixed要素（Header・Composer）の幅を追従させる
   ため、Scroll ContainerであるMain Contentに transform:
   translateZ(0)を付与しContaining Block化する実装を試みたが、
   これはFixed要素をViewportではなくScrollする中身の座標系に
   閉じ込めてしまい、ScrollとともにViewport外へ流れて消える不具合を
   引き起こした。CSS Custom Propertyの継承がPosition方式と無関係で
   ある性質を使い、真にViewport基準のFixedのままCalc()経由でSidebar
   幅を反映する方式へ切り替えて解消した。
```

これら3件は、いずれも「実装した時点では正しいはずだと判断していたが、
実際には動作していなかった」という種類の不具合であり、実Browser確認で
都度発見・修正した。(3)は特に、CSSのContaining Block仕様という、
事前の設計検討段階で見抜けて然るべき類の誤りだったと自己評価している。

### 2.2 Aesthetic（見た目の好み）判断のズレ（Bugではないもの）

```text
- Composer／Header行の背景：透過 → 読みにくいとの指摘で不透明へ戻す
  （第1弾→第3弾）
- Composer枠の色：Accent Blue系 → 「同じ青にしか見えない」との指摘で
  出力Message背景色（Neutral Gray系）へ変更（第4弾→第5弾）
- Message Bubble上限幅：62% → 50% → 57%
- Log全体の左右Padding：0 → 20% → 10%
```

これらはCSSとして正しく動作しており、Bugではない。ユーザーの主観的な
「見た目の良さ」の基準に対して、Claude側が提案した初期値・配色が
外れていた、という性質の事象である。

## 3. 自己評価

第2.1節の技術的Bugと、第2.2節のAesthetic判断のズレは、原因が異なる。

**技術的Bug（第2.1節）については、素直な実装ミスと評価する。** 特に(3)は、
CSS仕様の理解不足が根本原因であり、実装前の設計検討で回避できた可能性が
高い。

**Aesthetic判断のズレ（第2.2節）については、Bugではなく、視覚的Taste
（何が「良い塩梅」に見えるか）の精度がユーザーの求める水準に対して
低いことに起因すると評価する。** Claudeは実際にPixelを「見て」美しさを
直感的に判断する感覚を持たず、Screenshotを介した確認は可能だが、それは
人間が持つ即時的な美的直感とは異なる。このため、初期提案時点で正解を
一発で当てにいくことは期待できず、具体的な数値・配色を提案した上で
実際に見てもらい、Feedbackを受けて反復修正する、という今回実際に
採用した進め方が、現実的な協働Pattern であると考える。

## 4. 結論（今後の運用への反映）

```text
- 構造・挙動に関わる実装（State管理、Accessibility、Layout機構、
  Component設計）については、通常の実装Task同様の精度を期待して
  良いと判断する。
- Pixel単位の視覚的Taste（色の組み合わせ、余白の量感等）については、
  Claude側の初手の精度に過信せず、「提案→実際に見る→Feedback→
  修正」というIteration前提で計画するのが望ましい。
- CSSの高度な仕様（Position方式とContaining Blockの相互作用等）に
  関わる実装は、実装前に仕様を明示的に確認する一手間を、今後は
  より意識的に挟む。
```

## 5. Status

```text
Current Point            : 2-E-F/G CSS微調整全5Round完了後の振り返りとして、
                            ユーザー指示によりEvidence化した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Evidence記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし（記録目的）。
Exact Next Route          : ユーザーの次の指示待ち（2-E-Hは後日、
                            別途着手）。
```
