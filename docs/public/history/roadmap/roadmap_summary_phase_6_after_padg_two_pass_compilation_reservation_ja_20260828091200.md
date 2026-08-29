# MARGPA Runtime LLM Roadmap 要約版

```yaml
document_type: public_roadmap_summary
document_state: phase_6_interim_checkpoint
language: ja
created_at: 2026-08-23
updated_at: 2026-08-28 09:12 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
canonical_detailed_roadmap: docs/public/roadmap_ja.md
current_phase: phase_6_in_progress_adjust
```

MARGPA Runtime LLMは、Model、RAG、Guardrail、Judge、Repair、Agent、Tool、Memory、Audit、Governance Definitionを交換可能なComponentとして扱い、`OFF／OBSERVE／ENFORCE`の差を証跡付きで比較するAI Governance研究Platformである。

## 全体進捗

| Phase | 状態 | 主題 | 現在の主要成果／次の到達点 |
|---|---|---|---|
| Phase 0 | 完了 | 要件・基礎設計 | Model非依存、疎結合、Evidence、Authority境界を定義 |
| Phase 1／1-ex | 完了 | Portable LLM Runtime | Mac／Lightning、CLI／Web、Streaming、停止、Thinking、Public／Docs運用を成立 |
| Phase 2 | 完了 | 永続会話・React・RAG基礎 | Chat List、Resume、Branch、Citation永続化、Settings UI、Cross-provider Pilotを成立 |
| Phase 3 | 完了 | Generic Governance Definition基盤 | Provider、Manifest、Trusted Adapter、Normalized IR、Compiler、Audit／Evidenceを成立 |
| Phase 4 | 完了 | Main Model Governance | Main Model前後のGovernance Pointと`OFF／OBSERVE／ENFORCE`を実証 |
| Phase 5 | 完了 | Security／Policy／Authority | Guardrail、Injection検知、Policy、Authority、Approvalを独立Component化 |
| Phase 6 | 進行中／要修正 | Judge／Repair／Observability・Model制御 | Model切替等は成立。GD意味Rule、独立Judge／Guard、RepairをRework予定 |
| Phase 7 | 計画済み | RAG／Data Governance | Embedding、Retriever、Citation、Web Search、Data Controls、添付規模判定を予定 |
| Phase 8 | 計画済み | Agent／Tool／Memory／Handoff Governance | 通常Chat／Dev Agent切替、Approval Harness、Tool／MCP Port、Constitution／GD Hookを持つResearch Preview基盤を予定 |
| Phase 9 | 計画済み | Experiment／Multi-Governance研究基盤 | 構成比較、複数Governance競合、Context圧縮・観測を統合予定 |
| Phase 10以降 | 将来研究 | Hardening／Cloud／External R&D | Audit、Cloud、Agent Level 1〜3に加え、二周全Docs走査によるPADG Packageを編纂予定 |

## これまでの積み上げ

```text
LLM Runtimeの基礎
→ 会話永続化／Chat List／Resume
→ React化
→ RAG改善／Citation永続化
→ Rename／Delete／Settings UI
→ Generic Governance Definition基盤
→ Main Model Governance
→ Security／Policy／Authority分離
→ Judge／Evaluation／Repair／Observability（現在Rework待ち）
→ RAG／Data Governance
→ Agent／Tool／Memory／Handoff Governance
→ Multi-Governance研究Platform
→ Hardening／Cloud／External R&D
```

## Phase別の概要

### Phase 1 — LLM Runtime基礎

- GGUF／llama.cppをAdapter越しに動かすLocal Runtimeを実装。
- Streaming、生成停止、Thinking実行／表示分離、設定、CLI、Web UIを整備。
- Phase 1-exでDocs、Recovery、Git、Public Preview、Mac／Lightning運用を整備。

### Phase 2 — 永続会話と実験用Control Surface

- SQLiteによる会話永続化、Chat List、Resume、Retry／Regenerate／Branchを実装。
- React UI、Rename／Delete、Settings、RAG Follow-up、Citation永続化を実装。
- Codex／Claude間のHandoff、Role分離、Automation Pilotを初めて実証。

### Phase 3 — Generic Governance Definition基盤

- 任意Definitionを受けるProvider、Manifest、Validator、Trusted Adapterを実装。
- Normalized IR、Compiler、Repository State、Audit／Evidenceを疎結合化。
- ARGD／DAGD等をCoreへHard-codeせず、Definition 0件でも動く境界を確立。

### Phase 4 — Main Model Governance

- Main Modelの直前／直後へGovernance Pointを接続。
- Rule選択、Observation、Deviation、Action Resolutionを実装。
- 構造的Ruleで`OFF／OBSERVE／ENFORCE`を比較可能にした。意味評価は後続へ分離。

### Phase 5 — Security／Policy／Authority

- Prompt Injection、Secret、個人情報等を扱う決定論的Guardrailを実装。
- Detection、Policy、Authority、Approval、Recommended／Executed Actionを分離。
- OBSERVE非介入とENFORCE Pre-model停止をUser Macで確認。

### Phase 6 — Judge／Repair／Model制御

- Qwen既定を維持しながら、起動中のQwen／DeepSeek切替、Context Size、Max New Tokens、Runtime Identity UIを実装。
- Judge、Repair Budget、Recording／Evidence、停止・Deadline・Late Worker制御を実装し、第9 Rework時点でBackend 1602件、Frontend 221件が合格。
- Conversation、Citation、Branch、二つのBrowser Tab、再起動後Qwen復帰、StopおよびDeepSeek病的反復防止はUser Macで確認済み。
- 一方、ARGD／DAGD意味Rule 109件は全件Deferredで、MARGPA Definitionが意味評価へ未接続だった。
- Current JudgeはMain Model自己評価に留まり、Qwenは誤答を`accept／0.95`、DeepSeekは`malformed_output`、重いCallは`deadline_exceeded`となった。Repair成功経路も再現できていない。
- Phase 6 Reworkでは、Semantic Rule接続、Selene、Qwen3Guard、Role Provider選択、原因別Failure、Recording相関を成立させる。Phase 6は未完了である。

### Phase 7〜9 — 知識・行動・比較研究

- Phase 7で本格RAG、Data Source、Retrieval Evidence、Document Injection、Web Search、データコントロールを扱う。冒頭で汎用File Attachmentの規模を判定する。
- Phase 8でAgent、Tool、Memory、HandoffとMARGPA Constitutionを扱い、通常Chat／Dev Agent切替、段階的Approval Harness、Tool Registry／MCP Adapter Port、Generic GD Hookを備えた`MARGPA Dev Agent Research Preview`を作る。Level 1完成は主張しない。
- Phase 9でModel／GD／RAG／Judge／Repair／Modeの構成差、複数Governance競合、Progressive ENFORCE、Context圧縮・復旧・右側Trace観測を研究する。

### Phase 10以降 — Hardeningと外部展開

- Audit改ざん耐性、Cloud／AWS、Lightning更新、Desktop Application、Responsive UI、動画Multimodal、Long Context、Hardware自動適応を後続Gateで扱う。
- EASA、DLAGSA、OCILNS等の独立R&DはGeneric Port経由で接続する。
- Phase 8 Previewを、仮称`MARGPA Development Agent` Level 1の正式完成、`MARGPA EEAE Agent` Level 2の一案件完遂、`MARGPA FCAE Agent` Level 3の継続Lifecycle運営へ発展させる。Capability名と内部Agent構成を分離し、名称変更可能なInternal IDを維持する。
- Phase 3〜9のLossless Docs統合後に全Docsを二周走査し、`shared/`を重点Sourceとして、`common／Codex／Claude／Copilot`を分離した`Portable Autonomous Development Governance Package`（`PADG Package`）を作る。初版は第2周で再監査し、Gapを新Revisionへ反映する。

## 開発方法そのものの研究

製品機能と並行して、AI Agentを使った開発統治も実験している。

```text
Codex／Claude Cross-provider Handoff
→ 設計・実装・Test・ReviewのRole委任
→ Gate／Authority／Scope制御
→ Long-running Automation
→ Manual／Auto Compaction Recovery
→ Codexタスク間の直接報告
→ 複数Agent／TaskのScope分離並行稼働
```

- Repository内Index／Handoff／Evidenceを正本として、Provider Memoryへ依存しない復旧を運用した。
- ClaudeのAuto-compaction後Recoveryと利用制限後の自動再開、Codex別TaskへのExact Handoffを実証した。
- 大規模Executorと独立Reviewerを分離する構成は有効だったが、False Completion、指示保持、Root境界、Evidence過剰主張には独立Reviewが必要だった。
- 速度は初回実装だけでなく、Review、Rework、User実機Acceptance、Closureまでを含む総所要で評価する。
- これらのAutomation、Cross-provider、Compaction、Role分離およびTask間通信を、Provider-neutral Common ContractとCodex／Claude／Copilot固有Adapterへ分離し、Phase 10 READYでPADG Packageへ移植する。

## 現在地

Phase 3〜5は完了。Phase 6は主要基盤と第7〜9 Reworkを終えたが、User Mac Manual Acceptanceで、MARGPA Semantic Rule 109件の未接続、独立Judge／Guardrail Model未接続、固定TimeoutおよびRepair Golden Path不成立を検出したため`進行中／ADJUST`である。次は中心機能の差分Rework、再Acceptance、Phase 6最小Closureであり、Phase 7はまだ開始していない。

詳細は[Roadmap](roadmap_ja.md)、[Overview](overview_ja.md)、[Concept](concept_ja.md)を参照する。
