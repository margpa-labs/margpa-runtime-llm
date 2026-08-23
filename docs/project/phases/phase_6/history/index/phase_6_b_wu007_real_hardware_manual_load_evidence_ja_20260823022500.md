# Phase 6-B-WU-007 Real Hardware Manual Load Evidence（初の実Model検証）

```yaml
document_id: phase_6_b_wu007_real_hardware_manual_load_evidence
status: current_recovery_entry
phase: phase_6
subphase: phase_6_b
work_unit: p6_b_wu007_manual_load_evidence_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 02:25:00 JST
```

## 概要

本Sessionを通じて全てFake Fixtureのみで検証してきたRuntimeModelControllerを、
初めて実Qwen3-4B GGUF Artifact（Exact Model Authority Receipt記載のSHA-512
`f182f1d4...bfceb`と一致）に対して実行し、Manual Load Evidenceを確立した。

## Exact Mutation

```text
Created:
  tests/integration/test_runtime_model_control_smoke.py（@pytest.mark.model_smoke、
    既定Deselect、Apple Silicon限定）
```

## 実行結果（実Hardware、実Metal Backend）

```text
1. DirectoryModelDefinitionRegistryで実config/models/qwen3_4b_q4_k_m.tomlから
   ModelDefinitionを解決。
2. LlamaCppRuntimeModelBackend（実LlamaCppModelAdapter経由）でController.
   begin_switch()を実行し、Context Size 4096で実Load成功。
   → runtime_state=ACTIVE、artifact_digestがReceipt記載値と完全一致を実測確認。
3. Controller.request_context_change()でContext Size 4096→2048へ実Resize
   （Unload→Reload実サイクル）成功、runtime_state=ACTIVEを維持。
4. backend.unload()で正常終了。

実行時間: 5.23秒（2回の実Model Load／Unloadサイクルを含む）
```

## 意義

```text
これまでのFake-only Unit Test（30+件）が実装した抽象化（Port、Controller、
CAS、Switch Transaction）が実Hardwareの挙動と一致していることを直接実証した。
6-B-WU-002で「未実施：実Qwen GGUF Load経由のEnd-to-endテスト」としていた
Evidence Class Gapを解消。DeepSeek側は引き続きNOT EXECUTEDのままだが、
Qwen側のRuntime Model Control機構は実Hardware検証済みとなった。
```

## Validation

```text
New model_smoke Test : 1 passed（実Hardware、5.23秒）
既存model_smoke Suite : 3 passed／1 skipped（環境変数未設定、既存Non-scope）、
                        既存Qwen3 Smoke Test（別実装Path）も引き続きPASS、
                        回帰0を確認。
Default Suite（非model_smoke）: 1403 passed／4 deselected（新規model_smoke
                        Test 1件が正しくDeselectされることを確認、回帰0）
Ruff／Mypy            : Clean
```

## Next Exact Route

Phase 6-H（Comparative Experiment）へ進む。実Qwen Model Load機構が実証された
ため、実Generation経由の比較Experimentも現実的に着手可能になった。
