# MARGPA Runtime LLM Roadmap 要約版

```yaml
document_type: public_roadmap_summary
document_state: phase_7_closed_phase_8_ready
language: ja
created_at: 2026-08-23
updated_at: 2026-08-30 19:18 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
canonical_detailed_roadmap: docs/public/roadmap_ja.md
current_phase: phase_8_ready_not_started
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
| Phase 6 | 最小Closure／既知課題延期 | Judge／Repair／Observability・Model制御 | Model切替等は成立。Semantic 109、独立Judge／Guard、Repairは未解決Registryへ保持 |
| Phase 7 | 完了／Accepted／Closed | Local RAG／Citation／Data Governance | Local Corpus、Current／Historical Citation、Data Controls、継続性をUser Macで確認。実Web検索はPhase 11以降へ延期 |
| Phase 8 | READY／未開始 | Agent／Tool／Memory／Handoff Governance | 明示貼付URL Evidence、暫定Runtime Constitution、通常Chat／Dev Agent切替、Approval Harness、Tool／MCP Portを持つResearch Foundationを設計Freeze |
| Phase 9 | 計画済み | Semantic Debt／Experiment／Multi-Governance | Selene／Qwen3Guard／GD Semantic 109／Judge・Repairの有界Reworkと構成比較、Context技術Coreを予定 |
| Phase 10 | 計画済み | Project-wide Integration | 全Docs二周、Shared Constitution二周、PADG二周、Full Runtime Constitution、後半UI再編を順番に実施 |
| Phase 11以降 | 将来研究 | Hardening／External Web／Formal Agents／External R&D | 旧Phase 10のCloud、Model、Training、General Web Search、正式Agent Level 1〜3等を後ろ倒し |

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
→ Judge／Evaluation／Repair／Observability（基盤成立・中心Debt保持）
→ Local RAG／Citation／Data Governance＋External Web Scaffold
→ Manual URL Evidence＋Agent／Tool／暫定Constitution Foundation
→ Semantic Debt Rework＋Multi-Governance研究Platform
→ 全Docs／Shared Constitution／PADG／Full Runtime Constitution／UI統合
→ Hardening／Cloud／General Web／Formal Agents／External R&D
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
- Provider Registry、Lifecycle、Budget、Failure、Recording相関等の基盤は拡張したが、最終User MacではSelene／Qwen3Guardが`Active none`、Semantic 109件がDeferred、Built-in Judgeが`evaluated 0`、Repair Golden Pathが未成立だった。
- User判断により、これらを解決済みとせず未解決Registryへ保持し、Phase 6を特殊最小Closureした。技術的完全合格ではない。
- Selene、Qwen3Guard、GD Semantic Live Evaluation、Judge／Repair Golden PathおよびMain Semantic ENFORCEはPhase 9の有界Reworkへ再分類した。Phase 7〜8はRule／Pattern Base GuardrailとBuilt-in Deterministic JudgeまたはNone／OFFを暫定Baselineとする。

### Phase 7〜9 — 知識・行動・Semantic・比較研究

- Phase 7でLocal Corpus、Data Source、Retrieval Evidence、Document Injection、Citationおよびデータコントロールを成立させ、User Mac Manual Acceptance後にClosedとした。Provider非依存Web Search／Fetch Port、Fixture TestおよびSecurity Scaffoldまでは保持するが、実General Web Searchと自動検索は完成を主張しない。RAG ON＋NO_HIT時にModelを呼ばず設定言語の固定回答へ収束するStrict方式は、必要時だけ再開する保留案である。
- Phase 8冒頭で、Userが明示的に貼ったPublic `http／https` URLの取得・画面表示・Untrusted Evidence／Citation接続をBounded Candidateとする。Agent、Tool、Memory、Handoff、全Docs統合前の暫定Runtime Constitution、通常Chat／Dev Agent切替、段階的Approval Harness、Tool Registry／MCP Adapter Port、Generic GD Hookを備えたResearch Foundationを作る。Approval HarnessはLevel 1から、安全な事前Scope内作業を止めず重要GateだけUserへ確認するUXを目標とし、Platform Safety Gateは解除しない。併せてBranch Data／APIを残したUI既定非表示と、データコントロール内のアーカイブ済みChat一覧／開く／解除を追加する。完全削除は見送る。Level 1完成は主張しない。
- Phase 9でSelene、Qwen3Guard、GD Semantic 109、Built-in意味評価、Judge／Repair／RejudgeおよびSemantic ENFORCEの中心Debtを有界Reworkし、Model／GD／RAG／Judge／Repair／Modeの構成差、複数Governance競合、Progressive ENFORCE、Context圧縮・復旧の技術Coreを研究する。大規模UI再編は行わない。

### Phase 10 — Project-wide Integration

次を混同せず、順序を固定する。

1. Project全DocsをPass 1でInventory化し、`project/current/`、各Phase Stable、Public、Shared、History等の正本妥当性を更新する。
2. Pass 2で全Source Docsを再走査し、漏れ、Conflict、Current／Historical、Phase番号、Pointer、Digest、Provenanceを再監査する。
3. Shared Constitution Pass 1で全Docsを改めて走査する。`shared/`は重点Sourceだが唯一のSourceにしない。
4. Shared Constitution Pass 2で全Docsを再走査し、Rule漏れ、誤昇格、Provider／Common混同、過剰停止・過剰Authority等を監査する。
5. `Portable Autonomous Development Governance Package`（`PADG Package`）を`common／Codex／Claude／Copilot`分離で作り、別Project移植性を第2周で再検証する。
6. Phase 8暫定版からFull Runtime Constitutionへ移行し、Constitution Providerと17 JSON／18 Logical GD Providerを疎結合並列評価へ接続する。
7. 最後にAdvanced Settings、Sidebar、Context／Token、Context Action、右側Governance Trace、Strict／ProgressiveおよびResponsive UIをまとめて再編する。

この再編のLossless正本は`docs/project/shared/history/planned_work/phase_9_10_11_docs_constitution_padg_ui_web_and_no_hit_lossless_restructure_reservation_ja_20260830170415.md`である。

### Phase 11以降 — Hardeningと外部展開

- 実General Web Search、Automatic Search、Web-grounded Chat、外部送信Consent／PII EnforcementおよびHostile-site Sandboxを、Account／Credential／Cost／Privacy／Provider運用込みの`Governed External Web Knowledge Runtime`として扱う。
- Audit改ざん耐性、Cloud／AWS、Lightning更新、Desktop Application、Product-level Responsive、動画Multimodal、Long Context、Hardware自動適応を後続Gateで扱う。
- EASA、DLAGSA、OCILNS等の独立R&DはGeneric Port経由で接続する。
- Phase 8 Previewを、仮称`MARGPA Development Agent` Level 1の正式完成、`MARGPA EEAE Agent` Level 2の一案件完遂、`MARGPA FCAE Agent` Level 3の継続Lifecycle運営へ発展させる。Capability名と内部Agent構成を分離し、名称変更可能なInternal IDを維持する。

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
- これらのAutomation、Cross-provider、Compaction、Role分離およびTask間通信を、Provider-neutral Common ContractとCodex／Claude／Copilot固有Adapterへ分離し、Phase 10で全Docs／Shared Constitutionの各二周後にPADG Packageへ移植する。

## 現在地

Phase 3〜5は完了。Phase 6は主要基盤を成立させた一方、MARGPA Semantic Rule 109件、独立Judge／Guardrail Model、Judge／Repair Golden Pathを未解決として保持し、User判断による特殊最小Closureを完了した。Phase 7はLocal Corpus／Citation／Data Controlsと将来Web Runtime用Port／Security Scaffoldを実装し、User Mac Manual Acceptance後に`COMPLETE／ACCEPTED／CLOSED`となった。実Web検索はSecurity、Privacy、Provider運用および公開Demo Riskを理由にPhase 11以降へ延期した。現在はPhase 8の設計、35 Work Unit、40 AcceptanceおよびHandoffがFreezeされ、`READY／NOT STARTED`である。

詳細は[Roadmap](roadmap_ja.md)、[Overview](overview_ja.md)、[Concept](concept_ja.md)を参照する。
