"""Shared data + canvas for JogjaPulse video assets.
Every map layer is drawn on the SAME 1920x1080 canvas with the SAME extent,
so layers stack pixel-perfect in a video editor."""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap

PROJECT_DIR = Path(os.environ.get("JOGJAPULSE_DIR", "/home/claude/proj/jogjapulse"))
OUT = PROJECT_DIR / "outputs"
TAB, DER = OUT / "tables", OUT / "derived_data"

for f in font_manager.findSystemFonts():
    if "/inter/Inter-" in f:
        font_manager.fontManager.addfont(f)
FONT = "Inter"

INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#d9d8d3"
WHITE = "#ffffff"
BLUE, ORANGE, AQUA, RED = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
CMAP_BLUE = LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUE)

# Two "ink" themes: for placing on a light background vs a dark background
THEMES = {
    "untuk-bg-terang": dict(ink=INK, ink2=INK2, fill="#e8e7e3", edge="#ffffff", kab="#52514e", label_bg="#ffffff"),
    "untuk-bg-gelap": dict(ink="#f4f3ef", ink2="#c9c8c3", fill="#2b2b2e", edge="#141416", kab="#a9a8a3", label_bg="#141416"),
}

mpl.rcParams.update({"font.family": FONT, "font.size": 15, "text.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "xtick.major.size": 0, "ytick.major.size": 0})

W, H, DPI = 16, 9, 120  # 1920x1080

# ---------------- data ----------------
gdf = gpd.read_file(PROJECT_DIR / "data/external/diy_kapanewon_boundaries.geojson")
gdf = gdf.rename(columns={"KODE_KEC": "kapanewon_code"})[["kapanewon_code", "geometry"]].to_crs(32749)
rank = pd.read_csv(TAB / "S02_ranking_78_kapanewon_HQ.csv", dtype={"kapanewon_code": str})
rep = pd.read_csv(TAB / "P_representativeness_table.csv", dtype={"kapanewon_code": str})
clus = pd.read_csv(TAB / "L06_cluster_membership_profile.csv", dtype={"kapanewon_code": str, "cluster": str})
geo = gdf.merge(rank, on="kapanewon_code").merge(rep[["kapanewon_code", "ratio"]], on="kapanewon_code")
geo = geo.merge(clus[["kapanewon_code", "cluster"]], on="kapanewon_code", how="left")
geo["kab"] = geo.kapanewon_code.str[:5]
kab = geo.dissolve("kab").reset_index()
KAB_NAMES = {"34.01": "Kulon Progo", "34.02": "Bantul", "34.03": "Gunungkidul", "34.04": "Sleman", "34.71": "Kota Yogyakarta"}
kab["name"] = kab.kab.map(KAB_NAMES)
cent = geo.set_index("kapanewon_code").geometry.representative_point()
outline = geo.dissolve().boundary

# City centre = centroid of Kota Yogyakarta (as used in distance-ring analysis approx.)
CITY = kab[kab.kab == "34.71"].geometry.iloc[0].centroid

# ---------------- canvas ----------------
minx, miny, maxx, maxy = geo.total_bounds
pad = 0.06
h = (maxy - miny) * (1 + 2 * pad)
w = h * W / H
cx = (minx + maxx) / 2
cy = (miny + maxy) / 2
XLIM = (cx - w / 2, cx + w / 2)
YLIM = (cy - h / 2, cy + h / 2)


def map_canvas():
    """Transparent 1920x1080 figure with one full-bleed axes at the shared extent."""
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.patch.set_alpha(0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(*XLIM); ax.set_ylim(*YLIM); ax.set_aspect("equal")
    ax.set_axis_off(); ax.patch.set_alpha(0)
    return fig, ax


def save_png(fig, path):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, transparent=True)
    plt.close(fig)
    return path
