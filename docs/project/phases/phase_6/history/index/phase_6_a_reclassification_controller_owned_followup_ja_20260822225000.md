# Phase 6-A 再分類：CONTROLLER_OWNED_FOLLOWUP（User指示による訂正）

```yaml
document_id: phase_6_a_reclassification_controller_owned_followup
status: current_correction_entry
phase: phase_6
subphase: phase_6_a
work_unit: p6_a_wu002_reclassified
role: Claude側設計統括者役
provider: claude_code
created_at: 2026-08-22 22:50:00 JST
supersedes_classification_only: phase_6_a_wu002_pretokenizer_blocker_ja_20260822223100.md
```

本Entryは、直前の[Pre-tokenizer Blocker記録](phase_6_a_wu002_pretokenizer_blocker_ja_20260822223100.md)自体を上書き・訂正するものではない（Append-only、Evidence保持）。User指示に基づき、その事実に対する**分類**だけを訂正する。

## 訂正後の正確な分類

```text
旧分類（訂正対象）: BLOCKED（暗黙にPhase 6-A自体を止める含意を持ちうる表現）
新分類            : CURRENT CONVERSION TOOL REVISIONでPre-tokenizerを認識できず、
                    DeepSeek Derived Artifactを現時点では作成できなかった。
DeepSeek恒久Unsupported: 断定しない。TOOL REVISION依存の一時的Not Executedである。
Resolution Route  : CONTROLLER_OWNED_FOLLOWUP
Handling          : Phase 6 COMPLETE_CANDIDATE Handoff返却後のCodex Independent Reviewで扱う。
                    本Execution中はHomebrew更新、HF Hub照会、追加Network Authorityについて
                    Userへ再Escalateしない。
```

## Evidence保持（変更・削除しない）

```text
Canonical Snapshot (huggingface/) : 無変更のまま保持
失敗Command                        : convert_hf_to_gguf.py --outtype q8_0 ...
Tool Revision                      : Homebrew llama.cpp build 7970 (formula stable 0.2.0)
Exception                          : NotImplementedError: BPE pre-tokenizer was not recognized
                                      （chkhsh: 0d75215efe33c49084836cb245f2fa78de4b3858f5a3e54d5e1fd27f4ce33b05）
Intermediate Artifact              : conversion_work/ は空のまま保持（書込み前に例外発生）
Disk Evidence                      : Install前後・Conversion試行前後のDisk Availログを
                                      phase_6_a_wu002_recipe_freeze_and_dependency_evidence_ja_20260822222500.md
                                      および本系列のPretokenizer Blocker記録に保持済み
```

## Phase 6実行方針（本Entryにより確定）

```text
DeepSeek依存項目          : CURRENT_TOOLCHAIN_UNSUPPORTED／NOT EXECUTED として記録し、
                            成功を捏造しない。
Phase 6-B〜6-I            : DeepSeekに依存しない範囲（Qwen実Model、Model-neutral Runtime、
                            Judge、Repair、Observability、Safe Refusal、Feedback、Recording、
                            UI、Context Size、Max New Tokens、回帰Test）をそのまま連結実行する。
Stop Condition            : 既存Governance／Receiptの真のStop Conditionが発生した場合だけ
                            安全停止する。本DeepSeek Finding、Subphase報告、Auto-Compaction、
                            5時間制限後の自動再開は停止理由にしない。
Completion Line           : P6-I COMPLETE_CANDIDATE Handoffまで。Phase 6-J、Git、Phase 7へは進まない。
```

## Next Exact Route

Phase 6-B-WU-002（Backend Adapter／Model Definition）へ進む。Qwenの実LlamaCppModelAdapterをruntime_model_control.ports.ModelBackendPortへ適合させ、Model Definition Resolverを実Registryへ接続する。DeepSeek側のModel Definition登録は、Toolchain Followup解消まで見送る。
