# Phase 9-1 — Component完全疎結合 R3 Return Controller独立Review

```yaml
document_type: controller_independent_review
document_state: changes_required
recorded_at: 2026-09-05 19:50:51 JST
language: ja
reviewer_role: codex_controller
review_target: ../../handoffs/phase_9_claude_component_independence_r3_residual_rework_exact_return_ja_20260905193256.md
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_R3_CHANGES_REQUIRED
phase_9_1_closure: false
real_model_action: none
git_mutation: none
append_only: true
```

## 1. 判定

`CHANGES REQUIRED / Phase 9-1 INCOMPLETE`。

R3には有効な修正がある。しかし、Turn Snapshotの単一スロット、Cancellation Terminal Arbitration、三経路Identity Test、実GemmaのDeviation出力に残差がある。User実画面再確認やPhase 9-1 Closureへは進まない。

## 2. 受理する進展

- Conversationが解決済みのJudge／Repair ModeをSemantic Freezeへ渡し、同一Turn内の二重Live読取を減らした。
- Provider切替時のIdentity MismatchをModel Call 0のTyped Failureへ収束させた。
- Built-in EvidenceへMain Artifactを誤帰属させる実装を修正した。
- Main-priority PreemptionでWorker自身が確定したCancellation Reasonを保持する、指摘済みScheduleの回帰Testは成立した。
- Gemmaの通常All-Accept 32 Criterionは、同一条件2 Trialで全Batch Decode・32件評価が成立した。
- `build_phase1_web_runtime()`経由の32 Criterion Fixtureは、Main Governance起点Repair、同一32件Rejudge、同一Turn保存のProduction配線を検証するEvidenceとして受理する。

Controller Focused Verificationは131 passed。実Modelは再実行していない。

## 3. IR-R3-01 — Turn Snapshotはまだrequest-localではない

`JudgeSemanticTurnProvider`は失敗状態を`_begin_attempted_request_id`／`_begin_failed`の一枠だけで保持し、`SemanticRuntimeCoordinator`も`_current`一枠だけを保持する。別requestが入ると、先行requestの「Freeze失敗済み」も「Freeze成功済みSnapshot」も失われる。

Controller Probeは次を再現した。

```text
Aの開始Freeze失敗 → B成功 → Aを再読
context provider calls = 3
late A result          = request-A

A成功(generation 1) → B成功(generation 2) → Aを再読
late A generation     = 3
A digest changed      = true

A成功 → B成功 → AのResponseを記録
A record/evidence     = false / false
```

したがって「同一requestは後から再Freezeしない」「Main／Judgeが同一Turn Resultを共有する」「遅延Background結果をrequestへ相関保存する」は一般形で未成立である。`_current`はUIのLatest Pointerとして残してよいが、実Turn Snapshot／Freeze Failureはrequest-localに保持する必要がある。

## 4. IR-R3-02 — 三経路IdentityのTest完結は未成立

Built-in実装修正自体は妥当だが、新規Built-in TestはSemantic Snapshotを供給せず、`configured_judge_provider`／`active_judge_provider`をAssertしていない。Main-shared／Dedicatedを含め、Handoffが要求した次の保存JSON三経路Matrixを一つの明示的なTest契約として完結していない。

```text
Evaluated Main
Configured Judge
Active Judge
Executed Judge
Executed Artifact / Backend / Version
```

既存Testの組合せで暗黙に推定せず、各経路で上記を直接Assertする。

## 5. IR-R3-03 — 通常FailureがCancellationを上書きできる

ENFORCE Wait Loopは、Cancellation検知時にWorker Resultが`cancelled`だけでなく`failed`でも、そのFailureをそのまま採用する。これは直前の「Cancellation has deterministic priority」という契約と矛盾する。

Malformed／Unavailable／Timeout以外の通常FailureがResult Readyになった直後にUser StopまたはMain-priorityが成立すると、現在実装はCancellationではなく先行Failureを表示できる。保持対象は、Worker自身が既に確定した`cancelled`とその起源であり、任意の`failed`ではない。

## 6. IR-R3-04 — Gemma原因ClaimとSchema境界

実機一回から確定した事実は「Deviationを含むProduction形状でMalformedになった」までである。失敗BatchのRaw構造を採取していないため、`evidence_refs`／`reason_code`の非空内容が直接原因という記述は有力仮説だが一意確定ではない。

ただしDecoder契約上、Criterionの必須Fieldは`criterion_id`／`disposition`／`confidence`であり、`reason_code`／`evidence_refs`は省略可能である。Gemma専用Schemaからこの二つを外すProvider局所Compact Contractは、Decoder緩和なしで試せる最小修正である。共有Selene Schema、Main-shared、Decoderへ波及させない。

## 7. IR-R3-05 — 32件FixtureのContextは配線Evidence限定

Fixtureは`dedicated_role_load.context_size=32768`を設定し、実配置のGemma 8192と一致しない。Production Composition配線のEvidenceとしては受理するが、Context／Budget境界のProduction parityはClaimできない。実設定8192、またはRegistry／Profile由来値で同じFixtureを成立させる。

## 8. Disposition

[R4収束Rework Exact Handoff](../../handoffs/phase_9_controller_component_independence_r4_convergence_rework_exact_handoff_ja_20260905195051.md)のみを次に実行する。Selene、Phase 9-2／9-3、Phase 10、Git操作へは進まない。
