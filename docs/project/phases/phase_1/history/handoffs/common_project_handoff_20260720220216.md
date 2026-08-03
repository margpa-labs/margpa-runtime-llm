# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-20 22:02:16 JST
supersedes: common_project_handoff_20260719202333.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
```

## 1. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning CUDA Native Verify  : Waiting External Execution
Lightning CPU Native Verify   : Waiting External Execution
Phase 1 User Acceptance        : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1 Publication            : Planned／Not Authorized
Privacy Scrub                  : Complete for managed files
```

本HandoffはPhase 1-F Reviewを代替せず、実装完了をAcceptしない。

## 2. Identity／Privacy

- 第一者の公開識別子は`Nazuna Research`だけを使用する。
- 法的氏名、Local Account名、個人固有Path、Hostname、連絡先、CredentialをDocs、Source、Log、Sampleへ記録しない。
- 第三者の正式なAttributionは保持する。
- Privacy／Security削除はDocs Append-Onlyより優先する。
- `.venv/`、Model、Symlink、Cache、Local Runtime Dataは公開物へ含めない。

正本は[公開識別子・個人情報取扱方針](../requirements/public_identity_and_personal_information_policy_20260720220216.md)とする。

## 3. Current Entry Points

- Current Index: [documentation_index_20260720220216.md](../documentation_index_20260720220216.md)
- Documentation Rules: [documentation_rules_20260720220216.md](../requirements/documentation_rules_20260720220216.md)
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](../requirements/public_identity_and_personal_information_policy_20260720220216.md)
- Scrub Report: [publication_privacy_scrub_report_20260720220216.md](../operations/publication_privacy_scrub_report_20260720220216.md)
- Phase 1-F Status: [implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md](implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md)

## 4. Platform／Python

```text
Project Support : CPython >=3.12,<3.14
Mac Primary     : CPython 3.13.14
Lightning       : CPython 3.12.11
```

Lightning CUDA／CPU ProfileはRepositoryに実装済みと報告されているが、Lightning Native Evidenceは未取得である。

## 5. Next Gate

1. 設計者がPhase 1-F Statusと関連実装をReviewする
2. Lightningへ一括Uploadする対象を確定する
3. Lightning CUDAをNative検証する
4. Lightning CPUをNative検証またはDispositionする
5. Phase 1 User ManualをCurrent機能へ更新する
6. ユーザー受入と設計者完了宣言の両方を成立させる
7. Backup／公開準備へ進む

Phase 1-Gの最小Web UI案は要件相談中であり、本Handoffでは実装許可済みと扱わない。

## 6. Authorization Boundary

本HandoffとPrivacy Scrubは、Lightning外部操作、Git初期化、GitHub作成／Push、公開、Phase 1-F Acceptance、Phase 1-G実装を許可しない。
