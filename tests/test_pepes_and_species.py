import os
import sys
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import config
from core.constants import ErrorCode
from services.species_validator import SpeciesValidatorService

def test_dicot_leaf_rejection():
    """Menguji penolakan daun tanaman spesies lain (daun dikotil bukan pisang)."""
    validator = SpeciesValidatorService(
        min_vegetation_ratio=config.MIN_VEGETATION_RATIO,
        min_living_chlorophyll=config.MIN_LIVING_CHLOROPHYLL_RATIO,
        max_charred_soot=config.MAX_CHARRED_SOOT_RATIO,
        min_gabor_anisotropy=config.MIN_GABOR_ANISOTROPY,
        min_parallelism=config.MIN_VENATION_PARALLELISM
    )

    # Uji citra daun tanaman non-pisang (daun dikotil menjari / berlekuk)
    path = os.path.join(config.BASE_DIR, 'test', 'images (4).jpg')
    if os.path.exists(path):
        img = cv2.imread(path)
    else:
        img = np.full((400, 400, 3), 220, dtype=np.uint8)
        pts = np.array([[200, 40], [230, 150], [360, 150], [260, 230], [300, 360], [200, 270], [100, 360], [140, 230], [40, 150], [170, 150]], np.int32)
        cv2.fillPoly(img, [pts], (35, 165, 45))

    res = validator.validate(img)
    print(f"[TEST NON-BANANA] Category: {res.detected_category} | Anisotropy: {res.gabor_anisotropy} | is_banana: {res.is_banana_leaf}")
    assert not res.is_banana_leaf, "Daun non-pisang harus ditolak oleh Species Validator!"
    assert res.error_code == ErrorCode.NON_BANANA_LEAF.value


def test_cooked_pepes_leaf_rejection():
    """Menguji penolakan daun pisang olahan/pepes yang terbakar/hangus sebagai objek non-daun pisang."""
    validator = SpeciesValidatorService(
        min_vegetation_ratio=config.MIN_VEGETATION_RATIO,
        min_living_chlorophyll=config.MIN_LIVING_CHLOROPHYLL_RATIO,
        max_charred_soot=config.MAX_CHARRED_SOOT_RATIO,
        min_gabor_anisotropy=config.MIN_GABOR_ANISOTROPY,
        min_parallelism=config.MIN_VENATION_PARALLELISM
    )

    # Ambil daun pisang asli, lalu simulasikan efek memasak pepes (hilangnya klorofil cerah & goresan arang panggangan)
    base_sample = cv2.imread(os.path.join(config.SAMPLES_DIR, 'sample_fresh.jpg'))
    pepes_simulated = base_sample.copy()

    # Efek panas memasak pepes: klorofil hijau cerah terdenaturasi menjadi warna zaitun kusam/matang
    hsv_p = cv2.cvtColor(pepes_simulated, cv2.COLOR_BGR2HSV)
    hsv_p[:, :, 0] = np.clip(hsv_p[:, :, 0] * 0.45, 20, 35).astype(np.uint8)
    hsv_p[:, :, 1] = np.clip(hsv_p[:, :, 1] * 0.5, 30, 80).astype(np.uint8)
    pepes_simulated = cv2.cvtColor(hsv_p, cv2.COLOR_HSV2BGR)

    # Goresan hangus panggangan arang pepes (charred soot V <= 28)
    h, w = pepes_simulated.shape[:2]
    cv2.rectangle(pepes_simulated, (w//6, h//4), (5*w//6, h//4 + h//4), (10, 10, 10), -1)
    cv2.rectangle(pepes_simulated, (w//4, 3*h//5), (3*w//4, 3*h//5 + h//5), (10, 10, 10), -1)

    res = validator.validate(pepes_simulated)
    print(f"[TEST NON-LEAF/PEPES] Category: {res.detected_category} | Charred: {res.charred_soot_ratio}% | is_banana: {res.is_banana_leaf}")
    assert not res.is_banana_leaf, "Daun terbakar/olahan harus ditolak!"
    assert res.error_code in [ErrorCode.NON_PLANT_OBJECT.value, ErrorCode.NON_BANANA_LEAF.value]


def test_palmate_ornamental_plant_rejection():
    """Menguji penolakan tanaman hias daun menjari/dikotil dalam pot (Foto User 2)."""
    validator = SpeciesValidatorService(
        min_vegetation_ratio=config.MIN_VEGETATION_RATIO,
        min_living_chlorophyll=config.MIN_LIVING_CHLOROPHYLL_RATIO,
        max_charred_soot=config.MAX_CHARRED_SOOT_RATIO,
        min_gabor_anisotropy=config.MIN_GABOR_ANISOTROPY,
        min_parallelism=config.MIN_VENATION_PARALLELISM
    )

    path = r"C:\Users\M Bintang Mahardani\.gemini\antigravity\brain\5db4b8ec-421a-4b2b-9153-5cf034545f17\.user_uploaded\media_1793886754946_33ce9afa.jpg"
    if os.path.exists(path):
        img = cv2.imread(path)
        res = validator.validate(img)
        print(f"[TEST PALMATE/POT] Category: {res.detected_category} | Aniso: {res.gabor_anisotropy} | is_banana: {res.is_banana_leaf}")
        assert not res.is_banana_leaf, "Tanaman hias daun menjari/pot harus ditolak sebagai daun non-pisang!"
        assert res.error_code == ErrorCode.NON_BANANA_LEAF.value


if __name__ == '__main__':
    print("=== MENGUJI PENOLAKAN DAUN NON-PISANG & DAUN PEPES ===")
    test_dicot_leaf_rejection()
    test_palmate_ornamental_plant_rejection()
    test_cooked_pepes_leaf_rejection()
    print("=== SELURUH PENGUJIAN DAUN NON-PISANG & PEPES BERHASIL (PASS) ===")

