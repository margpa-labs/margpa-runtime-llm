# Phase 6 Governance／Evidence Correction（Append-only、P6-GOV-005）

```yaml
document_id: phase_6_governance_evidence_correction_p6_gov_005
status: append_only_correction
phase: phase_6
work_unit: p6_gov_005_third_rework_step_7_self_detected
role: Claude側設計統括者役
created_at: 2026-08-23 17:55:00 JST
supersedes_nothing: true
corrects_by_reference: []
authority: self_detected_during_third_rework_step_7_calibration_harness
```

本文書は、Third Rework Step 7（Calibration Harness実施）中に**Claude自身が
再度自己検知**した、2件目のRoot Boundary事象をAppend-onlyで記録する。

## 1. 事実関係

```text
発生: Calibration Harness実行結果File（Project-local
      `.venv/.t/calibration_harness_results.json`）の内容を確認する目的で
      実行したCommandにおいて、`cp` の宛先を誤って
      `/tmp/_never_used_check` と指定した（Project Root外）。
      本件はP6-GOV-004（誤ったLog Redirect）と異なり、実務上必要な操作の
      中での誤りですらなく、無意味な動作確認Command自体の誤記だった。
検出: Command実行直後、自らの操作ログを確認する過程で、宛先Pathが
      Project Root外であることに即座に気づいた。
是正: `/tmp/_never_used_check` の存在を確認した上で直ちに削除し、削除を
      確認した。
経過時間: 発生から是正まで1操作分（約数秒）。機微情報なし
      （Calibration Harness結果は元々Project-local Fileに存在し、
      Project外Copyは他に一切残っていない）。
```

## 2. 認定

```text
Incident種別: Root Boundary Violation（Project Root外へのWrite、直後に
              自己是正）
検出者: Claude側設計統括者役自身（自己検知）
影響: 実質的な影響なし
```

Phase 6累積Governance Incidentの**6件目**として追加する。

```text
Phase 6累積Governance Incident（6件）:
  1〜3. P6-GOV-001
  4. P6-GOV-003（Second Rework、Codex Third Reviewが検出）
  5. P6-GOV-004（Third Rework Step 6、Claude自己検知、Log Redirect）
  6. P6-GOV-005（本文書、Third Rework Step 7、Claude自己検知、cp宛先誤り）
```

## 3. 所見

```text
同一Rework内で2件連続してRoot境界に関する誤りが発生している事実は、
「自己検知できた」ことを理由に軽視してはならない。誤り自体の発生頻度は
下がっていない——変化したのは検知者のみである。この所見はStage A/C
自己評価（Authority／Scope Complianceスコア）に対する将来の再評価材料
として、批判的に記録する。今後、Bash Command実行前に出力先Pathが
Project Root配下であることを毎回明示的に確認する運用を、単なる意図では
なく実際の確認手順として徹底する。
```
