# Phase 6 Fifth Rework — Recovery Entry（Package B: DeepSeek Multi-turn 完了）

```yaml
document_id: phase_6_fifth_rework_package_b_deepseek_multiturn
status: recovery_entry
phase: phase_6
package: package_b
role: Claude側設計統括者役
created_at: 2026-08-23 20:57:24 JST
governing_handoff: phase_6_codex_fifth_independent_review_rework_handoff_ja_20260823183203.md
previous_entry: phase_6_fifth_rework_package_b_pre_model_run_ja_20260823204226.md
```

## Current Package／Work Unit

Package B（DeepSeek Multi-turn Chat Template Compatibility、対象P6-CODEX-037）完了。
Package Cへ進む直前。

## Last Completed Action

実DeepSeek（sha512=b32af428...）と実Qwen（sha512=f182f1d4...）を用いた
Multi-turn Matrix（tests/integration/llama_cpp/test_deepseek_multiturn.py::
test_deepseek_multiturn_chat_template_compatibility、`-m model_smoke`）を
実行し、1 passed（66.04s）を確認。直後にFull Backend Test（`tests/`全体、
real-hardware Marker除く）を再実行し、1556 passed, 1 deselected（Package A
完了時点と同数、回帰なし）を確認。

## Completed Findings

```text
P6-CODEX-037 CLOSED — DeepSeek GGUF（DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-
  from-Q8_0.gguf）のEmbedded Jinja Chat Templateが、Assistant Turn終端に
  '<｜end▁of▁sentence｜>'（U+2581 '▁'区切り）というliteral文字列を
  {{ eos_token }}変数を経由せずハードコードしており、この文字列がこの
  GGUF自身のTokenizerが持つEOS Special Token（151645）の正準byte表現
  （'<｜end of sentence｜>'、半角space区切り、model.detokenize()由来）と
  byte単位で一致しないことを、本Fifth Rework Session内でtokenize/
  detokenize実測により再確認・確定した（Fourth Rework時点の診断は
  手打ちの比較対象文字列を用いており、今回はTokenizer自身の正準bytesとの
  対比で再現・確定させた点が異なる）。

  Fix: src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
  chat_template.pyに_build_prompt_normalization()／
  _normalize_rendered_prompt()を新設し、Jinja Formatter Render直後・
  Tokenize直前でこの不一致を正規化。あわせてcreate_chat_completion()を
  Llama.create_completion()への手動呼び出しへ統一し
  （Jinja2ChatFormatter.to_chat_handler()の不透明Bridge`self._handler`を
  削除）、Main／Background両方の呼び出し経路に正規化を一様に適用した
  （Bridgeは自前でPromptをRender／Tokenizeする内部Closureを持ち、
  正規化の介入点が無かったため）。stream=True時はraw completion chunkを
  _stream_completion_as_chat_deltas()でOpenAI-chat delta shapeへ再整形し、
  既存Consumer（LlamaCppGenerationStream）とのShape互換を維持。

  Model-agnostic設計: _build_prompt_normalization()はeos_tokenに半角space
  が含まれ、かつ▁置換Variantがeos_token自体と異なる場合にのみ置換Pairを
  生成する——Qwen等、Templateが{{ eos_token }}を正しく変数参照するModelでは
  Variantがそもそも出現しないためno-op。DeepSeek固有のIf分岐やHardcodeは
  Adapter Codeに追加していない。

  実測Verification（本Session内、実Artifact）:
    1. vocab_only=True Metadata Loadで
       tokenize("<｜end▁of▁sentence｜>") = [27,130957,408,10417,223,1055,
       10417,223,51889,130957,29]（11 Sub-word Token、151645へ非収束）を
       再確認。
    2. 実DeepSeek＋実QwenでのMulti-turn Matrix（後述）を実行し、
       Zero可視Special-Token Leakage／Zero Turn混同／正しいUnrelated-topic
       Follow-up回答を確認。
```

## 実施した Multi-turn Matrix（Handoff §5要求、全項目Pass）

```text
1. DeepSeek-native 2ターン: 「日本の首都は？」→「東京」を含む回答、
   続けて「フランスの首都は？」→「パリ」を含み「東京」を含まない回答
   （Turn混同なし）。
2. Qwenで開始した会話をDeepSeekで継続: 実Qwenが生成した「日本の首都は
   東京です。」をAssistant Turnとして履歴に含め、DeepSeekで「フランスの
   首都は？」を継続 → 「パリ」を含む正しい回答。
3. DeepSeekで開始した会話をQwenで継続: 実DeepSeekが生成したTurn 1を
   Assistant Turnとして履歴に含め、Qwenで「フランスの首都は？」を継続
   → 「パリ」を含む正しい回答。
4. Retry／Regenerate相当: 同一履歴に対し、最終User発話の言い回しを変えて
   再生成 → 「パリ」を含む正しい回答。
5. Thinking ENABLED→DISABLED継続: 「1+1は？」をThinking ENABLEDで実行後、
   その回答を履歴に含め「では2+2は？」をThinking DISABLEDで継続 →
   「4」を含む正しい回答。
6. RAG／Tool Role Message経路: ConversationRoleはUSER／ASSISTANTのみで
   Tool Roleは存在せず（このCodebaseがChat-format Tool/Function Callを
   一切発行しないことは既存Docstringで確認済み）、DocumentationRagMode
   もPromptへ追加Contextを注入する形でしかMessage構造に影響しない
   ——本Fix（Turn境界のEOS表現）はRAG有無に依存しない箇所であるため、
   このItemはNOT_APPLICABLE（該当Role自体が存在しない）と判断した。

全項目で_run_turn()ヘルパーが可視Special-Token Marker
（'<｜end▁of▁sentence｜>'／'<｜end of sentence｜>'／'<｜User｜>'／
'<｜Assistant｜>'）の不在をAssertし、Zero Leakageを確認。
```

## テスト設計上の判明事項（Bugではなく、既存の意図された挙動）

```text
ConversationGenerationInput.settings.max_new_tokens（Turn単位の要求値）は
conversation_generation.py:1640の
`effective_max_new_tokens = min(value.settings.max_new_tokens,
runtime_snapshot.generation_defaults.max_new_tokens)`
により、build_phase1_application()呼び出し時の
generation_overrides["max_new_tokens"]（RuntimeModelController.
current_max_new_tokens由来）でClampされる——意図されたCeiling機構
（P6-CODEX-035のClamp設計と同じ思想）であり、Bugではない。
Test作成時にこれを見落とし、generation_overrides側を48のままTurn単位で
1024/2048を要求してもClampされ続け「finish_reason=length、
completion_tokens=48で空Content」という誤ったFailureを一時的に得た
（chat_template.py側の問題ではないことをStandalone Debug Scriptで切り分け
確認済み）。generation_overrides["max_new_tokens"]をTest内の最大Turn要求値
（2048、ConversationSettingsの検証上限MAX_WEB_NEW_TOKENSと同じ）に合わせて
修正し解消。

DeepSeek-R1蒸留系ModelはSoft-switch（'/no_think'をUser発話へ追記する方式、
DeepSeekのTemplateにはenable_thinkingによるHard-switchが存在しないため）
に対しても'<think>'ブロックを生成し続け、しかもUser発話中の'/no_think'
という注記自体について言及・考察する形で却って長いReasoningを行う実測
挙動を確認した——DeepSeek固有のModel挙動であり、本Fixの対象範囲外。
```

## Exact changed files（Package B、本Package全体での変更分）

```text
Modified:
  src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py

New:
  tests/integration/llama_cpp/test_deepseek_multiturn.py
    （P6-CODEX-037の実Model Regression Test。model_smoke Marker付き、
    macOS arm64限定。Qwen→DeepSeek→Qwenの順で3回Sequential Loadし、
    上記Multi-turn Matrixの6項目のうち5項目を実行・Assert、1項目を
    NOT_APPLICABLEとして明記。）

Deleted: なし
Model Definition TOML: 変更なし（Package B Pre-model-run Entryで既に
  再確認済み、実測値の誤りなし）
```

## Executed Commands／Exit Codes／Test Counts（Package B、本Entry時点までの累計）

```text
python3 -m mypy src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
  chat_template.py tests/integration/llama_cpp/test_deepseek_multiturn.py
  → Success: no issues found（Exit 0、複数回）

python3 -m ruff format --diff <files>; ruff check <files>
  → All checks passed（Exit 0、複数回）

python3 -m pytest tests/ -q --ignore=tests/integration/llama_cpp \
  --ignore=tests/integration/test_real_local_judge_smoke.py \
  --ignore=tests/integration/test_runtime_model_control_smoke.py
  → 1556 passed, 1 deselected（Exit 0、Package A完了時点と同数、
  本Package Bの変更による回帰なし）

python3 -m pytest tests/integration/llama_cpp/test_phase1b_runtime.py \
  -q -m model_smoke（実Qwen、Package B Pre-model-run Entryで実施済み）
  → 1 failed（P6-CODEX-039既知・Package Cスコープの陳腐化Assertion、
  本Fixとは無関係——Failure箇所より前の全Assertion、Main generate/
  stream/thinking/MODEL_BUSY/State遷移/Post-cancel/Conversation START
  Eventは全てPASS）

python3 -m pytest tests/integration/llama_cpp/test_deepseek_multiturn.py \
  -q -m model_smoke -s（実DeepSeek＋実Qwen）
  → 1 passed（66.04s、Exit 0）
```

## Active Process／Model Load／Scratch State

```text
Active Process: margpa_runtime_llm.entrypoints系のProcessは0件。
Model Load State: 実Qwen／実DeepSeekともにTest Fixture管理下でLoad／
  Unloadが発生したが、Test完了と同時に全てUnload済み。本Entry作成時点で
  永続Process・永続Load Stateは無い。
Scratch State: `.venv/.t/phase_6_fifth_rework_20260823204226/`配下に
  診断用のDebug Script 3本（debug_deepseek_turn1.py／
  debug_deepseek_conversation.py／debug_deepseek_after_qwen.py）を作成し、
  診断完了後に本Entry作成前にディレクトリごと削除済み（Project-local
  Scratch外への影響なし、削除もProject Root内で完結）。
```

## User runtime_data Contact Count

0。

## Root-outside／Git／Network／Provider Memory Action Count

0（Package B全体での新規発生なし）。

## Artifact／Snapshot／DigestのCurrent State

```text
Qwen Artifact: main.qwen3-4b-q4-k-m、sha512=f182f1d4...（未変更、
  実Load/Unloadのみ発生）
DeepSeek Artifact: main.deepseek-r1-0528-qwen3-8b-q4-k-m、
  sha512=b32af428...（未変更、vocab_only=True Read-only Metadata Load
  および許可されたExact Model Read/Load Exception範囲内の実Inference
  Loadのみ、Write/Delete/Move/Rename/Permission変更/再量子化なし）
config/models/*.tomlは未変更。
```

## Open Findings（Severity／Current Impact）

```text
P6-CODEX-038 CRITICAL PATH SAFETY／REQUIRED — Recording Path TOCTOU残存
  （Package Cで対応）
P6-CODEX-039 CRITICAL EVIDENCE／REQUIRED — 実Qwen Test Failure部分は
  Package C、Acceptance再導出はPackage Dで対応
P6-CODEX-040/P6-GOV-007 CRITICAL GOVERNANCE EVIDENCE／REQUIRED
  （Package Dで対応）
```

## Exact Next Action

Package C（Recording Atomic Path／Regression Repair、対象P6-CODEX-038＋
P6-CODEX-039の実Qwen Test Failure部分）を開始する:

```text
1. src/margpa_runtime_llm/adapters/runtime_observability/
   local_filesystem_recording_writer.py を読み、現在のTOCTOU残存箇所
   （Lexical Path経由のCheck-then-Open、dir_fd／openat／O_NOFOLLOW未使用）
   を特定する。
2. Authorized Root～Base Directoryまでの経路をdir_fd Chainで固定し、
   Lock／Temp／Target／Quota-Scan／Rename-Replace／Directory-fsyncを
   すべて同一の検証済みDirectory FDへ束縛する設計へ修正する。
   Symlink／Hardlink／Non-regular／Owner-Mode不一致はFail-closed。
3. Deterministic Fault Injection Test（Intermediate-swap-after-check、
   internal/external Symlink、Lock/Target Hardlink、multi-process Quota
   Race、Short Write、Replace/fsync failure）をProject-local Scratch
   （.venv/.t/phase_6_fifth_rework_<timestamp>/）のみを用いて追加する。
4. tests/integration/llama_cpp/test_phase1b_runtime.py::
   test_phase1b_production_runtime_load_generate_stream_cancel_and_unload
   のSTATUS Event Count Assertion（現在の実測値3、Assertionは1を期待）を
   現在のSTATUS Vocabularyに基づいて修正し、実Qwenで実際にPASSさせる
   （Exclude/Markではなく、正しいAssertionへの修正）。
5. 完了後、Package C完了Recovery Entryを作成し、Package Dへ進む。
```

## Exact Resume Command／Resume手順

```text
1. 本Entry、phase_6_fifth_rework_package_b_pre_model_run_ja_20260823204226.md、
   phase_6_fifth_rework_package_a_runtime_switch_integrity_ja_20260823202658.md
   を読む。
2. `git status --porcelain`で本Entry作成時点からの増分Diffを確認する
   （chat_template.py修正＋test_deepseek_multiturn.py新設以外に予期しない
   変更が無いことを確認）。
3. 上記「Exact Next Action」からPackage Cを開始する。
```
