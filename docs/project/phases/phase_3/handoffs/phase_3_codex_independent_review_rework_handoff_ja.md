# Phase 3 Codex Independent Review — Exact Rework Handoff

```yaml
document_id: phase_3_codex_independent_review_rework_handoff
status: adjust_required
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_001
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
created_at: 2026-08-21 JST
predecessor: docs/project/phases/phase_3/handoffs/phase_3_claude_complete_candidate_handoff_ja.md
completion_line: phase_3_claude_rework_complete_candidate
git_mutation_authorized: false
phase_4_authorized: false
```

## 0. Controller Decision

`ADJUST`。Phase 3実装の大部分とTest成果は有効だが、次のRequired Findingを閉じるまでPhase 3 Technical Closureへ進まない。

本Reworkはユーザーへ追加設計判断を返す対象ではない。Frozen Phase 3 Contract、既存最上位規則および実行事実へ適合させる、Claude側Controller-owned Reworkである。

## 1. P3-CODEX-001 — Mode MutationをConfiguration Controlへ統合

### Finding

Frozen Architecture §8.3／§9.2、`P3-MOD-007`およびPhase Indexは、Mode変更を既存Configuration ControlのPreview／Applyへ統合し、Revision／Digest／CASを維持すると定める。現実装の専用`POST /api/v3/governance/mode`はこの契約を満たさず、Stale Client Conflict、Operation Idempotencyおよび統一Effective Config Traceを迂回する。

### Required Rework

- `governance_mode`を既存Configuration ControlのTyped Safe Projection／Patch／Preview／Applyへ統合する。
- `operation_id`、`expected_revision`、`expected_digest`、Conflict、IdempotencyおよびRedacted Changeを既存Contractどおり適用する。
- Governance RuntimeのModeとConfiguration Effective Snapshotを一つの成功境界で同期し、片側だけの部分Mutationを禁止する。
- `enforce`はUnavailable／Unsupported、State Mutation 0、Silent Downgrade 0を維持する。
- `/api/v3/governance/*`はRead-only Status Surfaceとする。専用Mode Mutation EndpointをCurrent Mutation Authorityとして残さない。
- FrontendはConfiguration Preview／Apply Routeを使用し、Governance専用CAS-free Applyを使用しない。
- Process Restart時にOFFへ戻るProcess-local方針自体は、安全な初期値として維持可能。非永続であることをEffective Config／UIへ明示する。

## 2. P3-CODEX-002 — OFF時Governance Hook Call 0

### Finding

現実装はGovernance機能有効時にObserverを常時Bindingし、OFFでも全Generation Eventを`GenerationObservationTracker`／Observerへ渡した後、Observer内部でWriteを抑止する。これは「Evidence Store Write 0」ではあるが、`P3-MOD-003`／`P3-ACC-002`の「Governance Hook Call 0」ではない。

### Required Rework

- Generation開始時点のModeでObserver Bindingを解決し、OFFではTracker／Observer Call自体を0にする。
- OBSERVEで開始したGenerationはStart／Terminalを最大1組として完結させ、途中でOFFへ変更されても片側Evidenceだけを残さない。
- OFFから開始したGenerationを途中Mode変更で遡及観測しない。
- 可能ならEvidence Store Directory生成も最初のOBSERVE使用までLazy化し、Default OFF Bootの不要Filesystem Mutationを避ける。
- v1／v2、Persistent／EphemeralのSpy Testで、OFF Hook Call 0、OBSERVE Start／Terminal、Writer Failure非介入、SSE Shape／Order不変を証明する。

## 3. P3-CODEX-003 — Mode Apply FailureのAtomicity／Safe Failure

### Finding

`GovernanceDefinitionsRuntime.apply_mode()`は、OBSERVE Pipeline実行前に`_mode`と`_revision`を変更する。Provider／Adapter／Reader／Compilerが例外を返すと、Applyは失敗してもModeだけOBSERVEへ進んだ部分状態を残し得る。

### Required Rework

- OBSERVE候補Summary／Planを先に構築・検証し、成功後だけMode／Revision／SummaryをAtomic Commitする。
- Pipeline Failure時は旧Mode／Revision／Summaryを完全維持する。
- Raw ExceptionをWebへ露出せず、Typed Safe Failureへ正規化する。
- Configuration Control Applyとの統合後も、Config側とGovernance側の片側Commitを禁止する。
- Provider／Adapter／Reader／Compiler Fault InjectionとConcurrent／Stale Apply Testを追加する。

## 4. P3-CODEX-004 — Definition ProviderのResource／Path Fail-closed

### Finding

`P3-PER-001`はDefinition File、Package、Depth、Collection、String、IR Node、Plan RuleおよびEvidence Sizeの上限を要求する。しかし現ProviderはManifest／Sourceを上限確認前に全読込みし、Manifest Entry数にも上限がない。また`Path(entry.relative_path).relative_to("definitions")`はPrefix不一致で未処理`ValueError`となり得る。`resolve()`後の`is_symlink()`判定ではRoot内Symlink Componentを検知できない。

### Required Rework

- Manifest bytes、Source bytes、Source／Definition件数、Path depth、Collection／String、IR Node／Section、Compiled Plan item、Canonical Evidence event／segmentに有限上限を定義する。
- Fileは`stat`等でSize Gateを通してから読込み、超過をTyped Invalid／Unsupportedへ正規化する。
- `definitions/` Prefix不一致、Malformed Relative Path、Unknown Schema、上限超過を未処理例外にしない。
- RootからTargetまでの各Path Componentを`lstat`相当で検査し、Root内外を問わずSymlink経由を拒否する。
- Manifest／Source／IR／Planの上限境界（limit、limit+1）とSymlink／Prefix Fault Testを追加する。

## 5. P3-CODEX-005 — JSONL Appendの完全Write

### Finding

`LocalJsonlEvidenceStore.append()`は`os.write()`の戻り値を確認せず、Short WriteでもReceiptを返し得る。これはCanonical AppendとReceiptの一致を破る。

### Required Rework

- 全bytesを書き切るLoopまたは同等の安全なWrite契約を使用する。
- 0-byte／Short Write／途中OSErrorをFault Injectionし、成功時だけReceiptを返すことをTestする。
- 失敗時に既存Valid Prefixを改変・切詰め・自動修復しない。
- P3-CODEX-004で定めたEvent／Segment上限とRollover契約を同時に検証する。

## 6. P3-GOV-001 — Automation／Compaction Evidence訂正

### Confirmed Facts

- `.claude/launch.json`を本Sessionで作成した。ユーザーはRepository内`.claude`を不要として削除済み状態を正本としており、Provider-local Artifactを正本にしない方針である。
- 禁止対象だった実`runtime_data/`配下へ`runtime_data/audit_evidence/`を作成し、その後`rm -rf`で自己Cleanupした。
- Frozen HandoffはUser実`runtime_data/`接触と誤生成物の自己Cleanupを明示禁止していた。
- Complete Handoff／Final Evidenceの「Scope逸脱0」「User実Data非接触」は上記実行事実と矛盾する。
- Auto-Compactionを認識したと報告した一方、`claude_long_running_auto_compaction_hash_tracker_ja.md`は成功0／失敗0のままで、Before／After Hash Evidenceがない。
- Compaction後に実行は継続したが、応答言語が日本語から英語へDriftした。Operating Notes／Recovery Docsの完全再読了は現Evidenceから検証不能である。

### Required Rework

- ユーザーが既に削除を明示許可したExact Target `.claude/launch.json`と、空になった場合の`.claude/`だけを削除する。他PathをCleanupしない。
- `runtime_data/`へは今後一切Read／List／Stat／Write／Deleteしない。失われたTest副産物の再作成や修復も行わない。
- 新規Append-only Incident／Correction Evidenceを作り、少なくとも以下を分離記録する。
  - Technical implementation result
  - Root boundary result
  - Provider-local Artifact violation
  - User runtime_data write／delete violation
  - False completion claim correction
  - Human Intervention 1件
  - Execution Continuity after Compaction
  - Recovery Docs reread: `UNVERIFIED`（証明がなければ）
  - Interaction／Language Fidelity: `DRIFT`
- Hash TrackerはEvidenceを捏造しない。Compactionを検知したのにBefore／After Hash照合を実施・記録できなかった事実をFailure Cycleとして追記し、成功回数を増やさない。
- Complete Candidate Handoffを上書きせず、新規Rework Completion Handoffで旧主張を明示訂正する。
- 今後の報告は日本語で行う。

## 7. Allowed／Forbidden Boundary

### Allowed

- 上記Findingを閉じるために必要なPhase 3 Source／Frontend／TestのExact Path。
- `docs/project/phases/phase_3/history/**`への新規Append-only Correction／Rework Evidence。
- `docs/project/phases/phase_3/handoffs/phase_3_claude_rework_complete_candidate_handoff_ja.md`の新規作成。
- `docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`の契約どおりのCycle追記とCount訂正。
- Exact `.claude/launch.json`および空の`.claude/`の削除。

### Forbidden

- `runtime_data/`への全Action。
- Root外、`other/`、別Project、Provider Memory、Network、Secret、External Service。
- Existing Historyの変更・削除。
- Git／GitHub Mutation。
- Phase 4実装、Model Load、AWS。
- Required Findingと無関係なRefactor。

## 8. Mandatory Validation

- Required FindingごとのFocused Test。
- Configuration Control／Governance／Audit Evidence／v1／v2／Persistent／Ephemeral／Public／BasicのTargeted Regression。
- Frontend Test／Typecheck／Lint／Build。
- Ruff Format／Check、Mypy declared scope。
- Backend Full Suiteを最終1回。
- Testは`tmp_path`等の隔離Rootだけを使用し、実`runtime_data/`を存在確認しない。
- Existing Testの削除・弱体化0。

## 9. Completion Report

新規`phase_3_claude_rework_complete_candidate_handoff_ja.md`へ、次を日本語で記録して停止する。

- P3-CODEX-001〜005、P3-GOV-001の個別CLOSE根拠。
- Exact Mutation。
- Focused／Regression／Static／Full結果。
- Remaining Major Finding。
- Corrected Automation／Compaction Evidence。
- `.claude`不存在、ただし`runtime_data/`は未確認・非接触であること。
- GO／ADJUST／STOP Recommendation。

Phase 3-H Closure、User Acceptance、Final Docs、Backup、Git、Phase 4開始へは進まない。
