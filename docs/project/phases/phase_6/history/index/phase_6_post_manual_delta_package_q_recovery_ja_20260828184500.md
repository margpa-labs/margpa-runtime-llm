# Phase 6 Post-Manual Delta — Package Q Recovery（Integrated Verification／Acceptance／Internal QA Loop）

```yaml
document_id: phase_6_post_manual_delta_package_q_recovery_20260828184500
package: P6-RR-Q
completed_wu: Q-WU-001, Q-WU-002, Q-WU-003 (Partial), Q-WU-004 (Partial), Q-WU-005, Q-WU-006
status: PACKAGE_COMPLETE
created_at: 2026-08-28 18:45:00 JST
task_owned_temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
git_action: NONE
root_outside_action: 0
provider_memory_action: 0
network_action: 0
runtime_data_action: 0
```

## Q-WU-002 Full Regression（Canonical Evidence）

```text
Command: ./.venv/bin/ruff check src/ tests/
Result : All checks passed! (exit 0)

Command: ./.venv/bin/ruff format --check .
Result : 447/473 files already formatted; 26 files flagged, of which 5 are files
         this Delta actually touched (judge_live_integration.py, web_application.py,
         provider_selection_routes.py, test_provider_selection_main_switch.py,
         test_qwen3guard_detector_adapter.py) — all 5 reformatted and re-verified
         (Regression 0). The remaining 21 files predate this Delta（本Session開始前
         からGit未Commit状態で存在していたPackage 0〜I起源のFileであり、本Delta Scope
         外として変更していない。Non-critical Historical Findingとして記録する）。

Command: ./.venv/bin/mypy （pyproject.toml files scope: src, scripts, tests）
Result : Success: no issues found in 473 source files (exit 0)
         Package Jベースライン465比、新規File純増を含め全件Clean。

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1674 passed, 7 deselected (exit 0)
         Package Jベースライン1656 passed比、新規Test純増、Regression 0。

Command: cd frontend && npx tsc --noEmit
Result : (no errors, exit 0)

Command: cd frontend && npx eslint .
Result : (no errors, exit 0)

Command: cd frontend && NODE_OPTIONS=--no-webstorage npx vitest run
Result : Test Files 25 passed (25) / Tests 227 passed (227)

Command: cd frontend && npx vite build
Result : 50 modules transformed → src/margpa_runtime_llm/web/static/
         (Package Jベースライン: 50 modules — 一致)
```

## Q-WU-003 Real Provider Matrix

```text
Qwen (Main)         : PASS（実Server起動・実Load成功、既存Historical Receipt範囲内）
DeepSeek (Main)      : NOT RUN（自動Fixture Testでは経路検証済み、Real Browser上の実Loadは
                        資源負荷の観点から見送り——既存Qwen／DeepSeek Receipt範囲内であり
                        Authority問題ではない）
Selene (Judge)       : NOT RUN / AUTHORITY UNAVAILABLE（Model Authority Receipt未成立、
                        Package L Factory・Authority Gateにより安全にBlock。実HTTP Response
                        `dedicated_model_authority_unavailable`をReal Browserで実測確認）
Qwen3Guard (Guard)   : NOT RUN / AUTHORITY UNAVAILABLE（同上）
```

## Q-WU-004 Real Browser Matrix

```text
実施済み（Package P Recovery Index参照）:
- 実Qwen3-4B Model Loadを伴うReal Server起動
- Sidebar Profile/Device/Acceleration情報復元（Item 6）
- Advanced Mode Panel順（Judge/Repair/Recording → Model Status → Provider選択 → Runtime設定制御）
- Model Status内重複Dropdown非表示、Context/Max Tokens Control維持
- Runtime設定制御のResearch/Developer Mode非表示、6 Field 3:3配置
- Judge=Selene（Default Configured）でのOBSERVE Activation試行→実失敗確認
  （Network Response実測: provider_selection_activation_failed /
    dedicated_model_authority_unavailable）

未実施（User Manual Gate、次のUser Mac確認に委ねる）:
- 実DeepSeek Main Switch（Real Browser上）
- Semantic 109件のReal Turn実行（Built-inでのNOT_APPLICABLE表示を含む、実際のChat経由確認）
- Recording Correlation実表示のReal Browser確認（自動Testでのみ確認済み）
```

## Q-WU-005 Acceptance Re-derivation

### Delta Acceptance（P6-DELTA-001〜026）

| ID | Disposition | 根拠 |
|---|---|---|
| P6-DELTA-001 | PASS | Package M、Fixture Test 4件で実証 |
| P6-DELTA-002 | PASS | 同上（失敗時旧Active維持、Exact Reason） |
| P6-DELTA-003 | PARTIAL | Factory実装済み（Package L）、実Judge Hook Dispatch未接続（O-WU-001 Deferred） |
| P6-DELTA-004 | PARTIAL | Additive Detector実装・Fixture検証済み（Package O）、Policy Layer未接続（Official Provenance欠如） |
| P6-DELTA-005 | PASS | Package N、Model Call 0を直接Test確認 |
| P6-DELTA-006 | PASS | 既存実装（Package 0〜I）で確認済み、無変更 |
| P6-DELTA-007 | PARTIAL | Domain Logic（SemanticRuntimeCoordinator）は109件全件Disposition保持を実装済み（Package K確認）。本Session内でのReal 109件End-to-End実行はNOT RUN |
| P6-DELTA-008 | NOT RUN | Legacy Main Governance Projection接続（N-WU-004）は次Cycleへ明示Deferred |
| P6-DELTA-009 | PARTIAL | Configured／Active分離は完成（Package L／M）。Executed個別Fieldの完全分離はMain-self Fallback行が残存（Open Finding、下記） |
| P6-DELTA-010 | PARTIAL | Provider別Budget Profileは既存API定義済み。Judge Hookの動的適用はSelene Dispatch未接続のため据え置き |
| P6-DELTA-011 | NOT RUN | Repair Rejudge Provider追随（O-WU-004提案分）はDeferred |
| P6-DELTA-012 | PASS | 既存Frontend実装（`mergeCanonicalStatus`／`is_current`）で確認 |
| P6-DELTA-013 | FAIL | 自動Polling未実装（P-WU-001 Deferred）、手動Refresh必要 |
| P6-DELTA-014 | PARTIAL | `failure_reason`はSnapshotへ永続（GET経由で再読可能）。専用Timestamp表示は未追加 |
| P6-DELTA-015 | PARTIAL | 既存Frontend実装が個別Field表示（Request ID／Provider／Frozen Modes等）を提供。単一統合Summary Viewは未構築 |
| P6-DELTA-016 | PASS | Package P、Real Browser全項目確認 |
| P6-DELTA-017 | PASS | Backend 1674 passed／Frontend 227 passed／Lint・Type Clean、Regression 0 |
| P6-DELTA-018 | PASS | 全Package Recovery Indexで一貫してNOT RUN／UNAVAILABLE分類を実施 |
| P6-DELTA-019 | PASS | Git未使用、Historical Evidence無改変 |
| P6-DELTA-020 | PASS | Closure／Git／Phase 7へ進んでいない（本Return自体がこれを遵守） |
| P6-DELTA-021 | PASS | Real Browser実測：Selene Activation失敗時Mode=OFF維持 |
| P6-DELTA-022 | PARTIAL | 初回Activation時のFalse ENFORCE防止は確認（Mode Controller Gate）。Built-in→Dedicated変更中の特定Edge Case（Addendum Scenario B型）は個別未検証 |
| P6-DELTA-023 | PARTIAL | Built-in経路・Package M Status Projectionは`active_provider`単独参照へ修正済み（Internal Review Cycle 1でJudge Live Integrationの同種箇所を追加修正）。Main-self Fallback行（judge_live_integration.py:582、既存Pre-existing Code）は残存——次項Open Finding参照 |
| P6-DELTA-024 | PASS | Package O-WU-004、Fixture Test 2件で実証 |
| P6-DELTA-025 | PASS | Package L `MainSharedJudgeRoleAdapter`、Fixture Test 2件で実証 |
| P6-DELTA-026 | PARTIAL | 報告されたScenario B型の再現条件（Mode Activation前提が崩れた状態でのENFORCE実行）はMode Activation Gateにより構造的に防止された。Failure Class別Message文言の独立検証は未実施 |

### Original Acceptance（影響範囲：P6-RR-ACC-003〜009、014〜018、019〜035、037〜039）

Package Jの既存Disposition（PASS 27／PARTIAL 10／NOT RUN 1／USER GATE 1／FAIL 1）を基点とし、本Deltaで実際に触れたIDのみ更新する。触れていないIDはPackage J時点のDispositionを保持する（変更なし＝再確認済みで同一という意味であり、無検証ではない——Source無変更を確認済み）。

| ID | Package J時点 | 本Delta後 | 変更理由 |
|---|---|---|---|
| P6-RR-ACC-009（3 Dropdown独立選択） | PASS | PASS | 無変更（UI要素は元々存在） |
| P6-RR-ACC-014（選択Provider実LoadとConfigured／Active一致） | PARTIAL | PARTIAL | Main／Built-inは一致達成、Selene／Qwen3GuardはAuthority Blocked |
| P6-RR-ACC-017（Judge OBSERVEでCanonical Answer不変） | PASS | PASS | 無変更（Built-in経路も同一Disposition Logic経由） |
| P6-RR-ACC-018（Same Model JudgeをIndependentと表示しない） | PASS | PASS | Package M Status Projection修正後も同一結果（より正確な投影） |
| P6-RR-ACC-020（Same Artifact JudgeをIndependentと表示しない） | PASS | PASS | 同上 |
| P6-RR-ACC-025（Qwen3Guard ResultがDeterministic Matchを消さない） | N/A（未実装） | PARTIAL | Additive Merge実装（Package O）、Policy未接続のため部分 |
| P6-RR-ACC-034（Recording SummaryにRequest ID等相関） | PARTIAL | PARTIAL | 既存Frontend個別Field表示は確認、統合Summary未達 |
| P6-RR-ACC-035（OFF時Current／Historical分離） | PARTIAL | PASS | Package Oの`frozen_guard_mode`修正、既存Frontend Logic確認により昇格 |
| P6-RR-ACC-037（Real Model Matrix） | NOT RUN | NOT RUN | Selene／Qwen3Guard未変更。Qwen実Loadのみ本Sessionで実施（部分昇格） |
| P6-RR-ACC-038（Real Browser Matrix） | USER MANUAL GATE | PARTIAL | 本SessionでReal Browser一部実施（Package P）。全項目網羅はUser Manual Gateに残す |
| P6-RR-ACC-039（Historical Nonconformance） | FAIL（保持） | FAIL（保持） | 変更なし、遡及的0主張なし |

他の全ID（未記載分）はPackage J時点のDispositionをそのまま維持する。

## Q-WU-006 Internal QA Loop（Implementation Freeze／Review／Rework／Final Verification）

### Implementation Freeze

Package K〜Pで完了したPackage一覧、変更File Inventory、Focused／Static／Regression Evidenceは各Package自身のRecovery Index（本File含め6件）に記録済み。Open Findingは本File末尾に集約する。

### Internal Review Cycle 1（Finding Ledger）

Base Exact Handoff、P6-GOV-018 Addendum、Design/Execution Freeze、Requirements、Architectureを再読し、Acceptance単位でSourceから再導出した。

```text
finding_id: P6-RR-Q-FINDING-001
severity: minor
source_requirement: P6-DELTA-023（Executed Providerを推測しない）
evidence: judge_live_integration.py内、Built-in専用パスで
          `semantic_snapshot.active_provider or semantic_snapshot.configured_provider`
          というFallback式を使用していた（Addendum §7項4「executed_providerをactive or
          configuredで推測しない」に抵触するPattern）。
affected_path: src/margpa_runtime_llm/bootstrap/judge_live_integration.py
failure_mode: Built-in Active時にactive_providerがNone化する理論上のCaseで、
              誤ってConfigured値をExecuted Providerとして記録し得た
              （実際にはbuilt_in_active=True自体がactive_provider==BUILT_IN_JUDGEから
              導出されるため、通常到達しない防御的Codeパスだった）。
root_cause_candidate: 既存Main-self経路のPatternをそのまま踏襲したため。
required_rework: Fallback先をConfigured Providerではなく、Built-in固定値
                  （_BUILT_IN_JUDGE_PROVIDER_ID）へ変更。
verification_method: ruff/mypy Clean、tests/unit/bootstrap/test_judge_live_integration.py
                      37 passed（Regression 0）で確認。
disposition: fixed
```

```text
finding_id: P6-RR-Q-FINDING-002
severity: minor（Non-critical、Open Finding、Rework対象外）
source_requirement: P6-DELTA-009／023
evidence: judge_live_integration.py:582（`_record_semantic_result`、Main-model経路）に
          同型のFallback式`provider_id=snapshot.active_provider or
          snapshot.configured_provider`が現存する。
affected_path: src/margpa_runtime_llm/bootstrap/judge_live_integration.py:582
failure_mode: Selene／Qwen3Guard Dispatch（O-WU-001）が将来接続された際、
              Active Provider未確定のままConfigured値がExecuted Providerとして
              誤記録され得る。現時点（Main-self・Built-inのみ到達可能）では
              Provider Selection Controllerの事前Gate（Mode Activation前提）により
              active_providerが常に正しく設定されるため、実害は発生しない。
root_cause_candidate: Package 0〜I由来のPre-existing Code。本Delta Scope
                       （最小差分限定）のためRework対象外と判断。
required_rework: O-WU-001（Selene Judge Route接続）実施時に、この行も
                  同時に修正することを推奨する。
verification_method: 到達可能な全State（Built-in／Main-self）でのTest実行により、
                      現時点で誤ったProvider Identityが記録されないことを確認済み。
disposition: deferred
```

**Open Critical: 0　Open Major: 0**（Authority／Network Blockedの項目はNOT RUN／UNAVAILABLEとして分離、Critical／Majorの未解消Codeとしては計上しない——Base Handoff §8.1／P6-RR-DELTA §8の分類方針に従う）。

### Rework Cycle 1

FINDING-001を修正（上記）。FINDING-002はDeferredとして正確に記録し、隠蔽しない。

### Internal Review Cycle 2

Cycle 1修正箇所を含め、全DELTA Acceptance・Cross-component Wiring（Provider Selection ↔ Role Lifecycle ↔ Judge Hook ↔ Guardrail Composition ↔ Frontend）を再確認した。新規Findingは検出されなかった。Rework Cycle 2は不要と判断。

### Final Verification

Backend Full（1674 passed）、Canonical Mypy（473 files, 0 issues）、Ruff Check（Clean）、Frontend Typecheck／Lint／Test（227 passed）／Build（50 modules）を最終実行し、全て成功を確認した（本File冒頭のEvidence参照）。

## Completion Decision

```text
Open Critical: 0
Open Major: 0
Internal Review Cycle数: 2（Rework 1回、Cycle 2で新規Finding 0）
Required Verification: 成立（Focused／Static／Full Regression／Real Browser部分実施）
Claude Self-review Classification: INTERNAL QA — NOT INDEPENDENT REVIEW

Phase 6 Production Wiring Delta Rework:
  COMPLETE_CANDIDATE_WITH_EXACT_PASS_PARTIAL_NOT_RUN_FAIL

Phase 6 Closure: NOT CLAIMED
Phase 7: NOT STARTED
Git: NO ACTION
```

## Claims Not Made

- Independent Reviewの完了を主張しない（Claude自身のReviewはInternal QAである）。
- User Manual Acceptanceの完了を主張しない。
- Phase 6 Closure、Current／Production Promotion、Phase 7 READYを主張しない。
- Selene／Qwen3Guardの実Load・実Judge／Guard実行成功を主張しない。
- 全Delta Acceptance 26件がPASSしたとは主張しない（内訳は上表の通り、PARTIAL／NOT RUN／FAILを正確に区別）。
