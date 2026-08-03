# 実装担当向け Phase 1-ex Lightning Auto-start Go／No-Go Assessment Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment
phase: phase_1_ex
status: accepted_ready_for_assessment
language: ja
created_at: 2026-07-27 00:30:44 JST
owner: 設計統括者役
target_role: 実装者役
supersedes: null
depends_on:
  - implementer_handoff_phase_1_ex_lightning_auto_start_read_only_preflight_20260726192912.md
  - designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md
```

## 1. Objective

Lightning AI StudioでTraffic-aware Auto-startをPhase 1-ex前半に採用できるかを、既存Evidence、Repository内Read-only Preflightおよびユーザーが実施するPlatform Manual Checkから判定可能な状態へ整理する。

本Handoffの目的は、Auto-start機能を直ちに実装・有効化することではない。

次のいずれかをEvidence付きで提案することが目的である。

```text
GO
CONDITIONAL_GO
DEFER
NO_GO
```

最終決定権はユーザーと設計統括者役にあり、実装者役が単独でPlatform設定、公開状態または運用を変更しない。

## 2. Authoritative References

- [ADR-0025](../../adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [Public Demo／Auto-start要件](../../requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](../../architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Auto-start Read-only Preflight Handoff](implementer_handoff_phase_1_ex_lightning_auto_start_read_only_preflight_20260726192912.md)
- [Auto-start／Lifecycle Repository Review](designer_review_phase_1_ex_lightning_auto_start_and_lifecycle_scripts_20260726202036.md)
- [Lightning Manual Environment／Preflight Evidence](../operations/lightning_manual_environment_and_preflight_evidence_20260726233910.md)
- [Lightning Environment Recovery／Lifecycle Acceptance Evidence](../operations/lightning_basic_preview_environment_recovery_and_lifecycle_acceptance_evidence_20260727003044.md)
- [Lightning Basic Preview Manual Lifecycle Accepted Review](designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
- [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Phase 1-ex Index](../../phase_index_ja.md)

Conflict時は日本語正本、ADR、Requirements、Architecture、本Handoffの順に確認し、独断で要件または運用を変更しない。

## 3. Current Established State

次は合格済みであり、再実装対象ではない。

```text
Project-side Read-only Preflight:
  ACCEPTED_REPOSITORY_ONLY

Lightning Linux Lifecycle Unit Test:
  PASS／30

Lightning Basic Preview Preflight:
  PASS

Start／Status／Health／External Basic Authentication／Generation／Restart／Stop:
  ACCEPTED

Anonymous Public Demo:
  DISABLED

Git:
  NOT_INITIALIZED／OPERATION_NOT_AUTHORIZED
```

通常運用では`MARGPA_RUNTIME_STATE_ROOT`を明示設定しない。

## 4. Authorized Scope

### 4.1 Repository Read-only Assessment

既存の次を再確認する。

```text
scripts/runtime/lightning/auto_start_preflight.sh
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
```

確認内容：

- 現行ScriptがTraffic-aware Auto-startそのものを提供していると誤認させない。
- Project側起動Command、Environment、Health ContractおよびSecret境界がPlatform Hookから呼べる。
- Auto-start Hook候補がBasic Preview Lifecycleの単一入口を再利用できる。
- CredentialをArgument、File、Log、StatusまたはDocsへ出さない。
- Startup再実行が二重Processを作らない。
- Studio起動後のHookと、Public URL AccessによるTraffic-aware Wake-upを区別する。
- Public DemoとBasic Previewを混同しない。

### 4.2 Platform Manual Evidence Preparation

Repositoryだけで判定できない項目について、ユーザーがLightning UIまたはRead-only確認で実施できる、短く再現可能なChecklistとEvidence記録様式を用意する。

必須項目：

1. Account／Organization上でAPI Builder、Public Appまたは同等のTraffic-aware起動機能を利用できるか。
2. 現在のStudio、MachineおよびCredit条件で利用できるか。
3. 固定または再利用可能なPublic URLを発行できるか。
4. StudioがSleep中でもPublic URL Accessを契機にWake-upできるか。
5. Wake-up後にRepository Lifecycle ScriptをStartup Commandとして実行できるか。
6. Model LoadとSHA-512検証を経て`/healthz`が`200`になるか。
7. Cold Start時間がPreview用途として許容できるか。
8. Idle Sleep後に再度Wake-upできるか。
9. Restart／Sleep／Wake後もPublic URLが維持されるか。
10. Log、UI、Error、StatusまたはPublic ResponseへSecret、Credential、内部Pathが露出しないか。
11. CPU Machineでも運用可能か、GPUを要求してCreditを過剰消費しないか。
12. ユーザーがStudioへ張り付き続けなくても閲覧者が起動できるか。

未確認項目をPassにしない。

### 4.3 Minimal Repository Follow-up

AssessmentのためにRepository変更が必要な場合は、次に限定する。

- Read-only Preflightの表示またはEvidence Template
- Platform Manual Checklist
- `--help`または`--plan`
- Side Effectを持たないTest Fixture
- 実装者Status

Production Auto-start Hook、Public App AdapterまたはPlatform変更が必要と判明した場合は実装せず、必要工数、変更File、Riskおよび追加許可事項をStatusへ記載する。

## 5. Decision Criteria

### 5.1 GO

次をすべて満たす場合の候補：

- Traffic-aware Wake-up機能が現Account／Studioで利用可能。
- Public URL AccessでSleeping Studioが自動起動する。
- Startup CommandがBasic Preview Lifecycleを安全に起動する。
- `/healthz`が許容時間内に正常化する。
- URLが再利用可能。
- Credentialと内部情報が露出しない。
- Machine／Credit条件がPreview運用として許容可能。
- 大規模なBackend変更や別Framework追加を必要としない。

### 5.2 CONDITIONAL_GO

機能自体は成立するが、次のような条件付き運用が必要な場合：

- Cold Startが長い。
- URL維持に制約がある。
- 特定MachineまたはCredit条件が必要。
- User操作による初回設定が必要。
- Basic Preview用途に限れば許容できる既知制限がある。

条件、回避策、費用、手動操作および再評価条件を明記する。

### 5.3 DEFER

次の場合：

- 現AccountまたはFree Tierでは機能確認できない。
- Credit不足、Platform制約またはUI不明により判断不能。
- 追加工事がPhase 1-exの利益に対して大きい。
- Basic Previewを手動起動すれば当面の目的を満たせる。
- Lightning側仕様の確定待ちが必要。

延期理由と再開条件を明記する。

### 5.4 NO_GO

次の場合：

- Public URL AccessでSleeping Studioを起動できない。
- Startup Commandから安全にServiceを起動できない。
- Secretまたは内部情報露出を避けられない。
- URL、Machine、CreditまたはLifecycleがPreview用途として成立しない。
- Basic Previewを破壊する変更が必要。
- 大規模な別Adapter／Framework／Deployment再構築が必要。

## 6. Write Authority

実装者役が本Handoffで書き込める場所：

```text
scripts/                                              # 必要最小限
tests/                                                # 必要最小限
docs/project/phases/phase_1_ex/history/handoffs/
```

次はRead-only：

```text
docs/project/phases/phase_1_ex/adr/
docs/project/phases/phase_1_ex/architecture/
docs/project/phases/phase_1_ex/requirements/
docs/project/shared/
docs/project/current/
docs/public/
config/
pyproject.toml
uv.lock
```

`config/`、DependencyまたはProduction Source変更が必要な場合は、追加許可前に変更しない。

## 7. Explicitly Prohibited

- Lightning Platform設定の無断変更
- API Builder／Public App／Port／Auto-startの有効化
- Public URLの新規公開または公開範囲変更
- Basic認証の削除
- Credential実値、Private URLまたはSecretの保存・出力
- 匿名Public Demoの有効化
- Rate Limit／Public Policy本体の先行実装
- RAG、Tool、Agent、GuardrailまたはJudgeの追加
- Package Install、Native BuildまたはModel Download
- Git初期化、Commit、Push、GitHub操作
- 既存Docsの上書きまたは削除
- Go／No-Goの最終確定

Platform上でMutationが必要な確認は`manual_required`としてユーザーへ戻す。

## 8. Deliverables

最低成果物：

```text
1. Current Evidence Matrix
2. Platform Manual Checklist
3. 未確認項目
4. 工数・変更範囲・Risk
5. GO／CONDITIONAL_GO／DEFER／NO_GOの推奨
6. 推奨根拠
7. 次のUser Manual Action
8. 実装者Status
```

実装者Status：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment_YYYYMMDDHHMMSS.md
```

Statusは判定根拠を記録するが、最終決定を勝手に確定しない。

## 9. Acceptance Conditions

1. Repository自動確認とPlatform手動確認を分離している。
2. 未実行項目をPassにしていない。
3. Traffic-aware Wake-upとStudio起動後Hookを区別している。
4. Basic Previewと匿名Public Demoを分離している。
5. Secret、Credential、Private URLおよび個人情報を記録していない。
6. 提案判定に具体的Evidenceと未確定事項が付いている。
7. 追加実装が必要なら工数、変更File、Riskおよび許可事項を示している。
8. 既存Lifecycle Acceptanceを破壊していない。
9. Git、RAG、Public DemoまたはPlatform Mutationを実施していない。
10. Append-onlyの実装者Statusを作成している。

## 10. Review Gate

実装者Status作成後、設計統括者役がScope、Evidence、未確認事項および判定根拠をReviewする。

設計統括者Review後、ユーザーが次のいずれかを明示決定する。

```text
GO
CONDITIONAL_GO
DEFER
NO_GO
```

ユーザー決定前にAuto-startを有効化または実装しない。

## 11. Start Condition

本Handoffは実装担当へ渡せる状態である。

実装者役はRead-only調査と必要最小限のRepository内Assessment補助に着手できる。外部変更またはScope拡張が必要になった時点で停止し、Statusまたは質問として戻す。
