# Phase 8 観点変更型二段階Controller Review — 実測Evidence

```yaml
document_id: phase_8_changed_perspective_two_cycle_controller_review_empirical_evidence_20260831070840
document_type: append_only_automation_empirical_evidence
document_state: recorded
language: ja
created_at: 2026-08-31 07:08:40 JST
scope: phase_8_controller_independent_review_cycles
providers_under_review: [Claude, Copilot]
review_owner: Codex_project_controller
generalization_grade: repeated_phase_8_observation_not_universal_proof
```

## 1. 目的

Phase 8で、同じ実装Candidateへ観点を変えたController Reviewを二段階で適用した結果を記録する。
本Evidenceの焦点は「Review回数」ではなく、2回目が1回目と異なる仮説、Source Order、Negative ProbeおよびClaim監査を使うことで、
追加Findingを実際に検出できたかである。

## 2. 観測したReview構造

```text
Cycle 1 — Targeted／Implementation-relative Review
  Executorが申告した変更点
  Changed Paths
  Focused Tests
  直接的なRuntime経路
  Findingごとの解消条件

Cycle 2 — Assumption-reset／Requirement-relative Review
  Frozen Requirements／Exact Handoff／Acceptanceから再導出
  Production Composition／Persistence／UI／Observability
  Claimと実Evidenceの境界
  Contractを反転したNegative Probe
  Cycle 1のPASSを前提にしない
```

同じTestを二度実行するだけでは、ここでいう二段階Reviewに数えない。

## 3. 実測1 — Phase 8初回Candidate群

Phase 8実装側はInternal ReviewとCanonical Verificationを実施してComplete Candidateを返した。Codex Controllerの初回Review／Targeted Re-reviewでは、
少なくとも次を検出した。

```text
P8-CODEX-001  Concurrent advanceによる同一Tool二重実行
P8-CODEX-002  AuthorizationEnvelopeが実行経路へ未配線
P8-CODEX-003  Acceptance集計とUser Manual Gateの不整合
P8-CODEX-004  Approval EvidenceのRun Identity検証欠落
```

その後、解消済みClaimを前提にしないゼロベースReviewへ観点を変更した結果、次を追加検出した。

```text
Major／P0:
  P8-CODEX-005  Redirect後Source Authorityの虚偽分類
  P8-CODEX-006  Budget未実装をMax Stepで代替したPASS Claim
  P8-CODEX-007  Completion等のImportant Gate未配線
  P8-CODEX-008  Constitution 3 ModeのProduction比較経路欠落

Non-blocking:
  P8-CODEX-009  Completion TransitionとManualの不一致
  P8-CODEX-010  Manual URL Conversation Testの実DNS依存
```

追加Findingは、既存Testの単純な再実行ではなく、Authority Classification、Requirement Traceability、Mode Composition、
実User FlowおよびAcceptance Claimを別々に再導出したことで見つかった。

## 4. 実測2 — P8-RW6後の二段階Targeted Re-review

P8-RW6はP8-CODEX-005〜008を解消したとReturnした。

Cycle 1では、4件の中心Runtime経路を申告内容に沿って確認し、次を成立と判断した。

- Redirect後Canonical HostからSource Authorityを再計算する。
- Requested／Canonical URLを別Fieldで保持する。
- Deterministic BudgetがMax Stepと独立して実行前に作用する。
- Completion GateとTyped Completion Approval Evidenceが動作する。
- Constitution Preview API／UIが存在し、Production Active ModeをOFFに維持する。

このCycleだけなら、P8-RW6はUser Manual Candidateへ進める結論だった。

Cycle 2では、実装した修正点から離れ、Frozen Contract、実Manifest、Frontend表示およびAcceptance Claimを再導出した。その結果、
Cycle 1で検出しなかった次の2件を追加検出した。

```text
P8-CODEX-011  Non-blocking
  Completion Gateは動くが、Frozen AuthorizationEnvelope.gate_reasonsは空になり得る。

P8-CODEX-012  Major／P0 Closure Blocker
  Constitution PreviewはDecision Outcomeしか表示せず、Exact Handoff指定の
  Action Permission／Violation Presentation比較を実装していない。
```

Codex実Probeでは、Completion待機状態とEnvelope表示の不一致を次の通り再現した。

```text
envelope_gate_reasons = []
runtime_state         = awaiting_completion_approval
```

Current Constitution Manifestでは、OBSERVE／ENFORCEの全Ruleが`unsupported_action`へ収束した。これは未対応Ruleを
虚偽に`observed／enforced`と表示しない点では正しい。しかしFrontendはMode名とOutcomeだけを表示し、Action Permissionまたは
Violation Presentationを持たないため、Exact Handoff全体は未成立だった。

## 5. 追加検出の意味

二段階Reviewで有効だったのは、精査量を単純に二倍へ増やしたことではない。次を分離したことである。

```text
Cycle 1:
  「申告された修正は動くか」

Cycle 2:
  「その修正だけで上位要件、Composition、UI ClaimおよびAcceptanceが本当に成立するか」
```

Executorは、指示された修正をTest付きで実装できても、自分が選んだSolution Boundaryを前提として自己Reviewしやすい。
ControllerもTargeted Reviewだけでは同じBoundaryへ追随し得る。Cycle 2でSource Orderと仮説を変えることにより、
「コードは動くがClaimが実装より広い」問題を検出できた。

## 6. 限界

- Phase 8はAuthority、Persistence、UI、Runtime Compositionが交差するため、二段階Reviewの便益が大きく出やすい。
- 今回の結果だけで、全変更に必ず二回のFull Reviewが必要とは証明しない。
- Review回数を増やすだけではMoving Goalpost、Enterprise Hardening混入およびResource浪費を招く。
- Provider Internal Reviewは有用だが、同じ実装前提を共有するためController Independent ReviewのCycleへは数えない。
- Cycle 2で見つけたP1以下を全て即Reworkすると、Phase 6で発生した過剰Hardeningを再現する。

## 7. 実測から得た運用判断

```text
Material Change Default:
  Targeted Review
  -> Assumption-reset Review
  -> P0だけBounded Rework
  -> Final Targeted Verification
  -> User Manual

Trivial／Low-risk Change:
  Proportional Single Reviewを許容
```

二段階Review後に新しいP1以下が見つかっても、Stable未解決Registryへ送り、原則として追加Full Review Loopを開始しない。
人間の金銭、週間利用可能量、5時間制限、睡眠、作業時間および画面張り付きCostをReview Budgetへ含める。

## 8. Evidence参照

- `docs/project/phases/phase_8/history/operations/phase_8_codex_controller_zero_based_second_full_re_review_ja_20260831004652.md`
- `docs/project/phases/phase_8/history/operations/phase_8_codex_controller_rw6_two_cycle_targeted_re_review_ja_20260831065406.md`
- `docs/project/shared/history/automation/claude_current_task_r17_to_r20_internal_review_rework_empirical_result_ja_20260829062910.md`
- `docs/project/shared/history/automation/claude_current_task_r21_to_r24_internal_review_empirical_result_ja_20260829101215.md`
- `docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`
