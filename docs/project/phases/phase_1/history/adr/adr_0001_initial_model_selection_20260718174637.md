# ADR 0001 初期Model構成の選定

- 文書ID: `adr_0001_initial_model_selection`
- 状態: `accepted`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 正本言語: 日本語
- 関連文書: [model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)

## Context

初期実行環境はApple M2 Pro・16GBであり、OS、Model、KV Cache、UI、Audit、将来のRAG等がUnified Memoryを共有する。

プロジェクトの最優先事項は、最高品質の回答ではなく、Model交換可能なRuntime Governance型LLMの全体骨格を成立させることである。

検討対象にはDeepSeek、Llama、Qwen、Mistral、SmolLM等があった。

Guardrailと将来のLLM-as-a-Judgeについても、Mainとは別RoleとしてHookを設ける必要がある。

## Decision

初期構成を次とする。

```text
Main:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf
  Q4_K_M

Guard:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
  Q8_0
  Phase 4

Judge:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
  Q5_K_M
  将来On-Demand
```

3Modelを常時同時Loadしない。

必要性が出た場合は、次の通常版へ交換可能にする。

```text
Qwen/Qwen3Guard-Gen-0.6B
AtlaAI/Selene-1-Mini-Llama-3.1-8B
```

## Reason

### Main Q4_K_M

- M2 Pro・16GBで扱いやすい
- 4B級として軽量
- 日本語と開発支援のBalance
- llama.cpp系で利用可能
- MVP全体骨格に適する

### Guard Q8_0

- Model自体が小さい
- Q4_K_Mとの差が小さい
- Classification品質を優先
- 低Bit量子化による境界劣化を抑える

### Judge Q5_K_M

- 常時利用しない
- Evaluation品質を速度より優先
- On-Demand実行を前提にMemoryを許容する

## Consequence

Positive：

- Initial Hardwareで実行可能性が高い
- Roleごとに適切なQuantizationを選べる
- Main、Guard、Judgeを独立して交換できる
- 将来のCloud移行で通常版や大型版へ変更できる

Negative／Risk：

- Qwen3-4Bの回答品質には上限がある
- Guard GGUFは第三者変換の検証が必要
- Seleneの日本語Judge性能は未保証
- Judge Load時にMainのUnloadが必要になる可能性
- ModelごとのPrompt／Parser差をAdapterで吸収する必要がある

## Validation

実装後に次を検証する。

- MainのToken速度とMemory
- Main＋Guardの同時Memory
- Guardの日本語分類
- Guard GGUFと通常版の差
- Judgeの日本語評価
- Load／Unload時間
- File HashとRevision
