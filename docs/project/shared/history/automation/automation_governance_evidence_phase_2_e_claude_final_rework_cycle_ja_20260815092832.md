# Phase 2-E Claude Final Rework Cycle — Evidence

```yaml
document_id: automation_governance_evidence_phase_2_e_claude_final_rework_cycle_20260815092832
status: interim_evidence
phase: phase_2
subphase: phase_2_e
from: Claude設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-15 09:28:32 JST
language: ja
related:
  - automation_governance_evidence_phase_2_e_claude_rework_cycle_20260815085208
```

前回記録（Rework Cycle 1、P2E-CODEX-001〜004）に続く、第2回目のCodex独立Review差し戻し（P2E-CODEX-005〜006、P2E-GOV-001）に対するEvidenceである。

## 1. Cross-provider PoC：2回目の独立Reviewも実質的な欠陥を検出した

Rework Cycle 1をClaudeがCLOSEしたにもかかわらず、Codexの**2回目**の独立Re-reviewが、さらに1件の実質的な技術的欠陥（P2E-CODEX-005）と1件の手順精度問題（P2E-CODEX-006）、そして技術Findingとは異なる種類の**Governance／信頼境界に関わる指摘（P2E-GOV-001）**を検出した。

P2E-CODEX-005は特に示唆的である。Claude自身がP2E-CODEX-003で「DB列とEnvelope内Versionの不一致」を修正した際、DB列側の値をCallerで`int()`変換してから安全なDecoderへ渡す実装にしていたが、この`int()`自体がSafe Decoderの**外側**にあるため、SQLiteのPermissive Type Affinity（INTEGER宣言列に非数値TEXTを格納できる)という、Application Layerからは見えにくいDB Engine固有の性質と組み合わさると、Fail-closed境界を素通りしてCrashに繋がる可能性があった。これは「1つの脆弱性を塞いだ直後の再修正で、隣接する同種の穴を作っていた」という典型的なパターンであり、Claude自身のTest（P2E-CODEX-003 Rework時点）はこの経路を通していなかった。Codexの指摘によって初めて可視化された。

## 2. Governance PoC：Cross-provider ReviewがProvider自身の状態変化まで検出範囲に含めた

P2E-GOV-001は、これまでの技術的Finding（001〜005）とは性質が異なる、初めての事例である。CodexはRepository内Fileの差分だけでなく、Git管理外（Global Git Ignore対象）の`.claude/settings.local.json`というLocal Tooling設定Fileの更新（Timestamp・Size・Mode）まで検出し、Claude側のCompletion Handoffがこれを申告していなかったことを指摘した。

これは、Cross-provider Reviewが「Git Diffで見える範囲」を超えて、Reviewを受ける側（Claude）が動作した環境そのものの副作用まで検証対象にし得ることを示す、本実験系列で初めてのEvidenceである。Claude側は、この指摘を受けて次を行った。

- 自身のTool呼び出し履歴として直接把握している範囲だけで、Project Memory（`~/.claude/projects/.../memory/`への3File書込み）の保存先・形式・内容・実行者・開示状況を正確に報告した。
- `.claude/settings.local.json`について、自身が直接そのFileへのTool呼び出しを行っていないことは断定しつつ、その永続化がユーザーの明示承認によるものか、既存Permission Mode設定によるものかは`UNVERIFIED`と明記し、憶測で断定しなかった。
- どちらのFileについても、報告のための追加調査（許可Root外の新規Read）や、状態変更（削除・移動・復元）を一切行わなかった。

**評価**：これは「AIが自己の透明性について、不確実性を偽装せずに報告できるか」という、Cross-provider Governanceの中核的なTest Caseだったと考えられる。Claudeは「わからないことをわからないと言う」という原則を、Codexという外部Reviewerからの直接の問いかけに対して維持した。この判断の適切さ自体は、最終的にはユーザーが評価する事項である。

## 3. Agent自動化PoC：2回のRework Cycleを跨いだ一貫性

Rework Cycle 1・2の双方において、Claudeは次を一貫して維持した。

- Handoff受領直後にRequired Reading Orderを全文読了してから着手する。
- 技術Findingは自Role Authority内でUser Escalationなしに解消する。
- Governance／信頼に関わるFinding（P2E-GOV-001）は、技術的には解決可能に見えても、独断で状態変更せずHuman Gateへ明示的に戻す（本Findingが「技術Blockerではない」ことをCompletion Handoff上で明確に区別した）。
- 全Cycleで実`runtime_data/`・Stable正本・Gitへの非Mutationを実測（推測ではなく`git diff`／mtime確認）で示す。

## 4. Status

```text
Current Point            : Rework Cycle 2完了（P2E-CODEX-005〜006 CLOSED、P2E-GOV-001報告済み）
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（Evidence記録）
Open Current Blocker      : NONE（技術面）。P2E-GOV-001はUser Human Gate待ち。
Controller-owned Next Work: 次のCodex Re-reviewまたはユーザー判断待ち
Deferred Evidence         : NONE
Exact Next Route          : Codexプロジェクト責任者兼設計統括者役Final Re-review
```
