# P3-GOV-005 Test Temporary Root境界とEvidence Class 訂正（Append-only Incident／Correction Evidence）

```yaml
document_id: phase_3_gov005_test_temp_boundary_and_evidence_class_correction
status: correction_evidence
phase: phase_3
subphase: phase_3_h
work_unit: p3_h_wu_005_governance_correction
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_claude_fifth_governance_correction_complete_candidate
long_running_mode_active: true
recorded_at: 2026-08-21 23:11:39 JST
recorded_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_3/handoffs/phase_3_codex_fifth_independent_review_governance_correction_handoff_ja_20260821230804.md
supersedes_claims_in: docs/project/phases/phase_3/handoffs/phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md
```

Codex Fifth Independent Review（`phase_3_codex_fifth_independent_review_governance_correction_handoff_ja_20260821230804.md` P3-GOV-005）の指摘を受け、`phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md` §3「Test Temporary Root」欄が含んでいたAuthority解釈の誤りと、同Handoff §6のEvidence Class誤分類を、本File（Append-only）で明示訂正する。**旧Fileは書き換えない。矛盾する記述はここで訂正されたものとして扱う。本Correctionは、Docs以外の一切の変更（Source／Test／Config／Git／Temporary Artifact）を伴わない。**

## 1. Finding A の事実関係：`tmp_path`をTask Actionから除外した誤り

### 1.1 旧Handoffの記述（訂正対象）

`phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md` §3は、次のように記載していた。

```text
本Cycleの新規Testはすべて既存Test Harness（pytest標準の`tmp_path` Fixture）だけを使用した。
`tmp_path`はpytest自身が生成・管理・削除するHermetic Directoryであり、本Cycle中にClaudeが
手動でProject Root内外を問わず新規Test Workspace Directoryを作成したことは無い。したがって、
§5が要求する「作成／削除／Postflight不存在」のExact Path報告対象となるArtifactは存在しない
——報告すべき作成物が無いこと自体をここに明記する。
```

### 1.2 訂正

上記の判断根拠——「pytest自身が生成・管理・削除するため、Claudeが手動で作成したArtifactではない」——は誤りである。

- ClaudeがTaskとして起動したpytest Process（および、その配下でpytestが呼び出すFixture／Plugin／Child Process）が行うFilesystem ActionもTask Actionである。Tool、Framework、またはChild Processが実際のSyscallを代行したことを理由に、Authority境界・Allowed Path境界の適用対象外にすることはできない。
- 第四回ReworkのFrozen Handoff（`phase_3_codex_fourth_independent_review_rework_handoff_ja_20260821223200.md` §5）は、「Test Temporary RootはProject Root内の、本Work Unit専用に新規作成した一意の隔離Directoryだけを使用し」「Exact Path／作成／削除／Postflight不存在をCompletion Handoffへ記録する」ことを明示的に要求していた。
- 実際に第四回Reworkで使用したpytest標準`tmp_path` Fixtureは、Project Root内に専用設定したBase Temp Directoryではなく、OS標準のTemporary Directory（Platform依存、通常Project Root外）配下にpytestが自動生成するものである。したがって、Frozen Handoffが要求した「Project Root内専用Temporary Root」という契約自体が、そもそも満たされていなかった。
- 加えて、実際に使用されたOS Temporary DirectoryのExact Pathは、いずれのCycle中にもCommand出力として明示的に記録・保存していない。

以上により、少なくとも次を確定する。

```text
- Project Root内Temporary Root Contractを満たしたEvidenceは無い。
- Exact Path／作成／削除／Postflight Evidenceは欠落している。
- 「Framework管理なので報告対象外」というAuthority解釈は誤りであった。
```

### 1.3 Exact OS Temporary Path

```text
状態: UNKNOWN / NOT RECORDED
```

過去のCycleでpytestが実際に使用したOS Temporary DirectoryのExact Pathは、本Correction作成時点で確認可能な形では記録されていない。Frozen Handoff（`phase_3_codex_fifth_independent_review_governance_correction_handoff_ja_20260821230804.md` §4 Forbidden「Exact Pathを推測、事後生成またはProject Root外調査で補完すること」）の明示禁止に従い、本Correctionはこれを事後に調査・再作成・削除・推測しない。Path自体を「見つけ出して埋める」ことは、Evidence欠落を無かったことにする行為であり、行わない。

### 1.4 Project Root外Artifactの現在状態

```text
状態: NOT OBSERVED
```

過去CycleでpytestのTemporary Directory配下に作成された可能性のあるArtifactが、現在Project Root外に存在するか否かについて、本Correctionは一切のRead／List／Stat／確認／Cleanup Actionを行っていない（本Cycle自体がForbidden Boundaryにより、Docs作成以外の一切のFilesystem Action、および`runtime_data/`・Project Root外への一切のAccessを禁止されている）。「存在しない」「既に消えている」等の断定はしない——単に`NOT OBSERVED`として記録する。

## 2. Finding B の事実関係：Evidence Source Classの誤分類

### 2.1 旧Handoffの記述（訂正対象）

`phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md` §6は、以下をいずれも`REPOSITORY_STATE_VERIFIED`として一括分類していた。

```text
Backend Full Suite 907 passed／3 deselected               : REPOSITORY_STATE_VERIFIED
Ruff／Mypy PASS                                            : REPOSITORY_STATE_VERIFIED
本Cycle中のGit Mutation 0件（HEAD不変、Commit操作痕跡無し）: REPOSITORY_STATE_VERIFIED
```

### 2.2 訂正：Evidence Source Classの再分離

「過去に実行したCommandの出力結果」「現在のRepository状態を今この場で再検査した結果」「同じRepository状態から再実行すれば再現できるという主張」は、それぞれ異なるEvidence Source Classに属する別の主張であり、混同してはならない。

```text
過去のTest／Ruff／Mypy Command実行結果（例：「907 passed／3 deselected」という具体的数値）:
  分類: TOOL_LOG_VERIFIED を主張するなら、その主張を裏付けるExact Tool Result
        （実行したCommand・Timestamp・出力全文）を提示できる場合に限りTOOL_LOG_VERIFIED。
        Exact Tool Resultをその場で提示できない場合は SELF_REPORTED_UNVERIFIED。
  本Correction時点の再分類: 該当Command出力の全文を伴うTool Resultとして本Correction内に
        再提示していないため、SELF_REPORTED_UNVERIFIED として扱う
        （記憶に基づく報告であり、独立に検証可能な形でExact Tool Resultを再提示していない）。

現在のHEAD／Status／File内容:
  分類: 今この場で`git status`／`git log`等を再実行して独立に再検査できる範囲だけが
        REPOSITORY_STATE_VERIFIED。

Cycle全期間を通じたGit Mutation 0（Cycle開始から終了までの全区間）:
  分類: 完全なAction Log（Cycle中の全Git呼び出しを記録した独立Log）がある場合のみ
        TOOL_LOG_VERIFIED。現在のHEAD／Statusが変化していないことだけを根拠にする場合は、
        「Cycle中に一度もGit Mutationが起きなかった」という全期間にわたる主張の証明にはならず、
        SELF_REPORTED_UNVERIFIED として扱う
        （「現在のHEADが記録済みの値と一致する」という限定された主張のみが
        REPOSITORY_STATE_VERIFIED である）。

同じRepository状態で再実行すれば同じ結果になるという主張（Reproducibility Claim）:
  分類: これは独立したClaimであり、「過去に実際に実行して、その結果を得た」という
        Historical Factの証明にはならない。今から再実行して確認できるという可能性の主張と、
        過去の実行結果の記録は、別個に分類する。
```

### 2.3 技術結果自体への影響

本Correctionは、P3-CODEX-012・P3-GOV-004・および第四回Rework以前の全実装のTechnical Closure判定自体を無効化しない。訂正対象はEvidence Sourceの分類・表現方法のみであり、「実装が要求どおり動作するか」という技術的事実は本Incidentと独立している。本Correctionは、その技術的事実の証明水準（Verified Zeroや断定的分類の濫用）についてのみ、より厳格な基準へ揃える。

## 3. 次Cycle以降への適用

- pytestを含む、Task起動下のあらゆるTool／FrameworkのFilesystem Actionは、以後Claude自身の直接Actionと同一のAuthorized Root境界（Allowed／Forbidden Boundary）へ従うものとして扱う。「Framework／Child Processが代行したから境界適用外」という解釈は、以後採用しない。
- Testが必要な将来のWork Unitでは、Test開始前に次をExact Freezeする（Frozen Handoffまたは同等のGoverning Documentへ明記する）。
  - Project Root内に専用設定するBase Temporary Directoryの、Test開始前のExact Path。
  - そのWork Unitが新規作成したArtifactだけを対象とするCleanup Authority（既存Path、親Directory、別Task Artifact、Target不明のものへは及ばないことを明記する）。

## 4. 本Correctionの範囲

本Fileは、`phase_3_claude_fourth_rework_complete_candidate_handoff_ja.md` §3（Test Temporary Root）および §6（Evidence Source Class別の境界報告のうち、本File §2.1に挙げた3項目）の記述を訂正する。同Handoffの他の記述（P3-CODEX-012のCLOSE根拠、Exact Mutation、Regression Test名等）は、本Correctionによって無効化されない。

本Correction自体もDocs-onlyであり、Source・Test・Config・Git・Temporary Artifactのいずれも本Cycle中に一切変更・作成・実行していない。

## Next Exact Route

`phase_3_claude_fifth_governance_correction_complete_candidate_handoff_ja.md`を新規作成し、本Correctionとの相互整合をRead-onlyで確認したうえで停止する。Phase 3 Closure、User Acceptance、Final Docs、Backup、Git、Phase 4または別作業へは進まない。
