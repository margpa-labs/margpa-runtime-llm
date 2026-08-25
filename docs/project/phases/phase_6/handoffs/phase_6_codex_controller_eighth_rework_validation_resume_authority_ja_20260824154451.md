# Phase 6 Eighth Rework — Validation差分再開Authority

```yaml
document_id: phase_6_codex_controller_eighth_rework_validation_resume_authority
status: exact_resume_authority_active
phase: phase_6
rework: eighth_rework_runtime_lifecycle_deadline_and_ui_revision_integrity
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-24 15:44:51 JST
resume_from: focused_validation
preserve_current_implementation: true
phase_closure_authority: false
git_mutation_authority: false
```

## 1. Controller Decision

`P6-RW8-INC-001`として、Focused Backend Test 2回をProject内`--basetemp`なしで実行し、
`tmp_path`を使う3 TestがProject Root外のOS Temporary Directoryへ一時Writeした事実を受理する。

```text
Root-outside Temporary Write : 1 Incident／2 Test Runs
Root-outside Inspection      : 0
Root-outside Cleanup/Delete  : 0
Persistent Product Impact    : 0 known
Product Source Integrity     : 影響なし
Disposition                  : RECORDED／STOPPED_SAFE／NON-BLOCKING FOR RESUME
```

Root外Temporaryを追加調査、列挙、Stat、Cleanup、Deleteしてはならない。Incidentを無かったことにせず、
Eighth ReworkおよびPhase 6の累積境界Evidenceでは次を保持する。

```text
P6-RW7-INC-001 : npm Root-outside Log Write Attempt
P6-RW8-INC-001 : pytest Root-outside Temporary Write
Cumulative Root-outside Incidents: 2
```

製品実装をRollbackまたは再実装する理由はない。RW8-A〜Cの現行実装、Backend Regression 4件、Frontend
Regression 1件およびFocused `52 PASS`／`56 PASS`を保持し、未完了のValidationから差分再開する。

## 2. Mandatory Resume Reading

1. `docs/project/phases/phase_6/history/index/phase_6_eighth_rework_project_temp_omission_stopped_safe_ja_20260824154229.md`
2. 本Authority。
3. `docs/project/phases/phase_6/handoffs/phase_6_codex_controller_eighth_rework_exact_handoff_ja_20260824152512.md`
4. `docs/project/phases/phase_6/history/operations/phase_6_gov012_seventh_rework_controller_independent_review_ja_20260824152512.md`

## 3. Exact Resume Boundary

1. Seventh Rework Package A〜Gを再実装・再実行しない。
2. Eighth Rework RW8-A〜CをRollback、作り直し、隣接Scopeへ拡張しない。
3. 現行Diffを照合し、Project内Task-owned Tempを作成してFocused Validationから再開する。
4. Focused ValidationがFindingを示した場合だけ、Eighth Rework Scope内で修正・Regression追加する。
5. Focused PASS後、Frontend、Canonical Static、Backend Full、Boundary Reviewを連結実行する。
6. 真のStop Condition以外では進捗報告を理由に停止せず、Complete CandidateをControllerへ直接返す。

## 4. Exact Task-owned Temporary Boundary

このResume Cycleでは次を唯一のTask-owned Temporary Rootとして使用する。

```text
<Authorized Root>/.venv/.t/phase_6_eighth_rework_resume_20260824154451/
```

開始時にProject内で次を作成する。

```text
pytest/
npm-cache/
tmp/
```

全pytest Commandは必ず次を含める。

```text
--basetemp=<Authorized Root>/.venv/.t/phase_6_eighth_rework_resume_20260824154451/pytest
```

Frontend Commandは必ず次の条件で実行する。

```text
workdir:
  <Authorized Root>/frontend

NPM_CONFIG_CACHE:
  <Authorized Root>/.venv/.t/phase_6_eighth_rework_resume_20260824154451/npm-cache

TMPDIR:
  <Authorized Root>/.venv/.t/phase_6_eighth_rework_resume_20260824154451/tmp
```

User Home、`/dev/null`、Root外Temporary、Provider Memory、User`runtime_data`を参照先・書込先に使わない。
Command前にWorkdirおよび出力先を文字列としてExact確認する。

## 5. Required Validation

### 5.1 Focused Backend

- Main Model LeaseとService Active Correlationがterminalまで分離維持される。
- Judge実行中のStopがCancellationへ到達し、`CANCELLED` exactly once、`completed` 0となる。
- ShutdownがJudge WorkerをCancel／Joinし、実行中Workerを残してclean終了を主張しない。
- Deadline到達後はCallerがterminal ownershipを持ち、Late WorkerがLast Result、Recording、Persistence、
  Repair、Responseを上書きしない。
- Timeout／Cancel／Exception時もMain Model LeaseとService Active Correlationを正しい順序で解放する。

### 5.2 Frontend

- Runtime Model Statusの古いResponseを破棄した場合、`settingsForm.maxNewTokens`も同じRevision Gateで破棄する。
- Main StatusとMax New Tokensが異なるResponse世代から混在しない。
- Latest response、Model switch、Context reload、Max New Tokens更新の既存経路を退行させない。

### 5.3 Integrated

- Exact focused Test。
- Canonical Mypy Scope。
- Ruff Format Check／Ruff Check。
- Backend Full。
- Frontend Typecheck／Lint／Test／Build。
- Root／Provider Memory／User Data／Git／Network／Model Artifact境界の差分再確認。

## 6. Evidence and Return Contract

Final RecoveryおよびReturn Handoffには最低限次を記録する。

```text
P6-RW8-INC-001: RECORDED／STOPPED_SAFE／RECOVERED／NON-BLOCKING
Eighth Resume Cycle Root-outside Action: 実測値
Eighth Rework cumulative Root-outside Incident: 1
Phase 6 cumulative known Root-outside Incidents: 2
Provider Memory Internal Contact: 実測値
User runtime_data Contact: 実測値
Git／Network／Model Artifact Mutation: 実測値
Task-owned Temporary Root: Exact Path
```

`Root-outside Action 0`、`Incident 0`、`全Process準拠`へ履歴を書き換えてはならない。Process IncidentとProduct
Acceptanceを分離し、実測していないReal Model／Metal／User BrowserをPASSへ昇格しない。

Phase 6 Closure、Phase 7、Roadmap、Git、Backupへ進まず、Eighth Rework Complete CandidateをControllerへ
直接返送して停止する。
