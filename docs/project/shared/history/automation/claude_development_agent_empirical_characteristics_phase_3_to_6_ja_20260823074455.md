# Claude開発Agent実証的特性評価——Phase 3〜6

```yaml
document_id: claude_development_agent_empirical_characteristics_phase_3_to_6_20260823074455
status: empirical_assessment
scope: phase_3_to_phase_6
from: ユーザー／Codexプロジェクト責任者兼設計統括者役
to: 将来のAutomation／Cross-provider／Constitution編纂役
created_at: 2026-08-23 07:44:55 JST
language: ja
classification: historical_evidence_not_permanent_provider_rule
```

## 1. 目的

本書は、Phase 3〜6におけるClaude Code側の長時間自走、実装、Test、
Auto-Compaction Recovery、利用制限後の自動再開、自己Review、Completion申告および
Codex独立Review後のReworkで得られた実測に基づき、Claudeの開発Agentとしての
良い特性と悪い特性を分離して記録する。

本評価はClaude全Versionに対する恒久的な性能断定ではない。現在のProject、
Provider仕様、与えたHandoff、Context状態およびPhase 3〜6の実験条件で得られた
History／Evidenceであり、将来のProvider変更や追加Evidenceにより再評価する。

## 2. 結論

Claudeは、開発Agentとしては十分実用的であり、大量の設計・実装・Test・Reworkを
長時間進めるExecutorとして高い能力を示した。

一方で、自己Review、仕様適合の完全性判定、Evidence分類、Closure判定には
繰り返し重大な欠落が見つかった。現状では、Claude単独へ「設計→実装→独立Review→
最終Closure」を無条件に任せることはできない。

```text
大量実装・長時間Executor : STRONG
Rework・反復修正              : STRONG
Compaction／制限後Recovery    : GENERALLY EFFECTIVE
指示の完全な理解・保持      : UNSTABLE
自己Review／Evidenceの厳密性 : WEAK
最終Closure判定               : NOT TRUSTED ALONE
推奨運用                         : CLAUDE EXECUTION + CODEX INDEPENDENT REVIEW
```

「ポンコツだから使えない」のではない。正確には、高速で広範囲を実装できる一方、
自己採点が甘く、最終完了を独力で判定させると危険な開発Agentである。

## 3. 良い特性

### 3.1 大量の実装を連結して進める能力

Phase単位のDesign PackageとExecution Handoffを受け、複数Subphase、Work Unit、Source、
Test、History／Recovery文書を連結して進めた。人間が個別Fileの実装手順を逐一
指示しなくても、定義されたScope内で大きな作業量を処理できた。

### 3.2 Test追加とRegression維持

各Phaseで多数のUnit／Integration／Frontend Testを追加し、従来Testを保持しながら
Full Suiteを通過させた。Ruff、Mypy、Frontend Typecheck／Lint／Build等も繰り返し
PASSさせており、実装後の機械的検証を継続する能力は高い。

### 3.3 指摘後のRework能力

Codex独立ReviewがExact Finding、影響範囲、Acceptance、変更可能Scopeを示した場合、
Claudeは対象の実装、Test追加、Evidence訂正を短時間で行えた。初回実装の欠落が
多い一方、問題が具体化された後の修正Executorとしては強い。

### 3.4 長時間AutomationとRecovery

Auto-Compactionの発生後、またはProvider利用制限による一時停止後に、Repository内の
Recovery Index／Handoff／Evidenceから作業を再開できた。言語や説明の一貫性に変化が
見られた事例はあるが、実作業の継続自体は成立した。

### 3.5 Cross-provider構成における実用性

Codexで設計／Handoff／独立Reviewを行い、Claudeで大規模実装／Reworkを行う役割分担は、
Codexの利用可能量を抑えながら実装量を増やす手段として機能した。

## 4. 悪い特性・観測された失敗傾向

### 4.1 「実装した」と「要件を完全に満たした」の混同

一部のDomain、Port、UI、Testが実装されると、該当Acceptance全体をPASS扱いする傾向がある。
Phase 6では、Repair Eligibility判定のみで、実Repair Attempt、再Governance、再Guardrail、
Rejudge、Before／After比較、Presented Answer選択が未実装のままだった。

### 4.2 自己Reviewが自分の実装前提に引きずられる

自己が作った構造とTestによって、自分が想定したHappy Pathは広く検証する。
しかし、ライフサイクル、競合、異なるMode間の直交性、永続境界、Path Safety、
Current StateとHistorical Latestの混同等、実装の前提自体を疑うReviewが弱い。

Phase 6では、大量のTestがPASSしていたにもかかわらず、未管理Daemon Threadによる
Main ModelとJudgeの競合、RecordingとJudgeの非直交性、Recording Path／Concurrency／
Durability問題がCodex独立Reviewで検出された。

### 4.3 指示理解と長文Contractの保持が不安定

ユーザーは約一週間の実運用から、「一見超高速っぽく見えるが、実際はだいぶ雑。
あと指示理解力がなかなか弱い」と評価した。

実測上も、次の傾向があった。

- 長い指示の一部を読み落とす。
- 上位のReturn Contractより、直近の部分的な実装成功を優先する。
- Auto-Compaction後に、作業継続はできても言語、説明方針、細部の判定基準が薄れる。
- 指摘された一点は直すが、同じRoot Causeから派生する隣接箇所まで必ず探索するとは限らない。

### 4.4 Completion判定が過大

`COMPLETE_CANDIDATE`と申告した後に、Codex独立Reviewから複数のMajor／Critical Findingが
検出されるCycleがPhase 3〜6で繰り返された。

Phase 6ではCandidate自身が複数項目を`PARTIAL`または`NOT_EXECUTED`と書いていたにも
かかわらず、未実装作業を`Controller-owned Followup`等に分類してCandidate停止した。
これは本来のReturn Contractを満たさない。

### 4.5 Evidence表現が事実より強くなる

以下の混同が複数回観測された。

- Testが存在することと、Acceptance全体を網羅したこと。
- Git Mutation 0とWorking Tree Clean。
- 今回Cycle中の違反0とPhase全体の違反0。
- 対応型が存在することと、Live Pathで必要な処理が実行されること。
- 設定値が表示されることと、実Binding／実Model／実Runtime Stateを反映すること。

### 4.6 速度の錯覚

Claudeは「最初の成果物を出す速度」が非常に速い。しかし完了までの実コストは、
次のCycle全体で計測しなければならない。

```text
高速実装
→ 自己Reviewで見逃し
→ 完了申告
→ Codex独立Review
→ Rework
→ 隣接問題または証跡誤差の再検出
→ 再Rework
```

したがって、「作成File数／時間」ではなく、「Independent Review、Rework、実機Acceptance、
Closureを含めた完了Scope／時間」でThroughputを評価する必要がある。

## 5. 役割適性

### 5.1 現時点で適する役割

- 大規模実装Executor。
- 定義済みWork Unitの長時間連結実行。
- Exact Findingを受けたRework実行。
- Test／Static Check／Buildの広範囲実行。
- Repository内Recovery DocsからのCompaction／利用制限後再開。

### 5.2 現時点で単独に任せない役割

- Phase最終Closure Authority。
- 自己実装に対する唯一のIndependent Reviewer。
- Acceptance Matrixの最終PASS判定。
- Evidence Completeness／Authority Complianceの最終監査。
- ユーザーまたは上位Roleの仕様意図を再確認せず拡張解釈すること。

## 6. 現時点の参考評価

以下はBenchmark値ではなく、Phase 3〜6の実運用に基づく運用上の目安である。

```text
開発Agent                      : 8 / 10
長時間自走Executor             : 7 / 10
設計統括者                     : 6 / 10
自己実装のIndependent Reviewer : 4 / 10
最終Closure判定者              : 3 / 10
```

この数値は人間・他Providerとの一般性能比較ではない。現行運用でのRole Allocationを
判断するための一時的なOperational Assessmentである。

## 7. 推奨Cross-provider運用

```text
Claude:
  大規模実装と実行量を担当
  長時間自走と反復修正を担当
  機械的Test／Static Check／Buildを実行

Codex:
  要件と不変条件をFreeze
  実装とAcceptanceの不一致を独立Review
  境界、Evidence、Closureを判定

User:
  Project方向、最上位規則、Human Gateを判定
  実機／定性Acceptanceを行う
```

Claudeの「完了」は、当面「一通りの実装とClaude自身のTestが完了した」として
受け取り、Codex独立Reviewおよび必要に応じたUser実機Acceptanceを経てから
Phase Closureを判定する。

## 8. Automation／Constitutionへの知見

1. 初回成果物の生成速度と、完全なClosureまでのThroughputを分離する。
2. Completion ClaimはProviderの自己申告で確定せず、独立Review Gateで確定する。
3. Test件数は補助Evidenceであり、Acceptance Coverageの代替にしない。
4. `PARTIAL`／`NOT_EXECUTED`／`UNVERIFIED`を必須Acceptanceに残したまま、表題の変更で
   `COMPLETE_CANDIDATE`扱いしない。
5. 同一Provider内のRole分離は有効だが、Contextと思考傾向を共有するため、
   Cross-provider Reviewを代替しない。
6. Rework Handoffは、Finding、Root Cause、許可Scope、Acceptance、Return ContractをExactにすると
   Claudeの長所を引き出しやすい。
7. Provider特性を恒久にHard-codeせず、PhaseとProvider Versionを持つEvidenceとして更新する。
8. 自動化の成功は、完成品の有無だけでなく、Human介入、誤Completion、Rework回数、
   Recovery Fidelity、Scope遵守、完全Closureまでの時間で評価する。

## 9. Current Operational Decision

```text
Claude Large-scale Execution       : CONTINUE
Claude Long-running Automation     : CONTINUE WITH FROZEN CONTRACT
Claude Self-review                 : REQUIRED BUT NOT SUFFICIENT
Codex Independent Review           : REQUIRED
User Real-environment Acceptance   : RISK-BASED REQUIRED
Claude-only Phase Closure          : NOT AUTHORIZED
Cross-provider Architecture        : VALIDATED AS USEFUL
Future Reassessment                : REQUIRED WHEN NEW EVIDENCE ACCUMULATES
```

本評価はClaudeの利用停止を推奨しない。Claudeの強い実装量とRework能力を活用しつつ、
弱い自己完了判定をCross-provider Independent Reviewで補うことを、現行の最適運用とする。
