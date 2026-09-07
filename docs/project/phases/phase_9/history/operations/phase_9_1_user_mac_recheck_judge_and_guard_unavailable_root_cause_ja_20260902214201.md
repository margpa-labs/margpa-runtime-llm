# Phase 9-1 User Mac Manual Recheck — Judge／Guard不可用の原因(単独まとめ)

```yaml
document_id: phase_9_1_user_mac_recheck_judge_and_guard_unavailable_root_cause_20260902214201
document_type: root_cause_note
language: ja
recorded_at: 2026-09-02 21:42:01 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
recorder_role: Claude（設計者兼実装者役）
source_mutation: none
git_action: none
```

## 0. 位置づけ

Userが実機Mac Manual Recheckを実施した際、Judge(Selene)・Guard(Qwen3Guard)が両方とも起動できなかった件を、[Governance ENFORCEの設計齟齬](../../../../shared/history/planned_work/phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_ja_20260902214032.md)とは切り離し、単独の原因説明として記録する。

## 1. 結論(一言)

**Main Modelは一度も壊れていない。** Judge・Guardは「壊れた」のではなく、Package 2で新設したResource Gateが、このMacの実メモリ不足を検出して**正しく安全に拒否した**。これは未報告の新規Bugではなく、[OF-P2-003](../../handoffs/phase_9_claude_package_2_open_finding_of_p2_003_and_of_p2_001_resolution_exact_return_addendum_ja_20260902190930.md)(Selene)・OF-P2-006(Gemma)・OF-P2-007(Qwen3Guard)として、この同じ日の少し前にBackend実機Evidence付きで既に開示・報告済みの挙動が、今回Userの実機で実際に発生したものである。

## 2. 実測(稼働中のこのMacへ直接照会)

```text
curl -s http://127.0.0.1:8000/api/v6/provider-selection

main : configured=active=main.qwen3-4b-q4-k-m, state=active（Main無傷）
judge: configured=judge.selene-1-mini-llama-3.1-8b-q5-k-m
  active=null, state=unavailable
  failure_reason="resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role"
guard: configured=guard.qwen3guard-gen-0.6b-q8-0
  active=null, state=unavailable
  failure_reason="resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role"

実available memory(psutil、実測): 3.54 GB(全16GBのうち)
```

## 3. なぜ拒否されたか(Gateの計算式、実際の数字)

`SystemMemoryRoleResourceGate`(`memory_resource_gate.py`)は、Main Active時に限り、次の式で拒否判定する。

```text
required = 候補Artifact size_bytes + Main Artifact size_bytes + margin(3GiB)
拒否条件: required > 実available memory
```

このMacの構成(Main=Qwen3-4B)での実際の数字:

```text
Selene(Judge) required = 5.73GB(Selene) + 2.50GB(Main) + 3.00GB(margin) = 11.23GB
  → 実available 3.54GB を大幅に超過 → 拒否

Qwen3Guard(Guard) required = 0.75GB(Guard) + 2.50GB(Main) + 3.00GB(margin) = 6.25GB
  → 実available 3.54GB を超過 → 拒否
```

Guard(0.75GB)のように小さいModelでも、marginを含めた合計がこのMacの実available memory(3.54GB、ブラウザ・開発Tool等が並行稼働している現実的な状態)を上回れば同様に拒否される。

## 4. なぜこの挙動自体は「新しいBug」ではないか

2026-09-02、Package 2残作業(OF-P2-003)の中で、Main+Selene同時Load時の実Incident(2026-09-01、Server再起動が必要になったIncident)を防止するために、このGateを意図的に新設した。当時から次を実機Evidence付きで確認・報告済みである。

```text
OF-P2-003: Main+Selene → このMacの実条件下でGate拒否されることを確認済み
OF-P2-006: Main+Gemma(既定Judge) → 同様に拒否されうることを確認済み
OF-P2-007: Main(DeepSeek8B)+Qwen3Guard → 同様に拒否されうることを確認済み
```

今回Userの実機で発生したのは、上記のうちOF-P2-003(Selene)とOF-P2-007相当(Qwen3Guard、ただしMainがQwen3-4Bの組み合わせでも拒否されるケース)が、**Docs上の実測値としてではなく、実際にUser自身のManual Recheckの最中に起きた**、という点が新しい。挙動自体・原因自体は既に特定・開示済みだった。

## 5. 現在の対応方針(Userの既存決定、変更なし)

[3-Gate終了判定Index §6.1](phase_9_1_package_2_residual_work_three_gate_closure_index_ja_20260902201032.md)で記録済みのとおり、margin等のGate設計は「少なくとも現時点(2026-09-02)では変更せず現状維持」。理由はMVP優先・Platform=Model交換可能という思想上の判断であり、恒久的な最終決定ではない。

今回の実機Recheckは、この「現状維持」判断の**実際の影響範囲**(Judge・Guard双方が、開発機の現実的なメモリ条件下では高確率で拒否される)を、初めて実地で確認した、という位置づけになる。

## 6. Status

```text
Current Point            : User実機でJudge(Selene)・Guard(Qwen3Guard)が両方とも
                            Resource Gateにより拒否された事象を、既存OF-P2-003／
                            006／007の実機Evidenceと同一原因として単独に記録した。
Files Created／Modified   : 本Fileのみ(新規作成)。
Validation                : §2の実測(稼働中Serverへの直接照会)。
Open Current Blocker      : NONE(Main無傷、Gateは設計どおり動作)。
Controller-owned Next Work: margin再設計の要否判断(現状維持中、Phase 11以降視野)。
Exact Next Route          : User Mac Manual Recheckの残り項目(可能な範囲)を継続。
```
