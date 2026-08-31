# Phase 8 Claude用 ゼロベースController Blocker限定Rework Exact Handoff

```yaml
document_id: phase_8_claude_zero_based_controller_blockers_bounded_exact_handoff_20260831005304
document_type: exact_execution_handoff
document_state: final
language: ja
created_at: 2026-08-31 00:53:04 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
implementation_authority: true
independent_review_authority: false
phase_8_closure_authority: false
git_authority: false
network_authority: false
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
exact_start: P8-RW6-0
```

## 1. 目的

Phase 8を製品品質へHardeningするTaskではない。Codex Controllerのゼロベース再Reviewで確認した、PoC／MVP成立を妨げる4 Blockerだけを限定是正する。

```text
P8-CODEX-005  Redirect後Source AuthorityとRequested／Canonical URL
P8-CODEX-006  Deterministic Dev Agent Budget
P8-CODEX-007  Completionを含むImportant Gate実配線
P8-CODEX-008  Constitution OFF／OBSERVE／ENFORCE非Activation Preview
```

P8-CODEX-001〜004は解消済みBaselineであり、再実装しない。Phase 8全体、P8-A〜F、Web Search、正式Level 1 Agent、Real MCP、GD／Semantic Governance、Enterprise HardeningへScopeを拡張しない。

## 2. Task継続

現在のClaude Taskをそのまま継続する。Fresh Task化、Role Bootstrap、Authority初期化、過去Mandatory Readingの全再読、旧Packageの再実行を行わない。

Current Working Treeを正本とする。直前のClaude Returnを成立済みBaselineとして維持し、本HandoffとController Reviewだけを差分Contractとして読む。

## 3. Mandatory Differential Reading

次を全文確認する。

1. Controller Zero-based Review
   `docs/project/phases/phase_8/history/operations/phase_8_codex_controller_zero_based_second_full_re_review_ja_20260831004652.md`
   SHA-512: `116b8276bc08042eae75b3c7a16e8218bad4b1f76bb13dd721912d2c901aa38cd18c757b7af74bab5849385a9bbb0918d4ea03bce8a96383b9f1f9aabb8ee0bf`

2. Preserved Baseline Return
   `docs/project/phases/phase_8/handoffs/phase_8_claude_approval_evidence_scope_final_micro_rework_exact_return_handoff_ja_20260831003203.md`
   SHA-512: `ecc681f59a5893232125217e061987c978f6c5562ffa4a00d9250bf21323e2111dc7a1e928b8fe77a2dc013ab3036c5b8c46d7b2c501a05fa196b082d7549121`

正本の該当箇所に疑義がある場合だけ次を参照する。全再読Receiptは不要。

- `docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md`
- `docs/project/phases/phase_8/architecture/phase_8_architecture_ja.md`
- `docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md`

## 4. Explicit Non-Blockers／Do Not Rework

次は今回のPoC／MVP Blockerではない。実装・修正・追加調査を行わず、既存の未解決課題へ送る。

```text
P8-CODEX-009
最後のTool成功後、Run Completedまで追加Advanceが必要なManual／UI差。

P8-CODEX-010
Manual URL Conversation Test 3件の実DNS依存による非Hermetic性。
```

また、P8-ACC-038のGD相関PARTIAL、Real Browser User Gate、Phase 6／9残件、正式Constitution Enforcementは今回扱わない。

## 5. Work Packages

### P8-RW6-0 — Entry／Claim Correction

- 前回`USER_MANUAL_READY`をSupersededとして扱う。
- P8-CODEX-001〜004をRESOLVEDのまま保持する。
- 変更予定PathとFocused Testを確定する。
- 新しい設計基盤やSchemaを必要以上に増やさない。

### P8-RW6-A — Redirect Evidence Truthfulness

P8-CODEX-005を解消する。

- Requested URLと最終Canonical URLを別Fieldで保持する。
- Source Authorityは取得した最終Canonical URL Hostから算出する。
- Evidence、Citation、Persistence、REST／SSE、UIで両URLを損失なく扱う。
- RedirectによってAuthority Classが変わるRegression Testを追加する。
- Redirect Chain全履歴、Browser Isolation、Hostile-site解析は追加しない。

Acceptance Target: `P8-ACC-012 PASS`

### P8-RW6-B — Deterministic Dev Agent Budget

P8-CODEX-006を解消する。

- Fake／Deterministic Tool Foundationに比例したFrozen Budget LimitをRunへ追加する。
- Tool実行前に消費予定量をCheckする。
- UsageをRunへ記録・永続化する。
- 超過時はToolを呼ばずTyped Stop／Failureへ収束する。
- Reload／Restart後もLimitとUsageを保持する。
- 実料金、Token課金、Provider Cost API、Networkは使わない。

Acceptance Target: `P8-ACC-036 PASS`

### P8-RW6-C — Important Gate Runtime Completion

P8-CODEX-007を解消する。

- Important Gate 8 ReasonをGeneric Gate Contractで扱えることをFixture Testで証明する。
- `important_gate_only`ではCompletion前にRun-level Completion Gateを発行する。
- Completion Approval EvidenceはRun Identity、Reason、Decision、Actor、Timestampを持つ。
- Step Approval EvidenceをCompletionへ流用できない。
- Pending／Denied／Approved／Restart／CancelをTestする。
- Real Network、Cost、Secret、Irreversible Toolは追加しない。Category別Fixtureで十分とする。

Acceptance Target: `P8-ACC-034 PASS`

### P8-RW6-D — Constitution Three-mode Non-activation Preview

P8-CODEX-008を解消する。

- Production Active Constitution ModeはPhase 8の境界どおりOFF固定を維持する。
- 同一ManifestをOFF／OBSERVE／ENFORCEとしてPure EvaluationするPreview API／UIを追加する。
- PreviewはRuntime Activation、External Action、Tool Authority、Model Injectionを一切発生させない。
- 各ModeのDecision／Action Permission／Violation Presentation差を比較可能に表示する。
- 「PreviewでありActive Runtime Modeではない」とUIに明示する。
- 本格的なConstitution統合、GD接続、Enforcement Engineを前倒ししない。

Acceptance Target: `P8-ACC-021 PASS`

### P8-RW6-E — Canonical Verification／Internal Review／Return

- 変更範囲Focused Testを実行する。
- Backend Canonical Test、Mypy、Ruffを実行する。
- Frontend変更があるためFrontend Test、Typecheck、Lint、Buildを実行する。
- 40 Acceptanceを再集計する。
- 期待上限は次とする。

```text
PASS                 37
PARTIAL               1  P8-ACC-038
FAIL                  1  P8-ACC-039 / P8-CODEX-010（既知・PoC非Blocker）
USER MANUAL GATE      1  P8-ACC-040
TOTAL                 40
```

P8-ACC-039をPASSへ捏造しない。既存環境で全Suiteが通った事実と、Network制限環境で3 Testが非Hermeticな事実を両方記録する。

1 CycleのInternal Reviewを行い、今回の4 Blockerに直接関係するCritical／MajorだけをReworkする。Minor、Hardening、別Phase範囲は未解決へ送る。

## 6. Autonomy／Recovery

- P8-RW6-0からEまで連結実行する。
- Routine Report、Diff量、Core Pipeline、Review前、Minor Findingを理由に停止しない。
- Package Boundaryごとに簡潔なRecovery Indexを残す。
- Resource Hard Stopが近い場合はCurrent WUの成立点、Partial、Changed Paths、Tests、Exact Next Actionを記録してSafe Returnする。
- 不要な再Bootstrap、全Docs再読、重複Full Testを行わない。

## 7. Authority Boundary

許可：

- Project Root内Source／Test／Frontend／Phase 8 Docs変更
- Project Root内の既存Fixtureを使うCommand／Test／Build
- Package RecoveryとExact Return Handoff作成

禁止：

- Git操作
- Backup
- Phase 8 Closure／Roadmap変更／Phase 9開始
- Real Network／Real Model／Real MCP／外部Site／User runtime_data
- Root外へのWrite、Install、Temporary Artifact
- P8-CODEX-009／010および他Phase残件の便乗修正

## 8. Return

完了後は次を返す。

- 4 Finding別DispositionとEvidence
- Changed Paths
- Focused／Canonical Verification
- Corrected 40 Acceptance集計
- Internal Review Finding
- 未解決として保持したP8-CODEX-009／010／P8-ACC-038／040
- Recovery Index Path
- Exact Return Handoff PathとSHA-512

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL`。Return後はCodex ControllerのTargeted Re-review待ちで停止する。
