# ADR 0002 Model本体の外部配置

- 文書ID: `adr_0002_external_model_storage`
- 状態: `accepted`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 正本言語: 日本語
- 関連文書: [model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)

## Context

GGUF Modelは数百MBから数GBあり、通常のGit Repositoryに含める用途に適さない。

ユーザーは既存Modelを`/path/to/models/`で一元管理している。LLaVA等の他Modelと、MARGPA Runtime LLM専用Modelを混在させずに管理したい。

一方、Project内からは`./models/...`として分かりやすく参照したい。

## Decision

Model本体の物理Rootを次とする。

```text
/path/to/margpa-models/
```

Project直下の`models`はPOSIX Symbolic Linkとする。

```text
margpa-runtime-llm/models
  → /path/to/margpa-models
```

物理構造：

```text
models/
├─ main/<model>/<format>/
├─ guard/<model>/<format>/
├─ judge/<model>/<format>/
├─ classifier/
├─ embedding/
├─ reranker/
├─ shared/
└─ vision/
```

Symbolic LinkはLocal便利用とし、Runtimeは設定可能なModel Rootを正本とする。

Model本体とSymbolic LinkはGit管理対象外とする。

## Reason

- 他ProjectのModelと分離できる
- Main、Guard、Judgeを視覚的に管理できる
- GGUF、MLX、Transformersを将来分離できる
- 同じProject内に複数Modelを置ける
- Repositoryを巨大化させない
- Model Licenseと再配布問題を減らせる
- LocalとCloudでModel Rootを交換できる

## Finder Aliasを不採用とする理由

Finder AliasはFinder上では解決できるが、Pythonや通常のFilesystem PathからDirectoryとして透過的に扱えない。

そのため、当初のFinder Aliasを削除し、POSIX Symbolic Linkへ置換した。

## Consequence

Positive：

- Projectから`models/main/...`として参照できる
- Model本体をRepository外へ保てる
- Local利用が分かりやすい
- Cloudでは設定変更で別Rootを利用できる

Negative／Risk：

- Absolute Linkは他PCで壊れる
- Symbolic LinkをGitへCommitしてはいけない
- RuntimeがLinkだけに依存するとPortabilityが下がる
- macOSとLinuxのCase Sensitivity差に注意が必要

## GitHub方針

GitHubには次だけを掲載する。

- Model ID
- Distribution／Upstream
- File名
- Quantization
- Download手順
- Placement手順
- Hash検証手順
- License
- Sample Config

Model Binaryは掲載しない。

## Follow-up

実装時に次を用意する。

- Model Root設定
- Model Registry
- Missing Model Error
- Hash検証
- `.gitignore`
- GitHub向けDownload手順
