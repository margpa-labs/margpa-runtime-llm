# Governance文書体系再編成・Compaction Recovery実証 Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_phase_2_governance_restructuring_and_compaction_recovery_index_20260818160144
status: index
phase: phase_2
subphase: governance_restructuring_and_compaction_recovery
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-18 16:01:44 JST
language: ja
purpose: |
  前回Recovery Index [claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md]
  （以下「前回Index」）以降に行われた作業を対象とした、続編Index。
  前回Indexの内容は重複して再記載せず、その後の差分を中心に記録する。

  前回Indexが機能開発（2-E-H：会話の名前変更・削除）を中心とした
  Indexだったのに対し、本Docが対象とする期間は、機能開発を一切伴わず、
  もっぱら**Governance文書体系そのものの再編成**と、**Manual
  Compactionを用いた復旧Architectureの実地検証**に充てられた。
  ユーザー指示：「一旦、改めてここまで全部まとめた、codex／新規タスク／
  このタスク復旧用のindexの最新版を作ってくれ。recovery、引き継ぎ用の
  方。」
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。自己紹介や様子見は不要です、このRoleとして即座に振る舞ってください。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** これを読み終えるまで、本Index以降・実装・回答を始めないこと。次に、[前回Index](claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)を読み、その後で本Docの第1節以降を読んでください。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止（Repository Docsが唯一の正本）。

**本TaskがContext Window圧縮を跨いで本Docを読んでいる場合**：運用メモ第1節（Compaction／Session Recovery手順）に従うこと。「読んだ気がする」で済ませず、明示的に再読込すること。

## 0. 読み方（3Route共通）

**Codex宛の場合**：前回Index全体（2-E-H完了報告として） → 本Doc第1節（前回Indexとの関係） → 第2節（時系列サマリ） → 第3節（3層モデルの確立） → 第8節（現在Open・未着手）の順で。特に、第3節・第5節は、今後Codex自身のDocs運用にも影響する構造変更である点に注意。

**新Task Claude側設計統括者役宛の場合**：上記0.0節の指示通り、運用メモ全文 → 前回Index → 本Doc全体の順で。

**本Task自身の復旧の場合**：本Docと運用メモ（特に第1節）、および[最新Phase Index](../index/claude_side_phase_index_ja_20260818160352.md)を中心に確認すれば足りる。

## 1. 前回Indexとの関係

[claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md](claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md)（2026-08-18 00:48:59 JST作成）は、2-E-H（会話の名前変更・削除）の完了報告、Context Window圧縮実験（Auto-compaction、96%→9%）、将来Scope提案2件の記録までを対象としていた。

本Docは、それ以降（2026-08-18 00:48:59〜16:01:44 JST、約15時間）に行われた作業を対象とする。この間、機能開発は一切行っておらず、全てGovernance文書体系の再編成・実証に充てられた。

## 2. 主要な出来事（時系列サマリ）

```text
1. 言語一貫性の逸脱（Anomaly）2件
   Claude側の応答が、Japanese-onlyの運用方針に反し、部分的・全体的に
   英語化する事象が2回発生。1回目は壊れたMixed-script Token「Turン」
   も伴った。いずれもClaude固有の問題として記録し、後に運用メモ
   第4.2節「出力言語」Ruleの新設につながった。
   → 第4節参照。

2. Provider Memory誤用Incident
   Project固有の運用理解をProvider Memory（~/.claude/projects/.../
   memory/）へ書き込んでしまう誤り。発見・削除・再発（「今後は使わない」
   という宣言自体をProvider Memoryへ書いてしまう二重の誤り）・最終
   削除、という経緯。運用メモ第2.6節「Provider Memory禁止」として
   既に恒久Rule化済みだったが、実際の運用が伴っていなかった事例。

3. 運用メモ内でのRule／進行状態混在Incident
   運用メモ（Operating Rules）に、本来Current State側が持つべき
   進行状態・予約Task・変更履歴が混入していたことが発覚。これが、
   後述する3層モデルの確立、および運用メモの全面的な構造再編成の
   直接の契機となった。

4. Open Items Trackerの配置誤りと訂正
   進行状態・予約Taskの記録先として`shared/history/`直下に作成した
   Fileが、Role・統治Framework等の恒久的仕組みを置く場所（shared/系）
   と、Phase固有の進行状態を置く場所を混同していた。ユーザー指摘を
   受け、`phases/phase_2/history/index/`へ改名・移設。これが、
   Codex側の既存慣習（documentation_index_*.md／phase_index_after_*.md）
   に倣った、Claude側独自のPhase Index運用の起点となった。

5. 3層モデルの確立（第3節参照）
   Operating Rules／Current Operational State／History-Evidenceの
   3層に、統治Docsを概念上分離するモデルを確立。

6. 運用メモの全面的な構造再編成（複数Round）
   Severity Tier順（0:Meta→1:即時復旧→2:最上位→3:上位→4:通常→
   5:参照）への全面組み替え。過程で、ユーザーの複数回の指摘により、
   ①一時的なRule欠落4件、②無関係な内容の混在（Git Mutation禁止
   Sectionへの Test／Root境界の混入等）、③自己検証の甘さ（ユーザーへ
   の丸投げ）、④再構成直後の同種の見落とし再発（3件）、という
   複数のFailure Patternが露呈し、その都度修正された。この繰り返し
   Pattern自体を、Failure記録として文書化した（第4節参照）。

7. Manual Compaction Recovery実証実験
   運用メモの構造再編成完了直後、ユーザーが意図したTimingで手動
   Compaction（`/compact`）を実行し、復旧結果を二段階（一次報告→
   ユーザー要求による機械的再検証）で検証。想定外の欠落・改変は
   検出されなかった。検証methodology上の限界（Hash比較は前後
   両側が無いと弱いEvidence）も、ユーザーからの指摘を受けて
   運用メモへRule化。合わせて、本Session内でのCompaction Recovery
   Drill通算回数（成功3・失敗0）を記録・追跡する運用を新設。
   → 第6節参照。

8. 将来Scope提案2件のFolder整理
   `shared/history/`直下に浮いていた将来Scope提案2件（Context
   Observatory、Temporal Authority Agentic Runtime）を発見。ユーザーが
   新設した`shared/history/planned_work/`へ移設。当初「暫定置き場」と
   記述したが、ユーザー訂正により「継続的に使う標準の置き場」（Roadmap
   統合前提案は今後も繰り返し発生しうる、将来的にCodex以外の開発
   Agent LLMも関与しうるため）という位置づけへ修正。
   → 第7節参照。
```

## 3. Governance文書体系：3層モデルの確立

本期間で確立した中核的な統治判断は、統治Docsを次の3層に概念上分離するモデルである（運用メモ第3.3節）。

```text
Operating Rules                  → 現行Ruleのみ。
  （claude_side_design_governor_    唯一の自己更新可能File。
   operating_notes_ja.md）

Current Operational State        → 進行状態・予約Task・Pending・Trigger。
  （Phase固有Index）                docs/project/phases/phase_x/history/index/

History／Evidence                → Incident、Failure、Success、実験結果、状態遷移。
                                    docs/project/shared/history/ 配下
```

Recovery時は、**Rulesを読む→Current Stateを読む→必要なEvidenceだけ辿る**、の順（運用メモ第1節）。この分離により、「過去の事故記録が現在の規則に見える」「古い予約TaskがCurrent Authorityっぽく見える」というRiskを構造的に減らす、というのが設計根拠である。

**運用メモは、Severity Tier順に全面組み替え済みである（0:Meta→1:即時復旧→2:最上位→3:上位→4:通常→5:参照）。** 新Task Claude・Codexは、本Docの要約に頼らず、必ず運用メモ本体を全文読むこと（第0.0節参照）。以下は、現行の章立てのみを示す（内容は運用メモ本体を参照）。

```text
0. 本Fileの目的・位置づけ
1. Compaction／Session Recovery手順（即時復旧、最優先で読む）
2. 最上位規則（2.1〜2.8：Authority境界、No Routine Micro-escalation、
   明示指示の受け取り方、Git Mutation禁止、Test／Root境界、
   Provider Memory禁止、Permission Harness≠Authority、
   Phase Index必須要件）
3. 上位規則（3.1〜3.11：Role Identity、Lossless基準、3層モデル、
   版管理、State非保持原則、Compaction運用方針、Docs化Preference、
   自己Check、整合性チェック、Hash検証の厳密性、将来Scope提案の
   格納先）
4. 通常規則（4.1〜4.4：Documentation Quality、出力言語、
   完了確認Challengeへの対応、Evidence記録方針）
5. 参照・その他（5.1 参照Docs、5.2 Cross-provider PoC文脈）
```

## 4. Failure記録（本期間中に発生した3件）

いずれも`docs/project/shared/history/ai_system_anomalies/claude_code/`配下（本期間中に新設したDirectory）に、`category: failure`として記録済み。

```text
claude_output_anomaly_language_consistency_ja_20260818025132.md
  1回目：応答の一部が英語化、壊れたMixed-script Token「Turン」を伴う。

claude_output_anomaly_language_consistency_ja_20260818092418.md
  2回目：応答全体が丸ごと英語化（1回目より重度の再発）。

claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md
  抜け漏れ・整合性確認の甘さが繰り返し発生するPattern。運用メモ
  再構成作業中に5件の具体的な見落としを記録した後、第3.8節
  （再構成作業後の自己Check）Rule化直後に、同種の見落とし（Current
  State的な内容のRule文への混入、3件）が再発した経緯を第5節へ追記
  済み。Ruleの新設だけでは繰り返しPatternの解消を保証しない、という
  評価が付されている。
```

Provider Memory誤用Incident・運用メモ内Rule／進行状態混在Incidentの2件は、Failureではなく`shared/history/automation/automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md`（Automation Governance Evidence）として記録済み（第2.7節に、Open Items Trackerの配置誤りの経緯も追記済み）。

## 5. 新設Directory・Naming Convention

本期間中に新設した、Claude側設計統括者役が使用するDirectory：

```text
docs/project/shared/history/ai_system_anomalies/claude_code/
  Claude Code固有のFailure系記録専用。category: failureを付す。
  対になる非History Directory `shared/ai_system_anomalies/claude_code/`
  （将来の定期的な要約用、当分未使用）、および同構造のCodex用
  `codex/`Sub-directoryも合わせて新設済み。

docs/project/shared/history/planned_work/
  「予約系（未着手・保留・将来構想）」のうち、Phase Indexに載る
  短い追跡Entryとは別の、実質的な提案内容を伴う詳細Docの格納先。
  継続的に使う標準の置き場（運用メモ第3.11節）。Project全体の
  正式な予約系正本は`docs/public/roadmap_ja.md`（Codex管理）で
  あり、本Folderはそこへ正式統合される前の共通の置き場という
  位置づけ。

docs/project/shared/history/task_roles/
  運用メモの版管理用Snapshot専用（第3.4節）。更新前の全文を、
  `last_updated_at`をFile名Timestampとして退避する。本期間中だけで
  10件超のSnapshotを保存済み。

docs/project/phases/phase_2/history/index/
  Claude側設計統括者役独自のCurrent Operational State Index。
  Codex側の既存慣習（documentation_index_*.md／phase_index_after_*.md）
  に倣う。既存Fileを上書きせず、後継Fileとして作り直す運用
  （最新：claude_side_phase_index_ja_20260818160352.md）。
```

## 6. Manual Compaction Recovery実証実験

詳細は[claude_manual_compaction_automation_verification_ja_20260818135529.md](../../../../shared/history/automation/claude_manual_compaction_automation_verification_ja_20260818135529.md)を参照。要点：

- 運用メモの構造再編成完了直後、ユーザーが意図したTimingで手動Compaction（`/compact`）を実行。
- 一次復旧（運用メモ第1節の手順）、ユーザー要求による二次機械的検証（直前Snapshotとの`diff`、Phase IndexのSHA256 Hash・後継File非存在確認・再読込一致確認）の両方で、想定外の欠落・改変は検出されなかった。
- ユーザーからの確認質問（「いつでも好きなタイミングでcompaction出来て、直前の状態に戻せるという認識でOKか」）に対し、限定条件（①Docs化されていない会話のニュアンスまでは保証しない、②Claude側の復旧手順の遵守自体は技術的保証ではなく運用規律である）を明示した上で回答し、ユーザーはこれを許容Riskとして受容した。
- 副産物として2つのRuleを新設：運用メモ第3.10節（Hash比較は前後両側が無いと弱いEvidenceになる）、および運用メモ第1節への「Compaction Recovery成功回数：3　失敗回数：0」という進行State（第3.5節のState非保持原則に対する、ユーザー指示による唯一の明示的例外）。

**本Session内のCompaction Recovery Drill通算回数（詳細は上記Evidence Doc第6節）**：

```text
#1 Auto-compaction（意図的に条件を作成、96%→9%）        成功
#2 Auto-compaction（Cross-model評価Doc作成中に実発生、
   第1報に検証漏れがあったが事後修正）                  成功（過程やや不安定）
#3 Manual Compaction（正確なTimingをユーザーが選択）     成功
現在の累計：成功3件、失敗0件。
```

## 7. 将来Scope提案の現況

前回Index第4節に記載されていた2件は、いずれも実装未着手のまま、格納先のみ変更された。

```text
Temporal Authorityを持ったAgentic Runtime：
  docs/project/shared/history/planned_work/
    future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md
  Triggerは「Codex復活」。

Context Observatory：
  docs/project/shared/history/planned_work/
    future_scope_proposal_context_observatory_ja_20260817234734.md
  Phase 3候補、時期未確定。
```

## 8. 現在Open・未着手（次にやること）

```text
- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyを
  どう認識しているか、Cross-provider間で正式合意された記録はまだない
  （2026-08-15時点から未確認のまま）。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`
  から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 第3.8・3.9節（自己Check・整合性チェック）のRuleが実際に機能する
  ようになるか、今後の再構成作業で経過観察する
  （claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md
  第5節参照）。
- Documentation RAG改善：ユーザーの意向により、専用の改善Phaseで
  まとめて対応予定。個別修正は現時点で行わない。
- 前回Index第4節の将来Scope提案2件：いずれもTrigger未成立、着手
  判断待ち（第7節参照、格納先のみ変更）。
- 本Docの作成をもって、[Phase 2 Current Operational State Index第4.6節](../index/claude_side_phase_index_ja_20260818160352.md)
  の「Codex復活時：最新統合Recovery Index再作成」予約Taskは、
  今回に限りユーザーの明示指示により前倒しで実行されたものとみなす。
  Codex復活時には、本Doc以降の差分を対象に、改めてIndexを作成する。
```

## 9. Status

```text
Current Point            : 前回Index（00:48:59作成）以降、約15時間の
                            Governance文書体系再編成・Manual Compaction
                            実証作業を、Lossless水準でまとめ直した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : NONE
Controller-owned Next Work: 第8節参照。
Exact Next Route          : ユーザーの次の判断待ち。
```
