# Phase 3-D Complete／Recovery Entry

```yaml
document_id: phase_3_d_complete_recovery
status: current_recovery_entry
phase: phase_3
subphase: phase_3_d
work_unit: p3_d_wu_004_complete
role: Claude側設計統括者役
provider: claude_code
authority_revision: accepted_1
completion_line: phase_3_g_wu_004_complete_candidate
long_running_mode_active: true
created_at: 2026-08-21 20:00:00 JST
predecessor: phase_3_c_complete_recovery_ja_20260821191500
```

Lightweight Recovery Entry（Companion第4.1節）。Phase 3-D全体（WU-001〜004）を1件に統合。

## Current State

```text
Accepted Predecessor : Phase 3-C（完了）
Current WU            : Phase 3-D 完了（WU-001〜004）
Next WU                : P3-E-WU-001（Compiler Contract／Unbound Plan）
```

## Phase 3-D Summary（Trusted Adapter Registry／Normalized Governance IR）

```text
P3-D-WU-001 Trusted Adapter Registry              : ACCEPTED_LOCAL
P3-D-WU-002 Combined ARGD／DAGD Adapter            : ACCEPTED_LOCAL
P3-D-WU-003 CDOGD／Domain Extension Adapter         : ACCEPTED_LOCAL
P3-D-WU-004 Full Corpus IR Conformance             : ACCEPTED_LOCAL
```

**重要な設計判断（Local Judgment、要引き継ぎ）**：Normalized IRを**構造的Passthrough**として実装した。各Definition Sourceの Top-level Section（`description`／`domain_scope`／`activation`／`orchestration_reference`等、Definitionあたり最大20 Section）を、Key名・直下Child Key名・値種別として保持する`IrSection`にMapし、Rule／Evaluator／Action等への**深い意味的型付けは行っていない**。

理由：(1) 18 Definition全件の意味内容を本Sessionで精読し尽くすことは非現実的、(2) P3-IR-005「欠落Rule、Priority、Authority、Action Semanticsを推測補完しない」に照らすと、精読なしでの深いSemantic Mappingは不正確なAuthority／Rule解釈を生むRiskがあり、むしろ構造保持＋明示Warningの方が誠実、(3) P3-IR-006は変換LossをWarning／Errorとして保持することを求めており、本実装は`normalization_warnings`へ「structural passthrough only」を明記することでこれを満たす。

**Deferred Evidence（未完了・将来課題として明示）**：各Definitionの`rules`／`evaluators`／`actions`／`state_model`／`evidence_requirements`をArchitecture§5.4が定める個別Typed Fieldへ精密Mappingする作業は、本Phase 3-Dでは実施していない。Phase 4でARGD／DAGDを実際にBindingする際、この深いMappingが必要になる可能性が高く、その時点で本Session（またはCodex）が対応する前提とする。Compiler（Phase 3-E）は、この構造的IRからRule/Evaluator Referenceを選択する際、Section単位の粗い粒度で扱う。

3 Adapter Class（Combined ARGD/DAGD、CDOGD、Common Domain Extension）は共通のStructural Normalizerを共有しつつ、独立したAdapter ID／Classとして登録——将来一部だけ深いSemantic Parsingへ発展させる際に他へ影響しない設計（ADR-3-005の意図と整合）。

Acceptance：Manifest StringからImport 0、Unknown Adapter safe unsupported、Version／Identity／Source Digest保持、Routing/Activation実行0、17 Source／18 Definition全件正常Normalize（実File・実Manifestで検証）、SPPGD→DAAGD→SDAGD→SDMRGDの`orchestration_reference` Section保持確認、IR Digest決定論、Raw CoT Marker非含有——すべてTestで確認済み。

## Exact Mutation（Phase 3-D）

```text
Created:
  src/margpa_runtime_llm/modules/governance_definitions/domain/normalized_ir.py
  src/margpa_runtime_llm/modules/governance_definitions/adapter_registry.py
  src/margpa_runtime_llm/adapters/governance_definitions/reference_bundle_adapters.py
  tests/unit/governance_definitions/test_adapter_registry.py
  tests/integration/governance_definitions/test_full_corpus_ir_conformance.py
  docs/project/phases/phase_3/history/index/phase_3_d_complete_recovery_ja_20260821200000.md（本File）
Modified:
  src/margpa_runtime_llm/modules/governance_definitions/domain/__init__.py（累積Export追加）
Deleted: NONE
Git Mutation: 0　Root外Action: 0　User実Data接触: 0
```

## Tests Run／Results

```text
tests/unit/governance_definitions/ + tests/integration/governance_definitions/ : 45 passed
Full Suite                                                                       : 794 passed／3 deselected
                                                                                    （Baseline 697 + 97 new、Regression 0）
Ruff／Mypy（Repo全体）                                                            : PASS — 150 source files
```

## Open Findings

- Mypy bare（tests/全体）既存11件Error（Phase 2由来、継続Deferred）。
- 上記「構造的Passthrough」設計の深化（Rule/Evaluator/Action個別Typed化）は未着手、Phase 4以前の後続課題として本File第1段落に明記。

## Next Exact Route

P3-E-WU-001（Compiler Contract／Unbound Plan）へ進む。
