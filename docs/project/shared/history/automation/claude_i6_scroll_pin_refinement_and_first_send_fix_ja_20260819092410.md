# Claude Scroll Pin位置修正・Overflow追従・初回送信2回Click Bug修正

```yaml
document_id: claude_i6_scroll_pin_refinement_and_first_send_fix_20260819092410
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／将来の復旧Task
role: design_governor
created_at: 2026-08-19 09:24:10 JST
language: ja
purpose: |
  前回Evidence（claude_i6_hover_refinement_and_send_scroll_pin_ja_20260819090717.md）
  で実装したScroll Pinへの、ユーザー実機確認後の追加Feedback対応。
  Pin位置の再設計（CSS scroll-margin依存からJS明示計算への切替）、
  Overflow時の追従挙動の新規追加、および前回報告のみに留めていた
  初回送信2回Click Bugの修正、を1Cycleとして記録する。
created: Claude Code
```

## 1. 背景

前回のScroll Pin実装後、ユーザーが実Local Model・実Browserで確認し、次のFeedbackがあった。

1. **Pin位置が低すぎる**：意図していたのは、Topbar（White／Dark等の並び）の少し下ぐらいの位置。
2. **Overflow時の挙動**：入力Logが上部固定された状態のまま、出力Logが非常に長くなると、下の方が画面外に隠れて見えなくなる。生成中、出力Logがまだ画面に収まっている間は固定でよいが、収まらなくなったら、固定を解除して出力Logの末尾に追従する（結果として入力Logは自然に画面上へ流れて見えなくなる）べき。
3. **初回送信2回Click Bug**：前回報告のみに留めていたBugを修正してほしいとの指示。

## 2. Pin位置の再設計

### 2.1 原因

前回実装は、`scroll-margin-top: 64px`をCSS側に置き、`scrollIntoView({ block: "start" })`のNative計算に委ねていた。しかし`.main-content`（実際にScrollするAncestor）自体が`padding-top: 76px`を持ち、かつ`.messages`も`padding: 18px 10%`を持つため、特に会話の先頭に近い（Scroll可能範囲が浅い）局面で、期待した位置よりも実際の表示位置が下がる挙動になっていた（Scroll可能距離がScroll-marginの要求量に届かず、Browser側でClampされるため）。

### 2.2 対応

`scrollIntoView`のNative計算に依存する方式をやめ、`getBoundingClientRect()`を用いた明示的なScrollTop計算に切り替えた。

```ts
const PINNED_TOP_GAP_PX = 56; // Topbar Pillの下端から見た目上の余白

const containerRect = container.getBoundingClientRect();
const pinnedRect = pinned.getBoundingClientRect();
const targetScrollTop =
  container.scrollTop + (pinnedRect.top - containerRect.top) - PINNED_TOP_GAP_PX;
container.scrollTop = Math.max(0, targetScrollTop);
```

これにより、Scroll可能範囲の深さに関わらず、常に「Container可視領域の先頭から`PINNED_TOP_GAP_PX`（56px）」という一定の位置へ正確に固定できるようになった。CSS側の`scroll-margin-top`は不要になったため削除した。

## 3. Overflow時の追従挙動（新規実装）

Pin位置を計算した直後、末尾Sentinel（Assistant回答の直後に置かれた空Div）のBounding Rectを取得し、Container可視領域の下端を超えているかどうかを判定する。超えている場合は、Pinを維持せず、末尾Sentinelへ`scrollIntoView({ block: "end" })`することで、末尾（成長中の出力）へ追従する。

```ts
const sentinel = bottomRef.current;
if (sentinel !== null) {
  const updatedContainerRect = container.getBoundingClientRect();
  const sentinelRect = sentinel.getBoundingClientRect();
  if (sentinelRect.bottom > updatedContainerRect.bottom) {
    sentinel.scrollIntoView({ block: "end" });
  }
}
```

`messages`が更新されるたび（Streamingの1Token更新ごとを含む）この判定を毎回行うため、出力が伸びて画面に収まらなくなった瞬間から自動的に「Pin固定」から「末尾追従」へ切り替わる。入力Log自体を非表示にする特別なLogicは無く、単に画面が末尾へ追従した結果として、入力Logが自然に画面外（上）へ流れる形になる——ユーザーの要望通りの挙動である。

## 4. 初回送信2回Click Bugの修正

### 4.1 原因（前回報告済み）

`sendPersistentMessage()`が、`createPersistentConversationAndSelect()`呼び出し直後に`selectedConversationId`（React State）を読み直していたが、`await`後もこのClosureが参照する`selectedConversationId`は、この関数が呼ばれた時点（Render時）の値に固定されたまま（Stale Closure）であり、`setSelectedConversationId(...)`による更新を反映しない。結果、`conversationId`が`null`のままGuard節に達し、無言returnしていた。

### 4.2 対応

`createPersistentConversationAndSelect()`の戻り値を`Promise<void>`から`Promise<string | null>`へ変更し、作成した会話IDを直接返すようにした。`sendPersistentMessage()`側は、State再読込ではなく、この戻り値をそのまま使うよう変更した。

```ts
// 変更前
await createPersistentConversationAndSelect();
conversationId = selectedConversationId; // Stale Closure

// 変更後
conversationId = await createPersistentConversationAndSelect(); // 戻り値を直接使用
```

`newChat()`など、戻り値を使わない既存の呼び出し元には影響しない。

## 5. Validation

```text
Frontend : Vitest 78件 Pass（77→78、MessageList.test.tsxを新Logicに
           合わせて書き直し：Pin無し・Pin有り（収まる場合）・Pin有り
           （Overflowする場合）の3Case）、eslint clean、tsc --noEmit
           clean、vite build成功
```

## 6. 実Browser確認（実Local Model、Dark Theme）

1. 新規（未選択）状態から日本の四季についてMessageを送信 → **1回のClickで即座に送信・生成開始**したことを確認（#4修正）。
2. User発言が、Topbar Pill（White／Dark等）のすぐ下、意図した位置に固定されて表示されることを確認（#1修正）。
3. 47都道府県の説明という長文を要求するMessageを送信 → 出力が画面に収まらなくなった時点から、画面が末尾（成長中の出力）へ自動的に追従し始め、User発言が自然に画面上へ流れて見えなくなることを確認（#3新規実装）。
4. 生成完了後も、View位置が不自然にJumpしないことを確認（前回修正の維持を確認）。

## 7. Status

```text
Current Point            : Scroll Pin機能を、明示的な位置計算＋Overflow
                            追従の2段構えへ再設計し、実装・検証完了。
                            前回報告のみだった初回送信2回Click Bugも
                            修正済み。
Files Created／Modified   : Frontend 3File（MessageList.tsx、app.css、
                            App.tsx）、Test 1File（MessageList.test.tsx
                            書き直し）。
Validation                : Frontend Vitest 78件・eslint・tsc・build、
                            いずれもClean。実Browser確認完了（本Doc
                            第6節）。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。ユーザーの次の判断待ち。
Exact Next Route          : ユーザーの次の判断待ち。
```
