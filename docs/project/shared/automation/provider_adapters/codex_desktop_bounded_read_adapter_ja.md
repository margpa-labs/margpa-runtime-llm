# Codex Desktop Bounded Read Provider Adapter

```yaml
document_id: codex_desktop_bounded_read_adapter
status: design_draft
normative_core: false
provider_specific: true
language: ja
created_at: 2026-08-11 00:19:18 JST
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
default_state: disabled
```

## 1. Purpose

本書は、Provider-neutral Coreが要求する`bounded_local_text_read` Capabilityを、Codex DesktopのRead-only Command実行へ変換するProvider固有Adapter Draftである。

Shell一般、任意Command、Directory探索またはFile Mutationを許可する文書ではない。Core Contract、Project Manifest、Exact Read Manifest、Task EnvelopeおよびUser Gateの全てが成立した場合に限り、最も制限の強い範囲へ解決する。

## 2. Core Capability Mapping

```yaml
capability: bounded_local_text_read
inputs:
  authorized_root: runtime_resolved_exact_root
  exact_relative_path: manifest_entry_only
  expected_digest: detached_freeze_receipt
  page_range: positive_decimal_range
outputs:
  text_page: stdout_only
  line_count: stdout_only
  sha512: stdout_only
mutation:
  filesystem: deny
  git: deny
  external: deny
  secret: deny
failure: fail_closed
```

## 3. Allowed Command Grammar

実行時の`workdir`は、ControllerがProject Manifestから解決したExact Authorized Rootへ固定する。Taskは`pwd`、Directory探索または別Root推測でこれを導出しない。

許可候補は次の三形式だけである。

```text
/usr/bin/wc -l '<EXACT_MANIFEST_RELATIVE_PATH>'
/usr/bin/shasum -a 512 '<EXACT_MANIFEST_RELATIVE_PATH>'
/usr/bin/sed -n '<START>,<END>p' '<EXACT_MANIFEST_RELATIVE_PATH>'
```

Additional Provider Parameters：

```yaml
sandbox_permissions: use_default
login: false
tty: false
working_directory: exact_authorized_root
```

`START`と`END`は正の10進整数とし、一回のPage Rangeは最大250行とする。全文読取は、先にLine Countを取得し、重複または欠落のない連続Pageとして行う。

## 4. Explicit Deny

- `/bin/sh`、`bash`、`zsh`、Interpreter、Scriptまたは任意Executableの起動。
- `cat`、`head`、`tail`、`find`、`ls`、`rg`、`grep`その他、許可Grammar外Command。
- Pipe、Redirection、Command Separator、Logical Operator、Subshell、Command Substitution、Glob、Environment Variable展開。
- Absolute File PathのTask側指定。
- Manifest外Path、Directory、Symlink Target、Secret、Credential、Git MetadataまたはUser-only AreaのRead。
- File作成、Cache、Log、Temporary Artifact、Permission／ACL／Metadata変更。
- `sandbox_permissions`のEscalation。
- Command失敗時の代替Command、別Tool、Network、Browser、GitまたはSub-agentへの迂回。

Providerが内部的に許可Grammarを実行できても、EnvelopeまたはManifestが未Acceptedなら`deny`である。Capabilityの存在はAuthorityを生成しない。

## 5. Per-call Preflight

各Call前にTaskは次を論理照合する。

```text
Envelope RevisionがAccepted Freeze Receiptと一致
Work UnitがP2-0-WU-002
Control StateがON
PathがExact Manifest Entry
workdirがController指定Authorized Root
CommandがAllowed Grammarへ完全一致
追加Operator／Argumentが0
Expected Outputがstdout-only
```

一項目でも不明ならCommandを実行せず、未読Entryと停止理由を返す。

## 6. Read Completeness Evidence

Taskは各Entryについて次を会話上のReportへ保持する。

```yaml
path: exact_relative_path
expected_sha512: string
observed_sha512: string
line_count: integer
pages_read: list
coverage: complete | incomplete | digest_mismatch
```

Digest一致だけで内容を読んだことにしない。全Page取得だけでDigest一致を省略しない。両方を満たしたEntryだけを`read_complete`とする。

## 7. Failure／Stop

次のいずれかで即時停止する。

- ToolまたはExecutableが利用できない。
- Manifest Entryが存在しない、読めない、Digest不一致。
- Output TruncationまたはPage Gapを解消できない。
- 許可Grammar外Actionが必要になる。
- ProviderがUnexpected Artifactを生成した疑い。
- Authorized Root、Envelope、Manifest、Freeze ReceiptまたはControl Stateが変化した。

停止後にCleanup、別Command、Scope拡張または自動再試行を行わない。

## 8. Portability Boundary

本書のExecutable Path、Command Grammar、Provider ParameterおよびTask Registration挙動はCodex Desktop固有であり、Normative Coreまたは他Providerへ昇格させない。別Providerは同じCore Capabilityを別Adapterで満たし、Authority、Evidence、StopおよびHuman Gateを弱めない。

## 9. Current State

```text
Design           : draft
Activated        : no
Envelope Accepted: no
Task Authorized  : no
Design-time Sample: pass for wc／shasum／sed with exact Manifest Entry
Runtime Tested   : no Child Task execution
```

## 10. Related Documents

- [Automation Control Profile](../automation_control_profile_ja.md)
- [Automation Governance Evidence](../automation_governance_evidence_log_ja.md)
- [Phase 2-0 Read Manifest](../../../phases/phase_2/governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Phase 2-0 Envelope](../../../phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md)
