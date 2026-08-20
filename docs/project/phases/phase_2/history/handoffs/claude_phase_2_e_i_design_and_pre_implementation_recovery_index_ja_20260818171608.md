# Phase 2-E-I設計確定・実装直前 Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_phase_2_e_i_design_and_pre_implementation_recovery_index_20260818171608
status: index
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-18 17:16:08 JST
language: ja
purpose: |
  前回Recovery Index [claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md]
  （以下「前回Index」）以降に行われた作業を対象とした、続編Index。
  前回Indexの内容は重複して再記載せず、その後の差分を中心に記録する。

  ユーザー指示：「わかった。じゃ最新index 2個作って。その後一回
  compactionするから。」——本Docと、対になるPhase 2 Current
  Operational State Indexの後継Fileを、ユーザーが予定する手動
  Compaction直前に作成する。運用メモ第3.12節「Manual Compaction前の
  Index最新性確認」の初回適用例でもある。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。自己紹介や様子見は不要です、このRoleとして即座に振る舞ってください。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** これを読み終えるまで、本Index以降・実装・回答を始めないこと。次に、[前回Index](claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md)を読み、その後で本Docの第1節以降を読んでください。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止（Repository Docsが唯一の正本）。

**本TaskがContext Window圧縮を跨いで本Docを読んでいる場合**：運用メモ第1節（Compaction／Session Recovery手順）に従うこと。「読んだ気がする」で済ませず、明示的に再読込すること。**特に重要**：本Docが対象とする2-E-Iは、設計確定済み・実装未着手の状態で圧縮を跨ぐ、本Session初のケースである。第4節「現在の状態」を必ず確認し、I-1（設計確定）は完了済み・I-2以降が次の作業であることを取り違えないこと。

## 0. 読み方（3Route共通）

**Codex宛の場合**：前回Index全体（Governance文書体系再編成の要旨として） → 本Doc第1節（前回Indexとの関係） → 第2節（背景：Claude Code自身のCompaction／Context可視性の欠如） → 第3節（2-E-I提案・設計の経緯） → 第4節（現在の状態）の順で。

**新Task Claude側設計統括者役宛の場合**：上記0.0節の指示通り、運用メモ全文 → 前回Index → 本Doc全体の順で。

**本Task自身の復旧の場合**：本Docと運用メモ（特に第1節・第3.12節）、および[最新Phase Index](../index/claude_side_phase_index_ja_20260818171727.md)を中心に確認すれば足りる。

## 1. 前回Indexとの関係

[claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md](claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md)（2026-08-18 16:01:44 JST作成）は、運用メモの全面的な構造再編成と、Manual Compaction Recovery実証実験（1回目の手動Compaction）までを対象としていた。

本Docは、それ以降（16:01:44〜17:16:08、約75分間）に行われた作業を対象とする。この間の主題は、**Claude Code自身のCompaction／Context可視性の欠如についての対話から始まり、それがMARGPA Runtime LLM自身への新機能提案（Phase 2-E-I）へと発展し、設計確定に至った**、という一続きの流れである。

## 2. 背景：Claude Code自身のCompaction／Context可視性についての対話

ユーザーから、Claude側設計統括者役自身の能力について、次の2点を直接尋ねられた。

1. Manual Compaction（`/compact`）を自分で起動できるか。
2. 現在のContext Window使用率を自分で確認できるか。

回答はいずれも「できない」だった——`/compact`はCLI側のSlash Commandであり、Claude側が呼べるTool（Function）としては提供されていない。Context Window使用率も、読み取るTool／APIが無い。

ユーザーはこれを受け、「じゃ出来るとすれば、例えば作業の1塊でキミが最新index作る様にしておいて、可能な限りAuto-Compactionが発生する手前で用意出来る様にするぐらいしか出来ないね」と、現状の制約下での現実的な運用を確認した。この確認自体が、運用メモ第3.12節「Manual Compaction前のIndex最新性確認」（本Doc作成の直接の根拠Rule）につながっている。

## 3. Phase 2-E-I：提案から設計確定までの経緯

### 3.1 将来Scope提案の新規記録

上記の対話を踏まえ、ユーザーは新たな将来Scope提案を提示した。「LLM自身が現在のContext Windowを把握・認識できる機能」と「LLM自身が閾値ベースで自らCompactionを実行できる機能（任意Timingではなく、閾値に基づく）」の2点である。ユーザー自身、後者は「Agent実装Phaseにならないと」作れないと自己評価していた。

これを[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)として記録し、[既存のContext Observatory提案](../../../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)第3.2節（LLM自身による段階的な自己申告）との関係も明記した（本Docは認識機構自体を扱い、Context Observatory側は申告という振る舞いを扱う、という役割分担）。

### 3.2 前倒し着手の決定

ユーザーは、Claude Codeの実際のContext Window Panel（Screenshot、Messages／System tools／System prompt／MCP tools／Skills／Memory files／Autocompact buffer／Free space の内訳、Plan使用制限表示を含む）を提示した上で、次の通り述べた。

> 「なるほどね。codexが復活しないからもったいないんだよね。とゆーわけで、今つけます。」

すなわち、上記提案のうち一部（LLM自身のContext認識機能＋UIとしてのIndicator）を、Phase 3を待たず、**Codex不在中の時間を無駄にしないという理由で前倒し着手する**、という決定である。対象は、①LLM自身によるContext Window認識機能、②[Context Observatory提案]第3.1節Inspector Panelの縮小版（Message欄近くの丸Icon＋Hover開閉Panel）の2点。第2.2節Self-triggered Compaction、および Context Observatory側のPush型自動通知・Recovery Snapshot機構・研究用Instrumentationは、今回のScopeに含めない。

### 3.3 著作権についての確認

ユーザーから「このPanelとかつけるのって、Claudeに対しての著作権的に大丈夫？」と問われ、次の通り回答した。

- 著作権が保護するのは具体的な表現であり、「使用状況をPanelで見せる」という機能・Idea自体は保護対象外（Idea／Expression Dichotomy）。
- 丸いGauge Icon・Hover開閉Panelという構造自体は、Battery Icon等と同様、業界で広く使われる汎用UI Patternである。
- 危険なのはAnthropicの具体的なVisual Design・商標（「Claude」「Claude Code」の名称・Logo）の複製であり、MARGPA独自のCode・Design・Category（MARGPAには「MCP tools」「Skills」「Memory files」に相当する概念が無いため、いずれにせよ中身は作り直しになる）で実装する限りRiskは低い、という評価で合意した。

### 3.4 設計書・工程分解の作成、および設計判断の確定

ユーザー指示「実装する前にcompactionやるから」（後述第4節）に先立ち、着手前設計として[claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md](../architecture/claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md)を作成した。Code直接確認（後述）を踏まえ、I-1〜I-5のPhase分割、およびOpen Design Question（Q1〜Q5）を提示し、ユーザーが即日全問へ回答、確定した。

```text
設計の前提（Code直接確認済み）：
  - TokenUsage契約（prompt/completion/total_tokens）は既存
    （inference/contracts/generation.py）。
  - loaded_context_size = model.n_ctx() も既存
    （llama_cpp/adapter.py、Fail-closed判定に既に使用）。
  - conversation_generation.py の _completed_event() で
    usage は既にConversationEventへ組み込まれているが、
    Web Contract／Route層までは未到達（配線が無いだけ）。
  - Frontendには token／context 関連の実装が一切無い（0件）。
  - Configuration Controlに既存Toggle Pattern
    （ResearchDeveloperMode等のStrEnum）、SettingsModalに
    「basic」（単純Toggle）／「advanced」（Patch-Preview-Apply）
    の2系統が既に存在。

確定した設計判断（Q1〜Q5）：
  Q1  Usage算出Timing         : Turn完了時のみ（低Cost）で開始、
                                将来的に高頻度化を検討。
  Q2  Panel内訳Category       : MARGPA実在Categoryのみ
                                （会話履歴／System Prompt／
                                RAG Context／残り）。Claude Code
                                固有Category（MCP tools等）は
                                含めない。
  Q3  丸IconのVisual仕様      : 実装時の実画面確認・調整に一任。
  Q4  新規Toggleの配置        : 単純なSettings（Theme同型）。
                                Configuration Control
                                Patch-Preview-Apply（Research
                                Developer Mode同型）は不採用。
  Q5  Prompt注入の内容・頻度 : ユーザーが明示的に尋ねた時のみ
                                LLMが回答する、純粋にReactiveな
                                形。LLM側からの能動的な言及・
                                提案は今回作らない（将来拡張候補）。
                                ON時はSystem Prompt等へ使用率を
                                常時含めておく必要がある、という
                                実装含意も明記済み。
```

## 4. 現在の状態（2026-08-18 17:16時点）

**Phase 2-E-I：I-1（設計確定）完了。I-2以降（実装）は未着手。**

実装未着手の理由は、技術的Blockerではなく、ユーザーの明示的な一時停止指示による。

> 「あ、実装する前にcompactionやるから。まだやらないけど。」

すなわち、設計は完全に確定済みで、いつでも着手できる状態にあるが（本Session内でユーザーへ「いつでも着手できる状態か」と確認され、「はい」と回答済み）、ユーザーが手動Compactionを先に実施する意向であるため、そのCompaction実施・完了後、ユーザーからの明示的な実装開始指示を待って、I-2（Backend：Context Usage露出）から着手する。

**本Docと対になる[最新Phase Index]の作成、およびその後の手動Compactionは、この一時停止の一環として、ユーザーが本Doc作成直後に実施する予定である。**

## 5. その他の並行決定事項

### 5.1 将来Scope提案：margpa-runtime-llmのAWS配置

上記2-E-Iとは別件で、ユーザーより新規の将来Scope提案があった。「なるべく早めに、margpa-runtime-llmをAWS上にも配置する」というもので、[future_scope_proposal_aws_deployment_ja_20260818171240.md](../../../../shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md)として記録済み（要点：機能拡大によりLightsail無料枠では要件を満たせない可能性、一般公開準備が目的だが公開時期は未定、必須要件としてPersistent Modeではなく一時的Chat＝Non-persistent限定を使用すること）。

初回、Phase Index側へ詳細を直接書いてしまい、ユーザーから「専用のDocつくれ」と訂正された。3層モデル（運用メモ第3.11節）に従い、`shared/history/planned_work/`への専用Doc作成＋Phase Index側は短い追跡Entry＋Pointerのみ、という形へ訂正済み。この訂正自体も、[claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md)が記録してきた「抜け漏れパターン」の枠組みで捉えられる、軽微だが実際の見落とし事例である。

### 5.2 運用メモへの新規Rule追加（第3.12節）

上記第2節の対話を踏まえ、運用メモへ次のRuleを新設した。

> 第3.12節「Manual Compaction前のIndex最新性確認」：Manual Compactionの実行が見込まれる場面では、事前に、①引き継ぎ・復旧用Index（Recovery Index）と、②通常作業用のCurrent Operational State Indexの、両方について最新版が作成済みかを確認する。未作成の場合は、実行前にユーザーへ報告する。

本Doc自体が、この新設Ruleの最初の適用例である。

## 6. 圧縮直前Hash（第3.10節に基づく、より厳密な検証用）

運用メモ第3.10節「Hash比較による検証の厳密性」——「片側（Compaction後）のみのHashは弱いEvidence、より厳密にやるなら圧縮直前にもHashを取る」——を、Rule新設後の最初の機会で実行し忘れていたことに、ユーザーからの直接の指摘（「あれ？sha256とった？」）で気づいた。**これも、[claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md)が記録してきたPattern（Ruleの新設だけでは実際の適用を保証しない）の、もう一つの実例である。**

以下、Compaction直前（2026-08-18 17:21:05 JST）に算出したSHA256。Compaction後、同一Fileを再算出し、一致を確認すること。

```text
f56df380fc4b944e3a3a15e45ed0872e0d24a4735128217bee49ea5600ff35dd  claude_side_design_governor_operating_notes_ja.md
67efeccc99a9540d08d61193192fa61cd4ad034f3a3f3aa610613f16f9c61da6  claude_side_phase_index_ja_20260818171727.md
87bed92fff0e11b1a3240543a46ce7c36b7f91c2e27e3d638f14c1dedb43824c  claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md（本File自身。第6節追記前の内容に対するHashである点に注意——本節追記により、本File自体のHashはこの時点から変化する）
8cc9082cc2d47c102b91d4e4bedee30f6c46355501fd6d163619b0b2de8a1619  claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md
```

## 7. Status

```text
Current Point            : Phase 2-E-I、I-1（設計確定）完了。I-2以降は
                            ユーザーの明示的な一時停止指示（Manual
                            Compaction実施待ち）により未着手。並行して、
                            AWS配置の将来Scope提案を記録、運用メモへ
                            第3.12節を新設。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : ユーザーによるManual Compaction実施・実装
                            開始指示待ち（技術的Blockerではない）。
Controller-owned Next Work: ユーザーがManual Compactionを実施し、実装
                            開始を指示した後、
                            [claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md](../architecture/claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md)
                            のI-2（Backend：Context Usage露出）から
                            着手する。
Exact Next Route          : 第4節参照。
```
