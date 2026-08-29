# Phase 6 Post-Claude Independent Review Rework — Package R0 Entry／Resume Recovery Index（After Git Read Incident）

```yaml
document_id: phase_6_post_claude_independent_review_rework_r0_entry_after_git_read_incident_20260828183940
package: P6-RR-R0
role: entry_and_resume_recovery_index
created_at: 2026-08-28 18:39:40 JST
provider: Claude
task_identity: Current Claude Task
implementation_authority: TRUE（本Index作成後にP6-RR-R0-WU-001から発生）
```

## 0. Recovery Index Contract（本Task全体で維持）

```text
Entry Recovery Index                 : 最初のMutation／実装Commandより前に作成（本File）
Work Unit Checkpoint                 : 各Work Unit完了直後、Current Package Recovery IndexへAppend-only
Package Entry                        : 各Package開始時に作成
Package Final Recovery Index         : 各Package完了時に必ず作成
高Cost処理前Checkpoint                : Full Test／Canonical Static／Frontend Build／Browser・Model Load／
                                        長時間Command／Auto-Compaction接近／5時間制限接近／True Stop直前
Compaction／5時間制限解除後の再読       : Stable Role 3文書 + Active Exact Rework Handoff +
                                        最新Package Recovery Index + 直前Package Recovery Index +
                                        Current Package Section
Index未作成のままPackage遷移           : 禁止
```

## 1. Active Contract

```text
Path:
docs/project/phases/phase_6/handoffs/
phase_6_post_claude_independent_review_exact_rework_handoff_ja_20260828180240.md

SHA-512:
8de37770693bf84c7e6a51fb46189341a2f3035a3ccf30c19bf6dcb1284f1991a0322573c783d65153820dbdea62e6e99063f697fbded637ef65132b35d5736a

Digest verification: MATCH（本Task内で複数回shasum -a 512により確認済み）
```

併せて、Controller Independent Review Evidence（P6-GOV-019）を判断根拠として保持する。

```text
Path:
docs/project/phases/phase_6/history/operations/
phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_ja_20260828180240.md

SHA-512:
f77d0c6a376db6677935560f720304fe94cd809025457cfb1e9c00ec8cb51059e88df523348c48b39ab8ce229db5fd02f06b4b70cbdf90e1aca4329bfea5a240

Digest verification: MATCH
```

## 2. Resume Authority（P6-RR-R-INC-001 Disposition）

```text
Path:
docs/project/phases/phase_6/handoffs/
phase_6_post_claude_independent_review_git_read_incident_exact_resume_authority_ja_20260828183758.md

SHA-512:
08d516baf62eeeb3b4020405321c8881e1437eec8b56ae47e16d50d6cd5b59381dff9c5b1f04d0605261b04a67eb63aa4ecfd1decd135f5649637b6af8753996

Digest verification: MATCH

Disposition:
  P6-RR-R-INC-001:
    RECORDED / STOPPED_SAFE / REVIEWED_BY_CONTROLLER /
    PROCESS_NONCONFORMANCE / TECHNICALLY_NON_BLOCKING /
    EXACT_DIFFERENTIAL_RESUME_AUTHORIZED
```

Incident Evidence本体：

```text
docs/project/phases/phase_6/history/operations/
phase_6_post_claude_independent_review_p6_rr_r_inc_001_unauthorized_git_read_incident_ja_20260828183940.md
```

## 3. User観測Signal（推測更新しない）

```text
Context Compaction        : User報告「96% Compaction実施済み」をそのまま保持
Five-hour Remaining Signal : 直前User報告「39%」をそのまま保持、Current値へ自己推測更新しない
```

## 4. Preserved Baseline（再実装禁止）

```text
Phase 6 Package 0〜I                                    : REDO PROHIBITED
Claude Package K〜QのうちP6-GOV-019で棄却されていない成果  : REDO PROHIBITED
Main Provider DropdownのRuntime Model Switch Transaction  : PRESERVED
Production Role Adapter FactoryとAuthority Gateの骨格      : PRESERVED
Built-in Deterministic Model Call 0経路                    : PRESERVED
Qwen3Guard Additive Detectorの骨格                         : PRESERVED
Bounded UI Delta（User Manual確認済み配置・非表示化）        : PRESERVED
Claude Canonical Backend／Frontend／Static Regression Evidence: PRESERVED（Q時点 1674 passed / 227 passed 等）
Historical Incident・PARTIAL・NOT RUN・FAILおよびUser Gate   : PRESERVED（Literal 0昇格禁止）
```

## 5. Open Finding Ledger（P6-GOV-019由来、R0で登録・R1以降で解消対象）

```text
P6-CODEX-062 : Provider Selection／Mode／Lifecycleが非Atomic（Major、Judge/Guard、対象R1）
P6-CODEX-063 : Selected Provider実行RouterとExecuted Identityが未接続（Major、対象R2）
P6-CODEX-064 : Semantic 109件のLive評価／Projectionが未完了（Major、対象R3）
P6-CODEX-065 : Provider別Budget／Frozen Repair Rejudgeが未接続（Major、対象R4）
P6-CODEX-066 : Safe Fallbackの言語／理由契約が未達（Major、対象R5）
P6-CODEX-067 : Live Observability／Recording相関が未完了（Major、対象R6）
P6-CODEX-068 : Acceptance／Closure Claim分類の過剰（Major、対象R0/R8、本Index・今後のReturn Handoffで是正）
```

いずれもDisposition=open。R1〜R8の各Packageで対応し、Package Final Recovery Indexで都度Dispositionを更新する。

## 6. Source Anchors（P6-GOV-019由来、R0時点で再確認）

本Task内でのSource Read（Mandatory Reading 13〜26）により、次を直接確認済み。

```text
src/margpa_runtime_llm/web/provider_selection_routes.py
  apply_provider_selection(): typed_role is ModelRole.MAINのみ_apply_main_provider_selection()へ
  分岐、それ以外のRole（Judge/Guard）はcontroller.select()のみを呼び、Mode／Lifecycleと
  同一Transactionにしていない（P6-CODEX-062の直接確認）。

src/margpa_runtime_llm/bootstrap/judge_live_integration.py:582
  _record_semantic_result()内、provider_id=snapshot.active_provider or
  snapshot.configured_providerが依然として現存（P6-CODEX-063の一部）。

src/margpa_runtime_llm/bootstrap/judge_live_integration.py:780
  _run_judge_and_repair()の非Built-in経路はservice.generate(context.model_key)を呼ぶのみで、
  Selene Dedicated Judgeへの明示Dispatch経路が存在しない（P6-CODEX-063確認）。

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:374-377
  SEMANTIC_ENFORCEMENT_SAFE_FALLBACKが英語固定定数（P6-CODEX-066確認）。

frontend/src/components/FeatureModesPanel.tsx
  useEffect([visible])でPanel表示時／Mode変更時／Manual Refreshのみfetch、Bounded Poll／SSE等の
  自動更新機構が存在しない（P6-CODEX-067確認）。
```

## 7. Changed File Inventory（0時点）

```text
Source／Test／Config／Frontend Mutation: 0件（本Index作成時点、本Task内で一切未実施）
```

## 8. Task-owned Temporary

```text
Directory:
.venv/.t/phase_6_post_claude_independent_review_rework_20260828183206/
  pytest/, ruffcache/, mypycache/, npm-cache/, tmp/, verification_runtime_data/, server_logs/

Active Process: 0
Loaded Model  : 0
```

## 9. Action Inventory（本Index時点、累積）

```text
Git Read Action   : 1（P6-RR-R-INC-001として記録済み、RECORDED/NON-BLOCKING/EXACT_DIFFERENTIAL_RESUME_AUTHORIZED）
Git Mutation      : 0
Network Action     : 0
Provider Memory    : 0
User runtime_data  : 0
Root外Persistent Write: 0 known
```

## 10. Last Completed Work Unit

```text
None in R0（本Package未着手）
```

## 11. Exact Next Action

```text
Next Exact Work Unit: P6-RR-R0-WU-001（Mandatory Reading／Digest照合の最終確認とPackage R0残りWork Unit）
```

R0-WU-001（Digest照合）自体は本Task冒頭のReceipt段階およびGit Incident Disposition受領時点で実質的に完了しているため、本Indexでその成立を確認記録し、直ちにR0-WU-002（Claude Candidateの成立済み成果と棄却Claimの分離）以降へ進む。
