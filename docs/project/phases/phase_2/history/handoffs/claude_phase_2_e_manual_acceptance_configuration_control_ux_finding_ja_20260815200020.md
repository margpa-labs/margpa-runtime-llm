# Claude Phase 2-E Manual Acceptance — Configuration Control UX Finding

```yaml
document_id: claude_phase_2_e_manual_acceptance_configuration_control_ux_finding_20260815200020
status: deferred_finding
phase: phase_2
subphase: phase_2_e
from: Claude設計統括者役
to: Codexプロジェクト責任者兼設計統括者役／ユーザー
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 20:00:20 JST
language: ja
discovered_during: Phase 2-E Mac Manual Acceptance Step F（Phase 2-A〜D Regression、Configuration Control確認）
target_feature: Phase 2-D Configuration Control（Phase 2-E実装Scope外）
provenance: 本文書全体はユーザーの明示指示により作成された（第0節参照）。Claude側の自発的なScope拡張ではない。
```

## 0. Provenance（作成経緯の明示）

本文書は、Claude設計統括者役が自らの判断でScopeを拡張して作成したものではない。Phase 2-E Mac Manual Acceptance Step F実行中のChatで、ユーザーがConfiguration Control画面の挙動について実機で疑問を報告し、Claudeが実Source Codeを調査してFinding化した後、ユーザーが次を明示的に指示したことに基づく。

> 「うん。確かPhase 3か4かどこかでUI大幅改変するはずだったから、Codex宛の報告書みたいな感じで、この辺の話しまとめてdocs/のどこかに書いといて。ユーザーの指示って書いといていいから。」

これに従い、以下の調査内容をAppend-only Fileとして記録する。対象（Phase 2-D Configuration Control）はPhase 2-Eの実装Mutation Scope外であり、本文書はSource Codeの追加変更を一切伴わない（純粋な観察・報告のみ）。

## 1. 位置づけ

- 本Findingは**機能的なBugではない**。Restart-required Fieldが安全にLive適用されない、という設計自体（Configuration Controlの中核安全境界）は正しく動作していることを、実機Acceptance（Phase 2-E Mac Manual Acceptance Step F）で確認済みである。
- 本Findingは、Phase 2-D由来のConfiguration Control UIにおける**文言（Copy）・要素共有設計に起因する誤読可能性**に関するものである。
- Phase 2-Eの技術ScopeにもAcceptance Sequence A〜Gの合否判定にも影響しない。`docs/public/roadmap_ja.md`第10節「Phase 4 — MARGPA Main Runtime Governance」内の「Phase 4 UI Interaction Requirements」（同文書928行目付近）で、主要LLM Productに近いUI Interactionの拡張が既にRoadmap上で予定されていることから、本FindingはPhase 4（またはそれ以降のUI関連Phase）での改善候補として記録する。

## 2. 発見経緯（Chat記録、要約ではなく実際のやり取り）

ユーザーは実Mac上でConfiguration Controlを操作し、`Research・Developer Mode`をONにしてから`context_size`をPreview／Applyした際に次を報告した。

> 「『Restartが必要です。値は保存されていません。[...]』『Apply完了』普通『適用完了』って意味なので、previewのApply完了って出るのは非常にややこしい。」
>
> 「『Research・Developer Mode』をONに押した後に、『Research Modeを適用』を押すと、『Research Modeを適用』の場所がずれるんよ。そのずれて状態だと、previewの真下にApply完了が表示される様になるからややこしいって話し。あと、サーバー再起動〜でも不十分。実質config書き換えるか、コマンドに引数でやらんとダメなんだろ？」

Claudeは以下、実Source Codeを調査し、この報告の技術的な裏付けを取った。

## 3. Finding 1：Preview結果とApply結果が同一DOM要素を共有している

### 3.1 該当箇所

- `src/margpa_runtime_llm/web/static/index.html:76-79`（`#configuration-preview`／`#configuration-apply`Button、`#configuration-result`要素の並び）
- `src/margpa_runtime_llm/web/static/app.js:897`（Preview結果を`elements.configurationResult.textContent`へ書き込み）
- `src/margpa_runtime_llm/web/static/app.js:936`（Apply完了時、同じ`elements.configurationResult.textContent`を上書き）

### 3.2 機構

PreviewのDiff JSON（before/after等）と、Apply完了通知（`"Apply完了"`）は、**同一の`<pre id="configuration-result">`要素**へ`textContent`を直接上書きする形で表示される。両者は独立した表示領域を持たない。

### 3.3 誤読が起きる理由

`Research・Developer Mode`がOFFの間、`configuration-meta`（Revision／Digest）・`configuration-fields`（Field一覧）・Model欄・Context欄・`Preview`Buttonは`hidden`（`app.js:777-781`、`developerDetailsVisible`判定）。ONにした瞬間これらが一斉に表示され、`Research Modeを適用`Buttonおよびその直後の`#configuration-result`が画面下方へ押し出される。

この状態でPreviewを押すとDiffが`#configuration-result`に表示され、続けてApplyを押すと同じ場所が`"Apply完了"`に置き換わる。Developer Mode ONで諸Fieldが可視化されている状況下では、この`#configuration-result`はModel欄・Context欄・Preview／Apply Buttonの直下という、視覚的に「直前のDiffの結果である」ことを示唆する位置に来る。実際には`restart_required`Fieldの場合、値は一切保存・適用されていないにもかかわらず、「Apply完了」という表示が視覚的にそのDiff内容を追認しているように読める。

### 3.4 改善方向性（提案、実装は本文書のScope外）

- Preview結果表示領域とApply完了通知表示領域を、DOM上・視覚上ともに分離する。
- Apply完了通知は、`restart_required`を含むPatchの場合、単純な完了文言ではなく「何が記録され、何がまだ反映されていないか」を明示する文言にする。

## 4. Finding 2：「Apply完了」という文言自体の不正確さ

### 4.1 該当箇所

`src/margpa_runtime_llm/web/static/app.js:53`

```js
configurationApplied: "Apply完了",
```

### 4.2 問題

- 他のUI文言（`"Research Modeを適用"`、`"Restartが必要です"`等）はすべて日本語なのに、ここだけ英単語「Apply」が混在しており、Localization一貫性を欠く。
- より本質的な問題として、`apply_disposition: "restart_required"`のFieldに対しては、実際には値が保存も適用もされていない（`configurationRestartRequired`文言自身が「値は保存されていません」と明言している）。にもかかわらず、直後のApply操作結果表示が「完了」と言い切ることは、機能の実態と矛盾する。

### 4.3 改善方向性（提案）

- `restart_required`を含むPatchのApply結果には「Apply完了」ではなく、例えば「変更内容を記録しました（未保存）」のような、実態に即した文言を用いる。
- 英語ソース側（`app.js:158,165`の`"Apply Research Mode"`／`"Apply complete"`）も同様の観点で見直しが必要。

## 5. Finding 3：「Restart」という語の曖昧さ、および具体的な反映手順の欠如

### 5.1 該当箇所

`src/margpa_runtime_llm/web/static/app.js:48-49,54`

```js
configurationModel: "選択Model（Restart必要）",
configurationContext: "Context Size（Restart必要）",
configurationRestartRequired: "Restartが必要です。値は保存されていません。",
```

### 5.2 問題

- 本Project自体、Phase 2-E Acceptance Sequence D内で「Browser Reload」（項目3相当）と「Server再起動」（項目9相当）を明確に別事象として検証しているにもかかわらず、UI文言では両方とも単に「Restart」とだけ表記されており、区別がない。ユーザーが「Restartだけだと、ブラウザリロードも含まれそうな気がする」と指摘したとおりである。
- より実務上重要な問題として、`"Restartが必要です。値は保存されていません。"`という文言は、「何を変更すれば反映されるか」を一切示していない。実際には、Web UI経由の操作だけでは`restart_required`Fieldの新しい値はどこにも永続化されない。反映するには、次のいずれかで**起動時の値そのもの**を変更した上でServer Processを再起動する必要がある（`src/margpa_runtime_llm/entrypoints/web/main.py:113-122`の`--model-key`／`--context-size`CLI引数、または`src/margpa_runtime_llm/bootstrap/config_loader.py:60`の`MARGPA_CONTEXT_SIZE`等の環境変数）。現在の文言だけでは、「同じCommandのままServerを再起動すれば反映される」という誤解を招きかねない。

### 5.3 改善方向性（提案）

- 「Restart」を「サーバーの再起動」のように主語を明示した表記へ変更する。
- `configurationRestartRequired`の文言に、「この値はUI操作だけでは保存されません。反映するには起動時のCLI引数または環境変数を変更した上でサーバーを再起動してください」に相当する、具体的な次アクションを含める。

## 6. Scope・Status

```text
対象機能              : Phase 2-D Configuration Control（Phase 2-E実装Scope外）
発見経緯              : Phase 2-E Mac Manual Acceptance Step F（ユーザー実機操作、2026-08-15）
機能的Bugの有無        : NONE（Restart-required Fieldの安全境界自体は正しく機能）
性質                  : Copy／UI要素共有設計に起因する誤読可能性、3件
Phase 2-E判定への影響   : NONE（Acceptance Sequence A〜Gの合否を左右しない）
推定対応Phase          : Phase 4（docs/public/roadmap_ja.md第10節「Phase 4 UI Interaction
                        Requirements」、主要LLM Productに近いUI Interaction拡張）または、
                        それ以前にUIへ手が入る機会があればその時点
Source変更            : 0（本文書は観察・報告のみ、実装は行っていない）
Next Route            : ユーザーが本文書をご自身のAcceptance結果と合わせてCodexへ報告する
                        （本文書作成後、Claude側からの追加のCodexへの報告・実装着手は行わない）
```
