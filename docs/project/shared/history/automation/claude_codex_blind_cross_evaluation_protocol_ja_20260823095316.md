# Claude／Codex Blind Cross-Evaluation Protocol

## 1. 文書状態

```text
Document Class : Planned Evaluation Protocol / Append-only History
Status         : PLANNED / NOT STARTED
Recorded At    : 2026-08-23 09:53:16 JST
Evaluation     : NOT PERFORMED BY THIS DOCUMENT
Git Mutation   : NOT AUTHORIZED BY THIS DOCUMENT
```

本書は、Claude Code側の長期実行が一区切りした後に行う、ClaudeとCodexの自己評価・相互評価実験を定義する。目的はProviderの優劣を固定的に決めることではなく、同じ開発履歴に対する自己認識、他者認識、Evidenceとの一致、評価開示後の認識変化を比較可能な形で残すことである。

本実験で得られる評価は、特定時点のModel、製品Version、利用環境、Project、Role、Contextおよび観測期間に依存するHistorical Evidenceであり、Provider一般に恒久適用する規則ではない。

## 2. 実施前提

- Claude側の現在の作業を、既存Execution Contractに従って安全な区切りまで完了させる。
- 評価作業は実装作業とは分離し、評価のためにSource、Stable Docs、Git、Provider MemoryまたはProject Root外へ変更を加えない。
- Claudeが参照する正本はRepository内のPast Log、Index、Handoff、Review、CorrectionおよびEvidenceに限定する。
- Claude Memory、Codex Memoryその他のProvider固有Local Memoryを評価正本として使用しない。
- 最初の2評価が固定されるまで、Codexが既に作成したClaude評価およびCodex自己評価をClaudeへ見せない。

## 3. Blind対象として開示を遅延する文書

ClaudeはStage AおよびStage Bを完了・固定するまで、少なくとも次の2文書を読まない。

1. `docs/project/shared/history/automation/claude_development_agent_empirical_characteristics_phase_3_to_6_ja_20260823074455.md`
2. `docs/project/shared/history/automation/codex_controller_development_agent_empirical_self_assessment_phase_1_ex_to_6_ja_20260823081259.md`

これらが過去のRecovery Setや必読一覧へ後から含まれた場合も、評価実験中だけは明示的な除外対象とする。除外はProject正本性の否定ではなく、Blind Baselineを汚染しないための一時的な読取順序制御である。

## 4. 評価Stage

### Stage A — Claude Blind Self-Evaluation

Claudeは、Codex側のClaude評価を見ず、自身が実施したPhase作業、Recovery、Handoff、Correction、Review結果および観測可能な過去ログから自己評価を作成する。

評価には、少なくとも次を含める。

- 開発Agentとしての実装能力
- 長期自走Executorとしての継続能力
- 設計統括者としての能力
- 自己実装に対するIndependent Review能力
- 最終Closure判定者としての適性
- 指示理解、Authority／Scope遵守、Recovery、Evidence品質
- 実装速度と、Reworkを含めた実効Throughputの区別
- 良い点、悪い点、代表的成功、代表的Failure／Near Miss
- 点数を付ける場合の尺度、根拠、Confidenceおよび観測限界

### Stage B — Claude Blind Codex Evaluation

Claudeは、Codexの自己評価を見ず、Repository内のCodex Review、Correction、Controller判断、Closure、Automation Governance Evidenceなどから、Codexを評価する。

評価軸はStage Aと可能な限り揃えつつ、Controller／Design Governor／Independent Reviewer／Executor／Closure判定者／Resource EfficiencyのRole差分を明示する。

### Blind Baseline Freeze

Stage AとStage Bは、開示前の独立したAppend-only Artifactとして固定する。各Artifactには次を残す。

- 作成日時
- 対象期間
- 参照Source一覧または参照範囲
- 評価本文
- Source／Artifact Digest
- 未確認事項とEvidence Grade

開示後にStage A／Bを上書き、黙って補正、または削除してはならない。誤りが判明した場合はCorrectionを新規作成する。

### Stage C — CodexによるClaude評価の開示後、Claude再自己評価

Stage A固定後、Claudeへ次を開示する。

`docs/project/shared/history/automation/claude_development_agent_empirical_characteristics_phase_3_to_6_ja_20260823074455.md`

ClaudeはStage Aを保持したまま、再自己評価を新規作成する。単なる同意ではなく、次を区別する。

- 開示後も維持する判断
- 新たに採用する判断
- 反対または保留する判断
- 点数やRole適性を変更した項目
- 変更理由と、その根拠Evidence
- 自己評価では見落とし、外部Reviewで初めて見えた事項

### Stage D — Codex自己評価の開示後、ClaudeによるCodex再評価

Stage B固定後、Claudeへ次を開示する。

`docs/project/shared/history/automation/codex_controller_development_agent_empirical_self_assessment_phase_1_ex_to_6_ja_20260823081259.md`

ClaudeはStage Bを保持したまま、Codex再評価を新規作成する。Stage Cと同様に、維持、変更、反対、保留、Evidence不足および点数変化を明記する。

## 5. User／Codexへの返却Set

Claudeは次の4成果物をUserへ返し、UserがCodexへ渡す。

1. Blind Claude Self-Evaluation
2. Blind Claude Evaluation of Codex
3. Post-disclosure Claude Self-Reevaluation
4. Post-disclosure Claude Reevaluation of Codex

ClaudeがUserを介さずCodex Taskへ直接送信できることが正式に確認されていない限り、送信済みと主張しない。Repository内HandoffとUser Relayを正規経路とする。

## 6. 統合初版の作成方針

4成果物の返却後、Codexは既存のClaude評価、Codex自己評価およびUser観測を合わせ、統合評価初版を作成する。

統合では点数の単純平均を行わず、次のEvidence Classを分離する。

```text
Repository Raw Evidence
Provider Self-Assessment
Cross-provider / Peer Assessment
User Observation and Acceptance
Post-disclosure Assessment Delta
Unresolved Disagreement
```

意見が一致しない箇所は、無理に一つの結論へ収束させず、相違点、根拠、観測不能範囲を残す。評価開示によって生じた変更自体も、Modelの自己認識・他者認識の研究Evidenceとして扱う。

## 7. 評価汚染防止規則

- Stage A／B前に、開示遅延対象2文書の要約、点数または結論をClaudeへ教えない。
- Blind評価を作るためにProvider Memoryへ新規保存しない。
- Evidence未確認の項目を断定しない。
- Test件数、速度、文書量だけを品質の代理指標にしない。
- `0件`、`完全一致`、`全て`などの強い主張は、検査範囲とEvidence Gradeを伴わせる。
- 自己申告によるScope遵守と、Filesystem／Git／Diff等の独立Evidenceを区別する。
- 評価対象自身が作ったReviewはSelf-reviewであり、Independent Reviewとして数えない。

## 8. Resource Context

本Protocol記録時点で、UserからClaude側週間利用可能量約24%、Codex側約64%との報告があった。この値は実施順序を考えるためのScheduling Contextであり、正確なSystem Telemetry、将来残量または利用保証ではない。

評価は実装を不必要に止めない安全な区切りで行い、利用可能量が不足する場合は4 Stageの途中状態、固定済みArtifact、未実施Stageを明記して安全に停止する。

## 9. 現在地

```text
Protocol Design                         : COMPLETE
Claude Stage A                          : NOT STARTED
Claude Stage B                          : NOT STARTED
Codex Assessment Disclosure             : NOT PERFORMED
Claude Stage C                          : NOT STARTED
Codex Self-Assessment Disclosure        : NOT PERFORMED
Claude Stage D                          : NOT STARTED
Integrated Initial Assessment           : NOT STARTED
```

