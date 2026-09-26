"""Draw the 仲卸 floor with every stall at its real position -> block_map.png.

Layout per Tokyo's official plan (豊洲市場6街区水産仲卸売場棟・水産仲卸店舗全体配置図): 12 rows,
each one line of stalls numbered left to right (slot 1-146) and split into 9
block columns by the aisles (第1-第8通路). Rows face each other in back-to-back
pairs (1|2, 3|4, 5|6, 7|8, イ|ロ, ハ|ニ). From the bottom: 1 ... 8, イ, ロ, ハ, ニ,
so 山治 (1001, block 0101) is the bottom-left corner.

Consecutive stalls of the same shop merge into one bar. Colour = the shop's
first-listed 業会: the three largest get hues, the rest fold into grey
"その他" (a map puts every colour next to every other, which only three hues
survive for colour-blind readers). Runs of >= LABEL_MIN stalls are named.
Empty outlined slots = no 仲卸 stall listed there.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "block_map.png"
LABEL_MIN = 6
AS_OF = "2026.09.26"   # date stalls.csv was fetched from touoroshi.or.jp; update after a rebuild

plt.rcParams["font.family"] = ["BIZ UDGothic", "Yu Gothic", "Meiryo"]  # UD face with a real bold weight
plt.rcParams["hatch.linewidth"] = 0.7

SURFACE = "#fcfcfb"
TEXT, TEXT_2, MUTED, OUTLINE = "#0b0b0b", "#52514e", "#8a8984", "#dcdbd6"
# Lighter steps of the first three categorical hues, validated all-pairs
# (validate_palette.js --pairs all): passes; orange<->aqua sits in the CVD 6-8
# band. A hatch on 鮮魚 was tried as a second cue and dropped at the user's request.
GROUP_COLOR = {
    "特種物業会": "#6aa3e5",   # blue
    "大物業会": "#f19571",     # orange
    "鮮魚業会": "#5fc69f",     # aqua
}
HATCHED = {}                   # group -> hatch colour; empty = no hatching
OTHER = ("その他", "#cfcdc6")

ROWS = ["1", "2", "3", "4", "5", "6", "7", "8", "イ", "ロ", "ハ", "ニ"]  # bottom -> top
COL_FIRST = [1, 15, 31, 47, 63, 79, 95, 111, 127]                       # first slot per block column
N_SLOTS = 146

# geometry (data units): slot width 1, aisle gaps between block columns,
# a hairline between the two rows of a back-to-back pair, a wide aisle between pairs.
SLOT_W, AISLE, ROW_H, PAIR_GAP, ROW_AISLE = 1.0, 3.0, 5.0, 0.35, 3.2


def slot_x(slot):
    col = sum(slot >= f for f in COL_FIRST)          # 1..9
    return (slot - 1) * SLOT_W + (col - 1) * AISLE


def col_span(c):                                     # c = 0..8 -> (x_left, width)
    first = COL_FIRST[c]
    last = COL_FIRST[c + 1] - 1 if c < 8 else N_SLOTS
    return slot_x(first), (last - first + 1) * SLOT_W


def row_y(i):                                        # i = 0 (row 1) .. 11 (row ニ)
    pair, top = divmod(i, 2)
    return pair * (2 * ROW_H + PAIR_GAP + ROW_AISLE) + top * (ROW_H + PAIR_GAP)


def ink_on(hex_color):
    """Dark or white label ink, whichever contrasts more with the fill."""
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    lum = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    return "#ffffff" if (1.05 / (lum + 0.05)) > ((lum + 0.05) / 0.05) else TEXT


def main():
    stalls = list(csv.DictReader(open(ROOT / "stalls.csv", encoding="utf-8-sig")))
    at = {(r["row"], int(r["slot"])): r for r in stalls}

    fig, ax = plt.subplots(figsize=(20, 11.5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    for i, row in enumerate(ROWS):
        y = row_y(i)
        for c in range(9):                            # empty-slot outlines per block
            x, w = col_span(c)
            ax.add_patch(Rectangle((x, y), w, ROW_H, fill=False, ec=OUTLINE, lw=0.6))
        # runs of consecutive slots held by the same shop, not crossing an aisle
        s = 1
        while s <= N_SLOTS:
            r = at.get((row, s))
            if r is None:
                s += 1
                continue
            e = s
            while (e + 1 <= N_SLOTS and (row, e + 1) in at
                   and at[(row, e + 1)]["shop_code"] == r["shop_code"]
                   and (e + 1) not in COL_FIRST):
                e += 1
            group = r["groups"].split(" / ")[0]
            colour = GROUP_COLOR.get(group, OTHER[1])
            x0, n = slot_x(s), e - s + 1
            ax.add_patch(Rectangle((x0, y), n * SLOT_W, ROW_H, fc=colour, ec=SURFACE, lw=0.9))
            if group in HATCHED:
                ax.add_patch(Rectangle((x0 + 0.1, y + 0.1), n * SLOT_W - 0.2, ROW_H - 0.2,
                                       fill=False, ec=HATCHED[group], lw=0, hatch="///"))
            if n >= LABEL_MIN:
                name = r["shop_name"]
                ax.text(x0 + n * SLOT_W / 2, y + ROW_H / 2, name, color=ink_on(colour),
                        fontsize=8.6 if len(name) * 1.35 <= n else 6.9, fontweight="bold",
                        ha="center", va="center",
                        bbox=dict(boxstyle="round,pad=0.2", fc=colour, ec="none")
                        if group in HATCHED else None)
            s = e + 1
        ax.text(-1.2, y + ROW_H / 2, row, fontsize=13, fontweight="bold", color=TEXT_2,
                ha="right", va="center")

    top = row_y(11) + ROW_H
    for k in range(1, 9):                             # aisle names along the top
        ax.text(slot_x(COL_FIRST[k]) - AISLE / 2, top + 0.6, f"第{k}\n通路", fontsize=7.5,
                color=MUTED, ha="center", va="bottom", linespacing=0.95)
    for c in range(9):                                # block column numbers along the bottom
        x, w = col_span(c)
        ax.text(x + w / 2, -0.8, f"{c + 1}", fontsize=13, fontweight="bold", color=TEXT_2,
                ha="center", va="top")

    handles = [Patch(fc=c, ec=HATCHED.get(g, c), hatch="///" if g in HATCHED else None,
                     lw=0, label=g) for g, c in GROUP_COLOR.items()]
    handles += [Patch(fc=OTHER[1], label=f"{OTHER[0]}（海老・無所属・北洋・合物・塩干・煉・淡水魚・佃和・伊勢海老）")]
    ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.045), ncol=4,
              frameon=False, fontsize=16.5, labelcolor=TEXT)
    ax.set_title(f"豊洲 水産仲卸売場 店舗配置図（{AS_OF}現在）", fontsize=16, color=TEXT,
                 fontweight="bold", loc="left", pad=30)
    ax.set_xlim(-3.5, slot_x(N_SLOTS) + SLOT_W + 0.5)
    ax.set_ylim(-3.6, top + 3.2)
    ax.axis("off")
    fig.savefig(OUT, dpi=170, bbox_inches="tight", facecolor=SURFACE)
    print(f"{len(stalls)} stalls on {len(ROWS)} rows -> {OUT}")


if __name__ == "__main__":
    main()
