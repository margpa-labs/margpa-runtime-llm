# Phase 6 特殊最小Closure — Known Debt Deferred

```yaml
document_id: phase_6_special_minimal_closure_with_known_debt_20260829171422
document_state: closed_with_known_debt
phase: phase_6
language: ja
created_at: 2026-08-29 17:14:22 JST
decision_authority: user
authority_owner: Nazuna Research
technical_core_acceptance: failed_adjust
administrative_closure: complete
phase_7_transition: authorized
```

## 1. Closure Decision

Phase 6は中心Milestoneの技術合格として閉じるのではない。User Mac Manualで中心不成立を確認し、未解決をStable Registryへ固定したうえで、Resource／Portfolio／MVP優先により特殊最小Closureする。

```text
Phase 6 Technical Core: FAIL／ADJUST
Known Debt Recording: COMPLETE
Specified UI Fixes: COMPLETE／USER CONFIRMED
Administrative Minimal Closure: COMPLETE
Phase 7 Transition: USER AUTHORIZED
```

## 2. 成立した主要範囲

- Qwen Default、Qwen／DeepSeek切替、再起動後Qwen復帰。
- Conversation、Reload、二Tab、Citation、Branch継続。
- Context／Max New Tokens制御基盤。
- Judge／Repair／Recording／Provider Registry／Lifecycle／Lease／Cancellation／Shutdown／Correlation基盤。
- Recording Request相関とStop後Cancelled収束。
- DeepSeek病的反復の有界検出。
- Sidebar 2行表示、Guard未設定表示、Failure Code／Reason永続、Historical Recording Label分離。

## 3. 未成立の中心機能

- SeleneはConfiguredだが`Active none`、実Judge Call 0。
- Qwen3GuardはConfiguredだが`Active none`、実Guard Model Call 0。
- ARGD／DAGD Semantic 109件は全件Deferred。
- Built-in Deterministicはselected 32／evaluated 0／not_applicable 32／deferred 77。
- Judge結果はunknown／confidence 0。
- Repair／Rejudge／repair_accepted Golden Path未成立。
- Main Runtime Governanceの意味ENFORCE未成立。
- Qwen／DeepSeekの回答品質、Grounding、訂正追随は不合格。

正本は`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`とする。

## 4. Claim Correction

次を主張しない。

- Measurable Safety, Evaluation, and Repair Runtimeの完全達成。
- Dedicated Judge／Guard実用品質。
- Semantic 109件実行。
- Judge／Repair品質合格。
- Phase 6未解決0件。

Phase 7でRAG／Web Evidenceを追加しても、このDebtが自動解決したとは扱わない。

## 5. Verification Evidence

- Claude R25〜R28 Return：Backend 1811 passed、Mypy 483 files、Ruff、Frontend 231、Typecheck／Lint／Build PASS。
- Controller UI差分：Typecheck、Lint、Focused Frontend 54 Tests、Build PASS。
- Phase境界Canonical再検証：Backend 1811 passed／7 deselected、Mypy 483 files／0 issues、Ruff Format 483 files／Check PASS、Frontend 25 files／232 tests、Typecheck／Lint／Build PASS。
- User Mac：指定UI 4件、Main切替、Conversation継続、Restart、Recording、Stopを確認。
- User Mac：Selene、Qwen3Guard、Semantic 109、Judge／Repair中心Failureを確認。

最初のController再検証ではMarker名を`not real_model`と誤指定し、Project既定`not model_smoke`を上書きしたため、Real Model 6件がTask環境の`Failed to create llama_context`でFAILした。この実行はCanonical PASSへ数えず、正しいProject既定Commandを再実行して上記1811 PASS／7 deselectedを確定した。実Model FailureをRegression 0へ改変しない。

## 6. 次Phase品質境界

Known Debt受容はPhase 7を雑に作る許可ではない。Phase 7はFrozen Scopeの中心機能、正直なFailure、Data／Citation Integrity、RegressionおよびUser Manualを丁寧に成立させる。Enterprise Hardeningは追加しない。

## 7. Closure Authority

Userは、影響を理解した上でUI修正、未解決記録、反省、Phase 7進行および本Closure〜Handoffまでを明示許可した。本ClosureはUser Decisionを技術合格へ改変しない。
