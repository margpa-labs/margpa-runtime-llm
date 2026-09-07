# Phase 9-1 Package 2残作業 — 実施内容・Test内容・3-Gate終了判定Index

```yaml
document_id: phase_9_1_package_2_residual_work_three_gate_closure_index_20260902201032
document_type: closure_verification_index
language: ja
recorded_at: 2026-09-02 20:10:32 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
recorder_role: Claude（設計者兼実装者役）
source_mutation: none
git_action: none
```

## 0. 位置づけ

本Docは、[Failure記録：3-Gate終了判定を経ない"Done"宣言の反復](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_declared_done_without_three_gate_verification_ja_20260902193000.md)を受け、ユーザー指示「作業した内容とテストした内容を書け。indexを作れ」に基づき作成する。[Exact Return Addendum](../../handoffs/phase_9_claude_package_2_open_finding_of_p2_003_and_of_p2_001_resolution_exact_return_addendum_ja_20260902190930.md)の内容を、3-Gate(Planned work complete? / Required evidence persisted? / Acceptance/closure criteria actually satisfied?)の形式で再構成し、実装内容・Test内容を一箇所から俯瞰できるようにする。

## 1. 対象範囲

Package 2残作業として実施した4件: OF-P2-003(実装)、OF-P2-001(実装)、OF-P2-006(発見・Evidence化)、OF-P2-007(発見・Evidence化、本Doc作成と同時に判明)。

## 2. 実装内容(何を作ったか)

```text
新規Source(1ファイル):
  src/margpa_runtime_llm/adapters/runtime_model_control/memory_resource_gate.py
    SystemMemoryRoleResourceGate(RoleResourceGatePort実装)、
    ROLE_MEMORY_SAFETY_MARGIN_BYTES(3GiB)、real_available_memory_bytes()

変更Source(3ファイル):
  src/margpa_runtime_llm/bootstrap/web_application.py
    RoleProviderLifecycleManager()へresource_gate=SystemMemoryRoleResourceGate(...)を配線
  src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py
    freeze_semantic_turn()へrotation_offset引数追加、FrozenSemanticTurnへ
    next_rotation_offset追加、SemanticRuntimeCoordinatorへProcess-local Rotation Cursor追加
  src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_runtime.py
    SemanticTurnSnapshotへrotation_offset: int = Field(default=0, ge=0)追加
```

## 3. Test内容(何を確認したか、正確なPath)

```text
新規Test(2ファイル):
  tests/unit/adapters/runtime_model_control/test_memory_resource_gate.py (11 tests)
    Fixtureレベル、実機非依存。kind非MODEL/Main-shared Judge選択の無条件許可、
    Main Active時の容量不足Deny／容量十分Allow、Main非Active時の無条件許可
    (available=0でも短絡許可されることまで確認)、runtime_model_control_ref未設定時の
    無条件許可、候補/Main Definition解決失敗時のFail-open、Memory Probe例外時の
    Fail-open、option.model_key未設定時の許可。

  tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py
    (model_smoke、Parametrized 1関数×6組み合わせ = 6 tests)
    実Registry値(config/models/*.toml)・実psutil値使用、Model非Load。
    Main(Qwen4B／DeepSeek8B) × Dedicated(Selene／Gemma／Qwen3Guard)の
    全6組み合わせで、Gate判定が独立再計算した期待値と一致することを実測確認。

変更Test(3ファイル):
  tests/unit/runtime_model_control/test_role_lifecycle_manager.py (新規2 tests追加)
    Gate拒否時にactivate経由で実Loadが一度も呼ばれないこと、transition_to経由で
    Transition先の実Loadが呼ばれず既存Adapterが維持されることを確認。
  tests/unit/runtime_governance/test_semantic_runtime.py (新規2 tests追加)
    freeze_semantic_turnの回転算術そのもの(5件・max_criteria=2、Wrap-around含む厳密検証)、
    SemanticRuntimeCoordinator経由の109件・max_criteria=32・4連続Turnで全109件が
    最低1回選択されること(かつ4 Turnとも選択集合が異なる=真の回転であること)を確認。
  tests/integration/test_real_local_semantic_109_batched_judge_smoke.py (新規1 test追加)
    Model非依存(Canonical Suiteで実行、model_smoke Markerなし)。実ARGD/DAGD 109-Rule
    Corpusに対し、SemanticRuntimeCoordinatorで4連続Turnさせ、全109件が実Corpus
    データで最低1回選択されることを確認。
```

## 4. 3-Gate終了判定(各項目ごとに個別評価)

### OF-P2-003(Main+Selene同時Load破壊防止)

```text
Gate 1 Planned work complete?           : YES
  P2-WU-03「Selene切替後のMain Load破壊防止」に対応するResource Gateを実装・配線した。
Gate 2 Required evidence persisted?     : YES
  Fixture 11 tests(§3) + Parametrized実機Evidence 6 tests中2件(Qwen4B×Selene、
  DeepSeek8B×Selene)が直接該当。tests/unit/runtime_model_control/
  test_role_lifecycle_manager.py の2新規Testで実Load抑止も確認。
Gate 3 Acceptance/closure criteria satisfied? : YES(ただし限定的)
  Handoff文言(Selene→Main方向)自体は満たす。真の破壊メカニズム(Metal Backend共有等)は
  未確定のまま(正直に開示、Addendum§2.2)。逆方向(Main→Selene方向)は未実装、
  OF-P2-005として引き継ぎ(Controller Review対象)。
```

### OF-P2-001(Semantic 109 Turn間Rotation)

```text
Gate 1 Planned work complete?           : YES
  P2-WU-06「一つのRunで全109を無理に投入しない」に対応するTurn間Rotationを実装した。
Gate 2 Required evidence persisted?     : YES
  tests/unit/runtime_governance/test_semantic_runtime.py 新規2 tests(算術・
  Coordinator経由の両方) + tests/integration/test_real_local_semantic_109_batched_judge_smoke.py
  新規1 test(実Corpus)。
Gate 3 Acceptance/closure criteria satisfied? : YES
  既存の`evaluated=passed+deviated`等の不変式を変更していないことをFull Canonical
  Suite(2245 passed)で確認。「Final Aggregation」のうちTurn単位会計は既存のまま、
  Turn跨ぎ累積集計は要求外Scopeと判断し実装せず、その旨明示(Addendum§4.3)。
```

### OF-P2-006(Main Active時、既定Judge GemmaもGate拒否されうる)

```text
Gate 1 Planned work complete?           : N/A(Source変更は行わない、という方針自体がPlan)
  User決定「margin等は変更せず現状維持、様子見て後日判断」。ソース変更なし。
Gate 2 Required evidence persisted?     : YES(当初NOだったが是正済み、本Failureの本体)
  発見当初は即席Script実行のみ(未保存)。§3のParametrized Test6件中2件
  (Qwen4B×Gemma、DeepSeek8B×Gemma)として恒久化済み。
Gate 3 Acceptance/closure criteria satisfied? : DISCLOSED、対応は保留中
  Package 2既存の8項目Gemma契約(Handoff §9)のうち項目3・5が、Main Active時の
  実メモリ条件下で条件付きになることをUserへ開示済み。是正するかどうかはUser判断待ち。
```

### OF-P2-007(Main=DeepSeek8B稼働時、Qwen3GuardもGate拒否されうる)

```text
Gate 1 Planned work complete?           : N/A(OF-P2-006と同種、ソース変更は行わない)
Gate 2 Required evidence persisted?     : YES(発見と同時に恒久化)
  §3のParametrized Test6件中1件(DeepSeek8B×Qwen3Guard)として最初から恒久Test化。
Gate 3 Acceptance/closure criteria satisfied? : DISCLOSED、対応は保留中
  Qwen3Guardの既存Baselineへの影響を開示。OF-P2-006と暫定的に同一方針(現状維持)を
  仮適用、User確認待ち。
```

## 5. Full Verification(この時点の最終状態)

```text
.venv/bin/python -m pytest -q -m "not model_smoke"
  → 2245 passed, 22 deselected (Package 2基準2229 passed／16 deselectedから、
    新規Canonical Test 16件・新規model_smoke Test 6件、Regression 0件)

.venv/bin/python -m pytest tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py -m model_smoke -q
  → 6 passed(Main×Dedicated Role全6組み合わせ)

mypy src tests
  → Found 43 errors in 4 files(Package 2基準と同一、新規Error 0件)

ruff check .
  → All checks passed!

ruff format --check .
  → 7 files would be reformatted(Package 2基準と同一、新規Drift 0件)
```

## 6. 未対応のまま引き継ぐ項目(Controller/User判断待ち)

```text
OF-P2-002: Gemma構造化出力弱点。保留、User実機確認待ち(変更なし)。
OF-P2-004: UI実機確認。User自身の担当範囲のまま(変更なし)。
OF-P2-005: Main切替時の逆方向Resource Gate未実装。保留(理由は下記)。
OF-P2-006: Main Active時、既定Judge GemmaもGate拒否されうる。保留(理由は下記)。
OF-P2-007: Main=DeepSeek8B稼働時、Qwen3GuardもGate拒否されうる。保留(理由は下記)。
```

### 6.1 [Handoff起因ではない、User本人の判断] OF-P2-005／006／007を保留とする理由(2026-09-02時点)

OF-P2-007報告後、UserからOF-P2-005／006／007をまとめて保留とする明示指示を受けた。理由は次の3点(User本人の言葉、要約せず記録)。

```text
1: さっさとまずMVP(Phase 10完成)まで行きたい
2: そもそも『いずれどのモデルも古くなるので、いつでも交換可能なPlatform』
   という観点的に
3: とはいえ、まともに使えんのも困るが、個別調整なんかやってたらやはり
   1問題があるので
```

**重要な訂正(User本人、直後の発言、そのまま記録):**

> 厳密にいうと、少なくとも今は、ね。
> Phase11以降で必要性を感じたらやるけど、そもそもその頃はまた更にmodelに変えてるかもしれない。だからやるかもしれんし、やらんかもしれん。
> 絶対にしない的な書き方したのであれば、codexが混乱するから直せ。

**したがって本節、および本Addendum・phase_index_ja.mdの関連記述は、「OF-P2-005／006／007を今後一切実施しない」という恒久的な最終決定では断じてない。** 正確には「**少なくとも現時点(2026-09-02、Phase 9-1 Package 2時点)では、着手しない**」という、時点限定の優先順位判断である。Phase 11以降、必要性を感じれば着手する可能性がある。ただしその時点でMain/Dedicated Role側のModel構成自体が変わっている可能性もあり、着手するかどうかも含めて未定 — 「やるかもしれないし、やらないかもしれない」という、両方向に開いたOpenな状態のまま引き継ぐ。

`[Claude追加、User意図の解釈]` これは「Gateを個々のModel(Selene／Gemma／Qwen3Guard)ごとに特別扱いしない」という設計判断とも整合する。本Project全体が「どのModelもいずれ陳腐化するので差し替え可能であるべき」というPlatform思想を持つ以上、margin調整・個別除外のような**Model固有のTuning**は、そのPlatform思想そのものと現時点では衝突し、かつMVP到達を遅らせる。したがって、現状の「Main+Dedicated Model全般に一律の安全側Margin」という設計を、実用上まともに使えない水準にならない限りは当面維持し、Phase 11以降、その時点のModel構成と必要性に応じて改めて判断する、という**現時点限定の**優先順位である。

この決定により、OF-P2-005／006／007は「未検証だから保留」ではなく、「検証済みの上で、Platform思想とMVP優先度に基づき、少なくとも現時点では着手しない(恒久的にやらないとは決めていない)」という、明確な理由と明確な時点限定を伴う保留へと更新された。

## 7. Status

```text
Current Point            : Package 2残作業4件(OF-P2-003／001／006／007)を3-Gate形式で
                            再検証し、実施内容・Test内容を一元化したIndexとして記録した。
Files Created／Modified   : 本Fileのみ(新規作成)。
Validation                : §5参照(Full Verification再実行済み)。
Open Current Blocker      : NONE
Controller-owned Next Work: OF-P2-005／006／007のDisposition最終判断。
Exact Next Route          : 次はUser自身の実機(ブラウザ)Manual Recheck。本Doc提出後、
                            作業は再度停止する。
```
