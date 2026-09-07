# Phase 9-1 — Component完全疎結合 R4収束Rework Exact Handoff

```yaml
document_type: exact_implementation_handoff
document_state: ready
recorded_at: 2026-09-05 19:50:51 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_claude_component_independence_r3_residual_rework_exact_return_ja_20260905193256.md
review: ../history/operations/phase_9_1_component_independence_r3_return_controller_review_ja_20260905195051.md
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_R4_CONVERGENCE_REWORK_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. 目的と不変条件

R3をRollbackしない。解決済みのProvider Mismatch Gate、Built-in Artifact分離、Preemption起源、Gemma deterministic sampling、Production Root Fixtureを保持し、Reviewの残差だけを修正する。

```text
Component OFF／不在／空定義
  => 当該ComponentのCall／Mutation／Evidence／Authority 0
  => 他Componentの起動／Context／Evidenceを欠損させない

Turn Snapshot／Failure／Evidence
  => request_id + generationに帰属
  => 別Turn開始で上書き・再Freeze・誤相関しない
```

## 2. R4-WU-01 — request-local Semantic Turn Ledger

`JudgeSemanticTurnProvider`の単一失敗スロットと`SemanticRuntimeCoordinator._current`だけに依存する形を廃止し、request-localにSnapshot／Freeze Failure／Evidence相関を保持する。

- 同一requestの成功済みSnapshotは、別request開始後も同じgeneration／digestで返す。
- 開始Freezeに失敗したrequestは、別request成功後もLive値を再読せずCall 0／`None`を維持する。
- AのBackground Judge ResponseがB開始後に到着しても、AのSnapshotへ記録する。BのCurrent表示／Snapshotへ混入させない。
- UI向けLatest Current Pointerと、実Turn Ledgerを分離する。
- Lock下で重複Begin／同一request競合を防ぐ。無制限の一時State増殖は避け、既存History契約と整合する明示的なTerminal／Bounded保持方針を持つ。
- Main OFF／absentのMain Semantic Evidence Call 0は維持する。

Controller Review §3の三ProbeをそのままRegression Test化する。さらに二Threadが同じrequestを同時Beginしても一つのgenerationだけが得られることを確認する。Sabotageで単一スロットへ戻すと失敗することを示す。

## 3. R4-WU-02 — Judge Identity三経路Matrix

Dedicated Gemma、Main-shared Qwen、Built-in Deterministicそれぞれについて、実保存JSONで次を直接Assertする。

- `evaluated_model_identity`
- `configured_judge_provider`
- `active_judge_provider`
- `model_identity`（Executed）
- `artifact_digest_sha512`／`backend_key`／`backend_version`

Built-in Testにも本物のSemantic Snapshot Fixtureを渡し、Configured／ActiveがBuilt-in、ExecutedもBuilt-in、Artifact／Backend／Versionが`unavailable`になることを確認する。Main-sharedとDedicatedはExecuted Runtime自身の値を使う。実Modelは不要。既存Evidence Schemaは変更しない。

## 4. R4-WU-03 — Cancellation Terminal Arbitration

Cancellation検知時に再利用してよいWorker Terminalは、既に起源を確定した`execution_state=cancelled`だけに限定する。任意の`failed`結果はUser Stop／Main-priority Cancellationを上書きしてはならない。

- Worker Failure Ready → User Stopの固定Scheduleで、最終結果が`cancelled_by_request`になる。
- Worker Failure Ready → Main-priority Preemptionの固定Scheduleで、最終結果が`cancelled_by_main_priority_preemption`になる。
- R3で成立したWorker自身のPreemption Cancellation保持Testは維持する。
- Deadline、Evidence Publication不採用、Lease／Bookkeeping cleanupを退行させない。

Model Call数、Deadline、Cancel Graceは変えない。

## 5. R4-WU-04 — Gemma専用Compact Criterion Schema

共有Decoderを先に確認し、`reason_code`／`evidence_refs`が省略可能である現契約をTestで固定する。そのうえでGemma専用Prompt SchemaのCriterion entryを次の三Fieldだけにする。

```json
{"criterion_id":"exact id","disposition":"pass|deviation|unknown","confidence":"0..1"}
```

- Gemmaへ`reason_code`／`evidence_refs`を出力させないことを明示する。
- Overall `reasoning`は既存どおり保持してよい。
- Selene Prompt、Main-shared Prompt、共通Decoder、Domain Modelは変更しない。
- Decoder tolerance、JSON補修、Raw文字列からの推測採用、Retryは追加しない。
- 「二Fieldが直接原因」と先に断定せず、本修正で成立した範囲だけClaimする。

UnitでGemma SchemaのKey集合が三Fieldだけであること、当該出力を現Strict Decoderが受理すること、Selene Schemaが不変であることを確認する。

実機は、Deviationを必ず含む通常32 Criterion初回Judgeを同一条件で最大2 Trial。各Batchのfinish reason、completion tokens、Raw length／SHA-512、Decode state／reason、ID数だけをTest Logへ出し、Raw全文はDocsへ転記しない。一回でもMalformedなら、そのEvidenceを返して停止する。2/2成立時だけR4-WU-05へ進む。

## 6. R4-WU-05 — Production Root Golden Path再確認

Fixtureの`dedicated_role_load.context_size`を実Gemma配置と同じ8192、またはRegistry／Profileから導出した値にし、32 Criterion Repair→同一32 Rejudgeが引き続き成立することを確認する。32768固定で成功させない。

R4-WU-04が2/2成立した場合のみ、実`build_phase1_web_runtime()`のGolden Pathを最大1 Trial実行する。

```text
Main Governance: ENFORCE
Judge: Gemma ENFORCE
Repair: OFF
Guard: OFF
Recording: FULL
Criteria: 通常選択32
```

初回Deviation、`repair_requested_by=main_governance`、Repair improved／accepted、同一Gemma・同一32 Criterion Rejudge、Presented Final、同一Turn保存、Judge EvidenceをHard Assertする。Missing Artifact以外をSKIPしない。

## 7. R4-WU-06 — Verification／Review／Return

- Focused Unit／Integration、Backend非Model Full、Ruff、Canonical Mypyを実行する。
- Internal Review A: request-local Ledger／Freeze failure／重複Begin／Late A after B。
- Internal Review B: Identity Matrix／Cancellation Arbitration／Gemma Strict Decode／Production Root。
- ClaimはFixtureとRealを分け、実機一回からRoot Causeを一意断定しない。
- Exact ReturnとRecoveryは必ず新規Pathへ作る。既存Handoff／Return／History／Phase Indexを上書き・直編集しない。

## 8. 禁止事項

Selene修復／実機実行、Phase 9-2／9-3、Phase 10、全面Rollback、Context／Budget／Criterion上限変更、共有Decoder緩和、JSON補修、Retry追加、Native更新、Download、新Resource Gate、Git add／commit／push／stashは禁止する。

Return後はCodex Controller Review待ちで停止する。Phase 9-1 Complete、User Acceptance、次Phaseへ進まない。
