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

