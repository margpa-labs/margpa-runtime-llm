# 監査・評価・説明・安全性設計基準

- 文書ID: `audit_evaluation_security`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: Audit Log、Evaluation、Repair、Guardrail、Tool Permission、Judge
- 正本言語: 日本語
- 関連Governance: [runtime_governance_20260718174637.md](runtime_governance_20260718174637.md)

## 1. Audit Log基本要件

- 専用Log保存Directoryを作る
- User入力からAssistant回答までの一往復を基本単位とする
- 一往復に関係する観測可能情報を構造化保存する
- 各Log単位にSHA-512を適用する
- 整合性検証を可能にする
- 過去Logを原則上書きしない
- Evaluation、Regeneration、Repairを追記Eventとして残す
- System TraceとModel Generated Explanationを分離する
- Model、Governance、Guard、RAG、Toolを関連IDで接続する

「全情報」はSystemが観測・再現可能な情報を意味し、Model内部の真の思考過程を意味しない。

## 2. 記録項目候補

### Identity

- Schema Version
- Session ID
- Turn ID
- Request ID
- Message ID
- Event ID
- Parent Event ID
- Timestamp

### Input／Context

- User Input
- System Prompt
- Modelへ渡したMessage列
- Context
- Context Source
- Context Truncation
- Summary利用有無

### Model

- Model ID
- Model Revision
- Model File
- Model File Hash
- Quantization
- Backend
- Backend Version
- Generation Config
- Output
- Token Count
- Latency
- Stop Reason
- Error

### Governance

- Governance Definition
- Governance Version
- Governance Hash
- Governance Plan
- Governance Profile
- State Before
- State After
- Applied Rule
- Dimension Score
- Deviation
- Severity
- Affected Segment
- Recommended Action
- Executed Action
- Repair
- Re-fix

### Guard／Tool

- Guard Input
- Guard Output
- Guard Category
- Guard Severity
- Tool Call
- Tool Result
- Tool Permission
- Human Approval

### RAG／Judge／User

- RAG Query
- Retrieved Chunk
- Source
- Judge Result
- User Rating
- User Comment
- 問題Tag
- 高水準の説明概要

## 3. SHA-512

概念形：

```json
{
  "payload": {},
  "integrity": {
    "algorithm": "sha512",
    "canonicalization": "...",
    "digest": "..."
  }
}
```

`integrity`を除いた正規化済み`payload`へSHA-512を適用する。

未決事項：

- UTF-8の明文化
- Key Order
- Whitespace
- Unicode Normalization
- Number Representation
- JSON Canonicalization方式
- JCS採用可否
- Event単位／Turn単位
- Binary／Attachment
- Hash再計算手順

ARGD／DAGD本体はTurnごとに複製せず、内容Hash単位の不変Snapshotとして保存し、Turn Logから参照する。

## 4. SHA-512の限界

SHA-512単体では、PayloadとDigestを同時に改ざんされた場合を防げない。

将来候補：

- Hash Chain
- HMAC
- Digital Signature
- Append-Only Storage
- WORM
- Merkle Tree
- External Timestamp
- Remote Audit Sink

## 5. Chain of Thought方針

生のChain of Thoughtは原則保存・公開しない。

理由：

- Log量が膨大になる
- 真の内部推論と一致する保証がない
- 機密情報を含む可能性
- 安全上の問題
- 小型Modelへの負荷
- 説明用生成文と内部計算は同一ではない

代替として保存するもの：

- Interpreted Intent
- Answer Basis
- Process Summary
- Applied Governance Rule
- Retrieval Source
- Tool Usage
- Uncertainty
- Limitation
- High-Level Explanation
- Affected Claim
- Repair Summary

「Transparent Reasoning」は次として解釈する。

- Basis Disclosure
- Source Traceability
- Applied Rule
- Affected Claim
- High-Level Explanation
- Uncertainty Disclosure

System Trace由来の事実とModel Generated Explanationを明確に分離する。

## 6. User Evaluation

候補機能：

- Rating
- Comment
- 問題Tag
- Regenerate
- 修正要求
- 修正前後比較

問題Tag候補：

- 前提逸脱
- 根拠不足
- 文脈喪失
- 矛盾
- 過剰一般化
- 過剰肯定
- 過剰否定
- 不要な確認
- 出典不足
- 不確実性未開示

## 7. Automatic Evaluation

将来、GovernanceとJudgeを利用して次を評価する。

- Context Preservation
- Premise Preservation
- Scope
- Reasoning Integrity
- Expression Precision
- Dialog Efficiency
- Self Repair
- Guardrail Compliance
- Citation Support
- Uncertainty Disclosure

Rule Basedで評価できる項目はLLMへ投げない。

## 8. Repair Event Model

過去回答を削除・上書きしない。

```text
Original Answer
    ↓
Evaluation Event
    ↓
Repair Request Event
    ↓
Regenerated Answer Event
    ↓
Comparison Event
```

すべて関連IDで接続する。

## 9. Runtime GovernanceとGuardrailの分離

```text
Runtime Governance
  推論品質、前提、根拠、文脈、監査、修復

Guardrail
  安全性、禁止事項、秘密情報、攻撃検出

Tool Permission
  外部実行の許可、拒否、承認
```

関連はするが、別Moduleとして実装する。

## 10. 初期Guard方針

```text
Guard Model:
  Qwen3Guard-Gen-0.6B
  Phase 4で追加

Prompt Injection:
  Rule Based中心
  専用Classifierは後から追加

Tool Permission:
  Modelではなく決定論的Policy
```

将来候補：

- Input Guardrail
- Output Guardrail
- Tool Guardrail
- Prompt Injection
- Jailbreak
- Secret検出
- Personal Information検出
- Tool悪用
- Agent間攻撃
- Human Approval
- Allow／Deny List
- Capability Based Permission
- Side Effect確認

未決事項：

- 禁止範囲
- Guard強度
- Fail Open／Fail Closed
- False Positive
- False Negative
- User Override
- System Policyとの優先順位
- Governanceとの競合
- 日本語Moderation Dataset
- Streaming中のOutput停止
- Guard Model障害時

## 11. Tool Permission

Tool実行許可をLLMへ委ねない。

ModelはTool利用を提案できても、最終的な実行可否は決定論的Policy Layerが判断する。

候補状態：

- Allowed
- Denied
- Requires Human Approval
- Allowed with Constraints
- Capability Missing
- Policy Conflict
- Unknown

将来のDAAGDは既存の権限、委任、承認状態を解釈できるが、新しい権限を生成しない。

## 12. LLM-as-a-Judge

目的：

- 回答品質評価
- Governance Deviation評価
- Repair前後比較
- 複数候補Ranking
- Human Rating補助
- Rule Basedで判断しにくい意味的評価

原則：

- Judgeを常駐させない
- Judge出力を絶対視しない
- JudgeのModel ID、Config、Hashを記録する
- Judge PromptとRubricをVersion管理する
- Judge結果もAudit Eventとして記録する
- Judgeを交換可能にする
- Judge利用不可時はDegradeする
- Rule Based評価を優先できるものはJudgeへ投げない

初期候補：

```text
Selene-1-Mini-Llama-3.1-8B Q5_K_M
```

未決事項：

- 導入Phase
- Evaluation Axis
- Score
- 日本語性能
- Bias
- Self Preference
- Model系列間の偏り
- Evaluation Cost
- Judge障害時
- 複数Judge合議
- Human Ratingとの統合

## 13. Storage方針

初期候補：

- JSON
- JSONL
- Append-Only Event Log

SQLiteはIndex／検索用途のHookとする。

CloudではPostgreSQL、Object Storage、専用Audit基盤を候補とする。
