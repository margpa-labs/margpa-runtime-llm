# Phase 9-1 Claude Fresh Session — SSS Resource Gate局所復旧 Exact Return

```yaml
document_id: phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_20260903013117
document_type: exact_return_handoff
document_state: candidate_for_controller_review
phase: phase_9
program: phase_9_1
work_package: P9_1_SSS_TARGETED_RESOURCE_GATE_RECOVERY
from: Claude Code Fresh Session
to: Codex Controller
created_at: 2026-09-03 01:31:17 JST
language: ja_with_structured_english_terms
in_response_to: docs/project/phases/phase_9/handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_handoff_ja_20260903010310.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none
```

## 1. Maximum Claim

```text
P9_1_SSS_TARGETED_RESOURCE_GATE_RECOVERY_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
```

以下はClaimしない: Phase 9-1 Complete／Package 2 Complete／Closure Ready／Blocker NONE／Production Ready／Full Restore Unnecessary／Main＋Selene Incident Resolved。

## 2. Direct Cause（再確認・変更なし）

Handoff記載どおり。`src/margpa_runtime_llm/adapters/runtime_model_control/memory_resource_gate.py`の`SystemMemoryRoleResourceGate`が`bootstrap/web_application.py`の`RoleProviderLifecycleManager`構築時に`resource_gate=`として注入されており、Main Active時のDedicated Provider（Selene／Gemma／Qwen3Guard）Activationをmemory推定だけで事前拒否していた。

## 3. Files Changed

```text
src/margpa_runtime_llm/bootstrap/web_application.py
  - `SystemMemoryRoleResourceGate` importを削除。
  - `RoleProviderLifecycleManager(...)`構築から`resource_gate=SystemMemoryRoleResourceGate(...)`引数を削除。
    resource_gate引数を渡さないことで、Constructor Default
    (`AllowAllRoleResourceGate`)にフォールバックする。
  - 削除箇所に、何を・なぜ外したか、Incident参照、`memory_resource_gate.py`は
    Incident Evidenceとして意図的に未使用のまま残すことを明記するコメントを追加。
  - `dedicated_model_definitions`、`role_provider_runtime_model_control_ref`等の
    他の変数・配線はそのまま（Factory・Authority Gate配線は無変更）。

tests/unit/web/test_web_cli.py
  - import追加: `AllowAllRoleResourceGate`
    (`margpa_runtime_llm.modules.runtime_model_control.application`)。
  - 新規Regression Test追加:
    `test_web_runtime_never_gates_dedicated_role_activation_on_a_memory_estimate`
    実Production Composition Root (`build_phase1_web_runtime()`) が
    `role_provider_lifecycle._resource_gate`として`AllowAllRoleResourceGate`型を
    構築することを確認する。Gate自身のrequired/available算式を一切import・再計算
    しない、型ベースのProduct Contract Oracle。
    修復前Source (Gate配線あり)で実行し、意図した失敗を確認済み
    (`SystemMemoryRoleResourceGate is not AllowAllRoleResourceGate`)。
    修復後は Green。

tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py
  - Source/Assertionは無変更(Gate自身の自己参照算式検証のまま)。
  - モジュールDocstringの末尾に、P9-1 SSS Recoveryにより本Gateが
    Production Compositionから外れたこと、本Testの`独立に見えるOracleが
    実はGate自身の算式を再計算する自己参照であること」は変わらないため、
    本Testの通過を「実際のMain+Dedicated Role活動がProductionで拒否される」
    Evidenceとして読んではならないことを明記する注記を追加。
    Production Behaviorの正 Evidenceは`test_web_cli.py`側の新規Testと、
    本Returnの実Load Evidence(§6/§7)であることを明示。
```

## 4. Files Deliberately Not Changed

```text
src/margpa_runtime_llm/adapters/runtime_model_control/memory_resource_gate.py
  Incident Evidenceとして完全に無変更のまま保持。Productionからは未配線
  (Quarantined／Unused)。削除・算式変更なし。

tests/unit/adapters/runtime_model_control/test_memory_resource_gate.py
  無変更。Gate単体のFixture Unit Testとしてそのまま有効。

config/application.toml, config/profiles/local_macos_arm64.toml
  無変更(diff 1f0e70eに対して差分ゼロを確認済み)。
  Task中、Userより「Main起動が2倍消費するようにした」という別件の疑義提起があり
  調査したが、この2 Fileはこのセッションでは一切触れておらず、`1f0e70e`から
  byte-for-byte一致。`context_size=8192`(local_macos_arm64.tomlの
  `[load_overrides]`)はPhase 2のCommit `851dbbf`由来で、Phase 9のこのWork
  Packageより遥かに以前から存在する設定であることをgit logで確認した。
  Userからも「そこまでは知らない」旨の回答があり、本Task Scope外の未特定事項
  として§12 Open Findingsへ記録する。本Task ScopeであるResource Gate配線には
  無関係と判断し、Source変更は行っていない。

その他、Task開始前から既にDirtyだった以下は全て無変更のまま保持:
  src/margpa_runtime_llm/adapters/evaluation/selene.py
  src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py
  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
  src/margpa_runtime_llm/modules/evaluation/application/judge_prompt_builder.py
  src/margpa_runtime_llm/modules/evaluation/domain/stage_budget.py
  src/margpa_runtime_llm/modules/runtime_governance/application/semantic_runtime.py
  src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_runtime.py
  src/margpa_runtime_llm/modules/runtime_model_control/application/__init__.py
  src/margpa_runtime_llm/modules/runtime_model_control/application/provider_selection_controller.py
  src/margpa_runtime_llm/web/provider_selection_routes.py
  (および対応する既存Dirty Test群、Docs、config/judge_templates/gemma_4_e2b/等の
  未追跡File)
  `git status --short`で本Return作成時点も、これらへの追加差分がゼロであることを
  確認済み。
```

## 5. Before／After Product Behavior

```text
Before (修復前 Source, このSession開始時点):
  Main Active時、Selene／Gemma／Qwen3Guardいずれも`resource_gate_denied:
  insufficient_memory_for_main_plus_dedicated_role`でLoad前拒否され得る
  (実測: Fresh Default Judge Gemmaも通常条件でdeny)。
  Built-in／Main-shared Judgeのみ機能する。

After (このSessionの修復後):
  `RoleProviderLifecycleManager`のResource Gateは`AllowAllRoleResourceGate`
  (Pre-Package-2 Baseline)。Memory推定によるLoad前拒否は発生しない。
  実機Evidence(§6/§7)でMain+Gemma、Main+Qwen3Guardの同時Activationが実際に
  成立することを確認した。
```

## 6. Real Gemma Evidence

実行Script: `/private/tmp/.../scratchpad/main_plus_dedicated_role_concurrent_evidence.py`
(実Production `RoleProviderLifecycleManager` + `ProductionRoleAdapterFactory`を
`web_application.py`と同一の組み方で構築、`resource_gate`は渡さず
Constructor Defaultを使用。`dedicated_model_authority_granted=True`
(Userの実運用がこの状態でOF-P2-003 Incidentを起こしたこと自体が、実運用では
Authorityが既に付与されている根拠)。Bash経由の独立Subprocessとして実行し、
仮にNative Crashが起きても本Session／他Appには波及しない構成。)

```text
Configured/Active/Executed Provider : judge.gemma-4-e2b-it-q4-0 (Gemma 4 E2B Q4_0)
Model/Artifact Identity             : config/models/gemma_4_e2b_it_q4_0.toml定義どおり
                                       (Artifact 3.35GB宣言、models/judge/
                                       gemma-4-E2B_q4_0-it/gguf/以下の実File使用)
Manifest                            : config/judge_templates/gemma_4_e2b/manifest.json

Load result  : 成功。 state=active, active_provider=judge.gemma-4-e2b-it-q4-0,
               failure_reason=null。
               process RSS: Main単独3.572GB → Gemma同時Load後4.543GB
               (+0.97GB。3.35GB宣言Artifactよりかなり小さい増分 — mmap/OS
               Page Cache由来と推定、未確定)。
               system available: 3.493GB → 1.285GBまで低下したが、破綻・
               例外・Crashなし。

Inference result : 実SemanticEvaluator.evaluate()実行。
               provider_state=FAILED, failure_reason=
               "malformed_output:expected exactly one JSON object, found 0"。
               既存`tests/integration/test_real_local_gemma_e2b_judge_smoke.py`
               が明示的に許容している、このArchitectureの初回実運用でありうる
               正当なFail-closed Decode失敗と同種(強制PASSにしない、実際の
               結果をそのまま記録)。Load・Dispatch・Decoder自体は例外を
               投げず、既存のFail-closed契約どおり動作した。

OFF/Unload result : 成功。state=configured、
               `semantic_evaluator`が`None`にClearされたことを確認。
               RSSは3.615GBまで復帰(4.543GB→3.615GB、約0.93GB解放)。

Main preservation result : 成功。Unload直後、Main(同一InferenceService、
               loaded_context_size=8192)へ実generate()を実行し、
               content="OK"を正常取得。

Active process/worker cleanup : 単一Subprocess内で完結。Scriptの
               `application.close()`後、process RSSは0.216GBまで低下。
               Script終了後、system available memoryは5.706GBまで完全回復
               (Leakなし、残存Processなし)。
```

## 7. Real Qwen3Guard Evidence

同一実行内、Gemma Unload直後に継続実行。

```text
Configured/Active/Executed Provider : guard.qwen3guard-gen-0.6b-q8-0
Model/Artifact Identity              : config/models/qwen3guard_gen_0_6b_q8_0.toml
                                        定義どおり(Artifact 0.75GB宣言)
Manifest                             : config/guardrail/qwen3guard/manifest.json

Load result   : 成功。state=active, failure_reason=null。
                process RSS: 3.621GB → 5.268GB (Main+前段のGemma Unload後
                残存込み。Qwen3Guard自体は+1.65GB相当)。
                system available: 1.845GB → 2.252GB(この時点でのVariance)。
                破綻・例外・Crashなし。

Inference result (input + output_candidate) :
                `classify_point(target=Qwen3GuardTarget.INPUT, ...)` および
                `classify_point(target=Qwen3GuardTarget.OUTPUT_CANDIDATE, ...)`
                の両方を実行。
                input:  model_id=guard.qwen3guard-gen-0.6b-q8-0, failure=none
                output: model_id=guard.qwen3guard-gen-0.6b-q8-0, failure=none
                双方ともClean Success(Malformed Outputなし)。

OFF/Unload result : 成功。state=configured、
                `guard_adapter`が`None`にClearされたことを確認。
                RSSは3.651GBまで復帰。

Main preservation result : 成功。Unload直後、Mainへ実generate()を実行し、
                content="OK"を正常取得(loaded_context_size=8192、
                Step5時点と同一)。

Active process/worker cleanup : Script全体終了後、process RSS 0.216GB、
                system available memory 5.706GBまで完全回復。
                残存Processなし。
```

## 8. Selene Disposition

```text
本Taskでは、指示どおりMain＋Selene同時Real Loadを実行していない。

確認できたこと(Source-levelで確定、実Load不要):
  `AllowAllRoleResourceGate.allow_activation()`はrole/optionに関わらず
  常に`(True, None)`を返す(role_lifecycle_manager.py、無条件・無分岐)。
  したがって、Production Compositionが`resource_gate`未指定でこのDefaultを
  使う限り、Seleneも含め、いかなるDedicated Providerも「Memory推定による
  Load前拒否」の対象には一切ならない。
  これはUserの直近の追記指示(「Seleneも元通りLoadできる所までは直したい」)
  のうち、少なくとも「Gate由来の事前拒否」の解消には対応している。

未解決のまま残るRisk(意図的、Handoff §5の明示Non-goal):
  2026-09-01の元Incident(Main Active時にSelene Activationで実際にMainが
  Crashし、Server Restartが必要になった)の技術的Root Causeは未確定のまま
  (Metal/ggml Backend競合 対 真性OOMのいずれか、または両方、未検証)。
  Gate除去によりPre-Package-2 Baselineへ戻ったということは、この元Incidentを
  引き起こした未知の脆弱性そのものも、無防備な状態でそのまま復元された
  ということである。Selene(Artifact 5.7GB宣言)はGemma(3.35GB)や
  Qwen3Guard(0.75GB)より大幅に大きく、本Return §6/§7の実測(Gemma同時Load
  後にsystem availableが1.285GBまで低下)を踏まえると、このMac・この瞬間の
  他App起動状況次第では、Main+Selene同時実Loadは今回検証したGemma/Guardの
  ケースより明確に厳しい条件になる。

  この不確定Riskを理由に、本TaskではMain+Selene同時Real Loadを意図的に
  実行していない。Controller／Userの別判断を待つ。
```

## 9. Focused／Static Verification

```text
pytest (repair後、全てGreen):
  tests/unit/web/test_web_cli.py                                         37 passed
  tests/unit/runtime_model_control/                                      (含test_role_lifecycle_manager.py,
                                                                            test_provider_selection_controller.py 等)
  tests/unit/adapters/runtime_model_control/                             (含test_dedicated_role_adapters.py,
                                                                            test_dedicated_role_adapters_production_wiring.py,
                                                                            test_memory_resource_gate.py)
  tests/unit/evaluation/                                                 (含test_selene_adapter.py)
  tests/unit/bootstrap/                                                  (含test_judge_live_integration_dispatch_router.py)
  tests/unit/runtime_governance/
  tests/integration/web/test_feature_modes_routes.py
    -> 合計 463 passed (単一 pytest 実行、上記全Directoryを一括指定)

  tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py
    -m model_smoke                                                       6 passed
    (Gate自身の自己参照算式Testとして引き続きGreen。Docstring修正のみ、
     Assertion無変更。§3参照、Production Evidenceとしては数えない)

Ruff (touched files)      : All checks passed
  (web_application.py, test_web_cli.py,
   test_real_local_main_selene_concurrent_load_resource_gate_smoke.py)
Mypy (touched src)        : Success: no issues found in 1 source file (web_application.py)
Mypy (touched tests)      : Success: no issues found in 2 source files
git diff --check          : clean (差分なし = Whitespace Error等なし)
```

## 10. Review A Findings（Product Availability／既存Acceptance／Fresh Default／正経路Regression）

```text
[OK] Fresh Default Judge Gemma: 実Load/実Activationは成功。実Inferenceも実行され、
     例外を投げず既存Fail-closed契約どおりFAILED状態を返した(malformed_output)。
     これは「安全拒否」ではなく「Decode失敗」であり、Gate由来のAvailability
     Regressionではない — 混同していないことを明示する。
[OK] Qwen3Guard: 実Load/実Activation/実Classification(input+output_candidate)
     ともにClean Success。既存Accepted Capability(事故前の状態)への復帰を
     実機で確認。
[OK] Main: Gemma/Qwen3Guardいずれの同時Load/Unload Cycleを経ても、Inference
     可能な状態を維持。loaded_context_sizeも8192のまま不変。
[OK] Built-in/Main-shared Judge Regression: 直接の実機Re-testはしていないが、
     ソース上、`ProviderKind.BUILT_IN`/`ProviderKind.NONE`は`_activate_locked`
     内で`self._resource_gate.allow_activation(...)`呼び出しに到達する前に
     Returnする(role_lifecycle_manager.py L344-366)。Main-shared Judge
     (`MainSharedJudgeRoleAdapter`)もGate未変更(dedicated_role_adapters.py
     無変更)。463件のUnit/Integration Testが全Green。Regressionなしと判断。
[OK] 新規Regression Test(`test_web_runtime_never_gates_dedicated_role_
     activation_on_a_memory_estimate`)は、Gate自身のrequired/available算式を
     一切参照しない、型ベースのProduct Contract Oracle。修復前Sourceで意図した
     Failureを確認済み(§3参照)。「Green Test != Product Capability」の
     反省を踏まえ、本Testの合格だけでなく、§6/§7の実Load Evidenceを別途
     必須Evidenceとして扱った。
[FINDING] 実機Evidence(§6/§7)は`dedicated_model_authority_granted=True`を
     明示付与して実行した(Production Defaultは`False`。CLIの
     `--phase-6-dedicated-model-authority` opt-inでのみTrueになる)。
     元のSSS Incident自体がUserの実運用でSelene/Gemma/Qwen3Guardへ実際に
     到達していたことから、Userの実運用ではこのAuthorityは既に付与済みと
     推定されるが、本Returnではこれを独立に再確認していない。Blocking
     Issueとは判断しないが、Open Findingとして§12へ記録する。
```

## 11. Review B Findings（Authority／Lifecycle／Rollback／Unload／Main保全／Worker Cleanup／Dirty Tree保全）

```text
[OK] Authority: `dedicated_model_authority_granted`のProduction Default(False)
     およびCLI opt-in配線は本Taskで一切変更していない。既存Test
     (test_web_runtime_wires_dedicated_model_authority_opt_in_into_the_
     role_provider_factory)がByte-for-byte同じAssertionのままGreen。
[OK] Lifecycle/Rollback: `RoleProviderLifecycleManager`Class自体は完全無変更
     (Composition Root側の引数を1つ外しただけ)。`_activate_locked`の
     Rollback/Cleanup Pathも無変更。
[OK] Unload: §6/§7で実機Evidenceとして直接確認(semantic_evaluator/
     guard_adapterがNoneにClearされ、RSSが実際に解放されることを実測)。
[OK] Main保全: §6/§7で2回(Gemma Unload後、Qwen3Guard Unload後)、実Generate
     呼び出しで直接確認。Main Crash/Unload/Not Loadedへの遷移は一度も
     発生しなかった。
[OK] Shutdown: `web_application.py`の`_close()`(model_access_coordinator.
     shutdown() -> application.close())は本Taskで触れていない
     (編集箇所はRoleProviderLifecycleManager構築ブロックのみ)。
[PARTIAL] Worker Cleanup(TrackedStageWorkerRegistry): §6/§7の実機Evidence
     Scriptは、Production Wiringが実際に渡す`tracked_stage_registry=`
     (Real TrackedStageWorkerRegistryインスタンス)を使わず、単純化のため
     Factoryへ渡していない(Defaultの`None`のまま)。この機構自体は本Task
     で一切変更しておらず、既存Fixtureベースの`test_dedicated_role_
     adapters_production_wiring.py`側で別途カバーされている(Green)。
     実機Load条件下でのWorker Bounded-Join自体は本Returnでは直接検証して
     いない。Open Findingとして§12へ記録する。
[OK] Dirty Tree保全: 本Return作成時点の`git status --short`は、Session開始時
     から既にDirtyだった全File(selene.py, dedicated_role_adapters.py,
     judge_live_integration.py 等)を無変更のまま維持。新規差分は
     `web_application.py`(Gate配線除去)、`tests/unit/web/test_web_cli.py`
     (Regression Test追加)、および1件のDocstring追記のみ。
     `git diff --check`もClean。Commit/Push/Stash/Reset/Checkout/Restoreは
     一度も実行していない。
[FINDING] `config/application.toml`/`config/profiles/local_macos_arm64.toml`
     はUserからの「Main起動が2倍消費するようにされた」という追加指摘を受けて
     Byte-for-byte一致(diff 1f0e70eに対しゼロ)を確認したが、User自身も
     正確な原因箇所は特定できておらず(「そこまでは知らない」)、本Task Scope
     (Resource Gate局所復旧)からは独立した、未特定のOpen Issueとして残る。
     Source変更は一切行っていない。§12参照。
```

## 12. Open Findings／True Stop

```text
True Stop: なし。本Task Scope内(Resource Gate Production Wiring除去、
　　　　　　Regression Test、Real Positive-path Evidence)は完了した。

Open Finding 1 (Main+Selene同時Load Risk, 未解決・意図的):
  §8参照。元Incidentの技術的Root Causeは未確定のまま。Gate除去により
  Pre-Package-2の無防備状態へ復帰した。Controller/Userの別判断が必要。

Open Finding 2 (「Main起動が2倍消費」疑義, 未特定・本Task Scope外):
  User指摘の技術的実体を本Taskでは特定できなかった。調査で確認できたのは:
    - config/application.toml, config/profiles/local_macos_arm64.tomlは
      1f0e70eからByte-for-byte無変更(本Taskは触れていない)。
    - `local_macos_arm64.toml`の`context_size=8192`はPhase 2 Commit
      `851dbbf`由来で、Phase 9のこのWork Packageより遥かに古い。
    - 実機Main単体Loadの実測: process RSS 3.564~3.572GB
      (Artifact宣言2.326GB比で約1.53倍。loaded_context_size=8192)。
      これがKV Cache/Metal Buffer由来の正常範囲か、何らかの重複Loadかは
      本Task Scopeでは未特定。
  UserはField/File単位までは特定しておらず、本ReturnではSource変更を
  行っていない。Controller/User側で追加調査が必要な場合、独立Issueとして
  切り出すことを推奨する。

Open Finding 3 (Worker Cleanup未実機検証):
  §11参照。TrackedStageWorkerRegistry経由のBounded-Join挙動は、実機同時
  Load条件下では本Returnで直接検証していない(Fixtureレベルのみ既存Green)。

Open Finding 4 (Authority Granted状態の実運用整合性未再確認):
  §10参照。実機Evidenceは`dedicated_model_authority_granted=True`を明示
  付与して取得した。Userの実際のCLI起動フラグ状態そのものを本Taskでは
  再確認していない。
```

## 13. Action Inventory

```text
実行した (This Session):
  - 本Handoff全文、指定Bounded Read Set(Incident記録2件、memory_resource_gate.py、
    web_application.py、RoleProviderLifecycleManager/AllowAllRoleResourceGate定義、
    関連Test群)を読了。
  - `git status --short`でDirty Tree記録(Session開始時と終了時で比較、差分なしを確認)。
  - Regression Test追加(修復前Sourceで意図した失敗を確認)。
  - `web_application.py`からGate Production Wiring除去(Minimal Diff)。
  - Regression Test含む既存Test 463件 + Gate自己参照Test 6件、Green確認。
  - Ruff/Mypy/git diff --checkをTouched Scopeで実行、Clean確認。
  - 実機Positive-path Evidence取得(Main単体、Main+Gemma、Main+Qwen3Guard、
    Main保全×2回、Cleanup確認)。独立Subprocessとして実行、System全体への
    影響なしを確認。
  - Userからの追加疑義(「Main起動2倍消費」)を調査し、本Task Scope外の
    Open Findingとして記録(Source変更なし)。
  - 完全別観点Two-stage Internal Review(Review A/B)実施。
  - 本Exact Return作成(新規File 1件のみ)。

実行しなかった (指示どおり):
  - Full Restore、git reset/checkout/restore、Stash、Commit/Push。
  - Gate算式/3 GiB Margin/Memory Heuristicの調整。
  - Main+Selene同時Real Load。
  - Network/Model Download/外部Artifact変更。
  - Package 3、Context拡張、Phase 9-2/9-3、Roadmap、Public Docsへの着手。
  - Current Index/Stable Docs/既存Historyの変更。
  - `.claude/`の作成・更新。
  - `docs/project/shared/history/planned_work/phase_11_plus_governance_
    enforce_structural_semantic_layer_split_reservation_ja_20260902214032.md`
    の閲覧(明示禁止のため未読のまま)。
```

## 14. Exact Next Action for Codex Controller

```text
1. 本Exact Returnと§6/§7実機Evidence(Log: /private/tmp/.../scratchpad/
   concurrent_evidence_run1.log、および main_only_memory_probe.py実行結果)を
   Independent Reviewする。
2. Open Finding 1(Main+Selene同時Load Risk)の扱いを決定する:
   このまま無防備で保持するか、Selene concurrent-Load自体を別Authority/
   別Taskとして明示的にBlockする運用ルールを敷くか。
3. Open Finding 2(「Main起動2倍消費」疑義)の技術的実体を、Controller/User
   側で追加調査するか、Scope外として一旦保留するかを決定する。
4. Open Finding 3/4(Worker Cleanup実機未検証、Authority Granted状態の
   実運用再確認)の要否を判断する。
5. 上記Reviewを踏まえ、Phase 9-1 Closure可否およびPackage 3着手可否を
   Controller Authorityで判断する(本Returnはこれを主張しない)。
```
