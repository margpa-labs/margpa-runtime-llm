# Phase 9-1 Component完全疎結合 R3残差Rework Recovery

```yaml
document_id: phase_9_1_component_independence_r3_residual_rework_recovery_20260905193300
document_state: complete_recovery
language: ja
created_at: 2026-09-05T19:33:00+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 18:17:01 JST Controller Review(R2 Returnに対する`CHANGES REQUIRED`、IR-R2-01〜05)を受け、同時刻発行のR3残差Rework Exact Handoffに従い、R3-WU-01からR3-WU-06までを順に実施した。R3-WU-01(Turn開始Freezeの単一Immutable境界化)、R3-WU-02(Built-in経路のEvidence Identity修正)、R3-WU-03(Cancellation Terminal Raceの解消)の3件は解決を確認した。R3-WU-04(Gemma Schema非曖昧化)はHandoffが定義した通常All-Accept Scopeについては2/2実機Trialで解決を確認したが、続くR3-WU-05の実機Trialで、Deviation報告時(非空`evidence_refs`/`reason_code`)には同種のMalformed JSON Defectが再発するという新規Findingを確認した。R3-WU-05自体はFixture水準(実Composition Root経由)では完全に解決したが、実機水準は1 Trialで正直にFail(Skipなし)のまま停止した。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `runtime_governance.py`: `JudgeSemanticTurnProvider.__call__`が既に解決済みの`judge_modes`を第2引数として受理し独立Live再読を廃止。Turn開始Freeze失敗を`request_id`単位で記録し、以降の同一`request_id`呼び出しの遅延再Freezeを根絶。戻り値型を`SemanticTurnSnapshot \| None`へ変更。
- `conversation_generation.py`: `semantic_turn_begin_hook`のシグネチャを2引数(`request_id`, `judge_modes`)へ変更。
- `judge_live_integration.py`: Completion時解決Provider IdentityがTurn開始時Active Providerと不一致の場合のGate(Model Call 0)を追加。Built-in経路の`_pending_evidence()`呼び出しでMain自身のIdentityを誤って渡していたBugを修正。ENFORCE Wait LoopでWorkerの既に正しいTerminal ResultをGeneric Reasonで上書きしないよう修正。
- `semantic_criteria.py`: `SemanticDeferredReason.PROVIDER_IDENTITY_MISMATCH`を新規追加。
- `selene.py`: `GemmaPromptAdapter`(`SelenePromptAdapter`のSubclass)を新規追加——Gemma専用経路のみ、Schema例の自然言語Placeholderを非曖昧な実例へ置換。
- `dedicated_role_adapters.py`: `SeleneRoleAdapter`に`prompt_adapter_factory`を追加し、Gemma分岐のみ`GemmaPromptAdapter`を指定。
- `config/judge_templates/gemma_4_e2b/*`: R2で追加したRule 6(打ち消しRule)を削除、Manifest Digestを再計算。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_component_independence_r3_residual_rework_exact_return_ja_20260905193256.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_component_independence_r3_residual_rework_exact_return_ja_20260905193256.md](../../handoffs/phase_9_claude_component_independence_r3_residual_rework_exact_return_ja_20260905193256.md)

Maximum Claim: `P9_1_R3_WU01_WU02_WU03_RESOLVED_WU04_NORMAL_ACCEPT_SCOPE_RESOLVED_WU05_FIXTURE_RESOLVED_REAL_TRIAL_FAILED_MALFORMED_ON_DEVIATION_CONTENT`

## 5. Open Items at This Point

- Gemma Malformed JSON Defectは、Deviation報告時(非空`evidence_refs`/`reason_code`)については未根絶——R3-WU-05実機Trial(`execution_state='failed' failure_reason='malformed_output' criteria_evaluated=0`)で確認した新規Finding。次の一手はCodex Controllerの明示的判断待ち。
- R3-WU-05の実機Golden Path Hard Assertion(`repair_requested_by`等)は、初回Judge自体がMalformed Outputで停止したため実機では未到達のまま——Fixture水準では確認済み。
- R3-WU-05実機Trialは1回のみ、再現性は未検証(R3-WU-04の2 Trialが完全に決定的だったことから同一結果になる可能性を推定するのみ)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手、追加の実機Trial、Decoder緩和/JSON補修/Retry追加のいずれも行わない。
