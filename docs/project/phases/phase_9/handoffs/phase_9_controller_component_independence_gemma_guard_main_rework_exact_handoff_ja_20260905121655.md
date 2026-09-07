# Phase 9-1 — Component完全疎結合／Gemma／Guard／Main Rework Exact Handoff

```yaml
document_type: exact_implementation_handoff
document_state: ready
recorded_at: 2026-09-05 12:16:55 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_AND_USER_MAC_FAILURE_REWORK_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. 最上位設計不変条件

MARGPA Runtime LLMの第一価値は、Main Runtime Governance、Guardrail、Judge、Repair、Recordingその他の機能が完全に疎結合であり、各Componentの有無とOFF／OBSERVE／ENFORCEを自由に組み合わせて実験・検証できることである。

```text
Component AのOFF／不在／空定義
  != Component Bの起動条件欠落
  != Component Bの内部Context欠落
  != Component BのFailure
  != Component Bの暗黙Activation
```

OFFは当該Component自身のCall、Mutation、Evidence、Authorityを0にする。他Componentの前提初期化まで止めてはならない。Component間で共有してよいのは、Mode非依存の中立Port／Contract／Turn Correlationであり、一方の内部CoordinatorやModeを他方の必須条件にしてはならない。

Main Semantic ENFORCEが意味評価結果を必要とすることと、Judge単独利用がMain OBSERVEを必要とすることは別である。前者は明示Composition、後者は不正なActivation依存である。

## 2. 確定Failure

Current ProductionではMain Governance PREがOFFなら早期Returnし、`begin_semantic_turn()`を呼ばない。一方、Dedicated Judge共通Dispatchは`SemanticTurnSnapshot`がないと`semantic_snapshot_unavailable`で失敗する。Production CompositionはSnapshot Providerを`runtime_governance_composition.semantic_runtime`へ直接接続している。

Repository履歴上、この結合はCommit `fe034845`（2026-08-29 17:31:40 JST、Phase 6 checkpoint）で入った。同時期のController Review／Regressionは「Main Governance OFFでもJudge Modeは独立してOBSERVE／ENFORCEできる」を正規契約としているため、Current Sourceは既存契約と矛盾する。

加えて、2026-09-05 User Mac実画面Recheckでは次が確定した。

- Gemma通常初回JudgeはOBSERVE／ENFORCE／Main ENFORCE起点の全経路で`malformed_output`、evaluated 0。
- Backendで成立した実Gemma 32 Criterion Rejudgeは直接Rejudge経路だけの限定Evidence。
- Qwen3Guardの明確なPrompt Injectionに対する基本OBSERVE／ENFORCEは成立。
- 同一benign検証入力はGuard ENFORCEでMatch 1／Action 1、OBSERVEでMatch 0／Action 0となり、Mode間分類不一致と過剰介入の疑いがある。
- Main-shared Qwenの次TurnはUser Stop報告なしで`cancelled_by_request`となった。
- `judge_run_evidence`のindependent Judge RunでUI ExecutedはGemmaだが、保存`metadata_fields.model_identity`はMain Qwenだった。

## 3. WU-01 — 独立Turn Context境界

まずRegressionを作り、Current Sourceで意図どおり失敗させる。

最低Matrix:

1. Main OFF＋Dedicated Judge OBSERVE。
2. Main OFF＋Dedicated Judge ENFORCE、Repair OFF。
3. Main OFF＋Dedicated Judge ENFORCE、Repair ENFORCE。
4. Main OBSERVE／ENFORCE＋Judge OFF。
5. Main定義0件またはMain Composition不在＋Dedicated Judge ON。
6. Guard OFF／OBSERVE／ENFORCEを上記へ組み合わせてもJudge起動可否が変わらない。

最小修正で、Criterion Freeze／Request Correlation／Language／Dialogue／Evidence ContextをMain Governance Modeの内側から分離する。具体名やClass追加は固定しないが、次を満たすこと。

- 中立なEvaluation Turn境界が必要ContextをFreezeする。
- JudgeはMain OFF／不在でも独立して実行できる。
- 109 Criterionを使う場合は中立なCriteria Provider Portから取得し、Main内部Snapshotへ依存しない。
- Criteria Provider不在／0件なら、Judge自身の汎用品質評価へ明示的に収束し、Mainを暗黙ONにしない。
- Main OBSERVE／ENFORCEは同じTurn Resultを任意に消費できるが、Main OFFならMain Evidence／Action 0。
- Main定義0件でもJudge／Guard／Recordingへ影響0。
- Judge OFFでもMain structural Observe／Enforceは独立する。現行Semantic ENFORCEのJudge要件は、Userが許容した意味評価レイヤーの明示条件としてのみ残す。

全81組合せへ重い実Modelを回さない。Mode／Call／Authority不変条件はFixtureのParameterizeで確認し、実Modelは代表経路だけに限定する。

## 4. WU-02 — Gemma通常初回Judge

Production Decoder緩和、JSON補修、盲目的Retry、予算再拡大の前に、通常初回JudgeのBatch単位Test-only Observabilityを追加する。

記録対象:

- Batch index／期待Criterion ID。
- `max_new_tokens`、Prompt／Completion Token、`finish_reason`、生成時間。
- Raw長／SHA-512。Raw全文は保存しない。
- Strict Decode成功／`JudgeDecodeError.reason`。
- decoded ID、missing／extra／duplicate ID。
- Structured生成Parameter（temperature、top_p、top_k、seed等）。

実画面失敗Evidenceは4件すべて`call_count=1`なので、最初の8 Criterion Batchで停止した可能性を優先確認する。実機再現は完全Logを保存して1回。原因が確定した場合だけ最小修正を行い、修正後は最大2回までで次を確認する。

1. Main OFF＋Gemma OBSERVEがcompleted、evaluated > 0。
2. Main OFF＋Gemma ENFORCE＋Repair ENFORCEがJudge→Repair→同一Gemma Rejudge→採用。
3. 既存Rejudge 100 Token／Criterion、総Budget 3600を維持。

Structured出力のSampling固定が必要なら、Judge／Guard共通Defaultを全Modelへ一括変更せず、Role別Parameter Contractとして局所化する。

## 5. WU-03 — Qwen3Guard Mode非依存分類

ModeはDetection結果を変えず、Action Authorityだけを変えるべきである。現在Adapterは`max_new_tokens`以外を指定せず、汎用Generation Default（temperature 0.7、top_p 0.8、top_k 20、seed unpinned）を継承している。これを原因と断定せず、先に同一Input／同一Target／同一Provider条件で検証する。

- 明確なPrompt Injection: OBSERVEとENFORCEで同じMatch。Actionだけ0／1。
- benignな検証入力: 両ModeでClear。
- Mode値をModel Prompt／Decodeへ混入させない。
- 必要ならQwen3Guard Role専用の確定的Generation Parameterを導入する。
- 既存Category／Strict Decoder／Failure分類を緩めない。
- 拒否文二重表示は今回のBlockerと分ける。極小修正でなければ未解決維持。

## 6. WU-04 — CancellationとEvidence Identity

User Stop報告なしの`b252ec07-4aad-40a1-b5eb-aa68b0fa62c9`が`cancelled_by_request`となった経路を、Client disconnect、SSE close、Main-priority preemption、Mode変更、Deadline、明示Stopに分離する。真因を確認せず表示文言だけ変えない。

Judge Evidenceの`model_identity`も契約を確定する。

- 評価対象MainのIdentityならField名／UI説明を曖昧にしない。
- 実行JudgeのIdentityならGemmaを記録する。
- Configured／Active／Executed／Evaluated Modelを一つのFieldで混同しない。

## 7. WU-05 — Main起点RepairのProduction成立

WU-01〜04成立後、次をProduction Web Compositionで確認する。

```text
Main Governance: ENFORCE
Judge: Gemma ENFORCE
Repair: OFF
Guard: OFFまたはOBSERVE
Recording: FULL
```

明白なDeviationに対し、`repair_requested_by=main_governance`、Repair improved、同一Frozen Criterion Rejudge、採用、同一Turn保存まで確認する。Guardの誤Blockで代替しない。Main Structural 109件をJudge非依存で直接矯正するPhase 11以降の再設計とは区別する。

## 8. Verification／Review／停止線

- Focused Unit／Integration、Backend Full、Ruff、Canonical Mypyを実行する。
- Frontend変更時だけFrontend Test／Typecheck／Lint／Build／配信Staticを検証する。
- Internal Review 1: Component Independence／Mode／Authority／OFF Call 0。
- Internal Review 2: Model出力／Decode／Budget／Cancellation／Evidence Truthfulness。
- Review Findingは局所Rework後、観点を入れ替えて再Reviewする。
- User Mac再確認前にPhase 9-1 Completeを主張しない。

## 9. 禁止事項

Selene修復、Phase 9-2／9-3、Phase 10、全面Rollback、Context拡張、Decoder緩和、無制限Retry、Git add／commit／push／stash、既存Handoff／History上書きは禁止。新規Handoff／Return／Recoveryは必ず新規Pathへappend-onlyで作成する。Current Registry／Phase Indexは編集しない。

