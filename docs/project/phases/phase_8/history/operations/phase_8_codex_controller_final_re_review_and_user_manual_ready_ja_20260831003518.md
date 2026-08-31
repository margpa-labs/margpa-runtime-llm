# Phase 8 Codex Controller最終再Review／User Manual Ready

```yaml
document_id: phase_8_codex_controller_final_re_review_and_user_manual_ready_20260831003518
document_type: controller_final_re_review
document_state: final
language: ja
created_at: 2026-08-31 00:35:18 JST
provider: Codex
role: プロジェクト責任者兼設計統括者役
review_target: phase_8_claude_approval_evidence_scope_final_micro_rework_exact_return_handoff_ja_20260831003203.md
review_scope: P8-CODEX-004_only_plus_preserved_findings
controller_disposition: USER_MANUAL_READY
phase_8_closure: not_claimed
```

## 1. 結論

P8-CODEX-004は成立した。第1回ReviewからのP8-CODEX-001〜004にOpen Critical／Major／MVP Blockerは残っていない。P8-A〜P8-FはUser Manual Candidateとして扱える。

```text
P8-CODEX-001: RESOLVED
P8-CODEX-002: RESOLVED
P8-CODEX-003: RESOLVED
P8-CODEX-004: RESOLVED
Open Critical: 0
Open Major / MVP Blocker: 0
Controller Disposition: USER_MANUAL_READY
```

Phase 8 Closureはまだ主張しない。P8-ACC-040のUser実画面確認後に、User結果をEvidence化して最小Closureへ進む。

## 2. Review対象

```text
Exact Return:
docs/project/phases/phase_8/handoffs/phase_8_claude_approval_evidence_scope_final_micro_rework_exact_return_handoff_ja_20260831003203.md
SHA-512: ecc681f59a5893232125217e061987c978f6c5562ffa4a00d9250bf21323e2111dc7a1e928b8fe77a2dc013ab3036c5b8c46d7b2c501a05fa196b082d7549121

Recovery:
docs/project/phases/phase_8/history/index/phase_8_claude_approval_evidence_scope_final_micro_rework_complete_package_recovery_ja_20260831003203.md
SHA-512: 6d7927ef8f84c8823ce8b5693a3be2f12dc1d2f36357fce15d66fbc2b72dbdcf877c4ebe6b8dcd46ff2ad9595bc6c1cb595fbdd55d20cefd75b4ae880894e588
```

Source直接確認：

- `src/margpa_runtime_llm/modules/dev_agent/application/run_service.py`
- `src/margpa_runtime_llm/modules/dev_agent/contracts.py`
- `tests/unit/dev_agent/test_run_service.py`
- `tests/unit/dev_agent/test_json_file_run_store.py`
- `tests/integration/dev_agent/test_dev_agent_web_app.py`

## 3. P8-CODEX-004成立確認

### 3.1 Runtime Gate

`_has_approval_evidence()`は次をすべて照合する。

```text
evidence.run_id == run.run_id
evidence.step_id == step.step_id
evidence.tool_id == step.tool_id
evidence.decision == APPROVED
evidence.gate_reason == current Tool Descriptor gate reason
```

Run AのEvidenceをRun Bへ移してもRun BのApprovalとして成立しない。

### 3.2 Typed EvidenceとLegacy Boolの分離

- `run.envelope is not None`：Typed Approval EvidenceだけがGateを満たす。
- `run.envelope is None`：Pre-P8-CR2 Legacy Runに限り`StepRecord.approved`をCompatibility Fallbackとして使う。

Envelope付きRunの`approved=true`単独Gate bypassは閉じられ、Legacy Run互換は維持されている。

### 3.3 Contract／Persistence Boundary

`RunSnapshot`のValidatorが、親Runと異なる`ApprovalEvidence.run_id`を拒否する。JSON Run Storeで該当FileはCorruptとしてSkipされ、他の正常Runは回収される。`model_copy()`等でValidatorを迂回したIn-memory StateもRuntime GateのRun ID照合で拒否される。

## 4. Codex Focused Verification

Codex Controller側で次を再実行した。

```text
.venv/bin/pytest -q \
  tests/unit/dev_agent/test_run_service.py \
  tests/unit/dev_agent/test_json_file_run_store.py \
  tests/integration/dev_agent/test_dev_agent_web_app.py

65 passed in 1.59s
```

確認対象：

- Run A EvidenceからRun Bへの再利用拒否。
- Envelope付きBool-only bypass拒否。
- Gate Reason drift拒否。
- Persistence BoundaryでのForeign Evidence拒否。
- 正規Approval／Restart復元。
- Legacy Run互換。
- 既存Run／Step／Tool／REST Regression。

ClaudeのBackend Canonical `2090 passed, 7 deselected`、Mypy、Ruff PASS Evidenceと矛盾しない。Frontend SourceはP8-CR5で変更されておらず、Frontend再実行を要求しない。

## 5. Acceptance状態

```text
PASS             38
PARTIAL           1  # P8-ACC-038: GD相関はProvisional Boundary
USER MANUAL GATE  1  # P8-ACC-040
TOTAL             40
```

P8-ACC-038はPhase 8の正直なFoundation BoundaryでありClosure Blockerへ昇格させない。P8-ACC-040だけが残る。

## 6. User Manual Gate

既存のUser Manual Test Sheetを使う。

```text
docs/project/phases/phase_8/history/index/phase_8_claude_p8_f_user_manual_test_sheet_ja_20260830233316.md
```

最低限、実画面で次を確認する。

1. Manual URL Fetch：ON時のUntrusted Evidence、OFF時無実行、危険Port拒否。
2. Archive管理：一覧、開く、解除、解除後の手動Resume不要。
3. Branch選択UIが既定非表示。
4. Provisional Runtime Constitution：Revision／Digest／Rule数、chat／agent／toolがOFF。
5. Chat／Dev Agent切替。
6. Demo Run：list／read成功、writeでApproval Gate、承認後Completed。
7. 別Run：Cancel後Cancelledへ収束。
8. Chatへ戻した後、通常Chatが維持される。
9. 完全削除／一括Delete／Export等の未実装機能を虚偽表示していない。

## 7. Exact Next Action

UserがP8-ACC-040を実画面確認し、各項目を`確認できた／不具合再現／未実施`と実表示文言で返す。Codex Controllerが結果をEvidence化し、Closure Blockerだけを判定する。軽微FindingはStable未解決Registryへ送り、最小Closure、Roadmap更新、Clean／Commit／Push、Phase 9 Readyへ進む。
