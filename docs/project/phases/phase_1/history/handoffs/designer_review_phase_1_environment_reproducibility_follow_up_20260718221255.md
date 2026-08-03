# Phase 1 Environment再現性 Follow-up 設計レビュー

- 文書ID: `designer_review_phase_1_environment_reproducibility_follow_up`
- 状態: `accepted_phase_1_a_complete`
- 作成日時: `2026-07-18 22:12:55 JST`
- 更新日時: `2026-07-18 22:12:55 JST`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260718221255.md](../documentation_index_20260718221255.md)
- Review対象: [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md)
- Previous Review: [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](designer_review_phase_1_environment_and_metal_smoke_20260718212502.md)
- supersedes: `designer_review_phase_1_environment_and_metal_smoke_20260718212502.md`

## 1. Review Conclusion

Phase 1-AのEnvironment再現性Follow-upを合格とする。

前回ReviewでRequired Follow-upとした2項目は完了した。

```text
Required Follow-up 1: uv実行Fileの永続配置            : Pass
Required Follow-up 2: Metal Source Build Recipe永続化 : Pass
```

Recommended Follow-upとしていた次の2項目も完了した。

```text
Opt-in model_smoke Test : Pass
計測Fieldの分離         : Pass
```

重大または中程度の問題は確認されなかった。

これにより、Phase 1-AのEnvironment Setup、Python／Venv／Dependency、llama.cpp Metal Backend、Qwen3-4B実Model Smokeおよび再現性確認を完了と判定する。

Phase 1-B、Phase 2、Governance、RAG、Agentは未着手であり、本Reviewはそれらの実装を解禁しない。

## 2. Independent Verification

設計者役担当Taskから、Follow-up報告、Project内File、現在Environmentおよび実Modelを独立確認した。

### 2.1 uv／Login Shell／Lock

新規Zsh Login Shellから次を確認した。

```text
command -v uv          : <USER_HOME>/.local/bin/uv
uv --version           : uv 0.11.29
Architecture           : aarch64-apple-darwin
uv lock --check        : Pass／117 packages resolved
uv sync --frozen       : Pass
uv sync --offline      : Pass／115 packages checked
```

`uv`および`uvx`はUser Scopeの永続Pathへ配置され、別Taskと通常Login Shellから利用可能になった。

### 2.2 Environment／Static Verification

```text
Python                  : CPython 3.13.14
Architecture            : arm64
GIL                     : enabled
Venv                    : Project Root/.venv
Direct Dependency       : Exact Version一致
Out-of-scope Package    : 未導入
llama-cpp-python        : 0.3.34
GPU Offload             : supported
Backend System Info     : MTLあり
bash -n                 : Pass
Ruff Check              : Pass
Ruff Format Check       : Pass／18 files
mypy --strict           : Pass／18 source files
Default pytest          : 2 passed, 1 deselected
```

`uv.lock` SHA-256はFollow-up報告と一致した。

```text
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

### 2.3 Opt-in実Model Smoke

Sandbox外で明示的に`model_smoke`を実行した。

```text
pytest -m model_smoke : 1 passed, 2 deselected
```

次を独立確認した。

- Local Qwen3-4B GGUFを暗黙Downloadせずに使用
- Apple Silicon／Metal Backend
- GPU Offload
- Model Load
- Chat Template Metadata
- Japanese Generation
- Streaming開始とConsumer-side Close
- Close後の再Generation
- Stop Sequence
- Explicit Model Close／Unload経路

通常の`pytest`では`model_smoke`が除外され、明示指定時だけ大型ModelをLoadする構成も成立している。

## 3. Setup Recipe Review

対象：

[setup_macos_arm64_metal.sh](../../scripts/setup/setup_macos_arm64_metal.sh)

次を確認した。

- `set -euo pipefail`を使用する
- macOS／ARM64以外では非Zero Exitとする
- Xcode Command Line Tools／Apple clangを事前確認する
- PATH上の`uv 0.11.29`を確認する
- `uv.lock`を変更せず`uv lock --check`を実行する
- uv Managed CPython `3.13.14`を指定する
- `llama-cpp-python==0.3.34`をSource Buildする
- `CMAKE_ARGS=-DGGML_METAL=on`を対象の`uv sync` Processだけへ設定する
- Cloud／CUDA ProfileやApplication CoreへMetal Flagを伝播しない
- `--clean-source-build`では存在しないTarget Venvを要求する
- `--no-cache`によるClean相当Build経路を持つ
- `--smoke`指定時だけLocal ModelをLoadする
- Model Artifactを暗黙Downloadしない

Platform Guard、Metal Flag Scope、Dependency固定および失敗時の非Zero Exitは、現在のArchitecture／ADRに適合する。

## 4. Fresh Build Evidenceの扱い

Follow-up報告には、新規Temporary Venvと`--no-cache`を使用したFresh／Clean相当Buildの成功証跡がある。

設計者役担当Taskでは、再Downloadと全Native Buildを伴う同一Fresh Buildを重ねて再実行していない。

代わりに次を独立確認した。

- Setup Recipeの静的検査
- 現在EnvironmentのExact Version検査
- Login ShellからのLock／Offline Sync
- Metal／GPU Offload検査
- opt-in Qwen3実Model Smoke
- Follow-up報告のBuild条件、結果、Native Library Hash

上記を総合し、Fresh Build証跡を受理する。

## 5. Known Non-blocking Item: 通常Setup時のNative再Build

Setup Recipeは通常実行時にも次を指定する。

```text
--no-binary-package llama-cpp-python
--reinstall-package llama-cpp-python
```

このため、通常のEnvironment同期でも`llama-cpp-python`を毎回Sourceから再Buildする。

### 5.1 Impact

- Setupの実行時間が長くなる
- CPU使用率、発熱および消費電力が増える
- Dependency変更がない場合にもNative Buildが発生する

一方、毎回`GGML_METAL=on`を明示したSource Buildになるため、現時点ではNative Build条件の再現性を優先した保守的な構成として妥当である。

Phase 1-AのBlockerにはしない。直ちに修正する必要もない。

### 5.2 Future Recommendation

実運用でSetup頻度やBuild時間が問題になった場合、次の経路分離を検討する。

```text
Normal Sync
  └─ Lock済みEnvironmentを同期し、不要なNative再Buildを避ける

Explicit Native Rebuild
  └─ llama-cpp-pythonをGGML_METAL=onで明示的に再Buildする

Fresh Reproducibility Build
  └─ 新規Venv＋使い捨てCacheで完全検証する
```

候補Interfaceは`--rebuild-native`等であるが、具体名とDefault動作は将来の設計判断とする。

分離する場合も、Metal Build Flag、Version固定およびFresh再現性検証経路を失ってはならない。

## 6. Other Known Non-blocking Item

Qwen3へ`/no_think`を指定しても、空の`<think></think>`相当Tagが生成結果に残る場合がある。

これはPython／Metal／Model Loadの問題ではない。

Production Model Adapter、Raw Output、Display OutputおよびAudit LogのContract設計時に扱いを決める。

## 7. Phase Boundary

完了：

```text
Phase 1-A
  Environment Setup
  Python 3.13.14／Project .venv／uv 0.11.29
  Dependency Lock／Exact Version Verification
  llama-cpp-python Metal Source Build Recipe
  Qwen3-4B Model Load／Generation Smoke
  Streaming／Consumer-side Stop Probe
  Explicit Close／Unload Probe
  Opt-in model_smoke Test
  Fresh／Clean相当Build Evidence
```

未着手：

```text
Phase 1-B
  Model Port／Capability
  Generation Request／Result／Streaming Chunk
  Stop／Finish Reason／Error Contract
  llama.cpp Production Adapter
  Model Registry
  Config Schema／Generation Default
  Production CLI
```

「Phase 1-A完了」と「Phase 1全体完了」を混同しない。

## 8. Review／Index作成運用

今後、設計者役が実装報告等の正式Reviewを完了した場合は、原則として同じ作業単位で次の2文書を新規作成する。

1. Review結果を記録する新TimestampのReview文書
2. そのReviewと対象StatusをCurrent Document Setへ反映する新Timestampの`documentation_index`

旧Reviewと旧Indexは上書きしない。

新Indexでは、旧Review、旧Statusおよび旧Indexの状態と後継関係を示す。

## 9. Next Gate

次にPhase 1-Bへ進む場合は、次の順序を基本とする。

1. Model Port／Capability／Request／Result等の詳細設計
2. llama.cpp Production Adapterの責務境界確定
3. Config／Registry／CLIのMVP境界確定
4. 実装担当への新しいHandoff作成
5. ユーザーによるPhase 1-B実装許可
6. 実装
7. 実装Status作成
8. 設計Reviewと同時に最新Index作成

## 10. Authorization Boundary

このDocumentはPhase 1-A Follow-upの受入結果と、次段階へ進むための設計上のGateを記録する。

Phase 1-B実装、Setup Recipe変更、Dependency変更または追加Package Installを自動的に解禁するものではない。

