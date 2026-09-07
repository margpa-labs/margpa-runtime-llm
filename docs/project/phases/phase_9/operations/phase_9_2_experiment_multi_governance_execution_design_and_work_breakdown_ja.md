# Phase 9-2 — Experiment／Multi-Governance実行設計・工程分解

```yaml
document_id: phase_9_2_experiment_multi_governance_execution_design_and_work_breakdown
document_type: phase_program_execution_design_and_work_breakdown
document_state: frozen_ready_after_user_backup
phase: phase_9
program: phase_9_2
language: ja
created_at: 2026-09-06 21:16:43 JST
decision_authority: user
authority_owner: Nazuna Research
controller: codex
implementation_candidate: claude_code
entry_gate: user_backup_completed_and_explicit_resume
phase_9_1_status: complete_user_accepted_without_full_closure
phase_9_3_authorized: false
phase_10_authorized: false
git_write_authorized: false
```

## 1. 目的

Phase 9-2は、Phase 9-1で成立したMain／Judge／Guard／GD Semantic／Repair／Recordingの疎結合基盤を再利用し、同一Caseへ異なる構成を適用して比較できる研究実験Platformを成立させる。

完成条件は、単一Modelの回答品質向上ではない。次を同じIdentity Chain、同じCase、明示的なVariantおよび比較可能なEvidenceとして扱えることである。

```text
Main／Judge／Guard／GD／RAG／Repair／Mode
Source Freshness／Authority／Provenance
Strict NO_HIT／Model Callあり
Strict Buffer／Progressive Presentation
Human Review／LLM Review／定量Metric／定性Observation
```

## 2. Phase 9-1からの入口判断

2026-09-06 User Mac最終実画面Recheckにより、Gemmaを独立Judgeとして次が成立した。

- Judge単独OBSERVE。
- Judge起点Repair／Rejudge／採用。
- Main Governance起点Repair／Rejudge／採用。
- `judge_and_main`。
- 32 Criterion評価、109件Count保存、Recording、Guard、OFF／Unload。

Phase 9-1はUser判断で完了とし、通常Full Closureは挟まない。Phase 9-2のSource Mutation開始前にUserがCurrent Working TreeのBackupを取得し、完了を明示する。

Phase 9-1の未解決Provider品質は、Phase 9-2を止めない。

```text
Default representative path:
  Main  = Qwen3 4B
  Judge = Gemma 4 E2B
  Guard = Qwen3Guard 0.6B

Non-blocking alternatives:
  Qwen Self Judge Repair非収束
  DeepSeek JudgeのMain mismatchによるLoad前拒否
  Selene未解決／保留
```

## 3. 再設計方針

旧6 Packageの主題は維持するが、責任境界と依存順を次へ固定する。

```text
P9-2-A  Experiment Core
   ↓
P9-2-B  Evaluation Core
   ↓
P9-2-C  Variant Composition／Multi-Governance
   ↓
P9-2-D  Freshness／NO_HIT／Belief Revision Case Pack
   ↓
P9-2-E  Execution Trace／Strict・Progressive Presentation
   ↓
P9-2-F  Comparison／Verification／User Candidate
```

変更点は次である。

1. 実験Identityと保存を先に作り、後段が独自`run_id`や独自JSONを増殖させない。
2. Evaluationを実Model／Judgeから分離し、Human／LLM／Metricを別Resultとして保持する。
3. 組合せ実行を既存Componentの上位Adapterとし、Main／Judge／Guard等の内部契約を再実装しない。
4. Freshness／NO_HIT／Belief Revisionを、汎用Core完成後のVersioned Case Packとして作る。
5. ProgressiveはPhase 9-2専用Projectionで比較し、通常Chat全体やPhase 10右Panelを先取りしない。
6. 全組合せを実Modelで総当たりせず、Fixture Matrixで網羅し、実Modelは代表経路だけを有界実行する。

## 4. 最上位Invariant

### 4.1 Component疎結合

```text
Component OFF／不在／Unsupported
  => 当該ComponentのCall／Mutation／Evidence／Authority 0
  => 他Componentの起動条件、Turn Context、Evidenceを欠損させない
```

Experiment CoreはMain Governance、Judge、Guard、RAGまたは特定GDを必須依存にしない。各ComponentはPort経由のVariant Actorであり、追加・削除・交換でCore Schemaを変更しない。

### 4.2 Live Runtime非破壊

- Experiment Variantは開始時にEffective ConfigをFreezeする。
- 実行途中のUI設定変更を当該Runへ混入させない。
- Experiment実行のために通常ChatのConfigured／Active Modeを無言変更しない。
- Variant間でConversation、Cache、Criterion、Evidence、Provider Leaseを共有しない。
- 実験失敗を通常Chatまたは別VariantのCurrent ResultへPublishしない。

### 4.3 Truthful Comparison

- `NOT_RUN`、`UNAVAILABLE`、`UNSUPPORTED`、`FAILED`を0点の成功Runへ変換しない。
- Self JudgeとIndependent Judgeを分離する。
- Human ReviewとLLM Reviewを分離する。
- Model品質、Retrieval品質、Governance判断、Runtime Failureを別Metric／Observationにする。
- Raw Output、Final Output、Applied Action、Repair Candidateを同一内容として扱わない。

### 4.4 Resource

- 16GB Local Macでは実Model Variantを逐次実行する。
- Main＋Gemma＋Guardの並列Experimentは行わない。
- 全MatrixはFixture／Deterministic Adapterで網羅し、実機は代表Runだけとする。
- Model Unload、Cancel、DeadlineおよびProcess残存確認はPhase 9-1契約を再利用する。

## 5. Canonical Domain Candidate

Model固有FieldをCoreへ直結せず、最低限次を独立Contractとする。

```text
ExperimentIdentity
  experiment_id
  owner_scope
  created_at

EvaluationCaseManifest
  case_id／revision／input／evidence／expected_observations

ExperimentPlan
  case_revision
  variant_descriptors
  execution_order
  budget／deadline／stop_policy

EffectiveConfigurationSnapshot
  main／judge／guard／governance／rag／repair／recording
  provider／artifact／definition／plan digest

VariantRun
  run_id／experiment_id／variant_id／request_id
  state／started／completed／failure

EvaluationObservation
  evaluator_kind = metric | human | llm_judge | deterministic
  rubric_revision／outcome／score／reason／evidence_refs

GovernanceCompositionResult
  selected／suppressed／conflict／routing／actions／repair_propagation

BeliefRevisionObservation
  historical_claim／current_source／user_correction／final_claim

ExecutionTraceProjection
  ordered_stage／call_count／call_0_reason／latency／disposition
```

Canonical JSONとDigest規約を一つにし、Dict順序、時刻またはProcess固有値で同一PlanのDigestが揺れないようにする。

## 6. P9-2-A — Experiment Core

### A1. Identity／Plan

- Experiment／Run／Variant／Requestを別IDにする。
- 同一ExperimentでCase RevisionとVariant集合をFreezeする。
- 重複ID、空ID、未知Variant、Plan Digest不一致をTyped Rejectする。

### A2. Config Snapshot／Digest

- 現行`EffectiveConfigurationSnapshot`を再利用またはAdapterで正規化する。
- Configured／Active／Executedを混ぜない。
- Model Artifact、Definition、Case、PlanのDigestを分ける。
- Secret、絶対User Path、認証情報をSnapshotへ入れない。

### A3. Run Lifecycle／Persistence

- `planned／running／completed／failed／cancelled`を一方向遷移にする。
- 同一RunのTerminal結果を二重Publishしない。
- Restart後にExperiment／Variant／Raw Evidence／Comparisonを読めるStoreを用意する。
- Testは`tmp_path`を使い、Userの実`runtime_data`を自動変更しない。

### A4. API

最低限、Plan作成、Run開始、状態取得、Cancel、結果取得を提供する。Phase 10右Panel向け最終APIへ固定せず、Versioned Port／DTOとする。

## 7. P9-2-B — Evaluation Core

### B1. Dataset／Case Manifest

- Case ID、Revision、入力、Source Evidence、期待する観測をVersion化する。
- 正解を一つへ固定できないCaseは、許容範囲とHuman Review必要性を明示する。
- Test文言は中立な`ALPHA`等を使い、固有人物名をFixture正本にしない。

### B2. Metric／Rubric

最低限、成功状態、Latency、Call Count、Deviation、Repair採用、False Positive、False Grounding、Correction Acceptanceを測定する。

### B3. Reviewer Identity

- Deterministic Metric、Human Review、Self Judge、Independent Judgeを別Recordにする。
- `evaluator_kind`と実Provider Identityを保存する。
- Human未実施をLLM評価で代替して`human_pass`と表示しない。

### B4. Baseline／Regression／Ablation

同一CaseへBaselineと1要素差Variantを適用し、複数要素を同時変更した結果を単一要因の効果と主張しない。

## 8. P9-2-C — Variant Composition／Multi-Governance

### C1. Variant Descriptor

次をID参照で組み合わせる。

```text
Main Provider
Judge Provider／Mode
Guard Provider／Mode
Main Governance Mode
Definition／GD Set
RAG Mode／Source Set
Repair Mode
Recording Mode
Presentation Mode
```

### C2. Actor Adapter

既存Conversation、Judge、Guard、Runtime Governance、RAG、Repair、RecordingをPortへ包み、Experiment Coreが個別Bootstrap Objectを直接操作しない。

### C3. Independence Matrix

Fixtureで最低限次を確認する。

- 全Component OFF Baseline。
- JudgeだけOBSERVE／ENFORCE。
- GuardだけOBSERVE／ENFORCE。
- Main GovernanceだけOBSERVE。
- Main Governance＋Judge＋Repair。
- RAGだけON／OFF。
- 各Component absent／unavailable時も他Componentが成立。

### C4. Multi-Governance Conflict／Routing

- Multiple Definitionの一致、Conflict、Suppressionを別Outcomeにする。
- Manual／Static／Dynamic RoutingをStrategy Adapterとして比較する。
- PriorityとAuthorityの根拠をResultへ残す。
- Repair要求元を`judge／main_governance／judge_and_main／other_registered_actor`として追跡し、未登録Actorを暗黙許可しない。

### C5. Isolation

Variant AのContext、Provider Result、Late ResultまたはCancellationがVariant Bへ混入しない。並行性はFixtureで検証し、Local実Modelは逐次実行する。

## 9. P9-2-D — Semantic Research Case Pack

### D1. Freshness

- Historical Conversation ClaimとCurrent Source Revisionを分離する。
- Source更新／削除後も過去Turn／Citationを改変しない。
- Current Factを求める新TurnではCurrent Evidenceを優先する。

### D2. False-positive RAG／Strict NO_HIT

同一質問で次を比較する。

1. RAG OFF。
2. RAG ON＋Relevant Hit。
3. RAG ON＋無関係Hit。
4. RAG ON＋NO_HIT＋Model Callあり。
5. Strict NO_HIT＋Main Model Call 0＋設定言語の決定論的回答。

Strict NO_HITはExperiment Variantとして実装し、通常Chatの既定動作を無断変更しない。

### D3. Source Authority／Correction／Belief Revision

Source Provenance、Revision、User Correction、Historical Assistant Claimを別Authorityとして記録し、訂正前後の最終Claimと根拠を比較する。

### D4. False Improvement

Phase 9-1で観測した「機械的Repair成功だが意味的には誤り」を再現可能な中立Caseにし、Runtime SuccessとHuman Semantic Successを別Outcomeにする。

## 10. P9-2-E — Execution Trace／Presentation

### E1. Model Call 0 Trace

Manual URL Fail-closed、Strict NO_HIT、Guard入力Short-circuitで、Main／Judge／RepairのCall CountとCall 0理由を記録する。Call 0をUI文言だけで推定せず、実Adapter Call Counterまたは実行Evidenceで裏付ける。

### E2. Strict Buffer

未検証Candidateを表示せず、Judge／Repair後にFinalだけを確定するVariantを持つ。

### E3. Progressive Presentation

`started／retrieving／generating／evaluating／repairing／finalized`等の状態を表示し、未検証ChunkとFinalを区別する。既表示Tokenを回収できるとは主張しない。

### E4. 最小UI

Phase 9-2では、Preset Case選択、Variant選択、実行／Cancel、状態、比較表、詳細Evidenceを確認できる最小Experiment画面だけを作る。Settings／Sidebar／Main Chat／右側検証Panelの大改造はPhase 10へ残す。

## 11. P9-2-F — Comparison／Verification／User Candidate

### F1. Comparison Report

同一Case Revision、Variant差、Runtime状態、Metric、Human／LLM評価、Failure、Raw Evidence Pointerを一つのReportへまとめる。

### F2. Fixture Matrix

P9-REQ-201〜209およびP9-ACC-039〜045を、Deterministic Fixtureで全件機械検証する。

### F3. 実Model Evidence

Fixture／Static検証後に限り、Main Qwen、Gemma Judge、Qwen3Guardの代表Variantを最大3 Top-level Experiment Run、逐次実行する。SeleneとDeepSeek Judgeは実行しない。Memory Pressure、Swap、Process残存またはUnload失敗があれば追加実行を止める。

### F4. Internal Review

- Review A：Identity、Component疎結合、Authority、Variant Isolation、Persistence。
- Review B：Metric Oracle、False Success、Freshness、Call 0、Strict／Progressive Truthfulness。

同じ観点の反復Reviewで無限Reworkしない。Confirmed Critical／Major／MVP Blockerだけを修正し、Provider品質とUI Polishを未解決へ分離する。

### F5. Return Point

ClaudeはExact ReturnとRecoveryを新規Pathへ作成し、`P9_2_USER_MANUAL_CANDIDATE`以下の最大Claimで停止する。Phase 9-2 Complete、Phase 9-3開始、Phase 9 Closureを自己承認しない。

## 12. Acceptance Mapping

| Requirement／Acceptance | 主Package |
|---|---|
| P9-REQ-201／P9-ACC-039 | A |
| P9-REQ-202／P9-ACC-040 | C |
| P9-REQ-203／P9-ACC-045 | B／F |
| P9-REQ-204／P9-ACC-041 | C |
| P9-REQ-205〜207／P9-ACC-042〜043 | D |
| P9-REQ-208 | E |
| P9-REQ-209／P9-ACC-044 | E |

Phase 9-2のUser Candidateには全行のEvidenceが必要である。一部Providerの失敗を隠さず、代表経路が成立している場合はProvider固有未解決として分離できる。

## 13. Verification Strategy

```text
各Work Unit:
  Focused Unit／Integration

各Package末:
  当該Package間Integration

最終候補前:
  Backend Non-model Full Suite 1回
  Ruff
  Canonical Mypy（既存Baselineとの差分）
  Frontend Test／Typecheck／Lint／Build
  実Model代表Run
  Review A／B
```

Full Suiteを各小修正ごとに反復しない。Testを弱める、Skipで成功扱いにする、FailureをUnknownへ潰す、既存Baselineを無断更新することは禁止する。

## 14. Scope外

- Phase 9-1のQwen／DeepSeek／Selene Provider固有修復。
- 全Model／全Modeの実機総当たり。
- General Web Search、外部Search Provider、Network Access。
- Phase 9-3 Context Compaction／Recovery。
- Phase 10 Docs統合、Constitution、PADG、右Panel／全体UI改造。
- Phase 11以降のJudge非依存Structural Governance。
- Enterprise Hardening、Cloud、Home Server、正式Dev Agent Level。
- Git add／commit／push／stash／reset。

## 15. True Stop

次の場合だけLong Runを停止し、既成部分と正確なBlockerをReturnする。

- User Backup完了が明示されていない。
- Existing Dirty Working Treeの保持対象と新変更が判別できない。
- User Data破損、回復不能なPersistence MutationまたはProject Root外Mutationが必要。
- 新しいNetwork／License／Cost／Model取得Authorityが必要。
- 実ModelがMacを不安定化し、安全なUnload／停止ができない。
- Phase 9-1の成立済みGolden Pathを壊し、局所修正で回復できない。

単一Fixture Failure、既知Provider品質、Minor UI Finding、Mypy既存Baselineまたは後続Package未着手だけでは事実を隠さず、可能な範囲まで進めてPartial Returnする。
