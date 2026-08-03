# 実装担当向け Phase 1-ex Lightning Auto-start Read-only Preflight Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_auto_start_read_only_preflight
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-26 19:29:12 JST
owner: 設計統括者役
target_role: 実装者役
supersedes: null
```

## 1. Objective

Lightning上でTraffic-aware Auto-startを採用できるかを、Platform設定や外部状態を無断変更せずに判定するためのRead-only Preflightを実装する。

本Subphaseの成果は、Auto-startの本実装ではない。Project側の起動前提を機械的に確認できる仕組み、Platform側でユーザーが確認する項目、および後続のGo／No-Go判断に必要なEvidenceを揃えることである。

## 2. Authoritative References

- [ADR-0025](../../adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [Public Demo／Auto-start要件](../../requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](../../architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
- [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Phase 1-ex Index](../../phase_index_ja.md)

Conflict時は日本語正本、ADR、Requirements、Architecture、本Handoffの順に確認し、独断で要件を変更しない。

## 3. Authorized Scope

実装対象は次に限定する。

### 3.1 Project-side Read-only Preflight

次を副作用なしで検査できるCommandまたはScriptを追加する。

- Linux x86_64／Lightning Studio候補環境であること
- Project Root、Model Root、Project `.venv`の解決
- Project-local `uv`のVersionとPath
- `margpa-web`の存在と実行可能性
- Lightning Pure CPU Deployment Profileの存在
- Model RegistryとGGUF Artifact Pathの整合
- Web Host／Port／Profile／Model Rootを明示できること
- `/healthz`の期待契約
- Basic Previewと将来Public Demoを混同しないこと
- Auto-start用CommandにCredentialや秘密値を埋め込まないこと
- 不明または不足時にFail Closedできること

既存の`preflight_lightning_ai_studio.sh`、Pure CPU Setup、Web起動方法を再利用してよい。重複Scriptを増やす場合は、その必要性をStatusへ記録する。

### 3.2 Platform-side Manual Checklist

自動判定できない次の項目は、機械的にPass扱いせず、ユーザー確認用Checklistとして出力または文書化する。

- API Builder／Public App／Traffic-aware Auto-startのAccount上の可用性
- 使用可能MachineとCredit条件
- Public URL発行可否
- Sleeping StudioへのAccessによるWake-up
- Startup Command実行
- Model LoadとArtifact Hash確認
- `/healthz`到達
- Cold Start時間
- Idle後のSleep復帰
- Restart後のURL維持
- Log、Credential、Secretおよび内部Pathの露出有無

判定値は最低限`pass／fail／not_run／manual_required／unknown`を区別する。未実行項目をPassにしない。

### 3.3 Tests

次を自動Testで確認する。

- HelpまたはPlan実行がEnvironmentを変更しない。
- Package Install、Build、Network Access、Server公開およびPlatform変更を行わない。
- Project Root／Model Root／`.venv`をHard-codeしない。
- 必須FileまたはCommand不足時に非0で安全に失敗する。
- ErrorへCredential、Secretまたは不要な個人識別Pathを出さない。
- Platform固有項目を自動で偽Passにしない。
- 既存Mac／Lightning Pure CPU Profileを破壊しない。

## 4. Write Authority

実装者役が本Handoffの範囲で書き込める場所：

```text
scripts/
tests/
src/                         # 必要最小限の場合だけ
docs/project/phases/phase_1_ex/history/handoffs/
```

`config/`、`pyproject.toml`または`uv.lock`の変更が必要になった場合は、その理由と最小差分を提示し、追加許可を得るまで変更しない。

Requirements、Architecture、ADR、Governance、Shared Policy、Current CanonicalおよびPublic DocsはRead-onlyとする。

## 5. Explicitly Out of Scope

本Handoffは次を許可しない。

- LightningのAuto-start、Public App、API Builder、Portまたは公開設定の変更
- 匿名Public Accessの有効化
- Public Demo本体、Rate Limit、BudgetまたはAccess Profileの実装
- Basic認証の削除または無効化
- Mac限定簡易Documentation RAGの実装
- Lightning／外部Server用RAG Adapterの実装
- Tool、Agent、Guardrail、Judgeまたは外部I/Oの追加
- Model、`.venv`またはProject一式のUpload
- Package Install、Dependency変更またはNative Build
- Git初期化、Commit、Push、GitHub操作
- Credential、Secret、Public URLまたは個人情報のDocs保存

Platform上の確認に設定変更が必要な場合は`manual_required`として停止し、ユーザー判断へ戻す。

## 6. Preferred Deliverables

既存構造を優先し、必要最小限で次を作る。

```text
Read-only Preflight Command／Script
Unit Tests
必要なTest Fixture
実装者Status
```

実装者Statusは次へ新Timestampで作成する。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_auto_start_read_only_preflight_YYYYMMDDHHMMSS.md
```

Statusには、変更File、実行Command、Test結果、未実行項目、Manual Checklist、既知制限、Go／No-Go判断に必要な残作業を記録する。

## 7. Acceptance Conditions

次をすべて満たした場合だけ実装完了候補とする。

1. Project-side Read-only Preflightが再実行可能である。
2. Preflight自体がFile、Dependency、Platform設定または外部状態を変更しない。
3. 自動確認とManual確認が明確に分離される。
4. 未確認事項をPassと報告しない。
5. Path、Version、ProfileおよびCommandが設定または引数から解決される。
6. Secret、Credential、Prompt、Private URLおよび個人情報を出力・保存しない。
7. Failure時に安全な非0終了と原因分類を返す。
8. 新規Testと関連既存Testが合格する。
9. MacおよびLightning Pure CPUの既存動作を壊していない。
10. 実装者Statusが新Docs構造へ作成される。

## 8. Review Gate

実装者Status作成後、設計統括者役がRepository、Test、EvidenceおよびScope逸脱をReviewする。

Review Accepted前に次へ進まない。

```text
Lightning Platform上の変更操作
Auto-start Go／No-Go確定
Public Demo基盤実装
匿名Public Access
RAG実装
Git操作
```

## 9. Start Condition

本Handoffは設計上Acceptedであり、実装担当へ渡せる状態である。

実装担当Taskは、本HandoffとAuthoritative ReferencesをRead-onlyで確認したうえで、Section 3およびSection 4の範囲内に限り着手できる。範囲拡張が必要な場合は実装せず、Statusまたは質問として設計統括者役へ戻す。
