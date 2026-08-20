# Claude Phase 2-E Requirements

```yaml
document_id: claude_phase_2_e_requirements_20260815004739
status: frozen
phase: phase_2
subphase: phase_2_e
from_role: Claude Phase 2-E設計担当者役
to_role: Claude設計統括者役
role: phase_designer
baseline: e007110ba713b70f3715b991e0713e511ed21184
authorized_scope: docs/project/phases/phase_2/history/requirements/ (this file, CREATE_NEW)
forbidden_scope: docs/project/current/**, docs/project/shared/**, docs/public/**, docs/project/phases/phase_2/phase_index_ja.md, docs/project/phases/phase_2/requirements/**, docs/project/phases/phase_2/architecture/**, docs/project/phases/phase_2/adr/**, docs/project/phases/phase_2/handoffs/** (existing), docs/project/phases/phase_2/operations/**, Git/External/Secret/Destructive
created_at: 2026-08-15 00:47:39 JST
language: ja
```

## 0. Startup Integrity Note

開始時Git Baselineは`f923b1989d63e0df428b730a6024b9be07993d51`と記載されていたが、実HEADは`e007110ba713b70f3715b991e0713e511ed21184`（baselineの1コミット先）だった。差分は`phase_index_ja.md`と`docs/public/roadmap_ja.md`のStatus更新、および本Handoff自体を含むHistory Evidence追加のみで、コード変更・Rule変更は皆無であることをUnified Diffで確認済み。ユーザーへ報告し、「軽微な記載漏れであり支障なし」との判断とともに続行許可を得た（2026-08-15、本Task内会話）。以後、実HEAD `e007110` を本Handoff系列のEffective Baselineとして扱う。

## 1. Scope Statement

Phase 2-EはPhase 2-A〜2-Dで確立されたConversation Domain／Persistence／API-UX／Configuration Controlの上に、次の3領域を実装する。

1. Runtime Composition Switchboard Foundation
2. Documentation RAG Multi-turn Follow-up
3. Persistent Citation Evidence

Agent／Tool／Full Governance Engine／Policy Authority／Permission昇格／Phase 7 Full RAGの実装は含まない。

## 2. Functional Requirements

### FR-1 Runtime Composition Switchboard Foundation

- FR-1.1 各Runtime Component（最低限、既存のDocumentation RAG／Conversation Persistence／Configuration Controlの3件）についてTyped Component Descriptorを解決できる。Descriptorは最低限、Component Identity（Key／Kind／Version）、State（`ENABLED／DISABLED／UNAVAILABLE／DENIED`）、Capability一覧、Required／Optional Dependency、Conflict宣言、Degraded Reason、Side-effect Level、Apply Disposition（`runtime_applicable／restart_required／unsupported／read_only`）、Restart Requirement、Effective Source、Revision、Canonical Digestを含む。
- FR-1.2 Component登録は矛盾する組み合わせ（重複Key、宣言済みConflict同士が同時にENABLED等）を登録時に拒否し、Fail-closedとする。「黙って受理」しない。
- FR-1.3 Componentの存在・登録・Availability・Enabled・SelectionとAuthority・実行許可を混同しない。Registryは状態を記述・提供するだけであり、新しい実行許可・Permission昇格を生成しない。
- FR-1.4 Registryは既存の3 Component（Documentation RAG／Conversation Persistence／Configuration Control）が実際に解決した状態（既存コードの`resolve_documentation_rag_state()`等の出力）を反映する。既存のLocal／Loopback／認証チェック等、Security-criticalな既存Gateロジックは変更しない（Switchboardは観測・記述層であり、既存Gateの代替ではない。理由はADR参照）。
- FR-1.5 将来の`off／observe／enforce` Governance Bindingへ接続できるSeamとして、Descriptorに`governance_seam_mode`Fieldを持つ。Phase 2-Eでは値は`off`に固定し、他の値を構築不能にする（Fail-closed Placeholder）。
- FR-1.6 Registry状態はLocal／Loopback専用の新規Read-only Endpointから取得できる。Public／Basic Previewでは既存Configuration Controlと同型のZero-binding（未Bind時404、Path／Source情報を漏らさない）とする。

### FR-2 Documentation RAG Multi-turn Follow-up

- FR-2.1 選択中Branchの Completed Turn だけを Conversation Context に使用する（既存`project_generation_history()`のCompleted-only Walkを踏襲し、新規生成呼び出しでも同じ経路を使うことを保証する）。
- FR-2.2 過去のAssistant MessageをProject AuthorityまたはRetrieval Sourceとして扱わない（RAGは常にDocument Corpusに対して検索し、会話履歴Textを検索対象にしない）。
- FR-2.3 RAG OFF、Adapter Unavailable、Retrieval 0件、Warning、Failureを別状態として区別する（既存`DocumentationRetrievalState`／`DocumentationGroundingState`／Warning Codeを踏襲）。
- FR-2.4 Context Budget超過を黙って無制限投入・暗黙Truncate・根拠のないSummaryで処理しない（既存の`documentation_context_budget_insufficient` Warning経路を踏襲）。
- FR-2.5 公開可能Corpusの境界（Public／Basic Previewの8文書Allowlist等）を維持する。
- FR-2.6 Retry／Regenerate／Branch Selectを含むMulti-turn運用下でも、各TurnのCitationが他Turnと混線しないことをTestで証明する（既存ロジックへの変更は最小限とし、主として統合Testで契約を確認する）。
- FR-2.7 Phase 7 Full RAGへ差し替え可能なPort境界（既存`DocumentSourcePort`等のProtocol）を維持し、Phase 2-Eでは実装を追加しない。

### FR-3 Persistent Citation Evidence

- FR-3.1 Citation EvidenceはAssistant Message本文へ暗黙に埋め込まない。
- FR-3.2 Citation Evidenceは最低限、Conversation Scope、Conversation ID、Turn ID、Canonical Assistant Result（Turn経由）、Project-relative Source Path、Heading／Section、Source Digest、Corpus／Index Revision、Safe Retrieval Metadata（Retrieval State／Grounding State／Warning Codes）とTypedに関連付ける。
- FR-3.3 次を一切保存しない：Absolute Local Path、Secret／Credential、Raw Thinking、System Prompt、Tool内部情報、Hidden Original、未確定Partial Output、Raw Exception、無制限のRaw Retrieved Chunk。型のAllowlistによって構造的に混入不能にする（自由記述Fieldを持たない）。
- FR-3.4 次のいずれの再表示後もSafe Citation Projectionを復元できる：Browser Reload、Server Restart、Chat Listから保存済みConversationを再Open、Resume、Retry／Regenerate、Branch Select。
- FR-3.5 Assistant CompletionとCitation Evidenceの書き込みはAtomicとする（同一Turn Commit Transaction内で確定し、片方だけの書き込みが残る状態を作らない）。
- FR-3.6 Crash Recovery時、Citation Evidenceの書き込み未確定Turnは既存のIncomplete Turn Recovery機構に含めて扱う（別のRecovery経路を新設しない）。
- FR-3.7 Schema Versionを持ち、未知の新しいVersionのCitation RecordはFail-closedで「当該TurnのCitation Unavailable」として扱い、Conversation本体の読込・表示は妨げない。
- FR-3.8 Corrupt Citation Record（JSON不正／Digest不一致）も同様にFail-closedで「Citation Unavailable」として扱い、例外をConversation取得全体へ波及させない。
- FR-3.9 RAG OFF時はCitation Write 0とする（該当Turnに行を作らない）。
- FR-3.10 Public／Basic PreviewではPersistent Build／Read／Write／Bindingを一切行わない（既存のLocal専用Gateにより自動的に満たされる設計とする）。
- FR-3.11 Retry／Regenerate（Derived Turn）はSource Turnの既存Citation Evidenceを上書き・削除しない。Derived Turn自身が完了時に自分のCitation Evidenceを持つ。
- FR-3.12 Branch Selectは`head_turn_id`の切替のみで、Citation Evidenceの書き換えを一切伴わない。

## 3. Non-functional / Compatibility Requirements

- NFR-1 Phase 2-A〜2-Dは`COMPLETE／USER ACCEPTED`のまま維持する。
- NFR-2 既存`/api/v1/chat/**`のEphemeral Contract（Storage Write 0含む）を変更しない。
- NFR-3 既存`/api/v2/conversations/**`のContract（CAS、Idempotency、Derived Turn非上書き等）を変更しない。破壊的でない追加（Response Field追加）のみ許可する。
- NFR-4 既存`/api/v2/configuration/**`のContractを変更しない。
- NFR-5 Public／Basic PreviewへConversation Persistence、Citation PersistenceまたはConfiguration ControlをBindingしない。
- NFR-6 Local Private Persistent ConversationのScope Isolation、CAS、Retry、Regenerate、Branch、Restart Recoveryを維持する。
- NFR-7 SQLite Adapter内部実装（Canonical JSON＋SHA-512 Envelope、Commit-operations経由のIdempotency、Scope Key Hashing、ファイルPermission）はDomain／Port層へ漏らさない。
- NFR-8 Model生成中にDB接続・Transaction・File Lockを保持しない（既存原則を維持）。
- NFR-9 `runtime_data/`直下の新規Artifact生成は既存のScope（`persistent/<scope_key>/conversations/`、`recovery/**`）の範囲内に限定し、Project Root直下への新規生成は行わない。
- NFR-10 既存Documentation RAG OFF／ON、Safe Reference Projection、Markdown Security、Source Boundaryを維持する。

## 4. Out of Scope（明示的に対象外）

- Agent／Toolの実装。
- Full Governance Engine（Definition／Compiler／Governance Point Evaluator／Action Resolver／Audit Writer）の実装。`governance_seam_mode`はPlaceholderのみ。
- Policy AuthorityまたはPermission昇格の実装。
- Phase 7 Full RAG（Embedding稼働、高度Index、Evaluation）の実装。
- 既存Local／Loopback／認証チェック等、Security-criticalなGateロジックの置き換え（Switchboardはこれらの上に観測層を追加するのみ）。
- Lightning版Phase 2-Eの設計・実装・試験。
- Public／Basic PreviewへのPersistence Binding。
- Model Download、Dependency追加、Environment再構築。

## 5. Acceptance Criteria（Requirements Level）

Phase 2-E Handoff §12（Completion Criteria）を正本とする。本Requirementsの各FR／NFRはAcceptance Matrix（別文書）で個別Testへ写像する。

## 6. Source Evidence

- Phase 2-E Claude Design Governance Index／Handoff（`docs/project/phases/phase_2/handoffs/claude_code/`）
- Phase 2-E Persistent RAG Citation Evidence Reservation（`docs/project/phases/phase_2/history/operations/phase_2_e_persistent_rag_citation_evidence_reservation_20260814215110.md`）
- Phase 2-A〜2-D Architecture／ADR／Implementation Handoff一式
- Phase 2 Subphase／Task Orchestration Preplan §3（Phase 2-E目的）
- `docs/public/roadmap_ja.md` §Component Registry／Switchboard Foundation
- 実Source Tree調査（`src/margpa_runtime_llm/**`、Agentによる詳細調査結果）

## 7. Status

```text
Current Point            : Requirements Frozen
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（Requirements段階）
Open Current Blocker      : NONE
Controller-owned Next Work: Architecture／ADR／Mutation Manifest／Acceptance Matrix／Implementer Handoffの作成
Deferred Evidence         : NONE
Exact Next Route          : Architecture Design作成へ進む
```
