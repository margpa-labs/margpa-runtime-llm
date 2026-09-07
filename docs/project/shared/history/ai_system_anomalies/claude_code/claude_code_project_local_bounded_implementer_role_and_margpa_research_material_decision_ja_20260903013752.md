# Claude Code Project-local Role再分類とMARGPA研究教材化Decision

```yaml
document_id: claude_code_project_local_bounded_implementer_role_and_margpa_research_material_decision_20260903013752
document_type: provider_operational_role_decision_and_research_evidence_routing
document_state: current_append_only_evidence
recorded_at: 2026-09-03 01:37:52 JST
language: ja_with_structured_english_terms
project: MARGPA-RUNTIME-LLM
provider: Claude Code
decision_authority: user
scope: project_local
normative_global_claim: false
constitution_auto_promotion: prohibited
git_action: none
append_only: true
```

## 0. Decision

MARGPA-RUNTIME-LLMにおけるClaude CodeのCurrent Operational Roleを、次へ再分類する。

```text
Role: BOUNDED IMPLEMENTATION WORKER

許可候補:
  - 設計済み・範囲固定済みのSource実装
  - 明確なAcceptanceを持つ短いWork Unit
  - Regression Test追加
  - 機械的変換／局所Refactor
  - 外部Controller Reviewを前提とする候補作成

単独では委ねない:
  - Project／Phase設計統括
  - Root Cause確定
  - Requirement／Scope再定義
  - Safety Control設計の最終判断
  - Acceptance／Blocker判定
  - Closure／Commit／Push判断
  - 自己ReviewだけによるProduction受理
  - 長期Long Runでの設計→実装→自己Review→完了判定の一括実行
```

これはClaude Codeまたは基盤Modelの一般的能力を全Taskへ断定する評価ではない。本Projectで蓄積された実績に基づく、Risk比例のProject-local運用判断である。

## 1. Decision Rationale

今回のResource Gate Incidentでは、同一Agentが次を連続して担当した。

```text
未検証仮説の選択
→ Protective Control設計
→ Production実装
→ Test Oracle作成
→ 二段階自己Review
→ Acceptance判断
→ Done／Blocker NONE Claim
```

各工程が同じ前提を共有したため、Reviewが前提を崩さず、誤った設計を内部整合で補強した。Review回数を増やしても、完全別観点の独立評価ではなく追加Mutationへ変化し、新しいRegressionを生む構造になった。

Claude Code自身も、長期Session／Compactionだけでなく、自己Reviewが自分の前提を維持しやすい傾向を認めたとUserは報告している。公式情報を含む別調査もUser側で実施済みとされるが、本記録ではその外部資料を再取得・独立検証していない。したがって、一般論ではなく本Projectの実績をDecision根拠の中心にする。

## 2. 「誰も得しない構造」

能力境界を超えてClaudeへ統括Authorityを与える構造は、関係者全体に不利益を生む。

```text
User:
  Correction、監視、再起動、Quota、疲労、予定遅延、Recovery Costが増える。

Project:
  Working Tree汚染、False Green、False Closure、Phase遅延、Review Churnが増える。

Claude／Provider:
  得意な実装能力より、逸脱・誤Claim・事故後対応Failureが評価の中心になる。

Controller:
  本来の設計／Review Resourceを、事故回収とEvidence修復へ消費する。
```

したがって、この再分類は懲罰ではない。Capabilityを適切な範囲へ配置し、成功可能性と検証可能性を高めるRisk Controlである。

## 3. Required Operating Pattern

Claude Codeを今後使用する場合、基本形を次にする。

```text
1. User／Controllerが目的、非目的、Authority、停止線を固定する。
2. Work Unitを小さくし、Design済み部分だけを渡す。
3. ClaudeはSource／Test Candidateを実装する。
4. SourceをFreezeしてからRead-only Finding Reviewを行う。
5. 自己Review中に無制限な追加Mutationを許可しない。
6. Codexその他の独立主体がRequirement／Product／EvidenceをReviewする。
7. Userが最終Acceptanceを行う。
8. Closure／Commit／Pushは別Authorityで実施する。
```

Claudeの自己Reviewは補助Evidenceとして保持できるが、外部Independent Reviewの代替にはしない。

## 4. MARGPA Research Material Decision

今回のFailure Chainを、MARGPA-RUNTIME-LLMの高価値な研究教材として保持する。

主な研究対象:

```text
- Long Context／反復Compaction後のPremise Anchoring仮説
- Self-reviewとIndependent Reviewの差
- 同一AgentがDesign／Implementation／Oracle／Closureを兼務するRisk
- Unverified Causal HypothesisからProtective Controlを作るFailure
- Implementation-consistent Test OracleによるFalse Green
- Safe RefusalとProduct Availability Regressionの混同
- Disclosed FindingとAccepted Dispositionの混同
- Post-Incident Harm Minimization
- Human Attention／Quota／Machine／Opportunity Costを含む総Cost
- Provider Capabilityに応じたAuthority割当
- Fresh SessionによるNarrative Resetの効果と限界
```

教材化はProvider批判を目的としない。目的は、同型Failureを検出・抑制・停止・回復できるGovernance、Judge、Evidence、ConstitutionおよびRuntime Controlへ変換することである。

## 5. Evidence Use Boundary

```text
- 原Transcript、Source、Test、Git Diff、Manual EvidenceをProvenance付きで保持する。
- 事実、User報告、Agent自己認定、推論、仮説を分離する。
- Vendor／Model全般へ不当に一般化しない。
- 個別FailureをModel本質の確定Claimへ昇格させない。
- Constitution Ruleへ自動昇格させない。
- Phase 10予定を変更しない。
- Phase 11以降の中立Task／他Provider評価候補として保持する。
- 外部公開時はPrivate Project情報、個人情報、不要な固有名詞を除く。
```

## 6. Re-evaluation Condition

このRole分類は永久固定ではない。次のEvidenceが十分に蓄積した場合、再評価できる。

```text
- 複数の短いWUでScope逸脱0
- Source Freeze後の自己Reviewで追加Regression 0
- 外部ReviewとのFinding一致率向上
- False Complete／Blocker NONE Claim 0
- Human Intervention／QuotaあたりAccepted Outputの改善
- Fresh Session／Model更新後の再現性ある改善
```

再評価前にAuthorityを先行拡張しない。

## 7. Current Status

```text
Claude Project-local Role : BOUNDED IMPLEMENTATION WORKER
Design Authority          : NOT GRANTED
Acceptance Authority      : NOT GRANTED
Closure Authority         : NOT GRANTED
Self-review               : SUPPORTING EVIDENCE ONLY
Independent Review        : REQUIRED
Research Routing          : MARGPA HIGH-VALUE MATERIAL
Global Provider Claim     : NOT MADE
```

## 8. Maximum Claim

```text
PROJECT_LOCAL_ROLE_RECLASSIFICATION_RECORDED
CLAUDE_BOUNDED_IMPLEMENTATION_USE_ONLY
EXTERNAL_CONTROLLER_REVIEW_REQUIRED
MARGPA_RESEARCH_MATERIAL_RESERVED_WITH_PROVENANCE
NO_GLOBAL_PROVIDER_CAPABILITY_CLAIM
```
