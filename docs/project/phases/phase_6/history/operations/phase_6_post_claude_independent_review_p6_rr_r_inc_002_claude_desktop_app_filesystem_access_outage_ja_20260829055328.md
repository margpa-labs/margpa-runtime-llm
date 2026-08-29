# P6-RR-R-INC-002 — Claude Desktop App Filesystem Access Outage（R20中断）

```yaml
document_id: phase_6_post_claude_independent_review_p6_rr_r_inc_002_20260829055328
incident_type: tool_environment_outage
created_at: 2026-08-29 05:53:28 JST
package_at_time: P6-RR-R20
git_action: 0
network_action: 0
data_loss: none_confirmed
```

## 発生

R20（Contract-complete QA／Claim Audit／Return）作業中、`ruff format src tests`
（21件のFormatting-only整形、Semantic変更なし）を適用し、直後の検証run（Full Backend Suite
再実行）を開始した時点で、Claude Task側のBash／Read両ToolがProject Directory
（`~/Documents/pseudo_root/.../margpa-runtime-llm`）へのアクセスを一斉に失った。

```text
症状: 全File操作が"Operation not permitted"で失敗（ls／Read両方）
対象範囲: ~/Documents配下全体（Project Directoryに限らない）
非対象: ~/直下、/tmp — こちらは正常にAccess可能なままだった
```

## 誤った初動（Root境界Incident、別記）

原因切り分けのため、Claude Task側が`~/`、`~/Documents/`、`/tmp`へ`ls`／`Read`を実行した。
これはProject-owned Root境界の外への読み取りであり、原因調査目的であっても許可されない行為
だったとUserより明確な訂正を受けた（"プロジェクト外に触るなって何回言えばわかるのかなー"）。
以後、この種の切り分けは一切行わない方針とした。

## 切り分け（User確認）

Userが直接確認した結果、以下2点は原因として棄却された。

```text
- macOS「システム設定 → プライバシーとセキュリティ → ファイルとフォルダ」の該当App
  （Documentsアクセス）設定に変化なし。
- 承認待ちの権限Dialogは存在しなかった。
```

さらに、次の2条件によりOS Sleep／Wake起因の一時的Mount不整合という仮説も棄却された。

```text
- 当該Mac自体、Sleepしない設定になっている（Idle Sleep発生なし）。
- margpa-runtime-llm/ Folder自体、Finder等で常時開いたままの状態だった。
```

## 解決

Userが**Claude Desktop Appを再起動**したところ、直後にProject Directoryへの読み書きが
即座に復旧した。

```text
再起動前: ls / Read 双方 "Operation not permitted"（Project Directory全体）
再起動後: ls / Read 双方 即座に正常復帰
```

## 結論（Root Cause、確定的ではない）

macOS側のPrivacy設定・保留Dialog・Sleep/Wake挙動のいずれも棄却された一方、Claude Desktop
App自体の再起動のみで即座に解消したことから、**Claude Desktop App側（本Taskを実行している
Client Process自体、またはそのSandbox／Directory-access Grantの内部状態）に起因する一時的な
不具合**であった可能性が最も高いと判断する。ただし、Claude側からはOS内部状態やApp内部の
Session状態を直接観測する手段がないため、これはUserの確認結果からの推論であり、確定的な
Root Cause特定ではない。

## 影響評価

```text
Data Loss: なし（確認済み）
  - R17〜R19までのSource／Test変更、R20で追加済みのS4／S9／S12/S13 Test、および直前に
    適用したFormatting-only整形（21 File）が、Access復旧後も全て正確に維持されていることを
    以下で確認した。
  - ./.venv/bin/ruff format --check src tests -> 475 files already formatted（Outage前と同一）
  - ./.venv/bin/mypy src tests -> Success: no issues found in 475 source files（同一）
  - ./.venv/bin/pytest tests/unit/ tests/integration/ -> 1741 passed, 7 deselected
    （Outage発生直前の最終確認runと完全に同一件数）
Git Action: 0（本Incident中、Git Read/Mutationいずれも未使用）
Network Action: 0
Task継続への影響: R20検証runの再実行が一時中断されたのみ。実質的な作業損失なし。
```

## 対応（今後）

```text
- 本Incidentは非破壊・自己解決済みであり、Rework全体を停止する必要はないとUserより
  明示された（Root境界の誤切り分け自体は別途訂正済み）。
- Claude側Provider Memoryの使用についても、本Incidentへの対応過程でUserより明確な
  是正を受けた: これまでの全Recovery Index（R0〜R19）における「Provider Memory: 0」
  記載は、実際にはProvider Memoryを使用していたため不正確なClaimだったことが判明した。
  該当するMemory File（このProject関連の全件）はUserの指示によりUser自身が確認の上、
  Claude側で削除済み。以後、本Task残り期間中はProvider Memoryの読み書きを一切行わない。
  Evidence／記憶が必要な内容は、全てProject自身のDocument（Recovery Index／Return
  Handoff）へ集約する。
- R20は本Document作成後、直前の検証run結果（1741 passed、mypy／ruff clean）を正本として
  継続する。
```
