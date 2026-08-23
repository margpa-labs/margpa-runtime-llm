# Phase 3 Codex Fourth Independent Review — Exact Rework Handoff

```yaml
document_id: phase_3_codex_fourth_independent_review_rework_handoff_20260821223200
status: adjust_required
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_004_fourth_rework
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-21 22:32:00 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_3/handoffs/phase_3_claude_third_rework_complete_candidate_handoff_ja.md
completion_line: phase_3_claude_fourth_rework_complete_candidate
git_mutation_authorized: false
phase_3_closure_authorized: false
phase_4_authorized: false
```

## 0. Controller Decision

`ADJUST`。

第三Reworkの次の3件はCLOSE可能と判定する。

- `P3-CODEX-010`：Definition Source／Manifestの同一FD Verified Read。
- 前回指定した`P3-CODEX-011`のSegment容量、Index上限およびScope Component Symlink修正。
- `P3-GOV-003`：Auto-Compaction Cycle 2のFailure／Drift／Unverified分類。

一方、同じFrozen要件`P3-STR-006`に、Evidence Store RootとSegment Leafの未閉鎖経路が残る。また、既に確定したEvidence Classificationを第三Rework Handoffが再び破っている。

本Handoffは`P3-CODEX-012`と`P3-GOV-004`の2件だけを扱う。CLOSE済みFinding、Phase 4、Deferred事項、新機能またはUI改善を再活性化してはならない。

## 1. P3-CODEX-012 — Evidence Store Root／Segment Leaf境界が未閉鎖

### 1.1 Confirmed Finding A：Rootを安全確認前に`resolve()`している

`LocalJsonlEvidenceStore.__init__()`は、Directory-fd Chainへ入る前に次を行う。

```python
resolved_root = root.expanduser().resolve()
```

この時点で、Configured Rootまたは既存親ComponentがSymlinkなら、そのTargetへ追従したPathが新しいTrusted Rootとして扱われる。後続の`O_NOFOLLOW` Chainは、既に解決済みのTarget配下だけを検査するため、元のConfigured RootからのSymlink Escapeを検知できない。

これは次に反する。

- `P3-STR-006`：Symlink Escape／Root外参照を拒否。
- Root以下の全ComponentをDirectory-fd Chainで検証するという第三Reworkの主張。

### 1.2 Confirmed Finding B：Segment LeafのNon-regular／Bounded Read境界がない

`_segment_indices()`はSymlinkだけを拒否し、Manifest形式に一致するFIFO、Device、Socket等のNon-regular Leafを拒否しない。

`_read_segment_relative()`はLeafをBlocking Openでき、事前`fstat().st_size`確認後にEOFまで無制限に読む。したがって次が成立する。

- FIFO等でOpenまたはReadが無期限Blockする。
- `fstat`後に成長するFileを`MAX_SEGMENT_FILE_BYTES`超過まで読み続ける。
- Non-regular LeafをEvidence Segmentとして扱う。

Append側もOpen後にRegular File、Owner／Modeおよび外部Inode共有を検証しないため、Non-regular LeafまたはHard Linkされた外部FileへWriteし得る。

### 1.3 Required Rework

実装方式をPackage名や固定PathへHard-codeしてはならない。次の保証を満たす最小設計を選ぶ。

1. Evidence Rootを`resolve()`でTargetへ追従してからTrusted Anchor化しない。
2. Server-owned Trusted Anchor＋Relative Root、または同等のRoot FD契約を使用し、Configured Rootまでの各Componentを`dir_fd`／`openat`相当＋`O_NOFOLLOW`で段階的にOpen／必要時Createする。
3. Runtimeの標準Bindingでは、Trusted AnchorをProject Root、Relative Rootを`runtime_data/audit_evidence`相当としてServer側から与える。User入力PathをAuthorityにしない。
4. Root、Scope、`segments`およびSegment Leafのいずれも、Path文字列を`resolve()`して安全判定を迂回しない。
5. Segment Leafは`O_NOFOLLOW`に加えてBlockingを防ぐFlagを使用し、同じOpen済みFDへ`fstat()`を行う。
6. Segment LeafはRegular File、期待Owner、安全なModeおよび必要なLink方針を満たす場合だけRead／Appendする。Hard LinkでRoot外Inodeを共有する経路を許可しない。
7. Readは同じFDから`MAX_SEGMENT_FILE_BYTES + 1`までのBounded Readとし、`fstat`後の成長も上限超過で停止する。
8. Appendは同じFDのIdentity／Type／Mode／現在Sizeを確認後に行い、拒否時はWrite 0／Receipt 0とする。
9. 既存Valid Segment、Receipt、Rollover、Partial Tail、Degraded StateおよびSingle-worker契約を壊さない。

### 1.4 Required Regression

最低限、次をRegression Testとして固定する。

- Existing Configured Root自体がSymlinkの場合、Target側へDirectory／Fileを作らず`PATH_VIOLATION`。
- Configured Rootまでの既存親ComponentがSymlinkの場合も同様。
- Segment名に一致するFIFOを置いたReopen／ReadがBlockせずTyped Reject。
- Segment名に一致するFIFOを置いたAppendがBlockせずWrite 0／Receipt 0。
- `fstat`後にSize上限を超えるReadを模擬し、Bounded Reject。
- Unsafe Mode／OwnerまたはHard Link Segmentを採用しない。
- 正常な新規RootのLazy Creation、正常Append／Reopen／Rolloverは従来どおりPASS。

Testは隔離されたProject Root内Test Workspaceまたは既存Test Harnessだけを使用し、User実`runtime_data/`へRead／List／Stat／Write／Deleteしない。

## 2. P3-GOV-004 — 未検証Zero断定の再発

第三Rework Handoffは、`runtime_data/`について次を事実として断定した。

```text
runtime_data/ 配下の全て（一切のRead/List/Stat/Write/Delete Action無し）
```

完全なFilesystem Action Logを保有しない場合、この主張は既存Correctionの定義どおり`SELF_REPORTED_UNVERIFIED`である。Repository差分、現在のFile状態またはClaudeの自己認識だけを、過去の全Actionが0だった証明へ昇格させてはならない。

### Required Correction

- Existing Third Rework Handoffを編集・削除しない。
- 新規Append-only Correction Evidenceを作り、上記文言を`SELF_REPORTED_UNVERIFIED`として明示的に上書き訂正する。
- Test結果、Repository状態、Git状態、Root外Action、Network、Provider MemoryおよびUser Dataについて、Evidence Source Classを分離する。
- 完全なAction Logが無い対象に`VERIFIED_ZERO`、断定的`0件`または「一切無し」を使わない。
- Fourth Rework Completion Handoff自身にも同じ分類を適用する。

推奨Classは既存どおり次を使用する。

```text
TOOL_LOG_VERIFIED
REPOSITORY_STATE_VERIFIED
USER_REPORTED
SELF_REPORTED_UNVERIFIED
NOT_OBSERVED
```

## 3. Allowed Mutation

- `src/margpa_runtime_llm/adapters/audit_evidence/local_jsonl_store.py`
- Trusted Anchor／Root FD契約に直接必要な、次の最小既存Call Site／Port／Bootstrap変更。
  - `src/margpa_runtime_llm/bootstrap/audit_evidence.py`
  - `src/margpa_runtime_llm/modules/audit_evidence/ports.py`
  - 同契約の最小Export。
- `tests/unit/audit_evidence/test_local_jsonl_store_path_safety.py`
- `tests/unit/audit_evidence/test_local_jsonl_store_append_recovery.py`
- 同Boundaryへ直接必要な新規Focused Test File。
- Trusted Anchor変更に直接必要な既存Audit Evidence Integration Testの最小更新。
- `docs/project/phases/phase_3/history/**`への新規Append-only Correction／Rework／Validation Evidence。
- `docs/project/phases/phase_3/handoffs/phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md`の新規作成。

既存Port変更が不要なら変更しない。必要なFileだけを動的に選び、Allowed一覧を機械的に全変更しない。

## 4. Forbidden

- `runtime_data/`へのRead／List／Stat／Write／Delete。
- Project Root外、`other/`、別Project、Provider Memory、Network、Secret、External Service。
- Existing History／Existing Handoffの変更・削除。
- Git／GitHub Mutation。
- Stable Docs、Roadmap、Frontend、Generated Static、Definition Provider、CLOSE済みFindingの再変更。
- Phase 3-H Closure、Phase 4、Model Download／Load、AWS。
- Required Findingと無関係なRefactorまたは新機能。
- TestやValidationを理由にProject Root外Temporary Artifactを作成すること。

## 5. Mandatory Validation

- `P3-CODEX-012`の全Regressionを固定する。
- Local JSONL StoreのFocused／Contract／Integration Test。
- Audit Evidence／Governance Definition／Webの既存Regression。
- Backend Full Suiteを最終1回。
- Ruff Format／Check、Mypy `src`。
- Existing Test削除・弱体化0。
- Frontend Sourceを変更しないため、本CycleでFrontend Buildを再実行しない。既存Generated Staticを再生成しない。
- Test CountはCommand出力から数え、推測しない。
- Test Temporary RootはProject Root内の、本Work Unit専用に新規作成した一意の隔離Directoryだけを使用し、User実Dataと混同しない。本Handoffは、その専用Directory内に本Cycleが新規作成したTest Artifactだけについて、Validation完了後の削除を許可する。既存Path、親Directory、別Task ArtifactまたはTarget不明の削除は禁止し、Exact Path／作成／削除／Postflight不存在をCompletion Handoffへ記録する。

## 6. Completion Report／Stop Boundary

新規`docs/project/phases/phase_3/handoffs/phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md`へ、日本語で次を記録して停止する。

- `P3-CODEX-012`／`P3-GOV-004`の個別CLOSE根拠。
- Root Anchor／Segment Leaf／Bounded ReadのAs-built Contract。
- Exact Mutation。
- Regression Test名と実測結果。
- Focused／Regression／Static／Fullの実測結果。
- Evidence Source Class別の境界報告。
- Remaining Major Finding。
- `GO／ADJUST／STOP` Recommendation。

Phase 3-H Closure、User Acceptance、Final Docs、Backup、Git、Phase 4または別作業へ進まず、Codex Independent Re-reviewを待つ。
