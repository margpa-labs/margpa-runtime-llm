# Known Issues／Observations Register

- 文書ID: `known_issues_and_observations`
- 状態: `current`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象: Project横断の既知問題、非Blocking Observation、Technical Debt
- 正本言語: 日本語
- User Test補足: [phase_1_user_acceptance_findings_20260719195134.md](../user_manual/phase_1_user_acceptance_findings_20260719195134.md)
- supersedes: `known_issues_and_observations_20260719171836.md`

## 1. 状態分類

```text
open_blocking       : 現在のPhaseまたはReleaseを止める
open_required       : 必須Follow-upが必要
accepted_deferred   : 影響を理解して後続Phaseへ延期
monitor             : 条件発生時に再評価
resolved            : 後継文書で解決Evidenceを記録
not_reproducible    : 再現不能。再発時に再開
```

## 2. Current Items

### MARGPA-OBS-0001: Mixed-source Presentation Config Error Attribution

```yaml
state: accepted_deferred
severity: low
category: configuration_diagnostics
required_follow_up: false
```

Environment由来の不正なThinking Presentation値と、別Fieldの正常なCLI指定が同時に存在する場合、Error Codeの原因分類が少し不正確になる。不正値は安全に拒否され、正常動作、Security Boundary、Phase 1 Acceptanceを単独ではBlockしない。

Phase 2 Config UI、Field別Validation、External Release前のError Taxonomy整理時に再評価する。

### MARGPA-OBS-0002: Hidden Thinking Final Answer Exhaustion

```yaml
state: open_required
severity: low
category: cli_presentation_diagnostics
required_follow_up: true
```

Thinkingを有効、VisibilityをHiddenとし、Closing／Final Answerより前にToken上限へ到達すると、CLIの表示が空になる。Reasoning漏洩やParser故障ではないが、利用者が原因を判別できない。

Final Answer未生成を判定可能なEvidenceがある場合、Reasoning本文を露出せず、次の意味のSafe Warningを表示する。

```text
最終回答を生成する前にToken上限へ到達しました。
```

False Positiveを避け、正常な空回答、Model Error、User Cancelと混同しないことを実装条件とする。

### MARGPA-OBS-0003: Preserved Leading Whitespace in Final Answer

```yaml
state: accepted_deferred
severity: low
category: presentation_normalization
required_follow_up: false
```

Canonical Closing Tag後の改行をParserが保持するため、Final Answer先頭に空行が残る場合がある。Raw Output保持と無断Trim禁止の結果であり、Phase 1では修正しない。

UI／Presentation層で、Raw／Parsed Evidenceを変えず表示だけを正規化できる段階で再評価する。

### MARGPA-OBS-0004: Reasoning Language May Differ from Final Language

```yaml
state: accepted_deferred
severity: low
category: model_language_behavior
required_follow_up: false
```

`response_language = ja`でも、表示したQwen3 Reasoningが英語になる場合がある。Current Language PolicyはFinal AnswerへのBest-effort Instructionであり、Raw Reasoning Languageを強制しない。

Strict Language EnforcementはPhase 1-E Scope外である。Model固有Prompt、Reasoning Language設定、Model交換、表示用翻訳を後続で比較する。

### MARGPA-OBS-0005: Registered-platform Routing Is Not Full Hardware Auto-routing

```yaml
state: accepted_deferred
severity: low
category: deployment_portability
required_follow_up: false
```

OS／Architecture検出と登録済みDefault Profile選択は実装済みだが、Linux／Windows Profile、Platform別Native Build、実機検証は未完了である。また同一Linux x86_64内のCPU／CUDA／ROCm等をHardware Observationで自動選択する完成形は未実装である。

Application CoreはPlatform固有条件から分離済みであり、一般Cross-platform完成を延期しても後続Core PhaseをBlockしない。Lightning AI Studioのような明示環境は、当面Explicit Profileで追加・検証できる。

## 3. Phase／Backupへの影響

- `MARGPA-OBS-0001`、`0003`、`0004`、`0005`はAccepted Deferredであり、Phase 1を単独ではBlockしない。
- `MARGPA-OBS-0002`は実装対象候補であり、User Acceptance GateはFollow-upのDisposition確定までWaitingとする。
- Follow-upでSource／Config／Testsを変更した場合、影響範囲の再Review／再Testが必要である。

## 4. 更新規則

状態変更、Resolution Evidence、項目追加は既存Fileを編集せず、新Timestampの後継Registerで行う。
