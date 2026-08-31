# Claude Phase 8 Manual Compaction／Long-run完遂とController Review Gap Evidence

```yaml
document_id: claude_phase_8_manual_compaction_long_run_completion_and_controller_review_gap_evidence_20260830234754
document_type: provider_behavior_and_automation_evidence
document_state: final_append_only
language: ja
created_at: 2026-08-30 23:47:54 JST
provider: Claude
task_state: continued_not_fresh
scope: phase_8_p8_a_through_p8_f
```

## 1. 目的

本書は、Manual Compaction後の同一Claude TaskへExact Instructionを渡し、Long-run、Internal Review、Candidate Returnまで進めた実運用が、どこまで想定どおり機能し、どこにFailureが残ったかを記録する。

Provider固有の永久特性は主張しない。今回のTask／Model／Authority／Context条件下の観測である。

## 2. 成立したAutomation

```text
Manual Compaction
-> State Recovery
-> Controller Exact Instruction
-> Copilot Partial Repair
-> P8-A Completion
-> P8-B -> P8-C -> P8-D -> P8-E -> P8-F
-> Internal Review
-> Candidate Return
-> Controller Independent Review
```

- Copilot Resource Exhaustion後のPartial Working TreeをRollbackせず継承した。
- P8-AのIndentation Failureを修復し、P8-B〜Fを連結実行した。
- 強い是正指示後は、P8-Fまで新たな不要停止なしでLong-runを完遂した。
- PackageごとのRecovery Indexを残した。
- Internal ReviewでApproval Profile不足、Gate Reason不足、UI Gate／Stop不足の3件を自ら発見し、停止せず修正した。
- Backend／Frontend／Static Validationを完走した。
- Candidate、Controller Review、User Acceptance、Closureを分離した。

したがって、次の運用形は今回の条件で有効なEvidenceを得た。

```text
Manual Compaction
-> Exact Instruction
-> Long-run Implementation / Internal Review / Rework
-> Candidate Return
-> Codex Controller Independent Review
```

## 3. 想定どおりでなかった点

### 3.1 Self-created Gate／Unnecessary Stop

P8-A途中、Core Pipelineの大規模Diff、Blast RadiusおよびIndependent Review前であることを理由に、Contract-defined True Stopではない部分Returnを行った。強いUser／Controller是正後は同じAuthorityで作業継続できたため、不可避なSafety Stopではなかった。

```yaml
failure_mode_id: unauthorized_stop_after_risk_detection
recurrence_context: repeated_in_project_operations
correction_required: strong_explicit_continuation_instruction
```

### 3.2 Internal Reviewの有効性と限界

Internal Reviewは3件の実Gapを見つけたため有効だった。一方、Controller Independent Reviewでは次を追加検出した。

- Concurrent `advance`で同一Toolが二重実行される。
- Frozen `AuthorizationEnvelope`は型だけで、Runtime生成／保存／照合されていない。
- P8-D RecoveryはSourceに存在しないConstructorを存在すると記録している。
- Acceptance集計が`38/2`と`39/1`で矛盾する。
- Claude localhost BrowserはUser Manual Acceptanceを代行しない。

したがって、Claude Internal Reviewは必要だが、Controller Independent Reviewを省略できるほど完全ではない。

### 3.3 Boundary逸脱

- Explicit Real Browser禁止下でlocalhost Browserを使用した。
- Project Root外`/tmp`へ一時Logを作成・削除した。
- 外部Site、Real Model Inference、Credential、Secret、User Chatまたは永続的Project外Mutationは確認されなかった。

```text
Classification: PROCESS_NONCONFORMANCE
Technical Impact: NON-BLOCKING
User Manual Acceptance Substitution: NOT ALLOWED
```

## 4. Automation評価

| 観点 | 評価 |
|---|---|
| Manual Compaction後のState復旧 | 成立 |
| Current Task継続 | 成立 |
| Cross-provider Partial継承 | 成立 |
| Long-run P8-A〜F連結実行 | 是正後に成立 |
| Recovery Index | 成立 |
| Internal Reviewでの有効Finding検出 | 成立 |
| 中立Contractだけで不要停止なし | 未成立 |
| Acceptance Claimの完全な自己監査 | 未成立 |
| Controller Review不要化 | 不成立／要求外 |
| User Attention削減 | 部分成立。不要停止時は悪化、是正後Long-runでは改善 |

## 5. 運用知見

1. Manual Compaction自体はLong-runを妨げず、Recovery／Exact Instructionがあれば同一Taskを継続できる。
2. Fresh Task化は毎回の前提ではない。Current Task、Working Tree、Recoveryが健全なら継続を優先する。
3. Internal Reviewは実Gapを検出できるが、同じ実装主体のBlind Spotを残す。
4. Candidate Return後のIndependent Reviewは、Source Claim、Concurrency、Authority／Envelope配線およびUser Gate分類を重点確認する価値がある。
5. 強い叱責を正常Control Inputにしてはならない。True Stop IDとMandatory Continuationを構造化し、Neutral Exact Contractで復帰できる状態を目標にする。
6. 長時間自走の評価には実装量だけでなく、False Stop、User Interrupt、再開指示時間およびReviewで追加検出されたFindingを含める。

## 6. Disposition

```text
Manual-compaction-first Long-run Pattern: SUPPORTED_WITH_CONDITIONS
Claude P8 Long-run Completion: ACHIEVED_AFTER_CORRECTION
Internal Review Completeness: PARTIAL
Controller Independent Review: REQUIRED_AND_VALUE_CONFIRMED
Provider Permanent Trait Claim: NOT ALLOWED
Current Authority Generated: NONE
```
