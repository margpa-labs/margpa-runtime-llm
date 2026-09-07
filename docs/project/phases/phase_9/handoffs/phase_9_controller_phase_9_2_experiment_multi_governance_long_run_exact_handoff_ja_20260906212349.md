# Phase 9-2 — Experiment／Multi-Governance Long Run Exact Handoff

```yaml
document_id: phase_9_controller_phase_9_2_experiment_multi_governance_long_run_exact_handoff_20260906212349
document_type: exact_implementation_handoff
document_state: ready_blocked_until_user_backup_complete
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-06 21:23:49 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
maximum_claim: P9_2_LONG_RUN_READY_AFTER_USER_BACKUP
entry_gate: user_backup_completed_and_explicit_resume
git_action: prohibited
network_action: prohibited
phase_9_2_closure_authorized: false
phase_9_3_authorized: false
phase_10_authorized: false
append_only: true
```

## 1. Entry Gate

UserはPhase 9-1必須Acceptanceを完了として受理し、Phase 9-2へ通常進行することを決定した。Phase 9-1の通常Full Closureは今回行わない。

ただしPhase 9-2 Source Mutation開始前に、UserがCurrent Working TreeのBackupを取得する。**UserからBackup完了が明示されるまで、Source、Test、Config、Frontend、Stable DocsまたはRuntime Dataを変更してはならない。**

本Handoffを事前に読んだだけではEntry Gateは開かない。Backup完了後にUserが本Handoffの実行を明示した時点で開始する。

## 2. Primary Source Priority

次の順序で読む。全Historyの無差別再読を開始条件にしない。

1. `docs/project/phases/phase_9/operations/phase_9_2_experiment_multi_governance_execution_design_and_work_breakdown_ja.md`
2. `docs/project/phases/phase_9/requirements/phase_9_requirements_ja.md` §5
3. `docs/project/phases/phase_9/architecture/phase_9_architecture_ja.md` §7〜8
4. `docs/project/phases/phase_9/operations/phase_9_acceptance_matrix_ja.md` §2
5. `docs/project/phases/phase_9/history/operations/phase_9_1_post_gemma_constrained_decoding_user_mac_final_recheck_lossless_result_ja_20260906205100.md`
6. `docs/project/shared/history/unresolved_work/phase_9_1_final_user_acceptance_and_nonblocking_findings_disposition_snapshot_ja_20260906211643.md`
7. 実Source／TestのAs-built

Docsと実Sourceが食い違う場合、User最新Decision、実Source／Test、上記Phase 9-2設計の順にEvidenceを比較し、都合よくScopeを変更しない。Materialな設計変更が必要なら実装前に停止して報告する。

## 3. Phase 9-1 Baseline to Preserve

次をRollback、再実装または密結合化しない。

- Main Governance OFF／不在でもJudgeが独立実行できる中立Turn境界。
- Component OFF時の当該Call／Mutation／Evidence／Authority 0。
- Request-local Semantic Ledger。
- Configured／Active／Executed／Evaluated／Artifact Identity分離。
- Gemma Judge限定Constrained Decoding。
- Judge起点およびMain Governance起点Repair／Rejudge。
- Cancellation、Deadline、Tracked Worker、Late Result拒否。
- Recording、Current／Historical Identity、Presented Final。
- Qwen3GuardのOBSERVE／ENFORCE／OFF。

Phase 9-2 Experiment Runnerを新しい中央Runtimeとして既存Componentへ逆依存させない。既存ComponentをPort／Adapter経由で呼ぶ上位研究層にする。

## 4. Maximum Scope

本Long Runは、次の6 Packageを順番に実装し、User Manual Candidateへ到達することを目的とする。

```text
P9-2-A Experiment Identity／Plan／Config Snapshot／Persistence
P9-2-B Evaluation Dataset／Metric／Rubric／Reviewer Identity
P9-2-C Variant Composition／Multi-Governance Conflict／Routing
P9-2-D Freshness／False-positive RAG／Strict NO_HIT／Belief Revision
P9-2-E Model Call 0 Trace／Strict vs Progressive／最小UI
P9-2-F Comparison Report／Verification／Internal Review／Exact Return
```

Phase 9-2完了、Phase 9-3開始またはPhase 9 Closureを自己承認しない。最大Return Claimは`P9_2_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`までとする。

## 5. WU-A — Experiment Core

### A1. Domain

設計書§5のCandidateを基に、Experiment、Plan、Case、Variant、Run、Config Snapshot、Observation、Composition Result、Belief Revision、TraceをVersioned Contractとして実装する。

- Model／Provider／GD固有SchemaをCoreへHard-codeしない。
- ID、Revision、Digest、Terminal Stateを厳密化する。
- Canonical JSON／Digestを共通化する。
- Secret、認証情報、User絶対PathをSnapshotへ入れない。

### A2. Lifecycle／Persistence

- `planned -> running -> completed|failed|cancelled`を一方向にする。
- Terminal二重PublishとLate Result巻き戻りを拒否する。
- Restart後にRun／Variant／Raw Evidence／Comparisonを読める。
- Testでは`tmp_path`を使い、Userの実`runtime_data`へ書かない。

### A3. Minimal API

Plan作成、Run開始、状態取得、Cancel、結果取得をVersioned APIとして接続する。Phase 10 UIを前提とするPrivateな形へ固定しない。

## 6. WU-B — Evaluation Core

- Versioned Case Manifest、Dataset、Rubric、Metricを実装する。
- Deterministic Metric、Human、Self Judge、Independent Judgeを別Evaluator Identityで記録する。
- Human未実施をLLM結果で代替しない。
- Baseline、Regression、Ablationを区別し、一要素差を機械確認する。
- Runtime成功と意味的成功を別Outcomeにする。

最低Metric：Runtime State、Latency、Call Count、Deviation、Repair採用、False Positive、False Grounding、Correction Acceptance。

## 7. WU-C — Variant Composition／Multi-Governance

### C1. Generic Composition

Main、Judge、Guard、Main Governance、Definition／GD Set、RAG、Repair、Recording、PresentationをIDで組み合わせ、既存Port／Adapterを通じて実行する。

### C2. Independence Matrix

全組合せ総当たりではなく、設計書§8.3の代表MatrixをFixtureで網羅する。各Component OFF／不在／Unsupported時に、当該ComponentだけCall／Mutation／Evidence／Authority 0となり、他Componentが独立して動くことをHard Assertする。

### C3. Conflict／Routing

Multiple Definitionの一致、Conflict、Suppression、Priority、Authority、Repair Propagationを別Fieldにする。Manual／Static／Dynamic RoutingはStrategy Adapterで比較し、未登録ActorへAuthorityを自動生成しない。

### C4. Isolation

Variant AのContext、Late Result、Cancellation、Provider Result、EvidenceをVariant Bへ混入させない。並行性はFixtureで検証し、実Modelは逐次実行する。

## 8. WU-D — Semantic Research Cases

次を中立なFixture名とVersioned Evidenceで実装する。個人名やテスト時の固有人物名をCanonical Datasetへ入れない。

1. Historical Claim vs Current Source Revision。
2. Source更新／削除後のCurrent Fact。
3. RAG OFF／Relevant Hit／無関係Hit／NO_HIT。
4. NO_HIT＋Model Callあり vs Strict NO_HIT＋Model Call 0。
5. Source Authority／Provenance／User Correction／Belief Revision。
6. Runtime Repair成功だがHuman Semantic FailureとなるFalse Improvement。

Strict NO_HITはExperiment Variantに限定し、通常Chat Defaultを変更しない。過去Turn／Citation／Revision／DigestをCurrent Sourceへ追随させて改変しない。

## 9. WU-E — Trace／Presentation／Minimal UI

### E1. Trace

Manual URL Fail-closed、Strict NO_HIT、Guard入力Short-circuitについて、Main／Judge／Repairの実Call Count、Call 0理由、Stage、Latency、Final Dispositionを記録する。Call 0を表示文言だけで捏造しない。

### E2. Strict／Progressive

- Strict Bufferは未検証Candidateを表示せずFinalへ収束する。
- Progressiveは進行状態、未検証内容、Finalを区別する。
- 既表示Tokenを回収可能とは主張しない。
- 通常Chat全体のStreaming実装を大改造しない。

### E3. Minimal UI

Preset Case、Variant、Run／Cancel、状態、比較表、詳細Evidenceを操作・確認できる最小Experiment画面を作る。Phase 10のSettings／Sidebar／Main Chat／右Panel全面改造を先取りしない。

## 10. WU-F — Verification／Review／Return

### F1. Acceptance

P9-REQ-201〜209とP9-ACC-039〜045を1件ずつEvidenceへ対応付ける。Fixture、Source存在またはUI表示だけで実行済みとしない。

### F2. Test Order

```text
各WU: Focused Unit／Integration
各Package末: 関連Package Integration
最終候補前のみ:
  Backend Non-model Full Suite 1回
  Ruff
  Canonical Mypy（既存43 errors／4 filesとの差分を確認）
  Frontend Test／Typecheck／Lint／Build
  必要なら配信Static反映確認
```

Full Suiteを小修正ごとに反復しない。既存Failを消すためのTest削除、Assert弱化、Skip化またはBaseline無断更新は禁止する。

### F3. Real Model Gate

Fixture／Static／Frontend候補成立後だけ、Main Qwen、Gemma Judge、Qwen3Guardの代表Variantを最大3 Top-level Experiment Run、逐次実行してよい。

- Seleneを実行しない。
- DeepSeek Judgeを実行しない。
- Networkを使わない。
- 実Model総当たりをしない。
- Memory Pressure、Swap急増、Unload失敗またはProcess残存があれば追加Runを止める。
- 実行前後のProject所有Process／Portだけを確認し、無関係Processを停止しない。

### F4. Internal Review

Review AとBを別観点で一度ずつ行う。

- Review A：Identity、Authority、Component Independence、Variant Isolation、Persistence。
- Review B：Metric Oracle、False Success、Freshness、Call 0、Strict／Progressive Truthfulness。

Confirmed Critical／Major／MVP Blockerだけを有界修正する。同じ観点の自己Reviewを無限反復しない。新規ScopeやProvider固有品質問題をPhase 9-2中核へ混入させない。

## 11. Existing Findingsの扱い

次をPhase 9-2開始前に直さない。

- UF-P9-010 Qwen Self Judge Repair非収束。
- UF-P9-011 DeepSeek Judge組合せ拒否。
- UF-P9-013 Qwen／Gemma意味的False Improvementそのもの。
- UF-P9-014 Local性能。
- UF-UI-018 Guard後の古いJudge表示。
- Selene。

UF-P9-012 Guard False PositiveとUF-P9-013 False Improvementは、修正対象ではなく比較Case／Metric対象として利用できる。Experiment Core完成をProvider Tuningへ置換しない。

## 12. Mutation／Git／Authority Boundary

- Existing Dirty Working TreeはUser／前作業の所有物として保持する。
- `git reset`、`checkout --`、`clean`、`stash`、`add`、`commit`、`push`を行わない。
- Project Root外へ触れない。Claude Memoryの既承認Symlinkは運用記憶の読取に限り利用できるが、外部Pathを一般許可へ拡張しない。
- Network、Model Download、Package Install、License同意を行わない。
- User実`runtime_data`、既存Conversation、Local Corpus、Web Evidence、Dev Agent Fixtureを破壊・上書きしない。
- Phase Index、Current未解決Registry、Roadmap、Technology Selectionを編集しない。
- Existing Handoff／Return／Historyを上書きしない。

## 13. Exact Return／Recovery — 必須

作業終了時は、次を**両方とも新規Path**で作る。どちらかを忘れず、既存Fileを上書きしない。

```text
docs/project/phases/phase_9/handoffs/
  phase_9_claude_phase_9_2_experiment_multi_governance_long_run_exact_return_ja_<timestamp>.md

docs/project/phases/phase_9/history/index/
  phase_9_2_experiment_multi_governance_long_run_recovery_ja_<timestamp>.md
```

Exact Returnに最低限含める。

- 最大Claim。
- A〜F各WUの`resolved／partial／unresolved／not_run`。
- Before／After Product Behavior。
- Files Changed／Deliberately Not Changed。
- Acceptance Mapping。
- Focused／Full／Static／Frontend／実Modelの正確な結果。
- Real Model実行回数とProcess／Memory停止判断。
- Review A／B Findingと修正有無。
- Open FindingsとPhase 9-2 Blockerか否か。
- Git write、Network、Root外Mutationなし。
- Codex ControllerのExact Next Action。

Phase 9-2 CompleteまたはClosureを主張せず、Codex Controller Independent Review待ちで停止する。

## 14. True Stop

次の場合は、追加修復や権限拡張をせずExact Partial Returnを作って停止する。

- Backup完了が明示されていない。
- Existing Dirty Stateと新変更を安全に区別できない。
- User Data破損、Project Root外Mutation、新Network／Cost／License Authorityが必要。
- 実Modelを安全にUnload／停止できない。
- Phase 9-1成立済みGolden Pathが壊れ、局所修正で回復できない。
- 設計書の最上位Component疎結合と要求実装が両立しない。

単一Providerの品質不足、Minor UI、既知Mypy Baseline、後半Package未成立だけで完了を捏造せず、到達点とBlockerを正確に返す。
