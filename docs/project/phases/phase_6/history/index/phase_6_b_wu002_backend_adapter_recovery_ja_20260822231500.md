# Phase 6-B-WU-002 Backend Adapter／Model Definition Recovery Entry

```yaml
document_id: phase_6_b_wu002_backend_adapter_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_b
work_unit: p6_b_wu002_complete_qwen_only
role: Claude側設計統括者役
provider: claude_code
long_running_mode_active: true
created_at: 2026-08-22 23:15:00 JST
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/adapters/runtime_model_control/__init__.py
  src/margpa_runtime_llm/adapters/runtime_model_control/model_definition_registry.py
  src/margpa_runtime_llm/adapters/runtime_model_control/generation_busy_gate.py
  src/margpa_runtime_llm/adapters/runtime_model_control/llama_cpp_backend.py
  tests/unit/runtime_model_control/test_model_definition_registry.py
  tests/unit/runtime_model_control/test_generation_busy_gate.py
  tests/unit/runtime_model_control/test_llama_cpp_backend.py
Modified: なし
```

## 実装内容

```text
DirectoryModelDefinitionRegistry : config/models/*.tomlをmodel_keyでIndex化。
                                    既存load_model_definition()を再利用（TOML解析／Hash計算の再実装なし）。
                                    実Registry（現在Qwen 1件のみ）で解決Test済み。
ConversationServiceBusyGate      : ConversationGenerationService.active_request_id を
                                    Peekするのみ（Lock取得なし、副作用0）。Judge/Guard等
                                    非MAIN Roleは現時点でLease概念が無いため常にnot busy。
LlamaCppRuntimeModelBackend       : probe_capability()は宣言値（Definition+Deployment）を
                                    Load不要で返す。load()は実LlamaCppModelAdapter.load()を
                                    呼び、ModelRuntimeInfo.loaded_context_sizeから実測
                                    Capability（Architecture 3.2「Capability実測照合」）を構成。
                                    unload()は素通し委譲。
```

## Evidence Class（Governance「Model実Load TestとFake／Stub TestをEvidence Classで分離」準拠）

```text
Class: FAKE_ADAPTER_UNIT_TEST
  対象: DirectoryModelDefinitionRegistry（実config/models/を使うが、実Model Loadなし）、
        ConversationServiceBusyGate（Fake Conversation Service）、
        LlamaCppRuntimeModelBackend（Fake LlamaCppModelAdapter、実llama_cpp.Llama()構築なし）
  未実施: 実Qwen GGUF Load経由のEnd-to-endテスト（Real Model Loadは6-I Real Browser
          Golden Pathで実施予定。本WUはAdapter配線の正しさをFakeで検証する段階）
```

## Validation

```text
New Unit Test  : 22 passed（Domain 12 + Registry 3 + Busy Gate 4 + Backend 3）
Full Backend   : 1258 passed／3 deselected（既存1248 + 新規10、回帰0）
Ruff           : All checks passed
Mypy           : Success（13 source files、新規Adapter分含む）
```

## DeepSeek側の扱い

Model Definition登録・Backend Load実証ともにP6-A Toolchain Followup（CONTROLLER_OWNED_FOLLOWUP）解消まで見送る。CURRENT_TOOLCHAIN_UNSUPPORTED／NOT EXECUTEDとして記録し続ける。

## Next Exact Route

Phase 6-B-WU-004（Dynamic Context Size）およびWU-005（Dynamic Max New Tokens）へ進む。WU-003（Qwen→DeepSeek→Qwen Switch）はDeepSeek Artifact不在のため実Switch Testは不可。Switch機構自体（CAS／Busy／Rollback）はWU-001で汎用Fakeにより検証済みであり、DeepSeek Artifact成立後にQwen↔DeepSeekの実Switch Testを追加する。WU-006（bootstrap配線、web_application.pyへの統合）はContext/Token機構完成後にまとめて行う。
