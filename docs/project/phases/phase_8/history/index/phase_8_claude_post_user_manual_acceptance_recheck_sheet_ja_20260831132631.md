# Phase 8 Post-User-Manual-Acceptance Bounded Rework — User Manual Recheck Sheet

```yaml
document_type: user_manual_recheck_sheet
phase: phase_8
package: P8-MR1_through_P8-MR6
provider: Claude
created_at: 2026-08-31 13:26 JST
covers: P8-MANUAL-001, P8-MANUAL-002, P8-MANUAL-003, P8-MANUAL-004, P8-MANUAL-005, P8-MANUAL-006
supersedes_for_these_items: phase_8_user_mac_manual_acceptance_test_sheet_ja_20260831072507.md
```

このSheetは、User Mac Manual Acceptanceで再現した6件のFindingだけを対象にした差分Recheckである。
Phase 7の既存経路（通常Chat・Local RAG・Data Controls基礎）やP8-A〜Fの既に成立済みの経路は再確認不要——
このSheet全体を通しても`http://127.0.0.1:8000`のLoopback外へは一切出ない（本Rework自体がReal Network、
Real Model以外を必要としないFixture／実File Local I/Oだけで完結する）。

## 起動

```bash
uv run margpa-web
```

- 既定で`http://127.0.0.1:8000`（Loopback限定）で起動する。
- 実Model（Qwen3-4B）のRegistry読込には数秒〜十数秒かかる。「Application startup complete」のLogが出るまで待つこと。

## 1. Manual URL Reliability／Fail-closed Grounding（P8-MANUAL-001）

前回、`https://abehiroshi.la.coocan.jp/`のFetchが`url_rejected`となり、そのTurnでModelが未取得Pageに基づかない
人物説明を生成した（根拠のない内容）。

1. Settings → Web Search Panel で、通常のPublic URL（例：前回失敗した`https://abehiroshi.la.coocan.jp/`、または
   別の任意のPublic URL）を「取得URL」欄に入力し取得する。
   - **期待**：一時的な名前解決／接続失敗であれば、Retryの後に成功する場合がある。実Networkとそのサイトの
     現在の状態に依存するため、失敗が再現すること自体は許容される。
2. Chatへ戻り、同じURLを「添付URL」として貼り、そのPageの内容についてQuestionする（例：「このURLの内容を要約して」）。
   - **Fetchが成功した場合の期待**：取得内容に基づいた回答が生成される。
   - **Fetchが失敗した場合の期待（最重要）**：Modelが独自知識で人物・内容を説明することは一切なく、
     「指定されたURLを取得できなかったため、そのPageの内容を根拠とした回答は生成しませんでした。」という
     旨のTyped Safe Failure Messageだけが表示される。以前のように無根拠な説明文が生成されないことを確認する。
3. `https://example.org/`で同じ手順を確認する。
   - **期待**：確実に成功し、Example Domainの説明が生成される（既存Baseline、Regressionが無いことの確認）。

## 2. Web Citation必須Metadata（P8-MANUAL-002）

1. 上記1.でExample DomainのFetchに成功したChat回答のWeb Evidence表示を確認する。
   - **期待**：Source（Public Web）・Title（実HTML `<title>`である`Example Domain`。URLそのものではない）・
     URL（Canonical URL）・Source Authority・Fetched At・Content Type・Transformation・Document Digestが
     全て表示される。
2. URL行の隣のCopy Buttonにマウスを乗せる／押す。
   - **期待**：Buttonの表示文言が「Canonical URLをコピー」であり、以前のような「Pathをコピー」ではない。
3. 取得に失敗したURL（1.で失敗した場合、またはLoopback URL `http://127.0.0.1:8000/`を試す）のWeb Evidence表示を
   確認する。
   - **期待**：Aggregate Reason（例：`url_rejected`）に加えて「詳細理由」として具体的なReason
     （例：`private_or_loopback_address`）が併記される。

## 3. Archive Sidebar／Panel同期（P8-MANUAL-003）

1. 使い捨てChatを新規作成し、Sidebarの Chat Options → Archive を押す。
   - **期待**：ArchiveしたChatがSidebarの通常一覧から即座に消える（Browser Reload不要）。
2. Settings → Data Controls → 「アーカイブ済みChatを表示」を押す。
   - **期待**：先ほどArchiveしたChatが一覧に現れる。一覧の下（または付近）に「アーカイブ済みChatを閉じる」
     Buttonがあることを確認する。
3. 「アーカイブ済みChatを閉じる」を押す。
   - **期待**：一覧が閉じる（表示Buttonに戻る）。
4. Settingsを閉じ、再度開いてData Controlsを開く。
   - **期待**：Archive一覧は再度「初期状態（未表示）」に戻っており、「アーカイブ済みChatを表示」を押すと
     Freshな一覧が取得される（Reloadなしで最新状態が反映される）。
5. 一覧から「Archive解除」を押す。
   - **期待**：一覧から即座に消え、Sidebarの通常一覧へ即座に戻る。手動Resumeなしでそのままメッセージ送信できる。

## 4. Constitution Preview表示（P8-MANUAL-004）

1. Settings → アドバンスモード → Provisional Runtime Constitution セクションまでScrollする。
2. 3-Mode比較Previewの各Mode（OFF／OBSERVE／ENFORCE）の表示を確認する。
   - **期待**：Mode名（`OFF`等）がHeaderとして単独の行にあり、その下にDecision・評価区分・Action許可範囲・
     違反時の表示が1行ずつ縦に並ぶ。Mode名とDecisionが同一行に詰め込まれていないことを確認する。
   - **期待**：Backendの表示内容自体（`unsupported_action`等）は前回確認時と同じであること（Semantics無変更）。

## 5. Dev Agent Informed Approval／Traceable Fixture（P8-MANUAL-005）

1. Settings → アドバンスモード → Dev Agent（Foundation）で「Dev Agent」を選択する。
2. 「Demo Runを開始」を押し、「次のStepへ進める」を2回押してlist／readをSucceededにする。
   - **期待**：list Stepの下に`Input：—`（List Filesは入力不要）、`Output：paths: notes/readme.md, notes/todo.md`
     のような実際のList結果が表示される。read Stepの下に`Input：path: notes/readme.md`、
     `Output：path: notes/readme.md, content: ..., content_sha512: ...`が表示される。
3. 「次のStepへ進める」をもう1回押し、writeをGate待ちにする。
   - **期待（最重要）**：承認Boxの中に、**承認する前から** `Input：path: notes/new.md, content: Hello from the
     Dev Agent Demo Run.` という実際に書き込まれる内容が表示される。Resource Scope（`fixture_only`）と
     Gate Reason（`external_write`）、および「fixture_workspace限定・実Project FileやNetworkには一切接触しません。」
     という注記も表示される。
4. 「承認」を押し、「次のStepへ進める」を押す。
   - **期待**：write Stepの下に`Output：path: notes/new.md, written: True, content_sha512: ..., written_at: ...,
     overwrite: False`という実際の書き込み結果（Digest・Overwrite有無・書き込み日時）が表示される。
5. （任意・確認用）Terminalで以下を実行し、実Fileが存在することを確認する。
   ```bash
   cat runtime_data/persistent/default/dev_agent/fixture_workspace/notes/new.md
   ```
   - **期待**：「Hello from the Dev Agent Demo Run.」という内容が実際にDiskへ書き込まれている。
6. 「新しいDemo Runを開始」を押し、再度writeのGate待ちで今度は「却下」を押す。
   - **期待**：Runが停止し、`notes/new.md`の内容が上書きされない（5.のTerminal確認を再実行して同じ内容のままで
     あることを確認してもよい）。

## 6. Dev Agent Button Contrast（P8-MANUAL-006）

1. 上記5.の「承認」「却下」Buttonの見た目を確認する。
   - **期待**：「承認」は青系の塗り（Primary）、「却下」は赤系の塗り（Danger）で、Light Themeで文字が
     はっきり読める。
2. TopBarでThemeをDarkへ切り替え、同じBoxを再確認する。
   - **期待**：Dark Themeでも同様に文字が読める（白地に白文字のような状態が起きない）。
3. 「次のStepへ進める」「中止」Buttonについても同様にLight／Dark両方で確認する。
   - **期待**：「次のStepへ進める」はPrimary、「中止」はDangerの配色で、両Themeとも判読できる。

## 期待される制約（Regressionではない、意図された挙動）

```text
- Dev Agent Demo Runは引き続き固定Fixture Plan（list_files→read_file→write_note）のみ。
  任意のTool/Planを自由入力できるUIはまだ無い。
- Dev Agentが触れるのは fixture_workspace/ 配下のみ。Project SourceやNetworkには一切触れない。
- General Keyword Search（Web検索・Manual）は引き続きFixtureであり、実Search APIには接続しない
  （「Fixture Providerによる固定Sampleです」という文言はそのまま）。
- Archive完全削除・一括Delete・Exportは引き続き未実装（Buttonが存在しないこと自体がP8-REQ-012の成立）。
- Large HTML（例：前回のHololive公式Page）は、Model注入時にBudget化（約12,000文字でTruncate）される。
  これにより「入力がModelのContext上限を超えました。」という不透明な失敗にはならず、Truncateされた内容で
  回答が生成される（完全なRaw HTMLでの回答ではないことに注意）。
```

## Recheck結果の記録方法

各項目でPASS／FAILを記録し、FAILがあれば実際の画面表示（Screenshot可）とその時のURL／操作手順を残すこと。
本Sheet全体がPASSした場合でも、それはP8-ACC-040全体のPASSやPhase 8 Closureを意味しない——Codex Controllerの
Targeted Independent Reviewが別途必要である。
