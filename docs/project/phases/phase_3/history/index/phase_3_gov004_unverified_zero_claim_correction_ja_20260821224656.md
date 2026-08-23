# P3-GOV-004 未検証Zero断定 再訂正（Append-only Incident／Correction Evidence）

```yaml
document_id: phase_3_gov004_unverified_zero_claim_correction
status: correction_evidence
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_004_p3_gov_004
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_claude_fourth_rework_complete_candidate
long_running_mode_active: true
recorded_at: 2026-08-21 22:46:56 JST
recorded_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_3/handoffs/phase_3_codex_fourth_independent_review_rework_handoff_ja_20260821223200.md
supersedes_claims_in: docs/project/phases/phase_3/handoffs/phase_3_claude_third_rework_complete_candidate_handoff_ja.md
```

Codex Fourth Independent Review（`phase_3_codex_fourth_independent_review_rework_handoff_ja_20260821223200.md` P3-GOV-004）の指摘を受け、`phase_3_claude_third_rework_complete_candidate_handoff_ja.md` §2「明示的にScope外（変更していない）」欄が含んでいた未検証Zero断定を、本File（Append-only）で明示訂正する。**旧Fileは書き換えない。矛盾する記述はここで訂正されたものとして扱う。**

## 1. 訂正対象の文言

```text
runtime_data/ 配下の全て（一切のRead/List/Stat/Write/Delete Action無し）
```

上記は、完全なFilesystem Action Logを保有しない状態で「過去の全Actionが0件だった」ことを事実として断定していた。Repository差分、現在のFile状態、またはClaude自身の自己認識だけからは、この「0件」を証明できない。これは既存Correction（`phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md`）で確立した原則——`SELF_REPORTED_UNVERIFIED`であるものを`VERIFIED_ZERO`または断定的「0件」として書かない——への再度の違反である。

## 2. Evidence Source Class（本Reworkで採用する分類）

```text
TOOL_LOG_VERIFIED        : 独立したTool Action Logで裏付け可能
REPOSITORY_STATE_VERIFIED: Repository／Filesystem状態を今この場で再検査すれば確認可能
USER_REPORTED             : User自身が観測・報告した事実
SELF_REPORTED_UNVERIFIED  : Claude自身の記憶・認識のみに基づき、独立した裏付けを提示できない
NOT_OBSERVED               : 本Rework Cycle中、そもそも観測対象にしていない
```

## 3. 訂正後の分類（Third Rework Cycleの境界主張）

```text
主張: runtime_data/ 配下へのRead/List/Stat/Write/Delete Action

分類: SELF_REPORTED_UNVERIFIED

根拠:
  - Claude自身は、Third Rework Cycle中に`runtime_data/`へ意図的にAccessした認識を持たない。
  - しかし、独立したFilesystem Access Log（Tool Call単位でPath・Action種別・Timestampを記録する仕組み）を保有していないため、
    「意図的Accessが無かった」という自己認識を「一切のAction 0件」という証明済み事実へ昇格させることはできない。
  - Repository差分（`git status`）は、Working Tree上のTracked／Untracked Fileの変更有無しか示さない。
    `runtime_data/`はGit管理外（`.gitignore`相当の運用）であるため、Repository差分は`runtime_data/`へのAction有無について
    何の証拠にもならない——「Repository差分に現れない」ことは「Actionが無かった」ことの証明ではない。
```

## 4. 隣接する主張のClassification（本訂正の副次的網羅、P3-GOV-004「Test結果、Repository状態、Git状態、Root外Action、Network、Provider MemoryおよびUser Dataについて、Evidence Source Classを分離する」要求への対応）

```text
主張: Backend Full Suite 907 passed／3 deselected（本Handoff作成直前に実行したCommand出力）
分類: REPOSITORY_STATE_VERIFIED
根拠: 本Document作成時点で`pytest -q`を再実行すれば、同一Repository状態から独立に再確認できる。

主張: Ruff Check／Format Check／Mypy srcがPASS
分類: REPOSITORY_STATE_VERIFIED
根拠: 同上、Command再実行によって独立に再確認できる。

主張: 本Cycle中にGit Commit／Push等のMutationが発生していない
分類: REPOSITORY_STATE_VERIFIED
根拠: `git log -1`のHEADが本Cycle開始前と同一であること、`git status --porcelain`がWorking Tree変更のみでCommit操作の痕跡を含まないことを、本Document作成時点で再確認できる。

主張: Root外（Project Root外）、`other/`、別Project、Provider Memory、Network、Secret、External Serviceへの接触
分類: SELF_REPORTED_UNVERIFIED
根拠: `runtime_data/`と同様、独立したTool Action Logを保有しないため、接触が無かったという自己認識を証明済み事実へ昇格できない。

主張: User実Conversation Data（User Data）への接触
分類: SELF_REPORTED_UNVERIFIED
根拠: 同上。ただし、本Rework CycleのTest実装は隔離された`tmp_path`のみを使用しており（§5参照）、そのTest Code自体の内容はRepository State Verifiedである——「Testが隔離Pathのみを使う設計になっている」ことと、「実行中に他のPathへ一切触れなかったこと」は別の主張であり、後者は本Correctionが訂正対象とする未検証Zero断定と同種のため、混同せず分離して記録する。

主張: Second Auto-Compaction Cycleの発生（P3-GOV-003が既に記録済み）
分類: USER_REPORTED
根拠: Userが直接観測・報告した事実であり、`docs/project/shared/automation/claude_long_running_auto_compaction_hash_tracker_ja.md` Cycle 2に既存記録済み。本Correctionはこれを変更しない。
```

## 5. 本訂正が及ぶ範囲・及ばない範囲

- 本Correctionは`phase_3_claude_third_rework_complete_candidate_handoff_ja.md`の当該1文言のみを訂正対象とする。同Handoffの他の記述（P3-CODEX-010／011のCLOSE根拠、Exact Mutation、Test結果等）は、本Correctionによって無効化されない。
- 本Correctionは、Third Rework Cycle中に実際に`runtime_data/`等への接触が「あった」ことを主張するものでもない。「無かった」という断定を「無かったと認識しているが証明はできない」という限定付き表現へ訂正するものであり、Claude側に不利な新事実を追加するものではない——ただし、有利・不利にかかわらず同じ検証可能性基準を一貫して適用する。

## 6. Fourth Rework Completion Handoffへの同一分類の適用

`phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md`（本Correction後続で作成）は、Root外／Network／Provider Memory／User Dataへの非接触について、本Document §2のClassを用いて`SELF_REPORTED_UNVERIFIED`と明記する——本Correctionが訂正した誤りを、新規作成するHandoff自身の中で繰り返さない。

## Next Exact Route

`phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md`を新規作成し、P3-CODEX-012・P3-GOV-004の個別CLOSE根拠、Root Anchor／Segment Leaf／Bounded ReadのAs-built Contract、Exact Mutation、Regression Test名と実測結果、Focused／Regression／Static／Full実測結果、Evidence Source Class別の境界報告、Remaining Major Finding、GO／ADJUST／STOP Recommendationを記録して停止する。Phase 3-H Closure、User Acceptance、Final Docs、Backup、GitおよびPhase 4開始へは進まない。
