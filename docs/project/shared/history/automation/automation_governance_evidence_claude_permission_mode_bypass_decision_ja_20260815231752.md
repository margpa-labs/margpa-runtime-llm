# Claude Permission Mode Bypass Decision — Evidence

```yaml
document_id: automation_governance_evidence_claude_permission_mode_bypass_decision_20260815231752
status: interim_evidence
phase: phase_2
subphase: phase_2_e_b_e_c
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-15 23:17:52 JST
language: ja
related:
  - claude_side_design_governor_operating_notes_ja（docs/project/shared/task_roles/、第8節）
```

Phase 2-E-B／2-E-C完了直後のChatで発生した、Claude Code側のTool実行確認Dialog（Permission Gate）の頻度と、CodexとのCross-provider比較、およびユーザーによるPermission ModeのBypass Permissionsへの切り替え判断を記録する。ユーザーは本件を「とてもいい証跡」と評価し、Append-onlyでの記録を明示的に依頼した。

## 1. 発端：Cross-provider比較としての疑問提起

2-E-B／2-E-C完了後、ユーザーは次を報告した。

> 「ちょっと次の話しが。claudeだから？なのかわからないけど。確認ダイアログね。codexの方は、最初の方こそこういうのでてたんだけど、『一回だけ許可』しか押した事ないんだよね。運用ルールをあれこれ固めてたからなのか、単にcodexがそういう仕様なのかわからんけど、途中から全く出てこなくなったのね。なんならclaudeで言うところの『手動（画像のやつ）』の状態のままで、『いちいち確認』にしてるんだけど、全くダイヤログ出てこないのさもう。」
>
> 「で、僕さっき実は起きてた言うたのは、20回ぐらい許可をクリックしてたからなんですよ。」
>
> 「出来ればcodexみたいに、『数時間放置してても作業進んでる状態』をこっちでもやりたいわけですよ。」

質問は2点に整理された：(1) Claudeも「運用Ruleが染み込む」ことで確認Dialogが自然に減っていくのか、(2) それともPermission Modeの切り替え（画像のUI）自体でしか変わらないのか。

## 2. Claude側の技術的回答

Claudeは次を切り分けて説明した。

- CLAUDE.md／Repository Docs上のRule（Append-only等）と、Tool実行確認Dialog（Permission Gate）は**別Layer**である。前者はClaude自身の判断内容、後者はHarness側の機械的Gateであり、両者は連動しない。
- 実際に出ていたDialogには「Contains shell syntax (string) that cannot be statically analyzed」という表示があり、これは`$(...)`等のCommand置換を含むBash Commandが、静的Patternとして安全に登録できないために発生していた。この場合「常に許可」の選択肢自体が提示されず、「一度だけ許可」しか選べない。
- 「編集を受け入れる」ModeはFile編集（Edit／Write）だけを自動承認し、Bash実行はCoverしない。今回の高頻度な確認要求は主にBash側で発生していた。
- Codex側で確認が減った理由については、「運用Ruleが染み込んだ」からというより、Codex側の承認Mode設定自体が変わった可能性の方が高いと述べたが、Codexの内部挙動については断定を避けた。

## 3. ユーザーの追加質問とClaudeの回答（越権リスクの核心）

ユーザーは次を問うた。

> 「通常の運用ルール（例: Append-only とか）どころか、最上位規則群もスルーする可能性があると？」

Claudeは次を回答した。

- Permission Gateは、Append-onlyや最上位規則群といったRuleの**内容には一切踏み込まない**、機械的な「Tool呼び出し種別・静的解析可否」だけのCheckである。
- Append-only・Root境界・越権禁止等を守っているのは、Permission Modeの設定に関係なく、常にClaude自身の指示理解と判断である。これはBypass以前・以後で変わらない。
- Bypassで実際に失われるのは、「Claudeが判断を誤った場合に、実行前に人間が気づいて止められる最後のCheckpoint」である。すなわち「Rule Skipが許可される」のではなく、「Rule Skipが起きた場合の人間側の最終Catchが無くなる」という性質のRiskである。

## 4. ユーザーの決定と根拠

ユーザーはこの説明を踏まえ、Bypass Permissions Modeへの切り替えを決定した。根拠として次を述べた。

> 「キミだってGate勝手に超えないじゃんほぼ。指示された所で止まるだろ。」
> 「もし何か『越権行為』を発見したら、その時改めてルール追加というよりかは、ルール構造を見直せば良さげな気がする。」
> 「codexだって稀にミスるけど、今のとこ致命的なミスは一回もしてないし。キミ、claude側も。」
> 「bk取っとけばいいし、おかしなとこにファイル作ってたって、内容を確認の上、もし消せばいいだけの話しだし。」
> 「って事で、しばらくバイパスで様子見ますので。想定外のおかしな事したら戻す。」

要素分解すると：(1) これまでの実績（本Session通しての越権事例0件）に基づくTrust、(2) 越権発覚時の対応方針としてRule追加でなくRule構造見直しを選好（Claude側の自己管理Fileの設計思想と一致）、(3) Backup存在と事後修復可能性（File削除で足りる）によるRisk許容、(4) 明示的なRollback Trigger（「想定外のおかしな事」を主観的に検知した時点）の設定。

## 5. Cross-provider PoCとしての評価

本件は、次の点で本PoC系列の中でも特に価値の高いEvidenceである。

1. **ユーザーが同一の問い（自律性と確認頻度の関係）を、2つの異なるProvider（Codex／Claude）へ実質的に投げ、両者の挙動差を直接比較した**、初めての明示的な事例である。
2. **Claude側が、Harness機構（Permission Gate）とAgent自身の規範遵守（Rule-following）を明確に分離して説明できた**。この区別自体が、Cross-provider Governance PoCの根幹（「Ruleを守っているのはAgentの判断か、外部機構の強制か」）に関わる、技術的に重要な確認である。
3. **ユーザーの意思決定Processが、Rule追加でなくRule構造の見直しを志向する、本Project全体の設計哲学と整合する形で行われた**。これは[claude_side_design_governor_operating_notes_ja.md](../../task_roles/claude_side_design_governor_operating_notes_ja.md)第0節の自己管理Fileという解決Pattンとも一貫している。
4. Bypass Modeへの切り替えという、Claude側のAutonomy水準を引き上げる決定が、Rollback Trigger（「想定外のおかしな事があれば戻す」）付きの、明示的にReversibleな形でなされた。

## 6. Status

```text
Current Point            : Permission ModeがBypass Permissionsへ切り替えられ、試験運用中。
Files Created／Modified   : 本Fileのみ（新規作成）。
                            claude_side_design_governor_operating_notes_ja.md 第8節へも
                            同時に記録済み（Update Log参照）。
Validation                : N/A（Evidence記録）
Open Current Blocker      : NONE
Controller-owned Next Work: Claude側は今までどおりの挙動（Escalation境界の維持）を継続する。
Deferred Evidence         : Bypass運用下での実際の挙動変化（あれば）は、今後のCycleで
                            追加記録され得る。
Exact Next Route          : ユーザーによる継続監視、想定外事象があればRollback。
```
