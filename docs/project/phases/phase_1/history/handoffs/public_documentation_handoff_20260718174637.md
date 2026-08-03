# 対外向けDocs作成者役 引き継ぎ

- 文書ID: `public_documentation_handoff`
- 状態: `waiting_for_publication_phase`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: 将来の対外向けDocs作成者役担当タスク
- 正本言語: 日本語
- 共通引き継ぎ: [common_project_handoff_20260718174637.md](common_project_handoff_20260718174637.md)

## 1. 役割

- GitHub README
- Setup
- Architecture説明
- Runtime Governance説明
- Model Download手順
- Model配置手順
- Audit Log仕様
- SHA-512検証手順
- Sample Config説明
- License／Attribution
- 匿名化Sample Log

## 2. 言語方針

日本語を正本とする。

技術識別子、Model ID、License正式名称等だけ英語を保持する。

英語資料を参照する場合も、日本語で意味を説明し、元資料へのLinkを付ける。

英語版が必要になった場合は、日本語正本から派生させる。

## 3. 公開しないもの

- Model Binary
- 実会話Log
- Personal Information
- RAG投入資料
- API Key
- Cloud Credential
- Secret Key
- User固有絶対Path
- 内部機密情報

## 4. Model公開情報

Model本体はGitHubへ含めない。

掲載するもの：

- Model ID
- Distribution
- Upstream
- File名
- Quantization
- Download URL
- Placement
- Revision／Commit
- Hash検証
- License

## 5. Attribution

ARGD／DAGD：

```text
Author  : Nazuna Research
License : CC-BY-SA-4.0
```

ModelごとのLicenseとThird-Party Noticeを確認する。

SeleneはLlama 3.1由来。GuardとJudgeのGGUFは第三者変換としてDistributionとUpstreamを併記する。

## 6. 必読

- [project_requirements_20260718174637.md](../requirements/project_requirements_20260718174637.md)
- [model_strategy_20260718174637.md](../architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../governance/audit_evaluation_security_20260718174637.md)
- [documentation_rules_20260718174637.md](../requirements/documentation_rules_20260718174637.md)

## 7. 注意

公開／非公開、Repository License、Release形式はまだ未決定。公開操作はユーザーの明示指示後に行う。
