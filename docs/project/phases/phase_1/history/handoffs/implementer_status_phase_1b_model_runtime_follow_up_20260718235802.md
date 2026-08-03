# Phase 1-B Model Runtime Follow-up 実装状況

- 文書ID: `implementer_status_phase_1b_model_runtime_follow_up`
- 状態: `follow_up_complete_review_requested`
- 作成日時: `2026-07-18 23:58:02 JST`
- 更新日時: `2026-07-18 23:58:02 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718233938.md](../documentation_index_20260718233938.md)
- Designer Review: [designer_review_phase_1b_model_runtime_20260718233938.md](designer_review_phase_1b_model_runtime_20260718233938.md)
- Implementer Handoff: [designer_handoff_phase_1b_model_runtime_20260718224308.md](designer_handoff_phase_1b_model_runtime_20260718224308.md)
- 詳細設計: [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
- Accepted ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- Previous Status: [implementer_status_phase_1b_model_runtime_20260718232354.md](implementer_status_phase_1b_model_runtime_20260718232354.md)
- supersedes: `implementer_status_phase_1b_model_runtime_20260718232354.md`

## 1. 結論

設計ReviewでRequiredとなった2件を、Phase 1-BのSource／Test最小範囲で修正した。

```text
Required Follow-up 1: 実CLI Ctrl+C Cooperative Cancel : Pass
Required Follow-up 2: Artifact Digest事実性           : Pass
Regression Test                                       : Pass
Static／Default Gate                                  : Pass
実Model／Metal Gate                                   : Pass
Phase 2以降への越境                                   : なし
```

実装担当側ではFollow-up完了と判定し、Phase 1-Bの再Reviewを依頼する。

## 2. Follow-up 1：Process Control Exception境界

### 2.1 修正内容

Production Streamは、Backend由来の通常Exceptionだけを`generation_failed`へ変換する。

```text
KeyboardInterrupt／SystemExit／GeneratorExit
  ↓
Backend Errorへ変換しない
  ↓
CLIまたはProcess Control境界へ伝播
```

`LlamaCppGenerationStream.__iter__()`の一般捕捉を`BaseException`から`Exception`へ変更した。

`raise_mapped_backend_error()`も、`Exception`でないProcess Control Exceptionを受け取った場合は変換せず再送出するDefense-in-depthを追加した。

AdapterのLoad／Unload／Generation／Stream開始処理についても境界を見直した。

- 通常Backend Exceptionだけを安全な`InferenceError`へ変換する
- Load／Unload中の`KeyboardInterrupt`／`SystemExit`を変換しない
- Stream作成前のProcess Control ExceptionではGeneration Lockを解放する
- Non-stream Generationは既存`finally`でGeneration Lockを解放する
- 実Stream反復中の`KeyboardInterrupt`はActive StreamのままCLIへ到達する
- CLIが`stream.cancel()`を実行し、Terminal Stateを`cancelled`へ遷移させる
- Adapterの`on_terminal` CallbackによりGeneration Lockを解放する

### 2.2 Regression Test

追加確認：

- 実`LlamaCppGenerationStream`が`KeyboardInterrupt`を変換しない
- 実`LlamaCppGenerationStream`が`SystemExit`を変換しない
- Backend Error Mapperが両Process Control Exceptionを消費しない
- CLIと実`LlamaCppGenerationStream`を組み合わせる
- CLI Exit Code `130`
- Terminal State `cancelled`
- Native Iterator Close 1回
- `on_terminal`によるGeneration解放
- Cancel後に同じService Instanceで再Generation可能
- `generation_failed`を表示しない

実Model Integration Testでは、既存の同一Model Instanceに対する明示Cancel後の再Generationも再確認した。

### 2.3 実CLI／TTY確認

Metal実ModelをLoadし、長いStreaming Generation中にTTYからCtrl+Cを送った。

```text
^C
Generation cancelled.

Exit Code : 130
Error Code: generation_failedを表示しない
```

これにより、Reviewで再現されたExit Code `4`経路が修正されたことを実CLIで確認した。

## 3. Follow-up 2：Artifact Digest事実性

### 3.1 採用Contract

Designer Reviewで許容された次の方式を採用した。

```text
Phase 1-BではArtifact SHA-512を常に検証する
Hash検証の無効化を許可しない
Runtime Infoのartifact_digestは実測かつRegistry期待値との一致確認済み
Verification Stateをartifact_digest_verified=trueとして明示する
```

`ModelLoadConfig.verify_artifact_hash`は`Literal[True]`とし、Profile／Overrideから`false`を渡した場合は`invalid_configuration`となる。

`_verify_artifact()`はConfig値をRegistry期待Digestへ代入する処理を廃止し、File全体をSHA-512計算した実測値だけを返す。

実測値とRegistry期待値が異なる場合は、同一File Sizeでも`model_integrity_mismatch`となりModelをLoadしない。

`ModelRuntimeInfo`には次を追加した。

```text
artifact_digest_verified: Literal[True]
```

`model-info`と将来のAudit Consumerは、報告されたArtifact Digestが検証済みであることをJSON Fieldから判別できる。

### 3.2 Regression Test

追加確認：

- `verify_artifact_hash=false`を含むProfileを拒否する
- 同一Size／別DigestのArtifactを拒否する
- Runtime Infoで`artifact_digest_verified=true`
- CLI `model-info` JSONで`artifact_digest_verified: true`
- 実Model SHA-512を再計算してLoadする

実Modelの検証済みSHA-512：

```text
f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
```

## 4. 変更File

### Source

```text
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/error_mapping.py
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
M src/margpa_runtime_llm/modules/inference/contracts/runtime.py
```

### Test

```text
M tests/unit/inference/test_llama_cpp_boundary.py
M tests/unit/inference/test_config_and_registry.py
M tests/unit/inference/test_cli.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
```

### Config／Dependency

Tracked Profileの最終内容はReview前と同一であり、`verify_artifact_hash=true`を維持する。

```text
Config内容変更 : なし
pyproject変更  : なし
uv.lock変更    : なし
Dependency追加 : なし
```

Architecture／ADR／Review／旧Statusは編集していない。

## 5. Static／Default Gate

```text
bash -n Setup Recipe : Pass
Ruff Format Check     : Pass／48 files
Ruff Check            : Pass
mypy --strict         : Pass／48 source files
compileall            : Pass
Default pytest        : 46 passed, 2 deselected
```

Required Regression Testを含む対象Test：

```text
27 passed
```

Default TestはReview時の40件から46件となった。

## 6. Environment／Dependency Gate

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
uv lock --check           : Pass／117 packages
uv sync --dry-run offline : Pass／115 packages／Would make no changes
```

Phase 2以降のPackageは導入していない。

```text
torch／transformers／langchain／langgraph／mlx／mlx-lm : absent
```

## 7. 実Model／Metal Gate

```text
pytest -m model_smoke : 2 passed, 46 deselected
```

Production Runtime Acceptance：

```text
Success                         : true
Backend                         : llama-cpp-python 0.3.34
Device                          : Metal
GPU Offload                     : true
Context                         : 4,096
Artifact SHA-512 Verified       : true
Load including SHA-512          : 2.4538 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 30.72 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0447 seconds
```

ModelのDownload、Copy、Rename、変更は行っていない。

## 8. Hash／Lock不変性

```text
Model Definition SHA-512:
723954f2cd8f9df77a48614da05206c532ab56666069e57e117bddc219dcaefe5ad32b57f9b315b1e2e9cab5ba3526dad2176ca8d2df3ec997c05034bd98c415

Local Profile SHA-512:
f0d9c8e3ffe9264b77e0c7ca357705a200fc5419175910479ab53a8e49c543d13fb86484309d22ed39b57c81d10888e129282c62254da097ec89c3208b9b6b35

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 9. Deviation／残件

```text
Python Fallback            : なし
Backend Fallback           : なし
Dependency追加             : なし
Model Download             : なし
Phase 2以降への着手        : なし
Required Follow-up未完了   : なし
```

Review記載のNon-blocking Itemは今回変更していない。

- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Load済みDefinition／Load Configが異なる場合の扱いは後続設計事項
- Distribution Revision／Commitを推測で補完しない
- Raw Output／Display Output分離は後続設計事項
- Native Buildの毎回再BuildはPhase 1-A既知事項

## 10. 設計者への再Review依頼

次を再Reviewしてほしい。

1. Process Control ExceptionがBackend Errorへ変換されないこと
2. 実CLIのCtrl+C、Cooperative Cancel、Exit Code `130`
3. Stream Terminal StateとGeneration Lock解放
4. Cancel後の同一Model Instanceでの再Generation
5. Phase 1-BでSHA-512検証を無効化できないこと
6. Runtime Artifact Digestが実測かつ検証済みであること
7. `model-info`のVerification State
8. Regression TestとStatic／Default／Metal Gate

Phase 1-Bの最終受入および次Phase開始可否は、設計者再Reviewとユーザー判断に委ねる。
