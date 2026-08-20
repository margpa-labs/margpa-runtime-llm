# Claude Scroll Pin「#1位置が全く変わらない」への根本原因調査と最終修正

```yaml
document_id: claude_scroll_pin_root_cause_investigation_and_final_fix_20260819100203
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／将来の復旧Task
role: design_governor
created_at: 2026-08-19 10:02:03 JST
language: ja
purpose: |
  前回Evidence（claude_i6_scroll_pin_refinement_and_first_send_fix_ja_20260819092410.md）
  でPin位置を修正したはずが、ユーザーが3回試しても「全く変わっていない」と
  報告。運用メモ第4.3節（完了確認Challengeへの対応）に従い、防御的に
  即答せず、実機で一次資料を確認して原因を特定した過程と、最終的な
  修正内容を記録する。
created: Claude Code
```

## 1. ユーザーからの完了確認Challenge

「#1 全然変わってないけど？？？3回やらせて全部結果一緒ってどういうことよ？おまえが見てる画面と、僕が見てる画面は別ものなのか？」という、強い疑義を伴う指摘を受けた。運用メモ第4.3節に従い、防御的に「直っているはずです」と即答せず、検証可能な一次資料を直接確認した。

## 2. 調査過程

### 2.1 仮説1：Serverが別（Cache／別Process）

`lsof`・`ps aux`で確認した結果、ユーザーが実際に使用しているのは、本Session開始前から起動していた**Port 8000**の、`runtime_data`（本番相当のRuntime Data Root）を使う長期稼働Processであり、Claude側が検証用に使っていたPort 8001とは別Processだった。

- 該当Static File（`app.js`）は`no-store`Header付きで配信されており、Browser Cacheの影響は無い。
- `.venv`は`src/margpa_runtime_llm/`へのEditable Installであり、Port 8000のProcessも同じ`src/margpa_runtime_llm/web/static/`を参照している（`margpa_runtime_llm.__file__`で確認）。
- 配信中の`app.js`をDirect Curlで取得し、`main-content`・`getBoundingClientRect`（4回呼び出し）等、直近の実装変更に対応するMarkerが実際に含まれていることを確認した。

→ **Server・Cacheの問題ではないと判定**。ユーザーは確かに最新Buildを見ていた。

### 2.2 仮説2：Scroll可能範囲が無く、ClampされていたこはScroll不能

前回実装（`container.scrollTop = 計算値`）は、`.main-content`（実際にScrollするAncestor）の`scrollHeight`が`clientHeight`を超えていない限り、`scrollTop`をどんな値に設定しても`0`にClampされてしまう。

`.main-content`は`padding-top: 76px`、`.messages`は`padding: 18px 10%`を持つため、会話がまだ短く、全体の高さが1画面に収まっている間は、`.main-content`は**そもそもScroll不可能**であり、Message要素は常に自然な配置位置（`76 + 18 = 94px`）にとどまる。前回の`scrollTop`計算Logic自体は正しかったが、**適用先にScroll可能な余地が無ければ何をしても無意味**だった。

ユーザーが「3回やっても同じ」と感じたのは、Cacheでも見間違いでもなく、**短い会話（ほぼ全ての手動Test）では、Fix自体が実質的に一度も発火していなかったため**——本Docの前提となる調査結果である。

## 3. 修正：Gap Filler（Scroll余地の強制確保）

Pin中（`active && pinnedMessageId !== null`）のみ、`.messages`の末尾に`min-height: 100vh`の不可視Element（`.messages-gap-filler`）を追加し、`.main-content`のScroll可能範囲を強制的に確保するようにした。これにより、会話がどれだけ短くても、計算した目標`scrollTop`が実際に到達可能になる。

## 4. 2件目の自己発見Bug：完了直後にPinが解除される

Gap Filler追加後、実Browserで再検証した際、Claude自身が新たな問題を発見した。**生成完了直後（`active`が`false`になった瞬間）にGap Fillerを消していたため、`.main-content`の高さが急に縮み、Browserが`scrollTop`を自動的にClamp（縮小に合わせて強制的に0付近へ戻す）してしまい、せっかくPinした位置が完了と同時に消えてしまう**という挙動になっていた。

これは、ユーザーの短いTestMessage（「こんにちは」等）が典型的に数秒で完了することと相まって、「Pin中は一瞬正しい位置に来るが、完了した瞬間に元の位置（94px）へ戻ってしまい、結果的に『見た目上は変わっていない』ように見える」——ユーザー報告の直接の原因そのものだった可能性が高い。

### 4.1 対応

Gap Fillerの表示条件を、`active && pinnedMessageId !== null`から、`pinnedMessageId !== null`のみへ変更した（`active`を外す）。これにより、生成完了後もGap Fillerは残り続け（次の送信・会話切替・新規会話・Retry／Regenerateで`pinnedMessageId`自体がクリアされるまで）、Scroll位置は完了と同時に崩れない。

## 5. Validation

```text
Frontend : Vitest 81件 Pass、eslint clean、tsc --noEmit clean、
           vite build成功
```

## 6. 実Browser最終確認

Port 8001の独立Verification Instanceで、新規会話へ短いMessage（「やあ、元気？」）を送信し、生成完了後にJavaScriptで直接計測した。

```json
{"gap": 56, "scrollTop": 38, "gapFillerPresent": true}
```

目標Gap（56px）と完全に一致し、生成完了後もGap Fillerが残存していることを確認した。長文（世界の主要国50カ国の説明）でも、Overflow時の末尾追従が引き続き正しく動作することを確認した。

## 7. 反省点

前回のEvidence（`claude_i6_scroll_pin_refinement_and_first_send_fix_ja_20260819092410.md`）で「実Browser確認完了」と報告したが、その確認は「長文Messageで、Pin中の一瞬の見た目」を中心に見ており、**短い会話・生成完了後の最終状態という、実際にユーザーが繰り返しTestしていたであろう条件**を十分にCoverしていなかった。結果として、Scroll可能範囲の有無というEdge Caseと、それに伴う2件目のBugを、ユーザーからの強い指摘を受けるまで自分で発見できなかった。

## 8. Status

```text
Current Point            : Scroll Pin機能の根本原因（Scroll可能範囲不足
                            によるClamp）を特定し、Gap Filler方式で解決。
                            副次的に発見した「完了直後にPinが解除される」
                            Bugも合わせて修正。短い会話・生成完了後の
                            双方で正しく動作することを実機Numeric値で確認。
Files Created／Modified   : Frontend 3File（MessageList.tsx、app.css、
                            App.tsx）、Test 1File（MessageList.test.tsx）。
Validation                : Frontend Vitest 81件・eslint・tsc・build、
                            いずれもClean。実Browser・JavaScript直接計測
                            による確認完了（本Doc第6節）。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。ユーザーの次の判断待ち。
Exact Next Route          : ユーザーの次の判断待ち。
```
