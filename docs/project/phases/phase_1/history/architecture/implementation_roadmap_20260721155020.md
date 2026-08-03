# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Phase 1-ex Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- Phase 10 R&D Hooks: [phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md](../governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md)
- supersedes: `implementation_roadmap_20260721093952.md`

## 1. Current State

```text
Phase 1-A Environment／Metal                    : Complete／Accepted
Phase 1-B Model Adapter／CLI                    : Complete／Accepted
Phase 1-C Platform／Acceleration Hook           : Complete／Accepted
Phase 1-D Configuration／Response Language      : Complete／Accepted
Phase 1-E Thinking Presentation                 : Complete／Accepted
Phase 1 Acceptance Follow-up                    : Complete／Accepted
Phase 1-F Repository／Mac／Preflight             : Accepted
Phase 1-F Lightning Native Runtime              : Deferred／Not Run
Phase 1-G Minimal Web Surface                   : Cross-thread Follow-up Report Received／Review Pending
Phase 1-H Post-generation Summary Mode          : Waiting Phase 1-G Acceptance
Phase 1 Cross-environment Final Review          : Waiting
Phase 1 User Acceptance                         : Waiting
Phase 1 Backup                                  : Not Triggered
Phase 1-ex Operations Reorganization            : Accepted Reservation／Not Started
Initial GitHub Publication                      : Deferred until Phase 1-ex completion
```

本SnapshotではPhase 1-G Cross-thread Follow-up実装報告を受領済みだが、設計者Final Review前であるためAcceptedとしない。

## 2. Phase 1 Remaining Sequence

```text
Phase 1-G Final Review
  → Phase 1-H Summary Mode
  → Mac Acceptance
  → Batch Lightning Upload／Native／Web Gate
  → Cross-environment Final Review
  → User Manual Finalization
  → Designer Phase 1 Completion Declaration
  → User Final Acceptance
  → Phase 1 Backup
  → Phase 1-ex
```

## 3. Phase 1-H

```text
要約モード OFF／ON
Default OFF
Normal Generation max 2048
Summary Generation max 1024
Summary Thinking disabled
Same Main Model Sequential Reuse
Original Final Answer Preserve
Summary Failure時OriginalへWarning付きFallback
UI Status: 回答生成中 → 要約中
```

Phase 1-G Accepted後に専用Handoffで開始する。

## 4. Batch Lightning Gate

Phase 1-G／1-HのMac Accepted後に一括搬入する。

```text
Final Candidate Freeze
  → Transfer Manifest／Exclude確認
  → Source／Static／Lock Upload
  → GGUF Persistent Placement
  → Studio-local uv
  → Python 3.12.11 Dependency Sync
  → llama-cpp-python CUDA Build／Reuse
  → CLI／GPU／CPU Candidate Acceptance
  → Web UI／Access／Streaming／Cancel／Summary
  → Final Cross-environment Review
```

## 5. Phase 1-ex

Phase 1完了後、初回GitHub公開前に実施する。

- 設計統括者役／Phase別設計者役／実装者役／対外Docs役の再編
- Git移行
- Docs Directory Migration
- Stable Canonical Docs 5件
- Public README／LICENSE／CITATION／NOTICE／Overview／Concept／Roadmap
- Project Continuity Master
- Lossless Phase Compilation
- Public Identity／Privacy／License／Access整備
- Backup／Commit／Tag／GitHub公開対応
- 全担当Taskへの新構造通知

## 6. Phase 2以降の大分類

Phase 1公開後に正式なPhase番号と境界を再確認する。

- Conversation Persistence／History／Resume
- Audit Log／Definition Infrastructure
- Main Runtime Governance
- Guardrail／Judge／Repair／Observability
- RAG
- Agent／Tool／Memory／Handoff
- Experiment／Research Platform
- Cloud Scale／vLLM／PostgreSQL／Multi Model／Multi GD

## 7. Phase 10：本体完成後の独立R&D統合

MARGPA Runtime LLMが一通り完成した後、別Project／別Taskの独立R&D成果を疎結合統合する。

### 7.1 例外認識型安全統治機構

```text
研究領域：AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D機構。

### 7.2 分散証跡型例外認識エージェント統治安全機構

```text
研究領域：Multi-Agent Governance,
          Distributed Accountability,
          and Safety Assurance
```

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D機構。

### 7.3 Integration Principle

- Generic External Governance Provider Port経由
- Core非依存
- Optional／交換可能
- `off／observe／enforce`
- Providerなしでも本体動作
- Algorithm／核心は現在非掲載

## 8. Immediate Next Action

Phase 1-exまたはPhase 10へ移らず、最新のPhase 1-G Cross-thread Follow-up Statusを設計者役がReviewする。

## 9. Authorization Boundary

本Roadmapは順序と予約を更新する。Phase 1-ex、Phase 1-H、Lightning Upload、Phase 10 R&D実装、Git、公開を自動許可しない。
