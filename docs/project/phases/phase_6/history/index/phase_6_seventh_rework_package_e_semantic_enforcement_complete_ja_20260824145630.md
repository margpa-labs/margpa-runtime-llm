# Phase 6 Seventh Rework Package E Semantic Enforcement Complete Recovery

Timestamp: 2026-08-24 14:56:30 JST
Role: 設計者兼実装者役
State: PACKAGE_E_COMPLETE / PACKAGE_F_READY
Authority: `phase_6_codex_controller_seventh_rework_package_d_resume_authority_ja_20260824143226.md`

## 1. Current Boundary

Package A〜Dは再実行していない。Package D Current PartialからのResume Cycleを継続し、
Package EのJudge／Repair／Semantic ENFORCEを完了した。Phase 6 Closure／Phase 7／Roadmap／
Git／Networkへは進んでいない。

## 2. Implemented Contract

- Judge／Repair／Recording ModeをTurn開始時の単一SnapshotでFreezeし、途中のMode変更を
  Current Attemptへ混入させない。
- OFFはJudge Hook Action 0。OBSERVEはRaw Candidateを変更せずBackground Judge Evidenceのみを残す。
- ENFORCEはRaw CandidateのFinal DeltaをHoldbackし、Model Access Coordinator管理下でJudgeを待つ。
  `completed` / Persistent Canonical Turnへは次のいずれかだけを渡す。
  1. Completed ACCEPTのOriginal Candidate。
  2. 最大1回のRepair Generation＋RejudgeでIMPROVEDと確認されたRepair Candidate。
  3. Judge Failure／UNKNOWN／Budget Exhaustion／Repair Reject／Unavailable時のSafe User-facing Fallback。
- Known Failed CandidateはENFORCEのPresented Finalへ通さない。内部Exception名はChat回答へ出さない。
- Current User Correction、Prior User／Assistant Dialogue、RAG Reference BlockのPath／Heading／Contentを
  Judge Promptへ分離して渡し、同じContextをRepair Prompt／Rejudgeへ再利用する。
- ReferenceがないことだけでUNKNOWNにせず、User Correction矛盾／Premise Drift／Unsupported
  Definitive Assertion／Citation Evidence矛盾を`needs_repair`対象とした。
- Qwen／DeepSeekのThinking Prefix／Markdown Fence／短い前後説明に包まれる単一JSON Objectを
  Decode可能にした。複数Object、Unexpected Field、Enum／Confidence Schema違反、Malformedは
  `malformed_output` / UNKNOWN / FAILEDのままFail-closedとし、PASSを推測しない。
- Evaluation OrchestratorにOFF／OBSERVE／ENFORCEのTyped Dispositionを追加し、Failed／UNKNOWNを
  Candidate Presentableへ変換しない。
- Feature Modes API／UIへ`presentation_outcome`と`candidate_withheld`を追加し、Judge Failureと
  Presented Finalの関係を表示可能にした。Current Capabilityを現在形で説明し、ARGD／DAGD
  109 Semantic RuleがDeferredである境界は引き続き分離表示する。

## 3. Acceptance Mapping

- `P6-RW7-JDG-001`: Package CのCurrent Model Key／`main_self` Identityを維持。
- `P6-RW7-JDG-002`: Provider Wrapper付き単一Strict JSON PASS、Malformed／Ambiguous／Schema Extension
  Fail-closed Test PASS。
- `P6-RW7-JDG-003`: ReferenceなしUser Correction／Prior Dialogue／Unsupported Assertion Prompt Test PASS。
- `P6-RW7-JDG-004`: Citation EvidenceのJudge／Repair／Rejudge到達Test PASS。
- `P6-RW7-JDG-005`: Failed State／Failure Reason／Repair Acceptance非捜造／UI Projection Test PASS。
- `P6-RW7-JDG-006`: ENFORCE Raw Delta Holdback／Accepted Repair／Safe Fallback／Canonical Content Test PASS。
- `P6-RW7-JDG-007`: OFF Hook 0 Action／OBSERVE Candidate Unchanged／ENFORCE Disposition Test PASS。
- `P6-RW7-JDG-008`: `max_attempts=1`、Candidate＋Rejudgeの`max_total_model_calls=2`、Post-call Budget、
  Terminal Result／Safe Fallback Test PASS。

## 4. Exact Validation

- Backend focused: `169 passed`.
  - `tests/unit/evaluation`
  - `tests/unit/repair`
  - `tests/unit/bootstrap/test_judge_live_integration.py`
  - `tests/unit/bootstrap/test_repair_live_integration.py`
  - `tests/unit/conversation/test_conversation_generation_judge_hook.py`
  - `tests/unit/conversation/test_conversation_generation_runtime_snapshot.py`
  - `tests/integration/web/test_feature_modes_routes.py`
- Target Mypy: `Success: no issues found in 12 source files`.
- Target Ruff Check／Format: PASS.
- Frontend Typecheck: PASS.
- Frontend Lint: PASS.
- Frontend Full Test: `24 files / 220 tests passed`.

## 5. Mutation / Incident Boundary

- Product Source／Test／Frontendと本Append-only Recovery Entry以外のMutation: 0。
- Model Artifact Mutation: 0。Model Load／Inference: 0（Package FへDeferred）。
- Provider Memory Access: 0。User `runtime_data` Access: 0。Git／Network Action: 0。
- Resume CycleでのProject Root外Action: 0。
- Cumulative Root-outside Attempt: 1。`P6-RW7-INC-001`をHistorical Nonconformanceのまま維持し、
  `P6-RW7-REG-004` PASSへの捜造は行っていない。

## 6. Resume Point

Package Fから継続する。QwenのEvidence／Correction矛盾がJudge→Repair／Safe Finalで止まる
Golden Pathと、DeepSeekの病的反復をChat Template／EOS／Stop／Sampling／Raw Tokenに分解して
実Model確認する。Model Artifact自体は変更しない。Package F完了後は停止せずPackage Gへ
連結する。
