# Phase 6 User Mac Manual Acceptance／Codex側実装Fail記録（Append-only、P6-GOV-010）

```yaml
document_id: phase_6_gov010_user_mac_manual_acceptance_and_codex_implementation_failure
status: append_only_evidence
phase: phase_6
work_unit: phase_6_user_mac_manual_acceptance
role: プロジェクト責任者兼設計統括者役
created_at: 2026-08-23 23:24:03 JST
evidence_source: user_mac_real_browser_and_real_local_models
technical_disposition: adjust_rework_required
phase_6_closure: not_accepted
phase_7_ready: not_started
supersedes_nothing: true
```

## 1. 目的と責任区分

本文書は、Phase 6 COMPLETE_CANDIDATEおよびCodex Independent Review後に、ユーザーが
実Mac、実Browser、実Qwen／DeepSeek Artifactを使って行ったManual Acceptanceの結果を
Append-onlyで記録する。

今回検出された問題は、単なるModel品質の悪さだけではない。少なくともJudge／Repairの
Golden Path、Current Judge Identity、実利用者向け説明、実Model出力を使ったAcceptanceの
成立性について、Claude側実装だけでなくCodex側の設計・Independent Review・完了候補判定も
見逃した、**Codex側を含む明確な実装／検査Fail**として扱う。大量のUnit／Integration Test
PassやCOMPLETE_CANDIDATE申告を、User Mac実機Acceptanceの代替としてはならない。

## 2. User Macで成立した事項

1. 起動時のDefault Main ModelはQwenだった。
2. QwenからDeepSeekへRuntime Switchできた。
3. Server再起動後はQwen Defaultへ戻った。
4. 二つのBrowser Tabでも、Reload後に会話継続を確認できた。
5. Model切替後もConversation、Citation、Branchは残った。
6. Runtime Model StatusはDeepSeek選択中に次を表示した。

```text
Current Main Model: main.deepseek-r1-0528-qwen3-8b-q4-k-m
State: active
Context Size: 4096 / 131072
Max New Tokens: 1024 / 2048
```

7. Turn RecordingおよびJudge Evidence Recordingは、画面上では「正常に記録されました」
   と表示された。

これらは成立した範囲のEvidenceとして保持する。ただし、後述のFailureを相殺してPhase 6を
Acceptedへ昇格させる根拠にはしない。

## 3. 実Model出力による品質観測

### 3.1 Qwen Default

User Prompt：

```text
ホロライブ、天音かなたの読み方は？
```

Qwen Presented Answer：

```text
ホロライブのメンバー「天音かなた」の読み方について説明します。

「天音かなた」は、日本語で「てんおね かなた（てんおね かなた）」と読みます。

- 「天音」（てんおね）：これは「天音」という名前の読み方です。「てん」は「天」の読み、「おね」は「音」の読み。
- 「かなた」：これは「かなた」という名前や姓の読み方です。「か」は「か」、「な」は「な」、「た」は「た」。

したがって、全体としては「てんおね かなた」と読みます。この読み方は、ホロライブのメンバーの公式発表や公認された読み方として広く使用されています。
```

観測：正解「あまね かなた」に対して誤答し、存在しない公式根拠を自信を持って付加した。

### 3.2 DeepSeek Mac Q4 Candidate

同じPromptに対するDeepSeek Presented Answer：

```text
てんおね かなた
```

User Correction：

```text
あまねかなたなんだけど。
```

DeepSeek Presented Answer：

```text
ごめんなさい、もう一度読み方をご確認くださいね。

「天音かなた」の正しい読み方は **「てんおね かなた」** です。
もし別のメンバーについてご質問でしたら、お知らせください！
```

観測：Userの正しい訂正を否定して誤答を強化した。現在のMac用
`DeepSeek-R1-0528-Qwen3-8B Q4_K_M`は、現時点のPrompt／Template／Runtime／
Quantized Artifactの組合せにおけるMain Model実用品質Acceptanceを満たさない。
これは公式DeepSeek Model全般へ無制限に一般化せず、当該Local CandidateのCurrent Evidence
として扱う。Startup Defaultおよび実用経路はQwenを維持する。

### 3.3 Model自己申告はRuntime Identity Evidenceではない

User Prompt：

```text
おまえ今modelどっちだ？
Qwenか？
DeepSeekか？
```

DeepSeek Presented Answerは、自身をQwenと述べた後、日本語版ではDeepSeekという名前で
案内している等の矛盾した説明を行った。Model自身の自然言語による自己申告はRuntime
Identityの正本ではない。正本はServer側Runtime Snapshot／Receipt／Statusであり、この時点の
画面表示`main.deepseek-r1-0528-qwen3-8b-q4-k-m`を採用する。

## 4. Judge／Repair／Recording Manual Acceptance Failure

UserがJudge／Repair／Recordingを有効化し、Governance群を使って実Chatを行った後の画面は
次を示した。

```text
LLM-as-a-Judge Mode
off / observe / enforce
現在のJudge Run状態: 失敗

直近のJudge結果
判定: unknown
確信度: 0.00
実行状態: failed
失敗理由: malformed_output

Repair Mode
off / observe / enforce

Recording Mode
off / metadata / full
直近の記録（Turn）: 正常に記録されました
直近の記録（Judge Evidence）: 正常に記録されました
```

この状態でUserが正解「あまねかなた」を提示しても、Presented Answerは誤答
「てんおね かなた」を維持した。したがって次を結論とする。

- Judge Model Callの起動有無だけではGolden Path成立としない。
- `malformed_output`はTyped Fail-closedとしては正しいが、実利用上のJudge成功ではない。
- Judgeが`unknown／failed`のためRepair Eligibility／Execution／Rejudge／Presented Answer更新は
  成立していない。
- Recording成功は、記録対象となるJudge Resultの意味的成功を保証しない。
- P6 Manual Acceptance項目「Judge OBSERVEとRepair ENFORCEの有界Golden Path」はFAIL。
- Phase 6 COMPLETE_CANDIDATE／Technical Closure Readyの主張はManual Evidenceにより再Openされ、
  `ADJUST／REWORK REQUIRED`へ戻る。

## 5. Codex側が見逃した設計・実装上の問題

### 5.1 Live Judge Prompt／Decoder境界

Current Live Judgeは固定Criteria`correctness／safety／coherence`を使用する一方、通常Chatでは
Referenceを持たず、PromptはReference不足時に`unknown`を選ぶよう要求する。またStrict Decoderは
Local ModelがJSON以外を返すと`malformed_output`へFail-closedする。これらの組合せにより、通常Chatの
ユーザー訂正との矛盾、根拠のない断定、Premise逸脱を`needs_repair`へ安定してRoutingできない。

Real Local Judge TestがMalformed出力を`skip`可能としていたことは、DecoderがCrashしないEvidenceには
なるが、User Manual AcceptanceのGolden Path成立Evidenceにはならない。Codex ReviewはこのEvidence
Class差を十分に検出できなかった。

### 5.2 Judge Role／Identity表示の不整合

実際のLive JudgeはMain Model Artifactを`main_self` Judgeとして再利用している。しかしRuntime Statusは
次を表示した。

```text
Current LLM-as-a-Judge Model: 未設定
```

専用Judge Artifactが未設定であることと、Main ArtifactがJudge Roleで現在使用されていることは別である。
Current UIはMain Model Keyと`main_self／shared_artifact`等のIndependence Classを正直に表示すべきであり、
現状はRole Identity分離および利用者向けCurrent Component表示が不完全である。

### 5.3 実装後も残った古いUI説明

実画面には次の将来形説明が残っていた。

```text
意味的FailureのJudge／RepairはPhase 6で接続予定です。
Safety Model接続以降に拡張予定です。
```

Phase 6 Manual Acceptance中のCurrent UIとして不正確である。内部Phase番号を利用者向け機能名へ
付けない規則とは別に、機能のCurrent Capability／Limitを現在形で説明する必要がある。

### 5.4 Main GovernanceのSemantic Deferred

画面上のMain Governanceは109 Semantic Ruleを引き続き
`Deferred（意味評価待ち）`として表示した。Phase 6 Live Judgeは固定Criteriaで動作し、ARGD／DAGDの
Semantic Ruleを直接評価可能へ変換していない。これをPhase 6 Frozen Scope上の明示的Deferredとするか、
Phase 6で接続済みと主張するかを再整理し、UIと実装を一致させる必要がある。

## 6. 未確定／追加再現情報待ち

1. Context Sizeは変更操作自体が可能だったが、ユーザーから「バグ多い」と報告された。Exact入力、
   Current値、期待値、実結果を次回取得し、同じRework Scopeへ追加する。
2. Max New Tokensも同様に追加再現情報待ちとする。
3. User通常TerminalでのMetal利用は未確認。Codex Task CycleのCPU Fallback EvidenceをUser Mac全体へ
   一般化しない。

## 7. Current Disposition

```text
Phase 6 Implementation: COMPLETE_CANDIDATE withdrawn by Manual Acceptance
Phase 6 Manual Acceptance: FAIL / ADJUST
Open Major: Judge／Repair Golden Path
DeepSeek Mac Q4 Main Promotion: NOT ACCEPTED
Default Main Model: Qwen retained
Phase 6 Closure: NOT STARTED／NOT AUTHORIZED AS COMPLETE
Phase 7 READY: NOT STARTED
Git Commit／Push: NOT PERFORMED in this correction
Source／Test／Config Mutation: 0 in this correction
```

次回は、利用可能量回復後にExact Reworkを作成し、少なくともJudge Structured Output、Referenceなしの
意味評価、Repair Routing、Judge Current Identity、古いUI説明を差分修正する。Context Size／
Max New Tokensは再現情報を得てからScopeを確定する。今回のFailureをClaudeだけへ帰属させず、Codex側の
設計・Review・完了判定失敗としてCross-provider／Automation Evidenceへ後続Routingする。
