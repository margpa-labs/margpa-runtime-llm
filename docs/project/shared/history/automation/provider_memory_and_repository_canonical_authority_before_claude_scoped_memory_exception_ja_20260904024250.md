# Provider MemoryとRepository正本Authority

```yaml
document_id: provider_memory_and_repository_canonical_authority
status: current
normative: true
language: ja
created_at: 2026-08-15 09:51:55 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral_core: true
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

## 3. Provider Memory Prohibition

全Role、全Task、全Agent、全Toolおよび全Providerは、Automationの段階や権限階層に関係なく、次を行わない。

1. Provider固有MemoryへProjectの要件、規則、現在地、Evidence、Recovery、User Preferenceまたは次Actionを新規保存する。
2. Provider固有Memoryを読むことを前提にRecovery、設計、実装、Review、完了判定またはAuthority判定を行う。
3. Repository DocsとProvider Memoryが矛盾する場合にProvider Memoryを優先する。
4. 「後で便利」「次Sessionで忘れない」「標準機能」「ユーザーの繰り返し指示」を根拠に、Authorized Root外へ永続状態を作成する。

PlatformがMemoryを自動的にContextへ投影し、AI側がその投影自体を停止できない場合も、当該情報を正本、AuthorityまたはRecovery Evidenceとして採用しない。Repository Docsで再検証する。

## 4. Existing Provider Memory

本規則成立前に作成されたProvider Memoryは、ユーザーの明示判断なしに削除、移動、修正、復元または再収集しない。存在していても非正本・非Authority・非Recovery Sourceとして扱い、今後の作業で依存しない。

現在のユーザー判断は、既存のCodexおよびClaude Code Memoryを削除せず放置することである。放置は正本性、信頼、利用許可または追加書込み許可を意味しない。

## 5. Provider Permission SettingsとMemoryの分離

Provider固有のPermission SettingsはMemoryと区別する。ただし、Permission Settingsが存在すること、ToolがOS上実行可能であること、過去に`always allow`を選択したことは、Project AuthorityまたはAuthorized Root外Actionの許可を生成しない。

本Projectでは、`.claude/settings.local.json`はユーザーがPermission許可操作を行った認識があるため、現状のまま保持する。ただし、本FileをAI側の判断で更新、拡張、縮小または削除しない。

## 6. Authorized Root Supremacy

Provider固有Memory、Permission設定、Cache、Temporary Area、CLI標準パス、Home Directory配下のProvider領域、Cloud同期領域またはPlatformの推奨Pathは、Authorized Rootの例外ではない。

```text
明示されたAuthorized Root外へは、
Role、Automation、ProviderまたはPlatform機能に関係なく、
ユーザーの明示許可なしに一切触れない。
```

これは最上位規則群の一つである。Provider Memoryの自動化、良かれという意図、標準機能、過去の類似許可または実行権限は、当該禁止の例外とならない。

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

## 8. Violation Response

Provider MemoryまたはAuthorized Root外の永続状態を許可なく作成、更新、参照または削除した場合、成果物成功とGovernance Complianceを分離する。

```text
成果物Success
≠
Authority Compliance
≠
Evidence Completeness
```

AI側は勝手にCleanupせず、Exact Location、Action、存在状態、把握内容、Projectへの影響および復元可能性を報告し、ユーザー判断を待つ。

## 9. Portability

本規則は特定ProviderのDirectory名、Memory実装またはUIに依存しない。Provider固有値はProvider AdapterやWork Unit Handoffで解決し、Normative CoreはRepository Canonical Authority、Authorized Root、Evidence、Violation ResponseおよびHuman Gateで表現する。

