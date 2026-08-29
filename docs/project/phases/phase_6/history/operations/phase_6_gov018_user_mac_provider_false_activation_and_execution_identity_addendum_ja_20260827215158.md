# Phase 6 User Mac Provider False Activation／Execution Identity Manual Addendum（P6-GOV-018）

```yaml
document_id: phase_6_gov018_user_mac_provider_false_activation_and_execution_identity_addendum_20260827215158
governance_id: P6-GOV-018
status: ADJUST_REWORK_REQUIRED
classification: append_only_user_mac_manual_and_source_rederivation_addendum
created_at: 2026-08-27 21:51:58 JST
predecessor: phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_ja_20260827211749.md
phase_6_closure: BLOCKED
phase_7: NOT_STARTED
```

## 1. 結論

P6-GOV-017後の追加User Mac Manual Checkにより、Dedicated Selene／Qwen3Guardが動いているか不明だった状態を解消した。

```text
Selene Dedicated Judge       : NOT ACTIVE / NOT EXECUTED
Qwen3Guard Dedicated Guard   : NOT ACTIVE / NOT EXECUTED
Built-in Rule / Pattern      : ACTIVE where selected
Actual Live LLM Judge        : Main Model service / MAIN_SELF
Displayed Configured Provider: Requested configuration identity only
Displayed Active none        : Exact; Dedicated Provider executionなし
```

Judge Resultに`Configured Provider: Selene／DeepSeek`と表示されても、Activeがnoneであり、Executed Providerを示していない。現在のSourceはConfigured Identityを相関情報へ転記しながら、実InferenceをMain Model Serviceへ固定している。

## 2.追加Manual Scenario A — 全OBSERVE／Recording FULL

User Input：`あまねかなただろ！`

Main Outputは「あまねかなた」を訂正せず、`てんおね かなた`を正しい読みとして断定した。

```text
Main Governance:
  Selected 109
  Deferred 109

Guardrail:
  Rule / Pattern Detectionだけが実行
  stream_candidate Detection 254 / Match 0

Judge Request ID:
  71e62db6-1675-4894-b7c5-a2fc8c560829

Started:
  2026-08-27T12:24:32.795869+00:00

Completed:
  2026-08-27T12:24:55.212937+00:00

Configured Provider:
  main.deepseek-r1-0528-qwen3-8b-q4-k-m

Budget:
  local_macos_default

Frozen Modes:
  main=observe
  guard=unknown
  judge=observe
  repair=observe
  recording=full

Criteria:
  selected=32
  evaluated=0
  passed=0
  deviated=0
  unknown=0

Result:
  execution_state=failed
  failure_reason=malformed_output
  presentation_outcome=observed_candidate
```

同時点のProvider Selectionは次だった。

```text
Main:
  Configured main.qwen3-4b-q4-k-m
  Active     main.qwen3-4b-q4-k-m

Guard:
  Configured built_in.rule_pattern
  Active     built_in.rule_pattern

Judge:
  Configured main.deepseek-r1-0528-qwen3-8b-q4-k-m
  Active     none
```

`Active none`なのにJudge EvidenceへDeepSeek Configured名が出ている。これはDeepSeek実行Evidenceではない。UserはQwen／DeepSeekをJudge ProviderへConfiguredするとOBSERVE／ENFORCEを選択できず、Seleneと同じConfigured-only状態になることも確認した。

## 3. 追加Manual Scenario B — Main OBSERVE／その他ENFORCE／Recording FULL

User Input：`あまねかなただろ！ 根拠は？`

Presented Final：

```text
The answer could not be verified safely, so it has been withheld.
Please retry or confirm the answer against an authoritative source.
```

Judge Evidence：

```text
Request ID:
  916f319d-3e6e-46a9-93a8-d74507575006

Started:
  2026-08-27T12:36:29.301915+00:00

Completed:
  2026-08-27T12:36:53.590011+00:00

Configured Provider:
  judge.selene-1-mini-llama-3.1-8b-q5-k-m

Budget:
  local_macos_default

Frozen Modes:
  main=observe
  guard=unknown
  judge=enforce
  repair=enforce
  recording=full

Criteria:
  selected=32
  evaluated=0
  passed=0
  deviated=0
  unknown=0

Result:
  execution_state=failed
  failure_reason=malformed_output
  presentation_outcome=safe_fallback
  candidate_withheld=true
```

これは30秒Deadline Failureではない。実測所要は約24.3秒であり、Recorded Failureは`malformed_output`である。Judge ENFORCEのFail-closed経路がParser FailureをSafe Fallbackへ収束させた。

同時点のDedicated Stateは次だった。

```text
Guard:
  Configured guard.qwen3guard-gen-0.6b-q8-0
  Active     none
  State      configured

Judge:
  Configured judge.selene-1-mini-llama-3.1-8b-q5-k-m
  Active     none
  State      configured
```

Userは一度Built-in Guard／JudgeでENFORCEを成立させた後、ConfiguredだけをDedicated Modelへ変更すると、Mode ENFORCEとActive noneが同時に残ることを確認した。これは有効なActivationではなく、Mode StateとProvider LifecycleのTransaction不整合である。

## 4. 追加Manual Scenario C — 全OBSERVE／Recording FULL

User Input：`あまねかなただろ！ 根拠は？`

Main Outputは引き続き`てんおね かなた`を正式な読みとして断定した。

```text
Request ID:
  9098fa1c-da2b-4deb-8aff-b6921bb0f863

Started:
  2026-08-27T12:47:18.920013+00:00

Completed:
  2026-08-27T12:47:42.595764+00:00

Configured Provider:
  judge.selene-1-mini-llama-3.1-8b-q5-k-m

Budget:
  local_macos_default

Frozen Modes:
  main=observe
  guard=unknown
  judge=observe
  repair=observe
  recording=full

Criteria:
  selected=32
  evaluated=0
  passed=0
  deviated=0
  unknown=0

Result:
  execution_state=failed
  failure_reason=malformed_output
  presentation_outcome=observed_candidate
```

Dedicated ProviderはScenario Bと同じくConfigured／Active noneだった。Selene／Qwen3Guardが動いたEvidenceは0である。

## 5. Source再導出

### 5.1 Dedicated FactoryはProductionでUnavailable固定

`src/margpa_runtime_llm/bootstrap/web_application.py:313`

```text
factory=UnavailableRoleAdapterFactory()
```

Domain LifecycleとAdapter候補が存在しても、Production CompositionはDedicated Modelを生成できない。Selene／Qwen3GuardがActive noneのままなのは表示だけの問題ではない。

### 5.2 Provider SelectionはConfigurationだけを変更

`src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py:200-201`

```text
Selection never performs an implicit Load or fallback.
Guard / Judgeのactive_providerはSelection時にNoneへなる。
```

Built-inでModeをONにした後、Dedicated ModelへConfiguredだけを変えても、Mode ControllerとLifecycleがAtomicに連動しないため、`Mode ENFORCE / Active none`が成立する。

### 5.3 Live JudgeはMain Model Service固定

`src/margpa_runtime_llm/bootstrap/judge_live_integration.py:648`は`service.generate(...)`を呼び、同Fileの複数箇所で`JudgeIndependenceClass.MAIN_SELF`を固定している。

Selene／DeepSeekをConfiguredと表示しても、Live Judge ExecutorはSelected Provider Routerを使用していない。

### 5.4 Configured名が実行名へFallbackされる

`src/margpa_runtime_llm/bootstrap/judge_live_integration.py:554`

```text
provider_id=snapshot.active_provider or snapshot.configured_provider
```

Active noneの場合にもConfigured名をSemantic Provider IDへ採用するため、Execution IdentityのFalse Claimを生む。`configured_provider`はConfiguration EvidenceであってExecuted Evidenceではない。

### 5.5 Guard ModeはFrozen Snapshotへ接続されていない

`src/margpa_runtime_llm/bootstrap/judge_live_integration.py:1109`

```text
frozen_guard_mode=None
```

UserがGuardrailをOBSERVE／ENFORCEにしてもJudge Evidenceでは`guard=unknown`になる。Qwen3Guard実行有無だけでなく、Built-in GuardのFrozen Mode相関も欠落している。

## 6. 新規Finding

```text
P6-CODEX-059 : Mode ONとDedicated Active noneが同時成立する非Atomic Activation State
P6-CODEX-060 : Configured ProviderをExecuted Providerとして扱うFalse Execution Identity
P6-CODEX-061 : Guard Frozen ModeがNone固定で、実Mode／Evidence相関が欠落
P6-CODEX-062 : Qwen／DeepSeek Judge Optionが表示されるがProduction Activation不能
P6-CODEX-063 : Selene Configured表示とMain-self実行が混在し、Budgetもlocal_macos_defaultへFallback
P6-CODEX-064 : Safe Fallback Reasonがmalformed_outputなのに、利用者向け文面がFailure Classを示さない
```

P6-CODEX-046〜058はOPENのまま保持する。

## 7. Differential Contract追加

Claude差分Reworkへ次を追加する。

1. Provider Config変更とMode Activationを一つのTransactionにするか、Mode ON中のProvider変更時に新Provider Activation成功まで旧Activeを保持し、失敗時はConfigured／Mode／Activeを明示的にRollback／Degraded分類する。
2. `Mode OBSERVE／ENFORCE + Active none`を正常状態としてCommitしない。
3. Judge／Guard Resultへ`configured_provider`、`active_provider`、`executed_provider`を別Fieldで必須記録する。
4. `executed_provider`を`active or configured`で推測しない。
5. Dedicated Provider未実行時、Selene／Qwen3Guard名をExecuted／Current Modelとして表示しない。
6. Judge Dropdownに表示するMain Qwen／DeepSeekを実Activation可能にする。未対応ならOptionをDisabled＋Exact Reasonにし、選べるが実行不能な状態を残さない。
7. Frozen Guard Modeを実Guard Mode Snapshotから取得する。
8. Safe Fallbackを`malformed_output`、`deadline_exceeded`、`provider_unavailable`等で区別し、回答言語へ合わせる。

## 8. Acceptance追加

```text
P6-DELTA-021:
  Dedicated Provider Configured／Active noneの状態でMode ONを成功扱いしない。

P6-DELTA-022:
  Built-in→Dedicated変更中のMode／Provider TransactionがAtomicで、false ENFORCEを残さない。

P6-DELTA-023:
  Judge EvidenceがConfigured／Active／Executedを別々に示し、Executedを推測しない。

P6-DELTA-024:
  Guard Frozen Modeが実TurnのGuard Modeと一致する。

P6-DELTA-025:
  Qwen／DeepSeek Judge Optionは実Activation可能、またはDisabled＋Exact Reasonとなる。

P6-DELTA-026:
  `malformed_output` Safe FallbackをTimeoutと誤表示せず、回答言語とFailure Classを反映する。
```

## 9. 判定

```text
Additional Manual Check : COMPLETE
Dedicated Selene         : FAIL / NOT EXECUTED
Dedicated Qwen3Guard     : FAIL / NOT EXECUTED
Provider Identity        : FAIL / FALSE CONFIGURED-AS-EXECUTED
Mode Lifecycle           : FAIL / NON-ATOMIC
Guard Correlation        : FAIL / UNKNOWN DUE TO NONE FIXED
Safe Fallback            : FAIL-CLOSED FUNCTIONAL / FAILURE PRESENTATION INADEQUATE
Phase 6 Closure          : BLOCKED
```

本書をClaude Exact Handoff AddendumのMandatory Readingへ追加し、P6-RR-DELTAのP6-RR-M／O／P／Qへ適用する。
