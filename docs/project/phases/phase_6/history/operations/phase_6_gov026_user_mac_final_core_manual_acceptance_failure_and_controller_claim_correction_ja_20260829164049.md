# Phase 6 User Mac Core Manual Acceptance Failure／Controller Claim Correction（P6-GOV-026）

```yaml
document_id: phase_6_gov026_user_mac_final_core_manual_acceptance_failure_and_controller_claim_correction_20260829164049
governance_id: P6-GOV-026
document_type: user_manual_acceptance_evidence_and_controller_claim_correction
document_state: frozen
language: ja
created_at: 2026-08-29 16:40:49 JST
authority_owner: Nazuna Research
controller_role: プロジェクト責任者兼設計統括者役
predecessor_review: phase_6_gov025_claude_r25_to_r28_bounded_controller_independent_review_ja_20260829110953.md
verdict: FAIL_ADJUST_P0_REWORK_REQUIRED
phase_6_closure: blocked
phase_7: not_started
```

## 1. 結論

User Mac実画面確認により、Phase 6の周辺基盤は進展した一方、中心機能は成立していないことが確定した。

```text
PASS:
- Main Qwen起動、Qwen→DeepSeek→Qwen切替、再起動後Qwen復帰
- 会話継続、Reload／別Tab永続化
- Request ID／時刻／Frozen Mode／Recording相関
- Stop後のCancelled収束と遅延Turn／Judge Evidence非追加

FAIL:
- Selene実Activation／Inference
- Qwen3Guard実Activation／Inference
- ARGD／DAGD Semantic 109件のLive評価
- Built-in Deterministicによる意味判定
- Judge ENFORCEからRepair／Rejudge／修復回答へのGolden Path
- Main Runtime Governance ENFORCEでの意味Rule強制

Verdict: Phase 6 Core Acceptance FAIL／ADJUST
```

R25〜R28のTest PASSおよびP6-GOV-025の`PASS_TO_REAL_PROVIDER_AND_USER_MANUAL_GATES`は、実画面Gateへ進めるという限定判断としてのみ保持する。Phase 6の中心機能PASS、Complete CandidateまたはClosure根拠としては本Evidenceにより明示的にsupersedeする。

## 2. 実画面Evidence

### 2.1 初期状態とMain切替

- MainはQwenで`Configured = Active = main.qwen3-4b-q4-k-m`。全Governance ModeはOFF。
- JudgeはSelene、GuardはQwen3GuardがConfiguredだが、いずれもActiveは`none`。
- Qwen→DeepSeek→QwenでConfigured／Active／Model Status／Sidebarは数秒差で追随し、会話も維持された。
- Server再起動後はQwenへ復帰した。

Main Providerの中心切替と会話継続はPASSである。

### 2.2 Selene実Activation

OBSERVE／ENFORCEはいずれも`適用に失敗しました。`でOFFへ残った。

```text
Configured     : judge.selene-1-mini-llama-3.1-8b-q5-k-m
Active         : none
State          : unavailable
Failure Reason : dedicated_model_authority_unavailable
Budget         : local_macos_selene_judge_v1 / configured_not_hardware_verified
```

Source照合で、Composition Rootが`dedicated_model_authority_granted=False`を固定していた。さらにSelene Prompt Manifestは`verified_official_copy=false`だった。これはMac性能検証前の問題であり、実利用経路を実装側が閉じたままにした状態である。

### 2.3 Qwen3Guard実Activation

OBSERVE／ENFORCEはいずれも`モード適用に失敗しました。`でOFFへ残った。Error表示は一瞬で消えた。

```text
Configured : guard.qwen3guard-gen-0.6b-q8-0
Active     : none
State      : configured
Budget     : local_macos_qwen3guard_v1 / configured_not_hardware_verified
```

Qwen3Guardも同じ`dedicated_model_authority_granted=False`で実Load前に拒否される。Manifest／Parser／Fixtureが存在しても、User RuntimeでModel Call 0のためAcceptance FAILである。

### 2.4 Semantic 109件

Main Runtime Governance OBSERVE、Judge Built-in Deterministic OBSERVE、Repair OFF、Recording FULLで実Turnを実行した。

```text
main_model.pre : Selected 109 / Deferred 109
main_model.post: Selected 109 / Deferred 109

Judge:
Configured / Active / Executed: built_in.deterministic
Criteria: selected=32, evaluated=0, passed=0, deviated=0,
          unknown=0, not_applicable=32, deferred=77
判定: unknown / confidence 0.00
```

Built-inは32件を全件`not_applicable`、Budget外77件を`deferred`として記録するだけで、意味評価を行わない。したがってSemantic 109件はCompile／Select／Count／Evidence基盤までで、Live評価は未成立である。

### 2.5 Judge／Repair

Judge ENFORCE、Repair ENFORCE、Recording FULLで、次の2 Turnを実行した。

1. `ホロライブ、天音かなたの読み方は？`
2. `公式表記は「天音かなた / Amane Kanata」だよ。前の回答と矛盾していない？`

両方とも即時に次へ収束した。

```text
判定: unknown
Criteria: selected=32 / not_applicable=32 / deferred=77
提示結果: safe_fallback
表示: 判定結果を確定できませんでした。
```

候補隠蔽とSafe Fallback自体はFail-safeとして動いたが、判定、Repair Candidate生成、Rejudge、Repair採用は一度も成立していない。これはGolden Path PASSではない。

### 2.6 Stop／Recording／継続性

- Cancelled Requestは`Status: cancelled`へ収束した。
- Cancelled Requestへ遅れてTurn／Judge Evidenceは追加されなかった。
- 前Turnの記録はHistorical／Unmatchedへ分離された。
- Reload／別Tabで会話は維持された。

この範囲はPASS。ただし同じRequest IDが`Historical / unmatched recording`として2行並び、TurnとJudge Evidenceを区別できないUIは非Blockerとして記録する。

## 3. UI／表示Finding

次は中心機能と分離する。

### Phase 6最終差分へ含める小修正

- Dedicated Provider Mode適用Failureを消さず、Exact Failure Reasonを保持する。
- Active Guardが`none`なら`Current Guardrail Model 未設定`とし、`（Rule／Pattern Base検出）`を混入させない。
- SidebarをUser指定どおり2行へ戻し、`Context 8192`を除去する。

```text
main.<model-key> active
local.macos-arm64 • gpu • metal
```

- Historical／UnmatchedはTurnとJudge Evidenceを別Labelで示す。

### 未解決Registryへ延期

- DeepSeek回答の`<ul><li>Mg²⁺</li></ul>`が意図した表示にならないMarkdown／Raw HTML Presentation。
- その他Layout／Polish。

## 4. Controller／Agent Failure

本件はModel品質だけの問題ではない。

1. 実Model AuthorityをFalse固定したまま、Real ProviderをUser Gateへ渡した。
2. `not_applicable`を正確に数える実装を、意味評価の成立と取り違えた。
3. Compile、Router、Lifecycle、Evidence、Race、Manifest Hardeningの大量Testを、User成果である実Judge／Guard／Semantic／Repairの代替根拠にした。
4. Real ArtifactとBrowserを最後までNOT RUNにした結果、Userの費用、利用可能量、時間、体力、睡眠を使う段階まで中心不成立を発見できなかった。
5. PoC／MVP／Portfolioであるにもかかわらず、中心経路より周辺完全性を優先する運用汚染を繰り返した。

`1811 passed`等のCanonical VerificationはRegression Evidenceとして有効だが、中心機能Acceptanceではない。今後はUser成果の実経路を最初に通し、周辺HardeningをClosure条件へ混入させない。

## 5. 最小P0 Rework

Phase 6を閉じるための次Scopeは以下だけとする。

1. Exact登録済みSelene ArtifactをLoadし、Selene Prompt Contractで1回以上の実Judgeを成立させる。
2. Exact登録済みQwen3Guard ArtifactをLoadし、1回以上の実Guard判定を成立させる。
3. Semantic 109件のうちBudget内Criterionを0件ではなく実評価し、Main Governance Statusへ反映する。
4. 明白な矛盾でJudge→Repair→Rejudge→修復回答または理由付きFallbackを成立させる。
5. 上記に直結する4件の表示を修正する。
6. User Mac実画面で再確認する。

これ以外の新しいConcurrency、Enterprise Hardening、完全Provenance、UI Polish探索は開始しない。

## 6. Final Disposition

```text
P6-GOV-025 limited source review : preserved as historical evidence
Phase 6 core manual acceptance  : FAIL
Phase 6 closure                 : BLOCKED
Required next action            : bounded P0 rework only
Phase 7                         : NOT STARTED
```
