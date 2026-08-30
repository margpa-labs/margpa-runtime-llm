# Phase 7 P7-RW5-E Frontend Distribution Artifact Build — Recovery Addendum

```yaml
document_id: phase_7_p7_rw5_e_frontend_distribution_artifact_build_recovery_addendum_20260830174333
document_type: package_recovery_addendum
document_state: frozen
language: ja
created_at: 2026-08-30 17:43 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_7
execution_scope: P7-RW5-E
parent_finding: P7-CODEX-017
```

## 1. Recovery Index Pointer

```text
P7-RW5 Return (Active Baseline, Rollbackせず保持):
docs/project/phases/phase_7/handoffs/phase_7_claude_no_hit_citation_persistence_and_local_corpus_identity_bounded_rework_exact_return_handoff_ja_20260830171200.md
SHA-512: 75d75e1d7bd0be041ffdb62014b8a50a275e040da248d9ab6e331479d395f1fb9d03c233b6e2f62a12cdc09b39451b509ae81e048c67de62bf42fe159a540684

P7-RW5 Recovery Index:
docs/project/phases/phase_7/history/index/phase_7_no_hit_citation_persistence_and_local_corpus_identity_p7_rw5_final_recovery_ja_20260830170958.md
SHA-512: 6a26cd5552351bd1f1e0cb5b88c81c75d52d691b5e2ed60b8933a9477ff7784cd7877e64c964f630b472723aea998e9bcf48877ff32e822e6042f988f474c211

Controller Bounded Independent Review:
docs/project/phases/phase_7/history/operations/phase_7_p7_rw5_controller_bounded_independent_review_ja_20260830173339.md
SHA-512: 3b84a8745452abc99012235ae0dd2bf69e149da0cccf40a6328dd211b5808344bba0bb0ee9533ff4f2fc8fcb754865e42b084955bff1872a6e8d24618e3e3d57

Exact Handoff (P7-RW5-E):
docs/project/phases/phase_7/handoffs/phase_7_claude_p7_rw5_frontend_distribution_artifact_build_exact_handoff_ja_20260830173339.md
SHA-512: 416f7bedb283dfffc614600e047fff5b9fe81f16dd305ce5d2a82974ca6fbc3d284d5912c859ef1eff9e86aee00dc68b0f67954ea1dda98a47b26948cbef6045
```

Digest照合: 3文書とも記載SHA-512と一致した。

## 2. 対象Finding

`P7-CODEX-017`（`major_mvp_blocker`）: Frontend Source変更後の`npm run build`が未実行のまま、FastAPI配信`src/margpa_runtime_llm/web/static/`が旧Bundleを配信し続けていた。P7-RW5-A/B/CのSource修正自体はController Reviewで妥当と確認済みだが、User実画面へ未反映のためPhase 7 Closure対象にできない、という指摘。

## 3. Root Cause再確認

P7-RW5 Package内でBackend／Frontend双方のCanonical Suite（`tsc`／`vitest`／`eslint`）は実行したが、`vite build`（Static Bundle生成）は実行しなかった。Frontend Test PASSは実装の正しさを検証するが、配信Artifactの更新はBuild実行なしには発生しない。この区別を見落としたことが直接の原因。

## 4. Exact Work（実施内容）

1. 本Addendumの親Baseline 3文書（P7-RW5 Return／Controller Review／本Exact Handoff）を全文読み、Digestを照合した（一致）。
2. `frontend/`の既存Toolchainのみで`npm run build`（= `tsc --noEmit && vite build`）を実行した。`npm install`・追加Download・Node切替は一切行っていない。
3. Build出力（`STATIC_ROOT = ../src/margpa_runtime_llm/web/static/`、`frontend/vite.config.ts`で固定済み）を確認した。

## 5. `npm run build` Exit結果

```text
> margpa-runtime-llm-frontend@0.0.0 build
> tsc --noEmit && vite build

vite v8.2.1 building client environment for production...
transforming...
✓ 56 modules transformed.
rendering chunks...
computing gzip size...
../src/margpa_runtime_llm/web/static/index.html    1.14 kB │ gzip:  0.39 kB
../src/margpa_runtime_llm/web/static/app.css      19.28 kB │ gzip:  4.66 kB
../src/margpa_runtime_llm/web/static/app.js      333.72 kB │ gzip: 93.99 kB

✓ built in 91ms
```

`tsc --noEmit`はErrorなく完了し（`&&`で`vite build`へ継続したことがそれ自体の成功Evidence）、`vite build`はException・Non-zero Exitなく完了した。

## 6. 更新された配信Artifact一覧

```text
src/margpa_runtime_llm/web/static/index.html   (1,145 bytes,   mtime 2026-08-30 17:37)
src/margpa_runtime_llm/web/static/app.css      (19,284 bytes,  mtime 2026-08-30 17:37)
src/margpa_runtime_llm/web/static/app.js       (333,721 bytes, mtime 2026-08-30 17:37)
```

Build前（Controller Reviewが指摘したStale状態）: 3 File共にmtime 2026-08-30 13:15、Frontend Source最終更新（17:01）より前。
Build後: 3 File共にmtime 2026-08-30 17:37、Frontend Source最終更新より後 — Current Sourceからの再生成を確認した。

`index.html`の`<script type="module" crossorigin src="/assets/app.js">`参照は不変で、FastAPI `/assets/app.js`配信経路との整合を維持している。

## 7. 3 Markerの配信Bundle反映Evidence

配信`app.js`をRead-onlyでGrepし、Controller Reviewが要求した3件（+関連i18n Key 1件）の文字列存在を確認した。

```text
$ grep -o "warning_codes" src/margpa_runtime_llm/web/static/app.js | head -1
warning_codes

$ grep -o "document_title" src/margpa_runtime_llm/web/static/app.js | head -1
document_title

$ grep -o "storage_display_path" src/margpa_runtime_llm/web/static/app.js | head -1
storage_display_path

$ grep -o "citationFieldTitle" src/margpa_runtime_llm/web/static/app.js | head -1
citationFieldTitle
```

- `warning_codes`: `persistentDetailProjection.ts`の`detailToMessages()`がNO_HIT Citationを`turn.citations.warning_codes`から再構成するCurrent実装が配信Bundleへ含まれることを確認（Build前のBundleは`warnings: []`固定だった、とController Reviewが指摘した箇所）。
- `document_title` / `storage_display_path`: `CitationsSection.tsx`のLocal Corpus Citation表示（Title行・実Path表示／Copy）がCurrent実装のまま配信Bundleへ含まれることを確認。
- `citationFieldTitle`: `translations.ts`に追加したja/en両Localeの新規i18n Keyが配信Bundleへ含まれることを確認。

これらはSource文字列の直接一致であり、配信Bundleの動作を保証するものではない。Build後のUser実画面確認（Browser Gate）は本Package範囲外であり、引き続きUser Gateとして未実施のまま残る。

## 8. Scope遵守の確認

```yaml
backend_source_files_changed: 0
frontend_source_files_changed: 0
test_files_changed: 0
schema_or_heuristic_changed: 0
canonical_suite_rerun: false   # 要求どおり未実施（Source変更なしのため）
network_actions: 0
npm_install_or_download: 0
node_runtime_switch: 0
git_mutation_actions: 0
git_read_only_actions: 0        # 本Packageでは git status/diff すら未実行（Addendum作成に不要だったため）
backup_actions: 0
user_runtime_data_access: 0
real_model_access: 0
real_browser_access: 0
phase_7_closure_claimed: false
roadmap_touched: false
phase_8_started: false
provider_memory_used: false
project_root_外_access: 0
```

Build実行によって生成された成果物は指定Static Root配下のみであり、`frontend/`配下に既存Toolchainのcompile cache用一時Directory（`frontend/.build_tmp/`、Node compile cache）が1件副次的に生成された。Project内・空のCacheのみでSource／Artifactへの影響はなく、Task-owned Project Root外への書込みではない。

## 9. Incident開示（透明性のための記録）

Build完了後、Exit結果の再確認を目的に`npm run build`を再実行しようとする過程で、Log Redirect先を`/tmp_build_rerun.log`（`/tmp/`ではなくFilesystem Root直下）と誤って指定したCommandを提案した。Userはこれを即座に拒否し（"Root直下であり、Project外への書込み・削除になります"）、Build再実行および新規Temp/Log作成/削除の一切を禁止した。

**重要**: 当該Commandは拒否されたためTool実行されておらず、Filesystem Root直下に実File・実Writeは一切発生していない。既に成立していた Section 5〜7 のBuild結果・配信Artifact状態に変更・影響はない。本Addendum以降、Build再実行・追加Temp作成/削除は行っていない（Section 6〜7の確認はすべて既存生成物へのRead-only操作のみ）。

## 10. 検証順・結果

```text
1. Baseline 3文書 全文読了・Digest照合          -> 一致
2. npm run build (tsc --noEmit && vite build)  -> 成功 (Exception/Non-zero Exitなし)
3. 配信Artifact mtime確認 (Read-only ls)         -> Source最終更新後に更新済みと確認
4. 配信Bundle 3 Marker + i18n Key確認 (Read-only grep) -> 4件とも検出
```

Controller FocusedTestは前Cycleで既にPASS済み（Backend 82件／Frontend 19件）であり、Source／Test変更がないため本Packageでは再実行していない（Exact Handoff §3-6の指示どおり）。

## 11. Rework Cycle

不要。`P7-CODEX-017`はBuild実行と配信Artifact更新の確認により解消したと判断する（最終判定はController Review）。
