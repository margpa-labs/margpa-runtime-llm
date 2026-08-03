# Phase 1-G Review Follow-up 実装担当Status

- 文書ID: `implementer_status_phase_1g_review_follow_up`
- 状態: `implementation_and_verification_completed`
- 作成日時: `2026-07-21 12:18:17 JST`
- Snapshot: `20260721121817`
- 作成担当: 実装者役担当Task
- 対象Review: `designer_review_phase_1g_minimal_web_surface_20260721115330.md`
- 対象Handoff: `implementer_handoff_phase_1g_review_follow_up_20260721115330.md`

## 1. 結果

Phase 1-G Reviewで指摘されたDisconnect／Backpressure Cleanup、Token Exhaustion UI、Public Namingを修正した。必須Static／Default／Mac Native Model／Manual Browser Gateは合格した。

Phase 1-Hには着手していない。

## 2. 変更Fileと責務

| File | 変更内容 |
|---|---|
| `src/margpa_runtime_llm/web/streaming.py` | Bounded SSE QueueのProducer停止通知、投入待ちPolling、Session Iterator明示Close、Native Stream Cancel、Producer終了待ち、Timeout時失敗化 |
| `src/margpa_runtime_llm/web/static/app.js` | Request単位の`final_answer_token_limit`保持、`completed`後のWarning維持、Safe Warning Bubble表示、Canonical History非追加 |
| `src/margpa_runtime_llm/web/static/index.html` | 公開通称を`Nazuna Research Governance LLM`へ統一 |
| `src/margpa_runtime_llm/__init__.py` | Package公開名を`Nazuna Research Governance LLM`へ統一 |
| `tests/integration/web/test_web_app.py` | Backpressure早期Close、Token Warning Event列／UI Policy、Public NamingのRegression Test追加 |
| `docs/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md` | 本実装報告 |

Dependency変更はなく、`pyproject.toml`と`uv.lock`は変更していない。

## 3. Disconnect／Backpressure Cleanup

### 3.1 修正方式

- Queue Capacityは`32`のまま維持した。
- Consumer終了を`threading.Event`でBlocking Producerへ通知する。
- `run_coroutine_threadsafe(queue.put(...))`を50ms単位で確認し、Consumer終了時は待機FutureをCancelしてProducer Loopを抜ける。
- Client DisconnectまたはAsync Generator早期Closeでは、SessionへCancelを通知し、Native StreamをCancelする。
- Producer側`finally`でSession Iteratorを明示Closeし、Session `finally`とGeneration Gate解放を成立させる。
- QueueをDrainした後、Producer Taskを最大10秒待つ。Timeout時は再度Native Cancel／Drainして最大10秒待ち、なお終了しなければ成功扱いせず`RuntimeError`にする。

### 3.2 再現条件と解放Evidence

Regression Testでは96 Chunk（Queue Capacityの3倍）を生成し、Consumerは最初の`start`だけを取得した。Producerが33 Chunk以上を生成してQueue投入待ちへ入ったことを確認してからAsync GeneratorをCloseした。

限定時間内に次をAssertした。

- Native Fake Streamの`cancelled is True`
- `session.wait(2.0) is True`
- `active_request_id is None`
- 対象名の未完了Producer Taskが0件
- 直後の次Generationが`completed`

## 4. Token Exhaustion UI

ServerのEvent列が次の順序になるRegression Testを追加した。

```text
warning(code=final_answer_token_limit)
completed(assistant_message.content="")
```

Browserは対象WarningをRequest単位で保持し、直後の`completed`でStatusを上書きしない。Canonical Finalが空の場合はAssistant Bubbleへ次のSafe Warningを表示し、空Bubbleを残さない。

```text
最終回答を生成する前にToken上限へ到達しました。
```

Warning Textは`state.messages`のCanonical Assistant Historyへ追加しない。

## 5. Public Naming検索

次の範囲を検索した。

```text
src/
tests/
scripts/
config/
pyproject.toml
uv.lock
```

検索Patternは`<legacy-public-handle-pattern>`、結果は0件だった。`rg` Exit Code `1`は一致なしを示す期待結果である。Third-party Provenance等への機械的一括置換は行っていない。

## 6. Command Verification

| Command | Exit Code | 結果 |
|---|---:|---|
| `./.venv/bin/ruff format --check src scripts tests` | 0 | 88 files already formatted |
| `./.venv/bin/ruff check src scripts tests` | 0 | All checks passed |
| `./.venv/bin/mypy .` | 0 | 88 source files、issue 0 |
| `./.venv/bin/python -m compileall -q src scripts tests` | 0 | 合格 |
| `./.venv/bin/pytest -q` | 0 | 211 passed、3 deselected |
| `./.venv/bin/pytest -q tests/unit/conversation tests/unit/web tests/integration/web` | 0 | 28 passed |
| `./.venv/bin/pytest -q -m model_smoke` | 0 | 2 passed、1 skipped、211 deselected |
| `uv lock --check --offline` | 0 | 122 packages resolved、Lock整合 |
| `bash -n scripts/setup/*.sh` | 0 | 合格 |

Model Smokeの1 Skipは`MARGPA_PHASE1F_PROFILE`未指定による既定のCross-environment Skipである。Mac Native GGUF／Metal対象2件は合格した。

## 7. Mac Manual Browser Smoke

実Qwen3-4B、Metal、`MARGPA_THINKING_MODE=enabled`、`127.0.0.1:8765`で確認した。

1. `response_language=auto`、`max_new_tokens=256`でStreamingし、最終回答`OK.`、Status`完了 (stop)`を確認した。
2. Thinking有効、`max_new_tokens=1`で最終回答前Token Exhaustionを発生させた。StatusとAssistant Bubbleの双方へSafe Warningが残り、空Assistant Bubbleは0件だった。
3. Warning後にNew Chatし、`READY`を正常生成した。
4. 長文Generation中にStopし、Status`生成を停止しました`、Send再有効化、Stop無効化を確認した。
5. Stop後にNew Chatし、`AFTER-CANCEL`を正常生成した。
6. Browser Console Errorは0件だった。
7. Test ServerはApplication Shutdown完了を確認して終了した。

## 8. 未実行項目・Known Limit

- Phase 1-H Summary Modeは未着手。
- Lightning Full Upload／Model Transfer／Native Gateは未実行。
- Conversation永続化、Markdown Rendering、本格Auth、Governance／Guardrail／Judge／Repair／Agent／RAGは本Follow-upの対象外。
- Manual Browser SmokeはMac localhostの単一Browser Sessionで実施した。
