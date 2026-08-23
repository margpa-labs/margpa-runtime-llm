# Phase 3 Claude Third Rework Complete Candidate Handoff

```yaml
document_id: phase_3_claude_third_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_003_third_rework
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_claude_third_rework_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 22:06:04 JST
created_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_3/handoffs/phase_3_codex_third_independent_review_rework_handoff_ja_20260821213930.md
required_reading:
  - docs/project/phases/phase_3/handoffs/phase_3_codex_third_independent_review_rework_handoff_ja_20260821213930.md
  - docs/project/phases/phase_3/handoffs/phase_3_claude_second_rework_complete_candidate_handoff_ja.md（第2回Rework Handoff。本Fileと矛盾しない範囲でなお有効）
```

本HandoffはP3-CODEX-006／009（第2回Reviewで既にCLOSE済みと判定済み）を再変更しない。本Cycleが扱うのはP3-CODEX-010・P3-CODEX-011・P3-GOV-003の3件のみである。

## 0. Recommendation

**GO**（Codex Independent Re-reviewへ進めることを推奨する）。

P3-CODEX-010・P3-CODEX-011・P3-GOV-003の全3件をCLOSEした。実装はFocused／Regression／Static／Full／Frontend Buildで検証済み、Existing Testの削除・弱体化は0件。

Remaining Major Finding：本Cycle完了時点で未クローズの重大Findingはない（詳細は6章）。ただし本Document自身も自己申告Closure Candidateであり、次のExact RouteはCodex側の独立再現である。

## 1. P3-CODEX-010・P3-CODEX-011・P3-GOV-003 個別CLOSE根拠

### P3-CODEX-010 — Definition SourceのVerified ReadのCheck-to-open Race：CLOSED

`FilesystemDefinitionProvider`（[filesystem_provider.py](../../../../../src/margpa_runtime_llm/adapters/governance_definitions/filesystem_provider.py)）を全面書き換えした。

- `<root>`のみを唯一のTrusted-Anchor Open（`os.open(root, O_DIRECTORY|O_NOFOLLOW)`、絶対Path・単発）とし、それ以外の全Component（Manifestへの各Directory Hop、Source Entryの各Directory Hop、および両者のLeaf File自体）を`os.open(part, os.O_NOFOLLOW, dir_fd=parent_fd)`によるDirectory-fd Chainで段階的にOpenする（`_open_leaf_file_fd`）。旧実装は`_safe_resolve()`で各ComponentをlstatしてからPath経由で`.stat()`／`.read_bytes()`を別途実行しており、Check（lstat）とOpen（stat/read）の間にRace Windowが残っていた。新実装はCheckそのものがOpenであり（Symlink Component上で`ELOOP`）、Timingに関係なくSyscall Levelで閉じる。
- Leaf FDを`os.fstat()`し、Regular File・非World-writable（`st_mode & 0o002`）・Byte上限のいずれかを満たさなければRead前に拒否する（`_read_bounded_from_fd`）。Readは同一FDから`os.read()`を`MAX_*_BYTES`超過を検知するまでLoopし、超過時点で全体読了前に中断する。
- 同じFDから得たBytesに対してのみManifestの`byte_length`／SHA-512照合を行い、そのBytesだけをJSON Parse／`verified_source_json`へ渡す（P3-CODEX-007のSnapshot性質を維持）。
- Manifest自体（`_load_signed_manifest()`）も、Sourceと全く同じ`_open_leaf_file_fd`＋`_read_bounded_from_fd`境界へ統合した——旧実装が持っていた「Manifestは`self._manifest_path`という別のPath経由」という非対称性を解消した。
- Leaf Openには`O_NONBLOCK`を追加した。FIFO等の非Regular Fileへ差し替えられた場合、`O_NONBLOCK`なしではWriter接続を待って`open()`自体がProcessを無期限Blockしうる（Regular Fileに対しては無害）——Handoff指摘の「FIFO／Device等への差替えによるBlocking」を具体的に閉じた。
- macOS/BSD特有の挙動として、`O_DIRECTORY|O_NOFOLLOW`でSymlinkedディレクトリを開こうとした場合、Linuxの`ELOOP`ではなく`ENOTDIR`が返ることを実装中に検出した（Regression Testで顕在化）。`ENOTDIR`受信時のみ追加で`lstat`（Openは既に失敗済みで安全な状態、この`lstat`はReason Code選択のためだけの診断であり新たなRace Windowにはならない）してSymlink有無を判定し、正しく`path_unsafe`／`path_not_found`を区別するよう修正した。

### P3-CODEX-011 — JSONL Storeの容量超過ReceiptとIndex外Segment：CLOSED

`LocalJsonlEvidenceStore`（[local_jsonl_store.py](../../../../../src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py)）を修正した。

- **Finding A**：`append()`が`_open_active_segment_with_capacity()`を新設し、Active SegmentをOpenした直後に`os.fstat()`で現在Byte Sizeを取得、`current_size + len(encoded) > MAX_SEGMENT_FILE_BYTES`ならBytesへ一切触れずCloseして次のSegmentへRolloverする（新Segmentも収まらない場合のみ、Receiptを返さず`CAPACITY_EXCEEDED`として拒否——Typed Capacity Failureであり、成功ReceiptとRestart Recoveryの不一致は発生しない）。この容量拒否はWrite失敗ではないため、Storeを`degraded`にはしない（実際のOS Write／Fsync失敗のみがDegradeする、という既存のP3-CODEX-008契約と整合させた）。
- **Finding B**：`_segment_indices()`がFilename由来のIndexを`1..MAX_SEGMENT_COUNT`の範囲内かCheckし、範囲外（8桁Filenameが表現しうる`99999999`等）を検出した時点でFail-closedに`PATH_VIOLATION`を送出するよう変更した。`_load_existing_segments()`のDegraded-Highest-Segmentからの`highest + 1`進行にも同じ上限Checkを追加し、Ceiling上でDegradeした場合は9桁Segmentを新規作成せず`CAPACITY_EXCEEDED`で拒否する。
- **Finding C**：Directory-fd Chain取得を`segments/`単体の絶対Path Openから、`<root>`をTrusted-Anchor（唯一の絶対Path Open）とし、`root`配下の未作成Prefix・`<scope>`・`segments`の各Componentを`os.mkdir(..., dir_fd=parent_fd)`＋`os.open(..., O_NOFOLLOW, dir_fd=parent_fd)`で1段ずつ辿る方式（`_open_directory_chain`）へ拡張した。旧実装は`os.open(self._segments_dir, O_NOFOLLOW)`という単一の複数Component Pathで、`O_NOFOLLOW`が保護するのは最終Componentのみ（`scope`のようなIntermediate Componentは無防備）だった。新規作成したDirectoryは開いたFD自体へ`os.fchmod(fd, 0o700)`し、既存Directoryは同FDの`fstat`でOwner／Mode（`0o022`）を検証する——いずれもPath文字列の再導出なしに、既にOpen済みのFD上でのみ判定する。

### P3-GOV-003 — Second Auto-Compaction Cycle未記録：CLOSED

`docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md`へCycle 2を追記した（既存Cycle 1は変更せず、集計行のみ「成功0／失敗1」→「成功0／失敗2」へ更新——Handoffの`Allowed`が明示許可する「Cycle 2追記および集計更新」の範囲内）。

- 検知根拠：`USER_OBSERVED`と明記した（Claude自身のTool Logによる検知ではない）。
- Before／After Hash：いずれも`missing`と記録し、事後生成・成功認定を行わなかった。Hash Recovery自体はFAILUREとして記録した。
- Recovery Docs再読：具体的Read Evidenceを提示できないため`UNVERIFIED`とした。
- Language／Interaction Fidelity：Codex指摘（Compaction後に英語出力へDriftした事実）を`DRIFT`として記録した。
- 技術作業継続の成否（SUCCESS）と、Hash Recovery／Language Fidelityの成否（いずれもFailure/Drift）を別軸として明示し、「技術的に完走できたから問題なかった」という混同を避けた。

## 2. Exact Mutation（本Third Rework Cycleで変更したFileのみ）

### 変更（Source）

```text
src/margpa_runtime_llm/adapters/governance_definitions/filesystem_provider.py
src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py
```

### 変更（Test）

```text
tests/unit/governance_definitions/test_filesystem_provider.py
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py
```

### 変更（Docs、Allowedが明示許可するAppend-only／集計更新）

```text
docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md（Cycle 2追記、集計行更新）
```

### 新規作成（Docs）

```text
docs/project/phases/phase_3/handoffs/phase_3_claude_third_rework_complete_candidate_handoff_ja.md（本File）
```

### Mandatory Validationの副作用として再生成されたFile（Frontend Sourceは一切変更していない）

```text
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
```

6章のMandatory Validationが要求する「Frontend Buildを1回実行する」（`npm run build`）を実行した結果、Vite Buildが`frontend/`配下の既存Source（本Cycleで一切変更していない）から上記2Fileを決定論的に再生成した副作用。`frontend/`配下のSource File自体（`.tsx`／`.ts`等）は本Cycleで1行も変更していない——`git status`で示される`frontend/**`のModified状態は本Cycle開始前から存在した、以前のCycleに由来する既存差分である。

### 明示的にScope外（変更していない）

```text
runtime_data/ 配下の全て（一切のRead/List/Stat/Write/Delete Action無し）
frontend/** のSource File自体（.tsx/.ts等、Build副産物を除く）
docs/public/roadmap_ja.md、docs/project/shared/task_roles/**
P3-CODEX-006、P3-CODEX-009関連の実装・Test（第2回Reviewで既にCLOSE済み、再変更していない）
Git／GitHub Mutation（Commit・Push等）は本Cycle中0件
```

## 3. Regression Test名と実測結果

Codex Independent Reviewの§1〜§2（P3-CODEX-010／011）がそれぞれ要求したRegression Test（新規・既存の両方を含む、今後のRegressionを検知するために固定する）：

```text
P3-CODEX-010（新規3件・既存4件、Manifest／Sourceの両方でLeaf Swap・Parent Swap・Non-regular・Oversizedを網羅）:
  tests/unit/governance_definitions/test_filesystem_provider.py::test_manifest_reached_through_a_symlinked_intermediate_directory_is_rejected   [新規: Manifest Parent Swap]
  tests/unit/governance_definitions/test_filesystem_provider.py::test_rejects_source_reached_through_a_symlinked_intermediate_directory        [既存: Source Parent Swap]
  tests/unit/governance_definitions/test_filesystem_provider.py::test_rejects_a_source_file_that_is_itself_a_symlink                            [既存: Source Leaf Swap]
  tests/unit/governance_definitions/test_filesystem_provider.py::test_rejects_symlinked_manifest                                                [既存: Manifest Leaf Swap]
  tests/unit/governance_definitions/test_filesystem_provider.py::test_a_fifo_replacing_a_source_leaf_is_rejected_without_blocking               [新規: Source Non-regular/Blocking]
  tests/unit/governance_definitions/test_filesystem_provider.py::test_a_fifo_replacing_the_manifest_is_rejected_without_blocking                [新規: Manifest Non-regular/Blocking]
  tests/unit/governance_definitions/test_filesystem_provider.py::test_verify_sources_reports_source_too_large_without_crashing                  [既存: Source Oversized]
  tests/unit/governance_definitions/test_filesystem_provider.py::test_load_package_reports_manifest_too_large_without_crashing                  [既存: Manifest Oversized]

P3-CODEX-011（新規5件、Handoff§2 Required Reworkの5Bulletに1対1対応）:
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_segment_byte_limit_triggers_rollover_before_writing_and_stays_recoverable
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_event_larger_than_a_fresh_empty_segment_is_capacity_exceeded_not_a_receipt
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_out_of_range_existing_segment_index_is_rejected
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_degraded_highest_segment_at_index_ceiling_fails_closed_instead_of_rolling_over
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_symlinked_scope_component_is_rejected_even_when_its_target_has_a_real_segments_dir
```

いずれも既存Testの削除・弱体化は行っていない（既存4件のP3-CODEX-010系Testは、旧実装から新実装〔Directory-fd Chain〕へ切り替わった後も無修正のまま合格し続けている）。

## 4. Focused／Regression／Static／Full／Frontend Build 実測結果

すべてCommand出力から直接数えた値であり、推測値は含まない。

```text
Focused（上記13 Testのみ）                                            : 13 passed
tests/unit/governance_definitions/test_filesystem_provider.py（全体）  : 21 passed
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py（全体）: 20 passed
Backend Full Suite（`pytest -q`）                                      : 900 passed／3 deselected
Ruff Check（Full Repository）                                          : PASS（All checks passed!）
Ruff Format Check（Full Repository）                                   : PASS（237 files already formatted）
Mypy src                                                               : PASS（Success: no issues found in 153 source files）
Frontend Typecheck（`npm run typecheck`）                              : PASS
Frontend Lint（`npm run lint`）                                        : PASS
Frontend Test（`npm test -- --run`）                                   : 117 passed（16 files）
Frontend Build（`npm run build`）                                      : PASS（built in 84ms — 前回Handoffで`Claude: NOT RUN`だったMandatory Validationを本Cycleで実行した）
```

## 5. Auto-Compaction Cycle 2のEpistemic ClassificationとLanguage Fidelity

`docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md` Cycle 2に記録した内容の要約（詳細は当該File参照）。

```text
検知根拠         : USER_OBSERVED（Claude独自のTool Log検知ではない）
Before/After Hash: missing（事後生成・成功認定なし）→ Hash Recoveryとして FAILURE
Recovery Docs再読 : UNVERIFIED（具体的Read Evidence提示不能）
Language Fidelity : DRIFT（Compaction後に英語へDriftした事実をCodex指摘に基づき記録）
技術作業継続      : SUCCESS（別軸——P3-CODEX-009残実装・P3-GOV-002 Correction・Second Rework Handoff作成を完了）
```

Hash Recovery・Recovery Docs再読・Language Fidelityのいずれについても、「技術作業が継続できた」ことを根拠に成功認定へすり替えていない。

## 6. Remaining Major Finding

本Third Rework Cycle完了時点で、未クローズの重大Findingは無い。P3-CODEX-010・P3-CODEX-011・P3-GOV-003はいずれも本Document §1・§3・§4・§5で示した根拠によりCLOSEした。

本Documentの著者による自己申告Closure Candidateである点は明示しておく——次のExact Routeは、Codex Independent Re-reviewが本Documentおよび§3のRegression Testを独立再現し、CLOSEを検証することである。

## Next Exact Route

Phase 3-H Closure、User Acceptance、Final Docs、Backup、GitおよびPhase 4開始のいずれへも進まず、ここで停止する。次のExact Routeは、Codex Independent Re-reviewが本Cycleの3件のCLOSEを独立再現・検証することである。
