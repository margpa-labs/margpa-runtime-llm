# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260819144637
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-19 14:46:37 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence、
  [claude_side_design_governor_operating_notes_ja.md]第3.3節参照）における
  「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260819113202.md](claude_side_phase_index_ja_20260819113202.md)
  （2026-08-19 11:32:02 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：前版作成以降、実機Feedback対応4件（Markdown表
  崩れ修正・表Message横幅拡張・表現重視モード・表Cell内`<br>`／箇条書き
  Marker修正）が完了し、ユーザーより「一旦つけたいUI系は一通り完了」との
  確認を得た。続けてPhase 3実装計画（Codex復活後の設計→Claudeによる
  一括実装、Automation／Auto-Compaction Recovery長期実験兼務）が共有され
  たため、区切りとして新規作成する。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260819181056.md](claude_side_phase_index_ja_20260819181056.md)（2026-08-19 18:10:56 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md](../handoffs/claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md)（2026-08-19 14:46:37 JST作成）。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。2026-08-20のCodex復活時に確認できる可能性がある。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 2-E-I #4（Context使用率Injection Toggle OFF状態での、思考過程・メタ会話のような出力混入）の原因は未特定。原因調査自体もまだTrigger・担当が確定していない。
- Cycle 5のCompaction Recovery報告における、Procedure Fidelityの精度に関する指摘（「3Docs明示的再読込」と宣言しつつ、実際は1Fileのみ本Turn内Read Tool・残り2FileはSystem再挿入内容を利用）。独立Failure Docとして記録するかはユーザー判断待ち（詳細は[claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md](../../../../shared/history/automation/claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md)第3.4節・第4節）。

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

構想は[future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md](../../../../shared/history/planned_work/future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md)。**Trigger**：「Codex復活」。2026-08-20（木）のCodex復活予定により、成立が近い。

### 3.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_context_observatory_ja_20260817234734.md](../../../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)。第3.1節の縮小版は2-E-Iとして完了済み。残る部分は引き続きTrigger待ち。**Trigger**：「Phase 3の頭で作れそうなら作りたいが、後でもよい」。

### 3.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、修正未着手）

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)。**Trigger**：「RAG丸々改善Phase」。**関連**：第3.7節（同一Triggerで扱う新規観測分）。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)。第2.1節は2-E-Iとして完了済み。第2.2節はAgent Runtime基盤が前提でTrigger待ち。**関連**：第3.6節（自動復旧側を補完する続編提案）、第3.8節（Phase 3実装計画）。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

構想は[future_scope_proposal_aws_deployment_ja_20260818171240.md](../../../../shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md)。**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 3.6 LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md](../../../../shared/history/planned_work/future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md)。MARGPA Runtime自身が生成するLLMに、Claude Code等のAgent Harnessが既に備える「自動圧縮→自動復旧」Cycleに相当する機能を持たせる構想。第3.4節の続編（自動復旧側を補完）。**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。

### 3.7 既知の課題：Documentation RAG検索結果固定化・無関係質問への誤発火（2026-08-19、修正未着手）

詳細は[documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md](../operations/documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md)。Query内容に関わらず検索結果が固定化するPattern、および明らかに無関係な質問でもRAGが誤発火するPatternの2件。第3.3節の既存Known Issueとは別事象（送信Errorではなく検索結果自体の不適切さ）。**Trigger**：第3.3節と同一、「RAG丸々改善Phase」。ユーザー指示により優先度は低（週間利用可能量の制約、Docs記録済みで現状は十分）。

### 3.8 [新規] Phase 3実装：Governance Definition Platform構築のClaude一括実装（2026-08-19、ユーザー提示、Automation／Compaction Recovery長期実験兼務）

Phase 3（[roadmap_ja.md](../../../../../public/roadmap_ja.md)第9節「Audit, Evidence, and Generic Definition Infrastructure」、State`Planned`）の実装部分を、設計完了後にClaude側設計統括者役が一気通貫で実装する予定。これは同時に、本Session中に確立してきたAutomation／Auto-Compaction Recovery機構（3Docs明示的再読込、Hash Manifest、Phase Index／Recovery Index succession等）の長期戦（Long-running）実地検証を兼ねる。

設計体制：Codexプロジェクト責任者兼設計統括者役が2026-08-20（木）に復活予定。Phase 3の設計自体はCodexとユーザーが行う。Claude側は、設計完了・引き継ぎを受けてから実装Phaseへ入る。

使用予定のGovernance Definition群：ユーザーより`other/margpa-runtime-llm用_definitions_20260819.zip`（Project Root外、ユーザー管理領域）の提示を受け、Read-onlyで内容確認済み（Repositoryへは未格納）。構成：

- Core（1File内2件）：ARGD (Axiomatic Reasoning Governance Definition) v0.3.1、DAGD (Declarative AI Governance Definition) v0.4.4
- Orchestration（1件）：CDOGD (Cross-Domain Orchestration Governance Definition) v0.1.0
- Domain Extensions（14件、いずれもv0.1.0）：
  - Ordinary（10件）：AAGD、ACRGD、AIAGD、AIRGD、AISGD、DCAGD、DSGD、MPGD、OMRGD、PMOGD、SEGD
  - Decision Pipelines（3件）：SPPGD、DAAGD、SDAGD
  - Conditional Watchdogs（1件）：SDMRGD

詳細な経緯は[claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md](../handoffs/claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md)第2.7節を参照。

**Trigger**：Codexとユーザーによる設計完了・Claude側への引き継ぎ。

## 4. 完了済み予約Task（記録として残す）

### 4.1（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260819113202.md](claude_side_phase_index_ja_20260819113202.md)第4節、4.1〜4.11）を参照。2-E-I I-1〜I-6完了、実機Feedback対応一式（Scroll Pin・Composer Clearance・初回送信Bug修正・Streaming Markdown・Markdown表崩れ修正・表Message横幅拡張・表現重視モード・表Cell内`<br>`／箇条書きMarker修正）が全て完了。表Message横幅拡張・表現重視モードは、ユーザー自身の実機確認も完了。

### 4.2 長期戦運用Companion Doc新設・Auto-Compaction検知限界の検討（2026-08-19発令 → 完了）

Phase 3実装計画の共有を受け、Auto-Compaction検知限界・Phase Index／Recovery Indexの役割分担・Step単位Index更新運用・判断依存型Mode切替のRisk（Provider Memory Near-miss参照）等を10Turnにわたり検討し、[claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md](../../../../shared/history/automation/claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md)としてLossless記録した。

帰結として、[claude_side_long_running_automation_companion_ja.md](../../../../shared/task_roles/claude_side_long_running_automation_companion_ja.md)（運用メモ・Hash Manifestと並ぶ第3の自己編集可能Stable File、運用メモ第1節Step 2参照——後日、当初の第3.15節から第1節へ移設。第4.3節参照）を新規作成した。長期戦Automation実行時のDocumentation量のみを`long_running_mode_active`フラグで構造的に軽量化する設計であり、運用メモ第2節・第3節（Governance Rule）の全文読了は本Docの有無・Active状態に関わらず絶対に代替されない旨を明記している。既定`long_running_mode_active: false`（現在未Active）。運用メモへの追記は当初第3.15節（＋第0節・第2.1節の該当参照）のみに抑えたが、後日第1節へ移設した（第4.3節参照）。

### 4.3 Auto-Compaction Hash Tracker詳細化・History File直接編集Failureの是正（2026-08-19発令 → 完了）

第4.2節のCompanion Docへ、ユーザー追加要望（既存Hash Manifestと同粒度でのBefore／After Hash比較、作業開始時刻・所要時間Evidence化）を反映する過程で、既存History Evidence（第4.2節記載の[claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md](../../../../shared/history/automation/claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md)）へ直接追記するFailureが発生した。ユーザー指摘「キミの悪い癖が出てるぞ。運用メモ見返してみ？」を受け、運用メモ第2.1節「`history/`配下＝新規作成のみ」原則に反していたことを確認し、直接追記を取消・原状復元した上で、正しい形（新規Append-only File）で[claude_long_running_automation_hash_tracker_and_timing_evidence_refinement_ja_20260819165350.md](../../../../shared/history/automation/claude_long_running_automation_hash_tracker_and_timing_evidence_refinement_ja_20260819165350.md)として記録し直した。

帰結として、Companion Doc第3.4節（作成当時の節番号。本節末尾の追記により後日第4.4節へ繰下げ）を「長期戦専用Auto-Compaction Hash Tracker」（Rolling Baseline方式のBefore Hash取得・事後After Hash比較のBest-effort設計）へ改訂し、第3.5節（同、後日第4.5節、作業開始時刻・所要時間Evidence化）を新設した。実Trackerである[claude_long_running_auto_compaction_hash_tracker_ja.md](../../../../shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md)（既存Hash Manifestと同一形式、成功0件・失敗0件から開始）も、ユーザー要望通り前倒しで新規作成した。

さらにユーザーより、Companion Doc・Hash Tracker双方が「長期戦Docsは軽量であるべき」という自らの設計原則自体に違反する分量になっている（File Sizeが大きいほどCompaction後のRecovery失敗率が上がるという第4.2節のEvidenceと矛盾する）との指摘を受け、両Fileを圧縮した（Companion Doc：119行→74行、Hash Tracker：58行→43行）。

続けてユーザーより2点の追加指摘を受けた。(1) 運用メモ第3.15節の内容（長期戦Companionと本File全文読了の関係）が、本来の主題である第1節「Compaction／Session Recovery手順」ではなく、無関係な第3節「上位規則」の一項目として埋もれていた。(2) Companion Doc・Hash Trackerの「Status」節は、参照元であるHash Manifest・運用メモ自体のどちらにも存在しないPatternを、確認せず踏襲していた。

是正として、運用メモ第1節へStep 2（Companion Docの`long_running_mode_active`確認、本File全文読了は不省略、自己編集可能Stable Fileとしての権限記述込み）を新設した。Companion Doc・Hash Trackerの「Status」節は両方削除した（Companion Doc：74行→62行、Hash Tracker：43行→32行）。

ユーザーより「§3.15を1行参照として残す必要性自体あるのか」との追加指摘を受け、§3.15を完全に削除し、§0・§2.1の参照先（「第3.13節・第3.15節」）を「第1節・第3.13節」へ更新した。Companion Docは自己編集可能Stable Fileとしての権限記述を第1節Step 2が兼ねる。

ユーザー指示「整合性完全か確認しろ」を受けた全File横断Checkで、Phase Index内に既に削除済みの第3.15節を現在形で参照する記述が複数残留していたことを自ら発見・是正した（本節・Status Block双方）。

一連の6件（History File直接追記・軽量化原則違反・配置Miss・不要Status節・削除漏れ・整合性Check時の発見）を、共通の根本原因とともに[claude_output_anomaly_long_running_docs_construction_repeated_failure_ja_20260819173106.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_long_running_docs_construction_repeated_failure_ja_20260819173106.md)として記録した。

ユーザーより、この長期戦運用体制で本Companion Docを使用する旨、およびGPT監査でも十分な見込みがあるとの評価を得た旨の共有があった。続けて、Companion Docへ「無確認Autonomy原則」（長期戦Mode中は作業中に一度もユーザーへ確認を求めない。1回でも確認を挟めば長期戦Automation実験自体が成立しなくなるため。運用メモ第2.2節のEscalation Gateのみが適用除外対象で、Git禁止・Root境界・Provider Memory禁止等の絶対的禁止事項は不変。Backupはユーザー側で事前取得済み）を最上位Ruleとして追加する指示を受け、新規第2節として追加した（既存の第2節以降は第3節・第4節へ繰下げ。第3.4節→第4.4節、第3.5節→第4.5節）。

続けてユーザーより、「よっぽどなら止めていい」との明示的な例外条件が追加された。無確認Autonomyが適用されるのは、あくまで指示範囲・Scope・Rules・Governanceの範囲内に限られ、その範囲外に出る、規則と矛盾する、致命的Riskに該当する等の「よっぽどの場合」は、例外として停止・確認してよい旨をCompanion Doc第2節へ反映した。

## 5. Status

```text
Current Point            : Phase 2-E-I実機Feedback対応一式が、ユーザー
                            確認込みで完了（「一旦つけたいUI系は一通り
                            完了でいいかな」で相互確認）。Phase 3実装
                            計画（Codex復活後の設計→Claude一括実装、
                            Automation／Compaction Recovery長期実験兼務）
                            を第3.8節へ記録した。長期戦運用に向け、
                            Auto-Compaction検知限界の検討を経て長期戦
                            運用Companion Doc（第4.2節）を新設した。
Files Created／Modified   : docs/project/shared/task_roles/
                            claude_side_long_running_automation_companion_ja.md
                            （新規・第3.4節改訂・第3.5節新設・その後Trim、
                            第4.2〜4.3節）、claude_side_design_governor_operating_notes_ja.md
                            （最終的に第1節Step 2・第0節・第2.1節、
                            第4.2〜4.3節）、docs/project/shared/
                            automation/claude_long_running_auto_compaction_hash_tracker_ja.md
                            （新規・その後Trim、第4.3節）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE
Controller-owned Next Work: 第3節の各予約Task Trigger成立を待つ。特に
                            第3.1節・第3.8節はCodex復活（2026-08-20予定）
                            を待つ。長期戦Task着手時は
                            `long_running_mode_active`をtrueへ切替。
Exact Next Route          : ユーザーの次の判断待ち。
```
