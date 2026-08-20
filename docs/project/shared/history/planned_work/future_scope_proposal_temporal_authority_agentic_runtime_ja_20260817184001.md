# 将来Scope提案 — Temporal Authorityを持ったAgentic Runtime（Time Provider／Scheduler／Tool／Agent／Evidence）

```yaml
document_id: future_scope_proposal_temporal_authority_agentic_runtime_20260817184001
status: reservation_not_started
phase: cross_phase
subphase: null
from: ユーザー（原案）／Claude側設計統括者役（まとめ直し）
to: プロジェクト責任者兼設計統括者役（Codex）
role: design_governor
created_at: 2026-08-17 18:40:01 JST
language: ja
purpose: |
  ユーザーが2026-08-17に提示した将来Feature構想（Runtime常駐の
  Time Provider／Scheduler、Tool基盤、Agent Runtime、Evidence／
  Evaluationからなる「時間軸上で仕事を持つAgentic Runtime」）を、
  Codex復帰後のRoadmap更新Inputとして記録する。ユーザー明示指示：
  「codex復活したら、roadmap更新させるから」——本Docは実装着手を
  意味しない、あくまでCodexへの引き継ぎ材料。
authorization: |
  ユーザー指示（2026-08-17）：「いずれこれ作りたいから、まとめ直して
  docs/のどこかに書いておいて」。history/以下への新規Append-only
  File作成であり、Claude側設計統括者役の無許可書込み範囲内
  （運用メモ第3節）。
```

## 0. 位置付け（重要）

**本Docは提案・記録のみであり、実装は一切未着手・未着手予定。** ユーザーは「いずれ作りたい」「Codex復活したらRoadmap更新させる」と明言しており、本Docの役割はそのRoadmap更新時にCodexが参照するInput資料を残すことに限定される。Claude側設計統括者役は、本Docの作成をもって設計判断を確定させたり、実装Phaseへ組み込んだりしない。

## 1. 背景・要旨

MARGPA Runtime LLMの自然な延長として、「指定した時刻・周期でRuntimeが自律的にTool実行〜Data処理〜LLMによる分析〜結果保存までを完結させる」機能——一言でいえば**Scheduled Autonomous Workflow**——を将来実装したい、という構想。ユーザーの一次的な例：「毎週金曜18:00にサイトXからScraping→Data加工→DB投入→分析→結果保存」を、人間の介在なしに毎週自動で回す。

ただし、これを単なるCron機能として矮小化せず、MARGPAが既に持つ「Task／Authority／Evidence／Recovery／Canonical State」という設計哲学の延長として設計するのが良い、というのが本提案の核心。

## 2. 核心的な設計判断：時計はLLMではなくRuntimeのPrimitiveにする

ユーザーが提示した唯一かつ最重要の設計方針転換：

> 「LLMが起動中ずっと現在時刻を取得する」より、「RuntimeにTime Provider / Schedulerを常駐させて、LLMは必要時に現在時刻を参照する」の方が綺麗。LLM自身に毎秒「今何時？」させる必要はない。時計はRuntime側のPrimitiveでいい。

すなわち、時刻管理・Scheduling判断はRuntime層の責務であり、LLM（Agent）はその結果を「必要な時に参照する」だけの受動的な立場に留める。これにより、LLM推論Costと時刻管理を完全に分離できる。

## 3. Architecture概観（Runtime内Component構成、ユーザー原案）

```text
Runtime
├─ Time Provider
│    ├─ current datetime
│    ├─ timezone
│    └─ monotonic clock
│
├─ Scheduler
│    ├─ Job Definition
│    ├─ next_run_at
│    ├─ recurrence
│    ├─ missed-run policy
│    └─ concurrency / lock
│
├─ Tool / MCP Layer
│    ├─ Web Fetch / Scraper
│    ├─ Python
│    ├─ Database
│    └─ File / API ...
│
├─ Agent Runtime
│    ├─ planning
│    ├─ tool selection
│    ├─ branching
│    └─ recovery
│
└─ Evidence / Evaluation
     ├─ execution history
     ├─ inputs / outputs
     ├─ error / retry
     └─ final result
```

## 4. 実行Flow例（「毎週金曜18:00にScraping→分析→保存」）

```text
Friday 18:00 JST
       ↓
Scheduler fires Job
       ↓
Job Execution ID発行
       ↓
Scraping Tool
       ↓
Validation
       ↓
Transformation Tool
       ↓
DB Write
       ↓
Analysis
       ↓
LLM Evaluation / Interpretation
       ↓
Report
       ↓
Evidence / History
       ↓
COMPLETE
```

## 5. Agent／Tool／MCPの優先順位に関する提案

```text
Toolはほぼ必須：LLM単体では外部サイトScrapingもDB Writeもできない
  ため、「Scheduler → Tool execution」という道が必須。

Agentは必須ではない：初期段階はむしろ決定論的Workflow
  （18:00 → scrape() → transform() → insert() → analyze()）で十分。
  Agentを後から導入すると、「Scraping失敗→原因調査→Alternative
  source選択→Data異常検出→再取得→Analysis method変更」のような
  動的分岐が可能になる、という段階的な価値追加として位置づける。

MCPは必須ではない：Toolをどう標準化して外部Provider/Executorから
  扱うかのInterface候補の一つであり、Scheduler自体の前提ではない。
  Schedulerの実装とMCP採用は分離できる。
```

**提案する実装順序（ユーザー原案）**：

```text
1. Time Provider
2. Tool基盤
3. Scheduled Jobの最小実装
4. Persistent Job / History
5. Agent integration
6. MCPも含めたTool abstraction
7. 複雑なAutonomous Scheduled Workflow
```

既存Roadmapとの兼ね合いについては、「Agent/Toolがちゃんと育ってから本体をやる」進行でよいが、「Time/SchedulerのFoundationだけ先に薄く作っておく」ことは十分あり、という位置づけ。

## 6. 状態分離の設計（単なるCron機能で終わらせないための核心）

ユーザーが特に強調した点：Scheduled Jobの「実行された／されなかった」は、実際には単一のBoolではなく、複数の独立した状態の連鎖として扱うべき。

```text
Job exists
!=
Job enabled
!=
Trigger reached
!=
Execution authorized
!=
Execution started
!=
Tools succeeded
!=
Data committed
!=
Analysis accepted
```

この分離は、MARGPAが既存のPersistent Conversation機構等で採用している「Storage Revision・Optimistic Concurrency・Commit Receipt」的な、状態遷移を厳密に追跡する設計思想と親和性が高い（本Doc第9節）。

## 7. 再起動・Recovery・運用面のOpen Question（ユーザー原案）

### 7.1 Missed-runへの対応方針（Job Policyとして必要）

```text
例：金曜17:59にServer停止 → 18:05に再起動した場合、
  - 18:00分をSkipする？
  - 即実行する？
  - User確認する？
  - 次週まで待つ？
これ自体がJob単位で設定可能なPolicyになるべき。
```

### 7.2 その他、実装時に詰める必要がある論点（ユーザー原案列挙）

```text
- 同じJobが二重起動しない（Concurrency Lock）
- DB投入途中で落ちたら再実行して二重INSERTしない（冪等性）
- Scraping成功・DB失敗ならどこからRecoveryするか（部分失敗からの再開点）
- Job Definition変更前後のRevisionを残す（Job定義自体の変更履歴管理）
- どのAgent / Tool / Modelが実行したか（実行主体の記録）
- 外部へのWrite権限はどこまであるか（Tool実行時のAuthority境界）
```

## 8. MARGPAの既存Foundationとの親和性（ユーザー所感）

この構想の要点は、最終的な到達点が単なる「金曜18時にLLMを動かす」定時実行にとどまらず、Temporal Authority（時間軸上での実行権限）を持ったAgentic Runtimeになる、という点にある。これは、本Session（Phase 2-E）で実装してきたPersistent Conversation機構（Storage Revision・Commit Receipt・Optimistic Concurrency・Migration Checkpoint等）の設計哲学と、上記第6節・第7節で挙げたScheduled Job側の要件が、構造的に同型であることを指している。Codex側でRoadmapへ組み込む際、既存のConversation永続化Architectureで確立したPattern（Explicit Migration Path、Revision管理、Fail-closed設計）を、Scheduler／Job Historyの設計にも再利用できる可能性が高い。

## 9. Vision Framing（設計意義の要約）

本構想が実現した場合の利用イメージを、中立的な表現で要約する。ユーザーが金曜18時を指定してDataの収集・分析を依頼した場合、その時刻にRuntimeが自律的に稼働し、Scraping・加工・DB投入・分析までを完了させ、翌日以降にEvidence付きの結果を確認できる、という運用が可能になる。

この構想の技術的な意義は、AIの性質そのものの変化にある。従来の「人間がPromptを入力した時にのみ応答するAI」から、「時間軸上で継続的な責務（Scheduled Job）を持ち、その実行状況・Evidence・Recovery方針までRuntimeが管理するAI Runtime」への移行として位置づけられる。これは、将来的に専任のLLM Agentを継続運用する場合にも、そのまま基盤として機能しうる設計である。

## 10. Status

```text
Current Point            : ユーザー構想を記録・まとめ直し。実装着手・
                            設計確定は一切なし。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（提案記録）
Open Current Blocker      : NONE（Blockerではなく、将来Trigger待ち）
Controller-owned Next Work: ユーザーの「Codex復活」後、Codexが本Docを
                            Inputとしてdocs/public/roadmap_ja.md等へ
                            反映するかどうかを判断。
Exact Next Route          : 本DocはRead-only参照材料として保持。
                            Claude側設計統括者役から能動的に着手・
                            提案することはない（ユーザー・Codexの
                            判断待ち）。
```
