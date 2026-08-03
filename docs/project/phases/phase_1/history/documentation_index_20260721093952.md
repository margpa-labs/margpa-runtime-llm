# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721092818.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-A～1-E                         : Accepted
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Accepted
Lightning Project／Studio-local uv     : 0.11.29／Pass
Lightning Existing uv                  : 0.11.18／Unchanged
Lightning Python                       : 3.12.11／Retained
Lightning Full Upload                  : Deferred until Phase 1-H Mac Acceptance
Phase 1-F Lightning Native Gate        : Not Run／Not Complete
Phase 1-G Minimal Web Surface Design   : Accepted
Phase 1-G Implementation               : Authorized／Not Yet Reviewed
Phase 1-H Summary Mode                 : Accepted Reservation／Waiting Phase 1-G
generation.max_new_tokens              : 2048／Current Default
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721092818.md](documentation_index_20260721092818.md)から継承する。

本Snapshotでは、ユーザー判断により次の実施順を正式化した。

```text
Phase 1-F Lightning Read-only Preflight Accepted
  ↓
Phase 1-G Minimal Web SurfaceをMacで実装／検証
  ↓
Phase 1-H Post-generation Summary ModeをMacで実装／検証
  ↓
Project／ModelをLightningへ一括Upload
  ↓
Lightning GPU／CPU Native Verification
```

大量Uploadの重複を避けるための順序変更であり、Phase 1-F Lightning Native Gateの省略または合格扱いではない。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721092818.md](documentation_index_20260721092818.md) | 本文書 |
| superseded | [implementation_roadmap_20260719202333.md](architecture/implementation_roadmap_20260719202333.md) | [implementation_roadmap_20260721093952.md](architecture/implementation_roadmap_20260721093952.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [ADR-0016 Lightning一括Upload順序](adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md) | Phase 1-G／1-H先行とLightning搬入順序の決定 |
| current | [Implementation Roadmap](architecture/implementation_roadmap_20260721093952.md) | Phase全体の現行実施順とGate |
| accepted | [Phase 1-G Requirements](requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md) | Minimal Web Surfaceの正本要件 |
| accepted | [Phase 1-G Architecture](architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md) | UI／API／Auth／Concurrencyの設計正本 |
| accepted_ready_for_implementation | [Phase 1-G Implementer Handoff](handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md) | 実装担当への正式指示 |

## 5. Phase 1-G Fixed Scope

```text
Web Framework             : FastAPI 0.139.2
ASGI Server               : Uvicorn 0.51.0
ASGI Test Client          : HTTPX 0.28.1
UI                        : Local Vanilla HTML／CSS／JavaScript
Future UI                 : React等へ交換可能なAPI Boundary
Conversation              : Browser-owned Ephemeral Multi-turn
Persistence               : None
Streaming                 : Required
Cancellation              : Required
Model Load                : One Process／One Instance
Concurrent Generation     : One／Second Request is 409
Public Bind               : Server-side Preview Auth Required
Health Check              : Minimal Unauthenticated `/healthz`
Static Asset              : Local only／No CDN
Model Output Rendering    : Plain Text／No direct HTML injection
```

## 6. Phase 1-G UI Setting Boundary

一般利用者がPhase 1-G UIで変更できる設定は次の3項目だけである。

```text
response.language
  ja／en／auto

generation.max_new_tokens
  integer
  default: 2048

presentation.thinking.visibility
  OFF／ON
  default: OFF／hidden
```

`generation.thinking_mode`はUIのVisibility Switchとは別である。Visibility変更だけでThinking Executionを変更しない。

Thinking表示Labelの初期値は`高度推論`から`推論過程`へ変更する。UIでは`推論過程（モデル生成）`等、モデルが生成した区間であることを明示する。

## 7. Phase 1-H Reservation

Phase 1-Hは[post_generation_summary_mode_requirements_reservation_20260721090725.md](requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md)をCurrent Reservationとする。

```text
Summary Mode UI       : OFF／ON
Default               : OFF
Normal Generation Max : 2048
Summary Generation Max: 1024
Summary Thinking      : Disabled
Execution             : Same Model／Sequential Second Pass
Original Answer       : Preserved internally for Audit／Future Comparison
```

Phase 1-GのAccepted Review前にPhase 1-Hへ着手しない。Phase 1-G UIへ未実装Summary Switchを先行表示しない。

## 8. Lightning Decision

```text
Python                         : 3.12.11を維持
Project／Studio-local uv        : 0.11.29を維持
Studio既存uv                   : 0.11.18を変更しない
Full Project Upload            : Phase 1-G／1-H Mac受入後
Model Upload                   : 同一Batch候補
GPU Native Verification        : Full Upload後
CPU Native Verification        : Full Upload後
```

MacはPython 3.13.14、LightningはPython 3.12.11をSupport Pairとして扱う。

## 9. Immediate Next Gate

実装担当は次の文書を読み、Phase 1-Gだけを実装する。

1. [Phase 1-G Requirements](requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
2. [Phase 1-G Architecture](architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
3. [ADR-0016](adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
4. [Phase 1-G Implementer Handoff](handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md)

実装後は次を作成し、設計者Reviewへ戻す。

```text
docs/handoffs/implementer_status_phase_1g_minimal_web_surface_YYYYMMDDHHMMSS.md
```

Review時はRepository、Test、Manual Smoke、Statusを確認し、新TimestampのDesigner ReviewとDocumentation Indexを一緒に作成する。

## 10. Authorization Boundary

本IndexとPhase 1-G Handoffは、Phase 1-GのRepository実装とMac検証を許可する。

次はまだ許可しない。

- Phase 1-H実装
- Lightning Full Upload
- Lightning Dependency Install／Native Build／Model Transfer
- Phase 1完了宣言
- Backup
- Phase 1-ex開始
- Git初期化
- GitHub公開
- 本格UI／React化
- Chat永続化

## 11. Deferred Observations

過去Snapshotから次を継承する。

- Linux／Windowsの完全自動Profile Routingは後続の局所修正候補。
- Hidden Thinking時に最終回答前Token上限へ到達した場合の空表示は、Phase 1-Gで明示状態へ改善する。
- Thinking表示前後の余分な空行はPresentation正規化候補。
- Response LanguageがFinal Answerへ適用されても、Model生成Thinking区間の言語は一致しない場合がある。
- 不正Environment設定と別Field CLI Overrideが同時にある場合、Error原因分類が少し不正確になる低優先度観察事項がある。
- Setup Recipeの通常実行が`llama-cpp-python` Native Rebuildを毎回行う点は将来分離候補。

## 12. Append-Only

既存Docsを編集せず、新TimestampのRequirements、Architecture、ADR、Roadmap、Handoff、Indexとして追加した。新しいTimestampの文書を最新として扱い、旧Indexから変更のない正本文書は継承する。
