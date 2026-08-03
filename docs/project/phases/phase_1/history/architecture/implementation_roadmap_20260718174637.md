# 実装ロードマップと現在地点

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: Phase、順序、現在地点、未決事項
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718174637.md](../requirements/project_requirements_20260718174637.md)

## 1. 現在地点

現在は`Phase 0`。

```text
要件定義
技術選定
Architecture設計
Directory構成設計
```

Model選定とModel物理配置の基本判断は完了した。

Source Code、Config、Dependency、Gitは未着手。

## 2. Phase 0：要件定義・技術選定

対象：

- 要件定義
- Model選定
- Inference Backend選定
- UI選定
- Storage選定
- Governance実行方式
- Project Directory構成
- Docs設計
- MVP境界
- ADR

完了済み：

- Project目的の統合
- M2 Pro・16GB制約の確認
- Main Model選定
- Guard Model選定
- Judge候補選定
- Quantization選定
- External Model Root決定
- Model Directory作成はユーザー側で完了
- POSIX Symbolic Link作成
- Docs分類Directory作成はユーザー側で完了
- 初期基準Docs作成

未完了：

- Project全体Directory構成
- Python Package構成
- Local Backend最終決定
- UI最終決定
- Storage Schema
- Config方式
- Dependency管理
- Test方針
- Governance Compiler詳細
- MVP Acceptance Criteria

## 3. Phase 1：最小推論

- Model Load
- Model Unload
- 一問一答
- Chat Template
- Streaming
- Generation Config
- Stop
- Error Handling
- Model Adapter
- Model Registry
- Model Capability
- Token Count
- Latency

Acceptance候補：

- Qwen3-4B GGUFをLocalでLoadできる
- User Inputに対してStreaming回答できる
- Stopできる
- Generation Configを変更できる
- Model Metadataを取得できる
- Model固有処理がAdapter内に閉じている

## 4. Phase 2：対話Application

- FastAPI等
- Web UI
- Multi-Turn
- New Chat
- History
- Resume
- Stop
- Regenerate
- Session管理
- Error表示

## 5. Phase 3：AuditとCore Governance

- Audit Log Directory
- Turn Log
- JSON／JSONL
- SHA-512
- Definition Loader
- Definition Validator
- ARGD／DAGD Snapshot
- Governance Compiler初期版
- Core Governance Profile
- High-Level Explanation
- Governance State
- Status表示

## 6. Phase 4：Evaluation、Repair、Guardrail

- Evaluation
- Deviation
- Severity
- Repair
- Re-fix
- Rebind
- Status Reporting
- User Rating
- Audit Log UI
- Guardrail
- Qwen3Guard
- Rule Based Prompt Injection対策
- Output Guard

## 7. Phase 5：RAG

- Document登録
- Chunking
- Embedding
- Retrieval
- Context Injection
- Source
- Citation
- RAG Audit
- RAG On／Off

## 8. Phase 6：AI Agent

- Tool Registry
- Multi-Step Execution
- Planning
- Observation
- Tool Permission
- Human Approval
- Side Effect確認
- Agent Audit
- Loop制限

## 9. Phase 7：拡張

- SQLite
- Lightweight ARGD／DAGD
- 複数Model
- 複数GD
- Image
- Docker
- AWS／Azure
- vLLM
- Routing
- LLM-as-a-Judge本格統合
- CDOGD
- 他Domain GD

## 10. 現在の禁止事項

ユーザーから明示的な実装解禁があるまで、次を行わない。

- 実装
- Source／Config作成
- Dependency Install
- 追加Model Download
- Git初期化
- 外部Service変更

このDocs作成許可は、Source実装の解禁を意味しない。

## 11. 次の設計議題

次にProject全体のDirectory構成を設計する。

検討対象：

- `src/`のPackage名
- Domain
- Application
- Ports
- Adapters
- Model Runtime
- Governance Runtime
- Guardrail
- Audit
- Storage
- API
- UI
- RAG
- Agent
- Config
- Tests
- Local Runtime Data
- Git管理対象／非対象
- Cloud移行境界

概念候補：

```text
margpa-runtime-llm/
├─ docs/
├─ models -> External Model Root
├─ src/
├─ tests/
├─ config/
├─ data/
├─ logs/
└─ scripts/
```

この構成はまだ確定していない。

## 12. 主要未決事項一覧

### Model／Backend

- llama.cppとllama-cpp-pythonの選択
- Thinking Mode
- Initial Context Size
- Default Generation Config
- Load／Unload戦略
- Guard Prompt／Parser
- Judge日本語性能

### Governance

- Compiler仕様
- Rule表現
- State Machine
- Score／Weight
- Action Resolver
- Repair Loop
- Context Overflow Policy

### Audit

- JSON Schema
- Canonicalization
- ID体系
- Timestamp形式
- Hash Chain導入時期
- PII／Secret保存方針

### UI／Application

- StreamlitまたはFastAPI系
- Frontend分離
- Streaming方式
- Cancel方式
- Conversation Data Model

### Security

- Fail Open／Fail Closed
- Prompt Injection Rule
- Secret検出
- User Override
- Tool Approval
- Policy優先順位

### Public Release

- Repository License
- Public／Private
- ARGD／DAGD同梱方式
- Sample Log匿名化
- Third-Party Notice
