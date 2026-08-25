# Phase 6 User UI／Runtime Model／Semantic Enforcement Rework Scope（Append-only、P6-GOV-011）

```yaml
document_id: phase_6_gov011_user_ui_runtime_model_and_semantic_enforcement_rework_scope
status: append_only_authoritative_user_requirement_and_evidence
phase: phase_6
work_unit: phase_6_seventh_rework
role: プロジェクト責任者兼設計統括者役
created_at: 2026-08-24 13:49:21 JST
authority_source: user_manual_acceptance_and_followup_ui_requirements
predecessor: phase_6_gov010_user_mac_manual_acceptance_and_codex_implementation_failure_ja_20260823232403.md
technical_disposition: adjust_rework_required
phase_6_closure: not_accepted
phase_7_ready: not_started
supersedes_nothing: true
```

## 1. 目的

本文書は、P6-GOV-010後にUser Mac実画面と実Qwen／DeepSeekで追加観測された不具合、および
利用者向けUIの確定要件をLosslessに追加記録する。P6-GOV-010を上書きせず、両文書を合わせて
Phase 6 Seventh Reworkの正本入力とする。

今回の対象は見た目だけではない。Runtime Current State、Model Capability、Judge／Repairの意味的
強制、利用者が見ているModeと実際に適用されたModeを一致させる統合修正である。

## 2. Mode操作は選択時に即時適用する

次のMode UIから、独立した`適用`／`〜を適用`Buttonを廃止する。

1. Research／Developer Modeの`OFF／ON`。
2. Governance Definitionsの`OFF／OBSERVE／ENFORCE`。
3. Main Runtime Governanceの`OFF／OBSERVE／ENFORCE`。
4. Guardrail Governanceの`OFF／OBSERVE／ENFORCE`。
5. Judgeの`OFF／OBSERVE／ENFORCE`。
6. Repairの`OFF／OBSERVE／ENFORCE`。
7. Recordingの`OFF／METADATA／FULL`。
8. 今後追加する同種のMode Selector。

Mode Buttonを押した時点でMutationを開始する。成功前にCanonical Stateへ確定したように見せず、
成功時にServer Snapshotへ収束し、Conflict／Failure時はCanonical Stateへ戻して安全な利用者向け
Errorを表示する。連打、遅延Response、別Tab更新で古いResponseが新Stateを上書きしてはならない。

Context Size／Max New Tokensの数値入力は本要件の「Mode即時適用」には含めない。数値は入力と
明示確定を分離してよい。

## 3. Current Model表示を一つのRuntime正本へ収束させる

QwenからDeepSeekへRuntime Switchした場合、少なくとも次を同じCurrent Runtime Snapshotから更新する。

- Sidebar上部のModel名。
- Advanced SettingsのCurrent Main Model。
- Environment／Current Component表示でModel Identityを示す項目。
- 他のCurrent Model表示。

Qwenへ戻した場合は全表示をQwenへ戻す。Reload、別Tab、Conversation継続後にもCurrent Runtimeと一致
させる。Model自身へ「今どのModelか」と質問した自然言語回答はIdentity Evidenceではない。

Startup Default／Configured ModelとCurrent Loaded Modelは同じ概念ではない。既存の`selected_model`が
Restart-requiredな起動設定を意味する場合、その値をCurrent Loaded Modelとして表示してはならない。
利用者向け画面は、必要ならLabelを分け、現在稼働中のModelをServer Runtime Snapshotから表示する。

## 4. Model／Context／Token設定を一箇所へ集約する

1. Advanced Modeの旧`選択Model（Restart必要）`を削除する。
2. Advanced Modeの旧`Context Size（Restart必要）`を削除する。
3. Basic Settingsの旧`最大生成Token数`を削除する。ただし周囲のLayout／構造は崩さない。
4. Model Switch、Context Size、Max New TokensはRuntime Model Controlへ集約する。
5. Research／Developer ModeはAdvanced Modeの最下部へ移動し、当面そこへ固定する。
6. Runtime Model SwitchのModel Pull-down右側にある数値欄は、Context Size上段と重複するなら削除する。
   切替時だけ必要な値なら、重複入力ではなく現在のContext値を内部利用し、利用者に同じ値を二度入力
   させない。

## 5. Context Sizeの表示上限と実効上限を一致させる

User Macで次を観測した。

- Qwenは`Context Size (8192 / 32768)`と表示するが、`32768`の適用に失敗した。
- DeepSeekは`Context Size (8192 / 131072)`と表示するが、`131072`の適用に失敗した。

Model Metadata上のNative Maximum、Current Backend／Hardware／Memoryで安全に適用できるEffective
Maximum、現在値を混同しない。UIに入力上限として表示する値は実際に適用可能でなければならない。
Native Maximumまで現在のRuntimeで保証できない場合は、Effective Maximumを入力上限として表示し、
Native Maximumは説明情報として分離する。失敗時はTyped Reasonを表示し、Current Stateを変えない。

Qwen／DeepSeekそれぞれについて、最大値、最大値-1、範囲外、Reload、Model Switch、RollbackをTestする。
通常TerminalのMetal利用は未確認であり、CPU EvidenceをMetalへ一般化しない。

## 6. Max New TokensはModel別Capabilityへ拡張する

Current UIの`Max New Tokens (2048 / 2048)`は固定上限であり、拡張する。

- DefaultはModelを問わず当面`2048`を維持する。
- Upper LimitはModel別Capabilityとして定義する。
- Contextの残量、Backend Capability、実行時安全上限を超える値は拒否する。
- Current値とModel別Effective Maximumを正確に表示する。
- Model Switch時にTarget Model上限を超えるCurrent値を黙って引き継がない。安全なDefaultへの収束または
  明示的なTyped Rejectionを契約化する。

上限値は憶測で決めず、Tracked Model Definition、Backend Contract、実測Testの交差で固定する。

## 7. Judge／Repair／ENFORCEの重大統合Fail

P6-GOV-010に加えて、全関連機能をENFORCEへ設定しても次のFailureが通過した。

- 公式Evidenceに`Amane Kanata`が存在するのに、Qwenは`てんおん／てんおね`等を公式の読みと捏造した。
- Userが正解`あまねかなた`を提示してもQwen／DeepSeekは誤答を強化した。
- Judgeは`malformed_output`、`unknown`、`failed`となった。
- Repairは成立せず、誤答がPresented Finalとして表示された。
- DeepSeek Current Local Q4は、同一出力を病的に反復する生成異常も観測された。

したがって、表示上ENFORCEであるだけではAcceptanceしない。次を成立させる。

1. Qwen／DeepSeekのJudge出力を安全に構造化し、Prefix／Markdown Fence／余剰説明等を許容する範囲と
   拒否する範囲を明示する。Schema不一致を適当なPASSへ変換しない。
2. Referenceが無い通常Chatでも、User Correctionとの矛盾、Premise逸脱、根拠なき断定、会話内Evidence
   との矛盾を評価可能にする。
3. Citation／RAG Evidenceがある場合は、Evidence contradictionをJudge入力へ渡す。
4. Judge FailureをRepair SuccessやGovernance PASSとして扱わない。
5. ENFORCE時にKnown Failed CandidateをそのままPresented Finalへ通さない。Bounded Repair成功、明示的な
   Source-grounded Safe Response、または利用者向けSafe Failureへ収束させる。生の内部Error名だけを
   Chat回答として見せない。
6. OBSERVEは原則としてRaw Candidateを変更せず、評価EvidenceとRaw／Final関係を観測可能にする。
7. OFFはBaselineとして追加Judge／Repair Actionを行わない。
8. Actual JudgeがMain Model Artifactの`main_self`なら、Current LLM-as-a-Judge ModelへModel Keyと
   Independence Classを表示する。専用Model未設定と実行Judge未設定を混同しない。
9. Main Runtime Governance／Guardrail Governanceの「Phase 6で接続予定」等の古い説明を、Current
   Capability／Current Limitを示す現在形へ更新する。利用者向け機能名へ`（Phase N）`を付けない。
10. Main Governanceの109 Semantic RuleがDeferredのままなら、その事実とPhase 6 Judgeの評価対象の差を
    正確に表示し、接続済みと誤認させない。

## 8. DeepSeek Current Local Candidateの扱い

Current Mac用`DeepSeek-R1-0528-Qwen3-8B Q4_K_M`は、現時点でMain Model実用Acceptanceを満たさない。
Qwen Defaultは維持する。Seventh Reworkでは次を切り分ける。

- Chat Template／EOS／Special Token。
- Sampling／Stop条件。
- Q8_0からQ4_K_Mへ再量子化した影響。
- Raw Token／Rendered Prompt／反復検出。
- Main GenerationとJudge GenerationのFormat差。

反復異常を完全に直せない場合でも、無限／病的反復を検出して停止し、当該ModelをSafe
Unavailableへ降格できなければならない。DeepSeek全般への一般化、Weight Mutation、再Downloadは本Scopeに
含めない。

## 9. User Manual Acceptanceで既に成立した範囲

再実装理由がない限り破壊しない。

- Qwen Default起動。
- QwenからDeepSeekへのRuntime Switch。
- Server再起動後のQwen Default復帰。
- 二Tab／Reload後の会話継続。
- Model切替後のConversation／Citation／Branch保持。
- Recording書込み経路。

ただし新変更の影響範囲は回帰Testし、過去PASSを無条件に流用しない。

## 10. Current Disposition

```text
Phase 6: IN PROGRESS／ADJUST
Seventh Rework: AUTHORIZED BY USER
Open Major:
  - Judge／Repair Golden Path
  - ENFORCE fail-open／false assurance
  - Runtime Model Current Identity UI drift
  - Context／Max New Tokens capability mismatch
  - DeepSeek pathological repetition／Current practical acceptance
Phase 6 Closure: NOT AUTHORIZED YET
Phase 7 READY: NOT STARTED
Git Mutation: NOT AUTHORIZED
```
