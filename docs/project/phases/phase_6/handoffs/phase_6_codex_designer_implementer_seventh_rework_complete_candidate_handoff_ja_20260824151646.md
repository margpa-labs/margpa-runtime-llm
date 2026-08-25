# Phase 6 Seventh Rework 設計者兼実装者役 Complete Candidate Handoff

```text
From: 設計者兼実装者役
To: プロジェクト責任者兼設計統括者役
Status: COMPLETE_CANDIDATE
Completed Packages: A, B, C, D, E, F, G
Exact Next Action: Controller Independent Review
Phase 6 Closure: NOT EXECUTED
Phase 7 / Roadmap / Git / Network: NOT EXECUTED
```

Timestamp: 2026-08-24 15:16:46 JST
Authority: `phase_6_codex_controller_seventh_rework_package_d_resume_authority_ja_20260824143226.md`
Completion Recovery:
`docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_g_integrated_verification_complete_ja_20260824151646.md`

## 1. Result

Seventh Reworkは技術的Critical／Major 0でCOMPLETE_CANDIDATEに到達した。

- Mode SelectorはSeparate Apply 0、Click即時Mutation／Canonical Re-fetch／Sequence Guardへ統一。
- Sidebar／Advanced／Environment／`main_self` Judgeを単一Current Runtime Snapshotへ収束。
- Native／Backend／Deployment-Hardware Verified／Effective ContextとModel別Max New Tokensを分離。
- ENFORCEはRaw CandidateをHoldbackし、ACCEPT／Accepted Bounded Repair／Safe Fallbackだけを
  Canonical Presented Finalへ渡す。OBSERVEはRaw不変、OFFは追加Action 0。
- User Correction／Dialogue／Citation／RAG EvidenceをJudge／Repair／Rejudgeに同一Contextで渡す。
- Qwen／DeepSeekのWrapped Single JSONをStrict Decodeし、Ambiguous／Malformed／Schema逸脱は
  Fail-closed。
- DeepSeekのEOS LiteralをCanonical Tokenizer Bytesへ正規化し、病的反復は有界停止＋
  Typed Failure＋Current Load `FAILED`へ収束。
- Qwen実GGUF MetadataによりNative Contextを`40960`へAppend-only訂正。Effective Local
  MaximumはProfile `8192`のまま分離。

## 2. Changed Files

### Config

```text
config/models/qwen3_4b_q4_k_m.toml
config/models/deepseek_r1_0528_qwen3_8b_q4_k_m.toml
```

### Backend / Application Source

```text
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/repetition.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
src/margpa_runtime_llm/adapters/runtime_model_control/llama_cpp_backend.py
src/margpa_runtime_llm/bootstrap/judge_live_integration.py
src/margpa_runtime_llm/bootstrap/repair_live_integration.py
src/margpa_runtime_llm/bootstrap/runtime_model_control.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/modules/conversation/contracts.py
src/margpa_runtime_llm/modules/evaluation/application/evaluation_orchestrator.py
src/margpa_runtime_llm/modules/evaluation/application/judge_output_decoder.py
src/margpa_runtime_llm/modules/evaluation/application/judge_prompt_builder.py
src/margpa_runtime_llm/modules/runtime_model_control/application/runtime_model_controller.py
src/margpa_runtime_llm/modules/runtime_model_control/domain/errors.py
src/margpa_runtime_llm/modules/runtime_model_control/domain/snapshot.py
src/margpa_runtime_llm/modules/runtime_model_control/ports.py
src/margpa_runtime_llm/modules/runtime_observability/projection/component_identity_projection.py
src/margpa_runtime_llm/web/app.py
src/margpa_runtime_llm/web/feature_modes_routes.py
src/margpa_runtime_llm/web/runtime_model_control_routes.py
```

### Frontend Source / Built Static

```text
frontend/index.html
frontend/src/App.tsx
frontend/src/api/client.ts
frontend/src/components/ConfigurationControlPanel.tsx
frontend/src/components/FeatureModesPanel.tsx
frontend/src/components/GovernancePanel.tsx
frontend/src/components/GuardrailGovernancePanel.tsx
frontend/src/components/RuntimeGovernancePanel.tsx
frontend/src/components/RuntimeModelStatusPanel.tsx
frontend/src/components/SettingsModal/SettingsModal.tsx
frontend/src/components/SettingsPanel.tsx
frontend/src/i18n/translations.ts
frontend/src/lib/runtimeModelControlBootstrap.ts
frontend/src/types.ts
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.css
src/margpa_runtime_llm/web/static/app.js
```

### Tests

```text
frontend/src/App.test.tsx
frontend/src/components/ConfigurationControlPanel.test.tsx
frontend/src/components/FeatureModesPanel.test.tsx
frontend/src/components/GovernancePanel.test.tsx
frontend/src/components/GuardrailGovernancePanel.test.tsx
frontend/src/components/RuntimeGovernancePanel.test.tsx
frontend/src/components/RuntimeModelStatusPanel.test.tsx
frontend/src/components/SettingsModal/SettingsModal.test.tsx
frontend/src/lib/runtimeModelControlBootstrap.test.ts
tests/integration/test_real_local_judge_smoke.py
tests/integration/test_runtime_model_control_smoke.py
tests/integration/web/test_feature_modes_routes.py
tests/integration/web/test_runtime_model_control_mutation_routes.py
tests/integration/web/test_runtime_model_control_public_basic_call0.py
tests/unit/bootstrap/test_judge_live_integration.py
tests/unit/bootstrap/test_repair_live_integration.py
tests/unit/bootstrap/test_runtime_model_control_bootstrap.py
tests/unit/conversation/test_conversation_generation.py
tests/unit/conversation/test_conversation_generation_judge_hook.py
tests/unit/conversation/test_conversation_generation_runtime_snapshot.py
tests/unit/evaluation/test_evaluation_orchestrator.py
tests/unit/evaluation/test_judge_prompt_and_decoder.py
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_llama_cpp_boundary.py
tests/unit/inference/test_pathological_repetition.py
tests/unit/runtime_model_control/test_dynamic_context_and_tokens.py
tests/unit/runtime_model_control/test_llama_cpp_backend.py
tests/unit/runtime_model_control/test_runtime_model_controller.py
tests/unit/runtime_observability/test_component_identity_projection.py
```

Deleted Files: 0。Existing Test削除／Assertion弱体化／Mypy除外: 0。

### Append-only Recovery / Return

```text
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_a_start_ja_20260824135445.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_a_as_built_reproduction_ja_20260824135806.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_b_ui_immediate_mode_apply_ja_20260824140751.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_c_current_runtime_identity_projection_ja_20260824141853.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_d_root_outside_npm_log_attempt_stopped_safe_ja_20260824143020.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_d_capability_contract_complete_ja_20260824143627.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_e_semantic_enforcement_complete_ja_20260824145630.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_f_real_runtime_safety_complete_ja_20260824150832.md
docs/project/phases/phase_6/history/index/phase_6_seventh_rework_package_g_integrated_verification_complete_ja_20260824151646.md
docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_seventh_rework_stopped_safe_return_ja_20260824143020.md
docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_seventh_rework_complete_candidate_handoff_ja_20260824151646.md
```

## 3. Acceptance ID Disposition

```text
P6-RW7-UI-001 : PASS_DETERMINISTIC
P6-RW7-UI-002 : PASS_DETERMINISTIC / USER_BROWSER_GATE
P6-RW7-UI-003 : PASS
P6-RW7-UI-004 : PASS
P6-RW7-UI-005 : PASS_DETERMINISTIC / USER_BROWSER_GATE
P6-RW7-UI-006 : PASS

P6-RW7-MDL-001 : PASS_DETERMINISTIC / USER_RESTART_GATE
P6-RW7-MDL-002 : PASS_DETERMINISTIC_AND_METADATA / USER_MODEL_GATE
P6-RW7-MDL-003 : PASS
P6-RW7-MDL-004 : PASS
P6-RW7-MDL-005 : PASS_SAFE_UNAVAILABLE / USER_MODEL_GATE

P6-RW7-JDG-001 : PASS
P6-RW7-JDG-002 : PASS_DETERMINISTIC / USER_MODEL_GATE
P6-RW7-JDG-003 : PASS_DETERMINISTIC / USER_MODEL_GATE
P6-RW7-JDG-004 : PASS_DETERMINISTIC / USER_MODEL_GATE
P6-RW7-JDG-005 : PASS
P6-RW7-JDG-006 : PASS
P6-RW7-JDG-007 : PASS
P6-RW7-JDG-008 : PASS

P6-RW7-REG-001 : PASS_DETERMINISTIC / USER_BROWSER_MODEL_GATE
P6-RW7-REG-002 : PASS
P6-RW7-REG-003 : PASS
P6-RW7-REG-004 : HISTORICAL_NONCONFORMANCE_RECORDED
```

Full ID根拠とExact User GateはCompletion Recovery §3〜5を参照。

## 4. Backend / Frontend Verification

```text
Backend Full       : 1589 passed, 7 deselected / Exit 0
Canonical Mypy     : 443 source files, 0 issues / Exit 0
Ruff Format Check  : 443 files already formatted / Exit 0
Ruff Check         : All checks passed / Exit 0
Frontend Typecheck : PASS / Exit 0
Frontend Lint      : PASS / Exit 0
Frontend Test      : 24 files, 220 tests passed / Exit 0
Frontend Build     : PASS, 48 modules transformed / Exit 0
```

## 5. Real Qwen / DeepSeek Evidence

```text
Read-only Metadata Inspection : PASS
Qwen Native Context           : 40960
Qwen EOS / Thinking           : <|im_end|> / hard switch
DeepSeek Native Context       : 131072
DeepSeek Canonical EOS        : <｜end of sentence｜>
DeepSeek Template EOS Literal : <｜end▁of▁sentence｜>
DeepSeek Thinking             : soft switch
Real Model Test Collection    : 3 tests collected
Codex Task Real Inference     : NOT PASS; Qwen load failed before generation
Failure                       : Failed to create llama_context
Generalization to User Mac    : PROHIBITED / NOT PERFORMED
```

Exact User Terminal Gate:

```text
.venv/bin/python -m pytest -q -s -m model_smoke \
  tests/integration/test_real_local_judge_smoke.py \
  tests/integration/llama_cpp/test_deepseek_multiturn.py \
  tests/integration/test_runtime_model_control_smoke.py
```

## 6. Open Critical / Major / Non-critical

```text
Open Technical Critical : 0
Open Technical Major    : 0
Open Non-critical       : Real Model User Gate; Real Browser/Two-tab/Restart User Gate;
                          disclosed DeepSeek Requantization Caveat;
                          P6-RW7-REG-004 Historical Nonconformance
```

## 7. Action Inventory

```text
Current Resume Cycle Project Root外Action : 0
Cumulative Root-outside Attempt             : 1 (P6-RW7-INC-001)
Provider Memory Internal Access             : 0
User runtime_data Access                    : 0
Git Action                                  : 0
Network Action                              : 0
Model Artifact Mutation                     : 0
Phase 6 Closure / Phase 7 / Roadmap          : 0
```

`P6-RW7-REG-004`はPASSではない。Historical Nonconformanceを削除／0 Claimへ書き換えて
いない。Current Resume CycleではAuthority指定のExact Frontend Workdir／Project内Cache／Tempを
使用し、新規Root外Actionは0。

## 8. User Manual Acceptance Remaining

1. 上記Real Model CommandのUser通常Terminal実行。
2. Real Browser 2 TabでMode順序／Conflict収束、Current Model同期、Conversation／Citation／
   Branch／Regenerate保持。
3. Qwen→DeepSeek→Qwen／Server Restart後Qwen Default。
4. ENFORCE Known Failed CandidateのFinal非通過、OBSERVE Raw不変、OFF Additional Action 0。
5. DeepSeek病的反復再発時の有界停止／Safe Unavailable。

## 9. Stop / Return

Controller Independent Reviewに返送後、本Taskは停止する。Phase 6 ClosureはController／User Gate後の
別Authorityであり、本HandoffはClosureを代行しない。
