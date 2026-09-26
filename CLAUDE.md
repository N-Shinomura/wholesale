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
  then stall: stall_no, block, map_row, map_col, then every `shops.csv`
  column except n_stalls and blocks (company fields repeat across its stalls by design).
- `purchases.csv` — tracked in git. One row per purchase: date,
  buyer, shop_name, stall_no, shop_code, block, groups, item, origin, qty,
  unit, weight_kg, unit_price_yen, price_per (kg / 杯 / パック …),
  amount_ex_tax, total_incl_tax (as paid), tax_yen, note. shop_code / block /
  groups copied from `shops.csv` / `stalls.csv`; `?` = not in the 仲卸 list. Receipts so
  far are 8% tax, fraction dropped.

**Shop-master conventions**
- Block code (site's own, e.g. `0802`) = 2-digit row + 2-digit column, but
  the site's map draws code row 01 at the **bottom** and 12 at the top, in
  9 columns. `0710` is the right part of a split cell in column 9 (`0709` is
  the left part) — there is no 10th column. `map_row` (1 = top … 12 =
  bottom) and `map_col` (1 = left … 9 = right) in `stalls.csv` give the drawn
  position. All 101 blocks are clickable on the site's map (7 are narrow
  half-cells: 0404, 0407, 0702, 0709, 0710, 1004, 1007).
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
