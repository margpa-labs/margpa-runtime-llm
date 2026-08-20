# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260818181920
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-18 18:19:20 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence、
  [claude_side_design_governor_operating_notes_ja.md]第3.3節参照）における
  「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260818171727.md](claude_side_phase_index_ja_20260818171727.md)
  （2026-08-18 17:17:27 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：ユーザー指示「工程：I-1→I-2→I-3→I-4→I-5。
  一気によろしく。終わったら、作業用indexと、Automationのエビデンスを
  書いておいて。」に基づき、Phase 2-E-I（I-2〜I-5）を完了させたため。

  **前版からの構造変更**：前版第2節「現在進行中のSub-phase」を廃止した。
  2-E-Iが「設計確定・実装未着手」という一時的な状態だったために新設した
  節だが、本File作成時点でI-1〜I-5すべて完了し、この特例状態が解消した
  ため、以降は他Sub-phaseと同様「完了済み予約Task」（第4節）として扱う。
  節番号は前版の第3節（Open Questions）以降を1つ繰り上げた。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260818223600.md](claude_side_phase_index_ja_20260818223600.md)（2026-08-18 22:36:00 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下（Automation／Cross-provider PoC Evidenceは`shared/history/automation/`、Claude Code固有のFailure系は`shared/history/ai_system_anomalies/claude_code/`、将来Scope提案・保留Itemは`shared/history/planned_work/`）の役割である。この3層（Rules／Current State／History-Evidence）の分離は、運用メモ第3.3節に明文化されている。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md](../handoffs/claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)（2026-08-18 17:16:08 JST作成）

本File作成時点では、Recovery Indexの前倒し再作成条件（運用メモ第3.12節、Manual Compaction直前）に該当しないため、Recovery Index自体は前版から更新していない。2-E-I完了の詳細経緯は、[claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md](../../../../shared/history/automation/claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md)（Evidence Doc）を参照。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

Runtime常駐のTime Provider／Scheduler／Tool／Agent Runtime／Evidenceからなる構想（毎週定時のScraping→分析→保存等を完全自動化するScheduled Autonomous Workflow）。構想自体は[future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md](../../../../shared/history/planned_work/future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md)へ記録済み。

**Trigger**：「Codex復活」——ユーザーが「codex復活したら、roadmap更新させる」と明言。Claude側から能動的に着手・提案しない。

### 3.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

Context Window使用状況の可視化・圧縮発生前の状態外部化・圧縮前後の比較記録を伴う構想（Budget Monitor／Pressure・Threshold／Compaction Detection／Retention Comparison／Recovery Snapshot／Recovery Evaluationの6要素）。構想自体は[future_scope_proposal_context_observatory_ja_20260817234734.md](../../../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)へ記録済み（本File自体は未編集——既存History Fileの無許可上書き禁止、運用メモ第2.1節）。

**このうち第3.1節の縮小版（Message欄近くの丸Icon＋Breakdown Panel）は、2-E-Iとして完了済み**（第4.9節参照）。残る部分（Push型自動通知、Recovery Snapshot機構、研究用Instrumentation等）は引き続きTrigger待ち。

**Trigger**：ユーザーは「Phase 3の頭で作れそうなら作りたいが、後でもよい」という柔軟な位置づけ。Claude側から能動的に着手・提案しない。

### 3.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、修正未着手）

RAG回答自体をCopyして送り返すと、送信Message内のFile Path風Tokenが過剰にSubject判定され、既定top_k（4）を必ず超えて機械的に失敗するBug。原因特定済み、詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)。

**Trigger**：ユーザーの意向により「RAG丸々改善Phase」でまとめて対応予定。それまでは現状維持、個別修正は行わない。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

LLM自身が現在のContext Window使用状況を把握・認識できる機能、およびLLM自身があらかじめ定めた閾値に基づき自らCompactionを実行できる機能（好きなTimingでの実行ではなく、閾値到達時のみ）の構想。構想自体は[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)へ記録済み（本File自体は未編集——運用メモ第2.1節）。

**このうち第2.1節（LLM自身の認識機能）は、2-E-Iとして完了済み**（第4.9節参照）。第2.2節（Self-triggered Compaction）はAgent Runtime基盤が前提であり、引き続きTrigger待ち。

**Trigger**：「もし技術的に可能そうであれば」Phase 3の頭。ただしユーザー自身、Agent実装関連Phaseまで後ろ倒しになる可能性が高いと評価しており、技術的実現可能性自体が未検証。Claude側から能動的に着手・提案しない。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

なるべく早めに、`margpa-runtime-llm`をAWS上にも配置する構想（機能・画面周りの拡大によりLightsail無料枠では要件を満たせない可能性、一般公開準備が目的、必須要件としてPersistent Mode不可・Non-persistent限定）。構想自体は[future_scope_proposal_aws_deployment_ja_20260818171240.md](../../../../shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md)へ記録済み。

**Trigger**：ユーザーの「なるべく早めに」という指示。具体的な着手Timingは未確定。

## 4. 完了済み予約Task（記録として残す）

### 4.1 「index作って」Trigger（2026-08-16発令 → 2026-08-18完了）

**完了**：[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)として実行済み。

### 4.2 2-E-H実画面テスト後の統合Recovery Index再作成（2026-08-17発令 → 2026-08-18完了）

**完了（2026-08-18 00:48:59 JST）**：[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)として作成済み。

**重要な除外事項（今後の同種Index作成でも維持すること）**：このRecovery Indexには、**`automation_cross_provider_governance_ja.md`（Automation／Cross-provider Governance統合資料、`docs/project/current/automation_cross_provider/`）の存在を一切記載しない**。理由：ユーザーは、Codexへ同じ「Automation／Cross-provider Governanceをまとめ直す」Taskをあえて独立に行わせ、Claude側の成果物とCodex側の成果物の差分を見る意図である。

### 4.3 本File旧版の配置訂正（2026-08-18発令 → 2026-08-18完了）

旧版（`claude_side_phase_index_ja_20260818021437.md`）として、`phases/phase_2/history/index/`へ改名・移設済み。

### 4.4 運用メモの全面的な構造再編成（2026-08-18、複数Round）

詳細は[claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md第3節](../handoffs/claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md)を参照。

### 4.5 将来Scope提案2件のFolder整理（2026-08-18発令 → 2026-08-18完了）

**完了**：`future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md`・`future_scope_proposal_context_observatory_ja_20260817234734.md`の2Fileを`shared/history/planned_work/`へ移設。位置づけの確定（一時的避難所ではなく継続的に使う標準の置き場）は運用メモ第3.11節を参照。

### 4.6 Recovery Indexの前倒し再作成（1回目）（2026-08-18発令 → 2026-08-18完了）

**完了**：[claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md](../handoffs/claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md)として作成済み。

### 4.7 2-E-I設計書・工程分解の作成、および全Open Question確定（2026-08-18発令 → 2026-08-18完了）

**完了**：[claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md](../architecture/claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md)。Q1〜Q5、即日ユーザー確認により全問確定済み。

### 4.8 Recovery Indexの前倒し再作成（2回目）（2026-08-18発令 → 2026-08-18完了）

**完了**：[claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md](../handoffs/claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)（Recovery Index）＋前版Phase Index。

### 4.9 Phase 2-E-I：Context Window使用状況の可視化・LLM自己認識ON/OFF機能（2026-08-18発令 → 2026-08-18完了）

ユーザー指示「工程：I-1→I-2→I-3→I-4→I-5。一気によろしく」に基づき、設計確定済みだった2-E-Iの実装（I-2〜I-5）を完了。

**完了**：[claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md](../../../../shared/history/automation/claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md)（Evidence Doc、実装詳細・Test・実Browser確認結果を記録）。

**要点**：
- I-2：Backendで現在のContext使用状況（Token数・使用率・4分類Breakdown）を算出し、既存の完了時SSE Eventへ相乗りする形でFrontendへ伝達。
- I-3：Configuration Control（重量級Preview-Apply Flow）ではなく、`ConversationSettings`直下の単純Toggleとして実装（Q4の実装時解釈）。ON時、LLM自身のPromptへ現在の使用率を注入し、ユーザーから明示的に尋ねられた場合のみ回答する、純粋にReactiveな設計（Q5）。
- I-4：丸Gauge Icon＋Breakdown Panel＋Settings Toggleを新規実装。
- **実装過程での発見・修正**：llama-cpp-python（既存Backend）は、Streaming生成時にToken使用量を一度も報告しないという、Library自体の仕様上の欠落を発見。この欠落は2-E-Iのcontext_usageだけでなく、Phase 1-G以来存在する既存の`usage`Fieldにも影響していた。Adapter層（`llama_cpp/adapter.py`・`stream.py`）へFallback算出Logicを追加し、両方を修正。
- I-5：pytest 694件・Frontend Vitest 72件・Lint・Typecheck・BuildすべてClean。実Local Model（Qwen3-4B、Mac Metal）でのLive Browser確認において、Gauge表示・Breakdown Panel・Dark Theme・実際のLLMによる「1%」という正しい回答（Reactive設計の実地確認）まで、すべて動作確認済み。

## 5. Status

```text
Current Point            : Phase 2-E-I、I-1〜I-5すべて完了。前版で追跡
                            していた「進行中のSub-phase」特例は解消し、
                            通常の完了済み予約Task（第4.9節）へ移行した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE。
Controller-owned Next Work: 第3節の各予約Task Trigger成立を待つのみ。
Exact Next Route          : ユーザーの次の判断待ち。
```
