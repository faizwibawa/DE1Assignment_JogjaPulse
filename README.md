# DE1Assignment_JogjaPulse

> Temporary project README — basic info about the assignment and the dataset. Replace/refine as the project matures.

Analytics and visualization assignment for the **Data Engineering** course, built on the **JogjaPulse** mobility dataset (aggregated mobile-device presence and origin–destination flows for the Special Region of Yogyakarta, DIY). The end deliverable is a **video presentation** in which the team reports the insights drawn from the data.

---

## Assignment

- **Course:** Data Engineering
- **Goal:** explore, clean, integrate, and explain the JogjaPulse dataset; produce analytics + visualizations; infer findings and present them in a video.
- **Stack:** Python in Jupyter Notebooks (so code and visualizations stay together).
- **Team workflow:** a small group handles **cleaning + exploration** (offline, together), and the rest handle **integration** and the **explanatory** analysis. The `IndividualCode/` folders mirror those three stages.

---

## Repo layout

```
DE1Assignment_JogjaPulse/
├── RawDataset/                 # the 8 source CSVs (read-only) + the dataset's own README
├── IndividualCode/
│   ├── 1_ExploreCleaning/      # profiling, cleaning, exploratory analysis
│   ├── 2_Integration/          # merging files, building analysis-ready tables
│   └── 3_Explanatory/           # final analytics, visualizations, narrative
└── README.md                   # this file
```

---

## Dataset at a glance

- **What:** aggregated, privacy-protected counts of mobile devices — presence per grid cell and sub-district (kapanewon), and home-based origin–destination flows between kapanewon.
- **Where:** Special Region of Yogyakarta (DIY), Indonesia.
- **When:** 1 December 2021 – 30 April 2022 (151 days), local time WIB (UTC+7).
- **Source:** derived from ~44.4M GPS pings of ~594k devices. Individual-level data is **not** released.
- **Citation / license:** Widyawan (2026), *JogjaPulse*, Zenodo (doi.org/10.5281/zenodo.23157460). CC BY 4.0.
- **Full documentation:** see `RawDataset/README.md`.

### Files

| File | Content | Rows |
|---|---|---|
| `presence_cell500m_daily.csv` | Distinct devices per 500 m grid cell per day | 183,548 |
| `presence_kapanewon_hourly.csv` | Distinct devices + pings per kapanewon per hour | 230,418 |
| `home_maids_vs_population_kapanewon.csv` | Devices by estimated home kapanewon vs. official population | 78 |
| `validation_night_presence_kapanewon.csv` | Night-time presence per kapanewon (technical validation) | 156 |
| `tier1_summary.csv` | Row/suppression statistics for the two presence products | 2 |
| `od_home_visits_kapanewon_monthly.csv` | Home-based visitation flows between kapanewon per month | 9,894 |
| `od_origin_homes_monthly.csv` | Devices homed per origin kapanewon per month (OD denominators) | 390 |
| `od_summary.csv` | Row/suppression statistics for the OD product | 1 |

### Key columns / concepts

- **`n_maids`** — distinct devices present. **Not additive**: do not sum across cells, kapanewon, hours, or days.
- **`n_pings`** — GPS records; additive; present only in `presence_kapanewon_hourly.csv`.
- **Kapanewon** — sub-district (78 units). `kapanewon_code` (`dd.dd.dd`) is the safe key; the `kapanewon` **name** is not unique (see quirks).
- **Month format** `YYYY-MM`; codes follow the DIY Provincial Government Geoportal boundaries.

---

## Important quirks (read before analysis)

A full automated profile lives in `IndividualCode/1_ExploreCleaning/DatasetProfile.ipynb`. Summary of what it confirmed:

- **The data is clean** — no missing values, no empty cells, no duplicate rows, no format errors; all 151 days present; all cross-file row counts reconcile.
- **"Missing rows" are by design (k = 5 suppression).** A missing row means *fewer than 5 devices*, **not zero**. Do not fill gaps with 0. `presence_cell500m_daily` is ~79% suppressed vs its full grid; `presence_kapanewon_hourly` ~19%.
- **JETIS name collision** — 78 kapanewon *codes* but 77 *names* (JETIS exists in both Bantul and Yogyakarta). Join on `kapanewon_code`, never on name alone. `home_maids_vs_population` and `validation_night_presence` have **no code column** — disambiguate with `(kab_kota, kapanewon)`.
- **Read code columns as strings** — `kab_code` and the OD `*_kab_code` columns load as floats by default; a code like `34.10` would silently become `34.1`. Load with `dtype=str`.
- **Device sample declines over time** (~87k/day → ~9k/day). Normalize before comparing across dates.
- **`reduced_quality = True`** flags lower-quality OD flows for March–April 2022; keep separable for quality-sensitive work.
- **Two different "home" definitions** — full-period home (`home_maids_vs_population`) vs. monthly home (`od_origin_homes_monthly`). Don't conflate.

---

## Getting started

```bash
# Python 3.11 used for this project
python -m pip install pandas nbformat nbconvert ipykernel
```

Open notebooks in `IndividualCode/`. When picking a kernel, select **"JogjaPulse (Py3.11)"** — the default `python3` kernel on this machine points at a missing Miniconda install and will fail to start.

- `IndividualCode/1_ExploreCleaning/DatasetProfile.ipynb` — run this first; it profiles every file and prints a verdict summary.
- `IndividualCode/1_ExploreCleaning/ExplorationNote.ipynb` — personal exploration note.
- `RawDataset/README.md` — the dataset's full, authoritative documentation.
