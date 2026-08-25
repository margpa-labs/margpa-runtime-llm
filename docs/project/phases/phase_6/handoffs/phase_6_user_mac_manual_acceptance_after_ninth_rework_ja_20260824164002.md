# Phase 6 — Ninth Rework後 User Mac Manual Acceptance Handoff

```yaml
document_id: phase_6_user_mac_manual_acceptance_after_ninth_rework_20260824164002
status: ready
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: user
created_at: 2026-08-24 16:40:02 JST
technical_rework_review: pass
phase_closure: not_yet
```

## 1. 起動

Project Rootで次を実行する。

```bash
./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main \
  --host 127.0.0.1 \
  --port 8000 \
  --conversation-persistence \
  --conversation-runtime-data-root "$PWD/runtime_data" \
  --conversation-scope-id "mac-local-primary" \
  --configuration-control \
  --phase-3-governance-definitions \
  --phase-3-governance-definitions-root "$PWD/definitions" \
  --phase-4-runtime-governance \
  --phase-4-runtime-governance-definitions-root "$PWD/definitions" \
  --phase-5-guardrail-governance \
  --phase-6-runtime-model-control \
  --phase-6-feature-modes
```

## 2. 必須確認

### A. UIとMode

- 設定内のOFF／ON、OFF／OBSERVE／ENFORCE、Recording OFF／METADATA／FULLは、押下だけで即時適用される。
- 不要な「適用」Buttonが残っていない。
- 利用者向け機能名に`（Phase N）`が残っていない。
- Research ModeはAdvanced Mode最下部にある。
- Advanced Mode内の重複したModel／Context Size／Max New Tokens入力がない。

### B. Model State同期

- 起動直後はQwenがCurrent Main Modelである。
- Qwen→DeepSeek切替後、Model Status、左Sidebar、環境情報、選択表示がすべてDeepSeekへ同期する。
- DeepSeek→Qwenでも同様に戻る。
- Model自身の自己申告ではなく、Current Main Model表示を正本とする。
- Server Restart後はQwen Defaultへ戻る。

### C. Context／Max New Tokens

- Model切替欄に用途不明の重複入力がない。
- 表示上限以内のContext Sizeを適用でき、失敗時は実効上限と理由が明示される。
- Native上限と現在のHardware／Backend実効上限を同一値として偽装しない。
- Max New TokensはModel別上限を表示し、Default 2048を維持する。
- Apply後、Revisionと表示値が同じSnapshotへ収束し、古い応答で巻き戻らない。

### D. Judge／Repair／Recording Golden Path

1. Main Governance、Guardrail、Judge、RepairをENFORCE、RecordingをFULLにする。
2. RAGで公式Evidenceを取得できる質問を行う。
3. ModelがEvidenceと矛盾した場合、誤答をそのままCompletedとして通さず、Repair済み回答または明示Safe Fallbackへ収束する。
4. Judgeが`malformed_output`でもFail-openせず、Candidateを通過させない。
5. Current LLM-as-a-Judge Modelは、現状のMain-self構成なら実Main Model Identityとして表示され、「未設定」と偽装しない。
6. Judge／Repair Run状態、結果、失敗理由、Recording結果が実行内容と一致する。

推奨再現質問：

```text
ホロライブ、天音かなたの読み方は？
```

必要なら次Turnで公式表記`Amane Kanata`と「あまね かなた」をEvidenceとして提示し、Evidence矛盾が修復されることを確認する。

### E. Stop／Lifecycle

- JudgeまたはRepair中にStopし、TurnがCancelledへ一度だけ収束する。
- Cancelled／Rejected／Deadline TurnのJudge Evidenceが後から遅延Commitされない。
- 通常Completed TurnのJudge Evidenceは一度だけ記録される。
- Server終了時に処理中ならfalse-cleanでUnloadせず、安全に終了または明示失敗する。

### F. DeepSeek

- DeepSeekで複数Turnを実行し、特殊Token漏れや同一文の病的反復がない。
- 反復を検出した場合は無限継続せず、Typed Failureへ有界収束する。
- Q4 Artifactの存在だけを実用品質PASSと扱わない。

### G. Persistence／Browser

- 2 Tab、Reload、Server Restart後も会話、Citation、Retry／Regenerate、Branch Selectが維持される。
- Model切替後も同じConversationの正本とCitationが壊れない。

## 3. 判定

```text
全必須項目PASS        : Phase 6 Closure Reviewへ進める
Majorな挙動不一致あり : Phase 6 ADJUST／差分Rework
DeepSeekのみ品質不足  : Qwen Default維持のうえ、DeepSeek Support dispositionを別判定
```

Manual結果は、成立項目と不成立項目を分け、実際の画面表示・入力・出力をそのままControllerへ返す。未確認をPASSへしない。
