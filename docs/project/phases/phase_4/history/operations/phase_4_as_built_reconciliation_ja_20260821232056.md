# Phase 4 As-built Reconciliation

```yaml
document_id: phase_4_as_built_reconciliation_ja_20260821232056
status: pass
phase: phase_4
subphase: phase_4_0
recorded_at: 2026-08-21 23:20:56 JST
operation: read_only_source_and_design_reconciliation
source_mutation: not_performed
git_mutation: not_performed
```

## 1. Result

Phase 3 As-builtとPhase 4 Candidate Packageを照合した。Phase 4-A～4-Gの目的、依存順、Mode境界、Acceptance MatrixおよびClaude自走境界を変更する重大衝突はない。Phase 4 Candidateは次のCorrection／Interpretationを伴ってFreeze可能である。

## 2. Phase 3 As-built Baseline

| Area | As-built | Phase 4 Interpretation |
|---|---|---|
| Definition Runtime | `GovernanceDefinitionsRuntime`、Manifest／Provider／Repository State | Phase 4は置換せずBinding Consumerとして拡張する |
| Adapter | `TrustedAdapterRegistry`と`ArgdDagdCombinedAdapter`等が存在 | Phase 4-Cは同じAdapterを再登録せず、既存IRからGeneric Execution Descriptorへ拡張する |
| Plan | `CompiledPlan`は`unbound`かつ`executable=false` | Phase 4はPlanを上書きせず別のBound Artifactを作る |
| Mode | `off／observe`、`enforce`はUnavailable | Phase 4で`enforce`を明示的Capability／Authority Gate付きで追加し、Silent Downgradeしない |
| Observation | Generation Start／Terminalの非介入Observer | Main pre／post Point追加後もOFF Call 0とOBSERVE非介入を維持する |
| Evidence | Typed Envelope、Canonical SHA-512、Local JSONL Store | 新EventをAllowlist型で追加し、既存Event／Readerを破壊しない |
| Web／UI | Read-only Governance StatusとSettings Control | Phase 4-Fで拡張し、Public／BasicへのPrivate Control露出0を維持する |
| Runtime | Qwen Current Route、v1／v2、Persistent／Ephemeral、RAG | Phase 4必須Baseline。DeepSeek Load／PromotionはCompletion依存にしない |

## 3. Frozen Corrections

1. `P4-C-WU-002`の「ARGD／DAGD Trusted Adapter Extension」は、既存`ArgdDagdCombinedAdapter`の重複実装ではない。Phase 3 IRから、実Sourceに存在するSemanticsだけをGeneric Execution Descriptorへ変換する追加境界とする。
2. Phase 4はPhase 3の構造的Normalized IRを破壊的Migrationしない。追加Fieldが必要な場合はVersioned Extension／Derived Artifactを使用する。
3. `enforce`追加はConfiguration、Runtime Capability、Authority、Action Registry、UI表示を同一Acceptance Matrixで整合させる。`observe`へのSilent Fallbackは禁止する。
4. Existing SSE／Persistent Commit順序、Citation、Summary、Cancel、Retry／RegenerateおよびBranch Selectを維持する。Post Governance判定は未承認ContentのGhost Completionを生まない順序で接続する。
5. `definitions/manifest.json`とSource DigestをDefinition正本とし、特定GD名、Model名、Absolute PathをCore判断へHard-codeしない。
6. DeepSeek SnapshotはCandidate Artifactであり、Phase 4 Current Modelではない。本PhaseのClaude Execution ScopeではModel Load／Promotion／Network／AWSを行わない。

## 4. Allowed Path Classes for Phase 4 Execution

Phase 4開始後、各Work Unitの責任RoleがFrozen要件とAs-builtから必要なExact Pathsだけを動的に決定する。固定Package一式の機械的作成は要求しない。

許可候補Classは次に限定する。

- `src/margpa_runtime_llm/modules/**`のPhase 4 Governance実装と必要な既存Port拡張。
- `src/margpa_runtime_llm/adapters/**`のPhase 4 Adapter実装。
- `src/margpa_runtime_llm/bootstrap/**`のComposition変更。
- `src/margpa_runtime_llm/web/**`および`frontend/**`のLocal Status／Control／Main Point統合。
- `tests/**`の新規／更新Test。
- `docs/project/phases/phase_4/history/**`のAppend-only Recovery／Correction／Handoff。

各Work Unitで上記Class内のExact Mutationを開始前に記録し、必要のないFileを作らない。

## 5. Forbidden Boundary

- Authorized Project Root外、`other/`、別Project、Provider Memory。
- User実`runtime_data/`、Secret、External Service、Network、AWS、Model Load／Promotion。
- Git／GitHub Mutation。
- Phase 4 Stable Frozen Docsの無断変更。
- Phase 5／6本実装、Phase 4-H Closure。
- Existing Testの削除／弱体化、Definition由来Code実行、Raw Thinking／Secret／System Prompt永続化。

## 6. Decision

```text
As-built Reconciliation : PASS
Required Redesign       : NONE
Required Freeze Addendum: 本File §3
Open Major Finding      : NONE
Next                    : Phase 4 Exact Design Freeze
```
