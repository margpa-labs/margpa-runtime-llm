# Phase 2-E Claude Design Governance Handoff

```yaml
document_id: phase_2_e_claude_design_governance_handoff
status: frozen_provider_handoff
phase: phase_2
subphase: phase_2_e
provider: claude_code
language: ja
created_at: 2026-08-14 JST
from_role: Codexプロジェクト責任者兼設計統括者役
to_role: Claude設計統括者役
execution_target: complete_candidate
routine_human_confirmation: prohibited
stable_document_mutation: prohibited
history_operation: append_only_create_only
git_mutation: prohibited
lightning_work: deferred
```

## 1. Mission

Claude Code側でPhase 2-Eを次の順に完遂し、Codex最終Reviewへ渡せる`COMPLETE_CANDIDATE`を作る。

```text
Recovery／Inventory
  → Phase 2-E Design
  → Independent Design Review
  → Design Freeze
  → Implementation
  → Automated Test／Static Check
  → Designer Conformance Review
  → 必要なRework
  → Full Regression
  → Claude Design Governance Final Review
  → COMPLETE_CANDIDATE Handoff
  → Stop
```

Routineな確認、設計選択、実装判断、Test修正、Review再作業およびClaude側Role間連携をCodexまたはユーザーへ返さない。与えられたAuthority内の判断は各Roleが動的に行う。`COMPLETE_CANDIDATE`、または第14節のCurrent Transition Blockerが成立した場合だけ停止・報告する。

## 2. Role Chain

```text
Upstream Authority:
  Codexプロジェクト責任者兼設計統括者役

Claude Controller:
  Claude設計統括者役

Delegated Roles:
  Claude Phase 2-E設計担当者役
  Claude Phase 2-E実装者役

Review Route:
  実装者役
    → Phase 2-E設計担当者役
    → 必要なら実装者役へRework
    → Phase 2-E設計担当者役Final Review
    → Claude設計統括者役Final Review
```

Claude Codeが独立Task／Sub-agentを使用できる場合はRoleごとに分離する。使用できない場合も、同一Context内でRole Transitionを明記し、設計、実装、Reviewを同一判断として混ぜない。各ArtifactはSingle Writerとし、From／Toを必ず記録する。

Claude設計統括者役は、必要なRole、Read Scope、Write Scope、EvidenceおよびTestを、その時点のSource Inventoryと最上位規則に基づいて動的に決める。Package名、File数、Work Unit数またはRole数を機械的に固定しない。必要なものだけを作り、不要なTaskやEvidence Snapshotを量産しない。

## 3. Governing Authority

次を絶対境界とする。

- 作業Rootは、このHandoffが存在する`margpa-runtime-llm/`だけである。
- Project Root外をRead、List、Search、Stat、Execute、Write、Copy、Move、Delete、Permission変更またはTemporary Artifact作成の対象にしない。
- Symbolic LinkがProject Root外を指す場合は追跡しない。
- Human Backup、別Repository、別Project、Desktop、Home直下、Cloud環境、Lightning StudioまたはSecret Storeへ触れない。
- 上位規則、Docs運用、Role Authority、Append-only、Stable／History境界を変更しない。
- Authority内の通常判断を、単なる不確実性を理由に人間へ返さない。
- Authority拡張、Root外操作、外部副作用、不可逆操作、Secret、目的変更または最上位規則との衝突を独断で許可しない。

ProviderのTool Permission、Filesystem Permission、過去の類似許可、効率、善意または推測はAuthorityの代替ではない。

## 4. Documentation Contract

### 4.1 Existing Stable Docs — Absolute Read-only

Claude Codeは次の既存Stable文書を編集、上書き、Rename、Move、Delete、Formatまたは自動更新しない。

```text
docs/project/current/**
docs/project/shared/**
docs/public/**
docs/project/phases/phase_2/phase_index_ja.md
docs/project/phases/phase_2/requirements/**
docs/project/phases/phase_2/architecture/**
docs/project/phases/phase_2/governance/**
docs/project/phases/phase_2/adr/**
docs/project/phases/phase_2/handoffs/**
docs/project/phases/phase_2/operations/**
```

例外は、本Handoffが明示するHistory配下への新規Append-only Createだけである。本Indexと本HandoffもClaude側ではRead-onlyとする。Stable正本への統合、Phase Index更新、Roadmap更新およびCurrent／Shared更新は、Claude完了後のCodex Review工程で扱う。

### 4.2 Claude Append-only Write Scope

設計、ADR、Freeze、Handoff、Status、Review、Correction、ClosureおよびRecovery Checkpointは、必要なものだけを次の既存History Directoryへ新規作成する。

```text
docs/project/phases/phase_2/history/requirements/
docs/project/phases/phase_2/history/architecture/
docs/project/phases/phase_2/history/adr/
docs/project/phases/phase_2/history/handoffs/
docs/project/phases/phase_2/history/operations/
docs/project/phases/phase_2/history/index/
docs/project/shared/history/automation/
```

既存HistoryはImmutableであり、修正が必要でも旧Fileを編集しない。新しいCorrection／Superseding Evidenceを追加する。

推奨Filename：

```text
claude_phase_2_e_<subject>_<YYYYMMDDHHMMSS>.md
```

全Handoff／Status／Reviewに最低限、次を含める。

```text
From
To
Role
Status
Baseline
Authorized Scope
Forbidden Scope
Current Point
Files Created／Modified
Validation
Open Current Blocker
Controller-owned Next Work
Deferred Evidence
Exact Next Route
```

### 4.3 Checkpoint Density

Contextまたは利用可能量の途中終了から差分再開できるよう、意味のあるWork Unit境界でAppend-only Statusを残す。ただしTaskごと、Commandごと、軽微な判断ごとに大量Snapshotを作らない。

Checkpoint Trigger：

- Design Freeze完了。
- Implementer Handoff完了。
- Initial Implementation／Test完了。
- Required Rework判定。
- Rework完了。
- Final Review完了。
- Resource／Context限界が近く、安全停止が必要。

## 5. Source／Test／Config Mutation Authority

Phase 2-Eを成立させるSource、Testおよび必要最小限のConfigは変更・新規作成できる。Exact Pathは、Required ReadingとRead-only Inventoryの後にClaude Phase 2-E設計担当者役が動的に確定し、Frozen Design Handoffへ列挙する。

```text
Potential Mutation Classes:
  src/**
  tests/**
  config/** only when technically necessary and non-secret
```

既存Phase 1／Phase 2-A～2-D Contract、Public Demo、Basic Preview、v1 Chat、Persistent Conversation、Configuration ControlまたはSecurity Boundaryを暗黙に変更しない。変更が不可避な場合は、Compatibility、Rollback、Regression TestおよびExact ReasonをFreezeしたうえで、Phase 2-E目的に必要な最小差分だけにする。

ユーザーの実`runtime_data/`をTest Fixtureとして使用、初期化、削除、強制Migration、修復、Copyまたは内容確認しない。TestはTemporary Directoryまたは専用Test FixtureをProjectの既存Test Contractに従って使用する。

## 6. Phase 2-E Functional Scope

Phase 2-Eは次の3領域を一つのSubphaseとして設計・実装する。

### 6.1 Runtime Composition Switchboard Foundation

Runtime ComponentをHard-codeされた巨大条件分岐ではなく、交換可能なTyped Descriptor／Registry／Resolution境界として扱う。

最低限扱う情報：

- Component Identity、Kind、Version。
- Enabled／Disabled／Unavailable／Denied等の状態差分。
- Capability、Dependency、Conflict、Degraded State。
- Side-effect、Apply Timing、Restart Requirement。
- Effective Source、Revision、Canonical Digest。
- Configuration ControlとのSafe Link。
- 将来の`off／observe／enforce`へ接続できるSeam。

Phase 2-EではAgent、Tool、Full Governance Engine、Policy Authority、Permission昇格またはPhase 7 Full RAGを実装しない。Componentの存在、登録、Availability、Enabled、Selection、Authorityおよび実行許可を混同しない。

### 6.2 Documentation RAG Multi-turn Follow-up

Persistent ConversationにおけるDocumentation RAG Follow-upを、Phase 1-exのSource-preserving ContractとPhase 2のConversation Branch Contractを維持して成立させる。

- 選択中BranchのCompleted TurnだけをConversation Contextへ使用する。
- 過去Assistant MessageをProject AuthorityまたはRetrieval Sourceとみなさない。
- Project Docs由来の根拠、User Input、Assistant Outputを混同しない。
- RAG OFF、Unavailable、Retrieval 0件、Warning、Failureを別状態として扱う。
- Context Budget超過を黙って無制限投入、暗黙Truncateまたは根拠のないSummaryで処理しない。
- 公開可能Corpusの境界を維持する。
- Phase 7のより高度なRetrieval／Index／Evaluationへ差替え可能なPortを残す。

### 6.3 Persistent Citation Evidence

引用元をBrowser Page Memoryだけに置かず、次の再表示でSafe Citation Projectionを復元できるようにする。

- Browser Reload。
- Server Restart。
- Chat Listから保存済みConversationを再Open。
- Resume。
- Retry／Regenerate。
- Branch Select。

Citation EvidenceはAssistant Message本文へ暗黙に埋め込まず、少なくとも次との関係をTypedに保持する。

- Conversation Scope。
- Conversation ID。
- Turn ID。
- Canonical Assistant Result。
- Project-relative Source Path。
- Heading／Section。
- Source Digest。
- Corpus／Index Revision。
- Safe Retrieval Metadata。

次は保存しない。

- Absolute Local Path。
- Secret／Credential。
- Raw Thinking。
- System Prompt。
- Tool内部情報。
- Hidden Original。
- 未確定Partial Output。
- Raw Exception。
- 無制限のRaw Retrieved Chunk。

Assistant CompletionとCitation EvidenceのAtomicity、Crash Recovery、Schema Version、Migration、Rollback、Corruption、Unknown Newer Version、Retry／Regenerate／Branch整合をTestする。RAG OFFではCitation Write 0とし、Public／Basic Previewでは既存方針どおりPersistent Build／Read／Write Binding 0を維持する。

## 7. Compatibility Invariants

- Phase 2-A～2-Dは`COMPLETE／USER ACCEPTED`のまま維持する。
- Existing `/api/v1/chat/**`のEphemeral Contractを壊さない。
- Public／Basic PreviewへConversation Persistence、Citation PersistenceまたはConfiguration ControlをBindingしない。
- Local Private Persistent ConversationのScope Isolation、CAS、Retry、Regenerate、BranchおよびRestart Recoveryを維持する。
- Canonical Assistant Message、Citation Evidence、Raw Thinking、System PromptおよびRAG Internal Artifactを分離する。
- Existing Documentation RAG OFF／ON、Safe Reference Projection、Markdown SecurityおよびSource Boundaryを維持する。
- Model、Environment、Cloud、LightningまたはSecret Contractを変更しない。

## 8. Design／Implementation Execution Contract

Claude Phase 2-E設計担当者役は、実装前に少なくとも次をAppend-onlyで確定する。

1. Requirements。
2. Architecture。
3. ADR。
4. Exact Source／Test Mutation Manifest。
5. Acceptance Matrix。
6. Implementer Handoff。
7. Independent Design Review／Freeze Receipt。

設計Reviewで重大Findingを検出した場合、Claude設計統括者役の責任範囲で修正し、CorrectionをAppend-onlyで残してFreezeする。通常の設計判断を人間へEscalateしない。

Claude Phase 2-E実装者役はFrozen Handoffの範囲内だけを実装する。Scope外変更が必要と判明した場合は勝手に拡張せず、Claude Phase 2-E設計担当者役へ戻す。設計担当者役はAuthority内なら動的にCorrectionを発行し、実装者役へ返す。

実装完了後、設計担当者役はSource、Test、Contract、Security、PersistenceおよびForbidden Diffを独立Reviewする。Required Findingは実装者役へ返し、全件CloseするまでTechnical Closureにしない。

## 9. Required Validation

Repositoryの既存Toolchainと前Subphase Evidenceから正確なCommandを解決し、最低限次を実行する。

- Phase 2-E Target Unit／Integration Test。
- Conversation Domain／Persistence／API／UX Regression。
- Configuration Control Regression。
- Documentation RAG Regression。
- Public／Basic／v1 Zero-binding Regression。
- Browser Static／Security Contract。
- Ruff Format Check／Ruff Check。
- Mypy。
- Full Test Suite。
- `runtime_data/`非Mutation確認。
- Stable Docs非Mutation確認。
- Project Root外Mutation 0の確認。

特に次のMatrixを含める。

- Reload／Restart／Reopen／ResumeでCitation復元。
- Retry／Regenerate／Branch SelectでCanonical TurnとCitationが一致。
- CompletionとCitation CommitのAtomicity。
- Commit応答喪失、Crash Recovery、Idempotency。
- Schema Migration、Rollback、Corrupt Record、Unknown Newer VersionのFail-closed。
- RAG OFF／Unavailable／0件／Warning／Failureの区別。
- RAG OFF Citation Write 0。
- Public／Basic Build／Read／Write／Route Call 0。
- Existing v1 Persistent Call 0。
- Sensitive／Forbidden Field Persistence 0。

実Browserの最終UX確認は、Claude側Automated Contractが合格した後のユーザーAcceptance Gateとして明記する。Claude側の自動化可能な検査を未実施のままManual Gateへ押し戻さない。

## 10. Explicit Prohibitions

Claude Codeは次を行わない。

- 既存Stable Docsの更新。
- 既存Historyの編集。
- Git Commit、Push、Pull、Fetch、Merge、Rebase、Reset、Checkout、Stash、Tag、Release、BranchまたはPR操作。
- GitHub、Network、Lightning、Cloud、External ServiceまたはSecret操作。
- Phase 2-FまたはPhase 3の開始。
- Lightning版Phase 2-Eの設計・実装・試験。Lightning再反映はPhase 3またはPhase 4完了後の別判断とする。
- Public／Basic PreviewへのPersistence Binding。
- Agent／Toolの実装。
- Phase 7 Full RAGの先取り。
- Model Download、Dependency追加またはEnvironment再構築。ただし既存Dependencyだけで成立不能な重大Blockerを発見した場合は変更せず報告する。
- User Runtime Dataの削除、強制MigrationまたはTest利用。
- Project Root外操作。

## 11. Resource／Context Safety

Claude Code側の利用可能量またはContextが完遂前に不足する場合、無理に完了扱いしない。直近の意味あるWork Unit境界でAppend-only Recovery Statusを新規作成し、次を記録して安全停止する。

```text
status: paused_resource_boundary
completed_scope:
current_exact_point:
files_created:
files_modified:
validation_completed:
open_required_work:
current_blocker:
next_role:
next_exact_action:
```

中途半端なSourceをCommit／Pushしない。既存成果を削除、Rollbackまたは帳尻合わせしない。

## 12. Completion Criteria

次を全て満たす場合だけ`COMPLETE_CANDIDATE`とする。

1. Runtime Composition Switchboard Foundationが実装・Test済み。
2. Persistent Documentation RAG Multi-turn Follow-upが実装・Test済み。
3. Citation EvidenceがReload／Restart／Reopen／Resume／Retry／Regenerate／Branchを越えて復元可能。
4. Phase 2-A～2-D、v1、Public、Basic、Configuration ControlおよびRAG既存ContractのRegressionが合格。
5. Migration、Rollback、Corruption、Unknown Version、Crash Recovery、AtomicityおよびIdempotencyが合格。
6. Sensitive Data、Raw Thinking、System Prompt、Hidden Original、Partial OutputおよびAbsolute PathのPersistence 0。
7. Full Test／Static Checkが合格。
8. Existing Stable Docs Mutation 0。
9. Project Root外Mutation 0。
10. User Runtime Data Mutation 0。
11. Current Transition Blockerなし。
12. Phase 2-F、Lightning、GitおよびExternal Action未実施。

## 13. Final Completion Handoff

Claude設計統括者役は最後に次を新規作成する。

```text
docs/project/phases/phase_2/history/handoffs/
claude_phase_2_e_completion_handoff_<YYYYMMDDHHMMSS>.md
```

最低限、次を含める。

- `status: complete_candidate`。
- Git Baselineと開始時差分。
- Role Chainと各Roleの成果。
- Frozen Design文書一覧。
- Source／Test／Configの全Changed File。
- Initial Finding、ReworkおよびClose Evidence。
- Target／Regression／Static／Full TestのCommand、件数、結果。
- Manual Browser Acceptanceへ残すExact項目。
- Current Blocker。
- Controller-owned Next Work。
- Deferred Evidence。
- `runtime_data/` Mutation確認。
- Stable Docs Mutation確認。
- Project Root外Mutation確認。
- Git／External／Lightning未実施確認。
- Codex Final Review Entry Point。

Final Handoff作成後は追加修正を開始せず停止する。Codex側がReviewし、必要ならExact Reworkを別途返す。

## 14. Current Transition Blocker Eligibility

次の全条件を満たす場合だけ、Claude設計統括者役はCurrent Transition Blockerとして停止できる。

1. Phase 2-Eの`COMPLETE_CANDIDATE`成立に直接必要である。
2. 現時点で未解決である。
3. Claude側Roleの既存Authority、設計、調査、実装、TestまたはReworkでは解決できない。
4. 放置すると安全性、完全性、可逆性、AuthorityまたはUser Dataを破壊する。

次はBlockerにしない。

- Claude設計統括者役または委譲Roleが次工程で解決できる設計・実装判断。
- Accepted／Closed済みPhase 2-A～2-Dの過去Finding。
- Phase 2-F、Phase 3、Lightning、Claude以外のProviderまたはPhase 7 Full RAGの将来課題。
- Manual Browser Acceptanceの未実施だけ。
- 非必須の改善候補。

Blocker報告時は、事象、Evidence、試した安全な解決、影響、なぜClaude側Authorityで解決不能か、必要な最小Human Decisionを一つのAppend-only Statusへ記録する。

## 15. Final Route After Claude Stop

```text
Claude COMPLETE_CANDIDATE
  → Codexプロジェクト責任者兼設計統括者役がDiff／Design／Test／BoundaryをReview
  → 必要ならClaudeまたはCodexへExact Rework
  → ユーザーがMacで手動Acceptance
  → CodexがStable Docs／Roadmap／Phase Indexを通常運用で統合
  → ユーザーのBackup Gate
  → 別途許可後にCommit／Push
  → Phase 2-Fを別途開始
```

本HandoffはPhase 2-F開始、Git反映、Lightning反映またはStable Docs更新のAuthorityを生成しない。
