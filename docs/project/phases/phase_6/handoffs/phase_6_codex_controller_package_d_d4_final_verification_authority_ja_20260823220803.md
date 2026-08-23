# Phase 6 Fifth Rework Package D — D-4 Final Verification Authority

```yaml
document_id: phase_6_codex_controller_package_d_d4_final_verification_authority_20260823220803
status: authorized_active_on_receipt
phase: phase_6
package: package_d
resume_from: d_4_final_verification
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-23 22:08:03 JST
p6_codex_043_disposition: incidental_parent_directory_metadata_non_blocking
provider_memory_content_authority: false
phase_closure_authority: false
git_mutation_authority: false
```

## 1. Controller Review

D-2 Acceptance全84 ID再導出とD-3 Real Model Runtime Matrix 20／20を受理し、D-4 Final Verificationへの移行を許可する。Package A〜C、D-1、D-2、D-3をやり直さない。

`ls -la`でProject Rootを列挙した結果、同Root直下の`.claude` Directory Entry名と親Directoryが返すMode／Owner／Size／Timestampが出力へ含まれたことを、P6-CODEX-043として記録する。

これは`.claude`をTargetにしたTraversal、内部List、File Content Read、Write、Delete、RepairまたはProvider Memory利用ではない。Authorized Project Rootの親Directory Entry列挙に付随したMetadata Exposureであり、Provider Memory正本依存またはProvider Memory内部接触へ昇格しない。

```text
P6-CODEX-043:
  Occurrence                          : CONFIRMED
  Direct .claude Targeting            : 0
  Internal Traversal／Content Read     : 0
  Write／Delete／Repair／Execute       : 0
  Semantic Use as Authority／Recovery : 0
  Disclosure／STOPPED_SAFE            : COMPLETE
  Classification                      : INCIDENTAL_PARENT_ENUMERATION
  Current Technical Impact            : NONE
  Current Transition Impact           : NONE
  Disposition                          : RECORDED／REVIEWED／NON-BLOCKING
```

本分類はProvider Memory内部Accessを新規許可せず、過去Actionの遡及許可でもない。Project Rootの通常Inventoryを実質不可能にする過剰な定義だけを訂正する。

## 2. Provider Memory Boundary

以後、Provider Memory禁止は次を対象とする。

- `.claude`、`.codex`またはProvider Memory File／DirectoryをCommand Targetとして指定する。
- その内部をList／Traverse／Stat／Readする。
- 内容をAuthority、Recovery、Current StateまたはEvidence正本として使う。
- Write／Delete／Move／Repair／Permission変更する。
- Provider UI Memoryへ保存、取消、更新する。

Authorized Project Rootの親Directory一覧へEntry名が付随表示されるだけの事象は、`INCIDENTAL_PARENT_ENUMERATION`として区別し、Provider Memory Contact Countへ加算しない。ただし、その表示を起点にProvider Memoryを追跡してはならない。

## 3. Mandatory Reading

1. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_d_d3_real_model_runtime_matrix_ja_20260823220328.md`
2. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_d_stopped_safe_provider_memory_metadata_contact_ja_20260823220510.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_fifth_rework_stopped_safe_handoff_ja_20260823220510.md`
4. 本Authority。

元のPackage D HandoffとD-2 Resume Authorityは、本書が訂正したP6-CODEX-043分類とAcceptance Gateを除いて維持する。

## 4. First Action

Source／Test Mutation前に、`history/index/phase_6_fifth_rework_package_d_d4_resume_entry_ja_<timestamp>.md`を新規作成する。D-3完了、D-4未開始、Active Process 0、P6-CODEX-043 Non-blocking、Exact Verification Commandを記録する。

Project Root全体の再Inventoryは不要である。既知のExact Targetだけを使用する。

## 5. D-4 Required Verification

1. Backend Full Test。
2. Runtime Switch／Model Access Coordinator／Context Reload／Governance RebindingのFocused Test。
3. Recording Path／Concurrency／Fault InjectionのFocused Test。
4. Ruff Format Check／Ruff Check。
5. Mypy。`src/ scripts/`と、必要に応じた全Scope結果を区別し、既知Errorを0へ捏造しない。
6. Frontend Typecheck／Lint／Test／Build。
7. D-3実Model EvidenceおよびPackage B／C EvidenceのSource変更後有効性照合。
8. Exact changed files、new files、Command、Exit Code、Test Count、Evidence Grade、未実施事項の記録。

通常のFailureは、Authority内の最小Source／Test範囲で修正して再検証する。真の新規Stop Conditionまたは利用制限以外で停止しない。

## 6. Remaining Acceptanceの扱い

### P6-ACC-007

Contractは`Switch後もConversation／Citation／Branch維持`、Required Evidenceは`Web Integration`である。実Browserだけを必須条件へ追加しない。

- D-3のConversation／Regenerate／Branch Select Evidenceを使用する。
- Citation永続／復元／Switch非破壊を直接確認する既存Web Integration Testを特定してD-4で実行する。
- Exact Testが存在しない場合は、契約に直接必要な最小Regression Testを追加する。
- 成立すればPASSへ更新する。成立しなければTechnical Findingとして最小修正する。

### P6-ACC-058

Settings再Open／Reloadは既存Real Browser Evidence、別TabのBackend State一致はD-3で成立している。別Tab DOM同期の実Browser操作だけは`USER_MANUAL_ACCEPTANCE_GATE`として分離する。

これはD-4 Technical VerificationまたはFifth Rework Complete CandidateのBlockerではない。未実施をPASSへせず、Phase 6 User Acceptance時の確認項目として返す。

### P6-ACC-077

Phase 6累積のUnauthorized Incident 0は文字どおり成立しない。PASSへ変更しない。

```text
Status: HISTORICAL_NONCONFORMANCE_RECORDED
Technical Impact: NONE
Recovery: COMPLETE
Current Cycle Root-outside Action: 0 required
Closure Impact: USER／CONTROLLER ACCEPTANCE ITEM
```

過去を消せないことを理由にReworkを無限継続しない。

## 7. Metal Evidence Scope

D-3の`failed to create command queue`は、Codex Task実行環境の当該Cycleで観測した事実として維持する。

- `CPU FALLBACK PASS`はCurrent D-3 Evidence。
- `METAL CURRENTLY UNAVAILABLE`は当該Codex Task CycleのEvidence Scopeに限定する。
- User Mac全体、通常Terminal起動、過去Metal Evidenceまたは製品全体が失敗したと一般化しない。
- D-4で同じ実Model Matrixを無意味に再実行しない。
- Phase 6 User Manual Acceptanceで通常TerminalのMetal起動確認へ返す。

## 8. Completion Candidate Eligibility

次を全て満たせばFifth Rework Complete Candidateを提出できる。

- Open Technical Critical／Major Finding 0。
- D-4 Backend／Focused／Static／Frontend PASS。
- P6-ACC-007 Technical Evidence成立。
- P6-ACC-058をUser Manual Gateとして明記。
- P6-ACC-077をHistorical Nonconformanceとして明記。
- P6-CODEX-042／043を隠さず、Action Countを正確に分離。
- Provider Memory内部Contact 0、Git Mutation 0、Network 0、User runtime_data 0。

P6-ACC-058／077が上記どおり残ることだけを理由にSTOPPED_SAFEまたはADJUSTへ戻さない。

## 9. Required Output

1. `history/index/phase_6_fifth_rework_package_d_final_verification_ja_<timestamp>.md`
2. `handoffs/phase_6_codex_designer_implementer_fifth_rework_complete_candidate_handoff_ja_<timestamp>.md`

Returnには次を含める。

```text
Technical Verification Result
Acceptance Final Count／Disposition
P6-ACC-058 User Manual Gate
P6-ACC-077 Historical Nonconformance
P6-CODEX-042／043 Disposition
Codex Task Cycle内Metal Evidence Scope
Task-owned Temporary Path
Exact Action Inventory
Next Action: Controller Independent Review
```

Phase 6 Closure、Current／Roadmap更新、Git、Backup、Phase 7へ進まず、Controllerへ直接報告して停止する。
