# Phase 6 Fifth Rework — Recovery Entry（Package A: Runtime Switch Integrity 完了）

```yaml
document_id: phase_6_fifth_rework_package_a_runtime_switch_integrity
status: recovery_entry
phase: phase_6
package: package_a
role: Claude側設計統括者役
created_at: 2026-08-23 20:26:58 JST
governing_handoff: phase_6_codex_fifth_independent_review_rework_handoff_ja_20260823183203.md
previous_entry: phase_6_fifth_rework_entry_package0_ja_20260823183908.md
```

## Current Package／Work Unit

Package A（Runtime Switch Integrity、対象P6-CODEX-034／035／036）完了。Package Bへ進む直前。

## Last Completed Action

P6-CODEX-036（Governance Capability RebindingのUnit Test追加、`RuntimeModelController.on_commit`
のUnit Test追加）まで完了し、Full Backend Test（`tests/`全体、real-hardware Marker除く）
1556 passed, 1 deselected、mypy strict（`src/`＋`scripts/`）エラー0、ruffエラー0を確認済み。

## Completed Findings

```text
P6-CODEX-034 CLOSED — ModelAccessCoordinatorに排他的"switch" Leaseを新設
  （try_acquire_switch_lease／release_switch_lease）。acquire_main()は
  "switch" Lease保有中は即座にMODEL_BUSYで失敗（Background待機Loop復帰後の
  再Checkも含む）。start_background()は既存の`_current_kind is not None`
  Checkがそのまま"switch"もBlockする。RuntimeModelController.begin_switch()
  はUnload前にLeaseを排他取得し、finally句で必ず解放。実Coordinatorを使った
  決定的Race Test（test_switch_rejected_while_a_real_background_task_is_
  active_via_coordinator）で、Background保持中はUnload 0／Load 0／Snapshot
  Mutation 0、Background完了後は同じSwitchが成功することを確認。

P6-CODEX-035 CLOSED — begin_switch()のRole Binding再構築を修正。旧MAIN
  Bindingを除去するだけでなく、Targetの実LoadedModelHandle／Capabilityから
  新MAIN Bindingを構築して追加（従来はMAIN Bindingが0件になっていた）。
  非MAIN Binding（Judge等）はTestで保持を確認。current_max_new_tokensは
  Target Modelのmax_output_token_limitへ明示的にClamp
  （effective_max_new_tokens = min(previous.current_max_new_tokens,
  handle.capability.max_output_token_limit)）——Silent Invalid Snapshotを
  防止。

P6-CODEX-036 CLOSED — RuntimeGovernanceComposition.rebind_capability()を
  新設。bind_point()は既にself.capabilityをLive Read（Composition
  __init__時ではなく、毎Pre／Post Hook呼び出し時）していたため、
  rebind_capability()単体で次のAttemptから新Capabilityが反映される。
  RuntimeModelController.on_commit Hook（Fifth Rework新設、成功Commit時
  のみFire、Lock解放後に実行）経由でweb_application.pyがGovernance
  Capabilityを再構築（application.service.runtime_infoから都度Live取得）。
  Rollback／Busy拒否時はon_commitが発火しないことをUnit Testで確認。
```

## Open Findings（Severity／Current Impact）

```text
P6-CODEX-037 CRITICAL FUNCTIONAL／REQUIRED — DeepSeek Multi-turn Chat
  Template/EOS非互換（Package Bで対応）
P6-CODEX-038 CRITICAL PATH SAFETY／REQUIRED — Recording Path TOCTOU残存
  （Package Cで対応）
P6-CODEX-039 CRITICAL EVIDENCE／REQUIRED — Validation/Acceptance/Return
  Contract未達（Package C／Dで対応、実Qwen Test Failure部分はPackage C）
P6-CODEX-040/P6-GOV-007 CRITICAL GOVERNANCE EVIDENCE／REQUIRED — 存在しない
  User Override記録（Package Dで対応）
```

## Exact changed files／Exact new files（Package A、本Reworkでの変更分のみ）

```text
Modified:
  src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py
  src/margpa_runtime_llm/modules/runtime_model_control/application/runtime_model_controller.py
  src/margpa_runtime_llm/modules/runtime_model_control/ports.py
  src/margpa_runtime_llm/bootstrap/runtime_model_control.py
  src/margpa_runtime_llm/bootstrap/web_application.py
  src/margpa_runtime_llm/bootstrap/runtime_governance.py
  tests/unit/runtime_model_control/test_runtime_model_controller.py
  tests/unit/runtime_governance/test_bootstrap_composition.py
  tests/unit/bootstrap/test_runtime_model_control_bootstrap.py
  tests/integration/test_runtime_model_control_smoke.py
  tests/integration/web/test_runtime_model_control_mutation_routes.py
  tests/integration/web/test_runtime_model_control_public_basic_call0.py
  tests/integration/web/test_runtime_model_control_governance_layer_identity.py

Deleted（既存の`GenerationBusyGatePort`／`ConversationServiceBusyGate`が
  `ModelAccessLeasePort`／`ModelAccessCoordinator`へ完全に置き換わり、
  不要になったため削除——死んだCodeを残さない方針）:
  src/margpa_runtime_llm/adapters/runtime_model_control/generation_busy_gate.py
  tests/unit/runtime_model_control/test_generation_busy_gate.py

New: なし（既存File内へのMethod／Class追加のみ）
```

## Executed Commands／Exit Codes／Test Counts

```text
python3 -m mypy src/ scripts/
  → Success: no issues found in 279 source files（Exit 0）

python3 -m ruff format <touched files>; python3 -m ruff check <touched files>
  → All checks passed（Exit 0）

python3 -m pytest tests/ -q --ignore=tests/integration/llama_cpp \
  --ignore=tests/integration/test_real_local_judge_smoke.py \
  --ignore=tests/integration/test_runtime_model_control_smoke.py
  → 1556 passed, 1 deselected（Exit 0）

python3 -m pytest tests/unit/runtime_model_control/ tests/unit/runtime_governance/ -q
  → 124 passed（Exit 0）
```

model_smoke（実Qwen使用）Testおよび実Browser確認は、Handoff §5の定めに従い
Package D（Final Verification）で実施する——Package A自身の完了条件は
Unit／Integration／Race Testで満たされている。

## Active Process／Model Load／Scratch State

```text
Active Process: margpa_runtime_llm.entrypoints系のProcessは0件。
Model Load State: 現在いずれもUnload（Preview Server未起動）。
Scratch State: `.venv/.t/phase_6_fifth_rework_<timestamp>/`配下の新規作成は
  Package A時点でまだ発生していない（Source／Test変更のみ、実Model Load
  はPackage B／Dで発生予定）。
```

## User runtime_data Contact Count

0。

## Root-outside／Git／Network／Provider Memory Action Count

0（Package A自身での新規発生なし）。

## Artifact／Snapshot／DigestのCurrent State

```text
Qwen Artifact: main.qwen3-4b-q4-k-m、sha512=f182f1d4...（未変更）
DeepSeek Artifact: main.deepseek-r1-0528-qwen3-8b-q4-k-m、
  sha512=b32af428...（未変更）
config/models/*.tomlは未変更。
```

## Exact Next Action

Package B（DeepSeek Multi-turn Chat Template Compatibility、対象
P6-CODEX-037）を開始する。長時間の実Model Callへ入る直前に、Handoff §5の
定めに従い`history/index/phase_6_fifth_rework_package_b_pre_model_run_*_ja_
<timestamp>.md`を作成すること。最初の実施内容：

```text
1. 対象GGUF（DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf）の
   Embedded Chat Template（tokenizer.chat_template）、BOS/EOS Token ID、
   tokenizer.ggml.eos_token_id、Turn Separator表現を、vocab_only=Trueの
   Read-only Metadata LoadでExact As-builtとして再確認する
   （前Fourth Rework時点で `tokenizer.ggml.eos_token_id = 151645` かつ
   Templateが挿入するEOS区切り文字列トークナイズ結果が別Tokenへ分解される
   不一致を確認済み——この不一致の根本原因をSource側で特定する）。
2. src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py
   のstop_token_ids構築ロジックを読み、Qwen固有前提（tokenizer.chat_template
   のenable_thinking判定等）がDeepSeekへ無条件流用されていないか確認する。
3. Model Definition側（config/models/deepseek_r1_0528_qwen3_8b_q4_k_m.toml）
   で修正すべき項目があれば、実測値に基づいてのみ更新する。
```

## Exact Resume Command／Resume手順

```text
1. 本Entryおよび phase_6_fifth_rework_entry_package0_ja_20260823183908.md を読む。
2. `git status --porcelain`で本Entry作成時点からの増分Diffを確認する。
3. 上記「Exact Next Action」からPackage Bを開始する。
4. Package B完了条件（Handoff §5）を満たしていない場合、未完了の
   Findingから継続する。
```
