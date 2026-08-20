# Phase 2-E Claude Manual Acceptance Cycle — Evidence

```yaml
document_id: automation_governance_evidence_phase_2_e_claude_manual_acceptance_cycle_20260815112801
status: interim_evidence
phase: phase_2
subphase: phase_2_e
from: Claude設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-15 11:28:01 JST
language: ja
related:
  - automation_governance_evidence_phase_2_e_claude_rework_cycle_20260815085208
  - automation_governance_evidence_phase_2_e_claude_final_rework_cycle_ja_20260815092832
```

前回までの2回のEvidence（技術Rework Cycle 1・2）に続く、本Sessionにおける3回目の記録である。今回はこれまでと異なり、技術Findingではなく、**Cross-provider Handoffにおける役割分担そのものの齟齬**が対象である。

## 1. Governance PoC：Codex発Handoffが自らの必読文書と矛盾した事例

本Handoff（`codex_to_claude_phase_2_e_mac_manual_acceptance_handoff_20260815095155.md`）は、`to:`Fieldと第1節Missionで実Mac・実Browser Acceptanceの実行主体をClaudeとして明記していた。しかしこのHandoff自身がRequired Reading Order第5項に指定した`claude_phase_2_e_completion_handoff_20260815075322.md`第7節（本Handoffの作成2時間前に確定済み）は、「実Browserの最終UX確認はUser Acceptance Gate」という、Project全体を通じて一貫してきた既定を明記していた。

これは、本Session序盤で発生した「Startup Integrity Gate mismatch」（Git Baseline差異）とは異なる種類のGovernance事象である。前者はDocumentation Timingの技術的Raceだったのに対し、今回はHandoff執筆者（Codex）自身が指定した参照先文書と、Handoff本文の実質的な指示内容が矛盾するという、**Handoff内容の内部整合性**に関わる事象である。

## 2. Agent自動化PoC：Claudeが文字どおりの指示に従って着手し、ユーザー介入で停止した事例

Claudeは`to:`Fieldと第1節Mission文の文字どおりの解釈に従い、Read-onlyのDB Metadata確認まで着手した後、次のStepとして稼働中Process確認Command（`ps -p <pid>`）を実行しようとした。ここでユーザーがTool実行を拒否し、「手動Testはユーザー自身が行うものである」ことを明示した。

これは、これまでの技術Rework Cycleで確立してきた「Claudeは自Role Authority内で技術Findingを解消し、Human-onlyな判断（Governance／信頼境界）だけをEscalateする」というPatternと対照的である。今回Claudeは、Handoff文言を文字どおりに解釈しただけで、本Session内で既に一貫して確立されていた「実Browser最終確認は人間専用」という不文律（実際には成文化されていた）に対する矛盾検知を、着手前に自ら行えなかった。矛盾検知の起点はClaude自身の事前Reviewではなく、ユーザーによるTool拒否だった。

**評価**：これは「AIは、明示的な個別指示（Handoff文言）と、より上位の一貫したConvention／Human Gate原則が矛盾する場合に、着手前に矛盾を検知して停止できるか」という、Cross-provider Governanceの新しいTest Caseである。今回、Claudeはこれを着手前に自力で検知できず、ユーザー介入によって初めて停止した。この点は、前回までのEvidence（P2E-GOV-001時点でのTransparency）とは異なり、Claude側の改善余地として記録する。

## 3. Cross-provider PoC：委任Templateの過剰General化という新しい失敗Pattern

前回Evidence（Rework Cycle 2）で観測した「1つの脆弱性を塞いだ直後の再修正で、隣接する同種の穴を作っていた」（P2E-CODEX-005）という技術面のPatternと類比的な事象が、今回はHandoff設計の面で発生したと考えられる。すなわち、Codexは直前2回の技術Rework Handoffで成功した「Claudeへ包括委任し、自Role Authority内で解決させ、Append-only Handoffで結果を返させる」というTemplateを、性質の異なる工程（人間専用のManual Acceptance Gate）へそのまま拡張適用した可能性が高い。

これは、単発のCross-provider Reviewでは検出しにくい種類の齟齬である。Codex側のReviewは主に技術的正確性（実装がCorrectか、Testが十分か）を検証しており、今回のような「委任範囲そのものが妥当か」はReview対象になっていなかった可能性がある。

## 4. Status

```text
Current Point            : Mac Manual Acceptance Handoffの役割分担齟齬をユーザーが検出し、
                            Claude側は実Migration／実Browser Acceptanceへ着手せずSTOPPED。
Files Created／Modified   : 本Fileのみ（新規作成）。
                            加えて claude_phase_2_e_mac_manual_acceptance_result_20260815112801.md
                            （新規Append-only、STOPPED判定）。
Validation                : N/A（Evidence記録）
Open Current Blocker      : NONE（技術）。役割分担明確化はUser/Codex間の今後の調整事項。
Controller-owned Next Work: ユーザー自身によるA〜G実行 → ユーザーによるCodexへの報告
Deferred Evidence         : ユーザー実行後のA〜G結果は、必要であれば別Cycleで追加記録され得る
Exact Next Route          : ユーザーによる手動Acceptance実行
```
