# Phase 4 Claude Complete Candidate Handoff

```yaml
document_id: phase_4_claude_complete_candidate_handoff
status: phase_4_g_complete_candidate
phase: phase_4
subphase: phase_4_g
work_unit: p4_g_wu_003_self_review_complete_candidate
role: Claude側設計統括者役
provider: claude_code
completion_line: phase_4_g_complete_candidate
long_running_mode_active: true
created_at: 2026-08-22 01:27:10 JST
created_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor:
  - docs/project/phases/phase_4/handoffs/phase_4_claude_execution_handoff_ja.md
  - docs/project/phases/phase_4/history/operations/phase_4_activation_preflight_and_armed_receipt_ja_20260821233802.md
required_reading:
  - 本File自体（Phase 4-0からPhase 4-Gまでの連結実行に対する唯一のCompletion Handoff）
```

本HandoffはPhase 4-0からPhase 4-GまでをFrozen Boundary内で連結実行した結果のCompletion Handoffである。Phase 4-H、Git、Phase 5／6、DeepSeek Load／Promotion、AWS、Network、External Actionのいずれへも進んでいない。

## 0. Phase 4-G Recommendation

**GO**（Codex Phase 4-H Independent Major Reviewへ進めることを推奨する）。

Main Model Governance OFF／OBSERVE／ENFORCE MVPは、Qwen Current Route上でEnd-to-End（HTTP／SSE経由）に成立している。Zero Model Call on Stop（`P4-MOD-002`）とNo Ghost Completion on Reject（`P4-COM-006／007`、`P4-ACC-019／020`）という最も難しい2つの安全性質は、Ephemeral（`/api/v1/chat/stream`）とPersistent（`/api/v2/conversations/*/turns/stream`）の双方で実測されている。Public／Basic Private Governance Call 0（`P4-COM-005`）は、実装ギャップを1件発見し、その場でSourceを修正したうえでRegression Testを固定した（§2参照）。

Remaining Technical Major Finding：本Document著者（Claude）の自己申告としてはNONE。ただしこれはCodex Independent Reviewによる受理を経て初めて確定する自己申告Closure Candidateである。

## 1. Technical Blockers

NONE。Frozen Boundary内でPhase 4-G COMPLETE_CANDIDATEに到達しており、Phase 4-Hへの引き継ぎをBlockする既知の技術的問題は自己申告としてない。

## 2. Governance Incidents

### Incident A：Public／Basic Exposureに対するRuntime Governance Bindingの未Guard（本Cycle中に発見・即時是正）

`web/app.py`のApp Lifespanは、既存の`configuration_control`／`persistent_conversation`について「Local Loopback以外のExposureでBindされていたらAppを起動させずRuntimeErrorで落とす」という Hard Guardを持っていたが、同種のGuardが`runtime_governance_composition`には存在しなかった。現在のEntry Point（`entrypoints/web/main.py`）は`runtime_governance_enabled`を一度も`True`にして呼び出していないため、現状のCall 0は「Entry Pointが機能を有効化していないことによる偶然のCall 0」であり、「Appが構造的に拒否しているためのCall 0」ではなかった。

是正として、[app.py](../../../../../src/margpa_runtime_llm/web/app.py)のLifespanに、既存2件と同型のGuard（`runtime.runtime_governance_composition is not None`かつExposureがLocal Loopback以外の場合、`runtime.close()`を実行したうえで`RuntimeError("Runtime governance control requires local loopback access.")`を送出）を追加した。[test_runtime_governance_public_basic_call0.py](../../../../../tests/integration/web/test_runtime_governance_public_basic_call0.py)の`test_shared_exposure_refuses_to_start_with_bound_governance`が、`PUBLIC_DEMO`／`BASIC_PREVIEW`の両Exposureで実際にRuntimeErrorが送出されることを固定している。

本Incidentは、Codexからの指摘やUser指摘によるものではなく、`P4-F-WU-004`（Public／Basic Call-0 Regression）を実装する過程でClaude自身が発見し、Frozen Boundary内（既存Guardと同型のSource追加のみ）で即時是正したものである。

### Incident B：なし

上記以外にGovernance境界（Authority、Observe非介入、Zero Model Call、No Ghost Completion）に関するIncidentは自己申告としてない。

## 3. Controller-owned Work

以下はFrozen Boundaryにより本Cycleでは扱っていない、Controller（Codex／User）側の判断・実行が必要な項目である。

- Phase 4-H Codex Independent Major Review自体（本Handoffの唯一のNext Action）。
- User Mac Acceptance（Qwen OFF／OBSERVE／ENFORCE、UI、Restart、RAG／Persistent互換の手動確認）。
- Backup、Git Commit／Push判断（本Cycle中、Git Mutationは一切行っていない）。
- Phase 5／6実装、DeepSeek Current Load／Promotion、AWS／Network関連の一切。

## 4. Deferred Evidence／Current Impact

以下は、時間・Risk Tradeoffを踏まえてClaude自身が明示的にScope外と判断した項目であり、隠さずここに記録する。

### 4.1 `audit_evidence` JSONL Evidence Store統合（`P4-EVD-001`／`P4-F-WU-001`）：未実装

Governance Point（`main_model.pre`／`main_model.post`）のEvaluation結果・Action実行結果を永続Evidence（JSONL）として記録する統合は、本Cycleでは実装していない。理由は、Phase 3で既にDigest／Canonicalization Testが厚く張られている`local_jsonl_store.py`（第三・第四回Reworkで`P3-CODEX-010／011／012`により複数回是正済みの、最もFragileなComponentの一つ）に、時間制約下で新しいAuditEventKindを追加する変更を加えるリスクを避けたため。

**Current Impact**：`GET /api/v3/runtime-governance/status`が現在のMode／Revision／Descriptor Availabilityをリアルタイムに開示するため、運用時の可視性を部分的に代替しているが、個々のInvocationについて「いつ・どのDescriptorが・どのSeverityで・どのActionが実行されたか」を後から機械的に追跡できる永続Recordは存在しない。Codex Phase 4-H、およびUser Acceptanceにおいて、この不在を前提としたReviewを行う必要がある。

### 4.2 Runtime Governance Status／Mode操作のFrontend UI：未実装

`frontend/src/`には、Phase 4 Runtime Governance専用のUI Componentを一切追加していない（`frontend/index.html`および`governanceBootstrap.ts`に存在する`governance-bootstrap`Markerは、Phase 3 `governance_definitions`機能専用のものであり、本Phase 4 `runtime_governance`とは無関係であることを確認済み——§8「Frontend」参照）。`/api/v3/runtime-governance/status`・`/mode`は、Backend APIとしては完成しているが、これを操作するUIは存在しない。

**Current Impact**：現時点でMode切り替えはHTTP APIを直接叩く以外の手段がない。User Mac AcceptanceでOFF／OBSERVE／ENFORCEを手動確認する際は、`curl`等でMode APIを直接操作する必要がある。

## 5. Exact Mutation

以下は、Claude（本Session、Phase 4-0からPhase 4-Gまでの連結実行）が作成・変更したFileの一覧である。`git status`は他にも多数のPre-existing Mutation（未CommitのPhase 3成果、および本Session開始前に既に存在したPhase 4設計File）を含んでいるが、それらは本Cycleの成果として申告しない——具体的には`src/margpa_runtime_llm/modules/configuration_control/contracts.py`、`src/margpa_runtime_llm/web/configuration_contracts.py`、`tests/integration/web/test_persistent_web_app.py`、`tests/integration/web/test_web_app.py`、`tests/integration/web/test_governance_definitions_web_app.py`、`docs/project/shared/history/planned_work/phase_4_to_6_runtime_governance_program_design_ja_20260821220422.md`は、本Cycle中にClaudeが編集した認識がなく、Pre-existing Mutationとして扱う（SELF_REPORTED_UNVERIFIED——完全なTool Action Logを提示できないため）。

### 新規作成（Source、`src/margpa_runtime_llm/modules/runtime_governance/`）

```text
__init__.py
domain/__init__.py
domain/actions.py
domain/binding.py
domain/errors.py
domain/evaluation.py
domain/identities.py
domain/mode.py
domain/results.py
domain/snapshots.py
ports.py
application/__init__.py
application/action_resolver.py
application/binder.py
application/mode_controller.py
application/point_runtime.py
public.py
```

### 新規作成（Adapter、`src/margpa_runtime_llm/adapters/runtime_governance/`）

```text
__init__.py
deterministic_evaluator.py
reference_definition_adapter.py
registered_actions.py
```

### 新規作成（Bootstrap／Web、単独File）

```text
src/margpa_runtime_llm/bootstrap/runtime_governance.py
src/margpa_runtime_llm/web/runtime_governance_routes.py
```

### 変更（既存Source）

```text
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  — GovernancePreHook／GovernancePostHook型Alias追加、ConversationGenerationSession／
    ConversationGenerationServiceへgovernance_pre_hook／governance_post_hookパラメータ追加、
    _governance_pre_check()／_governance_post_check()の2Hookを_events_without_summary()／
    _events_with_summary()冒頭と_completed_event()冒頭へ配線。
src/margpa_runtime_llm/bootstrap/web_application.py
  — runtime_governance_enabled／runtime_governance_definitions_rootパラメータ追加、
    RuntimeGovernanceComposition構築、build_main_model_governance_hooks配線、
    WebRuntimeへruntime_governance_composition受け渡し。
src/margpa_runtime_llm/web/contracts.py
  — WebRuntimeへruntime_governance_composition: "RuntimeGovernanceComposition | None"フィールド
    追加（TYPE_CHECKING Guard付きForward Reference、bootstrap→web逆依存を回避）。
src/margpa_runtime_llm/web/app.py
  — runtime_governance_routes import、RuntimeGovernanceWebError Exception Handler、
    create_runtime_governance_router()登録、および本Cycle中に発見したLifespan Guard追加
    （§2 Incident A参照）。
```

### 新規作成（Test）

```text
tests/unit/conversation/test_conversation_generation_governance_hooks.py（7 tests）
tests/unit/runtime_governance/__init__.py
tests/unit/runtime_governance/test_binder.py（6 tests）
tests/unit/runtime_governance/test_point_runtime.py（5 tests）
tests/unit/runtime_governance/test_action_resolver.py（7 tests）
tests/unit/runtime_governance/test_deterministic_evaluator.py（8 tests）
tests/unit/runtime_governance/test_reference_definition_adapter.py（5 tests）
tests/unit/runtime_governance/test_bootstrap_composition.py（7 tests）
tests/unit/runtime_governance/test_bootstrap_hooks.py（7 tests）
tests/unit/runtime_governance/test_mode_controller.py（6 tests）
tests/unit/runtime_governance/test_concurrency_and_recovery.py（5 tests）
tests/integration/web/test_runtime_governance_web_app.py（6 tests）
tests/integration/web/test_runtime_governance_public_basic_call0.py（6 tests）
tests/integration/web/test_runtime_governance_persistent_and_rag.py（3 tests）
```

Phase 4専用Test合計：**78 tests**（実測、下記§6参照）。

### 副作用（手動編集ではないRegeneration）

```text
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.js
```

Validation Ladder実行の一環として`npm run build`をFrontend側で実行した副作用で、既存のFrontend Source（Phase 4以前から存在する`governance-bootstrap`Marker等を含む、Committされていない状態のもの）から静的Assetが再生成された。Claude自身によるFrontend Source（`frontend/src/**`）へのEdit Actionは本Cycle中に一切行っていない。

### 明示的にScope外（本Cycleで一切触れていない）

```text
runtime_data/ 配下の全て
Project Root外の一切
Git／GitHub（Commit・Push等）
frontend/src/**（Frontend Source Code）
Definitions（definitions/** — 新規Testが実File内容を検証のみ、Sourceは無変更）
audit_evidence関連Source（§4.1参照、明示的にDeferred）
```

## 6. Focused／Subphase／Full／Static／Frontend

実測Test数（本Handoff作成直前に実行、Shell出力をそのまま転記）。

```text
Phase 4専用Test（Focused）:
  uv run pytest tests/unit/runtime_governance
    tests/unit/conversation/test_conversation_generation_governance_hooks.py
    tests/integration/web/test_runtime_governance_web_app.py
    tests/integration/web/test_runtime_governance_public_basic_call0.py
    tests/integration/web/test_runtime_governance_persistent_and_rag.py -q
  -> 78 passed

Backend Full Suite:
  uv run pytest -q
  -> 985 passed, 3 deselected

Static（Backend）:
  uv run ruff check --fix  -> All checks passed
  uv run ruff format       -> 変更対象File数、内容とも冒頭のExact Mutationと一致
  uv run mypy src          -> Success: no issues found in 176 source files

Frontend:
  npm run typecheck  -> tsc --noEmit、Error 0
  npm run lint        -> eslint .、Error 0
  npm run test         -> 16 Test Files, 117 tests, all passed
  npm run build        -> vite build成功（副作用は§5「副作用」参照）
```

Phase 3 Baseline（907）からPhase 4本Cycleで+78、Backend Full Suiteは985（907 + 78 = 985で一致、Phase 4以外の新規追加はゼロ）。

## 7. OFF／OBSERVE／ENFORCE Matrix

実際にHTTP／SSE経由で実測したMatrix（`test_runtime_governance_web_app.py`、`test_runtime_governance_persistent_and_rag.py`）。

```text
                    | Ephemeral (/api/v1/chat/stream) | Persistent (/api/v2/.../turns/stream)
--------------------|----------------------------------|------------------------------------------
OFF                 | 通常応答、Governance呼び出しなし | 通常応答、Governance呼び出しなし
                     | （Bind 0、Evaluate 0、実測）     | （実測）
OBSERVE             | 実Deviation（空応答）検出後も    | (Ephemeralで実測、Persistentは同一
                     | 介入せず通常Completed（実測）    |  Session実装のため構造的に同一)
ENFORCE(Pre)        | RAG augmented Requestで          | (Ephemeralで実測)
                     | stop_before_generation発火、     |
                     | Zero Model Call実測              |
ENFORCE(Post)       | 空応答でreject_output発火、       | 空応答でreject_output発火、
                     | event:completed なし             | event:completed なし、
                     |                                   | 永続Turnにassistant Messageなし
                     |                                   | （No Ghost Completion実測）
Public／Basic       | Bound Compositionで起動失敗       | (同一Guard、Ephemeral／Persistent
                     | （RuntimeError、実測）            |  共通のApp Lifespan Guard)
```

Definition 0件（Descriptor未Load）、Reference Bundle（実File）、Invalid Bundle（Digest不一致でQuarantine相当）の3ケースは`test_bootstrap_composition.py`でOFF／OBSERVE／ENFORCE全経路を実測済み。

## 8. Qwen Manual／Automated Evidence

```text
Automated Evidence: 実測（上記§6・§7）。model_key="main.qwen3-4b-q4-k-m"（Qwen Current Route）
                     を全Test固定値として使用——実Modelへの推論呼び出しはFakeInference（
                     実LLM非稼働）を用いており、Governance Hook配線とHTTPプロトコルの正しさを
                     証明するものである。
Manual Evidence    : 実施していない（Claude Codeは対話的User操作を伴うManual Mac Acceptance
                     Testを実行できない——これは§3 Controller-owned Workの一部であり、
                     Phase 4-H以降でUserが実施する）。
```

## 9. Compaction Recovery／Human Burden

本Session中に少なくとも1回のAuto-compaction（Context Summary）が発生し、Summary直後に「作業中に利用制限に達しましたが、現在はリセットされています。中断したところから続けてください」という自動再開通知を受けた。いずれも、ユーザーへの追加確認や作業中断なしに、Summary内容を唯一の正本として作業を継続した——Human Burdenは実質ゼロ（Userからの追加入力・承認は本Cycle中一度も要求していない）。

Compaction前に完了していたWork（`runtime_governance`Core Module、`conversation_generation.py`のHook配線、`bootstrap/web_application.py`・`web/contracts.py`・`web/app.py`・`runtime_governance_routes.py`、Unit Test 8 File）はCompaction Summaryに詳細な形で保持されており、再検証なしにそのまま継続した。Compaction後に新規実施したWork（本§にて列挙）は、Compaction Summaryが「次にやるべきこと」として明示していた`test_runtime_governance_web_app.py`の続きから開始している。

## 10. Root／Git／User Data／External Evidence Class

```text
Project Root外Access       : NOT PERFORMED（自己申告、SELF_REPORTED_UNVERIFIED）
runtime_data/ Access        : NOT PERFORMED（自己申告、SELF_REPORTED_UNVERIFIED）
Git／GitHub Mutation        : NOT PERFORMED（自己申告、SELF_REPORTED_UNVERIFIED——
                               Commit／Push／Branch操作等のGit Mutationに該当するTool呼び出しを
                               本Cycle中に行った認識はない）
User実Data Access           : NOT PERFORMED（Test用Fixtureのみ、tmp_path経由の一時SQLite等）
External Service／Network   : NOT PERFORMED
Secret／Credential Access   : NOT PERFORMED
```

`REPOSITORY_STATE_VERIFIED`扱いできるのは、今この場でRead-only再検査した「§5 Exact Mutationに記載したFileが実際に存在し、記載どおりの内容であること」（Read／Bash出力で直接確認済み）のみである。「Cycle全期間にわたって上記6項目が一度も発生しなかった」という主張自体は、完全なTool Action Logの提示を伴わないため、Phase 3第五回Correctionと同じ基準でSELF_REPORTED_UNVERIFIEDとして扱う。

## Next Action: Codex Phase 4-H Independent Review only

Phase 4-H、Git、Phase 5／6、DeepSeek Load／Promotion、AWS、Network、External Actionのいずれへも進まず、ここで停止する。次のExact Routeは、Codex Phase 4-H Independent Major Reviewが本Handoffと実Sourceを独立に検証することである。
