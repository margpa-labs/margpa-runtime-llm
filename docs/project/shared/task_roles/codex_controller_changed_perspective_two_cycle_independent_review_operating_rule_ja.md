# Codex Controller — 観点変更型二段階Independent Review運用Rule

```yaml
document_id: codex_controller_changed_perspective_two_cycle_independent_review_operating_rule
document_type: stable_controller_operating_rule
document_state: stable_current
language: ja
created_at: 2026-08-31 07:08:40 JST
owner_provider: Codex
owner_role: プロジェクト責任者兼設計統括者役
applies_to: material_implementation_candidate_and_phase_closure_review
```

## 1. 目的

Materialな実装Candidateに対し、同じ観点とTestを繰り返すのではなく、仮説、Source Order、Negative ProbeおよびClaim監査を変えた
二段階のController Independent Reviewを原則とする。

```text
Review Cycle数を増やすこと
≠ Review観点を変えること
≠ 品質が自動的に上がること
```

本Ruleは、1回目で「実装した修正が動く」ことを確認し、2回目で「その修正により上位要件とClaimが本当に成立したか」を再導出する。

## 2. Default Review Flow

```text
Executor Internal Review
→ Complete Candidate Return
→ Controller Cycle 1: Targeted／Implementation-relative Review
→ Controller Cycle 2: Assumption-reset／Requirement-relative Review
→ P0だけBounded Rework
→ Final Targeted Verification
→ User Manual Acceptance
→ Closureまたは明示された最小残件
```

Executor自身のInternal Review／Rework／Re-reviewは重要な実装工程だが、Controller Cycle 1またはCycle 2の代替にはしない。

## 3. Cycle 1 — Targeted／Implementation-relative Review

Cycle 1は、Executor Returnの申告内容と変更差分を直接検証する。

必須観点：

1. Exact Handoffで指定したFinding別解消条件。
2. Changed Pathsと実Source。
3. Focused Testが対象BugをFix前に検出できるか。
4. Happy Path、Failure Path、Identity、PersistenceおよびUI Projection。
5. ReturnのTest数、Acceptance集計、NOT RUN／PARTIAL／FAIL開示。
6. Regressionが変更範囲に比例して抑えられているか。

Cycle 1の問いは次である。

> Executorが「直した」と申告したものは、申告どおり実際に動くか。

## 4. Cycle 2 — Assumption-reset／Requirement-relative Review

Cycle 2はCycle 1のPASSを前提にしない。Source Orderを実装差分からFrozen Contractへ切り替える。

推奨順序：

```text
User Decision／PoC停止線
→ Frozen Requirements
→ Exact Handoff
→ Acceptance Matrix
→ Production Composition Root
→ Persistence／Reload／Restart
→ API／SSE／UI Presentation
→ Changed Source／Tests
→ Return Claim
```

必須観点：

1. 要件の一部だけを実装し、広いAcceptanceへ昇格していないか。
2. Class／Port／Unit Testの存在をProduction Wiring成立と混同していないか。
3. Contract FieldとRuntime実挙動、UI表示、Persistenceが同じTruthを表すか。
4. Current Manifest／Registry／Configurationで実際に到達する値をProbeしたか。
5. OFF／Disabled／Unavailable／Unsupported／FailureをSuccessへ見せていないか。
6. Identity、Authority、Concurrency、Late ResultまたはCross-run再利用を反転したNegative Probe。
7. Acceptance集計、最大ClaimおよびUser Manual Ready判定をSourceから再導出したか。
8. Cycle 1が採用したSolution Boundary自体に抜けがないか。

Cycle 2の問いは次である。

> その修正だけで、上位要件、Composition、User表示およびAcceptance Claimは本当に成立するか。

## 5. 二段階Reviewとして数えないもの

- 同じTest Suiteを二回実行するだけ。
- 同じChanged Pathsを同じ順番で再読するだけ。
- Cycle 1の結論を言い換えるだけ。
- ExecutorのInternal ReviewをController Cycle 1として扱う。
- Test PASSを根拠にRequirements／Acceptance再導出を省略する。
- 新しいHardening観点を無制限に追加する。

## 6. Proportional Application

二段階ReviewはDefaultであり、全変更へ機械的にFull適用する絶対規則ではない。

### 6.1 二段階を原則必須とする変更

- Phase Closure Candidate。
- Authority、Approval、Gate、Security Boundary。
- Persistence、Migration、Reload／Restart Recovery。
- Provider／Model Selection、Lifecycle、Concurrency、Cancellation。
- Runtime Composition、Production Wiring、Cross-provider Handoff。
- UserにSuccess／Active／Verified／PASSを表示するUI。
- Acceptance集計またはComplete Candidate Claimを変更する実装。
- 複数Subsystemを跨ぐMaterial Diff。

### 6.2 一段階へ縮退できる変更

- Typo、Link、明白なDocs整形。
- Behaviorを変えない機械的Rename／Format。
- 単一の既知UI文言またはCSS微修正で、Data／Authority／Persistenceへ影響しない。
- Userが明示的に一段階で十分と判断した場合。
- Resource Hard Stopが近く、Cycle 2を後続Reviewとして明示予約した場合。

縮退時は、なぜCycle 2を省略したかをReturnまたはReviewへ一行で記録する。

## 7. Review Budget／終了条件

二段階Reviewは無限Review Loopを許可しない。

```text
Cycle 1
→ Cycle 2
→ P0だけRework
→ Final Targeted Verification
→ User Manual
```

- Cycle 2で見つかったP1以下はStable未解決Registryへ送る。
- Frozen AcceptanceをReview中に追加しない。
- Product／Enterprise HardeningをPoC／MVP Closureへ後付けしない。
- Final Targeted Verification後に、別観点のFull Cycle 3を自動開始しない。
- User実画面テストで初めて分かるものは、理論Reviewを増やさずUser Manualへ渡す。
- Data破損、Authority Bypass、虚偽Success、次Phase基盤破壊等のP0だけを即時Reworkする。

Review Budgetには次を含める。

- Codex／Claude／Copilot等の週間利用可能量とSession制限。
- Context／Compaction Cost。
- Userの金銭、時間、睡眠、Manual Test負担および画面張り付き時間。
- Portfolio公開、応募および就職Timing。

## 8. Cycle別Evidence

Review記録ではCycleを混ぜず、最低限次を残す。

```text
Cycle 1:
  Target Findings
  Source／Test範囲
  Focused Probe
  Disposition

Cycle 2:
  Changed Perspective
  Frozen Contract再導出
  Negative／Composition Probe
  New FindingまたはNo New Finding
  Acceptance再集計

Final:
  Closure Blocker
  Non-blocking Finding
  User Manual Ready
  Exact Next Action
```

2回目で新Findingが無くても、それ自体をFailureとは扱わない。観点を変えて再導出したEvidenceがあれば成立する。

## 9. Finding返送時のController義務

Cycle 1またはCycle 2の結果をExecutorへReworkとして返す場合、Controllerは同じUser-facing Responseで必ず次を作る。

1. Exact Differential Rework Handoff。
2. Absolute PathとSHA-512。
3. Userがそのまま貼れるProvider向け指示文。
4. Fresh／Continued／Resumed Taskの区別。
5. 成立済み範囲と再実行禁止範囲。

Review結果だけを返し、UserへHandoff作成を改めて要求させてはならない。

## 10. Relation／Precedence

本Ruleは次を補足・具体化する。

- `poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md` §7 Review Budget。
- `codex_controller_cross_task_cross_provider_instruction_package_operating_rule_ja.md`。
- Provider別Internal Review／Rework Contract。

矛盾時は、Userの最新明示Decision、PoC／MVP停止線、Resource Gate、本Ruleの順に適用する。
二段階Reviewは品質を口実にUser目的とDelivery Timingを無視するAuthorityをControllerへ与えない。
