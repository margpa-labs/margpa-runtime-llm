# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727125834
state_at: 2026-07-27 12:58:34 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
  - ../../../../../README.md
  - ../../../../public/overview_ja.md
supersedes: documentation_index_20260727123553.md
source: readme_overview_document_responsibility_correction
```

本Snapshotは[12:35:53版](documentation_index_20260727123553.md)までの全状態を継承する。

## Added Artifacts

- [README Stable](../../../../../README.md)
- [Public Overview Stable](../../../../public/overview_ja.md)
- [README Before Correction](operations/readme_before_document_responsibility_correction_20260727125332.md)
- [README After Correction](operations/readme_after_document_responsibility_correction_20260727125332.md)
- [Overview Before Correction](../../../../public/history/overview/overview_phase_1_ex_before_document_responsibility_correction_ja_20260727125332.md)
- [Overview After Correction](../../../../public/history/overview/overview_phase_1_ex_document_responsibility_correction_ja_20260727125332.md)
- [Responsibility Correction Record](operations/readme_overview_document_responsibility_correction_20260727125553.md)
- [Current Index Before Correction](../../../current/history/index/documentation_index_phase_1_ex_before_readme_overview_responsibility_correction_ja_20260727125332.md)
- [Current Index After Correction](../../../current/history/index/documentation_index_phase_1_ex_after_readme_overview_responsibility_correction_ja_20260727125753.md)
- [Phase Index Before Correction](operations/phase_index_before_readme_overview_responsibility_correction_20260727125332.md)
- [Phase Index After Correction](operations/phase_index_after_readme_overview_responsibility_correction_20260727125753.md)

## Corrected Document Responsibility

### README

READMEは59行の最小Project入口とした。

```text
Project Identity
短い説明
現在Phase
Roadmap最優先導線
主要文書
画面例
利用条件／免責への導線
短いEnglish Abstract
```

Model、Hardware、Memory、Architecture、Python、Acceleration、外部環境、Model配置、Setup、CLI、Server操作、Public Demo手順および未搭載機能の詳細列挙は収録しない。

### Public Overview

Public Overviewは23行から237行へ再構築した。

```text
Project概要
背景と対象問題
Projectの位置付け
全体構造
Governance Definition Platform
設計原則
Authority不変条件
比較可能な研究方法
Evidence／Project Continuity
現在地
完成とみなさない短絡
Public文書導線
実装状態／保証の境界
```

個別実行環境、Model Artifact、Backend Version、外部Service検証および操作手順は収録しない。

## Integrity

```text
README Before:
95badf6dd997dd8620c287c1d96719243eaf97386c477da535362d024039d74a3c43e2d2465cb5235e38515bfeb6752c6c144328b694442282dc0100920d4457

README After:
d859f29c406a97be4216d991aa6ec765f36b9e2a65dbd222bb24464fdbf05382cd9fcdb77898ce148d2d1c13786493c85c31f321026b74f99ab784218636efa0

Overview Before:
5866fceee5f43775d880b64fc6f0956c23efde8e81f6ba2f8b7774ba11d90a171e381d5706e01e29bc05dde932943c97c1563e34dc7964fbd81fa10e3957bf71

Overview After:
ca050df3a4538479394998c9633f8bb24f3cf4b79a6831c6ee2f55dbd4600863b2e00343b1cc5020f97841b2cd0024a282528e36bf2e89606afe79d2106961d9

Current Documentation Index:
3da96b9d153af34979b4b793846fd80d47a8c4a4478dbe40f3272abbcd3ce9ecff5fefe4dd4b52de1b66cf7543c709123a87d1a4854fb28c84f2b86a3d5c21cf

Phase 1-ex Index:
3e914a3738d9d8cf01d7d688d79770f0ebec97d0e5c1eb2fd27de546738342db3a68b4c363b40f25d2b315adffee0313d78855b296a9ab77ac5316a219236cb8

Correction Record:
fd974bbd739128012fc810170a2be997c54cf14b8b531c95de5568e27aa8440f108391b00789dafab34ded55f8c892274153bb1d065e939578cfb9c0684a3748
```

## Validation

```text
Relative Links Checked           : 256
Missing Links                    : 0
README Detailed Environment      : 0
Overview Detailed Environment    : 0
Old Identity／Private Path       : 0
Stable／After Snapshot Match     : pass
.DS_Store                        : 0 after cleanup
```

## Boundary

本更新はREADMEとPublic Overviewの責務是正である。Roadmap、Requirements、Architecture、Technology Selection、User ManualおよびPhase Evidenceは削除していない。Phase 1-ex、Git、GitHub、Public Demo、RAG、Final Lossless、Final ReviewまたはBackupの状態を変更しない。
