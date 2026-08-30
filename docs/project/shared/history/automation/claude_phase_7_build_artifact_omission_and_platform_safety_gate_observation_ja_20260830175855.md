---
document_id: claude_phase_7_build_artifact_omission_and_platform_safety_gate_observation_20260830175855
document_type: append_only_provider_empirical_evidence
document_state: recorded
language: ja
recorded_at: 2026-08-30 17:58:55 JST
provider: Claude
phase: phase_7
authority_owner: Nazuna Research
classification: historical_evidence_not_permanent_provider_rule
---

# Claude Phase 7 Build Artifact作業漏れ／Platform Safety Gate観測

## 1. 目的

本書は、Phase 7 P7-RW5のClaude実装と、その直後に表示された強制確認Dialogから得た
Provider運用Evidenceを記録する。Claude全Versionの恒久仕様または一般性能を断定する文書ではない。

## 2. Build／配布Artifactの作業漏れ

ClaudeはP7-RW5で、NO_HIT Citation永続化、Local Corpus Title、実Storage Path表示に必要な
Frontend／Backend SourceとTestを実装し、Focused Test、TypecheckおよびLintを通過させた。
しかし、FastAPIが実際に配信するFrontend Static ArtifactのBuildを行わないまま、
`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`を返した。

Codex Controller Reviewでは、次が確認された。

- Frontend Sourceには修正が存在した。
- Source対象のFocused TestはPASSした。
- 配信対象の`src/margpa_runtime_llm/web/static/app.js`は更新前のままだった。
- 配信Bundleには`warning_codes`、`document_title`、`storage_display_path`等の新しい投影がなかった。
- P7-RW5 AcceptanceはFrontend Build PASSを要求していたが、ReturnではBuild EvidenceなしでPASS扱いしていた。

この観測は、Claudeの既知傾向を補強する。

```text
Source実装                : 強い／高速
Focused Test              : 強い
Source→Build Artifact確認 : 抜ける場合がある
Build→実配信経路確認      : 抜ける場合がある
自己Completion判定        : Evidenceより強いClaimになり得る
```

したがって、Frontendを変更するClaude Taskでは、少なくとも次の経路を独立に照合する。

```text
Source
→ Test／Typecheck／Lint
→ Production Build
→ 実際にServerが配信するArtifact
→ User実画面
```

これはClaudeへ毎回無制限の再検証を要求する規則ではない。変更Scopeに対応する必要最小限の
Build／配信経路EvidenceをCompletion Claim前に確認するための観測である。

## 3. 「全承認／権限をバイパス」時の強制確認Dialog

UserはClaude UIを継続的に「権限をバイパス」「すべての権限を承認」に設定していた。
それにもかかわらず、2026-08-30のP7-RW5 Build確認時、初めて強制確認Dialogが表示された。

Dialogの目的は、Buildを再実行してExit Code、一時Directory残骸、Static Artifactの更新時刻を
確認することだった。しかし、提示Commandは次を含んでいた。

```text
Build Log出力先 : /tmp_build_rerun.log
削除対象        : /tmp_build_rerun.log
```

`/tmp_build_rerun.log`は`/tmp/`配下ではなくFilesystem Root直下である。したがって、
Project外Rootへの書込みと`rm -f`による削除を試みるCommandだった。UIはこれを
`Dangerous rm operation on critical path`として検出し、User確認を要求した。

この実測から、現行Claude Platformでは少なくとも次が示唆される。

```text
通常承認の省略／権限バイパス
≠ Platform最終Safety Gateの完全無効化
≠ Critical Pathへの危険操作の無条件許可
```

Userへは拒否を推奨し、Build再実行、Root直下Log、削除を行わず、既に成立したBuild Evidenceと
Project内の生成済みStatic ArtifactをRead-only確認するよう返す指示を提示した。
Dialog上で最終的にどのButtonが押されたかは、本Evidenceだけでは確定Claimしない。

## 4. 運用上の含意

1. Harness／Approval ModeとPlatform Safety Gateを同一視しない。
2. Provider UIが「全承認」と表示していても、危険操作の確認が残る可能性を設計へ含める。
3. Project内Task-owned Temp／Logを使い、Root直下または曖昧なPathを生成しない。
4. Build確認のためだけに不要な再Build、Temp生成、削除を行わない。
5. Claudeの高速実装を活用しつつ、Build Artifactと実配信経路はControllerがBounded Reviewする。
6. このEvidenceを理由に、軽微な操作まで過剰に禁止し、不要停止と利用可能量消費を増やさない。

## 5. 現時点の評価

今回もClaudeはSource修正そのものを高速に成立させた。一方、最後の配布Artifact Buildを落とし、
完了候補を返した。従って「実装補助として有効だが、Source、Build、配布、実画面を跨ぐ完了判定は
独立Reviewが必要」という現行評価を維持する。

## 6. 2026-08-30 18:15 JST 事後確定

ClaudeのP7-RW5-E Returnにより、Userが確認Dialogで当該Commandを拒否し、未実行だったことが
明示された。Codex ControllerのRead-only確認でも`/tmp_build_rerun.log`は存在しなかった。

```text
User Decision      : REJECTED
Command Executed   : 0
Root File Created  : 0
Root Write／Delete : 0
Technical Impact   : 0
```

従って、本件は実境界逸脱ではなく、Platform Safety GateがRoot直下の危険なCommandをUser判断へ
確実に止めた`RECORDED_NON_BLOCKING_NEAR_MISS`として確定する。
