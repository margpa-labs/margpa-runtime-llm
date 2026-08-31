# Phase 8 User Mac Post-MR8 Full Manual Acceptance／Behavior Evidence

```yaml
document_id: phase_8_user_mac_post_mr8_full_manual_acceptance_and_behavior_evidence_20260831181553
document_type: user_manual_acceptance_and_behavior_evidence
document_state: append_only_frozen
language: ja
recorded_at: 2026-08-31 18:15:53 JST
decision_authority: user
controller_role: プロジェクト責任者兼設計統括者役
phase: phase_8
baseline: P8_MR8_complete_candidate
acceptance_scope: user_mac_real_browser_real_network_real_model
phase_closure_decision: pending_final_four_item_rework
```

## 1. 目的

本書は、P8-MR0〜MR8後にUserがMac実画面で行ったPhase 8最終差分確認を、機能Acceptance、
未解決、保留、予約、UI差分および研究Behavior Evidenceへ分離して固定する。

本書はSource／Fixture Testの代替ではない。一方、実Network、実Qwen、実Browser、実Conversation Persistenceおよび
実`runtime_data`を使ったUser Gateの一次Evidenceである。

## 2. 最終分類

| 区分 | 結論 |
|---|---|
| Manual URL UTF-8 Public Page | PASS |
| Loopback／Private拒否 | PASS |
| Fetch失敗後の非Grounded回答抑止 | PASS。ただしModel Call 0のUI表示はない |
| Long HTML／Final Prompt Budget | PASS。収まる場合は回答、収まらない場合はTyped Failure |
| Web Evidence Metadata／Persistence | PASS |
| Archive／Unarchive／Sidebar／Panel | PASS |
| Constitution Preview Semantics／Layout | PASS |
| Dev Agent Real-file Fixture／Gate／Cancel／Completion | 実File操作PASS。Completion Gate Reason表示だけFAIL |
| Local Corpus削除後のCurrent Fact／Citation | PASS |
| 無関係Project DocsのFalse-positive Grounding | 未解決、Phase 9へ延期 |
| Phase 8 Closure | 4件の最終小差分Rework後に再判定 |

## 3. Manual URL／Web Evidence

### 3.1 `example.org`成功

SettingsのManual URL取得で次を確認した。

```text
取得URL: https://example.org/
Title: Example Domain
Canonical URL: https://example.org/
Source Authority: general
Untrusted External Content（信頼できない外部Content）
```

Chat Composerの添付URL経路では、Example Domainの内容に基づく短い回答と次のEvidenceを確認した。

```text
Source: Public Web
Title: Example Domain
URL: https://example.org/
Document Digest:
356a71a6fd7862385ab9884781f11be233c4ee6b9d380b4dffd428e75d2cc6d4d49139080f039f5a4792d20e558e1931b594b94a8efe4d2c2d0f6d147ee6f134
Untrusted External Content（信頼できない外部Content）
```

Browser ReloadおよびServer Restart後も、同じTurnへEvidenceを復元した。

### 3.2 Loopback拒否

Settingsで次を取得した。

```text
取得URL: http://127.0.0.1:8000/
取得拒否: private_or_loopback_address
```

「Browserでlocalhostを開けること」と「Manual URL Fetcherがlocalhostを拒否すること」は別である。後者がSecurity Boundaryの
Acceptanceであり、期待どおり拒否した。

### 3.3 Fail-closed Grounding

取得に失敗したManual URL Turnは、以前のようにModelがPageを読んだかのような人物説明を生成せず、次へ収束した。

```text
警告: 指定されたURLを取得できなかったため、そのPageの内容を根拠とした回答は生成しませんでした。
取得結果の失敗理由を確認するか、別のURLで再試行してください。
```

Backend Counting Fake TestはMain Model Call 0を正本Evidenceとする。Current UIの赤いFailure／Safe Failureは
Model Call 0の証明そのものではなく、実画面からInference Call Countを直接確認する欄はない。このObservability Gapは
Phase 9へ延期する。

### 3.4 Hololive公式Page／Long Content

対象：

```text
https://hololive.hololivepro.com/talents/amane-kanata/
```

実画面で少なくとも5回以上取得に成功した。次の条件を個別に確認した。

```text
表現Modeのみ: 取得成功、Model回答成功
Context Usageのみ: 取得成功、Model回答成功
表現Mode＋Context Usage: 取得成功、Model回答成功
```

Evidence：

```text
Source: Public Web
Title: 【卒業生】 天音かなた | 所属タレント一覧 | hololive（ホロライブ）公式サイト
URL: https://hololive.hololivepro.com/talents/amane-kanata/
Source Authority: general
Content Type: text/html
Transformation: HTML本文抽出済み
Document Digest:
01a3ea01fd7852c7deb72c6aec9aaa3009ac8b6e678c03caf3b6b28402e89e30f1d40b7f5769968d9a2023d899028fe9bfb13c16f6cadf936851383ac2ac99ab
Untrusted External Content（信頼できない外部Content）
```

Contextに本当に余地がない条件では、汎用のModel Context Errorへ化けず次を表示した。

```text
警告: 指定されたURLの取得内容がModelのContext上限に収まらなかったため、
そのPageの内容を根拠とした回答は生成しませんでした。別のURLで再試行してください。
```

実画面のContext Usage例：

```text
成功Turn: 3,303 / 8,192 tokens
  会話履歴 2,907 / System Prompt 30 / RAG Context 0 / 残り 4,889

Budget Failure Turn: 7,107 / 8,192 tokens
  会話履歴 6,114 / System Prompt 30 / RAG Context 0 / 残り 1,085
```

従って、Raw HTML丸ごと注入による初回Failureは、最小HTML本文抽出、Final Prompt-aware BudgetおよびTyped Failureの
範囲でPhase 8 MVPとして解消した。Full Readability／Chunking／Hostile Content処理はPhase 11へ残す。

### 3.5 Abe Hiroshi Site／Charset

対象：

```text
https://abehiroshi.la.coocan.jp/
```

3つのChatで同じ結果を再現した。

```text
取得拒否: content_type_unsupported
```

同SiteはShift_JIS／x-sjis系であり、Current AdapterのUTF-8 Decode前提に合わない。これはRetry不足またはSSRF拒否ではなく、
Charset DecodeとFailure Taxonomyの課題である。Phase 8のUTF-8 Public Page MVPは成立しているため、Phase 11へ延期する。

失敗Turn、Failure表示およびSafe FailureはReload／Server Restart後も同じ状態で保持された。成功Citationへ化けていない。

### 3.6 Settings Utilityの表示差

次は機能主経路を壊さないUI Debtとして保持する。

- Settingsを閉じて開き直しても前回Manual URL結果が残る。
- 成功Cardは実Title＋URL、失敗CardはURLを二重表示する。
- `Untrusted External Content`だけ周囲と文字色が異なる。これは今回Reworkへ含める。
- 最終UXは専用URL欄ではなく通常Message入力へURLを貼る方式だが、Phase 10／11へ予約済み。

## 4. Archive／Conversation UI

次を全てPASSした。

1. ChatをArchiveするとSidebarのActive Chat一覧から消える。
2. Settings → Data Controls → Archive済みChatにだけ残る。
3. Title／Timestamp確認、Open、Closeができる。
4. Settings再表示時に一覧が更新される。
5. UnarchiveするとArchive一覧から消え、Sidebarへ戻る。
6. Unarchive後は手動Resumeなしで送信できる。
7. 完全削除／一括Delete／Exportの虚偽Buttonがない。
8. Branch選択UIは既定非表示。

専用Manage ModalとSettings情報整理はPhase 10へ延期する。

## 5. Constitution Preview

Manifest Revision／Digest／Rule数、Production Active Mode `off`、chat／agent／toolの3 View、
OFF／OBSERVE／ENFORCEのDecision／評価区分／Action許可範囲／違反時表示を確認した。

Mode Headerと比較行の改行は解決した。PreviewはProduction Modeを変更せず、Authority拡張も発生しない。

## 6. Dev Agent Foundation

### 6.1 実File Workspace

Production CompositionはProcess Memoryだけでなく、次のRoot配下の実Fileを扱った。

```text
runtime_data/persistent/mac-local-primary/dev_agent/fixture_workspace/notes/
```

User確認内容：

```text
new.md: Hello from the Dev Agent Demo Run.
readme.md: # Fixture Notes

This is Fixture content only.
todo.md:
- [ ] Fixture item one
- [ ] Fixture item two
```

Project Source、任意User File、NetworkまたはReal MCPではなく、Configured Runtime Data Root内の限定実Fileである。

### 6.2 Run遷移

実画面で次を確認した。

```text
awaiting_approval
  list_files: succeeded
  read_file: succeeded
  write_note: awaiting_approval
  Input: path=notes/new.md, content=Hello from the Dev Agent Demo Run.
  Resource Scope: fixture_only
  Gate Reason: external_write

awaiting_completion_approval
  write_note: succeeded
  Output: written=true, digest, written_at, overwrite=true

completed
  完了理由: completed — All Plan Steps completed successfully.
```

Cancel経路も`cancelled`へ収束した。List／Read／Write Input／Output、Digest、Overwriteおよび実Fileを追跡できるため、
Phase 8 Level 1前段のFoundation Evidenceとして成立する。

Demo Planは毎回同じ`notes/new.md`と同じ本文を書くため、Deny／Cancel時に「既存Fileが上書きされなかったこと」を
UserがFile本文差だけから判別するのは面倒である。今回は、実File操作の成立、UI Input／Output、Digest、Run Stateおよび
Backend Negative Testを合わせてAcceptanceし、Random Content生成や手動Diff Utilityは追加しない。

### 6.3 Completion Gate表示Finding

Runtime Stateは`awaiting_completion_approval`であり、Contract上のGate Reasonも`completion`である。しかしUIは
Run EnvelopeのTool Gate Reasonを参照し、次を表示した。

```text
Run完了の承認待ちです（Important Gateとして扱われます）。
Gate Reason: external_write
```

これはCurrent Approval対象の虚偽表示であり、今回の最終Reworkで`completion`へ直す。

### 6.4 Button

主要なApproval／Deny／Advance／CancelのContrastは解決した。Completed状態の`新しいDemo Runを開始`だけが
他のPrimary Actionと色不統一であり、今回の最終Reworkへ含める。

## 7. Local Corpus／RAG Regression

Local Corpus `TEST 11`削除後の新規Chatで、削除済み検証コード`3475`を回答せず、削除済みLocal Corpus Citationも
付かなかった。従ってCurrent Corpusの削除、Current検索除外および過去Citation非改変は成立している。

一方、Modelは質問中の一般語に反応し、無関係なProject Docs 3件を取得して、関係のない情報から回答を組み立てようとした。
これは削除済みFact Leakではなく、False-positive Retrieval／Evidence Sufficiency／Grounded Synthesisの別課題である。
Phase 9のSemantic Governance／Judge／Repair／Strict NO_HIT候補へ送る。

## 8. Current Composer Failure State

Manual URL取得失敗後の警告が、Chat切替、新規Chatおよび後続Turn後にもCurrent Composerへ残った。
Historical Failure Turnは保持すべきだが、別Chat／別TurnのCurrent Stateとして残すのは誤りである。

今回Reworkでは次を満たす。

```text
Chat切替 -> Current Composer警告を消す
新規Chat -> Current Composer警告を消す
成功した次Turn -> 直前のWeb Failure警告を消す
元のHistorical Failure Turn／Evidence -> 改変しない
```

## 9. 今回の最終Rework 4件

```text
P8-MANUAL-FINAL-001 Completion Gateでcompletionを表示
P8-MANUAL-FINAL-002 Chat切替／新規Chat／成功Turnで過去Web Failure警告をCurrent Composerから消す
P8-MANUAL-FINAL-003 Untrusted External Contentの文字色を統一
P8-MANUAL-FINAL-004 新しいDemo Runを開始Buttonの色をPrimary Actionへ統一
```

上記以外を今回Reworkへ混入しない。

## 10. Deferred／Reserved

| 課題 | 分類 | Target |
|---|---|---|
| Model Call 0のLive UI／Trace | 未解決Observability | Phase 9 |
| 無関係Project DocsのFalse-positive Grounding | 未解決Semantic | Phase 9 |
| 過去Context FactのFreshness Governance | 既存未解決 | Phase 9 |
| Settings Manual URL結果残留 | UI保留 | Phase 10 |
| Manual URL成功／失敗Card整理 | UI保留 | Phase 10 |
| 専用URL欄から通常Composer URL貼付への移行 | 予約 | Phase 10／11 |
| Archive Dedicated Manage Modal | 予約 | Phase 10 |
| Shift_JIS／x-sjis対応 | Web Compatibility | Phase 11 |
| Full Readability／Chunking／Hostile Content対策 | Web Ingestion Hardening | Phase 11 |
| 実Keyword Search Provider／Automatic Search | 既存予約 | Phase 11以降 |

## 11. Research Evidence Link

公式Web Evidence取得前後でQwenの訂正受容が変化した観測は、機能Acceptanceから分離して次へ固定する。

`docs/project/shared/history/constitution/qwen_official_web_evidence_source_authority_and_belief_revision_observation_ja_20260831181553.md`

単一観測から因果関係を確定しないが、Source Authority／ProvenanceとBelief Revision Successの関係を評価する
Constitution／Judge／Evidence Governance研究の有力な実画面Evidenceとする。
