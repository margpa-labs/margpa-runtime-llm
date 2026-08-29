# Phase 6 Claude Production Wiring Delta Exact Handoff — P6-GOV-018 Addendum

```yaml
document_id: phase_6_claude_post_manual_production_wiring_delta_exact_handoff_addendum_20260827215158
status: frozen_prepared_not_active
classification: append_only_exact_handoff_addendum
phase: phase_6
from_provider: Codex
from_role: プロジェクト責任者兼設計統括者役
to_provider: Claude
to_role: 設計者兼実装者役
created_at: 2026-08-27 21:51:58 JST
base_handoff: phase_6_claude_post_manual_production_wiring_delta_exact_handoff_ja_20260827211749.md
implementation_authority: false
activation_key_2_user_start: missing
closure_authority: false
git_authority: false
```

## 1. Addendum Authority

本書は、Base Exact Handoff発行後にUserが追加実施したManual Scenario A〜CとSource再導出を、Append-onlyでExecution Contractへ追加する。

Base Handoff：

```text
docs/project/phases/phase_6/handoffs/
phase_6_claude_post_manual_production_wiring_delta_exact_handoff_ja_20260827211749.md

SHA-512:
0ff64eb24991a2fafa1b96a32af3555f949c3546339f27e5d79b66d6ff0e0149913379c9c6c2ca56827a1d79b9b140fe692874cad9c14c0ba94089aa6968eb91
```

追加Manual／Source Evidence：

```text
docs/project/phases/phase_6/history/operations/
phase_6_gov018_user_mac_provider_false_activation_and_execution_identity_addendum_ja_20260827215158.md

SHA-512:
4dc8792b65d9cee6161c3f5513b36cbc97a381427d62653063c49d341f9747db351257e449d35681c928a362bfe31d8cd5ede692c448e1a29593ba5c22d26df3
```

Base Handoffと本Addendumが衝突する場合、本Addendumを優先する。衝突しないAuthority、Scope、Temporary、Stop、Verification、Return ContractはBase Handoffをそのまま維持する。

## 2. Mandatory Reading追加

Base Handoff §4の21文書を読んだ直後、22番目としてP6-GOV-018、23番目として本Addendumを全文読む。

```text
22. docs/project/phases/phase_6/history/operations/
    phase_6_gov018_user_mac_provider_false_activation_and_execution_identity_addendum_ja_20260827215158.md

23. docs/project/phases/phase_6/handoffs/
    phase_6_claude_post_manual_production_wiring_delta_exact_handoff_addendum_ja_20260827215158.md
```

Activation Phraseは変えない。

```text
Phase 6 Production Wiring Delta Reworkを開始する。
```

本Addendumを渡しただけではImplementation Authorityは発生しない。

## 3. Corrected As-built Claim

次をCurrent As-builtの正本とする。

```text
Dedicated Selene Active / Executed       : NO
Dedicated Qwen3Guard Active / Executed   : NO
Live LLM Judge Executor                  : Main Model service / MAIN_SELF
Built-in Deterministic Actual Executor   : Main-self pathへ流れるためFalse
Configured Provider in Judge Result      : Configuration identity only
Active Provider none                     : Dedicated execution 0を示す
Executed Provider Field                  : Missing
Frozen Guard Mode                        : None固定 / UIではunknown
Mode ENFORCE + Active none               : Reproducible invalid committed state
```

Selene／Qwen3Guardが「動いたかもしれない」という表現をReturn、Evidence、UI、Acceptanceへ残さない。Active noneである限り、Dedicated Model実行は0である。

## 4. Source Anchors

ClaudeはP6-RR-K Source Mapで少なくとも次を再確認し、記憶でPathを置換しない。

```text
src/margpa_runtime_llm/bootstrap/web_application.py:313
  factory=UnavailableRoleAdapterFactory()

src/margpa_runtime_llm/modules/runtime_model_control/application/
provider_selection_controller.py:200-201
  SelectionはLoadせず、Guard／Judge active_providerをNoneにする

src/margpa_runtime_llm/bootstrap/judge_live_integration.py:648
  Main service.generate()を呼ぶ

src/margpa_runtime_llm/bootstrap/judge_live_integration.py:639-731 and related exits
  judge_role=MAIN_SELF固定

src/margpa_runtime_llm/bootstrap/judge_live_integration.py:554
  provider_id=active_provider or configured_provider

src/margpa_runtime_llm/bootstrap/judge_live_integration.py:1109
  frozen_guard_mode=None
```

Line Numberは現在Evidenceの補助であり、実装時にFile本文でSymbolとCall Graphを確認する。

## 5. Package Contract追加

### 5.1 P6-RR-Mへ追加

#### M-WU-005 Mode／Provider Atomic Transition

- Mode OFF→OBSERVE／ENFORCE時は、Configured Provider Activation成功後だけModeをCommitする。
- Built-in Active中にDedicated ProviderへConfigured変更する場合、新ProviderのPreflight／Load／ActivationとMode Stateを一つのTransactionとして扱う。
- 失敗時は、旧Activeを維持するかMode OFFへRollbackする。`Mode ON / Active none`を成功状態にしない。
- Provider変更だけで既存Activeを失う場合は、UIへTransition／Rollback／Failureを明示する。

#### M-WU-006 Executed Identity Contract

- Turn Frozen SnapshotへConfigured、Active、Executedを別Fieldとして保持する。
- ExecutedはAdapter Leaseから取得し、Configured名から推測しない。
- `active_provider or configured_provider`をExecution Identityに使用しない。

### 5.2 P6-RR-Nへ追加

#### N-WU-006 Built-in No-LLM Proof

- Built-in Deterministic実行時、Main／Selene／DeepSeek Model Call Countが0であるRegressionを追加する。
- Built-in Resultは対応可能Criterionだけを決定論評価し、未対応をTyped Unknown／Deferredにする。
- `malformed_output`をBuilt-in正常経路のOutcomeにしない。

### 5.3 P6-RR-Oへ追加

#### O-WU-006 Main Model Judge Options

- Judge DropdownのQwen／DeepSeek OptionをProduction Lifecycle／Routerへ接続する。
- 実行不能な構成ならOptionをDisabledにし、Exact Reasonを表示する。
- 選択可能だがMode Activation不能という状態を残さない。

#### O-WU-007 Guard Frozen Correlation

- Judge／Recording Frozen Snapshotへ実Guard Modeを格納する。
- Built-in Rule／PatternとDedicated Qwen3GuardのExecuted Identityを別々に記録する。
- Dedicated Active none時はQwen3GuardをExecutedと記録しない。

### 5.4 P6-RR-Pへ追加

#### P-WU-006 Invalid State／Failure Presentation

- Provider Selection Panel、Feature Mode Panel、Judge ResultにConfigured／Active／Executedを明記する。
- `Mode ON / Active none`をError／Degradedとして表示し、通常Active表示にしない。
- Failure Messageを`malformed_output`、`deadline_exceeded`、`provider_unavailable`、`activation_failed`で分ける。
- User回答言語へ合わせ、Userの再試行や情報源確認がFailure原因だったかのような文面を使わない。

### 5.5 P6-RR-Qへ追加

#### Q-WU-007 Manual Reproduction Regression

P6-GOV-018 Scenario A〜CをControlled Test／Browser Matrixへ変換する。

```text
A: Judge=DeepSeek Configured / Active none / OBSERVE
B: Built-inでENFORCE後、Selene／Qwen3GuardへConfigured変更
C: Selene／Qwen3Guard Configured / Active none / OBSERVE
```

期待結果は、Dedicated Providerが動いたように表示することではない。Production Factory／Authorityが成立すればActive／Executedへ遷移し、成立しなければMode／Failure／Identityが正確にRollback・表示されることである。

## 6. Acceptance追加

Base FreezeのP6-DELTA-001〜020に、次を追加する。

| ID | Acceptance |
|---|---|
| P6-DELTA-021 | Dedicated Configured／Active noneの状態でOBSERVE／ENFORCEを正常Commitしない。 |
| P6-DELTA-022 | Built-in→Dedicated変更のProvider／Mode TransitionがAtomicで、False ENFORCEを残さない。 |
| P6-DELTA-023 | Configured／Active／Executedが別々に記録され、ExecutedをConfiguredから推測しない。 |
| P6-DELTA-024 | Frozen Guard Modeが実TurnのGuard Modeと一致し、`unknown`固定にならない。 |
| P6-DELTA-025 | Qwen／DeepSeek Judge Optionは実Activation可能、またはDisabled＋Exact Reasonとなる。 |
| P6-DELTA-026 | Safe FallbackがMalformed／Timeout／Unavailableを区別し、回答言語に従う。 |

Final ReturnはOriginal Acceptance 40件とDelta Acceptance 26件を全件示す。

## 7. Failure Classification Correction

Request `916f319d-3e6e-46a9-93a8-d74507575006`は次である。

```text
Elapsed       : 約24.3秒
Recorded Code : malformed_output
Disposition   : safe_fallback / candidate_withheld
```

`deadline_exceeded`または「30秒Timeout」と分類しない。Safe Fallback自体はJudge ENFORCE Fail-closedとして作動したが、Failure Presentationは不正確・不十分である。

## 8. Return Format追加

Base Handoff §16へ次を追加する。

```text
Mode / Provider Atomic Transition result
Built-in→Dedicated switch rollback evidence
Configured / Active / Executed separate identities
Executed Provider derivation source
Built-in Deterministic Model Call count = 0 evidence
Frozen Guard Mode evidence
Qwen / DeepSeek Judge option activation or disabled reason
P6-GOV-018 Scenario A-C regression result
Delta Acceptance 001-026 disposition
```

## 9. Completion Boundary

Completion Claim BoundaryはBase Handoffから変えない。

```text
Maximum Claude Claim:
  Phase 6 Production Wiring Delta Rework COMPLETE_CANDIDATE

Forbidden Claim:
  Phase 6 Closure
  Dedicated Provider PASS without Active / Executed Evidence
  Incident 0
  Git / Backup / Roadmap / Phase 7 Ready
```

Return Handoff作成後はController Independent Reviewで停止する。
