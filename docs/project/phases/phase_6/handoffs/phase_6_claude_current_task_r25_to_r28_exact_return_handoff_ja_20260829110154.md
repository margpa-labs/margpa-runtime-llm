# Phase 6 Claude Current Task R25〜R28 Exact Return Handoff

```yaml
provider: Claude (Sonnet 5)
role: 設計者兼実装者役
task_identity: Phase 6 Current Claude Task（R25〜R28 Differential Rework）
active_contract: phase_6_claude_current_task_r25_to_r28_exact_rework_handoff_ja_20260829101215.md
reviewed_against: phase_6_gov024_claude_r21_to_r24_controller_independent_review_ja_20260829101215.md
r28_recovery: phase_6_current_claude_task_r28_final_recovery_ja_20260829110047.md
claim: Complete Candidate with Real Provider and User Manual Gates
next_owner: Codex（プロジェクト責任者兼設計統括者役）
next_exact_action: Controller Independent Review
network_authority: prohibited（本Task全体）
```

## Disposition（P6-CODEX-088〜091）

| Finding | Disposition |
|---|---|
| P6-CODEX-088 | Fixed（R25）: `TrackedStageWorkerRegistry.submit()`を新設し、受付確認・Thread Dispatch・Registry登録を単一Lock Acquisition内でAtomicに実行。`shutdown()`は同一Lockで`_accepting`をFalseにしFuture Snapshotを取得するため、両者の臨界区間は絶対に交錯しない。`future.add_done_callback()`はLock解放後に登録し、即時完了Futureに対するSame-thread Reentrant Lock Deadlockを回避。150試行の実Thread Race Testで、Controller Probe Aの正確な悪状態（Clean Shutdown後もWorkerがActiveに残る）が一度も再現しないことを実証。 |
| P6-CODEX-089 | Fixed（R26）: `begin_role_turn()`にSelection ACTIVE状態・`active_provider`非None・Adapter Provider一致・`_pending_unload`非該当の4Checkを同一Lock内で追加。`_unload_locked()`をException時もSuccess時と同様にAdapter Referenceを常にPopするよう対称化（`_transition_to_locked`の既存Discipline踏襲）。`end_turn()`のDrain完了時State解決を`_unload_locked()`の戻り値駆動へ修正し、Unload失敗をCONFIGUREDに偽装するBugを解消。実Thread Mode-Freeze Race Test含む4件の決定論的Testで、Post-OFF/Drain中/Unload-Exception後いずれの経路でも新規Lease拒否を証明。 |
| P6-CODEX-090 | Fixed（R27）: `Qwen3GuardManifest`へPydantic `model_validator`によるExact Contract Cross-field Validationを追加。R23の実取得値から固定した`_EXPECTED_*`定数（Official Repository Identity、Provider ID、Label Schema ID、Safety/Refusal Label Set、Target別Required Fields、Target別Category Set9/8件）と、`verified_official_contract=True`時のみ厳密照合——不一致はConstruction自体を失敗させる。Controller Probe Cの正確な再現（`provider_id="wrong.provider"`等）がConstruction時ValidationErrorで拒否されることを直接Testで証明。未検証Placeholder（`verified_official_contract=False`）はCheck免除のまま維持。 |
| P6-CODEX-091 | Fixed（R27）: `ModelDetectionProvenance`（Optional Typed Provenance）を`GuardDetection`へ追加し、`Qwen3GuardDetectorAdapter.detect()`がClassificationの実Identity（model_id/Exact Revision/Artifact SHA-512/Contract Manifest Digest/Schema ID）をCLEAR/MATCH両Pathで投影するよう修正。既存Generic Detectorとの互換性は全Field Optional Defaultにより維持（Full Suite Regression 0で確認）。3 Target×5 Outcome形状＝15 Case Round-trip Testで、ResultからEvidence（GuardDetection）までIdentityが厳密一致することを証明。Adapter Construction時のManifest provider_id／model_id一致要求、`label_schema_id`のManifest投影（Hardcode廃止）も併せて実装。 |

## R25〜R28 Recovery Index（各Package1件、簡潔）

```text
R25: phase_6_current_claude_task_r25_recovery_ja_20260829103844.md
R26: phase_6_current_claude_task_r26_recovery_ja_20260829104503.md
R27: phase_6_current_claude_task_r27_recovery_ja_20260829105704.md
R28: phase_6_current_claude_task_r28_final_recovery_ja_20260829110047.md（Internal Review含む）
```

## Atomic Admission、Post-OFF Lease拒否、Unload Failure、偽Manifest拒否、Guard Evidence Identity Round-tripのTest（名前／結果）

```text
[R25 — tests/unit/bootstrap/test_tracked_stage_worker.py]
test_atomic_submit_closes_the_admission_shutdown_toctou_probe_a
  （150試行、Barrier強制競合、Probe A非再発証明） ................................ PASS

[R26 — tests/unit/runtime_model_control/test_role_lifecycle_manager.py]
test_off_inserted_between_frozen_belief_and_lease_acquisition_is_refused
  （実Thread2本、Mode Freeze直後とLease取得直前の間へOFF挿入） .................... PASS
test_begin_role_turn_refuses_a_second_lease_once_drain_has_begun
  （Drain待ち中の第二Lease拒否） .................................................. PASS
test_begin_role_turn_refuses_after_an_immediate_unload_exception
  （Unload Exception後の新規Lease拒否） ........................................... PASS
test_end_turn_drain_completion_with_unload_failure_settles_degraded_not_configured
  （CONFIGURED偽装Bugの直接再現・修正実証） ........................................ PASS

[R27 — tests/unit/adapters/guardrail_governance/test_qwen3guard_manifest.py]
test_construction_rejects_incomplete_or_wrong_exact_contract_when_claimed_verified
  （5 Case、Probe C literal reproduction含む、Construction時ValidationError拒否） .. PASS
test_unverified_manifest_with_wrong_fields_still_constructs_as_placeholder ........ PASS

[R27 — tests/unit/adapters/guardrail_governance/test_qwen3guard_detector_adapter.py]
test_model_provenance_round_trips_from_result_to_evidence
  （3 Target×5 Outcome形状＝15 Case、Identity厳密一致） ........................... PASS
test_model_provenance_is_none_when_unavailable_no_classification_exists .......... PASS
```

## 66 IDの再集計

```text
Baseline（P6-GOV-024 §6）: PASS 56 / PARTIAL 5 / N/A 3 / NOT RUN 2 = 66

再判定（R26/R27のEvidenceが成立した4 IDのみPASSへ）:
  P6-RR-ACC-016: PARTIAL -> PASS（R26 Evidence）
  P6-RR-ACC-017: PARTIAL -> PASS（R25/R26 Evidence）
  P6-RR-ACC-022: PARTIAL -> PASS（R27 Evidence）
  P6-DELTA-004  : PARTIAL -> PASS（R27 Evidence）
  P6-DELTA-016  : PARTIAL のまま維持（Handoff明示指示）

最終集計:
  PASS    : 60
  PARTIAL : 1（P6-DELTA-016のみ）
  N/A     : 3
  NOT RUN : 2
  合計    : 66（60+1+3+2=66、機械検証PASS）
```

個別62 ID（本R25〜R28で変更していないID）のDisposition／Evidence Pointerは
`phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md`の元表を正本として保持。
上記4 IDのDiffは`phase_6_current_claude_task_r28_final_recovery_ja_20260829110047.md`
「2. P6-RR-ACC-016／017／022、P6-DELTA-004の再判定」に個別Evidence Pointer付きで記載した。

## Canonical Verification結果

```text
ruff check .                : All checks passed（483 files）
ruff format --check .       : 483 files already formatted
mypy（pyproject.toml既定）   : Success: no issues found in 483 source files
pytest（Backend Full）       : 1811 passed, 7 deselected
frontend typecheck           : Clean
frontend lint                 : Clean
frontend test                : 231 passed（25 test files、R20時点と同数、Frontend Source変更0）
frontend build                : Clean（87ms、警告0）
```

## Internal Review Finding Ledger

Requirement-by-Requirement（R25〜R27全21 Contract項目、未実装0）、Cross-component
（R25/R26独立Lock間Deadlock Risk 0、R26/R27直列合成競合なし）、Concurrency（Atomic Lock範囲
再確認）、Failure Injection（R25/R26/R27計11件のFailure Injection Test新規追加）、Negative
Path（4構成でHonest Failure確認）、Claim Audit（66 ID再判定4件の個別Evidence根拠を明示、
DELTA-016/Real Model/Real BrowserをPASSへ格上げしていないことを確認）の6観点で実施。

```text
Finding 0件（Rework Trigger 0件）。
```

R20／R24で二度発生した「Evidence不十分なままPASS主張」というPatternが本Packageの4 ID
再判定で再発していないか、各々についてR25〜R27で追加した実Thread／Deterministic
Reproduction Testの存在を個別に再確認した上でのFinding 0件——単なるObservationへの格下げ
ではなく、Acceptance／Lifecycle／Evidence契約への影響を都度判定した結果である。Cycle 2
Reviewは未実施（Reworkが発生しなかったため、Handoff §3 R28-6の前提条件を満たさない）。

## Open Critical／Major／Minor／Real Model／User Gate

```text
Open Critical: 0
Open Major   : 0（P6-CODEX-088／089／090／091全てR25〜R27で解消）
Open Minor   : P6-DELTA-016（Phase 9予約Frontend Layout項目、本Task対象外）
Real Model   : Qwen3Guard／Selene実Artifact NOT RUN（`dedicated_model_authority_granted=
  False`のまま、本Taskでは変更していない）
User Gate    : P6-RR-ACC-037（Real Artifact実測）、P6-RR-ACC-038（Real Browser確認）
```

## Action Inventory（R25〜R28累積）

```text
Git Action        : 0
Network Action     : 0（本Task全体でNetwork Access禁止。R27の`_EXPECTED_*`定数は全て
  R23の既取得値をLocal定数化したもので、新規Fetch 0）
Provider Memory Action: 0
Root外Read/Write   : 0
Destructive/Irreversible Mutation: 0
```

## Incident Record

本Package群（R25〜R28）中に新規Incidentは発生していない。既存記録（P6-RR-R-INC-001、
P6-RR-R-INC-002）はそのまま保持。

## Changed Source/Test SHA-512（R25〜R28）

```text
[R25〜R28 Semantic変更 Source]
a7b93bee2215cdef55e1bb7bbba711f556b7c9e4ef6ba7493860d1e260d7ca4e07df70c361bd9dff7b5b93fc40806c5cee8e10b19a69fba57397371be8db02eb tracked_stage_worker.py
9c91aae650a278bd3968cadcc38c7b620f1a5c9507b09cf2d110b959b5629cd531fdd3e4f28b1a4b0be2037389bb795eb0f29dd70c12fa3421d13c3d8b9d97ae role_lifecycle_manager.py
dc6817e2a66e5bb0a2828ee4d5aad3f9a1c0c85d981cc2b96511e26a440865625190ca7a256a4201cfff491f9a90ac4fc080de00299edc683257055c9c696b54 qwen3guard_manifest.py
2e1f1b4c97396d5fbd1c0a7c76cec80aed883d85204fa908fd3e8f86f308a20c4677699159583d4f832271890b885b07d7eb2ee384c84ad7da535714aa105940 qwen3guard_adapter.py
46821eb3bf6fe086fc5f96f8a72825f29582e4ed8327b98deb7b3356ea1c037ac9d79de37ab8fab620d24069125f8aba32ad5490a80dbd8772d46c1697b42640 modules/guardrail_governance/domain/qwen3guard.py
dba48fd571a34a07f464b0ba9931f336bbe3eddac5384dcf5d3b775bd3f1c71ddbe943536fadf871b3ef6c2edc1a9db2ef6a95def128bbec26f5d369888120c3 modules/guardrail_governance/domain/results.py
bfd981cfada5291e3c8b4f3a2967869910aed7a7e894285db37a2ab93ccc7c0673bdedbb188a7c6a6723b7c5a4438ea5cb4de75a43578545761e2939734ec8b9 modules/guardrail_governance/domain/__init__.py
05bdf6928e32b77a3d23d8dddc2ad8c499a3205bfae9203875bf8bd4930d0c40cedba5597f50c4c769f09dafca542d1591e955fd84497acda2d5d5b218f88dfa qwen3guard_detector_adapter.py

[R25〜R28 Test変更]
a2864e06f5b020fd34eebf9d2ab499afc17f8bb78b2da8e6d969d0d182770ee7a383805235f3112a4d369b0a43aec74c25a3618c44e00ae8589a7b83347fddc3 test_tracked_stage_worker.py
1b1833497590dfbee20b8d12197dff45a36f579fad3700810a9daecae9fe40eb384a347cdda4c4b60c13c0d12633ccd3e1481245d3a55a21ef620feae43a2796 test_role_lifecycle_manager.py
d16725572f541cd1a880be5835db3bf8be34a49cc17af818713d971aefcea9b70e756790e598150b1e63dda3a40319a61b22087b03a3081a8988f186f9956887 test_qwen3guard_manifest.py
9e84caac6f505559fc01964e3f7ba38f7485f0b2872321d38366646bb92ff3e98f7e61e46e34e8a141f513a1ad56b96523d86cc0538352653b63a85debed7872 test_qwen3guard_adapter.py
fa4c9a943116ff2663a011b5095cb35969de3e2f1f79dbb71880ef8bfdbefbe06a7150307a6621c785d3f50d88c060b435d131f761db7804150fd434c46a93d9 test_qwen3guard_detector_adapter.py
```

R21〜R24分を含む完全なFile一覧は前回Return Handoff
（`phase_6_claude_current_task_r21_to_r24_exact_return_handoff_ja_20260829091444.md`）と
本Documentの合算を正本とする。Frontend Source File変更は本R25〜R28累積で0件。

## Test Node ID実数（機械算出）

```text
R25: test_tracked_stage_worker.py                              : +1
R26: test_role_lifecycle_manager.py                             : +4
R27: test_qwen3guard_manifest.py                                 : +3
R27: test_qwen3guard_detector_adapter.py                         : +16
R25〜R28合計新規Test Node ID: 24（1+4+3+16）
Canonical Full Suite: R24末1787 -> R25 1788 -> R26 1792 -> R27 1811 -> R28 1811（推移完全整合）
```

Exact next action: Codex Controller Independent Review。Phase 6 Closure、Phase 7、Git
Actionのいずれも本Claudeからは着手していない。
