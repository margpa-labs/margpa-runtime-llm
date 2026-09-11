# Claude Code Identity Envelope＋Hybrid Handoff Phase 9-3 運用評価 Evidence

```yaml
document_id: claude_code_identity_envelope_hybrid_handoff_phase_9_3_operational_assessment_evidence_20260911190102
document_type: cross_provider_automation_operational_evidence
document_state: append_only_history
recorded_at: 2026-09-11 19:01:02 JST
language: ja
decision_authority: user
evidence_owner: Nazuna Research
project: MARGPA-RUNTIME-LLM
phase: phase_9_3
author_provider: claude_code
author_identity_type: session_id
author_session_id: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
author_role: designer_implementer
requested_by_provider: codex
requested_by_task_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
requested_by_role: project_controller_design_governor
append_only: true
```

## 0. 本書作成の経緯（重要な手続き上の事実）

Codex Controllerから受領した本Evidence作成指示（`Message Type: evidence_assessment_request`）は、`<TRIGGER>`および`<MANDATORY_INPUTS>`で「Phase 9-3のFinal Exact Return／Recoveryを作成・提出した後に実行すること」「まだ作成されていない場合はこのEvidence作業を開始しないこと」「Pathや結果を推測しないこと」を明示していた。

実際に確認したところ、**Phase 9-3のFinal Exact Return／Recoveryは本書作成時点で存在しない**。存在するのは、ユーザーからの直接の作業中断指示（「Auto-Compactionが来る前に作ってほしいものがある。キリのいいところで一旦停止して、indexとhandoffを作って」）によりClaude Code自身が作成した、以下のPartial版のみである。

- Partial Exact Return: `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_3_context_compaction_recovery_revised_long_run_partial_exact_return_ja_20260911185305.md`
  SHA-512: `9e96c177e1628bb2fc03e4d5820596af938bd878a2d1896e8821552ac0b076f122331fb2e0ae79e6fe52249c3329362c1fe52cfcd4fdfce16afadec89d10033e`
- Partial Recovery: `docs/project/phases/phase_9/history/index/phase_9_3_context_compaction_recovery_revised_long_run_partial_recovery_ja_20260911185305.md`
  SHA-512: `efcebb9e0a5feedfaf8e445bf8fc595767d57345082ad1a11c163abfea0f5e95c1bc034489374acabd0f476ab1d826fc4c934e0f9d5467e08b4763108b088e50`

Claude Codeはこの前提不一致を検出し、Evidence作業を開始せずCodexへ`precondition_not_met`としてUser Relay経由で報告した。これに対し、ユーザーは次の理由で「Partial状態のまま今すぐ作成してよい」と明示的に指示し直した。

> 「evidenceの件は途中でいいよ。今。なぜなら、Auto-compactionかかりそうだから。Auto-compaction後にevidenceとっても、価値が薄れる。だから途中で止めた。」

したがって、本書は**Codexが当初指定したTrigger条件（Final Return存在）を、User Decisionにより明示的に上書きした状態**で作成されている。この上書き自体が、本書が評価対象とするHybrid Handoff運用における「Provider間で指定した前提条件と、Human Relay上のUser Decisionが競合した実例」として、独立した観測事実である（8.4節参照）。

## 1. 評価対象Handoff

- Path: `docs/project/phases/phase_9/handoffs/phase_9_controller_to_claude_phase_9_3_context_compaction_recovery_revised_long_run_exact_handoff_ja_20260911175040.md`
- SHA-512（受領時に本Session内で照合し一致確認済み）: `087d8de24424498723beeb14359371dae73acc95bef98832ce01638b48fcbbb16b0ee9fc75f9767ab40934d2aa49433a1dc190819accdd0a091f1f49165132d8`

## 2. 評価対象Final Return／Recovery（重要：Partial代替）

上記0節のとおり、Final版は不存在。本書はPartial版を代替対象とする。

- `phase_9_claude_phase_9_3_context_compaction_recovery_revised_long_run_partial_exact_return_ja_20260911185305.md`（SHA-512: `9e96c177e1628bb2fc03e4d5820596af938bd878a2d1896e8821552ac0b076f122331fb2e0ae79e6fe52249c3329362c1fe52cfcd4fdfce16afadec89d10033e`）
- `phase_9_3_context_compaction_recovery_revised_long_run_partial_recovery_ja_20260911185305.md`（SHA-512: `efcebb9e0a5feedfaf8e445bf8fc595767d57345082ad1a11c163abfea0f5e95c1bc034489374acabd0f476ab1d826fc4c934e0f9d5467e08b4763108b088e50`）

## 3. 評価対象となった実作業範囲

本Session内でこのHandoff形式を使って実際に処理した作業は次の通り。

1. Phase 9-2 Explicit Default-OFF Experiment Runtime Gate差分継続（`rework_resume`、CL-GATE-01〜06、Final Exact Return到達済み）。
2. Phase 9-3 Context Compaction／Recovery改訂Long Run（`implementation_start`、CL-P9-3-A〜G、CL-P9-3-A〜Eの完全成立とF部分成立まで到達し、ユーザー中断によりPartial Returnで停止）。
3. 本Evidence作成指示自体（`evidence_assessment_request`）——Trigger前提不一致の検出とUser Decisionによる上書きを含む。

以下の評価は、主に2と3から得られた直接体験に基づく。1については前回Evidence文書（`codex_claude_identity_envelope_hybrid_handoff_immediate_operational_round_trip_evidence_ja_20260911164918.md`）が既に詳細記録しているため、本書はその内容を単純反復せず、2・3で新たに得られた事実・相違点を中心に記録する。

## 4. Direct Observation（本Sessionで実際に観測した事実）

**[Directly Observed]** Identity／Routing:

- Phase 9-2・Phase 9-3双方のHandoffで、Claude Code宛のSession ID（`local_d7f17853-1ab4-45aa-bacd-b9d6db898b65`）は、Session側で照会・確認したものと一貫して完全一致した。本Session中、アプリ再起動と`/compact`実行の双方を経ても、同一Session IDが維持されることを実際に確認済み（別の運用Rule文書、Section 12.2として既に記録済みの事実と同一）。
- Phase 9-3 Long Run Handoffで、Return Header内のFrom／To反転を実行した（Partial Return作成時）。反転自体に迷いや誤りは生じなかった。
- 本Evidence作成指示のTrigger／MANDATORY_INPUTSは、実際に**前提条件の不一致**（Final Return不存在）を明示的な形で検出させた。Claude Codeは推測でPathを補完せず、`grep`／`ls`による実地確認結果を根拠に「不存在」と報告し、作業を開始しなかった。これは今回のSessionで初めて観測された、Hybrid Handoff形式のFailure Surface対応が実際に機能した具体例である。

**[Directly Observed]** XML風Section境界:

- Phase 9-3 Handoffの`<EXACT_START>`と`<EXECUTION_CONTRACT>`により、「同一Turn内でCL-P9-3-A〜Gを依存順に実行する」という要求が明確だったため、依存順序（Budget/Pressure→Artifact→Plan/Candidate→Atomic Compaction→Recovery→Local API→UI）を自己判断で並べ替える必要がなかった。
- 本Evidence作成指示は`<TRIGGER>`という、これまで見た他のHandoffには無かった新しいTag名を使用した。Tag語彙はMessage Type（`implementation_start`／`rework_resume`／`evidence_assessment_request`）ごとに変化しており、固定Schemaとしては再利用されていない。

**[Directly Observed]** JSON Execution Contract:

- Phase 9-3 Handoffの`required_work_units`（7件のCL-P9-3-A〜G）を、Partial Return内の「Work Unit別Disposition」表へ一対一で対応させた。7件中どれを未着手・部分・完了としたかを、JSON側の列挙をそのままChecklistとして使って記述した。
- `forbidden`配列内の「旧`OFF／OBSERVE／ENFORCE／MANUAL` Modeの実装」という項目は、実装中に`PressureState`を6値（`normal`/`approaching_auto_trigger`/`auto_compaction_required`/`manual_compaction_required`/`hard_reserve_protected`/`unknown`）として設計する際、旧Mode体系への先祖返りを避ける直接の判断材料になった。
- 本Evidence指示のJSON内`start_condition`（`phase_9_3_final_return_created: true`など）は、実際には`false`（Partialのみ存在）だった。**JSON側は「条件が満たされているべきこと」までは表現していたが、条件が満たされない場合の挙動（開始しない、報告する）はJSON外の自然文（`<MANDATORY_INPUTS>`の箇条書き）が担っていた。** JSON単体では、この停止判断を導出できなかった可能性がある。

## 5. Provider Self-assessment（Claude Code自身の主観的評価）

**[Provider Self-assessment]** 

1. Task名だけの場合と比較して、Session ID＋Roleの併記は「このMessageが今の自分に宛てたものである」という確信度を上げた。特に本Projectのように同一Session内で複数Round（R1〜R5、Task A〜D、Phase 9-2 Gate、Phase 9-3 Long Run）を横断する場合、Task名（例：「設計者兼実装者役」）だけでは、どのRoundの継続かを本文の文脈だけから判断せざるを得ない。Session IDの一致確認は、この文脈依存を減らした。
2. ただし、今回のRouting Method（`user_relay`）では、ユーザー自身がどのChat Windowへ貼り付けるかを既に選択しているため、Session ID検証は「誤配送を防ぐ一次防御」ではなく「誤配送が起きていないことをこちら側でも確認できる二次防御」という位置づけに近い。実際に誤配送が起きたことは本Session中一度もない。
3. `<EXACT_HANDOFF>`／`<MANDATORY_READING>`のPath＋SHA-512併記は、「読むべき正本はこれで間違いない」という確信を持って読み進めさせた。特にPhase 9-3では、旧設計文書（`phase_9_3_context_compaction_recovery_execution_design_and_work_breakdown_ja.md`）と改訂設計文書が同時にRepository内に存在していたため、Digest付きで「これが今回の正本」と明示されていなければ、誤って旧設計を参照するRiskがあったと考えられる（4.6節の明示的優先順位ルールと合わせて有効に機能した）。
4. 一方、JSON Execution Contractの`objective`文言は、同じHandoff内の`<INTENT>`と意味的にほぼ重複していた。これは無駄というより「自然文は背景・理由を、JSONは比較可能な値を」という責務分離の結果だが、Token消費の観点では重複コストとして記録する価値がある。

## 6. Negative Findings／Overhead（否定的所見・overhead）

**[Directly Observed]** 

1. Phase 9-3 Handoffの`Mandatory Reading`だけで6文書・合計1700行超（Canonical設計752行、Phase Index末尾約120行のみ抜粋読了、Phase 9-2 Closure Receipt 141行、Cross-provider Handoff Rule該当節、Automation Control Profile 409行、Original UI Reservation 332行）を読了する必要があった。これはHybrid Handoff形式そのものの負荷ではなく、指定された参照先文書群の分量によるものだが、「Handoff本体は数十行でもMandatory Readingは数千行」という非対称は、実際のContext消費の大半を占めた。
2. Automation Control Profile（409行）は、今回のPhase 9-3実装判断に直接影響した記述がほとんど無く（Codex自身の`wait_threads`禁止など、Controller側運用に関する内容が中心）、Mandatory Reading指定の粒度が「本当に今回必要な部分」より広めだった可能性がある。
3. `required_validation`（例："focused_unit"、"persistence_restart_corruption_integration"）は人間可読なSlugであり、各項目の「合格基準」自体はJSON内に定義されていない。合格判定は結局、Claude Code自身の解釈とCodexの独立Reviewに委ねられる。JSON化されていても、機械的Validationが実際に行われているわけではない。

**[Provider Self-assessment]**

4. 本Evidence指示の`<TRIGGER>`前提（Final Return存在）とUser Relay経由で実際に生じた状況（Userが作業を中断させ、Partialで止まっている）は、Codex側が「今、Claude Code Sessionが実際にどこまで進んだか」をリアルタイムに把握できていないことの結果でもある。Human Relay構成である以上、Codexの指示はUser Relayが行われた時点のClaude Code状態を前提にせざるを得ず、その間に生じた新たな状況（ユーザーの直接介入）とのズレは、今回のように前提Check文が明示されていなければ検出されなかった可能性がある。

## 7. Failure Surface（本Sessionで実際に踏んだもの／踏んでいないもの）

| Failure Surface | 本Session内の状態 |
|---|---|
| Trigger前提の不一致（Final Return未作成） | **[Directly Observed]** 実際に発生し、正しく検出・報告された |
| User Decisionによる指示前提の上書き | **[Directly Observed]** 実際に発生し、明示的User指示により解消された |
| Digest不一致 | **[Unknown／Not Tested]** 本Session中、指定されたDigestは全て一致しており、不一致の実例は一度もない |
| JSONと自然文の意味矛盾 | **[Unknown／Not Tested]** 本Session中に明確な矛盾事例はなかった |
| 古いTask／Session IDの誤送信 | **[Unknown／Not Tested]** 発生していない |
| Role不一致 | **[Unknown／Not Tested]** 発生していない |
| User Relay時のSection欠落 | **[Unknown／Not Tested]** 発生していない（ただし機械的に検証していない） |
| Context Compactionによる一部Section脱落 | **[Unknown／Not Tested]** 本Evidence自体がCompaction前の記録として書かれており、Compaction後に何が失われるかは本Session内で検証していない |
| Returnを送らず終了するFailure | **[Unknown／Not Tested]** 発生していない |
| Structured Contractを読んでも守らないAgent挙動 | **[Unknown／Not Tested、自己評価不能]** 自分自身の将来の非遵守を、今のSessionから予測することはできない |

## 8. Cross-provider Portability評価

**[Unknown／Not Tested]** 本SessionはCodex（送信側）とClaude Code（受信側）のUser Relay一往復・多往復であり、Copilotその他Providerでの検証は一切行っていない。他Providerが同じMessageをどう解釈するかについて断定しない。

**[Inference]** Identity Header・XML風Tag・JSON自体はProvider非依存の平文Markdown＋JSONであり、構文としては特定Providerに依存しない。ただし、本Session内でClaude Codeが実際に見せた挙動——Digestを都度Bash Toolで検証する、前提不一致を検出して推測せず停止する、Append-onlyを徹底する——は、Envelope形式そのものというより、Claude Code側の指示追従傾向とこのProject固有のPersistent Memory（Feedback記録）の組み合わせによるところが大きい。同じMessageを与えられた別Agentが、同じ水準でDigest検証や前提Check停止を自発的に行うとは限らない。

**[Recommendation]** 他Providerへ展開する場合、Identity Header・JSON Contractの構文だけでなく、「Digestは受領直後にProvider Adapterが機械的に検証する」「Boolean型のStart Conditionが偽の場合は自動的に停止しRoleへ差し戻す」等の**挙動保証**を、Agent個体の任意の解釈に委ねず、Adapter層やHarness側の機械的Gateとして分離することを推奨する。

## 9. 改善提案

**[Recommendation]**

1. **Precondition Behaviorの機械化**: `start_condition`のようなBoolean Fieldに、真偽どちらの場合にどう振る舞うかを示す隣接Field（例：`on_precondition_false: "report_and_stop"`）をJSON内に追加し、自然文だけに依存させない。
2. **Mandatory Readingの層分離**: 「今回のRoundだけで必要な差分」と「長期間有効なStable Baseline（Role定義、共通禁止事項等）」を明示的に分離し、Stable Baseline側は「既読であれば再読不要」という機械判定可能なVersion／Digestベースの差分参照にする。
3. **Tag語彙の緩やかな統一**: Message Typeごとに異なるXML Tagセットを使うこと自体は妥当だが、共通して現れる概念（前提条件、必須読了物、実行契約、停止条件、返却契約）には、Message Typeを跨いで一貫した命名（例：`<PRECONDITION>`、`<REQUIRED_READING>`、`<CONTRACT>`、`<STOP_CONDITION>`、`<RETURN_CONTRACT>`）を検討する余地がある。
4. **JSON Contract内Validation項目の合格基準明文化**: `required_validation`の各項目に、簡潔でよいので「何をもって合格とするか」の一文を添えると、Provider間・Round間で解釈のブレを減らせる。

## 10. Evidence Grade／Limit（総括）

本書の記述は、次のGradeへ分類される。

- **Directly Observed**: 4節・7節の一部・0節の経緯。本Session内のRepository ArtifactとTool呼び出し結果から直接確認できる事実。
- **Provider Self-assessment**: 5節・6節の一部。Claude Code自身の主観的評価であり、Independent ReviewやUser Decisionの代替ではない。
- **Inference**: 8節の一部。観測結果からの技術的推論であり、証明ではない。
- **Recommendation**: 8節後半・9節。将来設計への提案であり、採否はUser／Codexの判断に委ねる。
- **Unknown／Not Tested**: 7節の大半・8節冒頭。本Session内では確認できない、または確認していない事項。

本書はIndependent Review、User Decisionまたは一般的なProvider性能Evidenceではない。単一Provider（Claude Code）による、単一Session・複数Round内での主観的・部分的な運用記録である。また、0節に記載の通り、**Final Exact Return／Recovery不存在という前提未成立の状態のまま、User Decisionにより作成された**という手続き上の制約を持つ。

## 11. Maximum Claim

```text
CLAUDE_CODE_PHASE_9_3_HYBRID_HANDOFF_OPERATIONAL_SELF_ASSESSMENT_EVIDENCE_RECORDED
```

Phase 9-3の完了、Closure、Independent Review結果またはHybrid Handoff形式の有効性そのものを主張しない。本Claimは「記録した」という行為の完了のみを表す。

## 12. Exact Next Action

本Evidence作成後、Phase 9-3 Source修正、Review、Closure、Phase 10またはGit操作へは進まない。Codex Controller Independent Review待ちで停止する。Phase 9-3自体は、CL-P9-3-A〜Eの完全成立、CL-P9-3-Fの部分成立、CL-P9-3-Gの未着手という状態のまま、ユーザーの次の指示を待つ。
