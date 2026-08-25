# Phase 6 Seventh Rework Package G Integrated Verification Complete Recovery

Timestamp: 2026-08-24 15:16:46 JST
Role: 設計者兼実装者役
State: PACKAGE_G_COMPLETE / COMPLETE_CANDIDATE
Authority: `phase_6_codex_controller_seventh_rework_package_d_resume_authority_ja_20260824143226.md`

## 1. Completion Boundary

Package A〜Gを完了し、Seventh Reworkの技術的Critical／Majorは0と判定した。
Package A〜CおよびDの既完了範囲はやり直さず、Controller Resume Authorityに従って
D Current Partial→E→F→Gの差分Cycleを連結した。

Phase 6 Closure／Phase 7／Roadmap／Git／Network／Backup／Cleanupは実行していない。
Real Model／BrowserのUser Mac固有項目は、未実施をPASSに変換せずExact User Gateとして
分離した。

## 2. Integrated Verification

### 2.1 Backend Full

```text
Command : .venv/bin/python -m pytest tests/ -q -p no:cacheprovider --basetemp=<Project Task Temp>
Result  : 1589 passed, 7 deselected in 66.80s
Exit    : 0
```

`pyproject.toml` Canonical Markerの`not model_smoke`により、7 deselectedはopt-in Real Model Testである。

Initial Fullでは新Contractに対する旧Test期待3件を検出した。修正は次の最小Test範囲のみ。

1. `ConversationSettings` Global 2048 Ceilingの旧期待を、Frozen Runtime SnapshotがModel別
   Upper Limitを所有するCurrent Contractへ更新。
2. Documentation RAG予算前とAugmentation後のExact Remaining-context Enforcementで、
   1 Turnあたり2回Token CountするCurrent Contractへ更新。
3. Qwen実GGUF Native Context訂正`40960`により、Oversized Preload Testを`50000`へ更新。

Focused再検証は7 passed、最終Fullは上記のとおりRegression 0。

### 2.2 Canonical Static / Format

```text
Canonical Mypy : Success, 443 source files, 0 issues, Exit 0
Ruff Format    : 443 files already formatted, Exit 0
Ruff Check     : All checks passed, Exit 0
```

Canonical Mypyは引数なし`.venv/bin/python -m mypy`を使用し、`pyproject.toml`の
`files = ["src", "scripts", "tests"]`を全件対象とした。旧Constructor Argumentを保持していた
opt-in Runtime Model Smoke Test 1件を型契約に追随させた。Assertion弱体化／Any化／
Mypy除外は0。

Ruff Initial Format Checkで3件を検出し、Exact 3 FilesにMechanical Formatを適用した。
Format後のRuntime Model Controller／Web Focusedは25 passed。

### 2.3 Frontend

Authority指定のExact `<Root>/frontend` WorkdirとProject内Task-owned `NPM_CONFIG_CACHE`／
`TMPDIR`を使用した。

```text
Typecheck : PASS, Exit 0
Lint      : PASS, Exit 0
Test      : 24 files / 220 tests passed, Exit 0
Build     : PASS, 48 modules transformed, Exit 0
Static    : index.html 0.87 kB / app.css 18.94 kB / app.js 303.41 kB
```

BuildはAuthorized Sourceの`src/margpa_runtime_llm/web/static/`を更新した。

## 3. Exact Acceptance Disposition

| Acceptance ID | Disposition | Evidence / Remaining Gate |
|---|---|---|
| P6-RW7-UI-001 | PASS_DETERMINISTIC | Apply Button 0、Click単一Mutation、Frontend Interaction Test |
| P6-RW7-UI-002 | PASS_DETERMINISTIC / USER_BROWSER_GATE | Queue／Sequence Guard／Conflict Rollback PASS。実2 TabはUser Gate |
| P6-RW7-UI-003 | PASS | 重複Field 0、Layout／Keyboard Button Semantics PASS |
| P6-RW7-UI-004 | PASS | Research Mode Advanced最下部／Click即時Mutation PASS |
| P6-RW7-UI-005 | PASS_DETERMINISTIC / USER_BROWSER_GATE | 単一Runtime SnapshotからSidebar／Advanced／Environment収束。実2 TabはUser Gate |
| P6-RW7-UI-006 | PASS | Phase Suffix 0、Current Capability Copy、109 Semantic Rule Deferred境界維持 |
| P6-RW7-MDL-001 | PASS_DETERMINISTIC / USER_RESTART_GATE | Startup Default QwenとCurrent Loadedを分離。実Server RestartはUser Gate |
| P6-RW7-MDL-002 | PASS_DETERMINISTIC_AND_METADATA / USER_MODEL_GATE | Qwen Native 40960／DeepSeek 131072／Effective 8192分離。実Maximum LoadはUser Gate |
| P6-RW7-MDL-003 | PASS | Maximum／Maximum-1／Minimum／範囲外／Busy／CAS／RollbackをDeterministic Test |
| P6-RW7-MDL-004 | PASS | Default 2048／Model別Upper／Exact Remaining Context／Switch収束 PASS |
| P6-RW7-MDL-005 | PASS_SAFE_UNAVAILABLE / USER_MODEL_GATE | 有界反復検出→Typed Failure→Load FAILEDをTest。実DeepSeek再生成はUser Gate |
| P6-RW7-JDG-001 | PASS | Current Main Model Key／`main_self`／Dedicated Judge Unconfiguredを分離表示 |
| P6-RW7-JDG-002 | PASS_DETERMINISTIC / USER_MODEL_GATE | Wrapper付き単一Strict JSONはDecode、Ambiguous／Malformed／Schema逸脱はFail-closed。実Qwen／DeepSeekはUser Gate |
| P6-RW7-JDG-003 | PASS_DETERMINISTIC / USER_MODEL_GATE | User Correction／Premise Drift／Unsupported AssertionをPrompt／Routing Test。実Qwen Golden PathはUser Gate |
| P6-RW7-JDG-004 | PASS_DETERMINISTIC / USER_MODEL_GATE | Citation／RAG EvidenceのJudge／Repair／Rejudge到達Test。実Golden PathはUser Gate |
| P6-RW7-JDG-005 | PASS | Judge Failure State／Failure Reason／Repair非捨造／UI Projection PASS |
| P6-RW7-JDG-006 | PASS | ENFORCE Raw Final Holdback／Accepted Repair／Safe Fallback／Canonical Persistence PASS |
| P6-RW7-JDG-007 | PASS | OFF Additional Action 0／OBSERVE Raw Candidate Unchanged／ENFORCE Typed Disposition PASS |
| P6-RW7-JDG-008 | PASS | Repair 1 Attempt／Candidate+Rejudge最2 Model Calls／Budget／Terminal保証 PASS |
| P6-RW7-REG-001 | PASS_DETERMINISTIC / USER_BROWSER_MODEL_GATE | Conversation／Citation／Branch／Regenerate／Reload State Test PASS。実2 Tab／Switch／RestartはUser Gate |
| P6-RW7-REG-002 | PASS | Turn Recording／Judge EvidenceのMode Freeze／Correlation／Failure Injection PASS |
| P6-RW7-REG-003 | PASS | Backend Full／Canonical Mypy／Ruff／Frontend全PASS。Test削除／弱体化0 |
| P6-RW7-REG-004 | HISTORICAL_NONCONFORMANCE_RECORDED | Cumulative Root-outside Attempt 1を維持。Resume CycleはRoot外Action 0。0 Claimに捨造しない |

## 4. Real Model Evidence

Current Codex TaskでMetal Profileと明示CPU Qwen Loadを試行したが、両方とも
`Failed to create llama_context`でGeneration前に終了した。このTask環境Failureは
User Mac全体や通常Terminal Metal Failureへ一般化しない。

Read-only `vocab_only` Metadataは成立し、Qwen Native `40960`／EOS `<|im_end|>`／
Hard Thinking Switch、DeepSeek Native `131072`／Canonical EOS `<｜end of sentence｜>`／
Template Literal `<｜end▁of▁sentence｜>`／Soft Thinking Switchを確認した。

Real Model Smoke 3件はCollection PASS、Inference未PASSとしてExact User Gateへ残した。

## 5. Exact User Manual Acceptance Remaining

### Gate 1 — User通常Terminal Real Model

```text
.venv/bin/python -m pytest -q -s -m model_smoke \
  tests/integration/test_real_local_judge_smoke.py \
  tests/integration/llama_cpp/test_deepseek_multiturn.py \
  tests/integration/test_runtime_model_control_smoke.py
```

確認対象:

1. Qwen Real Judge Prompt／Decoder Round-trip。
2. User Correction／Official Evidenceと矛盾するKnown-wrong CandidateをENFORCEがFinalにせず、
   Safe Finalへ収束する。Real Judgeの誤ACCEPTはTest FailureでありPASSに変換しない。
3. DeepSeek Native Multi-turn／Qwen↔DeepSeek Cross-model History／Thinking ToggleでSpecial Token
   Leakage 0、Unrelated Follow-upのTopic正常化。
4. Runtime Model Controllerの実Qwen Load／Context Resize。
5. DeepSeek反復が再発する場合、無限出力ではなくTyped Failure／Safe Unavailableへ
   有界収束する。

### Gate 2 — User Mac Real Browser / Two Tabs

1. Startup Qwen Default、DeepSeek Switch、Qwen Rollback、Server Restart後Qwen Default。
2. Sidebar／Advanced／Environment／Current Judge Identityが同一Current ModelとRevisionへ収束。
3. Context／Max New TokensのMaximum／Maximum-1／範囲外／Conflict／Failure Rollback表示。
4. Research／Governance／Runtime Governance／Guardrail／Judge／Repair／Recordingの
   Click即時適用、Separate Apply 0、Rapid Click／2 Tab Conflict後のCanonical収束。
5. Conversation／Citation／Branch／RegenerateがModel Switch／Reload／2 Tab後も維持。
6. ENFORCEでKnown Failed Candidateが表示／Canonical Turnに残らず、Accepted Repairまたは
   Safe User-facing FallbackだけがPresented Finalとなる。
7. OBSERVEはRaw Candidateを変更せずEvidenceを表示し、OFFは追加Judge／Repair Action 0。

## 6. Open Findings

```text
Open Technical Critical : 0
Open Technical Major    : 0
Open Non-critical       :
  - Current Codex Taskのllama_context作成不成立によるReal Model User Gate
  - Real Browser／Two-tab／Restart目視User Gate
  - DeepSeek Q8_0→Q4_K_M Requantizationの既開示Quality Caveat
  - P6-RW7-REG-004 Historical Nonconformance
```

## 7. Mutation / Authority Inventory

```text
Current Resume Cycle Project Root外Action : 0
Cumulative Root-outside Attempt             : 1 (P6-RW7-INC-001)
Provider Memory Internal Access             : 0
User runtime_data Access                    : 0
Git Action                                  : 0
Network Action                              : 0
Model Artifact Mutation                     : 0
Model Read/Metadata/Load Attempt             : Authorized Scope内
Phase 6 Closure / Phase 7 / Roadmap          : 0
```

`P6-RW7-REG-004`は`HISTORICAL_NONCONFORMANCE_RECORDED`のままであり、Forbidden Action 0の
PASSに捨造していない。Provider Memory内部／Root外の追加Inspection／Cleanupは行っていない。

## 8. Exact Next Action

Direct Return Handoffを作成し、プロジェクト責任者兼設計統括者役のController Independent
Reviewへ返す。Phase 6 Closureへは進まない。
