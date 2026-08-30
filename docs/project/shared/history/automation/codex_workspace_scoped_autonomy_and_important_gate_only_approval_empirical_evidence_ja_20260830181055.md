---
document_id: codex_workspace_scoped_autonomy_and_important_gate_only_approval_empirical_evidence_20260830181055
document_type: append_only_provider_empirical_evidence
document_state: recorded
language: ja
recorded_at: 2026-08-30 18:10:55 JST
provider: Codex Desktop
authority_owner: Nazuna Research
classification: observed_behavior_not_complete_platform_specification
---

# Codex Workspace内自走／重要Gate限定承認の実測Evidence

## 1. 背景

本ProjectのCodex Controller TaskはPhase 0相当の初期要件定義段階から継続している。
初期には確認Dialogが頻発したため、UserとCodexは「安全でScope内の通常作業について
逐次確認しない。User判断が必要な重要Gateだけを確認する」という運用境界を作った。

2026-08-30時点で、Codex Desktopの承認方法UIは`承認を求める`が選択されている。
表示説明は、外部File編集やInternet利用について確認を求める趣旨である。Userは過去のDialogで
常に`1回だけ許可`を使用し、`似た操作を常に許可`に相当する永続承認を一度も選んでいない。

それにもかかわらず、現在はWorkspace内の通常作業中に確認Dialogがほとんど表示されず、
重要な境界だけで確認が生じる。この状態により、UserはCodexのLong Run中に別の作業を行える。

## 2. 観測された現在の挙動

```text
Project Workspace内のRead
→ 原則として自走

Userが依頼したScope内の編集
→ 原則として自走

必要最小限の非破壊Test／Inspection
→ 原則として自走

Project外Write／Network／危険な削除／不可逆Action
→ PlatformまたはAgentの確認Gate候補

外部State変更／金銭／Authority拡張／Scopeの重大拡大
→ User判断Gate
```

この実測は、過去の`1回だけ許可`が暗黙の恒久Allowlistへ変換されたことを示さない。
むしろ、次のLayerが重なっていると解釈するのが妥当である。

1. Userが依頼したTask Scope。
2. Workspace／Sandbox等の実行境界。
3. Projectで確立した「安全なScope内作業は止めない」Agent運用規則。
4. 外部・破壊的・高コスト・Scope拡張時のHuman Gate。
5. Agent設定とは独立して残るPlatform Safety Gate。

内部実装の完全なPlatform仕様は公開Evidenceだけでは断定しない。本書は、現在のCodex Desktop、
Project設定、Task運用およびUser実操作を組み合わせた実測である。

## 3. User評価

Userは現在の状態を、作業中に別のことを行え、重要Gateだけ確認すればよいため非常に楽だと評価した。
これは単なる確認回数削減ではなく、Human Attentionを本当に判断が必要な地点へ集中させる効果を持つ。

```text
Approval Fatigue        : 低減
Long Run中のUser拘束    : 低減
重要Gateの可視性        : 維持
Platform最終Safety Gate : 維持
```

## 4. OpenAI公式Guidanceとの整合

OpenAI公式Model Guidanceは、安全なLocal Actionを明示し、Scope内作業を不要に停止せず、
外部Write、破壊的Action、購入またはScopeの重大拡大で確認するCompact Policyを推奨している。

Source:
https://developers.openai.com/api/docs/guides/latest-model

本Projectの実測は、この一般Guidanceと整合する。ただし、当該GuidanceだけからCodex Desktop UIの
全内部仕様、永続承認保存方式または全Safety Gate条件を推定しない。

## 5. Codexの傾向／仕様として保持する要点

- 安全なWorkspace内作業は、毎回の確認なしに連結実行できる。
- `承認を求める`設定は、全Commandを逐次確認する意味ではない。
- `1回だけ許可`の履歴がなくても、最初から許可済みのScope内Actionは自走できる。
- Agent運用規則は不要確認を減らすが、Platform Gateを解除しない。
- 重要Gate限定運用は、Userの時間、集中力およびLong RunのThroughputに実利がある。
- この挙動はProvider Version、Desktop仕様、Sandbox、Workspace設定およびTask Contractで変化し得るため、恒久Hard-codeせず再観測する。

## 6. 運用判断

現行Codex Controller Taskでは、今後も次を維持する。

```text
安全・Scope内・可逆的な通常作業 : 不要確認なしで継続
重要な曖昧性                     : 必要な時だけ確認
外部／破壊的／高コストAction     : User Gate
Platform強制Gate                 : Bypassを前提にしない
```

確認を減らすこと自体を目的にせず、Authority、Scope、RecoveryおよびUser Sovereigntyを維持したまま、
Human Attentionを重要Gateへ限定する。

