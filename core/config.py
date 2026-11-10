"""
MusaVision — Core Configuration
Menyimpan konfigurasi path, ambang batas inferensi, dan parameter validasi pra-inferensi.
"""

import os
from dataclasses import dataclass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class AppConfig:
    """Konfigurasi immutable aplikasi dan model pembelajaran mesin."""
    BASE_DIR: str = BASE_DIR
    
    # Prioritaskan bobot model terbaik hasil training YOLO26n CLAHE di direktori utama
    MODEL_PATH: str = os.path.join(BASE_DIR, 'best_yolo26n_clahe.pt')
    FALLBACK_MODEL_PATH: str = os.path.join(BASE_DIR, 'MusaVision_Sidang_Data', 'best_yolo26n_clahe.pt')
    SECONDARY_FALLBACK_PATH: str = os.path.join(BASE_DIR, 'MusaVision_Sidang_Data', '4_YOLO26n_LAB_CLAHE', 'weights', 'best.pt')
    SAMPLES_DIR: str = os.path.join(BASE_DIR, 'static', 'samples')
    SIDANG_DATA_DIR: str = os.path.join(BASE_DIR, 'MusaVision_Sidang_Data')
    
    # Ambang batas default inferensi YOLO (Optimal untuk memangkas false-positive pada latar non-daun)
    DEFAULT_CONF_THRESHOLD: float = 0.40
    DEFAULT_IOU_THRESHOLD: float = 0.45
    IMG_SIZE: int = 640
    
    # Parameter Pra-Pemrosesan CIE-LAB CLAHE
    DEFAULT_USE_CLAHE: bool = True
    CLAHE_CLIP_LIMIT: float = 2.0
    CLAHE_TILE_GRID_SIZE: tuple = (8, 8)
    
    # Ambang batas deteksi citra sintetis AI
    AI_DETECTION_THRESHOLD: float = 0.55
    
    # Ambang batas validasi genus Musa (Daun Pisang Hidup di Pohon)
    MIN_VEGETATION_RATIO: float = 0.15           # Minimal biomassa foliar (daun hijau/kuning/nekrotik)
    MIN_LIVING_CHLOROPHYLL_RATIO: float = 0.05   # Minimal klorofil aktif pada daun hidup
    MAX_CHARRED_SOOT_RATIO: float = 0.12         # Maksimal batas hangus/arang (pepes/bakar)
    MIN_GABOR_ANISOTROPY: float = 0.80           # Minimal keteraturan serat sejajar monokotil genus Musa
    MIN_VENATION_PARALLELISM: float = 0.16       # Konsentrasi puncak sudut pertulangan daun sejajar


config = AppConfig()


def get_system_device_name() -> str:
    """
    Mendeteksi secara akurat spesifikasi perangkat keras (GPU / CPU) yang digunakan.
    Mendukung deteksi GPU CUDA serta nama prosesor CPU lokal (misal: Intel Core i5 Gen 8).
    """
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            return f"GPU ({gpu_name} - PyTorch FP32/AMP)"
    except Exception:
        pass

    # Deteksi nama prosesor di OS Windows via Registry
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        cpu_clean = " ".join(cpu_name.strip().split())
        if cpu_clean:
            return f"CPU ({cpu_clean})"
    except Exception:
        pass

    import platform
    proc = platform.processor()
    if proc:
        return f"CPU ({proc})"

    return "CPU (PyTorch FP32)"


