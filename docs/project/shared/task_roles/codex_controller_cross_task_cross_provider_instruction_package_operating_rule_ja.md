# Codexプロジェクト責任者兼設計統括者役 — Cross-task／Cross-provider指示Package運用Rule

```yaml
document_id: codex_controller_cross_task_cross_provider_instruction_package_operating_rule
status: stable_current
classification: controller_role_operating_rule
owner_provider: Codex
owner_role: プロジェクト責任者兼設計統括者役
created_at: 2026-08-27 22:04:47 JST
applies_to: every_cross_task_or_cross_provider_delegation_resume_rework_review_cycle
```

## 1. 目的

プロジェクト責任者兼設計統括者役は、別Taskまたは別Providerへ作業を委譲する際、UserへDocument Pathと短い開始宣言だけを渡して中継作業を委ねてはならない。

毎回、受領側がそのまま読めるCopy-paste可能な指示Packageを作成する。

```text
Handoff Artifactの存在
≠ 受領側が正しいArtifactを解決できる
≠ Role／Authorityを正しく認識できる
≠ Mandatory Readingを順番どおり読める
≠ Exact Startが成立する
```

本Ruleの目的は、Human RelayのPath Copy負担を減らし、旧Context、旧Authority、類似Path、Digest違い、曖昧な開始宣言およびProvider固有の自己解釈によるExecution Driftを防ぐことである。

## 2. 適用範囲

次の全場面へ毎回適用する。

- Claude、Copilotその他、Codexから直接Messageを送れずUserが中継するProvider。
- Codexの別Taskへ設計、実装、Review、Rework、ResumeまたはClosure Candidate作業を渡す場合。
- Fresh Taskを作り直した場合。
- Auto-Compaction／Manual Compaction／5時間制限／Resource停止後に差分再開する場合。
- Complete Candidate後のIndependent Review Findingを実装側へ戻す場合。
- Exact Handoff発行後にAddendum／Correction／新Evidenceが追加された場合。

単純な雑談、Read-onlyな一問一答、委譲を伴わないController自身の作業には適用しない。

## 3. Provider別の伝達方法

### 3.1 User Relayが必要なProvider

Claude／Copilot等へUserが中継する場合、ControllerはUserへ次の形式で完成済み指示文を返す。

```text
Message 1 : Fresh Role／Authority Bootstrap
Message 2 : Exact Handoff／Mandatory Reading Bootstrap
Message 3 : Exact User Start
Optional  : Resume／Rework／Addendum Message
```

各Messageは、そのままCopy-pasteできなければならない。UserへPathの探索、File名の補完、Digest Copy、Role説明、禁止事項の再構成または開始文の創作を要求しない。

### 3.2 Codex別Task

Codex別Taskへ直接Messageを送れる場合、Controller自身がTask間Message機構で指示を送る。この場合、UserへCopy-paste作業を要求しなくてよい。

ただし、直接送信するMessageの内容は、本Ruleの必須項目を同じ精度で含める。直接通信可能であることは、Authority、Path、Digest、Start、Stop、Return Contractを省略する理由にならない。

Userが「送る前に指示文を見せて」と指定した場合は、Codex別Taskであっても送信前に全文を提示する。

## 4. 毎回作成する指示Package

### 4.1 Message 1 — Role／Authority Bootstrap

最低限、次を明記する。

```text
Provider
Role
Task Identity
Fresh / Continued / Resumedの別
旧Context／Memory／Authority／未完了状態の継承可否
この段階で許可するRead Target
この段階で禁止するMutation／Command／Network／Git／Model Action
要求するReceipt Format
Receipt後の停止状態
```

Fresh Taskでは、旧Taskと同じTitleまたはRole名であってもAuthority継承を禁止し、Repository内HandoffとACKから再構成する。

### 4.2 Message 2 — Exact Handoff Bootstrap

最低限、次を明記する。

```text
Base Exact HandoffのAbsolute Path
Base HandoffのSHA-512
Addendum／CorrectionのAbsolute PathとSHA-512
Mandatory Readingの順序と対象Path
優先順位
Current Phase／Package／Work Unit
成立済み範囲と再実行禁止範囲
Open Finding／Partial／Not Run／Incident
この段階のImplementation Authorityの有無
要求するDigest／Reading Receipt Format
次のExact Work Unit
Receipt後の停止状態
```

UserがPathをCopyしやすいよう、重要PathはMarkdown LinkだけでなくCode Block内のPlain Absolute Pathでも提示する。

Handoff本文にMandatory Readingが列挙されていても、指示Message内でHandoff Pathと「Mandatory Reading全件を指定順で読む」ことを明示する。単に「このDocsを読んで」で済ませない。

### 4.3 Message 3 — Exact User Start

開始指示は、HandoffでFreezeしたExact Phraseを独立Code Blockで提示する。

開始Messageには少なくとも次を含める。

```text
Exact Start Phrase
Active Execution Contract
First Exact Work Unit
Long-run／Package連結条件
Recovery Index条件
True Stop Conditionsの参照
進捗報告後に自走継続するか
Authority未成立項目があっても継続できる範囲
Maximum Claim
Closure／Git／Backup／次Phase禁止
Exact Return先／Return Format
```

「よろしく」「続けて」「開始して」等を、Freeze済みExact Phraseの代わりにしない。

### 4.4 Resume／Rework／Addendum

停止、Review Findingまたは新Evidence後は、以前の開始Messageをそのまま再利用しない。毎回、差分指示Packageを作る。

最低限、次を明記する。

```text
Previous Return／RecoveryのAbsolute PathとDigest
新Finding／Incident／User EvidenceのPathとDigest
前回成立済み範囲
やり直さない範囲
ResumeするExact Work Unit
追加／変更されたAuthorityと禁止事項
Superseded Artifact／Claim
新しいAcceptance
Exact Return条件
```

Addendum発行後は、Base HandoffだけをUserへ渡さない。Baseと全Active Addendumを一つのCopy-paste指示Packageへ統合して提示する。

## 5. Path／Digest Rule

- User Relay用指示文では、対象のAbsolute Pathを明示する。
- Repository Artifact本文では、Portable性が必要な箇所にRelative Pathを使用してよい。
- 類似名、最新らしいTimestampまたは会話記憶からPathを推測させない。
- Digestを取得済みならSHA-512を指示文へ含める。
- Digest未取得を取得済みと書かない。
- Handoff更新やAddendum追加でDigestが変わった場合、古い指示文を再利用しない。
- Self-hashをArtifact本文へ無理に埋め込まず、外側のInstruction PackageまたはManifestで固定する。

## 6. Authority Rule

指示PackageはAuthorityを説明するが、それ自体で未承認Authorityを生成しない。

次を分離する。

```text
Document Read Authority
Implementation Authority
Project Root／Allowed Path Authority
Network Authority
Exact Model Authority
Provider Memory Authority
User Data Authority
Git Authority
Closure Authority
Next Phase Authority
```

特定項目のAuthorityが未成立でも、残る許可範囲を継続できる場合は、そのContinuation Contractを明記する。受領側へ「許可しますか」と毎回尋ねさせず、未成立項目だけをTyped PARTIAL／NOT RUNへ分類させる。

Human-only Gate、Destructive Action、External Action、User Data、Git、ClosureまたはScope拡張は、明示Authorityなしに継続させない。

## 7. Receipt Rule

Controllerは、受領側に作業開始前Receiptを返させる。

Receiptは最低限、次を含む。

```text
Provider / Role / Task Identity
Mandatory Reading Complete / Missing
Digest Match / Mismatch
Active Contract
Old Context / Authority Inheritance
Recognized Allowed / Forbidden Scope
Current State
Next Exact Work Unit
Implementation Authority
Waiting / Active / Blocked State
```

Receiptが不完全または誤っている場合、開始宣言を発行せず、Exact Correctionを返す。

`OK`、`読みました`、`開始できます`だけをReceiptとしてAcceptanceしない。

## 8. User負担の禁止

ControllerはUserへ次を要求しない。

- Repository内から必要Pathを探す。
- 複数HandoffのどれがCurrentか判断する。
- Pathを一件ずつ手作業でCopyする。
- SHA-512を別回答から拾って組み立てる。
- Authority、禁止事項またはStop条件を要約し直す。
- Role名やProvider Identityを補完する。
- Claude／Copilot向けの開始文を自作する。
- AddendumをBaseへ自力で統合する。

Userの役割は、完成済みMessageを必要なProviderへCopy-pasteし、Human-only Start／Approval／Acceptanceを判断することである。

## 9. Exactnessと簡潔性

指示文は必要情報をLosslessに持つ一方、Historical経緯全文を貼り付けない。詳細EvidenceはRepository Artifactへ置き、指示文はExact Path、Digest、Authority、Current State、Action、Stop、Returnを中心にする。

```text
短いが欠落している指示
≠ 簡潔な指示

長いがCurrent Contractを特定できない指示
≠ Exactな指示
```

受領側が追加質問なしに開始前Receiptを返し、Exact Start後に許可範囲内を自走できる粒度を基準とする。

## 10. Controller Completion Check

別Task／別Providerへ委譲する前に、Controllerは毎回次を確認する。

```text
[ ] Provider／Role／Task Identityを明記した
[ ] Fresh／Resume／Reworkの別を明記した
[ ] Base Handoff PathとDigestを含めた
[ ] Active Addendum／Correctionを全件含めた
[ ] Mandatory Readingと順序を示した
[ ] 成立済み／再実行禁止範囲を示した
[ ] Authorityと禁止事項を分離した
[ ] Exact Start Phraseを独立提示した
[ ] Recovery／Compaction／Resource復帰を示した
[ ] Maximum Claimと禁止Claimを示した
[ ] Exact Return Format／Return先を示した
[ ] UserがPathや文面を再構成せずCopy-pasteできる
```

一項目でも欠ける場合、Pathと開始宣言だけをUserへ返して完了扱いしない。

## 11. 恒常運用判定

```text
User Relay Provider:
  Copy-paste Instruction Package = REQUIRED EVERY TIME

Codex Direct Task Communication:
  Controller Direct Send = REQUIRED
  Equivalent Exact Content = REQUIRED

Path-only Handoff:
  PROHIBITED

Start Phrase-only Handoff:
  PROHIBITED

Base Handoff without Active Addendum:
  PROHIBITED
```

本Ruleは、今後のPhase、Rework、Review、Resume、Closure CandidateおよびProvider追加でも継続する。
