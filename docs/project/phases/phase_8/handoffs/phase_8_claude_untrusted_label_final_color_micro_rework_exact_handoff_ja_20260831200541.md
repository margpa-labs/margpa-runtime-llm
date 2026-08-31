# Phase 8 Untrusted Label Final Color — Claude Micro Rework Exact Handoff

```yaml
document_type: exact_differential_execution_handoff
document_state: final
provider: Claude
role: designer_and_implementer
task_identity: current_continued_claude_task
task_state: continued_not_fresh
phase: phase_8
package: P8_MR10_single_CSS_truthfulness_fix
implementation_authority: true
independent_review_authority: false
phase_8_closure_authority: false
maximum_claim: COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK
created_at: 2026-08-31 20:05:41 JST
```

## 1. Objective

P8-MR9 Controller Reviewで未解決となったP8-CODEX-021だけを直す。Current Claude Taskを継続し、
Fresh Task化、BootstrapまたはPhase 8再読を行わない。

## 2. Mandatory Differential Reading

1. Controller Review：

```text
docs/project/phases/phase_8/history/operations/phase_8_post_mr9_controller_single_review_adjust_ja_20260831200541.md
```

2. Latest Return：

```text
docs/project/phases/phase_8/handoffs/phase_8_claude_final_four_user_manual_UI_truthfulness_micro_rework_exact_return_handoff_ja_20260831184853.md
SHA-512:
d56b6d809d2685acb591f9bd37cf3a994fd2218b70c58228580c17c3363b7050f974574c3e3f75a0b525bc551096c95555ed23cd2138d227a75c855500cc245f
```

3. Latest Recovery：

```text
docs/project/phases/phase_8/history/index/phase_8_claude_final_four_user_manual_UI_truthfulness_micro_rework_recovery_ja_20260831184853.md
SHA-512:
dedf78d968482a9e83af6edae42387b5d10f149db95fa2c7089d63c1dfed7f817e5af45b9ad7f466d5040d16a5f89c296e937864785d804cba488783eb73d5c6
```

## 3. Preserved PASS

```text
P8-MANUAL-FINAL-001 PASS
P8-MANUAL-FINAL-002 PASS
P8-MANUAL-FINAL-004 PASS
P8-MR0〜MR8全Baseline
```

これらを変更、再実装または再Testしない。

## 4. Required Fix

Current：

```css
.web-search-panel-untrusted-label {
  color: var(--gauge-warn);
  font-weight: 600;
}
```

`--gauge-warn`はLight Citation背景でContrast 2.93:1であり、Userが指摘した「このLabelだけ他と色が違う」状態も残す。

次へ変更する。

```css
.web-search-panel-untrusted-label {
  color: var(--citation-text);
  font-weight: 600;
}
```

同等の既存Metadata Tokenを使うより適切な理由がSource上ある場合のみ代替を許す。その場合も、周囲Metadataとの統一と
Light／Dark双方4.5:1以上を数値で示す。

文言、Class、Untrusted Semantics、Card Layout、Backend Contract、React Componentは変更しない。

## 5. Verification

1. CSS Sourceを確認する。
2. Light／DarkでForeground／Background Contrastを計算し、両方4.5:1以上を記録する。
3. 既存WebCitationsSection／WebSearchPanel Focused Testを実行する。
4. Frontend Buildを行いStatic Artifactを更新する。
5. 生成`app.css`が同じTokenを含むことを確認する。
6. Source変更がCSSだけならFull Frontend、Backend、Mypy、Ruff、Internal Review追加Cycleは不要。

## 6. Authority／Prohibitions

許可：対象CSS、生成Static CSS／JS、Focused Test、Build、Recovery、Exact Return。

禁止：Git、Network、Install、Browser、Model、MCP、User runtime_data、Backend、React／Testの不要変更、Roadmap、Closure、Phase 9。

## 7. Return

```text
P8-CODEX-021 Disposition
Changed Paths
Light／Dark Contrast
Focused Test Result
Build Result
Static Artifact Result
Recovery Index
Exact Return Handoff／SHA-512
```

最大Claimは`COMPLETE_CANDIDATE_FOR_FINAL_USER_RECHECK`。完了後、Codex Controller Targeted Review待ちで停止する。
