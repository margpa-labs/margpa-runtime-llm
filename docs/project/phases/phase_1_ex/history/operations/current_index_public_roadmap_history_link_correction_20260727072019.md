# Current Index Public Roadmap History Link Correction

```yaml
document_id: current_index_public_roadmap_history_link_correction
phase: phase_1_ex
status: corrected_verified
language: ja
created_at: 2026-07-27 07:20:19 JST
owner: 設計統括者役
supersedes: null
```

## 1. Finding

`docs/public/history/roadmap/`の現行構造に対し、Current Documentation Indexだけが旧位置を参照していた。

```text
Broken:
  docs/public/history/roadmap_phase_1_ja.md

Actual:
  docs/public/history/roadmap/roadmap_phase_1_ja.md
```

Stable Current／Shared／Phase文書のLocal Markdown Link検証で、この1件だけを検出した。

## 2. Correction

次を修正した。

```text
docs/project/current/documentation_index_ja.md

Before:
  ../../public/history/roadmap_phase_1_ja.md

After:
  ../../public/history/roadmap/roadmap_phase_1_ja.md
```

Public Roadmap History原本は変更していない。

## 3. Current Index History

```text
Before:
  docs/project/current/history/
  documentation_index_phase_1_ex_ja_20260727072019.md

Before SHA-512:
  9434b1569a9f53d6cf063609bb689e8fa2302519adc46e8d912dbcbeb65e162bfda0977bed24e702ff347bde581ecdb38e8500c79cc4e659e444f567e56f6e1b

After:
  docs/project/current/history/
  documentation_index_phase_1_ex_ja_20260727072057.md

After SHA-512:
  401d177338bfa01bc55c3a0b848d1774c261ed42a823319b80cd29ae43b5d06020811f4bfab077f7ae7b9fe499fe864457577dfb68dc7f7710b08241354790d6
```

更新前後Snapshotは各Stable原文と完全一致する。

## 4. Phase Index History

```text
Before:
  docs/project/phases/phase_1_ex/history/operations/
  phase_index_before_current_index_public_roadmap_history_link_correction_20260727072019.md

Before SHA-512:
  a3ab6a732b005a30ba230bc4d8274b8ce8da93d6b47fa4b28cb894c336e27716689d00b8fe89a249c31b485342aef0b9394029cf1e7aedb539f17ba2b4803993

After:
  docs/project/phases/phase_1_ex/history/operations/
  phase_index_after_current_index_public_roadmap_history_link_correction_20260727072019.md

After SHA-512:
  cf478bebf1a97eee8d0d149215581085611e966fedb2c488c00aaba0f6ab94936ddbcee087d2efbccb248705bd9b6f9cb1eaee12b2499ba3e3d24f64bc51bafa
```

## 5. Validation

```text
Current Stable Local Links:
  PASS

Shared Stable Local Links:
  PASS

Phase 1-ex Stable Index Local Links:
  PASS

Public Roadmap History Exists:
  PASS

Existing Public History Modified:
  NO

Git Operation:
  NONE
```
