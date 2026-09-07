# Phase 9-1 Claude Package 2 残Open Finding(OF-P2-003・OF-P2-001)解消 Exact Return Addendum

```yaml
document_id: phase_9_claude_package_2_open_finding_of_p2_003_and_of_p2_001_resolution_exact_return_addendum_20260902190930
document_type: exact_return_addendum
document_state: frozen_return_ready
language: ja
created_at: 2026-09-02 19:09:30 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
provider: Claude
role: 設計者兼実装者役
governing_handoff: docs/project/phases/phase_9/handoffs/phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_handoff_ja_20260902121740.md
governing_handoff_sha512: 65f9d7c3b0b1d09380e74b1f0f64223178f8910283828966e49fc817dac9d083cc78b752f5919748d7a836846c1270e79aee51fc848b387069de37ba36cec3a8
base_return: docs/project/phases/phase_9/handoffs/phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_return_handoff_ja_20260902160000.md
resume_precondition_doc: docs/project/phases/phase_9/history/operations/phase_9_1_package_2_open_finding_disposition_and_resume_precondition_ja_20260902182320.md
resume_authorization: user_explicit_2026-09-02_after_handoff_reread
maximum_claim: P9_1_JUDGE_SEMANTIC_AND_MAIN_RUNTIME_ENFORCE_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
real_model_load_by_this_addendum: false
network_action_by_this_addendum: none
git_action_by_this_addendum: none
backup_action_by_this_addendum: none
```

## 0. 位置づけ

本Docは[Package 2 Exact Return](phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_return_handoff_ja_20260902160000.md)(§14.2)が正直に引き継いだOpen Finding4件のうち、[User決定](../history/operations/phase_9_1_package_2_open_finding_disposition_and_resume_precondition_ja_20260902182320.md)によりこの時点で実施対象となったOF-P2-003・OF-P2-001の2件を解消したExact Returnである。OF-P2-002は保留のまま、OF-P2-004はUser自身の担当範囲のまま、いずれも本Docの対象外。

**起源表記の凡例**(User指示により本Doc全体で徹底): 各記述の冒頭に `[Handoff起因]` または `[Claude追加]` を付す。前者はCodex作成Handoff本文に明記された要求、後者はClaude自身がその場で判断して追加した設計・記述であることを示す。

## 1. 結論

```text
OF-P2-003(Main+Selene同時Load時のMain破壊防止): DONE
OF-P2-001(Semantic 109のTurn間Rotation):        DONE
```

いずれも実装・Focused Test・実機Evidence取得・二段階Internal Review(観点入れ替え、2周実施、2周目でFinding 0件)まで完了した。Full Verification(Canonical Test、Mypy、Ruff)を再実行し、Package 2基準からの新規Regression 0件を確認した。

**ただし本Return提出後、User自身の指摘により、2周のReviewでは検出できていなかった追加の相互作用(OF-P2-006、Main Active時の既定Judge GemmaもGate拒否されうる件)が1件見つかっている(§3.3)。** Userへ報告済みで、対応は現状維持と決定済み。「2周でFinding 0件」はReview自体の記録として訂正しない(実際に2周ともFinding 0件だった)が、Review完了後にUserの独立した再確認で初めて発見された事実は、Review Loopの網羅性に限界があったことの正直な記録として本Doc内に残す。

## 2. OF-P2-003 — Main+Selene同時Load時のMain破壊防止

### 2.1 [Handoff起因] 要求の再確認

Package 2 Exact Handoff §4 P2-WU-03: 「Main-shared Qwen: Structured Output安定性、Model Identity維持、Selene切替後のMain Load破壊防止。」

### 2.2 [Claude追加] 設計判断とその理由

実装前に既存Source(`RoleProviderLifecycleManager`)を確認した結果、Judge/Guard Role活性化の直前に呼ばれる`RoleResourceGatePort.allow_activation()`という既存のFail-closed Hookが、Production配線では常に`AllowAllRoleResourceGate`(無条件許可)に固定されており、**本Package以前は実質的に何もGateしていなかった**ことを確認した(`role_lifecycle_manager.py`の既存コード、本Docでの新規実装ではない)。

真の破壊メカニズムは2026-09-01時点でも未確定(仮説: Apple Silicon上のllama.cpp/Metal Backend共有状態による競合)。`[Claude追加]` この2回目の対応では、確定できない仮説を無理に検証するのではなく、**確実に観測・防止できる要因(実メモリ不足)**を対象にGateを実装する方針を採った。16GB統合メモリのMacで、開発作業と並行稼働中は実際にはSelene(約5.7GB)+Main(2.3〜4.7GB)+margin(3GB)の合計を賄えないケースが多く、これは本Incidentの一因として十分plausibleである(§2.5の実測値参照)。**このGateはIncidentの真因を特定したと主張しない** — 観測・防止可能な一側面(実メモリ不足)への対処である。

### 2.3 実装

新規`SystemMemoryRoleResourceGate`(`RoleResourceGatePort`実装、`src/margpa_runtime_llm/adapters/runtime_model_control/memory_resource_gate.py`)を追加し、`web_application.py`のProduction配線(`RoleProviderLifecycleManager`構築箇所)へ`resource_gate=`として接続した。

```text
挙動:
- Main非Activeの場合: 無条件許可(既存の単独Judge/Guard稼働を一切妨げない、Package 2実機Evidence
  で既に安全性実証済みの経路)。
- Main-shared Judge選択(QWEN_MAIN/DEEPSEEK_MAIN)の場合: 無条件許可(第二のModelを実際には
  Loadしないため、Risk対象外。ProductionRoleAdapterFactory.create()の既存分岐と同一条件)。
- 上記以外(Main Active時のSelene/Gemma/Qwen3Guard等、実際にModelをLoadする候補)の場合:
  候補Artifact size_bytes + Active Main Artifact size_bytes + Safety Margin(3GiB、ヒューリスティック、
  §2.4)が実available memory(psutil、既存依存関係、新規Install無し)を超えるならUNAVAILABLE/
  ACTIVATION_FAILEDへFail-closed。超えなければ許可。
- 内部Fault(Definition解決失敗、Memory Probe失敗)は全てFail-open(Package 2以前の既定=常時許可
  より制限的になることは無いが、そのFail-openをLoggingで可視化する。§3のReview 1周目で追加)。
```

### 2.4 [Claude追加] Safety Margin 3GiBの根拠

OS+Server Process+KV Cache+一般オーバーヘッドを見込んだ丸め値であり、Model個別のKV Cache厳密計算(Registryに未保持のArchitecture別Metadataが必要)ではない。目的は「破壊防止」であって「同時Load許可率の最大化」ではないため、意図的に保守的な値とした。

### 2.5 実機Evidence(This Mac、実測)

```text
Registry実size_bytes(config/models/*.toml、実測):
  Main Qwen3-4B Q4_K_M      : 2,497,280,256 bytes (約2.33GiB)
  Main DeepSeek-R1 8B Q4_K_M: 5,027,782,720 bytes (約4.68GiB)
  Selene 8B Q5_K_M          : 5,732,992,896 bytes (約5.34GiB)

実行時点(2026-09-02 19時台、本Session並行稼働中)の実psutil読取:
  total    : 17,179,869,184 bytes (16.0 GiB、公称16GBと一致)
  available:  7,124,942,848 bytes (約6.63 GiB)

Gate実判定(Main=Qwen ACTIVE、候補=Selene、実Registry値・実psutil値使用、
  Fixtureなし、tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py):
  required = 2,497,280,256 + 5,732,992,896 + 3,221,225,472(margin) = 11,451,498,624 bytes
  available = 7,124,942,848 bytes
  → allowed=False reason=resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role
```

`[Claude追加]` 本Mac上の現実的な(開発作業と並行稼働中の)条件下では、Main+Selene同時稼働は margin込みで実際に不足しており、Gateは正しく安全側に拒否した。ALLOW方向(十分な実メモリ下での実成功)は、この場でわざと「メモリは十分」と偽装したProbeを使って実Loadを強行する形では検証していない — それはまさに本Gateが防ごうとしている状況を意図的に再現する行為であり、Fixture Test(§2.6)による決定論的検証に留めた。この判断もClaude自身の安全側判断である。

### 2.6 Fixture Test(決定論的、実機非依存)

```text
tests/unit/adapters/runtime_model_control/test_memory_resource_gate.py: 11 tests
  - kind非MODEL・Main-shared Judge選択の無条件許可
  - Main Active+容量不足時のDeny(reasonのPrefix確認含む)
  - Main Active+容量十分時のAllow
  - Main非Active時の無条件許可(available=0でも許可されることまで確認、真の短絡動作の証明)
  - runtime_model_control_ref未設定時の無条件許可
  - 候補Definition解決失敗時のFail-open
  - Main Definition解決失敗(Active報告だが不整合)時のFail-open
  - Memory Probe自体が例外を送出した場合のFail-open
  - option.model_key未設定時の許可

tests/unit/runtime_model_control/test_role_lifecycle_manager.py: 新規2 tests
  - Gate拒否時、実Loadが一度も呼ばれないこと(activate経路)
  - Gate拒否時、Transition先の実Loadが呼ばれず、既存Adapterが維持されること(transition_to経路)
```

## 3. 二段階Internal Review(観点入れ替え、2周)

### 3.1 1周目

**観点1(Runtime/Concurrency/Lifecycle/Cancellation/Authority)**:
- Lock順序を検証: `RoleProviderLifecycleManager._condition`保持下で`RuntimeModelController.snapshot()`(別Lock)を取得する経路は、本Gate導入以前から`MainSharedJudgeRoleAdapter.preflight()`が同一パターンで既に安全に使用しており、新規のLock順序は導入していない(Deadlock Risk無し)。
- `SystemMemoryRoleResourceGate`自体はMutable共有状態を持たず、Thread-safety上の懸念無し。
- Authority: 新規Network/Dependency/Artifact変更/Git/Backup無し。psutilは既存依存関係。

**Finding 1件**: Fail-open経路(内部Fault時)が完全にSilentであり、Gate自体が機能しなかったことを事後に追跡する手段が無かった。

**対応**: `logging.getLogger(__name__).warning(...)`をFail-open経路へ追加(§2.3後半に反映済み)。`[Claude追加]`、Handoff必須要求ではない。

**観点2(Requirement/Semantic/Evidence/Manual Truthfulness/Claim)**: この時点でのClaim(「実メモリ不足という観測可能な一側面への対処」)は正確であり、真因特定を主張していないことを確認。Finding無し。

### 3.2 2周目(1周目のFindingへの対応を含め再度全体を確認)

**観点1**: 追加したLogging呼び出し自体が新たなLock/Deadlock/情報漏洩Riskを生まないことを確認(`logging`標準モジュールの一般的な安全な使用パターン、User会話内容等の機微情報はGateの入出力に一切含まれない)。

**観点2**: Return記述の正確性を再確認。Finding無し。

**2周目でFinding 0件のため、Review Loopをここで終了する(User指示: 「Finddingなくなるまで繰り返す」に基づく判定)。**

### 3.3 [Claude追加] User指摘によるReview後の追加Finding(OF-P2-006)

上記2周のReview完了・本Return提出後、Userから「Package 2既存のGemma既定Judge契約8項目([Handoff起因]§9)を本当に全て満たしているか」との直接の再確認指示を受けた。改めてこの1件だけを実測したところ、**2周のReviewでは検出できていなかった、本Addendum自体が生んだ新規の相互作用**が判明した。

```text
実測(このMac、実Registry値・実psutil値、Main=Qwen ACTIVE、候補=Gemma、
  発見当時: tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py::
  test_gate_decision_for_main_plus_gemma_matches_real_registry_and_real_memory
  (§3.4で§5・§7時点のParametrized Testへ統合、現在は
  test_gate_decision_matches_real_registry_and_real_memory_for_every_main_and_dedicated_role
  の一部として存在)、-m model_smoke、実測値は実行毎に変動しうる):
  required = 2,497,280,256(Main) + 3,349,516,256(Gemma) + 3,221,225,472(margin)
           = 9,068,021,984 bytes
  available = 6,760,759,296 bytes(本Test実行時点)
  → allowed=False
```

`[Claude追加]` §2で実装したGateはSelene・Gemmaを区別せず、Main Active時のDedicated Role Load全般へ一律のMargin(3GiB)を適用する。Package 2本体で「軽量・Seleneより導入しやすい既定Judge」として位置づけたGemma(§4 Handoff §9参照)が、Main稼働中はこのMacの現実的なメモリ条件下でSeleneと同様にGateされうる — 8項目契約のうち項目3(Load・実行)・項目5(Repair→Rejudge、項目3成立が前提)がこの条件に該当する。項目1・2・4・6・7は本Gateと無関係な経路であり影響を受けない(§3.3自体の実測とは別に、既存Fixture Testで確認済み)。既存のGemma用Fixture Test(`test_gemma_e2b_role_adapter_composes_with_the_real_lifecycle_manager_as_fresh_default`等)はいずれも`runtime_model_control_ref=[None]`(Main非Active)で書かれており、Canonical Suiteはこの相互作用を一度も検出していなかった。

発見当初は即席Scriptでの1回限りの実測に留まっていたが、事後に恒久的なReal-hardware Evidence Testへ格上げした(同一Fileへ、共通Helperを介して追加。§3.4で全6組み合わせのParametrized Testへ最終的に統合済み、§5・§7参照)。ソースコードには一切手を入れておらず、Gate自体の判定を毎回機械的に記録するだけである。

**Userへ確認した結果、現時点の対応方針は「margin等は変更せず現状維持、様子見て後日判断」である。** Claude自身の裁量では変更しない。以下を新規Open Findingとして引き継ぐ。

```text
OF-P2-006(Main Active時、既定Judge Gemmaも実メモリ条件下でGate拒否されうる):
  [Claude追加、Userへ報告済み、対応=現状維持(2026-09-02時点のUser指示)]
  本Mac実測でrequired 9.07GB > available(実行時点変動、本Addendum作成時点は6.76GB)
  となり拒否される条件を確認。Selene(意図した挙動)とGemma(意図せぬ副作用の可能性)を
  区別しないMargin設計のトレードオフをUserへ提示し、選択肢(margin再設計／現状維持／
  Gemma個別除外／保留)を提示した結果、「現状維持、様子見て後日判断」との回答を得た。
  ソースコード変更は行っていない。恒久Real-hardware Evidence Testを追加済み(上記)。
```

### 3.4 [Claude追加] 3-Gate終了判定をUserから指示された後、自ら網羅性を検証して判明した追加Finding(OF-P2-007)

OF-P2-006をUserへ報告した後、Userから改めて「Agentの終了判定には最低でも3 Gate(Planned work complete? Required evidence persisted? Acceptance/closure criteria actually satisfied?)必要、全部Yesになるまで"Done"禁止」との指摘を受けた(詳細は[Failure記録](../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_declared_done_without_three_gate_verification_ja_20260902193000.md)参照)。この指摘を受け、Gate3(Acceptance/closure criteria実際に満たされているか)を自らもう一度、場当たり的にではなく網羅的に検証した。

`SystemMemoryRoleResourceGate`が実際にGateしうるDedicated Model-kind Providerは、現行Catalog全体でSelene・Gemma・Qwen3Guardの3つのみ(JUDGE Roleの`QWEN_MAIN`／`DEEPSEEK_MAIN`はMain-shared、Gate対象外)。Main側もQwen4B／DeepSeek8Bの2つのみ。よって全組み合わせは2×3=6通りで尽くされる — この6通り全てを実測した(`test_gate_decision_matches_real_registry_and_real_memory_for_every_main_and_dedicated_role`、Parametrize、6 Test)。

```text
実測(このMac、実Registry値・実psutil値、real_available=6,776,979,456〜6,777,012,224 bytes
  (実行順に微小変動)):
Main       ×Dedicated  : required(bytes)    → allowed
Qwen4B     ×Selene     : 11,451,498,624      → False (OF-P2-003、既知)
DeepSeek8B ×Selene     : 13,982,001,088      → False (追加確認、Selene側は元々意図した挙動)
Qwen4B     ×Gemma      :  9,068,021,984      → False (OF-P2-006、既知)
DeepSeek8B ×Gemma      : 11,598,524,448      → False (追加確認、OF-P2-006と同種)
Qwen4B     ×Qwen3Guard :  6,523,259,200      → True  (このMacでは僅差でAllow)
DeepSeek8B ×Qwen3Guard :  9,053,761,664      → False (新規、OF-P2-007)
```

`[Claude追加]` DeepSeek8B(Main)×Qwen3Guardの組み合わせが新たにDenyされることが判明した。Qwen3GuardはPackage 2以前から「成立済み基本Baseline」として扱われてきたGuardrail機能であり、これもOF-P2-006と同種の「既存Acceptance対象への意図しない影響」に該当する。Qwen4B(Main)×Qwen3Guardはこのマシンでは僅差でAllowされているが、これはたまたま現在の実available memoryがこの1点だけ閾値を上回っているに過ぎず、安定してAllowされる保証があるわけではない。

```text
OF-P2-007(Main=DeepSeek8B稼働時、Qwen3Guardも実メモリ条件下でGate拒否されうる):
  [Claude追加、User未報告(本Addendum作成と同時に発見、Index経由で報告)]
  本Mac実測でrequired 9.05GB > available 6.78GBとなり拒否される条件を確認。
  OF-P2-006と同種のトレードオフであり、現時点でOF-P2-006と同一の対応方針
  (現状維持、様子見て後日判断)を仮に適用し、Userへ報告する。ソースコード変更は
  行っていない。恒久Real-hardware Evidence Testを追加済み(上記、6組全てを
  1つのParametrized Testでカバー)。
```

**この時点で「Gate3: Acceptance/closure criteria actually satisfied」を、Main×Dedicated Roleの組み合わせという観点では網羅的に検証し終えた。** これ以上の未検証の組み合わせはCatalog上存在しない。

## 4. OF-P2-001 — Semantic 109のTurn間Rotation

### 4.1 [Handoff起因] 要求の再確認

Package 2 Exact Handoff §4 P2-WU-06: 「Batching、Token Accounting、Deferred ReasonおよびFinal Aggregationを正直に設計する。」「一つのRunで全109を無理に投入してContext／Deadlineを破壊しない」。この記述が複数Turnにまたがる設計を要求している、という解釈は、本Session内で既にUserとの間で確定済みである([Authority境界Failure記録](../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_authority_boundary_violation_and_origin_misattribution_ja_20260902182320.md)§1.1参照)。

### 4.2 症状(修正前)

`freeze_semantic_turn()`の選択ロジックは`applicable[:max_criteria]`という固定Sliceであり、複数Turnにまたがる回転機構が存在しなかった。同じ32件が毎Turn繰り返し評価され、残り77件は恒久的にDeferredのままになり得た。

### 4.3 実装

`freeze_semantic_turn()`へ`rotation_offset: int = 0`引数を追加し、Sort済みApplicable Criteria列を`rotation_offset`だけ回転させたうえで`max_criteria`件を選択する。次回Turn向けの`next_rotation_offset`(`(offset + max_criteria) % total`)を`FrozenSemanticTurn`として返す。`SemanticTurnSnapshot`(Domain Contract)へ`rotation_offset: int = Field(default=0, ge=0)`を追加し、どの回転窓が選ばれたかをEvidence自体から監査可能にした(`frozen_digest_sha512`計算にも算入)。`SemanticRuntimeCoordinator`(本番で唯一Process内Singletonとして稼働、`bootstrap/runtime_governance.py`で1回のみ構築されTurnをまたいで再利用されることを確認済み)へProcess-local Rotation Cursorを追加し、`begin()`呼び出しごとに自動で回転する。

```text
保証: applicable件数をn、max_criteriaをmとすると、ceil(n/m)回の連続Turnで
  必ず全applicable Criterionが最低1回選択される(n=109, m=32の場合、4 Turn)。
  109と32は互いに素であるため、長期運用では特定Criterionだけが恒常的に
  優遇/冷遇されることもない(副次的な公平性、設計目標として明示的に要求
  されたものではないが自然に得られる性質)。
```

`[Claude追加]` 「Final Aggregation」については、Turn単位の正直な会計(`passed+deviated+unknown+deferred_criteria_count == 109`)は既にPackage 2本体(§9)で実機実証済みであり、本件のRotation実装でもこの不変式は一切変更していない(§4.5で再確認)。Turnをまたいだ累積(Cross-turn Cumulative)集計という新機能は、Handoff本文に明記が無く、要求外の新規Scope拡大と判断し実装していない — 必要であれば別途User/Controller判断を仰ぐ事項として、ここに明示する。

### 4.4 Test

```text
tests/unit/runtime_governance/test_semantic_runtime.py: 新規2 tests
  - freeze_semantic_turnの回転算術そのもの(5件・max_criteria=2の小規模・厳密検証、
    Wrap-around含む)
  - SemanticRuntimeCoordinator経由の109件・max_criteria=32・4連続Turnで、
    全109件が最低1回選択されること(Union確認)、かつ4 Turnとも選択集合が
    異なること(真の回転であることの確認)

tests/integration/test_real_local_semantic_109_batched_judge_smoke.py: 新規1 test
  (Model非依存、実ARGD/DAGD 109-Rule Corpusを使用、Canonical Suiteで実行、
  model_smoke Markerなし)
  - 実Corpusの109件に対し、SemanticRuntimeCoordinatorで4連続Turnを実行し、
    全109件が最低1回選択されることを実Corpusデータで確認
```

`[Claude追加]` 実LLM Judge Dispatchを複数Turn分実行する形での実機Evidenceは取得していない — Dispatch自体の正しさはPackage 2本体(§6〜§9)で既に実機実証済みであり、本件で新規に証明すべきは「選択されるCriterionがTurnごとに変わること」のみで、これはModelを介さない純粋な選択ロジックの性質であるため、追加のReal Model Loadは不要と判断した(既に確立された実機Evidenceの無意味な反復を避ける)。

### 4.5 既存不変式への影響確認

```text
Package 2 Return §9記載の不変式: evaluated = passed + deviated、
  (passed+deviated+unknown) + deferred_criteria_count == 109
→ 本Rotation変更は「どのCriterionがselectedか」のみを変え、selected件数+
  deferred件数の合計が常にtotal件数と一致する性質(len(selected)+len(deferred)==total)
  は変更していない。Full Canonical Suite(§5)で回帰無し確認済み。
```

## 5. Full Verification(再実行)

```bash
.venv/bin/python -m pytest -q -m "not model_smoke"
→ 2245 passed, 22 deselected
  (Package 2基準2229 passed／16 deselected + 本Addendum新規Canonical Test 16件
   (Gate Fixture 11 + Lifecycle Manager wiring 2 + Rotation算術 1 + Rotation
   Coordinator(Toy) 1 + Rotation(実Corpus) 1) + 新規model_smoke Test 6件
   (Gate実機Evidence、Main×Dedicated Role全6組み合わせのParametrized Test、§3.4参照)
   = 2245 passed／22 deselected。Package 2基準からの新規Regression 0件)

.venv/bin/python -m pytest tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py -m model_smoke -q -s
→ 6 passed(§2.5・§3.3・§3.4の実機Evidence全て。実行毎に実psutil値へ依存するため結果の
  絶対値は実行環境・実行時点により変動しうるが、本Addendum作成時点の実測値は§3.4の表
  参照)

mypy src tests
→ Found 43 errors in 4 files (checked 568 source files)
  Package 2基準と同一43件・同一4ファイル(guardrail_governance/judge_live_integration:604関連の
  既存Error)。本Addendumによる新規Errorは0件。ファイル数565→568は新規追加ファイル3件
  (memory_resource_gate.py、test_memory_resource_gate.py、
  test_real_local_main_selene_concurrent_load_resource_gate_smoke.py)分の増加のみ。

ruff check .
→ All checks passed!

ruff format --check .
→ 7 files would be reformatted(Package 2基準と同一7ファイル、本Addendumの新規/変更ファイルは
  含まれない)
```

## 6. Open Finding 更新後の状態

```text
OF-P2-001(Semantic 109 Turn間Rotation): DONE(本Addendum§4)
OF-P2-002(Gemma構造化出力弱点)        : 保留のまま(User実機確認待ち、変更なし)
OF-P2-003(Main+Selene同時Load破壊防止): DONE(本Addendum§2、実メモリ不足という
  観測可能な一因への対処。真の破壊メカニズムは依然未確定のまま、§2.2参照)
OF-P2-004(UI実機確認)                : User自身の担当範囲のまま(変更なし)

新規Open Finding(本Addendumで発見、Claude追加、Controller Review対象):
OF-P2-005(Main切替時の逆方向Resource Gate未実装): `[Claude追加]`
  本Addendumで実装したGateは「Main Active時にDedicated Role(Judge/Guard)を
  追加Loadする」方向のみをGateする(P2-WU-03の文言「Selene切替後のMain Load
  破壊防止」および実Incidentの発生順序に対応)。逆方向(Dedicated Role Active時に
  MainのModel切替(RuntimeModelController.begin_switch())を行う)は、対称的に
  同じ物理的Risk(共有Metal Backend、実メモリ不足)を持ちうるが、本Addendumでは
  Gateを実装していない。理由: (1) Handoff本文はSelene→Main方向のみを明記して
  おり、逆方向は明示要求ではない、(2) RuntimeModelControllerはPackage 2以前
  から広範囲にTestされているCore Transactional Componentであり、Signature変更
  (Constructor拡張)は本Addendumの minimal-diff方針を超える可能性があると判断
  した。Controller Reviewでの要否判断を仰ぐ。

OF-P2-006(Main Active時、既定Judge GemmaもGate拒否されうる): `[Claude追加、Userへ報告済み]`
  本Addendum§3.3参照。Package 2既定Judge(Gemma)がMain稼働中はSeleneと同様に
  Gate拒否されうることが判明した(§9で言う8項目契約の項目3・5に該当)。User確認の結果、
  2026-09-02時点の対応方針は「margin等は変更せず現状維持、様子見て後日判断」。
  Source変更は行っていない。次にこのFindingへ対応する場合は、User自身の明示指示を
  待ってから着手する(本Sessionで確立した「提案と実行許可の分離」原則に従う)。

OF-P2-007(Main=DeepSeek8B稼働時、Qwen3GuardもGate拒否されうる): `[Claude追加、本Addendumで報告]`
  本Addendum§3.4参照。OF-P2-006発見後、Userの3-Gate終了判定指摘を受けて自ら
  網羅的にMain×Dedicated Role全6組み合わせを検証した結果、新たに判明した。
  OF-P2-006と同種のトレードオフ、暫定的に同一対応方針(現状維持)。Source変更なし。

OF-P2-005／006／007 現時点(2026-09-02)のDisposition(User本人の判断、恒久的な最終決定ではない):
  `[User本人の判断]`
  3件とも「少なくとも現時点では」保留・現状維持。理由:「1: MVP(Phase 10完成)優先、
  2: どのModelもいつでも交換可能なPlatform思想上、Model個別Tuningは避けるべき、
  3: とはいえ実用に堪えない水準は困るが、個別調整をやり始めるとPlatform思想と矛盾し
  MVP到達も遅れる」。**User本人による明示的な訂正**: 「絶対にしない、という書き方は
  誤り。Phase 11以降、必要性を感じれば着手する可能性がある。ただしその頃にはMain/
  Dedicated Role側のModel構成自体が変わっている可能性もあり、着手するかどうかも
  含めて未定(やるかもしれないし、やらないかもしれない)」。両方向に開いたOpenな
  状態のまま引き継ぐ。詳細・User原文は
  history/operations/phase_9_1_package_2_residual_work_three_gate_closure_index_ja_20260902201032.md
  §6.1参照。
```

## 7. Project側変更Path(本Addendum分のみ、Package 2本体分は§16参照)

```text
新規Source(1件):
  src/margpa_runtime_llm/adapters/runtime_model_control/memory_resource_gate.py

変更Source(3件):
  src/margpa_runtime_llm/bootstrap/web_application.py
  src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py
  src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_runtime.py

新規Test(2件):
  tests/unit/adapters/runtime_model_control/test_memory_resource_gate.py
  tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py
    (Main×Dedicated Role全6組み合わせをカバーするParametrized Test 1関数、§3.4参照)

変更Test(3件):
  tests/unit/runtime_model_control/test_role_lifecycle_manager.py
  tests/unit/runtime_governance/test_semantic_runtime.py
  tests/integration/test_real_local_semantic_109_batched_judge_smoke.py

Docs(本File新規、および phase_index_ja.md 更新)

上記以外のSource／Test変更は本Addendumでは0件。
```

## 8. Network／Artifact／Active Process Inventory

```text
Network Access   : 0件
Artifact変更     : 0件
Real Model Load  : 0件(本Addendumの実機Evidenceはpsutil実測値とRegistry実size_bytesの
  みで、実GGUF LoadはPackage 2本体分から新規に追加していない)
Dependency Install: 0件(psutilは既存依存関係)
Git Action       : 0件
Backup Action    : 0件
User runtime_data接触: 0件
```

## 9. Recovery / Exact Next Route

```text
Package 2残作業(OF-P2-003・OF-P2-001)は本Addendumで完了した。
OF-P2-002は引き続きUser実機確認待ちで保留。
OF-P2-005(新規、逆方向Gate)はController Review対象のOpen Findingとして引き継ぐ。

次に必要なのはUser自身による実画面(ブラウザ)でのMac Manual Recheckである
(Phase Index Next Authorized Sequence #8、Package 2 Handoff §5「Manual／
Observability Truthfulness」参照)。これは本Addendum自体が実行許可を兼ねる
ものではなく、Userが実際に行う。

本Addendum提出後、実行は一旦停止する(User指示「完了して僕の実機テストまで
行ったら一旦作業停止」に基づく)。Package 3着手は、User Manual Recheckの
結果とUser自身の明示的なPackage 3開始宣言を経てからとする(変更なし、
Package 3 Handoff §2 Mandatory Entry Audit項目6・7)。
```

## 10. Claim

```text
Maximum Claim: P9_1_JUDGE_SEMANTIC_AND_MAIN_RUNTIME_ENFORCE_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

Package 2 Exact Return(base_return)の最大Claimを変更しない。Phase 9-1 Closure、User Final Acceptance、Phase 9-2 Readyのいずれも主張しない。
