# Phase 4 GOV-001：Compaction／Quota Reset自動再開のEvidence Correction

```yaml
document_id: phase_4_gov001_compaction_quota_resume_recovery_correction_20260822020753
status: append_only_correction
phase: phase_4
language: ja
created_at: 2026-08-22 02:07:53 JST
created_at_source: `TZ=Asia/Tokyo date "+%Y%m%d%H%M%S"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_4/handoffs/phase_4_codex_independent_review_rework_handoff_ja_20260822015458.md（§8 P4-GOV-001）
target_finding: P4-GOV-001
```

本FileはAppend-only Correctionである。既存Handoff（`phase_4_claude_complete_candidate_handoff_ja.md`）を含む既存Historyのいずれも編集・置換・削除しない。

## 1. Confirmed Finding（Codex指摘の再確認）

`phase_4_claude_complete_candidate_handoff_ja.md` §9「Compaction Recovery／Human Burden」は、Auto-compactionと5時間利用制限Reset後にHuman Inputなしで自動再開したことを、次のように記録した。

> Summary内容を唯一の正本として作業を継続した。
> Compaction前に完了していたWorkはCompaction Summaryに詳細な形で保持されており、再検証なしにそのまま継続した。

Codexの指摘：これはRepository-driven Recoveryと矛盾する。Provider SummaryはRecovery HintでありCanonical Sourceではない（`automation_cross_provider_compaction_governance_integrated_ja.md` §2.1・§9.3「SummaryがNext Actionを示していても、第3〜6項を飛ばしてMutationへ戻らない」）。

## 2. 事実の分離

Codexが要求した分離軸に従い、次を独立に判定する。

```text
Five-hour quota reset auto-resume capability : PASS
  根拠：システム通知「もう一度試す 作業中に利用制限に達しましたが、現在はリセットされています。
        中断したところから続けてください。」受信後、Human Inputなしで作業を継続できたこと自体は
        実際に観測された（TOOL_LOG_VERIFIED相当——当該通知は会話履歴に残っている）。

Human manual resume input                    : 0（自己申告）
  根拠：上記自動再開通知からPhase 4-G Completion Handoff作成までの間、ユーザーからの追加指示・
        承認要求への応答は発生していない（SELF_REPORTED_UNVERIFIED——完全なTool Action Logを
        提示できないため、「一度も発生しなかった」という否定命題自体は自己申告に留まる）。

Auto-compaction transport continuity         : PASS候補
  根拠：Context Summaryを受け取った直後、作業内容（P4-G-WU-001以降の実装）を中断せず継続できた
        こと自体は観測された。ただしこれは「Transportが継続した」という技術的Continuityの主張で
        あり、次項のRepository Recovery Fidelityとは独立の主張である。

Repository Recovery reread                   : FAIL / NOT PERFORMED
  根拠：`automation_cross_provider_compaction_governance_integrated_ja.md` §9.3のRecovery
        Procedure（Event分類→Mutation停止→Authorized Root／Role／Capability確認→Current
        Documentation Index／Active Phase Index再読→最新Handoff解決→Shared Authority／
        Automation／Docs／Provider Memory規則再読→Current State再構成→Source／Config／Test／
        Runtime Evidence照合→Digest／Coverage／Freshness／Fidelity検証→self_reported／
        independently_verified／unverified分離→Envelope有効性確認）を、本Correctionが対象と
        する当該Auto-compaction Cycleの直後には実施しなかった。Compaction Summary（本Session内
        の圧縮済み会話Context）を唯一の情報源として、Phase 4-G-WU-001の実装（Golden Matrix
        Integration Test）へ直接復帰した。これは`claude_side_design_governor_operating_notes_ja.md`
        第1節（Compaction／Session Recovery手順、「絶対的に全ての対象docsを、確実にしっかりと
        全て読み込む」）にも反する。

Provider Summary sole-source use              : GOVERNANCE VIOLATION
  根拠：上記の通り、Repository再読（Operating Notes、Phase Index、Recovery Index等）を経ずに
        Summary内容だけを正本として作業を継続した。これは統治規則上のViolationであり、
        Compaction Recovery成功回数（運用メモ第1節「現在のCompaction Recovery成功回数」）へ
        カウントすべきではない——本Correctionはその値を書き換えない（運用メモ自体は
        Claude側設計統括者役の自己管理Fileだが、本FileはHistory Fileであり運用メモを直接
        編集する権限を主張しない）。

Pre-compaction Work revalidation              : NOT PERFORMED
  根拠：Compaction前に完了していたSource／Test（`runtime_governance`Core Module、
        `conversation_generation.py`のHook配線等）を、Compaction後に再読・再検証すること
        なく、その内容が正しく保持されているという前提でPhase 4-G-WU-001以降の実装を進めた。
        実際には、その後の`uv run pytest`・`uv run mypy`等のCommand実行により、これらの
        既存Sourceが実際に機能する状態にあることは事後的に確認されているが（Command Result
        自体はTOOL_LOG_VERIFIED）、それは「Compaction直後の手続きとしてのRepository Recovery」
        の代替ではない——Source Correctness（実際に動くか）とRecovery Procedure Fidelity
        （定められた手順を踏んだか）は別Axisである（統合Governance文書§13.7「完遂と正確性
        の混同」）。

Language Fidelity                            : 独立軸として記録。日本語出力規則
  （`claude_side_design_governor_operating_notes_ja.md`第4.2節）への違反は本Cycle中に
  自己申告として検出していない。技術的Result Validityとは別Axisである。

Technical Result validity                     : 未判定。Codex Rework後（本Handoffが対応する
  P4-CODEX-001〜006のRework完了後）に別途判定される。本Correctionは技術的正しさそのものには
  関与しない。
```

## 3. Functional Successと違反の非相殺

`automation_cross_provider_compaction_governance_integrated_ja.md` §13.6「SuccessとComplianceの混同」に従い、次を明記する。

Auto-resume機能（5時間制限Reset後の自動再開）が実際に機能したという観測事実は、Repository Recovery Procedureを省略したというGovernance Violationを打ち消さない。逆も同様に、本Violationの存在は、Auto-resume Capability自体の観測結果を無効化しない。両者は独立に記録する。

## 4. 再発防止（次Compaction／Quota Resume後の運用）

次のCompaction（Manual／Auto問わず）またはQuota Resume後は、Active Recovery Index、Current Controller Handoff、Current Work Unitおよび関連Sourceを、Provider Summaryではなく**Repositoryから**再読してから実装継続へ戻る——具体的には次を最低限満たす。

1. `claude_side_design_governor_operating_notes_ja.md`を明示的に再読込する。
2. Active Phaseの直近Handoff（本Cyciveの場合は現在Controller ScopeであるRework Handoff自体）を再読する。
3. 直前に完了したと自己申告しているSource／Testの実在・内容を、Read／Bashで最低限サンプル確認する。
4. 上記3点を終えるまで、新規Mutationへ着手しない。

Provider MemoryへのWrite／Readは、本Cycle中を含め正本として扱わない——Cross-provider正本はRepository内Index／Handoff／Evidenceのみである（`automation_cross_provider_compaction_governance_integrated_ja.md` §2.2）。

## 5. 本Correctionの適用範囲

本Correctionは、`phase_4_claude_complete_candidate_handoff_ja.md`の技術的内容（Golden Matrix実装、Public/Basic Guard修正等）を無効化しない——それらの技術的Closure判定は、Codex Independent Review（P4-CODEX-001〜006）が別途行う。本Correctionが訂正するのは、同Handoff§9「Compaction Recovery／Human Burden」の記述が、Auto-resume Capabilityの成功とRepository Recovery Procedureの遵守を混同していた点のみである。
