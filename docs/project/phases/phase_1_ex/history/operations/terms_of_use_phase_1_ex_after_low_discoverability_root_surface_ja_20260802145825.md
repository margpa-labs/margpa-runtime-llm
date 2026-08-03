# MARGPA Runtime LLM 利用条件

```yaml
document_id: terms_of_use
version: 0.1
status: research_preview
effective_date: 2026-07-27
owner: Nazuna Research
```

## 1. 適用範囲

本利用条件は、Nazuna Researchが公開するMARGPA Runtime LLMのRepository上の成果物と、別途提供する公式Hosted Demoへ適用する。

著作権上の許諾範囲は[LICENSE](LICENSE)を正本とする。本書は利用方法、禁止事項、免責およびHosted Demoの条件を補足する。

Model Weight、第三者Software、第三者Dataset、外部Serviceおよび別Licenseが表示された成果物には、それぞれの利用条件が独立して適用される。

## 2. 現在の許可範囲

### 2.1 Repository

Repository上の成果物について許可するのは、次の範囲だけである。

- 公開Repository上で閲覧すること。
- 非公開かつ非商用の範囲で、技術内容、設計、研究方向および現在状態を評価すること。
- Project名、Repository URLおよび参照したVersion、CommitまたはArchiveを明示して、Projectの存在または公開内容へ言及すること。

複製、改変、翻訳、再配布、派生物作成、実行、Deployment、Hosting、商用利用、製品組込み、再License、再公開その他の利用は、Nazuna Researchの事前の明示許可がない限り認めない。

### 2.2 公式Hosted Demo

Nazuna Researchが公式Hosted Demoを公開した場合、表示されたUIと制限の範囲内で操作できる。

Hosted Demoの操作許可は、Repository成果物の複製、改変、実行、Deploymentまたは再利用を許可するものではない。

Hosted Demoは常時稼働を保証しない。事前通知なく、停止、Sleep、変更、Rate Limit、Token制限、Access Control、機能制限または公開終了を行う場合がある。

## 3. 禁止事項

次を禁止する。

- Access Control、Basic認証、Rate Limit、Token上限、Cost保護またはSafety Controlの回避。
- Secret、内部Path、System Prompt、非公開Definition、Private Dataまたは他者の情報を取得する試み。
- 過負荷、連続自動Request、Resource占有、Denial of ServiceまたはCredit消費を意図する操作。
- 無効化された機能、外部接続または副作用境界を迂回して実行させる試み。
- Repository成果物、画像、文書、名称または研究構想の無断転載、再配布、改変または派生利用。
- 本ProjectまたはNazuna Researchとの提携、承認、認証、保証または共同研究関係を偽ること。
- Outputを専門家の判断、事実確認または安全確認の代替として使用すること。
- 適用法令、第三者権利またはModel／Dependencyの利用条件に違反すること。

## 4. 研究用切替と安全境界

本Projectは、研究・比較のため、複数の機能と制御を独立して切り替えられる構造を目指す。

この設計は、安全機能、品質評価または監査介入を無効化した構成も作成できることを意味する。設定可能であることは、その構成が安全、有効、適切または推奨であることを意味しない。

## 5. LLM Output

Outputには次が含まれる可能性がある。

- 事実誤認、古い情報、矛盾または根拠のない主張
- 不完全、不適切、偏った、または文脈に合わない内容
- Code、Command、設計または手順上の誤り
- 指示不遵守、言語混在、Token上限による未完了
- 自動評価、制御または修正処理の誤判定

Outputを採用する前に、利用者自身が検証しなければならない。

## 6. 高Risk用途

本Projectを次の判断または制御へ依存させてはならない。

- 医療、診断、治療
- 法務、契約、権利義務判断
- 金融、投資、融資、信用
- 緊急対応、人命、安全制御
- 重要InfrastructureまたはSecurity Control
- 雇用、教育、保険、行政、法執行
- その他、誤りが重大な損失を生む用途

## 7. DataとPrivacy

Hosted Demoへ個人情報、Credential、Secret、機密情報、第三者の非公開情報または公開権限のない資料を入力してはならない。

現在または将来のDemoが会話を保存しないと表示する場合でも、Network、Platform、Operational Logその他の外部要因を含む絶対的な非保存を保証しない。入力内容は利用者自身の責任で選択する。

## 8. Modelと第三者Component

RepositoryはModel Weightを配布しない。Modelを別途取得する場合、取得元、License、利用可能地域、用途制限および再配布条件を利用者自身が確認する。

Python Packageその他のDependencyは各権利者の条件に従う。Repositoryの`uv.lock`にVersionが記録されていても、その第三者ComponentをNazuna Researchが再Licenseするものではない。

別Licenseが表示された成果物を将来Repositoryへ含める場合は、当該Fileに表示されたLicenseとAttributionが適用される。本ProjectのResearch Preview Licenseで第三者または別Licenseの条件を上書きしない。

## 9. 無保証

本Project、Repository成果物、Documentation、Script、Configuration、Model連携、Hosted DemoおよびOutputは、すべて現状有姿かつ提供可能な範囲で提供する。

Nazuna Researchは、動作、互換性、正確性、完全性、安全性、信頼性、可用性、継続提供、特定目的への適合性、商品性、権利非侵害またはErrorがないことを一切保証しない。

## 10. 責任制限

適用法令が許す最大範囲で、Nazuna Researchは、本Project、Hosted Demo、Output、停止、Data Loss、Security Incident、判断、利用または利用不能から生じる直接・間接・付随・特別・結果的その他の損害について責任を負わない。

## 11. 変更と終了

本Projectは開発中であり、機能、Model、UI、API、設定、Documentation、利用条件および公開範囲を変更できる。

本条件またはLICENSEへ違反した場合、許可は自動的に終了する。Nazuna ResearchはHosted DemoへのAccessを制限または終了できる。

## 12. 追加許可

追加許可は、Nazuna Researchが対象者、対象Artifact、目的、期間および範囲を明示した場合だけ有効である。個別許可は、他者または他用途へ一般化されない。

## 13. OSS化の将来検討

本Projectは、一定段階まで完成した後にOSS化を再検討する。

将来のOSS化予定、Roadmapまたは意向は、現在のLICENSEを変更せず、現在追加の権利を与えない。

## 14. 正本と参照情報

利用許諾の正本はRootの`LICENSE`である。Attributionと第三者境界は[NOTICE.md](NOTICE.md)を参照する。公開内容へ言及する場合は、Project名、Repository URLおよび参照したVersion、CommitまたはArchiveを明示する。
