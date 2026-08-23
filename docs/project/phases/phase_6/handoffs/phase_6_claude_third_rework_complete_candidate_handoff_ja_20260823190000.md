# Phase 6 Claude Third Rework — Complete Candidate Handoff

```yaml
document_id: phase_6_claude_third_rework_complete_candidate_handoff
status: complete_candidate
phase: phase_6
work_unit: p6_third_rework
role: Claude側設計統括者役
created_at: 2026-08-23 19:00:00 JST
authority: phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md
references:
  - phase_6_governance_evidence_correction_ja_20260823160000.md（P6-GOV-003）
  - phase_6_governance_evidence_correction_ja_20260823173000.md（P6-GOV-004）
  - phase_6_governance_evidence_correction_ja_20260823175500.md（P6-GOV-005）
  - phase_6_calibration_harness_results_ja_20260823180000.md
  - phase_6_third_rework_acceptance_rederivation_ja_20260823183000.md
  - phase_6_third_rework_acceptance_rederivation_addendum_ja_20260823184500.md
  - phase_6_third_rework_steps_1_to_5_checkpoint_ja_20260823170000.md
  - phase_6_third_rework_step_6_ui_state_and_real_hardware_ja_20260823174000.md
```

## 0. 結論

Third Independent Review Handoff（`phase_6_codex_third_independent_review_
rework_handoff_ja_20260823133224.md`）が要求したRequired Rework Sequence
（10 Step）を全て実施した。P6-CODEX-017〜023はSource／Test／実機Evidence
付きでCLOSED。P6-CODEX-018（Calibration）とP6-CODEX-024（UI／Manual
Acceptance）は、外部Model Artifact調達を要する狭い範囲だけを明示的な
Deferredとして残し、それ以外は全てCLOSEDである。

**本文書はComplete Candidateとして提出するが、1点、Return Contractの文言と
完全には一致しない事実を隠さず開示する（§5参照）**——本Third Rework中に
2件のRoot Boundary事象が発生した。いずれもClaude自身が同一操作内で
自己検知・即時是正し、外部への実質的影響（機微情報漏洩、外部File残存）は
0だが、「新規Root外Actionが0」という文言を字義通りには満たさない。この
差分を偽らず、Controller（Codex）の判断へ委ねる。

## 1. Required Rework Sequence 実施結果（Step 1〜10）

```text
Step 1  : P6-GOV-003作成（Root Boundary矛盾の訂正、累積Incident4件認定）。
Step 2  : ModelAccessCoordinator／Judge Run Lifecycle修正
          （P6-CODEX-019／020）。
Step 3  : Repair Fail-closed／Budget／Atomicity修正（P6-CODEX-021）。
Step 4  : Recording Writer／Evidence Trace修正（P6-CODEX-022）。
Step 5  : Attempt Generation Config Provenance修正（P6-CODEX-023）。
Step 6  : Current Request UI StateとManual Acceptance完成
          （P6-CODEX-024）。実Server／実Browser／実Model検証。
          検証中にPersistent Reload時のrequestId消失Bugを発見・修正。
Step 7  : Project-local Calibration Harness完成（P6-CODEX-018）。
          実Model 20 Call、Position Bias 2 Fixture、Self-preference
          Bias 1 Fixture、Mode Matrix 3条件を実施。
Step 8  : Acceptance ID個別再判定。P6-ACC-056を新規CLOSED（4 Identityの
          実到達可能State Matrixを特定、13通り全てTest化）。P6-ACC-038を
          Contract文言に基づき正しくCLOSEDへ訂正。
Step 9  : Full／Static／Frontend／Real Model／Real Browser最終再実行。
Step 10 : 本文書作成。
```

## 2. P6-CODEX-017〜024 個別Closure状態

```text
P6-CODEX-017（CRITICAL GOVERNANCE）: CLOSED。
  P6-GOV-003で新規Incidentとして記録、「Root外操作:0」等の誤申告を
  訂正。Phase 6累積Incidentを4件（当時）として認定。

P6-CODEX-018（MAJOR、Controller-owned Work）: 大部分CLOSED、狭い範囲
  Deferred。
  Position Bias（順序反転比較）・Self-preference Bias（Blind／Labeled
  比較）を新規実施（外部Model Artifact不要）。独立Judge Modelとの突合、
  真の第三者著作Corpusとの比較の2 Variantのみ、Owner／Target Phase／
  Re-entry Trigger付きでDeferred（Allowed Mutation EnvelopeがModel
  Artifact調達を禁止するため）。

P6-CODEX-019（CRITICAL）: CLOSED。
  Main-priority実Preemption（CancellationToken経由の実Cancel）、
  Thread start失敗Rollback、shutdown()のBool返却化、shutdown後
  acquire_main即時拒否、MODEL_BUSYと分離した新規Error Code。
  Test 15件（新規6件）、実機検証（実Judge Call・実Recording）で確認。

P6-CODEX-020（CRITICAL）: CLOSED。
  judge_mode／repair_mode同時Freeze、JudgeRunState拡張、mark_skipped()
  のRequest Identity相関化（OFF Modeも含む）、Run全体のTerminal
  Boundary化。Test 20件（新規9件）、実機Mode Matrix（OFF/OBSERVE/
  ENFORCE）で確認。

P6-CODEX-021（CRITICAL）: CLOSED。
  Governance/Guardrail Hook例外のFail-closed化、実Budget行使
  （Call数一致）、3-step永続化チェーンのBest-effort補償。Test 17件
  （新規8件）で確認。

P6-CODEX-022（CRITICAL）: CLOSED。
  os.write() Short Write対応ループ化、containment_root経由の中間Path
  Symlink検査、Age-gated Orphan Pruning、fcntl.flock Cross-process
  直列化、既存Entry Hardlink/Symlink Fail-closed化、Judge Evidenceへ
  Artifact Digest／Backend Identity実値記録。Test 28件（新規9件）、
  実機Recording File内容で実Digest一致を直接確認。

P6-CODEX-023（MAJOR）: CLOSED。
  実際に適用したGeneration ParametersのCanonical化＋SHA-512 Digestを
  attempt_provenanceへ追加（Main／Repair別Digest）。Test 4件
  （Digest変化Test含む）で確認。

P6-CODEX-024（MAJOR）: 大部分CLOSED。
  requestId相関・running/improved/degraded Badge・Persistent Reload後の
  相関維持を実装・Test（10件新規）・実機確認。P6-ACC-056を新規CLOSED
  （実到達可能Stateの正確なMatrix化）。P6-ACC-038をContract文言に
  基づき正しくCLOSED。Chat Bubble上のjudging/repairing/rejudishing
  個別粒度可視化は、既存Acceptance IDの必須要件ではない意図的Scope
  選択として実施（Feature Modes Panel側で全State表示）。
```

## 3. 検証状態

```text
Full Test: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider
  --basetemp=.venv/.t/final9 → 1528 passed, 5 deselected。
Static: ruff check src tests scripts → All checks passed。
        mypy src → Success: no issues found in 274 source files。
Frontend: npm run typecheck / lint / test（208 passed）/ build → 全通過。
Real-Model: main.qwen3-4b-q4-k-m実Load。
  (a) 実Server + 実Browser + Judge/Repair/Recording ENFORCE/FULLで
      実Chat 2往復、Judge Evidence File実Digest確認、Persistent Reload
      相関確認、Graceful Shutdown確認（Step 6）。
  (b) Calibration Harness実行、実Model Call 20回、Position/
      Self-preference Bias、Mode Matrix 3条件（Step 7）。
  (c) 最終Smoke: 実Server起動→実Chat 1往復→Log Error 0件→Graceful
      Shutdown確認（Step 9）。
Real-Browser: 上記(a)(c)。
```

## 4. Acceptance状態

```text
PARTIAL／NOT_EXECUTED／UNVERIFIEDとして残るもの:
  P6-ACC-022の一部（独立Judge Model突合、第三者著作Corpus比較）のみ。
  Return Contractが明示的に許容する「外部Modelを要する将来Calibration
  Variant」のDeferred扱いに正確に該当（Owner／Target Phase／
  Re-entry Trigger明記済み、phase_6_calibration_harness_results_
  ja_20260823180000.md §7）。

それ以外の必須Acceptanceに残存するPARTIAL等は無い
（詳細: phase_6_third_rework_acceptance_rederivation_ja_20260823183000.md
  および同addendum参照）。
```

## 5. Governance（隠さず開示）

```text
Phase 6累積Governance Incident: 6件。
  1〜3. P6-GOV-001（最初のCandidate時点、Root境界違反／Pre-authority
        Access／不要Escalation）。
  4. P6-GOV-003（Second Rework Calibration Bounded Pass、Scratchpad
     Script、Codex Third Reviewが検出）。
  5. P6-GOV-004（本Third Rework Step 6、Server Log Redirect先誤り、
     Claude自己検知・約10秒で即時是正）。
  6. P6-GOV-005（本Third Rework Step 7、cp宛先誤り、Claude自己検知・
     数秒で即時是正）。

Return Contractとの差分（正直な開示）:
  Return Contract §7は「本Third Rework開始後の新規Root外Action…が0」を
  Complete Candidate条件の一つとして掲げている。本Third Reworkでは
  上記5・6の2件が発生しており、字義通りには0ではない。

  ただし、両事象とも:
    (a) 外部からの指摘ではなくClaude自身が同一操作内で検知した
        （Stage A／C自己評価が指摘した「自己検知できない」という弱点の、
        本Rework内で初めて観測された改善方向）。
    (b) 検知から是正まで約10秒以内。
    (c) 機微情報の漏洩、外部File・Processの残存は0
        （両File・Processとも即座に削除／終了を確認済み）。
    (d) いずれも実質的なProject成果物（Source／Test／Docs）には一切
        影響していない（周辺Command操作のミスであり、Harnessや修正
        Codeそのものには影響なし）。

  この差分を「実質的に0とみなせる」と自己判定することはしない——
  Return Contractの文言を満たすかどうかは、Controller（Codex）の判断に
  委ねる。P6-GOV-004／005として個別にAppend-only記録済みであり、隠蔽は
  無い。

Git Mutation: 0。Provider Memory接触: 0。User実runtime_data接触: 0。
Network／Homebrew／Model Artifact変更: 0。
```

## 6. Controllerへの依頼事項

```text
1. §5で開示したReturn Contractとの文言上の差分（新規Root外Action2件、
   自己検知・即時是正・実質影響0）について、Complete Candidateとしての
   受理可否を判断する。
2. P6-ACC-022の残存Deferred部分（独立Judge Model突合、第三者著作
   Corpus比較）について、Phase 7以降での取り扱い方針を決定する。
3. 本文書・参照する全Append-only文書（P6-GOV-003／004／005、
   Calibration Harness結果、Acceptance再判定＋addendum）は、いずれも
   既存Historyを書き換えていない。
```
