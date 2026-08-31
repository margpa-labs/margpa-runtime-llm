# Phase 8 Claude Approval Evidence Scope Final Micro Rework — Exact Handoff

```yaml
document_id: phase_8_claude_approval_evidence_scope_final_micro_rework_exact_handoff_20260831001957
document_type: exact_differential_execution_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 00:19:57 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-CR5_approval_evidence_scope_only
implementation_authority: true
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
phase_8_closure_authority: false
phase_9_authority: false
git_authority: false
network_authority: false
real_browser_authority: false
real_model_authority: false
real_mcp_authority: false
backup_authority: false
```

## 1. 継続前提

これはFresh Task Bootstrapではない。現在のClaude Task、Current Working TreeおよびP8-CR0〜CR4の成立済み実装を継続する。

次を行わない。

- Role Bootstrap、旧Mandatory ReadingまたはP8-A〜P8-Fの再読。
- P8-A〜P8-F、P8-CODEX-001、P8-CODEX-003の再実装。
- 新Task化、Context／Authority初期化、Rollback。
- Frontend変更またはFrontend Test再実行。

## 2. Active Differential Contract

本Handoffと次のController再Reviewだけを差分正本として読む。

```text
/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_8/history/operations/phase_8_codex_controller_post_first_rework_re_review_ja_20260831001957.md
SHA-512: 607920be01773844bb2639c266238ef3eaaee473415c79f3a3f7770b4f9694e77f647883dce3fddeba3f9949d1ce23a8b80b895554c38b16a0fc1933403bad14
```

Preserved Baseline：

```text
Exact Return:
docs/project/phases/phase_8/handoffs/phase_8_claude_post_controller_first_review_bounded_rework_exact_return_handoff_ja_20260831000825.md
SHA-512: f2d55c1eddfc8ef96fa075e6a192f516f1cb7158ad4fbe9b779861031037b3f48220607159265a634f34be35e7ab63b269cfe0e7bedc4fdc40d22d5df3cd02a7

Recovery:
docs/project/phases/phase_8/history/index/phase_8_claude_post_controller_first_review_bounded_rework_complete_package_recovery_ja_20260831000825.md
SHA-512: 1e65a6a1f9c441b820ecf2c2c0d50d804cf274a2e0d57c582879c9c24ed9688e6b37acd242f8c55ac02e0d51b0dcfcc41d4dde1334c5680fbaacb30fe1b7246f
```

Preserved Baselineは再読不要。Current Taskが既に保持する成立済みStateの識別子である。

## 3. Finding Freeze

本Taskで扱うFindingは1件だけである。

```text
P8-CODEX-004 Approval EvidenceのRun Scope不照合とCompatibility BoolによるGate迂回
```

成立済みの次は変更しない。

- Run単位LockとConcurrency Regression。
- EnvelopeのServer-side発行、Persist、Run／Step／Tool／Resource／Expiry照合。
- Acceptance `38 PASS / 1 PARTIAL / 1 USER MANUAL GATE`。
- Manual URL Evidence、Archive、Runtime Constitution、Dev Agent UI。

## 4. Required Rework

### 4.1 Typed Approval Evidenceを真の正本にする

- `_has_approval_evidence(run, step)`は少なくとも次をすべて照合する。
  - `evidence.run_id == run.run_id`
  - `evidence.step_id == step.step_id`
  - `evidence.tool_id == step.tool_id`
  - `evidence.decision == APPROVED`
- 対象ToolにImportant Gate Reasonがある場合、Evidenceの`gate_reason`も現在Descriptorと一致させる。
- Envelope付き新規Runでは、Typed `ApprovalEvidence`なしに`StepRecord.approved=true`だけでGateを通過させない。

### 4.2 Contract／Persistence Boundary

- `RunSnapshot`またはRun Store Load Boundaryで、`ApprovalEvidence.run_id`が親Runと異なるStateを拒否またはFail-closedにする。
- EvidenceのStep ID／Tool IDがPlan／Step Recordと相関しないStateも、Approval Authorityとして使用しない。
- 既存のPre-P8-CR2 Run（`envelope is None`、`approvals == ()`）を破壊しない。
- Legacy `approved: bool`を維持する場合、その効力はLegacy Runへ明示的に限定する。安全なMigrationを選ぶ場合は、虚偽Actor／Timestamp／Gate Reasonを捏造しない。

### 4.3 Required Regression Tests

最低限、次を実行可能Testで証明する。

1. Run Aで承認したEvidenceを、同一Step／Toolを持つRun Bへ移してもRun BのTool Executionは0。Store Loadで拒否するか、RuntimeでGate／authority denialへ収束する。
2. Envelope付きRunで`approved=true`、Typed Evidence 0件へ改変してもTool Executionは0で、Approval Gateを迂回しない。
3. 同一Run／同一Step／同一Tool／正しいGate Reasonの正規Evidenceは、Restart後も一度だけ実行を許可する。
4. 別Step／別Toolの既存Regressionを保持する。
5. Pre-P8-CR2 Legacy Runは既存互換Contractどおり読取り・実行可能。

ProbeはFake／Deterministic Toolだけを使う。User `runtime_data/`へ触れない。

## 5. Scope Stop

次を実装しない。

- Generic Authorization Policy Language。
- Envelope署名、暗号化、Key管理。
- Cross-process／Distributed Lock。
- Real Filesystem／Network／MCP Tool。
- P8-CODEX-004と無関係なHardening、UI調整またはDocs再編。
- Phase 8 Closure、Roadmap、Git、Backup、Phase 9。

## 6. Verification

1. Approval／Envelope／Persistence Focused Test。
2. Backend Canonical Test。
3. Mypy。
4. Ruff。
5. Internal Review 1 Cycle。

Frontend Source変更は禁止しているため、Frontend Test／Buildは再実行しない。

## 7. Execution Control

- Current TaskのままP8-CR5を開始し、修正、Test、Internal Review、Recovery、Exact Returnまで連結実行する。
- 実装難度、Blast Radius、Review前、Minor Finding、Progress ReportはTrue Stopではない。
- Routine Progress報告後も自走する。
- Resource Hard Stopが接近した場合だけ、Current WUのExact Recoveryを作成してSafe Returnする。
- 新しいBootstrap、再Compaction要求または確認待ちは行わない。

## 8. Return Contract

Exact Returnには次を含める。

```text
P8-CODEX-004 Disposition
Changed Paths
Run A Evidence -> Run B Reuse Rejection Evidence
Envelope付きBool-only Bypass Rejection Evidence
Normal Approval / Restart / Legacy Compatibility Evidence
Focused / Canonical / Mypy / Ruff Results
Internal Review Finding / Rework
Process Action Inventory
Exact Next Action: Codex Controller Final Re-review -> User Manual Gate
```

Append-only Recovery IndexとExact Return Handoffを作成し、最大Claimを`COMPLETE_CANDIDATE_FOR_USER_MANUAL`として停止する。
