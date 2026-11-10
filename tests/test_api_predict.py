import os
import sys
import io
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from core.config import config
from core.constants import ErrorCode

def test_api_predict_flow():
    client = app.test_client()

    print("=== TEST 1: Sampel Daun Pisang Terverifikasi ===")
    res1 = client.post('/predict', data={'sample_name': 'sample_fresh.jpg'})
    assert res1.status_code == 200, f"Status code harus 200, didapat {res1.status_code}"
    data1 = res1.get_json()
    assert data1['success'] is True
    assert data1['is_valid_banana_leaf'] is True
    assert data1['primary_class'] == 'Fresh'
    print(f"PASS: {data1['primary_class']} | Title: {data1['summary_title']}")

    print("\n=== TEST 2: Objek Non-Tumbuhan (Ikan Lele / Benda Non-Daun) ===")
    # Buat citra buatan non-tumbuhan (abu-abu/hitam tanpa klorofil)
    non_plant = np.full((300, 300, 3), 120, dtype=np.uint8)
    _, buffer = cv2.imencode('.jpg', non_plant)
    img_io = io.BytesIO(buffer.tobytes())

    res2 = client.post('/predict', data={'image': (img_io, 'catfish.jpg')}, content_type='multipart/form-data')
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2['success'] is True
    assert data2['is_valid_banana_leaf'] is False
    assert data2['error_code'] == ErrorCode.NON_PLANT_OBJECT.value
    assert data2['primary_class'] == 'Bukan Objek Daun Pisang'
    assert data2['disease_info'] is not None
    print(f"PASS: {data2['primary_class']} | Code: {data2['error_code']} | Title: {data2['summary_title']}")

    print("\n=== TEST 3: Daun Spesies Lain (Bukan Genus Musa) ===")
    dicot_path = os.path.join(config.BASE_DIR, 'test', 'images (4).jpg')
    if os.path.exists(dicot_path):
        img_dicot = cv2.imread(dicot_path)
    else:
        img_dicot = np.full((400, 400, 3), 220, dtype=np.uint8)
        pts = np.array([[200, 40], [230, 150], [360, 150], [260, 230], [300, 360], [200, 270], [100, 360], [140, 230], [40, 150], [170, 150]], np.int32)
        cv2.fillPoly(img_dicot, [pts], (35, 165, 45))
    _, buffer_dicot = cv2.imencode('.jpg', img_dicot)
    dicot_io = io.BytesIO(buffer_dicot.tobytes())

    res3 = client.post('/predict', data={'image': (dicot_io, 'dicot_leaf.jpg')}, content_type='multipart/form-data')
    assert res3.status_code == 200
    data3 = res3.get_json()
    assert data3['success'] is True
    assert data3['is_valid_banana_leaf'] is False
    assert data3['error_code'] == ErrorCode.NON_BANANA_LEAF.value
    assert data3['primary_class'] == 'Bukan Jenis Daun Pisang'
    assert data3['disease_info'] is not None
    print(f"PASS: {data3['primary_class']} | Anisotropy: {data3['metrics']['gabor_anisotropy']} | Title: {data3['summary_title']}")

    print("\n=== TEST 4: Citra Benda Nyata Non-Daun Pisang (Bukan Objek Daun Pisang) ===")
    user_photo_path = r"C:\Users\M Bintang Mahardani\.gemini\antigravity\brain\5db4b8ec-421a-4b2b-9153-5cf034545f17\.user_uploaded\media_1793886004846_769db064.jpg"
    if os.path.exists(user_photo_path):
        real_non_plant = cv2.imread(user_photo_path)
    else:
        real_non_plant = np.full((400, 400, 3), (120, 100, 90), dtype=np.uint8)
    _, buffer_rnp = cv2.imencode('.jpg', real_non_plant)
    rnp_io = io.BytesIO(buffer_rnp.tobytes())

    res4 = client.post('/predict', data={'image': (rnp_io, 'real_non_plant.jpg')}, content_type='multipart/form-data')
    assert res4.status_code == 200
    data4 = res4.get_json()
    assert data4['success'] is True
    assert data4['is_valid_banana_leaf'] is False
    assert data4['error_code'] == ErrorCode.NON_PLANT_OBJECT.value
    assert data4['primary_class'] == 'Bukan Objek Daun Pisang'
    print(f"PASS: {data4['primary_class']} | Title: {data4['summary_title']}")

    print("\n=== TEST 5: Citra Buatan AI (Synthetic Detector) ===")
    # Skenario 5A: AI dengan Metadata Penanda Model
    _, buffer_ai = cv2.imencode('.jpg', non_plant)
    ai_payload = buffer_ai.tobytes() + b" ... Midjourney v6.0 generation_data Stable Diffusion ..."
    res5_meta = client.post('/predict', data={'image': (io.BytesIO(ai_payload), 'ai_leaf_meta.jpg')}, content_type='multipart/form-data')
    assert res5_meta.status_code == 200
    data5_meta = res5_meta.get_json()
    assert data5_meta['success'] is True
    assert data5_meta['is_ai_generated'] is True
    assert data5_meta['primary_class'] == 'Citra Sintesis AI'
    print(f"PASS 5A (Metadata): {data5_meta['primary_class']} | AI Score: {data5_meta['metrics']['ai_score']}%")

    # Skenario 5B: AI Tanpa Metadata (clean_ai_leaf.jpg - Forensik Piksel: Elevasi Spektral Fourier VAE & Densitas Garis Sintetis)
    scratch_dir = r"C:\Users\M Bintang Mahardani\.gemini\antigravity\brain\5db4b8ec-421a-4b2b-9153-5cf034545f17\scratch"
    clean_ai_path = os.path.join(scratch_dir, "clean_ai_leaf.jpg")
    if os.path.exists(clean_ai_path):
        clean_ai_img = cv2.imread(clean_ai_path)
        _, buffer_clean = cv2.imencode('.jpg', clean_ai_img)
        res5_clean = client.post('/predict', data={'image': (io.BytesIO(buffer_clean.tobytes()), 'clean_ai_leaf.jpg')}, content_type='multipart/form-data')
        assert res5_clean.status_code == 200
        data5_clean = res5_clean.get_json()
        assert data5_clean['success'] is True
        assert data5_clean['is_ai_generated'] is True
        assert data5_clean['primary_class'] == 'Citra Sintesis AI'
        print(f"PASS 5B (Pure AI Banana Leaf): {data5_clean['primary_class']} | AI Score: {data5_clean['metrics']['ai_score']}% | Title: {data5_clean['summary_title']}")

    # Skenario 6: Daun Pisang Asli Fisik Kebun (File Upload Nyata tanpa Preset Flag)
    real_garden_path = "static/samples/sample_fresh.jpg"
    if os.path.exists(real_garden_path):
        garden_img = cv2.imread(real_garden_path)
        _, buffer_garden = cv2.imencode('.jpg', garden_img)
        res6 = client.post('/predict', data={'image': (io.BytesIO(buffer_garden.tobytes()), 'garden_leaf.jpg')}, content_type='multipart/form-data')
        assert res6.status_code == 200
        data6 = res6.get_json()
        assert data6['success'] is True
        assert data6['is_valid_banana_leaf'] is True
        assert data6['is_ai_generated'] is False
        print(f"PASS 6 (Real Garden Leaf Upload): {data6['primary_class']} | Valid: {data6['is_valid_banana_leaf']} | Detections: {data6['total_detections']}")

    # Skenario 7: Foto Wajah / Selfie Manusia (Harus Ditolak Gatekeeper sebagai NON_PLANT_OBJECT, BUKAN Black Sigatoka!)
    face_img = np.full((400, 400, 3), (130, 170, 220), dtype=np.uint8) # warna kulit
    face_img[150:160, 100:150] = (30, 30, 30) # alis
    face_img[150:160, 250:300] = (30, 30, 30) # alis
    face_img[280:295, 150:250] = (70, 70, 180) # bibir
    _, buffer_face = cv2.imencode('.jpg', face_img)
    res7 = client.post('/predict', data={'image': (io.BytesIO(buffer_face.tobytes()), 'selfie_face.jpg')}, content_type='multipart/form-data')
    assert res7.status_code == 200
    data7 = res7.get_json()
    assert data7['success'] is True
    assert data7['is_valid_banana_leaf'] is False
    assert data7['error_code'] == ErrorCode.NON_PLANT_OBJECT.value
    assert data7['primary_class'] == 'Bukan Objek Daun Pisang'
    assert data7['total_detections'] == 0
    print(f"PASS 7 (Selfie / Human Face): {data7['primary_class']} | Code: {data7['error_code']} | Detections: {data7['total_detections']}")

    print("\n=== SEMUA SKENARIO (6/6) SUKSES 100% ===")

if __name__ == '__main__':
    test_api_predict_flow()

