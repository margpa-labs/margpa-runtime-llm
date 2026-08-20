> **[2026-08-18 12:18:42 追記] 後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260818121842.md](claude_side_phase_index_ja_20260818121842.md)に更新された。最新の状態はそちらを参照。

# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260818021437
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-18 02:14:37 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence、
  [claude_side_design_governor_operating_notes_ja.md]第3.3節参照。
  2026-08-18の運用メモ構造再編成により、旧「第0.5節」は現在
  「第3.3節」）における
  「Current Operational State」層を担う、Phase 2固有のIndexである。
  Claude側設計統括者役の未解決Open Question・未着手予約Task・完了済み
  予約Taskを一元管理する。恒久的な運用Rule（それは運用メモ側の役割）
  ではなく、直近の引き継ぎ用／自己復旧用Index（Recovery Index）への
  最新Pointerも保持する。

  本Fileは、`docs/project/phases/phase_2/history/index/`に既存の
  `documentation_index_*.md`／`phase_index_after_*.md`（Codex側が
  Phase 2-0〜2-E序盤で確立した、同種のCurrent State Snapshot慣習）に
  倣った、Claude側設計統括者役独自のIndexである。

  旧配置（誤り）：`docs/project/shared/history/claude_side_design_governor_open_items_ja_20260818021437.md`
  （`claude_side_design_governor_open_items_ja_20260818021437.md`という
  名称で作成）。ユーザー指摘（「shared/系は運用ルールを置く場所で
  あって、作業系がーとか予約系がーとか置く場所じゃない」）を受け、
  本Fileへ改名・移設した。経緯は
  [automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md](../../../../shared/history/automation/automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md)
  第2節を参照。
created: Claude Code
```

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下（Automation／Cross-provider PoC Evidenceは`shared/history/automation/`）の役割である。この3層（Rules／Current State／History-Evidence）の分離は、運用メモ第3.3節に明文化されている。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする（既存の`documentation_index_*.md`／`phase_index_after_*.md`と同じ方式）。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)（2026-08-18 00:48:59 JST作成）

Recovery Indexは、Codex復帰時・新Task Claude起動時・本Task自身のContext Window圧縮後復旧時、という3つの復旧経路で共用される、より重厚な統合文書である。本Current Operational State Indexは、それとは別に、日常的な参照用として、現在Open・未着手の項目だけを軽量に保持する。本節のPointerは、新しいRecovery Indexが作成されるたびに更新する。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Codex復活時：最新統合Recovery Index再作成（2026-08-18、ユーザー指示）

Codexが復活したら、その時点までの全作業を改めてまとめ直した、最新の統合Recovery Indexを作成する。対象範囲：

- [claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)作成以降の全て。
- Cross-model Evidence Doc（[automation_governance_evidence_cross_model_recovery_architecture_convergent_evaluation_ja_20260818011114.md](../../../../shared/history/automation/automation_governance_evidence_cross_model_recovery_architecture_convergent_evaluation_ja_20260818011114.md)、Compaction実地生存実験・自己監査を含む）。
- Provider Memory誤用・運用メモ構造混在の2件のHygiene Lapse、および本File自体の配置訂正（Open Items Tracker→本File）（[automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md](../../../../shared/history/automation/automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md)）。
- 運用メモへ新設した3層モデル（Rules／Current Operational State／History-Evidence）、および本Fileという新しいFile分類の導入。

**Trigger**：「Codex復活」。**現時点では着手しない**（ユーザー明示：「今はいい」）。除外事項（後述3.3の`automation_cross_provider_governance_ja.md`非記載方針）が今回も適用されるかは、着手時にユーザーへ改めて確認する。

### 3.2 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

Runtime常駐のTime Provider／Scheduler／Tool／Agent Runtime／Evidenceからなる構想（毎週定時のScraping→分析→保存等を完全自動化するScheduled Autonomous Workflow）。構想自体は[future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md](../../../../shared/history/future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md)へ記録済み。

**Trigger**：「Codex復活」——ユーザーが「codex復活したら、roadmap更新させる」と明言。Claude側から能動的に着手・提案しない。

### 3.3 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

Context Window使用状況の可視化・圧縮発生前の状態外部化・圧縮前後の比較記録を伴う構想（Budget Monitor／Pressure・Threshold／Compaction Detection／Retention Comparison／Recovery Snapshot／Recovery Evaluationの6要素）。構想自体は[future_scope_proposal_context_observatory_ja_20260817234734.md](../../../../shared/history/future_scope_proposal_context_observatory_ja_20260817234734.md)へ記録済み。

**Trigger**：ユーザーは「Phase 3の頭で作れそうなら作りたいが、後でもよい」という柔軟な位置づけ。Claude側から能動的に着手・提案しない。

### 3.4 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、修正未着手）

RAG回答自体をCopyして送り返すと、送信Message内のFile Path風Tokenが過剰にSubject判定され、既定top_k（4）を必ず超えて機械的に失敗するBug。原因特定済み、詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)。

**Trigger**：ユーザーの意向により「RAG丸々改善Phase」でまとめて対応予定。それまでは現状維持、個別修正は行わない。

## 4. 完了済み予約Task（記録として残す）

### 4.1 「index作って」Trigger（2026-08-16発令 → 2026-08-18完了）

ユーザーが「index作って」と言ったら、Phase 2-E作業（当初Scopeから2-E-B〜Gまで拡張した一連の作業）で作成した全Docsをまとめ直し、Indexを作成する、という予約Task。目的はCodex復帰後の正確な状況伝達。

**完了**：[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)として実行済み。

### 4.2 2-E-H実画面テスト後の統合Recovery Index再作成（2026-08-17発令 → 2026-08-18完了）

2-E-H（名前変更・削除）の実画面テストが完了し、ユーザーから明示的な作成指示があったら、「Codex／新規Task／このTaskの復旧」の3者に向けた、最新状態の統合Recovery Indexを改めて作成する、という予約Task。

**完了（2026-08-18 00:48:59 JST）**：[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](../handoffs/claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)として作成済み。

**重要な除外事項（今後の同種Index作成でも維持すること）**：このRecovery Indexには、**`automation_cross_provider_governance_ja.md`（Automation／Cross-provider Governance統合資料、`docs/project/current/automation_cross_provider/`）の存在を一切記載しない**。理由：ユーザーは、Codexへ同じ「Automation／Cross-provider Governanceをまとめ直す」Taskをあえて独立に行わせ、Claude側の成果物とCodex側の成果物の差分を見る意図である。IndexでこのFileの存在に触れると、Codexが先にそれを読んでしまい、独立した比較実験にならなくなる。

### 4.3 本Fileの配置訂正（2026-08-18発令 → 2026-08-18完了）

Provider Memory Incident是正の過程で、進行状態・予約Taskの切り出し先として`shared/history/claude_side_design_governor_open_items_ja_20260818021437.md`を作成したが、`shared/`はRole・統治Framework等の恒久的仕組みを置く場所であり、Phase固有の進行状態を置く場所ではない、とユーザーから指摘された。

**完了**：本File（`claude_side_phase_index_ja_20260818021437.md`）として、`phases/phase_2/history/index/`へ改名・移設済み。旧Fileは削除した。

## 5. Status

```text
Current Point            : 運用メモ・旧Open Items Trackerから、本Fileへ
                            現在の状態を集約・移設済み（未解決2件、
                            未着手予約Task4件、完了済み予約Task3件）。
Files Created／Modified   : 本Fileのみ（新規作成、旧Fileからの移設）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE
Controller-owned Next Work: 第3節の各予約TaskのTrigger成立を待つ。
                            内容更新時は、本Fileを上書きせず後継Fileを
                            作成する。新Phaseへ移行した場合は、新Phase
                            配下の`history/index/`へ同種のIndexを新設
                            する。
Exact Next Route          : ユーザーの次の判断待ち。
```
