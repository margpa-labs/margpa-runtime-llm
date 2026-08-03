# README／Overview Document Responsibility Correction

```yaml
document_id: readme_overview_document_responsibility_correction
status: completed
phase: phase_1_ex
created_at: 2026-07-27 12:55:53 JST
owner: 設計統括者役
targets:
  - README.md
  - docs/public/overview_ja.md
trigger: user_identified_critical_document_responsibility_failure
```

## Finding

READMEとPublic Overviewの文書責務を取り違え、下位文書で扱うべき内容を上位入口へ過剰に持ち込んでいた。

### README

READMEはProjectの最小入口であるにもかかわらず、次を収録していた。

- ModelとArtifactの詳細
- Hardware、Memory、Architecture、Python、Accelerationおよび外部環境の詳細
- Model配置
- Setup Command
- CLI Command
- Web起動・停止
- Public Demo運用状態
- 将来Componentの詳細列挙
- Runtime Governance内部構造の説明

これにより、Roadmap、Overview、Technology Selection、User ManualおよびOperationsの責務がREADMEへ重複していた。

### Public Overview

Public OverviewはProject概要を説明する文書であるにもかかわらず、23行だけで、内容の大半が個別実行環境、Model、Backend、Phase 1機能および外部環境検証の要約になっていた。

Projectの目的、対象問題、位置付け、全体構造、設計原則、Authority不変条件、研究方法およびEvidence思想が不足していた。

## Corrected Responsibility

### README

```text
Project Identity
短いProject説明
現在Phase
Roadmap最優先導線
主要文書導線
現在の画面例
利用条件／免責への導線
短いEnglish Abstract
```

READMEから、環境仕様、Model配置、Setup、CLI、Server操作、Public Demo手順および未搭載機能の詳細列挙を削除した。

### Public Overview

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
Public文書の読み方
実装状態／保証の境界
```

Overviewから個別実行環境、Hardware、Memory、Backend Version、Model Artifact、外部Service検証および操作手順を除外した。

## Source of Detailed Information

削除した内容は情報そのものを破棄していない。

```text
実装状態／未実装状態／将来構想:
  docs/public/roadmap_ja.md

技術と実行環境:
  docs/project/current/architecture/technology_selection_ja.md

System構造:
  docs/project/current/architecture/system_architecture_ja.md

Component／Contract:
  docs/project/current/architecture/basic_design_ja.md

操作手順:
  docs/project/phases/phase_1/user_manual/phase_1_user_manual_ja.md

詳細Evidence:
  docs/project/phases/phase_1/
  docs/project/phases/phase_1_ex/history/
```

## Stable／History

### README

```text
Before:
  docs/project/phases/phase_1_ex/history/operations/
  readme_before_document_responsibility_correction_20260727125332.md

After:
  docs/project/phases/phase_1_ex/history/operations/
  readme_after_document_responsibility_correction_20260727125332.md
```

```text
Before Lines : 240
After Lines  : 59

Before SHA-512:
95badf6dd997dd8620c287c1d96719243eaf97386c477da535362d024039d74a3c43e2d2465cb5235e38515bfeb6752c6c144328b694442282dc0100920d4457

After SHA-512:
d859f29c406a97be4216d991aa6ec765f36b9e2a65dbd222bb24464fdbf05382cd9fcdb77898ce148d2d1c13786493c85c31f321026b74f99ab784218636efa0
```

### Public Overview

```text
Before:
  docs/public/history/overview/
  overview_phase_1_ex_before_document_responsibility_correction_ja_20260727125332.md

After:
  docs/public/history/overview/
  overview_phase_1_ex_document_responsibility_correction_ja_20260727125332.md
```

```text
Before Lines : 23
After Lines  : 237

Before SHA-512:
5866fceee5f43775d880b64fc6f0956c23efde8e81f6ba2f8b7774ba11d90a171e381d5706e01e29bc05dde932943c97c1563e34dc7964fbd81fa10e3957bf71

After SHA-512:
ca050df3a4538479394998c9633f8bb24f3cf4b79a6831c6ee2f55dbd4600863b2e00343b1cc5020f97841b2cd0024a282528e36bf2e89606afe79d2106961d9
```

## Boundary

- READMEはOverviewの代替ではない。
- OverviewはRoadmap、Requirement、Architecture、Technology SelectionまたはUser Manualの代替ではない。
- RoadmapをPhase別の実装状態、未実装状態、依存順序および将来構想の正本とする。
- OverviewとREADMEへ個別環境または操作手順を再流入させない。
- 現在の画面例はREADMEに残すが、完成像または機能仕様とは扱わない。

## Index History

### Current Documentation Index

```text
Before:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_before_readme_overview_responsibility_correction_ja_20260727125332.md

After:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_after_readme_overview_responsibility_correction_ja_20260727125753.md
```

```text
Before SHA-512:
32e7a6465a7ba2379091020f0a148efefe7a4af6cad2a92c4ce36e13d9ca28107f89517395b5429c52a4cd59515c4e5f72bfa4e91dcac9a4f34172c85c48bf06

After SHA-512:
3da96b9d153af34979b4b793846fd80d47a8c4a4478dbe40f3272abbcd3ce9ecff5fefe4dd4b52de1b66cf7543c709123a87d1a4854fb28c84f2b86a3d5c21cf
```

### Phase 1-ex Index

```text
Before:
  history/operations/
  phase_index_before_readme_overview_responsibility_correction_20260727125332.md

After:
  history/operations/
  phase_index_after_readme_overview_responsibility_correction_20260727125753.md
```

```text
Before SHA-512:
33f15a4d143df3e293385ce5a75f398b4c72854ae1dae8dd250713cfa225c5f71bdb35cf34ae96e0e0fa6847e82ea13c24e0be452b2af6e6813aa294e1d16838

After SHA-512:
3e914a3738d9d8cf01d7d688d79770f0ebec97d0e5c1eb2fd27de546738342db3a68b4c363b40f25d2b315adffee0313d78855b296a9ab77ac5316a219236cb8
```

Snapshot作成時のFilename Timestamp訂正により、`20260727125806`版も同一内容・同一HashのImmutable Duplicateとして残っている。正規導線は実際の作成時刻に対応する`20260727125753`版を使用する。

## Validation

```text
Files Checked                    : 5
Relative Links Checked           : 256
Missing Links                    : 0
README Detailed Environment Scan : 0
Overview Detailed Environment    : 0
Old Identity／Private Path       : 0
README Stable／After Snapshot    : exact match
Overview Stable／After Snapshot  : exact match
Current Index／After Snapshot    : exact match
Phase Index／After Snapshot      : exact match
.DS_Store                        : 0 after cleanup
```

Validation中に再生成されていた`.DS_Store` 4件を削除し、Project内0件を再確認した。

## Result

READMEをProjectの短い入口へ戻し、Public OverviewをProject全体の目的、対象問題、構造、原則、研究方法および現在地を説明する概要文書へ再構築した。
