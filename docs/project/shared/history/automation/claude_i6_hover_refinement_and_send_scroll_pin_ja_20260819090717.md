# Claude I-6ライブ確認Feedback対応：Hover範囲修正・送信時Scroll Pin・新規Bug発見

```yaml
document_id: claude_i6_hover_refinement_and_send_scroll_pin_20260819090717
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／将来の復旧Task
role: design_governor
created_at: 2026-08-19 09:07:17 JST
language: ja
purpose: |
  I-6実装完了後、ユーザーが実Local Model・実Browserで動作確認した結果の
  Feedback対応記録。#2の修正が不十分だった点の再修正、および新規要望
  （送信時のInput側Log位置固定）への対応。作業中に、無関係な既存Bug
  （新規会話への初回送信が2回Clickを要する）を偶然発見したため、
  合わせて記録する（本Doc作成時点では未修正）。
created: Claude Code
```

## 1. 背景

I-6完了報告後、ユーザーが実際にBrowserで動作確認し、次のFeedbackがあった。

1. **#2再修正**：Hover Tooltipは出るようになったが、Panel自体の上にCursorがある間も表示され続けるのはおかしい。Button上にCursorがある時だけにしてほしい。
2. **#3・#5**：問題なし（確認完了）。
3. **#1**：問題なし（保留のままでよい）。
4. **#4**：継続してScope外。実装中に類似要因を見つけたら都度報告する方針を確認。
5. **新規要望**：Message送信時、入力側（User）Log表示位置が下へ流れ続け、Assistant回答が画面最下部でStreaming表示されるため「画面がガクガクする」。送信時は、User側の発言を画面上部付近に固定表示してほしい。

## 2. #2再修正：Hover TooltipをButton自身のHoverのみへ限定

### 2.1 原因

前回の修正（`.context-usage-wrap:hover .context-usage-tooltip { opacity: 1; }`）は、Button・Popouts（Tooltip＋Panel）を包む`.context-usage-wrap`全体のHoverを条件にしていたため、Panel自体にCursorが乗っている間もTooltipが表示され続けていた。

### 2.2 対応

`.context-usage-button`と`.context-usage-popouts`（Tooltip・Panelを包むWrapper）は兄弟要素であるため、一般兄弟結合子（`~`）を用いて、Button自身の`:hover`のみを条件にするよう変更した。

```css
.context-usage-button:hover ~ .context-usage-popouts .context-usage-tooltip {
  opacity: 1;
}
```

実Browserで、Button上Hover時のみTooltip表示・Panel上Hover時は非表示・Panel外へCursorを移すと即座に非表示になることを確認した。

## 3. 新規要望：送信時のScroll Pin機能

### 3.1 原因

`MessageList.tsx`は、`messages`配列が変化するたび（Streaming中の1Token更新ごとを含む）、末尾Sentinelを`scrollIntoView({ block: "end" })`していた。これにより、Assistant回答が伸びるたびにPage全体が最下部を追いかけ続け、結果として「画面がガクガクする」体感になっていた。

### 3.2 対応

`App.tsx`に新規State `pinnedMessageId`（送信したTurnのUser Message IDのみを保持、それ以外はnull）を追加し、`MessageList`の挙動を2つに分岐させた。

```text
pinnedMessageId が null の場合（会話読込・切替時）
  → 従来通り、末尾SentinelへscrollIntoView（履歴の末尾＝完了した回答全体を表示）

pinnedMessageId がTurnのUser Message IDの場合（Liveな送信中）
  → そのUser Message要素自体へscrollIntoView({ block: "start" })
  → User Message要素自体は動かないため、Assistant回答が下で伸びても
    再Scrollは実質No-op——これがPinとして機能する
```

`pinnedMessageId`は、`sendPersistentMessage`・`sendEphemeralMessage`で送信直後にUser Message IDへ設定し、会話切替・新規会話作成・Retry／Regenerate開始時にはnullへ戻す（これらはUser発言を伴わない、または別の会話文脈のため、従来のSentinel挙動へ戻す）。

**完了後もPinを維持する設計判断**：Turn完了後、`sendPersistentMessage`はServer側Canonical Data（`turn_id`ベースの新しいMessage ID体系）で`messages`を再読込する。この際、`pinnedMessageId`（Local生成の`msg-N`体系）を意図的にクリアしない——再読込後のDOMには一致するIDが存在しなくなるため、`scrollIntoView`呼び出しは静かにNo-opとなり、結果としてPin位置がそのまま維持される（Bottom-scrollへの意図しないJumpを防ぐ）。ユーザー提示のScreenshot（Userの質問のみが上部付近に表示され、大きな余白がある静止状態）と一致する挙動として、この設計を選択した。

CSS側では、`.message`に`scroll-margin-top: 64px`を追加し、固定表示される右上TopbarのPillと重ならないようにした。

### 3.3 Validation

```text
Frontend : Vitest 77件 Pass（75→77、MessageList.test.tsx新規追加：
           Pin無し時のSentinel Scroll、Pin有り時のTop Scroll）、
           eslint clean、tsc --noEmit clean、vite build成功
```

### 3.4 実Browser確認

1. 新規会話へ長文回答を要求するMessageを送信 → User発言がTopbar Pillの下に固定され、Assistant回答がその下でStreaming成長する間も、User発言の位置が動かないことを確認（複数回のScreenshot比較で同一位置を維持）。
2. Streaming完了後も、View位置がBottomへJumpせず、Pin位置のまま維持されることを確認（再修正後）。
3. 既存の会話をSidebarから選択して開いた場合は、従来通り履歴の末尾（完了した回答の全文）が表示されることを確認（回帰なし）。
4. 開いた会話へ続けてMessageを送信した場合も、新しいUser発言へ正しくPinし直されることを確認。

## 4. 偶然発見したBug（未修正、報告のみ）

上記の検証作業中、無関係な既存Bugを発見した。**新規（未選択状態）の会話へ初めてMessageを送信すると、1回目のClickでは何も送信されず、2回目のClickで初めて送信される。**

### 4.1 原因

`sendPersistentMessage()`の該当箇所：

```ts
let conversationId = selectedConversationId;
if (conversationId === null) {
  await createPersistentConversationAndSelect();
  conversationId = selectedConversationId;  // ← Stale Closure
}
if (conversationId === null || persistentRevisionRef.current === null) {
  return;  // ← 1回目はここで無言return
}
```

`createPersistentConversationAndSelect()`内部で`setSelectedConversationId(...)`を呼んでいるが、React の状態更新は非同期であり、`await`後に読む`selectedConversationId`は、この関数が呼ばれた時点（Render時）のClosureに固定されたままの値（＝まだ`null`）である。そのため、`conversationId = selectedConversationId;`は依然として`null`となり、直後のGuardで無言returnし、実際には何も送信されない。2回目のClick時には、既に前の呼び出しで`selectedConversationId`のReact State自体は正しく更新済み（Re-renderにより`sendPersistentMessage`のClosureも新しいものに差し替わっている）なので、正常に送信される。

`sendEphemeralMessage()`側にはこのPatternが無いため、影響は永続会話（Persistent）Modeの、かつ「会話未選択状態からの最初の送信」に限定される。

### 4.2 対応方針

本Doc作成時点で修正は行っていない。ユーザーへ報告済み、対応要否・Timingはユーザー判断待ち。

## 5. Status

```text
Current Point            : #2再修正・送信時Scroll Pin機能の実装完了、
                            Validation・実Browser確認済み。作業中に
                            無関係な既存Bug（初回送信2回Click問題）を
                            発見し、報告した（未修正）。
Files Created／Modified   : Frontend 5File（ContextUsageGauge.tsx（styles
                            経由でCSS変更のみ、Component自体は前回のまま）、
                            app.css、MessageList.tsx、MessageBubble.tsx、
                            App.tsx）、Test 1File新規（MessageList.test.tsx）。
Validation                : Frontend Vitest 77件・eslint・tsc・build、
                            いずれもClean。実Browser確認完了（本Doc
                            第2.2節・第3.4節）。
Open Current Blocker      : NONE（第4節のBugは報告のみ、Blockerではない）
Controller-owned Next Work: 第4節Bugの修正要否をユーザーへ確認する。
Exact Next Route          : ユーザーの次の判断待ち。
```
