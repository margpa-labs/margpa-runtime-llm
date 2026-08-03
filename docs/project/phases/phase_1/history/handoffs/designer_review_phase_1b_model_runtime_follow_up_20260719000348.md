# Phase 1-B Model Runtime Follow-up 設計レビュー

- 文書ID: `designer_review_phase_1b_model_runtime_follow_up`
- 状態: `test_follow_up_required`
- 作成日時: `2026-07-19 00:03:48 JST`
- 更新日時: `2026-07-19 00:03:48 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719000348.md](../documentation_index_20260719000348.md)
- Review対象: [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md)
- Previous Review: [designer_review_phase_1b_model_runtime_20260718233938.md](designer_review_phase_1b_model_runtime_20260718233938.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- supersedes: `designer_review_phase_1b_model_runtime_20260718233938.md`

## 1. Review Conclusion

前回ReviewでRequired Follow-upとしたRuntime実装2件は、Source、Contract、実CLI、実Model／Metalの独立確認で合格した。

```text
Required Follow-up 1: 実CLI Ctrl+C Cooperative Cancel : Pass
Required Follow-up 2: Artifact Digest事実性           : Pass
```

新たなRuntime不具合は確認されなかった。

ただし、Hash検証無効化を拒否するRegression Testが、意図したPydantic ContractではなくTOML重複KeyエラーによってPassしている。

```text
Runtime Source Fix          : Pass
実CLI／Metal                : Pass
Artifact Verification       : Pass
Required Regression Test    : Fail／Test Fixture修正のみ必要
```

したがってPhase 1-B Runtime実装本体は受理可能な状態であるが、前回Required Acceptanceに含めたRegression Test完了までは最終受入を保留する。

必要なFollow-upはTest File 1件の最小修正であり、Production Source、Config、Dependencyまたは実Modelの変更は不要である。

## 2. Required Follow-up確認

### 2.1 Ctrl+C Cooperative Cancel

対象：

- [stream.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py)
- [error_mapping.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/error_mapping.py)
- [adapter.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)
- [main.py](../../src/margpa_runtime_llm/entrypoints/cli/main.py)

確認結果：

- `LlamaCppGenerationStream`はBackend由来の`Exception`だけをError Mappingする
- `KeyboardInterrupt`／`SystemExit`を`generation_failed`へ変換しない
- Error MapperにもProcess Control Exceptionを再送出するDefense-in-depthがある
- Stream開始前のProcess Control ExceptionでGeneration Lockを解放する
- Non-stream Generationは`finally`でGeneration Lockを解放する
- CLIが`KeyboardInterrupt`を受けて`stream.cancel()`を実行する
- CancelによりNative IteratorをCloseし、Terminal Callbackを1回実行する
- Terminal Stateを`cancelled`とする
- Cancel後に同じServiceでGeneration可能なRegression Testがある

実TTYへ長いStreaming Generation中にCtrl+Cを送った独立結果：

```text
^C
Generation cancelled.
Exit Code: 130
```

`generation_failed`は表示されなかった。

Follow-up 1はPassとする。

### 2.2 Artifact Digest事実性

対象：

- [runtime.py](../../src/margpa_runtime_llm/modules/inference/contracts/runtime.py)
- [adapter.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)
- [config_and_registry test](../../tests/unit/inference/test_config_and_registry.py)
- [llama.cpp boundary test](../../tests/unit/inference/test_llama_cpp_boundary.py)

確認結果：

- `ModelLoadConfig.verify_artifact_hash`は`Literal[True]`
- `_verify_artifact()`はFile全体のSHA-512を常に計算する
- Registry期待値を実測値として代入する旧処理は存在しない
- File Size一致／Digest不一致を`model_integrity_mismatch`で拒否する
- `ModelRuntimeInfo`は`artifact_digest_verified=true`を持つ
- Production Adapterは検証成功後にだけRuntime Infoを構築する
- 実`model-info`は検証済みDigestを構造化表示する

実`model-info`独立結果：

```text
artifact_digest.algorithm : sha512
artifact_digest.value     : f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
artifact_digest_verified  : true
device                    : metal
gpu_offload               : true
```

有効なTOMLで`verify_artifact_hash=false`だけを設定した独立確認では、`invalid_configuration`として拒否された。

Follow-up 2のProduction ContractとRuntime動作はPassとする。

## 3. Finding

### 3.1 [P3／Required Test Correction] Hash無効化Testが重複TOMLを検査している

対象：

- [test_config_and_registry.py](../../tests/unit/inference/test_config_and_registry.py)

現在のTestは次の置換を行う。

```text
verbose_backend = false
```

を次へ置換する。

```text
verbose_backend = false
verify_artifact_hash = false
```

しかし元のProfileには、直後に既存の次の設定がある。

```text
verify_artifact_hash = true
```

生成されるFixtureは同じTable内に`verify_artifact_hash`を2回持つ。

独立確認結果：

```text
tomllib.loads(fixture)
  ↓
TOMLDecodeError: Cannot overwrite a value
```

したがってTestは、`ModelLoadConfig.verify_artifact_hash: Literal[True]`が`false`を拒否したためではなく、TOML Parserが重複Keyを拒否したためにPassしている。

このままでは、将来`Literal[True]`制約が誤って通常の`bool`へ戻ってもTestが緑のままとなる。

#### Required Test Acceptance

- 元Profileの`verify_artifact_hash = true`を`false`へ置換する
- 生成Fixtureが有効なTOMLであることを前提にする
- `load_phase1_profile()`が`invalid_configuration`を返すことを確認する
- 可能であれば`ModelLoadConfig(verify_artifact_hash=False)`自体もValidation Errorになることを直接Testする
- Default Testを再実行する
- 新TimestampのImplementer Statusを作成する

Production Source修正は不要である。

## 4. Independent Verification

### 4.1 Static／Default Gate

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／48 files
Ruff Check                 : Pass
mypy --strict              : Pass／48 source files
compileall                 : Pass
Default pytest             : 46 passed, 2 deselected
Environment Verification   : Pass
Core llama_cpp Import Scan : Pass／0件
Out-of-scope Import Scan   : Pass／0件
```

### 4.2 実Model／Metal Gate

Metalアクセス可能な実機条件で確認した。

```text
pytest -m model_smoke : 2 passed, 46 deselected
```

確認項目：

- Qwen3-4B Artifact SHA-512検証
- llama-cpp-python 0.3.34
- Metal／GPU Offload
- Context 4,096
- Thinking Default OFF／Explicit ON
- One-shot Generation
- Streaming
- 明示Cancel
- Cancel後の再Generation
- Unload／Unload Idempotency

### 4.3 Dependency／Hash

```text
uv lock --check : Pass／117 packages
uv sync --dry-run --frozen --offline
  --extra inference-llama
  --group dev
  --group notebook
  --no-binary-package llama-cpp-python
Result           : Checked 115 packages／Would make no changes
```

報告書記載Hashはすべて一致した。

```text
Model Definition SHA-512 : 723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415
Local Profile SHA-512    : f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35
pyproject.toml SHA-256   : a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa
uv.lock SHA-256         : e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 5. Acceptance Matrix

```text
Process Control Exception境界     : Pass
実CLI Ctrl+C                       : Pass
CLI Exit Code 130                  : Pass
Stream Terminal State cancelled   : Pass
Generation Lock解放               : Pass
Cancel後の再Generation            : Pass
SHA-512常時検証                    : Pass
同一Size／Digest不一致拒否         : Pass
Runtime Digest事実性               : Pass
model-info Verification State      : Pass
Regression Test／Ctrl+C            : Pass
Regression Test／Digest不一致      : Pass
Regression Test／false Config拒否  : Fail／Fixture修正必要
Static／Default Gate               : Pass
実Model／Metal Gate                : Pass
Dependency／Config不変             : Pass
Phase 2以降への越境                : なし
```

## 6. Non-blocking Items

前回までの次の項目は変更していない。

- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Load済みDefinition／Load Configが異なる場合の扱いは後続設計事項
- Distribution Revision／Commitを推測で補完しない
- Raw Output／Display Output分離は後続設計事項
- Native Buildの毎回再BuildはPhase 1-A既知事項

## 7. Re-review Gate

次を満たした後にPhase 1-Bを最終受入する。

1. `verify_artifact_hash=false`のTest Fixtureを有効なTOMLへ修正する
2. 意図したPydantic Contract拒否を確認する
3. Default Test／Static Gateを再実行する
4. 新しいImplementer Statusを作成する
5. 設計者がTestと結果を再確認する

Production Source、Config、Dependencyまたは実Modelを変更した場合は、対象に応じてMetal Gateも再実行する。

## 8. Authorization Boundary

本ReviewはFollow-up結果の確認と、Test-only残件を記録する。

Test修正、Source変更、Config変更、Dependency変更または次Phase実装を自動的に許可するものではない。実装担当はユーザーから与えられたWrite Scopeと実装許可に従う。

