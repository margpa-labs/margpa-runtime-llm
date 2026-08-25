# Phase 6 Remaining Rework — Claude Exact Execution Handoff

```yaml
document_id: phase_6_claude_remaining_rework_exact_handoff_20260825130924
status: frozen_prepared_not_active
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役兼長期実装Executor
created_at: 2026-08-25 13:09:24 JST
implementation_authority: false
activation_key_1_design_handoff: frozen
activation_key_2_user_start: missing
closure_authority: false
git_authority: false
```

## 1. 現在状態

```text
Phase 6                 : IN PROGRESS / REMAINING REWORK REQUIRED
P6-GOV-015              : OPEN FOR REWORK
Design                  : FROZEN
Execution Plan          : FROZEN
Implementation Authority: FALSE
Expected Start Window   : around 2026-08-31 / FORECAST ONLY
```

本書は、Claudeに渡しただけでImplementation Authorityを発生させない。
Userが次を明示的に宣言した時点でTwo-key Activationが成立する。

```text
Phase 6 Remaining Reworkを開始する。
```

開始日時の予測、利用可能量の回復、本書のRead、Preflight PASSのいずれも、このUser宣言の代わりにはならない。

## 2. Frozen Package Identity

```text
Preparation Baseline HEAD:
3510dd6d9d26167df59f37e4d821cad815a8fb9f

Design Freeze:
docs/project/phases/phase_6/history/operations/
phase_6_remaining_rework_design_freeze_ja_20260825130924.md
SHA-512:
3489ad52522bd19c75d47f186d21ef9f82c289da4b11b8315387a54e7ea6a3fc559afc8edb899678cb6a321037e30de767b7618c6eb819d80e6a8bda4c44b89e

Execution Plan / Acceptance:
docs/project/phases/phase_6/history/operations/
phase_6_remaining_rework_execution_plan_and_acceptance_ja_20260825130924.md
SHA-512:
6d66367e88ddd33d85979837871a2e4028bf9c8efd72df69cb237fc286e78a781ed098bd585966db23702d91044f46ceca55c92e1bc7ded7c768c8da01c021cc
```

Preparation Baseline後にControllerが作成した本3文書、またはそれらを含むController CommitはExpected Changeである。
それ自体をDirty Blocker、改ざん、無許可変更と判定しない。Git Commandを使わず、File本文と指定SHA-512で確認する。

## 3. Mandatory Reading Order

実装開始後、P6-RR-0-WU-001で次を順番どおり全文読み込む。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. `docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`
5. `docs/project/phases/phase_6/requirements/phase_6_requirements_ja.md`
6. `docs/project/phases/phase_6/architecture/phase_6_architecture_ja.md`
7. `docs/project/phases/phase_6/adr/phase_6_adr_ja.md`
8. `docs/project/phases/phase_6/operations/phase_6_execution_plan_ja.md`
9. `docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md`
10. `docs/project/phases/phase_6/history/operations/phase_6_gov014_ninth_rework_controller_independent_final_review_ja_20260824164002.md`
11. `docs/project/phases/phase_6/handoffs/phase_6_user_mac_manual_acceptance_after_ninth_rework_ja_20260824164002.md`
12. `docs/project/shared/history/planned_work/phase_6_manual_acceptance_consolidated_rework_and_phase_9_ui_research_reservation_ja_20260825090037.md`
13. `docs/project/phases/phase_6/history/operations/phase_6_gov015_semantic_definition_execution_omission_controller_reflection_ja_20260825090037.md`
14. `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_design_freeze_ja_20260825130924.md`
15. `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_execution_plan_and_acceptance_ja_20260825130924.md`
16. 本Exact Handoff。

過去のClaude Complete Candidate／Rework HandoffはHistorical Evidenceであり、本書のScopeを縮小しない。

## 4. Exact Objective

P6-RR-0からP6-RR-Jまでを連結実行し、次を成立させる。

1. ARGD／DAGD Semantic RuleをDefinition→Criterion→Evaluation→Action→Repair→Evidenceへ接続する。
2. Main／Guardrail／Judgeを独立Provider Selectionとして実装する。
3. SeleneをDedicated Judge、Qwen3Guard-GenをDedicated Safety Modelとして実Runtimeへ接続する。
4. Main-selfの暗黙Fallback、False ENFORCE、固定30秒Deadline、汎用Failure、Recording相関不足を是正する。
5. Acceptance 40 IDを個別再導出し、Complete CandidateをControllerへ返す。

## 5. Authorized Root / Mutation Scope

Authorized Root:

```text
margpa-runtime-llm/
```

User開始宣言後、次の最小差分のみ変更できる。

- `src/margpa_runtime_llm/modules/runtime_governance/`
- `src/margpa_runtime_llm/adapters/runtime_governance/`
- `src/margpa_runtime_llm/modules/evaluation/`
- `src/margpa_runtime_llm/adapters/evaluation/`
- `src/margpa_runtime_llm/modules/guardrail_governance/`
- `src/margpa_runtime_llm/adapters/guardrail_governance/`
- `src/margpa_runtime_llm/modules/runtime_model_control/`
- `src/margpa_runtime_llm/modules/inference/`
- `src/margpa_runtime_llm/bootstrap/`
- `src/margpa_runtime_llm/web/`
- `src/margpa_runtime_llm/entrypoints/web/`
- `frontend/src/`
- 上記に対応する`tests/`。
- `config/models/`のSelene／Qwen3Guard Role Definition。
- `config/judge_templates/selene/`のExact Official Template Copy／Manifest。
- `config/profiles/`のRole／Stage Budgetに必要な最小追記。
- `docs/project/phases/phase_6/history/index/`のPackage Recovery。
- `docs/project/phases/phase_6/history/operations/`のAppend-only Evidence／Correction。
- `docs/project/phases/phase_6/handoffs/`のReturn Handoff。

## 6. Read-only / Forbidden Scope

### 6.1 Read-only

- `definitions/`全体。Canonical Definitionを変更しない。
- 次のModel ArtifactとそのSibling Metadata。

```text
models/main/qwen3-4b-q4-k-m/
models/main/deepseek-r1-0528-qwen3-8b/
models/judge/selene-1-mini-llama-3.1-8b/
models/guard/qwen3guard-gen-0.6b/
```

### 6.2 常に不許可

- Project Root外Filesystem Action。`/dev/null`、OS Temp、User Cacheを含む。
- `.claude/`、`.codex/`その他Provider Memoryの内部Read／Write／Enumeration／Semantic Use。
- User `runtime_data/`のRead／Write／Migration／Test Use。
- GitのRead／Write全て。`status`、`diff`、`rev-parse`、`log`、`add`、`commit`、`push`も含む。
- Model ArtifactのConversion／Quantization／Delete／Move／Overwrite。
- Roadmap、Phase 6 Closure文書、Phase 7／以降のDocs／Source。
- AWS／Lightning／外部Deployment。
- Secret／Login／Token／License同意操作。
- `pyproject.toml`のDependency変更、Package Install、Homebrew変更。

## 7. Exact Network Exception

User開始宣言後、P6-RR-F-WU-001／P6-RR-G-WU-001に限り、次のOfficial Public Sourceの
Read-only GETだけを許可する。Package Install、Model Download、Repository Clone、Loginは許可しない。

```text
https://github.com/atla-ai/selene-mini/tree/main/prompt-templates
https://raw.githubusercontent.com/atla-ai/selene-mini/
https://huggingface.co/AtlaAI/Selene-1-Mini-Llama-3.1-8B
https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B
https://qwenlm.github.io/blog/qwen3guard/
```

- Exact TemplateはUpstream Revision／URL／SHA-512とともにProject内へ保存する。
- `main`だけをImmutable Revisionと偽装しない。Revisionが取得できなければTyped Findingとする。
- 上記Networkが一時的に使えなくても、その場でTurnを停止せず、Local Evidenceで可能なPackageを継続し、
  最終Returnで該当AcceptanceをPARTIALとする。

## 8. Task-owned Temporary Contract

開始時に次のProject内Directoryを1個作成し、全Temporary／Cache／Test Artifactをそこへ隔離する。

```text
.venv/.t/phase_6_remaining_rework_claude_<YYYYMMDDHHMMSS>/
```

- 全`pytest`に`--basetemp=<task temp>/pytest`を指定。
- Frontend Commandは`frontend/`をWorkdirとし、`NPM_CONFIG_CACHE`と`TMPDIR`をTask Temp内へ指定。
- Python／HF／XDG／llama.cpp／BrowserのTemporary／Cacheも必要に応じTask Temp内へ指定。
- Shell Redirectで`/dev/null`を使わない。
- 既存`.venv/.t/`を無断Cleanupしない。Task-owned TempのみReturn時に列挙する。

## 9. Execution Control

### 9.1 Activation後

- P6-RR-0-WU-001からP6-RR-J-WU-006までを連結実行する。
- Preflight、Progress Report、Package完了、「次から性質が変わる」という事実を理由に停止しない。
- 状況報告は日本語で出し、報告後も自走を継続する。
- 一部ProviderのReal LoadがUnavailableでも、Contract／Fake／Fixture／UI／Failure Pathを継続する。
- Work Unitを記憶で実行せず、毎回Frozen PlanのExact WUを参照する。

### 9.2 Package Boundary

各Package終了時にRecovery Indexを作るが、その作成自体を停止点にしない。
Indexの最後に`next_exact_work_unit`を明示し、そのまま次へ進む。

### 9.3 Auto-Compaction / 5時間制限復帰

復帰後は次を実行する。

1. 本Handoff、Design Freeze、Execution Plan、最新Recovery Indexを再読。
2. Frozen PackageのSHA-512とActive WUを確認。
3. Current Source／Test DiffをGitではなく対象File本文から再構成。
4. 完了済みPackageをやり直さず`next_exact_work_unit`から自動継続。
5. 報告言語を日本語へ戻す。

## 10. True Stop Conditions

次だけは即時に停止し、`STOPPED_SAFE`とRecovery／Return Handoffを作る。

- Project Root外Action、Provider Memory内部接触、User `runtime_data`接触。
- 無許可Git／Network／Install／Model Artifact Mutation。
- Canonical Definition／Model Artifact Integrityの不整合。
- Scope外の不可逆Mutation。
- User Decisionなしに選ぶと最終仕様が実質的に変わる新しいMaterial Scope。

これ以外はWork UnitのFindingとして記録・修復・分類し、可能な後続を継続する。

## 11. Completion Claim Boundary

Claudeが主張できる最大状態は次である。

```text
Phase 6 Remaining Rework: COMPLETE_CANDIDATE
Phase 6 Closure: NOT CLAIMED
```

次は主張しない。

- Testが通っただけでSemantic Governanceが完成した。
- Configured ProviderだけでActive／Usableである。
- Selene／Qwen3GuardのLocal LoadなしでReal Model Acceptance PASS。
- Deferred／Unknown／UnavailableをPassへ読み替えた。
- Phase 6 Closure、Roadmap更新、Backup、Git、Phase 7 Ready。

## 12. Exact Return Format

Final Returnは日本語で、少なくとも次を含む。

```text
Status
Completed Package / WU
Acceptance 40 ID disposition
Semantic count by result and reason
Configured / Active Main, Guard, Judge
Selene / Qwen3Guard artifact and prompt identity
Focused / Full / Static / Frontend / Real Model / Browser evidence
Open Critical / Major / Non-critical findings
Historical and current incident accounting
Root-outside / Provider Memory / runtime_data / Git / Network / Model mutation inventory
Task-owned temp / active process / loaded model
Claims not made
Exact next action: Controller Independent Review
```

Return Handoffを作成したら停止する。Phase 6 Closureへは進まない。
