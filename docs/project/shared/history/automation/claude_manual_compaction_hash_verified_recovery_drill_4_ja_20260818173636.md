# Manual Compaction Recovery Drill（4回目）：Before/After Hash比較を伴う初の完全実施

```yaml
document_id: claude_manual_compaction_hash_verified_recovery_drill_4_20260818173636
status: evidence
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（将来の参照用）
role: design_governor
created_at: 2026-08-18 17:36:36 JST
language: ja
purpose: |
  運用メモ第1節「現在のCompaction Recovery成功回数」が3→4へ更新された
  今回のManual Compaction Recovery Drill（4回目）について、第4.4節
  （Evidence記録方針）に基づき、新規Append-only Fileとして記録する。
  既存Evidence File
  [claude_manual_compaction_automation_verification_ja_20260818135529.md]
  （以下「前回Evidence」）の第6節へ追記はしない——本Fileが独立した
  4回目のRecordである。
created: Claude Code
```

## 0. 位置づけ（本Drillの新規性）

過去3回のDrill（前回Evidenceの第6節参照）は、いずれもCompaction後の状態を、再読込内容の一致確認・（一部は）Compaction後のみのFile Hashで検証していた。運用メモ第3.10節「Hash比較による検証の厳密性」——片側（Compaction後）のみのHashは弱いEvidence、という指摘——は、直前のDrill（3回目）の振り返りの中で新設されたが、その新設直後の最初の適用機会自体で、Compaction直前Hashの取得を一度失念する、という抜け漏れが発生していた（ユーザーの直接指摘「あれ？sha256とった？」により発覚、[claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md]が記録するPatternの再現例として記録済み）。

**本Drill（4回目）が初めて達成したこと**：

1. Compaction**直前**（2026-08-18 17:21:05 JST）に、対象4File分のSHA256を実際に算出し、Recovery Index第6節へ記録した状態でCompactionへ入った。
2. Compaction**後**（2026-08-18 17:31:35 JST）に、同一4Fileの SHA256 を再算出し、直前Hashと直接比較した。
3. 比較の結果、**単純な全一致ではなく、1件の意味のある不一致が実際に発生し、それを正しくTriageできた**（第3節参照）——これは、Hash比較手法そのものが「実際のData損失」と「想定内の自己参照的な差異」を区別できるかを試す、初めての実地Testでもあった。

また、復旧対象自体も、前回までの2文書（運用メモ＋Phase Index）から、ユーザー明示指示「いつも通り、docs 3つから復旧してくれ」により**3文書**（運用メモ＋Phase Index＋Recovery Index）へ拡張された初回でもある。

## 1. 契機

ユーザーは、Phase 2-E-I（Context Window可視化機能）の設計確定後、実装着手前に意図的にManual Compactionを実施する方針を明言していた（「実装する前にcompactionやるから。まだやらないけど」）。これに先立ち、運用メモ第3.12節（Manual Compaction前のIndex最新性確認、本Session内で新設）の初回適用として、ユーザー指示「最新index 2個作って。その後一回compactionするから」により、Phase Index後継File（`claude_side_phase_index_ja_20260818171727.md`）とRecovery Index（`claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md`）を新規作成した。

続けてユーザーから「あれ？sha256とった？」との指摘を受け、対象4File（運用メモ／Phase Index／Recovery Index／2-E-I設計書）の圧縮直前SHA256を算出し、Recovery Index第6節へ記録した。

その後、ユーザーは「ほい。じゃ次かけるんで、いつも通り、docs 3つから復旧してくれ。」と述べ、`/compact`（Manual Compaction）を実施した。

## 2. 実施内容

Compaction直後、ユーザーから「状態は？」と問われ、次を実施した。

1. 運用メモ（`claude_side_design_governor_operating_notes_ja.md`）を明示的に全文再読込。
2. 最新Phase Index（`claude_side_phase_index_ja_20260818171727.md`）を明示的に全文再読込。
3. 最新Recovery Index（`claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md`）を明示的に全文再読込。
4. 対象4Fileの SHA256 を再算出し、Recovery Index第6節記載の圧縮直前Hashと直接比較。

## 3. 検証結果

```text
File                                                        | 圧縮直前Hash | 圧縮後Hash | 判定
claude_side_design_governor_operating_notes_ja.md            | f56df38…35dd  | f56df38…35dd | 一致
claude_side_phase_index_ja_20260818171727.md                 | 67efecc…1da6  | 67efecc…1da6 | 一致
claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md | 8cc9082…1619 | 8cc9082…1619 | 一致
claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md | 87bed92…824c | 2b3add0…5028 | 不一致（想定内）
```

4件中3件は完全一致。残る1件（Recovery Index自身）の不一致は、Data損失ではない。Recovery Index第6節自体が「圧縮直前Hashは、本節（第6節）をFileへ追記する**前**の内容に対して算出したもの」と明記しており、Hash算出後に同一Fileへ第6節を追記したことによる、既知・想定内の自己参照的な差異である（Recovery Index本文第6節に、この注記自体が事前に記載済み）。

再読込した3文書の内容（見出し構成、第3.10〜第3.12節、第2節「現在進行中のSub-phase」等）も、Compaction前のSummary記載内容と突き合わせ、欠落・文字化けなしを確認した。

## 4. Manual Compaction Recovery Drillとしての意味づけ

本Drillは、次の2点で、過去3回のDrillより検証の厳密性が一段階向上している。

- **真のBefore/After比較**：初めて、圧縮直前・直後の双方でHashを取得し、直接比較した。片側のみのHashでは検出できない「本当に一致しているか」を、機械的に確認できる状態になった。
- **不一致のTriage能力の実地確認**：単なる全一致ではなく、実際に1件の不一致が発生し、それが「Data損失」ではなく「想定内の自己参照的な差異」であることを、Recovery Index自身の記述と照合して正しく判定できた。これは、Hash比較手法が実運用で意味のある差異検出能力を持つことの、初めての実地証跡である。

## 5. 限定条件

- 本Drillが確認したのは、Docs（運用メモ・Phase Index・Recovery Index・設計書）の**File内容がByte単位で保持されている**ことであり、会話全体の細かいNuance（口調、細部の言い回し等）まで復元されることを意味しない。
- 本Drillは、Claude側設計統括者役が毎回、運用メモ第1節の復旧手順・第3.10節のHash比較手順を律儀に実行することが前提であり、この前提自体は本Drillの範囲外（過去に実際、第3.10節新設直後の最初の機会でHash取得自体を一度失念している——第1節参照）。

## 6. 通算Compaction Recovery Drill回数（4回目時点、成功4　失敗0）

```text
#  | 種別               | Recovery      | Before/After Hash比較 | 結果
1  | 狙ったAuto-compaction | 2文書        | 未実施                | わりと成功
2  | 狙ったAuto-compaction | 2文書        | 未実施                | やや不安定だったが、成功
3  | Manual Compaction     | 2文書        | 未実施（片側のみ検討） | 成功
4  | Manual Compaction     | 3文書（本Drill、Recovery Index追加） | 実施（本Drill、初）    | 成功
```

\#1〜3の詳細経緯は前回Evidence（[claude_manual_compaction_automation_verification_ja_20260818135529.md](claude_manual_compaction_automation_verification_ja_20260818135529.md)第6節）を参照。運用メモ第1節の成功回数は、本Drill完了に伴い3→4へ更新済み（Snapshot退避→編集→Diffによる意図外変更なしの確認済み）。

## 7. Status

```text
Current Point            : 4回目のManual Compaction Recovery Drill、
                            Before/After Hash比較を伴う初の完全実施
                            として完了。運用メモ第1節の成功回数を
                            3→4へ更新済み。
Files Created／Modified   : 本Fileのみ（新規作成）。運用メモの成功
                            回数更新は別途実施済み（本Session内、
                            本Doc作成の直前）。
Validation                : Hash比較（4File中3件完全一致、1件は
                            想定内の自己参照的差異と特定）。再読込
                            内容とCompaction前Summaryとの突き合わせ
                            も実施済み。
Open Current Blocker      : NONE。
Controller-owned Next Work: ユーザーからのPhase 2-E-I実装開始指示
                            待ち（I-2：Backend Context Usage露出、
                            から着手予定）。
Exact Next Route          : ユーザーの次の判断待ち。
```
