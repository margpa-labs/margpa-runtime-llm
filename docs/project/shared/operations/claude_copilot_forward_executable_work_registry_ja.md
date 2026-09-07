# Claude／Copilot 前倒し可能作業Registry

```yaml
document_id: claude_copilot_forward_executable_work_registry
document_type: stable_forward_work_registry
document_state: current_catalog_not_execution_authority
language: ja
created_at: 2026-09-02 12:17:40 JST
updated_at: 2026-09-02 12:17:40 JST
owner: Nazuna Research
providers:
  - Claude
  - GitHub_Copilot
execution_authority: false
parallel_mutation_default: prohibited
```

## 1. Purpose

本Registryは、主担当ProviderのQuota、ContextまたはSessionが不足した際に、Claude／Copilotへ前倒し可能なBounded Workを選ぶためのCurrent Catalogである。登録だけでは実行Authorityを生成せず、開始時に一つのTask IDを個別Exact Handoffで指定する。

同一Source範囲へ二つのExecutorを同時投入しない。ControllerはExecutorのReturnまで原則待機し、無断のW稼働、重複Test、重複Docs読込および競合Mutationを避ける。

## 2. Routing Rules

- `Provider ≠ Role ≠ Task ≠ Authority`。Provider名だけで権限を推定しない。
- Current Working Tree、Recovery、Exact HandoffおよびEvidenceを正本とする。
- Explicitに割り当てた一項目だけを実行し、Stale Taskや過去Partialを自動再開しない。
- Completed Work Unitを再実行・Rollbackしない。
- Routine Progress、Minor FindingまたはPending ReviewでUserを呼ばない。
- Network、Artifact、Dependency、`runtime_data`、Git、Backup、ClosureおよびPhase移行はDefault Denyとする。
- Recent Verified ContextはInvalidation Triggerがない限り再利用し、毎Turnの全Docs再読をしない。

## 3. Current Forward Work Catalog

| ID | Work | Preferred Provider | Entry | Allowed Output | Default Prohibition |
|---|---|---|---|---|---|
| FW-P9-01 | 軽量独立Judge Shortlist／取得 | Claude | Package 1 Handoff | Artifact＋Identity＋Recovery | Judge修復／Git |
| FW-P9-02 | Judge／Semantic／ENFORCE Long-run | Claude | FW-P9-01 Return | Source／Test／Evidence／Return | Phase 9-2／Closure |
| FW-P9-03 | Focused Regression Guard追加 | Claude／Copilot | Controller FindingとExact Path | Test＋最小Source差分 | 全体再設計 |
| FW-P9-04 | Test Hermeticity／Fixture隔離 | Claude／Copilot | 再現可能な既知Failure | Fixture＋Regression Evidence | Real Network／User Data |
| FW-P9-05 | Static Type／Lint Debt局所解消 | Claude／Copilot | 対象Fileと既知Error固定 | Mechanical Diff＋Focused Check | Scope外Refactor |
| FW-P10-01 | Phase 10 Docs Source Inventory | Claude／Copilot | Read-only Handoff | Source Map／Conflict候補 | Constitution統合／書換え |
| FW-P10-02 | Constitution 3系統Traceability準備 | Claude | Read-only Handoff | Trace Matrix Draft | Normative昇格／統合 |
| FW-OBS-01 | Internal Observability UI項目設計 | Claude／Copilot | 予約事項と現UI一覧 | UI Concept／Field Contract | 実装／MVP Scope拡張 |
| FW-EVID-01 | Provider Resource Evidence正規化 | Claude／Copilot | 対象Evidence Paths | Comparable Metrics Table | Model一般化／順位確定 |
| FW-DOC-01 | Recovery／Handoff／Index整合確認 | Claude／Copilot | Exact Docs Scope | Docs-only Correction | Source／Git／Closure |

## 4. Provider Guidance

Claudeは、複数ModuleをまたぐLong-run、Architecture判断、Provider比較、Recoveryおよび二段階Internal Reviewを伴うWorkへ優先する。ただしRiskやPending Reviewを理由に独自Gateを挿入しない。

Copilotは、小さく固定したSource／Test範囲、Regression Guard、Mechanical Type修正およびDocs-only整合へ優先する。月間Quota消費とStale Task再開Riskがあるため、同一月に巨大Long-runを一つ渡さず、Matched Small WUで使う。

## 5. Return Schema

各Returnは最低限次を含む。

```text
Assigned Work ID
Provider／Model Profile
Task Identity
Completed／Partial／Invalid Boundary
Changed Paths
Tests／Checks
Findings／Rework
Resource／Compaction
Active Process／Temporary Artifact
Exact Next Action
Maximum Claim
```

本Registryは候補一覧であり、Executorが自分でTaskを選択、開始または連結するAuthorityを持たない。

