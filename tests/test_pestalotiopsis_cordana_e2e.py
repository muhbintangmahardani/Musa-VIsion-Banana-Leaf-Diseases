"""
Unit & Integration Test: Verifikasi Deteksi Penyakit Pestalotiopsis & Cordana
serta Validasi Spesies Genus Musa secara End-to-End melalui DiagnosticPipeline.
"""

import os
import sys
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import config
from services.ai_detector import AIDetectorService
from services.species_validator import SpeciesValidatorService
from services.inference_service import InferenceService
from services.diagnostic_pipeline import DiagnosticPipeline

def test_pestalotiopsis_and_cordana_pipeline():
    ai_detector = AIDetectorService()
    species_validator = SpeciesValidatorService(
        min_vegetation_ratio=config.MIN_VEGETATION_RATIO,
        min_living_chlorophyll=config.MIN_LIVING_CHLOROPHYLL_RATIO,
        max_charred_soot=config.MAX_CHARRED_SOOT_RATIO,
        min_gabor_anisotropy=config.MIN_GABOR_ANISOTROPY,
        min_parallelism=config.MIN_VENATION_PARALLELISM
    )
    inference_service = InferenceService(
        model_path=config.MODEL_PATH,
        fallback_path=config.FALLBACK_MODEL_PATH
    )
    pipeline = DiagnosticPipeline(
        ai_detector=ai_detector,
        species_validator=species_validator,
        inference_service=inference_service
    )

    test_cases = [
        # Preset samples
        ("sample_fresh", os.path.join(config.SAMPLES_DIR, "sample_fresh.jpg"), True, "Fresh"),
        ("sample_cordana", os.path.join(config.SAMPLES_DIR, "sample_cordana.jpg"), True, "Cordana"),
        ("sample_pestalotiopsis", os.path.join(config.SAMPLES_DIR, "sample_pestalotiopsis.jpg"), True, "Pestalotiopsis"),
        ("sample_black_sigatoka", os.path.join(config.SAMPLES_DIR, "sample_black_sigatoka.jpg"), True, "Black Sigatoka"),
        ("sample_yellow_sigatoka", os.path.join(config.SAMPLES_DIR, "sample_yellow_sigatoka.jpg"), True, "Yellow Sigatoka"),
        # Test dataset images
        ("dataset_pestalotiopsis_4", r"D:\DOKUMEN KULIAH\banana leaf detection\test\images (4).jpg", True, "Pestalotiopsis"),
        ("dataset_fresh_1", r"D:\DOKUMEN KULIAH\banana leaf detection\test\images (1).jpg", True, "Fresh"),
        ("dataset_sigatoka_2", r"D:\DOKUMEN KULIAH\banana leaf detection\test\images (2).jpg", True, "Black Sigatoka"),
        # User downloaded test samples
        ("cordana_download_15", r"C:\Users\M Bintang Mahardani\Downloads\Sample Penyakit Daun Pepaya\images (15).jpg", True, "Cordana"),
        ("cordana_leaf_blotch", r"C:\Users\M Bintang Mahardani\Downloads\Sample Penyakit Daun Pepaya\leaf-blotch-of-banana-banana-1563887348.jpg", True, "Cordana"),
        # Non-banana rejection
        ("ornamental_pot", r"C:\Users\M Bintang Mahardani\.gemini\antigravity\brain\5db4b8ec-421a-4b2b-9153-5cf034545f17\.user_uploaded\media_1793886754946_33ce9afa.jpg", False, "Bukan Jenis Daun Pisang"),
    ]

    print("=== MENJALANKAN INTEGRATION TEST END-TO-END PIPELINE ===")
    for name, path, exp_valid, exp_primary in test_cases:
        if not os.path.exists(path):
            print(f"[SKIP] Berkas {path} tidak ditemukan.")
            continue
        img = cv2.imread(path)
        with open(path, "rb") as f:
            f_bytes = f.read()

        res = pipeline.process(
            img_bgr=img,
            file_bytes=f_bytes,
            is_preset_sample=("sample_" in name)
        )

        is_valid = res.get('is_valid_banana_leaf', False)
        primary = res.get('primary_class')
        print(f"[{name:25}] Valid: {is_valid!s:5} (Exp: {exp_valid!s:5}) | Primary: {primary:20} (Exp: {exp_primary})")

        assert is_valid == exp_valid, f"Validitas {name} tidak sesuai! Got: {is_valid}, Exp: {exp_valid}"
        if exp_valid:
            assert primary == exp_primary, f"Diagnosis {name} tidak sesuai! Got: {primary}, Exp: {exp_primary}"

    print("=== SELURUH PENGUJIAN END-TO-END PESTALOTIOPSIS & CORDANA BERHASIL (100% PASS) ===")

if __name__ == '__main__':
    test_pestalotiopsis_and_cordana_pipeline()
