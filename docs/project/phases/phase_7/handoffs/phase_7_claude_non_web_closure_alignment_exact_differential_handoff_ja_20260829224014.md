# Phase 7 Claude Non-Web Closure Alignment — Exact Differential Handoff

```yaml
document_id: phase_7_claude_non_web_closure_alignment_exact_differential_handoff_20260829224014
document_type: exact_differential_execution_handoff
document_state: ready_waiting_exact_start
language: ja
created_at: 2026-08-29 22:40:14 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_claude_phase_7_task
fresh_task_bootstrap: false
phase: phase_7
baseline: p7_0_through_p7_i_complete_candidate_preserved
active_scope: non_web_closure_alignment_and_manual_readiness
external_web_scope: deferred_to_phase_11_plus
maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_7_closure_authority: false
phase_8_authority: false
git_mutation_authority: false
network_authority: false
```

## 1. Controller Direction

本Handoffは、同一Claude TaskでPhase 7 P7-0〜P7-I Complete Candidateを継承する**差分Continuation**である。Fresh Task初期化、Role Bootstrap、旧Context破棄またはP7-0からの再実装を行わない。

2026-08-29のUser Decisionにより、次はPhase 11以降へ延期した。

```text
実General Web Search Provider
External Network Search／Fetch
Web EvidenceのMain Model／Citation接続
Server Canonical Web OFF／ON
外部送信Consent／PII Enforcement
一般URL Fetch
Public／BYOP Endpoint UX
Hostile-site Sandbox／Parser Isolation
Provider CallとOutbound Network Callの観測分離
```

したがって、旧Controller Reviewの`BOUNDED WEB REWORK REQUIRED`を実行しない。P7-CODEX-001〜005の技術事実は保持するが、Phase 7 Closure BlockerではなくPhase 11以降の既知Debtである。

本差分では、Local Corpus／Citation／Data ControlsのPoC／MVP Closure品質、過大Claim訂正およびUser Manual Candidateだけを扱う。

## 2. Mandatory Differential Reading

次の8文書を指定順で全文読む。既に読了済みでも、Digestを照合しCurrent Decisionを再取得する。

1. Phase 7 Claude Exact Return

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_7/handoffs/phase_7_claude_bounded_mvp_implementation_exact_return_handoff_ja_20260829191047.md`

SHA-512:
`27f688584365d37dc8f02e9546ada01402f44aa98225fc491e625e64d85a2f789d25cc3e27e547a4fa3c2343a773ede8b797c4225f377fdb9a247185f5dffc31`

2. P7-I Final Recovery

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_7/history/index/phase_7_current_claude_task_p7_i_final_recovery_ja_20260829190939.md`

SHA-512:
`2f5da0fe56754490e1854b7c024e76af8d177936d5e99839ffb15dc2c8f78e5f3fbfeddedba52535ffd7ad49c4700a73807e5741675beb37f47f100c2efd3190`

3. Controller Bounded Independent Review

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_7/history/operations/phase_7_codex_controller_bounded_independent_review_adjust_ja_20260829215534.md`

SHA-512:
`5717ecd02866d57082d968cae1ed73ba2dfa869cf9e629fa39024702ea6723b954077858df495fd7346ebb7e550cf578f42c4b1399d08a992b5fd7459724d045`

4. External Web Phase 11以降延期Decision

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_7/history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md`

SHA-512:
`e66f7021b7e157574f3c4cf0236125f5c5172bb04fc3e92a3e6c22f1f5c0958025003b9b9660e39e4dcea6f443913639df17a81c5df629ab576b25a1e8cd5e44`

5. Phase 7 Current Index

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_7/phase_index_ja.md`

SHA-512:
`41773dd75a0bcc2227d3b470d5e67f910cec2bdb710604eeabbb8cb45b67b0a77042a2d94e1a4bead1171566e6c63ae6edab70737afabff298385919eee55f3f`

6. Phase 7 Acceptance Matrix

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_7/operations/phase_7_acceptance_matrix_ja.md`

SHA-512:
`65a33c7d491aafb89478ce43d6b9f3ad73c3a30bc78f2beaa943787383a7fd85f7d1a3fe7b4571c969a4c89612e5e4cf7f1fd15b0f97d93bf4fe45062b961bff`

7. Current Unresolved Registry

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`

SHA-512:
`923b84ec5519966953fcee80f56e1a8c5e84e5ee1cce603fa256370156e22a4b937146e9db137d1a0aaf4bf1953b4e6d525f914f786d3961d79480a6f6749fd0`

8. PoC／MVP Resource-constrained Operating Policy

`/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`

SHA-512:
`9b7dca30c94fb184b2978c4d4b42904cdc3c6550ae7ab0eb9b35a59b65342fa239c419ad59a65f2a78e6358514cfc8d3d777a6145cb0b8fecb7d94990cd45835`

Digest不一致時は対象PathとObserved Digestを報告する。ただし、ControllerまたはUserによる今回のDocs追記が原因と合理的に確認できる場合、破壊的ActionをせずCurrent Fileを正本として継続し、無意味に全Taskを停止しない。

## 3. Supersession／Preservation

### 3.1 Supersedeするもの

- Controller Review §4 P7-CODEX-001〜005の技術事実は保持する。
- 同Review §8の`Rework Scope: Web実利用経路だけ`と、P7-CODEX-001〜004成立前はClosure不可というDispositionは、後続User DecisionによりPhase 7 Scopeから外れた。
- Frozen Requirements／Architecture／AcceptanceのWeb項目は削除・改竄せず、Append-only Scope／Acceptance Addendumで`DEFERRED_TO_PHASE_11_PLUS`へ再分類する。

### 3.2 Preserveするもの

- P7-0〜P7-I Source／Test／Recovery。
- Local Corpus Registry、Document Source、Composite Source、RAG InjectionおよびCitation Persistence。
- BM25 Retriever Baselineと既存`EmbeddingPort`予約境界。
- Data ControlsのRetention Fact、Purpose別Consent、全Default OFFおよびPrivate Store。
- Web Port／Fixture／Security Scaffold。Phase 7実Web機能として昇格させない。
- Conversation／Branch／Regenerate／Recording／Stop／Persistenceの既存契約。

## 4. Exact Work Packages

### P7-NW-0 — Entry／Current Baseline Freeze

1. Mandatory Differential ReadingとDigestを確認する。
2. Current Source／Test／Docsを読み、P7-0〜P7-I成立範囲を再構築する。
3. P7-CODEX-001〜005をPhase 7で修正しないことをFinding Ledgerへ明記する。
4. Sourceを変更する前に、非Web Closure Blocker候補だけを列挙する。
5. P7-NW-0 Recovery Indexを作成する。

単に既存実装が存在することを理由に、全Sourceを機械的に書き直さない。

### P7-NW-A — Scope／Acceptance Claim Correction

Append-onlyのPhase 7 Non-Web Scope／Acceptance Addendumを作成する。Frozen Requirements／Architecture／Acceptance Matrixを履歴から削除・上書きしない。

最低限、32 Acceptanceを次のClassへ個別再導出する。

```text
CURRENT_PHASE_APPLICABLE:
  P7-ACC-001, 002, 004-015のLocal Corpus部分,
  023のLocal Context Source部分,
  025-031の非Web部分,
  032のLocal Corpus／Citation／Data Controls User Gate部分

DEFERRED_TO_PHASE_11_PLUS:
  P7-ACC-003,
  P7-ACC-016-022のExternal Web部分,
  P7-ACC-024,
  P7-ACC-028のWeb Provider／Network投影部分,
  P7-ACC-032のWeb Source部分

CURRENT_KNOWN_PARTIAL_NON_BLOCKING:
  P7-ACC-008 — Embedding実体未使用。BM25 Retriever／Index Identityは成立。
```

各IDへ、PASS／PARTIAL／DEFERRED／USER MANUAL GATEと直接Evidence Pointerを付ける。一括`Regression 0`だけで代替しない。

`P7-ACC-008`をPASSへ捏造しない。本差分でEmbedding Model、Vector DBまたは疑似Embeddingを追加しない。Current BM25 BaselineはPoCとして保持し、将来Retriever比較へ送る。

### P7-NW-B — Local Corpus／Citation Closure Readiness

次のProduction主経路をSourceと既存Testから確認する。

```text
Local Document Register
-> Revision／Digest／Chunk Identity
-> Composite Document Source
-> BM25 Retrieval
-> Selected EvidenceだけをContext Injection
-> Assistant ResponseとCitationを分離
-> Conversation Persistence
-> Reload／Restart／Branch／Regenerate／Resume
```

確認対象：

- RAG OFFでRetrieval／Injection Call 0。
- 登録／更新／Soft DeleteとCurrent／Historical分離。
- No Relevant EvidenceをCitationありへ変換しない。
- Selected Chunk、Score、Document／Chunk Digest、Retriever Identity。
- Local Corpus Contentが既存`guardrail.context_source`経路を迂回しない。
- Failureを成功表示へ変換しない。

既存Evidenceで成立する項目はTestを増やさない。Production Compositionの直接Evidenceが欠けるCritical／Major／MVP Blockerだけ、最小Testまたは最小修正を行う。

次は本Packageで直さない。

- Title変更時のSource／Chunk ID再生成。
- Semantic Embedding／Vector Store。
- Retrieval Ranking品質研究。
- 汎用File Attachment。
- Phase 6 Judge／Guard／Semantic Debt。

### P7-NW-C — Data Controls Closure Readiness

次を確認する。

- Retention Factは読取専用の実装事実であり、変更可能設定と表示しない。
- Purpose別Consentは互いに独立し、全Default OFF。
- Consent StoreのRevision／Schema、Atomic Replace、Private Mode、Symlink／Corrupt Failure。
- 保存されたConsentをTraining／Weight Update完了と表示しない。
- 未実装のFeedback収集、Synthetic生成、Training Export、全Data Export／Deleteを利用可能と表示しない。
- `external_query_transmission_consent`は将来予約であり、Phase 7で外部送信Enforcement成立とClaimしない。

UI／APIが未実装Capabilityを実行可能と誤認させる場合だけ、最小の文言／Capability Projectionを修正する。Conversation／Corpus全Export、一括Delete、TTL、Training PipelineまたはDataset Governanceを新設しない。

### P7-NW-D — User Manual Candidate／Observability

Userが実画面で確認できる短いManual Test Sheetを作成する。最低限次を含める。

1. 初期状態とRAG OFF副作用0。
2. Local Document登録。
3. 登録Documentだけで答えられる固有Factを質問。
4. CitationにLocal Source／Chunk／Digestが表示されること。
5. Reload／別Tab／Server Restart後のConversation／Citation。
6. Document更新後のRevision／回答／Citation。
7. Document削除後のCurrent検索除外とHistorical Citation保持。
8. Data Controls全Default OFF。
9. 各Consentの独立切替／Reload後の反映。
10. 未実装Capabilityと実Web未実装が虚偽成功表示されないこと。

User BrowserをClaudeが勝手に操作せず、`USER MANUAL GATE／NOT RUN`として返す。実Web検索、Public URL、NetworkまたはUser既存`runtime_data`をManual Sheetへ要求しない。

### P7-NW-E — Internal Review／Return

実装Freeze後に1 CycleのBounded Internal Reviewを行う。

```text
Requirement／Acceptance-by-Acceptance
Production Composition
False Success／False Capability Claim
Persistence／Citation Integrity
Data Controls Purpose Separation
Phase 11 Deferred Scope Leakage
```

Critical／Major／MVP Blockerが見つかった場合だけReworkし、同じ観点を再確認する。Minor、UI Polish、Hardening、性能研究およびPhase 11 Scopeは未解決へ送る。Open Finding 0を作るための探索を続けない。

Package別Recovery IndexとExact Return Handoffを作成する。最大Claimは`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`である。

## 5. Verification Contract

### 5.1 Reuse

P7-I成立Evidenceを無意味に再実行しない。

```text
Backend Full: 1924 passed / 7 deselected
Mypy: 526 source files clean
Ruff: clean
Frontend: 256 passed / typecheck / lint / build clean
Controller Focused: Backend 111 passed / Frontend 4 files 39 passed
```

### 5.2 変更時

- Docsだけの変更ならMarkdown、Path、Digest、Acceptance Mappingを確認する。
- Backend Source／Test変更時は、Project内Task-owned Tempと`--basetemp`を使い、変更範囲のFocused Test、Mypy、Ruffを実行する。
- Frontend Source／Test変更時は、Project内Task-owned npm cache／tmpを使い、Focused Test、Typecheck、Lint、Buildを実行する。
- Source変更がある場合だけ、最終Canonical Fullを1回実行する。
- Test数、Exit CodeまたはEvidenceを推測しない。

## 6. Hard Scope Exclusions

本Taskで実装・接続・実行しない。

- P7-CODEX-001〜005の実WebRework。
- Real Public Web、Real Search API、SearXNG、Braveその他Provider。
- Provider Account、Credential、Secret、Cost Plan。
- URL Fetch、Public／Private Endpoint Probe、Network Action。
- Server Canonical Web Mode、Web Evidence Chat Injection、Web Citation。
- Full Export／Delete／TTL／Dataset Cleaning／Label Governance。
- Embedding Model、Vector DB、Reranker、Retriever品質研究。
- 汎用Attachment、画像／音声／ZIP／動画処理。
- Phase 6 Known Debt。
- Phase 7 Closure、Git、Backup、RoadmapまたはPhase 8。

## 7. Execution／Stop Policy

通常のRead、Focused Test失敗、既知のWorking Tree差分、軽微なCommand修正、報告時点またはNon-blocking Findingだけで停止しない。自分で安全に訂正できる範囲は訂正して継続する。

停止するのは、次のようにUser Authorityまたは安全境界を実質的に超える場合である。

- 破壊的／不可逆Mutationが必要。
- External Network、Provider Account、Credential、SecretまたはUser既存Runtime Dataへの接触が必要。
- Project Root外への永続Mutationが必要。
- Scopeを実Web、Phase 6 Rework、Phase 8またはProduct Hardeningへ拡張しないと中心目的を達成できない。
- 同時編集により同一FileのUser／他Agent差分を安全に保全できない。

Git Mutationは行わない。作業に不要なGit Commandも実行しない。ただし、偶発的なRead-only Git Callだけを理由に、Source Mutation 0／Data Risk 0の状態で長時間Task全体を自己停止しない。事実をReturnへ記録し、技術作業を安全に継続する。

## 8. Required Return

Exact Return Handoffには次を含める。

```text
Status
Completed Work Units
Changed Paths
Non-Web Acceptance個別Disposition
External Web Deferred ID一覧
Local Corpus／Citation Production Evidence
Data Controls Production Evidence
Manual Test Sheet Path
Focused／Canonical Verification
Internal Review Finding／Rework
Known Partial／Deferred
Incident／Boundary Inventory
Active Process／Temporary Artifact
Maximum Claim
Exact Next Action: Codex Controller Review
```

Phase 7 Closure、Git、Backup、RoadmapおよびPhase 8へ進まず、Return後は停止する。
