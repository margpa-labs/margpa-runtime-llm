# Phase 1／Phase 1-ex Lossless Reconstruction Record

```yaml
document_id: phase_1_and_phase_1_ex_lossless_reconstruction
phase: phase_1_ex
state_at: 2026-07-27 10:28:50 JST
source_frozen_at: 2026-07-27 10:15:44 JST
status: completed
owner: 設計統括者役
language: ja
operation_type: phase_level_lossless_compilation
```

## 1. Purpose

Phase 1とPhase 1-exについて、Category別またはRaw Historyへ分散していたDocumentationを、Phase単位の単一Lossless Compilationから再構築可能にした。

- Phase 1:
  - 完了済みPhaseのFrozen Compilation
- Phase 1-ex:
  - 進行中PhaseのInterim／Current-to-date Compilation

どちらもSource本文を要約、意訳、再解釈または意味変更せず、Path、Byte SizeおよびSHA-512付きで直接収録する。

## 2. Format

各Entryは次のBegin Markerを持つ。

```text
<!-- MARGPA_LOSSLESS_ENTRY_BEGIN {"index":...,"path":"...","size_bytes":...,"sha512":"..."} -->
```

Marker直後の正確な`size_bytes`だけがSource本文である。Source本文後のContainer改行とEND MarkerはSourceに含めない。

```text
<!-- MARGPA_LOSSLESS_ENTRY_END index=... -->
```

VerificationはCompilationからSource本文をByte単位で再抽出し、Manifest上のSizeとSHA-512へ照合する。

## 3. Phase 1 Complete Lossless

### 3.1 Stable Artifacts

```text
docs/project/phases/phase_1/lossless/phase_1_lossless_ja.md
docs/project/phases/phase_1/lossless/phase_1_lossless_manifest.json
```

### 3.2 History Snapshots

```text
docs/project/phases/phase_1/history/lossless/phase_1_lossless_phase_1_ja_20260727101544.md
docs/project/phases/phase_1/history/lossless/phase_1_lossless_manifest_phase_1_20260727101544.json
```

### 3.3 Integrity

```text
Phase State          : complete_accepted
Status               : frozen
Source Count         : 316
Source Bytes         : 5,206,317
Compilation Bytes    : 5,322,615
Source Set SHA-512   : 52958a309007df372e0d31f91f576ecdb3f81bb44c632fb53561068cfe9e3a4a5073bb4d8a229b20a5dbfc87212950b2a55e45740dce350ba3a88789f7cc5165
Manifest SHA-512     : 4caec1970a190010503dfb1a6caea5075a0c9779352ee6c0129af1007f78bb696990c5d6fab5dba174e64fbca6210132723cf8dbe10c7bdc4f03c1ea95d8d543
Compilation SHA-512  : f0e5875b28d06425a9a5eb31c2004c976738f0236fc45acfd7712d6673d2d60f449f44bc6193643220590644369762bc2f2c9cf2aabf90bf0577084366793705
Verified Entries     : 316／316
Verified Source Bytes: 5,206,317
```

### 3.4 Source Composition

- Raw History Source:
  - 307件
- Existing Category Compilation:
  - 8件
- Source Freeze時のPhase Index:
  - 1件
- Total:
  - 316件

既存Category CompilationをRaw Historyの代替として捨てず、両方をPhase-level Masterへ含めた。

## 4. Phase 1-ex Interim Lossless

### 4.1 Stable Artifacts

```text
docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_ja.md
docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_manifest.json
```

### 4.2 History Snapshots

```text
docs/project/phases/phase_1_ex/history/lossless/phase_1_ex_interim_lossless_phase_1_ex_ja_20260727101544.md
docs/project/phases/phase_1_ex/history/lossless/phase_1_ex_interim_lossless_manifest_phase_1_ex_20260727101544.json
```

### 4.3 Integrity

```text
Phase State          : in_progress
Status               : interim_current_to_date
Source Count         : 145
Source Bytes         : 3,926,195
Compilation Bytes    : 3,982,558
Source Set SHA-512   : 0220358633c705e4c936455c613804bff6fff6ab90d9294318f0853278ae4154c6d088252650fe460ac44a0064f2c995a825c8649f642b9e206d1d29ebaef89b
Manifest SHA-512     : 844e8407811acbecedf990eb74092743b8eab3d13eb00ae79620a21f6e299f15910a92a20dbe74cd225c32a85f4207500dfa9124735cb1024ab97ce85c472a1f
Compilation SHA-512  : 1dfc8fc71eea947e61c75502cadc31b5d993f4a9834b23571cacf65aacf99a11913bb3333bdcb26dfb55a72a2f5120f623fb925b282cea2968fe026ab0cfc38c
Verified Entries     : 145／145
Verified Source Bytes: 3,926,195
```

### 4.4 Interim Boundary

本CompilationはPhase 1-ex完了版ではない。

Source Freeze後に作られた次のArtifactは含まない。

- Lossless Compilation自身
- Lossless Manifest自身
- Lossless History Snapshot
- 本Verification Record
- Phase Index更新前後Snapshot
- Documentation Index Snapshot
- Shared／Public／README／Legal等の後続成果物

これは自己参照を防ぐためのContainer境界である。Phase 1-ex完了時に、その後の全Sourceを含めた正式完了版を再生成する。

## 5. Exclusion

Source Setから次だけを除外した。

```text
.DS_Store
lossless/**
source_frozen_at後に作成されたArtifact
```

`.DS_Store`はDocumentationではなくOS Metadataである。公開前Sanitation対象とし、Lossless Sourceとして収録しない。

対象Extension：

```text
.md
.json
```

## 6. Verification Result

| Phase | Manifest Entries | Extracted Entries | Size Match | SHA-512 Match | Stable／History Match |
|---|---:|---:|---|---|---|
| Phase 1 | 316 | 316 | PASS | 316／316 PASS | PASS |
| Phase 1-ex | 145 | 145 | PASS | 145／145 PASS | PASS |

追加確認：

- Source削除:
  - なし
- Source移動:
  - なし
- Source本文変更:
  - なし
- Existing Category Compilation削除:
  - なし
- Raw History削除:
  - なし
- Git操作:
  - なし

## 7. Phase 1 Index

- [Stable Phase 1 Index](../../../phase_1/phase_index_ja.md)
- [Before](../../../phase_1/history/operations/phase_index_before_phase_1_master_lossless_20260727101749.md)
- [After](../../../phase_1/history/operations/phase_index_after_phase_1_master_lossless_20260727101902.md)
- [Documentation Index Snapshot](../../../phase_1/history/documentation_index_20260727101902.md)

## 8. Next

1. Phase 1-ex IndexへInterim Losslessを登録する。
2. Shared文書群を累積完全版として再構築する。
3. Public／README／Legal完成後にPhase 1-ex Source Setを再Freezeする。
4. Phase 1-ex完了時に正式なComplete Lossless Compilationを生成する。
