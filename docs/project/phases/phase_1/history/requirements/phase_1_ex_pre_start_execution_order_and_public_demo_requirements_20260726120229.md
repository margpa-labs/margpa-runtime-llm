# Phase 1-ex 開始順序／Public Demo／Git準備 要件予約

- 文書ID: `phase_1_ex_pre_start_execution_order_and_public_demo_requirements`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-26 12:02:29 JST`
- 更新日時: `2026-07-26 12:02:29 JST`
- Snapshot: `20260726120229`
- 作成担当: 設計者役担当Task
- 親要件: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- 統合記録: [phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](../operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)
- 正本言語: 日本語
- supersedes: `phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md`

## 1. Current Decision

Phase 1はComplete／Acceptedであり、Phase 1確定Backup後にPhase 1-exを開始する。

Phase 1-exの主要対象：

- Lightning Auto-start実現可能性の早期判定
- Git運用設計および公開準備
- `docs/` Directory構造再編
- 担当Taskへの新構造通知
- 既存DocsのLossless再整理
- Canonical／公開Docs作成
- Mac限定簡易RAG
- 初回GitHub公開

## 2. READMEのPublic Demo表記

公開Repositoryへ個人情報、個人連絡先または個人Profileへの導線を掲載しない。

したがって、READMEへ次の趣旨を記載しない。

```text
デモの閲覧を希望する場合は連絡してください。
連絡後にCredentialを案内します。
```

Current Phase 1 PreviewはBasic認証付きの少人数検証用である。

公開READMEでは次の趣旨だけを使用する。

> 将来、Public Demo方式も検討しています。

Public URLをREADMEへ掲載するかは、Traffic-aware Auto-start、Access Control、Cost Guardおよび公開時の稼働状態を確認してから決定する。

## 3. Basic認証

Current Lightning PreviewではBasic認証を維持する。

```text
Current Mode : preview_shared
Authentication: Basic
Account System: Not Implemented
```

Basic認証は、将来AWS上で導入する本格Account／Quota／Permission機能とは別物である。

`public_demo`のためのRate Limit、Token Budget、Cost Guard、Bot対策等はキリなくScopeが広がるため、Phase 1-ex必須機能にしない。

## 4. Lightning Auto-start Early Preflight

Phase 1-exの機能変更前半で、まずRead-only Preflightを行う。

確認対象：

- Current Lightning PlanでTraffic-aware Auto-startを利用できるか
- FastAPI＋Custom Port Viewerへ適用できるか
- Public URLからSleep中StudioをWakeできるか
- CPU MachineをDefaultに維持できるか
- Basic認証を維持できるか
- Public URLがSleep／Wake後に維持されるか
- Cold Start中の表示または待機動作
- Credit／無料枠への影響

Decision Rule：

```text
Simple Path:
  Native Auto-start／小規模Launcherで成立
  → Phase 1-ex前半で実装

Complex Path:
  Deployment移行、大規模Adapter、Plan変更または課金前提
  → Current Phase 1-exから延期可能
```

短時間のRead-only Preflightによって難易度を判定し、Platform制約が判明した後も無制限に実装Scopeを拡張しない。

## 5. Git準備の前倒し

Git運用設計および公開準備を、既存DocsのLossless再整理より前へ移動する。

前倒し対象：

- Branch Strategy
- Commit Message
- Phase Tag／Release
- Backup／Manifest／Commit対応
- Author Name／Commit Email
- Remote／Public Repository
- `.gitignore`
- `.gitattributes`
- Model／Binary／Secret／Cache除外
- Privacy Scan
- License／Terms／Notice方針
- Initial Commit Allowlist

## 6. Initial Commit Boundary

Git準備を先に行っても、次が完了するまで初回公開Commitを作成しない。

- `docs/` Directory再編
- 担当Taskへの新構造通知
- Lossless Phase Compilation
- Canonical Docs作成
- README／LICENSE等の公開文書
- Public Identity Scan
- Personal Information Scan
- Secret Scan
- Model／`.venv`／Cache除外
- Link Validation
- Test／Review

既存の細分化Docsまたは移行前Artifactを一度Commitし、後から削除する方式は採用しない。削除後もGit Historyへ残るためである。

`git init`自体を早期に行うか、初回Commit直前に行うかはGit運用設計で決める。いずれの場合も、初回Public Historyへ含める内容はSanitized Allowlistから決定する。

## 7. docs再編

Git準備後に次を実行する。

1. Current File Inventory
2. Target Directory Tree
3. Current／Historical／Superseded／Conflicting分類
4. Move／Keep／Compile／Exclude Manifest
5. Relative Link更新計画
6. Ownership／Write Authority再定義
7. Rollback Plan
8. Directory Migration
9. 全担当Taskへの通知
10. Lossless Compilation

既存文書を勝手に要約、意味変更または再解釈しない。

## 8. Canonical／Public Docs

少なくとも次を整備する。

```text
README.md
LICENSE
NOTICE.md
CITATION.cff
docs/overview_ja.md
docs/concept_ja.md
docs/roadmap_ja.md
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
docs/project_continuity_master_ja.md
```

実際の配置先はTarget Directory Tree確定時に決める。

## 9. Mac限定簡易RAG

Docs構造とCanonical Setが確定した後に実装する。

- Mac実機ではDocumentation Explainerとして利用する。
- Lightning初期公開ではHookのみを許容する。
- `docs/`がない場合は明示的Unavailable Resultを返す。
- RAG対象のPublic／Private分類を行う。
- Modelへ渡したDocument／Chunk／Hashを将来Audit可能にする。

Docs再編前にIndexを作り、移行後に作り直すことを避ける。

## 10. Final Phase 1-ex Order

```text
1. Phase 1確定Backup
2. Lightning Auto-start Read-only Preflight
3. Git運用設計
4. Git公開準備
5. docs/構造再設計
6. 全担当Taskへ通知
7. 既存Docs Lossless再整理
8. Canonical／公開Docs作成
9. Mac限定簡易RAG
10. Review／Test／Privacy Scan
11. Initial Commit／Tag／Phase 1-ex Backup
12. GitHub公開
```

## 11. Authorization Boundary

本要件予約はPhase 1-exの順序と境界を確定するが、次を自動許可しない。

- Lightning設定変更
- Auto-start有効化
- Git初期化
- Commit／Tag／Remote／Push
- Docs Move／Rename／Delete
- Source／Config変更
- RAG実装
- GitHub公開

Phase 1確定Backup完了後、ユーザーのPhase 1-ex開始指示に従う。
