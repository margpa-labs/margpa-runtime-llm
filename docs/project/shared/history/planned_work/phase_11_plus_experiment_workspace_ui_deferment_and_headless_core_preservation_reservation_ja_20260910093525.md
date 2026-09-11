# Phase 11以降 Experiment Workspace UI延期／Headless Core維持予約

```yaml
document_id: phase_11_plus_experiment_workspace_ui_deferment_and_headless_core_preservation_reservation_20260910093525
document_type: planned_work_architecture_and_priority_reservation
document_state: accepted_user_direction_not_started
language: ja
recorded_at: 2026-09-10 09:35:25 JST
decision_authority: user
authority_owner: Nazuna Research
target_phase: phase_11_plus_or_later_user_selected_window
immediate_bounded_action: hide_current_normal_ui_entry_only
backend_core_disposition: preserve
current_minimal_ui_disposition: defer
implementation_authority: limited_to_separate_exact_handoff_only
git_authority: not_granted
append_only: true
history_snapshot_of: docs/project/shared/planned_work/phase_11_plus_experiment_workspace_ui_deferment_and_headless_core_preservation_reservation_ja_20260910093525.md
```

## 1. User Decision

Phase 9-2で作成した「実験 — Multi-Governance比較」の現行Minimal UIは、MVP成立の必須機能ではない。Phase 10のUI大改造、後続のMain Governance／Runtime Constitution構造制御レイヤー、Semantic Evaluation、追加されるComponent群を反映すると、実験UIを再設計する必要が高い。

そのため、現行Minimal UIを今すぐ完成品へ磨き上げず、Phase 11以降またはユーザーが優先度を上げた時点まで延期する。通常UIの右上入口は当面非表示にする。

ただし、Phase 9-2で作成したExperiment Backend Coreは削除、Rollbackまたは失敗扱いしない。これはPhase 9-3のContext Compaction／Recovery前後比較と、後続の構造レイヤー／Multi-Governance比較に再利用できる。

## 2. 方針変更の直接Input

User Mac実画面で次が観測された。

- 中止Buttonを発見できない。
- Plan作成後、閉じて開き直してもModeを切り替えられない。
- 詳細Evidenceを押しても無反応に見える。
- Component別詳細の表示が間欠的で、2回操作が必要に見える場合がある。
- 実験条件を新しく試すにはBrowser Reloadが必要になる。
- 現UIのためにMVP・Phase 10・Constitution・UI大改造を遅らせる合理性が低い。

実測の詳細は次に保存する。

- `docs/project/phases/phase_9/history/operations/phase_9_2_user_mac_original_manual_checklist_partial_result_and_strategy_change_input_ja_20260910093525.md`

## 3. Experiment機能の価値とMVP境界

Advanced SettingsでComponent／Modeを手動変更し、右Panelで各Turnの結果を見る方式は、日常的な探索・動作確認に使える。その意味で、現Experiment UIはMVPの必須操作面ではない。

一方、Experiment Backend Coreには次の独自の価値がある。

- 同一Case／PlanにおけるVariant比較。
- `experiment_id／run_id／request_id`の分離。
- Desired／Frozen Configuration、Provider／Artifact／Definition／Plan Digestの保存。
- Raw Evidence、ComparisonおよびRestart Read。
- Baseline／Regression／Ablationの単一要因差検証。
- Deadline／Cancel／Terminal Resultの一回Publish。
- 手作業で条件を変えて目視比較するだけでは得にくい、復元可能な実験Evidence。

したがって、「機能全体が不要」ではなく、「現時点の利用者向けMinimal UIは非必須」とDispositionする。

## 4. Phase 9-3以降で維持する部品

Phase 9-3 Execution Planの入口条件は、「P9-2のExperiment Run／Trace Identityが成立し、Compaction前後を比較可能である」としている。

少なくとも次を維持する。

| 部品 | 維持理由 |
|---|---|
| Experiment／Plan／Variant／Run／Request Identity | Compaction前後の同一条件比較 |
| Effective／Desired／Frozen Config Snapshot／Digest | 条件差と実行時状態の固定 |
| Provider／Artifact／Definition／Plan Identity | 実行者・定義・成果物の誤帰属防止 |
| Execution Trace／Call 0 Reason | Compaction後の未実行と失敗の分離 |
| Raw Evidence／Restart Read | 後から比較・復元・監査するため |
| Comparison／Evaluation／Single-factor Declaration | 保持率、誤復元、Latency／Token／Failure差の比較 |
| Async Worker／Deadline／Cancel／Terminal Publish | Headless Runの有界Lifecycle |

Phase 9-3では、現Experiment Modalを使わず、Service／API／Testからこれらを利用できる。

## 5. 直近の最小Rework

別途Exact Handoffの範囲で、次だけを実施する。

1. 通常UIの右上Experiment Buttonを非表示にする。
2. 通常UIからExperiment Panelを開けないことをFocused Frontend Testで確認する。
3. Experiment Core、API、Persistence、Production Adapter、Configuration Lease、Case／Comparison／EvidenceのSourceはRollback／削除しない。
4. 現UIのCancel／Reset／Details修復は今回行わず、本予約の後続対象とする。

今回は新しいCLI Flag／Backend Feature Gateまで必須化しない。現Backend APIはLoopback-onlyで、Experiment Runが実行されない間、Configuration Leaseは実行経路を保持しない。通常UIからの誤起動を止める最小変更を優先する。

## 6. 後続Experiment Workspaceの必須候補

将来、実験UIを再開するときは、現モーダルの局所修復だけで完了しない。次をExperiment Workspaceの候補要件とする。

- 実験機能の明示的なDefault OFF／Opt-in Gate。
- 通常Chat／Advanced Settings／Experiment実行の権限とStateの分離。
- Immutable Planと「新しいPlan」／「Planを破棄」の両立。
- 開始直後から発見できるCancel、受理済み表示、Cancel後のTerminal確認。
- Queued／Running／Completed／Failed／Cancelled／Timed-out／Recheckingの明確な表示。
- DetailsのLoading／Failure／Retryと、単一操作での安定表示。
- 複数Variantが順次実行であること、各Variantが必要とするLive Config、Model Load、Resource Costの事前表示。
- Fixture／Production／Real Model／Human Review／未観測の区別。
- Phase 10で追加するMain Governance Structural、Runtime Constitution Structural、Runtime Constitution Semanticの独立Variant。
- Right-side Observatoryとの重複責務を避けた画面境界。
- Resource Pressure Gate、順次Queue、実Model上限、実行前確認およびEvidence Retention。

## 7. 優先度と再開Trigger

```text
Priority           : Phase 10 MVP、PADG、Constitution／Governance構造レイヤー、主UI改造より低い
Current UI         : DEFERRED / HIDDEN FROM NORMAL UI
Backend Core       : PRESERVED / REUSABLE
Phase 9-3 Use      : HEADLESS ONLY
Reopen Trigger     : Userが明示的に優先度を上げる、または構造レイヤー群完成後の実験Workspace設計
```

## 8. Authority Boundary

本予約は、別途Exact Handoffが許可する通常UI入口の最小非表示以外に、次を許可しない。

- Experiment Backend Core／API／Store／Schemaの削除またはRollback。
- Cancel／Reset／Details／Comparison UIの修復。
- Phase 9-3の開始。
- Phase 9-2 Complete／Phase 9 Closureの自己承認。
- Phase 10またはPhase 11以降の設計・実装開始。
- Real Model／Browserの追加Trial。
- Git Add／Commit／Push／Stash／Clean。
- Project Root外へのRead／WriteまたはExternal操作。

