# Phase 11以降 Guardrail Block Explanation／Regeneration Toggle予約

```yaml
document_id: phase_11_plus_guardrail_block_explanation_regeneration_toggle_reservation_20260909122852
document_type: planned_work_feature_reservation
document_state: reserved_not_started
earliest_target: phase_11_plus
recorded_at: 2026-09-09 12:28:52 JST
decision_authority: user
default_mode: undecided
implementation_authorized: false
append_only: true
```

## 1. User Decision

Guardrailが入力または出力候補をBlockした場合、固定された一般的な拒否文だけを返す方式に加え、RepairまたはGuardrail専用の再推論を使って、通常の回答に近い読みやすい形で、**何がBlockされ、なぜそのまま応答できないかを明確に説明する出力**を返せる機能を予約する。

- Blockを示す回答枠は当面、既存の赤表示を維持する。
- 機能はOFF／ONで切替可能にする。User原文の`OFF/OF`は本予約ではOFF／ON Toggleの意図として記録する。
- OFF時は既存の安全な固定Fallbackを維持する。
- ON時だけ、Guardrail Block専用のExplanation／Regeneration経路を使用する。

## 2. 目的

現在の一般的な拒否文では、どのCategory、どの入力部分またはどの安全境界によりBlockされたかが分かりにくい。安全境界を弱めず、次の理解を助ける。

- 対応できなかった理由。
- どの部分なら安全に答えられるか。
- 依頼をどう言い換えればよいか。
- BlockがGuardrail由来であり、通常回答の失敗ではないこと。

## 3. 非交渉の安全境界

Explanation生成はBlock判定の取消しではない。

```text
Guardrail Block remains authoritative
Explanation／Regeneration cannot release blocked content
Judge／Repair cannot override a Critical Security Block
```

- 元の危険なPromptをそのまま通常Mainへ再投入しない。
- System Prompt、Secret、内部Rule全文、検知Signatureまたは回避方法を漏らさない。
- 「普通に出力している風」であっても、Block理由であることを曖昧に隠さず明記する。
- 説明生成が失敗、Timeout、Unavailableまたは再Blockされた場合、既存固定FallbackへFail-closedする。
- Guardrail OFFを他のGovernance、Platform SecurityまたはTool Permission OFFとみなさない。

## 4. Architecture候補

```text
Guardrail Detection／Decision
  ├─ allow → normal path
  └─ block → immutable Block Evidence
             ├─ explanation feature OFF → fixed safe fallback
             └─ explanation feature ON
                  → sanitized explanation request
                  → dedicated re-inference or bounded repair
                  → output guard check
                  → red-frame explained response
```

説明生成はGuardrail固有Adapterとして隔離し、通常Chat、通常Repair、Judge Rejudge、RAG、Dev Agentへ暗黙波及させない。将来共有できる汎用Generation Portを使う場合でも、呼出しPolicyとPrompt／SchemaはGuardrail Block専用Bindingに置く。

## 5. 出力Contract候補

- `blocked: true`
- `block_stage`: input／output_candidate／stream等。
- `public_reason_category`: Userへ開示可能な抽象Category。
- `explanation`: 明確で短い理由。
- `safe_alternative`: 任意の安全な代替案。
- `generation_mode`: fixed／regenerated／repaired。
- `original_guard_evidence_pointer`
- `explanation_generation_evidence_pointer`
- `fallback_reason`: 生成失敗時だけ。

内部Detection詳細とUser向け説明を分離する。User向け説明が簡略でも、Audit側では元のBlock Decision、Provider、Rule Revision、Action、再推論回数、Cost、Latencyおよび最終Dispositionを追跡可能にする。

## 6. UI候補

- Block回答の枠は赤のまま維持する。
- SettingsにGuardrail Block ExplanationのOFF／ONを置く。
- 通常回答と誤認しないLabelまたはIconを持たせる。
- 元の固定警告と説明回答を二重に重複表示しない。
- 詳細Panelでは、BlockとExplanation生成を別Stageとして表示する。

## 7. Acceptance候補

- OFF時は説明用Model／Repair Call 0で、既存Fallbackが返る。
- ON時はBlock Decisionを維持したまま、理由と安全な代替が返る。
- Explanationが禁止情報、元の危険内容または回避手順を出さない。
- 説明生成失敗時に通常回答へFail-openしない。
- 赤枠、Block状態、Evidence Identityおよび最終Dispositionが一致する。
- 通常Chat、Judge、通常Repair、RAG、Dev AgentのSampling／Prompt／Retryへ影響しない。
- OFF／ON比較で、GuardrailのDetection結果自体を都合よく変更しない。

## 8. 未決事項

- Dedicated再推論と既存Repairのどちらを使うか。
- DefaultをOFF／ONのどちらにするか。
- Userへ開示できる理由粒度。
- Local ModelのLatency／Memory Costと最大Call数。
- Input Block、Output Block、Stream Blockを初期実装でどこまで扱うか。

これらは実装開始時に決める。本予約は現行Guardrailの変更、UI実装、Model Call、Mode Default変更またはGit操作を許可しない。
