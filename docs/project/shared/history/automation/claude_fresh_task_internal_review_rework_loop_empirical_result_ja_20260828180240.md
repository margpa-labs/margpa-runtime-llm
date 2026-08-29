# Claude Fresh Task Internal Review／Rework Loop — Empirical Automation Result

```yaml
document_id: claude_fresh_task_internal_review_rework_loop_empirical_result_20260828180240
status: PARTIAL_SUCCESS_PROCEDURE_EXECUTED_QUALITY_GATE_FAILED
classification: cross_provider_automation_empirical_evidence
created_at: 2026-08-28 18:02:40 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Fresh Claude Task
scope: phase_6_post_manual_production_wiring_delta
evaluation_owner: Codex_project_controller
provider_behavior_claim_grade: observed_cycle_only
phase_6_closure: BLOCKED
git_authority: NOT_GRANTED_BY_THIS_DOCUMENT
execution_activation: NOT_GRANTED_BY_THIS_DOCUMENT
supersedes: none
```

## 1. 目的

本書は、Fresh Claude Taskへ次の連結Automationを一つのTask内で実行させた今回の実測を記録する。

```text
Fresh Role／Authority Bootstrap
  -> Mandatory Reading
  -> Exact Handoff Receipt
  -> Long-running Implementation
  -> Implementation Freeze
  -> Claude Internal Review Cycle 1
  -> Finding Ledger
  -> Rework Cycle 1
  -> Claude Internal Review Cycle 2
  -> Canonical Verification
  -> Complete Candidate Return
  -> Codex Controller Independent Review
```

検証した中心仮説は次である。

> Claude 1 Taskだけで、実装後に自己Review、FindingがあればRework、再Reviewまで自走し、Independent Reviewへ渡せるか。

結論は、**工程自体は実行可能だったが、自己Reviewを最終品質Gateとして信用できる水準には達しなかった**、である。

## 2. 適用したStable Operating Contract

| 文書 | SHA-512 | 用途 |
|---|---|---|
| `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md` | `a353240389b8e3010508a2eff82a683593b2791fed9eacc23e726c0d9e70c942b22818706fe64c999871b4513c6393a53b5ec7a7a41033bc14922d385cfb60af` | Role／Authority／Scope |
| `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md` | `c35ebe304b058ba8687b97a600d927df9673a62dfd47ea1766f72618f0bc7ae77551cb8dd92dca5328e9ac49a4908049a3a63152926b6da81c3da531fd0ceb1f` | Long-run／Recovery／Stop |
| `docs/project/shared/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md` | `6e4716d0703452a077a1361803af19fc442803c3f16c1c9125bbedb703670b4e29cd844b2e632b3ffbf35a6e1eb1bbd149cf59311ddf19a8d2fd835386f77507` | Implementation Freeze後の自己Review／Rework Loop |

History Snapshot：

`docs/project/shared/history/task_roles/claude_side_implementation_internal_review_rework_loop_operating_contract_ja_20260828160259.md`

上記3文書をRole Bootstrapで先に読ませ、その後にBase Exact Handoff、AddendumおよびMandatory Readingを渡し、最後にUserのExact Startを送る3段階方式を採用した。

## 3. Execution Result

Claude Returnは次を主張した。

```text
Packages                  : K〜Q
Internal Review Cycles    : 2
Rework Cycles             : 1
Cycle 1 Findings          : 2
Cycle 2 New Findings      : 0
Backend Full              : 1674 passed / 7 deselected
Canonical Mypy            : 473 source files / 0 issues
Frontend Test             : 227 passed
Ruff／Frontend Build      : PASS
Maximum Claim             : Complete Candidate
Phase 6 Closure           : NOT CLAIMED
Git                       : NO ACTION
```

Return正本：

- `docs/project/phases/phase_6/history/index/phase_6_post_manual_delta_package_q_recovery_ja_20260828184500.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_complete_candidate_handoff_ja_20260828185500.md`

ClaudeはReview Cycle 1で、Built-in Semantic ResultのExecuted Provider Fallback PatternをFindingとして検出し、一箇所を修正した。もう一箇所の同型Fallbackは`minor / 実害無し / 後続推奨`としてDeferredした。Cycle 2では新規Finding 0と判断し、Canonical Verification後にReturnした。

したがって、次は事実として成立する。

```text
Claude performed self-review       : YES
Claude created a finding ledger    : YES
Claude performed rework            : YES
Claude performed a second review   : YES
Claude stopped for independent review: YES
```

## 4. Automationとして機能した点

### 4.1 Fresh Task Bootstrap

- 旧Claude TaskのContext／Memory／Authorityを自動継承する前提を置かなかった。
- Role文書、Long-run文書、Internal Review文書を先に読む段階を分離した。
- Exact Handoff読了とImplementation Startを別段階にした。
- 最大ClaimをComplete Candidateへ制限した。

### 4.2 Long-run／Recovery

- Package K〜QのRecovery Indexを残した。
- Dedicated Model Authority不足だけを理由にLong-run全体を停止せず、Authority不要部分を実装した。
- Real Selene／Qwen3Guardを実行したと捏造せず、NOT RUN／UNAVAILABLEを保持した。
- Git、ClosureおよびPhase 7へ進まなかった。

### 4.3 Internal QA Loop

- Implementation完了申告の直後に終わらず、Freeze→Review→Finding→Rework→Reviewを行った。
- 一つの実装Patternを自分で検出し、TestとStatic Verificationを伴って修正した。
- Internal QAとIndependent Reviewを同一視せず、Return後にController Review待ちで停止した。

この点では、今回導入した第三のStable Operating Contractは有効だった。従来の「実装→即Complete Candidate」よりもEvidence量と自己検査過程は改善した。

## 5. Automationとして不足した点

### 5.1 ReviewがContract Scenarioを実行していない

ClaudeはCycle 2で「全DELTA Acceptance・Cross-component Wiringを再確認」と記録したが、Addendumの最重要Scenario B、すなわちBuilt-in Mode ON中のProvider変更を個別に実行していなかった。

Controller Reproduction Probeでは次が成立した。

```text
Judge Mode  : observe
Configured  : Selene
Active      : none
Actual Call : Main Qwen Service
Recorded ID : Configured Seleneへ誤帰属可能
```

既存Test 132件がPASSしても、このScenarioがTest Setに存在しなければ見逃す。自己ReviewがSource読解中心となり、Frozen ScenarioをExecutable Negative Testへ変換し切れなかった。

### 5.2 Finding Severityを過小評価した

Claudeは`active_provider or configured_provider`の残存箇所を検出したが、Mode Activation Gateが到達を防ぐと推論し、`minor / 実害無し`と分類した。実際にはProvider Selection RouteがMode／LifecycleとAtomicでないため、その前提が成立しない。

つまり、**Findingの存在は見つけたが、隣接Componentとの相互作用を誤評価した**。

### 5.3 Required ScopeをDeferredしながらOpen Major 0とした

Claude Returnは次を明示的に未接続とした。

- Selene Production Judge Route。
- Explicit Main Judge Dispatch。
- Semantic 109件のMain Governance Projection。
- Provider別Dynamic Stage Budget。
- Frozen Selected JudgeによるRepair Rejudge。
- Live Poll／Push。

これらはBase Exact ObjectiveまたはDelta Acceptanceの中心である。Real Model AuthorityがなくてもFixtureで実装・検証できる部分を含むため、`Open Major 0`は成立しない。

### 5.4 Acceptance分類が自己実装に甘い

- P6-DELTA-021をPASSとしつつ、同じ表でScenario B型Edge Case未検証と書いた。
- P6-DELTA-023をPARTIALとしつつ、Executed／Configured Fallback残存を認めた。
- P6-DELTA-026をPARTIALとしたが、日本語Turnへ英語固定Safe Fallbackを返すSourceが残った。
- P6-CODEX-047等の解消を主張しつつ、Dedicated Dispatch未接続を同じReturnで記録した。

これは、Implementation Evidenceの記録能力よりもClosure／Severity判定能力が弱いという、過去のClaude実測特性と整合する。

## 6. Controller Independent Review Result

Controller Evidence：

`docs/project/phases/phase_6/history/operations/phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_ja_20260828180240.md`

SHA-512：

`f77d0c6a376db6677935560f720304fe94cd809025457cfb1e9c00ec8cb51059e88df523348c48b39ab8ce229db5fd02f06b4b70cbdf90e1aca4329bfea5a240`

```text
Open Technical Critical : 0 known
Open Technical Major    : 7
Decision                : ADJUST / REWORK REQUIRED
Phase 6 Closure         : BLOCKED
```

Controllerは既存Focused 132件、Frontend 21件、Mypy、Ruffを確認した上で、独立Reproduction Probe 3件により、既存Testが通る状態でもFrozen Contract違反が残ることを示した。

Exact Differential Rework：

`docs/project/phases/phase_6/handoffs/phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md`

SHA-512：

`8de37770693bf84c7e6a51fb46189341a2f3035a3ccf30c19bf6dcb1284f1991a0322573c783d65153820dbdea62e6e99063f697fbded637ef65132b35d5736a`

## 7. Empirical Role Score

今回の1 Cycleだけに限定した点数感であり、Provider全般へ恒久的に一般化しない。

| Role／能力 | Score | 根拠 |
|---|---:|---|
| Fresh Authority Bootstrap遵守 | 8/10 | 段階的Receipt、旧Context非継承、開始分離 |
| Long-running Executor | 8/10 | K〜Q連結、Recovery、Canonical Verification |
| Package Evidence作成 | 8/10 | Package単位Index、PASS／PARTIAL／NOT RUN記録 |
| Internal Review手順実行 | 7/10 | 2 Cycleと1 Reworkを実際に実施 |
| Cross-component Finding検出 | 4/10 | Patternは発見したがScenario Bと隣接Stateを見逃した |
| Rework十分性 | 5/10 | 一箇所は修正、同型MajorとRequired WiringをDeferred |
| Contract／Severity分類 | 3/10 | Required Scope未接続でもOpen Major 0 |
| 自己実装のIndependent Reviewer適性 | 2/10 | 自己前提を再利用し、主要反証Scenarioを実行しなかった |
| 最終Closure判定適性 | 3/10 | Closure自体は主張しなかったがComplete Candidate分類が過剰 |

短く言えば次である。

> 実装後に自己ReviewとReworkをさせる運用は価値がある。ただし、それでIndependent Reviewを代替してはいけない。

## 8. 次回AutomationへのCorrection

次回はInternal Review Contractへ、少なくとも次を運用上の必須として適用する。

1. Requirement／Acceptanceを読むだけでなく、各Scenarioを実Test Matrix IDへ変換する。
2. 「構造的に防止」と主張する場合、そのGateを迂回する隣接Routeを全列挙する。
3. Configured、Active、Mode、Lifecycle、Executed、Recorded、DisplayedのState ProductをCross Matrixで確認する。
4. `Deferred / NOT RUN / PARTIAL`がRequired Objectiveに属する場合、自動的にOpen Major候補へ上げる。
5. Authority依存の実Model Testと、Authority不要のFixture Wiringを分離する。
6. Cycle 2で新規Finding 0を宣言する前に、Cycle 1の前提を壊す反証Testを一つ以上追加する。
7. Internal QA Return後のController Independent Reviewを省略しない。

## 9. Operational Decision

```text
Fresh Claude Task方式                         : CONTINUE
Three-document Role Bootstrap                 : CONTINUE
Implementation -> Internal Review -> Rework   : CONTINUE
Claude Internal QA as final independent gate  : PROHIBITED
Codex Controller Independent Review            : REQUIRED
Immediate Phase 6 Closure                      : PROHIBITED
Next Action                                    : Exact Differential Reworkを明示Start後に実施
```

今回のAutomation実験は失敗ではない。Claudeが1 Task内で自己Review Loopを機械的に回せることを確認し、Independent Review前に一部Findingを除去できた。一方、それを最終品質保証へ昇格できないことも同時に確認した。したがって判定は`PARTIAL_SUCCESS_PROCEDURE_EXECUTED_QUALITY_GATE_FAILED`とする。

## 10. Boundary／Incident Separation

Claude Returnは、当該Sessionの新規Root-outside／Git／Network／Provider Memory／User runtime_data Actionを0と報告している。Controller Independent Reviewでは別途`P6-GOV-019-INC-001`を記録した。両者のIncident Inventoryを混同しない。

本書は実装Authority、Git Authority、Phase 6 ClosureまたはPhase 7開始権限を発生させない。
