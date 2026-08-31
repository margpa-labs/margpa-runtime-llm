# Phase 8 Claude Post-Controller First Review — Traceability Addendum

```yaml
document_type: traceability_addendum
phase: phase_8
package: P8-CR (P8-CR0-CR4)
provider: Claude
created_at: 2026-08-31 00:08 JST
supersedes_acceptance_summary_of:
  - phase_8_claude_p8_f_complete_package_recovery_ja_20260830233316.md
  - phase_8_claude_p8_f_requirement_acceptance_source_test_traceability_ja_20260830233316.md
```

正本は`phase_8_requirements_ja.md`・`phase_8_acceptance_matrix_ja.md`。P8-F時点のTraceability Matrix（40件）は改変せず、本Addendumは Controller Finding（P8-CODEX-001〜003）で影響を受けたID群のDispositionのみを差分として記録する。

## P8-CODEX-001 — Concurrent advanceによる同一Tool二重実行

```yaml
disposition: RESOLVED
```

### 是正内容

`DevAgentRunService`へRun単位の`threading.Lock`を導入（`_lock_for()`）。`advance`／`submit_approval`／`cancel_run`／`record_late_result`の4Public Methodすべてを、対応する`_xxx_locked()`実装へLock越しに委譲する形へ変更。同一Run宛のLockのみが直列化され、別Run同士は互いをBlockしない（Global Serial化を避ける設計）。Cross-process／Distributed Lockは実装していない（単一Local Process内Guaranteeのみ、Non-goal通り）。

### 影響Acceptance ID

| ID | 内容 | Disposition |
|---|---|---|
| P8-ACC-028 | Run／Step／State／Tool Request／Result／Dispositionを追跡できる | PASS（Lock化後もTracked State Modelは不変。追加でConcurrent時のExactly-once実行がEvidenceとして強化された） |
| P8-ACC-033 | Important-gate-onlyはFrozen Envelope内だけ逐次確認なしで進む | PASS（Gate判定Logic自体は不変。Envelope照合はP8-CODEX-002参照） |
| P8-ACC-036 | Max Step／Deadline／Retry／Budget／Loop防止が作用する | PASS（Concurrent環境下でもMax Step集計・Deadline判定が単一のLocked Read-Modify-Writeの中で行われるため、二重Countや二重Executionによる実質的なLimit破りが発生しないことをTestで確認） |
| P8-ACC-037 | Stop／Cancel後のLate ResultがCurrentへ追加されない | PASS（`record_late_result`もLock化。advance対cancelの代表RaceでLate Publishが起きないことをTestで確認） |

### Required Testの充足Evidence

```text
tests/unit/dev_agent/test_run_service_concurrency.py
  test_concurrent_advance_executes_tool_exactly_once
    -> 実Thread 2本 + Blocking/Counting Fake Toolで同時advanceを再現。
       port.calls == 1 をAssert（Lock除去下での再現実験で2に増えることを
       個別に確認済み — 本Testが実在のRegression Guardであることの検証）。
  test_concurrent_advance_vs_cancel_is_deterministic
    -> advance対cancelの代表Race。最終Stateが常にcancelled、Tool実行が
       常に1回であることをAssert。
  test_concurrent_approval_vs_cancel_is_deterministic
    -> Approval対Cancelの代表Race。最終Stateが常にcancelledであり、負けた
       側は例外なくInvalidRunTransitionErrorへ収束することをAssert
       （torn/虚偽Stateが発生しないことの実証）。

tests/integration/dev_agent/test_dev_agent_web_app.py
  test_concurrent_advance_via_rest_executes_tool_exactly_once
    -> Production Routeと同一のasyncio.to_thread()経路を通した状態で、
       実際に2つのHTTP POST .../advanceをasyncio.gatherで同時発行し、
       port.calls == 1 をAssert（「REST／asyncio.to_thread経路でも同じ
       Atomic Boundaryを通ることを示す」要件をFocused Testとして充足）。
```

## P8-CODEX-002 — Frozen AuthorizationEnvelopeの実配線

```yaml
disposition: RESOLVED
```

### 是正内容

- `contracts.py`：`AuthorizationEnvelope`をSingle-Step-Scope（`run_id`/`step_id`/`tool_id`/`decided_at`のみ）からRun-Scope（`run_id`/`allowed_step_ids`/`allowed_tool_ids`/`resource_scope`/`max_steps`/`max_attempts`/`expires_at`/`gate_reasons`/`issued_at`）へ全面差し替え。Architecture§3の`AuthorizationEnvelope`定義（Allowed Scope／Actions／Resource／Expiry／Gate Conditions）に整合。
- `contracts.py`：新規`ApprovalEvidence`（`run_id`/`step_id`/`tool_id`/`decision`/`actor_class`/`decided_at`/`gate_reason`）を追加。`RunSnapshot`へ`envelope: AuthorizationEnvelope | None = None`・`approvals: tuple[ApprovalEvidence, ...] = ()`を追加（共にDefault値によりPre-P8-CR2 Run Store FileはCorrupt扱いにならない）。
- `run_service.py`：`start_run()`が`_issue_envelope()`でPlan／Profile／Limitから実際にEnvelopeを構築し、Run Snapshotへ永続化。CallerはRequest Bodyに対応Fieldを持たないため、Envelopeを自由入力できない。
- `run_service.py`：`advance()`がStep実行直前に`_envelope_violation()`でRun Identity／Allowed Step／Allowed Tool／Resource Scope／Expiryを照合。不一致は`RunCompletionOutcome`新値`"authority_denied"`（Architecture§7が既に列挙していたFailure語彙）へ収束し、Tool Portは一切呼ばれない。
- `run_service.py`：`submit_approval()`が`APPROVED`／`DENIED`いずれの決定でも`ApprovalEvidence`をRunへ追記。Gate判定（`advance()`内）は`StepRecord.approved`（Compatibility Cache）と`_has_approval_evidence()`（Typed Evidence、真の正本）のORで行い、両方が同じ`(run_id, step_id, tool_id)`にしか一致し得ないため、別Run／別Step／別ToolへのApproval再利用は構造的に不可能。
- `web/dev_agent_contracts.py`：`DevAgentRunResponse`へ`envelope`／`approvals`をProjectionし、REST越しにEvidenceが実在することを確認可能にした。

### 影響Acceptance ID

| ID | 内容 | Disposition |
|---|---|---|
| P8-ACC-033 | Important-gate-onlyはFrozen Envelope内だけ逐次確認なしで進む | PASS（Gate判定に加え、Envelope自体がRun開始時に実際に発行・永続化されるようになった） |
| P8-ACC-038 | Run／Step／Tool／Approval／Constitution／GDをID相関して永続化する | PARTIAL継続（Constitution相関・Approval Evidence相関は共にPASS。GD相関のみ引き続き未実装 — 理由はP8-F時点から不変：Fake ToolはModel出力を生成せずGuardrailの評価対象が構造的に存在しない） |

### Required Testの充足Evidence

```text
tests/unit/dev_agent/test_run_service.py
  test_start_run_issues_a_frozen_envelope_matching_the_plan
  test_step_outside_the_envelope_is_authority_denied_with_zero_executions
    -> Envelope不一致 -> authority_denied / Tool実行0件をAssert。
  test_a_run_persisted_before_p8_cr2_has_no_envelope_and_is_not_corrupt
  test_approval_evidence_is_recorded_and_scoped_to_its_own_step_and_tool
  test_denied_approval_is_also_recorded_as_typed_evidence
  test_approval_evidence_for_one_step_never_authorizes_a_different_step
    -> 同一Tool・別StepへのEvidence再利用不可を実証。
  test_approval_evidence_persists_and_survives_restart

tests/unit/dev_agent/test_json_file_run_store.py
  test_envelope_and_approval_evidence_round_trip_through_the_file
  test_a_pre_p8_cr2_run_file_without_envelope_or_approvals_is_not_corrupt

tests/integration/dev_agent/test_dev_agent_web_app.py
  test_start_run_issues_an_authorization_envelope_via_rest
  test_approval_evidence_is_returned_via_rest_and_survives_restart
  test_a_legacy_run_without_an_envelope_is_still_advanceable_via_rest
```

## P8-CODEX-003 — Acceptance集計とUser Manual Gateの誤分類

```yaml
disposition: RESOLVED
```

`phase_8_claude_post_controller_first_review_correction_addendum_ja_20260831000825.md`の訂正2・訂正3を参照。統一後のCandidate集計：

```text
PASS             38
PARTIAL           1  # P8-ACC-038
USER MANUAL GATE  1  # P8-ACC-040
TOTAL             40
```

Real MCP／Real Modelは上記40件の内訳に含まれない、Scope外／NOT RUN Boundary（Authority不足によりFixture PASSとも実接続PASSとも異なる、試行自体が行われていない状態）として別記する。

## Rework全体を通じたAcceptance集計（本Package完了時点）

P8-A〜P8-F時点の39件のDispositionは`phase_8_claude_p8_f_requirement_acceptance_source_test_traceability_ja_20260830233316.md`のまま変更しない（本Addendumは差分のみを記録する方針のため）。上記3件のFinding是正を織り込んだ最終集計は次のとおり。

```text
PASS             38  (P8-ACC-001〜037, 039のうちP8-ACC-038を除く全件、
                       ならびにP8-ACC-040を除く全件)
PARTIAL           1  (P8-ACC-038: GD相関のみ未実装、正直な開示を継続)
USER MANUAL GATE  1  (P8-ACC-040: User実画面確認待ち。Claude Browser実演は
                       Automated Candidate Evidenceであり代替不可)
TOTAL             40
```
