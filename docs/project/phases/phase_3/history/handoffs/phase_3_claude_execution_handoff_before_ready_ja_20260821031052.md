# Phase 3 Claude Code Execution Handoff — Start-gated Candidate

```yaml
document_id: phase_3_claude_execution_handoff
status: draft_not_authorized_to_start
phase: phase_3
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
created_at: 2026-08-21 02:05:30 JST
authority_revision: candidate_1
automation_level_candidate: phase
automation_control_state: OFF
completion_line: phase_3_g_complete_candidate
git_mutation_authorized: false
provider_memory_authorized: false
root_external_action_authorized: false
implementation_authorized: false
```

## 0. STOP

本Handoffは設計候補であり、現時点でPhase 3実装を開始してはならない。

開始には、Phase 2-F Closure、User Design Acceptance、Backup通知、Codex `READY／ARMED`およびその後のUser開始宣言を必要とする。開始時には本FileのAccepted／Frozen Successorまたは明示Acceptance Evidenceが与えられる。

## 1. Mission after Activation

Phase 3-0からPhase 3-Gまでを、Phase 3 Design Packageと最上位規則の内側で連結実行し、`COMPLETE_CANDIDATE`としてCodexへ返却する。

Phase 3-H、Final Docs統合、ユーザー実Mac Acceptance、Backup、Git、Phase 3完了宣言またはPhase 4開始へ進まない。

## 2. Mandatory Reading Order

開始許可後、次を全文で読む。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. `docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`
5. `docs/project/phases/phase_3/phase_index_ja.md`
6. `docs/project/phases/phase_3/requirements/phase_3_requirements_ja.md`
7. `docs/project/phases/phase_3/architecture/phase_3_architecture_ja.md`
8. `docs/project/phases/phase_3/adr/phase_3_adr_ja.md`
9. `docs/project/phases/phase_3/governance/phase_3_claude_automation_governance_ja.md`
10. `docs/project/phases/phase_3/operations/phase_3_definition_source_inventory_ja.md`
11. `docs/project/phases/phase_3/operations/phase_3_execution_plan_ja.md`
12. `docs/project/phases/phase_3/operations/phase_3_acceptance_matrix_ja.md`
13. 本Handoff。
14. `docs/project/current/governance/runtime_governance_specification_ja.md`
15. `docs/public/roadmap_ja.md`のPhase 3／Phase 4。
16. `definitions/`のManifest対象Source。
17. Phase 3開始時点でCodexが指定する最新Phase 2-F Closure／Phase 3 Entry Index。

一つでも読めない、Stale、ConflictまたはSuccessor不明なら、実装せずRecovery Stateを返す。

## 3. Role

あなたは特定Subphase専属ではない`Claude側設計統括者役`であり、Phase 3内で`phase_designer／designer_implementer／reviewer`責務を動的に兼務する。

Routineな設計具体化、Exact Path選定、実装、Focused Test、局所ReworkおよびSelf-reviewを、毎回Userへ返さずに行う。Authority拡張、Root外、Stable Existing Write、Git、External、Secret、User実Data、Phase 4前倒しまたは重大Risk受容だけを上位へ返す。

## 4. Authorized Root／Forbidden Boundary

Authorized Rootは、開始時にCodexが示す`margpa-runtime-llm/`一つだけである。

禁止：

- Root外のRead／List／Stat／Search／Write／Execute／Temporary Artifact。
- `other/`、別Project、Provider Memory、外部`.claude/`／`.codex/`。
- Git／GitHub Mutation。
- User実`runtime_data/`。
- Network、Remote Download、External Service、Secret、課金。
- 誤生成物の自己Cleanup。
- Existing Historyの変更。

## 5. Candidate Write Classes after Activation

各Work UnitでExact PathをFreezeした後に限り、次を候補Write Classとする。

- `src/margpa_runtime_llm/modules/audit_evidence/**`
- `src/margpa_runtime_llm/modules/governance_definitions/**`
- `src/margpa_runtime_llm/adapters/audit_evidence/**`
- `src/margpa_runtime_llm/adapters/governance_definitions/**`
- 必要な`bootstrap／entrypoints／web`の限定Integration File。
- 必要な`frontend/src/**`とBuild Output同期対象。
- `tests/unit|integration/audit_evidence/**`
- `tests/unit|integration/governance_definitions/**`
- 必要な既存Configuration／Web／Frontend Regression Test。
- `definitions/`のManifest／README／明示Correction対象。
- `docs/project/phases/phase_3/history/**`の新規Append-only File。
- `docs/project/shared/history/automation/**`の新規Meaningful Cycle Evidence。

この一覧は全Fileの自動生成命令でも、無条件Write許可でもない。Unitに必要なものだけをExact Manifestへ選ぶ。

## 6. Mandatory Invariants

1. Default Modeは`off`。
2. `off`のProvider／Adapter／Compiler／Governance Hook Callは0。
3. `observe`は非介入、追加Model Call／Token／Repair 0。
4. Phase 3の`enforce`はUnavailable、Silent Downgrade 0。
5. 全Compiled PlanはUnbound／Non-executable。
6. Filename／Directory／Top Key inference 0。
7. Dynamic Import／Shell／URL Download／Definition Code Execution 0。
8. Raw CoT／Secret／System Prompt／Hidden Original／Full Content Evidence 0。
9. Public／Basic Governance／Definition／Evidence Binding 0。
10. Existing v1／v2／Conversation／RAG／Citation Regression 0。
11. Provider Memory、Git、Root外、User実Data Mutation 0。
12. ClaudeはPhase 3-Gで停止。

## 7. First Action after Activation

最初にP3-0-WU-001だけを実行する。Design Packageを読んだ直後にSource実装へ飛ばない。

P3-0-WU-001でAuthority、Phase 2-F Closure、Root、Completion Line、Current TreeおよびRecovery Entryを確認し、P3-0-WU-002へ進めるか自分で`GO／ADJUST／STOP`を判定する。

## 8. Compaction Protocol

UserがLong-running Modeを有効化した場合、Work UnitのMaterial BoundaryでCurrent Operational StateとRecovery Indexを最新化し、Rolling Hashを記録する。

Compaction後はOperating Notesから読み直し、Hashだけでなく、Role、Authority Revision、Current WU、Accepted Predecessor、Open Finding、Exact MutationおよびNext Routeを照合する。

Auto-Compactionを検知しなかったCycleをFailureとして捏造しない。検知したのに復旧できなかった場合は失敗として記録する。

## 9. Test／Evidence Policy

- Testは`tmp_path`等の隔離Fixtureを使用する。
- `PYTHONDONTWRITEBYTECODE=1`等で不要なProject内Cache増加を抑える。
- 既存Testを削除、Skip化、Assertion弱体化またはTarget外ししてPASSを作らない。
- Focused→Subphase→Fullの順で検証する。
- Evidence Fileは意味のあるWork Unit／Rework単位へまとめ、毎Commandごとに作らない。
- 完了報告前に自分でDesign Conformance Reviewを行う。

## 10. Completion Return

Phase 3-G-WU-004で一つのCompletion Handoffを作り、次を返す。

- `GO／ADJUST／STOP` Recommendation。
- Technical Blocker、Governance Incident、Deferred Evidence。
- Exact Source／Test／Definition／Docs Mutation。
- Full／Focused／Static／Frontend Result。
- Mode Matrix、Definition Corpus、Evidence Recovery Result。
- Compaction Cycle／Recovery Fidelity。
- Human Clarification／Intervention／Mismatch／False Completion／Self-repair。
- Manual Acceptance候補。
- Rollback Boundary。
- Codex Independent Reviewの入口。

返却後は停止し、追加修正を自動開始しない。
