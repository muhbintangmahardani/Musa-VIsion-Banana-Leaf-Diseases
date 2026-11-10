"""
MusaVision — Tri-Stage Diagnostic Pipeline (Unified Results Engine)
Mengorkestrasikan pipa pemrosesan bertingkat:
Stage 1: Deteksi Citra Sintetis Buatan AI (AI-Generated Image Detector)
Stage 2: Validasi Spesies Eksklusif Genus Musa & Filter Daun Olahan/Pepes
Stage 3: Inferensi Lokalisasi & Patologi Daun (YOLO Core Inference)

Pembaruan Task 1-8:
- Menghasilkan struktur respons diagnostik lengkap untuk SEMUA kasus (termasuk penolakan gatekeeper)
- Menyertakan telemetri latensi terurai (latency_breakdown)
- Menyertakan visualisasi raw_resized_base64 & preprocessed_clahe_base64
- Menyertakan granularitas wilayah deteksi (total_regions, lesion_level_count, leaf_level_count)
- Menghilangkan bingkai/overlay HUD pada citra preview sesuai instruksi user
"""

import time
import cv2
import numpy as np
from typing import Dict, Any, Optional
from core.constants import ErrorCode
from core.config import get_system_device_name
from services.ai_detector import AIDetectorService, AIDetectionResult
from services.species_validator import SpeciesValidatorService, SpeciesValidationResult
from services.inference_service import (
    InferenceService,
    image_to_base64,
    draw_warning_overlay,
    preprocess_lab_clahe
)


class DiagnosticPipeline:
    """
    Orkestrator utama sistem diagnostik daun pisang MusaVision.
    Menerapkan prinsip Single Responsibility & Dependency Injection.
    """

    def __init__(
        self,
        ai_detector: AIDetectorService,
        species_validator: SpeciesValidatorService,
        inference_service: InferenceService
    ):
        self.ai_detector = ai_detector
        self.species_validator = species_validator
        self.inference_service = inference_service

    def process(
        self,
        img_bgr: np.ndarray,
        conf_thresh: float = 0.25,
        iou_thresh: float = 0.45,
        file_bytes: Optional[bytes] = None,
        is_preset_sample: bool = False,
        use_clahe: bool = True
    ) -> Dict[str, Any]:
        """
        Menjalankan pipeline 3 tahap secara sekuensial dengan hasil laporan terintegrasi penuh.
        """
        start_perf = time.perf_counter()

        if img_bgr is None or img_bgr.size == 0:
            return {
                'success': False,
                'error_code': ErrorCode.INVALID_IMAGE.value,
                'title': 'Citra Tidak Valid',
                'message': 'Citra masukan kosong atau tidak dapat di-decode oleh server.'
            }

        # 1. Eksekusi Pra-pemrosesan CIE-LAB CLAHE untuk keperluan visualisasi tab (Task 1 & 8)
        t_prep_start = time.perf_counter()
        preprocessed_bgr, raw_resized_b64, preprocessed_clahe_b64 = preprocess_lab_clahe(
            img_bgr, target_size=(640, 640), use_clahe=use_clahe
        )
        preprocess_ms = round((time.perf_counter() - t_prep_start) * 1000, 2)
        original_b64 = image_to_base64(img_bgr)

        # Deteksi hardware kontekstual
        device_name = get_system_device_name()

        def build_gatekeeper_latency(total_ms: float) -> dict:
            return {
                "preprocess_ms": preprocess_ms,
                "inference_nms_ms": 0.0,
                "postprocess_encode_ms": round(max(0.1, total_ms - preprocess_ms), 2),
                "server_total_ms": total_ms,
                "device_name": device_name,
                "input_resolution": "640x640",
                "clahe_mode": (
                    "CIE-LAB (Channel L, ClipLimit=2.0, Grid=8x8)"
                    if use_clahe
                    else "Non-CLAHE (Standard RGB/BGR)"
                ),
                "iou_threshold": iou_thresh,
                "conf_threshold": conf_thresh
            }

        # -------------------------------------------------------------
        # STAGE 1: Pemeriksaan Penanda Metadata AI Generator
        # Citra yang memuat metadata resmi model generatif (Midjourney/DALL-E/SD) langsung ditolak
        # -------------------------------------------------------------
        ai_result: AIDetectionResult = self.ai_detector.detect(img_bgr, file_bytes)

        def build_ai_rejection_response() -> Dict[str, Any]:
            elapsed_ms = round((time.perf_counter() - start_perf) * 1000, 2)
            ai_details = [
                "DETAIL ANALISIS FORENSIK CITRA SINTETIS (AI):",
                f"- Tingkat Probabilitas AI: {ai_result.ai_score}% (Keyakinan: {ai_result.confidence_level})",
            ]
            for sig in ai_result.detected_signals[:4]:
                ai_details.append(f"- Indikator Terdeteksi : {sig}")
            ai_details.append("STATUS: Citra Ditolak. Gunakan foto daun pisang asli dari kamera fisik")

            annotated_bgr = preprocessed_bgr.copy()
            annotated_b64 = image_to_base64(annotated_bgr)

            return {
                'success': True,
                'is_valid_banana_leaf': False,
                'is_ai_generated': True,
                'error_code': ErrorCode.AI_GENERATED_DETECTED.value,
                'validation_stage': 'STAGE_1_AI_DETECTION',
                'primary_class': 'Citra Sintesis AI',
                'summary_title': 'Pemindaian Ditolak: Citra Hasil Generator AI',
                'summary_description': (
                    f"Sistem mendeteksi bahwa citra yang Anda unggah dihasilkan oleh kecerdasan buatan "
                    f"(Skor AI: {ai_result.ai_score}%, Tingkat Keyakinan: {ai_result.confidence_level}). "
                    f"{ai_result.reason} Untuk menjaga validitas dan integritas penelitian skripsi, gunakan foto tanaman asli."
                ),
                'disease_info': {
                    'indonesian_name': 'Citra Sintetis Kecerdasan Buatan (AI Generated)',
                    'scientific_name': 'Synthetic Diffusion / GAN Model',
                    'pathogen_scientific': 'Non-Biological (Synthetic AI Latent Diffusion Model)',
                    'severity': 'Penolakan Integritas Ilmiah',
                    'severity_color': 'red',
                    'status_summary': 'Citra terdeteksi hasil generate AI dan tidak mewakili biologi jaringan foliar asli.',
                    'visual_confusion_note': 'Citra buatan AI sering kali meniru warna daun pisang namun memiliki degradasi spektral frekuensi tinggi 2D-FFT dan ketiadaan sensor noise fisik.',
                    'symptoms': [
                        'Anomali spektrum daya frekuensi tinggi (2D-FFT) akibat proses upsampling model generatif.',
                        'Disparitas tekstur mikro tidak alami (tekstur seperti lilin/plastik atau over-smooth).',
                        'Pola lesi tidak mengikuti persebaran spora jamur patogen di alam liar.'
                    ],
                    'causes': [
                        'Citra digenerasi menggunakan model teks-ke-gambar (Midjourney, Stable Diffusion, DALL-E, Flux).',
                        'Ketiadaan sensor noise foton fisik dari lensa kamera nyata.'
                    ],
                    'sanitation_protocol': 'Tidak dapat diterapkan pada citra sintetis komputer.',
                    'fungicide_guidance': 'Tidak dapat diterapkan pada citra buatan AI.',
                    'recommendations': [
                        'Gunakan foto asli daun pisang segar langsung dari kamera smartphone Anda.',
                        'Pastikan daun yang difoto berada di pohon pisang di kebun atau pekarangan.',
                        'Hindari mengunggah hasil karya seni digital atau citra render 3D.'
                    ]
                },
                'total_detections': 0,
                'total_regions': 0,
                'lesion_level_count': 0,
                'leaf_level_count': 0,
                'avg_box_area_ratio': 0.0,
                'avg_box_area_ratio_pct': 0.0,
                'region_count': {
                    'total_regions': 0,
                    'lesion_level_count': 0,
                    'leaf_level_count': 0
                },
                'detections': [],
                'class_counter': {},
                'inference_time_ms': elapsed_ms,
                'latency_breakdown': build_gatekeeper_latency(elapsed_ms),
                'original_image': original_b64,
                'raw_resized_base64': raw_resized_b64,
                'preprocessed_clahe_base64': preprocessed_clahe_b64,
                'annotated_result_base64': annotated_b64,
                'annotated_image': annotated_b64,
                'metrics': {
                    'ai_score': ai_result.ai_score,
                    'confidence_level': ai_result.confidence_level,
                    'spectral_metric': ai_result.spectral_metric,
                    'texture_metric': ai_result.texture_metric
                }
            }

        # 1. Tolak jika berkas terkonfirmasi memuat metadata generator AI resmi
        if not is_preset_sample and ai_result.metadata_flag:
            return build_ai_rejection_response()

        # -------------------------------------------------------------
        # STAGE 2: Validasi Taksonomi Spesies Genus Musa & Filter Objek Non-Daun Awal
        # Menolak objek non-tumbuhan (wajah/selfie, ruangan, laptop, makanan),
        # daun pepes bakar, serta daun dikotil menjari SEBELUM inferensi YOLO.
        # -------------------------------------------------------------
        species_result: SpeciesValidationResult = self.species_validator.validate(img_bgr)

        def build_species_rejection_response(spec_res: SpeciesValidationResult) -> Dict[str, Any]:
            elapsed_ms = round((time.perf_counter() - start_perf) * 1000, 2)
            err_code = spec_res.error_code or ErrorCode.NON_BANANA_LEAF.value

            # Kustomisasi judul, overlay, dan knowledge base berdasarkan jenis penolakan
            if err_code == ErrorCode.NON_PLANT_OBJECT.value:
                tag_label = "[ BUKAN OBJEK DAUN PISANG ]"
                overlay_color = (80, 80, 80)  # Slate
                primary_class = 'Bukan Objek Daun Pisang'
                summary_title = 'Objek Terdeteksi Bukan Daun Pisang'
                knowledge_base = {
                    'indonesian_name': 'Objek Bukan Daun (Non-Tumbuhan)',
                    'scientific_name': 'Di luar Taksonomi Genus Musa',
                    'pathogen_scientific': 'Non-Plantae / Non-Musa Subject',
                    'severity': 'Tidak Dapat Didiagnosis',
                    'severity_color': 'zinc',
                    'status_summary': 'Objek yang dipindai tidak memiliki jaringan helai daun tanaman pisang hidup.',
                    'visual_confusion_note': 'Objek tidak memiliki klorofil aktif foliar maupun struktur serat daun monokotil.',
                    'symptoms': [
                        'Tidak terdeteksi klorofil daun aktif pada spektrum warna HSV (klorofil < 15%).',
                        'Tidak terdapat struktur lamina atau pertulangan daun monokotil sejajar.',
                        'Citra menampilkan objek lain (hewan, wajah manusia, laptop, meja, pakaian, atau ruangan).'
                    ],
                    'causes': [
                        'Sudut kamera tidak mengarah pada helai daun pohon pisang hidup.',
                        'Objek non-tanaman menghalangi bidang bidik kamera.',
                        'Pencahayaan ekstrem atau latar belakang non-kebun.'
                    ],
                    'sanitation_protocol': 'Tidak dapat diterapkan pada objek non-tanaman.',
                    'fungicide_guidance': 'Tidak dapat diaplikasikan pada objek non-tanaman.',
                    'recommendations': [
                        'Arahkan kamera secara tegak lurus pada helai daun pohon pisang hidup (Musa spp.).',
                        'Ambil foto dengan jarak 30–50 cm dan pastikan fokus tajam pada permukaan daun.',
                        'Singkirkan objek hewan, manusia, atau benda mati dari bidang pemotretan.'
                    ]
                }
            else:
                tag_label = "[ BUKAN JENIS DAUN PISANG ]"
                overlay_color = (30, 140, 230)  # Amber
                primary_class = 'Bukan Jenis Daun Pisang'
                summary_title = 'Daun Tanaman Lain (Bukan Daun Pisang)'
                knowledge_base = {
                    'indonesian_name': 'Daun Tanaman Spesies Lain (Bukan Pisang)',
                    'scientific_name': 'Spesies Tanaman Non-Musa (Mangga, Pepaya, Singkong, dll.)',
                    'pathogen_scientific': 'Di luar Genus Musa (Spesies Non-Target)',
                    'severity': 'Spesies di Luar Domain Sistem',
                    'severity_color': 'amber',
                    'status_summary': 'Morfologi dan venasi daun tidak bersesuaian dengan tanaman pisang (Musa spp.).',
                    'visual_confusion_note': 'Pertulangan daun menyirip jala/menjari khas tanaman dikotil membedakannya secara taksonomi dari venasi sejajar rapat genus Musa.',
                    'symptoms': [
                        'Pertulangan daun menyirip jala (reticulate) atau menjari (palmate) khas tanaman dikotil.',
                        'Tidak memiliki alur serat sejajar rapat monokotil (parallel venation).',
                        'Bercak atau tekstur pada daun ini bukan merupakan penyakit patogen pisang.'
                    ],
                    'causes': [
                        'Spesimen berasal dari pohon buah lain (mangga, jambu, jeruk, apel) atau tanaman pangan lain.',
                        'Arsitektur daun berbeda secara taksonomi biologis dari genus Musa.'
                    ],
                    'sanitation_protocol': 'Protokol deleafing MusaVision dikhususkan hanya untuk rumpun pohon pisang.',
                    'fungicide_guidance': 'Konsultasikan rekomendasi fungisida spesifik komoditas tanaman tersebut dengan PPL.',
                    'recommendations': [
                        'Pastikan sampel daun yang difoto berasal dari pohon pisang (Musa acuminata / Musa balbisiana).',
                        'Sistem MusaVision dikhususkan hanya untuk 5 kondisi daun pisang: Fresh, Black Sigatoka, Cordana, Pestalotiopsis, dan Yellow Sigatoka.',
                        'Ambil foto permukaan daun pisang dengan orientasi serat melintang jelas.'
                    ]
                }

            annotated_bgr = preprocessed_bgr.copy()
            annotated_b64 = image_to_base64(annotated_bgr)

            return {
                'success': True,
                'is_valid_banana_leaf': False,
                'is_ai_generated': False,
                'error_code': err_code,
                'validation_stage': 'STAGE_2_SPECIES_VALIDATION',
                'primary_class': primary_class,
                'summary_title': summary_title,
                'summary_description': spec_res.reason,
                'disease_info': knowledge_base,
                'total_detections': 0,
                'total_regions': 0,
                'lesion_level_count': 0,
                'leaf_level_count': 0,
                'avg_box_area_ratio': 0.0,
                'avg_box_area_ratio_pct': 0.0,
                'region_count': {
                    'total_regions': 0,
                    'lesion_level_count': 0,
                    'leaf_level_count': 0
                },
                'detections': [],
                'class_counter': {},
                'inference_time_ms': elapsed_ms,
                'latency_breakdown': build_gatekeeper_latency(elapsed_ms),
                'original_image': original_b64,
                'raw_resized_base64': raw_resized_b64,
                'preprocessed_clahe_base64': preprocessed_clahe_b64,
                'annotated_result_base64': annotated_b64,
                'annotated_image': annotated_b64,
                'metrics': {
                    'banana_confidence': spec_res.banana_confidence,
                    'vegetation_ratio': spec_res.vegetation_ratio,
                    'living_chlorophyll_ratio': spec_res.living_chlorophyll_ratio,
                    'charred_soot_ratio': spec_res.charred_soot_ratio,
                    'gabor_anisotropy': spec_res.gabor_anisotropy,
                    'venation_parallelism': spec_res.venation_parallelism
                }
            }

        # Penolakan Awal: Jika citra adalah objek non-tumbuhan (selfie/wajah/ruangan), pepes bakar, atau daun menjari:
        # Langsung tolak tanpa perlu proses inferensi model
        if not is_preset_sample and not species_result.is_banana_leaf:
            if species_result.error_code in [ErrorCode.NON_PLANT_OBJECT.value, ErrorCode.INVALID_IMAGE.value] or species_result.gabor_anisotropy < 0.50:
                return build_species_rejection_response(species_result)

        # -------------------------------------------------------------
        # STAGE 3: Verifikasi Forensik Daun Pisang Sintetis (AI Art)
        # Menolak citra buatan AI generator laten tanpa artefak kamera riil
        # -------------------------------------------------------------
        if not is_preset_sample and ai_result.is_ai_generated:
            return build_ai_rejection_response()

        # -------------------------------------------------------------
        # STAGE 4: Inferensi Deteksi & Patologi YOLO Core (Spesimen Genus Musa Valid)
        # -------------------------------------------------------------
        inference_output = self.inference_service.predict(
            img_bgr=img_bgr,
            conf_thresh=conf_thresh,
            iou_thresh=iou_thresh,
            use_clahe=use_clahe
        )

        # -------------------------------------------------------------
        # STAGE 5: Konfirmasi Taksonomi Pasca-YOLO
        # Jika nilai Gabor awal di bawah 0.80 akibat lesi nekrotik luas (Pestalotiopsis / Cordana),
        # periksa apakah model YOLO mengonfirmasi patogen spesifik daun pisang.
        # -------------------------------------------------------------
        detections = inference_output.get('detections', [])
        specific_diseases = [d for d in detections if d['class_name'] in ['Pestalotiopsis', 'Cordana', 'Yellow Sigatoka']]
        max_specific_conf = max([d['confidence'] for d in specific_diseases]) if specific_diseases else 0.0

        final_species_result = self.species_validator.validate(
            img_bgr,
            yolo_disease_detected=len(specific_diseases) > 0,
            max_disease_conf=max_specific_conf,
            specific_disease_detected=len(specific_diseases) > 0
        )

        if not is_preset_sample and not final_species_result.is_banana_leaf:
            return build_species_rejection_response(final_species_result)

        # -------------------------------------------------------------
        # STAGE 6: Pengemasan Hasil Inferensi Diagnostik Final (Daun Pisang Valid)
        # -------------------------------------------------------------
        inference_output['is_valid_banana_leaf'] = True
        inference_output['is_ai_generated'] = False
        inference_output['validation_status'] = {
            'is_ai_checked': True,
            'is_ai_generated': False,
            'ai_confidence_score': ai_result.ai_score,
            'is_banana_leaf': True,
            'detected_category': final_species_result.detected_category,
            'banana_domain_score': final_species_result.banana_confidence,
            'vegetation_ratio': final_species_result.vegetation_ratio,
            'living_chlorophyll_ratio': final_species_result.living_chlorophyll_ratio,
            'gabor_anisotropy': final_species_result.gabor_anisotropy,
            'venation_parallelism': final_species_result.venation_parallelism
        }

        return inference_output
