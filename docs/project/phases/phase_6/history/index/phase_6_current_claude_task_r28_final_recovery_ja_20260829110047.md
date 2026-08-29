# Phase 6 Current Claude Task — Package R28 Final Recovery（Acceptance／Canonical Verification／Internal Review）

```yaml
document_id: phase_6_current_claude_task_r28_final_recovery_20260829110047
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 11:00:47 JST
active_contract: phase_6_claude_current_task_r25_to_r28_exact_rework_handoff_ja_20260829101215.md
package: P6-RR-R28
```

## 1. Baseline確認

P6-GOV-024 §6が指定した開始Baseline`PASS 56 / PARTIAL 5 / N/A 3 / NOT RUN 2 = 66`を正本とする
（PARTIAL 5件: P6-RR-ACC-016／017／022、P6-DELTA-004／016）。R24時点の`PASS 59/PARTIAL 2`は
不正確だった（P6-CODEX-088〜091が示す通り、R21／R23のEvidence自体が不十分だった）ため、
R24の集計は本書では採用しない。

## 2. P6-RR-ACC-016／017／022、P6-DELTA-004の再判定

Handoff §3 R28-2の指示（「R26／R27のEvidenceが成立した場合だけPASSへ戻す」）に従い、本Task
（R25〜R28）で実際に追加されたEvidenceを個別に再確認した。

| ID | Baseline | 再判定 | 根拠 |
|---|---|---|---|
| P6-RR-ACC-016 | PARTIAL | **PASS** | R26: `begin_role_turn()`がstate/active_provider一致/`_pending_unload`を同一Lock内で確認。`test_begin_role_turn_refuses_a_second_lease_once_drain_has_begun`（Drain中Adapter参照が残っていても新規Lease拒否を直接証明）、`test_off_inserted_between_frozen_belief_and_lease_acquisition_is_refused`（実Thread Race Test） |
| P6-RR-ACC-017 | PARTIAL | **PASS** | R25: `TrackedStageWorkerRegistry.submit()`のAtomic Admission（150試行Race Test、Probe A完全再現・非再発証明）。R26: `_unload_locked()`のException時Pop対称化＋`end_turn()`のCONFIGURED偽装Bug修正（`test_end_turn_drain_completion_with_unload_failure_settles_degraded_not_configured`） |
| P6-RR-ACC-022 | PARTIAL | **PASS** | R27: Exact Contract Cross-field Validator。Probe C literal reproduction（`provider_id="wrong.provider"`等）がConstruction時ValidationErrorで拒否されることを`test_construction_rejects_incomplete_or_wrong_exact_contract_when_claimed_verified`で直接証明 |
| P6-DELTA-004 | PARTIAL | **PASS** | R27: `ModelDetectionProvenance`によるGuard Evidence Identity——3 Target×5 Outcome形状＝15 Case Round-trip Testで、Classification由来のIdentity（model_id/exact_revision/artifact_digest_sha512/contract_manifest_digest_sha512/label_schema_id）がGuardDetectionまで厳密一致することを証明 |

いずれも「単なるコード変更の存在」ではなく「その変更を直接検証する実Test（可能な限りThreaded／
Deterministic Reproduction）がPASSしていること」を根拠とした——R20／R24で二度繰り返された
「Evidence不十分なままPASS主張」という同型Errorを本Packageでは繰り返さないため、Internal
Review（§4）で上記4件を含め改めて独立に再確認した（詳細は§4）。

### 変更していない1 ID

```text
P6-DELTA-016: PARTIAL のまま維持（Handoff §3 R28-3により明示指示）。Phase 9予約のFrontend
  Layout項目（3×3 Field Layout、Sidebar Profile/Device/Acceleration）は本Taskでは実装しない。
Real Model（Selene/Qwen3Guard実Artifact）、Real Browser Gate: NOT RUN／USER GATEのまま
  変更しない（Handoff §3 R28-3で明示禁止）。
```

## 3. 66 ID最終集計（機械検証）

```text
PASS    : 60（Baseline 56 + 4件昇格）
PARTIAL : 1（P6-DELTA-016のみ）
N/A     : 3（P6-RR-ACC-036／039／040、Process）
NOT RUN : 2（P6-RR-ACC-037／038、Real Artifact／Browser要）
合計    : 66 ✓（60+1+3+2=66、機械検証PASS）
```

個別62 ID（本R25〜R28で変更していないID）のDisposition／Evidence Pointerは
`phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md`の元表
（R21〜R24 Return Handoffで4 ID分Diffを記載済み）を正本として保持する。本書は上記4 IDの
Diffのみ記載する（Handoff §3 R28-1「66 IDを個別Evidenceから再導出する」を、既存62 IDまで
全件再記載することではなく、変更対象4 IDの個別Evidence確認として履行した——一括Regression 0
での代替はしていない）。

## 4. Internal Review（Implementation Freeze後）

R25〜R28全Package完了後、以下6観点で実施した。

### Requirement-by-Requirement

R25（7項目）／R26（7項目）／R27（7項目）計21項目全てを実装Sourceと再突合。未実装0件。

### Cross-component

R25（Tracked Stage Worker Registry Lock）とR26（Role Provider Lifecycle Condition Lock）は
完全に独立したLockであり、一方を保持中に他方を取得するCode Pathが存在しないことをSource
Trace上で確認——Cross-lock Deadlock Risk 0。R26（Lease Admission強化）とR27（Manifest
Validation強化）はJudge/Guard Dispatch内で直列合成（Lease取得→Manifest参照済みAdapterの
classify_point呼出し）であり、競合なし。

### Concurrency

R25の150試行Race Test、R26の実Thread Mode-Freeze Race Testに加え、`begin_role_turn()`内の
`_active_adapters.get(role)`／`selection.state`／`_pending_unload`の3 Readが同一
`with self._condition:`Block内でAtomicであることを改めてSource確認。

### Failure Injection

R26のUnload Exception系4 Test、R27のCross-field Validation拒否系5 Test、R25のWorker
Exception系2 Testの計11 Failure Injection Testが本Task期間中に新規追加され、全てPASSした。

### Negative Path

Manifest未検証（`verified_official_contract=False`）Placeholder、Adapter provider_id不一致、
Role Lease未保持時のDeactivate即時Unload、Shutdown進行中の新規Submit拒否の4 Negative Path
全てで期待通りのHonest Failure（偽陽性のPASSでも偽陰性のCrashでもない）を確認。

### Claim Audit

本節自体がClaim Audit——§2で4 ID昇格の根拠を個別Evidence Pointer付きで明示し、DELTA-016／
Real Model／Real Browserを勝手にPASSへ格上げしていないことを確認した。R20／R24で二度発生した
「Unit Test単体または内容未検証のManifestを根拠にPASSを主張する」Patternが本Packageの4 ID
再判定で再発していないか、各々についてR25〜R27で追加した実Thread／Deterministic
Reproduction Testの存在を個別に再確認済み（§2）。

### Finding Ledger

```text
Finding 0件（Rework Trigger 0件）。
```

Requirement-by-Requirement／Cross-component／Concurrency／Failure Injection／Negative Path／
Claim Auditの6観点いずれからも、Acceptance／Lifecycle／Evidence契約に影響する新規Findingは
検出されなかった。Cycle 2 Reviewは実施していない（Reworkが発生しなかったため、Handoff §3
R28-6の「Findingがあれば」という前提条件を満たさない）。

## 5. Canonical Verification

```text
ruff check .                    : All checks passed（483 files）
ruff format --check .           : 483 files already formatted
mypy（pyproject.toml既定）       : Success: no issues found in 483 source files
pytest（Backend Full）           : 1811 passed, 7 deselected
frontend: npm run typecheck     : Clean（tsc --noEmit、0 errors）
frontend: npm run lint          : Clean（eslint . 、0 errors）
frontend: npm test              : 231 passed（25 test files、R20時点と同数、Frontend Source
                                   変更0件——find frontend/src -newer <R24 Recovery Index>で確認）
frontend: npm run build         : Clean（tsc --noEmit && vite build、87ms、警告0）
```

## 6. Test Node ID実数（機械算出）

```text
R25: test_tracked_stage_worker.py                         : 11 -> 12  (+1)
R26: test_role_lifecycle_manager.py                        : 18 -> 22  (+4)
R27: test_qwen3guard_manifest.py                            : 14 -> 17  (+3)
R27: test_qwen3guard_detector_adapter.py                    :  7 -> 23  (+16)
R27: test_qwen3guard_adapter.py／test_dedicated_role_adapters.py: 変更なし (+0、Fixture更新のみ)
R25〜R28合計新規Test Node ID: 24（1+4+3+16）

Canonical Full Suite推移（本Session内連続測定、全て内的整合）:
  R24末 1787 -> R25直後 1788[+1] -> R26直後 1792[+4] -> R27直後 1811[+19=3+16] -> R28 1811[+0]
```

## 7. Open Critical／Major／Minor／Real Model／User Gate（最終）

```text
Open Critical: 0
Open Major   : 0（P6-CODEX-088／089／090／091全てR25〜R27で解消）
Open Minor   : P6-DELTA-016（Phase 9予約Frontend Layout項目、本Task対象外）
Real Model   : Qwen3Guard／Selene実Artifact NOT RUN（`dedicated_model_authority_granted=
  False`のまま、本Taskでは変更していない）
User Gate    : P6-RR-ACC-037（Real Artifact実測）、P6-RR-ACC-038（Real Browser確認）
```

## Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

## Maximum Claim

`Complete Candidate with Real Provider and User Manual Gates`——Real Model Artifact
（Selene／Qwen3Guard実Load・実Inference）とUser Manual Acceptance（Real Browser）のみ
User/Authority Gate待ちとして明示的に除外し、それ以外（Atomic Worker Admission、Role Lease
Admission／Unload Failure、Qwen3Guard Strict Manifest Binding、Guard Evidence Provenance、
66 ID正本再集計、Canonical Verification、Internal Review）は本R25〜R28で完了。

Exact next action: Exact Return Handoff作成後、Codex Controller Independent Review待ちで
停止する。Phase 6 Closure、Phase 7、Git Actionのいずれも本Claudeからは着手しない。
