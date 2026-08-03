# Documentation Structure／Role Authority Consolidation Decision

```yaml
event_id: documentation_structure_and_role_authority_consolidation
phase: phase_1_ex
status: accepted
created_at: 2026-07-26 17:00:34 JST
owner: 設計統括者役
```

## Decision

Docs構造再設計、Docs共通運用、再構築境界、History、Lossless Compilation、Task間情報伝達および役割別Write Authorityを、次のShared Operations正本へ統合した。

```text
docs/project/shared/operations/documentation_structure_and_task_operations_ja.md
```

Documentation RulesとTask Role／Write Authority Policyは個別正本として維持し、Shared Operationsから横断参照する。

## Raw Documentation Index

Phase 1の76件とPhase 1-exの2件は、現在の`history/`直下を維持する。

`history/index/`へ単純移動するとRaw Index本文内の相対Linkが一段ずれるため、現Phaseでは移動しない。

Phase切替時に、Raw本文、SHA-512、相対Link、ManifestおよびTask Path解決を同時に維持できる方式を確定した場合に再検討する。

## Reconstruction Boundary

`docs/project/`単独では内部Raw Source 318件を再構築できる。Public 2件は`docs/public/`へ分離しているため、Whole Documentationの復元単位は`docs/`全体とする。

## Authority

役割別Write ScopeはTask Role／Write Authority Policyを正本とする。Write Scopeが不明またはCross-Phase影響がある場合は、設計統括者役へEscalateする。
