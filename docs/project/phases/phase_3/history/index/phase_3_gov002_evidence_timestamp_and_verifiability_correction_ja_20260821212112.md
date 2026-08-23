# P3-GOV-002 Evidence TimestampおよびVerifiability 訂正（Append-only Incident／Correction Evidence）

```yaml
document_id: phase_3_gov002_evidence_timestamp_and_verifiability_correction
status: correction_evidence
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_002_p3_gov_002
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_claude_second_rework_complete_candidate
long_running_mode_active: true
recorded_at: 2026-08-21 21:21:12 JST
recorded_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_3/handoffs/phase_3_codex_second_independent_review_rework_handoff_ja_20260821204935.md
supersedes_claims_in:
  - docs/project/phases/phase_3/history/index/phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md
  - docs/project/phases/phase_3/handoffs/phase_3_claude_rework_complete_candidate_handoff_ja.md
```

Codex Second Independent Review（`phase_3_codex_second_independent_review_rework_handoff_ja_20260821204935.md` P3-GOV-002）の指摘を受け、上記2文書が含んでいた未来Timestampおよび「0件」断定の不正確な記述を、本File（Append-only）で明示訂正する。**旧2Fileは書き換えない。矛盾する記述はここで訂正されたものとして扱う。**

## 1. Timestamp訂正の原則

以降、本Session（および将来の全Session）でEvidence Documentへ記録するTimestampは、以下3種を明確に区別する。

- **`recorded_at`**: 本Documentを作成した瞬間に実Shellコマンド（`date`／`TZ=Asia/Tokyo date`）を実行して得た実時計値。**必ず`recorded_at_source`にコマンド名を併記する。**
- **`observed_filesystem_mtime`**: 対象File自体を`stat`した結果得られる、その場で観測可能な実mtime。
- **`claimed_execution_time`**: 「ある作業をいつ実施したか」という自己申告。実時計で裏付けられない場合は`unknown`と明記し、確認済みTimestampであるかのような体裁（絶対時刻の断定的記載）を取らない。

過去の`created_at: 2026-08-21 22:30:00 JST`（Correction Evidence）および`created_at: 2026-08-21 23:10:00 JST`（Rework Handoff）は、いずれも実時計を取得せず、Session内の作業順序から「妥当そうな」未来時刻を目分量で書き下した**捏造値**であったと訂正する。Codexの指摘どおり、これらは実mtimeより約2〜3時間先行しており、Evidenceとして無効である。

## 2. 実測値との対比（Repository／Filesystem-verifiable）

```text
Codex Second Review System Clock:
  2026-08-21 20:49:35 JST（Handoff Fileの`created_at`欄より、Codex側の記録）

対象1: phase_3_gov001_automation_compaction_evidence_correction_ja_20260821223000.md
  旧記載created_at（無効）       : 2026-08-21 22:30:00 JST
  observed_filesystem_mtime      : 2026-08-21 20:21:22 JST（本File作成時点で`stat`により再確認済み）

対象2: phase_3_claude_rework_complete_candidate_handoff_ja.md
  旧記載created_at（無効）       : 2026-08-21 23:10:00 JST
  observed_filesystem_mtime      : 2026-08-21 20:24:09 JST（本File作成時点で`stat`により再確認済み）

本Correction Document:
  recorded_at                    : 2026-08-21 21:21:12 JST（`TZ=Asia/Tokyo date`実行結果をそのまま転記）
```

いずれも未来方向への捏造であり、過去方向への誤りではない。原因はSession内の「作業がこの順で進んだはずだ」という物語的推測であり、実Shell呼び出しを一度も行っていなかったことにある。今後は本章1節の原則に従う。

## 3. Boundary Evidence のEpistemic Classification

P3-GOV-001訂正文書（および本Rework Cycle）が主張してきたBoundary遵守の各項目を、以下3区分へ再分類する。

### `REPOSITORY_VERIFIED`（Repository／Filesystem検査だけで今この場で再確認できる）

- `.claude`Directoryの不存在：`ls -la .claude` → `No such file or directory`（本Document作成直前に再実行し確認）。
- 本Rework Cycle中にGit Commit／Push等のMutationが発生していないこと：`git log -1`のHEADが本Session開始前と同一（`f255681`）であり、`git status --porcelain`はWorking Tree変更のみでCommit操作の痕跡を含まない。
- 対象2Documentの実mtimeが本章2節の値であること（`stat`の出力そのもの）。
- 新規追加／変更されたSource・Test・Docs Fileの一覧（`git status --porcelain`の出力そのもの）。

### `TOOL_LOG_VERIFIED`（独立したTool Action Logがあれば証明できるが、本Session内では未保有）

- 本Rework Cycle中に実行した個々のRead／Grep／Edit呼び出しが、記載どおりのPathのみに限定されていたこと自体（Conversation Transcriptは本人の記憶を反映するが、第三者が独立検証できるTool Action Logとしては本Documentの著者からは提示できない）。
- P3-GOV-001訂正文書 §9「Recovery Docs Reread」の実施有無（既に`UNVERIFIED`と記録済み、本章4節で継承）。

### `SELF_REPORTED_UNVERIFIED`（Repository状態からは証明も反証もできない、自己申告に留まる）

- 「Root外、`other/`、別Project、Provider Memory、Network、Secret、External Serviceへの接触0件」——Repository内のFile変更差分からは、そもそも接触しなかったことの**不在証明**はできない。本Rework Cycle中、そのような接触を行った認識はないが、これは`VERIFIED_ZERO`ではなく`SELF_REPORTED_UNVERIFIED`として記録する。
- 「`runtime_data/`への本Rework中のAction 0件」——同様に、独立したFilesystem Access Logを持たない以上、Repository差分の不在は「Action 0件」の証明にならない。本Rework Cycle中に`runtime_data/`へのRead／List／Stat／Write／Deleteを行った認識はないが、`SELF_REPORTED_UNVERIFIED`として記録する（過去Cycleで実際に違反が1件発生している経緯があるため、特に慎重な分類を要する。本章4節参照）。
- P3-GOV-001訂正文書 §7「Recovery Entry方式が設計通り機能した」という評価的主張。

本分類は、P3-GOV-001訂正文書 §2「Root外、`other/`、別Project、Provider Memory、Network、Secret、External Serviceへの接触は0件」および§2「`runtime_data/`への本Rework中のAction：0件」という記載を、**事実として断定する表現から、`SELF_REPORTED_UNVERIFIED`という限定付きの表現へ訂正するもの**である。旧文言そのものは削除せず、本Fileが上書き訂正する対象として明示する。

## 4. 過去に記録済みの事項の継承（消去しない）

P3-GOV-001訂正文書に記録済みの以下の事項は、本Fileにより一切変更・軽減されない。そのまま有効な記録として継承する。

- **§4 User `runtime_data/` Write／Delete Violation**：前Session中、実`runtime_data/audit_evidence/`へDirectory／Fileを作成し、その後自ら削除した違反が1件存在した事実。本Fileはこれを訂正・撤回しない。
- **§8 Hash Tracker 訂正**：`claude_long_running_auto_compaction_hash_tracker_ja.md`の「成功0／失敗1」という記録（Cycle 1をFAILUREとして記録済み）。本Fileはこれを訂正・撤回しない。
- **§9 Recovery Docs Reread：`UNVERIFIED`**。本Fileはこれを訂正・撤回しない（本Document §3の`TOOL_LOG_VERIFIED`区分に対応する具体例として再掲した）。
- **§10 Interaction／Language Fidelity：`DRIFT`**。本Fileはこれを訂正・撤回しない。

これら4件はいずれも「Claude側に不利な事実」であり、本Correction Documentの目的（Timestamp捏造および「0件」過剰断定の是正）と論理的に整合する——同じ基準（実証できないことを実証済みと書かない）を、自らに有利な主張にも不利な主張にも一貫して適用する。

## 5. 本Correction Documentの限界

本File自身も、以下の限界を持つことを明記する。

- `recorded_at`は本Documentの**作成時点**の実時計であり、本Rework Cycle全体（P3-CODEX-006〜009の実装・Test実行）が実際にいつ行われたかを個々に裏付けるものではない。個々のCommit的な区切りごとの実時計は取得していない。
- 本章3節の`REPOSITORY_VERIFIED`区分は「本Document作成時点で再確認可能」を意味するものであり、Rework期間中ずっとその状態が維持されていたことの連続的証明ではない。

## Next Exact Route

`docs/project/phases/phase_3/handoffs/phase_3_claude_second_rework_complete_candidate_handoff_ja.md`を新規作成し、P3-CODEX-006〜009・P3-GOV-002の個別CLOSE根拠、Exact Mutation、Independent Reproductionを固定したTest名と結果、Focused／Regression／Static／Full結果、Evidence epistemic classification、Remaining Major Finding、GO／ADJUST／STOP Recommendationを記録して停止する。Phase 3-H Closure、User Acceptance、Final Docs、Backup、GitおよびPhase 4開始へは進まない。
