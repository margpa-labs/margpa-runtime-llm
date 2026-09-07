# 対外向け指定4文書 累積作成Rule追加Record

```yaml
document_id: public_facing_four_document_cumulative_authoring_rule_addition_ja_20260907093750
document_type: convention_change_record
document_state: recorded
recorded_at: 2026-09-07 09:37:50 JST
language: ja
decision_authority: user
owner: Nazuna Research
append_only: true
target_stable: docs/project/shared/conventions/public_facing_document_authoring_rules_ja.md
```

## 1. 追加したRules

既存の対外向け公開Document作成Rulesを維持し、次の4文書へ限定した累積作成RulesをStableへAppend Onlyで追加した。

```text
docs/public/roadmap_portfolio_edition_ja.md
docs/public/roadmap_summary_ja.md
docs/public/technology_selection_ja.md
docs/public/technology_selection_portfolio_edition_ja.md
```

追加内容は次のとおりである。

- 4文書へ着手するたび、対外向け公開Document作成Rulesを全文読んでから作業する。
- Nazuna Researchが直接再編集したRoadmap Portfolio EditionとTechnology Selection Portfolio EditionのCurrent版を、表現、文章の流れおよび情報粒度のBaseとする。
- 上記2文書も難解な箇所が残るため、単純模倣ではなく、さらに初見へ分かりやすく改善する。
- 作成者をAgent視点で`User`と呼ばない。ただし、一般利用者、UI、Codeまたは正式な技術用語として必要な`User`／`user`は使用できる。
- 嘘、誇大Claimおよび誤認を避ける一方、就職・転職等であえて不利になる不要な表現、内部FailureまたはRaw Errorの過剰開示を禁止する。
- 同一概念の日本語／英語表記を文書内で統一する。必要な英語は初出時の補足または一般的な正式用語として扱う。
- MARGPA Runtime LLM、Repository、Phase、内部略語および過去経緯を知らない読者が、単体で理解できる構成と表現にする。
- 元文書の基本Flow、YAML Metadataおよび視覚的Formatを尊重しながら、重要度に応じて情報粒度を変える。
- `roadmap_summary_ja.md`の通常更新対象、および残る3文書の原則保護対象という既存Ruleを変更しない。
- 4文書に限り、更新前Snapshotとは別に、作業担当が生成した直後のStableを、Nazuna Researchの直接編集前に対応Historyへ完全Copyする。
- 生成直後StableとHistory CopyはMetadataを含めて同一内容とし、SHA-512一致を確認する。
- 作成者はHistory File名で識別し、History用Metadataを本文へ加えて同一性を壊さない。
- この特別な生成直後Copy運用を、指定外の文書へ自動拡張しない。

## 2. 目的

対外向け文書を事実に忠実かつProfessionalに保ちながら、難解さ、Agent視点、不統一な用語および過剰に不利な表現を減らす。

また、AIが生成した版とNazuna Researchが直接編集したCurrent版を正確に比較し、以後の文書品質改善へ利用できる状態を維持する。

## 3. 運用境界

本Recordは実施済みRule追加のAppend-only記録である。4つのPublic Stable本文自体は本作業では変更していない。

