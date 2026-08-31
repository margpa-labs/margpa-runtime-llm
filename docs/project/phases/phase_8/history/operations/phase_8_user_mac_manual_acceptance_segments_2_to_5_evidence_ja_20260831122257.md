# Phase 8 User Mac Manual Acceptance — Segments 2 to 5 Evidence

```yaml
document_id: phase_8_user_mac_manual_acceptance_segments_2_to_5_evidence_20260831122257
document_type: user_mac_manual_acceptance_incremental_evidence
document_state: append_only_interim
language: ja
recorded_at: 2026-08-31 12:22:57 JST
test_owner: User
controller: Codex_project_controller
source_test_sheet: phase_8_user_mac_manual_acceptance_test_sheet_ja_20260831072507.md
previous_segment: phase_8_user_mac_manual_acceptance_web_segment_1_evidence_ja_20260831112449.md
phase_8_closure: not_claimed
```

## 1. Scope

Web Segment 1正本の次Turnから、Userが実画面で返却した次の結果をLosslessに保存する。

```text
Test 3: Branch非表示／Archive管理
Test 4: Provisional Runtime Constitution
Test 2追加: Web Citation必須Field監査
Test 5: Dev Agent Foundation／Gate／Stop
General Keyword SearchのFixture境界
Dev Agent Fixtureを追跡可能な限定実FileにするUser Decision
```

本書は中間Evidenceであり、P8-ACC-040全体PASS、Phase 8 Closureまたは後続Rework成立を主張しない。

## 2. Test 3 — Branch非表示／Archive管理

### 2.1 確認済み

Userは次を実画面で確認した。

- 使い捨てChatをArchiveできる。
- Settings → Data ControlsからArchive済みChat一覧を表示できる。
- Title／Timestampが表示される。
- `開く`で対象Chatを開ける。
- Archive解除できる。
- 解除後は手動`再開`なしで送信できる。
- 完全削除／一括Delete／Exportの虚偽Buttonはない。
- Branch選択UIは既定非表示である。

### 2.2 実画面で再現した不具合

1. `Archive済みChat`欄に、一覧を開いた後の`閉じる／非表示`がない。
2. Settingsを閉じて開き直してもArchive一覧が再Fetchされず、Browser Reloadまで内容が更新されない。
3. ArchiveしたChatがSidebarの通常Chat一覧へ残る。

Userが求める基本State Transitionは次である。

```text
Archive
  -> Sidebarの通常Chat一覧から即時消える
  -> Archive済みChat一覧にだけ残る

Unarchive
  -> Archive済みChat一覧から即時消える
  -> Sidebarの通常Chat一覧へ即時戻る
  -> 手動Resumeなしで送信できる
```

Source確認では、Sidebar用`fetchPersistentList()`が`state`を指定せず、BackendのDefaultがDeleted以外の
Active／Archivedを両方返す。Backendは既に`state=active`と`state=archived`の分離取得を持つ。
Archive Panelは`ready`状態を保持し続け、Settings Close／Reopen時のReset／Refetchがない。

### 2.3 予約

Data Controls内に情報が過密である。ChatGPT参考画像のような、次の専用Manage UIは後続UI Phaseへ予約する。

```text
Data Controls
  Archive済みChat: 管理する
    -> 専用Modal
    -> Title／Created At
    -> 開く／Archive解除
```

完全削除は今回実装しない。

## 3. Test 4 — Provisional Runtime Constitution

### 3.1 実画面の表示

Userは次を返却した。

```text
Revision 1
Digest a10bbc7dd74ce02a…
3 Rule

chat  OFF  2
agent OFF  3
tool   OFF  2

Actual Active Production Mode: off
```

3-Mode Previewは、chat／agent／toolそれぞれに対して次を表示した。

```text
OFF
  Decision: not_evaluated
  評価区分: 未評価
  Action許可範囲: Constitution由来のActionなし
  違反時の表示: 未評価のため提示なし

OBSERVE
  Decision: unsupported_action
  評価区分: 評価して記録のみ（Blockしない）
  Action許可範囲: Blockなし・Authority変更なし
  違反時の表示: 未対応（Typed Unsupported）

ENFORCE
  Decision: unsupported_action
  評価区分: 評価して対応済みActionのみ適用
  Action許可範囲: 対応済みActionのみ・Authority拡張なし
  違反時の表示: 未対応（Typed Unsupported）
```

### 3.2 Controller判定

- ManifestはUnique Rule 3件を持ち、Capability Viewの重複投影により`chat=2／agent=3／tool=2`となる。不整合ではない。
- Production Active Mode OFFは予定どおり。
- Current RuleはAction未対応のため、OBSERVE／ENFORCEの`unsupported_action／typed_unsupported`は虚偽の無い表示である。
- Production Activation、Tool Authority、Model InjectionまたはExternal Actionは発生していない。

以上からConstitution Semantics自体はPASS。

### 3.3 UI Finding

Mode名`OFF／OBSERVE／ENFORCE`と`Decision`が同一行に連結され、後続3軸だけが改行される。
Userは各Modeの下に4行を縦に分離する表示を求めた。

```text
OFF
  Decision
  評価区分
  Action許可範囲
  違反時の表示
```

Current CSSはMode NameとDecisionをFlexの同一Rowに置き、他3軸だけを`flex: 0 0 100%`とする。
これはFrontend限定の小規模修正対象である。

## 4. Test 2追加 — Web Citation必須Field監査

Userの`example.org`画面は次を表示した。

```text
Web Evidence
Source: Public Web
Title: https://example.org/
URL: https://example.org/
Document Digest: 356a71a6fd78…
Untrusted External Content
```

Reload／Server Restart後の保持は確認済みである。ただしPhase 8正本はCitationへ次を求める。

```text
P8-REQ-007:
  Requested URL
  Canonical URL
  Fetched At
  Content Type
  Digest
  Source Class

Architecture:
  Transformation
  Trust Label
```

Current Chat Citationで確認できたもの：

- Source Class: `Public Web`
- Canonical URL相当値
- Digest／Copy
- Untrusted Label
- Persistence

Current Chat Citationで欠ける、または不明確なもの：

- `Fetched At`。
- `Content Type`。
- `Source Authority`。Settings Previewの`general`はChat側にない。
- `Transformation`。Raw HTMLなのかNormalized Textなのか判別できない。
- `URL`表示がCanonical URLであることの明示。Copy Buttonも`Pathをコピー`と表示される。
- HTML `<title>`ではなくURLそのものがTitleとなる。
- Redirect時のRequested URL／Canonical URL差はSource上対応したが、今回のUser Manualで未検証。

したがってControllerが作ったManual Test SheetのTest 2は必須Fieldを網羅しておらず、
P8-ACC-010をPASSと扱うには不十分だった。これはControllerのChecklist不完全としても保持する。

## 5. General Keyword SearchのCurrent境界

Userは`天音かなた`をWeb検索（Manual）へ入れたが、次の固定結果が返った。

```text
Fixture Web Search Result
https://www.python.org/doc/
Python is a programming language ... (Fixture content, not fetched live.)
```

これは不具合ではなく、CurrentのGeneral Keyword Searchが未実装であることを明示するFixture境界である。

```text
Implemented:
  User明示Direct URL Fetchの限定MVP

Not Implemented:
  Query -> Search Provider -> Result Selection -> Fetch -> Normalize -> Evidence
```

General Search Provider、Automatic Search、Account／API Token、SearXNG、Search Result RankingはPhase 11以降へ保持し、
本Reworkで実装しない。Fixtureを実Searchと主張しないCurrent文言は保持する。

## 6. Test 5 — Dev Agent Foundation

### 6.1 Userが確認した状態

```text
Chat／Dev Agent Stable Capability ID切替: 確認
Registry Tool一覧: List Files／Read File／Write Note
Write Note Gate: external_write

Run状態: awaiting_approval
list: succeeded
read: succeeded
write: awaiting_approval
```

Userは、何をList／Read／Writeするか画面から追跡できないためApprovalを実行せず、却下／Cancel経路を確認した。

```text
Run状態: cancelled
list: succeeded
read: succeeded
write: cancelled
Completion: cancelled — Run was cancelled.
```

その後、新規Demo Runを開始できること、Chatへ戻し通常Chatが送信できることを確認した。

### 6.2 Current Source上のExact Fixture

```text
List Files:
  notes/readme.md
  notes/todo.md

Read File:
  path: notes/readme.md
  content: "# Fixture Notes\n\nThis is Fixture content only."

Write Note:
  path: notes/new.md
  content: "Hello from the Dev Agent Demo Run."
```

Current Write先は`FakeToolPort._written_notes`のProcess Memory内Dictionaryであり、OS上の実FileまたはNetworkへは触れない。
Server RestartでMemory Storeは失われる。Run SnapshotはJSON Storeへ残るが、Current UIはStep Input／Outputを表示しない。

### 6.3 Controller判定

Current UIで確認できるのは次だけである。

- Run／Step State Transition。
- Approval Gateへの到達。
- Deny／Cancel。
- Chat復帰。

List／Readの実Output、Write対象Path／Content／Destination、Approval対象をUserが確認できない。
内容を見ずにApprovalさせるUIは、Fixture限定で実害がなくてもApproval Harness Foundationとして不十分である。

### 6.4 User Decision — 追跡可能な限定実Fileへの変更

Userは、任意FileへのWriteではなく、`runtime_data/`配下の固定Sandboxであれば実File化を許容した。
目的は「何を読み、何をどこへ書き、何が残ったか」の完全な追跡性である。

Target Structure：

```text
runtime_data/persistent/<scope-id>/dev_agent/
  fixture_workspace/
    notes/
      readme.md
      todo.md
      new.md
  runs/
    <run-id>.json
```

必須境界：

- Configured Runtime Data RootとScope IDから動的にRootを導出し、User固有PathをHard-codeしない。
- 操作可能Rootを`fixture_workspace/`へ限定する。
- `..`、絶対Path、Symlink、Root Escapeを拒否する。
- Project Source、任意のUser File、Networkへ触れない。
- Approval前にTool、Path、Content、Overwrite有無、Resource Scopeを表示する。
- List／Read／Write ResultをUIで表示する。
- Write後にResult、Digest、Timestamp、Run ID、Step IDを追跡できる。
- Reload／Server Restart後もFileとRun Evidenceを照合できる。

これはReal Development AgentまたはProject File Toolの実装ではない。限定Fixture WorkspaceでApproval／Evidence境界を証明するPoCである。

### 6.5 Button Contrast

Userは次のButtonが白系背景と白系文字でほぼ読めないことを実画面で再現した。

```text
承認
却下
次のStepへ進める
中止
```

Current generic `button` Styleは`color: var(--button-text)`を与えるが、Dev Agent ButtonにPrimary／Secondary Background指定がない。
Primary／Secondary／Dangerの意味とContrastを与え、少なくともLight Themeで黒系文字が読めるようにする。

## 7. Incremental Disposition

| Scope | Disposition |
|---|---|
| Archive Title／Timestamp／Open／Unarchive／Resume不要 | PASS |
| Archive後Sidebar分離／List Refresh／Close | FAIL / Rework |
| Dedicated Archive Manage Modal | DEFERRED UI reservation |
| Constitution Semantics／Production OFF | PASS |
| Constitution Mode／Decision改行 | FAIL / UI Rework |
| Web Citation Persistence／Digest／Untrusted | PASS |
| Web Citation P8-REQ-007 Full Projection | PARTIAL / Rework |
| General Keyword Search | NOT IMPLEMENTED / Phase 11, Fixture is honest |
| Dev Agent Gate／Cancel／Chat Return | PASS |
| Dev Agent informed approval／Tool Result Traceability | FAIL / Rework |
| Dev Agent fixed real-file Sandbox | USER-AUTHORIZED bounded Rework |
| Dev Agent Button Contrast | FAIL / UI Rework |
| P8-ACC-040 overall | NOT PASS / Rework required |
