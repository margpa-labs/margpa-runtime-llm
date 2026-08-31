# Phase 8 Post-Controller First Rework — Codex Controller再Review

```yaml
document_id: phase_8_codex_controller_post_first_rework_re_review_20260831001957
document_type: controller_independent_re_review
document_state: final
language: ja
created_at: 2026-08-31 00:19:57 JST
provider: Codex
role: プロジェクト責任者兼設計統括者役
review_target: phase_8_claude_post_controller_first_review_bounded_rework_exact_return_handoff_ja_20260831000825.md
review_scope: p8_codex_001_through_003_bounded_re_review
phase_8_closure: not_claimed
```

## 1. 結論

P8-CODEX-001の同一Run並行実行と、P8-CODEX-003のAcceptance集計訂正は成立した。P8-CODEX-002も、Run-scoped `AuthorizationEnvelope`の生成・永続化・実行直前照合と、`ApprovalEvidence`の生成・永続化までは成立している。

ただし、Approval EvidenceのRun境界に1件の実欠陥が残る。別RunのTyped Approval Evidenceを、同じStep ID／Tool IDを持つRunへ移すと、そのEvidenceの`run_id`が現在Runと異なっていてもGateを通過し、Toolが実行される。加えて、新規Envelope付きRunでも`StepRecord.approved=true`だけでTyped EvidenceなしにGateを通過できる。

これは「Typed Evidenceを真の正本とし、別Runへの再利用を拒否する」というP8-CR2契約に反する。Dev Agent FoundationのImportant Gateを迂回するため、User Manualへ進む前にApproval境界だけをMicro Reworkする。

```text
Controller Disposition: MICRO_REWORK_REQUIRED
P8-CODEX-001: RESOLVED
P8-CODEX-002: PARTIAL — one approval-scope defect remains
P8-CODEX-003: RESOLVED
Open Critical: 0
Open Major / MVP Blocker: 1
Frontend Rework Required: 0
```

## 2. 成立確認

### 2.1 P8-CODEX-001

- `DevAgentRunService`にRun単位`threading.Lock`がある。
- `advance`、`submit_approval`、`cancel_run`、`record_late_result`が同じRun Lockを通る。
- 別Runを単一Global Lockで直列化していない。
- 実Thread／REST LevelのRegression Testが追加されている。

Dispositionは`RESOLVED`でよい。

### 2.2 P8-CODEX-002の成立部分

- `start_run()`がServer側でRun-scoped `AuthorizationEnvelope`を生成する。
- Envelopeは`RunSnapshot`とともにPersistされる。
- `advance()`はRun ID、Step ID、Tool ID、Resource Scope、ExpiryをTool実行直前に照合する。
- 不一致は`authority_denied`へ収束し、Toolを実行しない。
- `submit_approval()`はRun／Step／Tool／Decision／Actor Class／Timestamp／Gate Reasonを持つ`ApprovalEvidence`を作成する。
- EvidenceとEnvelopeはRestart後も復元される。
- Pre-P8-CR2 Runの読取り互換性が維持されている。

### 2.3 P8-CODEX-003

Append-only Correction／Traceability Addendumで、次へ統一されている。

```text
PASS             38
PARTIAL           1  # P8-ACC-038
USER MANUAL GATE  1  # P8-ACC-040
TOTAL             40
```

Dispositionは`RESOLVED`でよい。

## 3. 新Finding

### P8-CODEX-004 — Approval EvidenceのRun Scope不照合とCompatibility BoolによるGate迂回

```yaml
severity: major
priority: P0
classification: mvp_gate_authority_blocker
affected_acceptance:
  - P8-ACC-033
  - P8-ACC-038
origin: incomplete_resolution_of_P8-CODEX-002
```

#### 3.1 Source上の原因

`_has_approval_evidence(run, step)`は次だけを照合する。

```text
evidence.step_id == step.step_id
evidence.tool_id == step.tool_id
evidence.decision == approved
```

`evidence.run_id == run.run_id`を照合していない。Docstringは「同じRunのEvidenceしか格納されないため別Runでは成立しない」と仮定するが、`RunSnapshot` ContractにもRun ID相関Validatorがなく、永続化／復元される型付きStateとして構造保証されていない。

さらにGate条件は次のOR条件になっている。

```text
not next_step.approved
and not _has_approval_evidence(...)
```

このため、Envelope付き新規Runでも`StepRecord.approved=true`ならTyped Evidenceが0件でもGateを通過する。これは「`approved`は互換Cacheであり、真の正本はTyped Evidence」というActive Contractと一致しない。

#### 3.2 実Probe

同一Planを持つRun A／Run Bを作成し、Run Aだけを承認した後、Run Aの型付き`ApprovalEvidence`をRun Bの`approvals`へ移してRun Bを`advance()`した。

```yaml
run_a_id: different_from_run_b
transplanted_evidence_run_id: run_a_id
current_run_id: run_b_id
same_step_id: true
same_tool_id: true
run_b_result_state: running
run_b_step_state: succeeded
approval_gate_bypassed: true
tool_execution: occurred
```

既存`test_approval_evidence_and_envelope_never_cross_runs`は、通常操作でRun Aを承認してもRun BのEvidence配列が空であることだけを確認する。異なるRun IDを持つSchema-valid EvidenceがRun Bへ復元／混入した場合の拒否をTestしていないため、この欠陥を検出できない。

#### 3.3 必要な最小是正

- `_has_approval_evidence()`はRun ID、Step ID、Tool ID、Decisionを最低限すべて照合する。
- Important Gate Reasonが存在するToolでは、EvidenceのGate Reasonも現在Descriptorと一致させる。
- Envelope付きRunではTyped `ApprovalEvidence`だけをGate bypassの正本とし、`approved: bool`単独では実行しない。
- `approved: bool`互換は`envelope is None`のLegacy Runにだけ限定するか、Load時に安全なMigrationを行う。
- RunSnapshot／Run Storeの境界で、別Run IDのApproval Evidenceを拒否またはFail-closedにする。どちらを選んでもTool Execution 0であること。
- Run A EvidenceのRun B移植、Envelope付きRunのbool-only tamper、Restart後の正規承認、Legacy Run互換をRegression Testする。

## 4. Scope Stop

今回のMicro Reworkへ次を追加しない。

- P8-A〜P8-Fの再実装。
- Frontend変更またはFrontend再検証。
- Real Tool／Real MCP／Real Model／Network／Browser。
- Generic Policy Language、署名Envelope、暗号化Store、Cross-process Lock。
- `AuthorizationEnvelope.max_steps`等の新しいEnterprise Hardening。今回のBlockerはApproval Scopeに限定する。
- Phase 8 Closure、Roadmap、Git、Backup、Phase 9。

## 5. Exact Next Action

Current Claude TaskへApproval Evidence Scope Final Micro Reworkを渡す。P8-CODEX-004だけを修正し、Focused Dev Agent Test、Backend Canonical、Mypy、Ruff、1 CycleのInternal Reviewを行う。成立後、Codex Controllerが最終再Reviewし、User Manual Gateへ進める。
