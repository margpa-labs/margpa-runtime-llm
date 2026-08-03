# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 11:16:32 JST`
- 更新日時: `2026-07-26 11:16:32 JST`
- Snapshot: `20260726111632`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726094241.md`

## 1. Current Position

```text
Phase 1-A～1-I                              : Complete／Accepted
Mac Web Manual Acceptance                  : Passed
Phase 1-F Lightning External Pure CPU      : Accepted
Mac Full Repository Suite                  : Green
Lightning Full Repository Suite            : Green
Lightning External Web Acceptance          : Passed
Top-level Phase 1                          : Complete／Accepted
Phase 1 Backup Trigger                     : Ready／Not Executed
Phase 1-ex                                 : Next／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726094241.md](documentation_index_20260726094241.md)を継承する。

ユーザーがLightning Public Linkを、Lightning Accountと無関係なBrowserおよびSafariから確認した。Basic認証、Generation、Stop、New Chat、Language、Summary、Thinking、Copy、Model Busy、Browser Reload、Token打切りおよびServer停止を含むManual Acceptanceが合格した。

## 3. Phase 1 Final Review

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

```text
Blocking Finding            : None
Lightning Web Acceptance    : Passed
Top-level Phase 1           : Complete／Accepted
Next Phase                  : Phase 1-ex
```

## 4. Current User Manual

[phase_1_web_and_lightning_user_manual_20260726111632.md](user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)

Lightning環境をゼロから再構築する場合：

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 5. Accepted Runtime Evidence

```text
Mac Full Suite             : 267 passed／3 deselected
Lightning Targeted Test    : 41 passed
Lightning Full Suite       : 266 passed／1 skipped／3 deselected
Lightning Native Acceptance: all_required_checks_passed=true
Mac Web                    : PASS
Lightning External Web     : PASS
```

## 6. Accepted Deferred Items

- Lightning Pure CPUの生成Latency
- iPhone／iOS／Mobile Responsive UI
- Streaming中のRaw Markdown
- Markdown Table
- Code Block個別Copy
- Model Busy表示の重複

これらは理解済みの非Blocking項目である。

## 7. Phase 1-ex Reservation

### 7.1 Complete Operating Model

[phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)

### 7.2 Lightning Auto-start／Cost Control

[phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md](requirements/phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md)

Auto-startはPhase 1 CompletionをBlockしないOperations Follow-upである。

## 8. Backup Gate

Phase完了Policyの両Gateが成立したため、Phase 1 Backup TriggerはReadyである。

```text
Gate A: Designer Phase完了／次Phase着手可能宣言 : PASS
Gate B: User Manual Acceptance合格宣言           : PASS
```

Backupは未実行である。初回GitHub公開はPhase 1-ex完了後まで延期する。

## 9. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 10. Authorization Boundary

本Indexは次を自動許可しない。

- Backup生成
- Git初期化、Commit、Tag、Remote、Push
- GitHub公開
- Phase 1-exの実変更
- Lightning Auto-start設定
- Secret登録
- Machine Type変更

## 11. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。
