# Phase 8 User Mac — Final Delta Recheck Sheet

```yaml
document_type: user_manual_recheck_sheet
document_state: current
phase: phase_8
scope: final_changed_surfaces_only
created_at: 2026-08-31 15:12:08 JST
based_on_controller_review: phase_8_post_mr8_controller_targeted_review_pass_ja_20260831151208.md
expected_result: PASS_or_exact_failure_evidence
```

## 1. このRecheckの範囲

既にUserがPASSしたPhase 7 BaselineとPhase 8 Acceptance 40件を最初からやり直さない。P8-MR0〜MR8で実際に変更した次のSurfaceだけを再確認する。

```text
Manual Direct URL／Fail-closed Grounding
Long Page／Final Prompt Context Budget
Web Evidence Metadata／Persistence
Archive Sidebar／Panel同期
Constitution Preview Layout
Dev Agent Traceable Fixture／Approval／Button Contrast
```

## 2. 起動

Migrationが完了済みの通常起動でよい。Project Rootで実行する。

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

`http://127.0.0.1:8000`を開き、Model LoadとApplication Startupが完了するまで待つ。Public URL TestはUser Macから実InternetへOutboundする。

## 3. Test 1 — Manual Direct URLの成功経路

1. Settings → Web Search → URL取得（Manual）で次を取得する。

```text
https://example.org/
```

2. 次を確認する。

```text
取得成功
Title = Example Domain
Canonical URL = https://example.org/
Untrusted External Content表示
取得Contentが信頼済みと誤表示されない
```

3. Chat ComposerのManual URL欄に同URLを入れ、次を送信する。

```text
このURLから取得した内容だけを根拠に、Pageの題名と概要を短く答えて。
```

4. Example Domainに基づく回答とWeb Evidenceが表示されることを確認する。

## 4. Test 2 — 失敗経路／Security Boundary／Retry

### 4.1 Loopback拒否

SettingsのURL取得とChat Composerの両方で次を試す。

```text
http://127.0.0.1:8000/
```

期待：

```text
private_or_loopback_address
実Fetch 0
Local Application内容をModelが独自知識で答えない
URLを取得できないため回答しない旨のSafe Failure
```

### 4.2 通常Public URL

前回失敗した次をSettingsとComposerで再確認する。

```text
https://abehiroshi.la.coocan.jp/
```

実Internet／Site状態により成功と失敗のどちらも起こり得る。

```text
成功時: 取得したPage内容に基づく回答／Web Evidenceあり
失敗時: Aggregate Reason + 具体的詳細Reason／Model独自の人物説明なし
共通: 理由なく即時`url_rejected`だけで終わらない
```

Transient DNS Retryそのものは実画面で意図的に安定再現できないため、Controller／UnitのInjected Resolver Testを正本Evidenceとする。

## 5. Test 3 — Long Page／Final Prompt Context Budget

1. Settingsで次の2つを有効にする。

```text
表現Mode／Expressive Mode
Context UsageのPrompt Injection
```

2. Chat ComposerのManual URL欄に次を入れる。

```text
https://hololive.hololivepro.com/talents/amane-kanata/
```

3. 次を送信する。

```text
このURLから取得できた内容だけを根拠に、天音かなたの公式Pageの要点を短くまとめて。
```

期待：

```text
「入力がModelのContext上限を超えました」または汎用context_limit_exceededにならない
Contentが入る場合: Budget内にTruncateしたEvidenceで回答
入る余地が本当に0の場合: content_budget_exceeded相当のTyped Safe Failure
Evidenceのない事実をModelが勝手に補わない
```

## 6. Test 4 — Web Evidence Metadata／Persistence

Example Domainの回答で次を確認する。

```text
Source = Public Web
Title = Example Domain
Canonical URL
Source Authority
Fetched At
Content Type
Transformation
Document Digest
Untrusted External Content Label
Canonical URLのCopy Button
Document DigestのCopy Button
```

Browser ReloadとServer Restart後に、成功Citationが同じTurnへ復元されることを確認する。取得失敗Turnがある場合は、失敗ReasonもReload後に消えないことを確認する。

## 7. Test 5 — Archive Sidebar／Panel

1. 使い捨てChatをArchiveする。
2. Sidebarの通常Chat一覧から即座に消える。
3. Settings → Data Controls → アーカイブ済みChatを表示。
4. 最新の一覧がReloadなしで表示される。
5. 「アーカイブ済みChatを閉じる」でPanelを閉じる。
6. Settingsを閉じて再度開くと、Panelは未表示の初期状態に戻る。
7. Archive解除でPanelから消え、Sidebarへ即座に戻る。
8. 手動「再開」なしでそのまま送信できる。

完全削除／一括Delete／Exportの虚偽Buttonがないことも保つ。

## 8. Test 6 — Constitution／Dev Agent／Regression

### 8.1 Constitution Preview

```text
OFF／OBSERVE／ENFORCEがそれぞれ独立Header行
Decision／評価区分／Action許可範囲／違反時の表示が下に縦並び
Backend Semanticsは従来どおり
Production Active Mode = off
```

### 8.2 Dev Agent Fixture

Demo Runを開始し、list → read → write Gateまで進める。

```text
list: 実際のTarget Path一覧が見える
read: path／content／digestが見える
write承認前: path = notes/new.md／Write Contentが見える
Resource Scope = fixture_only
Gate Reason = external_write
承認後: written／digest／overwrite／written_atが見える
```

任意のTerminal確認：

```bash
cat runtime_data/persistent/mac-local-primary/dev_agent/fixture_workspace/notes/new.md
```

「却下」でFileが書き換わらないことを確認する。Light／Darkの両Themeで承認／次へ進むButtonと却下／中止Buttonが判読できることも確認する。

### 8.3 Regression

```text
Chatへ戻って通常送信できる
Local RAG ON／OFFの既存挙動を壊していない
Branch選択UIは既定非表示
Reload／別Tab／Server RestartでConversationを保持
```

## 9. User Return Format

次の6行で返す。FAILがある場合だけ、表示文言・URL・Screenshotを追記する。

```text
1. Manual URL Success／Failure: PASS / FAIL
2. Long Page／Context Budget: PASS / FAIL
3. Web Evidence／Persistence: PASS / FAIL
4. Archive Sidebar／Panel: PASS / FAIL
5. Constitution Preview: PASS / FAIL
6. Dev Agent／Regression: PASS / FAIL
```

全6区分PASS後に、Codex ControllerがP8-ACC-040とPhase 8 Closureを別途判定する。
