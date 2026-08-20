# Claude Phase 2-E-I（Context Window使用状況の可視化・LLM自己認識ON/OFF機能）工程分割・工程設計

```yaml
document_id: claude_phase_2_e_i_process_breakdown_design_20260818165116
status: design_draft
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-18 16:51:16 JST
language: ja
authorization: |
  ユーザー指示（2026-08-18）。「codexが復活しないからもったいないんだよね。
  とゆーわけで、今つけます。」——将来Scope提案として記録していた2件の
  一部を、Phase 3を待たず前倒しで着手する。実装は本Docの設計判断確定を
  経てから行う想定（未着手）。
related:
  - future_scope_proposal_context_observatory_ja_20260817234734
    （第0節参照。本Sub-phaseはこの提案の一部のみを対象とする）
  - future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021
    （同上。第2.2節Self-triggered Compactionは対象外）
created: Claude Code
```

## 0. 位置付け

前回のSub-phaseは2-E-H（会話の名前変更・削除、完了済み）。本Docは、その次のSub-phaseとして**2-E-I**を設計する。

**現在の状態（2026-08-18更新）**：第4節の設計判断Q1〜Q5、ユーザー確認により全問確定済み。ただし実装は依然として一切未着手——ユーザーが「実装する前にcompactionやるから」と明言しており、Manual Compaction実施後に実装着手指示を待つ。着手時は、運用メモ第3.12節（Manual Compaction前のIndex最新性確認）に従い、Compaction直前にRecovery Index・Phase Indexの最新性を確認すること。

**Scope（今回対象とする部分）**：
- [Context Observatory提案](../../../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)第3.1節「常時参照可能なInspector Panel（Pull型）」の、MARGPA向け縮小版。
- [LLM自身によるContext Window認識・Self-triggered Compaction提案](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)第2.1節「LLM自身によるContext Window認識機能」。ただしユーザー指示により、**Prompt注入の実施有無自体をConfiguration ON/OFFで制御**し、既定値はOFFとする（理由：PC Spec次第では追加Token Costが負担になりうるため）。

**Scope外（今回は対象としない）**：
- 同提案第2.2節「LLM自身による閾値ベースのSelf-triggered Compaction」——Agent Runtime基盤（Tool-calling機構）が前提であり、Phase 2には存在しない。
- Context Observatory第3.2節のPush型自動通知（使用率85%/90%/95%での自発的申告Message等）、第4節Recovery Snapshot機構、第6節研究用Instrumentation——いずれも本Sub-phaseのScopeには含めない。今回作るのは「①現在の使用状況をUserが見に行けるUI」と「②LLM自身のPromptへ使用率情報を注入するか否かのToggle」の2点に限定する。

## 1. Mission

1. **Backend**：現在のContext使用状況（使用Token数・Context Size・使用率）を、既存のTurn完了時Event（`_completed_event`）とは別に、Web API経由で取得できるようにする。
2. **Frontend**：Message入力欄近くに、丸いIcon（Claude Code類似だがMARGPA独自Design、著作権上の考慮は第6節参照）を配置する。Hoverで「コンテキスト状況を表示」「コンテキスト状況を非表示」を切替表示し、Click（または既存のHover Toggle）でIcon自体の塗り（Ring形式等）から一目で使用率がわかるようにし、詳細を開けばBreakdown Panelを表示する。
3. **Configuration Control**：「LLM自身のPromptへ、現在のContext使用率情報を注入するか」を制御する新規Toggle（既定OFF）を追加する。ON時のみ、生成Request構築時にSystem Prompt等へ使用率情報を加える。

## 2. 設計の前提（本Session内でCode直接確認した既存Architecture事実）

```text
src/margpa_runtime_llm/modules/inference/contracts/generation.py
  class TokenUsage(ImmutableContract):
      prompt_tokens: int
      completion_tokens: int
      total_tokens: int
  → 既存Contract。Turn単位のToken使用量は既に型として定義済み。

src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
  - loaded_context_size = model.n_ctx()（Runtime起動時に確定するContext容量）
  - required_tokens(prompt+max_new_tokens) > available_tokens(loaded_context_size)
    のFail-closed判定に、この2値が既に使われている。
  → 「使用量」「容量」の生Dataは、Backend内部に既に存在する。

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  _completed_event()内で、
    "usage": presented.usage.model_dump(mode="json") if ... else None
  としてConversationEventへ既に組み込まれている。
  → ただし、この`usage`はWeb Contract（persistent_contracts.py）
    ・Route（persistent_routes.py）まで到達していない（`grep`で0件）。
    Application層で止まっている。

frontend/src
  → token／context関連の実装は一切無い（`grep`で0件）。真っ新な状態
    から新規実装する。

src/margpa_runtime_llm/modules/configuration_control/contracts.py
  class ResearchDeveloperMode(StrEnum): OFF / ON
  class DocumentationRagControlMode(StrEnum): DISABLED / ENABLED
  → 既存のON/OFF系Toggle Patternが既に複数存在する。新規Toggleも
    同型のStrEnum＋Configuration Control経由で追加するのが素直。
  Web Route: /api/v2/configuration/{runtime,effective,preview,apply}
  → 既存のPatch申請→Preview→Apply、という重量級Flow。

frontend/src/components/SettingsModal/SettingsModal.tsx
  Category = "basic" | "advanced"。
  "basic" → SettingsPanel.tsx（Theme等、単純な即時反映系）
  "advanced" → ConfigurationControlPanel.tsx（Research Developer Mode等、
              Patch-Preview-Apply系。configurationBootstrapEnabled時のみ表示）
  → 新規Toggleを「basic」（Themeと同型の単純Toggle）に置くか、
    「advanced」（Research Developer Modeと同型のPreview-Apply Flow）
    に置くかは、設計判断が必要（第4節Q4）。
```

## 3. Phase分割（I-1〜I-5）

2-E-B〜Hの「設計→実装→Validation→実Browser確認→Docs化」のCycleを踏襲する。

```text
I-1  設計確定（第4節Open Question解消がGate）
     Q1〜Q4の確定。

I-2  Backend実装：Context Usage露出
     - web/persistent_contracts.py: Context使用状況を返す新規Response
       Contract（例：PersistentContextUsageResponse。prompt_tokens／
       completion_tokens／total_tokens／loaded_context_size／
       usage_ratio）。
     - web/persistent_routes.py: 新規Route（例：GET .../context-usage、
       または既存Turn完了Response・SSE Eventへ相乗り、Q1次第）。
     - Test: Unit（Contract）／Integration（Route経由の実値確認）。

I-3  Backend実装：Configuration Controlへの新規Toggle追加
     - contracts.py: 新規StrEnum（例：ContextUsagePromptInjectionMode:
       OFF / ON）、既定OFF。
     - Q4の結論に従い、SettingsPanel直結の単純Toggleか、
       Configuration Control Patch-Preview-Apply経由かを実装。
     - ON時：生成Request構築時（conversation_generation.py周辺）に、
       System Prompt等へ使用率情報を注入するLogicを追加。注入内容・
       頻度はQ5で確定させる。
     - Test: Unit（OFF時は注入されないこと／ON時は注入されること）。

I-4  Frontend実装
     - 丸Icon Component新規作成（Ring形式、使用率で塗り分け）。
     - Hover文言「コンテキスト状況を表示」「コンテキスト状況を非表示」
       （i18n/translations.tsへja/en両方追加）。
     - Click／Toggleで開くBreakdown Panel（Q2のCategory構成に従う）。
     - Settings側：新規Toggle UI（Q4の結論に従い配置）。
     - api/client.ts: Context Usage取得の新規関数追加。

I-5  全体Validation・実Browser確認・Docs化
     - npm run {lint,typecheck,test,build} Clean確認。
     - pytest -q Clean確認。
     - 実Browser・実LLM・実Backendでの動作確認（Icon表示、Hover文言、
       Panel開閉、Toggle ON/OFF切替、White/Dark両Theme）。
     - Completion Handoff＋Automation Governance Evidence作成。
     - Phase Index・future_scope_proposal 2件（該当箇所）の更新。
```

## 4. 設計判断（2026-08-18ユーザー確認により全5問確定）

```text
Q1. Context Usage算出のTiming
    【決定】まずは低Cost側（Turn完了時のみ、既存_completed_eventと
    同じTiming）で開始する。将来的に、より高頻度側（Streaming中の
    定期更新）への拡張を検討する。

Q2. Panel内のBreakdown Category
    【決定】MARGPAに現在実在するCategoryのみを使う（Claude Code固有の
    MCP tools／Skills／Memory files等は含めない）。会話履歴
    （Messages）／System Prompt／RAG Context（Citation含む）／残り
    （Free space）の区分とする。

Q3. 丸IconのVisual仕様
    【決定】実装時の実画面確認・調整に一任する（過去のCSS微調整
    5Roundと同じ運用）。

Q4. 新規Toggleの配置・制御Flow
    【決定】単純なSettings（Theme等と同型、SettingsPanel直結の
    即時反映Toggle）とする。Configuration ControlのPatch-Preview-
    Apply Flow（Research Developer Mode同型）は不採用。

Q5. ON時、Promptへ注入する情報の具体的な内容・頻度
    【決定】ユーザー側から「今コンテキスト何%？」等、明示的に尋ねられた
    場合にのみ、LLMがその場で回答できればよい（純粋にReactiveな
    Q&A）。使用率超過時の自発的な言及・提案（Context Observatory
    提案第3.2節のPush型自己申告相当）等、それ以上の機能は今回のScope
    に含めず、将来の拡張候補として残す。

    実装上の含意：LLMが「尋ねられたら答えられる」ためには、ON時は
    System Prompt等へ現在の使用率情報を常時含めておく必要がある
    （でなければ質問された瞬間に情報を持っていない）。ただし、LLM側
    から能動的に話題へ出す振る舞いは実装しない——あくまで尋ねられた
    時のみ回答する、受動的な位置づけに留める。
```

## 5. 既存慣習との対応表

```text
観点                  既存Toggle（Research Developer Mode）  今回の新規Toggle
Contract              StrEnum（OFF/ON）in                    同型のStrEnum新設
                       configuration_control/contracts.py
Web Route              /api/v2/configuration/*                Q4次第
                       （runtime/effective/preview/apply）
Frontend配置           SettingsModal「advanced」               Q4次第
                       （ConfigurationControlPanel）
既定値                 OFF                                    OFF（ユーザー指示通り）
```

## 6. Risk・複雑度メモ

```text
- I-2（Backend Usage露出）は、既存Data（TokenUsage・loaded_context_size）
  の配線のみであり、複雑度は低い（2-E-B相当）。
- I-3のうち、Toggleの箱自体（OFF/ON切替）は低Risk。一方、ON時の
  実際のPrompt注入Logic（Q5）は、Token Cost実測・PC Spec上の負荷検証
  が必要になりうり、単体でIterationを要する可能性がある。
- I-4（丸Icon＋Panel）は新規Frontend Componentであり、過去のCSS微調整
  5Roundと同様、実画面確認前提でIteration計画を組むことを推奨する。
- 著作権面：前回の会話で回答済みの通り、機能・UI Pattern自体（丸い
  Gauge Icon、Hover開閉Panel）はIdea／Expression Dichotomyにより
  保護対象外と考えられ、MARGPA独自のCode・Design・Categoryで実装する
  限りRiskは低い。実装時のGuardrailとして、Anthropic・Claudeの名称・
  Logoを一切使用しないことを明記する（運用メモ第4.1節の趣旨とも整合）。
```

## 7. Status

```text
Current Point            : 第4節の設計判断、全5問（Q1〜Q5）2026-08-18
                            ユーザー確認により確定済み（I-1実質完了）。
                            実装（I-2以降）はユーザーの明示的な一時停止
                            指示（「実装する前にcompactionやるから。
                            まだやらないけど」）により、依然として
                            未着手。
Files Created／Modified   : 本Fileのみ（第0節・第4節を更新）。実装Fileは
                            無変更。
Validation                : N/A（設計Doc）
Open Current Blocker      : ユーザーによるManual Compaction実施・実装
                            開始指示待ち（技術的Blockerではない）。
Controller-owned Next Work: ユーザーがManual Compactionを実施し、実装
                            開始を指示した後、I-2（Backend：Context
                            Usage露出）から着手する。着手直前に、運用
                            メモ第3.12節に従いRecovery Index・Phase
                            Indexの最新性を確認すること。
Exact Next Route          : 本Session（新Task化なし）が、ユーザーの
                            Compaction実施・実装開始指示を待つ。
```
