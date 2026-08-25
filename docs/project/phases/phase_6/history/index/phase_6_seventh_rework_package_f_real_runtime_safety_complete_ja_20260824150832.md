# Phase 6 Seventh Rework Package F Real Runtime Safety Complete Recovery

Timestamp: 2026-08-24 15:08:32 JST
Role: 設計者兼実装者役
State: PACKAGE_F_COMPLETE_WITH_EXACT_USER_MODEL_GATE / PACKAGE_G_READY
Authority: `phase_6_codex_controller_seventh_rework_package_d_resume_authority_ja_20260824143226.md`

## 1. Current Boundary

Package A〜Eは再実行していない。Package FではCurrent Local Qwen／DeepSeek Artifactの
Read-only Metadata照合、Real Load Attempt、DeepSeekのChat Template／EOS境界、および病的反復の
Safe Unavailable収束を実装・検証した。Model Artifact自体のMutationは0。Phase 6 Closure／
Phase 7／Roadmap／Git／Networkへは進んでいない。

## 2. Read-only Artifact Findings

`llama_cpp.Llama(..., vocab_only=True)`で実ArtifactのMetadataだけをRead-only確認した。

- Qwen `main.qwen3-4b-q4-k-m`
  - Architecture: `qwen3`
  - Native Context Metadata: `40960`
  - EOS Token ID: `151645`
  - Canonical EOS: `<|im_end|>`
  - Embedded Template: 4100 UTF-8 bytes
  - `enable_thinking`: present（Hard Switch）
- DeepSeek `main.deepseek-r1-0528-qwen3-8b-q4-k-m`
  - Architecture: `qwen3`
  - Native Context Metadata: `131072`
  - EOS Token ID: `151645`
  - Canonical EOS: `<｜end of sentence｜>`
  - Embedded Template: 2937 characters／3127 UTF-8 bytes
  - `enable_thinking`: absent（Soft Switch）
  - Embedded Template内のLiteralは`<｜end▁of▁sentence｜>`であり、Canonical EOSと
    byte-identicalではない。

Qwen Definitionの`native_context_limit`は実Artifact Metadataに合わせ`40960`へ訂正した。
Deployment Effective Maximumは引き続きProfile／Backend／Hardware Ceilingと分離され、
Current Profileの`8192`を自動的に拡張しない。Original HandoffのQwen `32768`という
記述はHistorical Inputとして残し、実Artifactの後発EvidenceでAppend-only訂正する。

## 3. Implemented Safety Contract

- llama.cppのNon-stream／Stream両経路に、最大8192 normalized charactersだけを扱う
  suffix-onlyの病的反復Detectorを追加した。
- 32〜512 charactersのExact Blockが最低192 characters連続する場合だけ検出し、
  短い強調／通常の箇条書き／短い繰り返しは検出しない。
- 検出時は生成を有界停止し、`GENERATION_FAILED` / retryable /
  `pathological_repetition_detected`を返す。生の反復ContentをCanonical Completionとして
  成功扱いしない。
- Current Load InstanceのLifecycleを`FAILED`へ降格し、Terminal Cleanupで`LOADED`へ戻さない。
  同一の不安定Loadは後続Requestを処理できず、既存のControlled Unload／Switch／
  Rollback境界でのみ回復する。
- DeepSeekのRendered Promptでだけ不一致Literal EOSをCanonical Tokenizer Bytesへ正規化し、
  Qwenの`<|im_end|>`はbyte-identicalのまま不変であることをUnit Testで固定した。
- Qwen実Model用に、User Correction／Official Evidenceと矛盾するKnown-wrong Candidateを
  `main_self` Judge ENFORCEに通し、Repair OFFでSafe Finalへ収束させるopt-in Golden
  Path Testを追加した。Real Modelが誤ってACCEPTした場合はTest Failureとし、PASSを
  捨て上げない。

## 4. Real Runtime Evidence and Exact Limit

Current Codex Task内で次を実行した。

1. Existing DeepSeek Multi-turn Model Smoke（Metal Profile）。
2. Qwenの明示CPU Load（`gpu_layers=0`, context `2048`, batch `64`）。

どちらもQwen Artifactの`Failed to create llama_context`でLoadが成立せず、Generation前に
終了した。これはCurrent Codex Task実行環境のEvidenceであり、Userの通常Terminal、
User Mac全体、Metal全般、またはModel Artifact品質のFailureへ一般化しない。

そのため、次の3 Real Model Testは定義／Collectionまで確認し、実Inference PASSは
Userの通常Terminal Gateへ正確に残す。

- `test_a_real_qwen_run_judges_its_own_answer_end_to_end`
- `test_real_qwen_enforce_withholds_an_evidence_contradicting_candidate`
- `test_deepseek_multiturn_chat_template_compatibility`

## 5. Exact Focused Validation

- Repetition／llama.cpp Boundary: `25 passed`.
- Target Mypy: `Success: no issues found in 5 source files`.
- Target Ruff Check／Format: PASS.
- Real Model Smoke Collection: `3 tests collected`.

Package GのCanonical Full Validationは次のMaterial Boundaryで実行する。

## 6. Acceptance Mapping

- `P6-RW7-MDL-002`: Qwen Native `40960`／DeepSeek Native `131072`を実Artifact Metadataから
  再導出。Effective MaximumはNativeと分離。
- `P6-RW7-MDL-005`: 病的反復の完全正常化はCurrent Task内Real Inference不成立のため
  主張しない。代替Contractの「有界停止＋Safe Unavailable」はSource／TestでPASS。
- `P6-RW7-JDG-003/004/006`: Deterministic Backend契約はPackage EでPASS。Real Qwen Golden
  PathはExact User Terminal Gate。
- `P6-RW7-REG-001`: Conversation／Citation／Branch／二Tab／RestartのReal Browser／Model回帰は
  Package GでUser Gate ListとしてExact化する。Deterministic RegressionはCanonical Suiteで再検証する。

## 7. Mutation / Incident Boundary

- Model Artifact Mutation: 0。Read-only Metadata／Load Attemptのみ。
- Provider Memory Access: 0。User `runtime_data` Access: 0。Git／Network Action: 0。
- Current Resume CycleでのProject Root外Action: 0。
- Cumulative Root-outside Attempt: 1。`P6-RW7-INC-001`はHistorical Nonconformanceのまま維持し、
  `P6-RW7-REG-004` PASSへの捨造は行っていない。

## 8. Resume Point

Package Gから継続する。Acceptance IDを1件ずつ再導出し、Backend Full／Canonical
Mypy／Ruff Format／Check／Frontend Typecheck／Lint／Test／Buildを実行する。Real Model／
BrowserのCurrent Task非実施項目はExact User Gate Listへ分離する。Open Technical Critical／
Major 0であればCOMPLETE_CANDIDATEを作成し、Controller Independent Reviewへ直接返送する。
