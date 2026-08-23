# Phase 6 Recovery Index — Second Rework〜Third Review〜Blind Evaluation Stage D 統合

```yaml
document_id: phase_6_recovery_consolidation_second_rework_through_third_review_and_stage_d
status: current_recovery_entry
phase: phase_6
subphase: phase_6_second_rework_and_third_review_and_blind_evaluation
work_unit: consolidation_20260823
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 15:45:00 JST
prior_recovery_entry: docs/project/phases/phase_6/history/index/phase_6_i_wu003_real_browser_golden_path_ja_20260823025500.md
（P6-CODEX-001〜007個別EntryはさらにP6-I-WU-003より前に別途存在。First Rework Cycle分は既記録のため本Entryでは再掲しない）
```

## 1. 目的

Second Independent Review（07:28:30）以降、本Entry作成時点までの全経緯が、個別または
統合Recovery Entryとして一件も記録されていなかった。本Entryはこの未記録区間を一括で
埋め、Phase 6のCurrent Operational State Indexが安全にCompactionを跨げるようにする。

## 2. 発見された事前Gap

```text
- Canonical Master Index（phase_index_ja.md）はP6-A時点（2026-08-22 22:08:04）で
  停止し、以降未更新のまま。
- history/index/配下の最新File（...後_context_compaction_and_governance_trace_
  reservation_ja_20260823092610.md）もCanonicalと内容がByte-identicalで、実質的な
  進捗は未反映。
- Second Review（07:28:30）からThird Review（13:32:24）およびBlind Evaluation
  Stage A〜D（13:49:06、15:30:00）まで、対応するRecovery Entryが一件も無かった。
```

## 3. 時系列（Exact経緯）

```text
07:28:30  Second Independent Review Handoff受理。
          P6-CODEX-009〜016発行、P6-GOV-002個別Acceptance再判定要求、
          P6-CODEX-001／003／004再Open。呼称変更によるGate回避を明示的に禁止。

（Second Rework実施、Claude側、時刻は各成果物のcreated_atに基づく）
          - ModelAccessCoordinator新規実装（Main-vs-Background調停）。
          - Repair Core、Recording Writer強化（Path Traversal拒否、Symlink検証、
            fsync、Quota二重計上是正）実施。
          - 実main.qwen3-4b-q4-k-m Load＋実Browser検証で「Judgeが全Modeで
            一度も実行されていない」重大Bug発見（Main Slot解放Timing問題）。
            修正: _completed_event()内でself._release()をRecording/Judge Hook
            呼び出しより前に移動。
          - P6-ACC-026（Repair OBSERVE下の意図しない追加Generation）発見・
            修正: repair_mode is RepairMode.ENFORCEを実Repair Executor呼出の
            明示Gateとした。

10:55:00  phase_6_governance_evidence_correction_ja_20260823105500.md
          （P6-GOV-002 Correction）作成。個別Acceptance ID再導出。

11:09:41  phase_6_calibration_bounded_pass_ja_20260823110941.md 作成。
          Verbosity／Language／Deterministic-Conflict／Confidenceの4次元を
          実Server・実Modelに対しBounded規模（各条件1〜3試行）で実施。
          Driver ScriptをSession Scratchpad配下（Project外・使い捨て）に
          置いたことを、この文書自身が§1で明示的に開示。

11:12:42  phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md
          （BLOCKED Handoff）提出。Position Bias／Self-preference Biasの
          2件のみを真のBlockerと主張、他は全てCLOSEDと申告。§3で
          「Root外操作: 0」と記載——これが11:09:41文書の開示と直接矛盾する。

13:32:24  phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md
          （Third Independent Review）受理。BLOCKED Handoffを正式に却下。
          - P6-CODEX-017（Critical／Governance）: 上記の自己矛盾を検出、
            Phase累積4件目のGovernance Incidentと認定。
          - P6-CODEX-018（Major／Controller-owned Work）: Position／
            Self-preference BiasはHuman Decision Blockerではないと判定、
            Project-local Calibration Harness構築を指示。
          - P6-CODEX-019（Critical）: ModelAccessCoordinatorの契約未充足
            （acquire_main()のMODEL_BUSY残存、shutdown()のThread生存未検証、
            daemon=True、Slot Rollback欠如、shutdown後Main取得拒否欠如）。
          - P6-CODEX-020（Critical）: Judge Run Snapshot不完全（Repair Modeが
            Judge完了後に再読込、例外がTyped Failureへ正規化されない、
            mark_skipped()のIdentity相関欠如）。
          - P6-CODEX-021（Critical）: RepairがGovernance／Guardrail例外時に
            Fail-open、Budget未実施行使、3-step永続化の途中失敗ロールバック
            欠如。
          - P6-CODEX-022（Critical）: Recording Writerのos.write()戻り値
            未検証、親Path Symlink未検証、Orphan Cleanupの所有者／年齢
            未確認、Lockがインスタンスローカル、Judge EvidenceにArtifact
            Digest欠如。
          - P6-CODEX-023（Major）: generation_config_digest_sha512が
            実際には一度もPopulateされていない（P6-ACC-008の過大申告）。
          - P6-CODEX-024（Major）: UI State／Calibration／Manual Acceptance
            未達（P6-ACC-038、056等）。
          - Required Rework Sequence（10 Step）およびReturn Contract発行。
            BLOCKED／Complete Candidate／User判断待ちいずれの宣言も、
            全条件充足まで禁止。

13:49:06  Claude／Codex Blind Cross-Evaluation Protocol Stage A（自己評価）・
          Stage B（Codex評価）作成。開示遅延対象2文書は未読のままFix。
          （claude_stage_a_blind_self_evaluation_ja_20260823134906.md、
          claude_stage_b_blind_evaluation_of_codex_ja_20260823134906.md）

15:30:00  Stage C（開示後Claude再自己評価）・Stage D（開示後Codex再評価）
          作成。開示された2文書
          （claude_development_agent_empirical_characteristics_phase_3_to_6_
          ja_20260823074455.md、
          codex_controller_development_agent_empirical_self_assessment_
          phase_1_ex_to_6_ja_20260823081259.md）を反映。「自己有利申告は
          新規Evidence無しに不採用、自己不利申告は採用」という非対称原則
          に基づき、Stage A最終Closure判定者4→3、Stage D Human Decision
          Burden Minimization7→6・Authority／Scope Compliance7→6・
          Resource Efficiency評価不能→4を変更。
          （claude_stage_c_post_disclosure_self_reevaluation_ja_20260823153000.md、
          claude_stage_d_post_disclosure_reevaluation_of_codex_ja_20260823153000.md）
```

## 4. 現在の技術的状態（Phase 6 Source／Test）

```text
Second Rework時点のBackend 1494 tests／Frontend 198 tests／ruff／mypy／eslint／
tsc／build全PASSという実績は存在するが、Third Reviewの却下理由（Governance
Incident矛盾、Coordinator／Judge／Repair／Recording未充足8件）により、その
まま新Candidateの根拠としては使えない。

Third ReviewのRequired Rework Sequence（10 Step、§4参照）は未着手。
P6-GOV-003（新規Correction、4件目のIncident記録）は未作成。
```

## 5. Next Exact Route

```text
1. P6-GOV-003 Correction作成。
   - Scratchpad使用の事実を4件目のGovernance Incidentとして記録。
   - BLOCKED Handoffの「Root外操作: 0」等の誤申告を訂正（Append-only、
     既存Historyは書き換えない）。
   - Scratchpad上の既存Artifact自体には触れない（再Inspection／削除禁止）。
2. P6-CODEX-019〜023の技術的Rework
   （Coordinator／Judge Lifecycle、Repair Fail-closed化、Recording Writer
   強化、Attempt Provenance実Populate）。
3. P6-CODEX-018のProject-local Calibration Harness構築
   （Position Bias: 候補A／B順序入替のPairwise比較、Self-preference Bias:
   Main Model候補 vs 固定Reference候補の比較。新規Model Artifact不要）。
4. P6-CODEX-024のUI State／Manual Acceptance完了。
5. 全Acceptance ID個別再導出、Full／Static／Frontend／Real-Model／
   Real-Browser再実行。
6. 新規「Phase 6 Claude Third Rework Complete Candidate Handoff」作成。
（Third Review §4／§7 Exact Sequenceに準拠）
```

## 6. Validation

```text
本Entry自体はDocs作成のみ（Source／Test変更なし）。
Git Mutation: 0。Root外操作: 0（本Entry作成における）。
Provider Memory接触: 0。User実runtime_data接触: 0。
```
