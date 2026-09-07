# Governance Component独立性／Repair Trigger／Selene延期 統合予約

```yaml
document_id: governance_component_independence_repair_trigger_and_selene_deferral_reservation_20260905171547
document_type: cross_phase_architecture_assessment_and_planned_work_reservation
document_state: recorded_and_reserved_not_started
language: ja
recorded_at: 2026-09-05 17:15:47 JST
decision_authority: user
authority_owner: Nazuna Research
current_phase: phase_9_1
future_target: phase_11_or_later
phase_10_plan_changed: false
implementation_authority: not_granted_by_this_document
mvp_priority: preserve_mvp_first
selene_status: unresolved_deferred_non_blocking
append_only: true
```

## 1. 記録範囲

本記録は、Phase 9-1のComponent完全疎結合Reworkを受けて、Userが次を確認した会話から、その後のSelene延期判断までをLosslessに整理したものである。

> Main Governance ENFORCEによるRepair要求は一旦は仕方ないとして、それ以外は完全疎結合気味に順調に戻せそうか。大きな工数をかけず、全部独立で動かせそうか。

同じ会話では、次の論点も扱った。

- Judge起点Repairと、GD系起点Repairの位置づけ。
- ARGD／DAGD等の構造レイヤーが持つ本来の価値。
- Runtime Constitutionを構造レイヤー／意味評価レイヤーへ分ける方針。
- 各Componentを自由に組み合わせられるPlatformとしての独自性。
- Seleneの既知Evidence、未確定原因、修復工数および実用性。
- SeleneをMainからさらに分離すれば診断・修復可能性が変わり得るが、現在は保留するというUser判断。

## 2. 今回の結論

現時点の見立てでは、**Platform全体の全面Rollbackや全面再設計をしなくても、主要Componentを再び独立して組み合わせられる構造へ戻せる可能性が高い**。疎結合そのものの修復は局所〜中規模であり、現在のPhase 9-1 Rework全体が中規模になっている主因は、Gemma実機安定性、Evidence Identity、Cancellation、Production Composition等も同時に検証しているためである。

ただし、「すでに全Componentの完全独立性が成立した」とはまだClaimしない。Main OFF時のEvidence所有権、Turn Snapshot、Identity、Cancellation、通常Web経路を含む組合せMatrixが最終確認を通るまでは、**回復可能性が高く、回復作業が進行中**という位置づけにする。

Phase 10 MVPの既定計画は変えない。物理的に完全な構造／意味評価分離と競合調停の本実装は、既存予約どおりPhase 11以降を基本とする。

## 3. 変えてはならない最上位の独立性契約

MARGPA Runtime LLMの中核価値は、各Componentが存在する／しない、ON／OFF、成功／失敗にかかわらず、残るComponentを自由に組み合わせて実験・検証できることである。

```text
あるComponentがOFF／不在／空／失敗:
  そのComponent自身のCall      = 0
  そのComponent自身のAction    = 0
  そのComponent自身のEvidence  = 0
  そのComponent自身のAuthority = 0
  他Componentの起動条件・結果・Evidence所有権へ暗黙の影響を与えない
```

共有してよいのは、中立な契約、明示されたPort、Frozen Turn Context、Budget／Deadline／Cancellation等の共通Primitiveである。特定のComponent、Provider名、Mode、Evidence Storeを、別Componentの暗黙の親として扱わない。

特に次を守る。

- Judge OBSERVE／ENFORCEは、Main Governance OBSERVEを先に有効化しなくても独立実行できる。
- Main GovernanceがOFFなら、Main Governance自身のSemantic Evidenceを作らない。
- GuardはJudge、Main Governance、ConstitutionのModeに依存せず独立分類・介入する。
- Recordingは他Componentを起動・成立させない受動的な記録Componentとする。
- ConstitutionとGD群は互いを親子関係にせず、個別にON／OFF／交換できる。
- UIの可用性表示も、隠れたMode順序や古い状態を成立条件にしない。

## 4. Repairだけに必要な接続関係

Repairは自発的に何を直すか決められないため、何らかの評価・規則・User操作から明示的なTrigger／Requestを受ける必要がある。この関係そのものは密結合ではない。

問題になるのは、Repairが「Judge専用品」「Main Governance専用品」のように、特定の呼出元へ固定されることである。目標は、呼出元に依存しない共通のRepair Request Portである。

```text
Judge ───────────────────┐
GD Semantic ─────────────┼─> neutral Repair Request Port ─> Repair ─> optional Re-evaluation
Constitution Semantic ───┤
Main Governance Semantic ┘
```

将来のRequestには、少なくとも次の意味境界が必要になる。ただしField名やClass設計は本記録では確定しない。

- Request／Turnの相関Identity。
- Trigger Origin（judge、main_governance、gd_semantic、constitution_semantic等）。
- Frozen Criterion／Evidence／Candidate Identity。
- 許可されたAuthorityと提示結果の扱い。
- Budget、Deadline、Cancellation、最大Repair回数。
- Repair後に誰が再評価するか、または構造判定だけで完了できるか。

Main Governance ENFORCEが現在Repairを要求する関係は、Phase 9-1／MVPでは一旦許容する。ただし最終構造では、Main GovernanceがJudgeの内部実装へ直接依存するのではなく、中立Portを通じて要求する。

## 5. Judge、GD、Constitutionの役割差

### 5.1 Judge起点Repair

LLM-as-a-JudgeがCandidateを評価し、Deviationを根拠にRepairを要求し、必要ならRejudgeして採用可否を決める流れは一般的な構成である。本Platformでも、この経路は独立した一つの機能として維持する。

### 5.2 GD系起点Repair

ARGD／DAGD等のGovernance Definitionが意味評価結果からRepairを要求する経路は、Judge単体の品質評価よりも、明示されたGovernance Sourceを実行Authorityへ接続する点に特徴がある。これはPlatformの強い独自性候補である。

ただし「世界で前例がない」とまではClaimしない。独自性の本体は、個々の仕組み単独ではなく、複数のGovernance Source、構造制御、意味評価、Repair、Rejudge、Authority、Frozen Evidenceを交換可能に組み合わせる全体構造にある。

### 5.3 GD系の構造レイヤー

GD系の本領は、JudgeやRepairを必要とせず、Runtimeで直接適用可能な規則を入力構築・生成制御・出力制約・Action許可等へ反映し、**最初からModelを矯正する**構造レイヤーにある。

現行ARGD／DAGD由来109 Criterionは、調査時点ではすべてSemantic評価へ委譲される形であり、この本来の構造レイヤーはまだ成立していない。Phase 11以降、規則を直接制御可能部分と意味評価必須部分へ再分類する。

### 5.4 Runtime Constitution

Runtime ConstitutionもGD系と同じく二つへ分ける。

- 構造レイヤー: JudgeなしでRuntimeへ直接適用し、可能な範囲でModel／Actionを事前・実行時に矯正する。
- 意味評価レイヤー: Constitutionの意味評価結果から中立Portを通じてRepairを要求し、必要なら再評価する。

GD群とConstitutionは同じ二層原則を採用しても、別Componentのまま維持する。両者が同時に有効な場合のAuthority、優先順位、Conflict、Merge、Failure収束は明示的な調停契約で解決し、相互の内部実装へ依存させない。

## 6. 現在の疎結合Reworkの規模感

現在見えている修正は、主に次の境界へ限定できる。

1. Main Governance専有だったSemantic Turn開始／Snapshotを中立なTurn Contextへ移す。
2. Main OFF時はMain Evidenceを生成しない。
3. Dedicated Judgeの実行Identity、評価対象Identity、Artifact／Backend Identityを分ける。
4. Repair Triggerを呼出元非依存の契約へ寄せる。
5. Cancellation／Preemptionの原因と所有権を一回限りの暗黙状態に依存させない。
6. Main、Judge、Guard、Repair、RecordingのON／OFF組合せMatrixをFixtureとProduction Compositionで検証する。

したがって、Phase 9-1で必要な「独立して起動・評価・停止できる状態へ戻す」修正は、現時点では局所〜中規模と判断する。Phase 11以降のGD／Constitution規則再分類、構造Compiler／Evaluator、競合調停、UI／Evidence分離は別の大きな設計作業である。

隠れた依存が追加で発見される可能性は残るため、工数を固定値では保証しない。小さく見せるためにTestやProduction経路を省略しない。

## 7. Seleneについて現在確定しているEvidence

Seleneに関するFailureを一つの原因へ混同しない。

### 7.1 `semantic_snapshot_unavailable`

Main Governance OFF／不在時にDedicated JudgeがSemantic Snapshotを取得できず失敗した事象は、Main GovernanceがTurn Contextを所有していた共通Architecture上の結合問題である。Selene固有障害の証拠ではない。この境界はComponent独立性Reworkの対象となった。

### 7.2 User実画面の即時`unavailable`

2026-09-05のClean Restart後の実画面では、Main Governance OBSERVE、Judge Selene ENFORCE、Repair OFFの条件でも、32 Criterion選択後、約31ミリ秒で`unavailable`へ失敗した。ProviderはConfigured／Active／ExecutedともSeleneを表示していた。

これは「単に長時間待った結果Timeoutした」挙動ではない。ただし現在のUI Evidenceだけでは、Native実行、Lease、Load、Lifecycle、Adapterのどこで失敗したかは確定できない。

### 7.3 過去の制御された実機Evidence

過去の有界な実機試験では、次を確認している。

- MainとSeleneを同一Processで同時Loadした条件で、`RuntimeError: llama_decode returned -3`が再現した。
- 同じ実Batch／Selene ContextをMain非LoadのSelene単体で実行すると成功した。
- Selene単体の32 Criterion評価は約93.451秒を要した。
- 使用中の`llama_cpp.py`契約では`-3`を一般的なFatal Errorとして扱っており、Metal固有Codeとは定義していない。

したがって、Main同時Loadは既知Failureの必要条件の一つである可能性が高いが、真の機構がMemory Pressure、Metal／GPU Backend、Native Context、Thread、Lease、Lifecycleのどれかは未確定である。「Metal Compute Buffer競合」と断定しない。

## 8. SeleneをMainからさらに切り離す案

Userは、Gemmaと同様にSeleneもMainから実行上さらに切り離せば、原因特定が容易になり、条件が変わるため修復不可能ではない可能性を指摘した。この見立てには合理性がある。

中立Turn Context、独立Lifecycle／Lease、単独ProcessまたはBackend境界、Provider固有Telemetryを用意すれば、少なくとも次を切り分けやすくなる。

- Main GovernanceとのArchitecture結合。
- Main Modelとの同時Load条件。
- GPU／Metal／Native Runtime共有の影響。
- Load成功表示と実Inference可能性の差。
- 速度問題と即時Failureの区別。

ただし、Mainからの論理的分離だけで`llama_decode returned -3`が解消するとは限らない。同一Process／同一Backendを共有したままならNative競合条件が残る可能性がある。別Process化や専用Backendまで必要なら、工数・運用負担・Memory使用量は増える。

原因をさらに絞るTelemetry／実験は小〜中規模で可能性がある一方、Mainとの同時実用を速度・安定性まで含めて成立させる修復は、真因未確定のため中〜大規模Riskとして扱う。

## 9. Seleneに関するUser決定

Seleneは、分離により原因特定や修復可能性が改善する余地を否定しない。しかし、単体32 Criterionでも約93.451秒を要し、仮に直っても現在のMac環境では日常利用に実用的ではない。

したがって、現時点の決定は次のとおり。

```text
Selene implementation status : unresolved
MVP blocker                  : no
current action               : defer
delete/deprecate             : no
claim fixed                  : no
revisit timing               : unknown / after higher-priority MVP work
```

Gemma等の軽量独立JudgeがMVP経路で成立するなら、それを優先する。Seleneは比較研究・将来Hardware・Process分離の検証候補として保持し、現在のPhase 9-1 Closureを無期限に止めない。

再開候補条件は、MVP後、Component独立性契約の安定後、専用Observability準備後、またはSeleneを比較対象として使う明確な研究目的が発生した時とする。

## 10. Phase別Routing

### Phase 9-1

- Component独立性の局所修復を完了させる。
- Judge／Guard／Main Governance／Repair／Recordingの組合せを確認する。
- Main OFFでもDedicated Judgeが独立実行できることを確認する。
- GemmaのMVP用Judge経路とMain起点RepairのProduction Evidenceを成立させる。
- Seleneの実用化をClosure条件に追加しない。

### Phase 10

- MVP完成を優先する。
- 本記録を理由に既定のUI／Docs統合作業を拡大しない。
- Advanced UIへ何を露出するかは、別のUI予約に従う。

### Phase 11以降

- GD群とRuntime Constitutionを、それぞれ構造レイヤー／意味評価レイヤーへ分ける。
- 共通Repair Request Portと再評価Portを設計する。
- 複数Governance SourceのAuthority／競合調停を設計する。
- Judge／Repairなしで働く構造制御を実装・検証する。
- 必要性があればSeleneのProcess／Backend分離とProvider固有Telemetryを再検討する。

## 11. 今回決めていないこと

- 全Componentの完全独立性がすでに実装済み、というClaim。
- Selene Failureの確定的な根本原因。
- Seleneの修復、削除、非推奨化、Artifact変更。
- Repair Request Portの具体的なClass／Schema／File配置。
- GD／Constitutionの各Ruleが構造／意味評価のどちらに属するか。
- 構造レイヤーと意味評価レイヤーの最終UI。
- Phase 10のScope拡大。
- Phase 11以降の着手時期と工数確約。

## 12. 後日確認する独立性Acceptance

1. Main Governance OFFでもJudge OBSERVE／ENFORCEが起動し、Main Evidenceは0である。
2. Judge OFFでもMainの構造制御、Guard、Recording、通常Chatが独立して動く。
3. Guard OFF／故障がJudge、Main Governance、Constitutionの起動条件を変えない。
4. Recording OFFでも各実行結果が変化せず、記録だけが0になる。
5. Repair OFFではRepair Call 0、ONでは明示されたTrigger OriginだけがRepairを要求する。
6. Judge起点、GD意味評価起点、Constitution意味評価起点のRepairが同じ中立契約を通る。
7. 構造GD／構造ConstitutionはJudge／Repairなしで独立適用できる。
8. 複数Source同時有効時のConflictとAuthorityが暗黙順序ではなくEvidenceへ残る。
9. 一つのProvider Failure、Unload、Cancel、Late Resultが別ComponentのCurrent Stateへ混入しない。
10. UIでConfigured、Active、Executed、Evaluated、PresentedのIdentityを混同しない。

## 13. 関連する既存予約との関係

- `phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_ja_20260902214032.md`: ARGD／DAGD 109件が当時Semantic-onlyだった発見と、GD系の再分類予約を維持する。
- `phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_ja_20260904172003.md`: GD群とRuntime Constitutionを別Componentのまま各二層化する決定を維持する。
- `phase_9_1_post_manual_internal_observability_judge_lifecycle_selene_and_lightweight_judge_reservation_ja_20260901180418.md`: Seleneの旧判定は履歴として保持し、本記録の新しいEvidenceと延期判断で補足する。

本記録は既存文書を上書き・取消ししない。後続作業では、古い「SeleneをPhase 9-1の未完了事項として必ず修復する」というRoutingより、2026-09-05のUser最新決定である「未解決のままMVP非Blockingとして延期」を優先する。
