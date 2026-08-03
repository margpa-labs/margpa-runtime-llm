# ADR-0016: Phase 1-G／1-HをMacで完成後にLightningへ一括搬入する

- 文書ID: `adr_0016_batch_lightning_upload_after_phase_1h`
- 状態: `accepted`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- Decision Owner: ユーザー
- 記録担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- Roadmap: [implementation_roadmap_20260721093952.md](../architecture/implementation_roadmap_20260721093952.md)
- supersedes: なし（ADR-0015のCross-environment要件を破棄せず実行順だけ変更する）

## Context

Phase 1-FのRepository実装、Mac Regression、Lightning Read-only PreflightはAcceptedになった。Lightningでは次が確認済みである。

```text
Ubuntu／Linux x86_64／Container
Python 3.12.11
Tesla T4／15360 MiB
nvcc Available
Project／Studio-local uv 0.11.29
GPU Preflight Exit 0
CPU Candidate Preflight Exit 0
```

一方、Project本体とGGUF ModelのLightning Uploadには非常に長い時間がかかる。Phase 1-GのWeb UIとPhase 1-HのPost-generation Summary Modeを先に実装すると、Source、Static Asset、Dependency、Lockが再び変わる。

途中状態を何度もUploadするより、Macで1-G／1-HをAcceptedにしてから最終候補を一括搬入する方が、ユーザーの時間と転送負荷を減らせる。

## Decision

1. Phase 1-FのLightning Native Gateを一時保留する。
2. Phase 1-Fを完了扱いにはしない。
3. Phase 1-G Minimal Web SurfaceをMac上で実装・検証する。
4. Phase 1-G Accepted後、Phase 1-H Post-generation Summary Modeを実装・検証する。
5. Phase 1-H Accepted後、最終候補Source／Static Asset／Lock／ModelをLightningへ一括搬入する。
6. LightningではPhase 1-F、1-G、1-Hを同じ最終候補でまとめて検証する。
7. Lightning Pythonは3.12.11を維持する。
8. Mac Primary Pythonは3.13.14を維持する。
9. Lightning既設uv 0.11.18は変更せず、隔離済みuv 0.11.29を明示して使用する。
10. 一括搬入は目標であり、Lightning固有Failureによる小規模な修正Uploadが絶対に発生しないとは主張しない。

## Revised Sequence

```text
Phase 1-F Repository／Preflight Accepted
  → Lightning Native Gate Deferred
  → Phase 1-G Minimal Web Surface on Mac
  → Phase 1-G Review／User Test
  → Phase 1-H Post-generation Summary Mode on Mac
  → Phase 1-H Review／User Test
  → Single Batch Upload Candidate
  → Lightning Dependency／CUDA／CPU／Web／Summary Verification
  → Cross-environment Final Review
  → Phase 1 User Acceptance
  → Phase 1 Completion Declaration
  → Backup
```

## Rationale

- FastAPI、Uvicorn、HTTPX等を含む最終`pyproject.toml`／`uv.lock`を一度で同期できる。
- UI Static Assetを完成状態で搬入できる。
- GGUFの大容量Uploadを繰り返さずに済む。
- LightningでCLI、Web、Summaryを同じModel Artifact／Backend Buildで検証できる。
- Preflightが既に合格しており、大きなHost／Python／GPU／uv不一致は先に排除できている。
- Phase 1-F未完了を明示維持するため、未実行Gateを合格扱いしない。

## Consequences

### Positive

- Upload回数と待機時間を抑えられる。
- LockとSourceのSnapshot不一致を避けやすい。
- Web UIとSummaryをLightning公開候補へ同時に含められる。
- Cross-platform Application Coreの検証範囲が広がる。

### Negative

- Phase番号どおりの厳密な直列完了ではなくなる。
- Lightning固有Failureの発見時期が1-H後になる。
- 1-G／1-HはLightning未検証の期間を持つ。
- 小規模な修正Uploadが後で必要になる可能性は残る。

## Risk Controls

- 1-G／1-HはPlatform固有処理をApplication Coreへ入れない。
- FastAPI／Uvicorn固有処理をEntrypointへ局所化する。
- Modelを用いないFake Port／ASGI Testを先に充実させる。
- Mac Native Smokeを各Subphaseで維持する。
- Python 3.12をRuff／Mypyの下限として維持する。
- Dependencyを最小化し、純Python Wheelを優先する。
- Tracked Config／SourceへLightning固有絶対Pathを保存しない。

## Publication Boundary

この順序変更はGitHub公開またはLightning Live URL公開を自動許可しない。

初回GitHub公開は、既存DecisionどおりPhase 1-ex完了後にユーザーが別途許可する。Lightning Live URLもAccess ControlとUser Test合格後にのみ公開候補となる。

## Authorization Boundary

本ADRはPhase順序変更をAcceptedとし、Phase 1-G HandoffによるRepository実装を許可可能にする。

Phase 1-H実装、Lightning Full Upload、Model Transfer、Dependency Sync、Native Build、Backup、Git、GitHub公開は、それぞれの後続Handoff／ユーザー指示前には開始しない。
