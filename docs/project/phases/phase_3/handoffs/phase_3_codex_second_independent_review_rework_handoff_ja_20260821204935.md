# Phase 3 Codex Second Independent Review — Exact Rework Handoff

```yaml
document_id: phase_3_codex_second_independent_review_rework_handoff_20260821204935
status: adjust_required
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_001_second_rework
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
created_at: 2026-08-21 20:49:35 JST
predecessor: docs/project/phases/phase_3/handoffs/phase_3_claude_rework_complete_candidate_handoff_ja.md
completion_line: phase_3_claude_second_rework_complete_candidate
git_mutation_authorized: false
phase_3_closure_authorized: false
phase_4_authorized: false
```

## 0. Controller Decision

`ADJUST`。申告されたBackend Full Suite `878 passed／3 deselected`、Ruff、MypyおよびFrontend `117 passed`はCodex独立実行でも再現した。しかし、既存Testが通過する一方で、Compiled Plan Cache、Definition Source Integrity、Local JSONL Evidence StoreおよびEvidenceの検証可能性に重大な未閉鎖経路を確認した。したがって、Claude側の`GO`および「Remaining Major Findingなし」は受理しない。

本Handoffは重大Findingだけを扱う。Deferred事項、UIの軽微な表現、Phase 4事項または新機能を再活性化しない。

## 1. P3-CODEX-006 — Compiled Plan CacheがIR内容変更を識別しない

### Confirmed Finding

`CompilerInput.normalized_ir_refs`はIR ID文字列だけを持ち、`plan_cache_key()`もそのIDだけをHash Inputへ入れている。実際のIR Digest／Source Definition DigestはCompile後のPlanには入るが、Cache Lookup Keyには入らない。

Reference Bundle Adapterの`ir_id`は`<definition_id>-ir`であり、同一Definition IDのSource内容、SectionまたはDigestが変わってもIR IDは変わらない。Codex独立再現では、同一`ir_id`で`old_section`から`new_section`へ内容を変更しても旧PlanがCache Hitした。

さらにArchitecture §8.2は`observe -> off`でPlan CacheをClearすると定めるが、Current RuntimeはSummaryだけをClearし、`CompiledPlanCache.clear()`を呼ばない。この組合せにより、OFFを挟んだ再Observeでも旧Planを再利用し得る。

これは`P3-CMP-004`、`P3-CMP-005`およびPhase 3 Architecture §7.2／§8.2に反する。

### Required Rework

- Compiler Input／Cache Keyへ、順序を固定したIR Digestおよび必要なSource Definition Digestを含める。IR IDだけをIntegrity Identityとして扱わない。
- Plan IDも同じ完全Inputへ追随させる。
- Cache Hit時、Cached Planが要求されたIR／Source Digestと一致することを再検証する。
- `observe -> off`でPlan CacheをClearする。
- 同一IR ID・異なるIR Digest／Source Digestが必ずCache MissするTest、OFF Round-trip後に旧Planを再利用しないTestを追加する。

## 2. P3-CODEX-007 — Definition Sourceの検証結果と実使用Bytesが分離している

### Confirmed Finding

`FilesystemDefinitionProvider.verify_sources()`はSize／Digest／Pathを確認するが、そのVerified BytesをRuntimeへ渡さない。Runtimeは後段で`bootstrap/governance_definitions.py::_make_project_root_reader()`から同じPathを再度読み直す。

後段Readerには次の欠陥がある。

- Read直前のByte上限がない。
- Manifestの`byte_length`／`content_digest_sha512`との再照合がない。
- `resolve()`後のFinal Pathだけを検査し、各Path ComponentのSymlink拒否契約を共有しない。
- Provider検証後、Runtime再Read前にSourceを差し替えると、Manifest Provenanceは旧Digestのまま新しい内容をNormalizeできる。

したがって、P3-CODEX-004のSize／Digest／Symlink Fail-closedは実際のNormalization Inputまで閉じていない。

### Required Rework

- Provider検証とRuntime使用を同一Verified Bytes／Verified Source Recordへ統合する。別Path再ReadをSource of Truthにしない。
- やむを得ず再Readする場合も、Read前Size Gate、全Path Componentの`lstat`相当検査、Non-regular拒否、Read後Length／SHA-512再照合を同一境界で行う。
- Source swap、Size拡大、Digest変更、Intermediate／Final SymlinkおよびMalformed JSONを、未検証内容のNormalizeなしでTyped Failureへ落とすTestを追加する。

## 3. P3-CODEX-008 — Local JSONL StoreのRoot EscapeとFalse Receipt

### Confirmed Finding A：Dangling Symlink Root Escape

`_reject_unsafe_path()`は`path.exists()`がTrueの場合だけ`is_symlink()`を確認する。Targetが未作成のDangling Symlinkは`exists() == false`となるため通過し、その後の`os.open(..., O_CREAT | O_APPEND)`がSymlinkを追跡する。

Codex独立再現では、`segments/segment-00000001.jsonl`をConfigured Root外の未作成Fileへ向けたDangling Symlinkにすると、`append()`がRoot外Fileを実際に作成した。これは`P3-STR-006`違反である。

### Confirmed Finding B：失敗後の成功Receiptが復元不能

Partial Write後に次の`os.write()`が失敗した場合、StoreはActive SegmentをDegradedへ移行せず、同じProcessの次回Appendも同じ破損Tailの後ろへ書く。

Codex独立再現では、1件目をPartial Write＋OSErrorで失敗させた後、2件目のAppendは成功Receiptを返したが、Reopen後に2件目を含めて復元Eventは0件だった。成功ReceiptとDurable Recordが一致しないため、P3-CODEX-005は未閉鎖である。

### Additional Integrity Defects in the Same Boundary

- Receipt IDがSegment Positionだけから作られるため、Segment rollover後に`receipt-000000000000`等が再利用され、独立Identityにならない。
- Reopen／Readは既存Segment数、Segment IndexおよびSegment Byte Sizeを上限確認前に列挙・全読込みする。
- Append Failureは同一ProcessのStore Statusを`degraded`へ変更しない。

### Required Rework

- Danglingを含むSymlinkを`lstat`等で拒否し、可能なPlatformでは`O_NOFOLLOW`／Directory FD等を用いてCheck-to-open Raceも閉じる。Open後のRegular File／Containmentも検証する。
- Partial／Zero／OSError発生後は現SegmentをDegradedとして固定し、既存Bytesを変更せず、次回Appendを新しい安全なSegmentへ送る。次回の成功ReceiptがReopen後もEventへ一致することをTestする。
- Receipt IDをStore／Segment／PositionまたはOpaque UUID等から一意にする。
- Existing Segment Count／Index／Byte Size、Serialized Event SizeおよびEvent内Collectionへ有限上限を適用し、上限前に全FileをMemoryへ読まない。
- Dangling Symlink Escape、Write failure then successful append、Rollover receipt uniqueness、Oversized existing segmentのTestを追加する。

## 4. P3-CODEX-009 — Evidence Write FailureがRuntime Statusへ反映されない

### Confirmed Finding

Architecture §4.5は、Evidence Write FailureでModel生成を止めず、Runtime Statusを`degraded`にして安全なError Codeを返すと定める。Current `EvidenceGenerationObserver`は全例外を`pass`で破棄し、Store／Observer／Governance StatusのいずれにもDegraded状態を反映しない。

Writer Failure非介入は成立するが、Failureが不可視となるため「Evidenceが保存された」と誤認できる。`audit_write_degraded` Event Kindと`EvidenceStoreStatus`が存在しても、Web Runtimeへ接続されていない。

### Required Rework

- Model／SSE非介入を維持しつつ、Observerまたは専用Status PortにProcess-local Degraded State、Safe Reason Codeおよび発生Countを保持する。
- Governance Statusまたは明示的なSafe Status Surfaceから確認可能にする。Raw Exception、Pathまたは内容を露出しない。
- Writer／Store Factory failure後もGeneration／SSEは成功し、StatusだけがDegradedになるTestを追加する。

## 5. P3-GOV-002 — Evidence Timestampと「0件」主張が検証可能性を満たさない

### Confirmed Finding

対象2文書のEvidence Timestampが実時計およびFile mtimeと一致しない。

```text
System Clock at Codex Review:
  2026-08-21 20:49:35 JST

Correction Evidence:
  filename / created_at : 20260821223000 / 2026-08-21 22:30:00 JST
  filesystem mtime      : 2026-08-21 20:21:22 JST

Rework Handoff:
  created_at            : 2026-08-21 23:10:00 JST
  filesystem mtime      : 2026-08-21 20:24:09 JST
```

いずれも作成時刻より約2〜3時間未来のJSTを記録している。TimestampをEvidenceとして扱う以上、推測・丸め・別Timezone値への`JST`付与は許容しない。

また、Correction Evidenceは過去のFalse Completionを訂正した一方、本Reworkについて再び「Root外、Network、Provider Memory等への接触0件」「runtime_data Action 0件」をVerified Resultのように断定する。しかし、Repository状態だけからRoot外Action 0や全Tool Action 0は証明できない。Provider側の完全なAction Logがない場合は`SELF_REPORTED_UNVERIFIED`であり、`VERIFIED_ZERO`ではない。

### Required Rework

- 既存2文書を上書きせず、新規Append-only Correctionを作る。
- 未来Timestampを訂正し、`recorded_at`、`observed_filesystem_mtime`および`claimed_execution_time`を混同しない。実時計を取得できない場合は`unknown`とする。
- Boundary Evidenceを少なくとも`REPOSITORY_VERIFIED`、`TOOL_LOG_VERIFIED`、`SELF_REPORTED_UNVERIFIED`へ分類する。
- `.claude`不存在やGit Mutation等のRepository／Filesystemで確認可能な事項と、Root外／Network／Provider Memoryへの非接触のように現Evidenceでは証明不能な事項を分離する。
- 過去Violation、Hash照合Failure、Recovery Reread `UNVERIFIED`およびLanguage `DRIFT`は消さずに継承する。

## 6. Independent Validation Evidence

Codexが実行した結果：

```text
Focused Governance／Configuration／Audit／Web : 242 passed
Backend Full Suite                            : 878 passed／3 deselected
Ruff Check                                    : PASS
Mypy src                                      : PASS（153 source files）
Frontend Test                                 : 117 passed（16 files）
```

上記Passは事実である。しかし、§1〜§5の経路は既存Testに含まれず、独立再現で失敗したためClosure根拠にはならない。

## 7. Allowed／Forbidden Boundary

### Allowed

- §1〜§4を閉じるために必要なPhase 3 Source／Frontend／TestのExact Path。
- `docs/project/phases/phase_3/history/**`への新規Append-only Rework／Incident／Validation Evidence。
- `docs/project/phases/phase_3/handoffs/phase_3_claude_second_rework_complete_candidate_handoff_ja.md`の新規作成。
- 必要なPhase 3 History Correction。Stable／Roadmapへ直書きしない。

### Forbidden

- `runtime_data/`への全Action。
- Root外、`other/`、別Project、Provider Memory、Network、Secret、External Service。
- Existing Historyの変更・削除。
- Git／GitHub Mutation。
- Phase 4実装、Model Load、AWS。
- Required Findingと無関係なRefactor。
- TestのためのProject実DataまたはProvider-local Artifact生成。

## 8. Mandatory Validation

- §1〜§4の独立再現をRegression Testとして固定する。
- Configuration Control／Governance／Audit Evidence／v1／v2／Persistent／EphemeralのTargeted Regression。
- Public／BasicのGovernance／Evidence Call 0。
- Ruff Format／Check、Mypy declared scope、Frontend Test／Typecheck／Lint／Build。
- Backend Full Suiteを最終1回。
- Existing Test削除・弱体化0。
- 全Testは隔離Rootだけを使用し、実`runtime_data/`へRead／List／Stat／Write／Deleteしない。

## 9. Completion Report

新規`phase_3_claude_second_rework_complete_candidate_handoff_ja.md`へ、日本語で次を記録して停止する。

- P3-CODEX-006〜009、P3-GOV-002の個別CLOSE根拠。
- Exact Mutation。
- Independent Reproductionを固定したTest名と結果。
- Focused／Regression／Static／Full結果。
- Evidence epistemic classification。
- Remaining Major Finding。
- `GO／ADJUST／STOP` Recommendation。

Phase 3-H Closure、User Acceptance、Final Docs、Backup、GitおよびPhase 4開始へ進まない。
