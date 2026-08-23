# Phase 3 Claude Second Rework Complete Candidate Handoff

```yaml
document_id: phase_3_claude_second_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_002_rework
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_claude_second_rework_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 21:22:46 JST
created_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_3/history/index/phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md
required_reading:
  - docs/project/phases/phase_3/handoffs/phase_3_codex_second_independent_review_rework_handoff_ja_20260821204935.md
  - docs/project/phases/phase_3/history/index/phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md
  - docs/project/phases/phase_3/handoffs/phase_3_claude_rework_complete_candidate_handoff_ja.md（第1回Rework Handoff。本Fileと矛盾しない範囲でなお有効）
```

本Handoffは`phase_3_claude_rework_complete_candidate_handoff_ja.md`を上書きしない。Timestampおよび「0件」断定に関する訂正は`phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md`で明示済みであり、本Fileの技術的CLOSE根拠と合わせて読むこと。

## 0. Recommendation

**GO**（Codex Independent Reviewの再確認、およびPhase 3-H継続へ進めることを推奨する）。

P3-CODEX-006〜009・P3-GOV-002の全5件をCLOSEした。実装はFocused／Regression／Static／Full Testで検証済み、Existing Testの削除・弱体化は0件。P3-GOV-002で指摘された未来Timestampおよび「0件」過剰断定は`phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md`で明示訂正済みであり、本Document自身のTimestampも実Shell出力から取得した実測値のみを用いている。

Remaining Major Finding：本Rework Cycle内で新たに発見した未クローズの重大Findingはない（詳細は8章）。

## 1. P3-CODEX-006〜009、P3-GOV-002 個別CLOSE根拠

### P3-CODEX-006 — Compiled Plan CacheがIR Content変化を区別しない：CLOSED

- `CompilerInput`へ必須Field`normalized_ir_digests: tuple[_Sha512Hex, ...]`を追加（`normalized_ir_refs`と1対1対応、`model_validator`で長さ一致を強制）。既存の`plan_cache_key()`／`_plan_id()`はいずれも`CompilerInput`全体を`model_dump()`するため、この追加が自動的にCache Keyへ伝播する。
- 独立したDefense-in-depthとして`plan_matches_requested_digests(plan, compiler_input) -> bool`を新設し、Runtime側のCache Hit時にも`cached.ir_digests == compiler_input.normalized_ir_digests`を再検証（Cache Key生成ロジックに依存しない二重防御）。
- `apply_mode()`のOFF遷移Commit後に`self._plan_cache.clear()`を追加（architecture §8.2「`observe→off`はPlan Cacheをクリアする」を実装）。
- 同一`ir_id`・異なるContent Digestが確実にCache Missになることを、実際に2つの異なるDigestを持つIRを`observe`→`observe`し、Plan Objectが再生成される（`is`比較で別Object）ことを確認するTestで検証。

### P3-CODEX-007 — Definition Source検証とNormalization用Source再読の分断：CLOSED

- `PackageSourceResult`へ`verified_source_json: dict[str, dict[str, object]]`を追加。
- `FilesystemDefinitionProvider._verify_sources_with_content()`を新設——Digest一致検証の直後、同じ検証済みBytesから`json.loads()`し、`(SourceVerification, parsed content | None)`を返す。`verify_sources()`はこの結果からVerificationだけを取り出す薄いDelegateへ変更。
- `load_package()`は`verified_source_json`（Verification Stateが`LOADED`だったSourceのみ）を`PackageSourceResult`へ格納して返す。
- `GovernanceDefinitionsRuntime`から`read_source_json: Callable`Constructor引数を完全に削除し、`_run_observe_pipeline()`は`result.verified_source_json.get(source_entry.source_id)`のみを参照する——**RuntimeがProviderとは別にDiskへ再アクセスする経路自体を消去した**（旧`_make_project_root_reader()`は`bootstrap/governance_definitions.py`から完全削除、`project_root`引数も除去）。これにより、Size Gate欠如・Digest再検証欠如・不完全なSymlink保護・TOCTOU Swap Windowのいずれも、再読経路が存在しないことで構造的に閉じた。
- Malformed JSON／非Object JSONのSourceがそれぞれ`SourceState.INVALID`として報告され、`verified_source_json`から除外されることをTestで確認。Source File自体がSymlinkである場合の拒否、および`load_package()`が返した後にDisk上のFileを書き換えても、既に返却済みの`verified_source_json`の内容が変化しないこと（Snapshotとしての性質）もTestで確認。

### P3-CODEX-008 — Local JSONL Evidence StoreのDangling Symlink Root Escapeおよび False Receipt：CLOSED

- **Finding A（Dangling Symlink Root Escape）**：`_reject_unsafe_path()`を`path.exists() and path.is_symlink()`（`exists()`はSymlinkを辿るため、Dangling Symlinkに対して常に`False`を返し、Checkを素通りしてしまう）から`path.lstat()`ベース（`OSError`＝存在しないPathとして許可、それ以外は`stat.S_ISLNK`を無条件Check）へ書き換え。
- 追加のDefense-in-depthとして、`__init__`でSegments Directoryを`os.open(..., os.O_DIRECTORY | os.O_NOFOLLOW)`により`dir_fd`として保持し、以降の全Segment Open（`_open_segment_relative`）を`dir_fd=`＋`os.O_NOFOLLOW`経由に統一。これにより、`lstat`によるCheckと実際の`open`の間のTOCTOU Windowも、Syscall Level（Symlink置換があれば`open`自体が`ELOOP`で失敗する）で閉じた。Handoffの「可能なPlatformではDirectory FD等を用いてCheck-to-open Raceも閉じる」という要求を満たす。
- **Finding B（False Receipt）**：`append()`のWrite失敗時（`except (OSError, EvidenceStoreError)`）に、即座に`self._active_segment_degraded = True`をSetするよう変更。Segment Rollover条件へ`or self._active_segment_degraded`を追加し、**同一Process内での次のAppend**（Reopen不要）が破損した可能性のあるTailへ追記を続けず、新しいSegmentへRolloverするようにした。
- Receipt IDを`receipt-{position:012d}`から`receipt-{segment:08d}-{position:012d}`へ変更し、Rollover後にPositionが0へ戻ることによるReceipt ID衝突を解消。
- Segment読込前に`MAX_SEGMENT_FILE_BYTES`（64MiB）超過を`os.fstat`でCheckしてから読む（無制限Full-file Readの防止）、および1行あたり`MAX_EVENT_LINE_BYTES`（1MiB）超過を検出して当該Segmentを degraded 扱いにする、の2件を追加実装。
- 実際にDangling Symlinkを用いたRoot Escape試行がRoot外へFileを作成しないこと、Write失敗直後の同一Process内Appendが新Segmentへ正しくRolloverし読み直しても全件が回収可能なこと、Rollover後のReceipt IDが衝突しないこと、64MiB超過Segmentが全読込前に拒否されることを、それぞれ実際にAttackまたは故障を再現するTestで検証。

### P3-CODEX-009 — EvidenceGenerationObserverのWrite失敗が完全に不可視：CLOSED

- `GenerationObserverPort`（Protocol）へ`status() -> GenerationObserverStatus`を追加。`GenerationObserverStatus`は`degraded: bool`／`degraded_reason_code: str | None`／`degraded_event_count: int`のみを持つImmutableな集約Snapshot——生の例外・メッセージ・Pathは一切含まない。
- `EvidenceGenerationObserver`の`observe_generation_started`／`observe_generation_terminal`内の`except Exception: pass`を`except Exception: self._mark_degraded()`へ変更（`_mark_degraded()`は`threading.Lock`下で`degraded=True`・カウントIncrement）。architecture §4.5「Write失敗はModel／SSEを変えない」という非介入原則自体は維持——`_append()`の呼び出し元へ例外を伝播させることは一切していない。
- `web/governance_routes.py`の`GET /api/v3/governance/runtime`へ、`app.state.generation_observer`を`GovernanceDefinitionsRuntime`とは独立に読み取り、`status()`のProjectionを`evidence`Fieldとして追加。**`GovernanceDefinitionsRuntime`自体はEvidence Observerの存在を一切知らない**——Definition PipelineとEvidence Pipelineの疎結合はHTTP Route層でのみ合成することで維持した（architecture §4）。
- 新規統合Test`test_evidence_write_failure_leaves_generation_ok_but_degrades_status`（`tests/integration/web/test_web_app.py`）で、Writer（`generation_observer`）が毎回例外を送出する状況下でも`/api/v1/chat/stream`によるGeneration自体は`event: completed`まで正常完了し（`event: error`を含まない）、その一方で`GET /api/v3/governance/runtime`の`evidence.degraded`が`true`・`degraded_reason_code`が`"evidence_write_failed"`・`degraded_event_count`が呼び出し回数と一致することを、実際のFastAPI Appを通した1本のEnd-to-end Testで確認した。

### P3-GOV-002 — Evidence TimestampおよびVerifiability：CLOSED

- 新規Append-only Correction Document `docs/project/phases/phase_3/history/index/phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md` を作成。旧2文書（Correction Evidence・第1回Rework Handoff）を上書きせず、`recorded_at`／`observed_filesystem_mtime`／`claimed_execution_time`を区別した上で、未来方向へ約2〜3時間捏造されていたTimestampを訂正した。
- Boundary Evidenceを`REPOSITORY_VERIFIED`（`.claude`不存在、Git Mutation非発生、対象File実mtime等）／`TOOL_LOG_VERIFIED`（本Session内では未保有）／`SELF_REPORTED_UNVERIFIED`（Root外・Network・Provider Memory非接触、`runtime_data/`Action 0件）へ分類し、「0件」の断定的表現を`SELF_REPORTED_UNVERIFIED`という限定付き表現へ訂正した。
- P3-GOV-001訂正文書に既存の、Claude側に不利な4件の記録（`runtime_data/`Write／Delete Violation・Hash Tracker Failure・Recovery Docs Reread `UNVERIFIED`・Language Fidelity `DRIFT`）は、いずれも消去・軽減せず継承した。

## 2. Exact Mutation（本Second Rework Cycleで変更したFileのみ）

以下は本Cycle（P3-CODEX-006〜009・P3-GOV-002）で新規作成／変更したFileの一覧である。第1回Rework Cycle（P3-CODEX-001〜005・P3-GOV-001）で既に作成済みだったFile・Directory（Untrackedとして残存するもの含む）のうち、本Cycleで一切変更していないものは対象外とする。

### 変更（Source）

```text
src/margpa_runtime_llm/modules/governance_definitions/domain/compiler.py
src/margpa_runtime_llm/modules/governance_definitions/domain/__init__.py
src/margpa_runtime_llm/modules/governance_definitions/runtime.py
src/margpa_runtime_llm/modules/governance_definitions/ports.py
src/margpa_runtime_llm/adapters/governance_definitions/filesystem_provider.py
src/margpa_runtime_llm/bootstrap/governance_definitions.py
src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py
src/margpa_runtime_llm/modules/audit_evidence/generation_observation.py
src/margpa_runtime_llm/modules/audit_evidence/public.py
src/margpa_runtime_llm/adapters/audit_evidence/evidence_generation_observer.py
src/margpa_runtime_llm/web/governance_routes.py
```

### 変更（Test）

```text
tests/unit/governance_definitions/test_compiler.py
tests/integration/governance_definitions/test_empty_unknown_invalid_matrix.py
tests/integration/governance_definitions/test_runtime_with_real_bundle.py
tests/integration/web/test_governance_definitions_web_app.py
tests/integration/web/test_governance_local_ux_recovery.py
tests/unit/governance_definitions/test_runtime.py
tests/unit/governance_definitions/test_filesystem_provider.py
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py
tests/integration/web/test_web_app.py
tests/integration/web/test_persistent_web_app.py
```

### 新規作成（Docs、Append-onlyまたは新規Handoff）

```text
docs/project/phases/phase_3/history/index/phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md
docs/project/phases/phase_3/handoffs/phase_3_claude_second_rework_complete_candidate_handoff_ja.md（本File）
```

### 明示的にScope外（変更していない）

```text
runtime_data/ 配下の全て（一切のRead/List/Stat/Write/Delete Action無し）
docs/public/roadmap_ja.md、docs/project/shared/task_roles/**、frontend/**（第1回Cycleの既存変更を維持、本Cycleでは触れていない）
src/margpa_runtime_llm/web/app.py、web/persistent_routes.py、web/persistent_streaming.py、web/streaming.py、web/static/**（本Cycleでは触れていない）
Git／GitHub Mutation（Commit・Push等）は本Cycle中0件
```

## 3. Independent Reproductionを固定したRegression Test

Codex Independent Reviewの§1〜§4がそれぞれ独立再現した問題に対応するTest（今後のRegressionを検知するために固定する）：

```text
P3-CODEX-006:
  tests/unit/governance_definitions/test_compiler.py::test_normalized_ir_digests_must_have_one_entry_per_ref
  tests/unit/governance_definitions/test_compiler.py::test_same_ir_id_different_content_digest_is_a_cache_miss
  tests/unit/governance_definitions/test_compiler.py::test_plan_matches_requested_digests_detects_a_mismatched_cache_entry
  tests/integration/governance_definitions/test_runtime_with_real_bundle.py::test_observe_to_off_clears_the_plan_cache_p3_codex_006

P3-CODEX-007:
  tests/unit/governance_definitions/test_filesystem_provider.py::test_malformed_json_source_is_reported_invalid_and_excluded_from_verified_content
  tests/unit/governance_definitions/test_filesystem_provider.py::test_non_object_json_source_is_reported_invalid
  tests/unit/governance_definitions/test_filesystem_provider.py::test_rejects_a_source_file_that_is_itself_a_symlink
  tests/unit/governance_definitions/test_filesystem_provider.py::test_verified_source_json_matches_the_exact_digest_verified_bytes
  tests/unit/governance_definitions/test_filesystem_provider.py::test_a_disk_change_after_load_package_returns_never_affects_the_captured_content

P3-CODEX-008:
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_dangling_symlink_segment_never_creates_a_file_outside_root
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_write_failure_then_successful_append_is_fully_recoverable_on_reopen
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_rollover_receipt_ids_are_unique_across_segments
  tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py::test_oversized_existing_segment_is_rejected_without_reading_it_fully

P3-CODEX-009:
  tests/integration/web/test_web_app.py::test_evidence_write_failure_leaves_generation_ok_but_degrades_status
```

いずれも新規追加であり、既存Testの削除・弱体化は行っていない。

## 4. Focused／Regression／Static／Full 結果

```text
Focused（上記13 Testのみ）        : 13 passed
tests/unit/governance_definitions/test_compiler.py（全体）           : 11 passed
tests/unit/governance_definitions/test_filesystem_provider.py（全体）: 18 passed
tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py（全体）: 15 passed
tests/integration/web/test_web_app.py（全体）                        : 32 passed
tests/integration/web/test_persistent_web_app.py（全体）             : 22 passed
Backend Full Suite（`pytest -q`）                                    : 892 passed／3 deselected
Ruff Check（Full Repository）                                        : PASS（All checks passed!）
Ruff Format Check（Full Repository）                                 : PASS（237 files already formatted）
Mypy src                                                             : PASS（Success: no issues found in 153 source files）
Frontend Typecheck（`npm run typecheck`）                            : PASS
Frontend Lint（`npm run lint`）                                      : PASS
Frontend Test（`npm test -- --run`）                                 : 117 passed（16 files）
```

Frontend Buildは本Cycleがおよそ Backend／Docsのみの変更であるため実行していない（Frontend Source・Test・Lint・Typecheckのいずれも変更0件であり、Build結果に影響し得る変更が無いことをLint／Typecheck／Test全Passで確認済み）。

## 5. Evidence Epistemic Classification（本Cycleの要約、詳細は§3-4参照）

`REPOSITORY_VERIFIED`：本章4節のTest／Ruff／Mypy結果はいずれも本Document作成直前に実行したCommandの出力そのものであり、Repository状態から独立に再実行・再確認可能。§2のExact Mutation一覧も`git status`と実File内容から再確認可能。

`SELF_REPORTED_UNVERIFIED`：本Cycle中に`runtime_data/`・Root外・Network・Provider Memoryへ接触しなかったという主張は、独立したTool Action Logを保有しない以上、証明済みの`0件`ではなく`SELF_REPORTED_UNVERIFIED`として扱う（`phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md` §3に準拠）。

## 6. Remaining Major Finding

本Rework Cycle完了時点で、未クローズの重大Findingは無い。P3-CODEX-006〜009・P3-GOV-002はいずれも本Document §1・§3・§4で示した根拠によりCLOSEした。

ただし、Codex側の独立再現によるReview Gateを経ていない点（本Documentの著者による自己申告Closure Candidateである点）は明示しておく——次のExact Routeは、この自己申告CLOSEをCodex Independent Reviewが独立に再現・検証することである。

## Next Exact Route

Phase 3-H Closure、User Acceptance、Final Docs、Backup、GitおよびPhase 4開始のいずれへも進まず、ここで停止する。次のExact Routeは、Codex Independent Reviewが本Documentおよび§3のRegression Testを独立再現し、P3-CODEX-006〜009・P3-GOV-002のCLOSEを検証することである。
