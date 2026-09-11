# Development Agent間 Task ID／Role二重識別通信 Decision Evidence

```yaml
document_id: development_agent_task_id_role_dual_identity_communication_decision_evidence_20260910150333
document_type: automation_operating_decision_evidence
document_state: append_only_history
recorded_at: 2026-09-10 15:03:33 JST
language: ja
decision_authority: user
scope:
  - inter_task_communication
  - task_identity_routing
  - role_binding
  - cross_provider_handoff
  - automation_auditability
```

## 1. 決定

2026-09-10、Development Agent間通信では、各Messageの先頭に送信元と送信先それぞれのTask IDおよびRoleを明記する運用を採用した。

Codex Task間では即時適用する。Claude、Copilotその他のProviderでも、Task／Thread／Session／Conversation／Run等の安定した識別子を取得できる場合は同じ意味Contractを適用する。識別子を取得できない場合は捏造せず、`unavailable`とHuman Relay等のRouting方式を明記し、Role Receipt、Handoff DigestおよびProject Identityによる代替照合を行う。

## 2. 起点となった観測

Phase 9-2の限定Rework指示を既存Codex Taskへ送る際、ユーザーは次の識別通知を使用した。

```text
このタスク（Task ID: 01a03b6c-2a68-7881-99bc-c788a600f632）が、
ずっと実装している現行の「設計者兼実装者役」タスクです。
識別通知のみです。
```

この通知により、表示名だけではなくTask IDで既存の現行Executorを一意に指定できた。Controllerは新しいTaskを作成せず、指定されたTask IDへRework指示を直接送信した。

この方式は、過去に発生した次のFailure Surfaceを減らせると判断された。

- 同じまたは似たRole名を持つTaskの混同。
- 旧Task、Historical Taskまたは誤って作成されたTaskへの誤配送。
- Userが既存Taskを指定したにもかかわらず新規Taskを作る事故。
- 完了報告、FindingまたはReworkがどのTask Instanceから来たか不明になる状態。
- Task名変更後に、表示Labelと実Routing先を同一視する状態。

## 3. Title／Role／Task IDの責務分離

今回のDecisionは次の三層を明示的に分ける。

```text
Task名／Title
  = 人間とAgentがRoleや用途を管理しやすくする表示Label

Role
  = 責任、Authority上限および作業Contractを表す論理Identity

Task ID等
  = Messageを特定の実行Instanceへ配送するRouting Identity
```

Task名を付ける主目的はRole管理と可読性であり、通信先の一意性を保証することではない。実配送はTask ID等を使用する。一方、Task IDを知っているだけではRoleまたはAuthorityを得ない。Task ID、Role、Active HandoffおよびUser Decisionが一致していることが必要である。

## 4. 採用するMessage Header

Codexを含む直接Task間通信では、本文より前に最低限次を置く。

```text
【Task Communication Identity】
From:
  Provider: <provider>
  Task ID: <exact-or-unavailable>
  Role: <exact-role>
To:
  Provider: <provider>
  Task ID: <exact-or-unavailable>
  Role: <exact-role>
Message Type: <instruction|receipt|return|finding|rework|resume|status>
```

複雑な指示ではHybrid JSON Execution Contractにも同値を保持する。自然言語Header、JSON、実Routing先および受領Receiptを比較することで、Expected TargetとObserved Deliveryの差分をEvidence化できる。

## 5. 通信Loop

```text
1. 送信側がCurrent Task IdentityとRole Bindingを確認
2. From／To Task ID＋Role Headerを生成
3. Task IDを実Routing先として送信
4. 受領側が宛先と自Roleを照合
5. Receipt／ReturnではFrom／Toを反転してIdentityを明記
6. Mismatch時は本文を実行せずConflictとして返却
7. Rework、Resume、Returnでも同じHeaderを継続
```

Userが既存Taskを明示した場合、ControllerはそのTask IDを照合して使用し、新規Taskを作らない。Task IDが不明な場合も、識別子取得のためだけにUser AuthorityなくTaskを新設しない。

## 6. Cross-provider境界

Providerごとに識別子の名称、公開範囲、寿命および送信方法は異なる可能性がある。したがって共通Ruleは意味Contractだけを定義し、具体的な取得・Routing方法はProvider Adapterへ分離する。

| Provider状態 | 運用 |
|---|---|
| 安定したTask／Thread IDが取得可能 | Exact ID＋Role Headerを必須化 |
| Session／Conversation／Run IDだけ取得可能 | Provider Adapterで`task_id`相当へ写像し、識別子種別も記録 |
| User Relayで宛先を直接指定できない | `Task ID: unavailable`、`Routing Method: user_relay`、Role Receipt必須 |
| 識別子の安定性が未検証 | 推測せず`unverified`として扱い、Project／Handoff Digestで補強 |

Cross-providerで同じRole名を使えることは、同じTask Instance、共有ContextまたはAuthority継承を意味しない。

## 7. 検証性と期待効果

Identity Headerにより次を後から照合できる。

- 誰が、どのProvider／Task／Roleから送信したか。
- どのTask／Roleを宛先として指定したか。
- 実際に応答したTask／Roleは何か。
- 新規Task作成が許可されていたか。
- Role、AuthorityまたはCurrent Handoffが配送途中で変化していないか。
- Failureが指示内容、Routing、Provider通信または受領後実行のどこで生じたか。

期待効果は誤配送と誤作成Riskの低減、Return相関の改善、Cross-provider比較可能性およびAutomation監査性の向上である。ただしTask ID Headerだけで事故を完全に防ぐ保証はなく、事前照合、Receipt、Hybrid Contract、RecoveryおよびIndependent Reviewを維持する。

## 8. 情報管理

Task IDはCredentialではないが、内部運用Instanceの識別情報である。内部Handoff、Recovery、Automation EvidenceおよびRouting Manifestへ必要最小限を保存できる。Public Docsへ無目的に転記せず、認証Token、Cookie、秘密URLまたはCredentialをHeaderに含めない。

Taskを再作成した場合は新しいTask IDへRoleを明示的にRebindし、旧IDをCurrent Targetとして使い続けない。旧TaskはHistorical Identityとして区別する。

## 9. 現行Ruleへの反映

恒常運用Ruleは次へAppend-onlyで追記した。

- `docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`

本EvidenceはDecisionの発生理由と適用境界を記録するHistoryであり、最新User Decision、Active HandoffまたはProvider上の実Task一覧を置換しない。

## 10. Claude Code Session Identity追加Evidence — 2026-09-11 16:00:28 JST

### 10.1 照会の目的

CodexではTask IDを使って実行Taskを一意に識別できることを確認済みだった。Cross-provider RuleをClaude Codeにも適用できるか確認するため、ユーザーは現行Claude Code Sessionへ、Codex Task IDに相当する識別子の有無、継続範囲およびアプリ再起動時の変化を照会した。

### 10.2 Claude側から返されたIdentity

Claude側は次を現行Sessionの実体として返した。

```text
Provider       : Claude Code
Identity Type  : Session ID
Session ID     : local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
Title          : 設計者兼実装者役
Created At     : 2026-09-02 16:09:15 UTC
Project CWD    : MARGPA-RUNTIME-LLM/margpa-runtime-llm
```

Claude側は、CodexのTask IDが一つの継続実行Taskを指す粒度に対し、この`local_...`Session IDがClaude Code側の対応Identityになると説明した。また、Codexの割り込み通知のようにSession冒頭で自動的にIDを名乗る挙動は現状なく、照会された場合に回答する形であるとした。

### 10.3 別系統Transcript UUIDとの分離

Claude側の生Transcript、File PathまたはScratchpadには、別系統のUUIDとして次も現れると報告された。

```text
bccb7444-2530-4d4f-bbda-033f06c5df80
```

今回の照会だけでは、このUUIDの正式なField名、寿命、Sessionとの一対一対応、Resume用途またはRouting用途は確定していない。したがって次のように分類する。

| Identifier | 今回確認した用途 | 現行Disposition |
|---|---|---|
| `local_d7f17853-1ab4-45aa-bacd-b9d6db898b65` | Claude App／Sessionの継続Identityとして返却 | Claude CodeのTask ID相当として採用 |
| `bccb7444-2530-4d4f-bbda-033f06c5df80` | Transcript／Path／Scratchpadに現れる別系統UUID | 意味未確定。Canonical Routingへ不採用 |

二つのIdentifierが同一対象を別形式で表したものか、異なる内部Layerを表すものかを推測で確定しない。

### 10.4 Compactionを跨ぐ継続観測

Claude側は、Session作成日時が`2026-09-02T16:09:15`のままであり、直前に`/compact`によるContext圧縮が実行された後も、同じ`local_...`Session IDが維持されたと説明した。

今回のClaude側回答による継続分類は次の通りである。

```text
IDを維持する場面:
  - /compactによるContext圧縮
  - --continue／--resumeによる同一Session再開
  - 同じ会話の継続

IDが変わる場面:
  - --resume／--continueなしの新規claude起動
  - UI上で明示的に新規Sessionを作成
```

この観測により、少なくとも今回の環境では、CompactionがSession Identityの再生成を意味しないことが示された。ただし、Session IDが同一であることは、Context内容、最新Authority、未完了状態またはReading済みDocsが完全に保持された証明ではない。Identity ContinuityとState／Authority Recoveryは分離する必要がある。

### 10.5 Claudeアプリ再起動後の再確認

ユーザーはClaudeアプリを再起動した後、同じSessionへIdentifierが変化したか再度照会した。Claude側は次の状態を返した。

```text
Session ID : local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
Created At : 2026-09-02 16:09:15 UTC
isRunning  : true
Change     : lastActivityAtのみ最新Activityへ更新
```

Session IDと作成日時はアプリ再起動前後で同一だった。これにより、今回のClaude Desktop／Claude Code環境では、アプリ再起動だけでは既存Session IDが変化しないという追加観測が得られた。

### 10.6 Evidence強度

本節で直接保存している事実は、ユーザーがClaude側へ照会し、そのClaude側出力を本Taskへ提示したことである。Codex ControllerがClaude内部Store、CLI SourceまたはProvider仕様を独立検証した結果ではない。

したがって、次を分離する。

| Claim | 分類 |
|---|---|
| 今回提示されたClaude出力で同一Session IDが返された | User-provided observed output |
| `/compact`後も同じIDだった | 今回のSession内観測に基づくClaude側説明 |
| アプリ再起動後も同じIDと作成日時だった | 再起動前後のClaude側出力による観測 |
| 新規Session作成時だけ必ず変わる | Claude側説明。全Version／Harnessでの普遍性は未検証 |
| `local_...`がClaude内部の唯一のCanonical IDである | 未証明。主張しない |
| Transcript UUIDの正確な意味 | 未確定 |

### 10.7 運用Decision

今回のEnvironmentでは、Claude Code Agent間通信Headerへ次を使用する。

```text
Provider: Claude Code
Identity Type: Session ID
Task ID Equivalent: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
Role: 設計者兼実装者役
```

送信前およびCompaction／Resume／アプリ再起動後の最初の通信では、Session ID、Role／Title、Project CWDおよびActive Handoffを再照合する。Claude側が自動Headerを出さない場合、ControllerまたはUser RelayがHeaderを付け、Claude側へIdentity付きReceiptを要求する。

新規Session作成時は、新Session IDへRoleとAuthorityを明示的にRebindする。旧Session IDをCurrent Routing Targetとして継続利用せず、Historical Identityとして扱う。

### 10.8 現行Ruleへの反映

上記Decisionを次の恒常運用RuleへAppend-onlyで追記した。

- `docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`

本追加EvidenceはClaude Code全Versionの公式仕様を主張するものではない。今回の実運用で得たVerified Operational Envelopeとして保持し、Provider挙動が変わった場合は新しいAppend-only EvidenceとAdapter訂正を追加する。
