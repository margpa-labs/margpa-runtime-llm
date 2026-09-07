# Phase 9-1 Claude Package 1 Lightweight Independent Judge Selection／Acquisition Exact Return

```yaml
document_id: phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_return_handoff_20260902132113
document_type: exact_return_handoff
document_state: frozen_return_ready
language: ja
created_at: 2026-09-02 13:21:13 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-1
provider: Claude
role: 設計者兼実装者役
governing_handoff: docs/project/phases/phase_9/handoffs/phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_handoff_ja_20260902121740.md
governing_handoff_sha512: 01b42625368a808d2006f0c999ed72d591d1de3c9eaba51983fed8341f9f3f8d8f9f519b7998bca78be95dfeb7135f4908def721baffb5c0bb7878945bb52616
maximum_claim: P9_1_LIGHTWEIGHT_INDEPENDENT_JUDGE_ARTIFACT_ACQUIRED_CANDIDATE_FOR_PACKAGE_2
package_2_ready: true
real_model_load_by_this_package: false
network_action_by_this_package: true
git_action_by_this_package: none
backup_action_by_this_package: none
```

## 1. 結論

Package 1(軽量独立Judge候補の比較・選定・公式Artifact取得)を完遂した。Package 2(共通Judge基盤診断・修復)へは入らず、Exact Returnとして停止する。

選定結果は当初提案の`Qwen3-1.7B`から、User指摘(Judge専用モデルか否か／Main・Guardと同じQwen系列である点)を受けて再調査し、**`Gemma 4 E2B`(公式`google/gemma-4-E2B-it-qat-q4_0-gguf`)**へ変更した。Artifact取得・Digest固定・最小Registry登録・Focused／Canonical Static Checkまで完了している。

Selene置換・廃止は行っていない。SeleneのModel Definitionおよび既存Registry Entryは無変更のまま保持している。

## 2. Shortlist比較と選定理由

| 候補 | Base/系列 | 用途特化 | 日本語適性 | サイズ(Q4級)／ライセンス | 公式Artifact | 採否 |
|---|---|---|---|---|---|---|
| Qwen3-1.7B | Qwen3(Main=Qwen3-4B, Guard=Qwen3Guardと同系列) | 汎用 | 実績十分 | 1.83GB／Apache 2.0 | 公式GGUF直配布 | 却下(User指摘: Main/Guardとの系列一致がPackage 2の診断上のリスク) |
| Flow-Judge-v0.1 | Microsoft Phi-3.5-mini系(独立系列) | **LLM-as-a-Judge専用リリース**(Rubricベース構造化採点にFine-tuning済み) | モデルカードに「英語データのみでFine-tuning、多言語は将来課題」と明記 | 3.8B／Apache 2.0 | 公式GGUF(`flowaicom/Flow-Judge-v0.1-GGUF`) | 却下(日本語適性の明示的懸念) |
| M-Prometheus-3B／7B | **Qwen2.5-3B／7Bベース**(調査で判明、Qwen系列) | Judge専用 | 未確認 | ライセンス"other"で不明瞭、Qwen2.5-3Bベースは非Apache | 公式Safetensors、GGUFはCommunity | 却下(Qwen系列一致＋ライセンス不明瞭の二重懸念) |
| **Gemma 4 E2B**(選定) | Google Gemma系(Qwen・Llamaいずれとも独立) | 汎用(Judge専用ではない) | 実測: 兄弟モデルE4BがJCommonsenseQAで93.5%、日本語特化9Bモデルを上回る | 3.35GB(QAT Q4_0)／Apache 2.0＋Prohibited Use Policy | 公式GGUF(`google/gemma-4-E2B-it-qat-q4_0-gguf`、Google自身が直接公開) | **選定** |

選定理由:

1. Main(`main.qwen3-4b-q4-k-m`)・Guard(`guard.qwen3guard-gen-0.6b-q8-0`)がいずれもQwen系列であるため、軽量Judgeを別系列(Google Gemma)にすることで、Package 2の診断目標(「Qwen固有の不具合」と「真の共通Judge基盤バグ」の切り分け)に対する診断力を高められる。
2. 実測日本語ベンチマーク根拠(JCommonsenseQA)が候補中で最も具体的。
3. Google自身が直接公開する公式GGUF(QAT Q4_0)であり、Selene(bartowski経由のCommunity量子化)より公式性が高い。
4. ライセンスがApache 2.0で明瞭(Prohibited Use Policyは無償Local R&D／Portfolio用途と矛盾しない一般的違法用途制限)。

不採用理由も含めて表に残した。Popularityだけでの選定ではない。

トレードオフとして正直に記録する: Gemma 4はJudge専用モデルではない(Flow-Judge-v0.1のみが専用リリース)。また`gemma4` architectureはこのRuntimeでLoad実績がない(Selene=`llama`、Main/Guard=`qwen3`は既存実績あり)。Real Model LoadはPackage 2の範囲であり、Package 1では未検証。

## 3. 実機ハードウェア確認(User指摘への対応)

Selene(8B, 5,732,992,896 bytes)使用時にMain Modelが不安定化した既知Incident(`phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md` §3)を踏まえ、実機を確認した。

```text
Model: MacBook Pro (Mac14,9) / Apple M2 Pro / 10 core (6P+4E)
Total Memory: 16 GB
```

Gemma 4 E2Bは「5B総パラメータ中、実稼働は2.3B(Per-Layer EmbeddingはFlash側常駐でRAM非占有)」という設計であり、QAT(量子化を意識した学習済み)Q4_0で3.35GB(Selene比 約58%)。コミュニティ報告値は4bit時で約5GB RAM。16GB統合メモリでMain Model(Qwen3-4B, Q4_K_M)と同時稼働させても、Selene級の破綻リスクは相対的に低いと判断できる(実稼働検証はPackage 2)。

## 4. 選定Artifact識別情報

```text
Model ID (upstream): google/gemma-4-E2B-it
GGUF Distribution Repository: google/gemma-4-E2B-it-qat-q4_0-gguf (Google公式)
File: gemma-4-E2B_q4_0-it.gguf
Format: GGUF
Quantization: Q4_0 (Quantization-Aware Trained checkpoint)
Byte Size: 3,349,516,256 bytes (HTTP HEAD x-linked-size / content-length 双方で確認)
SHA-512: 54b1e06eea3bcfd2f94d2a0195366830d25d63dc15dd2484fa7cd35f82cfd4b8503702ac3a1a3772775284e3d9a5531a54f1a9b8e3eaa16417d84eae360c76ad
  (取得後 shasum -a 512 で算出、TOML登録値と一致確認済み)
License: apache-2.0 (GGUF内 general.license メタデータでも確認)
  License Link: https://ai.google.dev/gemma/docs/gemma_4_license
Download Source: https://huggingface.co/google/gemma-4-E2B-it-qat-q4_0-gguf/resolve/main/gemma-4-E2B_q4_0-it.gguf
Local Path: /Users/yukitakagi/models/margpa-runtime-llm/models/judge/gemma-4-E2B_q4_0-it/gguf/gemma-4-E2B_q4_0-it.gguf
  (models/ は既存Symlink経由でProject Root外の設定済みModel Artifact Root)
```

GGUFヘッダー(Key-Value Metadataのみの純粋読み取り、`gguf` Pythonパッケージ使用、Real Model Load・推論は未実施)から直接確認した値:

```text
general.architecture = "gemma4"
general.size_label = "4.6B"
general.license = "apache-2.0"
gemma4.context_length = 131072
tokenizer.chat_template = present (Google Gemma 4 Canonical Chat Template, jinja2, GGUF内蔵)
general.quantization_version = 2
general.file_type = 2
```

同一リポジトリ内の`gemma-4-E2B-it-mmproj.gguf`(Multimodal投影用, 987MB)は、テキストJudge用途に不要のため取得対象から除外した。

## 5. Work Unit別Disposition

```text
P1-WU-01 Current Runtime Compatibility Freeze: DONE
  既存Model Registry(config/models/*.toml)、DirectoryModelDefinitionRegistry、
  Model Artifact Root解決(config/application.toml → models/ symlink →
  /Users/yukitakagi/models/margpa-runtime-llm/models)をTargeted確認。
  Source実装は変更せず、Selene/Qwen3Guard TOMLスキーマをそのまま踏襲。

P1-WU-02 Shortlist／Decision: DONE
  4候補(Qwen3-1.7B, Flow-Judge-v0.1, M-Prometheus-3B/7B, Gemma 4 E2B)を
  公式Model Card/Licenseベースで比較。User指摘を受けて一度Qwen3-1.7Bから
  Gemma 4 E2Bへ選定変更。§2参照。

P1-WU-03 Artifact Acquisition: DONE
  公式Source直接ダウンロード(curl)。Byte Size / SHA-512固定。§4参照。

P1-WU-04 Minimal Registration Preparation: PARTIAL(意図的境界)
  実施: config/models/gemma_4_e2b_it_q4_0.toml をSelene/Qwen3Guardと同一
  スキーマで新規追加。DirectoryModelDefinitionRegistryが自動検出・resolve
  できることをFocused Testで確認(regression-guard済み、§7参照)。
  未実施(意図的、Package 2範囲): ProviderSelectionController の選択可能
  Provider Catalog、Stage Budget Profile、Judge Prompt Template Manifest
  への配線。理由は§8参照。この部分はSource Mutation 0のまま。

P1-WU-05 Recovery／Exact Return: DONE(本書)
```

## 6. Project側変更Path

```text
新規: config/models/gemma_4_e2b_it_q4_0.toml
変更: tests/unit/runtime_model_control/test_model_definition_registry.py
  (model_key集合Assertionへ新規Entry追加 + 新規Focused Test 1件追加)
```

上記2件以外のSource／Test変更は0件。Selene、Qwen3Guard、Main、既存Provider Selection、既存Judge Dispatch経路は完全に無変更。

## 7. Static Check結果

Focused(新規Registry Entryのみ):

```text
pytest tests/unit/runtime_model_control/test_model_definition_registry.py -q
  → 5 passed (新規1件含む)
mypy tests/unit/runtime_model_control/test_model_definition_registry.py
  → Success: no issues found
ruff check / ruff format --check (同ファイル)
  → All checks passed / already formatted
```

Regression-guard(新規Testの真の検出力確認):

```text
1. config/models/gemma_4_e2b_it_q4_0.toml をScratchpadへBackup
2. sha512値を同じ128桁で1文字だけ変更(パターン検証を回避しつつ値を破壊)
3. 新規Test単体実行 → AssertionErrorで確実に失敗することを確認
4. Backupから復元 → diffでByte-identicalを確認
5. Registry Test 5件を再実行 → 5 passed
```

Canonical(Project全体、Resource残存につき実施):

```text
pytest -q (Backend全体)
  → 2 failed, 2215 passed, 7 deselected (77.33s)
  失敗2件はいずれも tests/unit/adapters/runtime_model_control/
  test_dedicated_role_adapters_production_wiring.py の既存Selene関連
  (test_selene_authority_granted_preflight_load_and_evaluate_wire_correctly,
  test_selene_role_adapter_composes_with_the_real_lifecycle_manager)。
  phase_index_ja.md記載の既知Baseline(2214 PASS/2 FAIL/7 DESELECTED)と
  一致(2215 = 2214 + 本Package新規Test1件)。Package 1由来の新規Regressionは0件。

mypy src tests
  → Found 45 errors in 5 files (checked 558 source files)
  全てguardrail_governance/judge_live_integration関連の既存Error。
  phase_index_ja.md記載の既知Baseline「Mypy 45 Errors」と一致。
  本Packageが触った2ファイルにErrorなし。

ruff check .
  → All checks passed!

ruff format --check .
  → 7 files would be reformatted (既存Drift、本Package未着手ファイルのみ:
    qwen3guard_adapter.py, guardrail_governance.py, judge_live_integration.py,
    conversation_generation.py, judge_output_decoder.py, cancellation.py,
    role_lifecycle_manager.py)。本Packageの新規/変更ファイルは含まれない。
```

## 8. Package 2 Exact First Action

Judge基盤配線(Provider Selection Catalog / Stage Budget / Prompt Template)はPackage 1の権限外(§6禁止事項「Package 2のJudge基盤修復、Inference比較またはUI実装」)のため、意図的にSource Mutation 0のまま残した。Package 2は以下の3箇所から着手する。

```text
1. src/margpa_runtime_llm/modules/runtime_model_control/application/
   provider_selection_controller.py
   - Line 23: SELENE_JUDGE 定数と並ぶ GEMMA_E2B_JUDGE = "judge.gemma-4-e2b-it-q4-0" を追加
   - Line 83-115: RoleProviderSelection の ModelRole.JUDGE Candidate一覧へ
     Gemma Entry(display_name, model_key, artifact_relative_path,
     artifact_digest_sha512, model_family="gemma4")を追加
     (artifact_digest_sha512は本書§4のSHA-512をそのまま使用可能)
   - Line 149-151: 必要であればConfigured Providerの選択肢として反映

2. src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py
   - Line 88-93 (LOCAL_MACOS_SELENE_JUDGE_BUDGET) と同型で
     LOCAL_MACOS_GEMMA_E2B_JUDGE_BUDGET を model_copy() 定義
   - Line 114-115 の provider_id 分岐へ追加

3. config/judge_templates/selene/ (manifest.json,
   project_derived_multi_criterion_prompt_v1.txt) と同型の
   config/judge_templates/gemma_4_e2b/ を新規作成
   (Gemma 4 Canonical Chat Template がGGUF内蔵のため、
   Prompt Template設計はSeleneと同一方針で流用可能と推定、要検証)

その後、共通Judge基盤診断(§4 of the underlying history evidence:
Criteria Selection, Semantic Snapshot, Prompt Build, Inference Result,
Strict Decode, Result Projection, Role Lifecycle, Mode Transition)を
Built-in / Main-shared Qwen / Selene / Gemma 4 E2B の4 Provider比較
Matrixで開始する。
```

## 9. Network／Artifact／Temporary Process Inventory

```text
Network Access: 公式候補調査(WebSearch/WebFetch) + 1件のArtifact Download
  (huggingface.co、既存huggingface_hub 1.28.0/.venv同梱、追加Install 0)
Artifact取得: gemma-4-E2B_q4_0-it.gguf 1件のみ(3,349,516,256 bytes)。
  mmproj.gguf(987MB)は取得除外。
Real Model Load / Inference: 0件(GGUFヘッダーのKey-Value Metadata読み取り
  のみ、Weight materializationなし)
Temporary Process: バックグラウンドDownload(curl)は完了済み、残存プロセス0
Dependency Install/Upgrade: 0件
Git Action: 0件(add/commit/push未実施、本Return自体もUnstagedのまま)
Backup Action: 0件
User runtime_data接触: 0件
Selene/Qwen3Guard/Main Artifact: 削除・上書き・変更 0件
```

## 10. Recovery Index

```text
本Return: docs/project/phases/phase_9/handoffs/
  phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_return_handoff_ja_20260902132113.md
governing Handoff: docs/project/phases/phase_9/handoffs/
  phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_handoff_ja_20260902121740.md
Package 2 governing Handoff(既存, 未開始): docs/project/phases/phase_9/handoffs/
  phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_handoff_ja_20260902121740.md
新規Registry Entry: config/models/gemma_4_e2b_it_q4_0.toml
新規/変更Test: tests/unit/runtime_model_control/test_model_definition_registry.py
Phase Index(未更新、次のTaskでCurrent Stateへ反映が必要):
  docs/project/phases/phase_9/phase_index_ja.md
```

`phase_9_index_ja.md`の`## 3. Canonical Phase 9 Documents`と`## 1. Current State`への本Return追記は、本書のScope外(Handoff §6で許可されるのはRecovery Docs作成のみで、Phase Index更新は明示的許可対象に含まれていない)として未実施。次のTask(Package 2、またはPhase Index専用の軽微な更新Task)側で反映する。

## 11. Claim

```text
Maximum Claim: P9_1_LIGHTWEIGHT_INDEPENDENT_JUDGE_ARTIFACT_ACQUIRED_CANDIDATE_FOR_PACKAGE_2
```

Load／Inference／Judge成立は主張しない。Phase 9-1 CompleteまたはClosureは主張しない。Package 2は本書§8のExact First Actionから、別Exact Handoffを起点に再開する。

## 12. True Stop 判定

本Packageの実行中止条件(§7)はいずれも発生していない。License/Provenance不確定、Credential/Payment要求、Artifact Root解決不能、Canonical State競合、Provider Resource Hard Stopのいずれにも該当しないため、WU-01〜WU-05を全て完了した上での正常Returnである。
