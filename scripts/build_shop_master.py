"""Build the Toyosu nakaoroshi (仲卸) shop list from touoroshi.or.jp/store/.

The store-search page loads its list from a CSV named in
<table id="s_list" data-url="...">; the upload filename changes when the
association republishes, so the URL is read from the page each run.

Output (repo root, UTF-8 with BOM so Excel opens them):
  shops.csv   one row per company (記号): names, groups, url, tel
  stalls.csv  one row per stall (店舗番号), sorted by block then stall: block,
              position on the site's map, plus the company columns
Text is NFKC-normalised (ﾛ117 -> ロ117).
"""
import csv
import io
import re
import ssl
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = "https://www.touoroshi.or.jp/store/"
SHOPS = ROOT / "shops.csv"
STALLS = ROOT / "stalls.csv"

# Norton TLS scanning breaks cert verification on this machine (same as curl -k).
CTX = ssl._create_unverified_context()


def fetch(url):
    with urllib.request.urlopen(url, context=CTX, timeout=60) as r:
        return r.read()


def nfkc(s):
    return unicodedata.normalize("NFKC", s).strip()


def plain_name(company):
    """'(株)やまふ水産' -> 'やまふ水産'; the name on the sign."""
    return re.sub(r"\((株|有|合|資|名)\)|株式会社|有限会社", "", nfkc(company)).strip()


def group_name(g):
    """'大物業会（マグロ・カジキ類）' -> '大物業会'."""
    return re.sub(r"（.*）$", "", g)


def map_pos(block):
    """Block code -> (map_row, map_col) as drawn on the site's store map.

    Code = 2-digit row + 2-digit column, but the site draws code row 01 at the
    BOTTOM (CSS .row01 top: 83%) and row 12 at the top, so map_row = 13 - row
    (1 = top). The map has 9 columns; 0710 is the right part of a split cell in
    column 9 (0709 is the left part), so column 10 maps to 9.
    """
    return 13 - int(block[:2]), min(int(block[2:]), 9)


def main():
    html = fetch(PAGE).decode("utf-8")
    csv_url = re.search(r'id="s_list"\s+data-url="([^"]+)"', html).group(1)
    raw = fetch(csv_url)

    shop_header = ["shop_code", "shop_name", "name_plain", "kana", "company", "n_stalls",
                   "groups", "groups_full", "url", "tel"]
    # stalls repeat the company columns (except n_stalls) so each row reads on its own.
    stall_header = ["stall_no", "block", "map_row", "map_col"] +         [h for h in shop_header if h != "n_stalls"]
    shops, stalls = [], []
    for code, name, kana, company, nos, grp, url, tel, blockmap in csv.reader(
            io.StringIO(raw.decode("utf-8-sig"))):
        glist = [g for g in grp.split("、") if g]
        pairs = [p.split("=") for p in blockmap.split("/") if "=" in p]
        shop = [code, nfkc(name), plain_name(company), kana, nfkc(company), len(pairs),
                " / ".join(group_name(g) for g in glist), " / ".join(glist), url, tel]
        shops.append(shop)
        for stall, block in pairs:
            stalls.append([nfkc(stall), block, *map_pos(block)] + shop[:5] + shop[6:])
    stalls.sort(key=lambda r: (r[1], r[0]))  # walk the floor block by block

    for path, header, rows in [(SHOPS, shop_header, shops), (STALLS, stall_header, stalls)]:
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
    print(f"{len(shops)} shops -> {SHOPS.name}, {len(stalls)} stalls -> {STALLS.name} "
          f"(from {csv_url})")


if __name__ == "__main__":
    main()
