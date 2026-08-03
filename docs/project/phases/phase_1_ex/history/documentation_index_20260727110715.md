# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727110715
state_at: 2026-07-27 11:07:15 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
supersedes: documentation_index_20260727104719.md
source: public_canonical_and_legal_documentation_reconstruction
```

本Snapshotは[10:47:19版](documentation_index_20260727104719.md)までの全状態を継承する。

## Added Evidence

- [Public／Canonical／Legal Documentation Reconstruction](operations/public_canonical_and_legal_documentation_reconstruction_20260727110347.md)
- [Phase Index Before Public Reconstruction](operations/phase_index_before_public_documentation_reconstruction_20260727110347.md)
- [Phase Index After Public Reconstruction](operations/phase_index_after_public_documentation_reconstruction_20260727110712.md)

## Completed Documentation Stage

```text
Project Continuity Pass 2 : complete
Roadmap Pass 2            : complete
Overview                  : created
Concept                   : created
README                    : created
LICENSE                   : created
TERMS_OF_USE              : created
NOTICE                    : created
CITATION                  : created
Stable Link Validation    : 262 / 262 pass
Old Identity              : 0
Private User Path         : 0
.DS_Store                 : 0 remaining
```

## Test／Static Validation

```text
pytest                     : 299 passed, 3 deselected
ruff check                 : pass
ruff format --check        : 96 files already formatted
mypy                       : pass
Phase 1 Lossless Extract   : 316 / 316 pass
Phase 1-ex Interim Extract : 145 / 145 pass
CITATION YAML Parse        : pass
```

## Integrity

```text
Phase 1-ex Index Before:
d02c22fb5d095b31401230d3b2ee4727be3858de9d8d5fc60c7d86b8489876a385866e5d4c02bdd84c46f058c10161c96880dfbb391b696cbfd77cd4a8a47b9f

Phase 1-ex Index After:
ba6af98ae4d774ad65f1304890dce79f5b4b3d105c992c5c400166b9d92639d159710ec031a41b9d36cd63c2e741dd841d2ce9f2df99327b4fbbc8d168238293

Current Documentation Index:
6c505c0d8b3a3658b6296e05be1debf0b3652058160408ee1ea21c3be96b029e77c9c73549e9c677f8f4351203599bad20f4483234464d32da01558f922a50fe

Reconstruction Record:
0535bfe992c34c110142f86197ba28d4011f7166d9a24ebe1a9bf49b2c7725b8de7238d8f0ab72fd05ed2999ab25d38188b8fbf3ab87ff9a5378bcffdb3f6598
```

## Known Pre-initial Commit Review

旧Lightning Basic Preview URLはPhase 1 Immutable Evidenceへ保持されている。Credentialは含まれない。Public Allowlist作成時に、保持公開、Internal除外またはRedacted Public Derivativeをユーザーが決定する。

Model WeightはExternal `models` Symbolic Link配下に存在するが、`.gitignore`で`models`と`*.gguf`を除外している。Initial Commit Candidateで再検証する。

## Next

Documentation初版再構築後の次作業は、Mac限定簡易Documentation RAG、Lightning残Manual Validation、Git運用設計、Pre-initial Commit Refresh、Phase 1-ex Final Lossless、Final Review、Backupおよび公開Gateである。
