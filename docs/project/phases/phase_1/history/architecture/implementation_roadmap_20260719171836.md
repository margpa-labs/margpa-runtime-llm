# MARGPA Runtime LLM 実装Roadmap

```yaml
document_state: current
created_at: 2026-07-19 17:18:36 JST
supersedes: implementation_roadmap_20260719164641.md
```

## 1. 目的

本書は、MARGPA Runtime LLMを、交換可能な単体推論Runtimeから、疎結合なAI実験・Runtime Governance Platformへ段階的に拡張するための現在有効な実装Roadmapである。

各Top-Level Phaseは、機能、独立Review、再現性、User Manual、User Acceptance Test、Designer Completion Declaration、Backupを分離して管理する。

## 2. 最上位方針

- Application CoreをModel、Backend、OS、GPU、UI、Storage、Governance Definitionから分離する。
- Model本体以外の各Layerと各Governance Pointを個別に無効化、観測、強制できる構造を目指す。
- Governance Definitionが0件でも起動可能とする。
- `ARGD`、`DAGD`を含め、特定のGD名やSchemaをCoreへハードコードしない。
- 共通Governance Control Planeと分散Governance Pointを分離する。
- Local macOSとLightning AI Studio上のLinuxを主要な開発・検証環境とする。
- UIは一般利用者向け設定と研究開発者向け設定を分離する。

## 3. Phase状態

### Phase 0: Requirements and Foundation Design

状態: `Complete`

### Phase 1: Portable Local Inference Runtime

```text
Phase 1-A Environment                          : Complete／Accepted
Phase 1-B Model Adapter／CLI                   : Complete／Accepted
Phase 1-C Platform／Acceleration Hook          : Complete／Accepted
Phase 1-D Configuration／Response Language     : Complete／Accepted
Phase 1-E Thinking Presentation                : Complete／Accepted
Phase 1 Cross-phase Readiness                  : Pass
Phase 1 Current User Manual                    : Ready
Phase 1 User Acceptance Test                   : Waiting
Designer Completion／Phase 2 Eligible Gate     : Waiting
Phase 1 Backup                                 : Not Triggered
```

Top-Level Phase 1状態: `Ready for User Acceptance Test`

### Phase 2: Conversation Application and Web UI

- FastAPI等によるApplication Boundary
- GPT風Chat UI
- Multi-turn Conversation
- Streaming、Stop、Regenerate
- New Chat、History、Resume
- 一般設定: Model、Response Language、New Chat等
- 研究開発者向け設定: Generation、Layer、Governance、Backend、Logging等
- Config Schema Validation、Effective Config、Diff、保存

状態: `Planned／Implementation Not Authorized`

### Phase 3: Audit and Definition Infrastructure

- Append-Only Turn／Event Log
- JSON／JSONL、Canonicalization、SHA-512
- Definition Repository／Loader／Validator
- Definition 0件での正常起動
- High-Level Explanation

状態: `Planned`

### Phase 4: Main Runtime Governance

- 任意GD Definitionの登録とCompile
- Governance Registry／Compiler／Shared State
- Main Model Governance Point
- `off`／`observe`／`enforce`
- Deviation、Action、Repair、Rebind、Enforce、Reinitialize

状態: `Planned／Priority Raised`

### Phase 5: Guardrail, Judge, Repair, and Observability

- Guardrail／Judge／Repair Layerと専用Governance Point
- LLM-as-a-Judge
- Rule Based Prompt Injection
- Deterministic Tool Permission
- Event Bus／Status Reporting

状態: `Planned／Priority Raised`

### Phase 6: External Linux Development Profile

- Lightning AI Studio
- Linux GPU／CPU Profile
- SSH、VS Code、永続化、Port公開
- MacとのConfig、Adapter、Test共有

状態: `Planned／Priority Raised`

### Phase 7: RAG

状態: `Planned`

### Phase 8: Agent and Tool Execution

状態: `Planned`

### Phase 9: Experiment and Research Platform

状態: `Planned`

### Phase 10: Expansion and Cloud Scale

状態: `Future`

## 4. Phase 1 Finalization Evidence

- Individual Reviews: Phase 1-A～1-E Accepted
- Cross-phase Review: [designer_review_phase_1_final_readiness_20260719171836.md](../handoffs/designer_review_phase_1_final_readiness_20260719171836.md)
- User Manual: [phase_1_macos_user_manual_20260719171836.md](../user_manual/phase_1_macos_user_manual_20260719171836.md)
- Known Issues: [known_issues_and_observations_20260719171836.md](../operations/known_issues_and_observations_20260719171836.md)
- Backup Policy: [phase_completion_backup_policy_20260719171836.md](../operations/phase_completion_backup_policy_20260719171836.md)

Static／Default／Native Evidence：

```text
Ruff／Mypy／Compileall／Bash : Pass
Default Pytest              : 161 passed, 2 deselected
Native Metal                : 2 passed, 161 deselected
uv Lock                     : 117 packages
uv Offline                  : 115 packages／No changes
```

## 5. Dual Approval／Backup Gate

Phase Backupは次の二重条件で発火する。

```text
Gate A: Designer Phase Completion + Next Phase Eligible Declaration
Gate B: User Acceptance Test Pass Declaration
```

両Gateは同じProject状態を参照する。片方だけではBackupしない。Gate成立後にMaterial Changeがあれば、影響範囲に応じて再Review／再Testする。

## 6. Current Next Action

1. ユーザーが`phase_1_macos_user_manual_20260719171836.md`のSection 22を実行する。
2. 全項目合格なら、対象Manualを明示して合格宣言する。
3. 設計者役がMaterial Changeなしを確認する。
4. 設計者役がPhase 1完了・Phase 2移行可能を宣言する。
5. Dual Gate成立後にPhase 1 Backupを作成・検証する。
6. Backup後にPhase 2へ進む。

現時点でPhase 2実装、Designer Completion Declaration、User Test Pass Declaration、Phase 1 Backupは未実施である。

