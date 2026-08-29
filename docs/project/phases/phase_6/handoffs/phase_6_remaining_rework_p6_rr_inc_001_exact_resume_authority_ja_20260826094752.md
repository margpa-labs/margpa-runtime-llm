# Phase 6 Remaining Rework — P6-RR-INC-001 Exact Resume Authority

```yaml
document_id: phase_6_remaining_rework_p6_rr_inc_001_exact_resume_authority_20260826094752
status: exact_resume_authority
phase: phase_6
provider: codex
from_role: プロジェクト責任者兼設計統括者役
to_role: 設計者兼実装者役
target_task_id: 01a03b6c-2a68-7881-99bc-c788a600f632
created_at: 2026-08-26 09:47:52 JST
resume_from: P6-RR-C-WU-001
phase_6_closure_authority: false
git_authority: false
```

## 1. Controller判定

P6-RR-INC-001は、Project Root外の`/tmp/not_allowed`をstderr Redirect先として指定したUnauthorized Root-outside Actionであり、Incident 0、Root-outside Action 0またはP6-RR-ACC-039 PASSへ再分類しない。

一方、ActorはIncidentを検出後、Project Root外の追加Stat、Read、Write、CleanupまたはDeleteを行わず、Source／Test／Config実装を停止し、Append-only Incident／Recovery／Returnだけを作成した。P6-RR-0／A／Bの技術成果とFocused Validationは、本Incidentと分離して保持できる。

```text
P6-RR-INC-001 Governance Classification : RECORDED／STOPPED_SAFE／NON-BLOCKING FOR DIFFERENTIAL RESUME
Current Root-outside Action Count        : 1 retained
P6-RR-ACC-039                            : FAIL retained
Product Source Rollback Required         : NO
P6-RR-0／A／B Redo Required               : NO
Resume                                   : AUTHORIZED FROM P6-RR-C-WU-001
```

## 2. `/tmp/not_allowed`取扱い

`/tmp/not_allowed`のBefore State、After Existence、Content、SizeおよびOwnershipは未確認のまま保持する。

本Resume Authorityは、対象のInspection、Cleanup、Delete、Truncate、Move、Permission変更または修復を許可しない。Project Root外Actionを追加して過去Incidentを治癒しようとしてはならない。

```text
External Target Inspection : NOT AUTHORIZED
External Target Cleanup    : NOT AUTHORIZED
External Target Mutation   : NOT AUTHORIZED
Historical Record          : PRESERVE AS UNKNOWN／UNVERIFIED
```

## 3. Mandatory Resume Reading

次を記載順に再読し、完了済みPackageを再実行しない。

1. `docs/project/phases/phase_6/handoffs/phase_6_remaining_rework_p6_rr_inc_001_exact_resume_authority_ja_20260826094752.md`
2. `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_root_outside_stderr_redirect_incident_ja_20260826094511.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_remaining_rework_stopped_safe_return_handoff_ja_20260826094511.md`
4. `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_0_entry_baseline_recovery_ja_20260826093853.md`
5. `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_a_requirement_definition_reconciliation_ja_20260826094400.md`
6. `docs/project/phases/phase_6/history/index/phase_6_remaining_rework_package_b_semantic_criterion_compiler_ja_20260826094401.md`
7. `docs/project/phases/phase_6/handoffs/phase_6_claude_remaining_rework_exact_handoff_ja_20260825130924.md`
8. `docs/project/phases/phase_6/history/operations/phase_6_remaining_rework_execution_plan_and_acceptance_ja_20260825130924.md`

## 4. Exact Resume Scope

```text
Completed／Preserve : P6-RR-0-WU-001〜004
Completed／Preserve : P6-RR-A-WU-001〜005
Completed／Preserve : P6-RR-B-WU-001〜005
Resume              : P6-RR-C-WU-001
Continue            : P6-RR-C-WU-002以降をFrozen順序で連結実行
```

P6-RR-C-WU-001のRead／Design Reconciliationは、Gitを使わず、Authorized Project Root内のExact Filesだけを対象として再開する。事故前に未完了だったWUであるため、WU-001自体の差分再開は許可するが、P6-RR-0／A／BをBaselineから作り直してはならない。

## 5. Command／Temporary Boundary Correction

- `/dev/null`、`/tmp`、OS Temporary、User CacheまたはProject Root外PathをRedirect、Log、Cache、Temp、basetemp、stderr抑制その他の目的で使用しない。
- Read CommandのMissing Pathやstderrは隠さず、Exit CodeとTool Outputとして保持する。
- Task-owned Tempが必要な場合は、既存のProject内Task Tempを使用する。
  - `.venv/.t/phase_6_remaining_rework_claude_20260826093407/`
- `pytest`でTemporary Pathを使用し得る場合は、Project内Task-owned `--basetemp`をExact指定する。
- Frontend ToolがCache／Tempを必要とする場合も、Project内Task-owned PathをExact指定する。
- Root外Actionを再度検出した場合は、結果の大小に関係なく即時`STOPPED_SAFE`とする。

## 6. Expected Concurrent Controller Artifacts

次はControllerが作成したScope外Docsであり、Expected Dirtyとして扱う。内容変更、削除、移動、Stage、Blocker化またはCompletion Scopeへの混入をしない。

- `docs/project/shared/history/automation/codex_task_recreation_identity_routing_authority_delivery_and_resource_preservation_evidence_ja_20260826092621.md`
- `docs/project/shared/history/planned_work/claude_fresh_designer_implementer_task_activation_sequence_reservation_ja_20260826094454.md`
- `docs/project/shared/history/automation/claude_task_recreation_and_cross_provider_role_identity_operating_correction_ja_20260826094454.md`

本Resume Authority自体もController-owned Handoffとして保持する。

## 7. Execution Control

- P6-RR-C-WU-001から直ちに差分再開する。
- Routine Progress、Package完了または次Packageへの移行を理由に停止しない。
- 各Package末尾にMandatory Recovery Indexを作成する。
- Complete Candidate、True Stop、Resource Safe StopまたはUser／Controller明示Stopまで連結実行する。
- ControllerはExecutor実行中、Polling、途中Review、並行Testを行わずWAITINGする。
- Return時はProvider、Role、Task Identity、Completed Package、Changed Path、Validation、Acceptance、Open Finding、Incident AccountingおよびExact Next Actionを集約する。
- Phase 6 Closure、Phase 7、Git、Network、Model Artifact Mutation、Provider MemoryおよびUser `runtime_data`へ進まない。

## 8. Resource保全

Codex週間利用可能量の最低保全線はUser Policyとして50%、警戒／停止判断帯は55〜60%付近である。Executorが製品表示を直接観測できない場合は残量を推測しない。

UserまたはControllerからResource Stopを受領した場合、直近Material BoundaryにRecoveryを残し、`STOPPED_SAFE`としてDirect Returnする。

## 9. Resume宣言

```text
P6-RR-INC-001 Review        : COMPLETE
Historical Nonconformance  : RETAINED
External Target Repair     : NOT AUTHORIZED
Exact Resume Authority     : GRANTED
Exact Resume Work Unit     : P6-RR-C-WU-001
Execution                  : RESUME NOW
```
