import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")


# ==========================================================
# 1. LOAD DATA
# ==========================================================

FILE_PATH = "transaksi.xlsx"

if not Path(FILE_PATH).exists():
    raise FileNotFoundError(f"File '{FILE_PATH}' tidak ditemukan.")

df = pd.read_excel(FILE_PATH)

print("=" * 50)
print("INFO DATA")
print("=" * 50)
print(f"Jumlah Baris : {df.shape[0]}")
print(f"Jumlah Kolom : {df.shape[1]}")
print("\nNama Kolom:")
print(df.columns.tolist())
print()


# ==========================================================
# 2. DATA CLEANING
# ==========================================================

df["Tahun_rilis_clean"] = (
    pd.to_datetime(df["Tahun_rilis"], errors="coerce").dt.year
)
df.loc[df["Tahun_rilis_clean"] < 2010, "Tahun_rilis_clean"] = None

df["tanggal_transaksi"] = pd.to_datetime(df["tanggal_transaksi"])
df["Bulan"] = df["tanggal_transaksi"].dt.month
df["Bulan_nama"] = df["tanggal_transaksi"].dt.strftime("%b")


def segmentasi_harga(harga):
    if harga < 5_000_000:
        return "Budget\n(<5 Jt)"
    elif harga < 15_000_000:
        return "Mid-range\n(5–15 Jt)"
    else:
        return "Flagship\n(>15 Jt)"


df["Segmen"] = df["Harga"].apply(segmentasi_harga)

print("=" * 50)
print("HASIL CLEANING")
print("=" * 50)
print("Tahun rilis tidak valid :", df["Tahun_rilis_clean"].isna().sum())
print()


# ==========================================================
# 3. ANALISIS
# ==========================================================

revenue_brand = (
    df.groupby("Brand")["Harga"].sum().sort_values(ascending=False)
)
avg_rating = (
    df.groupby("Brand")["Rating_pengguna"].mean().round(2)
    .sort_values(ascending=False)
)
monthly = df.groupby("Bulan").size().reindex(range(1, 13), fill_value=0)


# ==========================================================
# 4. TEMA & PALET WARNA
# ==========================================================

BG_DARK      = "#0D1117"   # background utama
BG_CARD      = "#161B22"   # card/panel
BG_CARD2     = "#1C2128"   # card sedikit lebih terang
BORDER       = "#30363D"   # border subtle
TEXT_PRIMARY = "#E6EDF3"
TEXT_SEC     = "#8B949E"
TEXT_MUTED   = "#484F58"

ACCENT_BLUE  = "#2F81F7"
ACCENT_GREEN = "#3FB950"
ACCENT_PINK  = "#F778BA"
ACCENT_AMBER = "#E3B341"
ACCENT_TEAL  = "#39D3BB"

PALETTE = [
    "#2F81F7", "#3FB950", "#F778BA", "#E3B341",
    "#A5A0F7", "#F0883E", "#FF7B72", "#39D3BB",
    "#D29922", "#58A6FF",
]

plt.rcParams.update({
    "figure.facecolor":  BG_DARK,
    "axes.facecolor":    BG_CARD,
    "axes.edgecolor":    BORDER,
    "axes.labelcolor":   TEXT_SEC,
    "axes.titlecolor":   TEXT_PRIMARY,
    "xtick.color":       TEXT_SEC,
    "ytick.color":       TEXT_SEC,
    "text.color":        TEXT_PRIMARY,
    "grid.color":        BORDER,
    "grid.alpha":        0.5,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.spines.left":  False,
    "axes.spines.bottom": False,
    "axes.titlepad":     14,
    "axes.titlesize":    11,
    "axes.titleweight":  "bold",
    "axes.labelsize":    9,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
})


# ==========================================================
# 5. HELPER FUNCTIONS
# ==========================================================

def card_bg(ax, color=BG_CARD2, radius=0.04):
    """Tambah rounded-rect background di belakang axes."""
    ax.set_facecolor(color)
    for spine in ax.spines.values():
        spine.set_visible(False)

def value_label_h(ax, bars, fmt="{:.1f}", offset=0.05, color=TEXT_PRIMARY, fs=8):
    for bar in bars:
        w = bar.get_width()
        ax.text(
            w + offset, bar.get_y() + bar.get_height() / 2,
            fmt.format(w), va="center", ha="left",
            color=color, fontsize=fs, fontweight="bold"
        )

def value_label_v(ax, bars, fmt="{}", offset=0, color=TEXT_PRIMARY, fs=8):
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + offset,
            fmt.format(h) if isinstance(fmt, str) else fmt(h),
            ha="center", va="bottom",
            color=color, fontsize=fs, fontweight="bold"
        )

def kpi_box(ax, label, value, sub="", color=ACCENT_BLUE):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    # Accent line kiri
    ax.add_patch(
        mpatches.FancyBboxPatch(
            (0, 0), 0.06, 1,
            boxstyle="round,pad=0",
            facecolor=color, edgecolor="none",
            transform=ax.transAxes, clip_on=False
        )
    )
    ax.text(0.14, 0.62, value, transform=ax.transAxes,
            fontsize=22, fontweight="bold", color=TEXT_PRIMARY, va="center")
    ax.text(0.14, 0.28, label, transform=ax.transAxes,
            fontsize=8.5, color=TEXT_SEC, va="center")
    if sub:
        ax.text(0.98, 0.25, sub, transform=ax.transAxes,
                fontsize=7.5, color=color, va="center", ha="right")


# ==========================================================
# 6. LAYOUT
# ==========================================================

fig = plt.figure(figsize=(20, 15))
fig.patch.set_facecolor(BG_DARK)

gs = gridspec.GridSpec(
    4, 3,
    figure=fig,
    hspace=0.52,
    wspace=0.32,
    top=0.90,
    bottom=0.05,
    left=0.06,
    right=0.97,
)

# ── Header ──────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.96,
    "Dashboard Analisis Penjualan HP 2024",
    ha="center", va="center",
    fontsize=22, fontweight="bold", color=TEXT_PRIMARY,
)
fig.text(
    0.5, 0.925,
    "Ringkasan performa penjualan berdasarkan brand, harga, rating, dan tren bulanan",
    ha="center", va="center",
    fontsize=10, color=TEXT_SEC,
)

# Garis separator header
fig.add_artist(
    plt.Line2D([0.06, 0.97], [0.915, 0.915],
               transform=fig.transFigure,
               color=BORDER, linewidth=1)
)


# ==========================================================
# ROW 0 — KPI Cards (4 metric boxes)
# ==========================================================

total_revenue = df["Harga"].sum() / 1e9
total_transaksi = len(df)
avg_harga = df["Harga"].mean() / 1e6
top_brand = revenue_brand.idxmax()

kpi_data = [
    ("Total Revenue",     f"Rp {total_revenue:.1f}B",    "Miliar Rupiah",        ACCENT_BLUE),
    ("Total Transaksi",   f"{total_transaksi:,}",          "Unit terjual",         ACCENT_GREEN),
    ("Rata-rata Harga",   f"Rp {avg_harga:.1f} Jt",       "Per transaksi",        ACCENT_AMBER),
    ("Brand Terbaik",     top_brand,                       "Revenue tertinggi",    ACCENT_PINK),
]

gs_kpi = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs[0, :], wspace=0.04)
for i, (label, val, sub, color) in enumerate(kpi_data):
    ax = fig.add_subplot(gs_kpi[0, i])
    ax.set_facecolor(BG_CARD2)
    for sp in ax.spines.values():
        sp.set_visible(False)
    kpi_box(ax, label, val, sub, color)


# ==========================================================
# ROW 1 — Revenue per Brand (large) | Volume Penjualan | Harga Rata-rata
# ==========================================================

# Chart 1 — Revenue per Brand (horizontal bar)
ax1 = fig.add_subplot(gs[1, 0])
card_bg(ax1)

rev = revenue_brand.sort_values() / 1e9
colors_rev = [PALETTE[i % len(PALETTE)] for i in range(len(rev))]

bars = ax1.barh(rev.index, rev.values, color=colors_rev, height=0.6, zorder=3)
ax1.set_title("Revenue per Brand", loc="left")
ax1.set_xlabel("Miliar Rupiah", color=TEXT_SEC)
ax1.xaxis.grid(True, color=BORDER, alpha=0.6, zorder=0)
ax1.tick_params(left=False)

for bar, val in zip(bars, rev.values):
    ax1.text(
        val + 0.05,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.1f}",
        va="center", ha="left",
        color=TEXT_PRIMARY, fontsize=8, fontweight="bold"
    )


# Chart 2 — Volume Penjualan (vertical bar)
ax2 = fig.add_subplot(gs[1, 1])
card_bg(ax2)

volume = df["Brand"].value_counts()
colors_vol = [PALETTE[i % len(PALETTE)] for i in range(len(volume))]

bars2 = ax2.bar(volume.index, volume.values, color=colors_vol, width=0.6, zorder=3)
ax2.set_title("Volume Penjualan", loc="left")
ax2.yaxis.grid(True, color=BORDER, alpha=0.6, zorder=0)
ax2.tick_params(bottom=False)
plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")

value_label_v(ax2, bars2, fmt="{}", offset=0.5)


# Chart 3 — Harga Rata-rata
ax3 = fig.add_subplot(gs[1, 2])
card_bg(ax3)

avg_price = df.groupby("Brand")["Harga"].mean().sort_values(ascending=False) / 1e6
colors_avg = [PALETTE[i % len(PALETTE)] for i in range(len(avg_price))]

bars3 = ax3.bar(avg_price.index, avg_price.values, color=colors_avg, width=0.6, zorder=3)
ax3.set_title("Harga Rata-rata per Brand", loc="left")
ax3.set_ylabel("Juta Rupiah", color=TEXT_SEC)
ax3.yaxis.grid(True, color=BORDER, alpha=0.6, zorder=0)
ax3.tick_params(bottom=False)
plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")

value_label_v(ax3, bars3, fmt=lambda v: f"{v:.1f}", offset=0.1)


# ==========================================================
# ROW 2 — Tren Bulanan | Distribusi Rating | Metode Pembayaran
# ==========================================================

# Chart 4 — Tren Bulanan
ax4 = fig.add_subplot(gs[2, 0])
card_bg(ax4)

bulan_label = ["Jan","Feb","Mar","Apr","Mei","Jun",
               "Jul","Agu","Sep","Okt","Nov","Des"]
x = np.arange(12)
y = monthly.values

ax4.fill_between(x, y, alpha=0.12, color=ACCENT_BLUE, zorder=2)
ax4.plot(x, y, marker="o", linewidth=2.2, color=ACCENT_BLUE,
         markersize=6, markerfacecolor=BG_CARD, markeredgewidth=2,
         markeredgecolor=ACCENT_BLUE, zorder=4)

# Annotate peak
peak_idx = y.argmax()
ax4.annotate(
    f"  Peak\n  {y[peak_idx]} unit",
    xy=(peak_idx, y[peak_idx]),
    xytext=(peak_idx + 0.5, y[peak_idx] * 1.06),
    color=ACCENT_AMBER, fontsize=7.5,
    arrowprops=dict(arrowstyle="->", color=ACCENT_AMBER, lw=1.2),
)

ax4.set_title("Tren Penjualan Bulanan", loc="left")
ax4.set_xticks(x)
ax4.set_xticklabels(bulan_label, fontsize=7.5)
ax4.yaxis.grid(True, color=BORDER, alpha=0.6)
ax4.tick_params(bottom=False, left=False)


# Chart 5 — Distribusi Rating
ax5 = fig.add_subplot(gs[2, 1])
card_bg(ax5)

rating = df["Rating_pengguna"].value_counts().sort_index()
gradient_colors = [
    "#FF6B6B", "#FF8E3C", "#E3B341",
    "#3FB950", "#2F81F7"
][:len(rating)]

bars5 = ax5.bar(
    rating.index.astype(str), rating.values,
    color=gradient_colors, width=0.55, zorder=3
)
ax5.set_title("Distribusi Rating Pengguna", loc="left")
ax5.set_xlabel("Rating (bintang)", color=TEXT_SEC)
ax5.yaxis.grid(True, color=BORDER, alpha=0.6, zorder=0)
ax5.tick_params(bottom=False, left=False)

value_label_v(ax5, bars5, fmt="{}", offset=0.5)


# Chart 6 — Metode Pembayaran (donut)
ax6 = fig.add_subplot(gs[2, 2])
card_bg(ax6)

payment = df["via_pembayaran"].value_counts()
donut_colors = [PALETTE[i % len(PALETTE)] for i in range(len(payment))]

wedges, texts, autotexts = ax6.pie(
    payment.values,
    labels=None,
    colors=donut_colors,
    autopct="%1.1f%%",
    startangle=90,
    pctdistance=0.78,
    wedgeprops=dict(width=0.55, edgecolor=BG_DARK, linewidth=2),
)

for at in autotexts:
    at.set_color(BG_DARK)
    at.set_fontsize(8)
    at.set_fontweight("bold")

ax6.legend(
    wedges, payment.index,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.18),
    ncol=2,
    fontsize=7.5,
    frameon=False,
    labelcolor=TEXT_SEC,
)
ax6.set_title("Metode Pembayaran", loc="left")


# ==========================================================
# ROW 3 — Scatter Harga vs Rating | Segmentasi HP | Status Stok
# ==========================================================

# Chart 7 — Scatter Harga vs Rating
ax7 = fig.add_subplot(gs[3, 0])
card_bg(ax7)

brands = df["Brand"].unique()
for i, brand in enumerate(brands):
    data = df[df["Brand"] == brand]
    ax7.scatter(
        data["Harga"] / 1e6,
        data["Rating_pengguna"],
        color=PALETTE[i % len(PALETTE)],
        alpha=0.65, s=40, zorder=3, label=brand,
        edgecolors="none",
    )

ax7.set_title("Korelasi Harga vs Rating", loc="left")
ax7.set_xlabel("Harga (Juta Rp)", color=TEXT_SEC)
ax7.set_ylabel("Rating Pengguna", color=TEXT_SEC)
ax7.yaxis.grid(True, color=BORDER, alpha=0.6, zorder=0)
ax7.xaxis.grid(True, color=BORDER, alpha=0.4, zorder=0)
ax7.tick_params(left=False, bottom=False)
ax7.legend(
    fontsize=6.5, frameon=False, labelcolor=TEXT_SEC,
    loc="upper left", ncol=2,
)


# Chart 8 — Segmentasi HP
ax8 = fig.add_subplot(gs[3, 1])
card_bg(ax8)

segment = df["Segmen"].value_counts()
seg_colors = [ACCENT_GREEN, ACCENT_BLUE, ACCENT_PINK][:len(segment)]

bars8 = ax8.bar(segment.index, segment.values, color=seg_colors, width=0.5, zorder=3)
ax8.set_title("Segmentasi Pasar HP", loc="left")
ax8.yaxis.grid(True, color=BORDER, alpha=0.6, zorder=0)
ax8.tick_params(bottom=False, left=False)

value_label_v(ax8, bars8, fmt="{}", offset=0.5)


# Chart 9 — Status Stok (grouped bar)
ax9 = fig.add_subplot(gs[3, 2])
card_bg(ax9)

stock = (
    df.groupby(["Brand", "Stok_tersedia"])
    .size()
    .unstack(fill_value=0)
)

x_pos = np.arange(len(stock.index))
width = 0.35
stock_cols = stock.columns.tolist()
stok_colors = [ACCENT_GREEN, "#FF6B6B"][:len(stock_cols)]

for i, (col, c) in enumerate(zip(stock_cols, stok_colors)):
    offset = (i - len(stock_cols) / 2 + 0.5) * width
    bars9 = ax9.bar(x_pos + offset, stock[col], width, label=str(col), color=c, zorder=3)

ax9.set_title("Status Stok per Brand", loc="left")
ax9.set_xticks(x_pos)
ax9.set_xticklabels(stock.index, rotation=45, ha="right", fontsize=7.5)
ax9.yaxis.grid(True, color=BORDER, alpha=0.6, zorder=0)
ax9.tick_params(bottom=False, left=False)
ax9.legend(
    title="Stok", fontsize=7.5, frameon=False,
    labelcolor=TEXT_SEC, title_fontsize=8
)


# ==========================================================
# FOOTER
# ==========================================================

fig.text(
    0.06, 0.02,
    "Sumber: transaksi.xlsx  ·  Data Penjualan HP 2024",
    fontsize=7.5, color=TEXT_MUTED,
)
fig.text(
    0.97, 0.02,
    "Generated by Python · Matplotlib",
    fontsize=7.5, color=TEXT_MUTED, ha="right",
)


# ==========================================================
# SIMPAN
# ==========================================================

OUTPUT = "dashboard_penjualan_hp.png"
plt.savefig(OUTPUT, dpi=200, bbox_inches="tight", facecolor=BG_DARK)
plt.show()

print("=" * 50)
print(f"✅  Dashboard berhasil disimpan → {OUTPUT}")
print("=" * 50)