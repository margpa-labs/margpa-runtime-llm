# Claude側設計統括者役 — 表現重視モード（Style限定Prompt Injection）実装

```yaml
document_id: claude_expressive_mode_style_only_prompt_injection_20260819124942
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
role: design_governor
created_at: 2026-08-19 12:49:42 JST
language: ja
```

## 1. 経緯

ユーザー要望：「Qwenの出力、推論そのものは変えずに、ノリ・テンション・草生やし（wwwなど）・顔文字・絵文字・アイコン・その他みたいな感じに出来る？ただし、元のQwenなのか改造Qwenなのかわかりずらくなるので、表現重視モードとして設定の普通の方に一緒につけておいてくれる？」

要件は2点：(1) 推論・結論・事実内容は変えず、表現（Tone）のみを変化させる、(2) Modelの素の挙動と区別できるよう、明示的なOpt-in Toggleとして「設定」の「基本（普通の）」Categoryへ追加する（Advanced Mode側ではない）。

## 2. 設計判断

既存の[claude_phase_2_e_i_i6_implementation_ja_20260819002250.md](claude_phase_2_e_i_i6_implementation_ja_20260819002250.md)等で確立済みの「Context使用率Prompt Injection」（`ContextUsagePromptInjectionMode`）と全く同じ設計Patternを踏襲した——専用Enum＋`ConversationSettings`Field（既定Disabled）→ `_build_request`内で条件付きにSYSTEM Roleの追加Message（`name`付き）を`messages`先頭付近へInsert、という構成。この既存Patternの再利用により、Web層（`PersistentTurnStreamRequest`等）は`ConversationSettings`を直接型として使っているため、追加のWeb Contract変更が不要だった。

Toggle既定値はDisabled——ONにしない限り、素のModel出力と完全に一致する（第1節の要件(2)を満たす）。Settingsの「基本」Category（`SettingsModal`の`category === "basic"`、`SettingsPanel`）へ配置し、「Advanced Mode」（Configuration Control）側には置いていない。

Style指示内容は、要求された6項目（ノリ・テンション・草生やし・顔文字・絵文字・アイコン・その他）を全て文言化し、「推論の正確性・結論・事実内容は、この指示が無い場合と全く同じ水準を保ってください」という明示的な制約を指示冒頭に置いた。

## 3. 実装内容

- [contracts.py](../../../../../src/margpa_runtime_llm/modules/conversation/contracts.py)：`ExpressiveMode`（`DISABLED`/`ENABLED`）Enumを新規追加。`ConversationSettings`へ`expressive_mode: ExpressiveMode = ExpressiveMode.DISABLED`を追加。
- [public.py](../../../../../src/margpa_runtime_llm/modules/conversation/public.py)：`ExpressiveMode`をExport。
- [conversation_generation.py](../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py)：`EXPRESSIVE_STYLE_NOTICE_MESSAGE_NAME`定数と`_inject_expressive_style_notice`（`@staticmethod`）を新規追加。`_build_request`内、`_inject_documentation_reference`の直後・`_inject_context_usage_notice`の前に、`expressive_mode is ExpressiveMode.ENABLED`のとき条件付きで適用。
- [types.ts](../../../../../frontend/src/types.ts)：`GenerationSettings`へ`expressive_mode: "enabled" | "disabled"`を追加。
- [SettingsPanel.tsx](../../../../../frontend/src/components/SettingsPanel.tsx)：`SettingsFormState`へ`expressiveMode: boolean`を追加。既存の`show-context-usage`Toggleの直後に、新規Switch-row（`id="expressive-mode"`）＋開示Note（`id="expressive-mode-note"`）を追加。
- [App.tsx](../../../../../frontend/src/App.tsx)：`settingsForm`初期値へ`expressiveMode: false`、`settingsPayload()`で`expressive_mode: settingsForm.expressiveMode ? "enabled" : "disabled"`へMapping。
- [translations.ts](../../../../../frontend/src/i18n/translations.ts)：JA/EN双方へ`expressiveModeLabel`・`expressiveModeNote`を追加。Note文言は「ONでは口調・表現のみ変化、推論・結論・事実内容は不変。素のModel出力と異なるため、Model本来の挙動を確認したい場合はOFFにすること」という開示内容とした（第1節の要件(2)を満たす）。

## 4. Validation

- Backend：`tests/unit/conversation/test_conversation_generation.py`へ3件追加（既定Disabled時にMessage無し／Enabled時にStyle限定Notice追加・内容検証／Context使用率Noticeとの共存）。Backend全体（`tests/unit`＋`tests/integration`）688 passed（3 deselected、実機依存Testで既存分）。
- Frontend：`SettingsModal.test.tsx`へ1件追加（既定OFF・Click時の`onSettingsChange`呼び出し検証）。Vitest全体は既存の無関係なlocalStorage既知問題（[claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md](claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md)第7節既報）を除き全てPass。ESLint・`tsc --noEmit`・`vite build`：Clean。
- 実Browser確認（Local LLMサーバー一時Instance）：
  - Toggle OFF（既定）：「日本の首都はどこですか？」に対し「日本の首都は東京です。」——平板な回答。
  - Toggle ON：同じ質問に対し「日本の首都は、✨東京です！🎉 （^ω^） www でも、他の都府県に比べて...」——事実内容（東京が首都という結論）は完全に保持されたまま、絵文字・顔文字・「www」・砕けたTone等の表現のみが変化することを確認。
  - Settings「基本」Category内、既存Toggle群の下に「表現重視モード」として表示され、開示Noteも正しく表示されることを確認。

## 5. Status

```text
Current Point            : 表現重視モード（Style限定Prompt Injection）を実装
                            完了。推論・結論は不変、表現のみ変化することを
                            実Browserで確認済み。
Files Created／Modified   : src/margpa_runtime_llm/modules/conversation/
                            contracts.py、public.py、application/
                            conversation_generation.py、
                            tests/unit/conversation/
                            test_conversation_generation.py、
                            frontend/src/types.ts、
                            frontend/src/components/SettingsPanel.tsx、
                            frontend/src/App.tsx、
                            frontend/src/i18n/translations.ts、
                            frontend/src/components/SettingsModal/
                            SettingsModal.test.tsx、本Evidence File。
Validation                : Backend pytest 688 passed（3 deselected）、
                            Frontend Vitest（既知の無関係localStorage
                            問題を除き）Pass、ESLint／tsc／Build Clean、
                            実Browser確認（OFF/ON比較）Clean。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。次のユーザー指示待ち。
```
