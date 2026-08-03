# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260802145825
state_at: 2026-08-02 14:58:25 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - documentation_index_20260802142024.md
  - operations/public_repository_low_discoverability_root_surface_adjustment_20260802145825.md
  - ../../../../../README.md
  - ../../../../../LICENSE
  - ../../../../../NOTICE.md
  - ../../../../../TERMS_OF_USE.md
  - ../../../../../CITATION.cff
supersedes: documentation_index_20260802142024.md
source: user_public_history_preservation_and_low_discoverability_root_surface_decision
```

本Snapshotは[2026-08-02 14:20:24版](documentation_index_20260802142024.md)までの全状態を継承し、Existing Repositoryの先行公開性を維持したRoot公開Artifactの低発見性調整をAppend-onlyで記録する。

## 1. Root Adjustment

```text
README.md       : minimized
LICENSE         : legal scope preserved／specific feature enumeration generalized
NOTICE.md       : attribution boundary preserved／non-included named candidates removed
TERMS_OF_USE.md : permission boundary preserved／specific feature names generalized
CITATION.cff    : unchanged locally／user manual deletion pending
```

READMEはProject名、現在Phase、Roadmap最優先導線、Research Preview、利用条件および免責だけを扱う最小入口へ変更した。

## 2. Discoverability Boundary

```text
README Lines Before                    : 79
README Lines After                     : 33
Selected Root Signal Terms Before      : 46
Selected Root Signal Terms After       : 0  # CITATION.cff削除後を想定
Selected Root Signal Terms Current     : 8  # CITATION.cffがLocalに残る現在値
```

本数値は、Root 5文書内の選定した分野語・固有研究語の出現数であり、検索順位またはCrawler非掲載を保証する指標ではない。

Project全体では同一の情報がSource／Docsへ保持されており、GitHub Code Search、正確なProject名、Repository URLまたは固有語による到達可能性は維持される。

## 3. CITATION Boundary

`CITATION.cff`はGitHubのMachine-readable Citation MetadataとRepository Landing Page上のCitation UIを有効化するため、現在方針ではDefault Branch Rootから削除する。

READMEおよびTERMS_OF_USEの参照は除去済みである。Local／GitHub上の削除はユーザーが手動で行い、Task側は本Snapshot時点で削除していない。過去HistoryのRewriteは行わない。

## 4. Root／GitHub Metadata Recommendation

```text
Topics            : none
About Description : empty or minimal neutral text
Website           : empty
Social Preview    : no custom promotional image
GitHub Pages      : disabled during low-discoverability operation
External Promotion: intentionally minimized
```

Repository名、Owner、Visibility、Existing HistoryおよびDefault Branchは本対応で変更しない。

## 5. History

- [Adjustment Record](operations/public_repository_low_discoverability_root_surface_adjustment_20260802145825.md)
- [README Before](operations/readme_phase_1_ex_before_low_discoverability_root_surface_ja_20260802145825.md)
- [README After](operations/readme_phase_1_ex_after_low_discoverability_root_surface_ja_20260802145825.md)
- [LICENSE Before](operations/license_phase_1_ex_before_low_discoverability_root_surface_en_20260802145825.md)
- [LICENSE After](operations/license_phase_1_ex_after_low_discoverability_root_surface_en_20260802145825.md)
- [NOTICE Before](operations/notice_phase_1_ex_before_low_discoverability_root_surface_ja_en_20260802145825.md)
- [NOTICE After](operations/notice_phase_1_ex_after_low_discoverability_root_surface_ja_en_20260802145825.md)
- [TERMS Before](operations/terms_of_use_phase_1_ex_before_low_discoverability_root_surface_ja_20260802145825.md)
- [TERMS After](operations/terms_of_use_phase_1_ex_after_low_discoverability_root_surface_ja_20260802145825.md)
- [CITATION Before／Pending Deletion Copy](operations/citation_phase_1_ex_before_low_discoverability_root_surface_20260802145825.cff)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_low_discoverability_root_surface_ja_20260802145825.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_low_discoverability_root_surface_ja_20260802145825.md)

## 6. Integrity

```text
Previous Documentation Index:
  babfaa0f0715ca2761b820626269489ff41f3aaa5255fde8ae5114c35c682a028ce293aaae04c1f955b448f39b8647cb28d96b19e4d788855080b869d612d2a1

README Stable／After:
  17fa7094146b13215f95e56f1f2babdc4a3be9bab4253d15ad987f0f158a2b5cacb1a0f903c6b981ce16216ac05251e5dcc1649975930862c2aa099fd38508a9

LICENSE Stable／After:
  ecb51b8b8ceff0a59a614db9103ef45cd976da5957f1221cbb647ba55fc7e394926664bb436057a19ae8463ec2c1b81435cfa163b1774e5901a520bd06cb19b7

NOTICE Stable／After:
  ca496fd132a3a3c66ab1c0347a797e4fe75b4a9ca5639428bd9bbf4c6dae5df808ff881b8b9cd7272a99f28fc7f1eb90efbf37b9da7f63bac4c723add8f755ec

TERMS Stable／After:
  fbc156316905b63d8963cf9f777ec8638d8d5bf307905fca5a11345d36d2cfa6978a624350cfa10c67b4e3005c87d3f263d111c242ccf39cc37a22f3631747b4

CITATION Current／History:
  9260fd358f8821df72a28c022b30630f948c91ae7611d132f7a777d343a0aade8ce2b3714773122267f173521b6a5968c397fa5643a07676a80278be2a5f86d1

Adjustment Record:
  9008484378346b273cf0377c4f133399ee94f231424772d510c09a2a8351aef5c39a183092033a0abcdc5cb684a2c659082dcec875a94ffcd992c56132c2731f

Phase Index Before:
  15adea35b8bcc38c54f2a2c8c13f8fcde087500e761aa0140b192e7a37b4b74c044c5129413a023367a81fbe09d121ed6e72f87caf7ce4b687de4ccd52f23561

Phase Index Stable／After:
  32c39ff99215e4ce1c27ccbc4cd4c8b79bf7773161502b772b3b00f908f0280da508d529b3412b1c228198f859a138fdd00b393ac1a7a0dff8ff80f5b1f2cb0a
```

## 7. Mutation Boundary

```text
User Backup Confirmation : received for Root 5 artifacts
Git Operation            : none
GitHub Operation         : none
Repository Metadata      : none
Repository Visibility    : unchanged
History Rewrite          : none
Runtime／Source           : unchanged
CITATION Deletion        : pending user action
```
