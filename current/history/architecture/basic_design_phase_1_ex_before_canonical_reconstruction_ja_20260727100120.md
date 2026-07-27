# MARGPA Runtime LLM 基本設計書

```yaml
document_id: basic_design
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 17:53:18 JST
owner: Nazuna Research
active_phase: phase_1_ex
rag_default: true
```

## 1. Scope

本書はRequirementsを実装へ渡すためのModule、Interface、State、Config、ErrorおよびDirectory境界を定義する。個別Classや関数単位の詳細設計はSourceとPhase別設計へ委ねる。

## 2. Project Module

```text
src/margpa_runtime_llm/
├─ domain／contracts
├─ application／use_cases
├─ adapters
├─ modules
└─ entrypoints
   ├─ cli
   └─ web
```

依存方向はDomain／Contractを中心とし、EntrypointやAdapterからCoreへ接続する。

## 3. Model Runtime

### Input

- Message列
- Generation Config
- Cancellation Handle
- Model Selection
- Deployment Profile

### Output

- Streaming Delta
- Final Text
- Thinking／Final Channel
- Stop Reason
- Token Usage
- Runtime Metadata

### Invariant

- 同一Runtime Instanceの同時Generation上限は1。
- Busy時は安全に拒否し、先行Requestを壊さない。
- StopはCooperative Cancelを基本とする。
- Close／ShutdownはIdempotentにする。
- Model Artifact Hash検証失敗時はLoadしない。

## 4. Configuration

```text
config/application/
  → 共通Model選択、回答、Generation、Presentation

config/profiles/
  → OS、Architecture、Device、Backend、Acceleration

config/models/
  → Model ID、Artifact Relative Path、Hash、Capability
```

Environment／CLI／Web RequestはTyped Validation後にOverrideする。UIがTOMLを直接無検証で書き換える構造にしない。

## 5. CLI

```text
margpa-llm model-info
margpa-llm generate
```

- `model-info`はEffective Config、Model、Capability、Deploymentを表示する。
- `generate`はPromptまたはstdinを受け、Streaming／Non-streamingを選べる。
- Help内の大文字表記は仮引数名であり、Literal入力ではない。
- Token上限到達、Cancel、Config Errorを区別する。

## 6. Web

### Current Surface

- New Chat
- Message Input
- Stop／Send
- UI Language
- Response Language
- Max New Tokens
- Thinking Generation／Visibility
- Summary Mode
- User／Assistant Copy

### State

- Conversation：Browser Memoryのみ
- UI Language：Browser側で保持可能
- その他Option：Reload時にRuntime Defaultへ戻る。
- Server側永続履歴：未実装

### Access Profile

```text
basic_preview:
  Basic認証

public_demo:
  匿名Access
  Side-effect-free
  Server-side Hard Limit
```

Access Modeは起動時に固定する。非Loopback BindでModeまたはPolicyが不足する場合はFail Closedとする。

Public Demoは最大生成Token、入力、Message数、会話全体量、Rate、Generation BudgetおよびTimeoutをServer側で制限する。Tool／RAG／Agent／外部I/O／永続化はLoadしない。

### Streaming Presentation

- 生成中は安全なPlain Textとして表示する。
- Completion後にSanitize済みMarkdownへ変換する。
- ThinkingとFinalを別Channel／表示領域で扱う。
- Hidden ThinkingをClientへ送らない。
- Raw Thinkingを永続化しない。

## 7. Summary Mode

```text
Original Generation
  ↓ completed
Summary Generation by same Main Model
  ↓
Summary成功  : Summaryだけを返す
Summary失敗  : OriginalへFallback
```

Summaryは情報を省略、変形する可能性があり、正確性を保証しない。追加LatencyとTokenをUIで明示する。

## 8. Error Model

最低限区別する。

```text
configuration_error
model_artifact_error
capability_error
model_busy
generation_cancelled
token_limit_reached
backend_error
summary_failed_with_fallback
authentication_required
docs_unavailable
```

内部ExceptionやPathをPublic Responseへそのまま露出しない。

## 9. Security

- Non-loopback BindはAccess Controlなしで許可しない。
- `/healthz`は最小Statusだけを返す。
- CredentialをDocs、Config、ScreenshotまたはGitへ保存しない。
- Raw HTML、Script、Event Handlerおよび危険URL Schemeを拒否する。
- Tool／RAG／外部操作は明示的に有効化されるまで実行しない。
- Public DemoではTool／RAG／外部操作をConfig Overrideでも有効化できない。

## 10. Documentation／RAG

簡易Documentation RAGの既定Source：

```text
docs/project/current/
docs/project/phases/<active_phase>/phase_index_ja.md
docs/project/phases/<completed_phase>/*_ja.md
docs/public/
```

`history/`は通常検索から除外する。`docs/`が存在しない場合は、推測で回答せず「docsが設置されていないため参照できません」と明示する。

実装はMac限定でも、次を交換可能なPortとして分離する。

```text
DocumentSourcePort
ChunkerPort
EmbeddingPort
IndexStorePort
RetrieverPort
ContextAssemblerPort
CitationPort
```

Lightning、Home ServerまたはCloudではAdapterを追加する。Public DemoではRAG PortをBindingしない。

## 11. Future Component Contract

各追加Componentは最低限次を持つ。

```text
component_id
enabled
mode
required_dependencies
optional_dependencies
capabilities
input_contract
output_contract
timeout
budget
failure_policy
status_events
audit_fields
```

Component本体と専用Governance Pointを別に有効化する。

## 12. Traceability

- [Requirements](../requirements/requirements_specification_ja.md)
- [System Architecture](system_architecture_ja.md)
- [Runtime Governance](../governance/runtime_governance_specification_ja.md)
- [Phase 1 Architecture Compilation](../../phases/phase_1/architecture/phase_1_architecture_ja.md)
