# Phase 6-0 Advanced Runtime Component Identity Projection 予約

```yaml
document_id: phase_6_0_advanced_runtime_component_identity_projection_20260822150342
status: planned_not_started_not_authorized
document_type: append_only_planned_work
target_phase: phase_6_0_before_judge_repair_freeze
recorded_at: 2026-08-22 15:03:42 JST
implementation_authorized: false
```

## 1. Purpose

Advanced SettingsのEnvironment／Effective Runtime Information一覧へ、Main Modelだけでなく、実際に選択・Load・BindingされているGuardrail Model、LLM-as-a-Judge ModelおよびGovernance Definition LayerをSafe Typed Identityとして表示する。

本予約は、[Phase 6-0 DeepSeek Local Runtime Switch設計](phase_6_0_deepseek_local_runtime_switch_design_ja_20260822105531.md)のModel／Context／Token表示を拡張するFollow-upである。

## 2. Required Projection

Advanced Settingsへ、少なくとも次を追加する。

```text
Current Main Model
Current Guardrail Model
Current LLM-as-a-Judge Model
Current Governance Layer
```

初期表示例：

```text
Current Main Model         : Qwen3-4B Q4_K_M
Current Guardrail Model    : None
Current LLM-as-a-Judge     : None
Current Governance Layer   : MARGPA Governance Definitions v1
```

表示名`MARGPA Governance Definitions v1`は暫定例であり、固定文字列を正本にしない。実際のManifest Identity、Schema／Contract Version、Bundle RevisionおよびDigestから表示名を構築する。正式名称はPhase 6-0 Exact Freezeで決定する。

## 3. State Semantics

単純な文字列だけで状態差を潰さない。

| State | UI Meaning |
|---|---|
| `active` | Validated Artifact／Bundleが現在のRoleへBinding済み |
| `none` | そのRoleへModel／Bundleが明示的に未選択・未Binding |
| `unavailable` | 構成は要求されたがArtifact／Backend／Capabilityが利用不能 |
| `invalid` | Manifest、Schema、DigestまたはBinding検証に失敗 |
| `loading` | Load／Switch Transaction中 |
| `degraded` | 一部機能だけ成立し、完全なActiveを主張できない |

空のDefinition Corpus、Definition 0件BaselineまたはLayer未Bindingは`None`へ投影できる。ただしInvalid、Load Failure、Unknown VersionまたはDigest不一致を`None`へ隠さない。

## 4. Role Identity Contract

各Roleは同じTyped Contractへ投影する。

```text
component_role
component_kind
identity_key
safe_display_name
artifact_or_bundle_revision
artifact_or_bundle_digest
backend_key
state
reason_code
source_class
```

- Absolute Path、Secret、Raw Definition本文、Prompt、Credential、Endpoint Secretまたは内部Exceptionを表示しない。
- UI表示はServer側Canonical Runtime Snapshotから取得する。
- Browser Local State、DOM、前回表示値またはTracked Configを実Runtimeの正本にしない。
- Settings再Open、Browser Reloadおよび別Tabでも現在値を再取得する。
- Load／Binding成功Receipt前にCandidateをCurrentとして表示しない。

## 5. Guardrail Model

- Phase 5のDeterministic GuardrailがModelなしで成立する場合、`Current Guardrail Model: None`と表示する。
- `None`はGuardrail機能全体がOFFであることを意味しない。Guardrail Mode／Deterministic Stateは既存の別Fieldで表示する。
- 将来Safety Modelを接続した場合だけ、実際に選択・LoadされたModel Identityを表示する。
- Requested Candidate、Load Failed ModelおよびFallback前ModelをCurrentへ残さない。

## 6. LLM-as-a-Judge Model

- Phase 6でJudge Modelが未接続の場合は`None`。
- Main ModelをJudgeにも利用する場合、実際のModel Identityを表示し、Roleが`judge`であることを区別する。
- Main／Judgeが同じ場合も一つへ潰さず、Role別Identityを維持する。
- Judge Model切替、Unavailable、Calibration未完了およびUnsupportedを状態として区別する。

## 7. Governance Layer

`definitions/`のDirectory名や存在だけでActiveを宣言しない。Current Governance Layerは、Validated Manifest、Selected Bundle、Schema／Contract Version、Revision、DigestおよびBinding Stateから投影する。

Candidate Display：

```text
MARGPA Governance Definitions v1
MARGPA Governance Definitions v1 · degraded
None
Unavailable
Invalid
```

- Definition 0件を研究Baselineとして意図的に選択した場合と、Manifest Load Failureを分離する。
- ARGD／DAGD等の個別Definition名一覧をEnvironment Summaryへ大量展開しない。必要ならDetail Viewへ分離する。
- Layer表示はAuthority、PermissionまたはEnforcement成功を生成しない。

## 8. UI Placement

Advanced Settingsの既存Environment／Effective Configuration一覧で、Metal、Backend、Current Main Model、SQLite等と同じSafe Summary群へ追加する。

推奨Group：

```text
Runtime
  Acceleration／Backend／Device／Storage

AI Components
  Main Model
  Guardrail Model
  Judge Model
  Governance Layer
```

SidebarへはPhase 6-0 DeepSeek GateでCurrent Main Modelを表示する。Guardrail／Judge／Governance LayerのSidebar常設は本予約では必須にせず、Advanced Settingsを正規の詳細表示場所とする。

## 9. Acceptance Candidate

- Model／Layer未接続時に`None`を表示する。
- Invalid／Unavailable／Degradedを`None`またはActiveへ誤投影しない。
- Qwen／DeepSeek切替後にMain Model表示が追随する。
- Guardrail Model接続有無とGuardrail機能Modeを混同しない。
- Judge Model未接続／Main再利用／独立Modelを正確に区別する。
- Governance Definition 0件、Valid Bundle、Invalid Bundle、Unknown Versionを区別する。
- Settings再Open／Browser Reload／別TabでServer側Canonical Stateへ追随する。
- Safe DisplayへPath、Secret、Raw DefinitionまたはPromptを露出しない。

## 10. Non-Authorization

本書は予約であり、Phase 6開始、Source／Frontend／Test／Config変更、Model Load、Definition変更、Git／GitHub、Network、AWS／LightningまたはUser Data接触を許可しない。

