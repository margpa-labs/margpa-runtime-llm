# Runtime動作・絶対Path境界 確認記録

- 文書ID: `runtime_and_absolute_path_verification`
- 状態: `verified_with_external_environment_pending`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 実施担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. 動作確認結果

Privacy Scrub後のMac環境で次を確認した。

```text
Default Test            : 181 passed／3 deselected
Ruff                    : Pass
Mypy                    : Pass／70 source files
Model Smoke on Mac Metal: 2 passed／1 skipped
```

Model Smokeの1 SkipはLightning用Profile Environment未指定による期待されたSkipである。

Sandbox内ではMetal Deviceが公開されず`llama_context`作成に失敗したが、Mac実機Execution Contextで再実行して2件Passした。Privacy ScrubによるMac Phase 1 Runtimeの機能破損は確認されなかった。

Lightning CUDA／CPUのNative Verificationは別Gateであり、未確認である。

## 2. Production Codeの絶対Path

次の管理対象を走査した結果、個人固有の`/Users/...` Pathは0件だった。

- `src/`
- `scripts/`
- `config/`
- Root Project Metadata／Lock／Ignore設定

Production Runtimeは個人固有Home PathをSourceへHard-codeしていない。

## 3. Test Fixture

`tests/`には`/Users/example/...`形式の架空Pathが存在する。これはNative ErrorからAbsolute PathをRedactするPrivacy Test Dataであり、実在するAccount情報ではない。

## 4. Local `.venv/`

`.venv/`にはPython仮想環境の仕様により、作成時環境の絶対Pathが自動生成される。

- `pyvenv.cfg`のBase Python Path
- Activate Scriptの`VIRTUAL_ENV`
- Console Entry PointのInterpreter Path
- Python ExecutableへのSymlink

`.venv/`は移植Artifactではなく、別環境でLockとSetup Recipeから再構築する。Git、ZIP、GitHub、公開物から除外する。

## 5. `models` Symlink

Project Rootの`models`はLocal Model Storageへの絶対Symlinkである。Production CodeのHard-codeではない。

SymlinkとTargetのModel本体はGit、ZIP、GitHub、公開物から除外し、Model配置規約と復元手順だけをManifestへ記録する。

## 6. 結論

```text
Managed Production Code : 個人固有絶対Pathなし
Tests                   : 架空Redaction Fixtureのみ
Local .venv             : 絶対Pathあり／正常／公開除外
Local models Symlink    : 絶対Pathあり／正常／公開除外
Mac Phase 1 Runtime     : Native Model Smoke Pass
Lightning Runtime       : Native Verification Pending
```

