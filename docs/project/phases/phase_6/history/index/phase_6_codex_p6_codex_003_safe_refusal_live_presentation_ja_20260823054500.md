# P6-CODEX-003 Safe Refusal Live Presentation — Rework Complete

```yaml
document_id: phase_6_codex_p6_codex_003_safe_refusal_live_presentation
status: current_recovery_entry
phase: phase_6
work_unit: p6_codex_003_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 05:45:00 JST
```

## 発見（Rework着手前の実態確認）

```text
既存Live SSE経路（handlePersistentEvent／handleEphemeralEvent）は既に
knownMessageText()経由でCodeをMappingしていたが、knownServerMessagesに
Guardrail／Governance Reject Codeが1件も登録されておらず、未Mapping時の
Fallbackが「Generation was stopped by the Guardrail before starting.」等の
内部向け英語Descriptionに落ちていた（Raw Codeではないが、Fixed JA/EN Safe
Refusalでもない）。
さらに致命的だったのは、Guardrail／Governance RejectはAssistant Messageを
一切生成しないため（P6-ACC-042の要求どおり）、Persistent Conversationを
Reload／Resumeした瞬間、その拒否表示が跡形もなく消える（Turn自体は
failed状態でSidebarのRetryは出るが、拒否理由のPresentationは再構築
されない）ことを確認した——これがCodexの指摘する構造的Gapの実体だった。
```

## Exact Mutation

```text
Backend:
  Modified:
    src/margpa_runtime_llm/modules/runtime_observability/presentation/safe_refusal.py
      + is_safety_reject_code()（"guardrail_"／"governance_" Prefix判定）
    src/margpa_runtime_llm/modules/conversation/domain/models.py
      + ConversationTurn.failure_reason_code（Optional、新規Migration不要—
        既存JSON Blob Storageに新規Optional Fieldを追加するだけで、旧Rowは
        Noneへ自然Decode）
      + validate_state_shape()へ「failed以外はfailure_reason_code禁止」Rule追加
      + transition_turn()へfailure_reason_code引数追加
    src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
      + fail_generation()／_transition_terminal_or_generating()へ
        failure_reason_code引数追加
      + ERROR Event処理箇所でevent.data["code"]をfailure_reason_codeとして
        実際にfail_generation()へ伝播（従来は破棄されていた）
    src/margpa_runtime_llm/web/persistent_contracts.py
      + PersistentTurnResponse.failure_reason_code、_project_turn_citations
        付近のProjectionへ追加
  Created:
    tests/unit/conversation/test_persistent_conversation_service.py へ2 Test追加
      （guardrail Reject→failure_reason_code永続化確認、非Safety Failureは
        Noneのまま確認）
    tests/unit/conversation/test_conversation_domain.py へ1 Test追加
      （transition_turnがFAILEDのみfailure_reason_codeを保持、COMPLETEDでは
        破棄することを確認）

Frontend:
  Created:
    frontend/src/lib/persistentDetailProjection.ts
      （emptyMessage／knownMessageText／translatedServerMessage／
        detailToMessages／buildTurnActionsをApp.tsxから抽出——
        react-refresh/only-export-componentsを解消する副次効果込み）
    frontend/src/lib/persistentDetailProjection.test.ts（3 Test）
  Modified:
    frontend/src/App.tsx（上記関数をlibから import、重複定義削除）
    frontend/src/types.ts（PersistentTurn.failure_reason_code追加）
    frontend/src/i18n/translations.ts
      + safeRefusalMessage（JA／EN、safe_refusal.pyの固定文言と同一）
      + knownServerMessagesへGuardrail／Governance Reject Code 14件を
        safeRefusalMessageへMapping
      + isSafetyRejectCode()（is_safety_reject_code()のTS版、Prefix判定）
```

## 設計判断

```text
Schema Migration不要: conversations Tableはsnapshot_json BLOBへ全Domain
  Modelを直列化する方式（storage_format_version="sqlite-json-1"）のため、
  Default Noneの新規Optional FieldはALTER TABLE無しに追加でき、既存Row
  はNoneへ自然Decodeされる。STORAGE_FORMAT_VERSION自体は変更していない
  （非破壊的Additive Changeのため）。
Internal CodeとPresentationの分離: Backend側のerror Event `message`は
  引き続き内部向け英語Description（Developer Detail）のまま変更せず、
  User向けFinal Textは全てFrontendのknownMessageText（Single Presentation
  Mapper）が生成する。これはsafe_refusal.pyのDocstringが元々想定していた
  「Raw Codeは通常Chat Bodyに出ない、別途Developer Detail Channelのみ」
  という設計と整合する。
Prefix判定（固定List不採用）: is_safety_reject_code()／isSafetyRejectCode()
  は"guardrail_"／"governance_"のPrefixで判定する。bootstrap側の両Moduleが
  将来新しいreason_codeを追加しても、本Mapperを都度修正しなくてもFail-safe
  にSafe Refusalへ倒れる。
Assistant Authority混入0の維持: Reload時の再構築Bubbleはdetail Response
  由来のTurn.failure_reason_codeから都度Client-side合成するだけであり、
  chatHistoryRef（次回GenerationのContextに使われる会話履歴）には一切
  追加しない——Persisted Assistant Messageでもない。
```

## Validation

```text
Backend: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider --basetemp=.venv/.t/f
  1408 passed, 5 deselected in 62.03s（新規3 Test含む、回帰0）
Ruff: All checks passed!
Mypy: Success: no issues found in 423 source files
Frontend: typecheck PASS／lint PASS（Warning 0）／
  Test Files 23 passed (23) / Tests 190 passed (190)（新規3 Test含む）／
  build PASS
```

## Acceptance Cross-check

```text
P6-ACC-041（Raw Error CodeでなくJA／EN Safe Refusal）: PASS
  （Live／Reload両経路でknownServerMessagesの14 CodeがsafeRefusalMessageへ
    Mapping、Unit Testで直接検証）
P6-ACC-042（Safe RefusalをAssistant Authority／次Context化0）: PASS
  （failure_reason_codeはTurnのみに保持、Assistant Message非生成を維持、
    Reload再構築もClient-side合成のみ）
P6-ACC-043（Reload／Resumeで安全表示再構築）: PASS
  （本Reworkの主目的、Unit Test 3件で直接検証）
```

## Next Exact Route

P6-CODEX-005（Four Component Identities）へ進む。Domain層は6-G-WU-002で
実装済みのため、比較的Tractableな次項目として先に着手し、その後
P6-CODEX-001／002（Live Judge／Repair Integration）という最大規模の
Reworkへ進む。
