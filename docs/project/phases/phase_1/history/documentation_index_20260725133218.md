# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 13:32:18 JST`
- 更新日時: `2026-07-25 13:32:18 JST`
- Snapshot: `20260725133218`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725132748.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Public Warranty Disclaimer               : Reserved for Phase 1-ex
Phase 4 UI Interaction Requirements      : Added／Planned
Responsive UI／Multi-device Experience   : Added／Future Phase
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Calculation Mode             : Added／Future Reservation
Research／Developer Mode                 : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Phase 1-ex公開免責およびPhase 4 UI Interaction要件は、[documentation_index_20260725132748.md](documentation_index_20260725132748.md)から継承する。

本Snapshotは、後半PhaseへResponsive UI／Multi-device Experienceを追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](public/history/roadmap_ja_20260722023908.md)

## 4. Placement

Responsive UI／Multi-device Experienceは、Phase 10のFuture R&Dへ配置する。

Phase 2およびPhase 4では本格的な全端末最適化を完了条件にせず、後続対応を妨げないComponent構造とCSS／Layout Boundaryを維持する。本格対応と検証は基本UIおよび主要Runtime機能の安定後に行う。

## 5. Target Environments

- Smartphone
- Tablet
- Laptop
- Desktop
- Wide Display
- Portrait／Landscape
- 異なるViewport
- 異なるDevice Pixel Ratio
- Browser Zoom／OS Text Scaling
- Mouse／Trackpad／Keyboard／Touch
- Mobile Virtual Keyboard／Safe Area

## 6. Main Responsive Surfaces

- Chat Timeline
- Composer／Send／Stop
- New Chat／History／Navigation
- Basic Settings
- 研究・開発者モード／高度設定群
- Governance／Guard／Judge／Repair／Agent Status
- Audit／Evidence／Source
- Dialog／Notification／Error
- Local Folder／File入力のCapability別Fallback

## 7. Design Boundary

- Device名だけで分岐せず、ContentとLayoutが破綻する幅を基準にBreakpointを決める。
- 狭い画面ではSidebarや高度設定をDrawer、Sheetまたは段階表示へ切り替える。
- Send／StopはTouch TargetとThumb Reachを考慮する。
- Virtual Keyboard表示中もComposerと主要操作を失わない。
- Code、Table、Audit Detail等を除き、意図しない横Scrollを発生させない。
- Text Reflow、Contrast、Focus、Keyboard、Screen Reader Labelを考慮する。
- 日本語／英語のLabel長差で操作を欠落させない。
- 未対応CapabilityはFallbackまたはWarningを表示する。
- Responsive UIをAccess ControlまたはSecurity Boundaryの代替にしない。

## 8. Validation Candidates

- 代表ViewportとBreakpoint境界値
- Orientation変更
- Browser Zoom
- OS Text Size
- Desktop Keyboard／Touch
- Mobile Virtual Keyboard
- 日本語／英語UI
- 長文／Code Block／大きなAudit Detail
- Streaming／Stop／Error／Reconnect

Responsive Webと、将来のNative Mobile App／PWAは別Decisionとして扱う。

## 9. Scoped Authorization

本更新はPublic Roadmapへの将来要件追加と最新Index作成だけを対象とする。

次を自動許可しない。

- Responsive UI実装
- Native Mobile App／PWA実装
- Phase 1-exまたはFuture Phaseの開始
- Git／GitHub操作
- Lightning外部操作

## 10. Next Gate

```text
Responsive UI／Multi-device Experience Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 11. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。
