# MusaVision — Deteksi Penyakit Daun Tanaman Pisang (*Musa spp.*)

Aplikasi web berbasis kecerdasan buatan (*computer vision*) untuk mendeteksi penyakit foliar pada daun tanaman pisang (*Musa spp.*) menggunakan arsitektur **YOLO26n** yang diintegrasikan dengan pra-pemrosesan kontras adaptif **CIE-LAB CLAHE** dan sistem validasi pra-inferensi (*Gatekeeper Pipeline*).

> **Peneliti / Pengembang**: Muh Bintang Mahardani — 17225123  
> **Fokus Penelitian**: Fitopatologi Pertanian & Visi Komputer (Skripsi)

---

## 🍌 Fitur Utama

1. **Deteksi Multi-Kelas Penyakit Daun Pisang**:
   - *Black Sigatoka* (*Pseudocercospora fijiensis*)
   - *Cordana Leaf Spot* (*Cordana musae*)
   - *Fresh / Sehat* (Daun pisang normal tanpa bercak patogen)
   - *Pestalotiopsis Leaf Spot* (*Pestalotiopsis microspora*)
   - *Yellow Sigatoka* (*Pseudocercospora musae*)

2. **Pipeline Pra-Pemrosesan CIE-LAB CLAHE**:
   - Penajaman kontras adaptif eksklusif pada kanal Luminans ($L$) dalam ruang warna CIE-LAB untuk meminimalisasi pergeseran warna (*anti-color shift*), mempertahankan integritas klorofil alami, dan meningkatkan daya beda lesi nekrotik.

3. **Gatekeeper Pipeline (Validasi Pra-Inferensi)**:
   - **Detektor Citra Sintetis AI**: Menganalisis anomali artefak piksel, saturasi berlebih, dan ketiadaan noise sensor kamera fisik untuk menyaring citra buatan generatif AI.
   - **Validasi Genus Musa (Daun Pisang Hidup)**: Menggunakan analisis ko-orientasi Gabor dan indeks klorofil untuk memastikan objek adalah daun pisang asli di kebun (bukan daun tanaman lain, bukan daun pepes/bakar, dan bukan benda non-tumbuhan).

4. **Antarmuka Web Responsif (Modern & Mobile-First)**:
   - Akses kamera langsung via WebRTC / HTTPS saat pengujian di kebun pisang.
   - Mode Terang (*Light Mode*) dan Gelap (*Dark Mode*) dengan rasio kontras WCAG AAA.
   - Halaman Metrik Evaluasi, Validasi Lapangan, dan Panduan Penyakit terintegrasi.

---

## 📁 Struktur Direktori

```text
├── core/                       # Konfigurasi sistem dan konstanta fitopatologi
│   ├── config.py
│   └── constants.py
├── services/                   # Layanan logika bisnis & pipeline inferensi
│   ├── inference_service.py    # YOLO26n inference + CLAHE pipeline
│   ├── validation_service.py   # Gatekeeper AI & Musa genus validation
│   └── data_service.py         # Parsing metrik evaluasi
├── static/                     # Aset web publik (CSS, JS, ikon, sampel citra)
├── templates/                  # Template HTML Jinja2 (Dashboard, Deteksi, Evaluasi)
├── tests/                      # Unit testing dan validasi otomatis skenario
├── MusaVision_Sidang_Data/     # Aset grafik evaluasi & tabel komparasi model
├── best_yolo26n_clahe.pt       # Bobot model YOLO26n teroptimasi (5.45 MB)
├── app.py                      # Server Flask utama
├── Procfile                    # Konfigurasi entrypoint deployment cloud
├── requirements.txt            # Dependensi Python produksi (CPU-optimized)
└── .gitignore                  # Filter berkas repositori bersih
```

---

## 🚀 Panduan Menjalankan Aplikasi

### 1. Menjalankan di Komputer Lokal

```bash
# 1. Buat dan aktifkan virtual environment (opsional)
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 2. Instal dependensi
pip install -r requirements.txt

# 3. Jalankan server Flask
python app.py
```
Akses di browser melalui `http://127.0.0.1:5000`.

### 2. Deployment ke Cloud (Render.com — 100% Gratis & Otomatis HTTPS)

1. *Push* repositori ini ke akun [GitHub](https://github.com/) Anda.
2. Buka [Render.com](https://render.com/) $\rightarrow$ **Sign In with GitHub**.
3. Klik **New +** $\rightarrow$ **Web Service** $\rightarrow$ Hubungkan ke repositori GitHub proyek ini.
4. Konfigurasikan pengaturan:
   - **Language**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free` ($0 / month)
5. Klik **Deploy Web Service** dan tunggu hingga status menjadi **Live**.
6. Buka URL HTTPS (misal: `https://musavision.onrender.com`) langsung di HP Anda untuk melakukan pengujian langsung di kebun pisang!

---

## ⚖️ Hak Cipta & Lisensi

Hak Cipta © 2026 **Muh Bintang Mahardani (NIM: 17225123)**.  
Seluruh hak cipta dilindungi undang-undang untuk keperluan penelitian akademis Program Studi Informatika / Ilmu Komputer.
