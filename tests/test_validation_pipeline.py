"""
Unit test suite untuk memvalidasi Clean Architecture dan Tri-Stage Gatekeeper Pipeline:
  1. AI Detector Service
  2. Species Validator Service
  3. Diagnostic Pipeline Orchestration
"""

import os
import sys
import cv2
import numpy as np

# Pastikan root direktori ada di sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import config
from core.constants import ErrorCode
from services.ai_detector import AIDetectorService
from services.species_validator import SpeciesValidatorService


def test_genuine_sample():
    """Menguji spesimen daun pisang asli terverifikasi."""
    sample_path = os.path.join(config.SAMPLES_DIR, 'sample_fresh.jpg')
    assert os.path.exists(sample_path), f"File {sample_path} harus ada."
    
    img = cv2.imread(sample_path)
    assert img is not None, "Gagal memuat citra sampel asli."

    # 1. Tes AI Detector
    ai_detector = AIDetectorService(threshold=config.AI_DETECTION_THRESHOLD * 100)
    ai_res = ai_detector.detect(img)
    print(f"[TEST 1] AI Score Daun Asli: {ai_res.ai_score}% | is_ai: {ai_res.is_ai_generated}")
    assert not ai_res.is_ai_generated, "Citra daun asli tidak boleh terdeteksi sebagai AI!"

    # 2. Tes Species Validator
    validator = SpeciesValidatorService(
        min_vegetation_ratio=config.MIN_VEGETATION_RATIO,
        min_parallelism=config.MIN_VENATION_PARALLELISM
    )
    species_res = validator.validate(img)
    print(f"[TEST 2] Banana Confidence: {species_res.banana_confidence}% | Biomassa: {species_res.vegetation_ratio}% | is_banana: {species_res.is_banana_leaf}")
    assert species_res.is_banana_leaf, "Sampel daun pisang asli harus lolos validasi taksonomi!"


def test_non_plant_rejection():
    """Menguji penolakan objek non-tumbuhan (misal latar abu-abu/ruangan)."""
    # Citra non-tumbuhan buatan: warna abu-abu polos tanpa klorofil
    non_plant = np.full((400, 400, 3), 128, dtype=np.uint8)
    
    validator = SpeciesValidatorService()
    res = validator.validate(non_plant)
    print(f"[TEST 3] Objek Non-Tumbuhan: Category: {res.detected_category} | is_banana: {res.is_banana_leaf}")
    assert not res.is_banana_leaf, "Objek non-tumbuhan harus ditolak oleh Species Validator!"
    assert "Bukan Objek" in res.detected_category or res.detected_category == "Objek Non-Tumbuhan"


def test_ai_generated_detection():
    """Menguji pendeteksian citra sintetis AI dengan penanda metadata / anomali."""
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    ai_bytes = b"EXIF Header... Software: Midjourney v6.0 prompt: banana leaf photorealistic"
    
    ai_detector = AIDetectorService(threshold=config.AI_DETECTION_THRESHOLD * 100)
    res = ai_detector.detect(img, file_bytes=ai_bytes)
    print(f"[TEST 4] Citra Bertanda AI: Score: {res.ai_score}% | is_ai: {res.is_ai_generated}")
    assert res.is_ai_generated, "Citra dengan metadata AI generator harus berhasil diblokir!"


if __name__ == '__main__':
    print("=== MENJALANKAN PENGUJIAN OTOMATIS GATEKEEPER PIPELINE ===")
    test_genuine_sample()
    test_non_plant_rejection()
    test_ai_generated_detection()
    print("=== SELURUH PENGUJIAN (4/4) BERHASIL (PASS) ===")
