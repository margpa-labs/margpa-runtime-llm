# Phase 1 macOS ユーザーマニュアル

- 文書ID: `phase_1_macos_user_manual`
- 状態: `current_user_acceptance_candidate`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 対象: MARGPA Runtime LLM Phase 1-A～Phase 1-E
- 対象ユーザー: Local Mac環境でPhase 1を操作・受入確認するユーザー
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719171836.md](../documentation_index_20260719171836.md)
- Phase 1 Readiness Review: [designer_review_phase_1_final_readiness_20260719171836.md](../handoffs/designer_review_phase_1_final_readiness_20260719171836.md)
- Phase 1-E Final Review: [designer_review_phase_1e_final_20260719164641.md](../handoffs/designer_review_phase_1e_final_20260719164641.md)
- Backup Policy: [phase_completion_backup_policy_20260719171836.md](../operations/phase_completion_backup_policy_20260719171836.md)
- supersedes: `phase_1_macos_user_manual_20260719004209.md`

## 1. このManualの目的

このManualは、現在のMacでMARGPA Runtime LLM Phase 1全体をユーザー自身が操作し、User Acceptance Testを行うための手順である。

対象：

```text
Phase 1-A : Python／uv／Metal Environment
Phase 1-B : Model Adapter／CLI Generation
Phase 1-C : Deployment／Platform／Acceleration Hook
Phase 1-D : Configuration Layer／Response Language
Phase 1-E : Thinking Execution／Parsing／Presentation
```

確認する主な機能：

- EnvironmentとDependency
- Model Runtime情報
- Qwen3-4B GGUF／Metal Load
- Streaming／Non-streaming
- Ctrl+C Cooperative Cancel
- `ja／en／auto`
- Thinking Executionと表示の独立
- Thinking非表示／Default Label／Custom Label
- Config SourceとSchema
- Default Test／Native Metal Test

Phase 1はCLIによる一問一答Runtimeである。GPT風Web UI、複数Turn会話、履歴保存、Runtime Governance本実装は後続Phaseで追加する。

## 2. 確認済み環境

```text
Project Name       : margpa-runtime-llm
Display Name       : MARGPA Runtime LLM
Internal Name      : Nazuna Research Governance LLM
OS                 : macOS
Architecture       : Apple Silicon／arm64
Hardware           : MacBook Pro／Apple M2 Pro／16GB
Python             : CPython 3.13.14
Backend            : llama-cpp-python 0.3.34
Acceleration       : Metal／GPU Offload
Main Model         : Qwen3-4B Q4_K_M／GGUF
Loaded Context     : 4,096 tokens
Application Schema : 2
Model Schema       : 2
Deployment Schema  : 3
Response Default   : ja
Thinking Default   : disabled
Visibility Default : hidden
Display Label      : 高度推論
Persistence        : disabled
```

この環境は設計者役の独立ReviewでStatic、Default Test、Native Metal Testまで確認済みである。ユーザー受入テストは、本Manualに従って別途実行する。

## 3. Platform境界

Native Verified：

```text
macOS／Apple Silicon arm64／Metal
```

Phase 1-CではWindows、Linux、CPU、CUDA、ROCm等を追加できるProfile／Registry／Validation Hookを用意したが、次はまだ主張しない。

- Windows Native Verified
- Linux Native Verified
- CUDA Runtime Verified
- ROCm Runtime Verified
- Intel Mac Verified
- Cross-platform Installer完成

未検証Platformで動く可能性と、動作確認済みであることを混同しない。

## 4. 前提

次が準備済みであることを前提とする。

- Project Rootに`.venv/`がある
- Phase 1 Dependencyが導入済みである
- `models/`がLocal Model Rootを参照するPOSIX Symbolic Linkである
- 次のModel Artifactが存在する

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Model FileをProject内へ複製、改名または自動Downloadしない。

## 5. Project Rootへ移動する

macOSのTerminalを開き、次を実行する。

```bash
cd /path/to/margpa-runtime-llm
```

以降のCommandはProject Rootで実行する。

## 6. CLI Helpを確認する

```bash
./.venv/bin/margpa-llm --help
./.venv/bin/margpa-llm generate --help
./.venv/bin/margpa-llm model-info --help
```

`generate`の主なOption：

```text
--response-language {ja,en,auto}
--no-stream
--thinking／--no-thinking
--show-thinking／--hide-thinking
--thinking-label
--max-new-tokens
--temperature／--top-p／--top-k
--seed／--stop
```

## 7. Environmentを確認する

```bash
./.venv/bin/python scripts/setup/verify_phase1_environment.py
```

主な合格条件：

```text
python.version                         : 3.13.14
python.implementation                  : CPython
python.machine                         : arm64
backend.gpu_offload_supported          : true
backend.metal_system_info_present      : true
validation.dependency_versions_match   : true
validation.out_of_scope_packages_absent: true
```

PathはLocal環境に応じて表示されるため、固定値との一致を要求しない。

## 8. Model Runtime情報を確認する

```bash
./.venv/bin/margpa-llm model-info
```

成功時はJSONが表示される。

主な確認項目：

```text
runtime.model_key                                      : main.qwen3-4b-q4-k-m
runtime.backend_key                                    : llama_cpp
runtime.backend_version                                : 0.3.34
runtime.model_architecture                             : qwen3
runtime.quantization                                   : Q4_K_M
runtime.artifact_digest.algorithm                      : sha512
runtime.artifact_digest_verified                       : true
runtime.loaded_context_size                            : 4096
runtime.device                                         : metal
runtime.gpu_offload                                    : true
effective_config.application_schema_version            : 2
effective_config.generation.thinking_mode              : disabled
effective_config.response.language                     : ja
effective_config.response.source                       : application
effective_config.presentation.thinking.visibility      : hidden
effective_config.presentation.thinking.display_label   : 高度推論
effective_config.presentation.thinking.persistence     : disabled
model_output_protocol.model_definition_schema_version  : 2
model_output_protocol.thinking.parser_key              : tagged_thinking_v1
```

`load_instance_id`はModel Loadごとに変化するため、固定値との一致を確認しない。

## 9. Configurationの責務を確認する

Phase 1の主なTracked Config：

```text
config/application.toml
  Common Model Selection
  Model Root Default
  Load Default
  Generation Default
  Response Language
  Thinking Presentation

config/models/qwen3_4b_q4_k_m.toml
  Model Identity
  Artifact／SHA-512
  Backend／Capability
  Canonical Output Protocol

config/profiles/local_macos_arm64.toml
  macOS／arm64／Metal Deployment
  Hardware-dependent Load Override

config/platforms/platform_registry.toml
  Platform Alias／Default Profile Resolution
```

通常のUser Acceptance TestではConfig Fileを編集しない。CLI Overrideを使う。

## 10. Default日本語Streaming生成

```bash
./.venv/bin/margpa-llm generate \
  --prompt "こんにちは。あなたの役割を日本語で短く説明してください。" \
  --max-new-tokens 128
```

合格条件：

- 日本語回答が生成される
- Streamingで文字が順次表示される
- Native ErrorやTracebackが表示されない
- Generation終了後にTerminal Promptへ戻る
- Canonical `<think>` Tagが表示されない

回答内容の完全一致は要求しない。

## 11. Response Languageを確認する

### 11.1 明示的な日本語

```bash
./.venv/bin/margpa-llm generate \
  --prompt "自己紹介してください。" \
  --response-language ja \
  --max-new-tokens 128
```

### 11.2 明示的な英語

```bash
./.venv/bin/margpa-llm generate \
  --prompt "Briefly introduce yourself." \
  --response-language en \
  --max-new-tokens 128
```

英語回答が生成されれば合格とする。

### 11.3 Auto

```bash
./.venv/bin/margpa-llm generate \
  --prompt "日本語でOKとだけ答えてください。" \
  --response-language auto \
  --max-new-tokens 32
```

`auto`は言語を自動判定するClassifierではなく、RuntimeからDefault Language Instructionを追加しないModeである。User Promptの明示指定にModelが従い、日本語で回答すれば合格とする。

## 12. Non-streaming生成

```bash
./.venv/bin/margpa-llm generate \
  --prompt "Runtime Governanceとは何か、日本語で短く説明してください。" \
  --max-new-tokens 128 \
  --no-stream
```

Generation完了後に回答全体がまとめて表示され、TracebackなしでTerminal Promptへ戻れば合格とする。

## 13. Thinking Execution／Presentation

Phase 1-Eでは次を分離する。

```text
Execution    : ModelにThinkingを実行させるか
Parsing      : Canonical Model OutputをReasoning／Finalへ分ける
Presentation : Reasoningを利用者へ表示するか
Persistence  : Raw Reasoningを永続保存するか
```

### 13.1 Thinking有効／表示なし

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1+1を考えて、最後に答えだけを示してください。日本語で。" \
  --max-new-tokens 256 \
  --thinking \
  --hide-thinking
```

合格条件：

- Canonical `<think>`／`</think>`が表示されない
- Reasoning本文が表示されない
- ModelがClosing／Finalまで生成した場合、Final Answerが表示される
- Tracebackがない

Token上限までにClosingへ到達しない場合、Hidden表示が空になることがある。Reasoning漏洩がなければ、直ちにParser不良とは判定しない。`--max-new-tokens`を512程度へ増やして再確認できる。

### 13.2 Thinking有効／Default Label表示

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1+1を考えて、最後に答えを示してください。日本語で。" \
  --max-new-tokens 512 \
  --thinking \
  --show-thinking
```

ReasoningがCanonical Protocolとして生成された場合：

```text
<高度推論>...</高度推論>
Final Answer
```

合格条件：

- 表示Tagが`高度推論`
- Canonical `<think>`／`</think>`が表示用Tagとして残らない
- Unclosed時も表示Containerが閉じる
- Tracebackがない

`高度推論`は表示Channelの名前であり、Reasoningの正しさや品質を保証しない。

### 13.3 Custom Label

```bash
./.venv/bin/margpa-llm generate \
  --prompt "小型LLMを交換可能にする設計を考えてください。日本語で。" \
  --max-new-tokens 512 \
  --thinking \
  --show-thinking \
  --thinking-label "思考過程"
```

Reasoningが生成された場合、`<思考過程>...</思考過程>`が使われれば合格とする。

### 13.4 ExecutionとVisibilityの独立

`--show-thinking`だけではThinking ExecutionをONにしない。

```bash
./.venv/bin/margpa-llm generate \
  --prompt "OKとだけ答えてください。" \
  --show-thinking \
  --max-new-tokens 32
```

Thinking SectionがなければFinalだけが表示される。これは正常である。

## 14. Generation Parameter Override

例：

```bash
./.venv/bin/margpa-llm generate \
  --prompt "短い雑談を日本語でしてください。" \
  --max-new-tokens 128 \
  --temperature 0.6 \
  --top-p 0.9 \
  --seed 2371
```

Thinking FlagはTemperature、Top-p等を暗黙変更しない。

## 15. Ctrl+C Cooperative Cancel

```bash
./.venv/bin/margpa-llm generate \
  --prompt "1から10000まで、数字だけを順番に出力してください。途中で省略しないでください。" \
  --max-new-tokens 2048
```

Streaming中に`Control + C`を押す。

成功時：

```text
Generation cancelled.
```

合格条件：

- `generation_failed`と表示されない
- Python Tracebackが表示されない
- Model Processを強制終了せずTerminal Promptへ戻る
- CLI Process Exit Codeが`130`

必要な場合はCancel直後に確認する。

```bash
echo $?
```

## 16. Default Test

実ModelをLoadしない高速Test：

```bash
./.venv/bin/pytest -q
```

Snapshot `20260719171836`の期待値：

```text
161 passed, 2 deselected
```

Test追加により件数は将来増加し得る。`failed`または`error`が0件であることを合格条件とする。

## 17. 実Model／Metal Test

```bash
./.venv/bin/pytest -q -m model_smoke
```

Snapshot `20260719171836`の期待値：

```text
2 passed, 161 deselected
```

このTestはQwen3-4Bを実際にLoadし、SHA-512、Metal／GPU Offload、Language、Thinking Presentation、Generation、Streaming、Cancel、Unloadを確認する。

Default Testより時間とMemoryを使用する。

## 18. 通常動作として扱うもの

### 18.1 回答開始まで数秒かかる

現在のCLIはCommand実行ごとにModel Artifact Size／SHA-512、Model Load、Generation、Unloadを行う。回答表示まで数秒待つことは異常ではない。

### 18.2 回答内容が毎回同じではない

確率的Generationのため、完全一致を要求しない。言語、表示境界、Error有無、構造で判定する。

### 18.3 一問一答で終了する

Phase 1 CLIは会話履歴を保持しない。新しいCommandは新しい一問一答である。

### 18.4 Thinkingが長くFinalへ到達しない

小型ModelとToken上限により、Closing Tag／Final Answerまで到達しない場合がある。Token上限を増やすかPromptを短くして再確認する。

## 19. 主なErrorと確認箇所

### `model_not_found`

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

Model FileのSizeまたはSHA-512がRegistryと一致しない。Model File、Registry、Hashを推測で変更せず、実装担当／設計担当へ報告する。

### `backend_unavailable`／`model_load_failed`

Backend Version、Metal Build、Environmentが一致していない可能性がある。Section 7のEnvironment Verificationを行う。

### `context_limit_exceeded`

Formatted Promptと`max_new_tokens`の合計がLoaded Context 4,096を超えている。Messageを無断削除せず、Promptまたは`max_new_tokens`を明示的に小さくする。

### `invalid_configuration`／`invalid_request`

Config、Environment、CLI Overrideの値がSchemaまたはValidationに合っていない。Raw値を推測修正せず、指定したOptionとEnvironment Variableを確認する。

## 20. Known Diagnostic Observation

異なるFieldへEnvironmentとCLIから同時に値を指定し、Environment側だけが不正な場合、Error Codeが`invalid_configuration`ではなく`invalid_request`となる組合せがある。

不正値は安全に拒否されるため、Phase 1の通常操作やSecurity Boundaryには影響しない。詳細は次を参照する。

- [known_issues_and_observations_20260719171836.md](../operations/known_issues_and_observations_20260719171836.md)

## 21. Phase 1で利用可能／未実装

### 利用可能

- Local Qwen3 GGUF／Metal推論
- Model Adapter／Raw Model Port
- Streaming／Non-streaming
- Cancel／Unload
- Generation Config
- `ja／en／auto`
- Thinking Execution
- Thinking Hidden／Visible／Custom Label
- Model／Application／Deployment／Platform Config分離
- Platform／Acceleration拡張Hook

### 未実装

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
- Windows／Linuxの実ProfileとNative Verification
- Cloud Runtime

## 22. User Acceptance Test Checklist

次を同じProject状態で実行する。

| # | 確認項目 | 合格条件 |
|---:|---|---|
| 1 | CLI Help | Errorなしで表示 |
| 2 | Environment Verification | Dependency／Metal Validation Pass |
| 3 | `model-info` | Schema／Model／Metal／Hash／Default Policy一致 |
| 4 | Default日本語Streaming | 日本語、Streaming、Tracebackなし |
| 5 | Explicit English | 英語回答 |
| 6 | Auto | Prompt指定に従う |
| 7 | Non-streaming | まとめて表示、Errorなし |
| 8 | Thinking Hidden | Reasoning／Canonical Tag漏洩なし |
| 9 | Thinking Visible Default | `高度推論` Label、Canonical Tagなし |
| 10 | Thinking Custom Label | Custom Label使用 |
| 11 | Ctrl+C Cancel | Cooperative Cancel、Tracebackなし |
| 12 | Default Pytest | Failed／Error 0 |
| 13 | Native Model／Metal Test | 2 Test Pass |

回答内容の完全一致ではなく、各Sectionの構造的な合格条件で判定する。

## 23. User Test Pass Declaration

全項目が合格した場合、ユーザーは設計者役へ次の趣旨を明示する。

```text
phase_1_macos_user_manual_20260719171836.mdの
Phase 1ユーザー受入テストは、全項目合格です。
```

一部未実施または失敗がある場合は、合格宣言を行わず、項目番号、Command、表示されたSafe Errorを共有する。Secret、Model Raw Reasoning、不要なAbsolute Pathは貼らなくてよい。

## 24. Backupとの関係

Phase 1 Backupは、次の両方が成立した後に実行可能となる。

1. ユーザーによる本Manualの受入テスト全項目合格宣言
2. 設計者役によるPhase 1完了・Phase 2移行可能宣言

本Manualの作成またはTest実行だけではBackupを開始しない。

両宣言後、Backup前に実装状態が変わった場合は、影響範囲に応じて再テストまたは再Reviewを行う。
