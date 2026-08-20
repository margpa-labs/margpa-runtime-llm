# Phase 3 Governance Definition Source Inventory

```yaml
document_id: phase_3_definition_source_inventory
status: observed_baseline
phase: phase_3
language: ja
observed_at: 2026-08-21 02:05:30 JST
observer_role: プロジェクト責任者兼設計統括者役
mutation_performed: false
source_root: definitions/
```

## 1. Summary

```text
JSON Source Files      : 17
Logical Definitions    : 18
Total Bytes            : 1,393,121
Total Lines            : 31,847
JSON Parse             : 17／17 PASS
Corpus Manifest Digest : dc8631643a0d48b272c7ec1c2f99aec5155e40957ec6d0924ce2aaab3ba4fbea930c6ea26c907ba3415cf01e73153287c997942cb312beb572e100d56f21cf7b
```

Corpus Manifest Digestは、各JSONについて`project-relative path<TAB>byte length<TAB>content SHA-512<LF>`をPath順に連結したByte列のSHA-512である。これは署名または真正性保証ではない。

## 2. Source Inventory

| Source | Bytes | Logical Definition | Version | SHA-512 |
|---|---:|---|---|---|
| `definitions/core_governance/argd_v0.3.1_en_dagd_v0.4.4_en.json` | 63,560 | ARGD／DAGD | 0.3.1／0.4.4 | `e32c6dc0289743794de7943cd9ebab252fbe4b0209522858a4f2c560d905fe6f4ac8fcc32c91bc89d56b9fd6fb079e8e29b110203905e33d6114b6b65cc22e16` |
| `definitions/orchestration/cdogd_v0.1.0_en.json` | 129,623 | CDOGD | 0.1.0 | `096039f899db7523eb2624226484b607efaef2f80d7fbfaa20f6d15759d577de34531dcddbf1c0e2e6d03d2f6d09f4adda3d6c63e7316528fb18306516a0d60b` |
| `definitions/domain_extensions/ordinary/aagd_v0.1.0_en.json` | 66,845 | AAGD | 0.1.0 | `55763622b6bb87261ca13309a21df723c12441c831dccfbc06dc1ee12525c963f30101a614259929bdae52792369d546cc35ec21ce3fd6870b4d42f874f42f10` |
| `definitions/domain_extensions/ordinary/acrgd_v0.1.0_en.json` | 78,615 | ACRGD | 0.1.0 | `c24f8e6e6b54d8def059a8f2b6973376ed11726b5497054a577128ca3827a0e4832b56a4b81a1a269dae30c85533af5e07eee5b8730b0c9efba7d5b7a904e73c` |
| `definitions/domain_extensions/ordinary/aiagd_v0.1.0_en.json` | 91,320 | AIAGD | 0.1.0 | `c7fdcba7e0a2d29d602ed86e406c03dbf30b706b6e67d373b447c1e220eb57562e98e6108970e99840fbb73188f8ec9b8d999ad728ba4f605b2d2b227cd2b1b0` |
| `definitions/domain_extensions/ordinary/airgd_v0.1.0_en.json` | 84,626 | AIRGD | 0.1.0 | `76e0b055a3a3abd1da6d76dc6735480ab2a13de71227fad3a7e3e54aa9912ced8f86de56bb9a1c40fe1ac474e89eeba14802f98e4aa2ebf40f770347ed6a0004` |
| `definitions/domain_extensions/ordinary/aisgd_v0.1.0_en.json` | 79,682 | AISGD | 0.1.0 | `1073d729ba2b39a4bac307ddb04cf2386eb6ca0584e474f4f355afe1243768d799798881470bcdb4f3d046980078668f3f693cf477f229ea73b80e7f7fe3d3ba` |
| `definitions/domain_extensions/ordinary/dcagd_v0.1.0_en.json` | 62,447 | DCAGD | 0.1.0 | `05ed1fc027d628b7fbd7c3c2a32f190dd1e0726939a92fa2da60f33b0695b69329bc0edb625c5eaf04b5749b85d362ddb4472bd5a9e7c3225381892e76716c4e` |
| `definitions/domain_extensions/ordinary/dsgd_v0.1.0_en.json` | 101,180 | DSGD | 0.1.0 | `ea8900286c3fc79f0d28aa9b6613480f2c2b88cd4fb0318b33cd47fdbb139cf16f41c542ee30e88106d9fe1379f0173db7640bea8f97d2b3e645d69aad1704e0` |
| `definitions/domain_extensions/ordinary/mpgd_v0.1.0_en.json` | 80,217 | MPGD | 0.1.0 | `1bfd1940cd2adde6ce21cb42544864194bfaee39d5e0bc66ae680b33f72bbbebdbd8c4fe4a7ff22598f8665dfc78aebb442e04b2f2888b158d400a301a9e0a80` |
| `definitions/domain_extensions/ordinary/omrgd_v0.1.0_en.json` | 87,117 | OMRGD | 0.1.0 | `3353e692ff9d25c6874ef804d44c1b1bf0032b5ab6cf5f4179b6f5d0f3b5470bb3d06f0806fda6d8d41839ebbc1af4ada56d520cbbbb1e99628f1d11e08c1979` |
| `definitions/domain_extensions/ordinary/pmogd_v0.1.0_en.json` | 97,425 | PMOGD | 0.1.0 | `24837615f90521cd0a712694253c9fbe566d10dd219b8a2c2b13fe9b3c6d722b6313f85107df2ed616ccee20c9efc60aed6d6c5b0443c3200370fea0eb8f5d11` |
| `definitions/domain_extensions/ordinary/segd_v0.1.0_en.json` | 95,436 | SEGD | 0.1.0 | `c18812354cc5b5e19f693dc06fda1db218f103c1417c32c1e4284f62593b591618ba2dcc6cf2810b939a167dba5deeacfccb51398780bda90641b8df426162f5` |
| `definitions/domain_extensions/decision_pipelines/sppgd_v0.1.0_en.json` | 67,696 | SPPGD | 0.1.0 | `763a110ebe9fefbc264390c1da5cc181679b6a13da55f938932d351f62f08e5d8733a1fd4690aaf66a6971aa1caeae1a1b6d4660c631cec2737253a3aef0a408` |
| `definitions/domain_extensions/decision_pipelines/daagd_v0.1.0_en.json` | 76,597 | DAAGD | 0.1.0 | `95392c7def5068db4c71f7369ff8bd4e15d7d4b846b4ad72701cca88910f03da390cb3111f77220a6e4b7e786369ce25d1d330606f05b4b484fb2da20e50f43d` |
| `definitions/domain_extensions/decision_pipelines/sdagd_v0.1.0_en.json` | 66,619 | SDAGD | 0.1.0 | `823afeccfac67bb89364313189a83515c8db236bdbaebd9782074f7ec21156b7f0d94333e73e64589582d6b628a3ee5eb7aceff3d09fc9aebb7a18eb6ff966da` |
| `definitions/domain_extensions/conditional_watchdogs/sdmrgd_v0.1.0_en.json` | 64,116 | SDMRGD | 0.1.0 | `92a31bc92ef1682a000bfd68990fc17864757bba1c3a3501208e2e7a1552bac22c62590b6ad5beda7bef5775868021c71f946f2d89add636cf4566ba78396bc2` |

## 3. Structural Observation

### 3.1 Schema Families

```text
Family 1: Combined Core Source
  ARGD + DAGD in one JSON

Family 2: Orchestration Source
  CDOGD

Family 3: Common Domain Extension
  15 extension definitions
```

一つのParserへ無理に統合せず、ManifestでTrusted Adapterを明示する。

### 3.2 Decision Pipeline

```text
SPPGD → DAAGD → SDAGD → SDMRGD（条件成立時のみ）
```

SDMRGDは常時Activeではない。SDAGDとの相互再帰監査を禁止する。Phase 3は関係をIRへ保持するだけで実行しない。

### 3.3 Common Extension Structure

15 Extensionは、ARGD／DAGD継承、External CDOGD参照、Domain Scope、Policy Goal、Capability、Role Separation、Activation、Evaluation、Repair、Self Audit、Audit-to-Action、Status Reporting、Record Schema、Orchestration ReferenceおよびAbstraction／Context Policyを共通に持つ。

共通構造はAdapter再利用の根拠になるが、全Sourceの意味が同一であることを意味しない。

## 4. Required Corrections／Wrappers

現行Sourceを実行可能にする前に、少なくとも次を外部Manifest／Envelopeで補う必要がある。

- Package ID／Version／Publisher／License。
- Source ID、Byte Length、SHA-512、Media Type。
- Schema ID、Trusted Adapter ID、Logical Definition ID、Object Pointer。
- Definition DescriptorのCapability／Role／Activation／Non-target／Dependency／Conflict。
- Canonical Manifest Digest。

これらをSource本文へ黙って埋め戻さない。

## 5. Non-source Files

`definitions/.DS_Store`および`definitions/domain_extensions/.DS_Store`を観測した。これらはManifest対象外であり、Definition Providerは読まない。本Inventory作成時に削除、移動、変更またはIgnore設定変更を行っていない。

## 6. Provenance Boundary

- 本InventoryはLocal観測結果であり、外部署名、公開日時またはPublisher真正性を証明しない。
- SHA-512は同一Byte確認用であり、改竄耐性または信頼性を単独で保証しない。
- Source内容はPhase 3開始時に再Hashし、差分があれば本Baselineをそのまま実行Manifestへ流用しない。
