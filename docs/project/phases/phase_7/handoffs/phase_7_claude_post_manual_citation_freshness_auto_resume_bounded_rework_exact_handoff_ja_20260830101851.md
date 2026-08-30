# Phase 7 Claude Post-Manual Citation／Freshness／Auto-Resume Bounded Rework — Exact Handoff

```yaml
document_id: phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_20260830101851
document_type: exact_differential_execution_handoff
document_state: frozen_ready
language: ja
created_at: 2026-08-30 10:18:51 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_claude_task
phase: phase_7
execution_scope: P7-RW2-0_to_P7-RW2-D
implementation_authority: requires_exact_user_start
maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_7_closure_authority: false
phase_8_authority: false
git_authority: false
```

## 1. Authority／継続方式

本書は、現在のClaude Taskへ渡す差分Handoffである。Fresh Task化、Role再初期化、旧Context消去または3段階Bootstrapを要求しない。

開始宣言を受領した後、P7-RW2-0からP7-RW2-Dまで連結実行する。True Stop Conditionがない限り、Packageごとの進捗報告だけを理由に停止またはUser確認待ちへ移行しない。

本書が許可するのは、Project Root内のPhase 7差分Source／Test／Docs、Project内Task-owned Temporary、変更範囲に比例した検証およびReturn Handoff作成である。

Phase 7 Closure、Phase 8実装、Git、Backup、Roadmap更新、Real Browser操作、Real Network、Provider Memory、User `runtime_data/`接触は許可しない。

## 2. Mandatory Reading

次を指定順で全文読む。既に同一Task内で読了済みでも、本差分の正本だけは再照合する。

1. PoC／MVP Delivery Policy

```text
docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md
SHA-512: 9b7dca30c94fb184b2978c4d4b42904cdc3c6550ae7ab0eb9b35a59b65342fa239c419ad59a65f2a78e6358514cfc8d3d777a6145cb0b8fecb7d94990cd45835
```

2. Frozen Phase 7 Requirements

```text
docs/project/phases/phase_7/requirements/phase_7_requirements_ja.md
SHA-512: e6d5802c36822174eeacb5d703e21e2eaa73e1f82082c31229444993f08b9429f4309ab711e9ab546cb0c5293f75fbf660cb7125fff48546b7e048a7b669b9e4
```

3. Frozen Acceptance Matrix

```text
docs/project/phases/phase_7/operations/phase_7_acceptance_matrix_ja.md
SHA-512: 65a33c7d491aafb89478ce43d6b9f3ad73c3a30bc78f2beaa943787383a7fd85f7d1a3fe7b4571c969a4c89612e5e4cf7f1fd15b0f97d93bf4fe45062b961bff
```

4. Previous Claude Exact Return

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_non_web_closure_alignment_exact_return_handoff_ja_20260829230500.md
SHA-512: af729a2c862e009d8061e0f8c16c5f643b00357cb70bea02f2fa174d4f60d4f19019b2bd95ca82d55fa9033c76146595e7ee1b08ef43f34890455644419188c5
```

5. Controller Review before Manual Gate

```text
docs/project/phases/phase_7/history/operations/phase_7_codex_controller_non_web_closure_alignment_review_ja_20260829230354.md
SHA-512: 1dd0179e114665268c784073e1ba9e84d7d5a1d692c504b81619eccca53e59ea221dd0e9493fd5f1b34a5d25152153cf84e3f6625242a9ae587c7c96f5577d2f
```

6. Controller Manual Test Sheet

```text
docs/project/phases/phase_7/history/operations/phase_7_local_corpus_data_controls_user_manual_test_sheet_controller_revision_ja_20260829230354.md
SHA-512: 8bf814d75795012ad9adb92565203a55ec621c3c8fdfd34f95d412983c3f863f3e992dd0ea6117f11fa66e06a1e35d8552ccc04bd6d7200bfa1bea0c0318bdc6
```

7. User Mac Manual Acceptance ADJUST Evidence

```text
docs/project/phases/phase_7/history/operations/phase_7_user_mac_local_corpus_data_controls_manual_acceptance_adjust_ja_20260830101851.md
SHA-512: 1a3c236fe22fb7e7a3e0da85b91e5e419e53f1056e96622a5895bc454d928bbbb7106db41aa1e9410e792d82491d3da3e0849bf78b41df8d7d47a7b03d217292
```

8. Web Scope Boundary（Phase 8／11へ混入しないため）

```text
docs/project/shared/history/planned_work/phase_8_manual_url_evidence_and_phase_11_general_web_search_lossless_scope_refinement_ja_20260830083225.md
SHA-512: 49649969a5115eaa5633be3da3c9b0c4b4f82dcd949fb0340eb3c6a5d1eb232b31b05ed6646f276500c27879ae04c6331cc4c7539662c2206273d5aca905ada6
```

## 3. Preserved Baseline／Claim Correction

次を保持し、再実装しない。

- Local Corpus登録／更新／Soft-delete／Revision Chain。
- RAG OFF時のLocal Retrieval／Injection Call 0。
- Local CorpusとProject DocsのComposite Source。
- Conversation／Citation Persistence。
- Data Controls Retention Fact／Purpose Consent／Reset。
- Consent全Default OFF。
- P7-ACC-008 Embedding未使用PARTIAL。
- P7-ACC-025 Full Export／一括Delete未実装PARTIAL。
- External Web RuntimeのPhase 11以降Deferred。

ただし、以前の`P7-ACC-012 PASS／Citation Identity完備`ClaimはUser Manualにより失効した。P7-CODEX-007修正・再検証前にPASSへ戻してはならない。

## 4. Active Findings

### P7-CODEX-007 — Citation Chunk／Digest Projection Gap

内部`DocumentationCitation`は`chunk_id`と`document_sha512`を保持するが、Persistent Response、SSE、Frontend型／表示が落としている。

### P7-CODEX-008 — Current Turn Freshness／Unsupported Historical Reuse

削除済みLocal Factを同一ConversationのHistoryから新Turnへ再利用し、無関係なProject Docs Citationを伴う回答を生成できた。過去Evidenceは固定したまま、Current TurnをCurrent CorpusまたはNo Current Evidenceへ収束させる必要がある。

### P7-CODEX-009 — Manual Resume Required

Restart Recovery後のActive ConversationおよびArchive解除後のConversationで、手動Resumeが必要である。起動時全件Resumeではなく、遅延自動Resumeへ変更する。

## 5. Package P7-RW2-0 — Entry／Regression Freeze

1. Mandatory Reading Digestを照合する。
2. 現行Sourceを限定読解し、P7-CODEX-007〜009の再現経路を固定する。
3. 既存Manual Evidenceの表示文言を改変しない。
4. Project内Task-owned Temporaryを使用する。
5. Package 0〜IおよびP7-NW-0〜Eを再実装しない。

Recovery Index:

```text
docs/project/phases/phase_7/history/index/phase_7_post_manual_bounded_rework_p7_rw2_0_recovery_ja_<timestamp>.md
```

## 6. Package P7-RW2-A — Citation Identity Projection

### 6.1 Required Behavior

- Live SSEとPersistent DetailのCitationへ、少なくとも次を損失なく投影する。
  - `source_class`
  - `project_relative_path`
  - `heading_breadcrumb`
  - `chunk_id`
  - `document_sha512`
  - `retrieval_score`
  - `selected_order`
  - `truncated`
- `SystemCitationAdapter`で`DocumentationReferenceBlock.source_class`をCitationへ渡す。
- 既存Citation RecordのBackward Compatibilityを壊さない。必要なら追加Fieldを既存既定値付きで読む。
- FrontendでLocal CorpusとProject Docsを明示的に区別する。
- Chunk ID／Document Digestは短縮表示してよいが、完全値をCopyまたは確認可能にする。
- 過去TurnのCitation IdentityをCurrent Revisionへ書き換えない。
- Reload／別Tab／Restart後も同一Turnへ同じCitation Identityを復元する。

### 6.2 Regression

- Live SSE Projection Test。
- Persistent Detail Projection Test。
- Citation SQLite Round-trip／旧Record Compatibility Test。
- Frontend Type／Render／Copy Test。
- Local CorpusとProject DocsのSource Class区別Test。

Recovery Index:

```text
docs/project/phases/phase_7/history/index/phase_7_post_manual_bounded_rework_p7_rw2_a_recovery_ja_<timestamp>.md
```

## 7. Package P7-RW2-B — Current Turn Freshness／Grounding

### 7.1 Immutable Historical Contract

```text
過去Turn:
  当時のCitation／Revision／Digestを固定する。

新Turn:
  Current Corpusだけを再検索する。
  更新済みなら最新Revisionを使用する。
  削除済み／Current Evidence不足なら現在の根拠なしへ収束する。
```

Historical CitationをCurrent Sourceへ追従更新する実装は禁止する。

### 7.2 Required Behavior

- Exact Manual Probe `Nazuna Probe Orion`をRegression Fixture化する。
- Local Document更新後、同一Conversationの新Turnが最新RevisionのFactを使用する。
- Local Document削除後、同一Conversationの新Turnが過去HistoryのFactをCurrent根拠として再提示しない。
- Current Retrievalが質問対象をCoverageしない場合、無関係なProject Docsを回答根拠ありへ変換しない。
- `NO_HIT`／`SUBJECT_COVERAGE_INSUFFICIENT`等のCurrent Grounding Stateを、過去Assistant Messageより強いCurrent Turn制御として扱う。
- Current Grounding不足時、回答を停止するか「現在のCorpusに根拠がない」と正直に表示する。過去会話にその値があったことを説明する場合も、Current Evidenceではないと明示する。
- Candidate／Partial Retrieval Evidenceを表示する場合は、回答を支持する「参照文書」と混同しない。
- Judgeは補助防衛線とし、RAG側FailureをJudgeだけへ依存させない。

### 7.3 Required Regression Scenario

```text
1. Local Document rev 1 = CEDAR-7319を登録。
2. 同一Conversationで質問し、rev 1 Citationを保存。
3. rev 2 = CEDAR-8420へ更新。
4. 同一Conversationの新TurnでCEDAR-8420とrev 2 Identityを確認。
5. DocumentをSoft-delete。
6. 同一Conversationの新TurnでCEDAR-8420をCurrent Factとして回答しない。
7. 新規ConversationでもCurrent Evidenceなしへ収束。
8. 手順2／4の過去回答と過去Citationは一切変化しない。
```

Lexical Retrieval／Subject Coverageの最小修正で成立させる。Embedding、Vector DB、一般的なTruth VerificationまたはPhase 6 Judge Reworkへ拡張しない。

Recovery Index:

```text
docs/project/phases/phase_7/history/index/phase_7_post_manual_bounded_rework_p7_rw2_b_recovery_ja_<timestamp>.md
```

## 8. Package P7-RW2-C — Lazy Auto-Resume

### 8.1 User Contract

- Server Restart後、ArchiveされていないConversationは手動の「再開」を押さず、最初の送信を開始できる。
- Archive Conversationは起動時にResumeしない。
- Archive解除後は手動の「再開」を押さず、最初の送信を開始できる。
- Sidebarの「再開」Actionは非表示にする。
- Backend Resume APIを互換性なく削除する必要はない。

### 8.2 Performance／Race Contract

- Server起動またはUI起動時に全Conversationを一括Resumeしない。
- 選択、最初の送信またはUnarchive時に必要なConversationだけを遅延自動Resumeする。
- CAS／Revision Conflictを既存Contractに従って処理する。
- 二重Tabまたは同時送信でActive Sessionを重複生成しない。
- Resume成功前にUser TurnをAppendしない。
- Archive中／Deleted Conversationを自動Resumeしない。
- Restart RecoveryでInterruptedとなった既存Turnを再生成または改竄しない。

実装方式はFrontend先行Resume、Server-side lazy ensureまたはBounded Combined Mutationのうち、既存Lifecycleを最も壊さず起動性能を保つ方式を選ぶ。方式選択理由をRecoveryへ残す。

### 8.3 Regression

- Restart後Active／Sessionなしから最初の送信成功。
- Unarchive後最初の送信成功。
- ArchivedのままではSession作成0。
- Double Tab／Revision ConflictでActive Session exactly one。
- SidebarにResume Buttonなし。
- Conversation／Branch／Regenerate／Stopの既存主経路Regression 0。

Recovery Index:

```text
docs/project/phases/phase_7/history/index/phase_7_post_manual_bounded_rework_p7_rw2_c_recovery_ja_<timestamp>.md
```

## 9. Package P7-RW2-D — Verification／Internal Review／Return

### 9.1 Verification

変更順にFocused Testを実行し、最終差分で次を行う。

```text
Backend focused citation/local corpus/conversation persistence tests
Frontend focused citation/sidebar/persistent conversation tests
Canonical mypy
Canonical Ruff format/check
Backend full pytest
Frontend typecheck/lint/test/build
```

既存Project内Test Temp／npm cache境界を使用する。成立した検証を理由なく再実行しない。

### 9.2 Internal Review

1 Cycleだけ実施する。観点は次に限定する。

- P7-CODEX-007〜009 Requirement-by-Requirement。
- 過去Evidence不変性。
- Current Turn Grounding。
- Resume Lifecycle／Race。
- API／SSE／Frontend Projection一致。
- Scope／Claim／Acceptance整合。

MaterialなCritical／Major／MVP Blockerを検出した場合だけ同Task内でBounded Reworkし、該当Focused Testを再実行する。非BlockingなUI Polish、製品化Hardeningまたは理論Finding探索を派生させない。

### 9.3 Return

最終Recovery IndexとExact Return Handoffを作成する。

```text
docs/project/phases/phase_7/history/index/phase_7_post_manual_bounded_rework_p7_rw2_d_final_recovery_ja_<timestamp>.md
docs/project/phases/phase_7/handoffs/phase_7_claude_post_manual_bounded_rework_exact_return_handoff_ja_<timestamp>.md
```

最大Claimは`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`である。User Manual再確認をPASSへ代行せず、Phase 7 Closureへ進まない。

## 10. Acceptance

### P7-RW2-ACC-001 — Citation Projection

Local CitationにSource Class／Path／Chunk ID／Document Digestが表示され、完全値を確認またはCopyできる。

### P7-RW2-ACC-002 — Citation Persistence

Reload／別Tab／Restart後も、同一TurnのCitation Identityが同一である。

### P7-RW2-ACC-003 — Historical Immutability

Document更新／削除後も、過去Turnの本文／Citation／Revision／Digestを改変しない。

### P7-RW2-ACC-004 — Latest Revision

同一Conversationの新TurnはCurrent Local Documentの最新Revisionを使用する。

### P7-RW2-ACC-005 — Deleted Source

削除済みLocal Factを、同一Conversationの過去HistoryだけからCurrent Factとして回答しない。

### P7-RW2-ACC-006 — Unsupported Citation

質問対象を支持しないProject Docsを、回答根拠のCitationとして表示しない。

### P7-RW2-ACC-007 — Lazy Resume

Restart後の非Archive Conversationは、Resume Buttonなしで最初の送信に成功する。

### P7-RW2-ACC-008 — Unarchive Resume

Archive解除後、Resume Buttonなしで最初の送信に成功する。

### P7-RW2-ACC-009 — Startup／Concurrency

起動時全件Resumeを行わず、二重TabでもActive Sessionが重複しない。

### P7-RW2-ACC-010 — Preserved Baseline

Local Corpus／Data Controls／Conversation／Citation／Branch／Regenerate／Stopの既存主経路にMaterial Regressionがない。

## 11. True Stop Condition

次の場合だけSTOPPED_SAFE Returnを作成して停止する。

- Data消失、過去Citation書換えまたはConversation Store破損を検出した。
- User `runtime_data/`、Project Root外、Git、Real Network等へ、許可されていないMaterial Mutationを実行した。
- P7-CODEX-007〜009の成立に新しいUser Decisionまたは外部Authorityが不可欠で、Project内Fixture／Test／Sourceでは進められない。
- Canonical Testが既存主経路のMaterial Regressionを示し、同Scope内で安全に原因を限定できない。

Read-onlyの軽微な操作ミス、Formatting、Test Fixture修正、既知の非Blocking Findingまたは進捗報告は単独Stop理由にしない。事実をRecoveryへ記録し、Scope内で自己修正して継続する。

## 12. Exact Next Action

UserのExact Start宣言受領後、P7-RW2-0から開始し、P7-RW2-DのExact Returnまで連結実行する。
