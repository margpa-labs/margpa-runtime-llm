# Phase 6 Fifth Rework Package D — D-2差分再開Authority

```yaml
document_id: phase_6_codex_controller_package_d_d2_resume_authority_20260823213619
status: authorized_active_on_receipt
phase: phase_6
package: package_d
resume_from: d_2_acceptance_rederivation
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-23 21:36:19 JST
incident_review: accepted_as_unauthorized_historical_evidence
retroactive_authorization: false
root_boundary_exception_created: false
phase_closure_authority: false
git_mutation_authority: false
```

## 1. Controller Decision

`2>/dev/null`による`/dev/null`使用を、P6-CODEX-042 Unauthorized Root Boundary Incidentとして受理する。永続Artifact、不可逆Mutation、Secret／Privacy接触、Source／Test Mutationは発生していない。

本DecisionはIncidentを許可済みへ変更せず、最上位規則の例外も生成しない。Incident発生、正確な申告、STOPPED_SAFE、Recovery作成までをHistorical Evidenceとして保持する。

同IncidentはPackage A〜CおよびD-1の技術成果を無効にせず、D-2以降のProject Root内作業を永久停止させるCurrent Blockerでもない。設計者兼実装者役は本書を新しいExact Resume AuthorityとしてD-2から差分再開する。

## 2. Action Countの分離

以後のReturn Contractでは、過去Incidentと新Resume Cycleを分離する。

```text
Package D Cumulative Root-outside Action:
  1 known unauthorized incident (`2>/dev/null`)

New Resume Cycle Root-outside Action:
  must remain 0

Root-outside Persistent Artifact:
  0 known

Retroactive Authorization:
  0
```

Complete Candidate Handoffで累積Actionを0と書いてはならない。一方、既知Incident 1を理由に技術的Completionを自動的に否定してはならない。Authority ComplianceとTechnical Acceptanceを別々に報告する。

## 3. Mandatory Resume Reading

1. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_d_stopped_safe_root_boundary_incident_ja_20260823213408.md`
2. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_fifth_rework_stopped_safe_handoff_ja_20260823213408.md`
3. `docs/project/phases/phase_6/history/operations/phase_6_gov008_provider_memory_action_inventory_correction_ja_20260823213007.md`
4. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_d_d1_governance_correction_ja_20260823213055.md`
5. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_package_d_resume_exact_handoff_ja_20260823212427.md`
6. 本Authority。

元HandoffのD-2〜D-4、Allowed Scope、Provider Memory禁止、Git禁止、Return Contractは、本書で訂正したAction Count部分を除いて維持する。

## 4. First Action

Source／Test Mutation前に、次を実施する。

1. 本Authority受領後のCurrent PositionをRead-onlyで確認する。
2. `history/index/phase_6_fifth_rework_package_d_d2_second_resume_entry_ja_<timestamp>.md`を新規作成する。
3. D-1完了、P6-CODEX-042記録済み、D-2未完了、Active Process 0を記録する。
4. D-2 Acceptance全ID再導出から再開する。

Package A〜CおよびD-1をやり直さない。Final Verificationで新Failureが出た場合だけ、その原因へ直接必要な最小範囲を修正する。

## 5. Filesystem／Temporary Discipline

- `2>/dev/null`、`>/dev/null`、`&>/dev/null`を使用しない。
- 存在しない可能性があるDirectoryは、Project Root内のExact Pathへ`test -d`等のRead-only確認を行ってから、存在するPathだけをCommand引数へ渡す。
- TestのTemporary、Cache、Base Temp、Logが必要な場合はProject Root内のTask専用Pathへ明示的に固定し、Pathと残存状態をRecoveryへ記録する。
- Task専用Temporaryを自己判断で削除しない。Final Returnでユーザー／Controller Cleanup Gateへ渡す。
- `.claude/`、`.codex/`その他Provider MemoryをRead／Write／Delete／Repairしない。
- User `runtime_data/`、`other/`、Backup置場、Public別Repositoryへ触れない。
- 既に明示許可されたPhase 6実Model Artifactは、既存Exact Model Authorityの範囲内でRead／Loadできる。許可済みResolved Model Target以外へ拡張しない。

## 6. D-2〜D-4

### D-2

Phase 6 Acceptance Matrixの全84 IDを個別再導出する。Status、Evidence Source、Evidence Grade、Current Impactを必須とし、Package A〜C変更の影響を再評価する。完了時にRecovery Entryを作成する。

### D-3

元Handoffに定めたReal Runtime／Browser Matrixを実施する。長時間実Model実行前とD-3完了時にRecovery Entryを作成する。

### D-4

Backend、Focused Test、Ruff、Mypy、Frontend、Real Model／Browser Evidenceを最終照合し、Exact changed／new files、Command、Exit Code、未実施事項を記録する。完了時にPackage D Final RecoveryとFifth Rework Complete Candidate Handoffを作成する。

通常のTest Failure、型Error、実装Bug、Evidence不足は、自身のAuthority内で解消できる限りUser／Controllerへ返さない。真の新規Stop Conditionまたは利用制限だけでSTOPPED_SAFEにする。

## 7. P6-CODEX-042 Disposition

```text
Incident occurrence             : CONFIRMED
Authorization at occurrence     : NONE
Persistent artifact             : NONE KNOWN
Irreversible／Data impact       : NONE OBSERVED
Disclosure                      : COMPLETE
STOPPED_SAFE                    : COMPLETE
Recovery entry                  : COMPLETE
Retroactive permission          : NONE
Current technical impact        : NONE
Current transition impact       : NONE after this new authority
Historical evidence disposition : RETAIN
```

P6-CODEX-042は「Incidentが存在しなかった」という意味ではClosedにしない。`RECORDED／STOPPED／RECOVERED／NON-BLOCKING FOR NEW IN-ROOT CYCLE`としてFinal Handoffへ残す。

## 8. Return Contract Correction

Final Returnは次を含む。

```text
Status: COMPLETE_CANDIDATE または STOPPED_SAFE
Package D Cumulative Root-outside Action: 1 known incident
New Resume Cycle Root-outside Action: 0
Root-outside Persistent Artifact: 0 known
Provider Memory Contact by Codex Tasks: 0
Git Mutation: 0
Network Action: 0
User runtime_data Contact: 0
P6-CODEX-042: RECORDED／STOPPED／RECOVERED／NON-BLOCKING
Next Action: Controller Independent Review
```

Phase 6 Closureへ進まず、Controllerへ直接報告して停止する。
