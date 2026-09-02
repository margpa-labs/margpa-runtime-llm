# Codex Controller Phase 9-1 User Manual UI Observability Hallucination／説明不足／User Cost Failure Evidence

```yaml
document_id: codex_controller_phase_9_1_user_manual_ui_observability_hallucination_and_user_cost_failure_evidence_20260901173556
document_type: append_only_controller_failure_evidence
document_state: final_append_only_failure_evidence
language: ja
created_at: 2026-09-01T17:35:56+09:00
provider: codex
role: project_controller_and_design_governance
phase: phase_9
program: phase_9_1
failure_class:
  - ui_observability_hallucination
  - backend_acceptance_misrepresented_as_user_visible_manual_check
  - terminal_and_ui_boundary_explanation_failure
  - undefined_jargon_and_ambiguous_instruction
  - redundant_manual_verification
  - dependency_order_failure_in_manual_test_plan
  - user_attention_and_local_hardware_cost
severity: major_controller_manual_acceptance_design_failure
source_mutation: none
data_loss: none_observed
git_mutation: none
user_manual_work_wasted: true
local_hardware_load_increased: true
phase_9_1_result_assessment_in_this_document: intentionally_deferred
responsibility: codex_controller
```

## 1. Executive Finding

Codex Controllerは、UserからPhase 9-1の現時点で可能な実画面確認項目を求められた際、Backend Test、Source Contract、Terminal Logまたは将来のObservability UIでしか確認できない事項を、現在の実画面に存在するManual確認項目として提示した。

Userが実際の画面を操作した結果、次の種類の確認項目が多数存在しないことが判明した。

- Model Call 0。
- Worker Drain／Tracked Worker残存0。
- Late Result／Late Publish 0。
- Cancellation Token伝播。
- Model／Artifact／Manifestの詳細Identity。
- Preflight、Artifact Check、Load、Prompt Build、Inference、Strict Decode、Evidence Projectionの段階別状態。
- Repair Candidateの内部Identity。
- Whole-stage Deadline／Maximum Repairの内部値。
- GuardのExecuted Provider専用表示。
- Guard Category／Safety／Refusal Strict Decodeの内部結果。
- Current Judge Runが明示的に「実行なし」となる専用表示。

これらの概念自体はSource／Test上に存在するものを含む。しかし、Userへ渡したものは「実画面テスト項目」であり、現在UIから確認できない以上、Manual Test Planとしては存在しない機能を確認させるHallucinationに等しい。

本Failureの本質は次である。

```text
Technically desirable acceptance
was treated as
currently user-visible acceptance.

Backend testability
was treated as
UI observability.

Source contract existence
was treated as
visible product feature existence.
```

## 2. User RequestとControllerの責務

Userの依頼は次だった。

```text
今週分を一旦締める前に、現時点で出来る範囲の実画面テストを行いたい。
起動Commandと検証項目を、このログへ出す。
Docs化は不要。
```

Controllerが行うべきだったこと：

1. Current UIに実在するPanel、Label、Button、StatusだけをInventory化する。
2. Terminalで確認するものとUIで確認するものを分ける。
3. Backend Test専用AcceptanceはUser Manualから除外する。
4. 各項目へ「どの画面の、どのLabelを見るか」を付ける。
5. 前段が失敗したら後続依存項目を自動的にNOT REACHEDへする。
6. 同じ通常Chat／RAG／Persistence確認を必要以上に繰り返さない。

実際には、Controllerは最新Manual DocsとSource上のAcceptance概念を参照したものの、Current Frontendへ投影されているかを検証せず、Backend AcceptanceをそのままUser Manualへ流した。

## 3. Failure Timeline

### 3.1 起動Commandと12項目のManual Plan提示

ControllerはMigration不要の起動Commandと、次の12区分をUserへ提示した。

1. 起動Baseline。
2. Main-shared Self-judge。
3. Real Selene Load／Judge。
4. Selene Repair／Rejudge。
5. Selene OFF／Unload。
6. Real Qwen3Guard OBSERVE。
7. Qwen3Guard ENFORCE。
8. Qwen3Guard OFF／Unload。
9. Stop／Cancel Probe。
10. Selene＋Qwen3Guard同時Turn。
11. Restart確認。
12. 最小Regression Sentinel。

構造上は広い範囲を覆っていたが、「UIから見えるか」というManual Testの最低条件を満たしていなかった。

### 3.2 Userの最初の指摘

UserはSeleneまでの実行で、次を指摘した。

- `Application startup complete`が何を意味するか分からない。
- `Dedicated Model`がどの画面を指すか分からない。
- Semantic 109とMain Runtime Governance／Judge Criteriaの関係説明が不足。
- Model／Artifact／Manifest Identityがどこにあるか分からない。
- Strict Decode結果がどこにあるか分からない。
- Preflight等のStageをどう調べるか分からない。
- Repair Candidate Identity／Frozen Rejudge／Budget値の表示が存在しない。
- Active Turn Drain、Call 0、Late Result 0が確認不能。

Controllerはこの時点で、Backend-only項目を実画面項目として出したFailureを認めた。しかし、Userが既に持っていた元の12項目を完全に置き換える、短いCorrected Manualを即時提示しなかった。

### 3.3 残るQwen3Guard／Restart／RegressionでFailureが再露呈

Userが残項目を実行した結果、さらに次が確認不能または不明瞭だった。

- GuardのConfigured／ActiveはProvider Panelで見えるが、Executed Provider専用表示はJudgeと同じ形では存在しない。
- Artifact／Manifest Identityの詳細表示はない。
- Input／Context／Output CandidateというPointは見えるが、内部Category／Strict Decode詳細は見えない。
- Guard Call 0を証明するCounterはない。
- Worker Drain、Cancellation Token、Late Publish 0、Unhandled Worker残存はUIから確認できない。
- `全Dedicated Mode`というController用語が、単純な「全てのModeをOFF」と同義なのに不必要に難解だった。
- Restart後の`CurrentとHistoricalが混ざらない`という表現は、何をどのPanelで比較するか定義されていなかった。
- `以前のFailure Codeが成功へ化けない`も対象Panel／Request IDを指定していなかった。
- 通常Chat送信を複数回確認させた。

Userは最終的に、実画面上に存在する情報だけを大量に手動転記し、存在しない項目について繰り返し「どこにあるのか」と確認する必要が生じた。

## 4. Hallucinated／Unsupported Manual Items Inventory

### 4.1 Terminal専用または説明不足だった項目

| Controller提示 | 実際 | Failure |
|---|---|---|
| `Application startup completeまで到達` | Terminal Logの文字列。通常起動できれば目的達成 | UI確認とTerminal確認を分離しなかった |
| `Startup Tracebackがない` | Terminalを見る必要がある | 確認場所を指定しなかった |
| `Dedicated Model Activeなし` | Selene／Qwen3Guardを意味した | 用語を定義しなかった |

### 4.2 Backend Test／Source Contract専用だった項目

| Controller提示 | Current UI | 正しい扱い |
|---|---|---|
| Model Call 0 | Counterなし | Automated Test Only |
| In-flight Cancellation Token | 表示なし | Automated Test／Terminal Instrumentation Only |
| Worker Drain／残存0 | 表示なし | Automated Test／Process Instrumentation Only |
| Late Result／Late Publish 0 | 明示Counterなし | Automated Test Only。UIでは後続変化を観測できるだけ |
| Exactly-once Release | 表示なし | Automated Test Only |
| Whole-stage Deadline | 表示なし | Automated Test／Evidence Artifact Only |
| Maximum Repair回数 | Current UIで確認不能 | Automated Testまたは将来UI |
| Repair Candidate内部Identity | Current UIで確認不能 | Persistent Evidence／Backend Test |
| Frozen Rejudge Identity | Final ResultのProviderから一部推定のみ | Backend Evidenceが必要 |

### 4.3 現在UIへ投影されていないStage

ControllerはSeleneについて、失敗Stageを次から特定するよう求めた。

```text
Preflight
Artifact Check
Load
Prompt Build
Inference
Strict Decode
Evidence Projection
```

しかし現在UIでは主に次しか表示されない。

- Configured Provider。
- Active Provider。
- Provider State。
- Independence。
- Budget Profile。
- Current LLM-as-a-Judge Model。
- Judge RunのResult／Failure Code／Reason。
- Criteria Count。

`unavailable`または`semantic_snapshot_unavailable`からStageを一意に分解するUIはない。したがって、UserへStage特定を要求したこと自体が不可能なTask Assignmentだった。

### 4.4 Guard UIに存在しない詳細

実画面で観測できたもの：

- `guardrail.input`。
- `guardrail.output_candidate`。
- `guardrail.context_source`。
- `guardrail.stream_candidate`。
- State、Severity、Detection数、Match数、Action数。
- Current Guardrail Model。
- Configured／Active／State／Independence／Budget。

Controllerが追加要求したが、Current UIで確認できないもの：

- Guard専用Executed Provider Field。
- Artifact／Manifest Digest詳細。
- Category SetのDecode詳細。
- Safety／Refusal ProtocolのStrict Decoder出力。
- Internal Failure Taxonomyの全Stage。

Visible Point名が存在することと、その内部ContractがLosslessに表示されることを混同した。

## 5. Undefined／Over-compressed Terminology Failure

Controllerは次の用語を、Userが既知であるかのように使った。

- Dedicated Model。
- Active Turn Drain。
- Late Result／Late Current追加。
- Historical分離。
- All Dedicated Modes。
- Canonical Green。
- Executed Provider整合。
- Strict Decode。
- Evidence Projection。

技術用語として意味があっても、Manual Testでは「画面上のどこを見るか」に変換しなければならない。

悪い例：

```text
Active Turn Drainを確認する。
```

必要だった表現：

```text
Turnの生成中にModeをOFFへした場合だけ、
Provider PanelのState欄に待機中を示す表示が出るかを見る。
その表示がなければ「UIから確認不能」とする。
```

悪い例：

```text
全Dedicated ModeをOFFにする。
```

必要だった表現：

```text
Main Runtime Governance、Guardrail Governance、
LLM-as-a-Judge、Repair、Recordingを全てOFFにする。
```

Controllerの圧縮表現により、Userは機能を理解する代わりに、Controllerの語彙を解読する追加作業を負った。

## 6. Dependency-order Failure

Manual Planは前段Failure時の停止条件を明確にしなかった。

正しい依存関係：

```text
Selene Provider Selection
→ Load／Active
→ Judge Success
→ Repair Eligibility
→ Repair
→ Rejudge
→ Selene＋Qwen3Guard Combined
```

実際にはSelene Judgeが`unavailable`で失敗した。それにもかかわらず、元PlanにはRepair／Rejudge、Stop／Cancel内部確認、Combined Turnが残った。

Userは合理的に、Seleneが機能していない以上Combined Turnは無意味と判断して中止した。Controllerが先に自動的に`NOT REACHED`へ落とすべきだった。

## 7. Redundant Verification Failure

Controllerは同一Session中に既に複数回成立している通常Chat送信を、最後のRegression Sentinelでも再度要求した。

同様に、RAG、Restart、Provider OFF後の通常Chat等を、目的と差分を明示せず反復させた。

Manual Testでは次を適用すべきだった。

```text
Recent PASS
+ no relevant state mutation
= reuse result
```

Model LifecycleやMode変更で回帰可能性がある場合だけ、何の回帰を見るかを一文で示して一度再実行する。今回は通常Chat確認の回数と目的が整理されていなかった。

## 8. Root Cause

### 8.1 Backend AcceptanceとUI Acceptanceの混同

ControllerはPhase 9 Requirements／Acceptance／Test上で必要な確認を、そのままUser Manualへ転記した。

```text
Requirement says it must be true
does not mean
the current UI exposes proof that it is true.
```

### 8.2 Canonical Manual／Docsへの過信

最新Manual Docsを読んだことを、Current UIで実行可能な手順であることの検証と誤認した。これはPhase 9-1で既に起きたCanonical Overtrustの再発形である。

```text
Canonical Manual
!= Executable Manual

Documented Acceptance
!= Visible User Acceptance
```

### 8.3 UI Inventory未実施

手順作成前に、Frontend Component、表示LabelまたはUser ScreenshotからActual Visibility Matrixを作らなかった。

### 8.4 Controller視点の語彙をUserへ直接出した

Lifecycle、Cancellation、Drain、Strict Decode等の内部概念を、UI Labelへ翻訳せず使用した。

### 8.5 Verification Coverageを増やすことを品質と誤認した

項目を多く列挙すれば安全になるというBiasにより、確認不能項目、重複項目および依存先失敗後の無意味な項目を残した。

## 9. Impact

### 9.1 User Attention／Time Cost

Userは次を行う必要が生じた。

- 存在しない項目をSettings内で探す。
- 各用語の意味をControllerへ質問する。
- 大量のStatus／Evidenceを手動Copyする。
- 同一Chat／Restart／Mode変更を繰り返す。
- Controllerの確認項目が実在するかを逆に監査する。
- 依存先が失敗しているCombined Testを自分で中止判断する。

### 9.2 Local Hardware Cost

SeleneはUser Mac上で非常に重く、UIが固まりやすくなり、Mode切替にも時間を要した。Judge OFFで通常の軽さへ戻った。

Controllerの過剰なManual Planは、機能しないSeleneの繰り返し操作と、不要なCombined Test候補まで含み、User Macの負荷と操作Riskを増やした。UserがCombined Testを中止したため、追加負荷は回避された。

### 9.3 Trust Cost

Userは以前から同種の「存在しない確認項目」を繰り返し経験しており、本件だけの単発Failureではないと指摘した。

```text
前回Web:
  Model Call 0を確認するよう要求
  → UIに確認機能なし

今回Judge／Guard:
  Stage／Call 0／Drain／Late Result等を要求
  → UIに確認機能なし
```

反復により、Controllerが提示するManual Test項目そのものをUserが信用できず、毎回「本当にその項目が存在するか」を検証しなければならなくなった。

## 10. Severity／Responsibility

```text
Source Damage: none
Data Loss: none
Git Mutation: none
Incorrect Phase Closure: none
User Time Waste: occurred
User Attention Waste: occurred
Local Hardware Burden: occurred
Manual Acceptance Reliability: failed
Repeated Failure Pattern: yes
Controller Responsibility: full
```

本Failureを、Current UIのObservability不足、Phase 9実装の未完了またはUserの技術理解不足へ転嫁しない。

UIに表示がないこと自体はProduct Findingになり得る。しかし「表示がない機能を、表示がある前提でUserへ確認させた」責任はCodex Controllerにある。

## 11. Required Corrective Operating Rules

### 11.1 Manual Test Visibility Matrix

今後、実画面テストをUserへ渡す前に、各項目を次へ分類する。

| Class | 意味 | Userへ依頼可能か |
|---|---|---|
| UI_VISIBLE | Current UIにLabel／値がある | 可。画面名とLabel必須 |
| TERMINAL_VISIBLE | Startup／Server Logで見える | 可。Terminal確認と明記 |
| BEHAVIOR_OBSERVABLE | 結果挙動から判断できる | 可。推論限界を明記 |
| AUTOMATED_TEST_ONLY | Counter／Token／Worker等 | 不可。User Manualから除外 |
| NOT_IMPLEMENTED_OBSERVABILITY | 必要だが表示機能なし | 未解決／予約へ分類 |

### 11.2 Exact Screen／Exact Label

各Manual項目には次を必須とする。

```text
Screen:
Panel:
Exact Label:
Action:
Expected Visible Result:
Failure Capture:
Dependent On:
```

Exact Labelを示せない項目は、実画面手順へ入れない。

### 11.3 Backend-only Acceptanceの排除

次は専用UI Counterが実装されるまでUser Manualへ入れない。

- Call 0。
- Worker／Thread残存0。
- Late Publish 0。
- Cancellation Token伝播。
- Exactly-once Release。
- Internal Deadline。
- Internal Candidate Identity。
- Stage別Preflight／Decode詳細。

### 11.4 Failure-dependent Short-circuit

前段がFAILなら、依存項目を自動的に`NOT REACHED`へ落とす。

```text
Judge FAIL
→ Repair／Rejudge NOT REACHED

Selene FAIL
→ Selene＋Qwen3Guard Combined NOT REACHED

Provider Load FAIL
→ Inference結果確認 NOT REACHED
```

### 11.5 User Languageへの翻訳

内部用語だけを単独で出さない。

```text
Dedicated Model
→ SeleneまたはQwen3Guard

Drain
→ 実行中の処理が終わるまで停止を待っている状態

Unload
→ Provider PanelのActiveがnoneになること
```

### 11.6 Recent Result Reuse

同一Sessionで既にPASSし、関連Stateが変化していない項目を再実行させない。再確認する場合は、どのMutationによるRegressionを見るかを明記する。

### 11.7 First User Confusion Is a Test-plan Failure Signal

Userが「何を言っているか分からない」「どこにあるか」と一度指摘した時点で、個別説明だけで済ませない。残るManual Plan全体を停止し、Visible項目だけの短いCorrected Planへ置き換える。

## 12. What Must Not Be Claimed

- Backend TestにあるからUIにもある、と主張しない。
- Provider PanelのActiveだけでReal Inference成功を主張しない。
- Point名が見えるだけでStrict Decode詳細が見えると主張しない。
- Userが画面を探せなかったことをUser理解不足と扱わない。
- 項目数の多さをManual品質と扱わない。
- 今回の後続Product結果が良かった場合でも、本Manual設計Failureを相殺しない。

## 13. Relationship to Prior Codex Failures

本件は次の既存Failureと接続する。

### Canonical Overtrust

`docs/project/shared/history/automation/codex_controller_phase_9_1_semantic_closure_canonical_overtrust_and_excessive_docs_reread_failure_evidence_ja_20260901002442.md`

Docsを読んでも、そのDocsがUser IntentまたはCurrent UIと一致するとは限らない。

### Phase 6 Resource／Delivery Failure

`docs/project/shared/history/automation/codex_controller_phase_6_resource_role_acceptance_and_delivery_failure_full_reflection_ja_20260829170117.md`

Controllerが品質を上げるつもりでUserの時間、利用可能量および体力を消費し、必要な結果へ直結しないFailureと同系列である。

### Previous Web Model Call 0 Manual Error

前回Web Manualで、UIから確認できない`Model Call 0`をUser確認事項として提示した。本件で同じ誤りをJudge／Guardへ拡大再発させた。

## 14. No Concealment

今回Userは、実際には起動、Main-shared、Selene、Qwen3Guard、OFF／Unload、Restart、RAG、Local Corpus、Archive、Dev AgentおよびWebを広く確認した。

しかしUserが最終的に多くのEvidenceを採取できたことは、ControllerのManual Planが正しかったことを意味しない。Userが不明な項目を自分で切り分け、無意味なCombined Testを中止し、存在するUI情報だけを大量に転記したことで成立した。

```text
User compensated for the controller failure.

Successful evidence collection
does not erase
invalid manual instructions.
```

本Failureの主責任はCodex Controllerにある。以後、実画面テストは「技術的に確認したいこと」ではなく、「現在のUser UIから実際に確認できること」を正本として設計する。
