# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- supersedes: `implementation_roadmap_20260719202333.md`

## 1. Current Decision

Phase 1-GとPhase 1-HをMacで完成・Acceptedにした後、Project／ModelをLightningへ一括搬入する。

Phase 1-FのRead-only PreflightはAcceptedであるが、Lightning Native Runtime Gateは保留中であり、Phase 1-F全体は未完了である。

## 2. Current State

```text
Phase 1-A Environment／Metal                    : Complete／Accepted
Phase 1-B Model Adapter／CLI                    : Complete／Accepted
Phase 1-C Platform／Acceleration Hook           : Complete／Accepted
Phase 1-D Configuration／Response Language      : Complete／Accepted
Phase 1-E Thinking Presentation                 : Complete／Accepted
Phase 1 Acceptance Follow-up                    : Complete／Accepted
Phase 1-F Repository／Mac／Preflight             : Accepted
Phase 1-F Lightning Native Runtime              : Deferred／Not Run
Phase 1-G Minimal Web Surface                   : Accepted Design／Ready to Implement
Phase 1-H Post-generation Summary Mode          : Accepted Reservation／Waiting 1-G
Phase 1 Cross-environment Final Review          : Waiting
Phase 1 User Acceptance                         : Waiting
Phase 1 Backup                                  : Not Triggered
Phase 1-ex Operations Reorganization            : Accepted Reservation／Not Started
Initial GitHub Publication                      : Deferred until Phase 1-ex completion
```

## 3. Phase 1-G: Minimal Web Surface

目的：

- Macで動く最小FastAPI／Web UIを成立させる。
- Lightningへ最終的にPort公開できるApplication Surfaceを作る。
- UI Frameworkを将来React等へ交換可能にする。

Scope：

```text
FastAPI Application Boundary
Minimal Vanilla HTML／CSS／JavaScript
Ephemeral Multi-turn Chat
Streaming
Stop／Cancel
New Chat
Response Language ja／en／auto
Max New Tokens／Default 2048
Thinking Visibility OFF／ON
Thinking Label／説明改善
Minimal Preview Access Control
Runtime／Error Status
Mac User Test
```

Scope外：

```text
History Persistence／Resume
Multiple Saved Chats
Regenerate
TOML直接編集／保存
Summary Mode本実装
Governance／Guard／Judge／Agent
Markdown HTML Rendering
React／Node Toolchain
Lightning Full Upload
```

## 4. Phase 1-H: Post-generation Summary Mode

Phase 1-G Accepted後に別Handoffで開始する。

```text
要約モード OFF／ON
Default OFF
Normal Generation max 2048
Summary Generation max 1024
Summary Thinking disabled
Same Main ModelをSequential再利用
Original Final Answer Preserve
Summary Failure時はOriginalへWarning付きFallback
UI Status: 回答生成中 → 要約中
```

正本予約：

- [post_generation_summary_mode_requirements_reservation_20260721090725.md](../requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md)

## 5. Batch Lightning Gate

1-G／1-HのMac Accepted後に、専用Handoffを作成する。

```text
Final Candidate Freeze
  → Transfer Manifest／Exclude確認
  → Project Source／Static／Lock Upload
  → GGUF Persistent Placement
  → Studio-local uv 0.11.29
  → Python 3.12.11 Dependency Sync
  → llama-cpp-python CUDA Build／Reuse
  → CLI Acceptance
  → GPU Native Acceptance
  → CPU Candidate Acceptance
  → Web UI／Access／Streaming／Cancel
  → Summary Mode
  → Final Cross-environment Review
```

## 6. Phase 1 Completion Gate

Top-Level Phase 1完了には次を必要とする。

- Phase 1-A～1-Hの対象ScopeがAcceptedである。
- Mac User Testが合格している。
- Lightning Mandatory CUDA Gateが合格している。
- CPU Candidateが合格、またはEvidence付きKnown Limitationとしてユーザー承認されている。
- Web Access ControlとLive URL Testが合格している。
- User ManualがCurrent Featureを反映している。
- 設計者役が「Phase 1完了、次Phaseへ移行可能」と宣言する。
- ユーザーが最終Test合格を宣言する。

このDual Gate成立後にBackupを取得する。

## 7. Phase 1-ex／Publication

既存予約を維持する。

- Task RoleとDocs Ownership再整理
- Git移行
- Docs Directory再編
- Phase単位のLossless Compilation
- Public README／LICENSE／overview_ja／concept_ja／roadmap_ja
- Initial GitHub Publication

最初のGitHub公開はPhase 1-ex完了後である。

## 8. Later Phases

Phase 2以降の大分類は既存Roadmapを継承する。Phase 1公開後に正式番号を再整理してよい。

- Conversation Persistence／History／Resume
- Audit／Definition Infrastructure
- Main Runtime Governance
- Guardrail／Judge／Repair／Observability
- RAG
- Agent／Tool／Memory
- Experiment／Research Platform
- Cloud Scale／vLLM／PostgreSQL／Multi Model／Multi GD

## 9. Immediate Next Action

```text
実装担当がPhase 1-G Handoffを読む
  → Phase 1-Gだけを実装
  → Mac Static／ASGI／Native Test
  → Implementer Status
  → Designer Review
```

Phase 1-HとLightning Uploadを同じ実装Change Setへ混在させない。
