# Phase 7 P7-RW4 NO_HIT Stale Code防止 — Codex Controller Independent Review

```yaml
document_id: phase_7_codex_controller_p7_rw4_no_hit_stale_code_prevention_independent_review_20260830152558
document_type: controller_independent_review
document_state: final
language: ja
created_at: 2026-08-30 15:25:58 JST
reviewer_provider: Codex
reviewer_role: プロジェクト責任者兼設計統括者役
phase: phase_7
review_scope: P7-RW4
disposition: PASS_WITH_USER_MANUAL_GATE
phase_7_closure_authority: false
phase_8_authority: false
git_authority: false
```

## 1. Review対象

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_stale_code_prevention_bounded_rework_exact_return_handoff_ja_20260830143000.md
SHA-512:
30c271507e81fcf2d8ad33a2cebeaefcb41d8baf15b00d2716c357e753f3c75bf4c53dab05e5c74bcf98405139a28f341ba8ba418d5d3cde8de00cae11a7c9b4
```

実File DigestはReturn記載値と一致した。

## 2. Controller Source Review

P7-RW4は、P7-RW3でGrounded Turnだけに適用されていたOutput Consistency Boundaryを、RAG ONかつCurrent Grounding Stateが`NO_HIT`のTurnへ拡張した。

```text
GROUNDED_READY : Current Evidence外のCode-shaped Identifierを拒否
NO_HIT         : Evidence 0のため、Candidate内Code-shaped Identifierを拒否
RAG OFF        : Boundary対象外
```

NO_HIT TurnはCandidate検査前にBufferされる。`CEDAR-9847`をStreamingした後で撤回する経路ではなく、検査後の固定Safe Grounding Failureだけを提示する。

新しいTitle-Case Run Heuristic、Project固有Allowlist、`Nazuna Probe Orion` Hard-codeまたは意味解析基盤は追加されていない。

## 3. Exact Regression Review

新規Integration Testは、ControllerがP7-RW3で指摘した不足を直接修正している。

```text
1. Current Local DocumentへCEDAR-25123を登録。
2. Historical Assistant TurnへCEDAR-9847を保持。
3. Local Documentを削除。
4. Scripted Inferenceが意図的にCEDAR-9847を返す。
5. 同一ChatのFinal／DeltaへCEDAR-9847を出さない。
6. 同一ChatのCitationは0。
7. 新規ChatでもCEDAR-9847を意図的に返させ、非提示とCitation 0を確認。
8. Historical Turn不変。
9. RAG OFFではCEDAR-9847とStreamingを従来どおり維持。
```

安全な回答を最初からScriptしてPASSへ見せる旧Test不足は解消された。

## 4. Independent Focused Verification

ControllerはProject内Task-owned Tempを使い、次を再実行した。

```text
tests/unit/conversation/test_conversation_generation.py
tests/integration/documentation_rag/test_local_corpus_end_to_end.py

Result: 54 passed
```

Claude Canonical Evidenceは次のとおり。

```text
Backend: 1944 passed / 7 deselected
Mypy: 526 source files / 0 issues
Ruff Check／Format: PASS
Frontend Source Mutation: 0
Network Action: 0
```

Controller Review CycleのNetwork／Git／User `runtime_data/`／Provider Memory／Model Artifact Actionは0。

## 5. Finding判定

```text
P7-CODEX-011 Citation UI                  : TECHNICALLY RESOLVED / USER BROWSER GATE
P7-CODEX-012 Current Evidence Precedence  : TECHNICALLY RESOLVED / USER REAL MODEL GATE
P7-CODEX-013 Delete NO_HIT Stale Code     : TECHNICALLY RESOLVED / USER REAL MODEL GATE
Auto-Resume                               : USER MAC PASS PRESERVED
P7-RW4 Open Critical／Major／MVP Blocker   : 0 known
```

Code-shaped Identifierを含まない一般的な古い事実文まで完全に意味判定する機能は本Bounded Scope外であり、将来のJudge／Semantic Governance／RAG品質改善へ残す。今回のExact Failureである`CEDAR-9847`型Code再利用は閉じている。

## 6. Controller結論

```text
P7-RW4 Technical Disposition : PASS
Phase 7 State                : READY_FOR_FINAL_USER_MANUAL_RECHECK
Phase 7 Closure              : NOT YET CLAIMED
```

User実画面では次だけを再確認する。

1. Citation UIのField順、3 Copy Button、短縮値とFull Copy値の対応。
2. Local Document登録後、Current値を回答する。
3. 更新後、同じChatの新Turnで最新値またはSafe Grounding Failureへ収束する。
4. 削除後、同じChat／新規Chatとも旧Codeを表示せず、Citation 0または根拠なし表示へ収束する。

全項目PASS後にPhase 7 Closure判定へ進む。
