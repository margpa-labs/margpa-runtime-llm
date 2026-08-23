# Phase 6 Fifth Rework — Recovery Entry（Package B: 実Model Call直前）

```yaml
document_id: phase_6_fifth_rework_package_b_pre_model_run
status: recovery_entry
phase: phase_6
package: package_b
role: Claude側設計統括者役
created_at: 2026-08-23 20:42:26 JST
governing_handoff: phase_6_codex_fifth_independent_review_rework_handoff_ja_20260823183203.md
previous_entry: phase_6_fifth_rework_package_a_runtime_switch_integrity_ja_20260823202658.md
```

## Current Package／Work Unit

Package B（DeepSeek Multi-turn Chat Template Compatibility、対象P6-CODEX-037）。
根本原因診断とSource修正が完了し、これから実DeepSeek ModelでのMulti-turn Matrix
検証に入る直前。Handoff §5「長時間の実Model Callへ入る直前にRecovery Indexを
作成する」の定めに従い、本Entryを実Model Call前に作成する。

## 診断結果（本Fifth Rework Session内で再確認・確定）

```text
対象GGUF: models/main/deepseek-r1-0528-qwen3-8b/gguf/
  DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf
  （sha512=b32af428...、Package A Recovery Entryと同一、未変更）

vocab_only=True Read-only Metadata Loadで本Session内に新規実測：
  eos_token_id = model.token_eos() = 151645
  bos_token_id = model.token_bos() = 151643
  model.detokenize([151645], special=True)
    = b'<\xef\xbd\x9cend of sentence\xef\xbd\x9c>'
    = "<｜end of sentence｜>"（通常の半角space区切り）
  この正準bytesをそのままtokenize(..., special=True)へ戻すと
    → [151645]（Clean Round-trip、Tokenizer自体は正常）

Embedded Jinja Chat Template（tokenizer.chat_template）を全文取得し確認：
  Assistant Turn終端をTemplateが挿入する箇所は
    {{content + '<｜end▁of▁sentence｜>'}}
  という「▁（U+2581, LOWER ONE EIGHTH BLOCK）区切りのliteral文字列」の
  ハードコードであり、{{ eos_token }}という Jinja変数を経由していない
  （{{ bos_token }}はPromptの先頭で変数として正しく使われている——
  これに対しAssistant Turn終端のみliteral化されている非対称な実装）。

  このliteral（▁区切り）をTokenizer自体でtokenize(..., special=True)した
  結果を本Session内で新規実測：
    "<｜end▁of▁sentence｜>".encode("utf-8")
      → tokenize結果 = [27, 130957, 408, 10417, 223, 1055, 10417, 223,
                         51889, 130957, 29]
    （151645という単一Special Tokenへは収束せず、11個の通常Sub-word
      Tokenへ分解される——Fourth Rework時点の診断と同じ結果を、今回は
      「Tokenizer由来の正準bytes」との対比込みで確定的に再現・確認）

確定した根本原因:
  Embedded Chat TemplateがAssistant Turn終端に挿入するliteral文字列
  （▁区切り）が、そのGGUF自身のTokenizerが持つEOS Special Token（151645）
  の正準byte表現（半角space区切り）とbyte単位で一致しない。このため
  Multi-turn Promptを構築する際、過去のAssistant Turnの終端が「本物の
  EOS Special Token」ではなく「通常の11個のSub-word Token列」として
  Prompt中に埋め込まれる。Modelはこれを実際のTurn境界ではなく通常の
  可視Textとして認識するため、会話構造の誤読（Turn混同・トピック取り
  違え）と、生成側での同種literalの再生成（可視Special-Token状Textの
  Leakage）の両方を同一の原因から説明できる。

  Qwen固有前提の誤流用ではない: BOS/EOSは{{ bos_token }}/{{ eos_token }}
  という汎用Jinja変数経由であるべきところ、"このGGUF固有のTemplateが"
  Assistant Turn終端のみliteralにハードコードしている、という当該
  Templateそのものの実装事実に基づく診断。
```

## 採用したFix Recipe（実装済み、Source Mutation）

```text
対象File: src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
  chat_template.py（Allowed Mutation Envelope内）

1. _build_prompt_normalization(eos_token) を新設。
   eos_token（Tokenizer自身のdetokenize()由来の正準文字列）に半角space
   が含まれる場合のみ、それを▁へ置換したvariantを計算し、variantが
   eos_tokenと異なる場合にのみ (variant, eos_token) という置換Pairを
   返す——Modelに依存しない汎用条件（Qwen等、Templateが{{ eos_token }}
   を正しく使うModelではvariantがそもそもPrompt中に出現しないため
   no-op）。

2. _normalize_rendered_prompt(prompt) を新設。Jinja Formatterが
   Render した直後のPrompt Text上で、上記置換Pairを適用する。

3. format_prompt() と create_chat_completion() の両方で、
   Formatter Render直後・Tokenize直前にこの正規化を挿入。

4. create_chat_completion()を、Main／Background両方の呼び出しについて
   Llama.create_completion()への手動呼び出しへ統一。従来Main専用だった
   Jinja2ChatFormatter.to_chat_handler()の不透明Bridge（self._handler）
   を削除——このBridgeは自分でPromptをRender／Tokenizeする内部Closure
   を持ち、正規化を差し込む介入点が無かったため。
   Background専用だった_create_cancellable_chat_completion()の実装を
   吸収し、単一実装へ統合（Duplicate Code除去も兼ねる）。
   stream=True時はraw completion chunk（choices[0]["text"]）を
   _stream_completion_as_chat_deltas()でOpenAI-chat delta shape
   （choices[0]["delta"]["content"]）へ再整形——既存Consumer
   （LlamaCppGenerationStream、stream.py:81-84）が要求するShapeを
   維持するため（Main-path streamはcancellation常にNoneであり、
   Background-path streamはsrcのCall Graph上どこからも呼ばれていない
   ことを事前にAgent Researchで確認済み——Shape回帰リスクなし）。

事前確認（Agent Researchによる、Source Codeへの機械的Grep結果）:
  create_chat_completion()のCall Siteはadapter.py内2箇所のみ
  （generate(): stream=False+cancellation可変、stream():
  stream=True+cancellation常にNone）。stream=True かつ
  cancellation not None の組み合わせはsrc全体のCall Graph上
  存在しない（Dead Path）——今回のReshape追加はMain-path streamの
  みが実際に通る経路であり、Shape不一致リスクは無い。
```

## 実施済みVerification（実Model Call前）

```text
1. python3 -m mypy src/margpa_runtime_llm/adapters/model_backends/
   llama_cpp/chat_template.py
   → Success: no issues found in 1 source file（Exit 0）

2. python3 -m ruff format --diff <file>; ruff check <file>
   → 1 file already formatted／All checks passed（Exit 0）

3. python3 -m pytest tests/ -q --ignore=tests/integration/llama_cpp \
     --ignore=tests/integration/test_real_local_judge_smoke.py \
     --ignore=tests/integration/test_runtime_model_control_smoke.py
   → 1556 passed, 1 deselected（Exit 0、Package A完了時点と同数——
     本Package Bの変更によるUnit/Integration回帰なし）

4. python3 -m pytest tests/integration/llama_cpp/test_phase1b_runtime.py \
     -q -m model_smoke（実Qwen Model使用）
   → 1 failed（AssertionError: STATUS event count 3 != 1）
     ただしこのFailureはP6-CODEX-039既知・Package C対応スコープの
     「STATUS Vocabulary変更に対しTestのAssertionが陳腐化している」
     既知不具合であり、本Package Bの変更に起因しない。このTest内で
     本Fix対象のchat_template.py経由コード（generate/stream/thinking
     mode ENABLED・HIDDEN・VISIBLE・custom Presentation/MODEL_BUSY
     即時Rejection/cancel()冪等性/State遷移LOADED→GENERATING→LOADED/
     Post-cancel generate成功/ConversationGenerationService.start()の
     START Event単一発火）は、Failure箇所より前で全てPASSしており、
     実QwenでのMain generate()／stream()両経路が本Refactorで正常に
     機能することを実Modelで確認済み。
```

## Open Findings（Severity／Current Impact）

```text
P6-CODEX-037 実装完了・実DeepSeek Multi-turn Matrix検証待ち（本Entry
  後、直ちに実施）
P6-CODEX-038 CRITICAL PATH SAFETY／REQUIRED（Package Cで対応）
P6-CODEX-039 CRITICAL EVIDENCE／REQUIRED（実Qwen Test Failure部分は
  Package C、Acceptance再導出はPackage D）
P6-CODEX-040/P6-GOV-007 CRITICAL GOVERNANCE EVIDENCE／REQUIRED
  （Package Dで対応）
```

## Exact changed files（Package B、本Entry時点）

```text
Modified:
  src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py
    （_build_prompt_normalization／_normalize_rendered_prompt新設、
    create_chat_completion()をManual create_completion()呼び出しへ統一、
    _create_cancellable_chat_completion()を吸収・削除、
    _stream_completion_as_chat_deltas()新設、self._handler削除）

Deleted: なし
New: なし
Model Definition TOML（config/models/deepseek_r1_0528_qwen3_8b_q4_k_m.toml）:
  再確認したが実測値の誤りは無く、修正不要と判断（architecture／
  native_context_limit／required_features等、Fourth Rework時点の
  実測値と現在のGGUF Metadataとの間に差異なし）
```

## Active Process／Model Load／Scratch State

```text
Active Process: margpa_runtime_llm.entrypoints系のProcessは0件。
Model Load State: 上記4のtest_phase1b_runtime.py実行中に実Qwenの
  Load／Generate／Stream／Cancel／Unloadが発生したが、Test完了と
  同時にProcess終了・Unload済み（Test Fixture管理下）。本Entry
  作成時点で永続Process・永続Load Stateは無い。
DeepSeek実Load: 本Entリ作成時点でまだ実施していない
  （vocab_only=True Metadata Loadのみ、実Verification済み）。
Scratch State: `.venv/.t/phase_6_fifth_rework_<timestamp>/`配下の
  新規作成はまだ発生していない。
```

## User runtime_data Contact Count

0。

## Root-outside／Git／Network／Provider Memory Action Count

0（Package B自身での新規発生なし）。

## Artifact／Snapshot／DigestのCurrent State

```text
Qwen Artifact: main.qwen3-4b-q4-k-m（未変更、実Load/Unloadのみ発生）
DeepSeek Artifact: main.deepseek-r1-0528-qwen3-8b-q4-k-m、
  sha512=b32af428...（未変更、vocab_only=True Read-only Metadata
  Loadのみ、Write/Delete/Move/Rename/Permission変更なし）
config/models/*.tomlは未変更。
```

## Exact Next Action

これから実DeepSeekをRuntime Loadし、Handoff §5要求のMulti-turn Matrix
を実施する:

```text
1. DeepSeek-native 2ターン以上の会話（1ターン目回答後、2ターン目で
   1ターン目の内容と無関係の話題を質問し、正しく2ターン目の質問に
   回答すること、および可視Special-Token Leakageが無いことを確認）
2. Qwenで開始した会話をDeepSeekで継続
3. DeepSeekで開始した会話をQwenで継続
4. Retry／Regenerate／Branch-Select後の継続
5. Thinking OFF／利用可能なModeでの動作
6. RAG／Tool Role Messageが関与する経路（該当する場合）
上記全てでZero可視Special-Token Leakage、Zero Turn混同、
Zero Assistant/User境界崩壊を確認する。
```

## Exact Resume Command／Resume手順

```text
1. 本Entryおよび phase_6_fifth_rework_package_a_runtime_switch_
   integrity_ja_20260823202658.md を読む。
2. `git status --porcelain`で本Entry作成時点からの増分Diffを確認する
   （src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
   chat_template.py 以外に予期しない変更が無いことを確認）。
3. 上記「Exact Next Action」のMulti-turn Matrixを実DeepSeekで実行する。
4. 全項目Pass後、Package B完了Recovery Entry
   （phase_6_fifth_rework_package_b_deepseek_multiturn_*_ja_
   <timestamp>.md）を作成し、Package Cへ進む。
```
