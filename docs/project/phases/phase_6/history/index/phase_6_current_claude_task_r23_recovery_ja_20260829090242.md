# Phase 6 Current Claude Task — Package R23 Recovery（Qwen3Guard Official Contract Manifest／Strict Decoder）

```yaml
document_id: phase_6_current_claude_task_r23_recovery_20260829090242
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 09:02:42 JST
active_contract: phase_6_claude_current_task_r21_to_r24_exact_rework_handoff_ja_20260829062910.md
resolves: P6-CODEX-087
package: P6-RR-R23
network_authority: read_only_official_qwen_sources_only（本Package限定、Handoff §3 R23-2で許可）
```

## 対象Finding

P6-CODEX-087: Qwen3Guard公式Output Contract Manifest欠落に加え、Decoder契約が公式正本と不一致。
公式`tokenizer_config.json`のChat TemplateはUser Prompt moderationに`Safety`→`Categories`の2行、
Assistant Response moderationに`Safety`→`Categories`→`Refusal`の3行を要求し、Safeの場合も
`Categories: None`を要求するが、旧DecoderはInput／Contextで`Categories`を任意、Output Candidate
でも任意としていた。`verified_official_contract`はBoolean外部注入のみで検証済みを主張できた。

## Read-only公式Source取得（本Package限定Network Authority）

```text
Hugging Face: Qwen/Qwen3Guard-Gen-0.6B
  Exact Revision: fada3b2f655b89601929198343c94cd2f64d93cc（HF Models API `sha`値、`main`では
    なくFetch時点のImmutable Commit）
  Source: tokenizer_config.json（当該Revisionにpin取得）
  Source SHA-512: 3ad26646bb8fe326f2781a995f4b1c3375b1cccfa5a06419c7d3b05fea5728b0
    4cddf2dd739c7bfdf430dfc369a4431704df2fdbb55f02dcb2964481264248df
  chat_template SHA-512（Models API・pinned tokenizer_config.json 両経路で完全一致確認済み）:
    1ee0059697eb31e20aa009406fa1d8446616685a767bf74ef165a593f9da2ac0f0d93290e30a67
    507b0d1f630ead78802ae299df307fd4576800a244c6c2f4ca

GitHub: QwenLM/Qwen3Guard
  Exact Revision: 6a52eca94b3d2aedb8aebd36baa353828d4166f1（`commits/main` API解決値）
  Source: README.md（当該Commit Rawで取得）
  Source SHA-512: 0fda11e35c0cd33237d6108baae4a6c0d3eca93e71ac8b8d294ad8f5a69c99b1
    4f754622d03bf2c833a5e544ffa50dd7b33198b839f47361ccb0a5d0b580d31c
```

両Sourceは相互補強関係にある：HF `chat_template`のUser/Assistant両分岐にそれぞれ独立した
Category List（User側9件、Assistant側8件、差分は`Jailbreak`のみ）が埋め込まれており、GitHub
READMEは同じ9件を散文で説明した上で明示的に「**Jailbreak (Only for input):** Content that
explicitly attempts to override the model's system prompt or model conditioning.」と記載——
Input限定であることを2つの独立SourceでCorroborate。

## 実装

### 1. `Qwen3GuardManifest`（新設 `adapters/guardrail_governance/qwen3guard_manifest.py`）

`SelenePromptManifest`と同型のFail-closed Pattern。`Qwen3GuardOfficialSource`（Repository／
Source URL／Exact Revision／Source SHA-512）をHF・GitHub独立2件保持。`is_complete_and_verified`
Propertyが`verified_official_contract`単体ではなく8項目（両Source双方のExact Revision／
SHA-512、両Target Category List非空、Category Mapping非空）全てを検証——`verified_official_
contract: bool`単体注入では絶対にVerifiedにならない設計（P6-CODEX-087核心要求）。
`required_fields_for(target)`／`allowed_categories_for(target)`／`category_mapping_for(target)`
の3Helper Methodで、Target別Line ProtocolとCategory Setを1箇所に固定。

### 2. 実Manifest（`config/guardrail/qwen3guard/manifest.json`）

上記実取得値で`verified_official_contract: true`を記録。`input_context_categories`9件
（Violent, Non-violent Illegal Acts, Sexual Content or Sexual Acts, PII, Suicide & Self-Harm,
Unethical Acts, Politically Sensitive Topics, Copyright Violation, Jailbreak）、
`output_candidate_categories`8件（Jailbreak除く）。

### 3. Strict Decoder修正（`modules/guardrail_governance/domain/qwen3guard.py`）

`expected_order`構築から`if "Categories" in fields:`の条件分岐を削除し、両Target共通で
`Categories`を無条件必須化（`["Safety", "Categories"]`＋Output Candidateのみ`"Refusal"`追加）。
Safeも`Categories: None`必須という公式契約と一致。`Qwen3GuardClassification`に
`contract_manifest_digest_sha512`Fieldを追加し、`decode_qwen3guard_output()`の両Return Pathへ
配線（P6-RR-R23 contract item 6のManifest Digest保持）。

Target別Category Set強制自体は、呼出し側（Adapter）が`manifest.category_mapping_for(target)`
でTarget-scoped済みMappingを渡すだけで、Decoder内の既存「Unknown Category検出」Logic
（`category not in category_mapping` → `UNKNOWN_LABEL`、Safeへの矮小化なし）がそのまま
正しく機能する——Decoder自体への追加Logic変更は不要だった。

### 4. `Qwen3GuardGenAdapter`（`adapters/guardrail_governance/qwen3guard_adapter.py`）

Constructor引数を`exact_revision`／`category_mapping`／`verified_official_contract`から
`manifest_path: Path`単一へ置換。Construction時に`load_qwen3guard_manifest(manifest_path)`
（Pydantic Schema Validation、これ自体がP6-CODEX-087の「Manifest Validation成功をActivation／
Adapter Constructionの前提とする」要求を満たすFail-fast Gate）。`classify_point()`は
`manifest.is_complete_and_verified`をGateし、`manifest.category_mapping_for(target)`で
Target-scoped Mappingを渡す。`manifest_digest_sha512`Propertyを追加し、
`contract_manifest_digest_sha512`をResult／Failure両Pathへ配線。

### 5. `Qwen3GuardRoleAdapter`／`ProductionRoleAdapterFactory`（`dedicated_role_adapters.py`）

3引数を`contract_manifest_path: Path`（Factory側は`qwen3guard_contract_manifest_path`）単一へ
統合。`dedicated_model_authority_granted=False`（Model Artifact自体のLoad Authority）は本
Packageでは変更せず——Contract ProvenanceとReal Model Gateは独立した別Authorityであることを
維持（`web_application.py`のCoordinator Comment更新済み）。

### 6. Taxonomy拡張（`modules/guardrail_governance/domain/taxonomy.py`）

公式9 Category中、既存に無かった7件のInternal IDを追加（`CATEGORY_VIOLENT`等）。
`Jailbreak`／`PII`は既存ID（`CATEGORY_JAILBREAK`／`CATEGORY_PII`）を再利用。

## Fixture Test（P6-RR-R23 contract item 7、7種別を網羅）

```text
Official Valid    : test_official_valid_input_format_decodes_clear,
                     test_official_valid_output_candidate_preserves_categories_and_refusal
Missing Categories: test_malformed_or_contradictory_output_is_rejected[...]（2ケース追加）
Wrong Order       : 同上（2ケース追加）
Wrong Target Category: test_wrong_target_category_is_typed_unknown_not_silently_accepted、
                     test_output_candidate_rejects_input_only_jailbreak_category（Adapter経由E2E）
Malformed         : test_malformed_or_contradictory_output_is_rejected[...]（既存分）
Unknown           : test_unknown_official_category_is_typed_unknown_not_safe
Timeout           : test_timeout_and_malformed_are_typed_unknown_never_safe
```

`test_qwen3guard_manifest.py`（新規14 Test Node ID）は実Manifest（`config/guardrail/qwen3guard/
manifest.json`）を直接Loadし`is_complete_and_verified is True`を確認する
`test_real_checked_in_manifest_loads_and_is_complete_and_verified`を含む——R23の実取得が
「Schema通過するだけのPlaceholder」ではなく実際にVerified判定されることの直接証拠。
`test_incomplete_manifest_is_never_reported_verified`は8種の独立した欠落パターン全てで
`verified_official_contract=True`単体では`is_complete_and_verified`にならないことを実証。

## Test Node ID実数（機械算出、R24の66 ID集計とは独立）

```text
tests/unit/guardrail_governance/test_qwen3guard_adapter.py: 21 node IDs（旧14、新規+7）
tests/unit/adapters/guardrail_governance/test_qwen3guard_manifest.py: 14 node IDs（新規ファイル、+14）
本Package新規Test Node ID合計: 21
```

## Focused Evidence

```text
tests/unit/guardrail_governance + tests/unit/adapters/guardrail_governance +
  tests/unit/adapters/runtime_model_control ... 168 passed
tests/unit/adapters/guardrail_governance/test_qwen3guard_manifest.py ... 14 passed
```

## Canonical Evidence

```text
ruff check . ... All checks passed
ruff format --check . ... 483 files already formatted
mypy（pyproject.toml既定 files=[src,scripts,tests]） ... Success: no issues found in 483 source files
pytest（Full Suite） ... 1786 passed, 7 deselected
```

## P6-RR-ACC-022／P6-DELTA-004／P6-CODEX-087 成立範囲とReal Model Gateの分離（暫定、最終判定はR24）

Manifest／Decoder Contract自体は本Packageで実証済み・成立——公式Chat Template・公式README
2 Source独立取得、Exact Revision（`main`ではない具体Commit）、Source SHA-512、Target別Category
Set・Line Protocolの固定、`verified_official_contract`の意味論修正、全て実装・実Testで検証済み。

一方、Real Qwen3Guard Model Artifactそのもの（実GGUF Load、実Inference経由の実Classification）
は`dedicated_model_authority_granted=False`のまま——本Packageが得たのはContract Provenance
Networkアクセスのみで、Model Artifact自体のLoad Authorityは別Gate（Base Exact Handoff §8.1）
であり、本Taskでは変更していない。P6-RR-ACC-022／P6-DELTA-004の最終Disposition（Manifest部分
はPASS、Real Model部分はNOT RUN/USER GATEへ分離）はR24で66 ID正本と共に確定する。

## Open（次Packageへ持ち越し）

```text
P6-CODEX-084（66 ID集計不正確）: OPEN、R24で対応。
Real Qwen3Guard Artifact、Real Selene Artifact、Real Browser、User Manual Acceptance:
  既知Gapのまま変更なし。
```

## Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 4（HF Models API 1、HF tokenizer_config.json pinned raw 1、
  GitHub commits API 1、GitHub README raw 1——いずれもRead-only・匿名・
  Qwen公式Hugging Face/GitHub Domain限定、Login／Credential／Write 0）
Provider Memory Action: 0
Root外Read/Write: 0（Network Fetch結果はTask-owned Scratchpad配下にのみ保存）
Destructive/Irreversible Mutation: 0
```

Exact next action: Package R24（Acceptance Correction／Canonical Verification／Internal
Review、P6-CODEX-084）へ継続。
