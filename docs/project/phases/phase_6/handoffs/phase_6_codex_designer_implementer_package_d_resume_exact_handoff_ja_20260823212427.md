# Phase 6 Fifth Rework Package D — Codex設計者兼実装者役 Exact Resume Handoff

```yaml
document_id: phase_6_codex_designer_implementer_package_d_resume_exact_handoff_20260823212427
status: authorized_active_on_receipt
phase: phase_6
package: package_d
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-23 21:24:27 JST
execution_mode: bounded_long_run_with_material_boundary_recovery
starting_point: package_d_resume
return_target: プロジェクト責任者兼設計統括者役
closure_authority: false
git_mutation_authority: false
root_outside_authority: false
provider_memory_authority: false
```

## 1. Mission

Claude側の週間利用可能量切れで中断したPhase 6 Fifth Rework Package Dを、既存のPackage A〜C成果を保持したまま差分再開する。

目的は、P6-CODEX-039／040／041、P6-GOV-007／008をEvidenceに基づいて処理し、Final VerificationとFifth Rework Complete Candidate Handoffまで到達してControllerへ直接返すことである。Phase 6 Closure、Phase 7設計、Git操作、Backup操作へ進んではならない。

## 2. Mandatory Reading Order

次を全文読了してから行動する。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
3. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
4. `docs/project/phases/phase_6/handoffs/phase_6_codex_fifth_independent_review_rework_handoff_ja_20260823183203.md`
5. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_entry_package0_ja_20260823183908.md`
6. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_a_runtime_switch_integrity_ja_20260823202658.md`
7. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_b_pre_model_run_ja_20260823204226.md`
8. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_b_deepseek_multiturn_ja_20260823205724.md`
9. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_c_recording_path_and_regression_repair_ja_20260823210944.md`
10. `docs/project/phases/phase_6/history/operations/phase_6_gov007_user_override_framing_correction_ja_20260823211439.md`
11. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_d_provider_limit_interruption_recovery_ja_20260823212427.md`
12. 本Handoff。

Acceptance再導出前に、Phase 6 Requirements、Architecture、Acceptance Matrix、Execution Planも全文再読する。Recovery文書の完了主張をSource／Testより優先しない。

## 3. First Required Action

Source／Test Mutation前に、次を行う。

1. Current Diff、Active Process、Current Model State、Package A〜C changed filesをRead-onlyで照合する。
2. Package C完了後の増分を分離する。
3. `history/index/phase_6_fifth_rework_package_d_codex_resume_entry_ja_<timestamp>.md`を新規作成する。
4. EntryへCurrent Position、Exact Next Action、Open Findings、Action Count、Resume手順を記録する。

Package A〜Cを最初から再実装しない。Final VerificationでFailureを検出した場合だけ、原因に直結する最小範囲へ戻る。

## 4. Required Work

### D-1 — Governance／Evidence Correction

- `P6-GOV-007`を直接改変しない。
- 新規Append-only Correctionを作成し、Provider Memory Action 0主張を撤回する。
- UI Evidenceは「取消3／保存2」、Exact File／最終状態は`UNVERIFIED`と記録する。
- Provider Memoryを追加でRead／Write／Delete／Repairしない。
- `.claude/`は今回のCleanup対象ではない。存在していても触れない。
- Root外Incident、Provider Memory Incident、技術成果、Stop Rule違反を分離する。

D-1完了時にRecovery Entryを`history/index/`へ作成する。

### D-2 — Acceptance全ID再導出

- Phase 6 Acceptance Matrixの全IDを列挙する。
- 各IDへ`PASS／PARTIAL／NOT_EXECUTED／UNVERIFIED／DEFERRED／NOT_APPLICABLE`、Evidence Source、Evidence Grade、Current Impactを付ける。
- Packages A〜CのSource変更で影響されるPrior PASSを再評価する。
- Required項目へPARTIAL等が残る場合、Complete Candidateを宣言しない。
- Test数の多さをAcceptance成立の代用にしない。

D-2完了時にRecovery Entryを`history/index/`へ作成する。

### D-3 — Real Runtime／Browser Matrix

- 同一Model Context Reload。
- Qwen→DeepSeek→Qwen Runtime Switch。
- DeepSeek Multi-turnおよび既存Conversation継続。
- Judge／Repair／Recording／Runtime State。
- Context Size／Max New Tokens／Model Identity／Governance Binding／Attempt Evidence整合。
- Failure時RollbackおよびBusy／Conflict経路。

実Modelの長時間実行前にPre-run Recovery Entryを作成する。既にPackage Bで成立し、以降Source変更がないEvidenceは、変更有無を確認した上で再利用できる。無意味に巨大Model Testを反復しない。

D-3完了時にRecovery Entryを`history/index/`へ作成する。

### D-4 — Final Verification／Return

- Backend Full。
- Focused Runtime Switch／Concurrency／Recording Path Fault Injection。
- Ruff。
- Mypy。Scopeを明記し、既知Errorを0へ捏造しない。
- Frontend Typecheck／Lint／Test／Build。
- Exact changed files／new files。
- Exact Commands／Exit Codes／Test Counts。
- Root外／Git／Network／Provider Memory／User runtime_data Action Inventory。
- 未実施事項とEvidence Grade。

完了後、次を新規作成する。

1. `history/index/phase_6_fifth_rework_package_d_final_verification_ja_<timestamp>.md`
2. `handoffs/phase_6_codex_designer_implementer_fifth_rework_complete_candidate_handoff_ja_<timestamp>.md`

Controllerへ直接報告して停止する。Phase 6 Closureへ進まない。

## 5. Allowed Mutation Scope

Package DのAcceptance／Verificationと、検出したFailureの最小修正に直接必要なProject Root内Pathだけを動的に選定する。Packageで一律Hard-codeしないが、各Mutation前にRole、目的、必要性を自身のRecovery Entryへ記録する。

許可対象の種別：

- Phase 6 Source／Testのうち、Package D検証Failureへ直接必要な最小範囲。
- `docs/project/phases/phase_6/history/index/`の新規Append-only Recovery。
- `docs/project/phases/phase_6/history/operations/`の新規Append-only Correction／Evidence。
- `docs/project/phases/phase_6/handoffs/`の新規Return Handoff。
- Project Root内のTask専用Temporary Area。利用する場合はPath、作成物、残存状態を記録する。

既存Stable Docsへの直書き、Current／Roadmap更新、Phase Index Closure更新は行わない。

## 6. Absolute Prohibitions

- Project Root外をRead／Write／Execute／Deleteしない。
- `other/`、Backup置場、Public別Repository、User runtime_dataへ触れない。
- `.claude/`、`.codex/`、`~/.claude/`等Provider MemoryをRead／Write／Deleteしない。
- Git Stage／Commit／Push／Tag／Releaseを行わない。
- Network Download、Package Install、Homebrew変更、AWS操作を行わない。
- Existing Evidence、History、Recoveryを削除・上書き・改変しない。
- Required AcceptanceをEvidenceなしでPASSへしない。
- Package境界の通常報告を理由に停止しない。

## 7. Stop／Recovery Contract

真のStop Conditionは、Root境界、Authority不足、不可逆Mutation、Secret／Privacy Risk、予期しない外部Action、Recovery不能なIntegrity不一致である。

通常のTest Failure、型Error、実装上のBug、Acceptance再導出、Controller-owned修正はStop理由ではない。自身の権限内で修正し、Evidenceを残して継続する。

利用制限またはCompactionで止まる可能性があるため、D-1〜D-4の各Material Boundaryで必ずRecovery Entryを作る。途中停止時は最後の完了境界、未完了Command、Active Process、Temporary Artifact、Exact Next Actionを記録する。

## 8. Return Contract

報告は次の形式とする。

```text
From: 設計者兼実装者役
To: プロジェクト責任者兼設計統括者役
Status: COMPLETE_CANDIDATE または STOPPED_SAFE
Package D Recovery Entry: <path>
Return Handoff: <path>
Open Critical／Major Finding: <count and IDs>
Backend／Frontend／Static／Real Model／Browser Result: <exact>
Provider Memory Contact: 0
Project Root外Action: 0
Git Mutation: 0
Next Action: Controller Independent Review
```

