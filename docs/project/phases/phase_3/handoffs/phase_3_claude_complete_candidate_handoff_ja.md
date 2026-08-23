# Phase 3 Claude COMPLETE_CANDIDATE Handoff

```yaml
document_id: phase_3_claude_complete_candidate_handoff
status: complete_candidate
phase: phase_3
subphase: phase_3_g
work_unit: p3_g_wu_004
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
long_running_mode_active: true
created_at: 2026-08-21 22:30:00 JST
predecessor: phase_3_g_wu003_automation_compaction_final_evidence_ja_20260821220000
required_reading:
  - docs/project/phases/phase_3/handoffs/phase_3_claude_execution_handoff_ja.md
  - docs/project/phases/phase_3/architecture/phase_3_architecture_ja.md
  - docs/project/phases/phase_3/operations/phase_3_execution_plan_ja.md
  - docs/project/phases/phase_3/history/index/phase_3_g_wu003_automation_compaction_final_evidence_ja_20260821220000.md
  - "docs/project/phases/phase_3/history/index/phase_3_{a,b,c,d,e,f}_complete_recovery_ja_*.md"
```

## 0. Recommendation

**GO**（Codex Independent Reviewへ進めることを推奨する）。

理由：Frozen Design／Execution Plan／Acceptance Matrixに定義された全Work Unit（Phase 3-0〜3-G-WU-003）が実装・検証済みであり、Full Suite・Ruff・Mypy・Frontend Build/Lint/Testは全てClean、実Serverでの手動End-to-end確認（Governance Mode切替、Evidence実書込、Off時Hook Call 0）も完了している。既知のDeferred Evidence・Open Findingはすべて本Handoffおよび各Recovery Entryに明記済みで、隠蔽Falseされたものはない。Git Mutationは0件（Working Tree差分のみ）。

ただし以下2点はCodex Reviewで重点的に見てほしい（GOの中でも特に確認が必要な箇所）：
1. `web/governance_routes.py`のMode Mutation Endpoint設計が、設計書§9.2の「Configuration Control Preview/Applyへ統合」提案から意図的に逸脱している点（§3 Findings参照）。
2. `GovernanceDefinitionsRuntime`のMode状態がProcess-local（再起動でOFFへ戻る）という設計上の割り切り（§3 Findings参照）。

**Phase 3-Hには進まない。Git操作、Codex Review実行、User Acceptance、Phase 3完了宣言、Phase 4開始のいずれも本HandoffをもってStopする。**

## 1. Scope Covered

Phase 3-0（Preflight）〜Phase 3-G-WU-003（Final Evidence）まで、Frozen Design Package／Execution Plan／Acceptance Matrixに定義された全Subphase・全Work Unitを実装・検証済み。

```text
Phase 3-0  Preflight                                          : COMPLETE
Phase 3-A  Audit／Evidence Domain（Identity/Event/Canonicalization）: COMPLETE
Phase 3-B  Local JSONL Evidence Store Adapter                 : COMPLETE
Phase 3-C  Definition Manifest／Provider／Repository State     : COMPLETE
Phase 3-D  Trusted Adapter Registry／Normalized Governance IR  : COMPLETE
Phase 3-E  Compiler／Unbound Compiled Plan                     : COMPLETE
Phase 3-F  Runtime／Web／UI／Generation Observation統合         : COMPLETE（WU-001〜006）
Phase 3-G  Integrated Verification／Completion Candidate       : WU-001〜003 COMPLETE、本Handoff＝WU-004
```

各Subphaseの実装詳細・Exact Mutation・個別Test結果は、対応するRecovery Entry（`docs/project/phases/phase_3/history/index/phase_3_{a..f}_complete_recovery_ja_*.md`）へのLinkとし、本HandoffではPhase 3全体のExact Mutation集約とFinal Validationのみを記載する（定型情報の重複を避ける）。

## 2. Exact Mutation（Phase 3全体、集約）

### 2.1 新規Created（主要File、Directory単位）

```text
Backend:
  src/margpa_runtime_llm/modules/audit_evidence/                （Domain: Identity/Event/Canonicalization/Errors、Generation Observation Port）
  src/margpa_runtime_llm/adapters/audit_evidence/                （In-memory／Local JSONL Evidence Store、Evidence Generation Observer）
  src/margpa_runtime_llm/bootstrap/audit_evidence.py
  src/margpa_runtime_llm/modules/governance_definitions/         （Manifest/States/Errors/Adapter Registry/Normalized IR/Compiler/Cache/Mode/Runtime）
  src/margpa_runtime_llm/adapters/governance_definitions/        （Filesystem Provider、Reference Bundle Adapters）
  src/margpa_runtime_llm/bootstrap/governance_definitions.py
  src/margpa_runtime_llm/web/governance_routes.py
  src/margpa_runtime_llm/web/generation_observation.py
  definitions/manifest.json、definitions/README.md               （実17 Source／18 Definition Bundleの実Hash生成Manifest）

Frontend:
  frontend/src/lib/governanceBootstrap.ts（＋.test.ts）
  frontend/src/components/GovernancePanel.tsx（＋.test.tsx）

Tests（Backend、主要新規File）:
  tests/unit/audit_evidence/*　tests/integration/audit_evidence/*
  tests/unit/governance_definitions/*　tests/integration/governance_definitions/*
  tests/integration/web/test_governance_definitions_web_app.py
  tests/integration/web/test_governance_local_ux_recovery.py
  tests/unit/web/test_generation_observation.py

Docs（Recovery Entry／Evidence、本File含め9件）:
  docs/project/phases/phase_3/history/index/phase_3_0_execution_freeze_and_recovery_ja_20260821163349.md
  docs/project/phases/phase_3/history/index/phase_3_a_complete_recovery_ja_20260821170500.md
  docs/project/phases/phase_3/history/index/phase_3_b_complete_recovery_ja_20260821174500.md
  docs/project/phases/phase_3/history/index/phase_3_c_wu001_recovery_ja_20260821182000.md
  docs/project/phases/phase_3/history/index/phase_3_c_complete_recovery_ja_20260821191500.md
  docs/project/phases/phase_3/history/index/phase_3_d_complete_recovery_ja_20260821200000.md
  docs/project/phases/phase_3/history/index/phase_3_e_complete_recovery_ja_20260821203000.md
  docs/project/phases/phase_3/history/index/phase_3_f_complete_recovery_ja_20260821210000.md
  docs/project/phases/phase_3/history/index/phase_3_g_wu003_automation_compaction_final_evidence_ja_20260821220000.md
  docs/project/phases/phase_3/handoffs/phase_3_claude_complete_candidate_handoff_ja.md（本File）
```

### 2.2 Modified（主要File）

```text
src/margpa_runtime_llm/entrypoints/web/main.py    （--phase-3-governance-definitions系Flag、Gate Function、app.state配線）
src/margpa_runtime_llm/web/app.py                 （Governance Bootstrap Marker、Router登録、Observer配線）
src/margpa_runtime_llm/web/streaming.py            （v1 SSE ProducerへのObservation Tracker追加）
src/margpa_runtime_llm/web/persistent_streaming.py （v2 SSE ProducerへのObservation Tracker追加）
src/margpa_runtime_llm/web/persistent_routes.py     （Observation Tracker生成）
src/margpa_runtime_llm/modules/audit_evidence/public.py（Export追加）
src/margpa_runtime_llm/modules/governance_definitions/domain/__init__.py（累積Export追加）
frontend/index.html、src/margpa_runtime_llm/web/static/index.html （governance-bootstrap Marker）
frontend/src/{App.tsx,App.test.tsx,types.ts,api/client.ts,i18n/translations.ts}
frontend/src/components/SettingsModal/{SettingsModal.tsx,SettingsModal.test.tsx}
src/margpa_runtime_llm/web/static/{app.js,app.css}  （npm run build再生成、Deterministic Output）
tests/integration/web/{test_web_app.py,test_persistent_web_app.py}（Generation Observer Test追加）
tests/unit/web/test_web_cli.py                      （Governance Gate Function／Mode Value Reader Test追加）
```

### 2.3 Phase 3 Scope外（既にWorking Treeに存在した、本Handoffの対象外）

以下は**Phase 3実装開始前**、または**Phase 3実装と並行するが別Scopeの正当な作業**として既にWorking Tree上に存在しており、本HandoffのExact Mutationには含めない（Codex Reviewでも別Scopeとして区別してほしい）。

```text
docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md
  → Phase 3着手直前、User明示指示によりLong-running Mode（無確認Autonomy原則）を有効化した編集。Phase 3実装そのものではない。

docs/project/shared/history/planned_work/phase_4_0_deepseek_*.md（5 File）
  → Phase 3着手前のRoadmap Q&Aで作成されたPhase 4計画文書。Phase 3のExecution Plan／Acceptance Matrixとは無関係。Phase 4着手はしていない（本Handoffの明示的Stop対象）。

.claude/launch.json
  → 本Session中の手動End-to-end確認用Dev Server起動設定（非Git管理File、Repository機能に影響しない）。
```

### 2.4 Deleted

```text
NONE
```

### 2.5 Git Mutation

```text
Commit: 0（HEAD は Session開始時と同一： f255681 docs(phase-2): record final push postflight）
Branch: main（変更なし）
Push／Tag／Release: 0
```

## 3. Validation

```text
Backend Full Suite     : 850 passed／3 deselected（Phase 3開始前Baseline 697 → 850、Regression 0）
  3 deselected は Phase 1/2由来の既存Marker Deselectのみ（Phase 3由来のSkipは0）
Ruff Check／Format      : PASS（src, tests）
Mypy（宣言Scope=src）   : PASS — 152 source files、Error 0
  ［継続Open Finding］bare mypy（tests/全体）にPhase 2由来の既存11 Errorが残存（Phase 3 Scope外、Deferred）
Frontend Test           : 116 passed（全File）
Frontend Typecheck／Lint／Build : PASS（tsc --noEmit、eslint、vite build）
実Server手動確認         : 実Model 1往復生成でGovernance Mode=observe時にEvidence Append 2件（generation_started／generation_terminal、
                          正しいrequest_id相関・token_count・latency_ms）を確認。Mode=off復帰後は追加0件。
                          OFF→OBSERVE→OFF往復（Revision増分・実18件Definition検出）をBrowser Pane経由で確認。
                          確認後、実Server生成物（runtime_data/audit_evidence/）はrm -rfで削除済み（User実Data非該当のTest副産物）。
```

## 4. Findings（Deferred Evidenceとして明記、隠蔽なし）

1. **Mode Mutation Endpoint設計の逸脱**：設計書§9.2は「Mode MutationをExisting Configuration ControlのPreview/Applyへ統合する」ことを提案しているが、本Phaseでは`POST /api/v3/governance/mode`という専用Endpointとして実装した。理由：Configuration ControlのRevision／Digest CASスキーマはGovernance Modeの状態機械（3値・Enforce常時Rejected）と型的に噛み合わず、統合には別途のSchema設計Workが必要と判断し、既に大きいWork Unit集合の上にこれ以上のScope拡張をしないことを優先した。安全性特性（Enforce Reject、無効Downgrade禁止）はConfiguration Controlと同等に満たしている。`web/governance_routes.py`のModule Docstringに明記済み。
2. **Governance ModeはProcess-local**：`GovernanceDefinitionsRuntime`のMode状態はProcess再起動でOFFへ戻る（Evidence StoreのみFile永続）。設計書§1の`governance.mode`はExplicit Runtime Configurationとして記述されており、Process間永続化（例：Config File）は本Phaseでは実装していない。P3-G-WU-002のRestart Recovery Testでこの挙動自体は意図通り動作することを確認済み。
3. **構造的Passthrough Normalized IR**（Phase 3-D由来、継続）：Normalized Governance IRはRule/Evaluator/Action個別型を持たず、Source JSONのTop-level Key構造（`section_key`/`child_keys`/`value_kind`）をそのまま保持する設計。Phase 4のBinding時に個別型が必要になった場合の設計判断として引き継ぐ。
4. **Evidence Store単一Scope**：`runtime_data/audit_evidence/web_preview/`固定のScope ID一つのみ。複数Worker／複数Scopeの分離は本Phaseでは未実装（Single-worker Phase 1-G Preview Web Surfaceという既存制約と整合）。
5. **mypy bare（tests/全体）の既存11 Error**：Phase 2由来、Phase 3の新規Mutationとは無関係。`mypy src`（宣言Scope）はClean。

## 5. Manual Checklist（Codex Review前にUser／Codexが確認すべき項目）

```text
[ ] git status／git diff で、本HandoffのExact Mutation（§2.1／§2.2）とWorking Tree実State が一致することを確認
[ ] §2.3（Phase 3 Scope外）に記載したFileが、実際にPhase 3実装Mutationへ含まれていないことを確認
[ ] Phase 4 Codeへの一切の変更がないことを確認（本Handoffの記録通り、Phase 4着手は0件）
[ ] .claude/launch.json は正式Deliverableではなく、開発用Dev Server起動設定である旨を確認（削除しても機能に影響しない）
[ ] runtime_data/ 配下に、本Session由来の実Data（Evidence／Conversation）が残存していないことを確認（既にrm -rf済みだが、念のため）
```

## 6. Rollback（説明のみ、Claudeは実行しない）

Git Mutationが0件のため、Rollbackは単純にWorking Tree差分を破棄するだけで完了する。ただしこの判断・実行はUserまたはCodexが行うこと（Claude自身はGit操作を行わない）。

```bash
# 例（Userが判断の上、手動実行する場合の参考コマンド。Claudeはこれを実行しない）
git status --short          # 変更File一覧を確認してから
git checkout -- <files>     # 個別に破棄、または
git clean -fd -- <new-dirs> # 新規作成Directoryの削除（要事前確認）
```

## 7. Codex Review 入口

Required Readingは本File冒頭のFrontmatter `required_reading` を参照。Codex Independent Reviewは、設計適合・Source・Test・Security・Mode・Definition Corpus・Evidence Store・Automation Evidenceを独立Reviewし、FindingをExact Rework Handoffへ変換すること（`phase_3_execution_plan_ja.md` §10 P3-H-WU-001）。

## 8. Explicit Stop

本HandoffをもってClaude側の実行をStopする。Phase 3-H（Codex Independent Review、User Final Acceptance）、Git操作（Commit／Push／Branch操作）、Phase 3完了宣言、Phase 4開始のいずれも実行しない。次のActionはCodex側またはUser側に委ねる。
