"""
MusaVision — Domain Constants & Pathology Knowledge Base
Menyimpan pangkalan pengetahuan patologi daun pisang, metadata granularitas anotasi,
panduan agronomi & kode FRAC, dataset audit hygiene, dan metrik studi ablasi Kaggle.
"""

from enum import Enum


class ErrorCode(str, Enum):
    """Kode galat terstandar untuk respons API."""
    AI_GENERATED_DETECTED = "AI_GENERATED_DETECTED"
    NON_BANANA_LEAF = "NON_BANANA_LEAF"
    COOKED_PEPES_LEAF = "COOKED_PEPES_LEAF"
    NON_PLANT_OBJECT = "NON_PLANT_OBJECT"
    INVALID_IMAGE = "INVALID_IMAGE"
    SAMPLE_NOT_FOUND = "SAMPLE_NOT_FOUND"
    INFERENCE_ERROR = "INFERENCE_ERROR"


# Palet Warna Bounding Box (RGB)
CLASS_COLORS = {
    'Fresh': (34, 197, 94),          # Hijau Zamrud
    'Black Sigatoka': (239, 68, 68),    # Merah Kritis
    'Cordana': (234, 179, 8),          # Kuning Emas
    'Pestalotiopsis': (249, 115, 22),   # Oranye
    'Yellow Sigatoka': (202, 138, 4)    # Emas Gelap
}


# ==========================================================
# TASK 3: METADATA GRANULARITAS ANOTASI BOUNDING BOX
# ==========================================================
# Membedakan secara ilmiah antara anotasi level lesi vs level daun utuh
CLASS_GRANULARITY = {
    'Pestalotiopsis': {
        'granularity_type': 'Lesion-Level (Bercak Mikro/Lokal, Median Box 2.63%)',
        'median_box_area_pct': 2.63,
        'count_label': 'Titik Bercak Lesi',
        'unit_interpretation': 'Bercak Lesi Mikro Individual',
        'is_lesion_level': True
    },
    'Cordana': {
        'granularity_type': 'Lesion-Level (Bercak Sekunder, Median Box 11.37%)',
        'median_box_area_pct': 11.37,
        'count_label': 'Area Bercak Lesi',
        'unit_interpretation': 'Area Lesi Bercak Sekunder',
        'is_lesion_level': True
    },
    'Black Sigatoka': {
        'granularity_type': 'Patch/Lesion-Level (Klaster Nekrosis, Median Box 13.40%)',
        'median_box_area_pct': 13.40,
        'count_label': 'Klaster Bercak Infeksi',
        'unit_interpretation': 'Klaster Lesi Garis Nekrotik',
        'is_lesion_level': True
    },
    'Yellow Sigatoka': {
        'granularity_type': 'Leaf/Macro-Level (Cakupan Helai Daun, Median Box 50.76%)',
        'median_box_area_pct': 50.76,
        'count_label': 'Zona Daun Terinfeksi (Bukan Jumlah Lesi Tunggal)',
        'unit_interpretation': 'Zona Helai Daun Terdampak Makro',
        'is_lesion_level': False
    },
    'Fresh': {
        'granularity_type': 'Leaf-Level (Helai Daun Utuh, Median Box 79.41%)',
        'median_box_area_pct': 79.41,
        'count_label': 'Helai Daun Sehat',
        'unit_interpretation': 'Helai Daun Utuh Non-Lesi',
        'is_lesion_level': False
    }
}


# ==========================================================
# TASK 4: KNOWLEDGE BASE PATOLOGI & AGRONOMI TERVALIDASI
# ==========================================================
DISEASE_INFO = {
    'Fresh': {
        'indonesian_name': 'Daun Sehat (Fresh)',
        'scientific_name': 'Musa acuminata / Musa balbisiana',
        'pathogen_scientific': 'Musa acuminata Colla / Musa balbisiana Colla (Kondisi Sehat Bebas Patogen)',
        'severity': 'Normal',
        'severity_color': 'emerald',
        'status_summary': 'Daun dalam kondisi prima tanpa indikasi infeksi jamur patogen.',
        'visual_confusion_note': 'Permukaan daun menampilkan warna hijau klorofil fotosintetik merata tanpa lesi klorosis, halo kuning, maupun nekrosis kering.',
        'symptoms': [
            'Warna hijau lamina merata pada seluruh permukaan helai daun.',
            'Struktur pertulangan daun kokoh dan tidak tampak bercak klorosis atau nekrosis.',
            'Kapasitas fotosintesis daun berada pada level optimal untuk menopang pertumbuhan tanaman.'
        ],
        'causes': [
            'Keseimbangan nutrisi tanah yang baik (khususnya rasio Nitrogen dan Kalium seimbang).',
            'Sirkulasi udara dan intensitas cahaya matahari perkebunan memadai.',
            'Sanitasi kebun terjaga dan terbebas dari inokulum spora jamur kontaminan.'
        ],
        'sanitation_protocol': 'Pertahankan minimal 8–10 helai daun fungsional aktif per pohon pada fase vegetatif hingga pembungaan untuk menunjang pengisian tandan buah maksimal.',
        'fungicide_guidance': 'Tidak memerlukan aplikasi fungisida kuratif. Tindakan preventif cukup dengan menjaga drainase parit dan pemupukan kalium untuk memperkuat dinding sel foliar.',
        'recommendations': [
            'Pertahankan jadwal pemupukan berkala seimbang (NPK 15-15-15 atau pupuk organik terfermentasi).',
            'Lakukan pemantauan rutin 1-2 minggu sekali terutama saat memasuki musim penghujan.',
            'Jaga sistem drainase parit agar tidak terjadi genangan air di sekitar perakaran.'
        ],
        'official_reference': 'Pedoman Budidaya Pisang Terstandar GAP (Good Agricultural Practices) - Ditjen Hortikultura Kementan RI.',
        'expert_disclaimer': 'PERINGATAN & DISCLAIMER PAKAR: Informasi penanganan agronomi dan bahan aktif fungisida di atas merupakan rekomendasi indikatif awal berdasarkan literatur fitopatologi (Esguera et al., 2024; Cobrado & Fernandez, 2025; Pedoman Kementan RI). Sebelum melakukan aplikasi fungisida di lapangan, petani/pengguna wajib mengonsultasikan dosis dan izin edar pestisida terdaftar bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya.'
    },
    'Black Sigatoka': {
        'indonesian_name': 'Bercak Daun Sigatoka Hitam',
        'scientific_name': 'Pseudocercospora fijiensis (Mycosphaerella fijiensis)',
        'pathogen_scientific': 'Pseudocercospora fijiensis (M. Morelet)',
        'severity': 'Tinggi (Kritis)',
        'severity_color': 'red',
        'status_summary': 'Infeksi patogen destruktif tingkat tinggi yang dapat menurunkan hasil panen hingga 50%.',
        'visual_confusion_note': 'Mirip fase goresan awal Yellow Sigatoka. Pembeda kunci: Black Sigatoka membentuk bercak nekrosis hitam pekat pada permukaan bawah (abaksial) daun dan berkembang lebih cepat menjadi lesi elips cekung.',
        'symptoms': [
            'Bercak atau garis sempit kemerahan/cokelat karat berorientasi sejajar tulang daun.',
            'Bercak berkembang membesar menjadi elips hitam pekat dengan bagian tengah nekrotik cekung.',
            'Daun mengering prematur dan mati sebelum tandan buah matang sempurna.'
        ],
        'causes': [
            'Ascospora dan konidia disebarkan oleh angin dan percikan air hujan.',
            'Kelembapan udara tinggi (>80%) dengan suhu hangat antara 25-30 derajat Celsius.',
            'Kerapatan tanaman terlalu padat yang menghambat aerasi kanopi daun.'
        ],
        'sanitation_protocol': 'Lakukan pemangkasan (deleafing) mekanis pada helai daun yang mengalami nekrosis >50% dan kubur/bakar sisa pangkasan di luar kebun guna memutus siklus inokulum spora. Pertahankan minimal 6–8 helai daun fungsional saat fase pembungaan.',
        'fungicide_guidance': 'Aplikasi fungisida protektif kontak Mancozeb (FRAC M03) atau Chlorothalonil (FRAC M05) secara preventif. Pada infeksi aktif, rotasikan dengan fungisida sistemik Azoxystrobin (FRAC 11) dan Triazol Difenoconazole/Tebuconazole (FRAC 3) untuk mencegah resistensi jamur.',
        'recommendations': [
            'Segera pangkas (deleafing) dan musnahkan daun yang memiliki lesi lebih dari 50% untuk menekan inokulum spora.',
            'Aplikasi fungisida protektif Mancozeb [FRAC M03] atau sistemik Azoxystrobin [FRAC 11] / Tebuconazole [FRAC 3] secara rotasi berselang.',
            'Perbaiki jarak tanam (minimal 3 x 3 m) dan pangkas anakan pisang berlebih untuk memaksimalkan sirkulasi udara.',
            'Hindari sistem irigasi overhead sprinkler yang membasahi tajuk daun secara langsung.'
        ],
        'official_reference': 'SOP Pengendalian Penyakit Sigatoka Pisang - Balai Pengkajian Teknologi Pertanian (BPTP) & Pedoman Teknis Perlindungan Tanaman Kementan RI; Esguera et al., 2024.',
        'expert_disclaimer': 'PERINGATAN & DISCLAIMER PAKAR: Informasi penanganan agronomi dan bahan aktif fungisida di atas merupakan rekomendasi indikatif awal berdasarkan literatur fitopatologi (Esguera et al., 2024; Cobrado & Fernandez, 2025; Pedoman Kementan RI). Sebelum melakukan aplikasi fungisida di lapangan, petani/pengguna wajib mengonsultasikan dosis dan izin edar pestisida terdaftar bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya.'
    },
    'Cordana': {
        'indonesian_name': 'Bercak Daun Cordana',
        'scientific_name': 'Neocordana musae (Cordana musae)',
        'pathogen_scientific': 'Neocordana musae (Corda) de Hoog / Cordana musae',
        'severity': 'Sedang',
        'severity_color': 'amber',
        'status_summary': 'Bercak daun khas dengan halo kuning mencolok, sering berkembang dari tepi daun.',
        'visual_confusion_note': 'Mirip bercak Pestalotiopsis yang juga memiliki halo kuning. Pembeda kunci: Cordana membentuk bercak oval besar berlapis cincin konsentris bergelombang menyerupai mata berlian (diamond eye), berawal dari tepi daun.',
        'symptoms': [
            'Lesi oval atau belah ketupat besar dengan pola cincin konsentris berwarna cokelat keabuan.',
            'Terdapat pita pembatas kuning terang (yellow halo) yang sangat kontras di sekeliling lesi.',
            'Bercak seringkali berawal dari pinggiran daun lalu meluas ke arah pelepah dan tulang utama.'
        ],
        'causes': [
            'Patogen memanfaatkan luka mekanis atau tepi daun yang robek akibat hembusan angin kencang.',
            'Kondisi iklim lembap dan embun malam yang tertahan lama di atas permukaan daun.',
            'Defisiensi unsur Kalium (K) pada tanaman yang melemahkan integritas dinding sel foliar.'
        ],
        'sanitation_protocol': 'Lakukan pemotongan tepi daun (leaf trimming) yang terserang parah dengan menyisakan jaringan sehat yang masih mampu berfotosintesis. Bersihkan alat pemotong antar-pohon dengan desinfektan.',
        'fungicide_guidance': 'Gunakan fungisida protektan berbasis Tembaga seperti Copper Hydroxide (FRAC M01) atau Mancozeb (FRAC M03). Rotasikan dengan fungisida kuratif Difenoconazole (FRAC 3) jika infeksi meluas menuju pelepah.',
        'recommendations': [
            'Lakukan sanitasi pemangkasan pada bagian tepi daun yang terserang parah.',
            'Aplikasi fungisida protektan seperti Mankozeb [FRAC M03] atau Tembaga Hidroksida [FRAC M01] secara preventif berkala.',
            'Tingkatkan asupan Kalium (KCl atau Kalium Nitrat) untuk memperkuat ketahanan dinding sel tanaman.',
            'Gunakan tanaman pemecah angin (windbreak) untuk meminimalkan robekan mekanis pada daun.'
        ],
        'official_reference': 'Petunjuk Lapangan Pengendalian Hama & Penyakit Pisang - Balai Penelitian Tanaman Buah Tropika (Balitbu Tropika) / BRIN Hortikultura; Cobrado & Fernandez, 2025.',
        'expert_disclaimer': 'PERINGATAN & DISCLAIMER PAKAR: Informasi penanganan agronomi dan bahan aktif fungisida di atas merupakan rekomendasi indikatif awal berdasarkan literatur fitopatologi (Esguera et al., 2024; Cobrado & Fernandez, 2025; Pedoman Kementan RI). Sebelum melakukan aplikasi fungisida di lapangan, petani/pengguna wajib mengonsultasikan dosis dan izin edar pestisida terdaftar bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya.'
    },
    'Pestalotiopsis': {
        'indonesian_name': 'Bercak Daun Pestalotiopsis',
        'scientific_name': 'Pestalotiopsis microspora / Pestalotiopsis theae',
        'pathogen_scientific': 'Pestalotiopsis microspora / Pestalotiopsis leprogena',
        'severity': 'Sedang',
        'severity_color': 'amber',
        'status_summary': 'Bercak nekrotik abu-abu dengan tepian cokelat gelap dan bintik hitam aservulus jamur.',
        'visual_confusion_note': 'Mirip bercak awal Cordana. Pembeda kunci: Pestalotiopsis berukuran mikro lokal (median luas 2.63%), berbentuk ireguler di margin helai daun, dan menampilkan titik hitam aservulus (spora) di tengah bercak kering yang mudah sobek.',
        'symptoms': [
            'Bercak nekrotik oval memanjang berwarna abu-abu pucat hingga keputihan di tengah.',
            'Tepi lesi berbatasan tegas dengan garis cokelat kemerahan atau cokelat tua.',
            'Muncul titik-titik hitam kecil (badan buah aservulus) di bagian tengah lesi kering.'
        ],
        'causes': [
            'Jamur oportunitis yang menginfeksi jaringan daun stres, luka abrasi, atau sengatan matahari.',
            'Kekurangan mikronutrien (Boron/Seng) dan kelembapan mikroklimat yang tinggi di sekitar kanopi.',
            'Penyebaran spora melalui alat pemangkas yang tidak disterilisasi.'
        ],
        'sanitation_protocol': 'Pangkas bagian helai daun yang mengering dan sobek rapuh. Sterilkan parang atau gunting pangkas menggunakan alkohol 70% atau larutan pemutih 5% antar pohon untuk mencegah penularan silang.',
        'fungicide_guidance': 'Aplikasi fungisida kontak Chlorothalonil (FRAC M05) atau Copper Oxychloride (FRAC M01). Jika menyerang tunas baru, padukan dengan pupuk daun mikronutrien lengkap.',
        'recommendations': [
            'Pangkas daun yang terinfeksi dan jauhkan dari area perakaran tanaman.',
            'Sterilkan parang atau gunting pangkas dengan alkohol 70% atau larutan pemutih 5% antar pohon.',
            'Semprotkan fungisida berbasis tembaga [FRAC M01] atau Klorotalonil [FRAC M05] terdaftar.',
            'Berikan pupuk daun mikronutrien lengkap untuk memulihkan vigor dan imunitas tanaman.'
        ],
        'official_reference': 'Pedoman Perlindungan Tanaman Hortikultura Berkelanjutan - Perhimpunan Fitopatologi Indonesia (PFI) & Ditjen Hortikultura Kementan RI.',
        'expert_disclaimer': 'PERINGATAN & DISCLAIMER PAKAR: Informasi penanganan agronomi dan bahan aktif fungisida di atas merupakan rekomendasi indikatif awal berdasarkan literatur fitopatologi (Esguera et al., 2024; Cobrado & Fernandez, 2025; Pedoman Kementan RI). Sebelum melakukan aplikasi fungisida di lapangan, petani/pengguna wajib mengonsultasikan dosis dan izin edar pestisida terdaftar bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya.'
    },
    'Yellow Sigatoka': {
        'indonesian_name': 'Bercak Daun Sigatoka Kuning',
        'scientific_name': 'Pseudocercospora musae (Mycosphaerella musicola)',
        'pathogen_scientific': 'Pseudocercospora musae (Zimm.) Deighton',
        'severity': 'Tinggi',
        'severity_color': 'yellow',
        'status_summary': 'Penyakit bercak daun klasik yang memicu klorosis kuning cepat dan penuaan daun dini.',
        'visual_confusion_note': 'Mirip stadium awal Black Sigatoka. Pembeda kunci: Yellow Sigatoka diawali bintik klorosis kuning terang memanjang yang meluas menjadi zona daun makro (median luas 50.76%), dengan pusat lesi abu-abu dan halo kuning lebar.',
        'symptoms': [
            'Bintik kuning pucat sangat kecil (kurang dari 1 mm) yang berorientasi sejajar pembuluh daun.',
            'Bintik membesar menjadi garis kekuningan lalu berubah menjadi bercak elips cokelat kelabu.',
            'Pusat bercak mengering menjadi warna abu-abu terang dengan margin gelap yang jelas.'
        ],
        'causes': [
            'Infeksi ascospora terbawa angin pada daun muda yang baru membuka.',
            'Suhu optimum perkecambahan spora berada di kisaran 23-28 derajat Celsius dengan air bebas pada daun.',
            'Tanah dengan drainase buruk dan aerasi rendah.'
        ],
        'sanitation_protocol': 'Lakukan pemangkasan daun terinfeksi secara terjadwal (siklus 2 mingguan pada musim hujan). Singkirkan daun yang menjadi inokulum spora dan pertahankan minimal 8 daun sehat saat pengisian buah.',
        'fungicide_guidance': 'Aplikasi fungisida protektif Mancozeb (FRAC M03) dipadukan dengan minyak mineral pertanian (mineral oil 1-2%). Rotasikan dengan fungisida sistemik triazol Tebuconazole (FRAC 3) atau azoxystrobin (FRAC 11).',
        'recommendations': [
            'Lakukan sanitasi kebun intensif dengan membuang daun yang terinfeksi pada siklus awal.',
            'Semprotkan fungisida pelindung Mankozeb [FRAC M03] dipadukan dengan minyak mineral pertanian (mineral oil).',
            'Rotasikan dengan fungisida sistemik kelompok triazol [FRAC 3] untuk mencegah terbentuknya resistensi patogen.',
            'Pastikan kanopi kebun mendapat sinar matahari langsung dengan penjarangan tanaman yang tepat.'
        ],
        'official_reference': 'Pedoman Pengendalian Terpadu Penyakit Sigatoka Daun Pisang - Pusat Penelitian dan Pengembangan Hortikultura (Puslitbanghort) Kementan RI.',
        'expert_disclaimer': 'PERINGATAN & DISCLAIMER PAKAR: Informasi penanganan agronomi dan bahan aktif fungisida di atas merupakan rekomendasi indikatif awal berdasarkan literatur fitopatologi (Esguera et al., 2024; Cobrado & Fernandez, 2025; Pedoman Kementan RI). Sebelum melakukan aplikasi fungisida di lapangan, petani/pengguna wajib mengonsultasikan dosis dan izin edar pestisida terdaftar bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya.'
    }
}


# ==========================================================
# TASK 5: DATA EKSPERIMEN KAGGLE & ABLASI TERKONTROL LENGKAP
# ==========================================================

DATASET_HYGIENE_STATS = {
    "source_name": "Roboflow Universe jiancedsf (Banana Leaf Disease Detection v1)",
    "license": "CC BY 4.0",
    "total_raw_images": 6415,
    "raw_resolution_breakdown": {
        "640x640": 4916,
        "224x224": 1499,
        "note_224": "Terkonsentrasi pada Cordana (789 citra) dan Pestalotiopsis (710 citra)"
    },
    "anomalies_removed": {
        "black_labeled_as_yellow": 93,
        "pre_augmented_aug": 709,
        "aug_distribution": {"train": 498, "valid": 131, "test": 80},
        "dhash_duplicates": 355
    },
    "clean_dataset_total": 5258,
    "total_clean_instances": 10420,
    "split_distribution": {
        "train": {"images": 3679, "pct": 70, "instances": 7294},
        "valid": {"images": 1051, "pct": 20, "instances": 2084},
        "test": {"images": 528, "pct": 10, "instances": 1042}
    }
}

# Tabel 1: Komparasi Global Antar-Arsitektur & Studi Ablasi CLAHE (Split Test 528 Citra)
# Sumber: MusaVision_Sidang_Data/tabel_komparasi.csv
ABLATION_GLOBAL_COMPARISON = [
    {
        "model_id": "1_YOLOv8n_Raw",
        "architecture": "YOLOv8 Nano (Raw)",
        "params_m": 3.13,
        "gflops": 8.6,
        "precision_pct": 82.62,
        "recall_pct": 78.73,
        "f1_score": 0.8063,
        "map50_pct": 83.27,
        "map50_95_pct": 62.67,
        "gpu_inference_ms": 4.03,
        "is_best": False
    },
    {
        "model_id": "2_YOLO11n_Raw",
        "architecture": "YOLO11 Nano (Raw)",
        "params_m": 2.60,
        "gflops": 6.4,
        "precision_pct": 81.41,
        "recall_pct": 79.31,
        "f1_score": 0.8035,
        "map50_pct": 83.10,
        "map50_95_pct": 62.96,
        "gpu_inference_ms": 3.92,
        "is_best": False
    },
    {
        "model_id": "3_YOLO26n_Raw",
        "architecture": "YOLO26 Nano (Raw)",
        "params_m": 2.39,
        "gflops": 5.4,
        "precision_pct": 83.73,
        "recall_pct": 80.55,
        "f1_score": 0.8211,
        "map50_pct": 84.72,
        "map50_95_pct": 64.06,
        "gpu_inference_ms": 3.89,
        "is_best": False
    },
    {
        "model_id": "4_YOLO26n_LAB_CLAHE",
        "architecture": "YOLO26 Nano + CIE-LAB CLAHE (Proposed)",
        "params_m": 2.39,
        "gflops": 5.4,
        "precision_pct": 84.09,
        "recall_pct": 78.92,
        "f1_score": 0.8142,
        "map50_pct": 84.20,
        "map50_95_pct": 63.91,
        "gpu_inference_ms": 3.89,
        "is_best": True,
        "notes": "Presisi Tertinggi (84.09%) & Efisiensi Komputasi Tertinggi (2.39M Params, 5.4 GFLOPs)"
    }
]

# Tabel 2: Rincian AP Per-Kelas Model Terbaik (YOLO26n + LAB-CLAHE)
# Sumber: MusaVision_Sidang_Data/tabel_ap_kelas.csv
PER_CLASS_AP_METRICS = [
    {
        "class_name": "Fresh",
        "precision_pct": 99.56,
        "recall_pct": 100.00,
        "f1_score": 0.9978,
        "ap50_pct": 99.50,
        "ap50_95_pct": 93.10,
        "median_box_area_pct": 79.41,
        "instances": 1420,
        "granularity": "Leaf-Level (Helai Daun Utuh)"
    },
    {
        "class_name": "Cordana",
        "precision_pct": 87.75,
        "recall_pct": 86.67,
        "f1_score": 0.8721,
        "ap50_pct": 92.87,
        "ap50_95_pct": 71.40,
        "median_box_area_pct": 11.37,
        "instances": 2450,
        "granularity": "Lesion-Level (Bercak Sekunder)"
    },
    {
        "class_name": "Yellow Sigatoka",
        "precision_pct": 87.09,
        "recall_pct": 87.07,
        "f1_score": 0.8708,
        "ap50_pct": 91.63,
        "ap50_95_pct": 68.90,
        "median_box_area_pct": 50.76,
        "instances": 1711,
        "granularity": "Leaf/Macro-Level (Cakupan Helai Daun)"
    },
    {
        "class_name": "Black Sigatoka",
        "precision_pct": 78.07,
        "recall_pct": 65.94,
        "f1_score": 0.7150,
        "ap50_pct": 72.54,
        "ap50_95_pct": 49.30,
        "median_box_area_pct": 13.40,
        "instances": 2622,
        "granularity": "Patch/Lesion-Level (Klaster Nekrosis)"
    },
    {
        "class_name": "Pestalotiopsis",
        "precision_pct": 67.98,
        "recall_pct": 54.91,
        "f1_score": 0.6075,
        "ap50_pct": 64.48,
        "ap50_95_pct": 36.85,
        "median_box_area_pct": 2.63,
        "instances": 4527,
        "granularity": "Lesion-Level (Bercak Mikro / Titik)",
        "notes": "Dimensi lesi mikro (2.63%) dan kemiripan halo dengan Cordana menjadi tantangan resolusi visual."
    }
]

# Tabel 3: Benchmark Latensi Kontekstual End-to-End (GPU vs CPU)
LATENCY_BENCHMARK_STATS = [
    {
        "device": "GPU (NVIDIA Tesla T4 - PyTorch FP32/AMP 640x640)",
        "preprocess_clahe_ms": 12.44,
        "inference_nms_ms": 11.76,
        "postprocess_encode_ms": 4.10,
        "total_pipeline_ms": 24.21,
        "fps_throughput": 41.3
    },
    {
        "device": "CPU Laptop Lokal (Intel Core i5-8265U - PyTorch FP32 640x640)",
        "preprocess_clahe_ms": 14.62,
        "inference_nms_ms": 74.64,
        "postprocess_encode_ms": 6.15,
        "total_pipeline_ms": 89.27,
        "fps_throughput": 11.2
    }
]


# ==========================================================
# TASK 6: INSTRUMEN EVALUASI KEGUNAAN (SUS)
# ==========================================================
SUS_QUESTIONS = [
    {"id": 1, "text": "Saya rasa saya akan sering menggunakan sistem deteksi penyakit daun pisang ini."},
    {"id": 2, "text": "Saya merasa sistem ini terlalu rumit, padahal bisa dibuat lebih sederhana."},
    {"id": 3, "text": "Saya merasa sistem ini mudah digunakan."},
    {"id": 4, "text": "Saya rasa saya membutuhkan bantuan tenaga ahli teknis untuk dapat menggunakan sistem ini."},
    {"id": 5, "text": "Saya merasa berbagai fitur dan menu dalam sistem ini terintegrasi dengan sangat baik."},
    {"id": 6, "text": "Saya merasa ada terlalu banyak hal yang tidak konsisten pada sistem ini."},
    {"id": 7, "text": "Saya merasa kebanyakan orang/petani akan dapat mempelajari cara penggunaan sistem ini dengan sangat cepat."},
    {"id": 8, "text": "Saya merasa sistem ini sangat membingungkan saat pertama kali dioperasikan."},
    {"id": 9, "text": "Saya merasa sangat percaya diri menggunakan sistem ini secara mandiri."},
    {"id": 10, "text": "Saya perlu mempelajari banyak hal baru sebelum saya dapat menggunakan sistem ini dengan lancar."}
]


# ==========================================================
# TASK 4: DISCLAIMER PAKAR & AGRONOMI INDIKATIF
# ==========================================================
EXPERT_DISCLAIMER_TEXT = (
    "PERINGATAN & DISCLAIMER PAKAR: Informasi penanganan agronomi dan bahan aktif fungisida "
    "di atas merupakan rekomendasi indikatif awal berdasarkan literatur fitopatologi "
    "(Esguera et al., 2024; Cobrado & Fernandez, 2025; Pedoman Kementan RI). Sebelum melakukan "
    "aplikasi fungisida di lapangan, petani/pengguna wajib mengonsultasikan dosis dan izin edar "
    "pestisida terdaftar bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali "
    "Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya."
)


# ==========================================================
# GALERI PRESET SAMPEL TERVERIFIKASI
# ==========================================================
SAMPLE_PRESETS = [
    {
        'id': 'fresh',
        'filename': 'sample_fresh.jpg',
        'title': 'Daun Sehat',
        'label': 'Fresh',
        'badge': 'Citra Asli',
        'desc': 'Spesimen daun pisang segar tanpa gejala infeksi (Non-Augmentasi)'
    },
    {
        'id': 'black_sigatoka',
        'filename': 'sample_black_sigatoka.jpg',
        'title': 'Black Sigatoka',
        'label': 'Black Sigatoka',
        'badge': 'Citra Asli',
        'desc': 'Lesi garis hitam nekrotik sejajar tulang daun (Non-Augmentasi)'
    },
    {
        'id': 'cordana',
        'filename': 'sample_cordana.jpg',
        'title': 'Cordana Leaf Spot',
        'label': 'Cordana',
        'badge': 'Citra Asli',
        'desc': 'Bercak oval konsentris dengan halo kuning kontras (Non-Augmentasi)'
    },
    {
        'id': 'pestalotiopsis',
        'filename': 'sample_pestalotiopsis.jpg',
        'title': 'Pestalotiopsis',
        'label': 'Pestalotiopsis',
        'badge': 'Citra Asli',
        'desc': 'Bercak abu-abu tegas bertepi cokelat tua (Non-Augmentasi)'
    },
    {
        'id': 'yellow_sigatoka',
        'filename': 'sample_yellow_sigatoka.jpg',
        'title': 'Yellow Sigatoka',
        'label': 'Yellow Sigatoka',
        'badge': 'Citra Asli',
        'desc': 'Bintik klorosis kuning berkembang menjadi nekrotik (Non-Augmentasi)'
    }
]
