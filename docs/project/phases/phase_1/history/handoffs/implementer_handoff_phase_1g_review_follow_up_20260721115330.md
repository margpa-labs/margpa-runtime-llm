# 実装担当向け Phase 1-G Review Follow-up Handoff

- 文書ID: `implementer_handoff_phase_1g_review_follow_up`
- 状態: `waiting_user_implementation_authorization`
- 作成日時: `2026-07-21 11:53:30 JST`
- 更新日時: `2026-07-21 11:53:30 JST`
- Snapshot: `20260721115330`
- 作成担当: 設計者役担当Task
- 対象担当: 実装担当Task
- 正本言語: 日本語
- Review: [designer_review_phase_1g_minimal_web_surface_20260721115330.md](designer_review_phase_1g_minimal_web_surface_20260721115330.md)
- 要件: [phase_1g_minimal_web_surface_requirements_20260721093952.md](../requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- 実装報告: [implementer_status_phase_1g_minimal_web_surface_20260721105005.md](implementer_status_phase_1g_minimal_web_surface_20260721105005.md)
- 最新Index: [documentation_index_20260721115330.md](../documentation_index_20260721115330.md)
- supersedes: なし（Phase 1-G Review Follow-up Handoff系列の初回）

## 1. Current State

Phase 1-GのStatic／Default／Web／Mac Native Model Smokeは合格した。Architecture、Conversation分離、3設定、Basic Auth、Plain Text Rendering、既存CLI非回帰の主要部分も成立している。

ただし、設計ReviewでMandatory Finding 3系統を確認したため、Phase 1-GはChanges Requestedである。Phase 1-Hへはまだ進まない。

## 2. Authorized Scope after User Approval

ユーザーがFollow-up開始を明示した後、次の範囲だけ変更できる。

```text
src/margpa_runtime_llm/web/streaming.py
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/__init__.py
tests/unit/web/
tests/integration/web/
docs/handoffs/implementer_status_phase_1g_review_follow_up_*
```

責務分離に必要な最小限のHelper追加は可能だが、Inference／Presentation Core Contractを不用意に変更しない。

## 3. Required Work

### 3.1 Disconnect／Backpressure Cleanup

1. Consumer終了をProducerへ確実に伝える。
2. Bounded Queue満杯時でもProducerが投入待ちから脱出できるようにする。
3. Client Disconnect／Async Generator Close後にSession IteratorをCloseする。
4. Native Stream Cancel、Producer終了、Session `finally`、Generation Gate解放の順序を安全に成立させる。
5. Cleanup Timeout時もOrphan Producerを残したまま成功扱いしない。
6. Queue Capacityを超えるEvent列でConsumerを早期CloseするTestを追加する。
7. 限定時間内の終了、`active_request_id is None`、次Generation成功をAssertする。

実装方式は固定しない。ただし、Unbounded Queueへの変更、Event Loop上での同期Generation、Threadを放置する回避は不可とする。

### 3.2 Token Exhaustion UI

1. `final_answer_token_limit` WarningをRequest単位で保持する。
2. 直後の`completed`でWarning Statusを上書きしない。
3. Canonical Finalが空の場合も、画面へ次を明示する。

```text
最終回答を生成する前にToken上限へ到達しました。
```

4. Warning TextをCanonical Assistant Historyへ追加しない。
5. Empty Assistant Bubbleだけを残さない。
6. `warning → completed` Event列後の最終UI Stateを決定論的に検証する。

### 3.3 Public Naming

次の2箇所を`Nazuna Research Governance LLM`へ統一する。

```text
src/margpa_runtime_llm/__init__.py
src/margpa_runtime_llm/web/static/index.html
```

修正後、Source／Test／Script／Config／Root Metadataを検索し、廃止済み第一者名義が0件であることをStatusへ記録する。Third-partyの作者名、Model Provenance、Repository IDは意味を確認し、機械的一括置換しない。

## 4. Required Verification

最低限、次を実行する。

```bash
./.venv/bin/ruff format --check src scripts tests
./.venv/bin/ruff check src scripts tests
./.venv/bin/mypy .
./.venv/bin/python -m compileall -q src scripts tests
./.venv/bin/pytest -q
./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web
./.venv/bin/pytest -q -m model_smoke
uv lock --check --offline
bash -n scripts/setup/*.sh
```

追加Regression Testは、通常の短いDisconnectだけでなく、Queue Capacity超過／Consumer早期終了を再現する。

Mac Manual Browser Smokeで次を補完する。

1. `response_language=auto`でStreamingと最終回答が成立する。
2. Thinkingを有効にし、最終回答前Token Exhaustionを発生させた場合にSafe Warningが残る。
3. Warning後、New Chatまたは再送信が正常にできる。
4. Stop／Post-cancel Generationが引き続き成立する。

## 5. Implementer Status Requirement

完了後、次の新Timestamp文書を作成する。

```text
docs/handoffs/implementer_status_phase_1g_review_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ次を記録する。

- 変更Fileと責務
- Backpressure Disconnectの再現条件、修正方式、解放Evidence
- Token Exhaustion Event列と最終UI表示
- Public Naming検索範囲と0件結果
- 全CommandのExit Code／Test件数
- Manual Browser `auto`／Warning／Post-cancel結果
- 未実行項目、Known Limit、Phase 1-H未着手の明記

## 6. Out of Scope

- Phase 1-H Summary Mode
- React／Node／本格UI
- Conversation永続化
- Markdown Rendering
- Developer／Research Settings UI
- Auth方式の本格化
- Runtime Governance／Guardrail／Judge／Repair／Agent／RAG
- Lightning Full Upload／Model Transfer／Native Gate
- Phase 1完了宣言／Backup
- Phase 1-ex／Git／GitHub公開

## 7. Start Condition

本Handoffは準備済みだが、実装開始指示ではない。

ユーザーが実装担当TaskへPhase 1-G Follow-up開始を明示した時点で、Section 2の限定範囲を変更できる。

## 8. Append-Only

既存文書を変更せず、新TimestampのHandoffとして追加した。
