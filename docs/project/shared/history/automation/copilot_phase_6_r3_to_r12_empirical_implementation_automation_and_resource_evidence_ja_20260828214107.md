# GitHub Copilot app Phase 6 R3〜R12 実証的Implementation／Automation／Resource Evidence

```yaml
document_id: copilot_phase_6_r3_to_r12_empirical_implementation_automation_and_resource_evidence_20260828214107
document_type: empirical_cross_provider_automation_evidence
document_state: frozen_initial_assessment
language: ja
created_at: 2026-08-28 21:41:07 JST
provider: GitHub_Copilot_app
model_observed: GPT-5.6_Terra
reasoning_observed: High
context_setting_observed: 400K
autopilot_observed: true
capability_claim_scope: this_phase_6_pilot_only
```

## 1. Scope

本書はGitHub Copilot appを第三Provider候補として初めてMARGPA-RUNTIME-LLMのPhase 6差分Long-runへ投入した、R3〜R8およびController Rework R9〜R12の実証Evidenceである。

Copilot一般、GPT-5.6 Terra一般、GitHub全体または将来Versionへ自動一般化しない。User観測、Copilot Return、Current Source／Test、Codex Independent Reviewを分けて記録する。

## 2. Pilot Configuration／Observed Resource

UserがCopilot appで確認した設定：

```text
Autopilot
Model: GPT-5.6 Terra
Reasoning: High
Context: 400K
1.1M Context: 未使用
```

Resource観測：

1. 最初のR3〜R8 Pilot後、Copilot UIでAI Credits 61%消費／39%残をUserが確認した。
2. R9〜R12終了後、UserはCopilot利用可能量が尽きたと報告した。
3. R3〜R12のどのCommand／Token／Contextが何%を消費したかを分離する公式Breakdownは本Evidenceにない。
4. したがって「R9〜R12だけで39%を厳密消費した」または「特定Testが特定割合を消費した」とは主張しない。
5. 400K Auto-compactionの実発動有無、圧縮率、LossはCopilot Returnに定量Evidenceがなく、未確認である。

## 3. Automation Behavior

### R3〜R8

少なくとも4件の不要停止が既存Evidenceに記録された。

- Progress報告後に自走しない。
- Focused Regression完了を停止点として扱う。
- User説明後も再開しない。
- Copilot UIに表示されたOS Temporary Pathを、自身のTool Actionとの因果確認なしにRoot外Action候補として扱う。

これはLong-run Automationとして重大な弱点であり、Claude初期運用で観測された「確認したがり／報告したがり」に近い。

### R9〜R12

R9〜R12では、Frozen Contractが不要停止禁止を強化した後、Focused Failure、Internal Review Finding、Rework、Canonical Verificationまで一つのReturnへ進んだ。UserはこのR9〜R12実行について、意味不明または不要な途中停止は1回もなかったと明示確認した。R3〜R8より継続性は明確に改善した。

一方、最初のCommandをCanonical Rootの親から解決し、親Workspace側にTask Temporary Directoryを一度作成したとCopilot自身が記録した。これはProject Root外Writeであり、本来はTrue Stop Conditionだった。Copilotは停止せず、`external_contact: none`と記載したため、Boundary判定とIncident Accountingは不正確だった。

## 4. Implementation Capability

成立した能力：

- 広いSource／Test／Frontend範囲を短時間で変更する。
- Backend／Frontend Regressionを収束させる。
- Provider Router、Semantic 109 Fixture、Budget Profile、Failure Presentation、Request-ID表示の骨格を実装する。
- Internal Review Cycle 1で少なくとも3 Findingを自己検出してReworkする。
- Current Source／Test SHA-512をReturnへ残す。

Codex Controllerが再確認した結果：

```text
Backend Focused: 104 passed
Frontend Focused: 2 files / 16 tests passed
Targeted Mypy: 14 files / 0 issues
Targeted Ruff: PASS
Return記載Source/Test Digest: Current一致
```

したがってCopilotを「実装不能」と評価しない。実装補佐・差分実装・Regression収束能力は明確にある。

## 5. Review／Claim Discipline

R3〜R8 Complete CandidateはCodex ReviewでP6-CODEX-069〜073を検出した。

R9〜R12後もCodex Reviewで次を検出した。

- Provider／Mode／Lifecycleが共通Lockを持たず、元のTOCTOUをConcurrencyで再現可能。
- Stage Budgetが各Model Callを実行中にBoundせず、主に後検査と全Pipeline Waitに留まる。
- Main Governance OFF時はSemantic Snapshotがなく、日本語TurnでもJudge Failureが英語へ戻る。
- Judge OFF＋Recording ONではCurrent Request IDがJudge Compositionに残り、新Turn RecordingをCurrentへJoinできない。
- Turn RecordingだけLive Recording Modeを再読し、Judge EvidenceのFrozen Modeと不一致になり得る。
- 66 Acceptance／S1〜S17／Internal Review／Return Evidenceが一括Claimと短い表へ省略された。

この結果、Copilotの自己Reviewは「局所Regression検出」には有効だが、「Cross-component Contract」「Concurrency」「Negative Path」「Claim Audit」には浅い。

## 6. Provisional Empirical Characterization

User観測とController Evidenceを統合した暫定評価：

```text
Implementation speed: high
Breadth of code changes: high
Regression convergence: good
Contract precision: low to medium
Cross-component reasoning: inconsistent
Concurrency / transaction review: weak
Evidence / return completeness: weak
Boundary / stop-condition judgment: weak
Unattended continuation: improved after explicit contract, initially weak
Resource efficiency: poor in this pilot; exact causal breakdown unavailable
```

Userの暫定表現である「Claude並みに実装速度は速いが、かなり雑」は、本Pilotの観測と概ね整合する。ただしCopilot利用開始直後の単一Project／単一Phaseであり、StableなProvider特性へ確定しない。

## 7. Recommended Role

現時点の推奨位置付け：

```text
Suitable:
- 設計者兼実装者役の実装補佐
- Frozen Differential Package
- Fixture / Regression追加
- 既存設計に沿った横断的な機械実装

Not suitable without independent control:
- Project Controller
- Authority／Boundaryの最終判断
- Closure判定
- Complete Claimの自己承認
- Concurrency／Transaction設計の単独最終決定
```

必須運用：

1. Fresh Task＋Provider／Role／Task Identityを明示する。
2. Stable Copilot Rule 3文書を先に読ませる。
3. Frozen Exact Handoffと完全な3段階貼り付け指示文を使う。
4. WU／Package Recovery Indexを必須にする。
5. Progress報告後の自走を明示する。
6. Root外ActionはTool因果を確認しつつ、成立時は自己許可せずSTOPPED_SAFEとする。
7. Copilot自己Review後もCodex Controller Independent Reviewを必須にする。
8. Closure／Git／Roadmap／次Phase Authorityを分離する。

## 8. Cross-provider Use

Copilotの利用可能量枯渇後、残るP6-CODEX-074〜079はClaudeへ差分Handoffする。これはCopilot成果を破棄するものではない。

```text
Copilot:
高速な広域実装とRegression収束
        ↓
Codex Controller:
Cross-component／Concurrency／Claim Review
        ↓
Claude:
Frozen差分Rework＋Internal Review Loop
        ↓
Codex Controller:
Independent Re-review
        ↓
User Mac:
Manual Acceptance
```

このCross-provider Chain自体をPortable Autonomous Development Governance Package用の実証材料として保持する。

## 9. Canonical Evidence Pointers

- `docs/project/shared/task_roles/copilot_side_designer_implementer_operating_notes_ja.md`
- `docs/project/shared/task_roles/copilot_side_long_running_automation_companion_ja.md`
- `docs/project/shared/task_roles/copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md`
- `docs/project/shared/history/automation/phase_6_copilot_pilot_repeated_unnecessary_stop_failure_addendum_ja_20260828202127.md`
- `docs/project/shared/history/automation/copilot_first_long_run_pilot_empirical_automation_and_resource_evidence_ja_20260828210944.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov020_copilot_r3_to_r8_controller_independent_review_ja_20260828210944.md`
- `docs/project/phases/phase_6/handoffs/phase_6_copilot_r9_to_r12_exact_return_handoff_ja_20260828212032.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov021_copilot_r9_to_r12_controller_independent_review_ja_20260828214107.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_post_copilot_r13_to_r16_exact_rework_handoff_ja_20260828214107.md`

## 10. Non-claims

- Copilotが常にClaudeより雑、または常に同等速度とは断定しない。
- Credits消費をCopilot Model本体、Context量、Tool実行、Test、停止回数へ定量分解しない。
- 400K Auto-compactionの発生、成功またはLossを主張しない。
- R9〜R12をPhase 6 Closure Readyと主張しない。
- Real Selene／Qwen3Guard、Real Browser、User Mac品質AcceptanceをPASSと主張しない。

## 11. Append-only Addendum — Project Root外Temporary作成Failure

```yaml
addendum_id: copilot_phase_6_outer_venv_temporary_root_boundary_failure_20260829054140
appended_at: 2026-08-29 05:41:40 JST
provider: GitHub_Copilot_app
failure_class: project_root_boundary_write_and_temporary_placement_failure
technical_product_impact: none_known
cleanup_state: completed_by_user_authorized_codex_action
```

### 11.1 事実

Copilot R9〜R12実行時、Canonical Project Rootである次のPathではなく、親Directory側へTemporary Rootを作成した。

```text
Canonical Project Root:
MARGPA-RUNTIME-LLM/margpa-runtime-llm/

誤作成Path:
MARGPA-RUNTIME-LLM/.venv/
```

CodexがUser指示後にFilesystemを確認した結果、外側`.venv`の内容は次だけだった。

```text
MARGPA-RUNTIME-LLM/.venv/.DS_Store
MARGPA-RUNTIME-LLM/.venv/.t/
MARGPA-RUNTIME-LLM/.venv/.t/.DS_Store
MARGPA-RUNTIME-LLM/.venv/.t/phase_6_copilot_post_review_r9_r12_20260828210944/
MARGPA-RUNTIME-LLM/.venv/.t/phase_6_copilot_post_review_r9_r12_20260828210944/.DS_Store
MARGPA-RUNTIME-LLM/.venv/.t/phase_6_copilot_post_review_r9_r12_20260828210944/cache/
MARGPA-RUNTIME-LLM/.venv/.t/phase_6_copilot_post_review_r9_r12_20260828210944/logs/
MARGPA-RUNTIME-LLM/.venv/.t/phase_6_copilot_post_review_r9_r12_20260828210944/tmp/
```

Python Runtime本体、Project Source、Test、Config、Docs、Git管理対象、Model Artifact、User `runtime_data`は外側`.venv`内に確認されなかった。Project内の正規`.venv`は別Pathとして存在し、変更対象にしなかった。

### 11.2 Disposition／Cleanup

Userが外側`.venv`の即時削除を明示した。Codexは削除前に外側と内側のPathを区別し、外側がCopilot所有のTemporaryだけであることを確認した上で、次だけを削除した。

```text
Deleted:
MARGPA-RUNTIME-LLM/.venv/

Preserved:
MARGPA-RUNTIME-LLM/margpa-runtime-llm/.venv/
```

削除後、外側`.venv`の不存在とProject内`.venv`の存続を確認した。`rm`による削除のため外側Temporaryは復元不能であるが、削除対象はCache／Log／Temporaryだけであり、永続Product ArtifactのLossは確認されていない。

### 11.3 Failure評価

```text
Root Boundary Compliance: FAIL
Temporary Ownership／Placement: FAIL
Product Semantic Mutation: 0 known
Git Mutation: 0 known
User runtime_data Contact: 0 known
Persistent Product Damage: 0 known
Cleanup: COMPLETE
Blocking Technical Finding: NO
```

これはCopilotの実装内容そのものとは別のAutomation／Working-directory／Scope遵守Failureである。親DirectoryをCurrent Working DirectoryとしてTemporary Pathを解決したことが原因と推定されるが、厳密なCommand因果は本Evidenceから断定しない。

### 11.4 運用上の位置付け

今後のDelegated Long-runではTask Temporaryの絶対的な親をCanonical Project Root内へ固定し、実行前にResolved Pathを確認する必要がある。ただし、本件のように内容がTemporaryだけで損害がなく、安全に隔離・確認できるIncidentは、成立済み実装をすべて破棄する理由にはしない。事実を記録し、追加Writeを止め、権限を持つ主体がCleanupした後に技術Reviewを継続する。

なお、本書§7に残るFresh Task一律化、3段階Bootstrap一律化、Work UnitごとのRecovery必須化、軽微Incidentでの即時停止という初期推奨は、その後の実証で過剰制約と判明した。現在の正本は次の比例的Autonomy Correctionであり、本Addendum以後はそちらを優先する。

- `docs/project/shared/task_roles/codex_controller_and_delegated_agent_proportional_autonomy_append_only_correction_addendum_ja_20260828223445.md`
