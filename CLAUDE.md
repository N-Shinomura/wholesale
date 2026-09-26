# wholesale — personal fish-purchase records at Toyosu market

Personal log of fish purchases (date, item, weight, price) at the Toyosu
market 仲卸 (intermediate wholesaler) shops, joined to a shop master built
from the 東京魚市場卸協同組合 store list (https://www.touoroshi.or.jp/store/).
Independent of `fishery`; do not link the two unless asked.

**Key files** (flat repo: no `data/` or `private/` folders)
- `scripts/build_shop_master.py` — reads the store page, downloads the CSV
  it loads (URL taken from `<table id="s_list" data-url=...>`, filename
  changes on each republish) and writes `shops.csv` and `stalls.csv`. The raw download is
  not saved.
- `shops.csv` — one row per company (記号), 447 rows (public data, UTF-8
  with BOM): shop_code, shop_name (商号), name_plain (company without
  (株)/(有)), kana, company, n_stalls, blocks (all its blocks, ` / `-joined),
  groups (業会 short), groups_full, url, tel.
- `stalls.csv` — one row per stall (店舗番号), 1,572 rows, sorted by block
  then stall: stall_no, block, row, map_col, slot, then every `shops.csv`
  column except n_stalls and blocks (company fields repeat by design).
- `scripts/plot_block_map.py` → `block_map.png` — floor map with every stall
  at its real position, coloured by 業会 (3 hues + grey その他), shop names on
  runs of ≥ 6 stalls.
- `purchases.csv` — tracked in git. One row per purchase: date,
  buyer, shop_name, stall_no, shop_code, block, groups, item, origin, qty,
  unit, weight_kg, unit_price_yen, price_per (kg / 杯 / パック …),
  amount_ex_tax, total_incl_tax (as paid), tax_yen, note. shop_code / block /
  groups copied from `shops.csv` / `stalls.csv`; `?` = not in the 仲卸 list. Receipts so
  far are 8% tax, fraction dropped.

**Shop-master conventions**
- Floor layout (Tokyo's official plan, 豊洲市場6街区水産仲卸売場棟・水産仲卸店舗
  全体配置図, shijou.metro.tokyo.lg.jp): 12 rows, each ONE line of stalls
  numbered left to right, slot 1–146 = last three digits of the stall
  number. Rows from the bottom: 1, 2, … 8, イ, ロ, ハ, ニ (`row` = the
  stall's own prefix; there is no 9000 row). Rows face each other back to
  back in pairs (1|2, 3|4, 5|6, 7|8, イ|ロ, ハ|ニ). 山治 1001 (block 0101) is
  the bottom-left corner.
- Block code (site's own, e.g. `0802`) = 2-digit row (01–12, bottom-up) +
  2-digit column. 9 block columns separated by 第1–第8通路 (slots 1–14,
  15–30, …, 127–146); `0710` is the right part of a split block in column
  9, so `map_col` maps 10 → 9.
- Stall numbers are NFKC-normalised (site's half-width `ﾛ117` → `ロ117`).
- One shop (記号) can have many stalls in different blocks and belong to
  several 業会.
- Network: Norton TLS scanning breaks cert checks — the script uses an
  unverified SSL context (same as `curl -k`).

**Data roots:** none; everything is in this repo.

**Build:** no manuscript; no LaTeX. Run with `python scripts/build_shop_master.py`
(standard library only). Close `shops.csv` / `stalls.csv` in Excel before running.

## Audit flags

### goal
Keep an accurate record of fish purchases linked to the current
Toyosu 仲卸 shop master.

### sub-goals
- Shop master rebuildable from the live site in one command.

### required-patterns
- No `data/` or `private/` folders: xlsx/csv live at the repo root.

### forbidden-patterns
- Any `*.xlsx` tracked by git (data lives in CSV).
- Hard-coded CSV upload URL (`HomepageUpload_*.csv`) in scripts — it must be
  read from the store page.

### completion-marker
`.claude/audit/TASK_COMPLETE.md`

### audit-output
`.claude/audit/AUDIT_RESULT_<timestamp>.md`
