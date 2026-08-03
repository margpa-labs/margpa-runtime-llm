# Phase 1 macOS ユーザーマニュアル

- 文書ID: `phase_1_macos_user_manual`
- 状態: `current`
- 作成日時: `2026-07-19 00:42:09 JST`
- 更新日時: `2026-07-19 00:42:09 JST`
- 対象: MARGPA Runtime LLM Phase 1-A／Phase 1-B
- 対象ユーザー: Local Mac環境でPhase 1を操作・確認するユーザー
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719004209.md](../documentation_index_20260719004209.md)
- Phase 1 Final Review: [designer_review_phase_1b_model_runtime_final_20260719001604.md](../handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
- supersedes: なし（新規User Manual系列）

## 1. このManualの目的

このManualは、現在のMacでMARGPA Runtime LLM Phase 1をユーザー自身が操作し、次を確認するための手順である。

- Model Runtime情報
- Qwen3-4Bによる一問一答
- Streaming表示
- Non-streaming表示
- Thinking Mode
- Ctrl+C Cooperative Cancel
- Default Test
- Qwen3実Model／Metal Test

Phase 1はCLIによる一問一答Runtimeである。GPT風Web UI、複数Turn会話、履歴保存、Runtime Governance本実装は後続Phaseで追加する。

## 2. 確認済み環境

```text
Project Name     : margpa-runtime-llm
Display Name     : MARGPA Runtime LLM
Internal Name    : Nazuna Research Governance LLM
OS               : macOS
Architecture     : Apple Silicon／arm64
Hardware         : MacBook Pro／Apple M2 Pro／16GB
Python           : CPython 3.13.14
Backend          : llama-cpp-python 0.3.34
Acceleration     : Metal／GPU Offload
Main Model       : Qwen3-4B Q4_K_M／GGUF
Loaded Context   : 4,096 tokens
Thinking Default : OFF
```

ユーザーは`2026-07-19 JST`に、本Manualへ記載した主要操作がすべて成功することを確認済みである。

## 3. 前提

次が準備済みであることを前提とする。

- Project Rootに`.venv/`がある
- `.venv`へPhase 1 Dependencyが導入済みである
- `models/`がLocal Model Rootを参照している
- 次のModel Artifactが存在する

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Model FileをProject内へ複製、改名または自動Downloadしない。

## 4. Project Rootへ移動する

macOSのTerminalを開き、次を実行する。

```bash
cd /path/to/margpa-runtime-llm
```

以降のCommandはProject Rootで実行する。

## 5. Model Runtime情報を確認する

```bash
./.venv/bin/margpa-llm model-info
```

成功時はJSONが表示される。

主な確認項目：

```text
runtime.model_key                   : main.qwen3-4b-q4-k-m
runtime.backend_key                 : llama_cpp
runtime.backend_version             : 0.3.34
runtime.model_architecture          : qwen3
runtime.quantization                : Q4_K_M
runtime.artifact_digest.algorithm   : sha512
runtime.artifact_digest_verified    : true
runtime.loaded_context_size         : 4096
runtime.device                      : metal
runtime.gpu_offload                 : true
effective_config.thinking_mode      : disabled
```

`load_instance_id`はModel Loadごとに変化するため、固定値との一致を確認しない。

## 6. 通常のStreaming生成を確認する

```bash
./.venv/bin/margpa-llm generate \
  --prompt "こんにちは。あなたの役割を日本語で短く説明してください。" \
  --max-new-tokens 128
```

成功時は、回答が少しずつTerminalへ表示される。

回答内容は生成ごとに変化し得る。完全一致ではなく、次を確認する。

- 日本語回答が生成される
- Streamingで文字が順次表示される
- Native ErrorやTracebackが表示されない
- Generation終了後にTerminal Promptへ戻る

## 7. Non-streaming生成を確認する

```bash
./.venv/bin/margpa-llm generate \
  --prompt "Runtime Governanceとは何か短く説明してください。" \
  --max-new-tokens 128 \
  --no-stream
```

成功時は、Generation完了後に回答全体がまとめて表示される。

## 8. Thinking Modeを確認する

```bash
./.venv/bin/margpa-llm generate \
  --prompt "小型LLMを交換可能にする設計を考えてください。" \
  --max-new-tokens 256 \
  --thinking
```

成功時はThinking有効設定でGenerationが完了する。

注意：

- Thinking有効化は回答品質を保証するものではない
- 小型Modelのため、回答品質には限界がある
- 生の内部推論をAudit Logへ保存する機能ではない
- DefaultはThinking OFFである

## 9. Ctrl+C Cooperative Cancelを確認する

長めの回答を要求する。

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1から10000まで、数字だけを順番に出力してください。途中で省略しないでください。" \
  --max-new-tokens 2048
```

Streaming中に、Keyboardの`Control`を押しながら`C`を押す。

成功時：

```text
Generation cancelled.
```

次を正常条件とする。

- `generation_failed`と表示されない
- Python Tracebackが表示されない
- Model Processを強制終了しなくてもTerminal Promptへ戻る
- CLI Process Exit Codeは`130`

Exit Codeを通常操作で見る必要はない。必要な場合は、Cancel直後に次を実行する。

```bash
echo $?
```

期待値：

```text
130
```

## 10. Default Testを実行する

実ModelをLoadしない高速Test：

```bash
./.venv/bin/pytest -q
```

本Manual作成時点の期待値：

```text
47 passed, 2 deselected
```

Test追加により件数は将来増加し得る。重要なのは`failed`または`error`が0件であること。

## 11. 実Model／Metal Testを実行する

```bash
./.venv/bin/pytest -q -m model_smoke
```

本Manual作成時点の期待値：

```text
2 passed, 47 deselected
```

このTestはQwen3-4Bを実際にLoadし、Metal／GPU Offload、Generation、Streaming、CancelおよびUnloadを確認する。

Default Testより時間とMemoryを使用する。

## 12. 通常動作として扱うもの

### 12.1 回答開始まで数秒かかる

現在のPhase 1 CLIは、Command実行ごとに次を行う。

1. Model ArtifactのSize確認
2. SHA-512全体検証
3. Qwen3-4BのLoad
4. Generation
5. Model Unload

そのため、回答表示まで数秒待つことがある。異常ではない。

### 12.2 回答内容が毎回同じではない

Generation設定とSeedにより、同じ質問でも回答が変化し得る。

### 12.3 一問一答で終了する

Phase 1 CLIは会話履歴を保持しない。新しいCommandは新しい一問一答として実行される。

## 13. 主なErrorと確認箇所

### `model_not_found`

確認するもの：

```bash
ls -l models
ls -l models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Model Rootを明示する場合：

```bash
MARGPA_MODEL_ROOT=/path/to/margpa-models \
  ./.venv/bin/margpa-llm model-info
```

### `model_integrity_mismatch`

Model FileのSizeまたはSHA-512がRegistryと一致していない。

Model File、RegistryまたはHashを推測で変更しない。実装担当／設計担当へ報告する。

### `backend_unavailable`または`model_load_failed`

Backend Version、Metal BuildまたはEnvironmentが一致していない可能性がある。

確認Command：

```bash
./.venv/bin/python scripts/setup/verify_phase1_environment.py
```

### `context_limit_exceeded`

Formatted Promptと`max_new_tokens`の合計がLoaded Context 4,096を超えている。

Messageを無断削除または要約せず、Promptを短くするか`--max-new-tokens`を明示的に下げる。

## 14. Phase 1でまだ利用できない機能

- GPT風Web UI
- 複数Turn会話
- Chat履歴保存／再開
- Runtime Governance本実装
- ARGD／DAGD実行
- Audit Log本実装
- Guard Model
- LLM-as-a-Judge
- RAG
- Agent／Tool実行
- Windows実行Profile
- Cloud Runtime

これらは後続Phaseまたは将来拡張で追加する。

## 15. Phase 1成功判定

最低限、次が成功すればユーザー動作確認は完了とする。

```text
model-info                  : Pass
Streaming Generation       : Pass
Non-streaming Generation   : Pass
Thinking Generation        : Pass
Ctrl+C Cancel              : Pass
Default Test               : Pass
実Model／Metal Test         : Pass
```

ユーザーは本Manual作成前に、上記すべての成功を確認済みである。
