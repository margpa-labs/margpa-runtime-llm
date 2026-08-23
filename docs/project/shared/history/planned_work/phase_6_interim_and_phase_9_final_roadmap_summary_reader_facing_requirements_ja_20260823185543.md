# Phase 6暫定版／Phase 9最終版 Roadmap要約 — 人間向け表示要件予約

```yaml
document_id: phase_6_interim_and_phase_9_final_roadmap_summary_reader_facing_requirements_20260823185543
status: planned_requirements_frozen_pending_implementation
document_type: append_only_planned_work
recorded_at: 2026-08-23 18:55:43 JST
decision_authority: user
applies_to:
  - phase_6_closure_interim_summary
  - phase_9_closure_final_summary
supersedes: none
extends:
  - phase_9_closure_roadmap_summary_reservation_ja_20260823154121.md
canonical_detailed_roadmap: docs/public/roadmap_ja.md
planned_summary_path: docs/public/roadmap_summary_ja.md
primary_language: ja
source_mutation_authorized_now: false
git_mutation_authorized_now: false
```

## 1. Decision

Phase 6 Closureで人間向けRoadmap要約の暫定版を作成し、Phase 9 Closureでその時点の全成果を反映した最終版へ更新する。配置先は詳細版と同じ`docs/public/`、予定Pathは`docs/public/roadmap_summary_ja.md`とする。

要約版は、Project内部の設計者向け詳細Roadmapではなく、第三者が短時間で「何を作っているか、現在どこまで進んだか、今後何を行うか」を把握するための公開入口である。内容は可能な限り日本語とし、固有の技術名称、規格名、製品名およびMode名だけ必要に応じて英語を併記する。

## 2. Source-of-truth Boundary

```text
詳細正本 : docs/public/roadmap_ja.md
要約版   : docs/public/roadmap_summary_ja.md
実装事実 : Source／Test／Accepted Phase Closure Evidence
```

- 要約版は派生Navigation文書であり、新しい計画正本を増やさない。
- 詳細版と衝突する場合、AcceptedなAs-built、Phase Closureおよび詳細Roadmapを優先する。
- Phase 6暫定版とPhase 9最終版のどちらも、生成時点、対象Phase、参照正本および状態をYAMLへ記載する。
- 未完了、部分成立、延期、予約、未着手を、読みやすさのために完了へ変換しない。
- 内部用Absolute Path、個人情報、Secret、Provider Memory、会話内の愛称／口語、未公開の機密Evidenceは掲載しない。

## 3. 文書構造と行数方針

内容は簡潔にし、内部Evidenceの列挙やWork Unit単位の長い履歴を持ち込まない。基本構造は次とする。

1. YAML Header。
2. Projectを一文で説明する短い概要。
3. 全Phaseの簡易進捗表。
4. Phaseごとの短い目的／主要成果／次の到達点。
5. 製品開発と並行して行っている開発方法研究の進捗。
6. 現在地と次のPhase。
7. 詳細Roadmap、ConceptおよびOverviewへのLink。

各Phase節は原則として短い導入文と3〜6個程度の要点に収める。Subphase、Acceptance ID、Test Command、Handoff名および個別Incidentの詳細は、全体像の理解に不可欠な場合だけ記載する。

## 4. 先頭の全Phase簡易進捗表

文書上部に、`roadmap_ja.md`に存在する全PhaseをPhase 1から漏れなく載せる。Phase 1-ex等のExtensionはPhase 1行へ統合するか従属行として表示できるが、成果を欠落させない。

推奨列は次とする。

| Phase | 状態 | 主題 | 現在の主要成果／次の到達点 |
|---|---|---|---|

状態Labelは日本語を優先し、必要に応じて括弧内へ正本の英語Stateを併記する。

```text
完了
進行中
開始可能
計画済み
将来研究
延期／別Gate
```

表は一目で現在地が分かる密度にし、各Phaseの詳細説明をそのまま複製しない。

## 5. Phase別要約の要求粒度

Phaseごとの説明は、次の積み上げを理解できる粒度とする。実際の状態、名称および完了範囲は、要約作成時のAs-builtと詳細Roadmapから再導出する。

### Phase 1 — LLM Runtime基礎

- ローカルLLM Runtime、Model Adapter、Streaming、停止、Thinking表示、Web UI、Profile／Configurationの基礎。
- Phase 1-exのPublic／Git整備、Recovery／Docs／運用基盤はPhase 1の拡張成果として簡潔に統合する。

### Phase 2 — Persistent Chat／React／RAG基礎／Cross-provider実験

- 会話永続化、Chat List、Resume、Retry／Regenerate／Branch、Citation永続化。
- React化、Rename／Delete／Settings UI、RAGとCitationの改善。
- Automation Pilot、Claude Code併用、Cross-provider Handoff／Reviewの初期実証。

### Phase 3 — Generic Governance Definition基盤

- 任意のGovernance Definitionを受け入れるProvider、Manifest、Validator、Trusted Adapter、Normalized IR、Compiler、Evidence基盤。
- 特定GDをCoreへHard-codeせず、交換可能なGovernance Foundationを成立させたこと。

### Phase 4 — Main Model Governance

- Main Modelの前後へGovernance Pointを置き、Definition選択、評価、Action ResolutionおよびOFF／OBSERVE／ENFORCEを実証。
- ARGD／DAGDを最初の候補として接続するが、Coreでは特別扱いしない。
- Dynamic Model／Context／Max Tokens、Current Model表示および一般的なChat UX改善を、実際の成立範囲に合わせて記載する。

### Phase 5 — Security／Policy／Authority分離

- Guardrail、Prompt Injection／Secret／個人情報等の検知、安全境界。
- Policy適用、委任、承認待ち、Human Approval、責任主体およびTool Permissionの分離。
- 安全判定、Policy判断、Authority判断をMain Governanceから独立Component化したこと。

### Phase 6 — Judge／Evaluation／Repair／Observability

- LLM-as-a-Judgeを含む評価、Repair Trigger／Budget／無限Loop防止、Status Reporting、Recording／Evidence。
- `idle → generating → judging → repairing → rejudging → terminal`等の利用者向け観測。
- Main／Guardrail／Judge／Repair／RecordingおよびModel切替を、実際のClosure状態に基づいて記載する。

### Phase 7 — RAG and Data Governance

- 本格RAG、Chunking、Embedding、Index／Retriever、Citation、Query／Chunk Digest／Score等のEvidence。
- Source Quality、Document Prompt Injection、Knowledge境界および必要に応じたWeb SearchのGovernance。

### Phase 8 — Agent／Tool／Memory／Handoff Governance

- LLMを回答生成器から実行主体へ拡張し、Planning、Tool、Agent、Memory、Handoffを統治。
- Agent／Toolへ適用する`constitution/`と、開発体制用`docs/project/shared/constitution/`を混同しない。
- MARGPA Constitution、Authority、停止／復旧、EvidenceおよびOFF／OBSERVE／ENFORCE研究Mode。

### Phase 9 — Experiment／Multi-Governance Research Platform

- Model、GD、RAG、Judge、Repair、Mode等を組み替え、BaselineとGoverned Runtimeを比較する研究基盤。
- 複数GovernanceのConflict Resolution、Cross-domain Orchestrationおよび実験Evidence。
- Phase 9末尾へ予約されたContext自動圧縮／手動圧縮、Recovery／Handoff生成、Governance観測Panel等は、実装済み範囲だけを記載する。

### Phase 10以降 — Hardening／Cloud／External R&D

- Audit強化、Hash Chain／WORM、Cloud／AWS、複数Model、Responsive UI、Desktop Application、外部独立R&D接続等。
- EASA、DLAGSA、OCILNSその他の独立R&DはGeneric Port経由で接続し、Coreへ専用実装を固定しない。
- Phase 10群が将来分割された場合は、詳細Roadmapの現行Phase構造へ追随して全行を追加する。

## 6. 一行で伝える全体の積み上げ

要約版では、少なくとも次のProduct進捗を一つの連続した流れとして読めるようにする。

```text
LLM Runtimeの基礎
→ 会話永続化／Chat List／Resume
→ React化
→ RAG改善／Citation永続化
→ Rename／Delete／Settings UI
→ Generic Governance Definition基盤
→ Main Model Governance
→ Security／Policy／Authority分離
→ Judge／Evaluation／Repair／Observability
→ RAG／Data Governance
→ Agent／Tool／Memory／Handoff Governance
→ Multi-Governance研究Platform
→ Hardening／Cloud／External R&D
```

## 7. 開発方法そのものの研究進捗

Product Roadmapとは別に、`Automation／Cross-provider／Compaction／Agent間Role分離／Codexタスク間情報共有`を一つの短い節へまとめる。

### 7.1 進展の流れ

```text
Codex／Claude Cross-provider Handoff
→ 詳細設計・実装・Test・ReviewのRole委任
→ Gate／Authority／Scope制御
→ Long-running Automation
→ Manual／Auto Compaction Recovery
→ Codexタスク間の情報共有・直接報告
→ 複数Agent／TaskのScope分離並行稼働
```

### 7.2 現在の成果

- Repository内Index／Handoff／EvidenceをCross-provider正本とし、Provider Memoryに依存しない引継ぎが成立した。
- Claude Codeによる大規模Long-running実装、Auto-Compaction後のRecovery、5時間利用制限後の自動再開を実運用で確認した。
- CodexをController／Independent Reviewer、ClaudeまたはCodex別Taskを大規模Executorとして分ける構成の有効性を確認した。
- Project責任者兼設計統括者、設計者兼実装者、Phase担当、Reviewer等へRoleを分離し、それぞれのSource／Docs／実行Authorityを限定した。
- Recovery Index、Exact Handoff、Material Boundary、Two-key Activation、Stop Conditionにより、長期作業の再開可能性を高めた。
- Codexの別Task間でExact Handoffと完了報告を直接受け渡し、SubAgentではないTask同士のReview／Rework往復を行える状態にした。
- 複数Agent／Taskを、対象Path、Mutation Envelopeおよび責務が競合しない範囲へ分け、並列稼働できる状態を実証した。

### 7.3 誇張しない制約

- Cross-provider実装は有効だが、自己Review、False Completion、指示保持、Root外ActionおよびEvidence表現に独立Reviewが必要である。
- Auto-Compaction／利用制限Recoveryは成立した事例を持つが、毎回の完全復元を保証するものではない。
- Long-running Automationは最上位規則、Authorized Root、Human Gate、Role AuthorityおよびStop Conditionを無効化しない。
- 「高速に作成した時間」だけでなく、Independent Review、Rework、実機AcceptanceおよびClosureまでを含む総所要で評価する。

## 8. 読者向け表現規則

- 見出し、表、状態、説明文は可能な限り日本語にする。
- `OFF／OBSERVE／ENFORCE`、RAG、LLM-as-a-Judge、Runtime等、Project理解に有益な名称は維持し、初出で日本語説明を添える。
- Codex／Claudeの役割と成果は技術的事実として記載し、会話内の愛称、感情的評価またはProviderへの恒久的性格断定を掲載しない。
- 「全自動」「完全」「安全」等は、成立範囲とEvidenceがない限り使用しない。
- 内部の大量Docs、Incident、Rework回数をそのまま列挙せず、成果、制約、改善された運用へ要約する。
- Public Documentとして、Project固有のPrivate Path、User Data、Local Account、Credentialおよび非公開運用情報を除外する。

## 9. Phase 6暫定版とPhase 9最終版

### Phase 6 Closure

- Phase 1〜6はAs-builtの完了成果を記載する。
- Phase 7以降は詳細Roadmapに基づく計画として明確に分ける。
- Phase 6 Closure時点のAutomation／Cross-provider／Compaction／Role分離成果を短く掲載する。
- Phase 7 READYを現在地として示す。

### Phase 9 Closure

- Phase 6暫定版をSourceとして盲目的に更新せず、Phase 1〜9のClosure Evidenceと最新Roadmapから再導出する。
- Phase 7〜9のRAG、Agent／Tool／Constitution、Experiment PlatformおよびContext／Governance観測の実成果を追加する。
- Phase 10以降のPhase再分割、Desktop／Cloud／External R&D予約を最新状態へ合わせる。
- 先頭の全Phase進捗表、本文、現在地およびLinkの整合を最終検査する。

## 10. Acceptance Checklist

- [ ] `docs/public/roadmap_ja.md`と同じDirectoryへ要約版が存在する。
- [ ] YAML Header、生成時点、対象Gate、詳細正本Pathを持つ。
- [ ] 詳細Roadmapに存在する全Phaseを、Phase 1から先頭表へ掲載する。
- [ ] Phase 1〜各Phaseの目的、主要成果および現在状態が簡潔に読める。
- [ ] Product進捗と、開発方法研究の進捗を分けて説明する。
- [ ] Automation、Cross-provider、Manual／Auto Compaction、Role分離、Codexタスク間共有および並列稼働を含む。
- [ ] 完了、部分成立、延期、予約、未着手を区別する。
- [ ] 本文は可能な限り日本語で、第三者が短時間で読める行数に収まる。
- [ ] Private Absolute Path、Secret、User Data、Provider Memoryおよび会話内愛称を含まない。
- [ ] Concept、Overview、詳細RoadmapへのLinkが解決する。
- [ ] Phase 6暫定版ではPhase 7 READY、Phase 9最終版ではPhase 10 READYと整合する。

## 11. Non-authorization

本書は要件予約である。現時点で`docs/public/roadmap_summary_ja.md`、`roadmap_ja.md`、Source、Stable Docs、GitまたはGitHubを変更するAuthorityを生成しない。Phase 6 ClosureまたはPhase 9 Closureの明示Gateで実装する。
