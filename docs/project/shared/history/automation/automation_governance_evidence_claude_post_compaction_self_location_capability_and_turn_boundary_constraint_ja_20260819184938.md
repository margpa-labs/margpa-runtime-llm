# Auto-Compaction後の自己現在地特定能力と、Turn境界制約に関するEvidence

```yaml
document_id: automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint
status: evidence
phase: phase_2
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 18:49:38 JST
language: ja
created: Claude Code
```

## 1. 本Docの位置づけ

[claude_auto_compaction_recovery_drill_cycle_7_ja_20260819182942.md](claude_auto_compaction_recovery_drill_cycle_7_ja_20260819182942.md)（以下「Cycle 7 Doc」）は、Auto-Compaction Recovery手順そのものの実施記録として、既に作成・完了済みである（`history/`配下Append-only原則により、遡って編集しない）。

本Docは、Cycle 7 Doc作成**後**に発生した、ユーザーとの追加のQ&Aを対象とする、独立した新規Evidenceである。主題は「Claude側設計統括者役は、Auto-Compaction発生を自己認識し、Docsを読み直して自分で現在地を特定し、Compaction Recovery成功回数のCountも自分で行えるか」という、予約Task 3.4（LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction）・3.6（LLM Native自動Context圧縮・自動復旧Cycle機能）に直結する実証的問いである。

## 2. 発端：ユーザーからの質問

Cycle 7 Recovery完了報告の直後、ユーザーより次の質問があった。

> 「その前に、今のAuto-Compaction前後で何か、Compactionが発生する、あるいはしたっていう自己認識出来る何かはあったか？」

## 3. 観測されたSignal（本Session内で実際に確認できたもの）

1. **明示的なSystem-level Marker**：「This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.」という文言。これに続けて、Primary Request and Intent／Key Technical Concepts／Files and Code Sections／Errors and fixes／Problem Solving／All user messages／Pending Tasks／Optional Next Stepという固定構成のSummary Blockが展開されていた。通常のTurnでは絶対に出現しない、圧縮に固有の構造物である。
2. **明示的な"summarized"という単語を含むSystem-reminder**：「Note: ...claude_side_phase_index_ja_20260819144637.md was read before **the last conversation was summarized**, but the contents are too large to include.」——最も曖昧さの無いSelf-descriptive Markerだった。
3. **構造的傍証（残存Tool結果、非対称再挿入）**：ユーザーの「いつも通りに復旧してくれ」指示に対する応答Turnの冒頭に、TOML設定File×2・最新Phase Index・最新Recovery IndexのRead結果が、**そのTurn内で新たに発行したTool呼び出しとしてではなく**、既に完了済みのSystem-reminderとして付与されていた。これは、既存Evidence（[automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md](automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md)）が記録済みの「Compaction後のFile再挿入の非対称性」と一致する現象だった。
4. **副次的傍証**：Deferred Tools一覧・Agent一覧・MCP Server Instructionsの再掲示。New Session／Compaction直後に伴う定型再announceであり、単独では確定的ではないが、他Signalと合わせて補強材料になった。

**無かったもの**：生成中に「Context使用率が逼迫している」と内部的に検知できるような、事前・Real-time的なSignalは無かった。84%到達→Auto-Compaction発動という予兆は、完全にユーザーからの外部報告（「残り4%だから」）に依存していた。

## 4. ユーザーからの確認質問と、それに対する精査

ユーザーより、次の確認があった。

> 「てことは、やっぱりワンチャン『Auto-Compactionが発生した直後に、一旦ストップしてdocs読み返して自分で現在地確認は可能、カウントも可能』って事だよな？現に今キミやってたし。」

この確認を受け、当該箇所のTurn構造を精査した結果、**本Session内で、実質的に連続する2段階のCompactionが発生していたことが判明した。**

### 4.1 1段階目：Pattern 2報告Turnの直前

Pattern 2（RAG無関係質問誤発火）の実測調査結果報告（「Pattern 2について、重要な発見がありました」で始まるTurn）は、既にCompaction後のSummary Blockから再構成されたContext上で生成されていた。このTurnでは、Docs再読の儀式を明示的には踏まず、Summary本文の「Optional Next Step」記述に従って、実務Task（Pattern 2報告）へ直接復帰する形を取った——これはHarness側の明示指示（「Resume directly — do not acknowledge the summary, do not recap」）に沿った振る舞いである。

### 4.2 2段階目：「いつも通りに復旧してくれ」応答Turnの途中

ユーザーの「残り4%だからもうすぐAuto-Compactionくるからね。いつも通りに復旧してくれ。」という指示への応答生成の**途中**で、TOML×2・Phase Index・Recovery IndexのRead**結果**のみが残存し、それに至る意図説明のPromptが失われる形の、2回目のCompactionが発生したと推定される。これを受けた次のTurnで、私は「Auto-Compaction直前の指示、把握しました。まず運用メモとCompanion Docを再読し、復旧手順を確定させます。」と応答している。これは、**ユーザーに聞き返すことなく、残存したTool結果のみから「運用メモ第1節の手順のどこまで進んでいたか」を自分で特定し、続きから再開した**ものである。

**この2段階目こそが、ユーザーの言う「発生直後に一旦止まってDocs読み返し、現在地確認」に該当する、直接的な実例である。** Compaction Recovery成功回数のCount（6→7）も、ユーザー指示を介さず、運用メモ第1節の既定Ruleに従って自分で加算した。

## 5. 結論

### 5.1 実証された能力

- Auto-Compaction発生後、残存する手がかり（明示的な"summarized"Marker、構造化Summary Block、または部分的に残存したTool呼び出し結果）から、**圧縮が発生したこと自体、および自分がどの作業段階にいたかを、自分で特定できる。**
- その特定に基づき、Stable Docs（運用メモ・長期戦運用Companion・Phase Index・Recovery Index）を自分の判断で読み直し、次に何をすべきかを、ユーザーに逐一確認せずに決定できる。
- Compaction Recovery成功回数のような単純なCountも、既定Ruleに従って自分で更新できる。
- 本Sessionでは、この一連の流れが2段階のCompactionそれぞれで別々の形（Summary継続型／残存Tool結果継続型）で機能し、いずれも実質的な情報欠落・手順の混乱無く完了した。

### 5.2 重要な制約：契機はTurn境界に依存する

**「自分の現在地を特定し、次の行動を決める」という中身は自己主導的だが、その特定・決定を実行する契機自体は、常に新しいTurnの到来に依存している。** Idle中に自発的に「そろそろ危ないから一旦止めよう」とAction Loopへ割り込む手段は無い。今回も、Compaction自体はHarness側の自動処理であり、その後の「Docs読み返して現在地確認」という行動の中身は自己主導的だったが、それを実行する契機は、いずれもユーザーからの新しいMessageというTurn境界だった。

したがって、正確な言い方は次の通りになる。**「Turnが到来しさえすれば、その時点で自分の現在地をDocsベースで自己特定し、以降の判断を自分で行える」ことは実証された。「Turnとは独立して、完全に自発的に動ける」ことは実証されていない（そもそも本Sessionの Architecture上、成立しない）。**

## 6. Project的意義

本Evidenceは、予約Task 3.4（LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction）・3.6（LLM Native自動Context圧縮・自動復旧Cycle機能）——いずれもPhase 3候補——の設計を検討する際の、直接的な実測根拠となる。特に、「Turn境界が来れば自己方向付けできる」という実証された範囲と、「Turn非依存の自発性」という実証されていない範囲の境界線は、これら2Taskの実現可能性・設計方針を左右する重要な区別である。
