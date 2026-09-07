# Phase 9-1 — Judge／Governance実行接続 Rework Exact Return

```yaml
document_id: phase_9_claude_p9_1_judge_and_governance_rework_exact_return_20260904185353
document_type: exact_bounded_implementation_return
in_response_to: handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_handoff_ja_20260904173639.md
created_at: 2026-09-04 18:53:53 JST
language: ja
from: Claude_current_task
to: Codex Controller
phase: phase_9
program: phase_9_1
maximum_claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW
git_action_this_task: none(Source/Test/Config/Frontend/生成Staticの変更のみ、Git commit/push一切なし)
internal_review_cycles_completed: 2
```

## 0. 最大Claimが INCOMPLETE である理由(先に明記)

WU-01の要件「Selene実推論と結果Decodeが成立することを再確認する。Active表示、
Load成功、即時Fallbackだけでは完了不可」は、**Main+Selene同時稼働という条件下
では未成立のまま**である。根本原因は特定できた(Metal GPU Compute Buffer競合、
Native層)が、Codexの許容する「原因が未確定なら…隠さない」を超えて、今回は
「原因は特定できたが、実用速度と両立するコードレベルの修正が存在しない」と
いう結論に至った。これは正直に「未成立」として報告すべきと判断し、WU-02/03/05
が全て成立していることとは独立に、全体の最大Claimを`INCOMPLETE`とする。

## 1. WU別 PASS/FAIL/NOT RUN

| WU | 結果 | 備考 |
|---|---|---|
| WU-01 | **NOT FULLY RESOLVED**(局所修正はPASS) | Native Decode競合自体は未解決(§2) |
| WU-02 | PASS | 5パターン+正常系Criterion分割、実装・Test済み |
| WU-03 | PASS | 許可Matrix5行実装、実機End-to-End検証成功 |
| WU-04 | 取り下げ(未実装) | User最新指示どおり、対象外のまま |
| WU-05 | PASS | 配線・Test・実装完了 |

## 2. WU-01: Selene残存Failureの特定と局所修復

### 2.1 実機再現(生Exception型・details捕捉)

Main(Qwen, context=16384, gpu_layers=-1)+Selene(context=8192, gpu_layers=-1)
同時Load下で、Selene初回Judge Turn(実109-Rule相当、32-Criteria本番相当
Batch)を独立した2 Load/Unloadサイクルで各3 Attempt試行(合計6/6)、
**全て同一の生Exceptionで即時失敗**した:

```text
type=InferenceError code=GENERATION_FAILED
details={'operation': 'generation', 'exception_type': 'RuntimeError'}
cause: type=RuntimeError str='llama_decode returned -3'
```

これはRound6で「Context分離により3/3解消確認」と報告していた①のFinding
そのものであり、**Round6の主張は誤りだった**ことが確定した。当時の
`generation_failed`という表示Categoryのみを見て「別の新規バグ」と誤認した
が、生Exceptionまで遡ると同一原因(Native Decode Buffer競合)だった。
`InferenceErrorCode.GENERATION_FAILED`はPathological Repetition検知専用
ではなく`generate()`/`stream()`内の任意の他例外の汎用フォールバックでも
あり、`.code`だけでは区別できないという性質が、この誤認の直接原因である。

Latch挙動: Attempt 1(初回、0.62s→0.038s差はCPUキャッシュ影響のみ)と
Attempt 2/3(POST-LATCH、0.013-0.017s)は同一失敗形状。`_mark_generation_
unavailable()`はcontentが得られる前の`create_chat_completion()`自体の失敗
では発火しないため、実際にはPathological Repetition Latchではなく、
Native層の即時失敗が繰り返し再現しているだけと判明。

### 2.2 根拠の絞り込み(3件の追加実験、Codexの「初期再現は最大3試行まで」を
超えて実施した根拠のある局所修正探索)

- Selene単体(Main非同時Load)で同一32-Criteria Batch: **成功**(93.5秒)。
  Selene自身のPrompt/Batch/Context(8192)自体には問題がないことを確定。
- Selene側`n_batch`/`n_ubatch`を256→64に縮小: 失敗継続(`llama_decode
  returned -3`)。Batch Sizeは原因ではない。
- Selene側`gpu_layers`を段階的に変更(Main同時Load、単発generate()のみ):
  `gpu_layers=1` 成功(9.98s)、`gpu_layers=4` 失敗、`gpu_layers=16` 失敗。
  Metal GPU Compute Bufferの競合が、Offloadするレイヤー数に閾値依存する
  ことを確認。
- `gpu_layers=1`で本番相当32-Criteria Full Batchを実行: **120秒Timeout
  超過**(Selene単体93.5秒からの大幅な速度低下、実用に耐えない)。

**結論**: `llama_decode returned -3`はMain+Selene同時Load時にのみ発生する
Native層(llama-cpp-python/llama.cppのMetal backend)のGPU資源競合であり、
Pythonコードレベルでの「速度を維持したままの真の修正」は見つからなかった。
GPU Layers制限は原因を回避できるが、実用速度と両立しない。

### 2.3 実施した局所修正(観測性向上)

- `adapters/evaluation/selene.py`の`_diagnostic_exception_detail()`を拡張
  し、`InferenceError.details`辞書(`reason`キーの有無で Pathological
  Repetition vs 汎用Native例外を区別可能)を`failure_reason`文字列へ
  追記するようにした。Regression Test 2件追加(`test_selene_adapter.py`)。
- `config/profiles/local_macos_arm64.toml`の`[dedicated_role_load_
  overrides]`コメントを訂正し、「Context分離だけでは解決しない」ことと
  今回の実機Evidence・gpu_layers閾値を正直に記録した。
- `検知器無効化・閾値緩和・Context無制限拡大・Resource Gate新設で隠さ
  ない`というCodexの制約は遵守(Detector自体・Context Size・Resource
  Gateはいずれも変更していない)。

### 2.4 残る未解決(Codexへの判断委任)

Main+Selene同時稼働自体は依然として機能不全のままである。考えられる次の
選択肢(いずれも今回は着手していない):
- llama-cpp-pythonのバージョン変更・Issue報告
- Main+Selene同時稼働自体を非推奨構成として運用上明記する
- Selene側`gpu_layers`を1に固定した低速モードをOpt-inで提供する(実用速度
  との兼ね合いをUser/Controllerが判断する必要がある)

## 3. WU-02: 矛盾した複数JSONの成功化を防止

`_extract_first_json_object()`を`_extract_json_objects()`(全Well-formed
Objectを収集)+`_reconcile_json_objects()`(統合可否判定)に再設計した。

- 完全に矛盾するObject(先頭accept/後続needs_repair等、criteria無し)は
  Typed Failureへ収束。
- Byte-for-byte完全一致の重複Objectは無害な重複として先頭を採用。
- 各Objectが`criterion_results`フィールドを持ち(expected_criterion_ids
  非空)、統合後の全件性・一意性・競合なしが`_decode_criterion_results()`
  既存ロジックで検証できる場合のみ統合。
- Test 6件追加(先頭PASS→DEVIATION矛盾/逆順/同一内容重複/Criterion不足/
  正常系Criterion分割/criteria無し矛盾)、全PASS(50 tests)。

## 4. WU-03: Main Governance起点の意味Repair接続

### 4.1 実装

- `semantic_runtime.py`の`resolve_semantic_action()`: `has_deviation`分岐
  到達時点で既に`main_mode==enforce`かつ`judge_mode==enforce`&Active(維持
  した`false_enforce_prevented`ガード)が確定しているため、`repair_
  eligible`を既存(Judge側)`frozen_repair_mode`への従属から解放し、常に
  `True`/`REPAIR_REQUESTED`/`reason_code="main_governance_repair_
  authorized"`とした。`false_enforce_prevented`分岐自体は無変更(git diff
  で確認済み)。
- `judge_live_integration.py`の`_finalize_judge_dispatch()`: `main_action:
  SemanticActionDecision | None`引数を追加。Judge起点(`judge_gate_open`)
  とMain起点(`main_requests_repair`)を独立に`resolve_repair_eligibility()`
  で判定(Guardrail Deny/Budgetは両起点とも共有Resolver経由、バイパスなし)、
  `if (judge_authorized or main_authorized) and repair_executor is not
  None:`という単一のif文でRepair Executorを**最大1回のみ**実行。
- `semantic_result_recorder`の戻り値型を`object`(実質捨てられていた)から
  `SemanticRuntimeEvidence | None`へ変更、`main_action`として伝播。
- `LiveJudgeResult.repair_requested_by`("judge"/"main_governance"/
  "judge_and_main"、Repair Attemptが実際に走った場合のみ設定)を追加し、
  Web API Contract(`JudgeLastResultResponse`)・Frontend型・UI表示まで
  貫通させた(Round1 Self-Review後に追加、§6参照)。

### 4.2 許可Matrix5行の実機/Unit検証結果

| Main | Judge | 既存Repair | 検証結果 |
|---|---|---|---|
| OFF/OBSERVE | ENFORCE | ENFORCE | Unit Test PASS(既存Judge起点維持、Main起点なし) |
| OFF/OBSERVE | ENFORCE | OFF/OBSERVE | Unit Test PASS(自動Repair増えず) |
| ENFORCE | ENFORCE&Active | OFF/OBSERVE | **Unit Test PASS + 実機End-to-End PASS**(§4.3) |
| ENFORCE | ENFORCE&Active | ENFORCE | Unit Test PASS(`repair_requested_by="judge_and_main"`、Executor呼び出し1回のみ) |
| 任意 | OFF/利用不能 | 任意 | Unit Test PASS(Zero Model Call) |

### 4.3 実機End-to-End検証(Main-self、Qwen)

新規`tests/integration/test_real_local_main_governance_origin_repair_smoke.py`
で、`build_judge_completion_hook()`をフルProduction経路で通し、既存Repair
Mode=OFFのまま実際にMain Governance起点でRepair Executorが実行され、矛盾
する回答(「パリの首都はTenon」)が安全な形に収束することを実機確認(8.37秒、
`result.repair_requested_by == "main_governance"`)。既存の
`test_real_local_main_runtime_governance_enforce_smoke.py`も再実行し
(`reason_code`期待値をこのReworkに合わせて更新)、実機でPASS。

### 4.4 二周Self-Review後の修正(Round1 Finding)

独立Reviewで`repair_requested_by`がBackend内部でのみ計算され、Web API
Contract・Frontend型・UI表示のいずれにも到達していない(Handoff §6要件
未達)ことが判明し修正した:
- `web/feature_modes_routes.py`の`JudgeLastResultResponse`にフィールド
  追加、`_last_result_response()`でマッピング。
- `frontend/src/types.ts`の`JudgeLastResult`型に追加。
- `FeatureModesPanel.tsx`の結果表示欄に追加(`#feature-modes-judge-
  repair-requested-by`)。
- 翻訳キー(ja/en)追加。
- 既存統合Test(`test_status_projects_a_real_judge_result_including_
  repair_fields`)にアサーション追加、Frontend Test(1件)にもアサーション
  追加。

## 5. WU-05: UF-UI-017の最小修正

`FeatureModesPanel`/`ProviderSelectionPanel`に`onJudgeReadinessChanged`
コールバックを追加。Judge Mode変更成功時(Repair/Recording Mode変更では
発火しない)、JUDGE役Provider変更成功時(main/guard役では発火しない)にのみ
発火し、`App.tsx`の既存`loadRuntimeGovernanceStatus()`(既存sequence guard
で遅延応答を安全に無視)を呼ぶ。「OFF→ENFORCE直接選択」は`RuntimeGovernance
Panel.tsx`自体を変更していないため無変更で維持。

Round1 Finding(ProviderSelectionPanel側にこの挙動のTestが0件)を修正し、
Test 3件追加(JUDGE役commitで通知/main・guard役では非通知/失敗時は非通知)。

## 6. 内部Review 2回の実施結果

### Round1(要件・Mode Matrix・実行配線・Presented Final・User視点)

CONFIRMED 2件、いずれも修正済み(§4.4、§5)。他は全項目「確認できた」。

### Round2(異常系・並行性・Lifecycle/Restart・Test Oracle・証拠の独立性)

CONFIRMEDバグなし。PLAUSIBLE 1件: `apply_judge_budget_gate()`がトークン/
レイテンシ超過時に`execution_state`のみFAILEDへ書き換え`criterion_results`
をクリアしないため、Budget超過で失敗したTurnでもSemantic Evidence上は
`REPAIR_REQUESTED`と記録され得る。ただし`_finalize_judge_dispatch()`の
外側ガード(`gated.execution_state is COMPLETED`)によりRepair Executorの
誤発火は起きない(構造的に防がれている)。これは`resolve_semantic_action()`
のhas_deviation判定ロジック自体(WU-03以前から存在)に起因し、WU-03は
到達条件を広げたのみで新規に作り出したものではないため、今回は修正せず
記録に留めた。Status/監査UIでこの`executed_disposition`を直接表示する
実装がある場合は注意が必要。

いずれのRoundも「対象コードの分岐を無効化すれば確実に失敗する」という
基準でTest Oracleの検証力を確認し、Round6で発生した「検証力のないTest」
の再発は見られなかった。

## 7. 最終Backend確認

```text
./.venv/bin/pytest -q -k "not model_smoke"
  -> 2284 passed, 23 deselected(Round6完了時点2260→+24、
     model_smoke deselected 22→23)

./.venv/bin/mypy src tests
  -> 私の変更したファイルは全てClean。
     既存の43件のエラー(judge_live_integration.py:621「"None" not
     callable」1件、guardrail_governance関連42件)はgit stash比較で
     直近コミット(1f0e70e)から一切変更されていないことを確認済み、
     このReworkとは無関係の既存問題(Codexへ明記のうえ、修正はScope外
     として見送った)。

./.venv/bin/ruff check src tests
  -> 私の変更したファイルは全てClean(プロジェクト全体へのruff check
     は今回実施していない)。
```

実機Test(`-m model_smoke`、個別実行、同時に複数Modelは実行していない):
```text
test_real_local_main_runtime_governance_enforce_smoke.py: 1 passed, 1 skipped
  (skipはReal Model非決定性、コード欠陥ではない)
test_real_local_main_governance_origin_repair_smoke.py(新規): 1 passed
test_real_local_gemma_e2b_judge_smoke.py: 1 skipped
  (正当なFail-closed、"no JSON object found"、WU-02とは無関係の既知の
  Gemma出力品質問題)
```

## 8. 最終Frontend確認

```text
npx tsc --noEmit -> Clean
npx eslint(変更対象ファイル) -> Clean
npx vitest run(変更対象ファイル: FeatureModesPanel.test.tsx,
  ProviderSelectionPanel.test.tsx, SettingsModal.test.tsx)
  -> 全PASS(FeatureModesPanel関連23 tests含む)
npm run build -> 成功、src/margpa_runtime_llm/web/static/{app.js,app.css}
  へ配信Static反映済み(2回、Round1 Finding修正後に再ビルド)
```

既存の`App.test.tsx`/`usePreference.test.tsx`/`DevAgentPanel.test.tsx`の
`window.localStorage.clear is not a function`失敗(48 tests)は、`git
stash`で変更前コードでも同一エラーが再現することを確認済みの、Test環境
インフラ(vitest/jsdom localStorage mock)固有の既存問題であり、このRework
とは無関係。

## 9. Mode別修復起点・実Context(まとめ)

```text
Main Context: 16384(load_overrides、無変更)
Dedicated(Selene等)Context: 8192(dedicated_role_load_overrides、無変更)
両方 gpu_layers=-1(無変更、WU-01でgpu_layers縮小は不採用のため)

Main起点Repair実機確認: Main=enforce, Judge=enforce&Active(Main-self,
  Qwen), 既存Repair=off -> repair_requested_by="main_governance"
Judge起点+Main起点合流のUnit確認: 両方enforce -> repair_requested_by=
  "judge_and_main"、Executor呼び出し1回のみ
```

## 10. 実際に存在するUIだけを使う再確認手順

1. Settings ModalのAdvanced Modeを開く。
2. Feature Modes PanelでJudge ModeをENFORCEへ、Provider Selection Panelの
   JUDGE役を任意のModelへ設定する。
3. Runtime Governance PanelでMain Governance ModeをENFORCEへ切り替える
   (この操作自体はUF-UI-017修正前後で変わらず既存動作のまま)。
4. Feature Modes PanelのRepair ModeをOFFのままにする。
5. 会話を送信し、意味的にRuleへ違反する回答が生成されるのを待つ(または
   ARGD/DAGDのいずれかへ意図的に矛盾する内容を送る)。
6. Feature Modes PanelのJudge結果欄に「Repair起点: main_governance」が
   表示されることを確認する(既存Repair ModeがOFFのままであってもRepair
   が実行されていることが、この行でのみ判別できる)。
7. Judge Mode/JUDGE役Providerを変更した直後、Runtime Governance Panelの
   ENFORCEボタンの有効/無効表示が(手動Refreshなしで)即座に更新されること
   を確認する。

## 11. 停止

内部Call数・Worker数・Digest等、上記に明記していない実行時内部状態の
主張は行わない。本Returnをもって停止し、Codex Independent Reviewを待つ。
Userの実画面Acceptance、Phase Closure、Git操作、次Phaseには進まない。
