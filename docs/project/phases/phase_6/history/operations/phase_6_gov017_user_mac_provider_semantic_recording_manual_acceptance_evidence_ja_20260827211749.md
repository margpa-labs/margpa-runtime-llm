# Phase 6 User Mac Provider／Semantic／Recording Manual Acceptance Evidence（P6-GOV-017）

```yaml
document_id: phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_20260827211749
governance_id: P6-GOV-017
status: ADJUST_REWORK_REQUIRED
classification: user_mac_manual_acceptance_evidence
created_at: 2026-08-27 21:17:49 JST
predecessor: phase_6_gov016_remaining_rework_controller_independent_review_ja_20260826202919.md
manual_check_contract: phase_6_user_mac_bounded_manual_check_after_remaining_rework_ja_20260826202919.md
phase_6_closure: BLOCKED
phase_7: NOT_STARTED
```

## 1. 結論

User MacでM-1〜M-7を全件実施した。初期Provider State、Turn RecordingおよびJudge Evidence Recordingは成立した。一方、P6-GOV-016で検出したProduction Wiring未成立、Provider False Identity、Semantic Criterion未評価、Status Projection不整合およびFrontend更新Lifecycle不具合を実画面で再現した。

```text
Manual Check Executed : M-1〜M-7 ALL EXECUTED
PASS                   : Initial State、Turn Recording、Judge Evidence Recording
PARTIAL                : Historical Result分離、Recording Correlation
FAIL／REPRODUCED       : Main Switch、Selene、Qwen3Guard、Built-in Judge、Semantic Evaluation、Status Projection、Live Refresh
Phase 6 Acceptance     : FAIL／ADJUST
Phase 6 Closure        : BLOCKED
```

本EvidenceはQwen／DeepSeekの回答品質、Selene／Qwen3Guardの実用品質またはPhase 6 ClosureをPASSへ昇格させない。

## 2. Test Context

正本Manual Check：

`docs/project/phases/phase_6/handoffs/phase_6_user_mac_bounded_manual_check_after_remaining_rework_ja_20260826202919.md`

起動Optionは同Manual Check §2のPhase 3〜6 Featureを有効化するCommandを使用した。User `runtime_data`の内容をControllerは参照していない。Screenshot 8件はUserが会話上で提示し、本書は画面文言をText Evidenceとして固定する。Screenshot File自体はProjectへCopyしていない。

## 3. M-1 初期Provider State

Result：`PASS／DISPLAY CONTRACT CONFIRMED`

```text
Main
  Configured : main.qwen3-4b-q4-k-m
  Active     : main.qwen3-4b-q4-k-m
  State      : active

Guard
  Configured : guard.qwen3guard-gen-0.6b-q8-0
  Active     : none
  State      : configured
  Independence: independent_other_model
  Budget     : local_macos_qwen3guard_v1 / configured_not_hardware_verified

Judge
  Configured : judge.selene-1-mini-llama-3.1-8b-q5-k-m
  Active     : none
  State      : configured
  Independence: independent_other_model
  Budget     : local_macos_selene_judge_v1 / configured_not_hardware_verified

All Feature Modes: OFF
```

ConfiguredとActiveを分離表示し、Startup時にDedicated Guard／JudgeをLoadしていない点は成立した。

## 4. M-2 Main Dropdown実動作

Result：`FAIL／P6-CODEX-049 REPRODUCED`

Role Provider SelectionでMainをDeepSeekへ変更した。

```text
Provider Selection
  Configured : main.deepseek-r1-0528-qwen3-8b-q4-k-m
  Active     : main.qwen3-4b-q4-k-m
  State      : configured

Model Status
  Current Main Model : main.qwen3-4b-q4-k-m

Sidebar
  main.qwen3-4b-q4-k-m
  active · Context 8192
```

Provider SelectionだけがDeepSeek Configuredへ変わり、Runtime Main Switch Transaction、Model StatusおよびSidebarはQwenのままだった。Dropdownの存在をMain Switch PASSとしない。

## 5. M-3 Selene Activation

Result：`FAIL／P6-CODEX-046 REPRODUCED`

Selene ConfiguredのままJudge ModeをOBSERVE／ENFORCEへ変更した。

```text
User-visible Error : 適用に失敗しました。
Judge Mode         : OFFのまま
Configured         : judge.selene-1-mini-llama-3.1-8b-q5-k-m
Active             : none
State              : configured
Independence       : independent_other_model
Budget             : local_macos_selene_judge_v1 / configured_not_hardware_verified
```

Dedicated SeleneはProduction Loadされなかった。BackendのExact Failure Reasonに相当する情報は画面へ永続表示されず、汎用Errorだけだった。

## 6. M-4 Qwen3Guard Activation

Result：`FAIL／P6-CODEX-046／048 REPRODUCED`

Qwen3Guard ConfiguredのままGuardrail ModeをOBSERVE／ENFORCEへ変更した。

```text
User-visible Error : mode適用に失敗しました。
Visibility         : 一瞬表示された後に消える
Guardrail Mode     : OFFのまま
Configured         : guard.qwen3guard-gen-0.6b-q8-0
Active             : none
State              : configured
Independence       : independent_other_model
Budget             : local_macos_qwen3guard_v1 / configured_not_hardware_verified
```

Dedicated Qwen3GuardはProduction Loadされず、Rule／Pattern Base GuardrailへModel Resultを加算する経路も成立しなかった。Exact Failure Reasonを検証可能な形で保持しないUI不具合を追加Findingとする。

## 7. M-5 Built-in Judge／Semantic Rule

Result：`CRITICAL FAIL／P6-CODEX-047／050 REPRODUCED`

### 7.1 Provider表示

```text
Configured   : built_in.deterministic
Active       : built_in.deterministic
State        : active
Independence : built_in
Budget       : none
```

### 7.2 API Evidence

`GET /api/v5/feature-modes/status`で、次を確認した。

```text
request_id          : f0678597-dbc9-4287-a342-a15dec5da60a
judge_role          : main_self
recommendation      : unknown
confidence          : 0.0
execution_state     : failed
failure_reason      : malformed_output
configured_provider : built_in.deterministic
active_provider     : built_in.deterministic
budget_profile      : local_macos_default
criteria_selected   : 32
criteria_evaluated  : 0
criteria_passed     : 0
criteria_deviated   : 0
criteria_unknown    : 0
presentation_outcome: observed_candidate
failure_message     : Judgeの応答を解釈できなかったため、判定結果を使用していません。
failure_language    : ja
```

UI／Provider StateはBuilt-in DeterministicをActiveと表示したが、実Judge Roleは`main_self`だった。これは単なる表示不足ではなく、研究Evidenceの実行主体を誤認させるFalse Identityである。

### 7.3 Main Governance表示

```text
main_model.pre
State: evaluated · Selected Rule数: 109 · Severity: moderate · 実行Action数: 0
Observation数: 110 (Pass 0, Deviation 1, Deferred（意味評価待ち） 109)

main_model.post
State: evaluated · Selected Rule数: 109 · Severity: none · 実行Action数: 0
Observation数: 109 (Pass 0, Deviation 0, Deferred（意味評価待ち） 109)

Evidence状態: 正常
```

### 7.4 Semantic再確認

Main Runtime Governance=OBSERVE、Judge=OBSERVE、Repair=OFF、Recording=FULLで追加Turnを実行した。

```text
Request ID          : 2473c1de-aecc-4d6c-88f5-96e45586a8ed
Recommendation      : unknown
Confidence          : 0.00
Execution State     : failed
Started             : 2026-08-27T12:11:16.395815+00:00
Completed           : 2026-08-27T12:11:38.176700+00:00
Configured Provider : built_in.deterministic
Active Provider     : built_in.deterministic
Budget              : local_macos_default
Frozen Modes        : main=observe, guard=unknown, judge=observe, repair=off, recording=full
Criteria            : selected=32, evaluated=0, passed=0, deviated=0, unknown=0
Failure Reason      : malformed_output
Presentation        : observed_candidate
Turn Recording      : success
Judge Evidence      : success
```

109 CriterionのCompile／Selection入口は存在し、Current Batch上限32件が選択された。しかし有効なCriterion Resultは0件であり、意味評価は成立していない。残り77件のBudget Deferred、選択32件のEvaluation FailureおよびLegacy `Deferred 109`の関係もUI上で復元できない。

## 8. M-6 Judge OFF後のCurrent／Historical表示

Result：`PARTIAL／OBSERVABILITY FAIL`

JudgeをOFFへ戻したProvider Stateは次であり、Dedicated／Built-in Active解除は成立した。

```text
Configured   : built_in.deterministic
Active       : none
State        : configured
Independence : built_in
Budget       : none
```

一方、画面は次を表示した。

```text
現在のJudge Run状態: 失敗

直近のJudge結果
（別のTurnの結果です — 現在実行中）

Request ID: f0678597-dbc9-4287-a342-a15dec5da60a
Execution: failed
Failure: malformed_output
```

過去結果をCurrent Result本体から分離するData Contractは一部成立したが、次が不成立だった。

- OFFなのにCurrent Run Stateが`失敗`のまま。
- 実行中のRunがないのに「現在実行中」と表示。
- OBSERVE／ENFORCE実行中は完了結果を自動更新せず、OFF適用または画面再Open時に遅れて表示。

## 9. M-7 Recording相関

Result：`RECORDING PATH PASS／UI CORRELATION PARTIAL`

Judge=OBSERVE、Repair=OFF、Recording=FULLでTurnを実行した。最初に設定画面を開いた時点ではJudgeが実行中であり、Previous Turnが表示された。

```text
Current Judge State : Judge実行中
Displayed Result    : Previous Turn 395cffa9-800a-411b-bfe8-984965fc2e00
Turn Recording      : 正常に記録されました
Judge Evidence      : まだ記録がありません
```

設定画面を閉じて再Openすると、最新結果へ更新された。

```text
Request ID          : 899c5315-10ff-4211-859f-32381b41cd03
Recommendation      : accept
Confidence          : 0.95
Execution State     : completed
Started             : 2026-08-27T11:46:46.721732+00:00
Completed           : 2026-08-27T11:46:54.406672+00:00
Configured Provider : main.qwen3-4b-q4-k-m
Active Provider     : main.qwen3-4b-q4-k-m
Budget              : local_macos_main_self_judge_v1
Frozen Modes        : main=unknown, guard=unknown, judge=observe, repair=off, recording=full
Criteria            : selected=0, evaluated=0, passed=0, deviated=0, unknown=0
Presentation        : observed_candidate
Turn Recording      : 正常に記録されました
Judge Evidence      : 正常に記録されました
```

機能面ではTurn RecordingとJudge Evidence Recordingが成立した。`recording=off／full`をFrozen Modesへ残すことは記録成立を意味せず、そのTurnのMode相関Metadataであるため正しい。

不成立範囲は次である。

- Judge完了後の自動Polling／Push更新がない。
- Judge Evidence Publication完了後の自動更新がない。
- Recording Summary自身は成否だけで、Request ID、時刻、Provider、Outcome／Reasonを表示しない。
- Previous Turn、Current Running、Current CompletedのLifecycle表示が遅延Snapshotで混同される。

## 10. Model Status Projection

実画面のModel Statusは次を表示した。

```text
Current LLM-as-a-Judge Model : main.qwen3-4b-q4-k-m
Current Guardrail Model      : 未設定（Rule／Pattern Base検出）
```

Role Provider SelectionのConfigured DefaultはSelene／Qwen3Guardであり、Built-inへ変更した場合もModel StatusはMain Qwenのままだった。Current SourceはJudgeを旧Runtime Model Snapshot＋Main-self availabilityから投影し、Guardを`None`固定で投影している。

正しい表示はConfiguredとActiveを分離し、少なくとも次を矛盾なく示す必要がある。

```text
Judge Configured / Active / Executed
Guard Configured / Active / Executed
```

Mode OFFでConfigured Selene／Qwen3Guard、Active noneであることと、Built-inをActive表示しながらMain-selfを実行したFalse Identityを同じ状態として扱わない。

## 11. User指定のBounded UI Delta

UserはManual Check中、次をClaude差分Reworkへ含めるよう明示した。従来Phase 9へ送っていたUI磨き込みのうち、本節のExact項目だけをPhase 6へ前倒しする。その他のPhase 9予約を移動しない。

1. Model Status内に残る重複Main Model切替Dropdownを削除せず一旦非表示にする。Context Size／Max New Tokensは維持する。
2. Advanced ModeのPanel順を、少なくとも`Judge／Repair／Recording → Model Status → Role Provider選択 → Runtime設定制御`とする。
3. Research・Developer ModeのOFF／ON Controlを非表示にし、詳細内容を初期状態から表示する。Backend ContractはRollback可能なまま保持する。
4. 詳細Field中の`research_developer_mode`を非表示にする。
5. 残る6 Fieldを左右3:3に整理する。左は`conversation_storage_kind → conversation_storage_version → profile_key`、右は`acceleration_api → backend_kind → device_kind`を基本順とする。
6. Sidebarの`model · active · Context`だけの表示を修正し、Current Modelと従来のProfile／Device／Acceleration情報を失わない表示へ戻す。Current Model切替には追随する。
7. Selene／Qwen3Guard Activation失敗を一瞬の汎用文言で消さず、Exact Failure Reasonを永続表示する。
8. Judge実行中、完了、Evidence PublicationおよびMode OFF遷移を自動更新し、Previous／Current／Historicalを混同しない。

## 12. Finding連結

| Finding | Manual Result |
|---|---|
| P6-CODEX-046 | Selene／Qwen3Guard Activation失敗、Active noneで再現 |
| P6-CODEX-047 | Built-in Active表示に対し`judge_role=main_self`でCritical再現 |
| P6-CODEX-048 | Qwen3Guard Production Guardrail未接続を再現 |
| P6-CODEX-049 | Main Configured DeepSeek／Active Qwenで再現 |
| P6-CODEX-050 | Model Statusが旧Main-self／Guard noneを投影して再現 |
| P6-CODEX-051 | Main-self Budget表示、Selected Provider Budget未使用を再確認 |
| P6-CODEX-052 | ManualではOfficial Provenance昇格なし |
| P6-CODEX-053 | Frozen Guard unknown、Recording相関不足、Live更新不足を再現 |

追加Manual Finding：

```text
P6-CODEX-054 : Feature Modes Live Snapshot／Current-Historical Lifecycle Update不成立
P6-CODEX-055 : Activation Failure Reasonが汎用・一時表示で検証不能
P6-CODEX-056 : Built-in DeterministicがDeterministic実行主体として実装されていない
P6-CODEX-057 : Semantic Batch 32／残77／Legacy Deferred 109のResult統合不成立
P6-CODEX-058 : User指定Bounded Advanced Mode／Sidebar UI Delta未実装
```

## 13. Acceptance再分類

今回のManual Checkだけから、P6-RR-ACC-012とRecording Write Pathの一部は確認できる。一方、次は少なくとも未成立である。

```text
P6-RR-ACC-008  Definition→Evaluation→Action／Final→Evidence End-to-end
P6-RR-ACC-009  Main／Guard／Judge Dropdownの実Runtime切替
P6-RR-ACC-014  選択Providerの実LoadとConfigured／Active一致
P6-RR-ACC-018  Same／Independent Judge Identityの正確性
P6-RR-ACC-021  Selene Active Turn Evidence
P6-RR-ACC-025  Qwen3Guard Additive Production Merge
P6-RR-ACC-027  Selected Provider別実Budget
P6-RR-ACC-031  Semantic Failureの実Judge判定
P6-RR-ACC-032  Selected JudgeによるRepair Rejudge
P6-RR-ACC-034  Recording Summary相関表示
P6-RR-ACC-035  OFF Current／Historical分離
P6-RR-ACC-037  Real Selene／Qwen3Guard Matrix
P6-RR-ACC-038  Real Browser Provider／Semantic Acceptance
P6-RR-ACC-039  Historical Root-outside Incidentが存在するためLiteral 0 Claim不可
```

## 14. 次Action

P6-GOV-016のSource Findingと本Manual Evidenceを正本として、Fresh Claude `設計者兼実装者役`向けの差分Exact Handoffを発行する。

- Package 0〜Iの成立済みDomain／Adapter／Fixtureを最初から再実装しない。
- Production Factory、Execution Router、Main Switch同期、Status Projection、Semantic Result統合、Selected Provider Budget／Rejudge、Qwen3Guard加算経路、Official ProvenanceおよびObservabilityを差分修正する。
- User指定のBounded UI DeltaだけをPhase 6へ含める。
- Final Controller ReviewとUser Manual AcceptanceまでPhase 6 Closureを宣言しない。
