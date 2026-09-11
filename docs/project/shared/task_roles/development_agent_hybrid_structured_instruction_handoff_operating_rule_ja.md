# Development Agent間 Hybrid Structured Instruction／Handoff運用Rule

```yaml
document_id: development_agent_hybrid_structured_instruction_handoff_operating_rule
document_type: cross_provider_operating_rule
document_state: stable_current
recorded_at: 2026-09-09 08:32:26 JST
language: ja
decision_authority: user
provider_neutral: true
append_only: true
```

## 1. User Decision

次回のRework結果を受けて作成する追加指示／Handoffから、Development Agent同士の作業移転Messageは、原則として次のHybrid形式を使用する。

```text
Natural-language Intent／Rationale
  + XML Section Boundary
  + JSON Execution Contract
```

本RuleはCodex、Claude、Copilotおよび将来追加されるその他Provider／Modelへ共通適用する。特定ProviderだけのPrompt作法を共通Coreへ固定せず、同じ意味Contractを各Provider Adapterで表現できる状態を保つ。

## 2. 適用対象

次のように、Role、責任、Authority、入力、判定または次Actionを別Task／Agent／Providerへ移転する場合に適用する。

- 新規実装、設計、調査、ReviewまたはDocs作業の委任。
- Review Findingを戻すRework指示。
- Resource Limit、Compaction、停止またはTask再作成後のResume。
- Exact Handoff、Addendum、CorrectionおよびClosure Candidateの移転。
- Controller、Designer、Implementer、Reviewerその他のDevelopment Agent間通信。

単純な一問一答、雑談、作業移転を伴わない短いStatus通知には強制しない。

## 3. 採用理由

複雑なHandoffでは、目的、背景、Role、Authority、禁止事項、作業順序、Evidence、停止条件および返却条件が一つの自然文へ混在しやすい。実運用では、Task数、待機方法、Review範囲、完了報告、Append-only、Git禁止その他の明示条件が誤読または脱落し、不要な作業、Quota／時間消費およびUser負担へつながった。

JSONは固定Field、真偽値、列挙、ID対応および機械的な比較に向く一方、背景、設計意図、例外理由および長いContextを全てJSONへ入れると、Escape、重複、可読性およびToken Costが悪化する。自然言語だけに戻すと、実行Contractと説明の境界が曖昧になる。XML／MarkdownのSection境界で内容種別を分離し、厳密な実行条件だけをJSONへ置くHybridを採用する。

OpenAIの公式Prompt Guidanceは、明確なSection構造を基本とし、JSONはCoding Contextで理解されやすい一方、冗長化とEscape負荷があると説明している。Anthropicの公式Guidanceは、複雑なPromptでXML TagによりInstructions、Context、Examples等を分離し、Task StateやTest結果等の構造DataにはJSON等を使うことを推奨している。

- OpenAI: `https://developers.openai.com/api/docs/guides/latest-model?model=gpt-4.1`
- Anthropic: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`

本形式は誤読Riskを下げるための運用であり、Provider不具合、Model切替、Context欠落、Compaction、Tool異常またはAgent自身の逸脱を完全に防ぐ保証ではない。Recovery、Evidence、Independent ReviewおよびStop Contractは引き続き必要である。

## 4. 情報の配置責務

### 4.1 Natural-language

次を短く明確に書く。

- 達成したい結果と背景。
- なぜ今回その判断・優先順位・境界を採るのか。
- JSONの固定値だけでは失われる設計意図、例外および注意点。

### 4.2 XML／Markdown Boundary

少なくとも`role`、`intent`、`execution_contract`、`context`、`evidence`、`acceptance`、`return_contract`を意味的に分離する。Tag名は一貫して記述的にし、Context内の引用文や参考資料を実行指示として混同させない。

### 4.3 JSON Execution Contract

作業に該当するFieldだけを使い、空の飾りFieldを増やさない。複雑な委任では少なくとも次を候補とする。

```json
{
  "schema_version": "development_agent_handoff_v1",
  "message_type": "start_or_rework_or_resume",
  "from_role": "logical_sender_role",
  "to_role": "logical_receiver_role",
  "task_identity": "exact_or_unavailable",
  "objective": "required outcome",
  "scope": {
    "in_scope": [],
    "out_of_scope": []
  },
  "authority": {
    "read": [],
    "write": [],
    "git": "deny_or_exact",
    "external": "deny_or_exact"
  },
  "required_actions": [],
  "forbidden_actions": [],
  "acceptance_criteria": [],
  "resume_triggers": [],
  "stop_conditions": [],
  "reporting": {
    "intermediate": "allowed_or_forbidden",
    "final": "required",
    "destination": "exact"
  },
  "resource_policy": {},
  "maximum_claim": "exact",
  "artifacts": []
}
```

## 5. Meaning／Authority解決

- Userの最新明示指示が最上位であり、生成されたJSONがUser Intentを置換しない。
- JSON Contractは既存Authorityを明示するものであり、未承認のWrite、Git、External、Destructive、ClosureまたはScope拡張Authorityを生成しない。
- 実行条件はJSON Contractを優先して判定し、説明文は背景と理由を補う。説明文だけでJSONの禁止・上限を拡張しない。
- JSON、XML、自然言語、Base HandoffまたはAddendumが矛盾する場合、受領側は都合のよい部分を選ばず、Conflictを報告して停止する。
- `unknown`、`not_authorized`、`not_run`および`not_applicable`を区別し、欠落値を推測で補完しない。
- Invalid JSON、重複Keyまたは必須Field欠落を黙って補修して実行しない。自然言語と正本から一意に確認できなければCorrectionを求める。

## 6. ExactnessとResource節約

Hybrid化を理由に、Handoff本文、全Evidence、全Historyまたは同じ禁止事項を無制限に複製しない。詳細はExact Path、Document ID、RevisionおよびDigestで参照し、Messageには実行判断へ必要なCurrent Contractだけを載せる。

固定Field名とSchema VersionをProvider間で共有し、Providerごとの表現差はAdapterへ閉じ込める。短い指示を不必要に巨大なJSONへ変換せず、構造化による誤読低減がToken Costを上回る場面へ適用する。

## 7. Start／Rework／Resume／Return

- StartはRole、Task Identity、Authority、Scope、First Work UnitおよびStart Conditionを含める。
- ReworkはConfirmed Finding ID、成立済み範囲、再実行禁止範囲、修正AcceptanceおよびReturn先を含める。
- Resumeは停止時点、部分Mutation、確認済みTest、次の最小Actionおよび再開Authorityを含める。
- Returnは実施結果、未実施、Failure、Test Evidence、変更File、残件、Maximum Claimおよび次のController Actionを同じ意味Schemaで返す。
- 最終報告必須のTaskは、作業完了後に報告を送らず終了してはならない。

## 8. 次回からの適用

現在進行中のRework結果そのものを遡及的に書き換えない。その結果にControllerが追加Reworkを要求する場合、その次Handoff／指示Messageから本Ruleを適用する。その後はDevelopment Agent間の対象通信へ継続適用する。

## 9. 送信前Check

```text
[ ] Intent／Rationaleと実行Contractを分離した
[ ] From／To／Provider／Task Identityを明記した
[ ] Required／Forbidden／In Scope／Out of Scopeを分離した
[ ] Acceptance、Stop、Resume Trigger、Final Reportを明記した
[ ] User IntentとAuthorityをJSON生成時に変更していない
[ ] Current Handoff／Addendum／Digestを特定した
[ ] Provider固有値を共通CoreへHard-codeしていない
[ ] 無駄な重複とJSONの過剰な深いNestを避けた
[ ] 受領側がConflictやMissing Fieldを推測で埋めない契約がある
```

## 10. Task ID／Role二重識別Header Rule（2026-09-10追記）

Development Agent間で作業、Authority、Finding、Return、Resumeまたは状態を移転するMessageは、本文より前に送信元と送信先のTask IdentityおよびRoleを明記する。

Task名／TitleとTask IDは同じ目的で使わない。

```text
Task名／Title
  = 人間とAgentがRole、用途および状態を理解しやすくする表示Label

Role
  = 責任、Authority上限および期待される行動を示す論理Identity

Task ID／Thread ID／Session ID等
  = Provider上で実際の通信先または実行Instanceを一意に識別するRouting Identity
```

同じRole名のTask、改名前後のTask、Historical Taskまたは誤って作成されたTaskが共存し得るため、Task名またはRoleだけで通信先を決めてはならない。逆に、Task IDが一致してもRoleやAuthorityは自動付与されない。RoleとRouting Identityの両方が、Active HandoffおよびUser Decisionと一致して初めて通信対象として扱う。

### 10.1 必須Header

Codex Task間通信では、各Messageの先頭を原則として次の形にする。

```text
【Task Communication Identity】
From:
  Provider: Codex
  Task ID: <exact sender task/thread id>
  Role: <exact sender role>
To:
  Provider: Codex
  Task ID: <exact receiver task/thread id>
  Role: <exact receiver role>
Message Type: <instruction|receipt|return|finding|rework|resume|status>
```

Hybrid JSON Execution Contractにも同じ値を持たせる。

```json
{
  "communication_identity": {
    "from": {
      "provider": "codex",
      "task_id": "exact",
      "role": "exact"
    },
    "to": {
      "provider": "codex",
      "task_id": "exact",
      "role": "exact"
    },
    "message_type": "instruction_or_receipt_or_return_or_finding_or_rework_or_resume_or_status"
  }
}
```

自然言語HeaderとJSONの値が矛盾する場合は送信または実行を続けず、Identity Conflictとして扱う。Headerは本文のAuthority、Scope、Acceptance、StopまたはReturn Contractを置換しない。

### 10.2 送信前／受領時の確認

送信側は、利用可能なTask一覧、直近のIdentity Receipt、Current HandoffまたはUserによる識別通知を使い、少なくとも次を確認する。

- 送信先Task IDが現在対象とするTaskと一致する。
- 送信先RoleがそのTaskへ現在BindingされているRoleと一致する。
- Historical／Archived／旧Role／同名Taskへ誤配送していない。
- Userが既存Taskの使用を指定している場合、新規Taskを作成していない。
- 作業RootまたはProject Identityが必要な通信では、それもCurrent Contractと一致する。

受領側はReceipt／ReturnのHeaderでFrom／Toを反転し、どのTask InstanceがどのRoleとして返したかを明示する。宛先またはRoleが不一致の場合、本文を実行せずIdentity Mismatchとして返す。

### 10.3 Cross-provider適用

Claude、Copilotその他のProviderが、Task ID、Thread ID、Session ID、Conversation ID、Run ID等の安定した識別子を表示または返却できる場合は、そのProvider固有識別子を`task_id`相当として同じRuleを適用する。共通CoreのField名は維持し、Provider上の実Field名と取得方法はAdapterへ分離する。

識別子を取得できない、安定性を確認できない、またはHuman Relayによって送信先をAPI上で一意指定できない場合は、値を捏造しない。

```text
Task ID: unavailable
Routing Method: user_relay
Role Receipt: required
```

この場合は、Role、Provider、Project、Handoff Digest、開始前ReceiptおよびReturn先による代替照合を必須とする。識別子取得のためだけに、User Authorityなしで新しいTaskを作ってはならない。

### 10.4 永続化／公開境界

Task ID等はCredentialではないが、運用Instanceを特定する内部識別情報である。Active Handoff、Recovery、Automation Evidenceまたは内部Routing Manifestへ必要最小限を保存できるが、Public Docsへ無目的に掲載しない。Token、Cookie、認証情報、秘密URLその他のCredentialをTask Identity Headerへ含めない。

Task再作成、Fork、Provider移行またはCompaction後にTask IDが変わった場合、旧IDを新Taskへ引き継いだことにせず、RoleとAuthorityを新IDへ明示的にRebindする。旧TaskはHistorical Identityとして保持し、Current Routing Targetと区別する。

### 10.5 このRuleの目的と限界

本Ruleは、Task名だけに依存した誤配送、同名Taskの混同、旧TaskへのRework送信、意図しない新規Task作成およびReturn元不明を減らし、Expected RoutingとObserved Deliveryを比較可能にする。

ただし、Providerの通信障害、誤ったTask一覧、Task IDの再利用、Platform BugまたはAgentのInstruction違反を完全に防ぐ保証ではない。Identity Header、事前照合、受領Receipt、Execution ContractおよびEvidenceを組み合わせて使用する。

## 11. Task Identity追記後の送信前Check

```text
[ ] Message本文より前にFrom／ToのProvider、Task ID、Roleを明記した
[ ] Task名ではなくTask IDを実Routing先として使用した
[ ] Task IDとRole BindingをCurrent情報で照合した
[ ] Historical／旧／同名／誤作成Taskを除外した
[ ] 新規Task作成のUser Authorityを勝手に推定していない
[ ] 受領側へIdentity付きReceipt／Returnを要求した
[ ] Providerが識別子を提供しない場合、unavailableを明記して代替照合を要求した
[ ] Task IDをAuthorityまたはCredentialとして扱っていない
```

## 12. Claude Code Session Identity Adapter（2026-09-11追記）

### 12.1 今回確認したIdentity

Claude Code側への照会と、Context CompactionおよびClaudeアプリ再起動後の再照会により、今回の現行`設計者兼実装者役`では次のSession Identityが継続して表示された。

```text
Provider       : Claude Code
Identity Type  : Session ID
Session ID     : local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
Title          : 設計者兼実装者役
Created At     : 2026-09-02 16:09:15 UTC
Project CWD    : MARGPA-RUNTIME-LLM/margpa-runtime-llm
```

この`local_...`Session IDを、今回のClaude Code運用におけるCodex Task ID相当の継続Identityとして扱う。ただしProvider固有の名称を消さず、HeaderとJSONには`identity_type: session_id`を併記する。共通Field上で`task_id`相当へ写像する場合も、元のProvider FieldがSession IDであることをEvidenceから失わせない。

Claude側Transcript／Scratchpad／File Pathでは、別系統のUUID `bccb7444-2530-4d4f-bbda-033f06c5df80`も観測された。このUUIDの意味、寿命およびRouting用途は今回確定していないため、`local_...`Session IDと同一視せず、現時点ではClaude Role通信のCanonical Continuity Identityに採用しない。

### 12.2 今回観測した継続境界

同一の`local_...`Session IDと作成日時が、次の状態変化を跨いでも維持されたというClaude側出力を、今回の運用Evidenceとして扱う。

- 同一会話の継続。
- `/compact`によるContext圧縮。
- `--continue`／`--resume`相当での同一Session再開。
- Claudeアプリの再起動。

アプリ再起動後もSession IDと作成日時は同一で、`isRunning: true`が表示され、`lastActivityAt`だけが新しいActivityへ更新されたと報告された。

Claude側説明では、`--resume`／`--continue`を使わない新規`claude`起動、またはUI上での明示的な新規Session作成時にSession IDが変わる。この境界は今回のClaude側自己申告と単一環境での観測に基づく。すべてのClaude Code Version、Harness、Desktop実装または将来仕様で不変とは主張せず、Provider AdapterのVerified Operational Envelopeとして保持する。

### 12.3 Claude Code用Header

Claude Codeとの直接通信またはHuman Relayでは、次のようにIdentity種別を明示する。

```text
【Task Communication Identity】
From:
  Provider: Claude Code
  Identity Type: Session ID
  Task ID Equivalent: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
  Role: 設計者兼実装者役
To:
  Provider: <receiver provider>
  Identity Type: <task_id|thread_id|session_id|conversation_id|unavailable>
  Task ID Equivalent: <exact-or-unavailable>
  Role: <exact receiver role>
Message Type: <instruction|receipt|return|finding|rework|resume|status>
```

JSON Execution Contractでは次の形へ拡張する。

```json
{
  "communication_identity": {
    "from": {
      "provider": "claude_code",
      "identity_type": "session_id",
      "task_id": "local_d7f17853-1ab4-45aa-bacd-b9d6db898b65",
      "role": "designer_implementer"
    },
    "to": {
      "provider": "exact",
      "identity_type": "task_id_or_thread_id_or_session_id_or_conversation_id_or_unavailable",
      "task_id": "exact_or_unavailable",
      "role": "exact"
    }
  }
}
```

Claude CodeがSession冒頭で自動的にIDを名乗らない場合、ControllerまたはUser Relay MessageがHeaderを提示し、Claude側に同じSession ID、Title／RoleおよびProject CWDを含むReceiptを返させる。Session IDの照会結果だけでAuthorityを付与せず、Active Handoff、Project Root、Role ContractおよびUser Decisionとの一致を別に確認する。

### 12.4 App再起動／Compaction後の再照合

Compaction、Resumeまたはアプリ再起動後は、過去に同じIDだったという記憶だけで継続を断定せず、最初の作業移転Messageで次を再照合する。

```text
Session ID
Identity Type
Title／Role
Project CWD
Active Handoff／Revision／Digest
新規Session作成の有無
旧Authorityを自動継承していないこと
```

Session IDが同一でも、Compaction後にContext、最新User DecisionまたはAuthority理解が完全に維持されているとは限らない。Identity ContinuityとContext／Authority Recoveryを分離し、Bootstrap／Handoff／Receiptで復旧する。

## 13. Claude Adapter追記後のCheck

```text
[ ] ClaudeではProvider固有FieldをSession IDとして記録した
[ ] local_ Session IDとTranscript側UUIDを混同していない
[ ] アプリ再起動またはCompaction後にID／Role／CWDを再照合した
[ ] 同一Session IDをContext完全保持またはAuthority継承の証明にしていない
[ ] 新規Sessionでは新IDへRole／Authorityを明示的にRebindした
[ ] Human RelayでもIdentity付きReceiptを要求した
```
