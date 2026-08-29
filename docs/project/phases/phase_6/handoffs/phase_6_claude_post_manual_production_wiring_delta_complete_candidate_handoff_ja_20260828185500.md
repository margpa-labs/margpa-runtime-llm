# Phase 6 Claude Post-Manual Production Wiring Delta — Complete Candidate Return Handoff

```yaml
document_id: phase_6_claude_post_manual_production_wiring_delta_complete_candidate_handoff_20260828185500
from_provider: Claude
from_role: 設計者兼実装者役
to_provider: Codex
to_role: プロジェクト責任者兼設計統括者役
status: COMPLETE_CANDIDATE_WITH_EXACT_PASS_PARTIAL_NOT_RUN_FAIL
created_at: 2026-08-28 18:55:00 JST
base_handoff: phase_6_claude_post_manual_production_wiring_delta_exact_handoff_ja_20260827211749.md
addendum: phase_6_claude_post_manual_production_wiring_delta_exact_handoff_addendum_ja_20260827215158.md
phase_6_closure: NOT_CLAIMED
phase_7: NOT_STARTED
git_action: NONE
independent_review: NOT_CLAIMED
user_manual_acceptance: NOT_CLAIMED
```

## 1. Provider／Role／Task Identity

Provider: Claude／Role: 設計者兼実装者役／Task Identity: 本Fresh Claude Task（Bootstrap Receiptに記載の通り旧Context非継承）。

## 2. Frozen Contract Digest Verification

Base Exact Handoff・Addendum・Mandatory Reading 23文書は本Task冒頭でSHA-512照合済み、全件MATCH（Receipt既送付）。本Return作成時点でこれらFrozen Contractへの変更は行っていない。

## 3. Status

```text
Phase 6 Production Wiring Delta Rework: COMPLETE_CANDIDATE_WITH_EXACT_PASS_PARTIAL_NOT_RUN_FAIL
Internal Review Cycle数: 2（Rework 1回実施、Cycle 2で新規Finding 0）
Open Critical: 0
Open Major: 0
Claude Self-review Classification: INTERNAL QA — NOT INDEPENDENT REVIEW
```

## 4. Completed Package／Work Unit

| Package | 状態 | 主要成果 |
|---|---|---|
| P6-RR-K | COMPLETE | Recovery／As-built Reconciliation、Source-to-Production Map確定 |
| P6-RR-L | COMPLETE | Production Factory（Selene／Qwen3Guard／Main-shared-Judge）、Authority Gate実装 |
| P6-RR-M | COMPLETE（一部Defer） | Main Dropdown実Switch接続、Status Projection修正 |
| P6-RR-N | COMPLETE | Built-in Deterministic Model Call 0化、Semantic 109件Honest NOT_APPLICABLE化 |
| P6-RR-O | COMPLETE（一部Defer） | Qwen3Guard Additive Detector、Frozen Guard Mode実値化 |
| P6-RR-P | COMPLETE（一部Defer） | Bounded Advanced Mode UI Delta全7項目、CLI Help修正 |
| P6-RR-Q | COMPLETE | Full Regression、Acceptance再導出、Internal QA Loop（Review×2、Rework×1） |

個別詳細は各Package自身のRecovery Index（`docs/project/phases/phase_6/history/index/phase_6_post_manual_delta_package_{k,l,m,n,o,p,q}_recovery_ja_*.md`）を正本とする。

## 5. Changed Files and Semantic Purpose

```text
[新規]
src/margpa_runtime_llm/adapters/runtime_model_control/dedicated_role_adapters.py
  Production Role Adapter Factory（Selene／Qwen3Guard／Main-shared-Judge）、Authority Gate

src/margpa_runtime_llm/adapters/guardrail_governance/qwen3guard_detector_adapter.py
  Qwen3Guard Additive DetectorPort実装

[変更]
src/margpa_runtime_llm/modules/runtime_model_control/application/role_lifecycle_manager.py
  active_adapter()アクセサ追加（Read-only）

src/margpa_runtime_llm/bootstrap/web_application.py
  ProductionRoleAdapterFactory配線、Qwen3Guard Detector配線、Judge Provider/Guard Mode Resolver配線

src/margpa_runtime_llm/bootstrap/guardrail_governance.py
  Qwen3Guard Additive Detector統合（3 Point全てへ）

src/margpa_runtime_llm/bootstrap/judge_live_integration.py
  Built-in Deterministic Dispatch追加、Frozen Guard Mode Resolver追加、
  Executed Provider Fallback修正（Internal Review Cycle 1 Rework）

src/margpa_runtime_llm/web/provider_selection_routes.py
  Main Dropdown実Switch Transaction接続

src/margpa_runtime_llm/web/runtime_model_control_routes.py
  Judge／Guard Identity投影をProvider Selection Controller基準へ変更

src/margpa_runtime_llm/modules/evaluation/domain/llm_judge.py
  JudgeIndependenceClass.BUILT_IN追加（Additive）

src/margpa_runtime_llm/entrypoints/web/main.py
  --phase-6-feature-modes Help文言修正（Live Generation-path効果を正確に記述）

frontend/src/App.tsx
  Sidebar Profile/Device/Acceleration情報復元

frontend/src/components/SettingsModal/SettingsModal.tsx
  Advanced Mode Panel順変更

frontend/src/components/RuntimeModelStatusPanel.tsx
  重複Main Switch Dropdown非表示（Context/Max Tokens Control維持）

frontend/src/components/ConfigurationControlPanel.tsx / .test.tsx
  Research/Developer Mode Control非表示、詳細常時表示化、Field 3:3再配置

src/margpa_runtime_llm/web/static/{index.html,app.css,app.js}
  Frontend Build成果物（上記変更を反映）

[新規Test]
tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters.py（9 tests）
tests/unit/adapters/guardrail_governance/test_qwen3guard_detector_adapter.py（6 tests）
tests/integration/web/test_provider_selection_main_switch.py（4 tests）

[拡張Test]
tests/unit/bootstrap/test_judge_live_integration.py（+5 tests）
tests/unit/guardrail_governance/test_bootstrap_hooks.py（+3 tests）
frontend/src/components/ConfigurationControlPanel.test.tsx（+2 tests）
```

Model Artifact・Canonical Definition・Config TOMLは無変更。`config/models/*.toml`／`config/judge_templates/selene/manifest.json`はRead-onlyのまま参照した。

## 6. Configured／Active／Executed／Recorded Main, Guard, Judge

```text
Main    : Configured=Active=main.qwen3-4b-q4-k-m（本Session内Real Browser実測）
Guard   : Configured=guard.qwen3guard-gen-0.6b-q8-0 / Active=none / State=configured
          （Authority未成立、正確にUnavailable表示。旧来のFabricated Active表示は解消）
Judge   : Configured=judge.selene-1-mini-llama-3.1-8b-q5-k-m / Active=none / State=configured
          （同上。Mode Activation自体がGate側で失敗し、False ENFORCE状態は発生しない）
```

`Executed`個別Fieldとしての完全分離（Configuredからの推測排除）は、Built-in経路・Package M Status Projectionでは完成。Main-self経路の`judge_live_integration.py:582`は既存Pre-existing Fallback Codeが残存（Open Finding P6-RR-Q-FINDING-002、Non-critical、実害無し、O-WU-001接続時に同時対応を推奨）。

## 7. Main Switch Result and Status Convergence

Fixture Test 4件（成功／失敗（Exact Reason保持）／No-op／Runtime Model Control未Bind）で実証。Real Browser上ではQwen Active確認済み。DeepSeekへの実Switch自体はReal Browser上で未実施（Fixture Testでは経路を検証済み、資源負荷の観点から見送り）。

## 8. Selene／Qwen3Guard Factory, Artifact, Prompt／Output Contract Identity

`ProductionRoleAdapterFactory`により両者ともFactory自体は実装済み。`dedicated_model_authority_granted=False`固定（本Handoffが許可しないため）により、`preflight()`はSymlink Target（Project Root外）へ一切接触せず`dedicated_model_authority_unavailable`で安全に失敗する。Selene Prompt Manifest（`config/judge_templates/selene/manifest.json`）・Qwen3Guard Category Mappingは、既存のFail-closed状態（`verified_official_copy: false`／Category Mapping空）を維持し、遡及的にTrueへ書き換えていない。

## 9. Built-in Model Call Count

`0`（Code Path自体がMain Model呼び出し分岐へ到達不能な構造で保証。Test `test_built_in_judge_provider_makes_zero_model_calls_and_completes_unknown`で実測確認）。

## 10. Semantic 109 Disposition Count and Remaining Reason Count

Built-in選択時：選択された全Criterion（本Session Test上は1件のFixture、Real 109件はNOT RUN）が`NOT_APPLICABLE`＋`reason_code=unsupported_mapping`で記録される。Domain層（`SemanticRuntimeCoordinator`、Package K確認、無変更）は109件全件（Batch選択分＋Budget Exhausted分）のDispositionを保持する設計を既に持つ。Legacy Main Governance表示への接続（N-WU-004）はDeferred——本Session内での改善は`judge_role`の正確性（Built-in／Main-self正確表示）に限定される。

## 11. Judge／Repair／Rejudge Budget and Provider Identity

Provider別Budget Profile（`LOCAL_MACOS_SELENE_JUDGE_BUDGET`等）はAPI Response（`/api/v6/provider-selection`）で既に正確に投影される（Package 0〜I実装、無変更、Real Browserで実測確認）。Judge Hook自体が動的にBudgetを切り替える経路（Selene Dispatch接続時に必要）はDeferred。Repair Rejudge Provider追随も同様にDeferred。

## 12. Current／Historical／OFF／Live Refresh Evidence

既存Frontend実装（`FeatureModesPanel.tsx`の`mergeCanonicalStatus`、Backend`is_current`判定）がCurrent／Historical分離を構造的に実装済みであることを確認した（無変更）。自動Live Refresh（Poll／Push）は未実装のまま（P-WU-001、Non-critical Open Finding）。

## 13. Recording Correlation Evidence

既存Frontend実装がRequest ID・Provider・Frozen Modes・Outcomeを個別Field表示する（無変更）。単一統合Summary Viewへの再構成はDeferred。

## 14. Bounded UI Result

P6-GOV-018で指定された7項目全てを実装し、実Qwen Model Loadを伴うReal Browserで視覚確認した（Package P Recovery Index参照）。Phase 9予約項目（Context 16384昇格、Progressive ENFORCE等）は混入していない。

## 15. Original Acceptance 40 Disposition

Package J時点（PASS 27／PARTIAL 10／NOT RUN・UNAVAILABLE 1／USER MANUAL GATE 1／FAIL 1）を基点とし、本Deltaが実際に触れたIDのみ再導出した（詳細はPackage Q Recovery Index参照）。主な変化：P6-RR-ACC-035がPARTIAL→PASSへ昇格（Frozen Guard Mode修正）、P6-RR-ACC-025がN/A→PARTIALへ（Qwen3Guard Additive実装）、P6-RR-ACC-037／038がAuthority境界内で部分的に実測範囲拡大。

## 16. Delta Acceptance 001-026 Disposition

```text
PASS    : 001, 002, 005, 006, 012, 016, 017, 018, 019, 020, 021, 024, 025（13件）
PARTIAL : 003, 004, 007, 009, 010, 014, 015, 022, 023, 026（10件）
NOT RUN : 008, 011（2件）
FAIL    : 013（1件、自動Polling未実装）
```

詳細根拠はPackage Q Recovery Index §Q-WU-005参照。

## 17. Focused／Static／Full／Frontend／Real Provider／Browser Evidence

```text
Backend Full   : 1674 passed, 7 deselected（Package Jベースライン1656比、Regression 0）
Canonical Mypy : 473 source files（src/scripts/tests全Scope）, 0 issues
Ruff Check     : All checks passed
Ruff Format    : 本Delta変更File（5件）は全てFormat準拠。無変更File（21件）はPre-existing
                 Divergenceとして記録（Non-critical Historical Finding）
Frontend       : Typecheck 0 errors / Lint 0 errors / Test 227 passed / Build 50 modules
Real Provider  : Qwen PASS（実Load）、DeepSeek/Selene/Qwen3Guard NOT RUN（詳細は§8参照）
Real Browser   : 実施項目・未実施項目とも本Handoff§14・Package P Recovery Index記載の通り
```

## 18. Open Critical／Major／Non-critical Findings

```text
Open Critical: 0
Open Major: 0
Non-critical Open Findings:
  - P6-RR-Q-FINDING-002: judge_live_integration.py:582のExecuted/Configured Fallback
    （実害無し、O-WU-001接続時に同時対応推奨）
  - O-WU-001 Selene Judge Route未接続（Authority Blocked）
  - N-WU-004 Legacy Main Governance Projection未接続
  - P-WU-001 Live自動更新（Poll/Push）未実装
  - P6-DELTA-022型 Atomic Mode/Provider Transition Edge Case未個別検証
  - Ruff Format Pre-existing Divergence（21 File、本Delta非変更）
```

P6-CODEX-046・047・048・049・050は本Deltaで解消したと判断する（Package L／M／N Recovery Index参照）。P6-CODEX-051（Stage Budget動的切替）・052（Official Provenance）はAuthority／Network Blockedとして正確にNOT RUN／UNAVAILABLE分類し、Open Critical／Majorとしては計上しない（Base Handoff §8.1の分類方針）。

## 19. Historical and Current Incident Accounting

P6-RR-INC-001（Root-outside Stderr Redirect、Historical）は無変更で保持。本Session中の新規Incidentは0件。

## 20. Root-outside／Provider Memory／runtime_data／Git／Network／Model Mutation Inventory

```text
Root-outside Action        : 0
Provider Memory Action     : 0
runtime_data (User実Data)  : 0（検証用は全てTask-owned Temp内に隔離）
Git Action                 : 0
Network Action             : 0
Model Artifact Mutation    : 0
Selene/Qwen3Guard Symlink Target Read/Stat/Load: 0
Qwen Symlink Target (main/のみ) Read: あり（Historical Receipt範囲内、ls -la 1回のみ、
  judge/・guard/ Subtreeへは一切接触していない）
```

## 21. Task-owned Temporary／Active Process／Loaded Model

```text
Task-owned Temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
  内訳: pytest/, ruffcache/, mypycache/, npm-cache/, tmp/,
        verification_runtime_data/, server_logs/
Active Process : 0（検証用Web Server・Browser Tabとも本Return作成前に正常終了・Close済み）
Loaded Model   : 0（検証用Server起動時にQwen3-4Bを実Loadしたが、Server終了と共にUnload済み）
```

## 22. Claims Not Made

- Independent Review完了を主張しない。
- User Manual Acceptance完了を主張しない。
- Phase 6 Closure、Current／Production Promotion、Phase 7 Readyを主張しない。
- Selene／Qwen3Guardの実Load・実Inference成功を主張しない。
- Delta Acceptance 26件全PASSを主張しない（PASS 13／PARTIAL 10／NOT RUN 2／FAIL 1、正確に区別）。
- Real DeepSeek Main SwitchのReal Browser実施を主張しない。
- Semantic 109件のReal Turn実行を主張しない（Fixture 1件のみ）。
- Git Stage／Commit／Push・Backup完了を主張しない。

## 23. Exact Next Action

Codexプロジェクト責任者兼設計統括者役によるIndependent Reviewを次Actionとする。本Return作成後、Claudeは追加Mutation・Phase 6 Closure・Git・次Phaseへ進まず停止する。
