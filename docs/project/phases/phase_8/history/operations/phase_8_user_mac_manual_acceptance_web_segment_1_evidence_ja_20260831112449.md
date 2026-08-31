# Phase 8 User Mac Manual Acceptance — Web Segment 1 Evidence

```yaml
document_id: phase_8_user_mac_manual_acceptance_web_segment_1_evidence_20260831112449
document_type: user_mac_manual_acceptance_incremental_evidence
document_state: append_only_interim
language: ja
recorded_at: 2026-08-31 11:24:49 JST
test_owner: User
controller: Codex_project_controller
source_test_sheet: phase_8_user_mac_manual_acceptance_test_sheet_ja_20260831072507.md
phase_8_closure: not_claimed
remaining_manual_tests: pending
```

## 1. Scope

Userが分割送信したPhase 8実画面確認のうち、初期状態とManual Web／Direct URL経路だけを一区切りとして保存する。
本書は途中Evidenceであり、P8-ACC-040全体のPASS、Phase 8 Closureまたは後続Test完了を主張しない。

## 2. Test 1 — 初期状態／既存Chat

User判定：`全て問題なし`。

したがって、今回確認対象だった通常Chat、Web検索既定OFF、Branch UI既定非表示および既存Chatの手動Resume不要は、
この実画面CycleではPASSとして保持する。詳細表示文言はUserから追加Findingなし。

## 3. Test 2 — `https://example.org/`

### 3.1 Settings Direct URL Fetch

User実表示：

```text
取得結果を表示しています。

https://example.org/
https://example.org/ · general
Untrusted External Content（信頼できない外部Content）

<!doctype html><html lang="en"><head><title>Example Domain</title> ...

検索が完了しました。
```

判定：

- Public URLの実Fetch：確認できた。
- Raw HTML表示：確認できた。
- Untrusted Label：確認できた。
- SuccessをTrustedへ偽装：再現なし。

### 3.2 Main Model Evidence／Citation

User質問に対する表示：

```text
題名: Example Domain
概要: このドメインはドキュメンテーション例用に使用され、操作には適しません。
詳しくはhttps://iana.org/domains/exampleを参照してください。
```

Web Evidence：

```text
Source: Public Web
Title: https://example.org/
URL: https://example.org/
Document Digest:
356a71a6fd7862385ab9884781f11be233c4ee6b9d380b4dffd428e75d2cc6d4d49139080f039f5a4792d20e558e1931b594b94a8efe4d2c2d0f6d147ee6f134
Untrusted External Content（信頼できない外部Content）
```

UserはURL Copy、Digest Copy、ReloadおよびServer Restart後のEvidence保持を確認した。

判定：`https://example.org/`のManual URL → Main Model Evidence → Citation → PersistenceはPASS。

## 4. Loopback拒否とFixture Searchの区別

Userは`http://127.0.0.1:8000/`を次の2経路へ入力した。

### 4.1 Web検索（Manual）

```text
Fixture Providerによる固定Sampleです。実Search APIには接続していません。

検索語句
http://127.0.0.1:8000/

Fixture Web Search Result
https://www.python.org/doc/ · general
Python is a programming language ... (Fixture content, not fetched live.)
```

これは入力Queryに関係なく固定Sampleを返すFixtureであり、Loopback URLを実取得した結果ではない。
General Web Search完成を意味しない。

### 4.2 URL取得（Manual）

```text
取得URL
http://127.0.0.1:8000/

http://127.0.0.1:8000/ · unknown
取得拒否: private_or_loopback_address
```

判定：Loopback拒否はPASS。Network Fetch成功として表示されていない。

## 5. Hololive公式URL — Raw HTMLとContext Budget Failure

対象：

```text
https://hololive.hololivepro.com/talents/amane-kanata/
```

User質問：

```text
天音かなたってどんな人？
```

Chat結果：

```text
入力がModelのContext上限を超えました。
```

Settings Direct URL Fetch自体は成功し、WordPress PageのRaw HTMLを先頭から末尾まで表示した。Userが別途確認した
実Contentは約8.9万文字で、概算2.5万〜3.5万Token級と報告された。Current Main Model Effective Context 8192へ
Raw HTMLをそのまま注入する設計では、必要な本文より大量のHTML／CSS／JavaScript／Attribute／URLがBudgetを消費する。

判定：

```text
Fetch: PASS
Raw Preview: PASS
Main Model Evidence Injection: FAIL / context_budget_exceeded
```

このEvidenceは、将来のNormalizer、Readable Text Extractor、Script／Style除去、Chunking、Evidence Selectionおよび
Budgeted Injectionが必要である理由として保持する。

## 6. UI Scope差 — 専用URL欄と通常入力

Userの当初イメージは、通常のMessage ComposerへURLを貼り付け、必要な時に同じTurn内で読む方式だった。
Current実装は専用Manual URL入力欄を使う。機能の成立自体とは分離するが、期待UXとの差として保留する。

```text
Current: 専用Manual URL欄
Desired candidate: 通常入力へ貼ったURLを、明示的なUser Action／Modeの下でCurrent Turn Evidenceとして取得
Decision: 今回は保留。Phase 10 UI／Phase 11 Governed Web Runtimeで再設計候補。
```

## 7. Abe Hiroshi Public URL — 取得失敗と非Grounded回答

対象：

```text
https://abehiroshi.la.coocan.jp/
```

User質問：

```text
阿部寛ってどんな人？
```

Model出力：

```text
阿部寛（あべ のり）は、日本の俳優で、テレビドラマや映画に出演しています。
主な作品には『クレイジーサンデー』や『サザエ・サンデイ』などがあります。
彼は、タレントとしての活動に加え、政治的な活動にも関わっている人物です。
```

Web Evidence：

```text
取得拒否: url_rejected
```

判定：FAIL。

- Public URL Contentを取得できていない。
- 取得失敗にもかかわらずModel生成が継続した。
- 回答は取得PageにGroundされず、読み、作品および政治活動について根拠のない内容を出力した。
- Chat EvidenceはAggregate Reason `url_rejected`だけを表示し、具体的な拒否／失敗理由を失っている。

## 8. 原因診断の訂正

Controllerは当初、Codex実行環境の`socket.getaddrinfo()`で`dns_resolution_failed`を再現し、これをUser Runtimeの
Exact原因と断定した。しかし同じCodex診断環境では他の外部DomainもDNS解決できず、Network制限環境の影響を分離できない。
したがって次のように訂正する。

```text
確定:
  User RuntimeでPublic URL取得が失敗した。
  Chat Projectionは具体理由をurl_rejectedへ集約して失った。
  取得失敗後もModelが非Grounded回答を生成した。

未確定:
  User Runtimeの具体原因がDNS失敗、TLS、HTTP Transport、Content-Type、Timeoutその他のどれか。

撤回:
  dns_resolution_failedをUser Runtimeの確定原因としたController断定。
```

この原因未確定自体がObservability Gapである。

## 9. Segment判定

| 項目 | 判定 |
|---|---|
| Test 1 初期状態 | PASS |
| Example Domain Direct Fetch | PASS |
| Example Domain Chat Evidence／Citation／Persistence | PASS |
| Loopback拒否 | PASS |
| Fixture Searchが実Searchでない表示 | PASS／仕様どおり |
| Hololive Raw HTML Fetch | PASS |
| Hololive Main Model Evidence | FAIL — Context上限超過 |
| Abe Hiroshi Public URL安定取得 | FAIL |
| Fetch失敗後のGrounding | FAIL |
| Exact Failure Reason表示 | FAIL |
| P8-ACC-040全体 | 未判定 — 後続Manual Test継続中 |

本SegmentだけでPhase 8 Closureへ進まない。
