# 実装者役担当タスク 引き継ぎ

- 文書ID: `implementer_handoff`
- 状態: `waiting_for_implementation_unlock`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: 将来の実装者役担当タスク
- 正本言語: 日本語
- supersedes: `implementer_handoff_20260718174637.md`
- 共通引き継ぎ: [common_project_handoff_20260718193435.md](common_project_handoff_20260718193435.md)

## 1. 現在の状態

実装は未解禁。

ユーザーから明示的な解禁を受けるまで、Source、Config、Dependency、Gitを変更しない。

## 2. 実装者の責務

- Current Requirementsに従う
- Current Architectureに従う
- ADRを確認する
- Module Boundaryを守る
- Model固有処理をAdapterへ閉じ込める
- User固有PathをCoreへ入れない
- Testを実施する
- 実装上のDeviationを報告する
- 設計上の不明点を設計者へ差し戻す
- 勝手にScopeを拡張しない

## 3. 実装開始前の必読

1. [documentation_index_20260718193435.md](../documentation_index_20260718193435.md)
2. [common_project_handoff_20260718193435.md](common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../requirements/project_requirements_20260718193435.md)
4. [system_architecture_20260718193435.md](../architecture/system_architecture_20260718193435.md)
5. [model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)
6. [runtime_governance_20260718174637.md](../governance/runtime_governance_20260718174637.md)
7. [implementation_roadmap_20260718193435.md](../architecture/implementation_roadmap_20260718193435.md)

## 4. 最初のImplementation Scope

実装解禁後も、最初はPhase 1から開始する。

- Model Load
- 一問一答
- Chat Template
- Streaming
- Stop
- Generation Config
- Error Handling
- Model Adapter
- Model Registry
- Model Capability

RAG、Agent、16GD、自動Routingを同時実装しない。

## 5. Model

Initial Main：

```text
models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

GuardとJudgeはPhaseに従って追加する。

Model File名を解析してMetadataを推測しない。Registryを使用する。

## 6. 実装上の重要境界

- CoreはModel Backendを直接Importしない
- CoreはFilesystemを直接操作しない
- UIはGovernance Logicを持たない
- Tool PermissionをLLMへ委ねない
- Audit Eventを上書きしない
- 生のChain of Thoughtを保存しない
- Guardを通常Chat Modelとして扱わない

## 7. 未決事項

Project Directory構成は決定済みで、Phase 1最小Directoryのみ作成済み。

Local Backend、Config方式、Dependency管理、UI等はまだ未決。設計確定と実装解禁前にSource Fileを作成しない。

Directory構成の正本：

- [project_directory_structure_20260718192110.md](../architecture/project_directory_structure_20260718192110.md)
