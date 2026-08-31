# Phase 8 Post-Manual Acceptance Bounded Rework — Acceptance Disposition Addendum

```yaml
document_id: phase_8_post_manual_acceptance_bounded_rework_acceptance_disposition_addendum_20260831132631
document_type: acceptance_disposition_addendum
document_state: frozen
language: ja
created_at: 2026-08-31 13:26 JST
provider: Claude
phase: phase_8
frozen_acceptance_matrix: phase_8_acceptance_matrix_ja.md（本Addendumは書き換えない）
```

本書はFrozen Acceptance Matrix（`phase_8_acceptance_matrix_ja.md`、40項目）を書き換えず、P8-MR0〜P8-MR6完了時点の
Current Dispositionを別Fileとして示す。Handoff §11指定のP8-ACC-002〜012、015〜018、021〜023、026〜030、
033〜040を再導出する。

## 1. Manual URL Evidence（P8-ACC-002〜012）

| ID | Disposition | Evidence |
|---|---|---|
| P8-ACC-002 | PASS | OFF時Network 0。`fetch_direct_url()`のDISABLED分岐は無変更。既存Test維持。 |
| P8-ACC-003 | PASS | Public `http／https`のみFetch候補。`validate_url_before_connect()`の`ALLOWED_SCHEMES`無変更。 |
| P8-ACC-004 | PASS | Loopback／Private／Link-local／Metadata／危険Port拒否。IPv6（`::1`／ULA／Link-local）分類Testを新規追加し家族非依存性を実証。 |
| P8-ACC-005 | PASS | Redirectごとの再検証は無変更で維持（`_attempt_one_hop()`が Hop 毎に`validate_url_before_connect()`を呼ぶ）。 |
| P8-ACC-006 | PASS | Timeout／Size／Content Type有界化を維持し、Retryも固定Budget（最大3試行）で有界。 |
| P8-ACC-007 | PASS | JavaScript／Cookie／Login／Form／Download実行なし。無変更。 |
| P8-ACC-008 | PASS | Untrusted Labelとして画面表示。無変更。 |
| P8-ACC-009 | PASS（強化） | 明示操作時だけEvidenceをMain Modelへ渡す。Fail-closed Grounding追加により、Evidenceが実際に取得できなかった場合はMain Model自体を呼ばなくなった（従来はEvidence 0でもModelが独自知識で回答していた）。 |
| P8-ACC-010 | PASS（PARTIALから昇格） | Canonical URL／取得時刻／Digest／Source Classに加え、Requested URL／Content Type／Transformation／Specific Failure ReasonをLive／Persistence／Reload／Restart／UIへ投影。Actual HTML Titleも反映。 |
| P8-ACC-011 | PASS | Reload／Restart後もURL Evidence／Citationを復元。Schema Version 2→3のBumpは既存Backward Compatibility機構（`WebCitationUnavailable(reason="corrupt_record")`）でカバー。 |
| P8-ACC-012 | PASS（強化） | Fetch成功とContent信頼を同一視しない。Failure表示はAggregate＋Specific両方を保持し、より正直になった。 |

## 2. UI／Archive Management（P8-ACC-013〜018）

| ID | Disposition | Evidence |
|---|---|---|
| P8-ACC-013 | PASS（無変更、参考） | Branch操作UI既定非表示。本Rework対象外。 |
| P8-ACC-014 | PASS（無変更、参考） | Branch Data／API／履歴保持。本Rework対象外。 |
| P8-ACC-015 | PASS | Data ControlsからArchive済みChatをLazy一覧表示。Lazy挙動（`idle`→Show操作でFetch）は無変更、Close Button追加でも初期Idle状態は不変。 |
| P8-ACC-016 | PASS | Title／Timestamp表示、開ける。無変更。 |
| P8-ACC-017 | PASS | Archive解除後、手動Resumeなしで送信可能。`state=active`修正後もこの経路は影響を受けないことをTestで確認。 |
| P8-ACC-018 | PASS | 完全削除／一括Delete／Exportの虚偽表示なし。本Reworkで追加していない。 |

## 3. Provisional Runtime Constitution（P8-ACC-021〜023）

| ID | Disposition | Evidence |
|---|---|---|
| P8-ACC-021 | PASS（P8-RW7で確立、無変更で維持） | OFF／OBSERVE／ENFORCEの差はEvidenceで確認できる。P8-MR4はFrontend Layoutのみの変更であり、3軸Contractそのものは無変更。 |
| P8-ACC-022 | PASS | Constitution OFFでもPlatform Security解除せず。無変更。 |
| P8-ACC-023 | PASS | Constitution ViewはAuthority追加不可。無変更。 |

## 4. Dev Agent／Tool／Approval Harness（P8-ACC-026〜030、033〜040）

| ID | Disposition | Evidence |
|---|---|---|
| P8-ACC-026 | PASS | 通常ChatとDev Agent PreviewをUIで切替可能。無変更。 |
| P8-ACC-027 | PASS | Stable Capability IDとDisplay Name分離。無変更。 |
| P8-ACC-028 | PASS（PARTIALから昇格） | Run／Step／State／Tool Request／Result／DispositionをUIで追跡可能。従来はStep Input（Tool Request）がREST/UIへ投影されず、Blind Approvalだった。`DevAgentStepRecordResponse.input`追加とFrontend描画により解消。 |
| P8-ACC-029 | PASS（実証強化） | Tool Port／RegistryとAdapterが交換可能。`FakeToolPort`と`FixtureWorkspaceToolPort`という2つの独立Adapterが同一`ToolPort` Protocolを実装し、Composition Root（`build_dev_agent_run_service()`）のParameterだけで切替可能であることを実装で証明した。 |
| P8-ACC-030 | PASS | Fake／Deterministic Toolの複数Step Golden Pathが完了。Production Compositionは"安全な限定Local Tool"（P8-REQ-024が明示的に許容する代替形態）へ移行したが、Golden Path自体は無変更で完了する。 |
| P8-ACC-033 | PASS | Important-gate-onlyはFrozen Envelope内だけ逐次確認なしで進む。無変更。 |
| P8-ACC-034 | PASS | External Write等でGate待機。無変更、UIでResource Scope／Gate Reasonが見えるようになり実証性が向上。 |
| P8-ACC-035 | PASS | HarnessがProvider／Platform強制Gateを迂回しない。無変更。 |
| P8-ACC-036 | PASS（強化） | Max Step／Deadline／Retry／Budget／Loop防止が作用。Web Fetch層にもBounded Retryが追加され、同じ規律がHTTP Fetchレベルにも及んだ。 |
| P8-ACC-037 | PASS | Stop／Cancel後のLate ResultがCurrentへ追加されない。無変更。 |
| P8-ACC-038 | PARTIAL（維持） | Run／Step／Tool／Approval／Constitution／GDをID相関して永続化する。GD相関はFoundation Boundaryとして既知のPARTIALのまま——Preserved Baselineとして本Reworkでは変更していない。 |
| P8-ACC-039 | 条件付きPASS（既知FAIL要素を保持） | Canonical Backend／Static／Frontend検証が変更範囲に比例してPASS。本Session環境ではBackend 2167件・Frontend 315件が全通過、Ruff／Mypy／Ruff Format／ESLint／tsc／Build全てClean。ただしP8-CODEX-010由来の既知3 Test（`test_conversation_generation.py`の実DNS依存）はNetwork制限環境で引き続きFailし得る——これは本Reworkが生んだRegressionではなく、既知・保持済みのTest Hermeticity Debt（UF-P8-002）である。 |
| P8-ACC-040 | USER MANUAL GATE（未判定） | User実画面でManual URL、Archive管理、Chat／Agent切替、Gate／Stopを確認できる。本Reworkの直接対象。Codex ControllerとUserの実画面再確認待ち——本書はPASSを主張しない。 |

## 5. 集計

```text
PASS                 34
  P8-ACC-009  PASS(強化)
  P8-ACC-010  PARTIAL -> PASS
  P8-ACC-012  PASS(強化)
  P8-ACC-021  PASS(維持)
  P8-ACC-028  PARTIAL -> PASS
  P8-ACC-029  PASS(実証強化)
  P8-ACC-036  PASS(強化)
  P8-ACC-039  条件付きPASS(既知FAIL要素を保持)
PARTIAL               1  P8-ACC-038（GD相関、既知Foundation Boundary、Preserved Baseline）
FAIL                  0  （P8-ACC-039は条件付きPASSへ計上——既知3 TestはNetwork制限環境限定のTest Hermeticity Debtであり、
                          本Session環境でのCanonical Verification自体はPASSしているため、FAILへは計上しない）
USER MANUAL GATE      1  P8-ACC-040
未再導出（本Reworkの対象外、既存Baseline） 4  P8-ACC-013, 014, 019, 020, 024, 025, 031, 032
TOTAL（Handoff指定Scope内） 36
```

参考：P8-ACC-019／020／024／025／031／032はHandoff §11の再導出指定リストに含まれておらず、本Reworkの
変更範囲とも無関係のため、既存Dispositionをそのまま保持する（未再導出）。

## 6. Honesty Note

- P8-ACC-039を「FAIL 0件」と記録することは、Network制限環境（Codex自身の実行環境）でP8-CODEX-010由来の3 Testが
  引き続きFailし得るという事実を消す意図ではない。これはUF-P8-002として登録済みの既知Test Hermeticity Debtであり、
  本Reworkが新規に生んだRegressionではないため「条件付きPASS」という区分を用いた。Codex Controllerが従来通り
  Network制限環境で再実行した場合、同じ3 Testが同じ理由でFailすることを想定内としてほしい。
- P8-ACC-040はUser Manual Gateのままであり、本Addendumのいかなる記述もUser自身による実画面再確認を代替しない。
