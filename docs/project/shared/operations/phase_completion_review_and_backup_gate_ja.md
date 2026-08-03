# Phase Completion Review／Backup Gate

```yaml
document_id: phase_completion_review_and_backup_gate
status: current_effective
normative: true
language: ja
created_at: 2026-08-02 22:36:57 JST
updated_at: 2026-08-02 22:36:57 JST
owner: 設計統括者役
applies_to: all_phases
rag_default: true
```

## 1. 目的

本書は、各Phaseを「実装が終わったら完了」と誤認せず、Phase単位のFinal Check、Finding解決、User Acceptance、完全復元性、BackupおよびGit／GitHub対応を一つの完了Gateとして扱う共通運用を定める。

本書は既存のPhase Lifecycle、Design Governance Recovery、Research Asset Mutation Control、Git WorkflowおよびUser Authorityを弱化しない。

## 2. 長時間Orchestrationの目標

ユーザーがAccepted Orchestration Envelopeの範囲内で「じゃ、あとよろしく」と委任した場合、設計統括者役、Phase設計担当者役および実装者役は、次のユーザー確認時までに少なくとも1つの有界なWork Unitを完了、Review待ちまたは安全なPauseへ到達させることを運用目標とする。典型的には、夜間に委任され、翌朝までに1 Subphase、1 Follow-up、1 Review Packageまたは1つの同等な作業単位が明確な状態になっている運用を目指す。

これは完了時間の保証またはUser Gateの代行ではない。次の場合は、無理に完了を作らず安全なPauseとEvidenceを優先する。

- Codex利用可能量、Credit、QuotaまたはService Limit
- User Decision、Manual Test、Secret、External Serviceまたは課金操作待ち
- Authority不明、Scope逸脱、Unexpected DiffまたはTest Failure
- Backup、Destructive Action、Git／GitHubまたは公開Gate待ち
- Platform Sleep、Tool停止、Task Limitまたは再開に必要なContext不足

完了できない場合も、最後の確認済み状態、Files Changed、Test、Open Finding、停止理由、次の最小Actionおよび必要Authorityを残す。

## 3. Phase Final Checkの必須化

すべてのSubphaseまたは実装作業がAcceptedに見えても、Phase完了宣言の前にPhase単位Final Checkを必ず行う。

最低限のCheck対象：

```text
Phase Goal／Requirements／Acceptance Criteria
SubphaseごとのAccepted Review／Follow-up
Source／Config／Schema／Migration／Dependency
Static／Unit／Integration／Native／Manual Test
Cross-environment／Lifecycle／Rollback／Recovery
Security／Privacy／Secret／Identity／License／Attribution
Authority／Write Scope／Mutation Inventory／Git／External State
Requirements／Architecture／ADR／Governance／User Manual／Index
Known Limitation／Open Finding／Deferred Item／Non-blocker
Current／Shared／Public／Phase Compilation／Recovery Manifest
Backup Target／Manifest／Hash／Restore Method
Next Phase Entry／Handoff／Task Recovery
```

Final Checkは、個別Subphase Reviewの単な再掲ではない。Subphase間の統合、依存関係、設定元、データ移行、交差Failure、Docsと実装のずれ、権限逸脱および未収録EvidenceをPhase全体として検査する。

## 4. Finding／Non-blockerの扱い

原則として、Phase中に検出したFindingは当該Phase内で解決し、Follow-upと再Reviewを完了してからPhaseを完了する。`non-blocker`というLabelだけで無条件に後送りしない。

次はPhase完了をBlockする。

- Requirements／Acceptance未充足
- Security／Privacy／Secret／Authority／Data Integrity／Recoveryへの未解決影響
- 再現性、安定性、Cross-environment、MigrationまたはRollbackの未確認
- 主要TestのFailure／未実施／証跡不足
- Docsと実装の重要な不一致
- Owner、影響、再開条件または対応Phaseが不明なDeferred Item
- 当該Phase内で安全に解決可能であり、後送りの合理的理由がないFinding

非Blockerの延期は例外とし、少なくとも次を満たす。

```text
受入条件、安全性、正確性、互換性、復元性への未解決影響がない
影響／Reason／Owner／Target Phase／Re-entry Trigger／Verificationが記録済み
Roadmap／Open Finding／Continuity／Handoffへ反映済み
設計統括者役が妥当性をReview済み
ユーザーが延期を明示的に受け入れ済み
```

条件を満たさないFindingは、LabelにかかわらずPhase完了前に解決する。

## 5. Phase完了順序

```text
全Subphase実装／Review完了
  → Phase Final Check
  → Finding解決／Follow-up／再Review
  → 許可されたDeferred Itemの完全記録
  → User Acceptance／User Test Acceptance
  → 設計統括者役のPhase完了／次Phase移行可能宣言
  → Current／Shared／Phase／Public／Continuity Refresh
  → Phase Lossless Compilation／Final Review／Recovery Manifest
  → Design Governance Reconstruction Validation
  → 設計統括者役が「Phase Backupを取得してください」と明示
  → ユーザーがPhase Backup完了を明示
  → Backup Manifest／Hash／Restore Verification
  → Git運用に従いCommit／Tag／Push／GitHub更新
  → 次Phase開始
```

GitとBackupの正確な先後関係はAccepted Git Workflowに従う。ただし、同一のPhase確定SnapshotをBackup、Commit、Tag、Pushおよび公開Evidenceへ関連付け、別状態を同じPhase完了点として混同しない。

## 6. Backup勧告責任

設計統括者役は、各PhaseのBackup Gateへ到達したら、ユーザーが自発的にBackupを取得する予定であっても、必ず「Phase Backupを取得してください」と明示的に伝える。

設計統括者役はユーザーの明示指示なしにBackupを作成、Copy、Move、Delete、Archive、Uploadまたは外部保存しない。役割はBackupを代行することではなく、必要タイミング、対象、除外、Manifest、Hash、Restoreおよび完了確認を案内することである。

## 7. 規模／RiskベースBackup Checkpoint

Phase完了時以外でも、変更の規模、復元難度、不可逆性、作業期間またはResearch Asset Riskに応じ、設計統括者役はBackup Checkpointを勧告する。

勧告または必須Gate候補：

- 大規模なDirectory Migration、Bulk Rename、Bulk Rewriteまたは大量ファイル変更
- Storage／Schema／Migration／Model Artifact／Registry Layoutの変更
- 複数Subphaseまたは長期作業をまたぐ大きな中間到達点
- Git History、Branch、Tag、Merge、Remote、Repository Visibilityまたは公開Surfaceの変更
- 公開Sanitation、Identity／Privacy一括変更、License／Termsまたは外部配布準備
- Cloud／Lightning／External Service／Secret／Permission／Deploymentの大きな再構築
- Destructive Action、Overwrite、Delete、History Rewriteまたは復元不能の可能性がある操作の前
- Context Limit／Task不安定化／Role交代により、完全復元の不確実性が上がる前
- 大きな障害、無許可Mutation疑い、RollbackまたはRecovery完了後
- ユーザーがBackupを希望した場合

Backup必須Gateの場合は、ユーザーのBackup完了宣言を得るまで後続Mutationを開始しない。勧告に留める場合も、その理由と、取得しない場合のRiskを明示する。

## 8. Phase単位GitHub／Backup原則

原則として、Backup、Git Commit／Tag、GitHub更新およびRelease EvidenceはPhase完了単位で対応付ける。ただし、各ActionはそれぞれのAuthorityとユーザー明示承認を必要とし、Phase完了だけを理由に自動Commit、Tag、Push、Uploadまたは公開を行わない。

Phase間の大規模Checkpoint BackupはPhase Backupを代替しない。Phase BackupはFinal Check、User Acceptance、Phase完了／次Phase移行可能宣言、Continuity RefreshおよびReconstruction Validationに対応する確定Snapshotとする。

## 9. Role Responsibility

### 設計統括者役

- Phase Final CheckのScopeとEvidenceを確定する。
- FindingのBlocker／Deferred判定をReviewする。
- Phase完了／次Phase移行可能宣言の前に未解決状態を再確認する。
- Phase Backupまたは規模ベースBackupが必要な時点で、ユーザーへ明示的に伝える。
- Backup完了を推測せず、ユーザーの完了報告を待つ。

### Phase設計担当者役

- SubphaseごとのAcceptance、Finding、Follow-upおよびPhase-local適合性を整理する。
- Final Checkに必要なPhase-local Evidenceと未解決事項を欠落なく渡す。
- Non-blockerを独断で次Phaseへ送らない。

### 実装者役

- Accepted HandoffのTest、Status、Files Changed、Known Limitation、FailureおよびOpen Findingを完全列挙する。
- Test未実施またはFinding残存を「完了」と表現しない。
- Backup、Git、GitHubまたはPhase完了を自動実行／宣言しない。

### ユーザー

- User Acceptance／Manual Test Acceptanceを判定する。
- Backupを実施し、完了を明示する。
- Finding延期、Git／GitHub反映、公開およびPhase移行の必要Gateを最終承認する。

## 10. Stop Conditions

次の場合はPhase完了処理または後続Mutationを停止する。

- Final Check未実施またはEvidence不足
- 未解決Blockerまたは条件不備のDeferred Item
- User Acceptance未完了
- Continuity Refresh／Recovery Manifest／Reconstruction Validation未完了
- Backup必須Gateでユーザー完了報告がない
- Backup SnapshotとCommit／Tag／Push対象が不一致
- Phase完了宣言と実際のRequirements／Test／Docs／External Stateが不一致

## 11. Related Documents

- [Documentation Structure／Task Operations](documentation_structure_and_task_operations_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Research Asset Mutation Control](research_asset_mutation_control_ja.md)
- [Project Continuity Master](../../current/project_continuity/project_continuity_master_ja.md)
- [Public Roadmap](../../../public/roadmap_ja.md)
