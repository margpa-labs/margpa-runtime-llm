# Phase 5-0 Entry Preflight／As-built Reconciliation／Threat Model／Execution Freeze

```yaml
document_id: phase_5_0_entry_preflight_reconciliation_and_execution_freeze_20260822103200
status: append_only_evidence
phase: phase_5
subphase: phase_5_0
work_units: P5-0-WU-001, P5-0-WU-002, P5-0-WU-003, P5-0-WU-004
recorded_at: 2026-08-22 10:32:00 JST
git_mutation: not_performed
```

Recovery Entry：本Documentが現時点のPhase 5最新Entry。先行するPointerは`docs/project/phases/phase_5/phase_index_ja.md`第8節。

## 1. P5-0-WU-001 Entry Preflight（Read-only）

```text
Phase 4 Closure                 : COMPLETE／ACCEPTED／CLOSED（確認済み）
Phase 5 Frozen Package           : Requirements/Architecture/ADR/Governance/Execution Plan/Acceptance Matrix/
                                    Index/Handoff 全文読了済み
User Backup                     : USER REPORTED COMPLETE（AI Read／Mutation NOT PERFORMED）
Codex Activation Preflight/ARMED: PASS（Receipt確認済み）
Authorized Root                 : margpa-runtime-llm/ 直下のみ
Current Qwen Route              : main.qwen3-4b-q4-k-m（config/models/qwen3_4b_q4_k_m.toml存在確認）
Working Tree                    : Dirty（Phase 2/3/4 Docs/Source/Test、既知・想定内。Known Dirty Working Treeとして
                                   ARMED Receiptに記載済み）
Git Mutation                    : NOT PERFORMED（本Cycle開始時点でbranch=main、`git status`/`git branch`は
                                   Read-onlyのみ実行）
User runtime_data/              : 内容非参照（存在有無の`git status`表示のみ認識）
Baseline Test（本Cycle実測）     : Backend 1048 passed／3 deselected、Frontend 155 passed、
                                   ruff check／mypy／frontend typecheck・lint 全てPASS
                                   （Phase 4 Minimal Closure記載値と一致）
```

## 2. P5-0-WU-002 Phase 4 As-built Compatibility Matrix

Phase 4 Runtime Governanceの実Source構造を確認し、Phase 5がAdditive Compositionとして接続する境界を固定する。

```text
既存Module              : src/margpa_runtime_llm/modules/runtime_governance/**（domain/application/ports/public）
既存Bootstrap           : src/margpa_runtime_llm/bootstrap/runtime_governance.py
                          （RuntimeGovernanceComposition、build_main_model_governance_hooks）
既存統合点              : src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
                          （governance_pre_hook／governance_post_hook、Optional Constructor引数として注入）
既存Web Route           : src/margpa_runtime_llm/web/runtime_governance_routes.py（Read-only Status）
既存Configuration Control: src/margpa_runtime_llm/modules/configuration_control/**
                          （main_governance_modeがPreview→Apply CASの独立Field）
既存Frontend            : frontend/src/components/RuntimeGovernancePanel.tsx、
                          frontend/src/lib/runtimeGovernanceBootstrap.ts
                          （#runtime-governance-bootstrap Tag、独立Bootstrap Flag）
```

Phase 5の接続方針（Additive、既存内部Rewriteなし）：

1. `ConversationGenerationService`へ`guardrail_pre_hook`／`guardrail_post_hook`／`guardrail_stream_guard`を、既存`governance_pre_hook`／`governance_post_hook`と同型のOptional Constructor引数として追加する。既存Phase 4 Hookの型・呼び出し順・意味は変更しない。
2. Guardrail Pre-hookはPhase 4 `governance_pre_hook`より先に評価する（Input Rejectは最も安価なEarly-out、かつSecurityはRuntime Governanceより上位の境界であるため）。
3. Guardrail Post-hookはPhase 4 `governance_post_hook`の後、Persistence Commitより前に評価する（Architecture第6.3節のTerminal順序）。
4. Guardrail Stream GuardはOptionalとし、`None`の場合は`_run_stage`の既存Per-chunk Yield Loopを一切変更しない（Byte-identical経路。P5-ACC-004のGuardrail OFF Call 0／既存同値をComposition Root Wiring自体で保証する）。
5. Guardrail独自のBootstrap（`bootstrap/guardrail_governance.py`）、独自Web Route（`web/guardrail_governance_routes.py`）、独自Configuration Control Field（`guardrail_mode`）、独自Frontend Panel（`GuardrailPanel.tsx`）、独自Bootstrap Tag（`#guardrail-bootstrap`）を新設する。Phase 3／4の同名Module／Fieldは変更しない。

## 3. P5-0-WU-003 Threat Model／Trust Boundary（要約）

```text
Threat                          | Asset                    | Boundary                     | Failure Mode
Direct Prompt Injection         | Model Instruction整合性  | guardrail.input              | Instructionへの偽装採用
Indirect Injection（RAG内）      | Model Instruction整合性  | guardrail.context_source     | Retrieved TextのAuthority昇格
Secret／PII Leak（Input）        | User／System秘匿情報     | guardrail.input              | Evidenceまたは下流への複製
Secret／PII Leak（Output）       | User秘匿情報             | guardrail.output_candidate   | 未検査Output永続化
Encoded／Multilingual Evasion   | Detector正確性           | Deterministic Detector       | Pattern非検出
Streaming Leak（後でReject無効）| Client露出制御            | guardrail.stream_candidate   | 検査前Content先行送出
Authority／Approval Spoofing    | Action Authority         | Action Resolver              | AI自己発行Approval採用
Stale Policy／Authority Reuse   | 現在Authority正確性       | Snapshot Digest              | 古いGrant／Denyの黙認再利用
Approval Forgery                | Human Approval正当性      | ApprovalPort                 | AI生成Approvalの受理
Evidence Leak                   | Secret／PII非開示         | Evidence Projection          | 実値のStatus／Log混入
Over／Under-refusal             | Functional Baseline      | Mode Routing                 | OFF汚染／過剰Reject
```

Actor：User（Prompt経由）、RAG Document（間接経由）、Model自身（自己申告Approval等）。境界外（Phase 5 Non-scope）：Tool／Agent実行本体、Safety Model実Load、AWS／Lightning。

## 4. P5-0-WU-004 Exact Execution Freeze／Baseline

```text
Allowed Path Class（新規作成予定）:
  src/margpa_runtime_llm/modules/guardrail_governance/**
  src/margpa_runtime_llm/adapters/guardrail_governance/**
  src/margpa_runtime_llm/bootstrap/guardrail_governance.py
  src/margpa_runtime_llm/web/guardrail_governance_routes.py
  tests/unit/guardrail_governance/**
  tests/integration/guardrail_governance/**
  tests/integration/web/test_guardrail_*.py

Allowed Path Class（既存Additive変更予定）:
  src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
    （Optional Constructor引数追加のみ、既存Signature/挙動は非破壊）
  src/margpa_runtime_llm/bootstrap/web_application.py
  src/margpa_runtime_llm/modules/configuration_control/**（guardrail_mode Field追加）
  src/margpa_runtime_llm/web/configuration_contracts.py
  frontend/src/**（GuardrailPanel、Bootstrap Flag、App.tsx配線、translations）
  src/margpa_runtime_llm/web/static/**（Generated Static同期）
  tests/unit/configuration_control/**、tests/integration/web/test_web_app.py等の関連既存Test

Forbidden Path Class:
  definitions/、runtime_data/、models/、Existing Stable Docs／History、Project Root外全般

Baseline Test（Phase 5開始時点、本Document§1に既述）:
  Backend 1048 passed／3 deselected、Frontend 155 passed

Material Recovery境界:
  各Subphase（5-A〜5-G）完了時点でAppend-only Recovery Evidenceを作成する。

Completion Line: phase_5_g_complete_candidate
Current Dirty Tree: 本Document§1に既述、Phase 3／4 Docs／Source／Test由来（Known／Expected）
```

## 5. Subphase Recommendation

```text
P5-0-WU-001..004 : CLOSED
Next             : Phase 5-A（Contracts／Taxonomy／Ports）
Recommendation   : GO
```
