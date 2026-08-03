# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260727121947
state_at: 2026-07-27 12:19:47 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - ../../../current/documentation_index_ja.md
supersedes: documentation_index_20260727110950.md
source: post_documentation_design_governance_recovery_refresh
```

本Snapshotは[11:09:50版](documentation_index_20260727110950.md)までの全状態を継承する。

## Added Artifacts

- [Interim Design Governance Recovery Manifest](../../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260727121343.md)
- [Post-documentation Recovery Refresh Record](operations/post_documentation_design_governance_recovery_refresh_20260727121814.md)
- [README Before Refresh](operations/readme_before_phase_status_and_recovery_refresh_20260727121225.md)
- [README After Refresh](operations/readme_after_phase_status_and_recovery_refresh_20260727121343.md)
- [Phase Index Before Refresh](operations/phase_index_before_post_documentation_recovery_refresh_20260727121343.md)
- [Phase Index After Refresh](operations/phase_index_after_post_documentation_recovery_refresh_20260727121814.md)
- [Current Index Before Refresh](../../../current/history/index/documentation_index_phase_1_ex_before_post_documentation_recovery_refresh_ja_20260727121343.md)
- [Current Index After Refresh](../../../current/history/index/documentation_index_phase_1_ex_after_post_documentation_recovery_refresh_ja_20260727121814.md)

## Current State

```text
Phase 1                      : complete／accepted
Phase 1 Backup               : completed／verified
Phase 1-ex                   : in progress
Initial Documentation Corpus : complete／validated
Design Governance Recovery   : interim current state／ready
Git／GitHub                  : not started
Mac Documentation RAG        : not implemented
Traffic-aware Wake-up        : manual validation pending
Phase 1-ex Final Lossless     : not created
Phase 1-ex Final Backup       : not created
```

README上部には、現在地を`Phase 1-ex / 最終予定 Phase 10`として表示し、Roadmapへ直接到達できる導線を追加した。

## Integrity

```text
README:
95badf6dd997dd8620c287c1d96719243eaf97386c477da535362d024039d74a3c43e2d2465cb5235e38515bfeb6752c6c144328b694442282dc0100920d4457

Current Documentation Index:
27fcbf1cba153b9760b7bc75c46efda2b624bb39e7c38529fe6831f3d805f3901763c1a64e23bcf5d407a5f94f1d52b9f888e35fe8ee888bc7acc4d9077f076b

Phase 1-ex Index:
2dff3fbd188a7794757a3aa546c2ee1285152b79d37c2a3279fc399938f6b226326c5f2133f31857f219fb6a9ed087bdebc3137b67b5fa40d1e37299a3e87e9b

Design Governance Stable Handoff:
68cdd050d5b3902249d04ec7b7262946645a03dc4ddfeb20d708c6bfb939a08b798007052e7e8e3c38f66f8278de43b44c339d9ef8d7822b4a460b8773d7e05d

Interim Recovery Manifest:
8b7640fb112e5425c0a20f9be62dc081e428bf075c643a5a59bd9095adaa121fd89cccab97f0eff050eee99fa9da5786435bbec60187bb142da84e5d1fd4af24

Recovery Refresh Record:
1d277b8fa697da95f4630e7a1abf28235a7c207ea7e322f3a89f4cc022223e52a7300fd16d8520296f952137e3157ea044cea62c2feb73fae8b2b006ceb1fecb
```

## Recovery Entry

新しい設計統括者役Taskは、次を順に読めば旧Task会話なしで再開できる。

1. `docs/project/current/documentation_index_ja.md`
2. `docs/project/current/project_continuity/project_continuity_master_ja.md`
3. `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md`
4. `docs/project/shared/history/design_governance_handoff/design_governance_recovery_manifest_20260727121343.md`
5. `docs/project/phases/phase_1_ex/phase_index_ja.md`
6. `docs/public/roadmap_ja.md`

## Boundary

本Snapshotは、初回Documentation Corpus完成直後の設計統括者役臨時完全復旧点を示す。Phase 1-ex完了、Final Lossless、Final Review、Backup、Git、GitHub、匿名Public DemoまたはExternal Actionの完了を示さない。
