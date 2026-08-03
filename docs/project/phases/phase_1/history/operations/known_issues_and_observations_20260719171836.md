# Known Issues／Observations Register

- 文書ID: `known_issues_and_observations`
- 状態: `current`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 作成担当: 設計者役担当Task
- 対象: Project横断の既知問題、非Blocking Observation、Technical Debt
- 正本言語: 日本語
- Phase 1-E Review: [designer_review_phase_1e_final_20260719164641.md](../handoffs/designer_review_phase_1e_final_20260719164641.md)
- supersedes: なし（新規Operations系列）

## 1. 目的

本書は、Phase受入を妨げないが、将来の設計、実装、UI、運用、診断品質で参照すべき既知事項を失わないためのCurrent Registerである。

各項目は、Severity、影響、再現条件、現在のDisposition、再評価条件を分離して記録する。

本書に記載されたことだけを理由に、実装者役へSource修正権限が発生するものではない。

## 2. 状態分類

```text
open_blocking       : 現在のPhaseまたはReleaseを止める
open_required       : 必須Follow-upが必要
accepted_deferred   : 影響を理解して後続Phaseへ延期
monitor             : 条件発生時に再評価
resolved            : 後継文書で解決Evidenceを記録
not_reproducible    : 再現不能。再発時に再開
```

## 3. Current Items

### MARGPA-OBS-0001: Mixed-source Presentation Config Error Attribution

```yaml
id: MARGPA-OBS-0001
state: accepted_deferred
severity: low
category: configuration_diagnostics
introduced_or_found_in: phase_1e_review
security_boundary_impact: none_observed
runtime_behavior_impact: none_for_valid_configuration
required_follow_up: false
```

#### Summary

Thinking Presentation Policyの複数Fieldへ異なるSourceから値が入った状態で、Environment由来のFieldが不正、別Fieldに正常なExplicit Overrideが存在すると、Error Codeが不正値のSourceではなく「いずれかのExplicit Overrideがあるか」に引っ張られる。

#### Reproduction

```text
MARGPA_THINKING_VISIBILITY = sometimes
explicit_display_label     = 明示推論
```

現在の結果：

```text
invalid_request
```

より精密な診断候補：

```text
invalid_configuration
offending_field  = visibility
offending_source = environment
```

#### Cause

`resolve_thinking_presentation_policy`は全Fieldの最終Validationを一括で行い、Error Code選択時に、実際に失敗したField／Sourceではなく、`explicit_visibility`または`explicit_display_label`が存在するかを確認している。

#### Impact

- 不正値は安全に拒否される
- Raw Config値、Absolute Path、SecretはSafe Errorへ露出しない
- 正常値のPrecedenceとSource Trackingには影響しない
- Thinking表示、Hidden No-flash、Persistence、Raw Model Portには影響しない
- UIやSupport時に、原因がCLI入力なのかEnvironment設定なのかを示す精度が低下する可能性がある

#### Disposition

Phase 1-EのAcceptance Criteriaには抵触せず、Source修正を必須としない。Phase 1-Eは`Complete／Accepted`のままとする。

次のいずれかで再評価する。

- Phase 2の設定UI／Config Validation設計時
- Field別Validation ErrorをUIへ表示する時
- Config Source Diff／Effective Config診断を強化する時
- External Release前にError Taxonomyを整理する時
- 同じ分類方式による実害または類似Findingが発生した時

改善候補は、FieldごとにValidationとSource Attributionを保持し、実際に失敗したFieldのSourceからError Codeを決定することである。

## 4. Phase／Backupへの影響

`MARGPA-OBS-0001`はAccepted Deferred Observationであり、Phase 1完了またはBackupを単独ではBlockしない。

Manifest／Phase Final Reviewでは、Known Observationとして本書を参照する。

## 5. 更新規則

新しいIssue／Observation、状態変更、Resolution Evidenceを追加する場合、既存Fileを編集せず、新Timestampの後継Registerを作成する。

