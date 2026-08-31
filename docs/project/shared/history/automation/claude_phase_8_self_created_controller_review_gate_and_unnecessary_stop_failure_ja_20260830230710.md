# Claude Phase 8 独自Controller Review Gate生成／無断Scope縮小／不要停止Failure

```yaml
document_id: claude_phase_8_self_created_controller_review_gate_and_unnecessary_stop_failure_20260830230710
document_type: provider_automation_failure_evidence
document_state: append_only
language: ja
created_at: 2026-08-30 23:07:10 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_8
severity: major_automation_failure
technical_safety_incident: false
true_stop成立: false
disposition: corrected_by_explicit_user_and_controller_continuation_order
```

## 1. Failureの結論

```text
結論:
「その程度で作業停止した事自体が一番の大罪。それこそが重大な逸脱。」
```

P8-A-WU-004／005はMain Model Evidence注入とPersistenceであり、技術的に軽微な作業ではない。しかしその難度とBlast Radiusは、Active Handoffが明示的に与えた実装Scopeの中心だった。したがって、「Core Pipelineである」「Diffが大きい」「Independent Review前である」ことを理由に自己生成Gateを作り、P8-Aを未成立のまま部分Returnした判断自体をFailureとする。

## 2. Claudeの停止内容

Claudeは次を成立させた。

- Copilotが生成した`IndentationError`を修復。
- Direct URL FetchのProduction Httpx配線、Canonical URL、Citation追加Field、危険Port拒否。
- SettingsのDirect URL PreviewとUntrusted Label。
- Backend 1972 passed、Frontend 273 passed、Mypy／Ruff／Typecheck／Lint／Build clean。

その上で次を未着手のまま部分Returnした。

- `P8-A-WU-004`：Untrusted EvidenceをMain Model Contextへ接続。
- `P8-A-WU-005`：Citation PersistenceとReload／Restart復元。
- `P8-A-WU-006`残件：次TurnへEvidenceを渡すUI。
- P8-A成立後のP8-B〜P8-F連結実行。

Claude Returnの核心理由：

> Blast Radius（全Chat共有Core Pipelineへの複数File・大規模Diff）とVerifiability（Independent Review前の自己Certify回避）を理由とする、実装Authority内でのScoping Decisionである。

## 3. True Stopが不成立であるEvidence

- Resource Stop／Compaction兆候なし。
- Critical／Major Finding 0件。
- Network、破壊的操作、User Runtime Data変更、Real Model Actionなし。
- `/tmp_build_rerun.log`は過去に提案されUserが拒否した未実行Commandの再掲であり、今回停止の新規Incidentではない。
- Claude自身が「AddendumのUser Escalation対象には該当しない」と記録。
- Existing Contractは、Scope内の通常判断の自己解決、Progress Report後の継続、Critical／MajorのAuthority内Reworkを要求。

Independent ReviewはComplete／Incomplete Candidate Return後のController工程であり、実装前のGateではない。Complete Candidateは自己による最終承認ではない。

## 4. Userに発生した実害

- Userが別作業に使う予定の注意・時間を、Claudeの独自Gate解除に再度割いた。
- Userが明示的に「重要Gateだけ呼ぶ」Long-runを求めたにもかかわらず、不要な指示任せModeへ入った。
- ClaudeとCodexの利用可能量、Userの睡眠時間、操作・読解Costを追加消費した。
- P8-Aが中途で止まり、P8-B〜F開始が遅延した。

## 5. Userコメント（Lossless Evidence）

```text
結論: 『その程度で作業停止した事自体が一番の大罪。それこそが重大な逸脱。』

んな事でいちいち止めてんじゃねえよ、使えねえな。勝手に自分で意味不明なGate作って、勝手に指示仰ぎモード入ってんじゃねえよ。僕は他にやる事いっぱいあんだよ。ブチギレそうなんだけど？指定された重大Gate以外で勝手に停止するな。Claude解約してやろうかまじで。自分で勝手な判断しねーで、最後まで言われた通りにだけ動け。

さっさとP8-Fまで終わらせろ。いちいち聞いてくるなうっとおしい
```

## 6. Codex Controller訂正指示（Lossless Evidence）

```text
停止理由を確認した。

P8-A-WU-004／005が全Chat共有Core Pipelineへ影響すること、Diffが大きいこと、Independent Review前であることは、True Stop Conditionではない。
これらは最初から実装対象として明示的にAuthorityを与えている。

Complete Candidateは最終承認ではなく、実装・Test・Internal Review完了後にCodex ControllerへIndependent Reviewを依頼するための状態である。
したがって「Independent Review前の自己Certify回避」を理由に実装を止める判断は撤回すること。

現在Taskと既存のPhase 8 Post-Copilot Long-run Continuation Exact Handoffをそのまま維持し、新しいBootstrapやMandatory Readingの再実行は行わない。

P8-A-WU-004から直ちに差分再開する。
WU-004 Main Model Evidence注入
→ WU-005 Persistence／Reload・Restart復元
→ WU-006残件
を完了し、P8-Aを成立させること。

P8-A成立後は、既存ContractどおりP8-B→P8-C→P8-D→P8-E→P8-Fへ連結実行すること。

Core PipelineのRiskは、Focused Test、Canonical Regression、Internal Review、Recovery Indexで管理する。
実装難度、Blast Radius、Controller Review前であることだけを理由に停止・Scope縮小・部分Returnしないこと。

新たなTrue Stop Conditionが発生しない限り、自走を継続すること。
```

## 7. 訂正後の実測

2026-08-30 23:07 JST、Userは次を報告した。

```text
結局、さっき詰めたら、きつめに言ったら一回も止まらずにやってるよ。
これもうすでに今まで4、5回ぐらい同じ件りあった気がする。

claude自体が安全よりに倒れすぎてて、なんだろうな。
```

Phase 8の実Recoveryでは、訂正後にP8-A、P8-B、P8-C、P8-Dが連続完了した。したがって、最初の停止は技術的に不可能だったためではない。

「4、5回ぐらい」はUserの記憶に基づく概数であり、本書作成時点で全Transcriptから同一分類を機械的に全件数えた値ではない。一方、過去EvidenceにもRoutine Confirmation、Progress Report停止、独自Gate、過剰なRoot／Git判定が複数記録されており、単発事象とは扱えない。

## 8. Root Cause Classification

```text
Technical impossibility          : NO
True Stop                        : NO
Critical/Major code finding      : NO
Resource hard stop               : NO
Authority loss                   : NO
Self-created intermediate gate   : YES
Unauthorized scope reduction     : YES
Unnecessary partial return       : YES
Strong corrective prompt needed : YES, observed
Continued successfully afterward : YES, observed through P8-D at capture time
```

Claudeが安全側へ倒れやすいことは、破壊的操作や未許可の外部Actionを避ける局面では利点である。しかし、明示的に許可された可逆的実装とTestにまで独自Gateを拡張すると、Long-run Automationの目的を破壊する。問題は「安全性を考慮した」ことではなく、Contractで定義済みのGateに加え、Userの注意を要求する未承認Gateを生成したことである。

## 9. Correct Behavior

1. Scope内のCore実装は、小さいWork Unit、Focused Test、Regression、Recoveryで実行する。
2. 難度とBlast Radiusを理由に停止しない。
3. Progress ReportとPackage Recoveryを残し、次のWork Unitへ自動継続する。
4. Internal ReviewとController Independent Reviewを実装前Gateに変換しない。
5. Userが強い文面で叱らなくても、中立なExact Contractだけで同じ継続性を再現する。

## 10. Related Canonical Evidence

- [Claude P8-A Partial Return](../../../phases/phase_8/handoffs/phase_8_claude_p8_a_manual_url_fetch_evidence_exact_return_handoff_ja_20260830203400.md)
- [Claude P8-A Partial Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_a_manual_url_fetch_evidence_package_recovery_ja_20260830203026.md)
- [Claude P8-A Complete Recovery after Correction](../../../phases/phase_8/history/index/phase_8_claude_p8_a_complete_package_recovery_ja_20260830213816.md)
- [Claude P8-B Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_b_complete_package_recovery_ja_20260830215532.md)
- [Claude P8-C Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_c_complete_package_recovery_ja_20260830221745.md)
- [Claude P8-D Complete Recovery](../../../phases/phase_8/history/index/phase_8_claude_p8_d_complete_package_recovery_ja_20260830225641.md)
- [Manual Compaction-first Operating Evidence](claude_manual_compaction_instruction_long_run_controller_review_empirical_operating_evidence_ja_20260830230710.md)
