---
document_id: phase_6_claude_current_task_r25_to_r28_exact_rework_handoff_20260829101215
document_type: differential_exact_rework_handoff
document_state: ready_for_single_step_start
language: ja
created_at: 2026-08-29 10:12:15 JST
authority_owner: Codex_プロジェクト責任者兼設計統括者役
target_provider: Claude
target_role: 設計者兼実装者役
target_task: current_existing_claude_task
preserved_baseline: current_working_tree_after_r0_to_r24
first_exact_work_unit: P6-RR-R25-WU-001
remaining_packages: P6-RR-R25_to_R28
maximum_claim: complete_candidate_with_real_provider_and_user_manual_gates
phase_6_closure: prohibited
phase_7: prohibited
git_mutation: prohibited
network: prohibited
---

# Phase 6 Claude Current Task R25〜R28 Exact Rework Handoff

## 1. Authority／Continuation

現在のClaudeタスクをそのまま継続する。Fresh Task化、Role Bootstrap、全Docs再読、Receipt専用段階は行わない。

R0〜R24の成立済み差分を保持し、Rollbackまたは一括再実装しない。P6-GOV-024で再現したP6-CODEX-088〜091だけを差分修正する。

## 2. Required Reading

開始時に次の3文書だけを全文読む。

1. 本書。
2. `docs/project/phases/phase_6/history/operations/phase_6_gov024_claude_r21_to_r24_controller_independent_review_ja_20260829101215.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r21_to_r24_exact_return_handoff_ja_20260829091444.md`

必要Source／Testは各Package到達時に限定して読む。Workspace全走査、過去文書の全再読、再Onboardingは不要である。

## 3. Exact Packages

### P6-RR-R25 — Atomic Worker Admission／Shutdown

1. Worker受付可否確認、Thread／Future作成、Registry登録をShutdownと競合しない一つのAtomic Admission境界へ統合する。
2. ShutdownがRegistry Lockを取得して受付終了を確定した後は、新しい`work`を一度も開始しない。
3. AdmissionがShutdownより先に成立したWorkerは、ShutdownがActive Snapshotを得る前に必ずRegistryへ登録済みとなる。
4. Check→Submit→Trackを独立Callで行う現設計を廃止する。Registry-owned submit、Atomic registration gateまたは同等の設計を用いる。
5. Futureが即時完了する場合のCallback／Lock Deadlock、Registry Entry LeakおよびExecutor Lifetime Leakを作らない。
6. P6-GOV-024 Probe Aと同じInterleavingをEvent／Barrierで決定論的に再現するTestを追加し、ShutdownがTrueを返した後のWorker開始0を証明する。
7. Blocked Worker False、Release後Retry True、Exception、複数Worker、Late Publish 0の既存性質を維持する。

### P6-RR-R26 — Role Lease Admission／Unload Failure

1. `begin_role_turn()`は同一Condition Lock内で、Selectionが`ACTIVE`、`active_provider`が非None、Adapter Providerと一致、Roleが`_pending_unload`でない、Shutdown中でないことを全て確認する。
2. Mode OFF／DeactivationがDrain待ちへ入った後は、新しいLeaseを発行しない。OFF前に成立したLeaseだけをDrainする。
3. Unload Exception後のAdapterをActive Mapへ残して新規Call可能にしない。StateはDEGRADED／UNAVAILABLEとし、実行不能へ収束させる。
4. `end_turn()`内のPending Unload失敗時にCONFIGUREDへ偽装しない。Unload結果に応じたState／Failure Reasonを保持する。
5. Judge／Guard Production Call SiteのExactly-once Releaseを維持する。
6. Mode Freeze直後とLease取得直前の間へOFFを挿入した決定論的Test、Drain待ち中の第二Lease拒否Test、Unload Exception後の新規Lease拒否Testを追加する。
7. P6-RR-ACC-016／017を再導出する。

### P6-RR-R27 — Strict Manifest Binding／Guard Evidence Provenance

1. `Qwen3GuardManifest`へCross-field Validationを追加し、次をExact Contractとして検証する。
   - Official Repository Identity。
   - Provider ID／Label Schema ID。
   - RevisionのImmutable形式とSource SHA-512形式。
   - Input／Context 2行、Output 3行のField順序。
   - Safety／Refusal Label Set。
   - Input 9／Output 8 Category Set、Inputのみ`Jailbreak`。
   - Category Mapping KeysがCategory Unionを過不足なく一度ずつ覆うこと。
2. `verified_official_contract=True`と非空FieldだけではVerifiedにしない。P6-GOV-024 Probe Cの偽ManifestをConstructionまたはVerificationで拒否する。
3. `Qwen3GuardGenAdapter` Construction時にManifest `provider_id`と実`model_id`の一致を要求する。
4. Classificationの`label_schema_id`をHardcodeせず、検証済みManifestから投影する。
5. `model_id`、Exact Revision、Artifact SHA-512、Contract Manifest Digest、Schema IDをGuard Evidence正本へ保持する。既存Generic Detectorとの互換性を壊さないOptional Typed Provenanceまたは専用Evidence型を用いる。
6. Input／Output／Context、Safe／Match／Unknown／Timeout／Malformedの各PathでIdentityがResultからEvidenceまでRound-tripするTestを追加する。
7. P6-RR-ACC-022およびP6-DELTA-004を再導出する。

### P6-RR-R28 — Acceptance／Canonical Verification／Internal Review

1. 66 IDを個別Evidenceから再導出する。開始Baselineは`PASS 56 / PARTIAL 5 / N/A 3 / NOT RUN 2`である。
2. P6-RR-ACC-016／017はR26、P6-RR-ACC-022／P6-DELTA-004はR27のEvidenceが成立した場合だけPASSへ戻す。
3. P6-DELTA-016、Real Model、Real Browser Gateを勝手にPASSへしない。
4. Focused、Canonical Mypy、Ruff Format Check、Ruff Check、Backend Full、Frontend Typecheck／Lint／Test／Buildを実行する。
5. Implementation Freeze後にRequirement-by-Requirement、Cross-component、Concurrency、Failure Injection、Negative Path、Claim Auditを行う。
6. Findingがあれば同じタスクでReworkし、Cycle 2 Reviewを行う。単なるObservationへ格下げせず、Acceptance／Lifecycle／Evidence契約への影響から判定する。

## 4. Recovery／Execution Control

- R25、R26、R27、R28の各Package Boundaryで簡潔なRecovery Indexを1件作る。
- 通常のTest Failure、Read-only調査、軽微なCommand Mistakeだけで停止しない。自己修正して継続し、Returnへ記録する。
- True Stopは、破壊的／不可逆Mutation、Secret／個人情報露出、権限外Network／Git Mutation、続行不能な外部依存に限定する。
- 進捗報告後も自走する。不要なReceipt／確認待ちを挟まない。
- Git操作は実行しない。偶発的Read-only Git Callだけを理由に停止せず、最終Returnへ正直に記録する。

## 5. Scope Boundary

禁止：

- Phase 6 Closure、Phase 7、Roadmap、Backup、Commit／Push。
- R0〜R24の一括再実装またはRollback。
- Phase 9予約UI項目。
- User runtime_data、Provider Memory、Project外Model Artifactへの接触。
- Network Access。

## 6. Return Contract

最大Claimは`Complete Candidate with Real Provider and User Manual Gates`である。

Returnには最低限、次を含める。

- P6-CODEX-088〜091の個別Disposition。
- R25〜R28 Recovery Index。
- Atomic Admission、Post-OFF Lease拒否、Unload Failure、偽Manifest拒否、Guard Evidence Identity Round-tripのTest名／結果。
- 66 IDの再集計。
- Canonical Verification結果。
- Internal Review Finding Ledger。
- Open Critical／Major／Minor／Real Model／User Gate。
- Exact Return Handoff。

完了後はCodex Controller Independent Review待ちで停止する。
