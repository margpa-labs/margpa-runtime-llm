# MARGPA Runtime LLM 実装Roadmap

```yaml
document_state: current
created_at: 2026-07-19 16:46:41 JST
supersedes: implementation_roadmap_20260719142558.md
```

## 1. 目的

本書は、MARGPA Runtime LLMを、交換可能な単体推論Runtimeから、疎結合なAI実験・Runtime Governance Platformへ段階的に拡張するための現在有効な実装Roadmapである。

各Phaseは、機能の完成だけでなく、独立レビュー、再現性、文書、User Manual、監査可能性を含めて完了判定する。

## 2. 最上位方針

- Application CoreをModel、Backend、OS、GPU、UI、Storage、Governance Definitionから分離する。
- Model本体以外の各Layerと各Governance Pointを個別に無効化、観測、強制できる構造を目指す。
- Governance Definitionが0件でも起動可能とする。
- `ARGD`、`DAGD`を含め、特定のGD名やSchemaをCoreへハードコードしない。
- 共通Governance Control Planeと、各Execution Layer直前の軽量Governance Pointを分離する。
- Runtimeの状態通知は処理経路へ密結合せず、Eventを購読するObservability／Status Reportingとして構成する。
- Local macOSとLightning AI Studio上のLinuxを主要な開発・検証環境とする。
- UIは一般利用者向け設定と研究開発者向け設定を分離する。
- 各構成差の効果とCostを再現可能に比較できるExperiment Profileを将来導入する。

## 3. Phase構成

### Phase 0: Requirements and Foundation Design

- 要件定義
- ModelとBackendの分離選定
- Directory、Configuration、Documentationの基本設計
- Runtime Governanceの基本方針
- Role分離とAppend-Only Docs運用

状態: `Complete`

### Phase 1: Portable Local Inference Runtime

目的は、交換可能なGGUF Model Adapterを備えた、CLI中心のPortable Runtime骨格を成立させることである。

#### Phase 1-A: Environment and Metal Smoke

- Python 3.13系を本命とするEnvironment
- `.venv/`
- `uv`によるDependency再現
- `llama-cpp-python` Metal Build
- Model Loadと最小Generation Smoke Test

状態: `Complete／Accepted`

#### Phase 1-B: Model Adapter and CLI Generation

- Model Port／Adapter
- GGUF Model Load
- Chat Template
- Streaming可能なGeneration境界
- CLI `model-info`／`generate`
- Generation Config
- Error Handling

状態: `Complete／Accepted`

#### Phase 1-C: Cross-platform Hook

- Platform Profile
- macOS Apple Silicon以外の拡張Hook
- Windows、Linux、CPU、CUDA、ROCm、MetalなどをCoreから分離
- Unsupported Capabilityを黙って無視しない

状態: `Complete／Accepted`

#### Phase 1-D: Configuration Layer Separation

- 共通設定、Platform Profile、Model Registry、Runtime Overrideの分離
- Source PriorityとEffective Config
- 同じ共通設定をPlatformごとに重複させない
- 設定のValidationとSource Traceability
- `ja／en／auto` Response Language

状態: `Complete／Accepted`

#### Phase 1-E: Thinking Presentation

- Response Language Defaultとの共存
- Thinkingの生成要求と表示を分離
- Thinking表示／非表示
- 表示Labelの設定化
- 初期表示Labelは`高度推論`
- Model-declared Output Protocol
- Stateful Streaming Parser／Hidden No-flash
- Raw Model OutputとPresentation Outputの境界
- Raw Reasoning Persistence disabled

状態: `Complete／Accepted`

Phase 1実装Subphaseの状態: `1-A～1-E Complete／Accepted`

Phase 1全体の状態: `Documentation／Cross-phase Finalization Pending`

### Phase 2: Conversation Application and Web UI

- FastAPI等によるApplication Boundary
- GPT風Chat UI
- Multi-turn Conversation
- Streaming、Stop、Regenerate
- New Chat、History、Resume
- 一般設定: Model、Response Language、New Chat等
- 研究開発者向け設定: Generation、Layer、Governance、Backend、Logging等
- UI入力からConfig Schema Validation、Effective Config、Diff、保存への安全な経路

状態: `Planned／Implementation Not Authorized`

### Phase 3: Audit and Definition Infrastructure

- Append-Only Turn／Event Log
- JSON／JSONL
- CanonicalizationとSHA-512
- Model、Backend、Config、Definitionの識別情報
- Definition Repository／Loader／Validator
- Definition 0件での正常起動
- High-Level Explanation

状態: `Planned`

### Phase 4: Main Runtime Governance

- `ARGD`／`DAGD`を含む任意Definitionの登録とCompile
- Governance Registry
- Governance Compiler
- Shared Governance State
- Rule Selection
- Main Model直前のGovernance Point
- `off`／`observe`／`enforce`
- Deviation、Severity、Action Resolution
- Repair、Rebind、Enforce、Reinitialize
- Profile調整機能

状態: `Planned／Priority Raised`

### Phase 5: Guardrail, Judge, Repair, and Observability

- Guardrail LayerとGuardrail Governance Point
- Judge LayerとJudge Governance Point
- LLM-as-a-Judge
- Repair LayerとRepair Governance Point
- Prompt InjectionはRule Based中心から開始
- Tool Permissionは決定論的Policy
- Event Bus
- Status Reporting／Observability
- Layer単位の`off`／`observe`／`enforce`

状態: `Planned／Priority Raised`

### Phase 6: External Linux Development Profile

- Lightning AI Studio
- Repositoryを通常のLinux環境として実行
- GPU／CPU Profile
- SSH、VS Code、永続化、Port公開を前提にした検証手順
- Local macOSとのConfig、Adapter、Test共有
- Hugging Face ZeroGPUは将来の別Backend／Demo Adapter候補

状態: `Planned／Priority Raised`

### Phase 7: RAG

- Document Registration
- Chunking、Embedding、Index、Retrieval
- Context Injection
- Source、Document Hash、Chunk、ScoreのTraceability
- RAG LayerとRAG Governance Point

状態: `Planned`

### Phase 8: Agent and Tool Execution

- Tool Registry
- Planning、Observation、Replanning
- Multi-step State
- Memory、Handoff、Completion Check
- Tool Permission、Human Approval、Side Effect確認
- Agent Layer、Tool Layerと各Governance Point
- AAGD、AISGD、MPGD、DAAGD等との接続候補

状態: `Planned`

### Phase 9: Experiment and Research Platform

- 全LayerとGovernance Pointの個別切替
- Dependency、Conflict、Degraded ModeのValidation
- Experiment Profile
- `experiment_id`、`run_id`、Model／Definition／Config Digest
- Seed、Input、Output、Latency、Token、Audit、Repair回数
- BaselineとGovernance構成差の比較

状態: `Planned`

### Phase 10: Expansion and Cloud Scale

- 複数Model、複数GD、Dynamic Routing
- CDOGD等による将来Orchestration
- vLLM、Remote Inference API
- PostgreSQL、Object Storage
- Docker、AWS、Azure
- Image／Multimodal
- 公開Demoと本格運用Profile

状態: `Future`

## 4. Phase 1-E Review結果

Phase 1-Eは、設計者役の独立レビューにより`Complete／Accepted`となった。

```text
Blocking／High／Medium Finding : 0
Low Diagnostic Observation    : 1
Required Follow-up             : 0
Acceptance Criteria            : 22／22 Pass
Default Test                   : 161 passed, 2 deselected
Native Metal Test              : 2 passed, 161 deselected
uv Lock／Offline               : Pass／No changes
```

Low Observationは、複数Sourceに跨る不正Config時のError Code分類精度に関するものであり、不正値拒否、表示、Persistence、Raw境界には影響しない。

詳細は`docs/handoffs/designer_review_phase_1e_final_20260719164641.md`を正本とする。

## 5. Top-Level Phase完了Gate

Top-Level Phaseは、実装者役が完了を報告しただけでは完了しない。原則として次を満たす必要がある。

1. Phaseの受入条件を満たす。
2. 最新の実装者Statusと関連成果物を設計者役が独立レビューする。
3. Test、回帰、再現性、Error Handlingを確認する。
4. 発見事項がある場合はFollow-upと再レビューを完了する。
5. 必要なUser Manual、Architecture、ADR、Review、Indexを揃える。
6. 設計者役がユーザーへ明示的に「Phase Nは完了です。次はPhase N+1です」と宣言する。

この宣言により、そのPhaseのBackup取得条件が成立する。

## 6. Phase 1 Finalization Gate

Phase 1-A～1-Eの実装と個別Reviewは完了したが、Top-Level Phase 1はまだ完了宣言前である。

残作業：

1. `phase_1_macos_user_manual_20260719004209.md`の後継版を作り、Phase 1-C／1-D／1-Eを反映する。
2. Windows／LinuxはHookであり、Native Verifiedではないことを明記する。
3. Phase 1-A～1-EのCross-phase受入状態を最終確認する。
4. Review、Roadmap、Common Handoff、Indexの整合性を確認する。
5. 設計者役が「Phase 1は完了です。次はPhase 2です」と明示する。
6. 宣言直後にPhase 1 Backupを作成・検証する。
7. Backup後にPhase 2へ進む。

## 7. Phase間Backup Gate

すべてのTop-Level Phaseで、完了宣言の直後かつ次Phaseの実質的な変更開始前に、Source Archive、Evidence Manifest、外部Receiptを作成・検証する。

Subphaseの完了や実装報告だけではBackupを発火させない。詳細は`docs/operations/phase_completion_backup_policy_20260719142558.md`を正本とする。

現時点ではTop-Level Phase 1完了宣言前であるため、Phase 1 Backupはまだ取得しない。

## 8. 役割とRoadmap運用

役割別の書込権限は`docs/requirements/task_role_write_authority_policy_20260719142558.md`を正本とする。

設計者役と実装者役の分離はPhase 1-A～1-Eで有効に機能した。設計者役は受入条件とHandoffを管理し、実装者役は許可範囲の実装とStatus作成を行い、設計者役が独立レビューした。

対外向けDocs作成者役は権限境界を定義済みだが、運用評価は今後行う。

## 9. 現在の次作業

1. Phase 1 User ManualをCurrent Phase 1全体へ更新する。
2. Phase 1 Cross-phase Final Reviewを行う。
3. Top-Level Phase 1完了を明示する。
4. Phase 1 Backupを作成・検証する。
5. その後、Phase 2へ進む。

Phase 2の実装、Phase 1 Backup作成、Top-Level Phase 1完了宣言は、いずれも現時点では未実施である。

