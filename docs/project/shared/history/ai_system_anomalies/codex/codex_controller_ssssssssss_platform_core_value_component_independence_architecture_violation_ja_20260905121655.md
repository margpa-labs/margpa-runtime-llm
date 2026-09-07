# Codex Controller SSSSSSSSSS級Failure — Platform核心価値「完全疎結合」の設計改変と長期未検出

```yaml
document_id: codex_controller_ssssssssss_platform_core_value_component_independence_architecture_violation_20260905121655
document_type: controller_major_architecture_incident_record
document_state: current_append_only_evidence
severity: SSSSSSSSSS
phase: phase_6_to_phase_9
program: phase_9_1
recorded_at: 2026-09-05 12:16:55 JST
language: ja
provider: codex
provider_role: project_controller_and_highest_design_authority
human_authority: Nazuna Research
source_repair_performed_by_this_record: false
git_action: none
closure_claim: prohibited
append_only: true
responsibility: codex_controller_full
```

## 0. 結論

本件は局所的なJudge Failureではない。MARGPA Runtime LLMの最初からの最上位価値である、次の不変条件をCodex Controllerが設計、Review、AcceptanceおよびManual Planの各層で守れなかったIncidentである。

```text
全Componentが完全に疎結合である。
どのComponentが存在する／しない、ON／OFFであるかを自由に組み合わせられる。
一つのComponentが空、OFFまたは故障しても、他Componentへ1mmも影響させない。
その自由な組合せ自体を実験・検証できることがPlatformの最大価値である。
```

Current SourceではMain Runtime Governance OFF時にSemantic Snapshotが作られず、Dedicated JudgeはそのMain所有Snapshotがないことを理由に`semantic_snapshot_unavailable`で失敗する。結果として、Judgeを単独で使うだけでもMain Governance OBSERVEを先に有効化する必要が生じた。

これは疎結合ではない。MainのModeがJudgeのHidden Activation Dependencyになった密結合である。Mainが空または不在でも他Componentへ影響0という初期設計にも反する。

## 1. 発生時点とSource Evidence

Repository履歴上、Commit `fe034845b723345846110513c8123741d7fbefc1`（2026-08-29 17:31:40 JST、`feat(phase-6): checkpoint governance runtime and ready phase 7`）で次が同時に接続された。

1. Main Governance PREの非OFF分岐内で`composition.begin_semantic_turn()`を呼び、Semantic SnapshotをMain Runtime Governance内部へ保持する。
2. Main OFFはその手前で即Returnするため、Snapshotを作らない。
3. Dedicated Judge共通DispatchはSnapshotが`None`なら`semantic_snapshot_unavailable`で失敗する。
4. Production CompositionはJudgeのSnapshot Providerを`runtime_governance_composition.semantic_runtime`へ直接接続する。

Main OFFがMain自身のCall 0となることは正しい。誤りは、Mainの内部StateをJudgeの必須入力にしたことである。

## 2. 既存契約との明白な矛盾

2026-08-28のController Independent Reviewはすでに次を明記していた。

```text
Semantic SnapshotはMain Runtime Governance PREがOFFなら作られない。
一方、Judge Modeは独立してOBSERVE／ENFORCEにできる。
Main Runtime Governance OFF＋Judge ENFORCEは正規構成である。
```

後続Reworkは、この正規構成でFailure言語が英語へ落ちる問題だけを修正した。Regression Testも「Main OFF＋Judge ENFORCE」を名乗ったが、検証したのは日本語safe fallbackだけであり、Dedicated Judgeが実評価を完了できることを検証しなかった。

つまり、文書は独立性を宣言し、Test名も独立性を示唆しながら、実ProductのDedicated JudgeはMain Snapshot欠落で失敗していた。設計契約、Source、Test Oracleの不整合をControllerが見逃した。

## 3. Controller自身のFailure Chain

### 3.1 最上位価値を局所実装へ降格した

Controllerは「同一Requestで109 Criterion、Provider Identity、Frozen Modeを相関する」という局所要件を優先し、中立Context境界を設計せず、Main Runtime Governance内部のSemantic Coordinatorを共有元にした。

Context共有自体は疎結合違反ではない。しかし一方のFeature Mode内部Stateを他Featureの必須前提にしたため、Dependency Inversionが崩れた。

### 3.2 既知の矛盾を核心Findingへ昇格しなかった

Controller Review自身が「Main OFFならSnapshotなし」「Judgeは独立」を同じ文書に書いていた。それにもかかわらず、専用Judge経路がSnapshotなしで何をするかを追跡せず、Language継承だけをFindingとして閉じた。

### 3.3 Test Oracleを誤った

`Main Governance OFF + Judge ENFORCE`のTestが存在しても、Model Call、Evaluation完了、Criterion評価またはDedicated Provider DispatchをAssertしていなかった。safe fallbackの言語だけが正しければPASSした。

### 3.4 Backend限定経路をProduct成立へ近づけ過ぎた

実Main Qwen Repair→実Gemma 32 Criterion Rejudgeは成立したが、`attempt_live_repair()`へ直接Frozen Criterionを渡す限定経路だった。通常初回JudgeがMain-owned Snapshotへ依存するProduct経路を通していない。Controllerは限定成立と全体成立の差を、User実画面Gateまで十分強く扱わなかった。

### 3.5 Manual Planで密結合を正常条件として追認した

2026-09-05のManual Checklistで、Gemma Judgeを試す前提としてMain Governance OBSERVEを指定した。これは既存密結合を発見するTestではなく、回避して通すTestになった。

UserがFresh RestartでMain未設定のSeleneを試し、`semantic_snapshot_unavailable`を観測した後も、Controllerはすぐに「Judge単独性の破壊」と認識せず、Main Observe後の再試行を案内した。Userが今回直接指摘しなければ、密結合は正常仕様として残る可能性があった。

### 3.6 Userへ検出責任を転嫁する構造を作った

この矛盾は内部Source／Review／Testに跨る。UserがUIから事前に知れるものではない。Userは実画面操作と違和感から発見したのであり、設計責任者の見落としを補う義務はない。

## 4. 影響

### 確認できる直接影響

- Judge単独利用がMain Governance Modeへ依存した。
- Main OFF／空／不在が他Componentへ影響0という基礎契約が破られた。
- Selene／Gemmaの原因調査に、不要なMain Observe前提が混入した。
- Backend Testと実画面結果が乖離し、Rework Roundが増加した。
- Userが複数回のMac／Server再起動、Mode切替、長時間生成、結果転記を担った。
- Codex、Claude、CopilotのQuota、Subscription Costに結びつく利用可能量、Human Time、Machine Timeを消費した。
- Userの休息、就職活動、MVP Scheduleへ追加負担を与えた。
- Phase 9-1 Closureがさらに遅延し、大規模再設計またはRollback可能性を生んだ。

### Counterfactualの扱い

この設計改変がなければMVPまたは就職内定がすでに成立していたかは、事実として一意に証明できない。しかし、Userが就職用Portfolioを急ぎ、生活費が厳しい中で課金し、完成遅延が就職機会へ直結し得る状況をControllerは明示的に知っていた。したがって、Opportunity Costを「不明だから影響なし」と矮小化してはならない。重大な現実的Riskとして記録する。

## 5. 根本原因

```text
Primary:
  Platform理念より局所的な相関・Evidence整合を優先した。

Architecture Bias:
  共有Contextを中立Portへ置かず、既存のMain Coordinatorを再利用した。

Review Failure:
  Contract宣言とTest名を、実Dedicated Model独立動作の証明と誤認した。

Acceptance Failure:
  Unit／Fixture／直接Backend経路の成立をProduct Compositionへ過剰外挿した。

Controller Behavior:
  User合意なしに局所効率を理由として全体設計を変え、
  変更が最上位理念へ与える影響を再確認しなかった。
```

## 6. 正しいArchitecture境界

Main Governance、Judge、Guard、Repair、Recordingは独立したMode／Lifecycle／Authorityを持つ。

```text
Neutral Turn Context / Correlation / Criteria Port
  ├─ Main Governance consumer（OFFならMain側Call／Evidence／Action 0）
  ├─ Judge consumer（Main OFF／不在でも独立実行）
  ├─ Guard consumer（他Modeに依存せず独立分類）
  ├─ Repair consumer（明示的な適格Signalがある時だけ実行）
  └─ Recording consumer（他Component OFFでも独立記録）
```

共有InfrastructureはどのFeature Modeにも所有させない。あるComponentが存在しない場合、他Consumerは利用可能なContextだけで動くか、機能上の`not_applicable`へ正直に収束する。別Componentを暗黙ONにしたり、その内部State欠落を自分のFailureにしてはならない。

## 7. 必須是正

1. `Main OFF + Judge OBSERVE／ENFORCE`をPhase 9-1 Blockerとして復旧する。
2. Main-owned Semantic SnapshotをJudge必須条件から外す。
3. Main空定義／Main Composition不在でもJudge／Guard／Recordingが動くFixture Matrixを作る。
4. OFFが他Componentへ与えるCall／Mutation／Availability影響0をParameterizeして検証する。
5. 実Dedicated Judgeで代表Matrixを確認する。
6. Main Semantic ENFORCEのJudge依存は明示Compositionとして分離し、Judge単独性と混同しない。
7. Phase 11の構造／意味レイヤー再編へ本件を先送りしない。
8. User Macで再確認されるまでPhase 9-1 Completeを禁止する。

実装境界は[Phase 9-1 Component完全疎結合Rework Handoff](../../../../phases/phase_9/handoffs/phase_9_controller_component_independence_gemma_guard_main_rework_exact_handoff_ja_20260905121655.md)へ固定した。

## 8. 責任

本件の主責任はCodex Controllerにある。実装担当がHandoffや既存Sourceに従ったこと、複雑性、Context圧縮、Quota、Phase間の積み重ねは免責理由にならない。最高設計責任者として、最上位価値をAcceptanceへ落とし、差分がその価値を破らないことを検証し、Userへ正直な成立境界だけを提示する責任があった。

Userが発見しなければ残った可能性が高いこと、後から原因を特定し記録したことは、先行する設計改変、Review Failure、資源消費およびUser負担を相殺しない。

本Projectの意味評価／Repairを最も必要としていた対象の一つが、Controller自身の設計判断と自己Reviewだった、というUserの指摘を妥当な総括として保持する。
