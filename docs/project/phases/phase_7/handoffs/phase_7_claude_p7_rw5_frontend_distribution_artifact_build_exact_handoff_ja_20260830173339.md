# Phase 7 P7-RW5 Frontend Distribution Artifact Build — Exact Handoff

```yaml
document_id: phase_7_claude_p7_rw5_frontend_distribution_artifact_build_exact_handoff_20260830173339
document_type: exact_differential_execution_handoff
document_state: frozen
language: ja
created_at: 2026-08-30 17:33:39 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_claude_task
phase: phase_7
execution_scope: P7-RW5-E
implementation_authority: true
source_edit_authority: false
test_edit_authority: false
network_authority: false
git_authority: false
phase_7_closure_authority: false
phase_8_authority: false
```

## 1. Active Baseline

P7-RW5 Source実装はRollbackせず保持する。

```text
P7-RW5 Return:
docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_return_handoff_ja_20260830171200.md
SHA-512:
75d75e1d7bd0be041ffdb62014b8a50a275e040da248d9ab6e331479d395f1fb9d03c233b6e2f62a12cdc09b39451b509ae81e048c67de62bf42fe159a540684

Controller Review:
docs/project/phases/phase_7/history/operations/phase_7_p7_rw5_controller_bounded_independent_review_ja_20260830173339.md
SHA-512:
3b84a8745452abc99012235ae0dd2bf69e149da0cccf40a6328dd211b5808344bba0bb0ee9533ff4f2fc8fcb754865e42b084955bff1872a6e8d24618e3e3d57
```

## 2. Finding

```text
P7-CODEX-017:
Frontend Source変更後のnpm run buildが未実行で、FastAPI配信Static Bundleが
P7-RW5以前の旧実装のまま。Exact Handoffが要求したFrontend Build PASSを
実行せずP7-RW5-ACC-012をPASSとした。
```

## 3. Exact Work

P7-RW5-EはBuild Artifact反映だけを行う。

1. P7-RW5 ReturnとController Reviewを全文読む。
2. Project内Task-owned Temp／Cacheを用意する。
3. `frontend/`の既存Toolchainだけで`npm run build`を実行する。
4. Build出力先`src/margpa_runtime_llm/web/static/`の`app.js`、`index.html`および必要Assetが現行Frontend Sourceから生成されたことを確認する。
5. 配信`app.js`が次を反映していることを確認する。
   - Persistent Detailの`warning_codes`からNO_HIT Citationを再構成する。
   - Local Corpus Citationの`document_title`を表示できる。
   - Local Corpus Citationの`storage_display_path`を表示・Copyできる。
6. Buildが実行するTypecheck以外のCanonical Suiteを再実行しない。Controller Focused TestはBackend 82件／Frontend 19件PASS済みであり、Source変更がないため再実行不要。
7. Recovery AddendumとExact Return Addendumを作成する。

## 4. Explicit Prohibitions

- Backend／Frontend Source、Test、Schema、HeuristicまたはRuntime Logicを変更しない。
- `npm install`、Download、Network、Node切替を行わない。
- Git Read／Write、Backup、User `runtime_data/`、Provider Memory、Real Model、Real Browserへ触れない。
- Phase 7 Closure、Roadmap、Phase 8へ進まない。
- P7-RW5全体を再実装・再検証しない。
- Current TaskをFresh Taskとして初期化しない。

## 5. Exact Return

Returnには次だけを含める。

- `npm run build`のExit結果。
- 更新された配信Artifact一覧。
- 3 Markerの配信Bundle反映Evidence。
- Source／Test変更0件。
- Network／Install／Git／User runtime_data／Real Browser／Real Model Action 0件。
- Recovery Addendum Path。

最大Claimは`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。Controller Review待ちで停止する。
