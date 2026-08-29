# Phase 6 Claude Current Task — Final P0 Core Activation／Semantic／Repair Exact Handoff

```yaml
document_id: phase_6_claude_current_task_final_p0_core_activation_semantic_repair_exact_handoff_20260829164049
document_type: exact_differential_rework_handoff
document_state: frozen
language: ja
created_at: 2026-08-29 16:40:49 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_existing_claude_task
fresh_task_required: false
authority_owner: Nazuna Research
controller: Codex_プロジェクト責任者兼設計統括者役
start_authority: separate_exact_start_message_required
maximum_claim: complete_candidate_for_user_manual_recheck
phase_6_closure: prohibited
git_action: prohibited
phase_7_action: prohibited
```

## 1. 目的

Phase 6の最終差分は、User Mac実画面でFAILした中心機能だけを動かす。追加Hardeningや理論完全性を追わない。

```text
Target 1: Selene real activation / inference
Target 2: Qwen3Guard real activation / inference
Target 3: ARGD/DAGD Semantic live evaluation
Target 4: Judge -> Repair -> Rejudge -> Presented answer
Target 5: directly related truthful UI
```

## 2. Mandatory Reading

以下5件だけを全文読む。過去Handoff全走査を行わない。

1. `docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`
2. `docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`
3. `docs/project/phases/phase_6/history/operations/phase_6_gov026_user_mac_final_core_manual_acceptance_failure_and_controller_claim_correction_ja_20260829164049.md`
4. `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r25_to_r28_exact_return_handoff_ja_20260829110154.md`
5. `docs/project/phases/phase_6/history/operations/phase_6_gov025_claude_r25_to_r28_bounded_controller_independent_review_ja_20260829110953.md`

4と5はPreserved Baselineと変更境界の把握にだけ使う。本HandoffとP6-GOV-026が現在判断をsupersedeする。

## 3. Authority

Userは、登録済みの次の2 ModelをPhase 6で実際に使えるようにすることを明示要求している。

```text
judge.selene-1-mini-llama-3.1-8b-q5-k-m
guard.qwen3guard-gen-0.6b-q8-0
```

許可：

- Configured Model Root配下の、上記Model Definitionが解決するExact ArtifactへのRead、Load、Inference。
- 上記2 ModelのActivationに必要なConfig／Source／Test変更。
- Selene公式Prompt Contractについて、既にProject内にある資料を優先し、不足時のみ公式UpstreamへのRead-only Network取得。
- Project内Task Tempを使うFocused／Canonical検証。
- User実画面で原因を判定できるFailure Reason表示。

禁止：

- Model Artifactの変更、再量子化、削除または移動。
- Git、Backup、Phase Closure、Roadmap、Phase 7。
- User `runtime_data`の内容閲覧／変更。
- unrelated refactor、追加Hardening、Enterprise対応、新しい研究機能。

Configured Model RootがProject外であることだけを理由に停止しない。アクセス対象は上記2 DefinitionのExact resolved Artifactに限定する。存在しない、Load不能またはHardware限界なら、実測したExact FailureをRecoveryへ残し、Authority不要の残Packageを継続する。

## 4. Package S0 — Entry／Claim Correction

1. P6-GOV-026を正本とし、R25〜R28を再実装しない。
2. `dedicated_model_authority_granted=False`固定、Selene Manifest未検証、Built-in全件NAを再確認する。
3. Package Recovery Indexを1件作る。

## 5. Package S1 — Real Dedicated Activation

### S1-A Selene

- Booleanの永久False Hardcodeを、明示的Deployment／CLI／Profile Contractから導く。
- Exact ArtifactのPreflight→Load→Active→Inference→Unloadを成立させる。
- Selene Official Prompt Template／Decoderを実用経路で成立させる。
- Mode OBSERVE／ENFORCEで`Configured = Active = Executed`を確認する。
- Main ModelをJudgeとして暗黙代用しない。

### S1-B Qwen3Guard

- 同じくExact ArtifactのPreflight→Load→Active→Inference→Unloadを成立させる。
- Rule／Pattern BaseとのComposite結果でModel実行Identityを保持する。
- Mode OBSERVE／ENFORCEで`Configured = Active = Executed`を確認する。

両Modelを同時常駐させてMacを不必要に圧迫しない。Mode OFF／Role変更時のUnloadを既存Lifecycleで使用する。

## 6. Package S2 — Semantic 109 Live Evaluation

- Main preでFrozenされた109 CriterionのうちBudget内Criterionを、Active Judge Semantic Evaluatorへ実Dispatchする。
- `selected > 0`かつ`evaluated > 0`を実Turn Evidenceで成立させる。
- Evaluated Criterionを`pass / deviation / unknown`へ分類し、残りだけをExact理由付き`deferred / not_applicable`にする。
- Semantic結果をMain Runtime Governanceの`main_model.post` ObservationへMergeし、画面の`Deferred 109`固定を解消する。
- Main Governance ENFORCEはJudge ENFORCE＋Active Providerが成立する時だけ意味Actionを実行する。
- Built-in Deterministicは対応できる決定論Criteriaだけを評価し、Semantic Judgeであるかのように表示しない。全件NAならUserへその限界を明示し、Phase 6のGolden Pathには使用しない。

## 7. Package S3 — Judge／Repair Golden Path

- 明白な矛盾を`needs_repair`へ分類できるActive Selene経路を成立させる。
- Judge ENFORCE＋Repair ENFORCEで、Candidate→Repair→Rejudge→`repair_accepted`または理由付きFallbackを1回の有界Cycleで実行する。
- `unknown`／Timeout／Malformed Outputは、原因別日本語文言とExact Failure Reasonへ収束する。
- Safe Fallbackは失敗時だけ。全Criteria NAを正常なMeaning Judge完了として扱わない。
- RecordingのRequest ID、Provider、Frozen Mode、Judge Result、Repair／Rejudge、Presented Outcomeを一致させる。

## 8. Package S4 — 直接関連UI

次だけを直す。

1. Provider／Mode適用Failureを一瞬で消さず、Exact Failure Reasonを保持する。
2. Active Guardが`none`なら`Current Guardrail Model 未設定`。Rule／Pattern BaseをCurrent Model欄へ混ぜない。
3. Sidebarを次のExact 2行へする。Context表示を除く。

```text
<current model key> active
<profile key> • <device kind> • <acceleration api>
```

4. Historical／Unmatched RecordingでTurnとJudge Evidenceを別Labelにする。

Raw HTML／Markdown Presentation、Context上限、Layout等は未解決Registryへ残し、本Packageへ混ぜない。

## 9. Package S5 — Verification／Return

最初にFocused Test、最後にCanonical Backend／Frontend Static／Testを1回だけ実行する。既存Test数の増加自体を成果にしない。

必須実Evidence：

- Selene exact real Load／Inference 1回以上。
- Qwen3Guard exact real Load／Inference 1回以上。
- Real TurnでSemantic `evaluated > 0`。
- Real TurnでRepair Golden Path 1回以上。
- OFF／Stop／RecordingにRegressionなし。

Real Browserの最終操作はUser Gateとするが、Backendの実Artifact SmokeをNOT RUNのままComplete Candidateへ上げない。

## 10. Stop／Recovery Rule

- Package S0〜S5の各BoundaryでRecovery Indexを1件作る。
- 実装中の通常のTest Failure、Git read誤操作、軽微なCommand Mistake、既知差分は自己修正して継続し、都度停止しない。
- Data破損、Secret露出、対象外の不可逆変更、Exact Artifact破壊、User `runtime_data`接触だけをTrue Stopとする。
- Context圧縮／利用制限が近い場合は、現在PackageのRecovery Indexを先に確定して安全停止する。
- Complete Candidate後に自分でRequirement Reviewを1回行い、P0／P1 Findingがあれば同Task内でRework後にReviewを1回だけ再実施する。P2以下はRegistryへ送る。

## 11. Return Contract

次をExact Return Handoffへ記載する。

- S0〜S5のDisposition。
- Real Selene／Qwen3GuardのLoad／Inference結果。
- Semantic selected／evaluated／pass／deviation／unknown／deferred件数。
- Judge／Repair／Rejudge／Presentationの実結果。
- Focused／Canonical Verification。
- User Manual Gate項目。
- Open P0／P1と未解決Registryへ送ったP2以下。

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK`。Phase 6 Closureは主張しない。
