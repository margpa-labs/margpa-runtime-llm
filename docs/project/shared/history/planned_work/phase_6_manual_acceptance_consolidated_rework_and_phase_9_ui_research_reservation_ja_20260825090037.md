# Phase 6実画面Manual Acceptance統合Rework／Phase 9 UI・研究予約

```yaml
document_id: phase_6_manual_acceptance_consolidated_rework_and_phase_9_ui_research_reservation_20260825090037
status: accepted_user_direction_consolidated_planned_work
document_type: append_only_lossless_manual_acceptance_and_followup_reservation
source_window: user_mac_real_browser_followup_2026-08-25
recorded_at: 2026-08-25 09:00:37 JST
language: ja
phase_6_disposition: adjust_rework_required
phase_6_closure: blocked_by_functional_acceptance
phase_9_items: reserved_not_started
phase_10_items: reserved_not_started
implementation_authorized_by_this_document: false
supersedes_nothing: true
```

## 1. 目的と正本関係

本文書は、UserがMac実機、実Browser、実Qwen／DeepSeek Artifactを用いて行ったPhase 6再Manual
Acceptanceと、その後のUser／Codex間の切り分けをLosslessに統合する予約台帳である。対象は、Userが
「まだ全部見たわけではない」として状態／Source確認を開始した入力から、Phase 6で直す機能的問題、
Phase 9へ送る表示／研究機能、Phase 10以降へ送る自動Hardware適応を確定した時点までとする。

次の既存文書は削除、置換または遡及修正しない。

- `docs/project/phases/phase_6/history/operations/phase_6_gov010_user_mac_manual_acceptance_and_codex_implementation_failure_ja_20260823232403.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov011_user_ui_runtime_model_and_semantic_enforcement_rework_scope_ja_20260824134921.md`
- `docs/project/shared/history/planned_work/phase_9_late_context_compaction_recovery_and_governance_trace_observatory_ja_20260823092049.md`
- `docs/project/shared/history/planned_work/phase_6_0_advanced_runtime_component_identity_projection_ja_20260822150342.md`

既存文書が保持する当時のEvidenceと本文書の最新Dispositionが異なる場合、当時のEvidenceは当時の記録
として残し、今後の実装範囲とAcceptanceには本文書の新しいUser Decisionを追加適用する。

## 2. 最終分類

| 分類 | 対象 | Current Decision |
|---|---|---|
| Phase 6必須Rework | ARGD／DAGD Semantic Rule 109件 | 実行可能なSemantic Evaluationへ接続するまでClosure不可 |
| Phase 6必須Rework | Guardrail／Judge Provider | Qwen3Guard／Seleneを実際に登録・Load・実行可能にする |
| Phase 6必須Rework | Role Provider選択 | Main／Guardrail／Judgeを独立選択し、`None`とBuilt-inも選べるようにする |
| Phase 6必須Rework | Judge／Repair | 独立Judge、理由別Failure、Profile別Timeout、Repair成功Golden Pathを成立させる |
| Phase 6必須Rework | Recording暫定相関 | 最新Request ID、日時、Modeを表示する |
| Phase 9冒頭 | ENFORCE Delivery | `Strict`と`Progressive`を実験変数化し、既定値を`Progressive`にする |
| Phase 9 | Governance Trace | 右側PanelでRaw、Judge、Repair、Final、Recordingを同一Identityへ相関する |
| Phase 9 Closure手前 | UI／Layout／表示整理 | 本文書第9節の全項目 |
| Phase 9 Closure手前 | Mac Context Profile | 実測後に`8192`から`16384`への昇格を検討する |
| Phase 10以降 | Hardware自動検出／自動上限 | Profile自動選択・自動昇格を行う |

## 3. User Macで成立した項目

以下は今回の実画面操作で成立した。今後のReworkで回帰させない。

1. Modeは独立した`適用`Buttonなしで、`OFF／OBSERVE／ENFORCE`または
   `OFF／METADATA／FULL`を押した時点で反映された。
2. 不要な`適用`／`〜を適用`Buttonは削除されていた。
3. Advanced Settingsに重複していた旧Model／Context／Max New Tokens入力は概ね削除されていた。
4. 起動時Main ModelはQwenだった。
5. QwenからDeepSeekへ切り替えると、Sidebar、Model Statusおよび環境情報のCurrent Model表示が
   DeepSeekへ変わった。
6. DeepSeekからQwenへ戻すとCurrent Model表示もQwenへ戻った。
7. DeepSeek選択中にServerを再起動してもStartup DefaultのQwenへ戻った。
8. 二つのBrowser Tabで、別Tabの入出力を元TabのReload後に確認できた。
9. Server再起動後もConversation、CitationおよびBranchは残った。
10. Judge／Repair中のUser Stop操作は成立した。
11. DeepSeekの過去の病的な同文反復は、今回の複数Turnでは再現しなかった。
12. DeepSeek反復検出後の無限生成停止経路は、既存Regressionとして保持対象である。
13. Max New Tokensの起動時値は`2048`だった。
14. Turn RecordingおよびJudge Evidence Recordingは画面上で成功表示となった。

成立範囲は、Judgeの意味的正しさ、Repair成功、EvidenceのRequest相関、Dedicated Model稼働、Metal、
DeepSeekの回答品質またはPhase 6 Closureを意味しない。

## 4. Runtime Model／Context／Tokenの実画面観測

### 4.1 Current Status

Qwen選択中の画面では次を観測した。

```text
Revision: 0
Configured Startup Default: main.qwen3-4b-q4-k-m
Current Main Model: main.qwen3-4b-q4-k-m
State: active
Model Native Context Maximum: 40960
Backend Context Maximum: 40960
Deployment / Hardware Verified Maximum: 8192
Effective Context Maximum: 8192
Effective Limit Reason: deployment_hardware_verified_limit
Current LLM-as-a-Judge Model: main.qwen3-4b-q4-k-m
Current Guardrail Model: 未設定（Rule／Pattern Base検出）
Current Governance Layer: plan-...
```

DeepSeek選択中はNative／Backend Maximumが`131072`へ更新されたが、Effective MaximumはMac Profileの
`8192`を維持した。この分離自体は、未検証のNative MaximumをMac上で入力可能な上限として捏造しない
ためのCurrent Contractである。

### 4.2 Context／Max New Tokensの相互作用

Userは次を実測した。

```text
Initial:
Context Size (8192 / 8192)
Max New Tokens (2048 / 8191)

4096 / 1024を適用後:
Context Size (4096 / 8192)
Max New Tokens (1024 / 4095)

8192 / 2048へ戻した後:
Context Size (8192 / 8192)
Max New Tokens (2048 / 8191)

Max New Tokens 8191:
Context Size (8192 / 8192)
Max New Tokens (8191 / 8191)
```

`8191`はCurrent Context `8192`から最低1 Tokenを入力側に残す計算である。ただし、理論上限を入力欄へ
そのまま見せる現状は実際のPrompt／System／Governance Budgetを説明せず、利用者に実用上安全な生成上限
と誤認させる。Context Sizeを変更するとMax New Tokensの表示上限も変わるが、この依存関係の説明がない。

Qwenで`4096`へ変更後にDeepSeekへ切り替えても、画面は`Context Size (4096 / 8192)`を維持した。
Current実装はModel別Context設定を保持せず、Deployment ProfileのEffective Maximumを共用している。

### 4.3 確定した将来Disposition

- 当面のMac Verified Profileは`8192`を維持する。
- Phase 9 Closure手前でMac実機`16384`を測定し、成立時だけProfileを昇格する。
- 目標表示候補は`Context Size 8192 / 16384`および`Max New Tokens 2048 / 8192`とする。
- Max New TokensのDefaultは`2048`を維持する。
- Model別Context設定の記憶はPhase 9 Closure手前、利用可能量次第でPhase 10へ送る。
- Hardwareを自動検出してProfile／上限を自動昇格する仕組みはPhase 10以降とする。
- Cloud／Home Server等はHardware／Deployment Profileを分け、Current Verified LimitをProfileから投影する。

## 5. Phase 6 Closureを止める機能的Failure

### 5.1 ARGD／DAGD Semantic Rule 109件が未実行

Main Runtime Governanceは各Turnで次を表示し続けた。

```text
main_model.pre
Selected Rule数: 109
Deviation: 1
Deferred（意味評価待ち）: 109

main_model.post
Selected Rule数: 109
Deviation: 0
Deferred（意味評価待ち）: 109
```

Phase 4／5では、Hallucination、知ったかぶり、根拠なき断定およびARGD／DAGD Semantic Ruleの
意味的Judge／RepairをPhase 6の責務として明示していた。Phase 6は別Componentとして固定Criteriaの
Judgeを作ったが、Governance Definition DescriptorをSemantic Evaluation Criteriaへ変換していない。

したがって、109件を正直にDeferred表示したことはObservability上の正しさではあるが、Phase 6の
約束を履行したことにはならない。これはUser承認のないScope縮小であり、Phase 6必須Reworkとする。

必要な実行Chainは次である。

```text
ARGD／DAGD Definition
→ Validated Semantic Descriptor
→ Normalized Evaluation Criteria
→ Request-correlated Evaluation／Judge Input
→ Deviation／Unknown／Pass
→ Conflict Resolution／Action Resolver
→ Bounded Repair／Final Presentation
→ Evidence
```

### 5.2 Current Main-self Judgeは独立Judgeとして不成立

Current Judgeは選択中Main Modelを`main_self`として再利用する。Userの実測ではQwenが自身の明白な
誤答を次のように自己承認した。

```text
判定: accept
確信度: 0.95
実行状態: completed
Repair適格性: not_eligible_no_repair_recommendation
提示結果: candidate_accepted
```

Judge Port、状態遷移、Cancellation、RecordingおよびFail-closedの基盤価値はある。しかし通常利用では、
誤答したModelへ追加Callを行い、遅延とResourceを増やしながら誤答を承認したため、独立評価としては
目的を満たさない。Main-selfは研究条件として明示選択時だけ許可し、未設定時の暗黙Fallbackは禁止する。

### 5.3 Dedicated Judge／Guardrail Modelが未接続

Artifact候補は存在するが、Current Product経路ではSeleneをDedicated Judgeとして、Qwen3GuardをSafety
Modelとして登録、Load、Binding、Calibrationおよび実行するProduction経路が成立していない。

```text
Judge Candidate:
Selene-1-Mini-Llama-3.1-8B-Q5_K_M

Guard Candidate:
Qwen.Qwen3Guard-Gen-0.6B.Q8_0
```

Phase 6 Reworkでは、UI文字列だけでなく実Artifact、Definition、Registry、Backend、Role Binding、
Load／Unload、Resource Gate、Output Decoder、Timeout、EvidenceおよびCurrent Identityを接続する。

### 5.4 Judge Provider／Guardrail Provider選択

選択欄の正確な概念はModelではなく`Provider`とする。初期候補は次である。

```text
Main Model
- Qwen
- DeepSeek

Guardrail Provider
- None
- Built-in: Rule／Pattern Base
- Model: Qwen3Guard

Judge Provider
- None
- Built-in: Deterministic Evaluator
- Model: Selene
- Model: Qwen
- Model: DeepSeek
```

Configured Default候補は`Guardrail=Qwen3Guard`、`Judge=Selene`とする一方、全ModeのStartup Defaultは
`OFF`を維持する。OFF中はDedicated Role ModelをLoadせず、常時Resourceを消費しない。OBSERVE／
ENFORCEへ変更した時だけResource Preflight後にLoadし、OFFへ戻した場合は安全に解放する。

Resource不足、Unsupported、Load FailureまたはCalibration Failure時にMain Modelへ暗黙Fallbackしない。
`None／Unavailable／Invalid／Loading／Active／Degraded`を区別する。Main-self JudgeはQwen／DeepSeekを
Judge Providerとして明示選択した場合だけ成立させ、`Self Judge`と表示する。異なるMain／Judgeは
`Independent Judge`と表示する。

Current UIはConfigured ProviderとActive Providerを分離する。

```text
Configured Judge Provider: Selene
Active Judge Provider: None
Judge Mode: OFF
Load State: inactive
```

Built-in Provider選択時は`Current Judge Model`へModel名を捏造せず、
`Provider Type: deterministic／Current Judge Model: 該当なし`と表示する。

### 5.5 Timeoutは固定30秒Policyの設計不適合

Current Live Judge／Repairは一律30秒のBudgetを持ち、同じLocal Main Modelを同期的に再呼出しする。
UserはENFORCEで`deadline_exceeded`を観測した。Mac性能は実Latencyに影響するが、全Model、全Hardware、
Model Load待ち、推論およびDecodeへ同じ30秒を適用することが主たる設計問題である。

Phase 6 Reworkでは少なくとも次を分離する。

- Judge／Repair Role別Timeout。
- Model／Deployment Profile別のDefault／Verified Range。
- Queue／Lease待ち、Load、Inference、Decode／ValidationのElapsed Time。
- Timeout Stage、Configured Timeout、Actual Elapsed、Provider Identity。
- Cancel／Deadline／Resource Unavailable／Malformed OutputのTyped Reason。
- Timeout後に遅いWorkerがLast Result、Presented FinalまたはEvidenceを上書きしないTerminal Ownership。

単純に固定値を長くするだけではAcceptanceしない。

### 5.6 Failure Presentationは原因別・言語別にする

Current English Safe Fallback：

```text
The answer could not be verified safely, so it has been withheld.
Please retry or confirm the answer against an authoritative source.
```

これは`deadline_exceeded`、`malformed_output`、Cancel、Resource不足等の原因を隠し、User Inputに問題が
あったようにも読める。Research Platformとして検証不能である。

Phase 6 ReworkではReason Codeごとに文面を変え、Turn開始時の回答言語に合わせる。例：

```text
deadline_exceeded:
LLM-as-a-Judgeによる検証が30秒以内に完了しなかったため、候補回答を表示していません。
入力内容が原因とは限りません。Judge Model、実行環境またはTimeout設定を確認してください。

malformed_output:
LLM-as-a-Judgeの出力を解析できなかったため、候補回答を表示していません。
```

Canonical EvidenceにはLocalized Stringではなく安定したReason Code、Provider、TimeoutおよびElapsedを
記録する。内部ExceptionをそのままChat本文へ出さない一方、原因をGenericな安全文言へ隠さない。

### 5.7 Repair成功Golden PathをUserが再現できない

本来の成功経路は次である。

```text
Candidate
→ Judge: needs_repair
→ Repair: eligible
→ Bounded Repair
→ Rejudge: accept
→ Presented Final: repair_accepted
```

しかしCurrent実Modelでは、Qwenは誤答を`accept`、DeepSeekは`malformed_output`、重いCallは
`deadline_exceeded`となるため、Userは有効なManual Golden Pathを再現できなかった。偶然
`needs_repair`が返るまで質問を変えることをAcceptanceにしてはならない。

Phase 6 Reworkでは、Dedicated Judgeを用いた既知FixtureまたはProductionと混同しないDeterministic
Research Fixtureにより、実Browserで`judging → repairing → rejudging → completed`、Raw Candidateと
Repair Finalの差、Exactly-once Evidenceを確認可能にする。

### 5.8 Recordingの暫定相関表示

Current UIの次の表示だけでは、どのTurn、Mode、Judge ResultまたはRepair Attemptを記録したか分からない。

```text
直近の記録（Turn）: 正常に記録されました
直近の記録（Judge Evidence）: 正常に記録されました
```

Phase 6 Reworkでは暫定的に、最新Request ID、記録日時、Frozen Mode、Record Kind、OutcomeおよびReasonを
表示する。完全なRaw／Final相関TraceはPhase 9の右側Observatoryへ接続する。

## 6. Manual Scenario Evidence

### 6.1 Qwen／全Governance ENFORCE／Recording FULL

Userは「ホロライブ、天音かなたの読み方は？」に対し、Qwenが`てんねいかなと`等の誤った読みを
回答し、User Correction「あまねかなたなんだけど」および公式ページの`天音かなた／Amane Kanata`
Evidenceを提示しても、`てんねいかなと`を公式だと断定することを観測した。

各TurnでMain GovernanceのSemantic Rule 109件はDeferredのまま、GuardrailはMatch 0、Judgeは
`accept／0.95／candidate_accepted`を繰り返した。表示値がRequestごとに相関されず同じに見えることも、
最新結果のIdentity不足として扱う。

### 6.2 Qwen／OBSERVE／Recording METADATA

Userが論理矛盾とWeb検索未実装を指摘したTurnでは、Judgeは次を表示した。

```text
判定: needs_repair
確信度: 0.95
実行状態: completed
提示結果: observed_candidate
```

OBSERVEのためRaw Candidateを変更しないこと自体はMode Semanticsに合う。しかしMain Governanceの109件は
引き続きDeferredであり、Judgeの評価根拠とRequest相関は画面から追跡できなかった。

### 6.3 全Mode OFF後のStale Result

全ModeをOFFにしても、Advanced Settingsには前回の`completed／needs_repair／observed_candidate`等が
残った。OFF TurnではJudge Hookが動かずLast Resultが更新されないため、現在状態と過去履歴が混ざる。

Phase 9 Closure手前で、現在状態は`無効`、過去結果はRequest ID／日時／実行Mode付きの
`直近の履歴`として分離する。設定を開き直した時点でCanonical Current Modeを再取得する。

### 6.4 再ENFORCE時のDeadline Safe Fallback

再び全機能をENFORCE／FULLへ変更したTurnでは、Judgeが`deadline_exceeded`となり、English Safe
FallbackがPresented Finalとして表示された。この経路はRaw誤答をFail-openしなかったが、固定Timeout、
一括表示、英語固定、原因を隠す文言およびUser検証不能という別のFailureを持つ。

### 6.5 DeepSeek

DeepSeekは今回の複数Turnで過去の病的同文反復を再現しなかった。一方、次の品質Failureを観測した。

- `天音かなた（てんおう かなた）の読み方は「あめおかなた」`という自己矛盾。
- User Correction後も`あめおかなた／てんおうかなた`を支持。
- 公式`Amane Kanata` Evidence提示後にようやく「あまねかなた」へ修正。
- リポビタンDについて事実と異なる成分、量、単位および製品説明を生成。
- Judge Providerとして使うと`malformed_output／unknown／failed`が継続。
- ENFORCEではSafe Fallbackへ収束し、実回答を提示できない。

したがって、反復防止Regressionは成立候補だが、DeepSeek Current Mac Q4のMain／Judge実用品質は
Acceptedではない。公式DeepSeek系列全般、原Weightまたは別Quantizationへ無制限に一般化しない。

### 6.6 Stop／Late Result

Judge／Repair中のUser Stop操作は成立した。停止後に遅れて回答またはEvidenceが追加されないことは、
User Manualでは長い生成時間のため完全には再導出できなかった。既存のCancellation／Terminal Owner／
Late Worker Regressionを保持し、次回ManualではRequest IDと記録時刻を使って確認する。

## 7. Phase 6 Provider／Modeの確定仕様

### 7.1 Default

```text
Startup Main Model: Qwen
Configured Guardrail Provider: Qwen3Guard
Configured Judge Provider: Selene
Guardrail Mode Default: OFF
Judge Mode Default: OFF
Repair Mode Default: OFF
Recording Mode Default: OFF
```

OFFはConfigured Providerを消すことではなく、Active Load／Executionを行わないことを意味する。
Resource Gate結果次第ではConfigured Defaultを`None`へ戻せるが、判断は実測で行い、常時Loadを理由に
暗黙Main-selfへ戻さない。

### 7.2 ModeとProvider不在

- `Provider=None`かつModel必須のOBSERVE／ENFORCEを選択した場合、利用可能なBuilt-in Evaluatorが
  明示選択されていなければ適用を拒否する。
- `None`をMain Modelへ暗黙変換しない。
- Built-in Deterministic ProviderとModel Providerを同じDropdownで選択可能にするが、型を表示する。
- 初期Phase 6では単一Provider選択とする。Composite／HybridはPhase 9のMulti-Governance実験候補とする。

## 8. Phase 9冒頭／研究機能予約

### 8.1 ENFORCE Delivery Policy

次の二方式を選択可能にし、既定値は`Progressive`とする。

```text
Strict:
  全文Buffer → Judge → 承認後に一括表示

Progressive:
  短いChunkをBuffer → 高速検査 → 承認済みChunkからStreaming
  後段Judgeで残りを停止またはRepair
```

Progressiveは既に表示したChunkを回収できないことをUIとEvidenceへ明示する。記録候補：

```text
delivery_policy
released_chunk_count
withheld_chunk_count
late_deviation_detected
repair_triggered
```

Current Strict一括表示は安全側の実装だが、長い待機と一括表示によるUX低下が大きい。見せかけの
Typing AnimationでStreamingを捏造せず、実Chunk Releaseとして実装する。

### 8.2 Role／Provider比較

Phase 9では少なくとも次をExperiment Matrixにできる。

```text
Main Qwen     / Judge None, Deterministic, Selene, Qwen, DeepSeek
Main DeepSeek / Judge None, Deterministic, Selene, Qwen, DeepSeek
Guard None, Rule／Pattern Base, Qwen3Guard
```

Self JudgeとIndependent Judge、Cost、Latency、Malformed率、Timeout率、Detection、Repair成功率を比較する。

### 8.3 Governance Trace Observatory

既存予約に従い、右側Panelで次を同一Identity Chainへ関連付ける。

- Conversation／Turn／Request／Attempt／Repair Attempt ID。
- Main／Guardrail／Judge Provider、Model、Artifact、Mode。
- Raw Candidate、Selected Rule、Deferred／Deviation、Judge、Repair、Final。
- Recording Outcome、Evidence ID、Timestamp、Token、Latency、Failure Reason。

Advanced SettingsはCurrent Summaryを保持し、詳細相関は右側Panelへ送る。

## 9. Phase 9 Closure手前のUI／Profile予約

次を一括して扱う。

1. Judge ModeがOFFならCurrent Run状態を`無効`とし、過去結果を`直近の履歴`へ分離する。
2. Research／Developer Modeは内部的に元へ戻せる構造を残して常時ONとし、利用者向けの
   `OFF／ON／Apply完了`および`research_developer_mode` Cardを非表示にする。
3. Runtime設定制御を左右3項目ずつのLayoutへ整える。
4. `conversation_storage_kind`、`conversation_storage_version`を順序維持のまま`profile_key`の上へ移動する。
5. 回答言語Pull-downだけを`自動（Auto）`等の内容幅に合わせ、下の二つのCheckbox位置を動かさない。
6. `OFF／OBSERVE／ENFORCE`と`OFF／METADATA／FULL`のButton位置を揃える。
7. SidebarはCurrent Modelだけでなく、旧来のProfile、Device、Acceleration情報を失わない。
   `active／Context`を追加表示する場合も既存環境情報を上書きしない。
8. Advanced Settingsの順序を次へ変更する。

```text
Governance Definitions
Main Runtime Governance
Guardrail Governance
Judge／Repair／Recording
Model Status
Runtime設定制御
```

9. `Guardrail Governance`、`Judge／Repair／Recording`、`Model Status`、`Runtime設定制御`の見出し上へ
   区切り線、各Block下へ小さな縦余白を追加する。先頭候補の`Main Runtime Governance`と通常非表示候補の
   `Governance Definitions`は上区切り線の例外とする。
10. Mac `16384` Context Profileを実測し、成功時だけVerified Maximumを昇格する。
11. Max New TokensのDefault `2048`、目標上限`8192`、Prompt／Governance Reserveを含む実効契約を再設計する。
12. Model別Context設定を保持するか、Model切替時に既定値へ戻すかを確定する。利用可能量不足時はPhase 10へ送る。
13. Safe Fallbackを含む利用者向けJA／EN Copy全体を再確認する。ただし原因別Reason表示の基礎修正は
    Phase 6で先に行う。
14. 利用者向け機能名へ`（Phase N）`を付けない規則を維持する。

## 10. Phase 10以降予約

- Hardware Capability自動検出。
- Profile自動選択／安全な自動上限昇格。
- 未検証Hardware値をCurrent Effective LimitにしないAttestation／Benchmark。
- Phase 9で未完となったModel別Context保持。

## 11. Phase 6 Rework Acceptance Candidate

Phase 6 Closure前に少なくとも次を満たす。

- ARGD／DAGD Semantic Ruleが109件一律Deferredではなく、対象Ruleが実Criteriaへ変換・評価される。
- Rule非対象、Unknown、UnsupportedおよびDeferredを正確に区別する。
- SeleneがDedicated Judgeとして実ArtifactからLoad・実行・停止・解放できる。
- Qwen3GuardがGuardrail Providerとして実ArtifactからLoad・実行・停止・解放できる。
- Main、Guardrail、Judge Providerを独立選択できる。
- `None`、Built-in、Model Providerを型付きで表示する。
- OFF中にDedicated Role Modelを常時Loadしない。
- Main-selfは明示選択時だけ使用し、暗黙Fallbackしない。
- User Correction／会話内Evidenceとの矛盾を`accept 0.95`へ誤承認しないGolden Fixtureがある。
- `needs_repair → repair → rejudge → repair_accepted`を実Browserで再現できる。
- Timeout、Malformed、Unavailable、CancelはReason別に表示され、User Inputの責任へ転嫁しない。
- Latest RecordingにRequest ID、時刻、ModeおよびOutcomeが表示される。
- Stop後のLate Result／Evidence上書きがない。
- Qwen／DeepSeekの反復防止Regressionを維持する。
- Qwen Default、Model Switch、Restart復帰、二Tab、Conversation／Citation／Branchを回帰させない。

## 12. Current Disposition

```text
Phase 6 Manual Acceptance: ADJUST／REWORK REQUIRED
Phase 6 Closure: BLOCKED
Primary Functional Blocker:
  - ARGD／DAGD Semantic Rule execution missing
  - Dedicated Judge／Guardrail Provider missing
  - Judge／Repair real Golden Path missing
  - Fixed timeout／generic failure／recording correlation insufficiency
Phase 9 UI／Research Work: RESERVED
Phase 10 Hardware Auto-adaptation: RESERVED
Source／Test／Config Mutation by this document: 0
Git Mutation by this document: 0
```

本文書単独ではSource実装、Model Load、Git、Closureまたは次Phase開始を許可しない。次の実装時は、
本文書からPhase 6必須項目だけをExact Rework Handoffへ抽出し、Phase 9／10予約を混入させない。
