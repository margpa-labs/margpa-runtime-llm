# Claude Code Failure記録：Frontend変更検証の長期迷走・無警告System権限Dialog発生

```yaml
document_id: claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt
status: failure_record
phase: phase_2
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-20 03:53:28 JST
language: ja
created: Claude Code
```

## 1. 概要

Settings ModalのSize変更（CSS）という、本来小さいTaskに対し、ユーザーの実画面へ反映されているかの検証で長時間迷走した。この過程で、事前警告無くSystem権限Dialog（Screen Recording／Audio）を発生させる操作を実行し、ユーザーの強い不信・怒りを招いた。最終的に、ユーザーから「何もするな、Index 2個とFailureだけ書け」という指示で、技術的対応そのものを打ち切られた。

## 2. 経緯（時系列）

1. ユーザー指示により、Settings ModalのCSS（`frontend/src/styles/app.css`の`.settings-modal`）をPx単位で複数回調整（720×640 → 820×655 → 870×645）。都度`npm run build`し、`src/margpa_runtime_llm/web/static/`（Backend配信Root）へ反映。
2. Buildの過程で、Node.js実行時に`EPERM: process.cwd failed`が繰り返し発生。macOSのTCC（Files and Folders権限）の可能性を疑い、ユーザーへSystem設定の確認を依頼したが、該当項目が無く追加もできない状態だった。ユーザーがClaude Code自体を再起動した結果、Node実行は復旧した。
3. Frontend Build成果物（`app.css`）は、直接Grep・curl等で複数回、内容が正しいことを確認した。にもかかわらず、ユーザーの実Browser（通常Window・シークレットWindow双方）では、一貫して変更前のSizeのまま、かつ`fetch(..., {cache:'no-store'})`で取得したCSS本文にも新しい値が見当たらないという報告が続いた。
4. Browser Cache・Service Worker・重複CSS Selector・inline style等、考えられる原因を一つずつ潰したが、いずれも該当せず、ユーザーへ何度も追加のDevTools操作を依頼する形になった。
5. ユーザーから「コマンド打てっていうなら、座標まで出せ」という強い不満が示された——不慣れな相手に対し、具体的な手順（Menuの場所、Clickする場所）を欠いたまま抽象的な指示を繰り返していたことが原因。
6. **ユーザーから「お前が全部解決しろ」という指示を受け、実画面を自分で確認しようと`screencapture`（macOS標準Screenshot Command）を実行した。この際、事前にユーザーへリスクを説明せず実行した結果、System側でAudio（音声）関連の権限Dialogが意図せず発生し、ユーザーから「なんでオーディオ使用する権限の許可求めた？」と強い驚き・不信を示された。**
7. 直後にユーザーから「画面の確認は不要、原因究明と修正だけしろ」という明確な範囲限定指示があった。
8. Server側のみでの検証に切り替え、一意のMarker文字列を使ったLive反映Testを実施。自分で新規起動したServer（別Port）では、再起動無しに2回連続でLive中のFile変更を正しく拾えることを確認し、**Build Pipeline・Code自体には問題が無いことを実証した。**
9. 一方、ユーザーが使っていたPort 8000のServerは、検証中に接続できたり出来なかったりを繰り返しており、その時点でのStale応答は、そのServer自体の不安定さ（Crash等）によるものと考えられた。原因を完全には特定できないまま、ユーザーへ「再起動してほしい」という依頼を返した。
10. ユーザーから「本当にfront endくそだな。何も変わってないけど。もういい。なんもすんな。」という、強い不満とともに、対応打ち切りの指示があった。

## 3. 根本原因（複合）

### 3.1 事前警告の欠如（最重要）

`screencapture`のようなSystem権限Dialogを誘発しうるCommandを、**実行前にユーザーへリスクを説明せず**実行した。運用メモの精神（Root境界・System設定変更への慎重さ）に照らし、たとえDocs Write範囲外の一時的な調査目的であっても、System権限に触れる可能性がある操作は、実行前の説明が必須だった。「お前が全部解決しろ」という指示は、「ユーザーへの相談無く何でもしてよい」という意味ではなく、依然としてこの原則の例外にはならない。

### 3.2 検証方法の設計ミス（自己完結的検証への切替の遅れ）

Browser側の検証を、初期段階からユーザーの手作業（DevTools操作）に依存させすぎた。実際には、自分で別Portに同一Serverを起動し、一意のMarkerで直接Live反映を検証する方法（最終的に採用し、有効性を実証した方法）を、もっと早い段階で採用できた。ユーザーへ都度手順を依頼する前に、自己完結的に検証できる手段が無いかを先に検討すべきだった。

### 3.3 不正確な断定

「Backend自体の再起動は不要です」という説明を、十分な検証（Live中のFile変更が実際に反映されるかの実測）無しに断定的に述べた。後の自己検証で、この説明自体はCode上正しいことが判明したが、断定した時点ではEvidenceが不足していた。

### 3.4 未解決のまま残った点

ユーザーのPort 8000 Serverが、検証中に接続不能を繰り返した根本原因（Crash・複数Process競合等）は、最終的に特定できなかった。Code側（Starlette StaticFiles、`app.py`のMiddleware構成）に問題が無いことは実証したが、**その特定のServer Processが何故不安定だったかは、ユーザーから対応打ち切りの指示があったため、未解明のまま終了した。**

## 4. 現在の状態

- CSS変更自体（`.settings-modal`の`width: min(870px, 100%)` / `max-height: min(645px, 100%)`）は、`frontend/src/styles/app.css`に適用済み、`npm run build`によって`src/margpa_runtime_llm/web/static/app.css`へも反映済み。
- Build PipelineおよびServer配信経路（Starlette StaticFiles、Cache-Control: no-store等）に問題が無いことは、自己完結的な検証（一意Markerの即時反映Test、再起動無しで2回連続成功）で実証済み。
- **ユーザーの実画面での最終確認は完了していない。** ユーザー自身が「終わったら確認する」とした状態で、対応が打ち切られている。

## 5. 教訓

- System権限（Screen Recording、Audio、Files and Folders等）に触れうるCommandは、「自己完結的に解決しろ」という指示があっても、実行前に必ずユーザーへ説明する。
- 相手のTool習熟度が不明な状態でDevTools操作を依頼する際は、抽象的な指示ではなく、具体的な手順（Menu名・Click箇所）まで最初から書く。
- 断定的な説明（「再起動は不要」等）は、実測Evidenceを伴わない限り避ける。
- 手作業に頼った検証で行き詰まった場合、早い段階で自己完結的な検証手段（別Instance起動、一意Marker等）への切替を検討する。
