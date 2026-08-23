# Phase 3 Codex Fifth Independent Review — Governance Correction Handoff

```yaml
document_id: phase_3_codex_fifth_independent_review_governance_correction_handoff_20260821230804
status: docs_only_adjust_required
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_005_governance_correction
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-21 23:08:04 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_3/handoffs/phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md
completion_line: phase_3_claude_fifth_governance_correction_complete_candidate
source_mutation_authorized: false
test_execution_authorized: false
git_mutation_authorized: false
phase_3_closure_authorized: false
phase_4_authorized: false
```

## 0. Controller Decision

`DOCS-ONLY ADJUST`。

Fourth Reworkの技術実装はCLOSE可能である。

- `P3-CODEX-012`：CLOSED。
- `P3-GOV-004`のThird Rework Zero断定訂正：CLOSED。
- Backend Source Rework：不要。
- Test再実行：不要。

残るのは`P3-GOV-005`のAppend-only Incident／Evidence Classification Correctionだけである。本CycleでSource、Test、Config、Stable、Roadmap、Generated FileまたはGitへ進んではならない。

## 1. P3-GOV-005 — Test Temporary Root境界とEvidence Classの誤認

### 1.1 Confirmed Governance Finding A：`tmp_path`をTask Actionから除外した

Codex Fourth Exact Handoffは次を固定していた。

- Test／Validationを理由にProject Root外Temporary Artifactを作成しない。
- Test Temporary RootはProject Root内のWork Unit専用Directoryだけを使用する。
- Exact Path、作成、削除およびPostflight不存在をCompletion Handoffへ記録する。

Claude Fourth Rework Completion Handoffは、pytest標準`tmp_path`を使用した一方、次の理由で報告対象外と判断した。

```text
pytest自身が生成・管理・削除するため、Claudeが手動で作成したArtifactではない。
```

この判断は誤りである。Taskが起動したpytestによるFilesystem ActionもTask Actionであり、Tool／Framework／Child Processが代行したことを理由にAuthority／Path境界の適用対象外にはできない。

さらに、Project Root内の専用Base Tempを明示設定した記録とExact Path報告がない。したがって、少なくとも次は確定する。

- Project Root内Temporary Root Contractを満たしたEvidenceがない。
- Exact Path／作成／削除／Postflight Evidenceが欠落した。
- 「Framework管理なので報告対象外」というAuthority解釈が誤っていた。

OS Temporary DirectoryのExact Pathは未記録であり、今からProject Root外を調査、再作成、削除または事後推測してはならない。IncidentはEvidence欠落を含む境界違反として、そのままAppend-onlyで記録する。

### 1.2 Confirmed Governance Finding B：Evidence Source Classが不正確

Fourth Correction／Completion Handoffでは、過去のCommand実行結果と「Cycle中にGit Mutation 0」を`REPOSITORY_STATE_VERIFIED`へ分類した。

これは次のように分ける必要がある。

```text
過去のTest／Ruff／Mypy Command出力:
  Exact Tool Resultが保持されている場合 TOOL_LOG_VERIFIED
  Tool Resultを提示できない場合 SELF_REPORTED_UNVERIFIED

現在のHEAD／Status／File内容:
  現時点の再検査結果だけ REPOSITORY_STATE_VERIFIED

Cycle全期間のGit Mutation 0:
  完全なAction Logがある場合 TOOL_LOG_VERIFIED
  現在のHEAD／Statusだけなら SELF_REPORTED_UNVERIFIED

同じRepository状態で再実行可能:
  Reproducibility Claimであり、過去に実行した事実のEvidence Classとは別
```

現在状態から再現できることを、過去Command出力またはCycle全Actionの証明へ昇格させてはならない。

## 2. Required Correction

既存Handoff／Historyを編集・削除しない。次の新規2文書だけを作成する。

1. `docs/project/phases/phase_3/history/index/phase_3_gov005_test_temp_boundary_and_evidence_class_correction_ja_<timestamp>.md`
2. `docs/project/phases/phase_3/handoffs/phase_3_claude_fifth_governance_correction_complete_candidate_handoff_ja.md`

Correction Evidenceには最低限、次を記録する。

- `P3-GOV-005`の事実関係。
- pytest／Fixture／Plugin／Child ProcessによるActionもTask Actionであること。
- Project Root内専用Temporary Rootの設定／Exact Path Evidenceが欠落したこと。
- Exact OS Temporary Pathは`UNKNOWN／NOT RECORDED`であり、事後調査・捏造をしないこと。
- Project Root外Artifactの現在状態は`NOT OBSERVED`であり、確認・Cleanupしないこと。
- Source／Testの技術結果自体は本Incidentによって無効化しないこと。
- 過去Command結果、現在Repository状態、Historical Git Action、Root外Action、User DataのEvidence Source Class訂正。
- 次Cycle以降、pytestを含むTool／FrameworkのFilesystem Actionも同じAuthorized Root境界へ従わせること。
- Testが必要な将来Work Unitでは、開始前にProject Root内専用Base Tempと、そのWork Unitが新規作成したArtifactだけのCleanup AuthorityをExact Freezeすること。

Fifth Completion Handoffには次を記録する。

```text
P3-GOV-005 Correction: COMPLETE_CANDIDATE
Source Mutation       : NOT PERFORMED
Test Execution        : NOT PERFORMED
Temporary Action      : NOT PERFORMED
Git Mutation          : NOT PERFORMED / Evidence Class明記
Existing File Edit    : 0
New Docs              : Exact 2 paths
Remaining Technical Major Finding: NONE
Remaining Governance Major Finding: NONE after Codex acceptance
Recommendation        : GO to Codex Phase 3 Closure Review
```

`NOT PERFORMED`も、完全なAction Logがなければ断定的Verified Zeroにしない。少なくとも「本Handoffの指示として実行不要／禁止であった」と「Claudeの自己申告」を分離する。

## 3. Exact Allowed Scope

### Read

- 本Handoff。
- `docs/project/phases/phase_3/handoffs/phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md`。
- `docs/project/phases/phase_3/history/index/phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md`。
- Evidence Classificationの定義確認に直接必要な既存Correction Docs。

### Write

- `docs/project/phases/phase_3/history/index/phase_3_gov005_test_temp_boundary_and_evidence_class_correction_ja_<timestamp>.md`の新規作成。
- `docs/project/phases/phase_3/handoffs/phase_3_claude_fifth_governance_correction_complete_candidate_handoff_ja.md`の新規作成。

この2件以外のWriteは許可しない。

## 4. Forbidden

- Source、Test、Config、Frontend、Generated Static、Definitions、Stable、Roadmapの変更。
- Existing History／Existing Handoffの編集・削除。
- Test、Build、Format、Lint、Mypy、Runtime起動、Model Load。
- Temporary Directory／Fileの作成、確認、削除。
- `runtime_data/`へのRead／List／Stat／Write／Delete。
- Project Root外、`other/`、別Project、Provider Memory、Network、Secret、External Service。
- Git／GitHub Mutation。
- Phase 3 Closure、Backup、Phase 4開始。
- Incidentを「pytest管理だからTask Actionではない」と再分類すること。
- Exact Pathを推測、事後生成またはProject Root外調査で補完すること。

## 5. Validation

本CycleのValidationは、作成した新規2文書の相互整合をClaude自身がRead-onlyで確認することだけである。

- Test／Static Check／Buildを実行しない。
- Git StatusをCompletion Evidenceのために必須としない。
- Temporary Artifactを作らない。
- Source ClosureはFourth ReworkのAccepted候補Evidenceを継承し、再検証しない。

## 6. Stop Boundary

新規2文書を作成し、Docs-only Correctionの自己Reviewを終えたら停止する。

Phase 3 Closure、User Acceptance、Final Docs、Backup、Git、Phase 4または別作業へ進まず、Codex Independent Final Closure Reviewを待つ。
