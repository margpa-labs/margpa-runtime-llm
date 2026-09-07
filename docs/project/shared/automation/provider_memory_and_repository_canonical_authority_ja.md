# Provider MemoryとRepository正本Authority

```yaml
document_id: provider_memory_and_repository_canonical_authority
status: current
normative: true
language: ja
created_at: 2026-08-15 09:51:55 JST
last_updated_at: 2026-09-04 02:42:50 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral_core: true
claude_scoped_exception: memory_file_and_project_dot_claude_allowed_noncanonical
```

## 1. Purpose

本書は、Codex、Claude Codeその他Provider固有のLocal Memory、Auto Memory、Project Memory、Session間Memoryまたは不可視の状態を、Document-driven Developmentの正本、Recovery Source、AuthorityまたはHandoffの代替としないための共通契約である。

## 2. Canonical Source of Truth

本Projectの状態、要件、設計、権限、禁止、現在地、Evidence、RecoveryおよびHandoffの正本は、明示的にAuthorized Root内へ配置したRepository Documentationだけとする。

```text
Repository内のCanonical・Shared・Phase・History・Index・Handoff・Evidence
  = 正本候補

Provider固有Memory・Session間Memory・Local Cache・暗黙状態
  = 正本ではない
  = Authorityを生成しない
  = Recovery完了のEvidenceにならない
```

## 3. Default Provider Memory Prohibition

全Role、全Task、全Agent、全Toolおよび全Providerは、Automationの段階や権限階層に関係なく、次を行わない。

1. Provider固有MemoryへProjectの要件、規則、現在地、Evidence、Recovery、User Preferenceまたは次Actionを新規保存する。
2. Provider固有Memoryを読むことを前提にRecovery、設計、実装、Review、完了判定またはAuthority判定を行う。
3. Repository DocsとProvider Memoryが矛盾する場合にProvider Memoryを優先する。
4. 「後で便利」「次Sessionで忘れない」「標準機能」「ユーザーの繰り返し指示」を根拠に、Authorized Root外へ永続状態を作成する。

PlatformがMemoryを自動的にContextへ投影し、AI側がその投影自体を停止できない場合も、当該情報を正本、AuthorityまたはRecovery Evidenceとして採用しない。Repository Docsで再検証する。

### 3.1 Claude Code限定例外（User Decision 2026-09-04）

Claude Codeに限り、次の二対象の作成・読取・更新・保持を許容する。

```text
1. Claude Code Providerが本Projectへ対応付ける単一の`MEMORY.md`／`Memory.md`
2. Project Root直下の`.claude/**`
```

この例外はProvider機能の実効利用と、同一逸脱への反復Correction Cost削減を目的とする。Claude CodeはRoutineに利用してよく、その都度Userへ確認・報告しない。Codexその他Roleは原則として内容を読まず、削除・修正・Cleanup・監査・正本利用を行わない。

対象は引き続き非正本、非Authority、非Evidence、非Handoff、非Recovery Sourceである。User最新指示、Active HandoffまたはRepository Docsと矛盾する場合は、常にそれらを優先する。

Project `.claude/`は`.gitignore`対象のままとし、`git add -f`、Unignore、Stage、CommitまたはPush対象にしない。単一Memory File以外のRoot外領域、他Provider Memory、他Project Memoryその他未許可対象への例外は生成しない。

## 4. Existing Provider Memory

本規則成立前に作成されたProvider Memoryは、ユーザーの明示判断なしに削除、移動、修正、復元または再収集しない。存在していても非正本・非Authority・非Recovery Sourceとして扱い、今後の作業で依存しない。

現在のユーザー判断は、既存のCodex Memoryを削除せず非正本として放置することである。Claude Codeについては第3.1節の単一Memory Fileを、非正本のまま作成・読取・更新・保持してよい。これはClaude以外のProvider Memory利用許可を意味しない。

## 5. Provider Permission SettingsとMemoryの分離

Provider固有のPermission SettingsはMemoryと区別する。ただし、Permission Settingsが存在すること、ToolがOS上実行可能であること、過去に`always allow`を選択したことは、Project AuthorityまたはAuthorized Root外Actionの許可を生成しない。

本Projectの`.claude/settings.local.json`を含むProject Root直下`.claude/**`は、第3.1節のClaude Code限定例外に含まれる。Permission Settingsが存在または更新された場合も、それ自体からProject Authority、Git Authority、Network AuthorityまたはRoot外Action Authorityを生成しない。

## 6. Authorized Root Supremacy

Provider固有Memory、Permission設定、Cache、Temporary Area、CLI標準パス、Home Directory配下のProvider領域、Cloud同期領域またはPlatformの推奨Pathは、原則としてAuthorized Rootの例外ではない。唯一のCurrent例外は第3.1節のClaude Code二対象である。

```text
第3.1節の単一Claude Memory Fileを除き、明示されたAuthorized Root外へは、
Role、Automation、ProviderまたはPlatform機能に関係なく、
ユーザーの明示許可なしに一切触れない。
```

これは最上位規則群の一つである。第3.1節に列挙した二対象以外では、Provider Memoryの自動化、良かれという意図、標準機能、過去の類似許可または実行権限は、当該禁止の例外とならない。

## 7. Provider BootstrapとHandoff

ProviderまたぎのRecoveryは、次の順序で行う。

```text
Repository内Provider Bootstrap Index
  -> Repository内Handoff
  -> Repository内Canonical・Shared・Phase Docs
  -> Exact Source / Test Inventory
  -> In-band ACK
```

Provider Memoryを読んだ、過去Sessionを覚えている、またはLocal Permissionが残っていることでRecovery完了としない。

Claude Codeは第3.1節のMemoryを作業補助として利用できるが、そこから得た状態はRepository Handoff／Source／Testで再検証する。Memory利用可能性によって上記Recovery順序を省略しない。

## 8. Violation Response

第3.1節の二対象以外のProvider MemoryまたはAuthorized Root外永続状態を許可なく作成、更新、参照または削除した場合、成果物成功とGovernance Complianceを分離する。

```text
成果物Success
≠
Authority Compliance
≠
Evidence Completeness
```

AI側は勝手にCleanupせず、Exact Location、Action、存在状態、把握内容、Projectへの影響および復元可能性を報告し、ユーザー判断を待つ。

## 9. Portability

本規則のCoreは特定ProviderのDirectory名、Memory実装またはUIに依存しない。第3.1節はUserが選択したProject-local Provider Adapter例外であり、CoreのCanonical Authority、Evidence、Violation ResponseおよびHuman Gateを弱めない。

## 10. Historical Non-retroactivity

2026-09-04以前のProvider Memory Incident／Violationは、当時の規則に基づくHistory Evidenceとして保持する。第3.1節を遡及適用し、過去のFailure判定を削除・変更・軽減しない。

## 11. Claude MemoryのProject内配置と共同管理（2026-09-04 23:03 JST追記）

User許可により、第3.1・4・6節の単一Memory限定とCodex不干渉を、以下の範囲だけ更新する。他Provider・他Project・その他Root外への許可は増やさない。

- 実体は `docs/project/shared/claude_memory/`。`MEMORY.md`と参照先の補助メモを含む、このProject専用のMemory一式とする。
- Claude側の既存読込場所 `/Users/yukitakagi/.claude/projects/-Users-yukitakagi-Documents-pseudo-root-99-ps-Main-Creating-Objects---20260219-MARGPA-RUNTIME-LLM-margpa-runtime-llm/memory` は、上記実体へのシンボリックリンクとする。外部変更の今回の許可は、この場所の移転・リンク設置だけである。
- Claudeは既存読込PathまたはProject内実体から、Routineな読取・作成・更新をしてよい。Codexもこの実体の読取・更新をしてよい。同時編集を避け、相手の変更を上書きしない。Project `.claude/`の既存許可・Cleanupしない扱いは維持する。
- `claude_memory/`と`.claude/`はGit除外を維持し、強制追加・Stage・Commit・Pushしない。Cleanup時も消さない。Git外なので、別PCへの移行やバックアップでは明示的に含める必要がある。
- Memoryは短い注意事項と正本への参照を中心とし、要件・権限・現在地・Handoff・結果Evidenceの代替にしない。最新User指示／Active Handoffと矛盾する古いMemoryで、許可済み作業を止めたりScopeを変更したりしない。正本にも矛盾があればUser意図との整合を確認する。
- 必要なMemory更新のたびに許可を取り直したり、全Docsを読み直したり、大量の記録を複製したりしない。機密情報・認証情報は保存しない。
- Constitution研究に用いる場合、変更され続けるMemoryと、採取日時・対象内容を特定した挙動Evidenceを分ける。Memoryの存在だけで遵守・改善を証明したことにしない。正本／History／Handoffのappend-only規則は不変。

移転時に既存11ファイルをSHA-512全件一致で保持し、その後`MEMORY.md`に今回の扱いだけ追記した。元Pathから実体の読取とリンク解決、Git除外を確認した。Claude自身の自動読込は未確認であり、通知後にClaude側で確認する。Source・Test・実モデル・Git履歴操作は対象外。

Memoryが索引と補助ファイルで構成される点は[Claude Code公式Memory説明](https://code.claude.com/docs/en/memory#storage-location)を参照。今回のProject固有権限は公式機能から推定せず、User許可に基づく。
