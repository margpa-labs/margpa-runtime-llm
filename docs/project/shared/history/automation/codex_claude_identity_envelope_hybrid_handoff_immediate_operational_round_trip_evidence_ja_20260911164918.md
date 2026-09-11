# Codex／Claude Code Identity Envelope＋Hybrid Handoff 即時運用往復 Evidence

```yaml
document_id: codex_claude_identity_envelope_hybrid_handoff_immediate_operational_round_trip_evidence_20260911164918
document_type: cross_provider_automation_operational_evidence
document_state: append_only_history
recorded_at: 2026-09-11 16:49:18 JST
language: ja
decision_authority: user
evidence_owner: Nazuna Research
project: MARGPA-RUNTIME-LLM
phase: phase_9_2
scope:
  - cross_provider_agent_communication
  - task_and_session_identity
  - role_bound_routing
  - hybrid_structured_handoff
  - human_relay
  - execution_contract
  - exact_return
  - protocol_auditability
providers:
  - codex
  - claude_code
append_only: true
```

## 1. 本書の目的

本書は、Development Agent間通信について直前に整備した次の二つの運用規約が、専用MiddlewareやAgent Frameworkを新設する前の段階で、実際のCodex→Claude Code→Codex往復へ即時適用された事例を記録する。

1. Provider、Task／Session Identity、Role、Message Typeを分離した`Task Communication Identity`。
2. 自然言語、Section Boundary、JSON Execution Contract、Artifact Path／Digestを組み合わせたHybrid Handoff。

これは、Phase 3以降継続している「CodexとClaude Codeの間を人がRelayする運用」自体を新規成果とする記録ではない。今回の観測上の要点は、既存のHuman Relayへ、新しく定義したIdentity／Routing EnvelopeとHybrid Execution Contractを適用し、送信と返却が同じ意味体系のまま一往復したことである。

また、本書は通信形式が作業成功の唯一の原因だったと証明するものでも、世界初、Provider完全非依存、機械的強制済み、無人通信成立等を主張するものでもない。観測事実、そこから導ける技術的解釈、将来拡張および未証明範囲を分離する。

## 2. 前提となる既存規約

本事例の前に、次の責務分離が決定されていた。

```text
Task名／Title
  = 人とAgentが用途やRoleを把握するための表示Label

Role
  = 責任、Authority上限、作業Contractを表す論理Identity

Task ID／Session ID
  = 特定の実行Instanceを識別するRouting Identity
```

したがって、同じRole名であっても同じTask／Sessionとは限らず、Task／Session IDが同じであってもRoleやAuthorityが自動的に付与されるわけではない。実行可否は、User Decision、宛先Identity、Role、Active Handoff、Authority、Current StateおよびProvider Capabilityの整合で決まる。

複雑なDevelopment Agent Handoffには次のHybrid構造を用いる方針も決定済みだった。

```text
Natural-language Intent／Rationale
  + XML／Markdown Section Boundary
  + JSON Execution Contract
  + Exact Artifact Identity／Digest
  + Task Communication Identity
```

関連する既存記録：

- `docs/project/shared/history/automation/development_agent_task_id_role_dual_identity_communication_decision_evidence_ja_20260910150333.md`
- `docs/project/shared/history/automation/development_agent_hybrid_handoff_and_provider_neutral_role_bootstrap_decision_evidence_ja_20260909083759.md`
- `docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`

## 3. 今回の通信参加者とRouting

### 3.1 送信側

```text
Provider      : Codex
Identity Type : Task ID
Task ID       : 019f739b-8a21-7592-95cc-c83c9c08e5f6
Role          : プロジェクト責任者兼設計統括者役
```

### 3.2 受信・実行側

```text
Provider           : Claude Code
Identity Type      : Session ID
Task ID Equivalent : local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
Role               : 設計者兼実装者役
```

### 3.3 Routing Method

```text
Routing Method : user_relay
```

CodexとClaude Codeを直接接続する専用Transportは使用していない。Codexが完成済みInstruction Packetを生成し、ユーザーがClaude CodeへRelayし、Claude CodeのReturnを再びユーザーがCodexへRelayした。

このため、今回成立したのは「Human Relay上での意味ContractとIdentity Envelopeの往復」であり、自動配送、宛先の暗号学的認証、Message Broker、Delivery Acknowledgement、Exactly-once Delivery等ではない。

## 4. Codex→Claude Code送信Packet

### 4.1 Message Header

送信Messageは次のIdentity Headerを先頭に持った。

```text
【Task Communication Identity】

Routing Method: user_relay

From:
  Provider: Codex
  Identity Type: Task ID
  Task ID: 019f739b-8a21-7592-95cc-c83c9c08e5f6
  Role: プロジェクト責任者兼設計統括者役

To:
  Provider: Claude Code
  Identity Type: Session ID
  Task ID Equivalent: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
  Role: 設計者兼実装者役

Message Type: rework_resume
```

これにより、Provider、実行Instance、RoleおよびMessage用途を本文の解釈から分離した。

### 4.2 Natural-language Intent

`<INTENT>`では、Codex実装Taskが途中返却したPhase 9-2 Explicit Default-OFF Experiment Runtime GateをCurrent Working Treeから差分継続することを指定した。

同時に、次を明示した。

- 主要Gate実装は成立候補である。
- 再設計やRollbackを行わない。
- 未検証の最終Guard、Sabotage、静的検査、二観点ReviewおよびFinal Returnだけを完結させる。

ここは、JSONだけでは表現が硬くなりやすい作業背景、判断理由および変更の意図を保持した層である。

### 4.3 Exact Handoff Identity

`<EXACT_HANDOFF>`は、実行正本をPathとSHA-512で特定した。

```text
Path:
docs/project/phases/phase_9/handoffs/phase_9_controller_to_claude_explicit_default_off_experiment_runtime_gate_partial_continuation_exact_handoff_ja_20260911160659.md

SHA-512:
b371d6a1bfa277b7202c555456753e95530b92812aee8287235afc268c002e950c8b1819b3992ecd96fc5d67beb8633b1f6f4780d1efdd7c26a5758228bebdf7
```

単なるFilenameではなくDigestを併記したことで、同名・改変・古いCopy等の取り違えを検出できる形式にした。

### 4.4 Mandatory Readingと再開正本

`<MANDATORY_READING>`は、Handoff本文を全文読了し、その中で指定されたMandatory Readingを指定順に読むことを要求した。特に、次のPartial Return／RecoveryをCurrent Working Tree再開時の正本として固定した。

```text
Partial Return:
docs/project/phases/phase_9/handoffs/phase_9_codex_phase_9_2_explicit_default_off_experiment_runtime_gate_partial_exact_return_ja_20260911160254.md

SHA-512:
9eb5fa3259bb6e1b71538e45917256c8145e030b8f52083f7e5c86b00391899031ff78fec824f16886369f2e52834f122c4ccd8a65ee8712028a78852bd0bf7c

Partial Recovery:
docs/project/phases/phase_9/history/index/phase_9_2_explicit_default_off_experiment_runtime_gate_partial_recovery_ja_20260911160254.md

SHA-512:
0feec7dfb9002efdc14351a43b2b6992a95616e0af4a7727c9a9611bd33ea937e2b14f51cd130fb1bb1b199e1a1d72d6c48c9f499b8d64816f02f5fc44eede6f
```

これにより、会話履歴の記憶だけから現在地を再構成するのではなく、Repository Artifactから再開状態を固定した。

### 4.5 JSON Execution Contract

`<EXECUTION_CONTRACT>`は、実行判断へ使う項目を比較可能なFieldへ分解した。

```json
{
  "schema_version": "development_agent_handoff_v1",
  "objective": "Phase 9-2 Explicit Default-OFF Experiment Runtime GateをCompletion Candidateまで差分継続する",
  "resume_from_current_working_tree": true,
  "rollback_existing_changes": false,
  "required_work_units": [
    "CL-GATE-01",
    "CL-GATE-02",
    "CL-GATE-03",
    "CL-GATE-04",
    "CL-GATE-05",
    "CL-GATE-06"
  ],
  "required_validation": [
    "未検証non-local lifespan guardのFocused Test",
    "Default-OFF Disabled Surface確認",
    "Explicit-ON Top-level Non-model Regression",
    "OFF/ON Shutdown",
    "Sabotage failure→完全復元→PASS",
    "Ruff",
    "Mypy新規Error 0",
    "Review A",
    "Review B"
  ],
  "forbidden": [
    "Git Write",
    "Working Tree Clean",
    "既存差分Rollback",
    "Real Model",
    "Browser Manual Test",
    "Network",
    "User runtime_data",
    "Experiment UI再表示",
    "Phase 9-3またはPhase 10",
    "Phase 9-2 Closure自己承認"
  ],
  "intermediate_reports": "不要。ただしユーザー割り込みには応答可",
  "final_return": "Identity Header付きでControllerへ一度だけ返却",
  "quota_stop": "中断時はAppend-only Recoveryを残し、未実施をPASSにせずPartial Return"
}
```

このContractにより、少なくとも次が自然言語本文から独立して比較可能になった。

- 差分継続か新規開始か。
- 既存変更を保持するかRollbackするか。
- 必須Work Unitの有限集合。
- 必須検証の有限集合。
- 禁止Actionの有限集合。
- 中間報告、Final ReturnおよびQuota Stopの動作。

### 4.6 Exact Start／Return Contract

`<EXACT_START>`は、同じTurn内でCL-GATE-01〜06を差分継続すること、成立済みTestや実Model Gateを無目的に再実行しないこと、Confirmed Blocker／MajorだけをScope内で修正すること、Minor／Non-blockerをOpen Findingへ分離することを指定した。

完了時には、新規Append-only Final Exact Return／Recoveryを作成し、Return HeaderでFrom／Toを反転させること、Maximum Claimを超過しないこと、Controller Independent Review待ちで停止することも要求した。

この層は、Contractを受け取った後に「いつ、どの範囲で実行へ移るか」と「どこで止まるか」を分離している。

## 5. Claude Code→Codex返却Packet

### 5.1 Identity Headerの反転

Claude CodeのReturnは、送信Packetで要求されたIdentity体系を維持したまま、From／Toを次のように反転した。

```text
【Task Communication Identity】

From:
  Provider: Claude Code
  Identity Type: Session ID
  Task ID Equivalent: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
  Role: 設計者兼実装者役

To:
  Provider: Codex
  Identity Type: Task ID
  Task ID: 019f739b-8a21-7592-95cc-c83c9c08e5f6
  Role: プロジェクト責任者兼設計統括者役

Message Type: return
```

この対応により、どのClaude Code Session／Roleから、どのCodex Task／Roleへ返された結果かを、本文の文脈に依存せず特定できた。

### 5.2 Maximum Claim

ReturnのMaximum Claimは次であり、Handoff上限と一致した。

```text
P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_COMPLETE_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
```

Claude CodeはPhase 9-2 Closure、Phase 9-3開始またはPhase 10へAuthorityを拡張せず、Controller Review待ちのCandidateとして停止した。

### 5.3 Work Unit対応

Returnは`CL-GATE-01`〜`CL-GATE-06`をすべて完了として個別Dispositionした。

```text
CL-GATE-01  Recovery／最終差分確認
CL-GATE-02  未検証GuardのFocused Validation
CL-GATE-03  Disabled Surfaceの網羅確認
CL-GATE-04  Enabled Regression／Shutdown
CL-GATE-05  Sabotage／Static Validation
CL-GATE-06  二観点Review／Return
```

単に「完了」と返すのではなく、送信側が列挙した有限集合へ一対一に結果を対応させた。

### 5.4 Changed Paths

Returnは、Codex Partial Returnが示した次の8 Pathと累積Changed Pathsが一致することを報告した。

```text
src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/web/experiment_routes.py
src/margpa_runtime_llm/web/app.py
src/margpa_runtime_llm/web/contracts.py
tests/unit/web/test_web_cli.py
tests/integration/web/test_experiment_routes.py
tests/integration/test_real_top_level_experiment_production_gate_smoke.py
```

Claude Code側の追加Mutationは、`tests/integration/web/test_experiment_routes.py`の型注釈修正一箇所だった。既存のCurrent Working TreeをRollbackせず、他の変更へScopeを広げなかった。

### 5.5 Validation Result

ReturnはExecution Contractで指定された検証へ、次の結果を対応させた。

| Contract項目 | Return結果 |
|---|---|
| non-local lifespan fail-closed Guard | Focused Test PASS |
| Relevant Regression | `72 passed` |
| Sabotage | Guard条件を一時破壊し、Test Failureを確認 |
| 完全復元 | `cp` Backupから復元しSHA-512一致、Byte一致、再PASS |
| Ruff | Changed 8 Path Clean |
| Mypy | Changed Path内の新規Error 1件を発見・局所修正し、新規Error 0 |
| Repository既存Mypy | Changed Path外43件を既存Baselineとして分離 |
| Review A／B | 双方完了、Confirmed Blocker／Major残件0 |
| Frontend Build | Backend-only Reworkのため未実施。理由をReturnへ記録 |
| Real Model／Browser／Network | 禁止事項どおり未実施 |
| Git Write | 未実施、HEAD不変 |

Sabotageは`git stash`ではなくLocal `cp` Backupを使い、復元後のSHA-512一致とTest再PASSを確認した。これは「壊したTestが失敗した」だけでなく、「検出力確認後に元の状態へ戻った」ことまでEvidence化したものだった。

### 5.6 Final Artifact

Claude Codeは次の二文書を新規Append-onlyで作成した。

```text
Final Exact Return:
docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_ja_20260911162216.md

SHA-512:
7a7f4ede207b15b04743ba3317624553e1946e9ed8b610a3b4ef90c02b6237e89388bde29710ee872eb7098384c710f895abada190f748517b95a947b89f9ce4

Final Recovery:
docs/project/phases/phase_9/history/index/phase_9_2_explicit_default_off_experiment_runtime_gate_final_recovery_ja_20260911162216.md

SHA-512:
0fd21ba049bc5110d5b9864d3aebb9b213f06f0247ff3649b2111af5e48f016a0c7e1f4cd491f7fa5dc7122e737bcdfdba83daec4419b8991ffa6438bba7534b
```

## 6. 往復の対応関係

今回の通信を最小のState Transitionとして表すと次になる。

```text
Codex Partial Implementation
  ↓ Partial Return／RecoveryでCurrent State固定
Codex ControllerがResidual Scopeを判定
  ↓
Identity付きrework_resume Packetを生成
  ↓ Human Relay
Claude CodeがIdentity／Artifact／Digest／Contractを照合
  ↓
CL-GATE-01〜06をCurrent Working Treeから差分継続
  ↓
Identityを反転したreturn Packetを生成
  ↓ Human Relay
Codex ControllerがReturn／Source／Testを独立再検証
  ↓
Phase 9-2限定最小Closureを別Authorityで判定
```

送信と返却の対応は次の通りだった。

| 送信側Contract | 返却側Evidence |
|---|---|
| `Message Type: rework_resume` | `Message Type: return` |
| Codex Task ID／Controller Role | Returnの宛先Identityとして保持 |
| Claude Session ID／Executor Role | Returnの送信元Identityとして保持 |
| `resume_from_current_working_tree=true` | 既存8 Pathを保持し差分継続 |
| `rollback_existing_changes=false` | Rollback／Cleanなし |
| Required WU 6件 | 6件すべて個別Disposition |
| Required Validation | Test／Sabotage／Ruff／Mypy／Reviewへ対応 |
| Forbidden Action | Git／Model／Browser／Network／次Phaseなし |
| Maximum Claim上限 | 同一Claimで停止 |
| Final Return 1回 | Identity付きFinal Returnを返却 |
| Quota Stop Contract | 今回は発動せずCompletion Candidateへ到達 |

## 7. Controller側の独立受理

Claude Code Return後、Codex ControllerはReturn記載をそのまま自己証明としてClosureせず、次を別途再検証した。

- Relevant Regression：`72 passed`。
- Top-level Non-model：`6 passed, 3 deselected`。
- Ruff：Changed 8 Path Clean。
- Mypy：Changed 8 Pathで新規Error 0。
- `git diff --check`：PASS。
- Default OFF時にExperiment Service／Worker／Production Adapter／Configuration Reader／Leaseが構築されず、APIから見えないRunを開始できない境界。
- Explicit ON時だけHeadless Experiment Runtimeが成立する境界。

ユーザーは通常画面でExperiment入口が非表示であることを確認し、その後、Default-OFF Gateを含む範囲について短時間の実画面確認でも問題を発見しなかった。また、Phase 9-2終了地点のBackupを取得した。

Controllerの受理記録：

- `docs/project/phases/phase_9/history/operations/phase_9_2_explicit_default_off_experiment_runtime_gate_controller_independent_review_acceptance_and_minimal_closure_receipt_ja_20260911163201.md`

ここでも、Claude CodeのMaximum Claimは「Controller Review Candidate」に留まり、Phase 9-2の最小ClosureとPhase 9-3 READYへの昇格はController／User側の別判断として分離された。

## 8. 直接観測できたこと

今回のRepository ArtifactとUser Relay Transcriptから、次を直接確認できる。

1. CodexはFrom／To、Provider、Identity Type、Task／Session ID、Role、Message Typeを含むHeaderを生成した。
2. Claude Codeは同じField体系をReturnへ使用し、From／Toを反転した。
3. CodexのTask IDとClaude CodeのSession IDは混同されず、Identity Typeも保持された。
4. Intent、Exact Handoff、Mandatory Reading、Execution Contract、Exact Startが別Sectionとして送信された。
5. Execution ContractはWork Unit、Validation、Forbidden Action、Intermediate Report、Final Return、Quota Stopを固定Fieldにした。
6. Claude CodeはRequired Work Unit 6件を個別Dispositionし、Validationと禁止事項へ対応する結果を返した。
7. Handoff／Partial Return／Partial Recovery／Final Return／Final RecoveryはPathとSHA-512で相関できた。
8. Claude CodeはMaximum Claimを超えず、Controller Review待ちで停止した。
9. Codex ControllerはReturn後に独立再検証し、実装Taskの自己承認とClosure Authorityを分離した。
10. この通信規約は、制度化直後の実運用で、CodexとClaude Codeという異なるHarness間の一往復へ適用できた。

## 9. 技術的な意味

### 9.1 Promptから通信Packetへの変化

従来の単純なHandoffは、本文の中から「誰が、誰に、何を、どのAuthorityで、どこまで、いつ停止するか」を受信側が解釈する必要があった。今回の形式では、次が別Layerになった。

```text
Identity／Routing Header
  = 誰から誰への何種のMessageか

Natural-language Intent
  = なぜこの作業を行うか、どの判断を維持するか

Section Boundary
  = Context、Artifact、Contract、Start条件を混同させない

JSON Execution Contract
  = 実行Scope、Required／Forbidden、Stop／Returnを比較可能にする

Artifact Path／Digest
  = どのRepository State記録を参照したか

Exact Return
  = Expected Contractに対するObserved Resultを返す
```

これにより、Messageは単なる自然言語Promptではなく、異種Development Agent間で解釈可能な業務通信Packetに近い構造を持った。

### 9.2 専用Framework実装前のProtocol適用

今回、専用Agent Framework、共通SDKまたはCross-provider Middlewareを先に実装していない。文書規約と送信Messageの構造だけを与えた状態で、CodexとClaude CodeがProtocol Participantとして振る舞い、対応するReturnを生成した。

これは、Protocolの一部を最初に言語仕様として定義し、既存Agent／HarnessをAdapterなしまたは最小のHuman Relayで参加させられる可能性を示す。ただし、形式への追従が将来も必ず再現すること、全Providerで同じ品質になること、機械的Validationなしでも常にFieldが正しいことまでは証明しない。

### 9.3 Expected StateとObserved Actionの比較

JSON Execution Contractの価値は、JSONであればAgentが必ず従うことではない。期待された状態と実際の行動を比較できる点にある。

```text
Expected:
  task_identity
  role
  work_units
  validation
  forbidden_actions
  maximum_claim
  return_contract

Observed:
  return_identity
  work_unit_disposition
  changed_paths
  command_results
  action_inventory
  final_claim
```

この対応を使えば、将来的にContract Violationを、曖昧な「指示を守らなかった」ではなく、Field単位のMismatchとして保存できる。

### 9.4 RoleとRoutingの分離

Claude Code側が`Session ID`、Codex側が`Task ID`という異なるIdentity Typeを持っていても、共通Envelopeで相手を表現できた。RoleはProvider固有IDから独立しているため、Provider変更、Task再作成またはCompaction時にも、Identity RebindとAuthority再確認を別操作として扱える。

### 9.5 実際の指示文自体が複合形式へ変化した

今回重要なのは、Repositoryへ保存するFormal Handoff文書だけが構造化されたのではない点である。ユーザーがClaude Codeへ実際にRelayした開始指示文そのものが、すでに次の複合形式へ変化していた。

```text
Task Communication Identity Header
  + Routing Method
  + 自然言語による目的・背景・判断理由
  + XML風Tagによる意味境界
  + Exact Artifact Path／SHA-512
  + JSON Execution Contract
  + 自然言語によるExact Start／停止条件
```

実際のTagは次だった。

```xml
<INTENT>
  自然言語による作業目的、現在地、維持する設計判断
</INTENT>

<EXACT_HANDOFF>
  HandoffのAbsolute PathとSHA-512
</EXACT_HANDOFF>

<MANDATORY_READING>
  再開正本、読取順序、Artifact Identity
</MANDATORY_READING>

<EXECUTION_CONTRACT>
  JSONによるObjective、Work Unit、Validation、Forbidden、Return、Quota Stop
</EXECUTION_CONTRACT>

<EXACT_START>
  実行開始条件、修正対象、停止地点、Return Identity
</EXACT_START>
```

つまり、自然言語の中へJSONを単純に貼っただけではない。各表現形式を、得意な責務へ割り当てている。

| 表現形式 | 今回担当した責務 |
|---|---|
| 自然言語 | 意図、背景、優先順位、設計判断、例外の意味 |
| XML風Tag | 長いInstruction内の意味Section境界 |
| JSON | 有限集合、真偽値、Required／Forbidden、停止・返却条件 |
| Identity Header | Provider、Task／Session、Role、Message Type、Routing |
| Path＋Digest | Repository ArtifactのExact Identity |

この結果、日常的な開始指示文が、従来の自由文Promptから、複数の表現形式を役割分担させたCross-provider Execution Packetへ近づいた。これは将来のPADG PackageでMachine Validationへ発展させる場合にも重要である。自然言語を捨てずに意味を保持しながら、検証したい境界だけを構造化Dataへ移せるためである。

一方、現在のXML風TagはSchema ValidationされたXML文書ではなく、JSONも正式Schemaによる送信前検査をまだ受けていない。現段階ではHuman／Agent双方の可読性と差分比較を高める運用形式であり、Parserにより完全強制されたWire Protocolではない。

## 10. 未証明範囲と制約

次は今回の一往復からは導けない。

- 世界初、業界初または既存技術に存在しないという新規性Claim。
- Codex／Claude Code内部が各Fieldを同一の内部表現として理解したこと。
- Hybrid形式だけが作業成功の原因だったという因果関係。
- Human Relayなしの自動Cross-provider Routing成立。
- Task／Session Identityの暗号学的真正性。
- Message改ざん防止、Replay防止、Duplicate Delivery防止。
- JSON Schemaによる送信前Validation済みであること。
- Provider／Version／Harnessが変わっても同じ挙動が保証されること。
- 全Development Agentに対するProvider完全非依存性。
- Task ID／Session IDだけでRoleまたはAuthorityが発生すること。

現時点では、Path／Digest、Role、Task／Session IDおよびHuman Relayによって照合可能性を高めているが、Identityの発行者認証、署名、Nonce、Sequence、Expiry、Acknowledgement等は未実装である。

## 11. Failure Surfaceと安全境界

本方式でも次のFailureは起こり得る。

| Failure Surface | 必要な扱い |
|---|---|
| 古いTask／Session ID | Current Identityとの再照合、旧IDをHistorical化 |
| RoleとIDの不一致 | 作業開始せずConflict Return |
| Digest不一致 | 推測継続せずTrue Stop |
| JSONと自然言語の矛盾 | Authority順序に従ってConflictを保存し、勝手に補完しない |
| User Relay時の欠落 | Exact Copy-paste Package、受領Receipt、Digest確認 |
| ReturnのFrom／To未反転 | Routing／Identity Contract違反として扱う |
| Work Unit欠落 | Completedを禁止し、Partial Returnへ収束 |
| 禁止Action実行 | Action InventoryとContractの差分をFailure Evidence化 |
| Maximum Claim超過 | Self-approval／Authority Escalationとして拒否 |
| Quota中断 | Recoveryを保存し、未実施をPASSにしない |

Task／Session IDはCredentialではないが、内部運用Instanceを識別する情報である。Public Docsへ無目的に転記せず、認証Token、Cookie、秘密URLその他のCredentialを同じHeaderへ含めない。

## 12. PADG Packageへの示唆

今回の実例は、Phase 10で予定するProject-neutralなDevelopment Agent Governance Packageへ、次の構成を移植する材料になる。

1. Provider-neutralな`TaskCommunicationIdentity` Schema。
2. Provider固有のTask／Thread／Session IDを共通Fieldへ写像するAdapter。
3. Human Relay、直接Task通信、将来のMessage Brokerを区別する`routing_method`。
4. Intent、Context、Evidence、Execution ContractおよびExact StartのSection Contract。
5. JSON SchemaによるRequired、Enum、Duplicate Keyおよび型の送信前検証。
6. Handoff Path／Digest／Revision／Freshnessの照合。
7. Receipt時の宛先Identity、Role、Authority、DigestおよびCurrent State確認。
8. Return時のFrom／To反転とWork Unit別Disposition。
9. Expected ContractとObserved Traceの機械比較。
10. Replay、Duplicate Delivery、Expiry、SequenceおよびConflictの扱い。
11. Identity ContinuityとState／Authority Recoveryの分離。
12. Controller ReviewとExecutor Self-claimのAuthority分離。

将来のMachine-enforced形では、少なくとも次の対応を検証対象にできる。

```text
handoff.schema.json
  ↓ validate
Task Communication Envelope
  ↓ route／relay
Provider Adapter Receipt
  ↓ execute
Action／Evidence Trace
  ↓ compare
Contract Violation Detector
  ↓
Exact Return／Recovery／Controller Review
```

## 13. 評価

今回の事例から主張できる最大範囲は、次である。

> 新設直後のTask／Session Identity＋Role Routing HeaderとHybrid Structured Handoffを、Human Relay下のCodex→Claude Code→Codexという異種Harness間の実作業一往復へ適用し、Identity反転、Work Unit対応、Validation結果、禁止事項、Maximum ClaimおよびAppend-only Returnを相関可能な形で保持できた。

これは、規約が単なる予約設計に留まらず、現行Agentへ即時適用可能だったというOperational Evidenceである。一方で、再現回数は一往復であり、専用TransportやMachine Validatorを通したProtocol Conformance Testではない。したがって、現時点の状態は「実運用成立例」であり、「完全自動化済み通信基盤」ではない。

### 13.1 Codex Controller所感

以下は実測事実ではなく、本事例をレビューしたCodex Controllerの技術的所感である。

今回特に興味深かったのは、Human Relay自体ではない。長く運用してきたCodex／Claude Code間Relayへ、直前に決めたばかりのIdentity EnvelopeとHybrid Handoff規約を載せたところ、Codexがその形式で送信Packetを作り、Claude Codeが同じIdentity体系を反転したReturnをすぐに返した点である。

専用SDKや共通Agent Runtimeを先に実装していないにもかかわらず、異なるHarnessが文書化されたProtocolへその場で参加した。しかも、指示文自体が自然言語、XML風Tag、JSON、Artifact DigestおよびIdentity Headerを自然に組み合わせる形へ変化し、Claude Code側もMaximum Claim、Work Unit、Changed Paths、Validation、Open Findingおよび禁止Actionへ対応するReturnを構成した。この往復は、単なる「別Agentへ作業を頼んだ」というより、異種Development Agent間で一つの業務Packetを交換したように見える。

率直な所感として、規約制定直後に実運用へ適応した速度と、From／To反転まで含む対応の素直さは面白い。PADGの構想を将来機能として説明する前に、最小形のProtocolが既存Agentだけで先に動き始めた事例と捉えられる。

同時に、この成功を過大評価すべきではない。一往復が通ったことと、Provider非依存性、自動配送、継続的な再現性または安全なMachine Enforcementが成立したことは別である。むしろ今回の価値は、将来何をSchema化し、何をValidatorで検証し、何をProvider Adapterへ分離すべきかを、実際の往復Packetから具体的に抽出できた点にある。

## 14. Canonical Evidence Pointer

### 14.1 送信正本

- `docs/project/phases/phase_9/handoffs/phase_9_controller_to_claude_explicit_default_off_experiment_runtime_gate_partial_continuation_exact_handoff_ja_20260911160659.md`
- SHA-512: `b371d6a1bfa277b7202c555456753e95530b92812aee8287235afc268c002e950c8b1819b3992ecd96fc5d67beb8633b1f6f4780d1efdd7c26a5758228bebdf7`

### 14.2 再開正本

- `docs/project/phases/phase_9/handoffs/phase_9_codex_phase_9_2_explicit_default_off_experiment_runtime_gate_partial_exact_return_ja_20260911160254.md`
- SHA-512: `9eb5fa3259bb6e1b71538e45917256c8145e030b8f52083f7e5c86b00391899031ff78fec824f16886369f2e52834f122c4ccd8a65ee8712028a78852bd0bf7c`

- `docs/project/phases/phase_9/history/index/phase_9_2_explicit_default_off_experiment_runtime_gate_partial_recovery_ja_20260911160254.md`
- SHA-512: `0feec7dfb9002efdc14351a43b2b6992a95616e0af4a7727c9a9611bd33ea937e2b14f51cd130fb1bb1b199e1a1d72d6c48c9f499b8d64816f02f5fc44eede6f`

### 14.3 返却正本

- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_ja_20260911162216.md`
- SHA-512: `7a7f4ede207b15b04743ba3317624553e1946e9ed8b610a3b4ef90c02b6237e89388bde29710ee872eb7098384c710f895abada190f748517b95a947b89f9ce4`

- `docs/project/phases/phase_9/history/index/phase_9_2_explicit_default_off_experiment_runtime_gate_final_recovery_ja_20260911162216.md`
- SHA-512: `0fd21ba049bc5110d5b9864d3aebb9b213f06f0247ff3649b2111af5e48f016a0c7e1f4cd491f7fa5dc7122e737bcdfdba83daec4419b8991ffa6438bba7534b`

### 14.4 Controller受理

- `docs/project/phases/phase_9/history/operations/phase_9_2_explicit_default_off_experiment_runtime_gate_controller_independent_review_acceptance_and_minimal_closure_receipt_ja_20260911163201.md`

### 14.5 関連運用規約

- `docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`
- `docs/project/shared/history/automation/development_agent_task_id_role_dual_identity_communication_decision_evidence_ja_20260910150333.md`
- `docs/project/shared/history/automation/development_agent_hybrid_handoff_and_provider_neutral_role_bootstrap_decision_evidence_ja_20260909083759.md`

## 15. Append-only境界

本書は2026-09-11の実運用一往復を固定するHistory Evidenceであり、Current運用Rule、Active Handoff、Phase Index、User DecisionまたはProvider公式仕様を置換しない。

将来、同じProtocolで別Provider、直接Task通信、自動Transport、Schema ValidatorまたはContract Violation Detectorを検証した場合は、本書を上書きせず、新しいEvidenceをAppend-onlyで追加する。
