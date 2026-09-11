# Phase 9-2 全範囲 Independent Review 2 — UI Identity／Persistence Rework Handoff

- 作成: 2026-09-09 01:52:05 JST
- 判定: `CHANGES_REQUIRED`
- Review観点: Failure／非同期順序／再読込／Evidence表示の真実性
- 対象: Phase 9-2全範囲
- 修正対象: Confirmed Major 3件のみ

## 1. Review前提

Independent Review 1で指摘した4件のReworkは、対象Source確認とFocused Test `74 passed`により再確認済みである。本Reviewは観点を入れ替え、正常系の機能網羅ではなく、応答順序逆転、部分書込み、選択対象変更時に誤ったEvidenceを現在値として表示しないかを確認した。

## 2. Confirmed Findings

### IR-P9-2-WHOLE-R2-01 — MAJOR

`ExperimentPanel.refreshRunList()`は複数の非同期呼出しを識別せず、遅れて返った古いComparisonを無条件に`setComparison()`する。`handleRun()`は開始直後のRefreshをawaitせず、その後Terminal到達後にもRefreshするため、先行した古いResponseが後着し、Terminal Run一覧と古い／空のComparisonを同じ現在画面に混在させ得る。

要求:

- 同一Experiment内のRefreshに世代またはRequest tokenを持たせ、最新の有効なResponseだけがComparison状態を更新する。
- 新しいPlan作成／Experiment ID変更後に旧ExperimentのResponseが混入しない。
- 「Terminal状態を表示しているのにComparisonだけ古い」順序を決定的Testで再現し、修正前失敗・修正後PASSを証明する。

### IR-P9-2-WHOLE-R2-02 — MAJOR

`handleShowDetails()`は選択した`run_id`とResponseを相関せず、Aの取得後にBを選択した場合でも、遅れて返ったAのResponseがBのDetail EvidenceとExecution Mode表示を上書きできる。画面上はBが選択中なのに、AのInvocationまたはFixture／Production DisclaimerをBのEvidenceとして提示し得る。

要求:

- Detail取得Responseを選択中`run_id`および現Experimentへ相関し、古いResponseを破棄する。
- A→B選択後にAが遅着する決定的Testで、BのEvidence／Disclaimerだけが表示されることをHard Assertする。
- Detail取得失敗を未処理Promiseにせず、少なくとも誤った旧Detailを現在値として残さない。

### IR-P9-2-WHOLE-R2-03 — MAJOR

Plan作成Routeは`service.create_plan(plan)`でPlanを先に公開した後、各VariantのDesired Configuration Snapshotを別々に保存する。Snapshot保存が途中で失敗すると、HTTPは失敗しても永続Storeには既にPlanが存在し、必要Snapshotが欠落または一部だけ存在する。再試行はDuplicate Planで拒否され、Restart Read／Config相関の契約を回復できない。

要求:

- Planを可視なCommit pointとし、Planが読める時点では、そのPlanが参照する全Desired Snapshotも読める順序／Application境界へ変更する。
- 既存Planへ誤ってSnapshotを上書きしない。
- Snapshot保存途中の例外を注入し、Planが未公開のままか、再試行可能で完全状態へ収束することをTestする。
- 正常系でPlan Digest、Snapshot Digest、Variant相関、Restart Readが維持されることを確認する。

## 3. Scope／禁止事項

- 上記3件と直接必要な回帰Testだけを修正する。
- Cancel失敗時の表示改善など軽微なUXは今回扱わず、必要ならUnresolved Work候補として返す。
- 実Model、Browser実画面、User Manual、Phase 9-3、Phase 10、Git write、Commit、Push、Cleanを行わない。
- Phase 9-2 Complete／Closureを自己承認しない。
- 既存のUser変更および無関係なDirty Treeを変更しない。

## 4. Verification／Return

1. Findingごとの決定的Focused Test。
2. Phase 9-2 Backend／Frontend範囲Test。
3. Source変更範囲のRuff／Mypy／Frontend typecheck・lint・build。
4. 非Model Full Suiteは、費用対効果上必要と判断した場合のみ1回。
5. 修正前欠陥へ戻したSabotageで新規Testの検出力を確認し、元へ復元する。
6. 新規PathのExact ReturnとRecoveryをAppend-onlyで作る。既存文書を上書きしない。
7. 中間報告は禁止。完了時はController Taskへ必ず最終報告し、その後停止する。

