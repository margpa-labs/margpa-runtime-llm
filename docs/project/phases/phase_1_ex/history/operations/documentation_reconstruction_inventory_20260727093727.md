# Documentation Reconstruction Source Inventory

```yaml
document_id: documentation_reconstruction_source_inventory
phase: phase_1_ex
status: frozen_source_snapshot
language: ja
created_at: 2026-07-27 09:37:27 JST
owner: 設計統括者役
purpose: canonical_public_lossless_reconstruction
```

## 1. 対象

Canonical、Phase 1／Phase 1-ex Lossless再整理、Shared、Public、READMEおよび公開Metadataを再構築する前に、現時点のSource Setを固定した。

対象Root：

```text
docs/
assets/images/
```

除外：

```text
**/.DS_Store
Machine-readable Manifest自身
```

## 2. Machine-readable Manifest

[documentation_reconstruction_source_inventory_20260727093727.json](documentation_reconstruction_source_inventory_20260727093727.json)

```text
Files             : 499
Docs Files        : 493
Markdown          : 489
JSON              : 4
Demo PNG          : 6
Manifest Entries  : 499
Entry Verification: 499／499 PASS
```

Entry List Canonical SHA-512：

```text
1d1dd20dafc6184339bb6ce709269d6c8e058ec97aba982a1ab0554c4754a7148b1b5fc9cfd362891480eafd723f909792393e3ebd094d04fdd349cbfe46e22c
```

Manifest File SHA-512：

```text
c83b92063db185324feb1b4a907b79ddc72dac7eb0b17948fab77c8ba3dea5363fef6a06ee7a73439002aa1994c0a1a2e8a672d50824ab768b186a14d64aa513
```

## 3. Documentation Boundary

```text
Current／History : 15
Phase 1          : 316
Phase 1-ex       : 135
Shared／History  : 25
Public／History  : 2
```

上記Countは`.DS_Store`を除く。

Phase 1：

```text
Raw History Sources             : 307
ADR                             : 26
Architecture                    : 45
Governance                      : 5
Handoffs／Review／Status         : 99
Operations                      : 11
Requirements                    : 38
User Manual                     : 7
Documentation Index             : 76
Existing Lossless Marker Count  : 307
```

既存Phase 1 Compilationは、CategoryごとのRaw Source Countと`Source SHA-512` Marker Countが一致する。Phase 1再整理では、Frozen Compilationを破壊せず、Source Path、Hash、MarkerおよびRaw Historyとの一致を再検証する。

Phase 1-ex：

```text
Stable Phase Files : 20
History／Event     : 116
State              : IN PROGRESS
```

Phase 1-exは未完了である。再整理版を作る場合は`interim`または`current_to_date`と明記し、完了済みFrozen Compilationと誤認させない。Phase 1-ex完了時には再度Sourceを固定して最終版を作る。

## 4. Stable Output Plan

第1周：

1. Project Continuity Master
2. Roadmap

Canonical：

3. Requirements Specification
4. System Architecture
5. Technology Selection
6. Basic Design
7. Runtime Governance Specification
8. Current Documentation Index

Lossless：

9. Phase 1 Frozen Compilation再検証
10. Phase 1-ex Current-to-date Lossless再整理
11. Shared一式

第2周：

12. Project Continuity Master最終整合
13. Roadmap最終整合
14. Overview
15. Concept
16. README
17. LICENSE／TERMS／NOTICE／CITATION

## 5. Non-loss Requirements

- Project Continuity MasterとRoadmapは最初と最後の2周行う。
- Phase 1とPhase 1-exの両方を再整理対象とする。
- Phase 1-exは進行中状態を明記する。
- Current、Shared、Public、Phase StableおよびLossless正本はTimestampなしFilenameを維持する。
- TimestampはHistory SnapshotとEvent Artifactだけへ付ける。
- Stable更新前後の完全SnapshotとSHA-512を保持する。
- Accepted情報、失敗Evidence、例外、未決事項、保留理由および将来Hookを削らない。
- `_en`派生版はPhase 1-ex後半Refreshまで作らない。
- READMEでは6枚のDemo画像を相対Pathで参照する。
- READMEでは現在の実行環境制約、高性能Model等の将来交換予定、Roadmap導線、利用条件および無保証を明記する。

## 6. Acceptance

- Inventoryの全Entryが存在する。
- SizeとSHA-512が一致する。
- Demo画像6件を識別できる。
- Phase 1 Raw Source 307件と既存Compilation Marker 307件が対応する。
- Phase 1-exを完了済みと扱わない。
- 後続作業中に追加されたDocsはDelta Inventoryとして別記録する。
- 本Inventory作成後の新Fileを黙って元Source Setへ混入させない。

