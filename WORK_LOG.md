# Work log

## 2026-09-26
- Done: split out of `fishery/private/`. Shop master from touoroshi.or.jp
  (447 shops, 1,572 stalls; block rows drawn bottom-up, 9 columns); purchases.csv with
  stall_no lookups.
- Decisions: flat repo, no `data/` or `private/`; `*.xlsx` gitignored;
  shop list = shops.csv + stalls.csv (raw download not kept); purchases in
  purchases.csv, tracked in git (was gitignored until 2026-09-26); no Excel.
- Next: enter purchases; test the lookups in Excel with one row.
