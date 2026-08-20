# Automation／Cross-provider Governance Evidence — 長期戦Auto-Compaction Hash Tracker詳細化・作業時刻Evidence化

```yaml
document_id: claude_long_running_automation_hash_tracker_and_timing_evidence_refinement_20260819165350
status: evidence_record
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 16:53:50 JST
language: ja
related:
  - claude_long_running_automation_strategy_design_discussion_ja_20260819162822
    （前回Evidence、本Docの直接の前提）
  - claude_side_long_running_automation_companion_ja（本Docの帰結を反映）
```

## 1. 背景

[claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md](claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md)（前回Evidence）公開後、ユーザーより2点の追加要望が示された。

## 2. 追加要望

### 2.1 Auto-Compaction専用Hash Tracker

前回Evidence第2.6節・第2.8節で「軽量なCount記録」として構想されていた仕組みについて、単純な発生Count記録に留めず、既存Hash Manifestと同一粒度（成功／失敗理由を含む）でBefore／After Hash比較も試みたいとの要望があった。

Auto-Compactionは発生Timingを選べないため、専用のBefore Hash取得Timingは設けられない。そのため、Step境界（Index更新Timing）ごとに、その時点の最新2FileのHashを機械的にBefore Hashとして記録するRolling Baseline方式とし、Auto-Compactionを事後的に認識できた場合にのみAfter Hashを取得して比較する、というBest-effort（ユーザー表現：「ダメ元」「成立すれば僥倖」）な設計とした。既存Hash Manifestとは別File、成功0件・失敗0件から開始する。

### 2.2 作業開始時刻・所要時間のEvidence化

長期戦Task着手時の作業開始時刻を明示的に記録し、既存のIndex作成ごとの`created_at`と合わせて、Step間の所要時間・全体の経過時間を事後的に再構成できるEvidenceとして位置づけたいとの要望があった。

## 3. 発見された運用上のFailure：History File直接編集

上記2点の要望を反映する過程で、Claude側は次の2つの対応を行った。

1. [claude_side_long_running_automation_companion_ja.md](../../task_roles/claude_side_long_running_automation_companion_ja.md)（Stable File）第3.4節・第3.5節への反映——これは正しい対応である（同Docは運用メモ第3.15節が指定する自己編集可能Stable Fileであるため）。
2. **前回Evidence（`claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md`）自体への直接追記**——これは誤りであった。

ユーザーより「キミの悪い癖が出てるぞ。運用メモ見返してみ？」との指摘を受け、運用メモ第2.1節「Docs Write境界」を確認した。

```text
Docs Write: 無許可で書ける = 各`history/`配下のAppend-only File（新規作成のみ）
```

`history/`配下のFileは「新規作成のみ」が原則であり、既存Fileへの追記・書き換えは想定されていない。前回Evidenceは既に第4節Statusで完了を宣言した「閉じた」History Recordであり、これへ事後的に内容を追記する行為は、Cycle 4で発生した「Recovery Index自身へその場でHash値を書き込んだ結果、Hash算出後の追記によってRecovery Index自身のHashが事後的に変化する」という自己参照問題（Hash Manifest新設の直接の契機）と、構造的に同種の誤りである。ユーザーから該当Fileを名指しで「追記して」と明示指示されたことをもって、指示への表面的な準拠を優先し、より上位にあるHistory Append-only原則との緊張関係を検知・提起しなかった点が問題であった。

是正として、前回Evidenceへの直接追記を取り消し、原状（初版公開時点の内容）へ復元した。本Doc自体を、前回Evidenceの後続Append-only Fileとして新規作成することで、正しい形へ改めた。

## 4. 帰結（実装内容）

- [claude_side_long_running_automation_companion_ja.md](../../task_roles/claude_side_long_running_automation_companion_ja.md)第3.4節を「軽量Compaction Count Tracker」から「長期戦専用Auto-Compaction Hash Tracker」へ改訂し、Rolling Baseline方式のBefore Hash取得・事後After Hash比較・Best-effort（ダメ元）である旨を明記した。
- 同Doc第3.5節（新設）：作業開始時刻の明示記録、Index`created_at`を所要時間Evidenceとして位置づける方針を追記した。
- [claude_long_running_auto_compaction_hash_tracker_ja.md](../../automation/claude_long_running_auto_compaction_hash_tracker_ja.md)：既存Hash Manifestと同一形式のTrackerを、成功0件・失敗0件から新規作成した（Stable File、`docs/project/shared/automation/`配下）。
- 前回Evidenceへの直接追記を取り消し、原状復元した。

## 5. Status

```text
Current Point            : Auto-Compaction Hash Tracker・作業時刻Evidence
                            化の設計を確定・反映した。並行して、History
                            File直接編集というFailureを発見・是正した。
Files Created／Modified   : docs/project/shared/task_roles/
                            claude_side_long_running_automation_companion_ja.md
                            （第3.4節改訂・第3.5節新設）、
                            docs/project/shared/automation/
                            claude_long_running_auto_compaction_hash_tracker_ja.md
                            （新規）、claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md
                            （誤追記の取消・原状復元）、本Evidence File
                            （新規）。
Validation                : N/A（設計Discussion記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 長期戦Task着手時、`long_running_mode_active`
                            をtrueへ切替、作業開始時刻を記録する。
Exact Next Route          : Phase 3設計完了・Codexからの引き継ぎ待ち。
```
