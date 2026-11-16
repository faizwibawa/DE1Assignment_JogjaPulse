"""Static transparent PNG/SVG assets for the JogjaPulse video."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle
import common as c
import matplotlib.patheffects as pe
KAB_SHIFT = {"34.04": (2000, 9000), "34.02": (-3000, -9000), "34.01": (-4000, -2000), "34.03": (6000, 0)}

OUTDIR = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/viz/assets/out")
M = OUTDIR / "01_peta_dasar"
L = OUTDIR / "02_layer_data_peta"
G = OUTDIR / "03_elemen_grafik"

# ---------- 01 base maps (two ink themes) ----------
for theme, t in c.THEMES.items():
    # filled base
    fig, ax = c.map_canvas()
    c.geo.plot(ax=ax, color=t["fill"], edgecolor=t["edge"], linewidth=0.7)
    c.kab.boundary.plot(ax=ax, color=t["kab"], linewidth=1.3)
    c.save_png(fig, M / f"peta_dasar_isi_{theme}.png")
    # outline only: kapanewon + kabupaten
    fig, ax = c.map_canvas()
    c.geo.boundary.plot(ax=ax, color=t["kab"], linewidth=0.6, alpha=0.6)
    c.kab.boundary.plot(ax=ax, color=t["kab"], linewidth=1.4)
    c.save_png(fig, M / f"peta_dasar_garis_{theme}.png")
    fig, ax = c.map_canvas()
    c.geo.boundary.plot(ax=ax, color=t["kab"], linewidth=0.6, alpha=0.6)
    c.kab.boundary.plot(ax=ax, color=t["kab"], linewidth=1.4)
    p = M / f"peta_dasar_garis_{theme}.svg"
    fig.savefig(p, transparent=True); plt.close(fig)
    # kabupaten only
    fig, ax = c.map_canvas()
    c.kab.boundary.plot(ax=ax, color=t["kab"], linewidth=1.6)
    c.save_png(fig, M / f"peta_kabupaten_saja_{theme}.png")
    # province silhouette
    fig, ax = c.map_canvas()
    c.geo.dissolve().plot(ax=ax, color=t["fill"])
    c.save_png(fig, M / f"siluet_diy_{theme}.png")
    # kabupaten name labels
    fig, ax = c.map_canvas()
    offs = {"34.71": (0, 0)}
    for _, r in c.kab.iterrows():
        p = r.geometry.representative_point()
        if r.kab == "34.71":
            ax.annotate(r["name"], (p.x, p.y), xytext=(-150, -170), textcoords="offset points", ha="center",
                        fontsize=17, fontweight="bold", color=t["ink"],
                        arrowprops=dict(arrowstyle="-", color=t["ink2"], lw=1.2))
        else:
            dx, dy = KAB_SHIFT.get(r.kab, (0, 0))
            ax.text(p.x + dx, p.y + dy, r["name"].upper(), ha="center", va="center", fontsize=19,
                    fontweight="bold", color=t["ink"],
                    path_effects=[pe.withStroke(linewidth=5, foreground=t["label_bg"], alpha=0.85)])
    c.save_png(fig, M / f"label_kabupaten_{theme}.png")

# ---------- 02 data layers (same extent) ----------
def fill_layer(column, cmap, norm, name):
    fig, ax = c.map_canvas()
    c.geo.plot(ax=ax, column=column, cmap=cmap, norm=norm, edgecolor="#ffffff", linewidth=0.6)
    c.save_png(fig, L / name)

act_norm = LogNorm(0.03, 9)
fill_layer("activity_share_pct", c.CMAP_BLUE, act_norm, "layer_isi_keramaian.png")
c.geo["per100"] = c.geo.ratio * 100
rep_norm = LogNorm(1, 60)
fill_layer("per100", c.CMAP_BLUE, rep_norm, "layer_isi_keterwakilan.png")

fig, ax = c.map_canvas()
ccol = {"1": c.BLUE, "2": c.ORANGE, "3": "#86847d", "0": "#d6d5d0"}
c.geo.plot(ax=ax, color=c.geo.cluster.map(ccol), edgecolor="#ffffff", linewidth=0.6)
c.save_png(fig, L / "layer_isi_klaster.png")

# top-5 highlight only
fig, ax = c.map_canvas()
c.geo[c.geo["rank"] <= 5].plot(ax=ax, color=c.BLUE, edgecolor="#ffffff", linewidth=0.8)
c.save_png(fig, L / "layer_sorot_top5.png")

# label layers (both themes)
offs = {"DEPOK": (150, 60), "NGAGLIK": (130, 85), "BANGUNTAPAN": (170, -40), "GAMPING": (-170, 70), "KASIHAN": (-170, -50)}
for theme, t in c.THEMES.items():
    fig, ax = c.map_canvas()
    for _, r in c.geo[c.geo["rank"] <= 5].iterrows():
        p = r.geometry.representative_point()
        ax.plot(p.x, p.y, "o", ms=6, color=t["label_bg"], mec=t["ink"], mew=1.2)
        ax.annotate(f"{r.label.title()} {r.activity_share_pct:.1f}%".replace(".", ","), (p.x, p.y),
                    xytext=offs[r.label], textcoords="offset points", ha="center", va="center",
                    fontsize=14, fontweight="bold", color=t["ink"],
                    bbox=dict(boxstyle="round,pad=0.3", fc=t["label_bg"], ec="none", alpha=0.92),
                    arrowprops=dict(arrowstyle="-", color=t["ink"], lw=1))
    c.save_png(fig, L / f"label_top5_{theme}.png")

# OD flows + nodes
od = pd.read_csv(c.DER / "od_enriched.csv", dtype={"origin_code": str, "dest_code": str})
hqm = od[(od.month <= "2022-02") & (~od.is_self)]
fl = hqm.groupby(["origin_code", "dest_code"], as_index=False).n_maids.mean()
fl["a"] = fl[["origin_code", "dest_code"]].min(axis=1); fl["b"] = fl[["origin_code", "dest_code"]].max(axis=1)
pairs = fl.groupby(["a", "b"], as_index=False).n_maids.sum().nlargest(200, "n_maids")
pairs.to_csv("/tmp/pairs.csv", index=False)
w = pairs.n_maids.values
lw = 0.6 + 6 * (w - w.min()) / (w.max() - w.min())
o = np.argsort(w)
segs = [[(c.cent[a].x, c.cent[a].y), (c.cent[b].x, c.cent[b].y)] for a, b in zip(pairs.a, pairs.b)]
for theme, col in [("untuk-bg-terang", c.BLUE), ("untuk-bg-gelap", "#9ec5f4")]:
    fig, ax = c.map_canvas()
    ax.add_collection(LineCollection([segs[i] for i in o], linewidths=lw[o], colors=col, alpha=0.6, capstyle="round"))
    c.save_png(fig, L / f"layer_garis_aliran_kunjungan_{theme}.png")
inflow = (hqm.groupby("dest_code").n_maids.sum() / 3).reindex(c.cent.index).fillna(0)
fig, ax = c.map_canvas()
ax.scatter([p.x for p in c.cent], [p.y for p in c.cent], s=12 + 900 * inflow.values / inflow.max(),
           color=c.ORANGE, edgecolor="#ffffff", linewidth=1.5)
c.save_png(fig, L / "layer_titik_pengunjung.png")

# distance rings from city centre
for theme, t in c.THEMES.items():
    fig, ax = c.map_canvas()
    for r in [5, 10, 20]:
        ax.add_patch(Circle((c.CITY.x, c.CITY.y), r * 1000, fill=False, ec=t["ink"], lw=1.6 if r == 10 else 1.1,
                            ls="-" if r == 10 else (0, (5, 4)), alpha=0.9))
        ax.text(c.CITY.x, c.CITY.y + r * 1000, f"{r} km", ha="center", va="bottom", fontsize=13,
                color=t["ink"], fontweight="bold" if r == 10 else "normal")
    ax.plot(c.CITY.x, c.CITY.y, "o", ms=9, color=c.RED, mec=t["label_bg"], mew=2)
    c.save_png(fig, L / f"layer_lingkar_jarak_{theme}.png")

# ---------- legends (light + dark ink) ----------
def colorbar_png(norm, ticks, ticklabels, title, name):
    for theme, t in c.THEMES.items():
        fig = plt.figure(figsize=(5, 1.1), dpi=c.DPI); fig.patch.set_alpha(0)
        cax = fig.add_axes([0.04, 0.35, 0.92, 0.2])
        cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=c.CMAP_BLUE), cax=cax, orientation="horizontal")
        cb.set_ticks(ticks); cb.set_ticklabels(ticklabels); cb.outline.set_visible(False)
        cb.ax.tick_params(labelsize=13, colors=t["ink2"])
        cax.set_title(title, fontsize=14, color=t["ink"], loc="left")
        c.save_png(fig, L / f"legenda_{name}_{theme}.png")

colorbar_png(act_norm, [0.05, 0.1, 0.5, 1, 5], ["0,05%", "0,1%", "0,5%", "1%", "5%"], "Porsi keramaian (skala log)", "keramaian")
colorbar_png(rep_norm, [1, 3, 10, 30], ["1", "3", "10", "30"], "Perangkat per 100 penduduk", "keterwakilan")

# ---------- 03 chart elements (no titles, transparent) ----------
def chart_fig(rect=(0.12, 0.12, 0.82, 0.8)):
    fig = plt.figure(figsize=(c.W, c.H), dpi=c.DPI); fig.patch.set_alpha(0)
    ax = fig.add_axes(rect); ax.patch.set_alpha(0)
    return fig, ax

def style(ax, t, grid_y=True):
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(t["ink2"]); ax.spines[s].set_alpha(0.4)
    ax.tick_params(colors=t["ink2"], labelsize=16)
    if grid_y:
        ax.yaxis.grid(True, color=t["ink2"], alpha=0.18); ax.set_axisbelow(True); ax.spines["left"].set_visible(False)

hq = pd.read_csv(c.DER / "kapanewon_hourly_panel.csv.gz", dtype={"kapanewon_code": str})
hq = hq[hq.hq]
dh = hq.groupby(["date", "hour", "day_type"], as_index=False).n_maids.sum()
dh["idx"] = dh.n_maids / dh.groupby("date").n_maids.transform("mean")
prof = dh.groupby(["day_type", "hour"]).idx.mean().unstack(0)
prof.to_csv("/tmp/prof.csv")
rings = pd.read_csv(c.TAB / "S04_distance_rings.csv")
net = pd.read_csv(c.TAB / "R_network_metrics_HQ.csv")
dq = pd.read_csv(c.DER / "daily_quality.csv", parse_dates=["date"]).sort_values("date")
dq["idx"] = dq.device_hours / dq[dq.month == "2021-12"].device_hours.mean() * 100
DAYC = {"Hari kerja": c.BLUE, "Akhir pekan": c.ORANGE, "Libur nasional": c.AQUA}

for theme, t in c.THEMES.items():
    # ranking bars
    fig, ax = chart_fig((0.2, 0.06, 0.72, 0.88))
    tt = c.rank.nsmallest(10, "rank").iloc[::-1]
    ax.barh([f"{int(r)}. {l.title()}" for r, l in zip(tt["rank"], tt.label)], tt.activity_share_pct,
            color=[c.BLUE if r <= 5 else "#86b6ef" for r in tt["rank"]], height=0.72)
    for i, v in enumerate(tt.activity_share_pct):
        ax.text(v + 0.08, i, f"{v:.2f}%".replace(".", ","), va="center", fontsize=17, color=t["ink"])
    ax.set_xticks([]); [ax.spines[s].set_visible(False) for s in ["left", "bottom"]]
    ax.tick_params(axis="y", labelsize=18, colors=t["ink"])
    c.save_png(fig, G / f"batang_top10_kapanewon_{theme}.png")

    # distance rings lines
    fig, ax = chart_fig()
    rr = pd.concat([pd.DataFrame({"radius_km": [0], "activity_share_pct": [0], "area_share_pct": [0],
                                  "population_share_pct_(centroid_kapanewon)": [0]}), rings])
    for col, nm, cc in [("activity_share_pct", "Aktivitas perangkat", c.BLUE),
                        ("population_share_pct_(centroid_kapanewon)", "Penduduk", c.ORANGE),
                        ("area_share_pct", "Luas wilayah", c.AQUA)]:
        ax.plot(rr.radius_km, rr[col], color=cc, lw=3.5, marker="o", ms=9, mec="#ffffff", mew=2, label=nm)
    ax.axvline(10, color=t["ink2"], lw=1.2, ls=(0, (4, 4)))
    ax.set_xticks([0, 10, 20, 30, 40, 60], ["0", "10 km", "20 km", "30 km", "40 km", "60 km"])
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"]); ax.set_ylim(0, 105)
    style(ax, t); leg = ax.legend(loc="lower right", frameon=False, fontsize=17, labelcolor=t["ink"])
    c.save_png(fig, G / f"garis_jarak_pusat_kota_{theme}.png")

    # hourly rhythm
    fig, ax = chart_fig()
    for d in prof.columns:
        ax.plot(prof.index, prof[d], color=DAYC[d], lw=3.5, label=d)
    ax.axhline(1, color=t["ink2"], lw=1, ls=(0, (4, 4)))
    ax.set_xticks(range(0, 24, 3), [f"{h:02d}.00" for h in range(0, 24, 3)]); ax.set_xlim(-0.3, 23.3)
    style(ax, t); ax.legend(loc="upper left", frameon=False, fontsize=17, labelcolor=t["ink"])
    c.save_png(fig, G / f"garis_ritme_24jam_{theme}.png")

    # betweenness bars
    fig, ax = chart_fig((0.2, 0.06, 0.72, 0.88))
    nb = net.nlargest(8, "betweenness").iloc[::-1]
    ax.barh([l.title() for l in nb.label], nb.betweenness, color=[c.BLUE if l == "DEPOK" else "#86b6ef" for l in nb.label], height=0.68)
    for i, v in enumerate(nb.betweenness):
        ax.text(v + 0.008, i, f"{v:.2f}".replace(".", ","), va="center", fontsize=17, color=t["ink"])
    ax.set_xticks([]); [ax.spines[s].set_visible(False) for s in ["left", "bottom"]]
    ax.tick_params(axis="y", labelsize=18, colors=t["ink"])
    c.save_png(fig, G / f"batang_simpul_jaringan_{theme}.png")

    # data decline
    fig, ax = chart_fig()
    ax.axvspan(pd.Timestamp("2022-03-01"), dq.date.max(), color=c.ORANGE, alpha=0.12, lw=0)
    ax.plot(dq.date, dq.idx, color="#86b6ef", lw=1.3)
    ax.plot(dq.date, dq.idx.rolling(7, center=True, min_periods=1).mean(), color=c.BLUE, lw=3.5)
    ax.set_ylim(0, 140)
    import matplotlib.dates as mdates
    B = {12: "Des 2021", 1: "Jan 2022", 2: "Feb 2022", 3: "Mar 2022", 4: "Apr 2022"}
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, _: B.get(mdates.num2date(x).month, "")))
    ax.set_xlim(dq.date.min(), dq.date.max())
    style(ax, t)
    c.save_png(fig, G / f"garis_penyusutan_data_{theme}.png")

print("done", sum(1 for _ in OUTDIR.rglob("*.png")), "png")
