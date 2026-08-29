# Phase 7 Claude Bounded MVP Implementation — Exact Handoff

```yaml
document_id: phase_7_claude_bounded_mvp_implementation_exact_handoff_20260829172159
document_type: exact_execution_handoff
document_state: prepared_pending_preflight_activation
language: ja
created_at: 2026-08-29 17:21:59 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_or_user_selected_claude_task
phase: phase_7
authority_owner: Nazuna Research
controller: Codex project responsible and design governor role
maximum_claim: COMPLETE_CANDIDATE
fresh_task_required: false
implementation_authority: false_until_preflight_activation
```

## 1. Objective

Phase 2で成立したDocumentation RAG、Persistent Citation、Conversation／Branch／Regenerate境界を保持し、Phase 7の`Traceable Grounded Knowledge Runtime`をPoC／MVP水準で実装する。

中心経路は次である。

```text
Local Corpus／Document
→ Chunk／Index／Retriever
→ Selected Evidence
→ Context Injection
→ Answer／Citation
→ Reload／Restart／Branch／Regenerate Persistence

Web Search OFF／ON
→ Governed Search／Fetch
→ Canonical Web Evidence
→ Citation

Settings
→ Web検索Toggle
→ Data Controls
```

Phase 6のSelene、Qwen3Guard、Semantic 109、Built-in Judge／Repair等を解決済みと主張せず、Phase 7の実装Scopeへ混入させない。

## 2. Mandatory Reading — 最小集合

次を指定順で全文読む。Project全Docsの再走査や旧Phase全Handoffの再読は不要である。

### Role／Execution

1. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
2. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
3. `docs/project/shared/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md`
4. `docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`

旧文書に`Fresh Task`前提または旧Role名が残る場合、本Handoffの`fresh_task_required: false`およびCurrent Roleを優先する。現在のTaskが健全なら初期化、Task作り直し、旧Context継承否定の儀式を行わない。

### Phase 7 Canonical Design

5. `docs/project/phases/phase_7/requirements/phase_7_requirements_ja.md`
6. `docs/project/phases/phase_7/architecture/phase_7_architecture_ja.md`
7. `docs/project/phases/phase_7/adr/phase_7_adr_ja.md`
8. `docs/project/phases/phase_7/operations/phase_7_execution_plan_ja.md`
9. `docs/project/phases/phase_7/operations/phase_7_acceptance_matrix_ja.md`
10. `docs/project/phases/phase_7/phase_index_ja.md`

### Boundary／Known Debt

11. `docs/project/phases/phase_6/history/operations/phase_6_special_minimal_closure_with_known_debt_ja_20260829171422.md`
12. `docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`
13. `docs/project/shared/history/planned_work/post_phase_6_closure_claude_copilot_forward_execution_candidates_ja_20260829171422.md`

## 3. As-built Source Entry

実装前に次のCurrent Source／TestだけをAs-builtとして確認する。

```text
src/margpa_runtime_llm/modules/documentation_rag/contracts.py
src/margpa_runtime_llm/modules/documentation_rag/ports.py
src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/bootstrap/documentation_rag.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/persistent_contracts.py
src/margpa_runtime_llm/bootstrap/configuration_control.py
frontend/src/components/SettingsModal/SettingsModal.tsx
tests/unit/documentation_rag/
tests/integration/documentation_rag/
tests/integration/conversation/test_persistent_citation_evidence.py
```

検索Provider、Vector BackendまたはAttachment方式を先入観で固定せず、既存Port／Adapter境界とDependencyを先に確認する。

## 4. Exact Execution Scope

`P7-0`から`P7-I`までを連結実行する。Package内容はExecution Planを正本とし、以下を補足する。

### P7-0 Entry／As-built Freeze

- Phase 2 RAG／Citation／ConversationのCurrent Wiringを図示する。
- Phase 6 Known DebtがPhase 7のPASSへ混入しないTraceを固定する。
- Project内Task Temp、Test Command、Network Boundaryを固定する。

### P7-A Attachment Sizing

- Button／Drag & Drop、Transport、Metadata、Safe Storage、Parser、RAG取込、Archive、Multimodalを分離して規模判定する。
- 局所的に成立する最小Text系添付だけ採用可能。Phase級ならPhase 10以降へ延期する。
- Sizing Decision後は本体へ進み、Attachmentだけで全体停止しない。

### P7-B〜D Local RAG／Citation

- Corpus／Document／Revision／Chunk／Retrieval Run／Citation EvidenceをVersioned Contractとして実装する。
- 既存BM25をBaselineとして保持し、Embedding Portを交換可能にする。新しい重いVector Dependencyを必須化しない。
- Local Documentの登録、更新、削除、Retrieval、Selected Evidence、Citation Persistenceを成立させる。

### P7-E〜F Web Search／Governance

- DomainはProvider非依存Portとし、`httpx`等のTransport型を流入させない。
- Web検索Default OFF。OFF時はSearch／Fetch／Network Call 0をTestで証明する。
- 最低1つのManual Search Golden PathをFixture／Fake Providerで成立させ、Real Public WebはAuthorityと安定性が成立する場合だけ実行する。
- URL、Redirect、Private／Loopback／Link-local／Metadata Endpoint、Response Size、Content Type、Timeout、Secret／PII、Query最小化を有界化する。
- Snippet、Fetched Content、Canonical URL、取得時刻、Digestを分離する。

### P7-G Data Controls

- 通常Settingsへ`データコントロール`領域を追加する。
- 既存の要約Mode／RAG設定列の最上段へ、同じToggle Componentで`Web検索 OFF／ON`を置く。初期値OFF。
- Retention、Export、Delete、External Transmission、Feedback／Synthetic／Future Training Purposeを分離し、Training用途はDefault OFF。

### P7-H〜I Integration／Return

- Request IDでRetrieval／Web／Citation／Failureを相関する。
- Conversation、Citation、Branch、Regenerate、Resume、Recording、Stopを回帰確認する。
- User Manual CandidateとExact Return Handoffを作成する。

## 5. Authority

### Authorized

- Project Root内のPhase 7 Source、Test、Config、Frontend、Phase 7 History／Handoffの作成・編集。
- Existing Phase 2 RAG／Citation SourceのPhase 7に必要な後方互換変更。
- Project内Task-owned Temp／Cacheを明示して行うTest／Static／Build。
- Phase 7実装に必要なOfficial Public Technical DocumentationのRead-only参照。
- Fixture／Fake ProviderによるNetwork-free Test。

### Bounded Network

実Runtimeの外部Search／Fetchは、Credential、課金、Account作成、契約またはSecretを必要としない範囲だけを候補にできる。Real Public Web Probeを行う場合は、対象URL、回数、目的をPackage Evidenceへ記録し、User Data／Conversation全文を外部送信しない。

### Not Authorized

- Git Stage／Commit／Push／Tag／Branch／Remote Action。
- Backup、Phase 7 Closure、Phase 8開始、Roadmap再編。
- `runtime_data/`のUser実Data利用。
- Model Artifactの作成、削除、再量子化、移動。
- Credential／Secret／有料Search Provider／Account／Billing変更。
- Project Root外の永続Mutation。
- Phase 6 Known Debtの全面Rework。

## 6. Execution Control

- Routine Command Failure、Read-only確認、非Blocking FindingまたはProgress Reportだけで停止しない。
- Scope内の通常判断は自己解決し、Packageを連結実行する。
- Package境界ごとに1つのRecovery Indexを作る。Work UnitごとのDoc乱造は避ける。
- 成立済みPackage、Canonical Suite、Official Sourceを理由なく繰り返さない。
- Resource Limit、Compactionまたは5時間制限が近い場合、現在Packageを有界化してRecovery Indexを残す。
- 重大なData破損、Secret接触、課金／Account、Destructive Action、権限外永続Mutationまたは要件ConflictだけをTrue Stop Conditionとする。
- 軽微なIncidentは隠蔽せずEvidence化するが、技術作業を継続できるなら自己修正して進む。

## 7. Internal Review／Rework

全Package実装後にImplementation Freezeを作り、内部Reviewを行う。上限は次とする。

```text
Implementation
→ Internal Review Cycle 1
→ Critical／Major／MVP BlockerだけRework
→ Targeted Review Cycle 2
→ Return
```

Minor／Cosmetic／Enterprise HardeningはShared未解決Registryへ送る。1発完全合格を狙って無限Reviewしない。

## 8. Verification

変更範囲に比例してFocused Testを実行し、最後に次を確定する。

```text
Backend focused／integration
Canonical mypy
Ruff format check／check
Frontend typecheck／lint／test／build
RAG／Web OFF Network 0
Citation Reload／Restart／Branch／Regenerate
Failure／Stop／Persistence regression
```

全pytestはProject内`--basetemp`を使う。FrontendはProject内`NPM_CONFIG_CACHE`と`TMPDIR`を明示する。

Real Browser、Real Public WebおよびUser Dataを使うAcceptanceは未実施なら`USER MANUAL GATE／NOT RUN`とする。

## 9. Return Contract

Return Handoffへ次を含める。

```text
Completed Packages／Work Units
Changed Paths
Requirements／32 Acceptance Disposition
Focused／Canonical Verification
Internal Review／Rework Result
Attachment Sizing Decision
Real Network／Browser／User Data Action Inventory
Known Findings／Deferrals
Active Process／Temporary Artifact
Maximum Claim: COMPLETE_CANDIDATE or INCOMPLETE
Exact Next Action: Codex Controller Bounded Independent Review
```

Phase 7 Closure、Git、Backup、Roadmap、Phase 8へ進まず、Return後は停止する。

## 10. Activation

本HandoffはPreflight Receiptで`implementation_authority: true`へ昇格し、Controllerが開始宣言を提示した時点でActive Execution Contractとなる。
