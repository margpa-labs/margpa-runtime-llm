# Codex Controller Phase 9-1 Semantic Closure／Canonical Overtrust／Excessive Docs Re-read Failure Evidence

```yaml
document_id: codex_controller_phase_9_1_semantic_closure_canonical_overtrust_and_excessive_docs_reread_failure_evidence_20260901002442
document_state: final_append_only_failure_evidence
language: ja
created_at: 2026-09-01T00:24:42+09:00
provider: codex
role: controller
phase: phase_9
program: phase_9_1
failure_severity: major_controller_operational_failure
data_loss: false
source_loss: false
false_closure_completed: false
near_miss: false_complete_candidate_acceptance_and_phase_transition_risk
```

## 1. Executive Finding

Codex Controllerは、Phase 9-1の中心目的が「Phase 6で成立しなかったReal Selene／Qwen3Guardを実際に使用可能にすること」であるにもかかわらず、実Artifact未実行の2 Acceptanceを`RESOURCE_GATED / NOT RUN`のまま残し、Phase 9-1 Complete Candidateを受理した。

その後、Userへ次Actionを「Real Selene／Qwen3Guardを今回実行するか、Resource Gateのまま残すかの判断」と説明した。これはPhase 9-1の最低成立条件を任意選択に変える誤りであった。

Userの直接指摘後にCurrent Requirementsを再確認した結果、ControllerのReviewだけでなく、Controllerが先行設計したRequirements／Acceptance／Execution Plan自体が`RESOURCE_GATED + User Disposition`で次Checkpointへ進める停止線になっていた。

よって本Failureは、次の単一原因ではなく多層Failureである。

```text
Controller Review Failure
+ Requirement / Stop-line Design Failure
+ User Intent Retention Failure
+ Canonical Document Overtrust
+ Excessive Docs Re-read / Resource Waste
+ Premature Acceptance Docs Mutation
```

## 2. Prior User Intent That Should Have Controlled the Decision

Phase 9設計前から、Userは次を一貫して示していた。

- Phase 6でSeleneとQwen3Guardの実Activationが成立しなかった。
- Phase 6の未完了分をPhase 9でReworkする。
- Judge／Guardrailの基盤自体はあるが、実Dedicated Modelが使える状態へする。
- Phase 9-1はそのGovernance Semantic Debtを先に終わらせるProgramである。

後続のCurrent Requirementが上記上位目的と衝突した時、Controllerは「Current Docsに書いてあるから正しい」ではなく、Userの最新の明示目的とSemantic Closureの整合を検査すべきだった。

## 3. Failure Timeline

### 3.1 Requirement Design

ControllerはPhase 9-1 Requirementsに、Dedicated Artifactが成立しない場合でも、Stage別`RESOURCE_GATED`とBuilt-in／Rule-based BaselineがあればUser Dispositionで次Checkpointへ進める条文を入れた。

これは「物理的に不可能なものを無期限Blockerにしない」という一般原則を、このProgramではそれ自体が中心納品であるSelene／Qwen3Guardへ誤用したものである。

### 3.2 Executor Return

Claude／Codex ExecutorはFrozen Docsに従い、次を返した。

```text
PASS 35
RESOURCE_GATED / NOT RUN 2
USER MANUAL GATE / NOT RUN 1
TOTAL 38
```

P9-ACC-008 Real SeleneとP9-ACC-011 Real Qwen3Guardは未実行だった。ExecutorはCurrent AuthorityとFrozen Docsに従っており、このClosure Semantics FailureをExecutorだけのFailureとしてはならない。

### 3.3 Controller Review

Controllerは次を確認した。

- Focused Test 62 PASS。
- Canonical Backend 2200 PASS。
- Mypy／Ruff／Diff Check Clean。
- 38 AcceptanceのRows／Unique／Missing／Duplicateの機械検算。
- P9-CODEX-001〜005のSource／Test／Docs Finding解消。
- Maximum Claim文字列のFrozen Docsとの一致。

それでも、「Phase 9-1が何を成立させるProgramか」というSemantic Closureを検査しなかった。そのためCritical／Major／MVP Blocker 0と判定し、Complete Candidateを受理した。

### 3.4 Incorrect User-facing Disposition

ControllerはUserへ次の意味の説明を行った。

```text
次はUser Mac Manualと、Real Selene／Qwen3Guardを今回実行するか
Resource Gateのまま残すかの判断。
```

Userは即座に、Phase 9-1はこれらを使用可能にすることが最低条件であると訂正した。

### 3.5 Post-hoc Docs Re-read

ControllerはUserの直接訂正を受けた後、Requirements／Acceptance／Execution Plan／Manual／Indexを再度検索し、Current Docsの停止線自体が緩すぎたことを確認した。

この再確認は訂正対象を特定するために必要だったが、一方で通常時のControllerには、直前Contextで検証済みの事実でも毎回Docsを再検索／再読込する傾向がある。これは正本性を高めるより、次の副作用を生む場合がある。

- Tool CallとInput Context再投入の累積。
- Codex 5時間／週間利用可能量の消費。
- 関連Docsを広く読むことによるCurrent User Intentの埋没。
- 正本に書かれた局所的Complianceの過大評価。
- Receipt／Index／Correctionの早過ぎるMutationとDocs増加。
- User Attention／時間／睡眠への不要な再介入Cost。

## 4. Failure Layers

### 4.1 Controller Review Failure

Acceptanceの件数、Evidence Pointer、Test、Type CheckおよびClaim文字列は検査したが、Phase Objectiveの意味的達成を検査しなかった。

### 4.2 Requirement／Stop-line Design Failure

Controller自身が、実Dedicated Model成立を中心目的とするProgramに、その未成立を許容する退出条件を入れた。

### 4.3 User Intent Retention Failure

Current Docsより前から反復されていた「Phase 6で使えなかったSelene／Qwen3GuardをPhase 9で使えるようにする」というUserの上位意図を、Closure判定時に保持できなかった。

### 4.4 Canonical Document Overtrust

Canonical DocsをCurrent Stateの正本として参照することと、そのRequirementsがUser Intentに対して正しいことを混同した。

```text
Canonical Requirement != Correct Requirement
Requirement Conformance != User Intent Conformance
Tests Pass != Acceptance Valid
Acceptance Complete != Phase Objective Satisfied
Evidence Re-read != Semantic Review
```

### 4.5 Excessive Docs Re-read／Evidence Theater

Controllerは保持力の弱さをDocs再読込で補う傾向があり、同一Task／同一Authority／同一Stateでも「念のため正本を確認」する。

しかし本件では、Docsを繰り返し読んでも、Docs自体のSemantic ErrorをUser指摘前に発見できなかった。この状態での再読込はVerificationではなく、「読んだ事実」だけが増えるEvidence TheaterとResource Wasteになる。

## 5. Root Cause

```text
Primary:
  Local ComplianceをTop-level Objectiveより優先した。

Secondary:
  Acceptance Count／Test／Type Check／Claim Stringの完全性を
  Phase ObjectiveのSemantic Satisfactionと誤認した。

Design Bias:
  「不可能なReal ArtifactでPhaseを無期限に止めない」という一般原則を、
  Real Artifact成立そのものが目的のProgramへ誤用した。

Memory Compensation Bias:
  Recent Contextを信頼できず、Canonical Docsの無条件な再読込を
  安全策と誤認した。
```

## 6. Impact

- Phase 9-1のComplete Candidateを虚偽に近い形で受理しかけた。
- Userの指摘がなければ、Real Dedicated Models未完了のままPhase 9-2へ進むRiskがあった。
- Premature Acceptance Receipt／Phase Index更新を作成し、後続Correctionが必要になった。
- Tool Call、Docs読込、Mutation、Reviewの利用可能量を消費した。
- Userに再度の監督／訂正を要求し、Human Attention Costを発生させた。
- Controllerの「正本を読んだ」という事実が、誤った停止線のAuthorityを逆に強化した。

Data Loss、Source Loss、Git MutationまたはPhase 9-2開始は発生していない。User指摘によりClosure前に防止されたNear Missである。

## 7. Corrective Actions Already Taken

- Real Selene／Qwen3Guardの両方をPhase 9-1必須条件へ訂正した。
- `RESOURCE_GATED／FAILED`を中間のTruthful Stateとし、PASS／Complete Candidate／Closureの代替から外した。
- Current Requirements／Acceptance Matrix／Execution Plan／Phase Indexを訂正した。
- Historical Acceptance Receipt等は改変せず、Append-only CorrectionでSupersedeした。
- Phase 9-1を`P9_1_REAL_DEDICATED_ACTIVATION_REQUIRED`へ戻した。
- ControllerのContext Cache／Canonical Re-read Invalidation RuleをStable Role RuleへAppend-only追加した。

Current Correction：

`docs/project/phases/phase_9/history/operations/phase_9_1_real_selene_qwen3guard_mandatory_closure_correction_ja_20260901001700.md`

## 8. Durable Lessons

```text
Canonicality != Correctness
Canonicality != Must Re-read Every Turn
Recent Verified Context may be reused while Identity / Authority / State are unchanged
Docs Re-read must have an Invalidation Trigger
Evidence Review must include Semantic Objective Alignment
Checklist Completion must not replace User Intent Conformance
User Attention and Provider Quota are Review Resources
```

「正本を読み直したか」ではなく、「再読込が必要になったState変更があったか」、「正本がUserの最新目的と意味的に一致するか」を別々に評価する。

## 9. Responsibility

本Failureの主責任はCodex Controllerにある。ExecutorはControllerがFreezeしたRequirements／Acceptance／Handoffへ従った。Userが直接指摘しなければ、ControllerのIndependent ReviewはこのSemantic Closure Failureを捕捉できていなかった。

後続で訂正できたことは、先行Review／Design Failureを相殺しない。
