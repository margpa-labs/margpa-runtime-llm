# Phase 9-1 — Judge／Governance実行接続 Rework Handoff

```yaml
document_id: phase_9_claude_p9_1_judge_and_governance_rework_20260904173639
document_type: exact_bounded_implementation_handoff
document_state: ready_for_claude_execution
created_at: 2026-09-04 17:36:39 JST
language: ja
from: Codex Controller
to: Claude_current_task
phase: phase_9
program: phase_9_1
authority: bounded_source_test_config_and_return
internal_review_cycles: 2
cancelled_work_unit: WU_04_runtime_settings_persistence_by_latest_user_decision
maximum_claim: P9_1_REWORK_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_closure_authority: false
git_mutation_authority: false
network_authority: false
```

## 1. 現在地と今回の決定

[Claude統合報告](phase_9_claude_p9_1_full_history_consolidated_handoff_for_codex_ja_20260904170647.md)をCodexが全631行読了。Round 6の①②④⑤⑥、2273 passed／22 deselectedはClaudeの成果候補であり、独立Review・User Acceptance済みとはしない。既存Working Treeを起点とし、完了部分を再実装しない。

現在のSourceでも、Main Governanceの意味評価結果を返すRecorderの戻り値がJudge Dispatch側で捨てられ、Main独自のRepair起点として使われていないことを確認した。Seleneの残存`generation_failed`は原因未確定。一般的なFailure Codeだけで反復検知・Memory不足・Native障害のいずれかと断定しない。

Userは、Main Governance ENFORCE自身を修復許可とし、既存Repair Modeとは起点別に分ける方式を承認した。構造レイヤー／意味評価レイヤーの分離は[Phase 11以降の予約](../../../shared/history/planned_work/phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_ja_20260904172003.md)のまま。今回の意味評価→Repair接続を延期しない。

## 2. Scope・権限・停止境界

- 既存Claude Taskを継続する。本HandoffのWU-01／02／03／05と、その直接回帰だけを実装する。WU-04は最新User指示で取り下げ済み。運用ルールの通常二周Reviewを使い、三視点×無制限Roundや複数Agentの並列稼働へ拡張しない。
- Project内の関連Source／Test／Config／Frontend／生成Static、結果記録を変更可。Gitはread-only。Stage／Commit／Push／Branch変更／Restore／Stashは禁止。
- 設計条件は本書で確定する。Helper名・Test配置等の詳細は自己判断し、逐次確認しない。条件を満たせない場合だけ、証拠と代案を返す。
- 既存Registryが解決する承認済みローカルModel Root配下のMain Qwen／DeepSeek、Selene、Gemma、Qwen3GuardのArtifact読取・Load・Inference・Unloadを、今回の実証に限り許可。新規取得、Artifact変更、Root外の一般探索は禁止。
- 実機試験はTask所有の隔離プロセスとFixture Storeを使う。Userの稼働Server、既存Conversation／Consent／Local Corpusを操作しない。OS再起動、他App終了、全Process killを要求・実行しない。
- User実Dataを直接編集して成功を作ることは不可。Testは隔離Fixtureだけを使い、Runtime設定の永続化は今回追加しない。
- Claude Memory／Project `.claude/`は最新運用ルールの許可済み補助状態。過去Handoffの禁止へ戻さず、正本や完了証拠にも使わない。
- `SystemMemoryRoleResourceGate`再配線、新Memory推定式、Model入替、Phase 9-2以降、Constitution編纂、Roadmap／公開Docs更新、保留Hardeningは対象外。
- User STOPは即時停止。未許可領域・破壊的変更・繰り返すNative Crash／回復不能Workerなどの実質的危険では当該試験を止める。独立して安全なWUは継続し、未解決をPASSへ変更しない。

## 3. 最小ReadingとPreflight

本Handoff、統合報告§5〜8、現在のClaude運用三文書を使う。同一Taskで確認済みの背景は再利用し、全History／全Indexを毎工程読み直さない。新Task／Compaction時は必要な運用・Recovery文書を再取得する。

`git status`と対象差分から他者変更を識別する。実装前に対象Testの現状と失敗原因を記録し、2273という件数自体をAcceptanceにしない。以下のSourceと直接の呼出先／Testだけを必要に応じて読む。

- `bootstrap/judge_live_integration.py`、`repair_live_integration.py`、`runtime_governance.py`、`web_application.py`
- `modules/runtime_governance/application/semantic_runtime.py`、Repair Eligibility／Budget／結果Contract
- `adapters/model_backends/llama_cpp/{adapter,stream,repetition}.py`、`adapters/evaluation/selene.py`
- `modules/evaluation/application/judge_output_decoder.py`
- `bootstrap/{phase1_application,config_loader}.py`、必要なRuntime Model Controller／Routes
- `frontend/src/App.tsx`、`FeatureModesPanel.tsx`、`ProviderSelectionPanel.tsx`、`RuntimeModelStatusPanel.tsx`、`SettingsModal/`

## 4. WU-01 — Selene残存Failureの特定と局所修復

1. Main 16384／Dedicated 8192の現設定から、報告と同じ経路で生Exception型・`InferenceError.details`・Failure地点を採る。内容を保存する場合は合成入力を使い、秘密やUser会話を含めない。
2. 初回失敗と、FAILED Latch後の二次失敗を分ける。1回のLoad内で3回失敗しても「独立した3回再現」と数えない。MainとDedicatedの実Instance、実Context、残存Workerを記録する。
3. 初期再現は最大3試行まで。Crash・回復不能なら反復しない。原因が未確定なら検知器無効化・閾値緩和・Context無制限拡大・Resource Gate新設で隠さない。
4. 根拠のある局所修正と、修正前に意図した症状で失敗するRegressionを作る。Repetition／Native例外／正常終了を区別し、Mainの正常利用とOFF→Unload後の再利用を壊さない。
5. Selene実推論と結果Decodeが成立することを再確認する。Active表示、Load成功、即時Fallbackだけでは完了不可。未成立なら原因・条件・残件を明記して返す。

## 5. WU-02 — 矛盾した複数JSONを先頭優先で成功化しない

Codex確認：`test_decode_multiple_json_objects_uses_the_first_well_formed_one`は、`accept`のObjectに`needs_repair`のObjectが続いてもACCEPTを期待し、現SourceでPASSした（1 passed、0.07s）。これは仕様への適合を証明しても、判定の正当性を証明しない。今回の修正対象とする。

- Wrapperや同一Objectの重複を扱う場合も、異なる有効な判定が複数ある時に先頭・最大Confidence・都合のよい結果を黙って採用しない。曖昧な場合は既存Typed Failure／UNKNOWNへ収束させる。
- Criterion単位のObject分割を扱うなら、期待IDの全件性・一意性・競合なしを検証した場合だけ統合する。大きなParser再設計は不要で、曖昧な形式を無理に救済しない。
- 完全な`criterion_results`からRecommendationを導出する既修正は維持する。欠落、重複、矛盾、切断JSONをPASSへ補完しない。
- 少なくとも「先頭PASS・後続DEVIATION」「逆順」「同一内容重複」「Criterion不足」「正常単一Object」を区別してTestする。旧Testの期待値訂正はこのContract変更に基づくものと記録する。

## 6. WU-03 — Main Governance起点の意味Repairを接続する

### 許可Matrix（開始時にFreeze）

| Main Governance | Judge | 既存Repair Mode | 今回の動作 |
|---|---|---|---|
| OFF／OBSERVE | ENFORCE | ENFORCE | 既存Judge起点Repairを維持。Main起点は生成しない |
| OFF／OBSERVE | ENFORCE | OFF／OBSERVE | 自動Repairを増やさない |
| ENFORCE | ENFORCE・Active | OFF／OBSERVE | GD意味違反があればMain起点でRepairする |
| ENFORCE | ENFORCE・Active | ENFORCE | 要求元を合流し、同じCandidateのRepairを二重実行しない |
| 任意 | OFF／利用不能 | 任意 | 現行Main ENFORCE準備条件を維持。Judgeなしの構造矯正を今回導入しない |

- 既存Repair Modeを内部でENFORCEへ書き換えない。許可元（Judge／Main Governance）を明示した共通Repair要求を作り、共通Executor／Budget／Cancel／Rejudgeを再利用する。個別GDやModel名をCoreへ固定しない。
- `semantic_result_recorder: Callable[..., object]`の戻り値放棄を、型付き結果／要求の受渡しへ置き換える。Semantic評価を再度呼ぶだけの二重経路は作らない。
- `false_enforce_prevented`のJudge ENFORCE・Active条件は維持する。今回変更するのは、Main自身の修復許可を`frozen_repair_mode == enforce`へ従属させている部分と、その実行接続である。
- 同一TurnのFrozen Request／Candidate／Criterion／Provider／Budgetを使い、違反したRuleとその理由から修正を要求する。Guardrail・Authority Denyはどちらの修復要求でも解除しない。
- Deviation＋UNKNOWNなら既知の違反を修復する機会は残すが、UNKNOWNを合格に変えない。再評価結果と既存採用条件に基づき採用する。
- 正経路は「違反→Repair→同一Judge Identityで再評価→改善回答をPresented Finalへ採用」まで。Block／Observe／FallbackだけでMain ENFORCE成立としない。失敗時の安全なFallbackは保持する。
- `executed_disposition`やUIのAction数を、要求しただけで実行済みにしない。実行・再評価・採用結果へ相関させる。既存結果欄に修復起点を最小限表示し、Repair OFFなのに無断実行したように見せない。
- UnitのResolverだけでなく、Production Compositionと通常Conversation完了経路を通すTestで上記Matrix・二重実行なし・Stop／Late結果不採用を示す。

## 7. WU-04取り下げ — Context／max_new_tokensの保存は対象外

Handoff作成中、UserはDedicated ContextがMainとは別の8192設定であることを確認し、2項目の永続化を取り下げた。未実装のまま今回のScopeから除外する。将来の必須作業にも自動昇格させない。

現Sourceでは`RuntimeModelController`はProcess-localで、通常起動時はMain Context 16384／Current max_new_tokens 4096（明示Overrideなし）、Output上限8192。専用モデルのContextは`dedicated_role_load_overrides`により別途8192。画面でMainを8192に下げてから再起動することをSelene利用の前提にしない。ただし、この設定分離だけでSelene残存Failureの解決を主張しない。

## 8. WU-05 — UF-UI-017の最小修正

Judge Mode／Providerの準備状態が変わった後、Main Governanceの可用性をServerから再取得する。Backendの条件を外したり、Buttonだけ強制有効化したりしない。

`FeatureModesPanel`・`ProviderSelectionPanel`からの必要な状態更新通知と、既存`App.loadRuntimeGovernanceStatus()`を使う小修正を基本とする。OFF→ENFORCEをOBSERVE経由なしで選択できること、Judge OFF／失敗後の無効化、遅延した古い応答、取得失敗をTestする。無関係な全Panelの作り直しが必要なら、このWUだけ未解決で返してよい。

## 9. 検証・内部Review・Return

順序はWU-01→02→03→05（WU-04は取り下げ）。各原因・境界が確定したら進み、進捗報告や小Package完了だけで停止しない。WU-01の実機障害が残っても、他Provider／Fixtureで安全に独立検証できるWUは進める。

- 各WUで修正前Failure→修正後PASS、Production配線、Negative Pathを示す。既存2273件の件数合わせやFixture期待値だけの変更で成立扱いにしない。
- 最終Backendは`./.venv/bin/pytest -q`、`./.venv/bin/mypy src tests`、`./.venv/bin/ruff check`。実行対象・Deselected・既知Failを正確に記録する。結果未確認ならCleanと書かない。
- FrontendはTest／Typecheck／Lint／Buildを実施し、配信Staticも更新する。全Suiteは最終Freezeでまとめ、各編集後に無条件で全件再実行しない。
- 実Modelは一組ずつ逐次実証する。Main＋Seleneの修復、Main＋Gemma、Main-self、Qwen3Guardの既存正経路に必要な範囲とし、同時に全ModelをLoadしない。Model使用不能をBuilt-inやMockの成功へすり替えない。
- 内部Review 1：要件・Mode Matrix・実行配線・Presented Final・User視点。内部Review 2：異常系・並行性・Lifecycle／Restart・Test Oracle・証拠の独立性。各回のFindingを修正して確認し、二周後の重大残件はIncompleteで返す。自己ReviewをIndependent Reviewとは呼ばない。
- 成功済み正経路の未成立・重大残件・必須実機NOT RUNがあるなら、最大Claimは`P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW`。コード上の修正完了だけでPhase 9-1の完了を宣言しない。
- 手法・Failureの長大な再まとめ、Instruction専用Doc、全履歴の複写は不要。結果／Finding／実行Evidence／手順変更をExact Returnへ集約し、Recoveryは一つの現在地から必要時だけ追記する。元Historyは変更しない。
- ReturnにはWU別PASS／FAIL／NOT RUN、既修正分の回帰、実Machine条件・例外、Mode別修復起点、Main／Dedicatedの実Context、実際に存在するUIだけを使う短い再確認手順を含める。内部Call数・Worker・Digest等は実行側が証明し、Userへ存在しない画面項目の確認を頼まない。
- Return後は停止してCodex Independent Reviewを待つ。Userの実画面Acceptance、Phase Closure、Git、次Phaseには進まない。
