import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

warnings.filterwarnings("ignore")


# ==========================================================
# 1. LOAD DATA
# ==========================================================

FILE_PATH = "Transaksi_Penjualan_HP_DataSet.xlsx"

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

# Membersihkan tahun rilis
df["Tahun_rilis_clean"] = (
    pd.to_datetime(df["Tahun_rilis"], errors="coerce")
    .dt.year
)

df.loc[
    df["Tahun_rilis_clean"] < 2010,
    "Tahun_rilis_clean"
] = None

# Pastikan tanggal transaksi bertipe datetime
df["tanggal_transaksi"] = pd.to_datetime(
    df["tanggal_transaksi"]
)

# Tambah kolom bulan
df["Bulan"] = df["tanggal_transaksi"].dt.month
df["Bulan_nama"] = df["tanggal_transaksi"].dt.strftime("%b")


# Segmentasi harga
def segmentasi_harga(harga):
    if harga < 5_000_000:
        return "Budget\n(<5 Jt)"
    elif harga < 15_000_000:
        return "Mid-range\n(5-15 Jt)"
    else:
        return "Flagship\n(>15 Jt)"


df["Segmen"] = df["Harga"].apply(segmentasi_harga)

print("=" * 50)
print("HASIL CLEANING")
print("=" * 50)
print(
    "Tahun rilis tidak valid :",
    df["Tahun_rilis_clean"].isna().sum(),
)
print()


# ==========================================================
# 3. ANALISIS
# ==========================================================

print("=" * 50)
print("TOTAL REVENUE PER BRAND")
print("=" * 50)

revenue_brand = (
    df.groupby("Brand")["Harga"]
    .sum()
    .sort_values(ascending=False)
)

print((revenue_brand / 1e9).round(2))
print()


print("=" * 50)
print("RATA-RATA RATING")
print("=" * 50)

print(
    df.groupby("Brand")["Rating_pengguna"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
)
print()


print("=" * 50)
print("TRANSAKSI PER BULAN")
print("=" * 50)

print(df.groupby("Bulan").size())
print()


# ==========================================================
# 4. MEMBUAT DASHBOARD
# ==========================================================

fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor("#F8F9FA")

plt.suptitle(
    "Dashboard Analisis Penjualan HP 2024",
    fontsize=20,
    fontweight="bold"
)

brand_colors = [
    "#2A78D6",
    "#1BAF7A",
    "#E87BA4",
    "#EDA100",
    "#4A3AA7",
    "#EB6834",
    "#E34948",
    "#008300",
    "#D4537E",
    "#3B8BD4",
]

main_color = "#2A78D6"

# ==========================================================
# Chart 1
# Revenue per Brand
# ==========================================================

ax1 = fig.add_subplot(3, 3, 1)

revenue = (
    df.groupby("Brand")["Harga"]
    .sum()
    .sort_values()
    / 1e9
)

bars = ax1.barh(
    revenue.index,
    revenue.values,
    color=brand_colors[: len(revenue)],
)

ax1.set_title("Revenue per Brand")
ax1.set_xlabel("Miliar Rupiah")

for bar, value in zip(bars, revenue.values):
    ax1.text(
        value + 0.1,
        bar.get_y() + bar.get_height() / 2,
        f"{value:.1f}",
        va="center",
    )

ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

# ==========================================================
# Chart 2
# Volume Penjualan
# ==========================================================

ax2 = fig.add_subplot(3, 3, 2)

volume = df["Brand"].value_counts()

bars = ax2.bar(
    volume.index,
    volume.values,
    color=brand_colors[: len(volume)],
)

ax2.set_title("Volume Penjualan")

for bar, value in zip(bars, volume.values):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1,
        str(value),
        ha="center",
    )

plt.setp(ax2.get_xticklabels(), rotation=45)

# ==========================================================
# Chart 3
# Tren Bulanan
# ==========================================================

ax3 = fig.add_subplot(3, 3, 3)

bulan = [
    "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
    "Jul", "Agu", "Sep", "Okt", "Nov", "Des"
]

monthly = (
    df.groupby("Bulan")
    .size()
    .reindex(range(1, 13), fill_value=0)
)

ax3.plot(
    bulan,
    monthly.values,
    marker="o",
    linewidth=2,
    color=main_color,
)

ax3.fill_between(
    range(12),
    monthly.values,
    alpha=0.2,
)

ax3.set_title("Tren Penjualan")

# ==========================================================
# Chart 4
# Distribusi Rating
# ==========================================================

ax4 = fig.add_subplot(3, 3, 4)

rating = (
    df["Rating_pengguna"]
    .value_counts()
    .sort_index()
)

bars = ax4.bar(
    rating.index.astype(str),
    rating.values,
)

ax4.set_title("Distribusi Rating")

for bar, value in zip(bars, rating.values):
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1,
        value,
        ha="center",
    )

# ==========================================================
# Chart 5
# Metode Pembayaran
# ==========================================================

ax5 = fig.add_subplot(3, 3, 5)

payment = df["via_pembayaran"].value_counts()

ax5.pie(
    payment.values,
    labels=payment.index,
    autopct="%1.1f%%",
    startangle=90,
)

ax5.set_title("Metode Pembayaran")

# ==========================================================
# Chart 6
# Harga Rata-rata
# ==========================================================

ax6 = fig.add_subplot(3, 3, 6)

avg_price = (
    df.groupby("Brand")["Harga"]
    .mean()
    .sort_values(ascending=False)
    / 1e6
)

bars = ax6.bar(
    avg_price.index,
    avg_price.values,
)

ax6.set_title("Harga Rata-rata (Juta)")

plt.setp(ax6.get_xticklabels(), rotation=45)

# ==========================================================
# Chart 7
# Scatter Harga vs Rating
# ==========================================================

ax7 = fig.add_subplot(3, 3, 7)

for brand in df["Brand"].unique():
    data = df[df["Brand"] == brand]

    ax7.scatter(
        data["Harga"] / 1e6,
        data["Rating_pengguna"],
        alpha=0.5,
        label=brand,
    )

ax7.legend(fontsize=7)
ax7.set_title("Harga vs Rating")

# ==========================================================
# Chart 8
# Segmentasi
# ==========================================================

ax8 = fig.add_subplot(3, 3, 8)

segment = df["Segmen"].value_counts()

bars = ax8.bar(
    segment.index,
    segment.values,
)

ax8.set_title("Segmentasi HP")

for bar, value in zip(bars, segment.values):
    ax8.text(
        bar.get_x() + bar.get_width() / 2,
        value + 2,
        value,
        ha="center",
    )

# ==========================================================
# Chart 9
# Status Stok
# ==========================================================

ax9 = fig.add_subplot(3, 3, 9)

stock = (
    df.groupby(["Brand", "Stok_tersedia"])
    .size()
    .unstack(fill_value=0)
)

stock.plot(
    kind="bar",
    ax=ax9,
)

ax9.set_title("Status Stok")

plt.tight_layout(rect=[0, 0, 1, 0.96])

plt.savefig(
    "dashboard_penjualan_hp.png",
    dpi=200,
)

plt.show()

print("=" * 50)
print("Dashboard berhasil disimpan")
print("File : dashboard_penjualan_hp.png")
print("=" * 50)