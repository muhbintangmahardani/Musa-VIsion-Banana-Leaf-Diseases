# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Project: MusaVision v2.2 — Revisi Metodologi, Telemetri Latensi End-to-End, Validasi Agronomi, & Modul Uji Lapangan Perkebunan
**Target Environment:** Local Web Application (Python Flask 3.0 + Ultralytics YOLO + OpenCV + Tailwind CSS + Vanilla JS)
**Primary Model Weight:** `best_yolo26n_clahe.pt` (atau `best_yolo26n_lab_clahe.pt`)
**Objective:** Memperbarui arsitektur backend (`app.py`) dan frontend (`templates/index.html`, `static/js/main.js`) agar selaras 100% dengan standar audit akademik dosen pembimbing serta mendukung pengujian sampel foto lapangan primer dari perkebunan pisang tanpa merusak tata letak UI utama yang sudah berjalan.

---

## 1. KONTEKS & LATAR BELAKANG MASALANG
Berdasarkan audit akademik atas dataset (`jiancedsf/banana-leaf-disaes-detection-8dxpk` v1, CC BY 4.0) dan metodologi eksperimen, ditemukan 8 kebutuhan teknis pada aplikasi web yang wajib diterapkan:
1. **Inkonsistensi Pra-pemrosesan:** CLAHE pada ruang warna RGB berisiko menggeser warna bercak (kuning vs hitam), dan sebelumnya belum diterapkan secara identik pada alur inferensi web (`app.py`).
2. **Bias Granularitas Anotasi pada Fitur "Hitung Lesi":** Median luas bounding box tidak seragam (`Fresh` 79,41%, `Yellow Sigatoka` 50,76% mencakup satu daun penuh, sedangkan `Black Sigatoka` 13,40%, `Cordana` 11,37%, dan `Pestalotiopsis` 2,63% dianotasi per lesi). Menyebut seluruh kotak deteksi sebagai "Jumlah Titik Lesi" adalah keliru secara ilmiah.
3. **Ketiadaan Konteks Latensi End-to-End:** Klaim kecepatan inferensi model (misal 3,7 ms di GPU T4) tidak mencerminkan waktu nyata di aplikasi web lokal (CPU/GPU) yang mencakup decode citra, resize, LAB-CLAHE, inferensi, NMS, hingga render base64/HTTP round-trip.
4. **Pertanggungjawaban Panduan Fungisida:** Saran agronomi dan bahan aktif fungisida wajib mencantumkan rujukan literatur resmi serta banner *disclaimer* bahwa rekomendasi bersifat indikatif awal dan memerlukan validasi Penyuluh Pertanian Lapangan (PPL).
5. **Ketiadaan Komparasi Ablasi & AP Per-Kelas di Dashboard:** Diperlukan tampilan komparasi terkontrol (`YOLOv8n` vs `YOLO11n` vs `YOLO26n Raw` vs `YOLO26n + LAB-CLAHE`) serta tabel **AP per kelas** untuk menganalisis kemiripan visual (*Black vs Yellow Sigatoka* dan *Cordana vs Pestalotiopsis*).
6. **Pencatatan Log Pengujian & Kuesioner SUS:** Diperlukan fitur ekspor CSV atas riwayat pengujian beserta kalkulator *System Usability Scale* (SUS) terintegrasi.
7. **Kebutuhan Validasi Eksternal pada Sampel Perkebunan Pisang (Data Primer):** Dosen pembimbing mewajibkan pengujian menggunakan 15–20 foto daun asli yang diambil langsung di perkebunan pisang. Aplikasi harus memiliki mode pencatatan metadata lapangan (*Ground Truth*, jarak potret, kondisi cahaya) dan menghitung akurasi kecocokan prediksi terhadap *ground truth*.
8. **Transparansi Visual Pra-pemrosesan LAB-CLAHE:** Diperlukan tampilan perbandingan berdampingan (*side-by-side preview*) antara citra asli, citra hasil ekstraksi `CIE-LAB CLAHE (Channel L)`, dan citra hasil deteksi objek.

---

## 2. SPESIFIKASI TEKNIS PER KOMPONEN (TASKS 1 - 8)

### TASK 1: Standarisasi Pipeline Pra-Pemrosesan `LAB-CLAHE` di `app.py`
- **Requirement:** Setiap citra yang masuk ke endpoint `/predict` wajib melewati fungsi `preprocess_lab_clahe(img_bgr, target_size=(640, 640))` sebelum dimasukkan ke `model.predict()` (serta disediakan toggle parameter form `use_clahe=true/false` dengan nilai default `true` agar mendukung demo studi ablasi langsung di web).
- **Spesifikasi Algoritma:**
  1. Resize citra input ke ukuran `640 x 640` piksel menggunakan `cv2.resize(img_bgr, (640, 640), interpolation=cv2.INTER_LINEAR)`.
  2. Jika `use_clahe == True`:
     - Konversi citra dari ruang warna `BGR` ke `CIE-LAB` (`cv2.cvtColor(img_resized, cv2.COLOR_BGR2LAB)`).
     - Pisahkan kanal `L`, `A`, dan `B` (`l, a, b = cv2.split(lab)`).
     - Terapkan `cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))` **HANYA pada kanal Luminans (`L`)** agar informasi kromatis warna kuning (`b`) dan merah-hijau (`a`) tidak mengalami pergeseran warna (*color shift*).
     - Gabungkan kembali `(l_clahe, a, b)` dan konversi kembali ke `BGR`.
- **Output API Tambahan:** Kembalikan string base64 dari citra `raw_resized_base64` (citra 640x640 sebelum CLAHE), `preprocessed_clahe_base64` (citra 640x640 sesudah LAB-CLAHE), dan `annotated_result_base64` (citra hasil gambar bounding box).

### TASK 2: Telemetri Latensi End-to-End & Konteks Perangkat Keras di `app.py` dan `main.js`
- **Requirement:** Ukur waktu eksekusi secara terpisah menggunakan `time.perf_counter()` di dalam endpoint `/predict` dan waktu round-trip HTTP di `main.js`.
- **JSON Payload Baru pada `/predict`:**
  ```json
  {
    "latency_breakdown": {
      "preprocess_ms": 14.62,
      "inference_nms_ms": 74.64,
      "postprocess_encode_ms": 6.15,
      "server_total_ms": 95.41,
      "device_name": "CPU (PyTorch FP32)",
      "input_resolution": "640x640",
      "clahe_mode": "CIE-LAB (Channel L, ClipLimit=2.0, Grid=8x8)",
      "iou_threshold": 0.45,
      "conf_threshold": 0.25
    }
  }
  ```
- **Frontend UI (`index.html` & `main.js`):**
  - Hitung `client_roundtrip_ms` menggunakan `performance.now()` sejak tombol deteksi ditekan hingga respons JSON selesai dirender.
  - Tampilkan **Panel Telemetri Latensi Kontekstual** di dekat hasil deteksi yang memuat:
    - **Perangkat & Format:** (Contoh: `CPU / PyTorch .pt | Input: 640×640`)
    - **Pra-pemrosesan (Resize + LAB-CLAHE):** `X.XX ms`
    - **Inferensi Model + NMS:** `X.XX ms`
    - **Post-processing & Encoding:** `X.XX ms`
    - **Total Server E2E / Total Client E2E:** `X.XX ms / Y.YY ms`

### TASK 3: Koreksi Terminologi "Hitung Lesi" Berdasarkan Granularitas Anotasi
- **Requirement:** Hapus klaim generalisasi "Jumlah Titik Lesi" untuk seluruh kelas. Ubah payung istilah utama di UI menjadi **"Jumlah Wilayah Deteksi (Region Count)"** yang terbagi secara transparan antara *Level Lesi* dan *Level Daun*. Buat pemetaan metadata granularitas per kelas di `app.py` sesuai hasil audit Kaggle:
  - `Pestalotiopsis`: `granularity_type = "Lesion-Level (Bercak Mikro/Lokal, Median Box 2.63%)"`, `count_label = "Titik Bercak Lesi"`
  - `Cordana`: `granularity_type = "Lesion-Level (Bercak Sekunder, Median Box 11.37%)"`, `count_label = "Area Bercak Lesi"`
  - `Black Sigatoka`: `granularity_type = "Patch/Lesion-Level (Klaster Nekrosis, Median Box 13.40%)"`, `count_label = "Klaster Bercak Infeksi"`
  - `Yellow Sigatoka`: `granularity_type = "Leaf/Macro-Level (Cakupan Helai Daun, Median Box 50.76%)"`, `count_label = "Zona Daun Terinfeksi (Bukan Jumlah Lesi Tunggal)"`
  - `Fresh`: `granularity_type = "Leaf-Level (Helai Daun Utuh, Median Box 79.41%)"`, `count_label = "Helai Daun Sehat"`
- **Perhitungan Rasio Luas Kotak (`box_area_ratio_pct`):**
  - Untuk setiap bounding box `[x1, y1, x2, y2]` pada citra `640x640`, hitung persentase luas kotak terhadap luas gambar: `((x2 - x1) * (y2 - y1)) / (640 * 640) * 100`.
  - Tampilkan kolom baru **"Rasio Luas Box (%)"**, **"Kategori Granularitas"**, dan **"Interpretasi Unit Deteksi"** pada tabel rincian deteksi di `index.html`.
  - Ubah judul kartu penghitungan di UI dari *"Jumlah Titik Lesi"* menjadi **"Jumlah Wilayah Deteksi / Region Count (Terpisah: Level Lesi vs Level Daun)"**.

### TASK 4: Revisi Panduan Agronomi, Referensi Resmi, & Banner Disclaimer Pakar
- **Requirement:** Perbarui kamus data rekomendasi agronomi di `app.py` agar setiap kelas menyertakan:
  1. `pathogen_scientific`: Nama ilmiah patogen terkini (*Pseudocercospora fijiensis* untuk Black Sigatoka, *Pseudocercospora musae* untuk Yellow Sigatoka, *Cordana musae* untuk Cordana, *Pestalotiopsis microspora/leprogena* untuk Pestalotiopsis).
  2. `visual_confusion_note`: Catatan pembeda visual terhadap kelas yang mirip:
     - *Black vs Yellow Sigatoka:* Kemiripan fase goresan awal (*streaks*); Black Sigatoka berkembang menjadi bercak hitam pekat di permukaan bawah daun, sedangkan Yellow Sigatoka berupa garis kuning pucat di tepi daun yang mengering menjadi cokelat keabu-abuan.
     - *Cordana vs Pestalotiopsis:* Kemiripan bercak nekrotik berbatas cincin kuning (*yellow halo*); Cordana membentuk bercak oval besar berlapis konsentris menyerupai mata berlian (*diamond eye*), sedangkan Pestalotiopsis berupa bercak kecil ireguler di tepi helai daun yang memicu robekan kering.
  3. `sanitation_protocol`: Prosedur *deleafing* / pemangkasan sanitasi berdasarkan ambang daun sehat minimal (mempertahankan minimal 6–8 helai daun fungsional saat fase pembungaan hingga pengisian tandan buah).
  4. `fungicide_guidance`: Golongan bahan aktif sesuai kode FRAC (Fungisida kontak protektif *Mancozeb* [FRAC M03] atau *Chlorothalonil* [FRAC M05], serta fungisida sistemik *Azoxystrobin* [FRAC 11] / *Difenoconazole* & *Tebuconazole* [FRAC 3] dengan rotasi mode aksi untuk mencegah resistensi) beserta rujukan literatur eksplisit (*Pedoman Budidaya Pisang Kementan RI; Esguera et al., 2024; Cobrado & Fernandez, 2025*).
- **Banner Disclaimer Wajib di UI (`index.html`):**
  - Tambahkan kotak peringatan (*warning callout* berwarna amber/kuning) yang selalu tampil di bawah kartu rekomendasi agronomi:
    > **"PERINGATAN & DISCLAIMER PAKAR:** Informasi penanganan agronomi dan bahan aktif fungisida di atas merupakan **rekomendasi indikatif awal** berdasarkan literatur fitopatologi (*Esguera et al., 2024; Cobrado & Fernandez, 2025; Pedoman Kementan RI*). Sebelum melakukan aplikasi fungisida di lapangan, petani/pengguna **wajib mengonsultasikan dosis dan izin edar pestisida terdaftar** bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya."

### TASK 5: Seksi Dashboard Studi Ablasi, Komparasi Versi YOLO, & Analisis AP Per-Kelas (Data Riil Kaggle)
- **Requirement:** Tambahkan atau perbarui bagian evaluasi ilmiah di `index.html` dan endpoint `/api/model-metrics` di `app.py` (membaca CSV jika ada, atau menggunakan data konstanta eksak hasil Kaggle berikut sebagai *default fallback*):
  1. **Kartu Identitas & Audit Forensik Dataset Sumber:**
     - Sumber asli: *Roboflow Universe `jiancedsf` — Banana Leaf Disease Detection v1 (Lisensi CC BY 4.0)*.
     - Statistik Pembersihan Data (*Data Hygiene*):
       - Total Citra Awal: **6.415 citra** (4.916 citra `640x640` dan 1.499 citra `224x224` yang terkonsentrasi pada kelas *Cordana* [789 citra] dan *Pestalotiopsis* [710 citra]).
       - Penghapusan Anomali Label (`black-` berlabel *Yellow Sigatoka*): **-93 citra** (tersisa 6.322).
       - Penghapusan File Augmentasi Hulu (`_aug`): **-709 citra** (498 train, 131 valid, 80 test -> tersisa 5.613 citra murni).
       - Deduplikasi *Perceptual Hash* (`dHash` jarak Hamming $\le 3$ bit): **-355 citra duplikat**.
       - **Total Dataset Bersih Bebas Bocor:** **5.258 citra** (Diseragamkan ke `640x640`, dibagi ulang secara *stratified* 70:20:10 menjadi **3.679 Train | 1.051 Valid | 528 Test**).
  2. **Tabel 1: Komparasi Global Antar-Arsitektur & Studi Ablasi CLAHE (Split Test - 528 Citra):**
     - `1_YOLOv8n_Clean_NoCLAHE`: Parameter **3,13 Juta** (8,6 GFLOPs) | Precision **83,95%** | Recall **79,02%** | F1-Score **81,41%** | mAP@50 **77,08%** | mAP@50-95 **57,35%** | Inferensi GPU T4 **4,03 ms**.
     - `2_YOLO11n_Clean_NoCLAHE`: Parameter **2,60 Juta** (6,4 GFLOPs) | Precision **82,18%** | Recall **80,72%** | F1-Score **81,44%** | mAP@50 **76,58%** | mAP@50-95 **57,70%** | Inferensi GPU T4 **3,92 ms**.
     - `3_YOLO26n_Clean_NoCLAHE`: Parameter **2,39 Juta** (5,4 GFLOPs) | Precision **82,72%** | Recall **81,00%** | F1-Score **81,85%** | mAP@50 **78,23%** | mAP@50-95 **58,32%** | Inferensi GPU T4 **3,89 ms**.
     - `4_YOLO26n_Clean_LAB_CLAHE (Proposed)`: Parameter **2,39 Juta** (5,4 GFLOPs) | **Precision 84,62% (Tertinggi)** | Recall **79,73%** | **F1-Score 82,10% (Tertinggi)** | mAP@50 **77,84%** | mAP@50-95 **58,24%** | Inferensi GPU T4 **3,90 ms**.
  3. **Tabel 2: Rincian AP Per-Kelas pada Model Terbaik (`YOLO26n + LAB-CLAHE`) & Analisis Granularitas:**
     - `Fresh`: Precision **100,00%** | Recall **100,00%** | AP@50 **99,50%** | AP@50-95 **92,99%** | Median Luas Box **79,41%** (1.420 instance).
     - `Yellow Sigatoka`: Precision **93,73%** | Recall **90,32%** | AP@50 **88,44%** | AP@50-95 **60,90%** | Median Luas Box **50,76%** (1.711 instance).
     - `Cordana`: Precision **87,01%** | Recall **84,40%** | AP@50 **84,70%** | AP@50-95 **68,87%** | Median Luas Box **11,37%** (2.450 instance).
     - `Black Sigatoka`: Precision **79,42%** | Recall **69,13%** | AP@50 **68,41%** | AP@50-95 **34,99%** | Median Luas Box **13,40%** (2.622 instance).
     - `Pestalotiopsis`: Precision **62,94%** | Recall **54,81%** | AP@50 **48,15%** | AP@50-95 **33,44%** | Median Luas Box **2,63%** (4.527 instance — *AP terendah berbanding lurus dengan ukuran lesi mikro 2,63% dan kemiripan visual terhadap Cordana*).
  4. **Tabel 3: Benchmark Latensi Kontekstual End-to-End (GPU vs CPU):**
     - `GPU (NVIDIA Tesla T4 - PyTorch FP32/AMP 640x640)`: Rata-rata Pra-pemrosesan LAB-CLAHE **12,44 ms** | Rata-rata Inferensi + NMS **11,76 ms** | Total Latensi Pipeline **24,21 ms**.
     - `CPU (Intel Xeon / Local Web - PyTorch FP32 640x640)`: Rata-rata Pra-pemrosesan LAB-CLAHE **14,62 ms** | Rata-rata Inferensi + NMS **74,64 ms** | Total Latensi Pipeline **89,27 ms**.

### TASK 6: Fitur Pencatat Log Pengujian Sesi & Form Evaluasi Kegunaan (SUS)
- **Requirement:** Untuk memudahkan pengumpulan bukti pengujian Bab IV:
  1. **Log Pengujian Sesi Umum:** Menyimpan riwayat setiap gambar yang diuji di memori/localStorage dan tabel UI, lengkap dengan tombol **"Export Log Pengujian (.CSV)"** dan **"Reset Log"**.
  2. **Kalkulator / Modal Uji Kegunaan (System Usability Scale - SUS):** Sediakan modal atau seksi interaktif berisi 10 pernyataan standar SUS Bahasa Indonesia (skala Likert 1–5), input Nama/Peran Responden (misal: *Petani Pisang / Penyuluh / Mahasiswa*), yang otomatis menghitung skor SUS responden (`((jumlah skor ganjil - 5) + (25 - jumlah skor genap)) * 2.5`), menampilkan rata-rata skor SUS seluruh responden beserta predikatnya (*Acceptable / Good / Excellent*), dan memiliki tombol **"Export Hasil SUS (.CSV)"**.

### TASK 7 [BARU]: Modul Validasi Lapangan Eksternal (Sampel Perkebunan Pisang / Data Primer)
- **Requirement:** Untuk memenuhi instruksi dosen pembimbing terkait pengujian pada 15–20 foto daun pisang asli yang diambil langsung di perkebunan:
  1. **Panel Input Metadata Lapangan (Field Validation Form):** Di dekat area upload gambar pada `index.html`, sediakan *card/accordion* opsional **"Mode Validasi Sampel Kebun (Data Primer Bab IV)"** yang berisi:
     - **Sumber Citra (`source_origin`):** Pilihan `Sampel Perkebunan Pisang (Data Primer)` atau `Dataset Uji Publik (Roboflow)`.
     - **Label Asli / Ground Truth (`ground_truth`):** Dropdown (`Belum Diketahui / Tanpa Ground Truth`, `Fresh`, `Black Sigatoka`, `Yellow Sigatoka`, `Cordana`, `Pestalotiopsis`).
     - **Jarak Akuisisi Foto (`capture_distance`):** Dropdown (`Close-up Lesi (15-30 cm)`, `Jarak Sedang / Setengah Daun (30-80 cm)`, `Makro / Helai Daun Utuh (>80 cm)`).
     - **Kondisi Pencahayaan Kebun (`lighting_condition`):** Dropdown (`Cerah Pagi/Sore (Optimal)`, `Siang Terik (Silau/Glare)`, `Berawan / Teduh Bawah Kanopi`).
     - **Lokasi / Catatan Kebun (`field_notes`):** Input teks singkat (misal: *"Kebun Pisang Warga - Sampel Pohon #3"*).
  2. **Evaluasi Kecocokan Otomatis (`ground_truth_match`):**
     - Saat hasil prediksi keluar dan pengguna memilih `ground_truth` (selain *Belum Diketahui*), bandingkan apakah `ground_truth` terdapat di dalam daftar kelas yang berhasil dideteksi model (atau cocok dengan kelas ber-confidence tertinggi).
     - Tampilkan badge status: **`✅ SESUAI (True Positive)`** (hijau) atau **`❌ TIDAK SESUAI (Misclassified / False Negative)`** (merah).
  3. **Ringkasan Statistik Uji Lapangan & Ekspor CSV Bab IV:**
     - Pada tabel Log Pengujian Lapangan, tampilkan kartu ringkasan *real-time*: **Total Sampel Kebun Diuji**, **Jumlah Prediksi Sesuai**, **Akurasi Validasi Lapangan (%)**, dan **Rata-rata Latensi E2E (ms)**.
     - Saat tombol **"Export Log Uji Lapangan (.CSV)"** ditekan, hasilkan file CSV dengan kolom lengkap: `No, Timestamp, Nama_File, Sumber_Citra, Lokasi_Kebun, Jarak_Foto, Kondisi_Cahaya, Mode_CLAHE, Ground_Truth_Asli, Prediksi_Utama_Model, Status_Kecocokan, Confidence_Tertinggi_Pct, Jumlah_Wilayah_Deteksi, Rasio_Luas_Box_Rata2_Pct, Latensi_Preprocess_ms, Latensi_Inference_ms, Latensi_Total_Server_ms, Latensi_Client_E2E_ms`.

### TASK 8 [BARU]: Visualisasi Side-by-Side (Citra Asli vs Filter CIE-LAB CLAHE vs Deteksi Box)
- **Requirement:** Agar pengguna dan dosen penguji dapat memverifikasi secara visual bahwa `CIE-LAB CLAHE` hanya meningkatkan kontras bercak pada kanal Luminans (`L`) tanpa merusak warna kuning/hitam daun:
  1. Pada area hasil deteksi di `index.html`, tampilkan **3 Tab / Grid Perbandingan Visual**:
     - **Panel 1: Citra Input (640×640 Raw)** — Menampilkan gambar asli sebelum peningkatan kontras.
     - **Panel 2: Citra Pra-pemrosesan (CIE-LAB CLAHE Kanal L)** — Menampilkan gambar hasil ekualisasi histogram adaptif dari backend (`preprocessed_clahe_base64`).
     - **Panel 3: Hasil Deteksi Objek (YOLO26n Bounding Box)** — Menampilkan hasil akhir dengan kotak deteksi dan label.
  2. Sediakan *toggle switch* **`Gunakan Pra-pemrosesan CIE-LAB CLAHE`** di form upload sehingga pengguna dapat menguji gambar kebun yang sama dengan CLAHE menyala (`ON`) vs mati (`OFF`) dan melihat perbedaannya langsung pada tabel log.

---

## 3. KRITERIA PENERIMAAN (ACCEPTANCE CRITERIA)
1. Aplikasi `python app.py` berjalan lancar tanpa error import atau syntax error, serta otomatis memuat bobot model `.pt` terbaik yang tersedia di folder proyek.
2. Saat gambar diunggah ke `/predict`, respons JSON mengembalikan rincian `latency_breakdown`, status `clahe_mode`, `box_area_ratio_pct`, `granularity_type`, serta citra preview `preprocessed_clahe_base64`.
3. Tidak ada lagi klaim "menyatukan iklim dataran rendah-tinggi" atau klaim mentah "jumlah titik lesi" pada kelas daun utuh (`Fresh` dan `Yellow Sigatoka`) di seluruh teks UI; seluruhnya menggunakan terminologi **"Jumlah Wilayah Deteksi (Region Count)"** dengan keterangan granularitas per kelas.
4. Banner *Disclaimer* Penyuluh Pertanian/Kementan beserta referensi FRAC tampil jelas pada kartu rekomendasi agronomi.
5. Dashboard Evaluasi menampilkan angka eksak hasil eksperimen Kaggle (Tabel 1 Ablasi, Tabel 2 AP Per-Kelas, Tabel 3 Latensi GPU vs CPU, dan Statistik Pembersihan 6.415 $\rightarrow$ 5.258 citra).
6. Modul **Validasi Sampel Kebun (Task 7)**, perbandingan visual **Raw vs LAB-CLAHE (Task 8)**, dan kalkulator **SUS (Task 6)** berfungsi penuh beserta fitur ekspor CSV-nya di sisi browser.