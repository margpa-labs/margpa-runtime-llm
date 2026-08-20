# 長期戦Companion確立・RAG修正着手前 Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_20260819181056
status: index
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-19 18:10:56 JST
language: ja
purpose: |
  前回Recovery Index
  [claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md]
  （以下「前回Index」、2026-08-19 14:46:37 JST作成）以降に行われた作業を
  対象とした、続編Index。

  ユーザー指示：Documentation RAG既知課題2件（§3.3・§3.7）へ実装着手する
  前に、通常運用（長期戦Companionは非Active）でのAuto-Compaction Recovery
  動作確認を兼ねて、最新Index 2個を作成する。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** 第1節Step 2で、[claude_side_long_running_automation_companion_ja.md](../../../../shared/task_roles/claude_side_long_running_automation_companion_ja.md)（長期戦運用Companion）の`long_running_mode_active`フラグを確認する指示があります——**本Time点では`false`（非Active）です。** 通常運用のまま、前回Indexを読み、その後で本Docの第1節以降を読んでください。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止。

## 1. 前回Indexとの関係

[claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md](claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md)（14:46:37作成）は、Phase 2-E-I実機Feedback対応一式の完了と、Phase 3引き継ぎ計画（Codex復活・definitions.zip確認）の共有までを対象としていた。

本Docは、それ以降（14:46:37〜18:10:56、約3時間24分）に行われた作業を対象とする。この間、長期戦運用Companion Docの確立（複数回の是正Cycleを含む）、Failure記録、そして本題であるDocumentation RAG既知課題2件の根本原因調査を行った。

## 2. 前回Index以降の作業内容

### 2.1 長期戦Automation運用設計の検討

ユーザーより、Auto-Compaction検知限界・Phase Index/Recovery Indexの役割分担・判断依存型Mode切替のRisk等について、11Turnにわたる検討があった。詳細は[claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md](../../../../shared/history/automation/claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md)。

帰結として、[claude_side_long_running_automation_companion_ja.md](../../../../shared/task_roles/claude_side_long_running_automation_companion_ja.md)（運用メモ・Hash Manifestと並ぶ第3の自己編集可能Stable File、運用メモ第1節Step 2で指定）を新規作成した。長期戦Mode中のDocumentation軽量化運用・Step境界の粒度Self-check・無条件Re-read・Auto-Compaction Hash Tracker設計・作業時刻Evidence化を定める。

### 2.2 是正Cycle（History File直接編集・軽量化原則違反・配置Miss等）

Companion Doc確立の過程で、次のFailureが連続して発生し、都度ユーザー指摘により是正した。詳細は[claude_long_running_automation_hash_tracker_and_timing_evidence_refinement_ja_20260819165350.md](../../../../shared/history/automation/claude_long_running_automation_hash_tracker_and_timing_evidence_refinement_ja_20260819165350.md)、および共通根本原因の総括として[claude_output_anomaly_long_running_docs_construction_repeated_failure_ja_20260819173106.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_long_running_docs_construction_repeated_failure_ja_20260819173106.md)。

```text
1. 既に完了宣言済みのHistory Evidence Docへ直接追記（history/配下＝
   新規作成のみの原則違反）→ 取消・原状復元し、正しい形で新規File化。
2. 「長期戦Docsは軽量であるべき」という自らの設計目的に反する分量
   → Companion Doc・Hash Tracker双方を圧縮。
3. Companion Docの中核Ruleが、無関係な運用メモ第3節へ配置
   → 運用メモ第1節Step 2へ移設、旧節は完全削除。
4. 参照元に存在しない「Status」節を確認せず追加 → 両File削除。
5. 全File横断の整合性確認で、削除済み節への現在形参照が複数残留
   → ユーザー指示「整合性完全か確認しろ」を受けて自ら発見・是正。
```

現Companion Doc・Hash Trackerは、運用メモ第1節・第3.13節が指定する自己編集可能Stable Fileとして、上記是正を経た最終形で確立している。

### 2.3 無確認Autonomy原則の追加

ユーザーより、Companion Doc（長期戦Mode専用）へ最上位Ruleとして「作業中は一度もユーザーへ確認を求めない」旨の追加指示があった。Companion Doc第2節として新設し（既存節は第3・第4節へ繰下げ）、適用範囲を運用メモ第2.2節のEscalation Gateに限定し、Git禁止等の絶対的禁止事項は不変である旨を明記した。続けて「よっぽどなら止めていい」という例外条件（指示範囲・Scope・Rules・Governanceの範囲内に限定）が追加され、反映済み。

### 2.4 Documentation RAG既知課題2件の根本原因調査（実装前）

ユーザーより、Context使用率84%でのAuto-Compaction Recovery動作確認を兼ねて、Documentation RAG既知課題2件（§3.3・§3.7）へ着手する意向が示された。「実装／修正はまだ入らず、調査だけ」という明示指示を受け、Code Levelでの根本原因調査のみを行った。詳細は[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。

要旨：

- **§3.3（既存Known Issue）**：既存分析はCode Levelで再確認済み、Driftなし。
- **§3.7 Pattern 1（検索結果固定化）**：§3.3と**同一のSubject Coverage保証機構**が原因と新たに判明。`bm25_retriever.py`の`_coverage_candidate()`が、Query内の高Signal識別子（"LLM"等）ごとに決定論的に同一Chunkを強制選択するため、同じ識別子を含むQuery群は結果がほぼ固定化する。
- **§3.7 Pattern 2（無関係質問への誤発火）**：Stopword除外の不在＋`minimum_score=0.1`という低閾値＋Corpus全体のConfidence Gate不在の複合が原因。

ユーザーより、直後に次の実装指示があった（本Doc作成時点で未着手）：「top_k=4を無難な範囲で引き上げる（`documentation_subject_coverage_insufficient`Errorの頻度緩和）。§3.3・§3.7 Pattern 1・Pattern 2の両方（実質的に3事象）へ対応する。」

## 3. 現在の状態（2026-08-19 18:10時点）

**長期戦運用Companion体制は確立済み（`long_running_mode_active: false`、非Active）。Documentation RAG既知課題2件は根本原因調査完了・実装未着手。** 本Recovery Index作成直後、top_k引き上げおよびRAG両課題への実装対応に着手する予定。この実装Cycle自体が、通常運用でのAuto-Compaction Recovery動作確認を兼ねる。

## 4. Status

```text
Current Point            : 長期戦Companion確立・是正完了。RAG既知課題2件
                            の根本原因調査完了、実装未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : NONE
Controller-owned Next Work: top_k引き上げ、§3.3／§3.7 Pattern 1・2への
                            実装対応。
Exact Next Route          : 第3節参照。
```
