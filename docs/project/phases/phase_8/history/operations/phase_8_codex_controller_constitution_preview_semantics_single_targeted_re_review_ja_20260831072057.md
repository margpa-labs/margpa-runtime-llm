# Phase 8 Constitution Preview Semantics — Codex Controller Single Targeted Re-review

```yaml
document_id: phase_8_codex_controller_constitution_preview_semantics_single_targeted_re_review_20260831072057
document_type: controller_independent_review_evidence
document_state: final
language: ja
created_at: 2026-08-31 07:20:57 JST
review_owner_provider: Codex
review_owner_role: プロジェクト責任者兼設計統括者役
review_scope: P8-CODEX-012_only
review_cycles: 1
two_cycle_default_exception: user_explicit_single_targeted_review_for_this_micro_rework
```

## 1. 結論

P8-RW7の限定差分を1回のTargeted Reviewで確認した。

```yaml
P8-CODEX-012: RESOLVED
P8-ACC-021: PASS
new_critical: 0
new_major: 0
new_mvp_blocker: 0
user_manual_candidate: true
phase_8_closure_claimed: false
```

今回のUser明示判断により、観点変更型二段階Reviewは例外的に縮退し、別のFull Review Cycleは開始しない。

## 2. Input Evidence

- Exact Rework Handoff:
  `docs/project/phases/phase_8/handoffs/phase_8_claude_constitution_preview_semantics_micro_rework_exact_handoff_ja_20260831065824.md`
- Claude Exact Return:
  `docs/project/phases/phase_8/handoffs/phase_8_claude_constitution_preview_semantics_micro_rework_exact_return_handoff_ja_20260831071113.md`
- Return SHA-512:
  `c4eeaddb9337e5249c4b84a4d36e695274a2ca575e92a1aa5d4f60c958411701e182a2bc8a11f5d963cda9fe0f673fb32c654a239bca630fcae773e717de871a`
- Recovery Index:
  `docs/project/phases/phase_8/history/index/phase_8_claude_constitution_preview_semantics_micro_rework_recovery_ja_20260831071113.md`

DigestはUser／Claude報告値と実Fileで一致した。

## 3. Targeted Review

### 3.1 Backend Contract／Pure Resolver

`ConstitutionModePreviewEntry`へ次の3軸が追加されている。

```text
evaluation_disposition
action_permission
violation_presentation
```

OFF／OBSERVE／ENFORCEの固定意味論はExact Handoff §4と一致する。

```text
OFF
  not_evaluated
  no_constitution_action
  not_evaluated

OBSERVE
  evaluate_record_only
  no_block_no_authority_change
  observation_only | typed_unsupported

ENFORCE
  evaluate_and_apply_supported_action
  supported_actions_only_no_authority_expansion
  enforced | typed_unsupported
```

Current Production Previewは`supported_rule_ids`を渡さないため、実Manifest上の未対応Ruleを`observed`または`enforced`へ
虚偽昇格させず、`typed_unsupported`へ収束する。適用Ruleが存在しないViewは`not_evaluated`となる。

### 3.2 REST Projection

`ConstitutionModePreviewEntryResponse`と`project_mode_previews()`は3軸を欠落なく
`GET /api/v2/constitution/preview`へ投影する。既存のRule別Decision／Reason、Revision、Digest、Viewおよび
`active_production_mode`も保持される。

### 3.3 Frontend Presentation

`ConstitutionPanel.tsx`は各View／Modeについて次の4行を表示する。

```text
Decision
Evaluation
Action Permission
Violation Presentation
```

日本語／英語Labelが存在し、Production Active ModeがOFFであることと、PreviewがRuntime Activation、External Action、
Tool AuthorityまたはModel Injectionを起こさないことを示すDisclaimerも維持されている。

### 3.4 Negative／Truthfulness

- OFFは`allow all`ではなく、Constitution由来Actionなし／未評価として表示される。
- OBSERVEはBlockまたはAuthority変更を許可しない。
- ENFORCEは対応済みActionだけを対象とし、Authorityを拡張しない。
- Current未対応Ruleを「観測済み」「Enforce済み」と虚偽表示しない。
- Preview計算はProduction Active Modeを変更しない。

P8-CODEX-012の原因だった「Decision Outcomeだけを列挙し、Action Permission／Violation Presentationを比較できない」状態は解消した。

## 4. Controller Verification

Codex環境で次を再実行した。

```text
Backend focused:
  39 passed

Mypy targeted:
  Success: no issues found in 2 source files

Frontend focused:
  7 passed

Frontend typecheck:
  PASS

Frontend targeted lint:
  PASS
```

Claudeが既に報告したFull Suite／Build Evidenceは、今回のMicro Rework範囲に対して再度Full実行せず保持した。

## 5. Acceptance／Finding Disposition

```yaml
P8-CODEX-012:
  before: open_major_P0_closure_blocker
  after: resolved_controller_targeted_review_pass

P8-ACC-021:
  before: PARTIAL
  after: PASS
  basis:
    - three_axis_backend_contract
    - lossless_REST_projection
    - bilingual_UI_presentation
    - no_false_supported_or_enforced_claim
    - production_active_mode_remains_OFF
```

P8-CODEX-009／010／011およびP8-ACC-038は本Reviewの対象外であり、既存のNon-blocking／PARTIAL／FAIL分類を維持する。

## 6. Exact Next Action

```text
Phase 8 User Manual Acceptanceへ進む。
P8-CODEX-012を理由とする追加Reworkまたは追加Full Review Cycleは開始しない。
User Manual結果を受領するまでPhase 8 ClosureはClaimしない。
```
