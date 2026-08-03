# Public Repository Low-discoverability Root Surface Adjustment

```yaml
document_id: public_repository_low_discoverability_root_surface_adjustment
phase: phase_1_ex
status: implemented_local_pending_user_publication
created_at: 2026-08-02 14:58:25 JST
owner: 設計統括者役
decision_authority: user
target: public_repository_root_surface
```

## 1. 目的

Existing Repositoryの公開History、Project名、利用条件およびRoadmap導線を維持したまま、一般的な分野語検索、機械可読MetadataおよびRepository Landing Pageから偶発的に発見される可能性を下げる。

本対応はPublic Repositoryを非公開化するものではない。正確なProject名、Repository URLまたはSource内の固有語を知る者が検索・閲覧できる状態は維持する。

## 2. 限界

GitHubが生成するRepository PageのHTTP HeaderまたはHTML HeadをRepository File側から制御できないため、Rootへ`robots.txt`やHTML Metaを置く方式は採用しない。

Public Repository内のSource／DocsはGitHub内検索または外部Crawlerの対象になり得る。Root 5文書の調整は、Repository全体の検索除外を保証せず、主にLanding Pageと一般検索の露出を減らす。

Read-only Inventory時点で、Project名、分野語および独自研究名は多数のProject文書へ記録されている。これは先行公開性と公開Docsを維持する方針上、今回削除しない。

## 3. Root Artifact調整

### 3.1 README.md

- Project名、現在Phase、Roadmap最優先導線、Research Preview境界および免責を維持した。
- 詳細な機能説明、分野語列挙、英語Abstractおよび画面画像の展開をRoot入口から外した。
- Overview／Concept／Roadmapへの最小導線だけを残した。

### 3.2 LICENSE

- 閲覧・評価中心の許諾、禁止事項、無保証、責任制限および非OSS境界を変更していない。
- 無保証対象の具体的機能列挙を一般表現へ置き換えた。
- 第三者／別License境界を一般化し、法的意味を維持した。

### 3.3 NOTICE.md

- Project Identity、Copyright、Model Weight非同梱、第三者Software、別Licenseおよび無保証を維持した。
- 現時点でRepositoryへ含まれない個別候補名、将来研究名および詳細説明をRoot NOTICEから外した。
- 必須Third-party Attributionを削除する決定ではない。将来Artifactを追加する場合は、その時点でAttribution Reviewを行う。

### 3.4 TERMS_OF_USE.md

- 閲覧・評価範囲、禁止事項、Hosted Demo条件、安全境界、無保証、責任制限およびOSS化未確定を維持した。
- 個別機能名および別License候補名を一般表現へ置き換えた。
- Citation Fileへの依存を外し、言及時にProject名、Repository URLおよび参照Version／Commit／Archiveを明示する規則へ変更した。

### 3.5 CITATION.cff

Default Branch Rootの`CITATION.cff`は、GitHubのMachine-readable Citation MetadataとRepository Landing Page上のCitation UIを有効にするため、現在の低発見性方針と一致しない。

ユーザーがLocal CopyとGitHub上のDefault Branchから手動削除する。Task側は本変更で削除していない。削除後も過去Historyから自動的に消えるわけではなく、History Rewriteは行わない。

READMEおよびTERMS_OF_USEから`CITATION.cff`への参照を先に除去した。

## 4. GitHub Metadata側の推奨状態

```text
Topics              : none
About Description   : empty or minimal neutral text
Website             : empty
Social Preview      : custom promotional imageを設定しない
GitHub Pages        : low-discoverability期間は使用しない
Citation Metadata   : disabled by removing CITATION.cff from default branch
External Promotion  : intentionally minimized
```

Repository名、Owner、公開HistoryおよびDefault Branchは変更しない。

## 5. Evidence／先行公開性

本対応は既存Commit Historyを削除、置換またはRebaseしない。Root入口を簡素化しても、既存GitHub History、Commit SHAおよび公開日時の連続性は維持される。

Repository削除・再作成、Force Push、History RewriteまたはVisibility変更を本対応に含めない。

## 6. Backup／Mutation Boundary

ユーザーは変更前の対象5文書についてBackup取得済みと宣言した。

```text
Local Root Updated : README.md／LICENSE／NOTICE.md／TERMS_OF_USE.md
CITATION.cff       : unchanged／user manual deletion pending
Git Operation      : none
GitHub Operation   : none
History Rewrite    : none
Source／Runtime    : unchanged
```

変更前後原文はPhase 1-ex Historyへ保存する。
