# Phase 8 Post-User-Manual Rework Controller Findings — Corrected User Manual Recheck Sheet

```yaml
document_type: user_manual_recheck_sheet
document_state: current_candidate
phase: phase_8
package: P8-MR7-0_through_P8-MR7-6
provider: Claude
created_at: 2026-08-31 14:33 JST
covers: P8-MANUAL-001_through_006_plus_P8-CODEX-013_through_018
supersedes: phase_8_claude_post_user_manual_acceptance_recheck_sheet_ja_20260831132631.md
supersede_reason: >-
  P8-CODEX-017（Controller Review 2026-08-31 13:48:26 JST）が、旧Sheetの起動Commandが`uv run margpa-web`
  だけで必要なFlag（Conversation Persistence／Web Search／Data Controls等）が成立しないこと、Dev Agent
  Terminal確認PathがUserの実Scope（`mac-local-primary`）と一致しない`default`固定であったこと、
  「Loopback外へ一切出ない」という記載がPublic URL Fetchの実態と矛盾することを指摘した。
```

このSheetは、Codex Controllerが検出したP8-CODEX-013〜018の是正結果と、P8-MR1〜P8-MR6で解消した
P8-MANUAL-001〜006の両方をまとめて対象にした差分Recheckである。Phase 7の既存経路（通常Chat・Local RAG・
Data Controls基礎）は再確認不要。

## 起動

Project Rootで実行する。Userの実構成（Runtime Data Root: `$PWD/runtime_data`、Scope ID: `mac-local-primary`）に
合わせて、次の2種類を区別する。

### 1. 初回起動、または既存Conversation StoreがSchema Migrationを必要とする場合

```bash
./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main \
  --host 127.0.0.1 \
  --port 8000 \
  --conversation-persistence \
  --conversation-persistence-migrate \
  --conversation-runtime-data-root "$PWD/runtime_data" \
  --conversation-scope-id "mac-local-primary" \
  --configuration-control \
  --phase-3-governance-definitions \
  --phase-3-governance-definitions-root "$PWD/definitions" \
  --phase-4-runtime-governance \
  --phase-4-runtime-governance-definitions-root "$PWD/definitions" \
  --phase-5-guardrail-governance \
  --phase-6-runtime-model-control \
  --phase-6-feature-modes \
  --phase-7-local-corpus \
  --local-corpus-runtime-data-root "$PWD/runtime_data" \
  --local-corpus-scope-id "mac-local-primary" \
  --phase-7-web-search \
  --phase-7-web-search-governance-mode off \
  --phase-7-data-controls \
  --data-controls-runtime-data-root "$PWD/runtime_data" \
  --data-controls-scope-id "mac-local-primary"
```

`--conversation-persistence-migrate`は、既存Conversation Storeが旧Schemaの場合だけ、Checkpoint／Digest／Rollback付きの
明示Migrationを許可するFlagである。

### 2. Migration完了後の、以後の通常起動

Migrationが一度完了していれば、`--conversation-persistence-migrate`を付けたままでも不要な再Migrationは行われない
（安全に付けたままでよい）が、通常運用では次のFlag無し起動で足りる。

```bash
./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main \
  --host 127.0.0.1 \
  --port 8000 \
  --conversation-persistence \
  --conversation-runtime-data-root "$PWD/runtime_data" \
  --conversation-scope-id "mac-local-primary" \
  --configuration-control \
  --phase-3-governance-definitions \
  --phase-3-governance-definitions-root "$PWD/definitions" \
  --phase-4-runtime-governance \
  --phase-4-runtime-governance-definitions-root "$PWD/definitions" \
  --phase-5-guardrail-governance \
  --phase-6-runtime-model-control \
  --phase-6-feature-modes \
  --phase-7-local-corpus \
  --local-corpus-runtime-data-root "$PWD/runtime_data" \
  --local-corpus-scope-id "mac-local-primary" \
  --phase-7-web-search \
  --phase-7-web-search-governance-mode off \
  --phase-7-data-controls \
  --data-controls-runtime-data-root "$PWD/runtime_data" \
  --data-controls-scope-id "mac-local-primary"
```

起動後、`http://127.0.0.1:8000`を開く。停止時は起動Terminalで`Ctrl+C`。実Model（Qwen3-4B）のRegistry読込には
数秒〜十数秒かかる。「Application startup complete」のLogが出るまで待つこと。

Phase 8のConstitution／Dev Agent Foundationは現在のComposition RootへLocal Componentとして組み込まれているため、
専用の`--phase-8-*` Flagは存在しない。Dev AgentはConversation側と同じ`--conversation-runtime-data-root`／
`--conversation-scope-id`（未指定時は`default`）を再利用する。

### Network使用についての正直な明記

このSheet全体を通して、HTTP Serverの待受自体は`127.0.0.1`（Loopback限定）のままである。ただし、
「1. Manual URL Reliability」でPublic URL（`https://example.org/`等）をFetchする手順は、User Mac自身から
実Internetへの実Outbound Networkを発生させる——これはLoopback内で完結しない。本Reworkの実装・検証自体は
Injected Resolver／Mock Transportで実Network 0のまま行っているが、この手順自体はUserのMacから実際にPublic Web
へ到達する。

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
     旨のTyped Safe Failure Messageだけが表示される。
3. `https://example.org/`で同じ手順を確認する。
   - **期待**：確実に成功し、Example Domainの説明が生成される（既存Baseline、Regressionが無いことの確認）。
4. （新規・P8-CODEX-014）3.のTurnまたは2.の失敗したTurnについて、Browserを再Reload（またはServerを再起動）する。
   - **期待**：Reload後もそのTurnのWeb Evidence表示（成功時はCitation、失敗時はAggregate＋詳細Reason）が
     Live時と同じ内容で復元される。以前はFail-closedで終わったTurn（ERRORで終了したTurn）のWeb Evidenceが
     Reload後に消えてしまう欠陥があったため、この項目が最重要の再確認対象である。
5. （任意・大きいPageでのContext Budget確認）非常に長いPublic Page（例：日本語Wikipediaの長い記事）を
   「添付URL」として貼り、要約を依頼する。
   - **期待**：Modelの実際のContext残量に応じて内容がTruncateされた上で要約が生成される。「入力がModelの
     Context上限を超えました」という不透明な失敗にはならない。

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
     違反時の表示が1行ずつ縦に並ぶ。
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
5. （任意・確認用）Terminalで以下を実行し、実Fileが存在することを確認する。Pathは上記起動Commandの
   `--conversation-scope-id "mac-local-primary"`に対応する（`FixtureWorkspaceToolPort`はScope IDを
   Directory名としてそのまま使用し、SQLite Storeのような追加Hash化は行わない）。

   ```bash
   cat runtime_data/persistent/mac-local-primary/dev_agent/fixture_workspace/notes/new.md
   ```

   - **期待**：「Hello from the Dev Agent Demo Run.」という内容が実際にDiskへ書き込まれている。
   - Scope IDを指定せずに起動した場合（Flag省略）は、代わりに`runtime_data/persistent/default/dev_agent/...`を
     確認すること。
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
- Large HTML（例：長いWikipedia記事）は、Model注入時にこのTurnの実際のToken Budgetに応じてTruncateされる
  （固定12,000文字ではなく、実際のConversation History／RAG／Max New Tokens予約を差し引いた残量で決まる）。
  これにより「入力がModelのContext上限を超えました。」という不透明な失敗にはならず、Truncateされた内容で
  回答が生成される（完全なRaw HTMLでの回答ではないことに注意）。
```

## Recheck結果の記録方法

各項目でPASS／FAILを記録し、FAILがあれば実際の画面表示（Screenshot可）とその時のURL／操作手順を残すこと。
本Sheet全体がPASSした場合でも、それはP8-ACC-040全体のPASSやPhase 8 Closureを意味しない——Codex Controllerの
Targeted Independent Reviewが別途必要である。
