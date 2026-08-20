# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260818171727
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-18 17:17:27 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence、
  [claude_side_design_governor_operating_notes_ja.md]第3.3節参照）における
  「Current Operational State」層を担う、Phase 2固有のIndexである。
  Claude側設計統括者役の未解決Open Question・未着手予約Task・完了済み
  予約Taskを一元管理する。恒久的な運用Rule（それは運用メモ側の役割）
  ではなく、直近の引き継ぎ用／自己復旧用Index（Recovery Index）への
  最新Pointerも保持する。

  本Fileは、前版
  [claude_side_phase_index_ja_20260818160352.md](claude_side_phase_index_ja_20260818160352.md)
  （2026-08-18 16:03:52 JST作成）の後継Fileである。前版の内容は
  重複して再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：ユーザー指示「最新index 2個作って。その後
  一回compactionするから」。運用メモ第3.12節（Manual Compaction前の
  Index最新性確認）に基づく。

  **前版からの構造変更**：新規第2節「現在進行中のSub-phase」を追加
  （Phase 2-E-I：設計確定・実装未着手という状態は、既存の3分類
  ――未解決Open Question／未着手予約Task／完了済み予約Task――の
  いずれにも綺麗に収まらないため）。これに伴い、以降の節番号を1つ
  繰り下げた。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260818181920.md](claude_side_phase_index_ja_20260818181920.md)（2026-08-18 18:19:20 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下（Automation／Cross-provider PoC Evidenceは`shared/history/automation/`、Claude Code固有のFailure系は`shared/history/ai_system_anomalies/claude_code/`、将来Scope提案・保留Itemは`shared/history/planned_work/`）の役割である。この3層（Rules／Current State／History-Evidence）の分離は、運用メモ第3.3節に明文化されている。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md](../handoffs/claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)（2026-08-18 17:16:08 JST作成）

Recovery Indexは、Codex復帰時・新Task Claude起動時・本Task自身のContext Window圧縮後復旧時、という3つの復旧経路で共用される、より重厚な統合文書である。本Current Operational State Indexは、それとは別に、日常的な参照用として、現在Open・進行中の項目だけを軽量に保持する。本節のPointerは、新しいRecovery Indexが作成されるたびに更新する。

## 2. 現在進行中のSub-phase

### 2.1 Phase 2-E-I：Context Window使用状況の可視化・LLM自己認識ON/OFF機能

**状態：I-1（設計確定）完了。I-2以降（実装）は未着手。**

設計書：[claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md](../architecture/claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md)（Open Design Question Q1〜Q5、2026-08-18ユーザー確認により全問確定済み）。

未着手の理由は技術的Blockerではなく、ユーザーの明示的な一時停止指示（「実装する前にcompactionやるから。まだやらないけど」）による。設計上はいつでも着手可能な状態（ユーザーへ確認済み、「はい」と回答済み）。

**次にやること**：ユーザーが手動Compactionを実施し、実装開始を指示した後、上記設計Docの I-2（Backend：Context Usage露出）から着手する。詳細な経緯は[最新Recovery Index第3節](../handoffs/claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)を参照。

## 3. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。

## 4. 予約Task（未着手、Trigger待ち）

### 4.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

Runtime常駐のTime Provider／Scheduler／Tool／Agent Runtime／Evidenceからなる構想（毎週定時のScraping→分析→保存等を完全自動化するScheduled Autonomous Workflow）。構想自体は[future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md](../../../../shared/history/planned_work/future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md)へ記録済み。

**Trigger**：「Codex復活」——ユーザーが「codex復活したら、roadmap更新させる」と明言。Claude側から能動的に着手・提案しない。

### 4.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

Context Window使用状況の可視化・圧縮発生前の状態外部化・圧縮前後の比較記録を伴う構想（Budget Monitor／Pressure・Threshold／Compaction Detection／Retention Comparison／Recovery Snapshot／Recovery Evaluationの6要素）。構想自体は[future_scope_proposal_context_observatory_ja_20260817234734.md](../../../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)へ記録済み。**このうち第3.1節の縮小版・第2.1節（別Doc）は、2-E-Iとして前倒し着手済み（第2節参照）。** 残る部分（Push型自動通知、Recovery Snapshot機構、研究用Instrumentation等）は引き続きTrigger待ち。

**Trigger**：ユーザーは「Phase 3の頭で作れそうなら作りたいが、後でもよい」という柔軟な位置づけ。Claude側から能動的に着手・提案しない。

### 4.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、修正未着手）

RAG回答自体をCopyして送り返すと、送信Message内のFile Path風Tokenが過剰にSubject判定され、既定top_k（4）を必ず超えて機械的に失敗するBug。原因特定済み、詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)。

**Trigger**：ユーザーの意向により「RAG丸々改善Phase」でまとめて対応予定。それまでは現状維持、個別修正は行わない。

### 4.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

LLM自身が現在のContext Window使用状況を把握・認識できる機能、およびLLM自身があらかじめ定めた閾値に基づき自らCompactionを実行できる機能（好きなTimingでの実行ではなく、閾値到達時のみ）の構想。構想自体は[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)へ記録済み。**このうち第2.1節（LLM自身の認識機能）は、2-E-Iとして前倒し着手済み（第2節参照）。** 第2.2節（Self-triggered Compaction）はAgent Runtime基盤が前提であり、引き続きTrigger待ち。

**Trigger**：「もし技術的に可能そうであれば」Phase 3の頭。ただしユーザー自身、Agent実装関連Phaseまで後ろ倒しになる可能性が高いと評価しており、技術的実現可能性自体が未検証。Claude側から能動的に着手・提案しない。

### 4.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

なるべく早めに、`margpa-runtime-llm`をAWS上にも配置する構想（機能・画面周りの拡大によりLightsail無料枠では要件を満たせない可能性、一般公開準備が目的、必須要件としてPersistent Mode不可・Non-persistent限定）。構想自体は[future_scope_proposal_aws_deployment_ja_20260818171240.md](../../../../shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md)へ記録済み。

**Trigger**：ユーザーの「なるべく早めに」という指示。具体的な着手Timingは未確定。

## 5. 完了済み予約Task（記録として残す）

### 5.1 「index作って」Trigger（2026-08-16発令 → 2026-08-18完了）

ユーザーが「index作って」と言ったら、Phase 2-E作業（当初Scopeから2-E-B〜Gまで拡張した一連の作業）で作成した全Docsをまとめ直し、Indexを作成する、という予約Task。

**完了**：[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)として実行済み。

### 5.2 2-E-H実画面テスト後の統合Recovery Index再作成（2026-08-17発令 → 2026-08-18完了）

2-E-H（名前変更・削除）の実画面テストが完了し、ユーザーから明示的な作成指示があったら、「Codex／新規Task／このTaskの復旧」の3者に向けた、最新状態の統合Recovery Indexを改めて作成する、という予約Task。

**完了（2026-08-18 00:48:59 JST）**：[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)として作成済み。

**重要な除外事項（今後の同種Index作成でも維持すること）**：このRecovery Indexには、**`automation_cross_provider_governance_ja.md`（Automation／Cross-provider Governance統合資料、`docs/project/current/automation_cross_provider/`）の存在を一切記載しない**。理由：ユーザーは、Codexへ同じ「Automation／Cross-provider Governanceをまとめ直す」Taskをあえて独立に行わせ、Claude側の成果物とCodex側の成果物の差分を見る意図である。

### 5.3 本File旧版の配置訂正（2026-08-18発令 → 2026-08-18完了）

Provider Memory Incident是正の過程で、進行状態・予約Taskの切り出し先として`shared/history/claude_side_design_governor_open_items_ja_20260818021437.md`を作成したが、`shared/`はPhase固有の進行状態を置く場所ではない、とユーザーから指摘された。旧版（`claude_side_phase_index_ja_20260818021437.md`）として、`phases/phase_2/history/index/`へ改名・移設済み。

### 5.4 運用メモの全面的な構造再編成（2026-08-18、複数Round）

運用メモが複数Roundにわたり構造再編成された。詳細は[claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md第3節](../handoffs/claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md)を参照。

### 5.5 将来Scope提案2件のFolder整理（2026-08-18発令 → 2026-08-18完了）

`shared/history/`直下にTopic Sub-folder化されず浮いていた将来Scope提案2件について、ユーザーが新設した`shared/history/planned_work/`へ移設した。

**完了**：`future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md`・`future_scope_proposal_context_observatory_ja_20260817234734.md`の2Fileを移設。参照元のPathも更新済み。

**位置づけの確定（2026-08-18）**：正式な予約系正本は`docs/public/roadmap_ja.md`（Codex管理、`shared/conventions/documentation_rules_ja.md`第23.4節）である点は変わらないが、`shared/history/planned_work/`自体は、Roadmap正式統合までの一時的な避難所ではなく、継続的に使う標準の置き場である。詳細は運用メモ第3.11節を参照。

### 5.6 Recovery Indexの前倒し再作成（1回目）（2026-08-18発令 → 2026-08-18完了）

Trigger「Codex復活」を待つ予約Task（当時第3.1節）だったが、ユーザーが明示的に前倒しでの実行を指示した。

**完了**：[claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md](../handoffs/claude_phase_2_governance_restructuring_and_compaction_recovery_index_ja_20260818160144.md)として作成済み。

### 5.7 2-E-I設計書・工程分解の作成、および全Open Question確定（2026-08-18発令 → 2026-08-18完了）

ユーザー指示「設計書と、工程を分解してくれ」に基づき、[claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md](../architecture/claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md)を作成。Q1〜Q5、即日ユーザー確認により全問確定済み（詳細は同Doc第4節、または[最新Recovery Index第3.4節](../handoffs/claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)）。実装（I-2以降）は第2節の通り未着手。

### 5.8 Recovery Indexの前倒し再作成（2回目）（2026-08-18発令 → 2026-08-18完了）

ユーザー指示「最新index 2個作って。その後一回compactionするから」に基づき、本File自体を含む、最新2Indexを作成。

**完了**：[claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md](../handoffs/claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)（Recovery Index）＋本File（Phase Index）。

## 6. Status

```text
Current Point            : Phase 2-E-I（I-1完了、I-2以降はCompaction待ち
                            で一時停止）を新規第2節として追跡開始。
                            AWS配置の将来Scope提案（第4.5節）を追加。
                            最新Recovery Index作成に伴い、本節Pointerを
                            更新した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE（Phase 2-E-I自体はユーザーのCompaction
                            実施待ちだが、これはTracker文書としての
                            Blockerではない）。
Controller-owned Next Work: ユーザーのManual Compaction実施→実装開始
                            指示を待つ。その他、第4節の各予約Task Trigger
                            成立を待つ。
Exact Next Route          : ユーザーの次の判断待ち。
```
