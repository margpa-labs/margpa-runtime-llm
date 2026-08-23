# Phase 3 Codex Third Independent Review — Exact Rework Handoff

```yaml
document_id: phase_3_codex_third_independent_review_rework_handoff_20260821213930
status: adjust_required
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_003_third_rework
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-21 21:39:30 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_3/handoffs/phase_3_claude_second_rework_complete_candidate_handoff_ja.md
completion_line: phase_3_claude_third_rework_complete_candidate
git_mutation_authorized: false
phase_3_closure_authorized: false
phase_4_authorized: false
```

## 0. Controller Decision

`ADJUST`。

Codex独立検証では、Claude Handoffが申告したBackend Full Suite `892 passed／3 deselected`、RuffおよびMypyを再現した。Handoffで未実施だったFrontend BuildもCodexが独立実行しPASSした。また、P3-CODEX-006（Compiled Plan Cache）およびP3-CODEX-009（Evidence Write Failure可視化）はCLOSE可能と判定した。

一方、P3-CODEX-007とP3-CODEX-008には同じ安全境界内の未閉鎖経路が残る。さらに、ユーザーが今回のSecond Rework中に観測したAuto-Compaction CycleがTracker／Evidenceへ記録されていない。したがって、Phase 3-H Closureおよび「Remaining Major Findingなし」は受理しない。

本Handoffは以下3件だけを扱う。既にCLOSEしたFinding、Phase 4、Deferred事項、新機能またはUI改善を再活性化してはならない。

## 1. P3-CODEX-010 — Definition SourceのVerified ReadにCheck-to-open Raceが残る

### Confirmed Finding

`FilesystemDefinitionProvider._verify_sources_with_content()`は、`_safe_resolve()`でPath Componentを`lstat`した後、`source_path.stat()`と`source_path.read_bytes()`をPath経由で別々に実行する。

このため、検査後からOpenまでの間にSource Leafまたは親DirectoryをSymlink等へ差し替えられると、次が成立する。

- Pre-read Size Gateより前にRoot外Fileまたは巨大Fileを読む。
- `stat()`で確認したFileと、実際にDigest／JSON Parseへ渡すBytesのFile Identityが一致しない。
- FIFO／Device等への差替えによるBlockingまたはRoot外参照を、Open時点で防げない。

Runtimeによる二度目の再Readを削除し、Providerが返した同一BytesをNormalizationへ渡す修正自体は正しい。しかし、その最初のVerified Readが安全な単一Open境界になっていないため、P3-CODEX-007は完全には閉じていない。Manifest Readの`stat()`→`read_text()`にも同型の境界がある。

### Required Rework

- Trusted RootをDirectory FDとして保持し、各Directory ComponentおよびLeafを`dir_fd`／`openat`相当と`O_NOFOLLOW`で段階的にOpenする。絶対Pathを再解決してLeafを開かない。
- Open済みの同一FDへ`fstat()`を行い、Regular File、Owner／Mode方針、Byte上限を確認する。
- Readは同じFDから`MAX_*_BYTES + 1`までのBounded Readとし、上限超過を全File Read前に拒否する。
- 同じFDから得たBytesに対してManifestの`byte_length`とSHA-512を照合し、そのBytesだけをJSON Parse／Normalizationへ渡す。
- Manifestも同じ安全なOpen／Bounded Read境界へ統合する。
- Path／Leaf／親DirectoryのSymlink swap、巨大化、Non-regular差替えを未検証Read／NormalizeなしでTyped Failureへ落とすRegression Testを追加する。

## 2. P3-CODEX-011 — JSONL Storeが容量超過ReceiptとIndex外Segmentを作れる

### Confirmed Finding A：Append時にSegment Byte上限を強制していない

`LocalJsonlEvidenceStore.append()`は`MAX_EVENT_LINE_BYTES`と`MAX_EVENTS_PER_SEGMENT`を確認するが、Open済みSegmentの現在Byte Sizeと`len(encoded)`の合計を`MAX_SEGMENT_FILE_BYTES`と比較しない。

したがって、64MiB直前のSegmentへEventをAppendして上限を超えても、`fsync`後に成功Receiptを返す。次回Reopenは同じSegmentを`MAX_SEGMENT_FILE_BYTES`超過として拒否するため、成功ReceiptとRestart Recoveryが一致しない。これはP3-CODEX-008のFalse Receipt問題を別経路で再発させる。

### Confirmed Finding B：Segment CountとSegment Indexを混同している

`_segment_indices()`はDirectory Entry数だけを`MAX_SEGMENT_COUNT`と比較し、Filenameから得たIndex自体が`1..MAX_SEGMENT_COUNT`内かを検証しない。8桁Filenameは`segment-99999999.jsonl`まで受理できる。

最高Indexが破損している場合、`_load_existing_segments()`は無条件に`highest + 1`をActive Indexへ設定する。結果として9桁の`segment-100000000.jsonl`へ成功Appendできるが、次回Scanの8桁Regexから除外され、Receipt対象Eventが消える。

### Confirmed Finding C：Held Directory FDの初期取得前に親Component Raceが残る

`segments/`のFDを保持した後の相対Openは改善されている。しかし、保持FD自体を絶対Pathの`os.open(self._segments_dir, ...)`で取得しており、それ以前のPath検査とOpenの間に親`scope/`等が差し替えられる経路が残る。`O_NOFOLLOW`は最終Componentだけへ作用し、親ComponentのSymlink追跡を防がない。

### Required Rework

- Append前にOpen済みSegment FDを`fstat()`し、`current_size + len(encoded)`が上限を超える場合は既存Bytesへ触れず新SegmentへRolloverする。
- Event単体がSegment上限へ収まらない場合はReceiptを返さずTyped Capacity Failureとする。
- Discovery時、各Segment Indexが`1..MAX_SEGMENT_COUNT`内であることを確認し、範囲外IndexをFail-closed拒否する。
- Degraded Highest Segmentから`highest + 1`へ進む前にもIndex上限を確認する。9桁またはScan不能なSegmentを作らない。
- Root／Scope／Segmentsを、Trusted Root FDからComponentごとに`O_NOFOLLOW`で開く。最終Componentだけの`O_NOFOLLOW`へ依存しない。
- 次のRegression Testを追加する。
  - AppendでSegment Byte上限を跨ぐ場合にRolloverし、全成功ReceiptがReopen後も復元できる。
  - Event単体がSegment Byte上限を超える場合はReceipt 0。
  - 範囲外の既存Segment Indexを拒否する。
  - 最大IndexのDegraded Segmentから9桁Segmentを作らない。
  - 親Directory差替えでもRoot外Write 0。

## 3. P3-GOV-003 — Second Auto-Compaction Cycleが未記録

### Confirmed Finding

ユーザーはSecond Rework実行中にClaude Codeの利用可能Context Gaugeが回復し、Auto-Compactionが1回発生したことを観測した。Compaction後、Claudeは英語出力へ戻った後も作業を継続し、最終Handoff自体は日本語で作成した。

しかし、`docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`は現在も「成功0／失敗1」でCycle 1だけを記録している。Second Rework Handoffにも今回のCycle、Before／After Hash、Recovery Docs再読、Language FidelityまたはUser-observed Compactionの記録がない。

### Required Evidence Correction

- 今回のCycleをCycle 2として記録する。
- Compaction発生根拠は`USER_OBSERVED`とし、Claude自身がTool Logで検知したように書かない。
- Before／After Hashが取得されていなければ`missing`とし、事後生成または成功認定を行わない。Tracker契約上はHash Recovery Failureとして扱う。
- Recovery Docs再読は、具体的Read Evidenceを提示できなければ`UNVERIFIED`とする。
- Compaction後に英語出力へ戻った事実をLanguage／Interaction Fidelity `DRIFT`として記録する。
- 技術作業を継続できた事実と、Hash Recovery／Language Fidelityが成功したかを別軸で記録する。

## 4. Evidence Correction

Second Rework Handoffの次の記述は、次回Handoffで訂正する。既存Handoffを上書きしない。

- `Focused（上記13 Testのみ）: 13 passed`は誤り。列挙対象は14件であり、Codex独立実行結果も`14 passed`だった。
- Frontend Buildは前回HandoffのMandatory Validationだったが、Claudeは自己判断で省略した。Codex独立実行ではBuild PASSだった。次回Handoffでは`Claude: NOT RUN`と`Codex Independent Review: PASS`を混同せず記録する。

## 5. Allowed／Forbidden Boundary

### Allowed

- `src/margpa_runtime_llm/adapters/governance_definitions/filesystem_provider.py`
- `src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py`
- 上記2境界に直接必要な既存Port／Exportの最小変更。
- `tests/unit/governance_definitions/test_filesystem_provider.py`
- `tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py`
- 必要な同Boundaryの新規Focused Test File。
- `docs/project/phases/phase_3/history/**`への新規Append-only Rework／Compaction／Validation Evidence。
- `docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`のCycle 2追記および集計更新。
- `docs/project/phases/phase_3/handoffs/phase_3_claude_third_rework_complete_candidate_handoff_ja.md`の新規作成。

### Forbidden

- `runtime_data/`へのRead／List／Stat／Write／Delete。
- Project Root外、`other/`、別Project、Provider Memory、Network、Secret、External Service。
- Existing Historyの変更・削除。
- Git／GitHub Mutation。
- Stable Docs、Roadmap、Frontend、既にCLOSEしたP3-CODEX-006／009の再変更。
- Phase 3-H Closure、Phase 4、Model Load、AWS。
- Required Findingと無関係なRefactorまたは新機能。

## 6. Mandatory Validation

- P3-CODEX-010／011の再現TestをRegressionとして固定する。
- Governance Definition ProviderおよびLocal JSONL StoreのFocused／Integration Test。
- Backend Full Suiteを最終1回。
- Ruff Format／Check、Mypy `src`。
- Frontend Sourceを変更していなくても、前回未実施分を含めFrontend Typecheck／Lint／Test／Buildを各1回実行する。
- Existing Test削除・弱体化0。
- Testは隔離されたTest Rootだけを使用し、実`runtime_data/`へ接触しない。
- Test件数はCommand出力から数え、列挙数と一致させる。推測値を書かない。

## 7. Completion Report／Stop Boundary

新規`docs/project/phases/phase_3/handoffs/phase_3_claude_third_rework_complete_candidate_handoff_ja.md`へ、日本語で次を記録して停止する。

- P3-CODEX-010／011およびP3-GOV-003の個別CLOSE根拠。
- Exact Mutation。
- Regression Test名と実測結果。
- Focused／Regression／Static／Full／Frontend Buildの実測結果。
- Auto-Compaction Cycle 2のEpistemic ClassificationとLanguage Fidelity。
- Remaining Major Finding。
- `GO／ADJUST／STOP` Recommendation。

Phase 3-H Closure、User Acceptance、Final Docs、Backup、GitおよびPhase 4開始へ進まず、Codex Independent Re-reviewを待つ。
