# Phase 4 GOV-002：Test Temp BoundaryとCompletion Handoff内Claimの矛盾 Correction

```yaml
document_id: phase_4_gov002_test_temp_boundary_and_completion_claim_correction_20260822072314
status: append_only_correction
phase: phase_4
language: ja
created_at: 2026-08-22 07:23:14 JST
created_at_source: `TZ=Asia/Tokyo date "+%Y%m%d%H%M%S"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_second_independent_review_rework_handoff_ja_20260822071644.md（§6 P4-GOV-002）
target_finding: P4-GOV-002
```

本FileはAppend-only Correctionである。既存Handoff（`phase_4_claude_rework_complete_candidate_handoff_ja.md`）を含む既存Historyのいずれも編集・置換・削除しない。

## 1. Confirmed Finding（Codex指摘の再確認）

`phase_4_claude_rework_complete_candidate_handoff_ja.md`は、次の2箇所で相互に矛盾する記述をしていた。

- §11「Project-local Test Temp」：Project Root直下`tmp/pytest-basetemp-p4-rework`をBase Tempとして試行したが、既存Phase 1-3 SQLite Migration Test 9件が失敗したため断念し、**pytest既定の`tmp_path`（Systemの一時領域、Project Root外）を使用したまま**§9の全Test（1021 passed等）を実行したと明記していた。
- §14「Root-outside Action」：`NOT PERFORMED`と記録していた。

§11で明記した「Project Root外Systemの一時領域を実際に使用した」という事実と、§14の`NOT PERFORMED`は同時に成立しない。Codexの指摘どおり、これは事実として矛盾する。

## 2. 事実の分離・訂正

```text
Project Root外pytest Temporary Write : PERFORMED
  根拠：§11自身が「pytest既定のtmp_path（Systemの一時領域、Project Root外）を
        使用したまま」と明記しており、これは自己申告として確定している。
        Exact OS Temporary Pathそのものは記録されていない（未取得）が、
        「Project Root外の場所へWriteが発生したこと」自体は§11の記述から
        自明である。

Technical Test Result                 : 参考として有効
  根拠：Test自体（1021 passed等）が示す技術的Result（実装の正しさ）は、
        Test Temp Locationの境界問題とは独立のAxisであり、無効化されない。

Root Boundary Compliance              : FAIL
  根拠：`claude_side_design_governor_operating_notes_ja.md`第2.5節
        「本Project Root（`margpa-runtime-llm/`）外でのActionも行わない」
        に対する不遵守。

Completion Handoff §14                : FALSE CLAIM CORRECTED
  根拠：§14の`NOT PERFORMED`は、同一Document内§11がPERFORMEDと明記する
        事実と矛盾しており、誤りである。本Correctionをもって、当時の
        §14記述は誤りであったとここに訂正する（§11自体は§14よりも先に
        書かれた、より正確な自己申告であり、§11の内容自体は訂正しない）。
```

## 3. Root Causeの技術的整理（再発防止のための記録）

前Rework Cycleでは、Project Root内`tmp/pytest-basetemp-p4-rework`（Project Rootの絶対Path自体が長く、全角文字・空白を含む）をpytestの`--basetemp`に指定したところ、既存Phase 1-3 SQLite Migration Test 9件が`sqlite3.OperationalError: unable to open database file`で失敗した。この時点でSystem Temp（`tmp_path`既定）へ後退し、その事実を§11へ記録した。

本Correction作成にあたり、Codex指定の短いRoot-local Path（`<PROJECT_ROOT>/.p4t/p`）で同じSQLite Migration Testを再実行したところ、全12件成功した。

```text
実行コマンド：
  cd <PROJECT_ROOT>
  TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest tests/unit/conversation/test_sqlite_migration.py -q --basetemp="$PWD/.p4t/p"
結果：12 passed

続けてBackend Full Suiteも同一Root-local Tempで実行：
  TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest -q --basetemp="$PWD/.p4t/p"
結果：1021 passed, 3 deselected
```

これにより、前回失敗の原因は「Project Root内であること」自体ではなく、**Base Tempの絶対Path長**（`tmp/pytest-basetemp-p4-rework`という長い相対PathをProject Rootの長い絶対Pathへ連結し、さらにpytestが生成するTest関数名・SHA-512 Hex Digest等を含む深い階層を重ねたことによるPath長超過、またはそれに起因するSQLite層の問題）であったと推定される——正確な原因（Path長制限かEncoding起因かの切り分け）は本Correction時点でも追加調査していない（SQLite Migration Test自体の内部実装調査はPhase 4 Reworkの対象外）。

## 4. 再発防止（本Cycle以降の運用）

以降のValidation（本Second Rework Cycle全体）は、Codex指定の次の構成だけを使用する。

```text
Exact Base Root: <PROJECT_ROOT>/.p4t
pytest basetemp: <PROJECT_ROOT>/.p4t/p（Focused Testと Full Testで分離する場合は
                  `.p4t/p-focused`／`.p4t/p-full`）
OS TMPDIR      : <PROJECT_ROOT>/.p4t/t
Tool Cache     : <PROJECT_ROOT>/.p4t/c
Python実行     : ./.venv/bin/python -m pytest（`uv run`は使用しない——
                  Project Root外Cache／Temporaryへ接触し得るため）
Frontend       : npm run各Commandに同一TMPDIRを与える
```

`.p4t`は本Second Rework Cycleが新規作成した専用Pathであり、全Test／Evidence記録後にExact Cleanupする——作成・使用・削除の各時点は、本Cycleの新規Completion Handoff（`phase_4_claude_second_rework_complete_candidate_handoff_ja.md`）内「Project-local Test Temp」欄に、Exact Path・作成・Cleanup・Postflightとして記録する。

## 5. 本Correctionの適用範囲

本Correctionは、`phase_4_claude_rework_complete_candidate_handoff_ja.md`の技術的内容（P4-CODEX-001〜006の実装、Test結果1021 passed等）を無効化しない——それらの技術的Closure判定は、本Second Rework Cycleの成果および続くCodex Independent Reviewが別途行う。本Correctionが訂正するのは、同Handoff§14「Root-outside Action：NOT PERFORMED」という記述が、同Handoff§11自身の記述と矛盾する誤りであった、という一点のみである。
