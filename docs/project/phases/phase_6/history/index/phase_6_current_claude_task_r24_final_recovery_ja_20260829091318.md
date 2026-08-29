# Phase 6 Current Claude Task — Package R24 Final Recovery（Acceptance Correction／Canonical Verification／Internal Review）

```yaml
document_id: phase_6_current_claude_task_r24_final_recovery_20260829091318
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 09:13:18 JST
active_contract: phase_6_claude_current_task_r21_to_r24_exact_rework_handoff_ja_20260829062910.md
resolves: P6-CODEX-084
package: P6-RR-R24
```

## 対象Finding

P6-CODEX-084（Evidence/Claim Major、再Open）: R20の66 ID個別表自体は揃っていたが、Return記載の
「PASS 60」「合計66 ID／69行」は算術的に不成立。実内訳は`P6-RR-ACC: PASS 34/PARTIAL 1/N/A 3/
NOT RUN 2=40`、`P6-DELTA: PASS 23/PARTIAL 3=26`、合計`PASS 57/PARTIAL 4/N/A 3/NOT RUN 2=66`。
さらにP6-RR-ACC-016／017はProduction Lease未配線（P6-CODEX-086）によりPASSではなかった。

## 1. `failure_at` Backend実値Focused Test（P6-DELTA-014再判定）

`tests/integration/web/test_provider_selection_role_atomicity.py`に
`test_failure_at_is_backend_populated_and_re_readable_after_activation_failure`を追加。実
`preflight()`失敗Adapter（`_FailingPreflightFactory`／`_FailingPreflightAdapter`）を`POST
/api/v5/feature-modes/judge`（Mode-Apply-to-ON経路、`_activate_locked`の`if not ready:`分岐）
経由で発火させ、Failure Response（409、Body自体は`code`/`message`のみ）完了**後**の独立した
`GET /api/v6/provider-selection`で`failure_reason`／`failure_at`が実際に再読でき、かつ2回目の
独立GETでも同一値が安定していることを実証。`datetime.fromisoformat()`でPlaceholderでない実
ISO-8601値であることも確認。P6-DELTA-014はPARTIAL→**PASS**。

## 2. 66 ID正本再集計

`PASS + PARTIAL + N/A + NOT RUN = 66`を機械的に検証。R20個別表（`phase_6_current_claude_task_
r20_final_recovery_ja_20260829061552.md`「66 Acceptance ID 個別Disposition」）を正本Baseline
とし、以下4 IDのみDispositionまたはEvidence Pointerを更新した（他62 IDはR20記載を保持——
一括Regression 0での代替なし）。

### 更新した4 ID

| ID | R20 Disposition | R24 Disposition | 更新Evidence Pointer |
|---|---|---|---|
| P6-RR-ACC-016 | PASS（不正確な根拠） | **PASS**（根拠更新） | `test_role_lifecycle_manager.py::test_begin_role_turn_blocks_shutdown_from_unloading_until_release`; `::test_multiple_concurrent_role_turns_each_track_their_own_lease_generation`（R21新規、実Thread。Production Call Site自体は`judge_live_integration.py::_begin_judge_role_turn`/`qwen3guard_detector_adapter.py::detect()`のR21配線で実証） |
| P6-RR-ACC-017 | PASS（不正確な根拠） | **PASS**（根拠更新） | `test_begin_role_turn_pairs_adapter_and_lease_from_one_lock_acquisition`; `test_lease_released_via_finally_after_a_real_call_exception_leaves_zero_leak`（R21新規、Lock内Atomic取得＋finally Release実証） |
| P6-RR-ACC-022 | PARTIAL | **PASS** | `test_qwen3guard_manifest.py::test_real_checked_in_manifest_loads_and_is_complete_and_verified`（R23新規、実Manifest File・実Hugging Face／GitHub公式Source・Exact Revision・Source SHA-512全て検証済み） |
| P6-DELTA-014 | PARTIAL | **PASS** | 本節冒頭のFocused Test（R24新規） |

P6-RR-ACC-016／017の「不正確な根拠」とは、旧根拠が`begin_turn()`/`end_turn()`単体のUnit
Test（Production Call Site 0件）だった点——P6-GOV-023が正しく指摘した通り、Unit Test単体は
Production配線のEvidenceにならない。R21で実際にProduction Call Site（Judge Hook、Qwen3Guard
Detector Adapter）へ配線し、実Thread TestでBlocking/Release/Exception/複数並行を証明した
ことで、初めて正当なPASSとなった。

### 変更していない2 ID（P6-CODEX-087が明示的に区別を要求）

```text
P6-DELTA-004: PARTIAL のまま維持。
  Manifest／Decoder Contract自体（Identity Field: model_id/exact_revision/artifact_digest_
  sha512/contract_manifest_digest_sha512）はR23でClassification Levelまで実装・実Test済み
  だが（`test_qwen3guard_adapter.py::test_output_candidate_binding_uses_user_then_assistant_
  roles`のcontract_manifest_digest_sha512往復Assertion含む）、R20記載の元々のPARTIAL理由
  「実Provider Identity FieldがEvidenceまで往復記録されることを直接検証するTestなし」は、
  Guard専用のEvidence Recorder（Judgeの`JudgeEvidenceRecorder`に相当するもの）自体が
  現行実装に存在しないため、依然として未解消。過大にPASSへ格上げしない。

P6-DELTA-016: PARTIAL のまま維持（Handoff §3 R24-4により明示指示）。
  Phase 9予約のFrontend Layout項目（3×3 Field Layout、Sidebar Profile/Device/Acceleration）
  は本Taskでは実装しない。
```

## 3. 正本66 ID最終集計（PASS + PARTIAL + N/A + NOT RUN = 66 機械検証）

```text
P6-RR-ACC-001〜040:
  PASS    : 35（R20時点34 + ACC-022昇格1）
  PARTIAL : 0
  N/A     : 3（036, 039, 040 — Process）
  NOT RUN : 2（037, 038 — Real Artifact/Browser要）
  小計    : 40 ✓（35+0+3+2=40）

P6-DELTA-001〜026:
  PASS    : 24（R20時点23 + DELTA-014昇格1）
  PARTIAL : 2（004, 016）
  小計    : 26 ✓（24+2=26）

合計:
  PASS    : 59
  PARTIAL : 2
  N/A     : 3
  NOT RUN : 2
  合計    : 66 ✓（59+2+3+2=66、機械検証PASS）
```

個別62 ID（変更していないID）のDisposition／Evidence Pointerは
`phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md`「66 Acceptance ID
個別Disposition」記載のまま——本書はDifferentialとして4 ID分の更新のみ記載する。

## 4. 新規Test Node ID（機械算出、概算なし）

各値は`pytest --collect-only -q <file>`のNode ID実数から、本Session内でPackageごとに直接
測定した増分（推測・概算ではない）。

```text
R21:
  test_role_lifecycle_manager.py            : 13 -> 18  (+5)
  test_qwen3guard_detector_adapter.py        :  6 ->  7  (+1)
  test_judge_live_integration.py             :  変更なし (+0, パラメータ名変更のみ)
  test_judge_live_integration_dispatch_router.py: 変更なし (+0, 既存Testへの追加Assertionのみ)
  test_bootstrap_hooks.py                    :  変更なし (+0, パラメータ名変更のみ)
  R21小計                                    : +6

R22:
  test_tracked_stage_worker.py               :  5 -> 11  (+6)
  R22小計                                    : +6

R23:
  test_qwen3guard_adapter.py                 : 14 -> 21  (+7)
  test_qwen3guard_manifest.py（新規File）     :  0 -> 14  (+14)
  test_dedicated_role_adapters.py            :  変更なし (+0, パラメータ名変更のみ)
  R23小計                                    : +21

R24:
  test_provider_selection_role_atomicity.py  : 10 -> 11  (+1)
  R24小計                                    : +1

R21〜R24合計新規Test Node ID: 34（6+6+21+1、Package内訳と一致）
```

本Session内で連続測定したCanonical Full Suite件数の推移も、上記34件と完全に整合する
（R21直後1759 -> R22直後1765[+6] -> R23直後1786[+21] -> R24直後1787[+1]）。

一方、R20 Return Handoff自身が記載した「1744 passed」というBaseline値は、本Session内では
独立に再測定していない（Handoff §1の指示によりFresh Task化・全Docs再読・独立Baseline
再実行を行わずR21実装へ直接着手したため）。本Session実測の現在Canonical合計1787から本Session
自身の新規34件を差し引いた場合の逆算Baselineは1753であり、R20記載の1744との間に9件の差異が
残る。この9件の原因は本Session内では特定していない——正直にOpenとして記録する（R20自身の
Return Handoffには「新規49 tests」對「9+10+14+12=45」という別の算術不一致がP6-GOV-023で
既に指摘されており、1744という数値自体の精度も同様に不確実である可能性がある）。

## 5. Canonical Verification

```text
ruff check .                    : All checks passed（483 files）
ruff format --check .           : 483 files already formatted
mypy（pyproject.toml既定）       : Success: no issues found in 483 source files
pytest（Backend Full）           : 1787 passed, 7 deselected
frontend: npm run typecheck     : Clean（tsc --noEmit、0 errors）
frontend: npm run lint          : Clean（eslint . 、0 errors）
frontend: npm test              : 231 passed（25 test files）
frontend: npm run build         : Clean（tsc --noEmit && vite build、89ms、警告0）
```

Frontend Source Fileの変更は本R21〜R24で0件（`find frontend/src -newer <R20 Recovery
Index>`で確認）——231 passedはR20時点と同数で、Regressionが無いことの確認であり新規Frontend
実装のEvidenceではない。

## 6. Internal Review（Implementation Freeze後）

Implementation Freeze後、以下6観点で自己Reviewを実施した。

### Requirement-by-Requirement

R21〜R24 Handoff §3の各Contract項目を1行ずつ実装Sourceと突き合わせ、全項目の実装箇所を
確認した（R21: 7項目、R22: 7項目、R23: 8項目、R24: 8項目、計30項目）。未実装項目0件。

### Cross-component

R21（Role Turn Lease）とR22（Tracked Stage Worker Registry）は意図的に独立した機構である
ことを再確認——Prompt Build／DecodeはJudge Lease保持区間の内側で実行されるが、R18由来の
「CallerはBudget超過時に待たずに戻る」設計により、Timeout時はJudge Lease解放後もPrompt／
Decode Threadが単独で走り続け得る。この「Lease解放後もTracked Worker側は別途生存し得る」
非対称性はR22のRegistryが正しく個別に補足する設計であり、統合ではなく分離が正しい判断
だったことをCode Path追跡で再確認した。R21（Guard Lease）とR23（Manifest）は
`Qwen3GuardDetectorAdapter.detect()`→`turn.adapter.classify_point()`→内部で`self._manifest`
参照、という単純な直列合成であり、競合なし。

### Concurrency

R21新規5 Test、R22新規6 Testが実Thread／Eventで検証済み。追加で、`begin_role_turn()`内の
`_active_adapters.get(role)`Read と`_shutting_down`Readが同一`with self._condition:`Block内
で行われAtomicであることをSource再確認（分離していればTOCTOUが再発する）。

### Failure Injection

Judge: Prompt Build Timeout、Decode Timeout、Model Call Exception、ENFORCE Wait Timeout、
Coordinator Slot拒否（`not started`分岐、R21で新規Leak修正）の5経路全てでLease Releaseを
Source Trace上で確認。Guard: `classify_point()`のTimeoutError／Qwen3GuardDecodeError／
汎用Exceptionの3経路全てで`finally`Release確認。

### Negative Path

`role_provider_lifecycle`未配線（Feature Modes無効）、`begin_judge_role_turn`未供給
（Provider Selection概念なしDeployment）、Guard Governance無効の3構成全てで、旧Behavior
（Lease以前と同じ結果）が保たれることをSource Trace上で確認——新規Leak・新規Regressionなし。

### Claim Audit

本節自体がClaim Auditを兼ねる。過大主張の検出は0件——P6-DELTA-004を安易にPASSへ格上げ
しなかったこと、R20の1744件Baselineを検証せずそのまま転記しなかったこと（上記4節）、
P6-DELTA-016をHandoffの明示指示通りPARTIALのまま保持したことが、本Reviewでの
Self-correction Evidenceである。

### Finding Ledger（本Review発見、Rework要否判定）

```text
IR-R24-001（Observation、Rework対象外）: `RoleProviderLifecycleManager._unload_locked()`が
  Exception時（`adapter.unload()`失敗）に`_active_adapters`からのPop を行わないため、
  `_deactivate_locked`/`shutdown()`経由でUnload失敗したAdapterが、その後の`begin_role_turn()`
  呼出しに対して依然「Active」として新規Leaseを発行し得る（`active_adapter()`旧APIも同一
  Behavior、R21新規ではない既存性質）。`_transition_to_locked`の失敗Pathは既にPop実装済み
  だが、`_unload_locked`単体はPopしない非対称性が存在する。P6-CODEX-086の契約
  （「Production配線0件」の解消）はこの非対称性と無関係であり、R21〜R24のいずれのContract
  項目にも抵触しない。Rework対象とはせず、既知の未解決Observationとして正直に記録する
  （Codex Independent Reviewでの判断に委ねる）。
```

Finding 1件（Observationのみ、Rework Trigger 0件）——Cycle 2 Reviewは実施していない
（Reworkが発生しなかったため）。

## 7. Open Critical／Major／Minor／Real Model／User Gate（最終）

```text
Open Critical: 0
Open Major   : 0（P6-CODEX-086／087ともR21／R23で解消、P6-CODEX-081はR22で解消、
  P6-CODEX-084は本Packageで解消）
Open Minor   : P6-DELTA-004（Guard専用Evidence Recorder不在によるIdentity往復記録Test欠如）、
  P6-DELTA-016（Phase 9予約Frontend Layout項目、本Task対象外）、
  IR-R24-001（`_unload_locked`のException時Pop非対称性、Observation）
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
User/Authority Gate待ちとして明示的に除外し、それ以外（Production Lease配線、Tracked
Worker Shutdown、Qwen3Guard公式Contract Manifest、66 ID正本集計、Canonical Verification、
Internal Review）は本R21〜R24で完了。

Exact next action: Exact Return Handoff作成後、Codex Controller Independent Review待ちで
停止する。Phase 6 Closure、Phase 7、Git Actionのいずれも本Claudeからは着手しない。
