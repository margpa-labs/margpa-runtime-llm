# Phase 1-B Model Runtime 最終設計レビュー

- 文書ID: `designer_review_phase_1b_model_runtime_final`
- 状態: `accepted_phase_1b_complete`
- 作成日時: `2026-07-19 00:16:04 JST`
- 更新日時: `2026-07-19 00:16:04 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719001604.md](../documentation_index_20260719001604.md)
- Review対象: [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md)
- Previous Review: [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](designer_review_phase_1b_model_runtime_follow_up_20260719000348.md)
- Initial Phase 1-B Review: [designer_review_phase_1b_model_runtime_20260718233938.md](designer_review_phase_1b_model_runtime_20260718233938.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- supersedes: `designer_review_phase_1b_model_runtime_follow_up_20260719000348.md`

## 1. Review Conclusion

Phase 1-B Model Runtimeを最終受入し、完了と判定する。

前回までのRequired Follow-up 2件とTest-only Follow-up 1件は、すべて完了した。

```text
実CLI Ctrl+C Cooperative Cancel       : Pass
Artifact Digest事実性                 : Pass
false Config Regression Test Fixture  : Pass
Pydantic Contract直接Test             : Pass
Static／Default Gate                   : Pass
実Model／Metal Gate                    : Pass／直前独立確認を継承
```

重大、中程度または軽微な未解決不具合は、今回のReview Scopeでは確認されなかった。

Phase 1-BのModel非依存Contract、llama.cpp Production Adapter、Qwen3-4B／Metal Runtime、Registry／Config、CLI、Streaming、Cancel、Artifact VerificationおよびTestは、次段階の基盤として利用できる。

本ReviewはPhase 1-B完了を示す。次Phaseの設計または実装を自動的に解禁するものではない。

## 2. Test-only Follow-up確認

対象：

- [test_config_and_registry.py](../../tests/unit/inference/test_config_and_registry.py)

### 2.1 有効な単一Key TOML

Fixtureは、既存Profileの次の値そのものを置換する。

```text
verify_artifact_hash = true
  ↓
verify_artifact_hash = false
```

確認した事項：

- `tomllib.loads()`が成功する
- Fixture内の`verify_artifact_hash`は1件だけである
- Parse後の`load.verify_artifact_hash`は`false`である
- `load_phase1_profile()`が`invalid_configuration`を返す

旧TestのTOML重複KeyによるFalse Positiveは解消された。

### 2.2 Pydantic Contract直接Test

次の直接Validationが追加された。

```text
ModelLoadConfig.model_validate({"verify_artifact_hash": False})
  ↓
pydantic.ValidationError
```

将来、`Literal[True]`が通常の`bool`へ誤って緩和された場合、このTestはFailする。

前回Required Test Acceptanceを満たした。

## 3. Independent Verification

### 3.1 Targeted Test

```text
tests/unit/inference/test_config_and_registry.py : 7 passed
```

### 3.2 Static／Default Gate

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／48 files
Ruff Check                 : Pass
mypy --strict              : Pass／48 source files
compileall                 : Pass
Default pytest             : 47 passed, 2 deselected
Environment Verification   : Pass
```

Environment：

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

### 3.3 Production不変性

今回の変更はTest Fileだけである。

前回Review文書より後に更新されたProduction Python SourceとConfigは確認されなかった。

報告書記載Hashも一致した。

```text
Model Definition SHA-512 : 723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415
Local Profile SHA-512    : f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35
pyproject.toml SHA-256   : a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa
uv.lock SHA-256         : e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Production Source、Config、DependencyおよびModel Artifactが不変であるため、今回Metal Gateは重ねて実行していない。

直前の設計者独立Reviewで次を確認済みである。

```text
pytest -m model_smoke : 2 passed, 46 deselected
実TTY Ctrl+C          : Generation cancelled.／Exit Code 130
model-info            : artifact_digest_verified=true／Metal／GPU Offload
```

この証跡を本最終Reviewへ継承する。

## 4. Phase 1-B Final Acceptance Matrix

```text
Model-independent Contract          : Pass
Model Port Protocol                 : Pass
llama.cpp Adapter isolation         : Pass
Registry／Config Validation         : Pass
Qwen3-4B Load／Unload               : Pass
Default Context 4,096               : Pass
Thinking Default OFF               : Pass
Thinking Explicit ON               : Pass
One-shot Generation                : Pass
Streaming                          : Pass
Explicit Stream Cancel             : Pass
実CLI Ctrl+C Cooperative Cancel     : Pass
CLI Exit Code 130                   : Pass
Post-cancel Generation              : Pass
Finish Reason Mapping               : Pass
Token Usage／Timing                 : Pass
Capability Validation              : Pass
Safe Error Contract                 : Pass
SHA-512常時検証                     : Pass
Runtime Digest事実性                : Pass
model-info Verification State       : Pass
false Config拒否                    : Pass
false Config Regression Protection  : Pass
Unit／Contract／Integration Test    : Pass
Ruff／mypy --strict                : Pass
Modelの暗黙Downloadなし            : Pass
Phase 2以降への越境なし            : Pass
```

## 5. Phase 1-B Completion Scope

完了：

```text
Inference Domain／Public Contract
Model Port／Lifecycle／Capability
llama.cpp Production Adapter
Qwen3-4B GGUF／Metal Runtime
Embedded Chat Template／Thinking Control
One-shot Generation／Streaming
Cooperative Cancel／Ctrl+C
Token Usage／Timing／Finish Reason
Context Overflow Policy
Safe Error Mapping
Model Registry／TOML Profile
Artifact Size／SHA-512 Verification
Runtime Info／Verification State
Config優先順位
Bootstrap／Dependency Injection
Phase 1-B CLI
Unit／Contract／実Model Integration Test
```

未着手：

```text
Multi-Turn Conversation
Conversation History／Storage
FastAPI／Web UI
Runtime Governance本実装
Audit Log本実装
Guard／Judge
RAG
Agent／Tool実行
複数Model同時常駐／Router
Remote／MLX／Transformers／vLLM Adapter
```

## 6. Known Non-blocking Items

次はPhase 1-B Blockerではない既知事項として維持する。

- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Load済みDefinition／Load Configが異なる場合の扱いは後続設計事項
- Distribution Revision／Commitを推測で補完しない
- Raw Output／Display Output分離は後続設計事項
- Native Buildの毎回再BuildはPhase 1-A既知事項
- `.DS_Store`再生成は別のRepository Hygiene事項

## 7. Next Gate

次段階へ進む前に、設計者とユーザーが少なくとも次を決める。

1. 次の実装単位をPhase 2 Multi-Turn／Web UIとするか
2. 会話Session、Message、HistoryのContract
3. Storage MVP境界
4. FastAPI／UI技術の最終選択
5. Streaming CancelをHTTP／UI境界へ接続する方式
6. 実装担当HandoffとWrite Scope

次段階の実装は、新しい設計、Handoffおよびユーザー許可後に行う。

## 8. Authorization Boundary

本ReviewはPhase 1-Bの最終受入と完了を記録する。

Phase 2、Runtime Governance、Audit、Guard、Judge、RAG、Agent、追加Dependencyまたは新しいDirectory／Configの実装を自動的に解禁するものではない。

