# Phase 6特殊最小Closure — Roadmap 2種／Claude前倒し作業一覧予約

```yaml
document_id: phase_6_special_minimal_closure_roadmaps_and_claude_forward_work_reservation_20260824172813
status: reserved
classification: planned_work
created_at: 2026-08-24 17:28:13 JST
activation_condition: phase_6_user_manual_acceptance_pass
implementation_authority: false
```

## 1. 決定

Codex利用可能量を保全しつつPhase 6を安全に閉じるため、Phase 6 Closureは今回も特殊最小Closureとする。Manual Acceptanceで重大問題が残る場合は先に差分Reworkを行い、Closureを先行させない。

通常の最小Closure Evidenceに加え、次の3件だけを必須追加作業とする。

1. `docs/public/roadmap_ja.md`の更新。
2. `docs/public/roadmap_summary_ja.md`の更新。
3. Phase 6終了時点から後続Phaseへ前倒し可能な作業を整理した、新しいClaude向け一覧の作成。

大規模なDocs全統合、Phase 3〜6のLossless再編成、Portable Package作成およびPhase 9／10 Closure作業は再活性化しない。

## 2. Roadmap 2種

### 2.1 詳細Roadmap

`docs/public/roadmap_ja.md`

- Phase 6の実際のAccepted範囲、残るDeferred、DeepSeek Support dispositionを反映する。
- Phase 7を次PhaseとしてReadyにする場合、そのEntry条件と順序を反映する。
- 汎用File AttachmentのSizing予約、Phase 9 Context Panel更新、Phase 10以降のMultimodal／Long Context予約を反映する。
- 未完了、未検証、将来予約を実装済みとして書かない。

### 2.2 人向けRoadmap要約版

`docs/public/roadmap_summary_ja.md`

- Phase 6 Closure時点の進捗表と現在の成果を短く更新する。
- 詳細設計やHistoryを大量転記せず、人が現在地と次のPhaseを把握できる粒度を維持する。
- Automation／Cross-provider／Compaction／Agent間役割分離の研究成果も、成立範囲だけを簡潔に反映する。

## 3. 新しいClaude前倒し可能作業一覧

Phase 3時点の既存一覧を上書き正本化せず、Phase 6 Closure時点の新しい一覧をAppend-onlyで作成する。

予定Path：

`docs/project/shared/history/planned_work/post_phase_6_claude_forward_execution_candidates_ja_<timestamp>.md`

最低限、次を分類する。

- Phase 7以降で依存なしに前倒しできるRead-only調査。
- Design／Inventory／Test Matrix／Fixture作成。
- 実装可能だがCodex Reviewを必須とする作業。
- Model／Network／AWS／外部Side Effect／Git等のHuman Gate必須作業。
- Current Phaseの正本や実装と競合するため前倒し禁止の作業。
- Auto-Compaction／5時間制限後もRecovery可能なWork Unit境界。
- Completion Candidate後にClaudeが停止し、Codex Independent Reviewへ返す契約。

一覧は候補であり、Claudeへの実行Authority、Phase開始、Network、Gitまたは外部操作を自動付与しない。

## 4. Manual Acceptance結果による分岐

```text
User Mac Manual Acceptance
  |
  +-- PASS
  |     -> Controller Phase 6 Closure判定
  |     -> 特殊最小Closure Evidence
  |     -> Roadmap 2種更新
  |     -> Claude前倒し作業一覧作成
  |     -> Phase 7 Ready手順
  |     -> Phase 7冒頭で汎用File Attachment Sizing
  |
  +-- ADJUST
        -> Manual Acceptance結果をUserへ先に報告
        -> 発見Bugを再現条件・影響・成立項目と分離して整理／記録
        -> Phase 6はIN PROGRESSのまま保持
        -> Roadmap 2種へ不具合と現在地を反映
        -> Claude前倒し作業一覧を作成
        -> Working TreeをCleanなCommit対象へ整理
        -> Commit / Push
        -> 利用可能量回復まで安全停止
        -> 回復後にPhase 6 Reworkと汎用File Attachment Sizing
```

Manual AcceptanceがADJUSTでも、利用可能量枯渇前の安全なCurrent State固定として、Roadmap 2種とClaude前倒し作業一覧の3文書更新、Clean確認、Commit／Pushまでは実施する。この経路ではPhase 6 Closure、Phase 7 Readyまたは汎用File Attachment Sizingを完了主張しない。

ADJUST判定直後にRoadmap更新やCommitへ飛ばない。まずUserへ実結果を返し、PASSした範囲、失敗した範囲、再現入力／出力、Severity、推定責務境界および未確認事項をBug一覧としてまとめる。その記録をCurrent State更新のInputにしてから、3文書更新とRepository固定へ進む。

## 5. 利用可能量枯渇時の安全停止

PASS後にPhase 6 Closureへ入った場合でも、Closure途中でCodex利用可能量またはCreditが尽きる可能性を前提にする。残量だけを理由に不正確なClosureを宣言せず、次のMaterial Boundaryで安全停止する。

- 実行中Command／Processを残さない。
- 完了済み範囲、未完了範囲、Current Work Unit、次のExact ActionをRecovery／Indexへ記録する。
- 部分的なRoadmap更新を完了扱いしない。
- Stage／Commit／Push途中へ入る前に残作業を評価し、中途半端なGit状態を作らない。
- Secret、Personal Data、`runtime_data`等をCommit対象へ混入させない。
- 利用可能量またはCredit追加はUser専有判断であり、自動的に期待・要求しない。

安全停止後は、利用可能量回復またはUserの明示的な再開指示を受け、Recovery記載の差分から続行する。

Commit／PushはUserの本予約による明示的な将来許可として扱うが、実行時にExact Target、Stage対象、Secret／Personal Data除外およびRemote一致を確認する。新しい重大問題や安全なCommit対象へ整理できない状態が見つかった場合は、破壊的修復を行わず停止する。
