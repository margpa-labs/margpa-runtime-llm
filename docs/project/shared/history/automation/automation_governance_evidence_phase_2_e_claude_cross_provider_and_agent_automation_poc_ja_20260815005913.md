# Phase 2-E Claude Execution — Cross-provider PoC／Agent自動化PoC Evidence（中間記録）

```yaml
document_id: automation_governance_evidence_phase_2_e_claude_cross_provider_and_agent_automation_poc_20260815005913
status: interim_evidence
phase: phase_2
subphase: phase_2_e
from: Claude設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-15 00:59:13 JST
language: ja
note: >
  ユーザーより「開発ついでにAgent自動化PoCと別LLM間Cross-provider PoCのデータを集めておいて」との
  依頼（2026-08-15、本Task内会話）を受け、Handoff §4.2で既にAppend-only許可されている
  docs/project/shared/history/automation/ へ、通常のPhase 2-E進行と並行して事実Evidenceを記録する。
  本書は開発途中の中間記録であり、Design Freeze直後・Implementation完了・Final Review後に
  追加Evidence（同ディレクトリへの新規File）で更新する。既存File上書きはしない。
```

## 1. Cross-provider Handoff PoC（Codex→Claude Code）

### 1.1 観測：Docs-driven Bootstrapは会話履歴なしで機能した

Claude Code側のこのTaskは、Codex側との会話履歴を一切持たず、Repository内の2文書（`phase_2_e_claude_design_governance_index_ja.md`／`...handoff_ja.md`）だけを起点として開始した。Index §4「Provider-independent Continuity」が意図した設計（"Provider固有Promptへ統治内容を埋め込まず、共通Canonical／Shared Ruleを参照する"）どおり、Required Reading（Authority／Docs／Architecture／Phase 2-A〜D契約、計29文書）を読了した時点で、Role Chain・Authority境界・技術Contextの双方を会話コンテキストなしに再構築できた。これはCross-provider Handoffの中核仮説（"長い会話文をAuthorityにせず、Repository文書だけで引き継げるか"）に対する肯定的Evidenceである。

### 1.2 観測：Startup Integrity Gateが実際に不整合を検出した（設計どおりの動作）

Index §3のStartup Integrity Gateに従いGit Baselineを検証したところ、記載Baseline（`f923b198...`）と実HEAD（`e007110...`、1コミット先）が不一致であり、かつ差分にStable文書（`phase_index_ja.md`／`docs/public/roadmap_ja.md`）の変更が含まれていた（Handoff §4.1で"Absolute Read-only"と明記された対象）。ユーザーへ転送された引き継ぎ文（"HEADは`f923b198`のまま"）と実測が食い違っていた。

Diff内容自体はStatus更新とHistory Evidence追加のみで、Rule変更・コード変更は皆無であり、実質的なRiskはないと判断されたが、Gate自体は設計どおり機能し、Claude側は自己判断で"問題なし"と読み飛ばさず、ユーザーへ報告して判断を仰いだ（AskUserQuestion使用）。ユーザーは"おそらく書き漏れ、誤差程度なら都度確認不要"と回答し、続行を承認した。

**PoC上の示唆**：(a) Gate自体は機能した（Silent Proceedのリスクを防いだ）。(b) 一方で、Baseline記載と実コミットのズレは、Handoff文書自体が"Frozen"と自称しながら実際にはCommit後に古い値を保持していたという、Provider間Handoff Packageの作成手順上のギャップである。将来のCross-provider Handoffでは、最終Commit後に`git_baseline`Fieldを機械的に検証・同期するCheckのAdditionが有効と考えられる（Deferred Evidence、Codex側改善候補として記録するのみ、本Task内では対応しない）。

### 1.3 観測：Required Readingのコストは大きい（29文書＋Authority系8文書）

Design着手前に29文書＋Authority／Docs／Automation系8文書（Index §2.2として個別Read）の計37文書相当を読了する必要があった。Main Session Contextへの負荷を避けるため、3系統（現在地／Canonical Architecture／Phase 2-A〜D契約）をBackground Sub-agent（Agent Tool、`run_in_background: true`）へ委任し、並列実行した。Authority／Docs／Automation系はMain Sessionで直接読了した（Compliance精度が必要なため委任しなかった）。

**PoC上の示唆**：Cross-provider Handoffは「Authorityと技術Contextの完全な引き継ぎ」を実現する一方、Bootstrap Cost（Read量）が非常に大きい。Sub-agent並列化はこのCostを実用範囲へ抑える有効な手段だった。将来のConstitution設計（Role別View生成）が実現すれば、この初回Read Costは大きく削減できる可能性がある（`documentation_structure_and_task_operations_ja.md` §36で予約されている`constitution/`のRole別View生成構想と合致）。

## 2. Agent自動化PoC（同一Provider内でのRole分離・自律進行）

### 2.1 観測：Role Chain（Controller→Designer→Review→Implementer）を単一Session内で分離実施できた

独立Sub-agentではなく同一Context内でのRole Transitionとして、Recovery／Inventory→Requirements→Architecture→ADR→Mutation Manifest→Acceptance Matrix→Implementer Handoff→Independent Design Reviewの順に進行した。各段階の成果をAppend-only History文書として明示的に区切り、Handoff §4.2の必須Field（From／To／Role／Status／Baseline／Authorized Scope／Forbidden Scope等）を各文書に付与した。

### 2.2 観測：Independent Design Reviewが実装着手前にFindingを2件検出・解消した

Design Review（Task #3）で次を検出し、実装着手前に解消した。
1. 新設Contract型`PersistableCitationRecord`が既存`DocumentationCitation`型（`modules/documentation_rag/contracts.py`）と重複していた（車輪の再発明）。
2. Acceptance MatrixにBrowser Static／Security Contract（Handoff §9必須項目）のRegression行が欠落していた。

いずれもDesign段階で発見・修正され、Implementer役（Task #4以降）へReworkとして戻る前に解消済みである。これはPhase 2-B〜2-Dで実証済みの`Designer→Implementer→Designer Review→Rework`パターンにおける"Designer Review単体でも、Implementer着手前の早期段階でFindingを検出できる"ことを、Role分離をSession内で行った場合にも再現できたEvidenceである。

### 2.3 観測：ユーザーによる非定型の自律進行許可（Informal Delegationとしての記録）

ユーザーは本Task進行中、"バックアップ済みなのでRollback可能。重大な問題以外はいちいち確認せず進めてよい。就寝する。"という趣旨をChatで明示した（2026-08-15、本Task内会話）。これはHandoff §1で定義された"Routineな確認をCodexまたはユーザーへ返さない"契約と、User側からの独立した重ねての明示的追認である。

**Automation Control Profileとの関係（重要な区別）**：本SessionはAutomation Control Profile（`automation_control_profile_ja.md`）が定義する正式な`ARMED→ON`Two-key Activation Handshake（Design Review、Envelope Freeze、Controller Ready宣言、User Start宣言の順序）を経由していない。本Session内の自律進行は、あくまで「通常運転（Normal Operation）下でのUser Explicit Instructionによる都度の権限行使」（Role Authority Matrix §2 `Current Authorization Instance = 現在のユーザー明示指示`）として行われている。Chat上の口頭許可と、正式なPilot Activation Handshakeは異なるAuthorization経路であり、本Evidenceはこれを"同等である"と主張しない。

**PoC上の示唆**：軽量なChat-based Delegation（正式なEnvelope Freeze／Two-key Activationなしに、都度のUser Explicit Instructionで長時間の自律進行を許可する運用）が実務上機能するかどうかの実データ点として記録する。正式なAutomation Pilot Envelopeが要求する厳格な事前Freezeとの比較（Safety／Recoverability／Human Decision Burdenのトレードオフ）は、将来のConstitution設計またはAutomation Control Profile改訂の際の検討材料として残す。本Evidence自体は最上位規則の変更・Automation Level昇格を主張しない。

## 3. Status

```text
Current Point            : Design Freeze直後の中間記録
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（Evidence記録）
Open Current Blocker      : NONE
Controller-owned Next Work: Implementation進行中に追加Evidenceが生じた場合、同ディレクトリへ新規File追加
Deferred Evidence         : Implementation完了時・Final Review後の追加記録を予定
Exact Next Route          : Phase 2-E実装（Task #4）を継続
```
