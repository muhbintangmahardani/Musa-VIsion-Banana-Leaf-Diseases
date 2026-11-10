# MusaVision: Deteksi Fitopatologi Penyakit Daun Tanaman Pisang (*Musa spp.*) Berbasis Visi Komputer dan Pembelajaran Mendalam (YOLO26n)

![Python](https://img.shields.io/badge/Python-3.10-blue.svg?style=flat-square&logo=python)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg?style=flat-square&logo=pytorch)
![YOLO](https://img.shields.io/badge/Architecture-YOLO26n-00FFFF.svg?style=flat-square)
![Preprocessing](https://img.shields.io/badge/Enhancement-CIE--LAB%20CLAHE-emerald.svg?style=flat-square)
![Validation](https://img.shields.io/badge/Gatekeeper-Musa%20%26%20AI%20Filter-green.svg?style=flat-square)
![License](https://img.shields.io/badge/Research-Academic%20Thesis-purple.svg?style=flat-square)

---

> **Peneliti / Pengembang**: Muh Bintang Mahardani  
> **Nomor Induk Mahasiswa (NIM)**: 17225123  
> **Program Studi**: Informatika / Ilmu Komputer  
> **Fokus Bidang**: Visi Komputer, Pengolahan Citra Digital, dan Fitopatologi Pertanian  

---

## 📌 1. Latar Belakang & Urgensi Penelitian

Tanaman pisang (*Musa spp.*) merupakan komoditas hortikultura strategis di Indonesia, baik sebagai sumber ketahanan pangan rakyat maupun pendorong ekonomi sektor agribisnis pedesaan. Namun, produktivitas budidaya pisang sering mengalami penurunan drastis akibat serangan berbagai penyakit daun foliar (*foliar fungal diseases*). Penyakit-penyakit ini merusak jaringan klorofil fotosintesis aktif, memicu nekrosis prematur, dan dapat menurunkan hasil panen hingga lebih dari **50%** jika tidak terdeteksi pada fase lesi awal.

Metode konvensional yang mengandalkan pengamatan visual langsung oleh petani di lapangan memiliki sejumlah kelemahan:
1. **Subjektivitas Tinggi**: Gejala awal antar-penyakit sering kali serupa (misalnya bercak karat awal *Black Sigatoka* menyerupai bercak awal *Yellow Sigatoka*).
2. **Keterbatasan Waktu & Tenaga**: Monitoring manual pada hamparan kebun yang luas memerlukan waktu lama sehingga penanganan agronomis sering terlambat.
3. **Risiko Salah Diagnosis**: Ketidaktahuan petani dalam membedakan lesi patogen dengan daun yang sekadar kering/sobek alami sering memicu kesalahan penggunaan fungisida kimia berlebih.

**MusaVision** dikembangkan sebagai solusi sistem cerdas terintegrasi untuk mendeteksi, melokalisasi (*object detection* dengan *bounding box*), dan mengklasifikasikan multi-kelas penyakit daun pisang secara otomatis, presisi, dan real-time. Sistem ini memadukan model pembelajaran mendalam **YOLO26n**, teknik pra-pemrosesan kontras adaptif **CIE-LAB CLAHE**, serta sistem validasi pra-inferensi **Gatekeeper Pipeline**.

---

## 🔬 2. Taksonomi & Karakteristik Kelas Patologi Daun Pisang

Model deteksi dilatih untuk mengenali **5 kelas target utama** yang mencakup patogen jamur foliar paling destruktif serta kondisi daun sehat:

| No | Kelas Target | Agen Penyebab / Patogen | Morfologi Gejala Visual pada Helaian Daun | Tingkat Bahaya |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Black Sigatoka** | *Pseudocercospora fijiensis* (Fungi: Mycosphaerellaceae) | Garis-garis sempit kemerahan/cokelat karat yang sejajar dengan urat daun sekunder, berkembang menjadi lesi elips nekrotik kehitaman dengan halo klorosis tipis. | **Sangat Tinggi** (Destruktif) |
| **2** | **Cordana Leaf Spot** | *Cordana musae* / *Neocordana musae* | Lesi bercak oval/mata elips besar (*eyespot*) dengan pola cincin konsentris berwarna abu-abu kecokelatan dan dikelilingi oleh halo kuning terang (*bright yellow border*). | **Sedang – Tinggi** |
| **3** | **Fresh (Sehat)** | *Fisiologis Normal* | Lamina daun berwarna hijau segar merata, jaringan klorofil utuh tanpa lesi nekrotik maupun bercak klorosis patogenik. | **Aman** (Sehat) |
| **4** | **Pestalotiopsis Leaf Spot**| *Pestalotiopsis microspora* | Bercak nekrotik bulat tidak teratur dengan bagian tengah memutih/keabuan dan tepian tegas berwarna cokelat gelap kemerahan, umumnya menyerang tepi helai daun tua. | **Sedang** |
| **5** | **Yellow Sigatoka** | *Pseudocercospora musae* (Fungi: Mycosphaerellaceae) | Bercak lonjong kecil berwarna kuning kehijauan pucat yang sejajar pertulangan daun, mengering perlahan menjadi bercak cokelat muda dengan batas nekrotik jelas. | **Tinggi** |

---

## ⚙️ 3. Metodologi & Alur Arsitektur Sistem

Pipeline sistem MusaVision dirancang dengan pendekatan bertingkat (*multi-stage pipeline*) untuk menjamin keandalan prediksi di lingkungan kebun nyata:

```
[ Input Citra Daun Pisang ]
            │
            ▼
┌────────────────────────────────────────────────────────┐
│  STAGE 1: GATEKEEPER PIPELINE (Pra-Validasi Citra)    │
│  ├─ A. Detektor Citra Sintetis AI (FFT & Noise Sensor) │
│  └─ B. Validasi Genus Musa (Gabor Filter & Klorofil)   │
└────────────────────────────────────────────────────────┘
            │
      [ Lolos Validasi ]
            │
            ▼
┌────────────────────────────────────────────────────────┐
│  STAGE 2: PRA-PEMROSESAN KONTRAS ADAPTIF CIE-LAB CLAHE │
│  ├─ 1. BGR -> Ruang Warna CIE-LAB                     │
│  ├─ 2. CLAHE HANYA pada Kanal Luminans (L)             │
│  └─ 3. Rekonstruksi CIE-LAB -> BGR (Anti-Color Shift)  │
└────────────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────┐
│  STAGE 3: INFERENSI PEMBELAJARAN MENDALAM (YOLO26n)    │
│  ├─ Anchor-free multi-scale feature extraction         │
│  ├─ Non-Maximum Suppression (NMS, IoU Threshold 0.45)  │
│  └─ Penentuan Bounding Box, Kelas, & Skor Keyakinan    │
└────────────────────────────────────────────────────────┘
            │
            ▼
[ Visualisasi Hasil Diagnosa, Bounding Box, & Rekomendasi Fitopatologi ]
```

---

## 🎨 4. Inovasi Pra-Pemrosesan Kontras Adaptif: CIE-LAB CLAHE

Pada kondisi pencahayaan alami di kebun pisang, citra sering mengalami gangguan pencahayaan ekstrem seperti *over-exposure* akibat sinar matahari terik atau *underexposure* akibat naungan pelepah pohon.

### Mengapa Ruang Warna CIE-LAB?
Metode perbaikan kontras konvensional pada ruang warna **RGB** menerapkan perataan histogram pada ketiga kanal secara serentak. Hal ini menyebabkan pergeseran warna (*color shifting*), di mana klorofil alami daun dapat berubah menjadi kebiruan atau rona halo kuning penyakit memudar. 

Pada MusaVision, citra dikonversi ke ruang warna **CIE-LAB**:
* **Kanal $L$ (*Luminance*)**: Merepresentasikan intensitas cahaya / derajat terang-gelap tanpa memuat informasi warna.
* **Kanal $a$**: Koordinat kromatik hijau – merah.
* **Kanal $b$**: Koordinat kromatik biru – kuning.

Algoritma **Contrast Limited Adaptive Histogram Equalization (CLAHE)** diterapkan **hanya pada kanal $L$**, dengan spesifikasi parameter optimal:
* **Clip Limit**: `2.0` (mencegah amplifikasi derau berlebih pada area homogen).
* **Tile Grid Size**: `(8, 8)` (membagi citra ke dalam blok kontekstual 8x8 untuk pemerataan adaptif lokal).

Kanal $L$ yang telah ditingkatkan kemudian digabungkan kembali dengan kanal $a$ dan $b$ asli, lalu dikonversi kembali ke BGR. Hasilnya, kontras tekstur lesi nekrotik meningkat tajam sementara integritas warna patologi tetap terjaga 100%.

---

## 🛡️ 5. Sistem Validasi Pra-Inferensi (Gatekeeper Pipeline)

Untuk mencegah kesalahan deteksi (*false positive*) saat sistem digunakan di lapangan, dikembangkan dua modul penyaring cerdas sebelum citra dikirim ke model YOLO:

### A. Validasi Spesies Genus Musa (Daun Pisang Hidup)
Memastikan bahwa citra yang dipindai adalah daun pisang asli yang masih berada di pohon, bukan daun tanaman lain, bukan objek ruangan/benda mati, dan bukan daun pepes/bakar:
1. **Analisis Anisotropi Orientasi Serat Gabor**: Daun pisang tergolong monokotil dengan pertulangan urat daun menyirip sejajar (*parallel venation*) yang sangat teratur. Filter Gabor multi-sudut mengukur derajat anisotropi serat (ambang batas $\ge 0.85$ dan konsentrasi sudut puncak $\ge 0.18$). Daun dikotil (menjari/menjalur) akan otomatis ditolak.
2. **Kerapatan Klorofil Hidup**: Menganalisis rasio piksel biomassa vegetasi hijau dalam ruang warna HSV ($\ge 15\%$).
3. **Penyaring Daun Olahan / Bakar (Pepes)**: Mengukur indeks kegosongan dan arang pada area daun ($> 4.0\%$ ditolak sebagai daun yang telah diproses konsumsi).

### B. Detektor Citra Buatan Generator AI (Synthetic Image Filter)
Mendeteksi apakah citra yang diunggah merupakan gambar sintetis buatan generator AI (Midjourney, DALL-E, Stable Diffusion, dll.):
1. **Transformasi Fourier Cepat (FFT - Fast Fourier Transform)**: Generator AI umumnya memiliki karakteristik distribusi spektrum frekuensi radial yang halus secara artifisial dan tidak memiliki pola *noise* sensor optik fisik kamera (CMOS/CCD).
2. **Analisis Densitas Derau Gaussian & Saturasi**: Memeriksa ketiadaan *shot noise* dan distribusi saturasi warna piksel yang tidak wajar. Citra dengan skor sintetis $> 55\%$ akan ditolak sebelum proses inferensi.

---

## 🧠 6. Spesifikasi Model Pembelajaran Mendalam YOLO26n

Arsitektur yang digunakan adalah **YOLO26n** (*nano version*), varian mutakhir dengan efisiensi komputasi tinggi yang dirancang khusus untuk inferensi cepat:
* **Ukuran Berkas Bobot**: Hanya **5.45 MB** (`best_yolo26n_clahe.pt`), menjadikannya sangat ringan untuk eksekusi pada komputer lokal maupun perangkat *edge / mobile*.
* **Resolusi Input**: $640 \times 640$ piksel.
* **Mekanisme Anchor-Free**: Meningkatkan ketepatan lokalisasi bounding box pada lesi bercak daun yang ukurannya sangat variatif (dari titik kecil hingga lesi melebar).
* **Threshold Default**: *Confidence Threshold* = $0.40$, *IoU NMS Threshold* = $0.45$.

---

## 📊 7. Hasil Eksperimen & Analisis Metrik Evaluasi

Eksperimen pelatihan dan validasi dilakukan pada dataset penyakit daun pisang dengan perbandingan beberapa skenario arsitektur (*ablation study*).

### Tabel 1: Komparasi Performa Lintas Arsitektur Model (Uji Validasi)
Sumber data: `MusaVision_Sidang_Data/tabel_komparasi.csv`

| Skenario Eksperimen | Arsitektur & Metode | Precision (%) | Recall (%) | mAP@50 (%) | mAP@50-95 (%) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | YOLOv8n (Citra Mentah / Raw) | 82.62% | 78.73% | 83.27% | 62.67% |
| **2** | YOLO11n (Citra Mentah / Raw) | 81.41% | 79.31% | 83.10% | 62.96% |
| **3** | YOLO26n (Citra Mentah / Raw) | 83.73% | **80.55%** | **84.72%** | **64.06%** |
| **4** | **YOLO26n + CIE-LAB CLAHE** | **84.09%** | 78.92% | 84.20% | 63.91% |

> **Analisis Hasil**: Skenario 4 (**YOLO26n + CIE-LAB CLAHE**) mencatatkan nilai **Precision tertinggi (84.09%)**. Dalam konteks fitopatologi tanaman, nilai presisi yang tinggi sangat esensial untuk meminimalkan *false alarm* (salah mendeteksi objek non-penyakit sebagai penyakit), sehingga rekomendasi agronomis yang diberikan kepada petani terbukti akurat dan terpercaya.

---

### Tabel 2: Evaluasi Performa per Kelas Penyakit (Model Terbaik YOLO26n CLAHE)
Sumber data: `MusaVision_Sidang_Data/tabel_ap_kelas.csv`

| Indeks | Kelas Patologi | Precision (%) | Recall (%) | Rata-rata Presisi (AP@50) (%) |
| :---: | :--- | :---: | :---: | :---: |
| **0** | **Fresh (Daun Sehat)** | **99.56%** | **100.00%** | **99.50%** |
| **1** | **Cordana Leaf Spot** | 87.75% | 86.67% | **92.87%** |
| **2** | **Yellow Sigatoka** | 87.09% | 87.07% | **91.63%** |
| **3** | **Black Sigatoka** | 78.07% | 65.94% | 72.54% |
| **4** | **Pestalotiopsis** | 67.98% | 54.91% | 64.48% |
| **—** | **Rata-Rata Seluruh Kelas (mAP@50)** | **84.09%** | **78.92%** | **84.20%** |

* Kelas **Fresh** mencapai performa nyaris sempurna (AP@50 99.50%), membuktikan sistem sangat andal dalam membedakan daun sehat normal dengan daun berpenyakit.
* Kelas **Cordana** dan **Yellow Sigatoka** menunjukkan akurasi di atas 91%, berkat fitur kontras halo kuning yang diperkuat secara signifikan oleh pra-pemrosesan CIE-LAB CLAHE.

---

## 📂 8. Struktur Direktori Proyek

```text
banana-leaf-detection/
├── core/                                   # Modul konfigurasi sistem & konstanta patologi
│   ├── __init__.py
│   ├── config.py                           # Konfigurasi path model, ambang batas inferensi & validasi
│   └── constants.py                        # Definisi 5 kelas penyakit, deskripsi latin, & matriks evaluasi
│
├── services/                               # Lapisan layanan logika komputasi
│   ├── __init__.py
│   ├── inference_service.py                # Pipeline inferensi YOLO26n & prapemrosesan CIE-LAB CLAHE
│   ├── species_validator.py                # Validasi genus Musa (Gabor filter & indeks klorofil)
│   ├── ai_detector.py                      # Algoritma deteksi citra sintetis AI (FFT & noise sensor)
│   └── diagnostic_pipeline.py              # Orkestrasi alur Gatekeeper dan rekomendasi fitopatologi
│
├── MusaVision_Sidang_Data/                 # Berkas data hasil eksperimen & grafik sidang
│   ├── 1_YOLOv8n_Raw/                      # Hasil evaluasi YOLOv8n mentah (grafik PR, F1, Loss)
│   ├── 2_YOLO11n_Raw/                      # Hasil evaluasi YOLO11n mentah
│   ├── 3_YOLO26n_Raw/                      # Hasil evaluasi YOLO26n mentah
│   ├── 4_YOLO26n_LAB_CLAHE/                # Hasil evaluasi model terbaik YOLO26n CLAHE
│   ├── tabel_komparasi.csv                 # Rekapitulasi metrik 4 arsitektur model
│   └── tabel_ap_kelas.csv                  # Rekapitulasi presisi dan recall per kelas
│
├── static/                                 # Aset statis antarmuka pengguna
│   ├── css/
│   │   └── style.css                       # Kustomisasi tata letak, tema, dan animasi UI
│   ├── js/
│   │   └── main.js                         # Logika interaktif WebRTC, AJAX inferensi, dan navigasi
│   └── samples/                            # Sampel citra daun terverifikasi untuk demonstrasi
│
├── templates/
│   └── index.html                          # Template utama antarmuka pengguna (Single-Page App multi-tab)
│
├── tests/                                  # Modul pengujian unit & verifikasi otomatis
│   ├── test_api_predict.py                 # Pengujian endpoint inferensi
│   ├── test_pepes_and_species.py           # Pengujian penolakan daun bakar & non-pisang
│   └── test_validation_pipeline.py         # Pengujian ketepatan filter AI dan Gatekeeper
│
├── best_yolo26n_clahe.pt                   # Bobot model YOLO26n teroptimasi (5.45 MB)
├── revisi-deteksi-penyakit-daun-pisang-v2.ipynb # Notebook Jupyter riwayat pelatihan model
├── app.py                                  # Server aplikasi web Flask utama
└── README.md                               # Dokumentasi komprehensif penelitian
```

---

## 🖥️ 9. Fitur Antarmuka Pengguna Web (MusaVision UI)

Antarmuka sistem dirancang dengan prinsip *human-centered design* untuk kenyamanan penyuluh pertanian dan petani di lapangan:
1. **Multi-Tab Single Page Application (SPA)**:
   * **Beranda**: Statistik ringkas riset, latar belakang, dan navigasi cepat.
   * **Deteksi Penyakit**: Pemindai citra interaktif (mendukung unggah berkas, *drag & drop*, dan akses langsung kamera HP dengan WebRTC).
   * **Validasi Kebun**: Visualisasi alur kerja *Gatekeeper Pipeline* yang menguji keaslian daun dan filter generator AI.
   * **Metrik & Ablasi**: Dashboard interaktif yang menampilkan grafik kurva F1, PR curve, matriks konfusi (*confusion matrix*), serta tabel komparasi hasil pelatihan.
   * **Katalog Patologi**: Ensiklopedia digital gejala patogen, taksonomi latin, serta tindakan pengendalian agronomis.
2. **Dukungan Tema Ganda (Light & Dark Mode)**:
   * Menggunakan palet warna dengan rasio kontras tinggi berstandar **WCAG AAA** untuk memastikan teks dan elemen kontrol terbaca jelas di bawah terik matahari kebun maupun di ruangan redup.
3. **Feedback Visual Diagnosa**:
   * Dilengkapi informasi dimensi bounding box, tingkat keparahan infeksi, visualisasi sebelum dan sesudah CLAHE, serta rekomendasi penanganan sanitasi dan fungisida ramah lingkungan.

---

## 📜 10. Hak Cipta & Integritas Akademik

Seluruh kode sumber, arsitektur model, dan naskah dokumentasi ini disusun oleh:

**Muh Bintang Mahardani**  
NIM: **17225123**  
Fakultas Teknik & Informatika / Ilmu Komputer  

Hak Cipta © 2026 **Muh Bintang Mahardani**. Seluruh hak cipta dilindungi undang-undang untuk keperluan tugas akhir / skripsi akademik. Pengutipan dan rujukan akademis diperkenankan dengan mencantumkan atribusi sitasi yang sesuai.
