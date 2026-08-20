# Auto-Compaction Recovery Drill — Cycle 7（通常運用・初のAuto Compaction記録）

```yaml
document_id: claude_auto_compaction_recovery_drill_cycle_7
status: evidence
phase: phase_2
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 18:29:42 JST
language: ja
created: Claude Code
```

## 1. 本Docの位置づけ

[claude_side_design_governor_operating_notes_ja.md](../../task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）第1節が定めるCompaction／Session Recovery手順の、7回目の実施記録である。過去6回（Cycle 1〜3はHash Manifest新設前、Cycle 4〜6は[claude_compaction_recovery_hash_manifest_ja.md](../../automation/claude_compaction_recovery_hash_manifest_ja.md)参照）は全てManual Compaction（`/compact`）を対象としていたのに対し、**本Cycleは初めてAuto Compaction（Context使用率逼迫による自動発動）を対象とする**点が異なる。

ユーザー指示の要旨：「残り4%だからもうすぐAuto-Compactionくる。いつも通りに復旧してくれ。Manualじゃなくて、Autoだから、エビデンスは残すように。」——Manual Compactionは運用メモ第3.6節により基本運用（事前にIndex最新性を確認してから計画的に実施）である一方、Auto Compactionは同節が「例外的・自然発生側の扱い」と位置づける事象であり、ユーザーは、両者を区別した上で、Auto側の発生についても通常のManual Cycleと同水準のEvidence記録を明示的に求めた。

## 2. 発生条件・直前の状況

2026-08-19 18時台、Context使用率が84%（Auto-Compaction発動の目安に近い水準）に達した時点で、ユーザーより「通常運用でのAuto-Compaction Recovery動作確認の好機」として、Documentation RAG既知課題2件（§3.3・§3.7）の調査・実装Cycleを、その動作確認の実務的な題材とする方針が共有されていた。

Compaction発生の直前までに完了していた作業：

- §3.3・§3.7 Pattern 1・Pattern 2の根本原因調査（[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../../../phases/phase_2/history/operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)）。
- `top_k`を4→8へ引き上げ（`config/feature_profiles/local_documentation_rag.toml`・`lightning_public_documentation_rag.toml`の両方）。
- Pattern 2（無関係質問への誤発火）の修正設計に向けた実測調査（3本のScratchpad Probe Scriptによる、実際のRAG Compositionを用いたScore実測）。**この実測の結果、Score絶対値・Score内訳（Heading／Body／Exact-phrase）・`identifier_subject_count`のいずれの信号も、単独では「関連する質問」と「無関係な質問」を確実に分離できないという、当初想定（「無難な範囲のTuningで直せる」）を覆す知見が得られた**（例：本来RAGが答えるべき正当な広範質問「このProjectの目的は何ですか？」が50.2点、無関係な質問「リポビタンDの成分は？」が48.5点と、ほぼ同点だった）。この知見はユーザーへ報告済みだが、Pattern 2をどう扱うか（無難な範囲での部分的Mitigationを試みるか、RAG丸々改善Phaseまで見送るか）についての最終判断は、本Cycle開始時点でユーザーからの回答待ちのまま継続中である。

## 3. 復旧手順の実施記録（運用メモ第1節準拠）

1. **運用メモ本文の明示的再読込**：全文を再読込し、Compaction Recovery手順（第1節）・最上位規則（第2節）・上位規則（第3節）・通常規則（第4節）を再確認した。
2. **長期戦運用Companionの`long_running_mode_active`確認**：`false`（非Active）を確認。したがって本Cycleは**通常運用でのRecovery**であり、[claude_side_long_running_automation_companion_ja.md](../../task_roles/claude_side_long_running_automation_companion_ja.md)第2節（無確認Autonomy原則）・第4節（長期戦Mode運用）は適用対象外である——これは、ユーザーが以前「通常の方でいいので、いい機会だからAuto-Compaction recoveryの動作確認をしたいと思ってな」と述べていた方針とも整合する。
3. **Active PhaseのCurrent Operational State Index確認**：[claude_side_phase_index_ja_20260819181056.md](../../../phases/phase_2/history/index/claude_side_phase_index_ja_20260819181056.md)を再読込し、そこが指す最新Recovery Index（[claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md](../../../phases/phase_2/history/handoffs/claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md)）を辿った。
4. **必要Evidenceの個別参照**：会話Summaryに保持されていた情報と、上記2Indexの内容が完全に一致することを確認した（第4節参照）。追加のEvidence個別参照は、本Cycleでは不要と判断した（Summary自体がLossless水準で全経緯を保持していたため）。

## 4. Hash検証（運用メモ第3.10節・第3.13節準拠）

Auto Compactionは事前検知ができないため、Compaction直前のBefore Hash取得ができなかった。これは運用メモ第3.10節が定める「片側（多くはCompaction後）のみのHash」のケースに該当する。同節の指示に従い、次の補助的Evidenceと組み合わせて検証した。

- **After Hash（Best-effort、Compaction Recovery Hash Manifest記録）**：[claude_compaction_recovery_hash_manifest_ja.md](../../automation/claude_compaction_recovery_hash_manifest_ja.md)Cycle 7参照。運用メモ本文・長期戦運用Companion・最新Phase Index・最新Recovery Indexの4Fileについて、Compaction Recovery後の再読込時点でのSHA256を記録した。
- **後継File非存在確認**：`docs/project/phases/phase_2/history/index/`・`docs/project/phases/phase_2/history/handoffs/`の両Folderを走査し、2026-08-19 18:10:56 JST作成の両Fileより新しい後継Fileが、本Cycle開始時点で存在しないことを確認した。
- **再読込内容と会話Summaryとの一致確認**：会話Summary（Auto Compaction直前に生成）には、Phase Index・Recovery Indexの主要節の要旨、RAG両課題の調査結果、`top_k`変更後のToml設定値（`top_k = 8`）等が具体的に記録されていた。再読込した実File内容（本Doc第2節参照）と照合し、細部（Toml数値、File名、リンク先等）を含め、齟齬が無いことを確認した。

以上3種の補助的Evidenceにより、Before Hashが無い状態でも、Compaction前後で実質的な情報欠落は生じていないと判断する。

## 5. 結論・Cycle間の位置づけ

**復旧成功。運用メモ第1節・Hash Manifest第2節のCompaction Recovery成功回数を6→7へ更新した（本File作成と同時に反映済み）。**

過去のManual Compaction Cycle（4〜6）との違いは、Before Hashを事前に計画的に取得できたか否かの一点であり、復旧手順自体（運用メモ第1節Step 1〜4）は完全に同一の手順で実施し、同様に完了した。これにより、**運用メモ第1節の復旧手順が、Manual／Auto双方のCompaction契機に対して同等に機能する**ことを、実測ベースで初めて確認した。

Pattern 2（RAG無関係質問への誤発火）の設計方針は、本Cycleの対象外（Recovery完了後の継続作業）として、[claude_side_phase_index_ja_20260819182942.md](../../../phases/phase_2/history/index/claude_side_phase_index_ja_20260819182942.md)（本Cycleの後継Phase Index）へ引き継ぐ。
