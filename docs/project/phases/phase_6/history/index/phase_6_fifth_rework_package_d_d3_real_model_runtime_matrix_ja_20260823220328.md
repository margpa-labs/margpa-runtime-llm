# Phase 6 Fifth Rework — Package D D-3実Model Runtime Matrix完了Entry

```yaml
document_id: phase_6_fifth_rework_package_d_d3_real_model_runtime_matrix_20260823220328
status: recovery_entry
phase: phase_6
package: package_d
material_boundary: d_3_real_model_runtime_matrix_complete
owner_role: 設計者兼実装者役
created_at: 2026-08-23 22:03:28 JST
authority: phase_6_codex_controller_package_d_d2_resume_authority_ja_20260823213619.md
previous_entry: phase_6_fifth_rework_package_d_d3_pre_real_model_browser_run_ja_20260823214452.md
phase_closure_state: do_not_close
```

## 1. D-3 Result

Project Root内のTask専用Runtime、Conversation Store、Cache、LogおよびEvidenceだけを用い、実Model Runtime Matrixを完了した。

```text
Matrix Result              : PASS
Matrix Step Count          : 20／20
Initial／Final Model       : main.qwen3-4b-q4-k-m
Intermediate Model         : main.deepseek-r1-0528-qwen3-8b-q4-k-m
Server Restart during Round-trip: 0
Final Runtime Revision     : 3
Final Context Size         : 1024
Governance Layer           : active
Task-owned Active Process  : 0
Task-owned Active Model Load: 0
```

Evidence:

```text
.venv/.t/phase_6_fifth_rework_d3_20260823214452/
  browser_evidence/d3_runtime_matrix.json
  server_qwen_cpu_fallback_run3.log
  conversation_data/run3/

d3_runtime_matrix.json SHA-512:
  d0c40bc023a990326e0db7f63f53c4eacb90d90f4d8774464a4d11336c1e5886089f06fbf7ac0a4758e6edbb1091e50704caf5da953e92651f656543475c3535
```

Task専用TemporaryはController／User Cleanup Gateまで残し、自己判断で削除しない。

## 2. Exact Matrix Outcomes

1. Stale Runtime Revisionを伴う変更は`409`で拒否され、Current Digestは維持された。
2. 同一QwenでContext Sizeを`2048 -> 1024`へ変更し、Unload／Reload／Commitを実Modelで完了した。
3. Qwen Turn 1は`QWEN-ONE.`を返し、Judge `observe`、Repair `enforce`、Recording `full`を通過した。
4. Judgeは`completed`、Recommendation `accept`、Confidence `1.0`、RecordingとJudge Evidenceは双方`ok`へ到達した。
5. Server再起動0のままQwen→DeepSeek→Qwenを完了し、各Commit後のModel Key、Artifact Digest、Backend Identity、Governance BindingおよびRevisionを確認した。
6. DeepSeek Commit後の二つの独立Status取得は、同一Revision／Digest／Model Identityを返した。
7. 未登録Modelへの切替は`404 runtime_model_target_not_registered`で拒否され、直前のDeepSeek Stateは維持された。
8. Qwen復帰後、同一ConversationへTurn 2を追加し、`QWEN-THREE.`、既存Turn、Parent TurnおよびStorage Revision継続を確認した。
9. Regenerateで新しい派生Turnを作成し、Branch SelectでHeadを既存Turnへ戻した。
10. Conversation Store、Evaluation Record、Judge EvidenceはProject Root内Task専用Pathへ永続化された。

Package Bで成立したDeepSeek Multi-turnは、以後Chat Template変更0を確認したうえで再利用した。今回のD-3ではModel切替TransactionとConversation継続を同一Cycleで実証し、巨大Model生成の無意味な反復は行っていない。

## 3. Metal Availability and Explicit CPU Fallback

Current D-3 Cycleでは、通常のMetal起動がQwenでも次で失敗した。

```text
ggml_metal_init: error: failed to create command queue
failed to allocate context
```

Context／Batch削減および`n_gpu_layers=0`だけでは、linked Metal Buildの自動初期化を回避できなかった。したがってCurrent MetalをPASSと主張しない。

実Model Matrixは次の明示的Fallbackで実行した。

```text
GGML_METAL_DEVICES=none
compute_kind=cpu
acceleration_api=cpu_native
required_device=cpu
required_acceleration=cpu_native
gpu_layers=0
llama-cpp-python=0.3.34（installed build variant: metal）
```

これはCurrent Technical Evidenceとして`CPU FALLBACK PASS／METAL CURRENTLY UNAVAILABLE`である。Package B／Cの既存Metal EvidenceはHistorical Evidenceとして維持するが、今回の実行結果へ置換しない。

## 4. Browser Evidence Boundary

Browser SkillのInstruction FileがAuthorized Project Root外にあるため、本Taskは同SkillをReadせず、実Browser DOM操作も行っていない。Repository-local ServerとHTTP／SSE Harnessで、実Model Runtime、Conversation、Regenerate、Branch、Mode、Recordingおよび二つの独立Status取得を確認した。

FrontendはPackage A〜Cで変更されておらず、既存のReal Browser Evidenceを再利用できる。ただし今回の二つのStatus取得は実Browserの別Tab DOM同期ではない。Evidence Gradeを膨張させず、P6-ACC-058はPARTIALを維持する。

## 5. Acceptance Delta after D-3

```text
P6-ACC-004 : PASS
  Package A後の実Qwen→DeepSeek→Qwen、Server再起動0を新規実証。

P6-ACC-009 : PASS
  Package A後の同一Qwen Context Reloadを新規実証。

P6-ACC-007 : PARTIAL
  Switch後Conversation継続、Regenerate、Branch Selectは実証。
  Citationは当該ConversationにCitationが存在せず、実Browser表示も今回未実施。

P6-ACC-058 : PARTIAL
  二つの独立Statusは一致したが、実Browser別Tab DOM同期は未検証。

P6-ACC-077 : PARTIAL
  Phase 6累積の「違反0」は文字どおり成立しない。Technical ImpactはNONE。

Re-derived Current Count:
  PASS    : 81
  PARTIAL : 3
```

P6-ACC-077を0件へ改変せず、Authority ComplianceとTechnical Acceptanceを分離する。

## 6. Action Inventory

```text
Source／Test Mutation                    : 0
Project-local Task Temporary Mutation    : YES（上記Exact Root）
Provider Memory Contact                  : 0
Git Action                               : 0
External Network Action                  : 0
Local Loopback Server／Client             : authorized, 127.0.0.1:8011 only
User runtime_data Contact                : 0
New Resume Cycle Root-outside Action     : 0
Package D Cumulative Root-outside Action : 1 known unauthorized incident
Root-outside Persistent Artifact         : 0 known
Retroactive Authorization                : 0
P6-CODEX-042                             : RECORDED／STOPPED／RECOVERED／NON-BLOCKING
```

## 7. Exact Next Action

D-4 Final Verificationへ進む。Backend Full、Focused Runtime Switch／Concurrency／Recording Fault Injection、Ruff、Mypy、Frontend Typecheck／Lint／Test／Buildおよび今回のReal Model Evidenceを最終照合する。通常Failureは最小範囲で修正して継続し、完了時にPackage D Final RecoveryとReturn Handoffを新規作成する。Phase 6 Closureへは進まない。

