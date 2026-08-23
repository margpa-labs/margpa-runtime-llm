# Phase 3 Claude Rework Complete Candidate Handoff

```yaml
document_id: phase_3_claude_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_001_rework
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_claude_rework_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 23:10:00 JST
predecessor: docs/project/phases/phase_3/history/index/phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md
required_reading:
  - docs/project/phases/phase_3/handoffs/phase_3_codex_independent_review_rework_handoff_ja.md
  - docs/project/phases/phase_3/history/index/phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md
  - docs/project/phases/phase_3/handoffs/phase_3_claude_complete_candidate_handoff_ja.md（旧Handoff。§5訂正済み記述は無効化される）
```

本Handoffは旧`phase_3_claude_complete_candidate_handoff_ja.md`を上書きしない。矛盾する旧記述は`phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md`で明示訂正済みであり、本Handoffの内容が正である。

## 0. Recommendation

**GO**（Codex Independent Reviewの再確認、およびPhase 3-H継続へ進めることを推奨する）。

P3-CODEX-001〜005・P3-GOV-001の全6件をCLOSEした。実装はFocused／Regression／Static／Full Testで検証済み、Existing Testの削除・弱体化は0件（既存Testはすべて新設計へ適合するよう更新し、Assertion数を減らしていない）。P3-GOV-001で指摘されたFalse Completion Claimは`phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md`で明示訂正済みである。

本Rework自体もRequired Findingと無関係なRefactorを行っていないが、P3-CODEX-001（Mode Mutation統合）の実装規模がPhase 3-F本体に匹敵する大きさになった点はCodexに確認してほしい——Frozen Contractの要求どおりに実装したが、Configuration Controlという既存の大きいStateMachineへ新しいDomain（Governance）を統合する変更であり、影響範囲がConfiguration Control全体に及ぶ。

## 1. P3-CODEX-001〜005、P3-GOV-001 個別CLOSE根拠

### P3-CODEX-001 — Mode MutationをConfiguration Controlへ統合：CLOSED

- `GovernanceControlMode`（`off`／`observe`のみ——`enforce`はSchema Levelで表現不可能）、`GovernanceHookDescriptor`を`modules/configuration_control/contracts.py`へ追加。
- `ConfigurationPatch.governance_mode`、`EffectiveConfigurationSnapshot.governance_hooks`を追加し、`configuration_digest()`へ算入（CAS Digestが正しくGovernance State変化を検知する）。
- `GovernanceModeApplierPort`（`modules/configuration_control/ports.py`）を新設——Configuration ControlはGovernance Definitionsの具象型に依存しない。
- `ConfigurationControlService.apply()`を拡張：`governance_mode`変更はApplierを**先に**呼び、成功後にのみ`_fields`／`_governance_hooks`／`_revision`を一括Commitする（片側Mutation禁止）。
- `bootstrap/configuration_control.py`に`_GovernanceModeApplierAdapter`（実`GovernanceDefinitionsRuntime.apply_mode()`への薄いBridge）を追加。
- `web/governance_routes.py`から`POST /mode`を削除——`/api/v3/governance/*`はRead-only Status Surfaceのみ。
- `web/configuration_contracts.py`（Patch Request／Effective Response）、`bootstrap/web_application.py`、`entrypoints/web/main.py`（`governance_definitions_runtime`を`runtime_factory`構築前に配線）を対応する形で更新。
- Frontend：`App.tsx`の`handleGovernanceApply`を`api.applyConfigurationPatch`（Configuration Controlの共有Revision／Digest CAS）経由へ変更。専用`applyGovernanceMode`／`POST /api/v3/governance/mode`は削除。`GovernancePanel.tsx`自体はProp Contract不変のため無変更。

### P3-CODEX-002 — OFF時Governance Hook Call 0：CLOSED

- `GenerationObserverPort`へ`is_active()`を追加——Mode Gateを「呼出前のBind判定」1箇所へ一本化。
- `EvidenceGenerationObserver.observe_generation_started／observe_generation_terminal`から、Per-call Mode再確認を削除——一度Bindされたら、途中でModeが変わってもStart／Terminalの対を完結させる（片側Evidence化を防止）。
- `web/app.py`（v1 `chat_stream`）／`web/persistent_routes.py`（v2 `_stream_response`）を変更：Generation開始時点で`observer.is_active()`を確認し、Falseなら`GenerationObservationTracker`自体を生成しない（`None`を渡す）——OFF中はTracker／Observer Call自体が0件。
- `EvidenceGenerationObserver`の`store`引数を`store_factory`（Lazy resolve、初回Write時のみ呼び出し）へ変更——Default OFF Bootでは`runtime_data/audit_evidence/`のDirectory自体を作らない。
- Spy Test追加：v1／v2それぞれで`is_active() -> False`のObserverを使い、実際に生成が成功してもStart／Terminal Callが0件であることを確認。

### P3-CODEX-003 — Mode Apply FailureのAtomicity／Safe Failure：CLOSED

- `GovernanceDefinitionsRuntime.apply_mode()`を再構成：OBSERVE候補Summaryを`_mode`／`_revision`変更**前**に構築し、成功後だけAtomic Commitする。
- 新規`GovernanceObservePipelineError`（Typed Safe Failure）——Provider／Adapter／Reader／Compiler例外を捕捉し、Raw Exceptionを外へ漏らさない。
- Fault Injection Test（Provider即時失敗、初回成功→2回目失敗のFlaky Provider）、Concurrent Apply Test（4 Thread同時Apply、Lock直列化とDigest整合を確認）を追加。

### P3-CODEX-004 — Definition ProviderのResource／Path Fail-closed：CLOSED

- 新規`domain/limits.py`：Manifest／Source Byte、Source／Definition件数、Path Depth、Collection／String長、IR Section／Compiled Plan Item数の有限上限を定義。
- `FilesystemDefinitionProvider._safe_resolve()`を再実装：`resolve()`によるSymlink事後判定をやめ、RootからTargetまでの各Path Componentを`lstat`で検査し、Root内外を問わずSymlink経由を拒否。
- `verify_sources()`：`Path(entry.relative_path).relative_to("definitions")`の`ValueError`を捕捉し`SourceState.INVALID／path_prefix_mismatch`へ正規化。Source Size Gateを`stat()`後・`read_bytes()`前に追加。
- `_load_signed_manifest()`：Manifest Size Gateを追加、超過を`_ManifestTooLarge`→`manifest_too_large`Reason Codeへ正規化。
- Manifest／IR／Plan各Contractへ`max_length`制約を追加（`SourceEntry.relative_path`のPath Depth Validatorも含む）。
- Boundary Test（limit／limit+1）、Symlink Component Test、Prefix Mismatch Test、Size Gate Testを追加。

### P3-CODEX-005 — JSONL Appendの完全Write：CLOSED

- `LocalJsonlEvidenceStore.append()`に`_write_all()`（Short Write時はLoop継続、0-byte WriteはOSErrorとして扱う）を追加し、`os.write()`の戻り値を必ず確認する。
- `MAX_EVENTS_PER_SEGMENT`／`MAX_SEGMENT_COUNT`を追加し、Segment上限超過を`CAPACITY_EXCEEDED`Errorへ正規化（新規Error Code）。
- Fault Injection Test（0-byte Write、Short Write→正常完了、途中OSError→Valid Prefix非改変）、Segment Rollover／Capacity Boundary Testを追加。

### P3-GOV-001 — Automation／Compaction Evidence訂正：CLOSED

- `.claude/launch.json`（Exact Target）と、空になった`.claude/`を削除。他Pathは非接触。
- `runtime_data/`へのAction：本Rework中0件（Read／List／Stat／Write／Delete、すべて未実施）。
- `claude_long_running_auto_compaction_hash_tracker_ja.md`を訂正：成功0／失敗0 → 成功0／失敗1。Cycle 1をFailureとして追記（Hash未取得の事実をそのまま記録、捏造せず）。
- 新規Append-only Correction Evidence：`phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md`（Technical／Root Boundary／Provider-local Artifact／runtime_data Violation／False Completion訂正／Human Intervention／Execution Continuity／Recovery Docs Reread=UNVERIFIED／Language Fidelity=DRIFTを分離記録）。
- 旧Complete Candidate Handoffは上書きしていない（Append-onlyで訂正）。
- 本Handoff以降、日本語で報告する。

## 2. Exact Mutation（本Rework Session、集約）

### 2.1 新規Created

```text
src/margpa_runtime_llm/modules/governance_definitions/domain/limits.py
docs/project/phases/phase_3/history/index/phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md
docs/project/phases/phase_3/handoffs/phase_3_claude_rework_complete_candidate_handoff_ja.md（本File）
```

### 2.2 Modified（主要File）

```text
Backend:
  src/margpa_runtime_llm/modules/configuration_control/{contracts.py,ports.py,application.py,__init__.py}
  src/margpa_runtime_llm/bootstrap/{configuration_control.py,web_application.py}
  src/margpa_runtime_llm/entrypoints/web/main.py
  src/margpa_runtime_llm/web/{governance_routes.py,configuration_contracts.py,app.py,persistent_routes.py,streaming.py,persistent_streaming.py}
  src/margpa_runtime_llm/modules/governance_definitions/runtime.py（GovernanceObservePipelineError、Atomic Commit）
  src/margpa_runtime_llm/modules/governance_definitions/domain/{manifest.py,normalized_ir.py,compiler.py}（Limits適用）
  src/margpa_runtime_llm/adapters/governance_definitions/filesystem_provider.py（Symlink／Prefix／Size Gate）
  src/margpa_runtime_llm/modules/audit_evidence/{generation_observation.py,domain/errors.py}
  src/margpa_runtime_llm/adapters/audit_evidence/{evidence_generation_observer.py,local_jsonl_store.py}
  src/margpa_runtime_llm/bootstrap/audit_evidence.py（store_factory Lazy化）

Frontend:
  frontend/src/App.tsx（handleGovernanceApply → Configuration Control経由）
  frontend/src/api/client.ts（applyGovernanceMode削除）
  frontend/src/i18n/translations.ts（非永続明示）
  src/margpa_runtime_llm/web/static/{app.js,app.css,index.html}（npm run build再生成）

Tests（主要File、新規Test多数追加・既存Test更新）:
  tests/unit/configuration_control/test_configuration_control_service.py
  tests/unit/governance_definitions/{test_runtime.py,test_filesystem_provider.py,test_manifest_contract.py}
  tests/unit/governance_definitions/test_ir_and_plan_limits.py（新規File）
  tests/unit/audit_evidence/{test_evidence_generation_observer.py,test_local_jsonl_store_append_recovery.py}
  tests/integration/web/{test_governance_definitions_web_app.py,test_governance_local_ux_recovery.py,test_web_app.py,test_persistent_web_app.py}
  tests/unit/web/test_web_cli.py

Docs（既存File、契約どおりの訂正のみ）:
  docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md
```

### 2.3 Deleted

```text
.claude/launch.json（Exact Target、User既定Policyとの不整合を解消）
.claude/（空Directory）
```

### 2.4 本Rework Scope外（Working Treeに既に存在した、対象外）

```text
docs/public/roadmap_ja.md
docs/project/shared/history/operations/roadmap_phase_5_ex_phase_9_ex_reservation_update_ja_20260821193804.md
docs/project/shared/history/planned_work/post_phase_3_claude_forward_execution_candidates_ja_20260821193804.md
docs/project/shared/history/planned_work/phase_4_0_deepseek_*.md（5 File）
docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md
```

→ これらはPhase 3実装着手前後の別作業由来であり、本Rework（P3-CODEX-001〜005、P3-GOV-001）のExact Mutationには含めない。

### 2.5 Git Mutation

```text
Commit: 0（HEAD は本Rework開始時と同一：f255681 docs(phase-2): record final push postflight）
Branch: main（変更なし）
```

## 3. Validation

```text
Backend Full Suite   : 878 passed／3 deselected（Rework前Baseline 850 → 878、Regression 0）
  3 deselected は Phase 1/2由来の既存Marker Deselectのみ
Ruff Check／Format    : PASS（src, tests）
Mypy（宣言Scope=src） : PASS — 153 source files、Error 0
Frontend Test         : 117 passed（全File）
Frontend Typecheck／Lint／Build : PASS
Testは全てtmp_path／InMemoryEvidenceStore等の隔離Rootのみ使用。実runtime_data/への存在確認すら行っていない。
```

## 4. Remaining Major Finding

なし。P3-CODEX-001〜005、P3-GOV-001はすべてCLOSEDである。

継続Open（Deferred、Blocking外）：

- mypy bare（tests/全体）にPhase 2由来の既存11 Errorが残存（`mypy src`はClean）。
- Evidence Store単一Scope（`web_preview`固定）。複数Worker分離は将来Phase。
- Governance ModeはProcess-local（Restart で OFF へ戻る）——アーキテクチャ§1の意図どおりで、Deferred Evidenceではなく設計上の割り切り。

## 5. Corrected Automation／Compaction Evidence

`phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md`を参照。要旨：

- Technical：CLOSED（本File §1／§3）。
- Root Boundary：本Rework中0件逸脱。
- Provider-local Artifact：`.claude/launch.json`削除済み。
- User `runtime_data/` Write／Delete：**前Session中に1件の違反があったことを確認・訂正**。本Rework中は0件。
- False Completion：**旧Handoffの「Scope逸脱0」「User実Data非接触」を訂正**。
- Human Intervention：1件（Phase 3-0直後の状況報告停止）。
- Execution Continuity：Auto-Compaction 1 Cycleを認識し、Recovery Entry経由で正しく継続。
- Hash Tracker：成功0／失敗1へ訂正。
- Recovery Docs Reread：`UNVERIFIED`。
- Language Fidelity：`DRIFT`（是正済みではなく、発生した事実として記録）。

## 6. `.claude`不存在、`runtime_data/`未確認・非接触の確認

```text
$ ls -la .claude
ls: .claude: No such file or directory
```

`runtime_data/`は本Rework中、存在確認（`ls`／`stat`等）を含め一切実行していない。

## 7. Explicit Stop

Phase 3-H Closure、User Acceptance、Final Docs、Backup、Git操作、Phase 4開始のいずれへも進まない。次のActionはCodex側またはUser側に委ねる。
