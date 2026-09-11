# Development Agent Hybrid Handoff／Provider-neutral Role Bootstrap決定Evidence

```yaml
document_id: development_agent_hybrid_handoff_and_provider_neutral_role_bootstrap_decision_evidence_20260909083759
document_type: automation_operating_decision_evidence
document_state: append_only_history
recorded_at: 2026-09-09 08:37:59 JST
language: ja
decision_authority: user
scope:
  - development_agent_instruction_handoff
  - cross_provider_role_recovery
  - phase_10_portable_package_preparation
```

## 1. 記録対象

2026-09-09、Development Agent運用について次の2件を決定した。

1. 次回の追加Rework Handoff以降、Development Agent間の作業移転Messageへ、自然言語、XML／Markdown境界およびJSON Execution Contractを組み合わせたHybrid構造を使用する。
2. `プロジェクト責任者兼設計統括者役`と`設計者兼実装者役`を、新規Task、新規Project、既存Projectおよび異なるProviderで復旧するため、Project-neutralなBootstrap Indexを2種類作る。

本書は、決定内容だけでなく、なぜこの2件を組み合わせて導入するか、その観測根拠、期待効果および限界を保持する。

## 2. 観測された運用上の課題

### 2.1 複雑な指示の境界喪失

長い自然言語Handoffでは、目的、Role、Authority、Task数、作業順、禁止事項、待機条件、Review範囲、停止条件および最終報告契約が同じ本文へ混在する。Phase 9-2の二Task運用では、明示されていたTask数、完全待機およびReview対象範囲が誤って扱われ、不要なTask実行、待機状態の誤認、Quota／時間消費およびUser負担が発生した。

関連Evidence：

- `docs/project/shared/history/ai_system_anomalies/codex/codex_controller_duplicate_task_creation_complete_wait_violation_and_cross_task_communication_approval_anomaly_ja_20260908154353.md`
- `docs/project/shared/history/ai_system_anomalies/codex/codex_phase_9_2_task_orchestration_instruction_replay_and_resource_loss_consolidated_evidence_ja_20260908205225.md`

Claude／Copilotを含む過去のCross-provider運用でも、Role、Authority、開始条件、Append-only、Return形式または作業範囲の誤読・脱落が繰り返し観測されている。これは一つのProviderだけを責めるための記録ではなく、自然言語と長期Contextだけに依存するAgent運用の共通Riskとして扱う。

### 2.2 Context／Provider状態は固定ではない

Long Run、Compaction、Task再作成、Resource LimitおよびProvider側の実行状態変化により、同じ名称のTaskでも前提保持、Tool挙動およびInstruction Followingが一定とは限らない。2026-09-08にはCodex UI上で再試行時の別Model表示も観測されたが、実際の内部Routingとの因果は未確認であり、仮説と観測事実を分離している。

関連Evidence：

- `docs/project/shared/history/ai_system_anomalies/codex/codex_sol_to_luna_retry_fallback_ui_observation_and_effective_execution_hypotheses_ja_20260908211208.md`

この種のPlatform／Model状態変化は、指示形式だけでは防止できない。一方、Contractを明示Fieldへ分ければ、再開時に何が欠落・矛盾したかを比較しやすくなる。

### 2.3 Role復旧入口のProject依存

現在のRecovery／Handoff文書はMARGPA Runtime LLMのProject構造、Path、PhaseおよびCodex中心の運用履歴に強く結び付いている。完全新規Project、途中参加する既存Projectまたは別Provider Taskで同じRoleを復旧する場合、必要文書の探索とProject固有要素の切り分けを毎回やり直す必要がある。

Phase 10ではDocs統合と開発体制の移植Package作成を予定しており、Project-neutralなRole復旧入口は、その前段としても必要になる。

## 3. 決定1 — Hybrid Structured Instruction／Handoff

### 3.1 採用形式

```text
Natural-language Intent／Rationale
  + XML／Markdown Section Boundary
  + JSON Execution Contract
```

- 自然言語は目的、背景、判断理由および例外の意味を保持する。
- XML／MarkdownはInstruction、Context、Evidence、Example、AcceptanceおよびReturnの境界を分離する。
- JSONはRole、Task Identity、Scope、Authority、Required／Forbidden Action、Acceptance、Resume Trigger、Stop、ResourceおよびFinal Reportを固定Fieldとして保持する。

### 3.2 全文JSONを採用しなかった理由

JSONは構造、列挙、真偽値、ID対応および差分比較に強いが、背景や長文Contextまで格納するとEscape、Nest、重複、可読性およびToken Costが増える。自然言語だけでは実行Contractと説明の境界が曖昧になるため、どちらか一方へ統一せず、役割ごとに形式を分ける。

OpenAIの公式GuidanceはMarkdown等の明確なSection構造を基本とし、JSONはCoding Contextで理解されやすい一方、冗長化とEscape負荷があると説明している。Anthropicの公式Guidanceは複雑なPromptをXML Tagで分離し、Task StateやTest結果等の構造DataへJSON等を使用することを推奨している。

- OpenAI: `https://developers.openai.com/api/docs/guides/latest-model?model=gpt-4.1`
- Anthropic: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices`

### 3.3 適用線

次回のRework結果に追加指示が必要になった場合、そのHandoffから開始する。その後はCodex、Claude、Copilotおよびその他Providerを含むDevelopment Agent間で、責任、Authority、入力、判定または次Actionを移転するMessageへ原則適用する。雑談、単純な一問一答および作業移転を伴わない短いStatusには強制しない。

## 4. 決定2 — Provider-neutralな2種類のRole Bootstrap

### 4.1 対象Role

- `project_controller_design_governor_bootstrap_index_ja.md`
- `designer_implementer_bootstrap_index_ja.md`

前者はProject全体、Cross-Phase設計、Authority、Review、Recoveryおよび現在位置を復旧する。後者はAccepted Handoff内の設計、実装、Test、Evidence、ReturnおよびMutation境界を復旧する。両者を一文書へ統合してRole境界を曖昧にしない。

### 4.2 Provider-neutralとする理由

現在Claudeへ`プロジェクト責任者兼設計統括者役`を正式配置してはいない。しかし将来のRole構成変更、障害時代替、Cross-provider比較、移植Packageおよび新しいProvider追加を考えると、Codex専用Recoveryへ固定する合理性はない。

共通IndexはRole Archetype、Authority、Reading Order、Project現在位置の条件付きDiscovery、Handoff、Recovery、StopおよびEvidenceだけを持つ。Task作成、Memory、Compaction、Message、Tool Permission、FilesystemおよびStatus取得のProvider差はAdapterまたは補助Viewへ分離する。

### 4.3 新規／既存Projectへの対応

Current Documentation Index、Roadmap、Active Phase IndexまたはCurrent Handoffに相当する文書が存在する場合は、File名を固定せず、Authorized Root内で意味、Metadata、Current状態、更新日時および参照関係から候補を探索する。完全新規Project等で存在しない場合は正常にSkipし、存在や現在位置を捏造しない。複数候補が矛盾する場合は推測で一件を正本化しない。

### 4.4 Authority非自動付与

Bootstrap Indexを読んだこと、同じRole名を付けたこと、別Providerで同じ文書を利用できることは、Project AuthorityまたはMutation Authorityを自動生成しない。Effective AuthorityはUser Decision、対象Project、Authorized Root、Active Handoff、Role上限およびProvider Capabilityの交差で再構築する。

## 5. 2件を同時に導入する理由

Bootstrap Indexだけでは、新Taskへ作業を渡す都度のScope、Acceptance、禁止事項およびReturn条件を固定できない。Hybrid Handoffだけでは、受領側がProject横断のRole、Authority、Docs規則およびRecovery原則を知らない可能性がある。

```text
Bootstrap Index
  → stable role／authority／recovery baseline

Hybrid Handoff
  → current task／work unit／scope／acceptance delta

Both
  → recoverable and reviewable execution state
```

両方を組み合わせることで、StableなRole前提と、今回限りの実行Contractを分離できる。これはContextへ全履歴を詰め込む方式より、再利用性、比較可能性、誤読発見およびResource効率を高める狙いがある。

## 6. 期待効果と非保証

期待する効果：

- Task数、Authority、禁止事項、Stop、Review範囲およびFinal Reportの脱落を発見しやすくする。
- Providerを替えても同じ意味Contractを比較できる。
- Compaction／Resume後にBefore／After Contractを照合できる。
- UserがPath、Role説明、禁止事項および開始文を毎回再構成する負担を減らす。
- 誤読による無駄なRework、Quota、時間および疲労を抑える。
- Phase 10のDocs統合と移植Packageへ直接接続できる。

保証しないもの：

- ModelまたはProviderの完全なInstruction Following。
- Compaction、Fallback、Tool、Platformまたは通信異常の消滅。
- JSON ContractだけによるAuthority付与または機械的強制。
- Independent Review、Evidence、RecoveryまたはHuman Decisionの不要化。

効果は、将来のHandoffで誤読、Correction回数、無許可Action、Return欠落、Token／時間CostおよびCross-provider再現性を比較して評価する。

## 7. 関連する現在Rule／予約

- `docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`
- `docs/project/shared/task_roles/codex_controller_cross_task_cross_provider_instruction_package_operating_rule_ja.md`
- `docs/project/shared/planned_work/phase_10_project_neutral_controller_recovery_handoff_bootstrap_index_reservation_ja_20260909075701.md`
- `docs/project/shared/automation/automation_control_profile_ja.md`

本書はHistory Evidenceであり、上記Stable Rule、将来作成するBootstrap Index、Active HandoffまたはUser Decisionを置換しない。
