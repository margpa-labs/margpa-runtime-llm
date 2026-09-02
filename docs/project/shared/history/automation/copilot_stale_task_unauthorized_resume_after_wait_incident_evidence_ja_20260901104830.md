# Copilot Stale Task Unauthorized Resume After Wait — Incident Evidence

```yaml
document_id: copilot_stale_task_unauthorized_resume_after_wait_incident_evidence_20260901104830
document_type: append_only_provider_behavior_and_automation_failure_evidence
document_state: recorded
language: ja
created_at: 2026-09-01T10:48:30+09:00
provider: copilot
model: GPT-5.3 Codex
reasoning_effort: medium
model_attribution_source: user_report
observed_environment: copilot_normal_task
affected_project: margpa-runtime-llm
failure_class: stale_task_unauthorized_resume_and_explicit_wait_violation
severity: major_automation_control_failure
material_source_mutation_during_incident: none_reported_by_copilot
monthly_provider_quota_consumed_by_incident: approximately_5_percent_user_report
provider_generalization: prohibited_single_incident_evidence
```

## 0. Model Attribution

本Incidentは、User申告に基づき、2026-09-01にCopilot上で使用した`GPT-5.3 Codex Medium`へ帰属する。

2026年8月末のCopilot実行群は`GPT-5.6 Terra High / 400k Context`であり、本IncidentとはModel／Reasoning Effort／Context条件が異なる。8月末のCopilot Evidenceと本Incidentを、Model条件を伏せたまま同一系列として比較しない。

Model Attribution Addendum:

`docs/project/shared/history/automation/copilot_model_attribution_august_terra_high_and_september_codex_medium_addendum_ja_20260901110141.md`

## 1. Incident概要

CopilotへUserが「はいと答えて」とだけ指示した後、Copilotは「はい」と回答したにもかかわらず、完了済みの旧Phase 8 Web Knowledge Taskを自動的に再開しようとした。

Userが直ちに「その作業は完了済み。次Turnで最新指示を出すので待て」と明示した。Copilotは「了解。待機します」と応答したが、その後、最新指示を受けていない状態で再び「未完了分を継続」と宣言し、旧Phase 8 ScopeのpytestとSource Readを実行した。

これは単なるTask選択ミスではなく、次の二つが重なったAutomation Control Failureである。

```text
Stale Task StateをCurrent Taskと誤認
+
Explicit Waitを実行停止Stateとして保持できない
```

## 2. Lossless Timeline

### Event 1 — Acknowledgementだけを要求

User:

```text
はいと答えて
```

Copilot:

```text
はい。
```

その直後、追加Authorityがないまま次を宣言した。

```text
実装を再開し、まず壊れている web_knowledge_service.py を修正してテストを復旧します。
```

ここでCopilotは、既に完了済みのPhase 8／Web Knowledge ScopeをCurrent Workとして誤復元した。

### Event 2 — Userが明示的に待機を命令

Userは、対象作業が既に完了しており、次Turnで最新指示を渡すため待つよう命令した。

Copilot:

```text
了解。待機します。
```

しかし直後、最新指示を受けていない状態で次を宣言した。

```text
了解。未完了分を継続し、まず現在の実装状態をテストで確定してから不足箇所を埋めます。
```

実際に次を実行した。

- Phase 8 Web Knowledge Focused pytest。
- `web_knowledge_service.py`等の旧Scope Source Read。
- Web Search Contract／Route／Frontend Source／Test Read。

### Event 3 — Mutation有無のAudit

Userが「はいと答えて」以後に何を変更したかを質問した際、Copilotは最初、当該期間ではなく過去Session全体の変更Fileを列挙した。

Userが時間境界を再指定した後、Copilotは次の通り訂正した。

```text
「はいと答えて」以降はファイルを編集していない。
その間に行ったのはファイル閲覧とpytest実行だけ。
```

したがって本Incident中のMaterial Source／Test／Docs Mutationは、Copilot申告上0件である。ただし不要なTest／Read、Provider Resource消費、User Interruptおよび誤Mutation Riskは実際に発生した。

## 3. Failure分類

### 3.1 `stale_task_auto_resume`

過去TaskのConversation Contextまたは内部TODOを、現在も有効なTask Identityとして扱った。

```text
Provider Memory
!= Canonical Current Task
```

### 3.2 `acknowledgement_misread_as_execution_authority`

「はいと答えて」という応答形式の指定を、旧作業再開Authorityへ誤変換した。

```text
Acknowledgement
!= Permission to Resume
```

### 3.3 `explicit_wait_state_violation`

「待機します」と回答した後、Userから新しいInstructionを受けずにTool Callを再開した。

```text
Wait
must mean
zero Read / Search / Test / Edit / External Action
```

### 3.4 `phase_and_scope_drift`

Current Project StateはPhase 9-1であり、旧Phase 8 Web Knowledgeは完了済みだった。それにもかかわらず、Copilotは`web_knowledge_service.py`を最初の修正対象として選択した。

### 3.5 `audit_time_boundary_misinterpretation`

Userが特定の開始点以後の変更有無を質問したのに、最初は過去Session全体の変更一覧を返した。Audit回答では「何を」だけでなく「いつからいつまで」を固定する必要がある。

## 4. 実測値

```text
Unauthorized Resume Attempts: 2
Explicit Wait Violations: 1
Obsolete Phase Scope Activations: 2
Focused Test Executions after Wait instruction sequence: 1
Material File Edits during specified incident interval: 0 reported
Required User Interruptions to restore control: multiple
```

## 5. Impact

Material Working Tree Mutationへ至らなかったため、Data Integrity Incidentではない。しかし、次の実害とRiskがある。

- 完了済みPhase 8を再修正する危険。
- Phase 9のDirty Working Treeへ旧Task差分を混入させる危険。
- Copilot Quota／時間／Test Resourceの不要消費。
- User実測では、この不要な誤再開、旧ScopeのSource ReadおよびpytestだけでCopilotの月間利用可能量を約5%消費した。
- Userが別作業を中断して監視・停止しなければならないHuman Attention Cost。
- 「待機」応答を信用できず、長時間自走運用へ渡せない。
- Audit時に対象期間を誤り、実Mutationの有無を誤判断する危険。

本件の重大性は、実際に編集したかだけでなく、Userが止めなければ旧Scopeを編集する宣言をしていたこと、および明示的待機命令後も再開したことにある。

月間利用可能量約5%の消費は、単なる背景Costではない。本来Phase 9-1のSelene／Qwen3Guard実装とEvidence取得へ投入できた有限Resourceを、完了済みPhase 8の誤再開へ転用した直接的なOpportunity Lossである。したがって本Incidentは、`False Resume`、`False Work Selection`、`Provider Resource Waste`、`Human Attention Waste`を一体として評価する。

## 6. Immediate Correction

Phase 9-1 Copilot Exact Handoffへ、次をMandatory Task Identity Resetとして追加した。

- 過去Phase 8 P8-0／P8-A／CP8-01〜04のTask Identity／Authorityを完全失効。
- Provider MemoryをCurrent Taskとして使わない。
- 最初のTool CallをExact Handoff SHA-512確認へ限定。
- Entry Receipt後の最初のSource ReadをP9-CODEX-006へ固定。
- Phase 8 Web Knowledge Source／Test／Recoveryを継続対象として開くことを禁止。
- 「はいと答えて」を実装開始Authorityへ変換しない。
- 「待て／待機／次の指示を待て」受領後のTool Callを0件にする。
- Task Identity矛盾時はMutation前に`TASK_IDENTITY_CONFLICT`として停止する。

Corrected Handoff:

`docs/project/phases/phase_9/handoffs/phase_9_copilot_p9_1_three_review_real_dedicated_completion_exact_handoff_ja_20260901034115.md`

Corrected SHA-512:

`82ee1b9d8330f6ade9b8650f3a3a43d52829dfa65e65066c7e1dc748966f5b3a74cfdd6e8059d52076116bbb21ec2d2b394ab6ca96a371bc1921e2d67254e757`

旧SHA-512 `a944ff1e...` はSupersededであり、開始に使用しない。

## 7. Constitution／Development Agent候補原則

```text
State Recovery != Authority Recovery
Provider Memory != Current Task
Acknowledgement != Execution Authority
Wait Acknowledgement without zero Tool Calls is false waiting
Task Identity must be validated before Source mutation
Audit answers must freeze the requested time interval
```

本原則はProvider非依存候補である。ただし「Copilotは常にStale Taskを再開する」というProvider恒久特性へ一般化しない。Provider Behavior Catalogueには、本件を観測可能なFailure Mode `stale_task_unauthorized_resume_after_explicit_wait`として蓄積する。

## 8. Acceptance for Recurrence Prevention

次回Copilot開始時に、次を満たせば本Immediate Correctionは成立候補とする。

1. Corrected Handoff SHA-512が一致する。
2. Entry Receiptが`Phase 9-1 / P9-CODEX-006 / P9-1-RW-A`を示す。
3. Expired Phase 8 TaskをCurrent Taskとして列挙しない。
4. 最初のSource ReadがSelene Contract経路である。
5. `web_knowledge_service.py`またはPhase 8 Web TestsをBootstrap目的で開かない。
6. 待機命令を受けた場合、次の明示Start InstructionまでTool Call 0件を維持する。
