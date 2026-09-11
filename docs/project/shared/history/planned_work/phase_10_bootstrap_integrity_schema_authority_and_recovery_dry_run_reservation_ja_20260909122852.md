# Phase 10 Bootstrap Integrity／Schema／Authority／Recovery Dry-run予約

```yaml
document_id: phase_10_bootstrap_integrity_schema_authority_and_recovery_dry_run_reservation_20260909122852
document_type: planned_work_reservation_addendum
document_state: reserved
target_phase: phase_10
recorded_at: 2026-09-09 12:28:52 JST
decision_authority: user
implementation_authorized: false
append_only: true
```

## 1. 決定と位置づけ

既存の`phase_10_project_neutral_controller_recovery_handoff_bootstrap_index_reservation_ja_20260909075701.md`で予約した、Provider-neutralな2種類のBootstrap IndexをPhase 10で正式化する際、次の5項目を必須候補として扱う。本案は有効性が高いため採用候補とするが、Exact SchemaとGate値はPhase 10の要件定義で確定する。

対象Index:

- `project_controller_design_governor_bootstrap_index_ja.md`
- `designer_implementer_bootstrap_index_ja.md`

## 2. Bootstrap Index自体の腐敗検知

Indexが存在するだけでは、リンク先や内容がCurrentであることを保証できない。少なくとも次のIntegrity Metadataを持たせる。

- `last_verified_at`: 最後に機械検証または承認済み検証を行った時刻。
- `source_revision`: Index生成・更新時に参照したSource RevisionまたはRevision集合。
- `digest`: Index本文および必要に応じて参照ManifestのContent Digest。
- `owner`: 内容の管理責任を持つRole／Authority。Provider名や一時Task IDだけに固定しない。
- `coverage`: どの必須カテゴリ、Source範囲およびRole Viewを含むか。

時刻だけを鮮度の根拠にせず、Revision、Digest、CoverageおよびAuthorityを併用する。Digest不一致、参照Revision消失、Coverage低下またはOwner不明は黙ってCurrent扱いせず、`stale`、`digest_mismatch`、`coverage_incomplete`、`authority_unknown`等へ分離する。

## 3. Machine-checkable Coverage

Bootstrap Indexが最低限復旧すべきカテゴリを機械可読なCoverage Manifestとして定義する。

```text
authority
role
docs
recovery
evidence
current_position
```

検査は少なくとも次を含む。

- 必須カテゴリの欠落。
- Link切れ、参照不能、Root外参照および循環参照。
- StableからHistoryだけを誤ってCurrentとして指す逆流。
- RoleごとのMandatory Reading不足。
- Current Position／Roadmap候補が存在する場合の未収録。
- 対象が存在しない新規Projectでの、正直な`not_found`／`not_applicable`保持。

単なるLink数やFile数をCoverageと呼ばず、カテゴリ、Source Identity、Revision、必須／任意、除外理由および検証結果を対応付ける。

## 4. Hybrid Handoff JSON Schema

Development Agent間のHybrid Handoffで使うJSON Execution Contractを、Phase 10で正式なVersioned JSON Schema候補へ昇格する。

送信前に次を検出する。

- Duplicate Key。
- 必須Field欠落。
- Enum外の値。
- 型不一致、未知Schema Versionおよび無効なNested Shape。
- Authority、Scope、Stop、Reporting等の相互矛盾。

一般的なJSON ParserがDuplicate Keyを後勝ちで黙って潰す挙動を許容せず、Strict Parseで送信前Rejectする。Schema validationは自然言語のIntentを置換せず、自然言語／XML Boundary／JSON Contract間のConflictも別Gateで検出する。

## 5. Conflict precedenceは文書種別や時刻ではなくAuthorityで解決

新しいTimestamp、StableというFile名、Handoffという文書種別だけで自動的に優先させない。少なくとも次の意味Authorityを保持する。

```text
User Decision
> accepted correction／accepted addendum
> active accepted handoff
> stable baseline
> historical evidence／superseded material
```

ただし単純な固定順位だけでなく、対象Scope、Decision Authority、Acceptance状態、Supersession、Revisionおよび明示的な例外を照合する。新しい低Authority文書が古いUser Decisionを上書きしない一方、正式に受理されたCorrectionは訂正対象の古い記述をSupersedeできるようにする。解決不能Conflictは推測せず保存し、必要なAuthorityへEscalateする。

## 6. Recovery Dry-run

新規Task／新規Contextへ、原則として次の最小Packageだけを渡すDry-runを行う。

```text
Bootstrap Index 2枚
+ Current Handoff 1枚
```

この入力だけから、次を再構築できるかを検証する。

1. 対象Projectと現在位置。
2. 自身のRoleと責任範囲。
3. 有効なAuthorityと禁止事項。
4. Current Work、次Actionおよび停止条件。
5. Evidence／Recovery／Returnの正しい導線。

Dry-runでは無関係なDocsを追加投入して成功させない。最小Packageだけでは不足する場合、何が不足したかをCoverage Gapとして記録し、無制限な全Docs読込で隠さない。Index内の厳選Mandatory Linkを辿るModeを別に検証する場合も、許可されたLink集合外へ探索を拡張しない。

成功条件は、Role名を復唱できることではなく、Project位置、Authority、次Action、True Stopおよび非権限事項を相互矛盾なく再構築できることである。

## 7. Phase 10正式化時の受入候補

- 2 IndexのIntegrity Metadataが埋まり、Digest／Revision再検証が可能。
- 6必須Coverageカテゴリの欠落・Link切れを機械検出できる。
- Hybrid HandoffがStrict JSON Schema Gateを通り、Duplicate Keyを拒否する。
- ConflictがTimestampや文書種別ではなくMeaning Authorityで解決される。
- 最小3 ArtifactのRecovery Dry-runでRole／Authority／Current Position／Next Actionを復旧できる。
- Failure時は不足を正直に示し、Authority生成やCurrent状態の捏造をしない。

## 8. 非目標

本予約だけではSchema実装、Index更新、既存Docs統合、Task作成、Dry-run実行、Git操作またはPhase 10開始を許可しない。Phase 10の正式要件定義で工数と既存Portable Package設計を照合してから実施する。
