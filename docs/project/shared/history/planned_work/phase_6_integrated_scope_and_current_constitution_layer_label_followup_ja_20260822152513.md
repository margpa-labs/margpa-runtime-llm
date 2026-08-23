# Phase 6統合Scope／Current Constitution Layer名称 Follow-up

```yaml
document_id: phase_6_integrated_scope_and_current_constitution_layer_label_followup_20260822152513
status: accepted_user_direction_planned_not_started
document_type: append_only_planned_work_followup
recorded_at: 2026-08-22 15:25:13 JST
implementation_authorized: false
```

## 1. UI Label Decision

Phase 8最終実装でAdvanced Settingsへ追加するConstitution IdentityのField Labelは、次で固定する。

```text
Current Constitution Layer
```

Phase 6／8後のComponent Identity候補は次とする。

```text
Current Main Model
Current Guardrail Model
Current LLM-as-a-Judge Model
Current Governance Layer
Current Constitution Layer
```

`Current Governance Layer`は`definitions/`由来、`Current Constitution Layer`は`constitution/`由来であり、別Component／別Field／別Stateである。

## 2. Constitution／Constitutions Terminology

正式Component名とRoot Folder名は単数形を採用する。

```text
Product／Component : MARGPA Constitution
UI Field           : Current Constitution Layer
Root Folder        : constitution/
```

`Constitution`は、Project／Organization全体へ適用する一つの統合された上位規範体系を表すため、単数形が自然である。内部が複数章、複数Rule、複数Role Viewおよび複数Schemaへ分割されても、体系としては一つのConstitutionである。

`Constitutions`は複数の独立した憲法体系が並存する意味になりやすく、Current計画には適さない。複数Documentを強調する必要がある場合も`Constitution Package`、`Constitution Corpus`または`Constitution Chapters`と表現し、Component自体を`MARGPA Constitutions`とはしない。

一方、`MARGPA Governance Definitions`はARGD、DAGDその他の複数Definitionを束ねるCorpusであるため、複数形`Definitions`が自然である。二つの名称は文法上対称である必要がなく、単数／複数の違いはComponent構造の違いを正確に表す。

## 3. Phase 6 Integrated Scope Decision

次をPhase 6内で一体的に設計・実装・検証する。

1. DeepSeek-R1-0528-Qwen3-8B Q4 Local Feasibility／Integration。
2. Qwen／DeepSeekのServer再起動不要Runtime Model Switch。
3. Dynamic Context Size。
4. Dynamic Max New Tokens。
5. Phase 6本来のJudge／Evaluation／Repair／Observability。
6. Phase 6実装ターン最後のAdvanced Component Identity UI。

一つの巨大Work Unitにはせず、依存順に分割した上でPhase 6 COMPLETE_CANDIDATEまで連結実行する。

## 4. Candidate Execution Order

```text
Phase 6-0 : Entry／Phase 4・5 As-built Reconciliation／Exact Scope Freeze

Phase 6-A : DeepSeek Local Artifact／Backend Feasibility
            Canonical→Derived Q4 Provenance
            llama.cpp／Mac Compatibility
            Load／Streaming／Cancel／Unload Smoke

Phase 6-B : Runtime Model／Generation Control
            Qwen↔DeepSeek Hot Switch
            Safe Unload／Load／Rollback
            Dynamic Context Size
            Dynamic Max New Tokens
            Model／Context／Generation Identity

Phase 6-C : Evaluation Identity／Criteria／Dataset／Result Contract
            Deterministic Judge Baseline

Phase 6-D : LLM-as-a-Judge Adapter／Independence／Calibration
            Qwen／DeepSeek Role-separated Comparison

Phase 6-E : Repair Trigger／Budget／Orchestrator／Success Evaluation
            Bounded Repair／Loop Prevention／Authority Boundary

Phase 6-F : Runtime Status／Observability／User Feedback
            generating→judging→repairing→terminal

Phase 6-G : Advanced Settings／Sidebar Integrated UI
            Current Main Model
            Current Guardrail Model
            Current LLM-as-a-Judge Model
            Current Governance Layer
            Context Size／Max New Tokens

Phase 6-H : OFF／OBSERVE／ENFORCE／Repair Comparative Experiment
            Qwen／DeepSeek／Guardrail／Judge／Repair差分

Phase 6-I : Integrated Adversarial Verification／COMPLETE_CANDIDATE

Phase 6-J : Codex Independent Review／User Acceptance／Minimal Closure
```

Phase 6-JはClaude等の実装Executorへ自動委任せず、Codex／User Gateとして分離する。正式なSubphase Letter、Work Unit数およびCompletion LineはPhase 5 Closure後のPhase 6 Exact DesignでFreezeする。

## 5. Why the Combined Phase Is Feasible

- Phase 4／5のGovernance／GuardrailはModel Port周辺で分離され、Qwen固有Coreへ固定しない設計である。
- DeepSeekをJudge前に接続すれば、Phase 6 Evaluation／RepairへModel Identityと比較Contractを最初から含められる。
- Runtime Model Switch、Context SizeおよびMax New Tokensは、Judge／Repairが呼び出すGeneration Runtimeの前提として先行できる。
- Advanced UIは実Componentが成立したPhase 6実装ターン最後にまとめて投影できる。
- DeepSeek Local Feasibilityが不成立でも、Safe Unsupported EvidenceとModel-neutral Contractを残し、QwenでJudge／Repairを継続できる。

## 6. Principal Risks／Required Isolation

### DeepSeek／Q4

- Conversion Tool／Revision、Artifact Digest、Tokenizer／Template、Quality DeltaをFreezeする。
- V4 FlashをMac Gateへ混入しない。
- Qwen Current Artifactを変更しない。

### Runtime Switch

- Active Generation中の切替を拒否する。
- Load失敗時のQwen Rollbackを必須にする。
- Conversation、RAG、Citation、GovernanceおよびGuardrailを維持する。

### Context／Tokens

- `context_size`変更はServer再起動ではなくModel内部Reloadとする。
- `max_new_tokens`変更はReloadなしで次Generationへ反映する。
- Model／Backend／Deployment／Current Promptから動的上限を導出し、Silent Clampしない。

### Judge／Repair

- Main ModelとJudge RoleをIdentity上分離する。同一Artifact使用時もRoleを同一視しない。
- Judgeは最終Authorityを持たない。
- Guardrail Critical Rejectを品質Judge／Repairで解除しない。
- Repair Attempt／Token／Call／Time／Depthを有界化する。

### UI

- Advanced Settings表示はServer側Canonical Stateを正本にする。
- Candidate／Requested値を成功前にCurrentとして表示しない。
- Settings再Open／Browser Reload／別Tabで現在値へ追随する。

## 7. Default Mode

Phase 6で追加・統合するOFF／OBSERVE／ENFORCE対応Componentは、原則としてStartup Defaultを全て`OFF`とする。明示Applyがある場合だけOBSERVE／ENFORCEへ進める。

DeepSeekを追加してもStartup Default Main ModelはQwenのままとする。

## 8. Non-Authorization

本Follow-upはPhase 6統合設計の予約であり、Phase 6開始、DeepSeek Conversion／Load、Source／Frontend／Test／Config変更、Existing Docs編集、Git／GitHub、Network、AWS／Lightning、User Dataまたは外部操作を許可しない。

