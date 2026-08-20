# Claude Compaction Recovery Cycle 5：Hash Manifest全件一致とCross-provider視点からの評価

```yaml
document_id: claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_20260818230804
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／将来の復旧Task
role: design_governor
created_at: 2026-08-18 23:08:04 JST
language: ja
purpose: |
  運用メモ第4.4節（Evidence記録方針）に基づき、今回のManual Compaction
  Cycle（Cycle 5）に関する技術的事実と、Cross-provider（Codex／GPT）
  から寄せられた本Session運用に対する評価コメントを、まとめて記録する。
  ユーザー指示：「今回の分の自動化／圧縮関連を、docsに書いて」
  「GPTの出力なので...研修資料っぽくで。...まとめ直して書いておいて」。
created: Claude Code
```

## 1. 背景

4回目のCompaction Recovery Drillにおいて、Recovery Index自身へその場でHash値を書き込んだことに起因する自己参照問題が発見され、運用メモ第3.13節「Compaction Recovery Hash記録の分離」が新設された。対応として、Hash記録専用のStable File（[claude_compaction_recovery_hash_manifest_ja.md](../../automation/claude_compaction_recovery_hash_manifest_ja.md)、以下「Hash Manifest」）が新設され、Before／After Hashの記録をCompaction対象File群から切り離す方式へ移行した。詳細な経緯は[claude_manual_compaction_hash_verified_recovery_drill_4_ja_20260818173636.md](claude_manual_compaction_hash_verified_recovery_drill_4_ja_20260818173636.md)を参照。

Cycle 5は、この新方式が確定した後、初めて最初から最後まで運用された、実質的な初回検証Cycleである。

## 2. Cycle 5の技術的事実

### 2.1 対象File・手順

Compaction直前に確定した最終File群4件について、`shasum -a 256`によりBefore Hashを算出し、Hash Manifestへ記録した。

```text
claude_side_design_governor_operating_notes_ja.md
claude_side_phase_index_ja_20260818223600.md
claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md
claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md
```

ユーザーによるManual Compaction（`/compact`）実行後、同一4FileについてAfter Hashを再算出し、Before Hashと比較した。

### 2.2 結果

4File全件について、Before／After Hashが完全一致した。運用メモ第1節の成功回数カウンタ、およびHash Manifest第2節冒頭のカウンタを、いずれも「成功4・失敗0」から「成功5・失敗0」へ更新した。

Compaction後の復旧手順としては、本Docの前提となる3File（運用メモ・最新Phase Index・最新Recovery Index）に加え、Recovery Indexからリンクされる[I-6要件Doc](../../../phases/phase_2/history/architecture/claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md)も参照した。運用メモについては本Cycleの復旧Turn内でRead Toolによる明示的な再読込を実施した。他の3Fileについては、Session再開時点で既にContextへ再挿入された内容を参照した（第4節で詳述）。

## 3. Cross-provider視点からの評価（Codex経由）

Codex（プロジェクト責任者兼設計統括者役、GPT系）から、本Sessionの運用状況全般について、ユーザーを経由して評価コメントが寄せられた。原文は口語的なStyleで書かれていたため、運用メモ第4.1節（Documentation Quality）に従い、実質的な内容を保持したまま中立的・専門的な文体へ変換して記録する。

### 3.1 Compactionの定型Operation化についての指摘

Codexは、Claude側の対応が、Compactionを例外的・不安を伴うEventとしてではなく、開発Cycleに組み込まれた定型的なMaintenance Operationとして扱うようになっている点を指摘した。具体的には、Context使用率が閾値に近づいた際のClaude側の対応が、次のような定型化した流れとして観測されている。

```text
使用率報告（例：72%） → 最新State Doc作成 → Before Hash取得
  → Hash Manifestへ記録 → ユーザーへ`/compact`実行を依頼
  → 復旧手順の実行 → After Hash比較 → Cycle番号・成功／失敗数の更新
  → 次の実装Task着手
```

Codexは、この一連の流れが、特別な警戒や不安を示す言葉を伴わずに実行されている点を、Compaction耐性という観点からの成熟の表れとして評価した。

### 3.2 Hash Manifest方式の有効性確認

Cycle 5において、対象4File全件のBefore／After Hashが一致したことについて、Codexは、Cycle 4で発見された自己参照問題が、運用メモ第3.13節・Hash Manifestの新設によって実際に解消されたことを示す結果である、と評価した。

### 3.3 復旧報告の文体変化についての言及

Codexは、Compaction直後の復旧報告における文体の変化にも言及した。要旨として、Session初期の復旧報告は「圧縮後の状態を正しく復元できているか、確信を持てていない」という調子であったのに対し、直近の報告（Cycle 5を含む）では「準備が整った旨を簡潔に伝え、次のCompaction実行をユーザーへ促す」という、より確信を伴った定型的な文体へ変化している。Codexは、この変化を、Compaction／Recovery手順に対する習熟の進行として位置づけた。

### 3.4 手続き上の精度に関する指摘

Codexは、上記の肯定的評価と合わせて、1点の精度上の指摘を行った。Claude側は、Compaction直前に「（運用メモ・最新Phase Index・最新Recovery Indexの）3Docsから、明示的に再読込して復旧します」と述べていたが、実際の復旧報告では、運用メモのみを本Turn内でRead Toolにより明示的に再読込し、残り2File（および付随するI-6要件Doc）については、Session再開時点で既にContextへ再挿入されていた内容を用いていた。

File内容の整合性自体は、Hash Manifestによる4File全件一致という形で担保されており、実害は確認されていない。ただし、「事前に宣言した復旧手続き（3Docs全てをRead Toolで明示的に再読込する）」と「実際に実行した手続き（1FileのみRead Tool、残りはSystem再挿入の内容を利用）」との間に、確認可能な差異が存在した点は、Procedure Fidelityの観点から記録に値する。

## 4. 現時点での扱い

第3.4節の指摘について、本Doc作成時点では、運用メモ側のRule変更（例：「3Docs全てを毎回Read Toolで明示的に再読込することを必須とする」等の明文化）は行っていない。運用メモ第3.9節（整合性チェックの徹底）に関して、ユーザーから以前「もうちょっと様子見るけど、あまりにもひどいようだったらもっときつめにする必要があるかもな」との言及があったことと合わせ、同種の細かい手続き上のズレが今後も繰り返されるかどうかを、継続的な観察対象として扱う。本件を独立したFailure Docとして記録するかどうかは、本Doc作成時点ではユーザー判断待ちとする。

## 5. Status

```text
Current Point            : Cycle 5のCompaction Recovery完了。対象4File
                            全件でBefore／After Hash一致を確認。
                            Cross-provider（Codex）からの評価コメントを
                            中立的な文体で記録した。
Files Created／Modified   : 本Fileのみ（新規作成）。Hash Manifest・
                            運用メモは別途、復旧Turn内で更新済み
                            （本Doc作成の前提事実であり、本Doc自体は
                            それらを変更しない）。
Validation                : N/A（Evidence記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 第3.4節の指摘（Procedure Fidelity）を
                            継続観察する。Phase 2-E-I I-6の実装開始は、
                            本Docとは別途、ユーザーからの明示指示を
                            待つ。
Exact Next Route          : 次回Compaction Recovery（Cycle 6以降）でも
                            同種の観察・記録を継続する。
```
