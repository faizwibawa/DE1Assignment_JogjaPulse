# JogjaPulse — Aset Video (tanpa background)

Semua aset 1920×1080, background transparan. **Semua layer peta memakai kanvas & proyeksi yang sama**:
taruh di posisi yang sama (0,0, skala 100%) → otomatis pas bertumpuk. Kalau mau geser/zoom peta,
grup/nest semua layer peta dulu baru digeser.

Varian `untuk-bg-terang` = tinta gelap (dipakai di atas background terang).
Varian `untuk-bg-gelap` = tinta terang (dipakai di atas background gelap).

## 01_peta_dasar
- `peta_dasar_isi_*` — peta DIY kosong (isi abu + batas kapanewon + batas kabupaten)
- `peta_dasar_garis_*` (.png & .svg) — garis batas saja
- `peta_kabupaten_saja_*`, `siluet_diy_*`, `label_kabupaten_*`

## 02_layer_data_peta (taruh DI ATAS peta dasar)
- `layer_isi_keramaian` (F1), `layer_isi_keterwakilan` (F6), `layer_isi_klaster` (F5), `layer_sorot_top5`
- `label_top5_*`, `layer_garis_aliran_kunjungan_*` + `layer_titik_pengunjung` (F7), `layer_lingkar_jarak_*` (F3)
- `legenda_*` — legenda warna (ukuran kecil, posisikan bebas)

## 03_elemen_grafik
Grafik tanpa judul (judul/teks ditambah di editor): batang top-10, garis jarak, ritme 24 jam, simpul jaringan, penyusutan data.

## 04_animasi (30 fps)
| File | Isi | Durasi |
|---|---|---|
| anim_peta_24jam_hari_kerja | peta berubah tiap jam (rata-rata hari kerja), bisa di-loop | 14,4 s |
| anim_jam_penunjuk_* | jam 00.00→23.00 + progress bar, SINKRON dengan peta 24 jam (mulai di frame yang sama) | 14,4 s |
| anim_aliran_kunjungan_* | garis kunjungan tumbuh dari pusat, lalu titik muncul | 7,5 s |
| anim_lingkar_jarak_* | titik pusat kota + lingkar 5/10/20 km melebar (pas di atas peta) | 4,5 s |
| anim_batang_top10_kapanewon_*, anim_batang_simpul_jaringan_* | batang tumbuh + angka menghitung | 4 s |
| anim_garis_ritme_24jam_*, anim_garis_jarak_pusat_kota_*, anim_garis_penyusutan_data_* | garis tergambar kiri→kanan | 6–6,5 s |

Format:
- `.mov` (QuickTime Animation, alpha) → Premiere Pro, DaVinci Resolve, Final Cut, After Effects
- `.webm` (VP9 + alpha) → Canva, browser, editor berbasis web
- `_preview.mp4` → background solid, untuk editor yang tidak mendukung alpha (mis. CapCut)

Animasi peta memakai kanvas yang sama dengan `01_peta_dasar`, jadi tumpuk langsung.
Kode untuk render ulang ada di `05_kode` (set env `JOGJAPULSE_DIR` ke folder `jogjapulse/`).
