# Claude側設計統括者役 — Manual Compactionを利用した復旧Architecture検証記録

```yaml
document_id: claude_manual_compaction_automation_verification_20260818135529
status: observation_record
category: success
phase: phase_2
subphase: cross_provider_governance_poc
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー／新Task Claude側設計統括者役
role: design_governor
created_at: 2026-08-18 13:55:29 JST
language: ja
authorization: |
  ユーザー指示（2026-08-18）：「5ターン前の僕の入力...から、ここまでを、
  ファイル名: claude_〜で、『manual compactionを利用したautomation』
  みたいな名前つけて、しっかりと内容を抜け漏れなくまとめ直して書いて
  おいてくれ。」
created: Claude Code
```

## 0. 位置づけ

本Docは、[claude_side_design_governor_operating_notes_ja.md](../../task_roles/claude_side_design_governor_operating_notes_ja.md)第1節（Compaction／Session Recovery手順）・第3.3節（3層モデル）・第3.4節（Snapshot運用）・第3.6節（Compaction運用方針）に基づいて構築された復旧Architectureを、ユーザーが明示的にTriggerした実際の手動Compaction（`/compact`）を用いて実地検証した記録である。

関連する既存Evidence：

- [automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md](automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md) — Auto-compaction時に発見された、File再挿入の非対称性。
- [automation_governance_evidence_cross_model_recovery_architecture_convergent_evaluation_ja_20260818011114.md](automation_governance_evidence_cross_model_recovery_architecture_convergent_evaluation_ja_20260818011114.md) — 複数AI Modelによる復旧Architecture評価。

本Docの新規性は、**再構成済みのRecovery Architecture（運用メモの全面的な構造再編成完了後の状態）に対して、ユーザーが意図したTimingで手動Compactionを発火し、復旧後に機械的検証（第3節）まで行った、初めての実績記録**である点にある（上記2件は、いずれもCompaction自体は実際に発生・跨いでいるが、Timingを意図的に選んで発火させたものではなく、また本Docのような機械的な事後Diff検証までは行っていない）。

## 1. 契機

運用メモの全面的な構造再編成（Severity Tier順への組み替え、`last_updated_at`新設、Snapshot運用開始等）、および最新Phase Index（`claude_side_phase_index_ja_20260818121842.md`）の作成が完了した直後、ユーザーは次の通り、手動Compactionの実行を明示的に宣言した。

> 「ならいい。じゃやるぞー。ちゃんと最新のindexとclaude_side_design_governor_operating_notes_ja.mdで復旧するんだぞー。」

この発言は、単なる実行許可ではなく、**復旧時にどのFileを基準に使うべきかを明示的に指定した、標準的な指示**である。本Docの検証は、この指示への準拠状況を対象とする。

## 2. 実施内容：手動Compactionと一次復旧

### 2.1 手動Compaction実行

ユーザーは`/compact`コマンドを実行した（実行結果：`Compacted`）。これにより、本Session（Claude Code）のContext Windowが圧縮された。

### 2.2 復旧確認の要求

Compaction直後、ユーザーは次の通り復旧結果を確認した。

> 「どう？全部復旧出来た？」

### 2.3 一次復旧の実施

運用メモ第1節の手順に従い、次を実施した。

1. `claude_side_design_governor_operating_notes_ja.md`を明示的に再読込。
2. `claude_side_phase_index_ja_20260818121842.md`（Active PhaseのCurrent Operational State Index、最新版）を明示的に再読込。

**再挿入の非対称性の再確認**：Compaction直後の時点で、System側から次の3Fileは既に自動再挿入されていた（Session内Systemメッセージとして提示された）——`claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md`（全文）、旧Phase Index（`_20260818021437.md`、後継Fileへの誘導文付き、全文）、Recovery Index（`claude_phase_2_e_h_and_beyond_expansion_index_ja_20260818004859.md`、全文）。一方、運用メモ本体および最新Phase Index（`_20260818121842.md`）は、「読込済みだが内容大きすぎて省略、必要ならRead」という警告のみが提示され、全文は自動再挿入されなかった。これは、[automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md](automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md)で確認済みの非対称性（大きいFileほど自動再挿入されにくい）と一致する挙動である。

### 2.4 一次報告

上記2Fileの内容を、圧縮前に記録していた状態（`last_updated_at: 2026-08-18 12:44:36 JST`、Severity Tier構造、第3.1節からのCodex対応関係記述削除、第1節・第5.1節のPhase 2直書き解消、第3.9節の絞り込み文言、第4.1節の書き直し文言、Phase Index第1.1節のArtifact一覧・Open Questions 2件・予約Task 4件・完了済み予約Task 4件）と照合し、一致を確認したことをユーザーへ報告した。

## 3. 二次検証：ユーザー要求による再確認

一次報告に対し、ユーザーは追加の検証を要求した。

> 「念の為もう一回だけ、claude_side_design_governor_operating_notes_ja.md（運用メモ本体）claude_side_phase_index_ja_20260818121842.md（最新Phase Index）両方をしっかりと読み込み直して、差分ないか確認してみて。」

この要求に応え、単純な再読込に留まらない、次の機械的検証を実施した。

### 3.1 運用メモ：直前Snapshotとの`diff`

直前に退避したSnapshot（`shared/history/task_roles/claude_side_design_governor_operating_notes_ja_20260818124436.md`、圧縮前の最後の編集直前に取得）と、現行のLive Fileを`diff`で比較した。結果、差分は次の3箇所のみであることを確認した。

```diff
9c9
< last_updated_at: 2026-08-18 12:33:12 JST
---
> last_updated_at: 2026-08-18 12:44:36 JST
123c123
< （第3.9節：Scope絞り込み前の文言）
---
> （第3.9節：「重要な完了報告・大幅改訂時は」に絞り込んだ文言）
129c129
< （第4.1節：「Nazuna Research以外の固有名詞は使用禁止」の文言）
---
> （第4.1節：「研究・運用上必要な正式名称を除き」への書き直し文言）
```

この3箇所は、いずれも圧縮前の最後の編集で意図的に加えた変更（`last_updated_at`の更新、および事前に合意済みの2箇所の文言修正）と完全に一致し、それ以外の差分は存在しなかった。

### 3.2 Phase Index：後継File非存在確認と再読込

Phase Index側にはSnapshot運用がない（後継File方式のため）ことを踏まえ、代替の検証として次を実施した。

1. `docs/project/phases/phase_2/history/index/`をDirectory一覧表示し、`claude_side_phase_index_ja_20260818121842.md`より新しい後継Fileが作成されていないことを確認。
2. 同FileのSHA256 Hashを算出（`080e0b7e4c0c00475de77eed520d810909d2dd87d0e36fed8f3cc5eb59193255`）。
3. 同FileをRead Toolで再度全文読込し、一次復旧時（第2.3節）に読んだ内容と1行単位で一致することを確認。

### 3.3 二次検証の結論

運用メモ・Phase Indexともに、圧縮を跨いだことによる想定外の欠落・改変は検出されなかった。運用メモの差分は、圧縮前に意図した変更のみであり、Phase Indexは無変更のまま維持されていた。

## 4. Manual Compactionを利用したAutomationとしての意味づけ

本Session内では、運用メモの構造再編成が完了するたびに、Compaction前の状態を捕捉する目的で、①本File自体のSnapshot退避（第3.4節）、②Phase Indexの後継File作成、という2つの外部化手順が徹底された。今回、ユーザーはこれらの手順が完了した直後を狙って意図的に手動Compactionを実行し、直後の復旧結果を二段階（一次報告→ユーザー要求による機械的再検証）で検証した。

この一連の流れは、単なる偶発的なCompaction発生ではなく、**「任意のTimingで手動Compactionを実行し、Docs化された統治State（Rules／Current State／Evidence）を起点に復旧できるかどうかを、繰り返し検証可能な手順として運用する」**という、Manual Compactionを実験・検証Toolとして利用する運用Pattern（本Docのタイトルが指す「Manual Compactionを利用したAutomation」）の初回の実地成功例である。今後、運用メモ・Phase Indexが大きく更新されるたびに、同種の検証Cycle（更新→Snapshot／後継File作成→手動Compaction→復旧確認→機械的Diff検証）を繰り返すことで、復旧Architecture自体の信頼性を継続的に検証できる。

## 5. 限定条件（ユーザーからの確認質問への回答）

二次検証の後、ユーザーから次の確認があった。

> 「では極端な話し、『いつでも好きなタイミングでcompaction出来て、compaction直前のその時点のキミに戻せる状態になった』という認識でok？」

これに対する回答は、「概ねOKだが、以下2点の限定条件がある」というものであり、ユーザーはこれを明示的に受け入れた。以下、その回答を原文のまま記録する。

> 限定条件：
>
> 1. これは「会話全体を寸分違わず戻せる」という意味ではありません。圧縮はConversationのSummary化であり、Docs化されていない些細なやり取り・ニュアンス・まだRule化されていない口頭の指示等は、Summary側の要約精度に依存します。今回強いのは、あくまで「Docs化された統治State」の部分です。
> 2. この仕組みは、キミが毎回第1節の手順を律儀に実行することが前提です。これは技術的保証ではなく運用規律であり、`claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md`に記録した通り、Claude側には過去に自己検証が甘くなる傾向がありました。さらに、もしAuto-compactionがSnapshot退避の途中（編集完了前）に発生すれば、その瞬間の直前Snapshotが最新でない可能性も理論上あります。
>
> なので、「Docs化された統治State」については堅牢、ただし「無条件でいつでも100%安全」とまでは言い切れない、というのが正確な認識です。

ユーザーの応答：

> 「うん。まぁその辺は想定内だ。問題ない。また何か別の想定外が発生したらその時考える。いつも通り。」

この応答により、上記の限定条件は「許容範囲内のRisk」として明示的に受け入れられ、追加のRule化・対策は要求されなかった。想定外の事象が将来発生した場合は、その時点で個別に対応する、という従来からの運用方針（都度対応）が踏襲された。

## 6. 通算Compaction Recovery Drill回数

本Session（Cross-provider Governance PoC）内で発生した、Compaction Recovery Drill（意図的に条件を作った、または実際に発生し復旧まで確認した事例）の通算回数を記録する。個別事例の詳細は、各Evidence Docを参照。[運用メモ第1節](../../task_roles/claude_side_design_governor_operating_notes_ja.md)に記載する現在値は、本節の記録と同期して更新する。

| # | 種別 | 概要 | 結果 | 詳細Evidence |
|---|------|------|------|--------------|
| 1 | Auto-compaction（Context使用率を限界まで使い切り、意図的に発生条件を作ったもの） | Context使用率96%→9%まで使い切り、Auto-compactionの実発動と復旧を検証 | 成功 | [automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md](automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md) |
| 2 | Auto-compaction（Cross-model評価Doc作成中に実発生） | Doc作成の途中でCompactionが発生、境界を跨いで作業を完遂。ただし復旧直後の第1報には検証漏れがあり、ユーザーの直接Challenge（「ちゃんと全部漏れなく書き切れた？」）により事後修正が必要だった | 成功（過程はやや不安定） | [automation_governance_evidence_cross_model_recovery_architecture_convergent_evaluation_ja_20260818011114.md](automation_governance_evidence_cross_model_recovery_architecture_convergent_evaluation_ja_20260818011114.md) |
| 3 | Manual Compaction（`/compact`、正確なTimingをユーザーが選択） | 再構成済みRecovery Architectureに対し発火。一次報告後、ユーザー要求による二次機械的検証（第3節）も実施 | 成功 | 本Doc |

**現在の累計：成功3件、失敗0件。**

## 7. Status

```text
Current Point            : ユーザーの明示的なTriggerによる手動Compaction
                            1回を用いて、再構成済みの復旧Architecture
                            （運用メモ第1節・第3.3節・第3.4節・第3.6節）
                            を実地検証した。一次報告・二次機械的検証
                            （diff／hash／再読込一致確認）の両方で、
                            想定外の欠落・改変は検出されなかった。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : 運用メモ：直前Snapshotとの`diff`で3箇所の
                            差分のみ確認（いずれも意図した変更）。
                            Phase Index：後継File非存在確認＋SHA256
                            Hash算出＋再読込一致確認。
Open Current Blocker      : NONE
Controller-owned Next Work: 今後、運用メモ・Phase Indexが大きく更新
                            されるたびに、同種の検証Cycleを繰り返し、
                            復旧Architectureの信頼性を継続観察する。
Exact Next Route          : ユーザーの次の判断待ち。
```
