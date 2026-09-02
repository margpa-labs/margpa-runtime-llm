# Phase 9-1 Corrected User Manual／Recheck Sheet

```yaml
document_id: phase_9_1_corrected_user_manual_recheck_sheet_20260831234930
document_state: user_manual_gate_ready_not_run
language: ja
created_at: 2026-08-31T23:49:30+09:00
phase: phase_9
program: phase_9_1
real_browser_run_by_executor: false
real_model_run_by_executor: false
```

## 1. 目的と停止線

Provider変更前のBuilt-in結果やHistorical Resultを、新Providerで実行した結果と誤認しないための正順Manualである。ExecutorはReal Browser／Real Modelを実行していない。Userが実画面で確認するまでDispositionは`USER MANUAL GATE / NOT RUN`とする。

Dedicated Selene／Qwen3Guard Smokeは、別途Real Artifact AuthorityをUserが明示した場合だけ実施する。Startup Opt-inはAuthority Receiptの代替ではなく、FlagだけではModelをLoadしない。

## 2. 起動前の選択

### Main-shared self-judge確認

Dedicated Startup Authority Flagは付けない。通常のlocal loopback起動で、Phase 6 Runtime Model Control／Feature Modesを有効にする。Current Main Provider名を控える。

### Dedicated Smoke（別Authorityがある時だけ）

local loopback限定で、通常のFeature Flagに加えて次を明示する。

```text
--phase-6-dedicated-model-authority
```

このFlagだけでStartup Loadは起きない。Provider選択とMode ON後にのみPreflight／Candidate Loadへ進む。Authorityがない場合、この節は実施せず`RESOURCE_GATED / NOT RUN`を保持する。

## 3. Correct User Manual Order

### Step 1 — Judge ModeをOFFへ戻す

Advanced SettingsでJudge Modeを`OFF`にする。Repair確認前はRepair Modeも`OFF`にする。Current Judge Resultが「実行なし」、前回ResultがHistoricalとして分離されることを確認する。

確認欄：`[ ] Judge OFF` `[ ] Currentなし` `[ ] Historical分離`

### Step 2 — Judge Providerを選択する

Main-shared self-judgeの場合は、Current Mainと同一のProvider（QwenまたはDeepSeek）をJudge Dropdownで選ぶ。Dedicated確認の場合だけSeleneを選ぶ。Built-in DeterministicはCanonical 109の質的Criterionを評価できず、109件NOT_APPLICABLE／evaluated 0が正しいため、Semantic実評価確認には使用しない。

確認欄：`[ ] Current Main記録` `[ ] 意図したJudge Providerを選択`

### Step 3 — OFF状態のProvider Stateを確認する

Provider変更直後はModeが安全側でOFFである。直前TurnがまだLeaseを保持している場合は`active_turn_drain_pending`等のtyped pending stateを記録し、Turn終了とUnload収束を待つ。収束後の表示を次のように確認する。

```text
Configured Provider = 新しく選択したProvider
Active Provider     = none／未Active（drain収束後のOFF期待値）
State               = configured／none相当（pending中または収束後をActiveと偽装しない）
Failure Reason      = 無し、または正確なtyped gate reason
```

確認欄：`[ ] Configured一致` `[ ] drain待機` `[ ] OFF中Active偽装なし` `[ ] State／Reason記録`

### Step 4 — 目的に応じModeを再適用する

- 評価だけ：Judge `OBSERVE`、Repair `OFF`。
- Presented Finalまで強制確認：Judge `ENFORCE`。
- Repair／Rejudge確認：Judge `ENFORCE`、Repair `ENFORCE`。
- Evidence確認：必要に応じRecording `FULL`。

Provider変更でOFFへ戻った後は、必ずここでJudge Modeを再適用する。以前のMode表示を信用してTurnへ進まない。

確認欄：`[ ] Judge再適用` `[ ] Repair目的どおり` `[ ] Recording目的どおり`

### Step 5 — ON後のProvider Stateを確認する

Turn送信前にConfigured／Active／Stateをもう一度確認する。Main-sharedならConfiguredとActiveがCurrent Mainと一致し、Independenceが`self`であること。DedicatedならPreflight／Load成功時だけActiveとなり、失敗時は`RESOURCE_GATED／FAILED`とReasonが表示されること。

確認欄：`[ ] Configured=Activeまたはtyped failure` `[ ] self／independent表示正確`

### Step 6 — 必ず新しいTurnを送信する

Provider／Mode設定後に新しいChat Turnを送信する。設定前のTurn、Built-in Turn、Historical Last Resultを検証対象にしない。Request IDと開始時刻を控える。

確認欄：`[ ] 新Turn送信` `[ ] Request ID記録` `[ ] Historicalと混同なし`

### Step 7 — Semantic 109とExecuted Providerを確認する

同じRequest IDについて次を確認する。

```text
evaluated = passed + deviated（実評価分）
passed + deviated + unknown + not_applicable + deferred = 全対象109
selectedは今回Providerへ渡したBatch数として別に記録し、Outcome総和へ二重加算しない
unknown／not_applicable／deferredはReason付き
Configured Provider／Active Provider／Executed Providerが矛盾しない
Main-sharedはmain_self、Seleneはindependent_artifact
```

Main-sharedでは`evaluated > 0`となる新Turnを確認する。Built-inの`evaluated 0`をMain-sharedの失敗と誤認しない。

確認欄：`[ ] Outcome 109総和` `[ ] selected別記録` `[ ] evaluated整合` `[ ] Reasons` `[ ] Executed Provider一致`

### Step 8 — Repair／Rejudgeを確認する（Repair ENFORCE時）

Material Deviationを生む検証入力を新Turnで送る。同じRequest相関で次を確認する。

```text
:judge -> :repair -> :rejudge
Repair Candidateは原Candidateと別Identity
Rejudge Provider／RoleはTurn開始時のFrozen Judge Identity
Adopt／Reject／Safe Fallback／FailureとPresented Finalが一致
Budget／Deadline／Max Repairが有界
```

確認欄：`[ ] 3 stage` `[ ] Candidate別Identity` `[ ] Frozen Rejudge` `[ ] Final一致`

### Step 9 — OFF／Stopを確認する

Judge／RepairをOFFへ戻す。Active Turn完了後にDedicated ProviderがUnloadされること、以後の新TurnでJudge／Repair Call 0、Late ResultがCurrentへ追加されないことを確認する。アプリ停止後にFalse Cleanを表示しないことも確認する。

確認欄：`[ ] OFF` `[ ] Unload／非Active` `[ ] Call 0` `[ ] Late Current追加0` `[ ] Stop clean`

## 4. Result Sheet

```text
Environment／Main Provider:
Startup dedicated authority flag: NOT USED / USED WITH EXPLICIT AUTHORITY
Judge Provider:
Judge Mode:
Repair Mode:
Recording Mode:
Request ID:
Configured / Active / Executed:
selected / evaluated / passed / deviated / unknown / not_applicable / deferred:
Judge / Repair / Rejudge Identity:
Final Disposition:
Failure Reason:
Dedicated Artifact Result: RESOURCE_GATED / FAILED / PASS (User evidence required)
Manual Disposition: PASS / FAIL / STOPPED_SAFE
```

## 5. Executor Claims Not Made

Real Browser PASS、Real Selene／Qwen3Guard PASS、User Manual PASS、Phase 9-1 Closure、P9-2 Readyを主張しない。
