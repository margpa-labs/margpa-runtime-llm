# Phase 11以降予約 — GovernanceとRuntime Constitutionの構造制御／意味評価分離

```yaml
document_id: phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_20260904172003
document_type: planned_work_architecture_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-09-04 17:20:03 JST
decision_authority: user
authority_owner: Nazuna Research
target_phase: phase_11_or_later
phase_10_plan_changed: false
implementation_authority: not_granted_for_this_reservation
append_only: true
```

## 1. 今回の決定

Main Runtime Governance（ARGD／DAGD等）と、Project直下の`constitution/`の両方について、**それぞれの内部を構造レイヤーと意味評価レイヤーに分離する**。両Componentを一つに統合するという意味ではない。

目的は、Judgeの起動・成功を、GovernanceやConstitutionによる直接制御すべての前提にしないこと。まずMVPを優先し、分離の設計・実装はPhase 11以降とする。Phase 10の既定作業を変更・拡大せず、本予約を現在の完了条件へ追加しない。

## 2. 二つのレイヤー

| レイヤー | 担当すること | Judgeとの関係 |
|---|---|---|
| 構造レイヤー | 「Judge関係なしに直接モデルを矯正させる」。入力構築、生成・出力の制約、実行許可など、Runtime側で適用・強制できる規則を扱う | Judgeなし／OFF／故障時も独立して使える |
| 意味評価レイヤー | 内容が規則に沿っているかを意味評価し、その結果から必要なRepairを呼び出す。修復結果を再評価して採用・不採用を決める | 交換可能な評価器を接続する。失敗時は意味評価の不成立を明示する |

構造レイヤーを「Ruleが登録・Bindされているかの確認」だけに縮退させない。実際にどの入力・出力・Actionを制約したかまで設計・検証する。ただし、Promptへ規則を書くだけで完全な遵守を保証したとは扱わない。Model Weightの変更・再学習を決定したものでもない。

意味理解が必要な規則を、便宜的なPattern判定へ置き換えて「構造制御済み」としない。構造制御できる部分と意味評価が必要な部分を、同一条文の中でも区別する。全規則を構造化できるという前提は置かない。

## 3. 疎結合の境界

- ConstitutionとGD群は独立Componentのままにし、互いを必須の親Component・Selectorにしない。
- 両方の構造レイヤーが、Judge Providerや意味評価の可用性だけを理由に一括停止しない。
- 意味評価は共通の結果形式とRepair接続口を介して連携し、個別Model名やGD名をCoreへ固定しない。
- 構造制御だけの稼働と、意味評価・Repairまで含む稼働をUI／Evidenceで区別する。前者を全規則のENFORCE成立と表示しない。
- Mode、評価対象、結果の出所、競合解決、Repair回数・予算・停止条件は、着手時に設計する。今回数値や実装方式は決めない。

## 4. 読み取った現状と留保

[2026-09-02のGovernance予約](phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_ja_20260902214032.md)には、構造処理・意味評価・統合Gateの3層と、当時のARGD／DAGD 109件がすべて意味評価へ委譲されるとの調査結果がある。これは当時の実装・Criterion表現についての記録であり、元のGDの意図に構造制御可能な部分が一切ないという証明ではない。今回109件の再分類・再検算はしていない。

同文書§2・§9の「Resource Gateは正常／実装に欠陥なし」という説明は、後の[SSS Incident記録](../ai_system_anomalies/claude_code/claude_code_sss_resource_gate_foundation_destruction_and_resource_exhaustion_incident_ja_20260903001814.md)と整合しない。当時の発言として原文を保持するが、今回の技術的根拠には採用しない。

現在の[Runtime Constitution Manifest](../../../../../constitution/manifest.json)は3規則。各Rule本文は既存Harness等による制御とConstitution自身の評価・実行を区別し、後者の未対応を記している。Manifestや条文があることだけで、二レイヤーの実行が成立済みとはしない。

[既存のConstitution／GD疎結合予約](runtime_constitution_normal_chat_agent_tool_loose_coupling_and_hardcode_avoidance_reservation_ja_20260829114640.md)を維持し、本予約はJudgeへの依存をレイヤー単位で分離する条件を追加する。`shared/constitution/`とPortable Packageの編纂・他者評価の予約は変更しない。

## 5. 着手時の確認

1. GDとRuntime Constitutionの規則を、直接制御可能な部分／意味評価が必要な部分へ分類する。
2. 各構造制御について、Judgeなしで実際に矯正・阻止できる範囲を試験で示す。
3. 意味評価→Repair→再評価を接続し、失敗・未評価と成功を混同しない。
4. Judge OFF／故障、Constitution OFF、GD不在・交換の条件でも、残るComponentの独立性を確認する。
5. 工程と工数は分類結果を踏まえて決める。旧記録の「1〜3 Phase」は当時の見積りであり、確約ではない。

## 6. 今回の小UI Findingとの区別

Main GovernanceがOFFの時、JudgeをENFORCEにしても、一度Main GovernanceのOBSERVEを押すまでENFORCEを選べないという報告は、`UF-UI-017`として[未解決Registry](../../unresolved_work/current_unresolved_findings_registry_ja.md)へ記録した。表示更新の小修正候補であり、本予約のレイヤー再設計とは別に次のReworkで扱う。現行のJudge必須条件そのものを解除する修正ではない。
