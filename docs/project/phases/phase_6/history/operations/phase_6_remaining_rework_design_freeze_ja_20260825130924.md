# Phase 6 Remaining Rework 設計Freeze（P6-RR-DESIGN）

```yaml
document_id: phase_6_remaining_rework_design_freeze_20260825130924
status: controller_frozen_pending_user_activation
phase: phase_6
owner: プロジェクト責任者兼設計統括者役
created_at: 2026-08-25 13:09:24 JST
implementation_authority: false
phase_6_closure: blocked_until_acceptance
supersedes_nothing: true
```

## 1. 結論

Phase 6の残件は、小さなUI修正ではなく、MARGPA Governance DefinitionのSemantic Ruleを実行経路へ接続し、
Main、Guardrail、Judgeを独立したProviderとして選択・起動・記録できるようにする是正である。

```text
Definition
→ Trusted Adapter / Descriptor
→ Semantic Criterion
→ Selection / Evaluation
→ Pass / Deviation / Unknown / Deferred with reason
→ Conflict / Action Resolution
→ Repair / Safe Fallback / Final
→ Correlated Evidence
```

2026-08-31前後という見込みは、ClaudeとCodexの利用可能量回復見込みであり、実装開始権限ではない。
Userの明示的な開始宣言があるまで、本書は設計Freezeとしてのみ有効である。

## 2. 正本とRequirement Lineage

本設計は次をLosslessに継承する。

- Phase 4からPhase 6へ送られたARGD／DAGD Semantic Rule実行責務。
- Phase 5からPhase 6へ送られた意味的幻覚、知ったかぶり、根拠なき断定、Evidence矛盾のJudge／Repair責務。
- P6-GOV-015のController反省と、`109 Deferred`の継続をClosure Blockerとする判定。
- User Mac Manual Acceptanceで確認されたMain-self Judge、Selene／Qwen3Guard未接続、固定30秒Timeout、
  汎用Safe Fallback、Recording相関不足。
- 統合予約書
  `phase_6_manual_acceptance_consolidated_rework_and_phase_9_ui_research_reservation_ja_20260825090037.md`
  にあるPhase 6とPhase 9の境界。

## 3. As-built Gap

### 3.1 Semantic Governance

- Reference AdapterはARGDの`response_generation_priorities`とDAGDの`prohibited_behaviors`から
  `ExecutionDescriptor`を作る。
- Current Deterministic Evaluatorは構造的Ruleのみ評価し、Semantic Descriptorを全件Deferredにする。
- Live Judgeは固定CriteriaをMain Model自身へ渡す別経路で、Descriptor Identityを受け取らない。
- そのため`Selected 109 / Deferred 109`は正しい表示だが、Phase 6の完成状態ではない。

### 3.2 Provider

- Runtime Model ControlはMain Roleだけを切り替える。
- JudgeはMain Model Adapterを再利用する`main_self`である。
- GuardrailはRule／Pattern Baseのみで、Safety Model PortはあるがProduction AdapterはUnavailableである。
- Selene GGUFとQwen3Guard GGUFはLocalにあるが、実Runtimeに登録・起動・監視されていない。

### 3.3 Failure / Evidence

- Judge／Repairは固定30秒Budgetで、Local MacのModel Load／Inferenceと分離されていない。
- Timeout、Malformed Output、Provider Unavailableなどが、利用者にとって原因を検証できる文言になっていない。
- Recordingは成否のみで、Request ID、時刻、Frozen Mode、Provider、Outcome、Reasonの相関がUIに足りない。

## 4. Scope Freeze

### 4.1 Phase 6で必ず実装する

1. ARGD／DAGD Semantic DescriptorのCriterion化と実評価経路。
2. Main／Guardrail／Judge Providerの独立選択、Configured／Active分離、明示的None。
3. Selene JudgeとQwen3Guard-Gen Adapterの実接続。
4. Main-selfの暗黙Fallback廃止。Qwen／DeepSeekをJudgeに使う場合も明示選択とする。
5. Role別Model Lifecycle、Resource Gate、Cancel／Shutdown／Switch競合防止。
6. Stage別Budget、理由別／言語別Failure、選択JudgeによるRepair後再評価。
7. Recordingの相関表示と、実行されたRule／Provider／Actionを追えるEvidence。
8. 上記のAPI／Advanced Mode最小UI、Regression、Real Model／User Manual Gate。

### 4.2 Phase 9へ送る

- Advanced Modeの並び替え、区切り線、Margin、Sidebar表示改良、OFF時文言などの表示磨き込み。
- Context 16384のMac実測昇格、Model別Context／Max New Tokens保持。
- Strict ENFORCEとProgressive ENFORCEの研究Mode、右側Governance Trace Panel。
- Raw／Final研究Captureと本格的Recording Observatory。

## 5. Semantic Criterion Contract

`SemanticCriterion` は少なくとも次を不変に保持する。

```text
criterion_id
descriptor_id
source_definition_id
source_definition_digest
source_pointer
source_text_digest
governance_point
evaluation_stage (pre / post / both)
evaluation_method
severity_policy
recommended_action_policy
evidence_requirements
```

- `109`は固定値にしない。Canonical Definitionの実測結果として再導出する。
- ARGD／DAGD固有解釈はTrusted Adapterに閉じ込め、CoreはNormalized Criterionだけを扱う。
- Unknown、Evaluator不在、Budget不足、Provider不在をPassにしない。それぞれTyped Resultにする。
- 一度のTurnで同一Criterionを二重評価せず、Structural ObservationとSemantic ObservationはIdentity付きでMergeする。
- Batch化しても、各Criterionの判定、根拠、確信度、Failure Reasonを独立に復元できること。

## 6. Mode Matrix

| Main Governance | Judge | Semantic評価 | Finalへの介入 |
|---|---|---|---|
| OFF | any | 実行しない | なし |
| OBSERVE | OFF／None | `not_evaluated_judge_off` | なし |
| OBSERVE | OBSERVE／ENFORCE | 実行・記録 | なし |
| ENFORCE | OFF／None／Unavailable | ActivationをReject | False ENFORCE禁止 |
| ENFORCE | OBSERVE | ActivationをReject、またはMainをOBSERVEに留める | なし |
| ENFORCE | ENFORCE | 実行・Action Resolution | Repair／Fallback／Final |

- Repair ENFORCEが必要なActionでRepairがOFF／Unavailableなら、修復成功を捗造せずSafe Fallbackにする。
- Guardrail Modelの結果はDeterministic Detectorに対して加算的であり、既存Matchを消してはならない。

## 7. Provider Selection Contract

### 7.1 選択肢

```text
Main Model:
  - main.qwen3-4b-q4-k-m
  - main.deepseek-r1-0528-qwen3-8b-q4-k-m

Guardrail Provider:
  - none
  - built_in.rule_pattern
  - guard.qwen3guard-gen-0.6b-q8-0

LLM-as-a-Judge Provider:
  - none
  - built_in.deterministic
  - judge.selene-1-mini-llama-3.1-8b-q5-k-m
  - main.qwen3-4b-q4-k-m
  - main.deepseek-r1-0528-qwen3-8b-q4-k-m
```

### 7.2 Default

```text
Configured Main      : Qwen
Configured Guardrail : Qwen3Guard
Configured Judge     : Selene
Main / Guard / Judge / Repair Mode: OFF
Active Guardrail / Active Judge Model: none
```

Mode OFFの間はDedicated ModelをLoadしない。OBSERVE／ENFORCEへのActivation時にConfigured Providerを
Preflightし、成功した場合だけActiveにする。起動失敗は前Revisionを保持し、別Providerへ暗黙Fallbackしない。

`Configured Provider != Active Provider`を正常状態とし、UI／API／Evidenceで両方を表示する。

### 7.3 Local Artifact Identity

| Role | Artifact | Size | SHA-512 |
|---|---|---:|---|
| Judge | `models/judge/selene-1-mini-llama-3.1-8b/gguf/Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf` | 5,732,992,896 | `6d5472911fc347d51a73e57077dd34353c3e134a0af67b0dbe4e4df7d980e3246f0253ee16e5a241a41904d37e73ab3ba11ce5d800de37b9adddb2ada9b6c50d` |
| Guard | `models/guard/qwen3guard-gen-0.6b/gguf/Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf` | 804,753,472 | `0b8d213fd487980ce2667acaaf042d228486d9b467cd90ab6bfbe490527fa1b51d7a318af593bc920d59f5b22759196c09eaf8cba1974766ab170e6d6f6c19cb` |

これらはDesign時点のRead-only実測であり、Runtime Load／品質AcceptanceのPASSを意味しない。

## 8. Role Lifecycle / Resource / Scheduling

- Main Controllerの責務を無理に拡大せず、Role別Adapterを統括するProvider Lifecycle Managerを置く。
- Provider SelectionはRevision＋DigestによるCAS Transactionとする。
- Stateは少なくとも`none / unavailable / invalid / loading / active / degraded / failed`を分離する。
- Turn開始時にMain／Guard／Judge／Mode／BudgetをFrozen Snapshotにし、Turn中の変更を混入させない。
- OFFへ戻す場合はActive Turnの終了後にUnloadする。Main Switch／Shutdown／Cancelと競合させない。
- Local Macでは常駐を推測せず、実測Memory GateとSequential Loadを使う。Main、Selene、Qwen3Guardの同時常駐を前提にしない。
- 実Model Loadが不可能でも、`Unavailable`を正しく示しBuilt-inへ勝手に切り替えないことは受入対象である。

## 9. Selene Judge Contract

- SeleneはDedicated Judge Providerとして実装する。
- Official Selene prompt templateは、使うTemplateの種類、Upstream Revision、本文DigestをManifestに固定する。
  記憶から似たPromptを作って代用しない。
- ARGD／DAGD Criterionは`classification`、`classification-with-reference`、`absolute-scoring`等の
  どの評価Methodへ変換したかをEvidenceに残す。
- DecoderはTyped Resultを返し、Malformed／Partial／Contradictory OutputをAcceptしない。
- Qwen／DeepSeekをJudgeとして明示選択した場合は、同一Modelか否かを
  `self / independent_same_family / independent_other_model`として表示・記録する。

Official Selene Prompt Repository:
`https://github.com/atla-ai/selene-mini/tree/main/prompt-templates`

## 10. Qwen3Guard Contract

- Local ArtifactはQwen3Guard-Genであり、Token-level Stream Variantではない。
- Official Outputの`Safety: Safe|Controversial|Unsafe`、`Categories`、Response時の`Refusal: Yes|No`を
  Exact Parserで解釈する。
- 第一対象は`guardrail.input / output_candidate / context_source`。Streaming中のToken-level分類は本Scopeで捗造しない。
- Model結果はRule／Pattern Detectionに加算し、両者のIdentity／Severity／Category／Actionを保持する。
- Unknown Category／Malformed／TimeoutはTyped Unknownとし、Safeへ変換しない。

Official Model Contract:
`https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B`

## 11. Budget / Failure / Repair

### 11.1 Budget

固定30秒は廃止し、Role／Provider／Hardware Profileごとに次を分離する。

```text
load_budget
prompt_build_budget
inference_budget
decode_budget
repair_generation_budget
rejudge_budget
cancel_grace
```

Local Macの初期Candidateは、Load 180秒、Judge Inference 120秒、Decode 5秒、Repair 180秒、
Rejudge 120秒、Cancel Grace 10秒とする。ただしこれは
`CONFIGURED_NOT_HARDWARE_VERIFIED`であり、実測で昇格または修正する。

### 11.2 Failure Presentation

Failureごとに一意のReason Codeと、Turn開始時の回答言語に応じた文言を使う。

- `judge_timeout`: 判定が設定時間内に完了しなかったことを明示する。
- `malformed_output`: Judge応答を解釈できなかったと明示する。
- `provider_unavailable`: 選択ProviderをLoad／Useできなかったと明示する。
- `evaluation_inconclusive`: Evidence不足等で判定不能と明示する。
- `repair_exhausted`: Repair Budgetを使い切ったと明示する。

汎用的な「安全に検証できなかった」へ全Failureを潰さず、利用者の入力が悪いと読める文言を避ける。

### 11.3 Repair

- Judgeが`needs_repair`を返し、Repair ModeがENFORCEである場合のみRepairを実行する。
- RepairはMain ModelへCriterion、根拠、Evidence、禁止された誤りを再注入する。
- Repair後は必ず選択されたJudge Providerで再評価する。Main-selfへ戻さない。
- Budget上限後はReason付きFallbackとし、修復できたと主張しない。

## 12. Recording / Observability Minimum

Phase 9の本格Trace Panelより前でも、Advanced Modeに次を表示する。

```text
latest_request_id
started_at / completed_at
frozen_main_mode / frozen_guard_mode / frozen_judge_mode / frozen_repair_mode / recording_mode
configured_provider / active_provider
criteria_selected / evaluated / passed / deviated / unknown / deferred_by_reason
judge_outcome / repair_outcome / final_disposition
recording_kind / recording_outcome / failure_reason
```

OFFにした後も過去のLast Resultを実行中のように見せず、`disabled`とHistorical Last Resultを分離する。

## 13. Core Invariants

1. Definitionの存在を実行、選択をPass、Judgeの推奨をAuthorityと同一視しない。
2. Main Model、Judge Model、Guardrail ModelのIdentityを同一に見せない。
3. ConfiguredをActiveと言わず、UnavailableをNoneと言わない。
4. Semantic EvaluatorがないRuleをPassにしない。
5. Deterministic MatchをModelのSafe判定で消さない。
6. Late Worker、Cancelled Turn、Rejected FinalによるResponse／Last Result／Evidenceの後書きを許さない。
7. Model I/O LeaseとEvidence I/Oを分離する。
8. OFFを既定とし、Researcherの明示的なMode選択でのみ介入する。
9. Test Pass数をSemantic Acceptanceの代わりにしない。
10. User Manual Acceptanceが通るまでPhase 6 Closureを宣言しない。

## 14. Freeze後の変更

本FreezeのScopeを変更する場合は、UserまたはControllerのAppend-only Correctionを必要とする。
Executorは「重い」「時間がかかる」「実ModelがUnavailable」を理由にScopeを黙って縮小せず、
Typed UnavailableとEvidenceを作り、独立して完了可能なWork Unitを継続する。
