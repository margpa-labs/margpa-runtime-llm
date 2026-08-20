# Claude Phase 2-E Implementer Handoff

```yaml
document_id: claude_phase_2_e_implementer_handoff_20260815004739
status: frozen
phase: phase_2
subphase: phase_2_e
from: Claude Phase 2-E設計担当者役
to: Claude Phase 2-E実装者役
role: phase_designer
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 00:47:39 JST
language: ja
```

## From／To／Role／Status

```text
From    : Claude Phase 2-E設計担当者役
To      : Claude Phase 2-E実装者役
Role    : phase_designer -> implementer
Status  : Handoff Draft（Independent Design Review後にFreeze）
```

## Baseline

```text
Git HEAD : e007110ba713b70f3715b991e0713e511ed21184
```

## Authorized Scope

```text
- 本Mutation Manifest（claude_phase_2_e_mutation_manifest_20260815004739）に列挙された src/**／tests/** ファイルの
  新規作成・変更のみ。
- docs/project/phases/phase_2/history/handoffs/ 配下への implementer_status_* Append-only作成。
- docs/project/phases/phase_2/history/operations/ 配下へのTest Evidence Append-only作成。
```

## Forbidden Scope

```text
- docs/project/current/**, docs/project/shared/**, docs/public/**
- docs/project/phases/phase_2/phase_index_ja.md
- docs/project/phases/phase_2/{requirements,architecture,adr,governance,handoffs,operations}/**（既存File）
- modules/conversation/domain/**（Frozen、Citation Field追加を含め変更禁止）
- modules/configuration_control/**（既存Contract／Application変更禁止、Importのみ許可）
- web/access_profiles.py（既存Gate判定ロジック変更禁止）
- 既存 /api/v1/** Route定義
- Git Commit／Push／Branch等の一切
- Project Root外
```

## Current Point

```text
Design Freeze前。Requirements／Architecture／ADR／Mutation Manifest／Acceptance Matrixは作成済みDraft。
Independent Design Review未実施。
```

## 実装順序（推奨、依存関係に基づく）

1. `modules/runtime_composition/`新設（Contract→Port→Application→Public、既存Componentとの結合は最後）。
2. `modules/documentation_rag/contracts.py`・`ports.py`へCitation関連型追加（既存`DocumentationCitation`再利用）。
3. `modules/conversation/adapters/sqlite_conversation_store.py`・`sqlite_migration.py`：`turn_citations`Table追加、Migration Step追加、Commit経路拡張、Fail-closed読み取り実装。**この段階でUnit Test（Atomicity／Idempotency／Fail-closed／Migration）を先に通す。**
4. `modules/conversation/ports/conversation_store.py`：`CommitConversation`拡張。
5. `modules/conversation/application/conversation_generation.py`・`persistent_conversation_service.py`：Citation Commit配線。
6. `web/persistent_routes.py`：Detail Response拡張。
7. `bootstrap/web_application.py`：ComponentRegistry登録配線＋Citation Store配線。
8. `entrypoints/web/main.py`：新規CLIフラグ、Route Mount。
9. `web/runtime_composition_routes.py`：新規Endpoint。
10. `web/static/app.js`：`loadPersistentDetail()`拡張（Architecture §6の1箇所のみ）。
11. 統合Test（6経路Citation復元Matrix、Multi-turn／Branch非混線、Regression Full Suite）。

各Stepの完了時、動作するTestを伴わない次StepへのMerge的進行を避ける（Step 3のAtomicity/Fail-closed Testが通らないうちにStep 5以降へ進まない）。

## Validation（実装者役が実行するもの）

Acceptance Matrix（`claude_phase_2_e_acceptance_matrix_20260815004739`）全項目、および：

```text
- uv run ruff format --check .
- uv run ruff check .
- uv run mypy src/
- uv run pytest（Full Suite、Baseline 615 passed／3 deselected からの差分記録）
- git status --porcelain（Project Root外Mutation 0、対象がsrc/tests/docs/history配下のみであることを確認）
- git diff --stat <baseline>..HEAD -- docs/project/current docs/project/shared docs/public \
    docs/project/phases/phase_2/phase_index_ja.md \
    docs/project/phases/phase_2/requirements docs/project/phases/phase_2/architecture \
    docs/project/phases/phase_2/adr docs/project/phases/phase_2/handoffs \
    docs/project/phases/phase_2/operations
  （既存File部分が空であることを確認。ただし本Manifestで許可されたHistory配下への新規追加は対象外）
```

## Open Current Blocker

```text
NONE
```

## Controller-owned Next Work

```text
- Independent Design Review（本Controller Task内でDesigner役自身がReview、Freeze Receipt発行）
- Freeze後、実装者役へ本Handoffを最終Statusとして引き継ぐ
```

## Deferred Evidence

```text
- conversation_store.py の Port設計選択（CitationEvidenceStorePortをConversationRepositoryPortの一部として
  委譲するか、同一Adapter Classに両Protocolを実装させるか）は実装時に確定し、Implementer Statusへ記録する。
```

## Exact Next Route

```text
Independent Design Review／Freeze Receipt作成 -> Implementation開始
```
