# Phase 6 Current Claude Task — Package R27 Recovery（Strict Manifest Binding／Guard Evidence Provenance）

```yaml
document_id: phase_6_current_claude_task_r27_recovery_20260829105704
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 10:57:04 JST
active_contract: phase_6_claude_current_task_r25_to_r28_exact_rework_handoff_ja_20260829101215.md
resolves: P6-CODEX-090, P6-CODEX-091
package: P6-RR-R27
network_authority: prohibited（本Package含むR25〜R28全体でNetwork Access禁止。R23の既取得値のみ使用）
```

## 対象Finding

P6-CODEX-090（Major）: `is_complete_and_verified`は`verified_official_contract`Booleanと
各Fieldの非None／非空だけを確認し、値そのものを検証していなかった。Controller Probe Cは
`provider_id="wrong.provider"`、`required_fields=("Wrong",)`、`categories=("FakeInput",)`
でも`is_complete_and_verified=True`となることを再現した。

P6-CODEX-091（Evidence Major）: `Qwen3GuardClassification`は`model_id`／Exact Revision／
Artifact SHA-512／Contract Manifest Digest／Schema IDを保持するが、
`Qwen3GuardDetectorAdapter.detect()`がGeneric `GuardDetection`へ変換する際にこれら実
Provider Identityを全て破棄していた。P6-DELTA-004はPARTIALのまま、「未実装項目0」Claimと
矛盾していた。

## 実装

### 1. Exact Contract Cross-field Validation（P6-CODEX-090、`qwen3guard_manifest.py`）

R23の実取得値から`_EXPECTED_*`定数群（Official Repository Identity、Provider ID、
Label Schema ID、Safety／Refusal Label Set、Target別Required Fields、Target別Category Set
9／8件）をModule-levelで固定（本Package含むR25〜R28はNetwork Access禁止のため、新規Fetchでは
なくR23既取得値をそのままLocal定数化）。Pydantic `model_validator(mode="after")`
`_validate_exact_official_contract`を追加し、`verified_official_contract=True`のときのみ
全Fieldを`_EXPECTED_*`と厳密照合（一致しなければConstruction自体がValueError→
Pydantic ValidationErrorとして失敗）。`verified_official_contract=False`（未取得
Placeholder）はCheckを免除——`SelenePromptManifest`の「未検証でもConstructable」という
既存Patternを維持。Category Mapping Keysが9＋8（Jailbreak重複除き16件のUnion）を過不足なく
1回ずつ覆うことも検証。Revision Formatは40桁16進（Immutable Git SHA形式）を正規表現で強制。

実Checked-in Manifest（`config/guardrail/qwen3guard/manifest.json`）はこの新Strict
Validatorをそのまま通過する（データ自体は既に公式正本と一致していたため、Runtime Gate側の
不備のみが問題だった）。

### 2. Adapter Construction時Provider ID一致要求（`qwen3guard_adapter.py`）

`Qwen3GuardGenAdapter.__init__`が`self._manifest.provider_id != model_id`をConstruction時に
Check、不一致なら`Qwen3GuardManifestUnavailable`をRaise。

### 3. `label_schema_id`のManifest投影（`qwen3guard.py`, `qwen3guard_adapter.py`）

`decode_qwen3guard_output()`に`label_schema_id`引数を追加（直接Decoder Callerとの後方互換の
ためDefault値は維持）。Adapter側の2箇所（`decode_qwen3guard_output`呼出しと
`_failure_classification`呼出し3箇所）を`manifest.label_schema_id`から投影するよう修正、
Hardcode literalを削除。

### 4. Guard Evidence Identity（P6-CODEX-091、`results.py`, `qwen3guard_detector_adapter.py`）

`ModelDetectionProvenance`（`model_id`／Exact Revision／Artifact SHA-512／Contract Manifest
Digest／Schema ID）をOptional Typed Provenanceとして新設し、`GuardDetection.model_provenance:
ModelDetectionProvenance | None = None`を追加（既存Generic Detector互換——全て`None`
Default、Digest計算等への影響は Full Suite Regression 0で確認済み）。`Qwen3GuardDetectorAdapter.
detect()`がCLEAR・MATCH両Return Pathで`_provenance_for(classification)`を通じてIdentityを
投影。UNAVAILABLE（Classification自体が存在しない）Pathは`None`のまま——存在しないModel
Callの偽Identityを作らない。

## Round-trip Test（新規、`test_qwen3guard_detector_adapter.py`）

```text
test_model_provenance_round_trips_from_result_to_evidence
  （3 Target × 5 Outcome形状[Safe/Match/Unknown/Timeout/Malformed] = 15 Parametrize Case、
    全てPASS。GuardDetection.model_provenanceがClassification由来の5 Identity Field
    全てと厳密一致することを検証）
test_model_provenance_is_none_when_unavailable_no_classification_exists ... PASS
```

## Cross-field Validator Test（新規、`test_qwen3guard_manifest.py`）

```text
test_construction_rejects_incomplete_or_wrong_exact_contract_when_claimed_verified
  （5 Parametrize Case: 空Input Categories／空Output Categories／空Category Mapping／
    provider_id="wrong.provider"[Probe C literal reproduction]／Wrong Required Fields、
    全てConstruction時ValidationErrorで拒否されることを確認）
test_unverified_manifest_with_wrong_fields_still_constructs_as_placeholder ... PASS
  （verified_official_contract=FalseならStrict Checkを免除し、Placeholder Manifestとして
    構築可能なまま——is_complete_and_verifiedはFalseで正しく不使用に収束）
```

既存Fixture（`_complete_manifest_dict()`／`_write_manifest()`）は`qwen3guard_manifest`の
`_EXPECTED_*`定数を直接参照する形へ更新し、Toy Category Setとの乖離による重複保守リスクを
排除した。

## Focused Evidence

```text
tests/unit/adapters/guardrail_governance/test_qwen3guard_manifest.py ... 17 passed
tests/unit/guardrail_governance/test_qwen3guard_adapter.py ... 21 passed
tests/unit/adapters/guardrail_governance/test_qwen3guard_detector_adapter.py ... 23 passed
tests/unit/adapters/runtime_model_control/test_dedicated_role_adapters.py ... 9 passed
tests/unit/guardrail_governance + tests/unit/adapters/guardrail_governance +
  tests/integration/web ... 349 passed
```

## Canonical Evidence

```text
ruff check . ... All checks passed
ruff format --check . ... 483 files already formatted
mypy（pyproject.toml既定 files=[src,scripts,tests]） ... Success: no issues found in 483 source files
pytest（Full Suite） ... 1811 passed, 7 deselected
```

## P6-RR-ACC-022／P6-DELTA-004再導出（暫定、最終判定はR28）

P6-RR-ACC-022（Manifest実在・検証可能性）: Cross-field Validationにより実Manifest Validation
が偽Contractを拒否できることを実証。P6-DELTA-004（実Provider Identity往復記録）:
`ModelDetectionProvenance`によりClassification→GuardDetection→（将来のGuardrailResult
Evidence）までIdentityが往復することを15 Case Round-trip Testで実証。両IDの最終PASS
DispositionはR28（66 ID正本再集計）でまとめて確定する。

## Open（次Packageへ持ち越し）

```text
P6-CODEX-084相当（66 ID再集計）: R28で対応。
Real Selene/Qwen3Guard Artifact、Real Browser、User Manual Acceptance: 既知Gapのまま変更なし。
```

## Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0（本Package含む本Task全体でNetwork Access禁止。`_EXPECTED_*`定数は
  全てR23の既取得値をLocal定数化したもので、新規Fetch 0）
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Package R28（Acceptance／Canonical Verification／Internal Review、
66 ID正本再集計）へ継続。
