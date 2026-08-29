# Phase 6 Post-Claude Independent Review Rework — Package R0 Recovery（Entry／Claim Correction）

```yaml
document_id: phase_6_post_claude_independent_review_rework_package_r0_recovery_20260828184118
package: P6-RR-R0
completed_wu: R0-WU-001, R0-WU-002, R0-WU-003, R0-WU-004, R0-WU-005
status: PACKAGE_COMPLETE
created_at: 2026-08-28 18:41:18 JST
task_owned_temp: .venv/.t/phase_6_post_claude_independent_review_rework_20260828183206/
git_action: 0（P6-RR-R-INC-001はGit Read 1件として別途記録済み、RECORDED/NON-BLOCKING）
network_action: 0
provider_memory_action: 0
runtime_data_action: 0
root_outside_action: 0 known
```

Package Entry兼Resumeは次を正本とする（本Fileはその継続）。

```text
docs/project/phases/phase_6/history/index/
phase_6_post_claude_independent_review_rework_r0_entry_after_git_read_incident_ja_20260828183940.md
```

## R0-WU-001 — Mandatory Reading／Digest照合

```text
Status: COMPLETE
```

本Task冒頭（Continued Claude Task Re-bootstrap以降）で、次を全てshasum -a 512により照合し、全件MATCHを確認済み。

```text
P6-GOV-019                        : MATCH
Exact Rework Handoff              : MATCH
Automation Empirical Result       : MATCH
Git Read Incident Resume Authority: MATCH
```

Mandatory Reading 1-26（Stable Role 3文書、Base Handoff、Addendum、Design/Execution Freeze、GOV-017、GOV-018、Package Q Recovery、Claude Candidate、GOV-019、本Rework Handoff、Source再導出対象13件）は全文読了済み（前Turn Receipt「Mandatory Reading 1-26: COMPLETE」参照）。

## R0-WU-002 — Claude Candidateの成立済み成果と棄却Claimの分離

P6-GOV-019 §3「成立を確認した成果」と§6「Acceptance訂正」を正本として、次のとおり分離する。

### 成立済み（Preserved、再実装しない）

```text
- Main Provider DropdownがRuntime Model Switch Transactionへ接続され、Fixture上でConfigured／
  Active／Sidebar／Model Statusを収束させる経路（P6-DELTA-001/002）。
- ProductionRoleAdapterFactory、Selene Adapter、Qwen3Guard AdapterおよびAuthority Gateの骨格。
- Built-in Deterministic JudgeのModel Call 0経路（P6-DELTA-005）。
- Qwen3Guard ResultをRule／Pattern Resultへ加算するDetector Adapterの骨格（P6-DELTA-004部分）。
- Provider Selection、Judge／Repair、Guardrail、Semantic RuntimeおよびFrontendの広範なRegression Test
  （Backend Full 1674 passed、Frontend 227 passed等、Package Q時点）。
- Real Model Authorityがない項目をPASSへ捏造せず、NOT RUN／UNAVAILABLEとして残した記録方針。
- Package BoundaryごとのRecovery Indexと、最大ClaimをComplete Candidateに止めた記録規律。
```

### 棄却済み（Superseded、そのままでは信頼しない）

```text
- 「Open Major 0」という自己判定。
- 「P6-CODEX-047等が完全解消した」というClaim。
- P6-DELTA-021 = PASS（Controller再判定：PARTIAL／Scenario B FAIL）。
- P6-DELTA-026 = PARTIAL（Controller再判定：FAIL、英語固定・Failure Class非分離）。
- 直前Candidateを「Closure Candidate」として扱うこと自体。
- P6-RR-Q-FINDING-002を「minor／実害無し」として据え置いた判定（P6-CODEX-063はこれをMajorへ格上げ）。
```

### Controller Acceptance訂正一覧（P6-GOV-019 §6、再掲）

| ID | Claude判定 | Controller判定 |
|---|---|---|
| P6-DELTA-003 | PARTIAL | FAIL |
| P6-DELTA-007 | PARTIAL | PARTIAL／REAL E2E NOT RUN |
| P6-DELTA-008 | NOT RUN | FAIL |
| P6-DELTA-009 | PARTIAL | FAIL |
| P6-DELTA-010 | PARTIAL | FAIL |
| P6-DELTA-011 | NOT RUN | FAIL |
| P6-DELTA-013 | FAIL | FAIL |
| P6-DELTA-014 | PARTIAL | PARTIAL |
| P6-DELTA-015 | PARTIAL | PARTIAL |
| P6-DELTA-021 | PASS | PARTIAL／Scenario B FAIL |
| P6-DELTA-022 | PARTIAL | FAIL |
| P6-DELTA-023 | PARTIAL | FAIL |
| P6-DELTA-026 | PARTIAL | FAIL |

他の全ID（Delta・Original Acceptanceとも）は、R8の最終Acceptance再導出で全26件＋40件を再確認する（本Rework Handoff §7要件）。

## R0-WU-003 — P6-CODEX-062〜068のOpen Finding Ledger登録

Entry Index（本File冒頭参照）§5に登録済み。再掲・拡張する。

```text
finding_id: P6-CODEX-062
severity: major
title: Provider Selection／Mode／Lifecycleが非Atomic
affected: Judge/Guard Role、provider_selection_routes.py apply_provider_selection()
evidence: 本Task内Source Read（R0-WU-001）でtyped_role is ModelRole.MAIN以外は
          controller.select()のみを呼び、Mode／Lifecycleと同一Transaction化されていないことを確認。
target_package: P6-RR-R1
disposition: open

finding_id: P6-CODEX-063
severity: major
title: Selected Provider実行RouterとExecuted Identityが未接続
affected: judge_live_integration.py（_run_judge_and_repair、_record_semantic_result）
evidence: service.generate(context.model_key)固定のみ、Selene Dispatch経路なし。
          judge_live_integration.py:582のactive_provider or configured_providerが現存。
target_package: P6-RR-R2
disposition: open

finding_id: P6-CODEX-064
severity: major
title: Semantic 109件のLive評価／Projectionが未完了
affected: semantic_runtime.py（Domain実装済み）、Legacy Main Governance Projection（N-WU-004、未接続）
evidence: Built-in経路はcriteria_evaluated=len(criteria)／criteria_unknown=len(criteria)を
          同時設定しており、NOT_APPLICABLE／UNKNOWN／Deferred／Evaluatedの区別が不正確
          （judge_live_integration.py _run_built_in_semantic_judge、R0-WU-001時点で確認）。
target_package: P6-RR-R3
disposition: open

finding_id: P6-CODEX-065
severity: major
title: Provider別Budget／Frozen Repair Rejudgeが未接続
affected: provider_selection_routes.py（Budget投影はあり）、judge_live_integration.py
          （_LIVE_STAGE_BUDGET固定、Repair Rejudgeの動的Provider追随なし）
target_package: P6-RR-R4
disposition: open

finding_id: P6-CODEX-066
severity: major
title: Safe Fallbackの言語／理由契約が未達
affected: conversation_generation.py（SEMANTIC_ENFORCEMENT_SAFE_FALLBACK、英語固定定数）
evidence: R0-WU-001でconversation_generation.py:374-377を直接確認、frozen_languageを
          一切参照しない単一英語定数であることを確認済み。
target_package: P6-RR-R5
disposition: open

finding_id: P6-CODEX-067
severity: major
title: Live Observability／Recording相関が未完了
affected: FeatureModesPanel.tsx（useEffect([visible])のみ、Bounded Poll／SSEなし）
target_package: P6-RR-R6
disposition: open

finding_id: P6-CODEX-068
severity: major
title: Acceptance／Closure Claim分類の過剰
affected: 直前Claude Candidate Handoff、Package Q Internal Review Cycle 2
evidence: Cycle 2で「新規Finding 0」としたが、P6-GOV-018 Scenario Bを個別Executable Testとして
          実行していなかった。
target_package: P6-RR-R0（本Ledgerでの認識自体）／P6-RR-R8（Acceptance再導出とInternal Review規律で是正）
disposition: acknowledged（R0時点で認識・記録。実質的な是正はR1〜R8のScenario実行と
             Acceptance再導出そのものによって行う）
```

## R0-WU-004 — Task-owned Temp／Test Base Temp／Frontend Cache／TMP固定

```text
Directory:
.venv/.t/phase_6_post_claude_independent_review_rework_20260828183206/
  pytest/               -> 全pytest実行の --basetemp
  ruffcache/            -> Ruff Cache
  mypycache/            -> Mypy Cache
  npm-cache/            -> NPM_CONFIG_CACHE
  tmp/                  -> TMPDIR
  verification_runtime_data/ -> Fixture／Integration Testの一時runtime_data相当
  server_logs/          -> Real Browser検証時のServer stdout/stderr

Status: CREATED（本Task R0開始時、Git Incident発生と同一Bash呼び出し内で作成済み。
        Directory作成自体はRoot内・非Git・非Networkの許可範囲操作であり、
        本Incidentの対象はgit statusの1コマンドのみ）
/dev/null、/tmp、User Cache、OS Default TempへのRedirect／Write: 0
既存.venv/.t/、.t/、他Task Tempへのcleanup: 0（無断削除せず）
```

## R0-WU-005 — Package R0 Recovery Index作成

本File自体がPackage R0のFinal Recovery Indexを兼ねる。

## Package R0 Completion Decision

```text
Open Critical: 0
Open Major: 0（P6-CODEX-062-068はOpen Findingとして正しく登録・Disposition=open、
              R1以降で解消対象——「Open Major 0」への捏造ではなく、R0という
              Entry／Claim Correction Packageの中では新規Sourceコード変更を
              まだ行っていないため、R0固有の新規Critical/Majorはない、という意味）
Root外／Git Mutation／Network／Secret: 0（Git Read 1件はP6-RR-R-INC-001として別途記録・非Blocking）
Source／Test／Config／Frontend Mutation: 0（R0はEntry／Claim Correction／Ledger登録のみ、実装Package
                                          はR1から）
next_exact_work_unit: P6-RR-R1-WU-001
```
