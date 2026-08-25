# Phase 6 Seventh Rework — Package A As-built／Reproduction完了Recovery Entry

```yaml
document_id: phase_6_seventh_rework_package_a_as_built_reproduction_20260824135806
status: recovery_entry_complete
phase: phase_6
rework: seventh_rework_user_ui_runtime_model_semantic_enforcement
package: package_a
owner_role: 設計者兼実装者役
created_at: 2026-08-24 13:58:06 JST
authority: phase_6_codex_designer_implementer_seventh_rework_exact_handoff_ja_20260824134921.md
previous_entry: phase_6_seventh_rework_package_a_start_ja_20260824135445.md
next_package: package_b
```

## 1. Mandatory Reading／Authority

Exact Handoff指定の12文書を順序どおり全文読了し、Authorized Rootと`pwd`のExact一致を確認した。Git、Network、Provider Memory、User `runtime_data/`、Model Artifact Mutation、Phase 7、Roadmap、Closureには進んでいない。

## 2. Current As-built Source of Truth Inventory

### UI Mode／設定

| Surface | Canonical Server State | Current Frontend | Finding |
|---|---|---|---|
| Research／Developer | Configuration Control Snapshot | `ConfigurationControlPanel` local `researchPressed`＋`configuration-apply` | ClickだけではMutationされずP6-RW7-UI-001不適合 |
| Governance Definitions | Configuration Control CAS＋Governance Status | `GovernancePanel` local `selectedMode`＋`governance-apply` | Separate Apply Button残存 |
| Main Runtime Governance | Configuration Control CAS＋Runtime Governance Status | `RuntimeGovernancePanel` local `selectedMode`＋`runtime-governance-apply` | Separate Apply Button残存 |
| Guardrail Governance | Configuration Control CAS＋Guardrail Status | `GuardrailGovernancePanel` local `selectedMode`＋`guardrail-governance-apply` | Separate Apply Button残存 |
| Judge／Repair／Recording | `/api/v5/feature-modes/*` | Click即時Mutation済み | Failure後のCanonical再取得とResponse順序Guardが不足 |

Configuration ControlのResearch、Governance 3系は同一Snapshot Revision／Digestを共有する一方、Frontendの各Handlerは個別Async Flowであり、Response Sequence Guardがない。Rapid Click／別Panel競合／遅延Fetchが新Stateを旧Responseで上書きし得る。

### Runtime Model／Capability

```text
Startup Default Source : config/application.toml selected_model
Current Loaded Source  : RuntimeModelController RuntimeModelSnapshot
Current UI Source      : RuntimeModelStatusPanel own /api/v4/runtime-model/status fetch
Sidebar／Environment   : /api/v1/runtime bootstrap snapshot（起動時固定）
```

`RuntimeModelStatusPanel`はContext入力のHTML `max`と表示分母に`model_native_context_limit`を使用している。ControllerのContext Validationは`min(native, backend)`であり、`deployment_verified_context_limit`を含まない。さらにBackend／BootstrapはCurrent Loaded ContextをBackend／Deployment Limitへ設定するため、初期4096 Load時にQwen 32768／DeepSeek 131072をUI上限として表示しながらControllerの実適用上限は4096となる不整合をSource上で再現した。

Max New TokensのApplication Defaultは2048である。Runtime Snapshotの`max_output_token_limit`も現在2048だが、UI Basic Settingsにも固定2048入力が重複し、Runtime Model ControlのCurrent値と独立している。

### Judge／Repair／Presented Final

```text
Conversation Main Completion
  -> completed payloadを構築
  -> Main lease release
  -> Recording hook
  -> Judge hookをBackground起動
  -> completed SSEを返す

Judge
  EvaluationCase(reference=None)
  -> PromptがReference不足ならunknownを要求
  -> Strict JSON Decoder
  -> ENFORCE時だけRepair Eligibility
  -> Repairは別Turn Append候補
```

この順序では、ENFORCEでもJudge／Repair完了前にKnown-unevaluated CandidateがPresented Finalとして返る。Judge PromptはReferenceなしの通常Chatへ`unknown`を要求するため、User Correction矛盾、Premise逸脱、Unsupported Assertionを`needs_repair`へ安定Routingできない。Citation／RAG EvidenceもJudge Caseへ渡されていない。P6-GOV-010の実機`malformed_output`と誤答Presented維持はCurrent Source Flowと整合する。

Judge Identity ProjectionはSnapshot内にJUDGE Role Bindingがない場合`unavailable／None`を返す。一方Live JudgeはCurrent Main Modelを`main_self`で再利用するため、UIの「未設定」は実行Identityを表していない。

### DeepSeek

DeepSeek Model DefinitionはNative 131072、Current Deploymentは4096。Fifth ReworkのEOS正規化とMulti-turn Evidenceは保持されている。P6-GOV-010の訂正否定／病的出力はCurrent Local Q4＋Prompt／Sampling／Runtimeの品質FindingとしてPackage Fで実測する。Model Artifactは変更しない。

## 3. Reproduction／Baseline Evidence

```text
Frontend Focused Current Suite:
  7 files／80 tests PASS
  Evidence meaning: 旧Separate Apply／Native上限表示を前提とする既存TestがPASSし、
  GOV-011契約をまだ検査していないことを確認。

Backend Focused Current Suite:
  126 passed
  Targets: Runtime Model Control、Judge Prompt／Decoder、Judge／Repair Live Integration、
           Component Identity、Runtime Model Web Mutation、Feature Modes Route。
  Evidence meaning: Current As-builtの回帰Baseline。GOV-011新Acceptanceの代替ではない。

User Mac Real Browser／Models:
  P6-GOV-010／011をG5 Manual Evidenceとして採用。
```

System Process InventoryはExecution Environmentの`pgrep`がProcess List取得を拒否したため未観測であり、Active Process 0とは主張しない。

## 4. Exact Mutation in Package A

Production Source／Frontend／Test／Config／Model Definition Mutationは0。新規Append-only Recovery 2件とProject-local Task Temporaryだけを作成した。

## 5. Action Inventory

```text
Authorized Root外Filesystem Action : 0（本Cycle実行Log）
Provider Memory Internal Contact    : 0（本Cycle実行Log）
User runtime_data Contact           : 0（本Cycle実行Log）
Git Action                          : 0（本Cycle実行Log）
Network Action                      : 0（本Cycle実行Log）
Model Artifact Mutation             : 0（本Cycle実行Log）
```

## 6. Exact Next Action

Package BでMode Selector即時適用、Canonical rollback／response-order guard、UI重複Field整理、Research Mode最下部移動、Phase Suffix／旧CopyのUI基盤修正を行う。
