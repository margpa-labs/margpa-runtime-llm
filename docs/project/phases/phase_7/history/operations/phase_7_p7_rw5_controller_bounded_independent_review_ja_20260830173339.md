# Phase 7 P7-RW5 Controller Bounded Independent Review

```yaml
document_id: phase_7_p7_rw5_controller_bounded_independent_review_20260830173339
document_type: controller_bounded_independent_review
document_state: final
language: ja
created_at: 2026-08-30 17:33:39 JST
provider: Codex
role: プロジェクト責任者兼設計統括者役
phase: phase_7
review_scope: P7-RW5
implementation_authority: false
phase_7_closure_authority: false
git_authority: false
```

## 1. Review対象

- `docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_return_handoff_ja_20260830171200.md`
- `docs/project/phases/phase_7/history/index/phase_7_no_hit_citation_persistence_and_local_corpus_identity_p7_rw5_final_recovery_ja_20260830170958.md`
- P7-CODEX-014〜016のBackend／Frontend Source、Focused Testおよび実配信Frontend Artifact。

Return Handoff SHA-512は記載値と一致した。

```text
75d75e1d7bd0be041ffdb62014b8a50a275e040da248d9ab6e331479d395f1fb9d03c233b6e2f62a12cdc09b39451b509ae81e048c67de62bf42fe159a540684
```

## 2. 結論

```yaml
controller_disposition: ADJUST_REQUIRED
source_implementation: TECHNICALLY_ACCEPTABLE_CANDIDATE
open_critical: 0
open_major_mvp_blocker: 1
phase_7_closure: NOT_AUTHORIZED
exact_next_action: P7-RW5-E FRONTEND DISTRIBUTION ARTIFACT BUILD
```

P7-CODEX-014〜016のSource修正は、報告されたRoot Causeと一致し、Focused Regressionも成立した。ただしFrontend Source変更後の`npm run build`が実行されておらず、FastAPIが実際に配信するStatic Bundleは旧実装のままである。User実画面へ修正が届かないため、P7-RW5全体はまだComplete Candidateとして受理できない。

## 3. Source Review結果

### 3.1 P7-CODEX-014

`build_turn_citation_evidence()`はRAG OFFとRAG ON＋NO_HITを分離し、NO_HITを`citations=()`、既存`grounding_state`および`warning_codes`で永続化する。Persistent DetailとFrontend再構成も同じ既存Fieldを使用している。新規意味Heuristicはない。

### 3.2 P7-CODEX-015

`document_title`はLocal Corpus RecordからManifest、Chunk、Reference、Citation、Persistent Detail、UIへOptional Fieldとして中継される。Project Docsは従来のHeadingを維持する。

### 3.3 P7-CODEX-016

`storage_display_path`はActive Registryの`document_store_path`と`project_root`から動的に導出される。Production Sourceに`mac-local-primary`またはUser固有PathのHard-codeはない。Project Root内のCurrent Profileでは、実保存RegistryのProject-relative Pathを表示する。

## 4. Controller Focused Verification

```text
Backend Focused:
  82 passed

Frontend Focused:
  CitationsSection.test.tsx
  persistentDetailProjection.test.ts
  2 files / 19 passed
```

最初の`uv run pytest`はSandbox外の既定`~/.cache/uv`を初期化できずTest開始前に終了した。Source／Test Mutationはなく、Project内`.venv/bin/pytest`とProject内`--basetemp`で直ちに再実行し82件PASSを確認した。本件はProduct Findingではない。

## 5. Open Finding

### P7-CODEX-017 — Frontend Source変更が実配信Static Artifactへ反映されていない

```yaml
severity: major_mvp_blocker
disposition: OPEN_REWORK_REQUIRED
affected_acceptance:
  - P7-RW5-ACC-001
  - P7-RW5-ACC-002
  - P7-RW5-ACC-004
  - P7-RW5-ACC-005
  - P7-RW5-ACC-012
```

Evidence：

- `frontend/src/lib/persistentDetailProjection.ts`と`frontend/src/components/CitationsSection.tsx`は2026-08-30 17:01に更新されている。
- FastAPIが配信する`src/margpa_runtime_llm/web/static/app.js`／`index.html`は13:15のままである。
- `frontend/vite.config.ts`はBuild出力先をこのFastAPI Static Rootへ固定している。
- Current配信`app.js`はPersistent Detail再構成で依然として`warnings: []`を設定し、`warning_codes`、`document_title`、`storage_display_path`、`citationFieldTitle`を含まない。
- P7-RW5 Exact Handoff §6 ACC-012はFrontend `Build` PASSを要求しているが、Return §10はTypecheck／Test／Lintだけで`npm run build`の実行Evidenceがない。それにもかかわらずACC-012をPASSとしたClaimは不正確である。

影響：

```text
Source／Unit Test上のFix
  != FastAPIがUser Browserへ配信するFix

Current User実画面ではP7-CODEX-014〜016が未反映となる。
```

## 6. Non-blocking Observations

- P7-RW5-IR-001のProject Root外Fallback表示形はCurrent User Profileに影響せず、Phase 7 Closure Blockerへ昇格しない。
- ClaudeはExact HandoffのGit禁止下でread-only `git status`を実行したと記録している。Git Mutationは0でProduct Resultへ影響しないため、Process Nonconformanceとして保持するが、本ReworkのTechnical Blockerにはしない。
- 旧Local Corpus Citationは新Optional Fieldを持たないため従来表示へFallbackする。過去Evidenceの遡及書換えをしない契約上、非Blockingとする。

## 7. Required Minimal Rework

Source、Test、Schema、HeuristicまたはRuntime Logicを追加変更しない。

1. Project内Temp／Cacheだけを使用する。
2. `frontend/`で既存Toolchainによる`npm run build`を実行する。
3. FastAPI配信先`src/margpa_runtime_llm/web/static/`が更新されたことを確認する。
4. 配信Bundleが少なくともNO_HIT `warning_codes`再構成、Local Corpus `document_title`および`storage_display_path`を含む現行Sourceから生成されたことを確認する。
5. Network、Install、Runtime切替、Source再設計、Git、Phase 7 ClosureまたはPhase 8へ進まない。
6. Recovery AddendumとExact Return Addendumを作り、Controller Review待ちで停止する。

Build後のUser実画面確認は引き続きUser Gateであり、ClaudeがPASSを代行しない。
