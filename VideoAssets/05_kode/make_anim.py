"""Animated elements with transparent background.
Each animation -> .mov (QuickTime Animation/RLE, alpha; Premiere/DaVinci/Final Cut/After Effects)
               -> .webm (VP9 + alpha; Canva, browsers, CapCut-web)
               -> _preview.mp4 (solid background, plays anywhere)"""
import sys, subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.colors import LogNorm
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path as MPath
import common as c

OUTDIR = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/viz/assets/out") / "04_animasi"
ONLY = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
FPS = 30
BG = {"untuk-bg-terang": "#fcfcfb", "untuk-bg-gelap": "#141416"}


def ease(x):  # easeOutCubic, clipped
    x = np.clip(x, 0, 1)
    return 1 - (1 - x) ** 3


def render(name, fig, update, n_frames, theme="untuk-bg-terang", size=(1920, 1080)):
    OUTDIR.mkdir(parents=True, exist_ok=True)
    w, h = size
    mov = OUTDIR / f"{name}.mov"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                          "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-c:v", "qtrle", "-pix_fmt", "argb", str(mov)],
                         stdin=subprocess.PIPE)
    for i in range(n_frames):
        update(i)
        fig.canvas.draw()
        buf = np.asarray(fig.canvas.buffer_rgba())
        assert buf.shape[:2] == (h, w), buf.shape
        p.stdin.write(buf.tobytes())
    p.stdin.close(); p.wait()
    plt.close(fig)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mov), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                    "-b:v", "0", "-crf", "28", "-row-mt", "1", "-auto-alt-ref", "0", str(OUTDIR / f"{name}.webm")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"color=c={BG[theme]}:s={w}x{h}:r={FPS}",
                    "-i", str(mov), "-filter_complex", "[0][1]overlay=shortest=1,format=yuv420p",
                    "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", str(OUTDIR / f"{name}_preview.mp4")], check=True)
    print("rendered", name, n_frames, "frames")


def want(name):
    return ONLY is None or any(k in name for k in ONLY)


def fig_full(size=(16, 9)):
    fig = plt.figure(figsize=size, dpi=c.DPI); fig.patch.set_alpha(0)
    return fig


def poly_patches(geoms):
    """One PathPatch per kapanewon (handles MultiPolygons) for fast recolouring."""
    patches = []
    for g in geoms:
        polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
        verts, codes = [], []
        for pg in polys:
            for ring in [pg.exterior, *pg.interiors]:
                xy = np.asarray(ring.coords)[:, :2]
                verts += xy.tolist(); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
        patches.append(PathPatch(MPath(verts, codes)))
    return patches


# ======================= A1: peta 24 jam =======================
if want("peta_24jam"):
    panel = pd.read_csv(c.DER / "kapanewon_hourly_panel.csv.gz", dtype={"kapanewon_code": str})
    wk = panel[panel.hq & (panel.day_type == "Hari kerja")]
    m = wk.groupby(["kapanewon_code", "hour"]).n_maids.mean().unstack().reindex(c.geo.kapanewon_code)
    vals = np.log(m.fillna(4).clip(lower=4).values)  # suppressed (<5) -> floor
    norm = mpl.colors.Normalize(np.log(5), np.log(np.nanpercentile(m.values, 99)))
    SEC_PER_HOUR = 0.6
    n = int(24 * SEC_PER_HOUR * FPS)
    fig = fig_full(); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.patch.set_alpha(0)
    ax.set_xlim(*c.XLIM); ax.set_ylim(*c.YLIM); ax.set_aspect("equal")
    pc = PatchCollection(poly_patches(c.geo.geometry), edgecolor="#ffffff", linewidth=0.6)
    ax.add_collection(pc)

    def upd(i):
        t = i / (SEC_PER_HOUR * FPS)  # fractional hour
        h0 = int(t) % 24; h1 = (h0 + 1) % 24; f = t - int(t)
        f = f * f * (3 - 2 * f)  # smoothstep between hours
        v = vals[:, h0] * (1 - f) + vals[:, h1] * f
        pc.set_facecolor(c.CMAP_BLUE(norm(v)))
    render("anim_peta_24jam_hari_kerja", fig, upd, n)

    # matching clock (loops in sync: 0.6 s per hour)
    for theme, t in c.THEMES.items():
        fig = fig_full((5, 1.6)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
        txt = ax.text(0.02, 0.5, "", fontsize=64, fontweight="bold", color=t["ink"], va="center",
                      fontfamily=c.FONT)
        sub = ax.text(0.62, 0.5, "WIB", fontsize=26, color=t["ink2"], va="center")
        bar_bg = ax.add_patch(mpl.patches.Rectangle((0.02, 0.08), 0.9, 0.04, color=t["ink2"], alpha=0.25))
        bar = ax.add_patch(mpl.patches.Rectangle((0.02, 0.08), 0, 0.04, color=c.BLUE))
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)

        def upd(i, txt=txt, bar=bar):
            t_ = i / (SEC_PER_HOUR * FPS)
            txt.set_text(f"{int(t_) % 24:02d}.00")
            bar.set_width(0.9 * t_ / 24)
        render(f"anim_jam_penunjuk_{theme}", fig, upd, n, theme, size=(600, 192))

# ======================= A2: aliran kunjungan =======================
if want("aliran"):
    pairs = pd.read_csv("/tmp/pairs.csv", dtype={"a": str, "b": str}).sort_values("n_maids", ascending=False).reset_index(drop=True)
    od = pd.read_csv(c.DER / "od_enriched.csv", dtype={"origin_code": str, "dest_code": str})
    hqm = od[(od.month <= "2022-02") & (~od.is_self)]
    inflow = (hqm.groupby("dest_code").n_maids.sum() / 3).reindex(c.cent.index).fillna(0)
    w = pairs.n_maids.values
    lw = 0.6 + 6 * (w - w.min()) / (w.max() - w.min())
    A = np.array([[c.cent[a].x, c.cent[a].y] for a in pairs.a])
    B = np.array([[c.cent[b].x, c.cent[b].y] for b in pairs.b])
    # draw from the busier end (Depok etc.) outward
    swap = inflow.reindex(pairs.a).values < inflow.reindex(pairs.b).values
    A[swap], B[swap] = B[swap].copy(), A[swap].copy()
    start = np.linspace(0, 2.6, len(pairs))  # heaviest first
    DUR, NODE_T0, TOTAL = 1.2, 3.4, 7.5
    sizes = 12 + 900 * inflow.values / inflow.max()
    order_nodes = np.argsort(-inflow.values)
    node_start = NODE_T0 + np.linspace(0, 1.2, len(sizes))[np.argsort(order_nodes)]
    for theme, col in [("untuk-bg-terang", c.BLUE), ("untuk-bg-gelap", "#9ec5f4")]:
        fig = fig_full(); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.patch.set_alpha(0)
        ax.set_xlim(*c.XLIM); ax.set_ylim(*c.YLIM); ax.set_aspect("equal")
        lc = LineCollection([], linewidths=lw, colors=col, alpha=0.6, capstyle="round"); ax.add_collection(lc)
        sc = ax.scatter([p.x for p in c.cent], [p.y for p in c.cent], s=np.zeros(len(sizes)),
                        color=c.ORANGE, edgecolor="#ffffff", linewidth=1.5, zorder=3)

        def upd(i, lc=lc, sc=sc):
            t = i / FPS
            k = ease((t - start) / DUR)[:, None]
            E = A + (B - A) * k
            lc.set_segments([[tuple(a), tuple(e)] for a, e in zip(A, E)])
            lc.set_linewidths(np.where(k[:, 0] > 0, lw, 0))
            g = ease((t - node_start) / 0.5)
            sc.set_sizes(sizes * g)
        render(f"anim_aliran_kunjungan_{theme}", fig, upd, int(TOTAL * FPS), theme)

# ======================= A3: lingkar jarak =======================
if want("lingkar"):
    for theme, t in c.THEMES.items():
        fig = fig_full(); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off(); ax.patch.set_alpha(0)
        ax.set_xlim(*c.XLIM); ax.set_ylim(*c.YLIM); ax.set_aspect("equal")
        R = [5, 10, 20]; T0 = [0.5, 1.4, 2.3]
        circ, labs = [], []
        for r in R:
            ci = Circle((c.CITY.x, c.CITY.y), 1, fill=False, ec=t["ink"], lw=2 if r == 10 else 1.3,
                        ls="-" if r == 10 else (0, (5, 4)), alpha=0)
            ax.add_patch(ci); circ.append(ci)
            labs.append(ax.text(c.CITY.x, c.CITY.y + r * 1000, f"{r} km", ha="center", va="bottom", fontsize=14,
                                fontweight="bold" if r == 10 else "normal", color=t["ink"], alpha=0,
                                path_effects=[pe.withStroke(linewidth=4, foreground=t["label_bg"])]))
        dot, = ax.plot(c.CITY.x, c.CITY.y, "o", ms=0, color=c.RED, mec=t["label_bg"], mew=2)

        def upd(i, circ=circ, labs=labs, dot=dot):
            tt = i / FPS
            dot.set_markersize(10 * ease(tt / 0.4))
            for ci, lb, r, t0 in zip(circ, labs, R, T0):
                k = ease((tt - t0) / 0.9)
                ci.set_radius(max(r * 1000 * k, 1)); ci.set_alpha(0.9 * min(1, k * 2))
                lb.set_alpha(ease((tt - t0 - 0.6) / 0.4))
        render(f"anim_lingkar_jarak_{theme}", fig, upd, int(4.5 * FPS), theme)

# ======================= chart animations =======================
def bar_anim(name, labels, values, colors, fmt, xmax, theme, t):
    fig = fig_full(); ax = fig.add_axes([0.2, 0.06, 0.72, 0.88]); ax.patch.set_alpha(0)
    y = np.arange(len(values))
    bars = ax.barh(y, np.zeros(len(values)), color=colors, height=0.72)
    ax.set_yticks(y, labels); ax.tick_params(axis="y", labelsize=18, colors=t["ink"])
    ax.set_xticks([]); [ax.spines[s].set_visible(False) for s in ["left", "bottom", "top", "right"]]
    ax.set_xlim(0, xmax); ax.set_ylim(-0.6, len(values) - 0.4)
    txts = [ax.text(0, yi, "", va="center", fontsize=17, color=t["ink"]) for yi in y]
    st = np.linspace(0, 1.2, len(values))[::-1]  # top bar first

    def upd(i):
        tt = i / FPS
        for b, tx, v, s in zip(bars, txts, values, st):
            k = ease((tt - s) / 1.1)
            b.set_width(v * k); tx.set_x(v * k + xmax * 0.01)
            tx.set_text(fmt(v * k) if k > 0 else "")
    render(name, fig, upd, int(4 * FPS), theme)


def line_anim(name, xs, series, theme, t, xticks, yticks, ylim, xlim, extra=None, dur=4.5, total=6.0, legend=True):
    fig = fig_full(); ax = fig.add_axes([0.12, 0.12, 0.82, 0.8]); ax.patch.set_alpha(0)
    for s_ in ["left", "bottom"]:
        ax.spines[s_].set_color(t["ink2"]); ax.spines[s_].set_alpha(0.4)
    ax.spines["left"].set_visible(False)
    ax.tick_params(colors=t["ink2"], labelsize=16)
    ax.yaxis.grid(True, color=t["ink2"], alpha=0.18); ax.set_axisbelow(True)
    ax.set_xticks(*xticks); ax.set_yticks(*yticks); ax.set_ylim(*ylim); ax.set_xlim(*xlim)
    if extra: extra(ax)
    xs_num = mdates.date2num(xs) if np.issubdtype(np.asarray(xs).dtype, np.datetime64) else np.asarray(xs, float)
    xf = np.linspace(xs_num[0], xs_num[-1], 600)
    lines = []
    for ys, col, lab, lw_ in series:
        yf = np.interp(xf, xs_num, ys)
        ln, = ax.plot([], [], color=col, lw=lw_, label=lab, solid_capstyle="round"); lines.append((ln, yf))
    if legend:
        leg = ax.legend(loc="upper left", frameon=False, fontsize=17, labelcolor=t["ink"])

    def upd(i):
        k = ease(i / FPS / dur)
        m = max(2, int(k * len(xf)))
        for ln, yf in lines:
            ln.set_data(xf[:m], yf[:m])
        if legend:
            leg.set_alpha(min(1, i / FPS / 0.6))
    render(name, fig, upd, int(total * FPS), theme)


if want("grafik"):
    rank = c.rank.nsmallest(10, "rank").iloc[::-1]
    net = pd.read_csv(c.TAB / "R_network_metrics_HQ.csv").nlargest(8, "betweenness").iloc[::-1]
    prof = pd.read_csv("/tmp/prof.csv", index_col=0)
    rings = pd.read_csv(c.TAB / "S04_distance_rings.csv")
    rr = pd.concat([pd.DataFrame({"radius_km": [0], "activity_share_pct": [0], "area_share_pct": [0],
                                  "population_share_pct_(centroid_kapanewon)": [0]}), rings])
    dq = pd.read_csv(c.DER / "daily_quality.csv", parse_dates=["date"]).sort_values("date")
    dq["idx"] = dq.device_hours / dq[dq.month == "2021-12"].device_hours.mean() * 100
    dq["roll"] = dq.idx.rolling(7, center=True, min_periods=1).mean()
    DAYC = {"Hari kerja": c.BLUE, "Akhir pekan": c.ORANGE, "Libur nasional": c.AQUA}
    B = {12: "Des 2021", 1: "Jan 2022", 2: "Feb 2022", 3: "Mar 2022", 4: "Apr 2022"}
    month_ticks = [pd.Timestamp(x) for x in ["2021-12-01", "2022-01-01", "2022-02-01", "2022-03-01", "2022-04-01"]]

    for theme, t in c.THEMES.items():
        bar_anim(f"anim_batang_top10_kapanewon_{theme}", [f"{int(r)}. {l.title()}" for r, l in zip(rank["rank"], rank.label)],
                 rank.activity_share_pct.values, [c.BLUE if r <= 5 else "#86b6ef" for r in rank["rank"]],
                 lambda v: f"{v:.2f}%".replace(".", ","), 10, theme, t)
        bar_anim(f"anim_batang_simpul_jaringan_{theme}", [l.title() for l in net.label], net.betweenness.values,
                 [c.BLUE if l == "DEPOK" else "#86b6ef" for l in net.label],
                 lambda v: f"{v:.2f}".replace(".", ","), 0.62, theme, t)
        line_anim(f"anim_garis_ritme_24jam_{theme}", prof.index.values,
                  [(prof[d].values, DAYC[d], d, 3.5) for d in prof.columns], theme, t,
                  (range(0, 24, 3), [f"{h:02d}.00" for h in range(0, 24, 3)]),
                  ([0.4, 0.6, 0.8, 1.0, 1.2, 1.4], ["0,4", "0,6", "0,8", "1,0", "1,2", "1,4"]), (0.25, 1.5), (-0.3, 23.3),
                  extra=lambda ax: ax.axhline(1, color=t["ink2"], lw=1, ls=(0, (4, 4))))
        line_anim(f"anim_garis_jarak_pusat_kota_{theme}", rr.radius_km.values,
                  [(rr.activity_share_pct.values, c.BLUE, "Aktivitas perangkat", 3.5),
                   (rr["population_share_pct_(centroid_kapanewon)"].values, c.ORANGE, "Penduduk", 3.5),
                   (rr.area_share_pct.values, c.AQUA, "Luas wilayah", 3.5)], theme, t,
                  ([0, 10, 20, 30, 40, 60], ["0", "10 km", "20 km", "30 km", "40 km", "60 km"]),
                  ([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"]), (0, 105), (0, 61),
                  extra=lambda ax: ax.axvline(10, color=t["ink2"], lw=1.2, ls=(0, (4, 4))))

        def shade(ax, t=t):
            ax.axvspan(mdates.date2num(pd.Timestamp("2022-03-01")), mdates.date2num(dq.date.max()), color=c.ORANGE, alpha=0.12, lw=0)
        line_anim(f"anim_garis_penyusutan_data_{theme}", dq.date.values,
                  [(dq.idx.values, "#86b6ef", "Harian", 1.3), (dq.roll.values, c.BLUE, "Rata-rata 7 hari", 3.5)], theme, t,
                  ([mdates.date2num(x) for x in month_ticks], list(B.values())[:1] + ["Jan 2022", "Feb 2022", "Mar 2022", "Apr 2022"]),
                  ([0, 20, 40, 60, 80, 100, 120, 140], ["0", "20", "40", "60", "80", "100", "120", "140"]), (0, 140),
                  (mdates.date2num(dq.date.min()), mdates.date2num(dq.date.max())), extra=shade, dur=5, total=6.5)
