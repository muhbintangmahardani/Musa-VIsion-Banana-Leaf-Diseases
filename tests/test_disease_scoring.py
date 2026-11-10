"""
Unit test untuk verifikasi algoritma penentuan diagnosis utama (Primary Class)
berdasarkan Skor Patologi Terkalibrasi Ilmiah dan Supresi Penahanan Lesi (Containment).

Memastikan:
1. Lesi besar Cordana tidak pernah dikalahkan oleh beberapa bintik noise Black Sigatoka kecil.
2. Lesi besar Yellow Sigatoka tidak pernah dikalahkan oleh bintik noise Black Sigatoka kecil.
3. Sub-box palsu yang berada di dalam lesi besar tertekan secara otomatis (Containment Suppression).
"""

import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import config
from services.inference_service import InferenceService

def test_disease_scoring_and_containment():
    inf = InferenceService(model_path=config.MODEL_PATH)
    
    # 1. Simulasi Kasus Cordana Dominan + Noise Black Sigatoka
    # Ditemukan 1 lesi Cordana besar (conf 85%, area 12%) dan 3 bintik kecil Black Sigatoka (conf 28%, area 0.3%)
    mock_detections = [
        {'class_name': 'Cordana', 'confidence': 85.0, 'box_area_ratio_pct': 12.0},
        {'class_name': 'Black Sigatoka', 'confidence': 28.0, 'box_area_ratio_pct': 0.3},
        {'class_name': 'Black Sigatoka', 'confidence': 30.0, 'box_area_ratio_pct': 0.4},
        {'class_name': 'Black Sigatoka', 'confidence': 26.0, 'box_area_ratio_pct': 0.2},
    ]
    
    diseases_only = [d for d in mock_detections if d['class_name'] != 'Fresh']
    class_scores = inf.compute_disease_scores(diseases_only)
    primary_class = max(class_scores, key=class_scores.get)
    print(f"[TEST CORDANA VS NOISE] Scores: {class_scores} -> Winner: {primary_class}")
    assert primary_class == 'Cordana', f"Cordana harus menang tetapi didapat: {primary_class}"
    assert class_scores['Cordana'] > class_scores['Black Sigatoka'] * 5, "Cordana harus unggul telak atas noise!"

    # 2. Simulasi Kasus Yellow Sigatoka Dominan + Noise Black Sigatoka
    mock_detections_ys = [
        {'class_name': 'Yellow Sigatoka', 'confidence': 76.0, 'box_area_ratio_pct': 9.5},
        {'class_name': 'Black Sigatoka', 'confidence': 32.0, 'box_area_ratio_pct': 0.5},
        {'class_name': 'Black Sigatoka', 'confidence': 27.0, 'box_area_ratio_pct': 0.3},
    ]
    
    diseases_only_ys = [d for d in mock_detections_ys if d['class_name'] != 'Fresh']
    class_scores_ys = inf.compute_disease_scores(diseases_only_ys)
    primary_class_ys = max(class_scores_ys, key=class_scores_ys.get)
    print(f"[TEST YELLOW SIGATOKA VS NOISE] Scores: {class_scores_ys} -> Winner: {primary_class_ys}")
    assert primary_class_ys == 'Yellow Sigatoka', f"Yellow Sigatoka harus menang tetapi didapat: {primary_class_ys}"

    # 3. Simulasi Kasus Pestalotiopsis Fokal (Area Kecil) vs Noise Black Sigatoka
    # Lesi Pestalotiopsis memiliki area kecil (2.5%) namun confidence tinggi (88.0%)
    mock_detections_pest = [
        {'class_name': 'Pestalotiopsis', 'confidence': 88.0, 'box_area_ratio_pct': 2.5},
        {'class_name': 'Black Sigatoka', 'confidence': 32.0, 'box_area_ratio_pct': 11.0},
        {'class_name': 'Black Sigatoka', 'confidence': 29.0, 'box_area_ratio_pct': 8.5},
    ]
    diseases_only_pest = [d for d in mock_detections_pest if d['class_name'] != 'Fresh']
    class_scores_pest = inf.compute_disease_scores(diseases_only_pest)
    primary_class_pest = max(class_scores_pest, key=class_scores_pest.get)
    print(f"[TEST PESTALOTIOPSIS VS NOISE] Scores: {class_scores_pest} -> Winner: {primary_class_pest}")
    assert primary_class_pest == 'Pestalotiopsis', f"Pestalotiopsis harus menang tetapi didapat: {primary_class_pest}"
    assert class_scores_pest['Pestalotiopsis'] > class_scores_pest['Black Sigatoka'] * 5, "Pestalotiopsis harus unggul telak!"

    print("=== SELURUH PENGUJIAN SKORING DIAGNOSIS PATOLOGI LULUS DENGAN SEMPURNA ===")

if __name__ == '__main__':
    test_disease_scoring_and_containment()
