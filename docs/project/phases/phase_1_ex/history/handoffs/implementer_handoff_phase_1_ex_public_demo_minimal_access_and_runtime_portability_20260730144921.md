# 実装担当向け Phase 1-ex Public Demo最小公開／Runtime交換性 Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_public_demo_minimal_access_and_runtime_portability
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-30 14:49:21 JST
owner: 設計統括者役
target_role: 実装者役
platform_operator: user
supersedes: null
```

## 1. Objective

既存Basic認証Previewを一切壊さず、認証なしPublic Demoを別Access Profile／別Repository Entry Pointとして実装する。

Public専用Rate Limit、Generation Budget、Cooldown、追加Token Hard CapおよびCost Guardは今回実装しない。ただし将来追加可能なConfig／Port Hookを`off`状態で用意する。

Public DemoではDocumentation RAGを強制無効とし、Basic Previewでは将来有効化できる境界を残す。

Model、Deployment、Home ServerおよびCloud交換性を維持し、Public Demoへ現在のModel／Lightning環境をHard-codeしない。

## 2. Authoritative References

- [ADR-0027](../../adr/adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md)
- [Public Demo最小公開／Runtime交換性 Requirements](../../requirements/public_demo_minimal_access_and_runtime_portability_requirements_ja.md)
- [Public Demo Access Profile／Runtime交換 Architecture](../../architecture/public_demo_access_profile_and_runtime_portability_architecture_ja.md)
- [Scope Reduction Decision Record](../operations/public_demo_scope_reduction_and_runtime_portability_decision_20260730144921.md)
- [ADR-0025](../../adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [Existing Public Demo Requirements](../../requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Existing Public Demo Architecture](../../architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Lightning Traffic-aware Auto-start Acceptance](../operations/lightning_stage_b_traffic_aware_auto_start_acceptance_20260727224609.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
- [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
- [Phase 1-ex Index](../../phase_index_ja.md)

Conflict時は、ユーザーの最新指示、ADR-0027、新Requirements、新Architecture、本Handoffの順で現在有効なScopeを解決する。旧文書は履歴と未変更要件の参照に使用する。

## 3. Established State

```text
Mac Local Runtime:
  VERIFIED

Lightning Pure CPU Runtime:
  VERIFIED

Lightning Basic Preview:
  ACCEPTED／KEEP

Traffic-aware Auto-start:
  GO／PASS

Public Demo:
  NOT IMPLEMENTED

Public Authentication:
  NONE／SEPARATE PROFILE

Public Rate／Budget／Cost Controls:
  OFF／HOOK ONLY

Public Documentation RAG:
  DENIED

Basic Preview Documentation RAG:
  FUTURE ELIGIBLE
```

## 4. Mandatory Architecture

最低限次を分離する。

```text
Web Access Profile
Deployment Profile
Model Definition
Feature Profile
Optional Control Policy
Platform Lifecycle Adapter
```

禁止されるShort-cut：

```text
MARGPA_WEB_AUTH_MODE=disabledだけでNon-loopback公開
basic_preview_service.shからCredential検査を削除
Public ModeをLightning Profile名で判定
Public ModeをQwen Model Keyで判定
Public RequestからRAGを有効化
Public Limitが未実装なのに有効と表示
```

## 5. Authorized Implementation Scope

実装者役は本Handoffに限り、次へ必要最小限の変更を行える。

```text
src/margpa_runtime_llm/web/
src/margpa_runtime_llm/bootstrap/
src/margpa_runtime_llm/entrypoints/web/
config/web_profiles/
scripts/runtime/lightning/
tests/unit/
tests/integration/web/
docs/project/phases/phase_1_ex/history/handoffs/
```

既存Fileの変更前に対象と目的をStatusへ記録できる状態にする。Project Root外を読取・走査・変更しない。

## 6. Required Deliverables

### 6.1 Web Exposure Contract

次と同等の明示的Contractを追加する。

```text
local
basic_preview
public_demo
```

要件：

- `local`はLoopback＋認証なし。
- `basic_preview`はNon-loopback＋Basic認証。
- `public_demo`はNon-loopback＋認証なし。
- Unknown Modeは拒否。
- Auth DisabledだけではPublicにならない。
- Basic Credential不足は拒否。
- Public DemoはBasic Credential値を参照・表示・記録しない。

既存`WebAuthMode`を拡張するか、新しいExposure Contractを追加するかは実装者が選べる。ただしAuthenticationとPublic Authorityを同一Booleanへ潰さない。

### 6.2 Web Profile Config

追加候補：

```text
config/web_profiles/basic_preview.toml
config/web_profiles/public_demo.toml
```

最低Field：

```text
schema_version
profile_key
access.mode
access.authentication
access.non_loopback_allowed
features.documentation_rag
controls.rate_limit.mode
controls.generation_budget.mode
controls.cooldown.mode
controls.cost_guard.mode
```

Public Controlは全て`off`。

Config Source、Validation、Effective StateをTest可能にする。Model Key、Model Path、OS、GPUまたはLightning固有PathをWeb Profileへ入れない。

### 6.3 Feature Policy

Public Demo：

```text
documentation_rag = denied／disabled
summary = existing behavior
thinking = existing behavior
language = existing behavior
copy = existing behavior
```

現在RAG Moduleが存在しない場合でも、将来Composition RootがPublic DemoでRAGを構築しないためのPolicy Contractまたは明確なHookを置く。

実装のためだけにRAG本体を新規作成しない。

### 6.4 Optional Control Hook

Public用Rate／Budget／Cooldown／Cost Guardは実処理を持たない`off` Hookでよい。

要件：

- `off`を明示できる。
- Effective StateをTestできる。
- Unknown Modeを拒否する。
- 制限が動作していると誤表示しない。
- Web Routeへ将来制限ロジックの条件分岐を散在させない。
- Persistence、Counter、External StoreまたはTimerを追加しない。

### 6.5 Public Demo Repository Entry Point

Basic Previewとは別に、Public Demo用Foreground Entry Pointを用意する。

候補：

```text
scripts/runtime/lightning/public_demo_service.sh
```

最低Subcommand：

```text
preflight
run
--help
```

`run`はForegroundで`exec margpa-web`またはAccepted Web Entrypointへ委譲する。Background PID、Log、Lockまたは別Model Loaderを複製しない。

Basic Preview ScriptをPublic向けに書き換えない。

Public用Platform Bootstrap、API Builder、Port、URLおよび起動設定はユーザー担当である。RepositoryへCredential、Public URLまたはPrivate Bootstrap原文を保存しない。

### 6.6 Model／Deployment Override

Public Entry Pointは次を既存Config Layerへ渡せる。

```text
Deployment Profile
Model Root
Model Definition／Registry
Model Key
Context Size
Host
Port
Web Access Profile
```

現在のQwen3-4B、GGUF Filename、Lightning Pure CPU ProfileまたはPort `7860`をCoreへ固定しない。

Defaultを置く場合も、Config／Environment／CLIの既存優先順位とProvenanceを維持する。

## 7. Existing Feature Preservation

Public Demoで次を利用可能とする。

- Text Chat
- Streaming
- Stop
- New Chat
- Copy
- UI Language
- Response Language
- Thinking Generation
- Thinking Presentation
- Summary Mode
- Max New Tokens

Basic Previewの既存動作も同時に維持する。

UIへPublic Mode表示を追加する場合、最小限の中立表示にする。未実装のRate Limit、RAG、Guardrailまたは安全保証を有効と表示しない。

## 8. Required Tests

### 8.1 Access Matrix

| Profile | Bind | Credential | Expected |
|---|---|---|---|
| local | loopback | none | pass |
| local | non-loopback | none | fail |
| basic_preview | non-loopback | valid | pass |
| basic_preview | non-loopback | missing | fail |
| public_demo | non-loopback | none | pass |
| unknown | any | any | fail |

### 8.2 Web

- Basic RootはCredentialなしで`401`。
- Basic Rootは正しいCredentialで`200`。
- Public RootはCredentialなしで`200`。
- Public Chat Streamが動作する。
- Public Stop／New Chatが動作する。
- Public Summary／Thinking／Languageが既存Contractどおり動作する。
- Public ErrorへCredential、Secret、Stack Traceまたは不要な内部Pathを出さない。
- Security Headerを維持する。

### 8.3 RAG／Control

- Public `documentation_rag`は常に無効。
- Public RequestからRAGを有効化できない。
- Public起動時にRAG Adapterを構築しない。
- Basic RAG Capability Hookは存在するが、RAG未実装時は安全にUnavailableとなる。
- Public Controlsは`off`。
- Unknown Control Modeを拒否する。

### 8.4 Portability

- Web Profileを変えずModel Keyを差し替えられる。
- Web Profileを変えずDeployment Profileを差し替えられる。
- Model／Deployment名からAccess Modeを推測しない。
- Mac Local Testを壊さない。
- Lightning Basic Preview Lifecycle Testを壊さない。

### 8.5 Regression

最低限：

```text
Targeted Unit Tests
Web Integration Tests
Lightning Lifecycle Unit Tests
Full pytest
Ruff
Mypy
```

Model SmokeはModel実体が必要なため、実装者Statusで実施可否を分けて報告する。

## 9. Platform User Actions

実装と設計Review完了後、ユーザーがLightning上で行う。

- Repository File差替え
- Permission
- Environment
- Public Demo用API Builder／Entry設定
- Port
- URL
- Sleep／Wake
- Anonymous Browser Test
- Basic Preview Regression

実装者役はLightningへ接続・変更しない。

## 10. Stop Conditions

次の場合は実装を拡張せず、Statusへ記録して停止する。

- Basic Previewの削除または大規模Rewriteが必要。
- Authentication NoneとPublic Authorityを安全に分離できない。
- Public RAG無効をServer側で保証できない。
- Current Config Layerを破壊しないとWeb Profileを追加できない。
- Dependency追加が必要。
- Model Adapter Contract変更が必要。
- Project Root外操作が必要。
- Lightning設定変更が必要。
- Public専用制限を実装しなければ成立しない。
- Scope外のGuardrail／Judge／Agent／Toolが必要。

## 11. Explicitly Prohibited

- `basic_preview_service.sh`から認証を削除
- Basic Preview Credential Contractの弱化
- Public DemoでRAG有効
- Public DemoでTool／Agent／External I/O追加
- Public専用Rate／Budget／Cost制限の先行実装
- Public URLまたはCredentialのRepository保存
- Private BootstrapのRepository保存
- Model Download／変換／Rename
- Dependency追加／更新
- Native Backend Build
- Lightning UI／API Builder／Managed Secrets変更
- Home Server／Cloud操作
- Git Commit／Push／GitHub変更
- Project Root外の読取・走査・作成・変更
- 既存Docs、History、StatusまたはEvidenceの削除・上書き

## 12. Deliverables

実装担当は次を提出する。

1. 変更File一覧
2. Exposure Profile Contract
3. Web Profile Config
4. Feature Policy／Public RAG Denial
5. Disabled Control Hook
6. Public Demo Foreground Entry Point
7. Model／Deployment交換性の説明
8. Test一覧と結果
9. SHA-512
10. 未解決事項
11. Platform手動検証手順
12. Rollback
13. 実装者Status

Status Filename：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_YYYYMMDDHHMMSS.md
```

## 13. Acceptance Conditions

1. Basic Previewが完全に維持される。
2. Public Demoが別Access Profile／Entry Pointとして実装される。
3. Public Demoは認証なしでNon-loopback起動できる。
4. Auth Disabledだけで偶発Public化できない。
5. Public Demoで既存Phase 1 Web機能が動作する。
6. Public DemoでDocumentation RAGが強制無効である。
7. Public専用制限Hookは`off`であり、制限実装を追加していない。
8. Model／Deployment／Access／Feature／Lifecycleが分離される。
9. Qwen、GGUF、Lightning CPUまたは固定PathをPublic CoreへHard-codeしていない。
10. Targeted Test、Full Test、RuffおよびMypyが合格する。
11. 実装者がPlatformまたはProject Root外を変更していない。
12. StatusがAppend-onlyで提出される。

## 14. Review Gate

実装者Status提出後、設計統括者役がRepository差分、Test、Basic Preview Regression、Public RAG Denial、Control Hook、Model／Deployment交換性およびWrite BoundaryをReviewする。

Review Accepted前に、ユーザーはLightning Public Demo用設定へ差分を反映しない。

Anonymous Public Accessの最終有効化はユーザー判断であり、実装完了だけでは自動許可されない。

