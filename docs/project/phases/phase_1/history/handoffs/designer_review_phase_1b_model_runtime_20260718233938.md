# Phase 1-B Model Runtime 設計レビュー

- 文書ID: `designer_review_phase_1b_model_runtime`
- 状態: `follow_up_required`
- 作成日時: `2026-07-18 23:39:38 JST`
- 更新日時: `2026-07-18 23:39:38 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718233938.md](../documentation_index_20260718233938.md)
- Review対象: [implementer_status_phase_1b_model_runtime_20260718232354.md](implementer_status_phase_1b_model_runtime_20260718232354.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Previous Phase Review: [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)
- supersedes: なし（新規Phase 1-B Review系列）

## 1. Review Conclusion

Phase 1-B Model Runtimeは、主要な骨格、Model Port、llama.cpp Adapter、Config、CLI、Contract、実Model／Metal経路まで成立している。

一方、Phase 1-Bの明示的Acceptance Criteriaに反する問題1件と、Runtime Info／将来Auditの事実性に関わる問題1件を確認した。

```text
Required Follow-up 1: 実CLIのCtrl+C Cooperative Cancel修正     : Fail
Required Follow-up 2: Artifact Digestの観測値／期待値分離     : Fail
```

このため、現時点ではPhase 1-Bを最終受入しない。

実装担当は2件を修正し、Regression Testと新しいAppend-Only Statusを作成する。設計者はそのStatusと実装を再レビューする。

Phase 1-CまたはPhase 2の実装開始可否は、本Reviewだけでは確定しない。

## 2. Findings

### 2.1 [P1／Required] 実StreamがKeyboardInterruptを推論失敗へ変換する

対象：

- [stream.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py)
- [main.py](../../src/margpa_runtime_llm/entrypoints/cli/main.py)
- [test_cli.py](../../tests/unit/inference/test_cli.py)

`LlamaCppGenerationStream.__iter__()`は、`GeneratorExit`と`InferenceError`以外の`BaseException`を捕捉し、`generation_failed`へ変換する。

`KeyboardInterrupt`は`BaseException`の派生であるため、CLIの次の処理へ到達しない。

```text
CLIがKeyboardInterruptを受け取る
  ↓
stream.cancel()
  ↓
Terminal State = cancelled
  ↓
"Generation cancelled."
  ↓
Exit Code = 130
```

実際の経路は次となる。

```text
Ctrl+C
  ↓
LlamaCppGenerationStream.__iter__がKeyboardInterruptを捕捉
  ↓
Terminal State = failed
  ↓
InferenceError(code=generation_failed)
  ↓
CLI Error表示
  ↓
Exit Code = 4
```

実CLIへ生成中にCtrl+Cを送った独立確認結果：

```text
^Cerror [generation_failed]: Streaming failed in the model backend.
```

報告書の次の記載は、現在のProduction Stream経路では成立していない。

```text
Cooperative Cancel : Pass
User Cancel        : Terminal State=cancelled／CLI Exit Code=130
```

現在のCLI Unit Testは、`KeyboardInterrupt`を直接送出する`FakeStream`をCLIへ渡している。このFakeは`LlamaCppGenerationStream.__iter__()`の例外変換を通らないため、境界間の不整合を検出できない。

また、`adapter.py`のLoad、Unload、Non-stream Generation、Stream生成前処理にも`except BaseException`があり、`KeyboardInterrupt`と`SystemExit`をBackend Errorへ変換し得る。Backend由来の通常例外とProcess Control Exceptionの境界を全体で見直す。

#### Required Acceptance

- 実`LlamaCppGenerationStream`経路で`KeyboardInterrupt`を通常の`generation_failed`へ変換しない
- CLIが割込みを受け、`stream.cancel()`を実行する
- Stream Terminal Stateを`cancelled`とする
- Generation Lockを解放する
- CLI Exit Codeを`130`とする
- `Generation cancelled.`を安全に表示する
- Cancel後に同一Model Instanceで再Generationできる
- `LlamaCppGenerationStream`とCLIを組み合わせたRegression Testを追加する
- Backend Error Mappingが`KeyboardInterrupt`／`SystemExit`を飲み込まないことをTestする

### 2.2 [P2／Required] Hash未検証時にRegistry期待値を実測Digestとして返す

対象：

- [adapter.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)
- [runtime.py](../../src/margpa_runtime_llm/modules/inference/contracts/runtime.py)
- [test_llama_cpp_boundary.py](../../tests/unit/inference/test_llama_cpp_boundary.py)

`_verify_artifact()`は、最初に次を設定する。

```text
actual_digest = definition.artifact.sha512
```

`verify_artifact_hash=true`の場合だけFileを読み、実際のSHA-512へ置き換える。

したがって`verify_artifact_hash=false`の場合、File内容をHashしていないにもかかわらず、Registryの期待値を`actual_digest`として返す。返された値は`ModelRuntimeInfo.artifact_digest`へ格納される。

独立した最小再現では、登録SHA-512を`000...000`、同一Sizeの実File内容を別内容とし、Hash検証を無効化したところ、未観測の`000...000`が返された。

```text
verify_artifact_hash : false
File Hash計算        : 未実施
reported digest      : Registry期待値
```

Default Profileは`verify_artifact_hash=true`であり、今回の通常Metal実行で得たDigestは検証済みである。この問題はDefault Profileの実Model Hash結果を否定しない。

しかし、設定を無効化したRuntimeでは、期待値と観測値を区別できない。これは将来のAudit Log、Model Runtime Reference、再現性および「System Trace由来の事実」と矛盾する。

#### Required Acceptance

- Registry Expected DigestとRuntimeでObserved／VerifiedされたDigestを混同しない
- Hash未検証時に、未観測値を実測値として表現しない
- 次のいずれか、または同等に明示的なContractを採用する
  - Phase 1-Bでは常にHashを検証し、無効化設定を廃止する
  - Observed DigestをNullableにし、Verification Stateを別Fieldで持つ
  - Expected Digest、Observed Digest、Verification Stateを分離する
- `verify_artifact_hash=false`かつ同一Size／別内容のTestを追加する
- `model-info`と将来Audit Consumerが検証済みか否かを判別できるようにする

## 3. Independent Verification

設計者役担当Taskから、実装報告、設計正本、ADR、Config、Source、Test、CLIおよび実Model／Metalを独立確認した。

### 3.1 Static／Default Test

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／48 files
Ruff Check                 : Pass
mypy --strict              : Pass／48 source files
compileall                 : Pass
Default pytest             : 40 passed, 2 deselected
Environment Verification   : Pass
Core llama_cpp Import Scan : Pass／0件
Out-of-scope Import Scan   : Pass／0件
```

Environment：

```text
Python             : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python   : 0.3.34
GPU Offload        : supported
Metal System Info  : present
Out-of-scope Model Framework Package: absent
```

### 3.2 Dependency Lock／Offline Dry-run

Phase 1 Setup Recipeと同じExtra／Groupを指定して、環境を変更しないDry-runを確認した。

```text
uv lock --check : Pass／117 packages
uv sync --dry-run --frozen --offline
  --extra inference-llama
  --group dev
  --group notebook
  --no-binary-package llama-cpp-python
Result           : Checked 115 packages／Would make no changes
```

### 3.3 Config Hash

報告書記載値と一致した。

```text
Model Definition SHA-512:
723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415

Local Profile SHA-512:
f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35
```

### 3.4 Opt-in実Model／Metal

制限環境内ではMetal Contextを作成できないため、Metalアクセス可能な実機条件で明示的に再実行した。

```text
pytest -m model_smoke : 2 passed, 40 deselected
```

次を独立確認した。

- Qwen3-4B GGUFを暗黙DownloadせずLoadする
- llama-cpp-python 0.3.34／Metal／GPU Offload
- Context 4,096
- Artifact Size／SHA-512
- Embedded Chat Template
- Thinking Default OFF／Explicit ON
- One-shot Generation
- Streaming／Final Chunk
- 明示的`stream.cancel()`
- Cancel後の再Generation
- Explicit Unload／Unload Idempotency

明示的な`stream.cancel()`は正常である。Finding 2.1は、OS／Terminal由来の`KeyboardInterrupt`をProduction Streamが誤変換する問題であり、Cancel API自体の失敗ではない。

## 4. Acceptance Matrix

```text
Model-independent Contract        : Pass
Model Port Protocol               : Pass
llama.cpp Adapter isolation       : Pass
Registry／Config Validation       : Pass
Qwen3-4B Load／Unload             : Pass
Default Context 4,096             : Pass
Thinking Default OFF             : Pass
Thinking Explicit ON             : Pass
One-shot Generation              : Pass
Streaming                        : Pass
Explicit Stream Cancel           : Pass
CLI Ctrl+C Cooperative Cancel     : Fail／Required Follow-up
Post-cancel Generation            : Pass
Finish Reason Mapping             : Pass
Token Usage／Timing               : Pass
Capability Validation            : Pass
Safe Error Contract               : Pass
Runtime Digest Truthfulness       : Fail／Required Follow-up
Unit／Contract／Integration Test  : Partial／Regression不足
Ruff／mypy --strict              : Pass
Modelの暗黙Downloadなし          : Pass
Phase 2以降への越境なし          : Pass
```

## 5. Non-blocking Observation

同一ModelのIdempotent Load判定は、現在`model_key`だけを比較する。

同じKeyで異なる`ModelDefinition`または`ModelLoadConfig`を渡しても、既存の`runtime_info`を返す。現在のPhase 1-B Bootstrapは1回Loadするため、直ちに障害にはなっていない。

将来、Profile変更やContext Size変更を同一Processへ適用する場合は、次のいずれかを明示する。

- Idempotent条件をModel Key、Definition Hash、Load Configの同一性まで含める
- Load済みConfigと異なる場合は明示Errorにする
- Config変更には明示Unload／Reloadが必要とContractへ記載する

本項目は今回のRequired Follow-upには含めない。

## 6. Required Follow-up Scope

実装担当は、Source／Testの必要最小範囲で次を行う。

1. Process Control ExceptionとBackend Errorの境界を修正する
2. 実Stream経由のCtrl+C Regression Testを追加する
3. CLI Exit Code 130、Terminal State、Lock解放、Post-cancel Generationを確認する
4. Artifact Expected／Observed／Verifiedの意味を修正する
5. Hash検証無効時のRegression Testを追加する
6. Default Test、Static Gate、Opt-in Metal Testを再実行する
7. 新Timestampの`implementer_status_phase_1b_model_runtime_follow_up_*.md`を作成する

設計Contract自体の変更が必要な場合は、既存Architecture／ADRを編集せず、設計者へ報告する。

## 7. Authorization Boundary

本Reviewは調査と受入判定を記録する。

Source修正、Contract変更、Config変更、Dependency変更またはPhase 2実装を自動的に許可するものではない。実装担当はユーザーから与えられたWrite Scopeと実装許可に従う。

## 8. Re-review Gate

次を満たした後にPhase 1-Bを再レビューする。

1. Required Follow-up 2件が実装される
2. Regression Testが追加される
3. Static／Default／Metal GateがPassする
4. 新しいImplementer Statusが作成される
5. 設計者がSourceと実CLIを再確認する

