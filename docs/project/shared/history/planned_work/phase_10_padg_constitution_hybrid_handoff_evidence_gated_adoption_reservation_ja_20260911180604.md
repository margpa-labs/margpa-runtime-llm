# Phase 10 PADG／Constitution Hybrid Handoff Evidence-gated Adoption予約

~~~yaml
document_id: phase_10_padg_constitution_hybrid_handoff_evidence_gated_adoption_reservation_20260911180604
document_type: append_only_planned_work
document_state: accepted_user_direction_not_started
language: ja
recorded_at: 2026-09-11 18:06:04 JST
decision_authority: user
target_phase: phase_10_and_later
target_packages:
  - Portable Autonomous Development Governance Package
  - Runtime Constitution
  - Development Agent Constitution
current_evidence_state: initial_operational_evidence_accumulating
adoption_state: not_yet_formally_adopted
implementation_authorized: false
git_authorized: false
network_authorized: false
append_only: true
~~~

## 1. 予約の目的

Development Agent間Handoffで導入した次の複合形式について、単発の成功やProvider自身の好意的評価だけで正式採用せず、複数の実運用Evidenceを蓄積する。

~~~text
Task Communication Identity Envelope
+ Natural-language Intent／Rationale
+ XML／Markdown Section Boundary
+ JSON Execution Contract
+ Exact Artifact Path／Digest
+ Trigger／Stop／Return／Maximum Claim
~~~

Evidenceから有効性、限界、Resource CostおよびFailure Surfaceを確認できた場合、Portable Autonomous Development Governance Package（PADG Package）とConstitution関連へ、責務を分けて取り込む。

本予約は、現在のHybrid Handoff方式を最終仕様として固定するものではない。現在地は、有力な運用仮説と初期実Evidenceを得た段階である。

## 2. 背景と現時点の限界

CodexとClaude Code間では、Provider、Task／Session ID、Role、Message Typeを明示したIdentity Headerと、自然言語、XML風境界、JSONおよびExact Artifact Identityを組み合わせたHandoffが実運用され始めた。

初期Evidenceでは、別Providerが同じIdentity体系でFrom／Toを反転してReturnし、Execution Contractに対応したWork Unit、Test、Finding、Maximum Claimおよび停止状態を返せることが観測されている。

一方、現時点では次を一般化できない。

- 特定のPhase、Task、ModelまたはProviderに偶然適合した可能性。
- 指示脱落や誤読が、従来方式よりどの程度減少したか。
- Handoff長文化によるToken、Context、Quotaおよび読取時間のCost。
- Compaction、Task再作成、App再起動または長期Recoveryを跨いだ有効性。
- Copilotその他Provider／HarnessでのPortability。
- Structured Contractを読んでも遵守しないAgent Failureへの実効性。

したがって、正式採用の前に追加Evidenceを必要とする。

## 3. 追加Evidenceの対象

### 3.1 作業種別

- 新規実装Handoff。
- Review Findingを返すRework。
- Partial ReturnからのResume。
- Context Compaction後のRecovery。
- Task／Session再開または再作成。
- Independent Review。
- Documentation／Evidence作業。
- Stop／Cancel／Quota Stop。

### 3.2 Provider／Harness

- Codex Task間。
- CodexからClaude Code。
- Claude CodeからCodexへのReturn。
- 利用可能であればCopilotその他Provider。

未検証Providerの結果を推測で補わない。同一Model Familyまたは同一Harnessの反復だけをProvider-neutral Evidenceとしない。

### 3.3 成功とFailure

成功例だけでなく、次も保存する。

- Identity Mismatch。
- 旧Task／Sessionへの誤配送。
- 古いHandoffの再送。
- User Relay時の欠落。
- Natural LanguageとJSONの矛盾。
- Invalid JSON、Duplicate Key、必須Field欠落。
- Stale Path／Digest。
- Scope、Forbidden、StopまたはReturn条件の脱落。
- Return未送信。
- Done過大Claim。
- Structured Contractを受領したにもかかわらず発生した逸脱。

方式導入後にFailureが発生した場合、方式全体が無効とも、Agent固有問題とも即断しない。検出可能性、被害抑制、Recovery可能性および原因範囲を分離する。

## 4. 各Evidenceで保存する項目

- Provider、Model、Harness、Task／Thread／Session Identity。
- From／To Role、Message TypeおよびRouting Method。
- Handoff Schema Version。
- Input Artifact Path／Digest。
- Natural-language、Section Boundary、JSON Contractの使用有無。
- Required／Forbidden／Acceptance／Stop／Return条件。
- 実際に実行したAction。
- ReturnとExecution Contractの対応関係。
- 指示脱落、追加解釈、Authority逸脱および誤配送。
- Recovery、Compaction、再起動等を跨いだか。
- 成功、失敗、部分完了およびUnknown。
- 発見されたFailureが構造で検出されたか。
- Token、Quota、Context、Latencyまたは読取Cost。観測不能値を捏造しない。
- User Observation、Controller Review、Provider Self-assessmentの区別。
- 改善候補と未確認事項。

Raw Secret、Credential、Provider非公開情報、不要な個人情報またはUser入力全文をEvidenceのために複製しない。

## 5. Evidence Class

~~~text
Direct Runtime／Repository Evidence
User Observation／Decision
Controller Independent Review
Provider Self-assessment
Cross-provider Assessment
Inference
Recommendation
Unknown／Not Tested
~~~

Provider自身の「分かりやすかった」という感想は有効な研究材料だが、独立検証や一般的な効果証明ではない。Self-assessmentとして保存し、実際のContract遵守、Diff、Return、FailureおよびResource Evidenceと分離する。

## 6. 正式採用前の評価観点

固定回数だけで機械的に採用せず、少なくとも次を確認する。

1. 複数の作業種別でRequired／Forbidden／Return条件を再構築できる。
2. 可能な範囲で複数Providerまたは複数Harnessの結果がある。
3. 成功例だけでなくFailureまたはNear Missも評価されている。
4. Task／Session Identityが誤配送の予防または検出に役立つ。
5. XML／Markdown境界がContextとInstructionの混同を減らす。
6. JSON ContractがExpected StateとObserved Actionの差分を取れる。
7. Exact Path／DigestがArtifact誤認またはStale Inputを検出できる。
8. Natural LanguageがJSONだけでは保持しにくいIntentとRationaleを補える。
9. Token／Quota／Context Costが、得られる検証性に対して過大でない。
10. 短い作業へ過剰なPacketを強制しない適用境界を定義できる。
11. Compaction／Recovery後もRole、Authority、Current WorkおよびExact Next Actionを復元できる。
12. 未遵守Agentを完全に防げなくても、違反を検出、Evidence化、Recoveryできる。

## 7. PADG Packageへの取り込み候補

有効性が確認できた場合、PADGには運用Ruleの文章だけでなく、次のPortable Componentとして取り込む。

- Provider-neutral Communication Identity Envelope。
- Task／Thread／Session IDのProvider Adapter。
- Hybrid Handoff Template。
- Handoff JSON Schema。
- Duplicate Key、Enum、Required Field、Path、Digestの送信前Validator。
- Natural Language／XML／JSON間Conflict Detector。
- Expected ContractとActual Trace／Returnの差分検査。
- Start、Rework、Resume、Finding、Return、StopのMessage Type。
- Stable BaselineとCurrent Task Deltaの分離。
- Handoff Replay／Recovery／Compaction用Artifact。
- Provider／Harness別のVerified Operational Envelope。
- Token／Quota／Contextに応じたShort／Standard／Long Profile。

PADGへ取り込む場合も、IdentityをAuthorityとして扱わない。通信先を識別できることと、Mutation、Git、External Action、Closureその他の権限を持つことを分離する。

## 8. Constitutionへの取り込み候補

追加Evidenceで妥当性が確認できたRuleだけを、Provider非依存Invariant候補へ昇格する。

- Task／Session Identity一致はRole一致またはAuthority成立を意味しない。
- Knowledge／Context RecoveryはAuthority Recoveryを意味しない。
- Structured ContractはUser Decisionを置換しない。
- Natural Language／JSON／Artifact間Conflictを都合よく補完しない。
- Invalid／Stale／Identity Mismatch時は開始しない。
- Unknown、Not Run、PartialをPASSへ変換しない。
- Work StoppedはDoneを意味しない。
- DoneにはPlanned Work、Required Evidence、Acceptance／Closureの各Gateが必要である。
- Final Return必須Taskは、Return未送信のまま完了しない。
- Handoffを読んだこと自体はMutation／Git／External／Closure Authorityを生成しない。
- Provider固有識別子、ToolおよびPrompt作法をCommon CoreへHard-codeしない。

Constitutionへ取り込む際は、説明的Recommendation、機械検査できるRule、Runtime Enforcement、Evidence RequirementおよびHuman-only Authorityを分離する。

## 9. 採用State

~~~text
observed
  -> evidence_accumulating
  -> portable_candidate
  -> cross_context_validated
  -> adopted_in_padg_and_or_constitution
  -> monitored
  -> revised_or_deprecated
~~~

現時点はevidence_accumulatingである。Evidenceが不足した状態でcross_context_validatedまたは正式採用をClaimしない。

PADGとConstitutionは別々に採否を判断できる。Handoff Templateとしては有効でも、強制Constitution RuleとしてはEvidence不足というDispositionを許容する。

## 10. 採用後のRegression候補

- 正しいIdentity Packetの受領／Return反転。
- Task ID一致＋Role不一致の拒否。
- 古いHandoff Revisionの拒否。
- Digest不一致のCall／Mutation 0。
- Duplicate Key／Invalid JSON／必須Field欠落のReject。
- Natural LanguageとJSONのAuthority Conflict。
- Forbidden ActionをActual Traceから検出。
- Partial ReturnをCompleteへ変換しない。
- Compaction後にBootstrap＋Current Handoffから復旧。
- Provider Adapter変更後もCommon Contractが同義であること。
- Short Profileが必須Authority／Stop／Returnを落とさないこと。

## 11. 現時点のEvidence Pointer

- docs/project/shared/history/automation/codex_claude_identity_envelope_hybrid_handoff_immediate_operational_round_trip_evidence_ja_20260911164918.md
- docs/project/shared/history/automation/development_agent_task_id_role_dual_identity_communication_decision_evidence_ja_20260910150333.md
- docs/project/shared/history/automation/development_agent_hybrid_handoff_and_provider_neutral_role_bootstrap_decision_evidence_ja_20260909083759.md
- docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md
- Phase 9-3完了後に作成予定のClaude Code Operational Self-assessment Evidence。

最後の項目は、本予約作成時点では未作成である。存在しないPath、結果または結論を記録しない。

## 12. 現在地と次Action

~~~text
Hybrid Handoff operational use       : STARTED
Initial Codex-side assessment         : RECORDED
Claude Phase 9-3 self-assessment      : PLANNED／NOT YET RECORDED
Cross-task evidence accumulation      : IN PROGRESS
PADG formal adoption                  : NOT DECIDED
Constitution formal adoption          : NOT DECIDED
Schema／Validator implementation      : NOT STARTED
~~~

次Actionは、今後のDevelopment Agent間Handoffで追加Evidenceを蓄積し、成功、Failure、Resource CostおよびProvider差を比較することである。有効性が確認できた場合に限り、Phase 10以降のPADG／Constitution設計へ反映する。

本書は、PADG、Constitution、Validator、SchemaまたはRuntime Enforcementの実装Authorityを生成しない。

