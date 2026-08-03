# Response Language／Thinking Output Policy設計整理

- 文書ID: `response_language_and_thinking_output_policy`
- 状態: `proposed_deferred`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- 作成担当: 設計者役担当Task
- 対象: Response Language、Thinking Mode、Thinking表示、Output Parser、将来Governance
- 正本言語: 日本語
- Phase 1-B Review: [designer_review_phase_1b_model_runtime_final_20260719001604.md](../handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
- Governance: [runtime_governance_20260718174637.md](../governance/runtime_governance_20260718174637.md)
- supersedes: なし（新規設計整理系列）

## 1. 文書の位置づけ

本書は、Qwen3-4B Phase 1 CLIのユーザー動作確認で観測されたResponse Language、Thinking出力およびScope Driftを整理し、後続実装の設計候補を定義する。

本書はPhase 1-C Deployment Hookの実装Scopeではない。

Response／Presentation Policyを実装する際は、別のAccepted ADRと実装許可を必要とする。

## 2. 観測された事実

### 2.1 日本語指定なし

概念的な実行：

```bash
./.venv/bin/margpa-llm generate \
  --prompt "小型LLMを交換可能にする設計を考えてください。" \
  --max-new-tokens 256 \
  --thinking
```

観測：

- 出力が英語になった
- `--thinking`は有効だった
- 回答言語は明示していなかった

### 2.2 日本語を明示

概念的な実行：

```bash
./.venv/bin/margpa-llm generate \
  --prompt "小型LLMを交換可能にする設計を考えてください。日本語で。" \
  --max-new-tokens 256 \
  --thinking
```

観測：

- 出力が日本語になった

### 2.3 Output Budgetを拡張

`max_new_tokens=2048`とし、日本語を明示した実行では、`<think>...</think>`と最終回答の両方が日本語で完了した。

ただし内容は、Software上のModel Adapter／交換可能Architectureではなく、物理的なModel Slot、PCIe、USB-C、GPU Board等へ逸脱した。

## 3. 原因評価

「低スペックモデルだから」だけでは説明できない。

### 3.1 Model Capacity／Quantization

Qwen3-4B Q4_K_Mは小型・量子化Modelであり、次の能力が大型Modelより不安定になり得る。

- 曖昧な語の意味選択
- 長いInstructionの保持
- Scope維持
- Self Correction
- 日本語での技術的精度

これは一因である。

### 3.2 Project Context不足

Phase 1 CLIは一問一答であり、質問にはMARGPA Runtime LLMのProject Context、Model Port、AdapterまたはSoftware Architectureという前提が含まれていなかった。

Modelは「交換可能」を物理交換として解釈した。

### 3.3 Inputの曖昧性

「小型LLMを交換可能にする設計」は、少なくとも次に解釈できる。

- Software RuntimeでModel File／Backendを交換する
- Hardware Moduleとして物理交換する
- Remote Model Endpointを切り替える
- TaskごとにRouterでModelを選択する

前提を固定しないままThinkingを開始した。

### 3.4 Thinkingは正しさを保証しない

Thinking Modeは、最初の解釈を必ず訂正する機能ではない。

誤った前提から開始すると、誤った前提を長く具体化する可能性がある。

```text
誤解
  ↓
長いThinking
  ↓
詳細だがScope外の回答
```

### 3.5 Language指定不足

現行CLIの`--thinking`はQwen3のThinking Controlだけを変更し、Response Languageを指定しない。

日本語入力だけで出力言語が必ず日本語になるContractは存在しない。

### 3.6 Output Budget

Thinking Modeでは、ThinkingとFinal Answerが同じ`max_new_tokens`を消費する。

256 TokensではThinkingだけでBudgetを使い、Final Answerへ十分到達しない可能性がある。

2048 TokensではThinkingとFinal Answerの両方が完了した。

### 3.7 Sampling Profile

Current Profile：

```text
temperature = 0.7
top_p       = 0.8
top_k       = 20
min_p       = 0
```

これはQwen公式のNon-Thinking推奨値に対応する。

Qwen3 Thinking Mode候補：

```text
temperature      = 0.6
top_p            = 0.95
top_k            = 20
min_p            = 0
presence_penalty = 1.5
```

Sampling差は英語化の直接原因とは断定できないが、Thinking ModeとGeneration Profileを将来連動させる余地がある。

## 4. Governance上の分類

今回の日本語2048 Tokens出力は、Governance検証Sampleとして価値がある。

候補Deviation：

- Input Interpretation Error
- Premise Definition Failure
- Scope Drift
- Unsupported Assumption
- Reasoning Integrity Degradation
- Irrelevant Elaboration
- Thinking Lengthと品質の混同

ARGD／DAGD候補Dimension：

- Input Interpretation／Premise
- Premise Preservation
- Scope Definition
- Reasoning Integrity
- Context Preservation
- Dialog Efficiency
- Self Repair

将来、元出力を匿名化可能なSampleとして保存する場合は、ユーザーの明示許可とAudit／Sample Log規則を必要とする。本書には全文を複製しない。

## 5. 分離すべき3設定

```text
Thinkingを実行するか
Thinkingを利用者へ表示するか
回答言語を何にするか
```

これらを同一FlagまたはModel Adapterの暗黙挙動にしない。

## 6. Response Language Policy候補

### Config

```toml
[response]
language = "ja"  # ja／en／auto
```

初期候補：

```text
Default : ja
Allowed : ja／en／auto
```

将来はBCP 47相当のLanguage Keyへ拡張可能にする。

### Precedence

```text
UserがRequest内で明示した言語
  > Per-request CLI／API Override
  > Session／User Preference
  > Deployment Default
  > auto
```

### Injection Boundary

Language PolicyはApplication／Prompt Policy層でSystem InstructionへCompileする。

llama.cpp Adapterへ日本語をハードコードしない。

ユーザーが`--system`を指定した場合、Language Policyを黙って破棄せず、System Message Composition規則で合成する。

## 7. Thinking Policy候補

### Generation

既存：

```toml
[generation]
thinking_mode = "disabled"  # enabled／disabled／model_default
```

### Presentation

```toml
[presentation.thinking]
visibility = "hidden"       # visible／hidden
display_label = "推論"
```

将来候補：

```text
summary
debug_only
developer_only
```

`summary`は生Thinkingの単純表示ではなく、高水準の説明概要を生成・表示する別機能として扱う。

## 8. Model Protocolと表示の分離

Qwen3が使用するCanonical Protocol：

```text
<think>
...
</think>
```

Canonical TagをModel入力／出力Protocol上で任意名へ変更しない。

代わりに、Model固有Parserで次へ正規化する。

```text
reasoning_content
final_content
source_format
parse_warnings
```

Presentation層で表示を変更する。

```text
Canonical  : <think>...</think>
Display例  : <推論>...</推論>
Display例  : 【思考過程】...
Hidden     : final_contentだけ表示
```

使用者が変更するのは`display_label`であり、Model Protocol ParserのDelimiterではない。

## 9. Streaming Parser要件候補

Streamingでは`<think>`または`</think>`がChunk境界で分割され得る。

単純なChunk単位Regex削除だけで実装しない。

状態候補：

```text
before_reasoning
inside_reasoning
after_reasoning
malformed
```

Hidden Modeでは、Thinking ChunkがUIへ一瞬漏れてから消える挙動を禁止する。

Malformed Tag時のFallbackとWarningを明示する。

## 10. Audit／Privacy

既存方針を維持する。

- 生のChain of Thoughtを原則Audit Logへ保存しない
- System Trace由来の事実とModel Generated Explanationを分ける
- 高水準のProcess Summaryを使用する
- UI表示可否とAudit保存可否を同じ設定にしない
- Debug表示を有効にしても自動保存を意味しない

候補設定：

```text
thinking_visibility
thinking_persistence
high_level_explanation
```

を分離する。

## 11. CLI候補

```text
--response-language ja
--response-language en
--response-language auto
--thinking
--no-thinking
--show-thinking
--hide-thinking
--thinking-label "推論"
```

CLIはProfile Defaultを上書きするが、Model Adapter固有Flagを直接公開しない。

## 12. Initial Candidate Defaults

```text
Response Language    : ja
Thinking Mode        : disabled
Thinking Visibility  : hidden
Thinking Label       : 推論
Thinking Persistence : disabled
High-Level Summary   : 将来
```

これは設計候補であり、Accepted ADRではない。

## 13. Implementation Boundary

候補処理：

```text
User／Session／Profile
  ↓
Response Policy Resolver
  ↓
System Message Composer
  ↓
Model Port
  ↓
Model-specific Output Parser
  ↓
Normalized Response
  ↓
Presentation Policy
  ↓
CLI／Web UI／API
```

Adapterの責務：Model Protocolの正規化。

Applicationの責務：Language Policyと表示Policyの決定。

Entrypointの責務：CLI／UI形式への描画。

## 14. 非目標

- Thinkingを正解保証機能として扱わない
- Thinkingが長いほど高品質と評価しない
- 生ThinkingをRuntime Governance Scoreの唯一根拠にしない
- 表示ラベル変更のためにModel Chat Templateを改変しない
- Default日本語をModel Adapterへ埋め込まない
- Raw CoT保存を既定にしない

## 15. 次のDecision Gate

本機能を実装する前に、少なくとも次を決める。

1. `ja／en／auto`の正式Contract
2. Defaultを`ja`とするAccepted ADR
3. Explicit User LanguageとProfile Defaultの優先順位
4. Thinking ParserをどのModuleに置くか
5. Streaming HiddenのMalformed Policy
6. Raw ThinkingをResult Contractへ含めるか、非公開内部値にするか
7. CLIと将来Web UIで同じPresentation Contractを使うか
8. Thinking用Sampling Profileの自動切替有無
9. Test Fixtureとして今回のScope Driftをどう匿名化・保存するか

## 16. 外部参照

- Qwen3-4B-GGUF Model Card: https://huggingface.co/Qwen/Qwen3-4B-GGUF
- Qwen3-4B Model Card: https://huggingface.co/Qwen/Qwen3-4B

