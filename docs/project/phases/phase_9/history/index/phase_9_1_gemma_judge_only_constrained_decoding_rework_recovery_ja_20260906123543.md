# Phase 9-1 Gemma Judge限定Constrained Decoding Rework Recovery

```yaml
document_id: phase_9_1_gemma_judge_only_constrained_decoding_rework_recovery_20260906123543
document_state: complete_recovery
language: ja
created_at: 2026-09-06T12:35:43+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-06 11:10:43 JST Exact Handoff(`phase_9_controller_gemma_judge_only_constrained_decoding_rework_exact_handoff_ja_20260906111043.md`)を受け、Read First指定の4文書を読んだうえでWU-01からWU-06までを順に実施した。GemmaのJSON Schema由来Grammarを初回JudgeとRepair RejudgeだけへJudge Composition経由で明示的に注入する仕組み(`StructuredOutputConstraint`Contract、実Backend Capability Probe、Dynamic Judge Schema Factory)を新設し、Main通常回答・Repair Candidate生成・Qwen3Guard・RAG／Web／Dev Agentへは一切波及させていないことをIsolation Proof全8項目で確認した。Prior Dialogue投影漏れ(`{{dialogue}}`Placeholder新設)とBatch Evidenceの不正確なcall_count／token_usage／seed／Prompt Digest／Config Digestも修復した。実機Trial A・B(Handoffの2本上限どおり)がともに完全に成立し、Adoption Gate全7項目を実機Evidenceで満たしたため、Gemma継続候補として提案するExact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `generation.py`: `StructuredOutputConstraint`Contract新設(`GenerationParameters.structured_output`、Default `None`)。
- `adapter.py`: 実`hasattr(LlamaGrammar, "from_json_schema")`によるCapability Probe追加。
- `chat_template.py`: `_build_grammar()`追加、Grammar構築失敗はFail closed(通常生成へFallbackしない)。
- `inference_service.py`: `structured_output`を持つRequestに対するCapability検証追加。
- `selene.py`: Dynamic Judge Schema Factory `build_gemma_judge_structured_output_constraint()`、`SeleneSemanticEvaluator`への`structured_output_schema_factory`/`config_digest_sha512`/`BatchDispatchEvidence`Observer追加。`{{dialogue}}`Placeholder新設と`build()`での投影。
- `dedicated_role_adapters.py`: `ProductionRoleAdapterFactory`のGemma分岐だけへFactoryを注入(Selene/Main-shared経路は無変更)。
- `judge_live_integration.py`: `token_usage=0`Hardcodeバグ修正、Batch Evidence収集とRejudge Factory透過、`RepairExecutorPort`Protocol拡張。
- `repair_live_integration.py`: `attempt_live_repair()`のRejudge Callへ`structured_output`付与ロジック追加。
- `recording_live_integration.py`: `record_judge_evidence()`へ`call_count`/`prompt_digest_sha512_override`/`batch_evidence_json`追加。
- `web_application.py`: `_repair_executor`Wrapperへ新規引数透過。
- `config/judge_templates/{gemma_4_e2b,selene}/*`: Prior Dialogue Section追加、Manifest Digest再計算。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_ja_20260906123248.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_ja_20260906123248.md](../../handoffs/phase_9_claude_gemma_judge_only_constrained_decoding_rework_exact_return_ja_20260906123248.md)

Maximum Claim: `P9_1_GEMMA_JUDGE_ONLY_CONSTRAINED_DECODING_READY_FOR_USER_RECHECK`

## 5. Open Items at This Point

- `criteria_evaluated`が32に届かない未調査Anomaly(Trial A/Bとも31、Count保存則は成立)——根本原因は未調査。
- 他の既存実機Test5箇所(本Round対象外)はConstrained Decodingを経由するよう更新していない——Trial A/Bのみ2本上限内で実施。
- Trial B自身のRejudge Callへの`structured_output`付与は、Fixture Golden Pathでの直接確認とTrial B自身の実機成功(`repair_outcome='improved'`)から推定されるが、Rejudge Request Parameters自体への実機計装は追加していない。
- Latency実測値は報告したが、定量的なMemory(Process RSS等)計測は行っていない。
- R2-WU-05のGuardは本Roundで再確認していない(Scope外)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-1 Closure、User Acceptance、次Phase着手、追加の実機Trial、Selene実機実行、Guard修正・実機再試行、JSON Retry/Seed変更/Decoder緩和/JSON補修/部分採用、Main Context／Repair Budget／Criterion上限の変更のいずれも行わない。
