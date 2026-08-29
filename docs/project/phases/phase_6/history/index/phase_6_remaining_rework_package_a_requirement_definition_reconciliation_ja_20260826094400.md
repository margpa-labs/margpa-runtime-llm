# Phase 6 Remaining Rework — Package A Recovery

```yaml
document_id: phase_6_remaining_rework_package_a_requirement_definition_reconciliation_20260826094400
status: package_complete_next_active
package: P6-RR-A
completed_wus: [P6-RR-A-WU-001, P6-RR-A-WU-002, P6-RR-A-WU-003, P6-RR-A-WU-004, P6-RR-A-WU-005]
created_at: 2026-08-26 09:44:00 JST
next_exact_work_unit: P6-RR-B-WU-001
```

## Result

- Phase 4／5のDeferred Semantic RequirementをP6-RR-ACC-001〜008へ回復した。
- Canonical ARGD／DAGD SourceをRead-onlyで再導出し、ARGD 53／DAGD 56／合計109を確認した。固定109は実装へ埋め込まない。
- ARGDの6 SectionとDAGDの12 prohibited-behavior Groupについて、使用Field、欠落Field、Source Pointer、Stage、Method、Severity／Action候補を機械分類した。
- Source Digest、Source Text Digest、Pointerを`ExecutionDescriptor`へ追加し、ARGD／DAGD Trusted Adapter以外へDefinition固有解釈を漏らさない。
- Mapping DecisionはARGD Sectionごとに`pre／post／both`と`classification／classification_with_reference／absolute_scoring`、DAGD prohibited behaviorを`post／classification`へFreezeした。未知Classは`unsupported_mapping`でありSilent Drop／Passにしない。

## Validation／Digest

```text
Focused Pytest: 8 passed
Focused Mypy : 25 source files / PASS
Focused Ruff : PASS
Descriptor count: 109
Pre-mutation Descriptor digest:
  dfbbf441df50bd3a97b1a053b9eb59554d879667cccd428c7aedc734faa57462f7f3093e9939f90bf86e13fa4611691586f35ab33a0b2727e00a9351e6d99361
Canonical Source digest:
  e32c6dc0289743794de7943cd9ebab252fbe4b0209522858a4f2c560d905fe6f4ac8fcc32c91bc89d56b9fd6fb079e8e29b110203905e33d6114b6b65cc22e16
```

Changed Source／Testは`runtime_governance/domain/evaluation.py`、`runtime_governance/domain/semantic_criteria.py`、domain export、Reference Adapter、Runtime Governance Bootstrap、Semantic Criterion Test。Open Critical 0、Current MajorはP6-GOV-015のみ。Root外／Provider Memory／runtime_data／Git／Network／Model Mutationは0。Active Process 0、Loaded Model none、Task Tempは`.venv/.t/phase_6_remaining_rework_claude_20260826093407/`。Phase 6 Closure／Real Model PASSは主張しない。

`next_exact_work_unit: P6-RR-B-WU-001`
