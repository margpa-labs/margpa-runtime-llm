# Claude Phase 2-E-E〜H React移行 Design

```yaml
document_id: claude_phase_2_e_e_to_h_react_migration_design_20260816102654
status: design_approved
phase: phase_2
subphase: phase_2_e_e_to_h
from: Claude側設計統括者役
to: ユーザー／Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 10:26:54 JST
language: ja
authorization: ユーザーとのChat上でのDesign議論を経て承認（2026-08-16、「一通り読んだけど。okやね」）
```

## 1. 背景・目的

Codex不在の間、UIをClaude／ChatGPT的な構成へ改造し、Phase 4／Phase 10で予定されているUI Interaction Requirements・Responsive UI／Multi-device Experienceの一部を前倒しする。あわせて、FrameworkをReact（Vite Build）へ移行する。

Framework選定は、`docs/public/concept_ja.md`、`docs/public/roadmap_ja.md`、`docs/project/current/project_continuity/project_continuity_master_ja.md`をRead-onlyで確認した上で、Next.jsではなくReactを選定した。判断根拠は第4節に記録する。

## 2. Phase分割

| Phase | 内容 | 性質 |
|---|---|---|
| **2-E-E** | React Foundation：Vite＋React（＋TypeScript）へ基盤構築。既存の見た目・機能を1:1で再現するだけで、新規Layout要素は含めない。既存API・既存CSS Token（2-E-DのLight／Dark）をそのまま流用する。 | Framework移行RiskをUI変更Riskから独立させる |
| **2-E-F** | Sidebar化：全幅化、Sidebar本体（既定表示・隠す/出すButton）、上部4行＋3行Block、区切り線、新規チャット、保存済みChat縦並び（Hover時流れるChat名＋右端Option Button、中身はArchive/Unarchive・Resumeのみ）。 | 新規UI構築(1) |
| **2-E-G** | Account→設定Modal化：Sidebar最下部Account、設定Modal（×閉じ、画面中央）、中に既存「設定」＋（仮称）「アドバンスモード」→Runtime設定制御を格納。将来のPhase 10以降のCategory追加を妨げない拡張可能な構造にする。 | 新規UI構築(2) |
| **2-E-H（余力枠）** | 名前変更・削除：Domain→Port→Adapter→API→Testの新規Backend一式＋Frontend配線。 | Stretch（余裕があれば） |

2026-08-16のユーザー判断：F・Gは統合せず分離したまま進める。E-Hは「余力があったらやる」扱いで、最優先ではない。

## 3. Architecture設計

### 3.1 ディレクトリ構成

```text
frontend/                          ← 新規。npm/Vite/React/TSの世界はここに完全隔離
  src/
    api/                            ← 既存API（/api/v2/...）を叩くTyped Client
    state/                          ← Theme・Language・Conversation等のState管理
    components/
      Sidebar/
        Sidebar.tsx
        SidebarHeader.tsx           ← Title Block(4行) + Preview Note Block(3行)
        SidebarToggleButton.tsx
        NewChatButton.tsx
        ChatList.tsx
        ChatListItem.tsx            ← Hover Marquee + Option Button
        AccountFooter.tsx
      SettingsModal/
        SettingsModal.tsx
        BasicSettingsPanel.tsx      ← 旧「設定」
        AdvancedModePanel.tsx       ← 旧「Runtime設定制御」
      Chat/
        MessageList.tsx
        MessageBubble.tsx
        Composer.tsx
      ThemeLanguageSwitcher.tsx     ← 画面右上、White|Dark・日本語|English
    styles/                         ← 2-E-DのCSS Token（:root / [data-theme="dark"]）をほぼそのまま移植
  vite.config.ts
  package.json
  tsconfig.json

src/margpa_runtime_llm/web/static/  ← Vite Build成果物の出力先。既存FastAPIがそのまま配信する。
```

### 3.2 設計原則（Reactを選んだ理由と一貫させる）

- **Node.jsはBuild時だけ**。`npm run build`で生成した静的File（JS/CSS/HTML）をRepositoryへCommitし、既存のFastAPIがそのまま配信する。Mac・Lightning等の実行環境側にNode.jsを追加Installする必要は一切ない（現行の`app.js`配信の仕組みを維持する）。
- CSPの`script-src 'self'`・外部CDN不使用は継続する。Vite BuildはDefaultで全依存をBundleするため、この方針を自然に満たす。
- TypeScriptを採用する。Python側が`mypy --strict`を徹底していることと一貫させる意図、およびSidebar/Modal等でState数が増える際のBugを型で防ぐ目的による。

### 3.3 Framework選定根拠（React vs Next.js）

`docs/project/current/project_continuity/project_continuity_master_ja.md`第16.3節「Initial Non-goals」に次がある。

> 「SQL、Docker、Cloud SDKまたは特定FrameworkをCoreの必須Dependencyにしない。」

同第16.2節「Project Priority」：

> 「現在のMacで継続開発できる。」「将来のHome Server／Cloud移行時にModel／Backend交換だけで再開できる。」

実Resource制約（第16.1節、第23.2節）：

```text
Mac       : 16GB Unified MemoryをOS・Model・KV Cache・UI・RAG・Auditで共有
Lightning : 4 vCPU・約15GiB・Pure CPU Profile
```

Next.jsの中核価値（SSR、API Routes、ISR、File-based Routing）は、本Projectには不要である。3文書のいずれにもSEO要件、複数Page構成、Content配信Site的要素は存在しない。「Public Demo」も認証なしの最小限Read-only Previewであり、Next.jsが得意とするMarketing/Content Site的なものではない。

Next.jsをSSR／API Routes込みで採用すると、実運用時にPython（FastAPI／推論）とは別に常駐するNode.js Server Processが必要になり、Memory共有が明記されているMac・Lightning双方で推論用Processと資源を取り合う。React（＋Vite）であれば、Build成果物はただの静的File であり、既存のFastAPI配信の仕組みに変更なく乗る。Node.jsが要るのはBuild時（開発Machine／CI）だけで、実行環境側のFootprintは現状と変わらない。

## 4. 要Flag事項：既存Test Suiteの再設計が必要

現在のTest Suiteには、`app.js`／`app.css`をText として直接読んで文字列一致を見るPrivacy／Safety Contract Testが多数存在する（`test_persistent_static_contract.py`、`test_theme_static_contract.py`、`test_configuration_control_static_contract.py`、`test_web_app.py`内の一部等）。React化してVite BuildでBundle・Minifyすると、これらの文字列一致Testはほぼ全滅する（変数名変化、複数File統合等）。

これは実装後に気づいて直す類の話ではなく、最初から設計に組み込む。2-E-Eで次のように再設計する。

- Component単位のBehavior Test（Vitest ＋ React Testing Library）を新設し、「Privacy Contract（localStorage使用範囲等）」「Safety Contract（危険なDOM操作の不使用等）」をComponent側で検証する。
- Backend API Contractを検証している既存Test（実際のHTTP Responseを見るもの、例：`test_configuration_control_web_app.py`）はJS実装に依存しないため、無改修でそのまま使う。

## 5. Evidence方針

これまでのCycleと同様（Automation／Cross-provider EvidenceをAppend-onlyで都度記録）。本Migration一連はユーザーにより「Bypass実験その2」と位置づけられており、Phase間の区切り方（Non-stop一気通貫か、Phase完了ごとにStopするか）は別途調整中。

## 6. Status

```text
Current Point            : 2-E-E〜H全体のDesignがユーザー承認済み。実装未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Design記録）
Open Current Blocker      : NONE（技術）。進め方（Checkpoint方式）はユーザー判断待ち。
Controller-owned Next Work: 進め方確定後、2-E-Eの実装着手。
Exact Next Route          : ユーザーからの進め方指示待ち。
```
