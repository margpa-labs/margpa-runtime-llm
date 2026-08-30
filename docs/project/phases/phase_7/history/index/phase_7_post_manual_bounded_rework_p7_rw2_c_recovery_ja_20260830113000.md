# Phase 7 Post-Manual Bounded Rework — Package P7-RW2-C Recovery（Lazy Auto-Resume）

```yaml
document_id: phase_7_post_manual_bounded_rework_p7_rw2_c_recovery_20260830113000
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 11:30:00 JST
active_contract: phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_ja_20260830101851.md
package: P7-RW2-C
finding: P7-CODEX-009
```

## 0. Recovery Index Pointer

前Package: [P7-RW2-B Recovery](phase_7_post_manual_bounded_rework_p7_rw2_b_recovery_ja_20260830111500.md)。次Package: P7-RW2-D Recovery（Verification／Internal Review／Return）。

## 1. 実装方式の選定（Handoff §8.2「方式選択理由をRecoveryへ残す」）

Handoff提示の3方式（Frontend先行Resume／Server-side lazy ensure／Bounded Combined Mutation）を比較し、**Server-side lazy ensure**を採用した。

```text
Frontend先行Resume:
  Frontendが2回のHTTP Round-tripを明示的に調整する必要があり、
  Double Tab時のResume競合をFrontend側でも意識する必要がある。
  既存/turns/stream APIのRequest／Response契約を変えずに済むが、
  呼び出し側の実装が増える。

Bounded Combined Mutation:
  Resume＋AppendをServer側1 Commitへ統合する新しいMutation種別が必要。
  既存のresume_conversation／append_user_turnという2つの十分に確立された
  CAS Mutationをそのまま再利用できず、Source Surfaceが最も大きい。

Server-side lazy ensure（採用）:
  generate_turn／generate_derived_turnの入口で、既存resume_conversation
  ／append_user_turnを2回の逐次Commitとして内部Orchestrationするだけで
  済む。Frontendの/turns/stream Request／Response契約は完全に不変
  （Bodyの形も、Success時のDetail形も変わらない）。既存主経路への影響が
  最小。
```

"既存Lifecycleを最も壊さず起動性能を保つ"という基準に対し、Server-side lazy ensureが最も低Risk・低Source Surfaceと判断した。

## 2. 実装（`persistent_conversation_service.py`）

```text
_lazy_resume_operation_id() / _lazy_resume_session_id()（新設、Module級）:
  Caller供給のidentities.append_operation_idをSeedとしたDeterministic
  SHA-512導出。同一Requestの再試行は同一Resume Operation IDに収束する
  （operation_was_appliedによる冪等性チェックが機能する）。

_ensure_active_session()（新設、Instance Method）:
  Conversation StateがACTIVEでない場合、または既にActive Sessionが
  存在する場合は何もしない（Archived／Deleted自動Resume 0、
  重複Session 0）。それ以外の場合だけresume_conversation()を呼ぶ。
  CONFLICTまたはINVALID_LIFECYCLE（並行Requestが既にResume済み）を
  検出した場合は例外を握りつぶさず、最新StateをRe-fetchして返す。

generate_turn() / generate_derived_turn()（既存Method、書き換え）:
  _recover_one()と同型のBounded CAS Retry Loop（最大2回再試行）へ
  変更。各試行でCanonical Stateを取得 -> _ensure_active_session() ->
  append_user_turn()／append_derived_turn()。CONFLICTを検出した場合
  だけRevisionをNoneへ戻し次の試行でRe-fetchする。
```

`recover_incomplete_conversations()`（起動時1回のInterrupted化Pass）自体は無変更——Handoff指示通り「起動時全件Resumeは行わない」を維持した。

## 3. Regression（Handoff §8.3全項目）

```text
新規Test（tests/unit/conversation/test_persistent_conversation_service.py）:
  test_lazy_resume_on_restart_allows_first_send_without_manual_resume
    -> Restart後Active／Sessionなしから最初の送信成功、旧Interrupted
       Turn／Sessionは無変更のまま確認。
  test_lazy_resume_on_unarchive_allows_first_send_without_manual_resume
    -> Unarchive後最初の送信成功。
  test_archived_conversation_creates_zero_sessions_and_still_denies_send
    -> ArchivedのままではSession作成0、送信はinvalid_lifecycleのまま拒否。
  test_double_tab_stale_revision_race_ends_with_exactly_one_active_session
    -> 同一Stale Revisionを共有する2つの送信（Double Tab相当）が、
       Active Session exactly oneへ収束することを確認。
```

Sidebar Resume Buttonの除去（Handoff §8.1）:

```text
frontend/src/components/Sidebar/ChatListItem.tsx:
  ChatListAction型からresumeを削除、Resume Menu Item（JSX）を削除。
frontend/src/i18n/translations.ts:
  persistentResume（ja/en）を削除。
```

既存主経路Regression確認（Handoff §8.3「Conversation／Branch／Regenerate／Stopの既存主経路Regression 0」）:

```text
frontend/src/App.test.tsx:
  「resuming a non-selected conversation…」Testを「archiving a
  non-selected conversation…」へ改名・付け替え（同一Bugを保護する
  Regression Testそのものは、Actionの種類に依存しないため保持）。
frontend/src/components/Sidebar/ChatListItem.test.tsx:
  Resume特有のAssertionを除去。「Active session有無でResume表示が
  切り替わる」Testは前提が消滅したため削除、他2 Testは名称・
  Assertionを整理して保持。
```

## 4. 全体検証

```text
uv run pytest -q                     -> 1934 passed, 7 deselected（P7-RW2-B基準から+4）
uv run mypy                          -> Success, no issues found in 526 source files
uv run ruff check .                  -> All checks passed
uv run ruff format --check .         -> 526 files already formatted

frontend: npx tsc --noEmit           -> エラーなし
frontend: npx eslint .               -> エラーなし
frontend: vitest run                 -> 29 files, 259 tests passed
frontend: npm run build              -> 成功（tsc --noEmit && vite build、
  src/margpa_runtime_llm/web/static/app.js／index.htmlを再生成）
```

## 5. Scope境界の遵守（Handoff §8.1「Server-side lazy ensure」の意図的な限定）

```text
起動時全件Resume: 実装していない（recover_incomplete_conversationsは無変更）。
選択時（Conversation一覧からのSelect／GET Detail）でのResume:
  実装していない。Handoff §8.2は「選択、最初の送信またはUnarchive時」を
  Lazy Resumeの候補として並列に挙げているが（"or"であり全実装の必須指定
  ではない）、Acceptance（P7-RW2-ACC-007/008/009）はいずれも「最初の
  送信成功」だけを要求しており、読取専用のGET／Select経路を書き込み
  Mutationへ変えることはSource Surfaceの不要な拡大かつ意図しない副作用
  （閲覧しただけでSessionが作られる）のRiskがあるため、意図的に「最初の
  送信」のみをTriggerとした。
Backend Resume API（POST /resume）: 削除していない（Handoff明示指示通り）。
既存Interrupted Turnの再生成／改竄: 行っていない（_ensure_active_session
  はSessionだけを扱い、Turnには一切触れない）。
```

## 6. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation:
  Backend: persistent_conversation_service.py（Source）、
    test_persistent_conversation_service.py（Test、4新規Test）
  Frontend: ChatListItem.tsx, translations.ts（Source）、
    ChatListItem.test.tsx, App.test.tsx（Test）
Root外Read/Write: 0
```

Exact next action: P7-RW2-D（Verification／Internal Review／Return）へ連結して進む。
