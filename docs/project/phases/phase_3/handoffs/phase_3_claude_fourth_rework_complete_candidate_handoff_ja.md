# Phase 3 Claude Fourth Rework Complete Candidate Handoff

```yaml
document_id: phase_3_claude_fourth_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_004_fourth_rework
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_claude_fourth_rework_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 22:49:29 JST
created_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_3/history/index/phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md
required_reading:
  - docs/project/phases/phase_3/handoffs/phase_3_codex_fourth_independent_review_rework_handoff_ja_20260821223200.md
  - docs/project/phases/phase_3/history/index/phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md
  - docs/project/phases/phase_3/handoffs/phase_3_claude_third_rework_complete_candidate_handoff_ja.md（第3回Rework Handoff。§2の1文言のみ上記Correctionにより訂正済み、それ以外は矛盾しない範囲でなお有効）
```

本HandoffはP3-CODEX-010／011／P3-GOV-003（第4回Reviewで既にCLOSE可能と判定済み）を再変更しない。本Cycleが扱うのはP3-CODEX-012・P3-GOV-004の2件のみである。

## 0. Recommendation

**GO**（Codex Independent Re-reviewへ進めることを推奨する）。

P3-CODEX-012・P3-GOV-004の全2件をCLOSEした。実装はFocused／Regression／Static／Full Testで検証済み、Existing Testの削除・弱体化は0件。

Remaining Major Finding：本Cycle完了時点で未クローズの重大Findingはない（詳細は7章）。ただし本Document自身も自己申告Closure Candidateであり、次のExact RouteはCodex側の独立再現である。

## 1. P3-CODEX-012・P3-GOV-004 個別CLOSE根拠

### P3-CODEX-012 — Evidence Store Root／Segment Leaf境界の未閉鎖：CLOSED

**Finding A（Rootを安全確認前に`resolve()`していた）**：`LocalJsonlEvidenceStore.__init__()`のCoupled Root（`root: Path`一本）を、`anchor: Path`（Server-owned Trusted Anchor）＋`relative_root: str`（Anchor配下をDirectory-fdで段階的に辿るRelative Path）の2引数へ分離した。`.resolve()`は完全に削除した——`anchor`は唯一の単発絶対Path Open（`os.open(str(anchor), O_DIRECTORY|O_NOFOLLOW)`、Symlinkなら`O_NOFOLLOW`が即座に拒否）としてのみ扱われ、`relative_root`の各Component・`scope`・`segments`は既存の`_open_directory_chain`（`O_NOFOLLOW`＋mkdir-if-missing、1Hopずつ）へそのまま渡す。Runtimeの標準Bindingでは`bootstrap/audit_evidence.py`が`anchor=project_root`・`relative_root="runtime_data/audit_evidence"`をServer側から与える（User入力Pathは一切Authorityにしない）。

**Finding B（Segment LeafのNon-regular／Bounded Read境界が無かった）**：

- `_segment_indices()`（Discovery時点）へ、Segment名Patternに一致するがRegular FileでないEntry（FIFO／Device／Socket等）を`PATH_VIOLATION`で即時拒否するCheckを追加した（Open試行前）。
- `_open_segment_relative()`の全Openへ`O_NONBLOCK`を追加した——FIFOへの差替えがOpen自体を無期限Blockすることを防ぐ（Regular Fileには無害）。
- 新設`_verify_segment_leaf_fd()`が、既にOpen済みの同一FDへ`fstat()`し、Regular File・Owner（`os.getuid()`一致）・Mode（`0o022`非該当）・Link数（`st_nlink <= 1`、Hard Link経由のRoot外Inode共有を拒否）を検証する。Read（`_read_bounded_segment_from_fd`）・Append（`_open_active_segment_with_capacity`）の両方が、実際のRead／Writeへ入る前に必ずこのCheckを経由する。
- Readは同一FDから`MAX_SEGMENT_FILE_BYTES`超過を検知した時点でLoopを打ち切るBounded Readとし、`fstat`直後の値だけでなく、実際に読んだ累計Byte数でも上限超過を判定する——`fstat`後にFileが成長した場合でも上限を超えて読み続けない。
- Appendが上記いずれかのCheckで拒否された場合、Write 0・Receipt 0（例外送出のみ、Byte一切書込み無し）を維持した。

**As-built Contract**（3章参照）：既存Valid Segment・Receipt・Rollover・Partial Tail・Degraded State・Single-worker契約はいずれも変更していない（Regression結果は4章）。

### P3-GOV-004 — 未検証Zero断定の再発：CLOSED

`phase_3_claude_third_rework_complete_candidate_handoff_ja.md` §2の「runtime_data/ 配下の全て（一切のRead/List/Stat/Write/Delete Action無し）」という断定を、新規Append-only Correction Document（`phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md`）で`SELF_REPORTED_UNVERIFIED`へ明示訂正した。既存Handoffは編集・削除していない。Test結果・Repository状態・Git状態・Root外Action・Network・Provider Memory・User Dataのそれぞれについて、`TOOL_LOG_VERIFIED`／`REPOSITORY_STATE_VERIFIED`／`USER_REPORTED`／`SELF_REPORTED_UNVERIFIED`／`NOT_OBSERVED`のClassを個別に割り当てた（詳細は当該File §4）。本Document自身も6章で同じClassificationを適用している。

## 2. Root Anchor／Segment Leaf／Bounded ReadのAs-built Contract

```text
Anchor Open       : os.open(str(anchor), O_DIRECTORY | O_NOFOLLOW)
                     唯一の単発絶対Path Open。.resolve()は使用しない。
                     Symlinkなら即ELOOP -> PATH_VIOLATION。

Relative Root Walk: _open_directory_chain(anchor_fd, [*relative_root_parts, scope, "segments"])
                     各Componentを os.mkdir(part, 0o700, dir_fd=parent_fd)（存在すればFileExistsErrorを無視）
                     + os.open(part, O_DIRECTORY | O_NOFOLLOW, dir_fd=parent_fd) で1Hopずつ。
                     新規作成Directoryは os.fchmod(fd, 0o700)。既存Directoryは fstat で
                     Owner一致 かつ Mode & 0o022 == 0 を要求。

Segment Leaf Open : os.open(name, flags | O_NOFOLLOW | O_NONBLOCK, mode, dir_fd=segments_dir_fd)
                     Read/Append共通。O_NONBLOCKによりFIFO差替えのOpen Blockingを防止。

Segment Leaf Verify: _verify_segment_leaf_fd(fd) が同一fdへ fstat し、
                     stat.S_ISREG かつ st_uid == os.getuid() かつ (st_mode & 0o022) == 0
                     かつ st_nlink <= 1 を要求。Read・Append双方が実データ操作前に必ず通過。

Bounded Read      : _read_bounded_segment_from_fd(fd, MAX_SEGMENT_FILE_BYTES) が
                     Verifyの st_size 事前判定に加え、実読込累計が上限を超えた時点で
                     Loop自体を打ち切る（fstat後の成長にも対応）。
```

## 3. Exact Mutation（本Fourth Rework Cycleで変更したFileのみ）

### 変更（Source）

```text
src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py
src/margpa_runtime_llm/bootstrap/audit_evidence.py
```

`src/margpa_runtime_llm/modules/audit_evidence/ports.py`は変更していない——`EvidenceStorePort` Protocolは`append`/`read_all`/`status`のみを規定し、`LocalJsonlEvidenceStore`のConstructor引数（今回`root`から`anchor`+`relative_root`へ変更）を一切含まないため、Trusted Anchor契約の変更はPort契約に影響しない。「既存Port変更が不要なら変更しない」に従い、意図的に変更対象から除外した。

### 変更（Test）

```text
tests/unit/audit_evidence/test_local_jsonl_store_path_safety.py
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py
tests/integration/audit_evidence/test_evidence_store_contract.py
tests/integration/governance_definitions/test_empty_unknown_invalid_matrix.py
tests/integration/web/test_governance_local_ux_recovery.py
```

後者3件は、Allowed一覧に明示された2File（path_safety／append_recovery）以外で`LocalJsonlEvidenceStore(root=..., scope=...)`を直接呼んでいた既存Call Site——Constructor契約変更に伴い、動作させるために直接必要な最小Call Site更新のみを行った（Assertion・Test Logic自体は変更していない）。

### 新規作成（Docs、Allowedが明示許可するAppend-only／新規Handoff）

```text
docs/project/phases/phase_3/history/index/phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md
docs/project/phases/phase_3/handoffs/phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md（本File）
```

### 明示的にScope外（変更していない）

```text
runtime_data/ 配下の全て（本Cycle中の接触に関するClassificationは6章参照——「一切無し」という断定はしない）
frontend/**、src/margpa_runtime_llm/web/static/**（Generated Static、Frontend Source双方とも本Cycleでは一切触れていない。§5 Mandatory Validationの指示どおりFrontend Buildは再実行していない）
src/margpa_runtime_llm/adapters/governance_definitions/filesystem_provider.py（P3-CODEX-010、既にCLOSE済み、再変更していない）
Git／GitHub Mutation（Commit・Push等）は本Cycle中0件
```

### Test Temporary Root（§5「Test Temporary RootはProject Root内の...」要求への回答）

本Cycleの新規Testはすべて既存Test Harness（pytest標準の`tmp_path` Fixture）だけを使用した。`tmp_path`はpytest自身が生成・管理・削除するHermetic Directoryであり、本Cycle中にClaudeが手動でProject Root内外を問わず新規Test Workspace Directoryを作成したことは無い。したがって、§5が要求する「作成／削除／Postflight不存在」のExact Path報告対象となるArtifactは存在しない——報告すべき作成物が無いこと自体をここに明記する。

## 4. Regression Test名と実測結果

Codex Independent Reviewの§1.4（P3-CODEX-012）が要求したRegression Test（新規7件）：

```text
Finding A（Root/Anchor Symlink）:
  tests/unit/audit_evidence/test_local_jsonl_store_path_safety.py::test_anchor_itself_a_symlink_is_rejected_without_creating_anything_at_the_target
  tests/unit/audit_evidence/test_local_jsonl_store_path_safety.py::test_relative_root_component_that_is_a_symlink_is_rejected_without_creating_anything

Finding B（Segment Leaf Non-regular／Blocking／Mode／Link／Bounded Read）:
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_a_fifo_replacing_a_segment_is_rejected_at_reopen_without_blocking
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_a_fifo_replacing_the_active_segment_makes_append_fail_without_blocking
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_group_writable_segment_is_rejected
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_hard_linked_segment_is_rejected
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_segment_read_is_bounded_even_if_size_grew_after_fstat
```

実測（`pytest -v`個別実行）：**7 passed**（推測値ではなくCommand出力から数えた値）。

既存Regression（第3回Cycleで追加したP3-CODEX-011系5Test）は、Anchor/Relative Root契約変更後も無修正のまま合格し続けている：

```text
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_segment_byte_limit_triggers_rollover_before_writing_and_stays_recoverable
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_event_larger_than_a_fresh_empty_segment_is_capacity_exceeded_not_a_receipt
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_out_of_range_existing_segment_index_is_rejected
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_degraded_highest_segment_at_index_ceiling_fails_closed_instead_of_rolling_over
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_symlinked_scope_component_is_rejected_even_when_its_target_has_a_real_segments_dir
```

いずれも既存Testの削除・弱体化は行っていない。

## 5. Focused／Regression／Static／Full 実測結果

すべてCommand出力から直接数えた値であり、推測値は含まない。

```text
Focused（上記新規7 Testのみ）                                          : 7 passed
tests/unit/audit_evidence/test_local_jsonl_store_path_safety.py（全体） : 8 passed
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py（全体）: 25 passed
tests/integration/audit_evidence/test_evidence_store_contract.py（全体）: 8 passed
tests/integration/governance_definitions/test_empty_unknown_invalid_matrix.py（全体）: 5 passed
tests/integration/web/test_governance_local_ux_recovery.py（全体）      : 2 passed
Backend Full Suite（`pytest -q`）                                      : 907 passed／3 deselected
Ruff Check（Full Repository）                                          : PASS（All checks passed!）
Ruff Format Check（Full Repository）                                   : PASS（237 files already formatted）
Mypy src                                                               : PASS（Success: no issues found in 153 source files）
```

Frontend Typecheck／Lint／Test／Buildは、§5 Mandatory Validationの明示指示（「Frontend Sourceを変更しないため、本CycleでFrontend Buildを再実行しない」）に従い、本Cycleでは実行していない。

## 6. Evidence Source Class別の境界報告

`phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md`で定義したClassをそのまま適用する。

```text
Backend Full Suite 907 passed／3 deselected               : REPOSITORY_STATE_VERIFIED
Ruff／Mypy PASS                                            : REPOSITORY_STATE_VERIFIED
本Cycle中のGit Mutation 0件（HEAD不変、Commit操作痕跡無し）: REPOSITORY_STATE_VERIFIED
Second Auto-Compaction Cycle（P3-GOV-003既存記録）          : USER_REPORTED
runtime_data/ への本Cycle中のAction                         : SELF_REPORTED_UNVERIFIED（「0件」と断定しない）
Project Root外／other/／別Project／Provider Memory／Network/
Secret／External Serviceへの本Cycle中の接触                : SELF_REPORTED_UNVERIFIED
User実Conversation Dataへの本Cycle中の接触                  : SELF_REPORTED_UNVERIFIED
本Cycleの新規Testが`tmp_path`のみを使用する設計であること  : REPOSITORY_STATE_VERIFIED（Test Code自体を今この場で再検査すれば確認可能）
```

## 7. Remaining Major Finding

本Fourth Rework Cycle完了時点で、未クローズの重大Findingは無い。P3-CODEX-012・P3-GOV-004はいずれも本Document §1〜§6で示した根拠によりCLOSEした。

本Documentの著者による自己申告Closure Candidateである点は明示しておく——次のExact Routeは、Codex Independent Re-reviewが本Documentおよび§4のRegression Testを独立再現し、CLOSEを検証することである。

## Next Exact Route

Phase 3-H Closure、User Acceptance、Final Docs、Backup、Git、Phase 4または別作業のいずれへも進まず、ここで停止する。次のExact Routeは、Codex Independent Re-reviewが本Cycleの2件のCLOSEを独立再現・検証することである。
