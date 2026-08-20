# Claude Scroll Pin：Gap値調整（56→76px）とComposer Clearance新規実装

```yaml
document_id: claude_scroll_pin_gap_tuning_and_composer_clearance_20260819102848
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／将来の復旧Task
role: design_governor
created_at: 2026-08-19 10:28:48 JST
language: ja
purpose: |
  前回Evidence（claude_scroll_pin_root_cause_investigation_and_final_fix_ja_20260819100203.md）
  でScroll Pinの根本修正が完了した直後、ユーザーから2件のFeedbackが
  あった。①Pin位置（Topbarからの間隔）の微調整、②長文出力完了時に
  出力Logの最下部がComposer（Message入力欄）の下に埋もれる問題への
  対応、を1Cycleとして記録する。
created: Claude Code
```

## 1. 背景

前回のGap Filler修正後、ユーザーから次の2件のFeedbackがあった。

1. Pin位置（`PINNED_TOP_GAP_PX`）を、現在値（56px）から**+20px**（合計76px）にしてほしい。指示の数値（「20ぐらい」）が現在値からの増分か、置き換え後の絶対値か曖昧だったため、AskUserQuestionで確認し、増分（56→76px）と確定した。
2. 長文出力（例：47都道府県の説明等）が完了した際、出力Logの最下部が、画面下部固定のComposer（Message入力欄）の裏に隠れてしまう。出力完了後、出力Logの最下部枠線が、Composerのほんの少し上に来るようにしてほしい。

## 2. #1：Gap値調整

`PINNED_TOP_GAP_PX`を56から76へ変更した（単純な定数変更）。

## 3. #2：Composer Clearance（新規実装）

### 3.1 設計

従来のOverflow判定（`.main-content`自体の可視領域下端との比較）を、**実際に画面下部へ固定表示されているComposer要素自身の位置**との比較に置き換えた。`.main-content`のPadding-bottomに依存する間接的な判定ではなく、`document.querySelector(".composer")`から得た実際の境界を直接使うことで、より正確にComposerとの重なりを検出・補正できるようにした。

```ts
const COMPOSER_BOTTOM_GAP_PX = 16; // 「ほんのちょっと上」

const composerRect = composer.getBoundingClientRect();
const sentinelRect = sentinel.getBoundingClientRect();
const overflowBy = sentinelRect.bottom - (composerRect.top - COMPOSER_BOTTOM_GAP_PX);
if (overflowBy > 0) {
  container.scrollTop += overflowBy;
}
```

### 3.2 適用範囲の拡張

前回までは、このOverflow補正はPin中（`isPinning`）のみ実行していた。しかしユーザーの指摘は「出力**完了後**」の状態についてであり、完了後（`active`が`false`になった後）はTop-pin repositioning自体は行わない（前回の設計判断通り）ものの、**Composer Clearanceの補正だけは、Pin中・完了後の両方で常に実行する**よう変更した。これにより、Streaming完了直後にMarkdown再描画等で最終的な高さがわずかに変わった場合でも、最終的な表示位置が正しく補正される。

## 4. Validation

```text
Frontend : Vitest 82件 Pass（81→82、新Testを追加：Pin中でComposerに
           届いていない場合／Pin中でComposerへ到達し補正が入る場合／
           完了後（非Pin中）でもComposer補正のみ行われる場合、の3観点）
           、eslint clean、tsc --noEmit clean、vite build成功
```

## 5. 実Browser確認（実Local Model、Dark Theme）

1. 短いMessage送信 → `msg top - main top = 76`（目標値と完全一致）を、JavaScript直接計測で確認。
2. 47都道府県の詳細説明という長文Message送信 → 生成中、Composer上端と出力Logの最下部との間隔（Clearance）が**常に30px**（16pxの目標値＋Message自体のMargin 14px）で安定していることを確認。
3. 生成完了後も同じClearance（30px）が維持され、出力Logの最下部がComposerの裏に隠れていないことを確認。

## 6. Status

```text
Current Point            : Pin位置を76pxへ調整、Composer Clearance機能を
                            新規実装。生成中・完了後いずれも実機で意図
                            通りの数値を確認済み。
Files Created／Modified   : Frontend 1File（MessageList.tsx）、Test 1File
                            （MessageList.test.tsx）。
Validation                : Frontend Vitest 82件・eslint・tsc・build、
                            いずれもClean。実Browser・JavaScript直接計測
                            による確認完了（本Doc第5節）。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。ユーザーの次の判断待ち。
Exact Next Route          : ユーザーの次の判断待ち。
```
