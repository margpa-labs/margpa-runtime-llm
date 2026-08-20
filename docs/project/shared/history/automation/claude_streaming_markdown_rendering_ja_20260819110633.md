# Claude Streaming中のMarkdown逐次変換実装

```yaml
document_id: claude_streaming_markdown_rendering_20260819110633
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／将来の復旧Task
role: design_governor
created_at: 2026-08-19 11:06:33 JST
language: ja
purpose: |
  ユーザー要望「ストリーミング出力中、生のmarkdown原文なんだけど、
  ストリーミング出力中時点で変換しながら出力する様に出来る？
  注意点: コピーした時はmarkdownのままで。」への対応記録。
created: Claude Code
```

## 1. 変更内容

`MessageBubble.tsx`のMarkdown変換Gate条件から`message.isFinal`要件を外し、Assistant発言（Error・Incomplete状態を除く）であれば、Streaming中か完了後かを問わず、常にMarkdown変換を試みるようにした。

```text
変更前: isAssistant && message.isFinal && !isError && !isIncomplete
変更後: isAssistant && !isError && !isIncomplete
```

Copy機能（`CopyButton`）は元々、変換後の表示ではなく`message.content`（生Markdown原文）をそのまま受け取る配線になっており、この点はCode変更していない——Streaming中・完了後いずれの状態でCopyしても、常に生Markdown原文がClipboardへ送られる。

## 2. 付随して必要になった調整

Markdown Parserは、閉じられていないCode Fence等の不完全な構文に対し例外を送出する設計になっている。Streaming中は、Code Blockの終端がまだ届いていない等、**構文的に一時的に不完全な状態が頻繁に発生する**——これは異常ではなく、正常な途中経過である。

既存の「Markdown変換失敗時はPlain Textへ落とし、失敗Noteを表示する」Fallback自体はそのまま活かしつつ、**失敗Noteの表示条件へ`message.isFinal`を追加**した。Streaming中に一時的な構文不備でPlain Text表示へ落ちること自体は起こり得るが、その際に失敗Noteまで表示すると、Token到着のたびにNoteが点滅する体験になってしまうため、Noteの表示は完了後（本当にMarkdownとして解釈できなかった場合）に限定した。

## 3. Validation

```text
Frontend : Vitest 86件 Pass（82→86、MessageBubble.test.tsxへ新規Test
           4件追加：①Streaming中でもMarkdown変換される、②Streaming中の
           一時的な構文不備はNoteなしで静かにPlain Text Fallback、③完了後
           の構文不備はNote付きでFallback、④CopyはStreaming中か否かに
           関わらず常に生Markdown原文を送る）、eslint clean、tsc --noEmit
           clean、vite build成功
```

## 4. 実Browser確認（実Local Model、Dark Theme）

見出し・箇条書き・Code Blockを含む出力を要求するMessageを送信し、Streaming中（`回答を生成しています`Status表示中）の時点で、既に見出し・箇条書き・Code Blockが正しく整形表示されることを確認した。

Clipboard読み取り自体は、本Session内の自動化Toolの権限制約によりBrowser経由で直接検証できなかったが、`CopyButton`への配線（`text={message.content}`）はCode変更しておらず、Unit Test（本Doc第3節）で明示的に確認済みである。

## 5. Status

```text
Current Point            : Streaming中のMarkdown逐次変換を実装。Copy時は
                            常に生Markdown原文を維持。実装・Validation・
                            実Browser確認完了。
Files Created／Modified   : Frontend 1File（MessageBubble.tsx）、Test 1File
                            （MessageBubble.test.tsx）。
Validation                : Frontend Vitest 86件・eslint・tsc・build、
                            いずれもClean。実Browser確認完了（本Doc
                            第4節）。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。ユーザーの次の判断待ち。
Exact Next Route          : ユーザーの次の判断待ち。
```
