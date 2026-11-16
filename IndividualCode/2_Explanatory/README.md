# JogjaPulse: Understanding the Rhythm and Movement of Yogyakarta

Analisis data spasial dan temporal kehadiran perangkat seluler serta mobilitas antarkapanewon di Daerah Istimewa Yogyakarta (DIY), Desember 2021 – April 2022, berdasarkan dataset agregat **JogjaPulse** (Widyawan, 2026).

Notebook utama menjawab **83 pertanyaan penelitian** dalam 8 kelompok: spasial (S01–S10), temporal (T01–T14), keterwakilan populasi (P01–P10), dinamika harian/bulanan (D01–D08), origin–destination (M01–M15), daya tarik & jaringan (R01–R09), clustering (L01–L08), dan kualitas data (Q01–Q09). Semua tercatat di *insight register*, termasuk 5 pertanyaan yang masih membutuhkan data lokasi wisata.

## Struktur folder

```
jogjapulse/
├── JogjaPulse_Comprehensive_Analysis.ipynb   # notebook utama (sudah dijalankan, output tersimpan)
├── README.md
├── requirements.txt
├── data_dictionary.csv                       # kamus data seluruh kolom 8 CSV
├── data/
│   ├── raw/                                  # 8 CSV + README_dataset.md (JogjaPulse, tidak diubah)
│   └── external/
│       └── diy_kapanewon_boundaries.geojson  # batas 78 kapanewon DIY (lihat "Sumber data")
└── outputs/
    ├── insight_register.csv                  # tabel master seluruh insight
    ├── figures/                              # 8 visualisasi utama (V1–V8) + 4 grafik pendukung (PNG)
    ├── maps/                                 # V1 peta Folium, V2 heatmap & V5 peta aliran OD (HTML interaktif)
    ├── tables/                               # ±30 tabel hasil (CSV)
    └── derived_data/                         # dataset turunan hasil cleaning (CSV / CSV.GZ)
```

## Instalasi

Disarankan memakai virtual environment (Python ≥ 3.10).

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

> Di Windows, `geopandas`/`pyproj` terpasang lancar lewat pip untuk Python 3.10+. Jika gagal, gunakan `conda install -c conda-forge geopandas`.

## Konfigurasi path

Semua path diatur di **satu sel konfigurasi** (Section 0.1 notebook):

```python
PROJECT_DIR = Path.cwd()          # folder tempat notebook dijalankan
RAW_DIR = PROJECT_DIR / "data" / "raw"
EXTERNAL_DIR = PROJECT_DIR / "data" / "external"
OUTPUT_DIR = PROJECT_DIR / "outputs"
```

- Jalankan notebook dari folder `jogjapulse/` agar path relatif bekerja.
- Jika Anda hanya punya ZIP dataset, taruh ZIP di `data/` — notebook mengekstraknya otomatis ke `data/raw/` tanpa mengubah file sumber.
- Periode analisis utama (`HQ_START`, `HQ_END`) dan pembagian waktu (`TIME_PERIODS`) juga diatur di sel yang sama.

## Cara menjalankan

```bash
jupyter lab JogjaPulse_Comprehensive_Analysis.ipynb
```
lalu *Kernel → Restart Kernel and Run All Cells*. Seluruh notebook berjalan ±1 menit dan menulis ulang semua file di `outputs/`. Alternatif tanpa membuka Jupyter:

```bash
jupyter nbconvert --to notebook --execute --inplace JogjaPulse_Comprehensive_Analysis.ipynb
```

Grafik Plotly dan peta interaktif memuat library JavaScript/tile peta dari internet saat **dibuka**, jadi perlu koneksi internet untuk melihatnya.

## Sumber data

| Data | Sumber | Catatan |
|---|---|---|
| Dataset JogjaPulse (8 CSV) | Widyawan (2026). *JogjaPulse: An Aggregated Spatio-Temporal Mobility Dataset for Yogyakarta, Indonesia*. Zenodo. https://doi.org/10.5281/zenodo.23157460 | Agregat 44,4 juta ping dari 594.223 perangkat; suppression k = 5 |
| Batas kapanewon DIY | Repositori publik GitHub `Alf-Anas/batas-administrasi-indonesia`, berkas *Kecamatan SHP* (pembaruan 13 Juni 2023), disaring ke DIY (kode `34.*`) | Kode & nama 78/78 cocok dengan dataset; luas total ±3.168 km². Sumber hulu tidak dinyatakan di repositori. Untuk publikasi resmi, ganti dengan data kalurahan **Geoportal DIY** (https://geoportal.jogjaprov.go.id) yang di-*dissolve* ke kapanewon, simpan dengan nama file yang sama. |
| Libur nasional | Paket Python `holidays` (PyPI) | Cuti bersama tidak tercakup |
| Penduduk kapanewon | Kolom `pop_actual` di dataset (README dataset: BPS; tahun referensi tidak disebutkan) | — |

### Data tambahan opsional (belum tersedia)

1. **Lokasi wisata** → `data/external/tourism_poi_diy.csv` dengan kolom `name,category,lat,lon,source`. Instruksi query Overpass (OpenStreetMap) ada di Section 0.3 notebook. Setelah file ada, pertanyaan S07, T13, D08, R09, L08 otomatis dihitung.
2. **Klasifikasi urban/rural resmi** (Perka BPS No. 120/2020) → `data/external/urban_rural_kapanewon.csv` dengan kolom `kapanewon_code,urban_rural`. Tanpa file ini, notebook memakai **proxy tersil kepadatan penduduk**.

## Metodologi singkat

- **Tidak menjumlahkan `n_maids` sebagai perangkat unik.** Perbandingan memakai *presence share* (porsi kapanewon dari total kehadiran DIY pada jam yang sama), Location Quotient, dan rasio terhadap denominator yang sesuai.
- **Suppression ≠ nol.** Panel lengkap 78 × 151 × 24 dibangun; slot kosong = 0–4 perangkat, diperlakukan sebagai batas bawah dan diuji sensitivitasnya.
- **Periode berkualitas tinggi (Des 2021 – Feb 2022)** untuk kesimpulan kuantitatif; Mar–Apr untuk analisis sensitivitas.
- **Validasi:** notebook mereplikasi angka validasi README (korelasi night presence vs penduduk r = 0,82 linear / 0,70 log-log; model gravitasi R² 0,45–0,58, γ 0,77–0,93; resiprositas r 0,79–0,82).
- Teknik: Getis-Ord Gi\*, Gini/Lorenz, weighted centroid, Mann–Whitney/Kruskal–Wallis/Wilcoxon, OLS (HAC Newey–West), robust z-score, binary segmentation change-point, distance decay & model gravitasi, NetworkX (degree, strength, betweenness, reciprocity), K-means + Ward + PCA + silhouette + ARI.

## Temuan utama (ringkas)

- Aktivitas sangat terkonsentrasi: 5 kapanewon = ±30% kehadiran perangkat; ±60% aktivitas grid dalam radius 10 km dari pusat Kota Yogyakarta (±10% luas DIY). Pola monosentris dengan koridor utara (Depok–Ngaglik–Sleman).
- Mobilitas pendek dan bertetangga: ±60% kunjungan antarwilayah < 10 km, 43% ke kapanewon berbatasan; hubungan umumnya dua arah. Depok adalah magnet & hub jaringan; Wonosari dan Wates menjadi jembatan regional.
- Total aktivitas hampir sama setiap hari, tetapi akhir pekan menggeser aktivitas dari pusat kota ke pinggiran; puncak harian bergeser dari 12.00 ke 19.00.
- Sampel bias urban (keterwakilan kawasan padat ±3,4× kawasan jarang) dan menyusut ±89% hingga April.
- **Temuan kualitas data baru:** 25 sel grid pada titik kisi koordinat 0,1° (artefak presisi rendah, ±9% aktivitas grid) dan dua sel "lengket" (Gondomanan, Sleman) yang tidak ikut turun saat sampel menyusut — memengaruhi beberapa indikator kapanewon dan ditemukan kembali oleh clustering otomatis.

Detail lengkap ada di Section 13 notebook dan `outputs/insight_register.csv`.

## Keterbatasan

Perangkat ≠ penduduk; sampel tidak acak dan bias urban; suppression menghapus unit kecil (Gunungkidul dan malam hari paling terdampak); kualitas data menurun tajam pada Mar–Apr; artefak lokasi tidak dapat dibersihkan dari produk kapanewon × jam; aliran OD adalah jumlah pengunjung, bukan perjalanan, dengan jarak garis lurus; batas wilayah berasal dari mirror publik; urban/rural memakai proxy; data lokasi wisata belum tersedia.

## Sitasi

Widyawan (2026). JogjaPulse: An Aggregated Spatio-Temporal Mobility Dataset for Yogyakarta, Indonesia. Zenodo. https://doi.org/10.5281/zenodo.23157460
