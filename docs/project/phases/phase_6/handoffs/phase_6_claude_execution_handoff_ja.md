# Phase 6 Claude Execution Handoff

    document_id: phase_6_claude_execution_handoff
    status: accepted_frozen_not_activated
    phase: phase_6
    from: プロジェクト責任者兼設計統括者役（Codex）
    to: Claude側設計統括者役
    recorded_at: 2026-08-22 21:13:08 JST
    automation_control_state: OFF
    implementation_authorized: false
    completion_line: phase_6_i_complete_candidate

## 1. Current Instruction

本HandoffはAccepted／Frozen済みのPhase 6実行契約であるが、実行開始指示ではない。Phase 5は`COMPLETE／ACCEPTED／CLOSED`であり、現在はUser Backup待ちである。

次が全て成立した後だけActivateする。

    Phase 5 Closure／Phase 6 Design Freeze
      → User Phase 6開始前Backup
      → Exact Model／Disk／Scope Authority
      → Codex Activation Preflight
      → Codex ARMED
      → User Start

## 2. Mandatory Reading Order

1. docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md
2. docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md
3. docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md
4. docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md
5. docs/project/shared/history/planned_work/phase_4_to_6_runtime_governance_program_design_ja_20260821220422.md
6. docs/project/shared/history/planned_work/phase_6_0_deepseek_local_runtime_switch_design_ja_20260822105531.md
7. docs/project/shared/history/planned_work/phase_6_0_deepseek_local_runtime_switch_handoff_ja_20260822105531.md
8. docs/project/shared/history/planned_work/phase_6_0_advanced_runtime_component_identity_projection_ja_20260822150342.md
9. docs/project/shared/history/planned_work/phase_6_8_component_identity_mode_and_constitution_separation_followup_ja_20260822151607.md
10. docs/project/shared/history/planned_work/phase_6_integrated_scope_and_current_constitution_layer_label_followup_ja_20260822152513.md
11. docs/project/phases/phase_6/phase_index_ja.md
12. Phase 6 Requirements／Architecture／ADR。
13. Phase 6 Governance／Execution Plan／Acceptance Matrix。
14. Phase 5 Phase Index／Final Codex Acceptance／Final Closure／As-built Source／Tests。
15. Phase 4 Phase Index／Final Closure／As-built Source／Tests。
16. docs/project/current/governance/runtime_governance_specification_ja.md
17. docs/project/phases/phase_2/architecture/phase_2_runtime_data_root_and_recording_architecture_ja.md
18. Current Model Registry／Application／Deployment Profile／llama.cpp Adapter／Configuration Control／Web UI。
19. Phase 6 Activation Receipt。存在しない場合は開始不可。
20. Receiptで許可された範囲内のmodels/main/deepseek-r1-0528-qwen3-8b Canonical Snapshot、Qwen Load SubtreeおよびRepository内Download Evidence。Receiptより先にResolved Target内容を読まない。

Provider Memory、Conversation Summary、言語、Timestampまたは自己の記憶でMandatory Readingを代替しない。

## 3. Objective

Phase 6-0から6-Iまでを依存順に連結実行し、次を一つのRuntime Governance MVPとして成立させる。

1. Qwen Defaultを維持したDeepSeek Q4 Local Gate。
2. Runtime Model Switch、Dynamic Context Size、Dynamic Max New Tokens。
3. Deterministic Judge、LLM-as-a-Judge、Calibration。
4. Authority／Budget付きBounded Repair。
5. Request-correlated Status、Safe Refusal、Feedback、Recording。
6. Current Runtime Identityと利用者向けUI整理。
7. Qwen／DeepSeek、各Mode、Judge／Repair比較。

Subphase境界でRecoveryを残すが、状況報告だけを理由に停止しない。

## 4. Required Behavior

- 各WU開始前にFrozen ContractとAs-builtからExact Mutationを動的に解決する。
- 必要なSource／Testだけを作り、固定Packageを無条件に量産しない。
- Frozen Scope内の局所Bug／Test Failure／UI不整合はSelf-reviewして継続する。
- Model／Judge／Repair／Recordingの成功をFake／Stubだけで主張しない。
- User実runtime_dataをTest Fixtureにしない。
- RAGは機能互換Smokeに限定し、Phase 7前に最終品質Acceptedと主張しない。
- Completion Handoffは日本語で、Exact Result／Evidence Class／Open Major Findingを記録する。

## 5. Activation-time Model Authority

Activation Receiptで明示された場合だけ、次を許可できる。

- models/main/deepseek-r1-0528-qwen3-8b/gguf/へのDerived Q4_K_M新規作成。
- 同Model専用Manifest／Provenance新規作成。
- Current Registry／Model DefinitionへDeepSeek Candidateを追加するSource／Config変更。
- Local MacでのDeepSeek Load／Unload／Streaming／Cancel／Reload Test。

modelsはSymbolic Linkであるため、Activation ReceiptにはLogical Pathだけでなく、Userが確認したResolved Physical Targetと、Qwen Read／Load専用Subtree、DeepSeek Canonical Read専用Subtree、DeepSeek Derived／Manifest／必要時Work専用Write Subtree、期間および目的を記録する。過去Download Cycleの例外はPhase 6へ引き継がない。Exact ReceiptがなければModel Gateは開始せず、Qwen経路の設計／実装へも勝手にTarget Readを混入しない。Conversion Intermediateは無断削除しない。

許可しない。

- huggingface Canonical Snapshotの変更／削除。
- Qwen Current Artifactの変更／削除。
- DeepSeek V4のConversion／Load／削除。
- Network Download。
- DeepSeekのStartup Default昇格。
- Project Root外Cache／Temp／Model配置。
- 許可済みSymlink Target内であってもSibling Model、親Directoryまたは未指定Subtreeへの接触。

## 6. Frozen Decisions

    Startup Main Model          : Qwen3-4B
    Local DeepSeek Candidate    : R1-0528-Qwen3-8B Q4_K_M
    V4 Flash Local              : OUT OF SCOPE
    Server Restart for Switch   : 0
    Model Internal Reload       : Allowed for Context
    Runtime Selection Persist   : Deferred
    Judge Default               : OFF
    Repair Default              : OFF
    Recording Default           : OFF
    Protected Capture           : OFF／Deferred
    RAG Final Quality Review    : After Phase 7
    Current Constitution Layer  : Phase 8
    Claude Completion Line      : Phase 6-I

## 7. UI Decisions

- Current Main Model。
- Current Guardrail Model。
- Current LLM-as-a-Judge Model。
- Current Governance Layer。
- Context Size Current／Maximum／State。
- Max New Tokens Current／Maximum／State。
- Main Runtime GovernanceとGuardrail GovernanceからPhase番号Suffixを削除。
- 今後の利用者向け機能名にも原則Phase番号を付けない。
- Phase 3専用設定Panelは通常利用者向けSurfaceから整理し、内部Definition基盤は保持。
- Guardrail Rejectを生Error Codeでなく安全なJA／EN拒否表示へ変換。
- Current Requestで未実行のPointへ前回結果を表示しない。

## 8. Validation

Validation Ladderと全Acceptance IDは次を正本とする。

- operations/phase_6_execution_plan_ja.md
- operations/phase_6_acceptance_matrix_ja.md

最低限、Backend Full、Frontend Test／Typecheck／Lint／Build、Ruff、Mypy、Model実Load、Real Browser、Public／Basic Call-0、User実runtime_data 0、未許可Root外／Git Mutation／Network 0を含める。Read-only Git InspectionとReceipt記載のModel Symlink Target操作は、Unauthorized Action 0とは別にExact Evidence化する。

TemporaryはProject-local専用Rootを使う。Full SuiteはMaterial Boundaryで実行し、小修正ごとに大量Context／Evidenceを生成しない。

## 9. Stop Conditions

- Root／Authority／Stable／Git／External／User Data Scope拡張。
- Frozen User Decisionの変更。
- 未承認Model／Disk／Thermal／Memory Risk。
- models SymlinkのResolved Target／DeepSeek専用Subtreeに対するCurrent CycleのExact Human Authorization不足。
- Irreversible MigrationまたはCanonical Artifact破壊。
- Phase 7／8／10以降を実装しなければPhase 6が成立しない重大衝突。
- 最上位規則違反。

次は停止理由ではない。

- Routine Test Failure。
- Local UI Bug。
- Naming／Import衝突。
- Subphase完了報告。
- Auto-Compaction。
- 5時間利用制限後の自動再開。
- Deferred事項。

## 10. Completion Handoff

新規作成：

    docs/project/phases/phase_6/handoffs/phase_6_claude_complete_candidate_handoff_ja.md

必須内容：

    Phase 6-I Recommendation
    Technical／Security Blockers
    Governance Incidents
    Controller-owned Work
    Deferred Evidence／Current Impact
    Exact Mutation
    DeepSeek Canonical／Derived／Load Evidence
    Qwen→DeepSeek→Qwen／Rollback
    Context／Max Tokens
    Judge／Calibration／Repair／Budget
    Safe Refusal／Request Status
    Feedback／Recording／Sensitive Data
    Advanced UI／Naming／Legacy Panel
    Qwen／DeepSeek Comparative Result
    Focused／Full／Static／Frontend／Browser
    Public／Basic／runtime_data／Root／Git／Network
    Compaction／Quota／False Completion／Human Burden
    Open Major Finding
    Next Action: Codex Phase 6-J Independent Review only

Completion Handoff作成後はPhase 6-J、Git、Phase 7または外部作業へ進まず停止する。
