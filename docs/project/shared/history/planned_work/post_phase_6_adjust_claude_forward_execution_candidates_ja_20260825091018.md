# Phase 6 ADJUST以降 Claude前倒し実行候補 最新版

```yaml
document_id: post_phase_6_adjust_claude_forward_execution_candidates_20260825091018
status: accepted_reservation_not_execution_authority
document_type: append_only_forward_work_candidate_catalog
recorded_at: 2026-08-25 09:10:18 JST
from: プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役／Long-running Executor
current_phase: phase_6_in_progress_adjust
phase_6_closure: blocked
phase_7_ready: false
execution_authorized: false
source_mutation_authorized: false
git_mutation_authorized: false
network_authorized: false
external_action_authorized: false
```

## 1. 目的と旧一覧との差

本文書は、Phase 3時点の
`docs/project/shared/history/planned_work/post_phase_3_claude_forward_execution_candidates_ja_20260821193804.md`
を削除または上書きせず、Phase 3〜5完了、Phase 6第7〜9 ReworkおよびUser Mac Manual Acceptance後の
最新As-builtから、Claudeへ前倒し委任可能な作業を再分類する。

旧一覧にあるPhase 4／5実装、Phase 5-EX AWSおよびPhase 9-EX DesktopはCurrent候補から除く。
Phase 4／5は完了し、AWS／Lightning／DesktopはPhase 10以降へ移動済みである。

本書は候補Catalogであり、Claudeへの実行開始、Phase開始、Source変更、Model Load、Network、Git、
Roadmap、Closureまたは外部操作のAuthorityを生成しない。実行時は別のExact Handoffを必要とする。

## 2. Current State

```text
Phase 3: COMPLETE／CLOSED
Phase 4: COMPLETE／CLOSED
Phase 5: COMPLETE／CLOSED
Phase 6: IN PROGRESS／ADJUST
Latest Automated Candidate:
  Backend 1602 passed／7 deselected
  Frontend 221 passed
  Canonical Mypy 443 files／0 issues
  Ruff／Build PASS
User Mac:
  Qwen Default／Qwen↔DeepSeek／Restart Reset PASS
  Two-tab／Conversation／Citation／Branch PASS
  Stop／DeepSeek pathological repetition prevention PASS candidate
Open Functional Blockers:
  ARGD／DAGD Semantic Rule 109件 all Deferred
  Dedicated Selene Judge unavailable
  Qwen3Guard Provider unavailable
  main_self Judge false acceptance／malformed／deadline
  Repair accepted Golden Path unavailable
  Failure／Recording correlation insufficient
Phase 6 Closure: BLOCKED
Phase 7 READY: FALSE
```

## 3. Priority A——Phase 6 Current Rework候補

このPackageは前倒しではなくCurrent Critical Pathである。ControllerがExact Requirements／Acceptance／
Mutation ScopeをFreezeし、Userが開始した場合だけClaudeへ委任できる。

### A-1 Requirement／As-built Reconciliation

- Phase 4／5からPhase 6へ送られたSemantic Requirement Lineageを列挙する。
- Current Definition Descriptor、Compiler、Point Runtime、Judge、Action Resolver、Repairの未接続箇所を特定する。
- 109件を件数Hard-codeせず、実Manifest／Plan／Rule Identityから再導出する。
- `honest Deferred display`と`implemented semantic execution`を別Acceptanceにする。

### A-2 Semantic Definition Execution

- ARGD／DAGD Semantic DescriptorをNormalized Evaluation Criteriaへ変換するAdapter／Compilerを実装する。
- Request／Turn／Point／Rule／Observation／Judge／Action／Repair／Evidenceを相関する。
- Unsupported／Unknown／Deferred／Pass／Deviationを混同しない。
- Definition名をCoreへ特別扱いせず、同Capabilityを持つCustom Definitionへ交換可能にする。

### A-3 Guardrail／Judge Provider Registry

初期候補：

```text
Main Model:
  Qwen
  DeepSeek

Guardrail Provider:
  None
  Built-in Rule／Pattern Base
  Qwen3Guard

Judge Provider:
  None
  Built-in Deterministic Evaluator
  Selene
  Qwen
  DeepSeek
```

- Provider Type、Configured、Active、Loaded、State、ReasonおよびIndependence Classを分離する。
- Main-selfは明示選択時だけ許可し、未設定時の暗黙Fallbackを禁止する。
- OFF中はDedicated Role ModelをLoadしない。
- Qwen3Guard／SeleneのExact Artifact、Definition、Backend、Decoder、Resource GateおよびEvidenceを接続する。
- Resource不足またはLoad FailureをCurrent／Activeへ捏造しない。

### A-4 Judge／Repair Runtime

- 固定30秒をModel／Deployment Profile別のJudge／Repair Budgetへ分離する。
- Queue／Lease、Load、Inference、DecodeのElapsed／Timeout Stageを記録する。
- `deadline_exceeded／malformed_output／resource_unavailable／cancelled`を理由別・回答言語別に提示する。
- User Inputの責任へ転嫁するGeneric Safe Fallbackを廃止する。
- Known Contradictionから`needs_repair → repair → rejudge → repair_accepted`を再現するFixtureを作る。
- Deadline／Cancel後のLate WorkerがFinal／Last Result／Evidenceを上書きしない。

### A-5 UI／Recording Minimum

- Main／Guardrail／Judge Providerを独立Dropdownにする。
- `None／Built-in／Model`を型付きで表示する。
- Configured ProviderとActive Providerを分離する。
- Latest RecordingへRequest ID、日時、Frozen Mode、Record Kind、Outcome、Reasonを表示する。
- Phase 9 UI予約をPhase 6へ混入させない。

### A-6 Acceptance／Return

- Focused Unit／Integration、Canonical Mypy、Ruff、Backend Full、Frontend Typecheck／Lint／Test／Buildを実行する。
- Project内Task-owned TempとCacheをExact指定する。
- 実Model TestはModel Load、Hardware、時間および停止線をExact Handoffで別Gate化する。
- Package境界ごとにRecovery Indexを作成する。
- `COMPLETE_CANDIDATE`で停止し、Phase 6 Closure、Roadmap、Git、Phase 7へ進まない。

## 4. Priority B——Phase 6中でも競合なしに前倒し可能なRead-only調査

別TaskがPhase 6 Sourceを変更していないこと、ControllerがExact Read Scopeを指定したことを条件に、
Repository内Read-onlyで実施可能である。成果物を書く場合は`shared/history/planned_work/`の新規
Append-only Candidateだけとし、Stable／Public／Current Phase Docsを変更しない。

### B-1 Phase 7 RAG As-built Inventory

- Current Documentation RAG、Citation、Conversation Persistence、Tool RoleのAs-built Map。
- Chunk、Retriever、Source、Citation、Digest、Branch／RegenerateのCurrent Contract。
- Phase 7で置換せず再利用すべきBoundaryとKnown Debt。
- RAG最終品質AcceptanceはPhase 7の新構成後に行う。

### B-2 Web Retrieval Design Inventory

- `WebSearchPort／WebFetchPort／Normalizer`のRepository-neutral Interface候補。
- `disabled／manual／automatic`と`OFF／OBSERVE／ENFORCE`の分離。
- URL／Canonical URL／Source Authority／Freshness／Digest／Citation Evidence。
- SSRF、Private Network、Redirect、Content Size、Prompt Injection、Secret／PII、Cost Gate。
- Network Call、Provider選定、Credential作成およびPackage導入は行わない。

### B-3 Data Controls Information Architecture

- Settings第三領域`データコントロール`のField／State／Consent／Purpose Matrix。
- public_web、local_corpus、user_provided、human_feedback、synthetic_generated等のSource Class。
- Retention、Export、Delete、外部送信、Evaluation利用、将来Training利用の分離。
- 他製品のTrade Dressを複製せずMARGPA固有UI候補を作る。

### B-4 Generic File Attachment Sizing

- Icon／Drag & Drop、Image、WAV、Markdown、JSON、Document、ZIP等のTransport／Storage／Parser Matrix。
- Upload、Persistence、RAG Corpus、Model-native Multimodalを分離する。
- Conversation Schema、Citation、Recording、Public／Basic、Securityへの影響を見積もる。
- Phase 7へ局所前倒し可能か、Phase 10以降のPhase級工事かを判定候補として返す。
- File Upload、Archive展開、Parser実行およびUser実File接触は行わない。

## 5. Priority C——Phase 6 Closure後に前倒し可能なPhase 7設計

Phase 6 ClosureとPhase 7 READY後、Controllerが設計Authorityを明示した場合に限る。

1. Phase 7 Requirements／Architecture／ADR候補。
2. RAG Component、Embedding、Index、Retriever、Citation Evidence、Document Lifecycle。
3. Web Retrieval、Data Source、Data Controls、Document Injection Governance。
4. Generic Attachment Sizing結果の採用／延期。
5. Execution Plan、細分化Work Unit、Acceptance Matrix、Manual Test Matrix。
6. Claude Long-running Execution Handoff候補。

Phase 7の正式Freeze、開始宣言、Network／Provider／Credential、Package Install、Model Downloadおよび
Source実装はController／User Gateに残す。

## 6. Priority D——Phase 8／9へ前倒し可能な設計候補

### Phase 8

- Agent／Tool／Memory／HandoffのCurrent Port Inventory。
- `constitution/` Runtime Packageと`docs/project/shared/constitution/`開発運用体系の非混同Matrix。
- Tool Authority、Human Approval、Side Effect、Memory Retention、Handoff AuthorityのAcceptance候補。
- MARGPA Constitutionの`OFF／OBSERVE／ENFORCE`研究契約候補。

### Phase 9

- Experiment／Run／Request／Attempt／Repair Identity Schema候補。
- Main／Guardrail／Judge Provider比較Matrix。
- Strict／Progressive ENFORCEのTrade-off／Evidence／Acceptance候補。
- Right-side Governance Trace Observatoryの情報構造。
- Context Compaction／Snapshot／Recovery／RehydrationのTest Matrix。
- Phase 9 Closure手前UI Debt Inventoryの再確認。

これらはDesign Candidateに限定し、Phase 8／9のSourceまたはStable Docsを先行変更しない。

## 7. Phase 10以降へ送るためのRead-only候補

- AWS／Cloud／Lightning／DesktopのGate、Cost、Security、Rollback設計。
- Enterprise／Licensed Data Extension Boundary。
- Dataset Cleaning、Label Governance、Eligibility、Adjudication研究。
- Video Multimodal、Long Context、RoPE／YaRN、KV Cache、Hardware自動適応。
- Portable Development Governance PackageのSanitization／Manifest候補。

Cloud Resource、Billing、Network公開、Credential、Model Download、外部ProjectおよびRepository Root外操作は
候補整理だけでも自己許可しない。

## 8. 前倒し禁止／Human・Controller Gate

- Current Phase Sourceと競合するMutation。
- Stable／Public Roadmap、Current Phase Index、Completion Statusの最終更新。
- Phase Completion、Formal Deferral、次Phase READY／開始宣言。
- Git Status／Diff／Stage／Commit／Push／Tag／Release。Exact HandoffでReadを含め明示されない限り触れない。
- User実`runtime_data`、Chat、Citation、個人情報。
- `.claude`、`.codex`その他Provider Memoryの作成、読取、利用または保存。
- Project Root外Read／Write／Temp／Cache／Log／`/dev/null`。
- Network、Package Install、Download、AWS、Lightning、Public URL、External Messaging。
- Model Artifactの削除、上書き、PromotionまたはDefault変更。
- Backup完了の代理主張。

## 9. Long-running／Recovery Contract候補

Claudeへ実行を委任する場合、Exact Handoffに次を含める。

1. Mandatory Reading SetとDigest／Revision。
2. Authorized Root／Read／Write／Git／Network／Model／User Data Scope。
3. Project内Task-owned Temp、Cache、Log Path。
4. Package／Work UnitごとのAcceptanceとRecovery Index作成点。
5. Auto-compaction、5時間制限、Process中断後の再読込順序。
6. Status報告は停止理由にせず、True Stop Condition以外で自走継続する規則。
7. Incidentは0へ捏造せず、成立範囲を保持して差分再開する規則。
8. `COMPLETE_CANDIDATE`返却線とController Independent Review。

## 10. 推奨実行順

```text
Current:
  Controller Exact Phase 6 Rework Freeze
  → ClaudeまたはCodex設計者兼実装者役がA-1〜A-6
  → Controller Independent Review
  → Exact Rework往復
  → User Mac Manual Acceptance
  → Phase 6 Minimal Closure

After Phase 6 Closure:
  Phase 7 READY
  → Generic Attachment Sizing
  → Phase 7 Exact Design
  → Long-running Implementation
```

Claudeが作業中、Controllerは原則待機し、Completion／STOPPED_SAFE／True Input Gateの返却後にReviewする。
同一差分を常時並行Reviewして利用可能量を二重消費しない。

## 11. Return Contract

各実行の返却には最低限次を含める。

```text
Status
Completed／Unfinished Work Unit
Exact Changed Files
Verification／Evidence Grade
Open Critical／Major／Non-critical
Incident／Root／Provider Memory／Git／Network／User Data Inventory
Task-owned Temporary
Active Process／Model Load
Exact Next Action
Controller Independent Review Requested
```

前倒し候補の整理速度、Test数またはCOMPLETE_CANDIDATEを、Phase CompletionまたはUser Acceptanceと
同一視しない。
