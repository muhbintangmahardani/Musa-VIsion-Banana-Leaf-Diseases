"""
MusaVision — YOLO Inference Service
Menjalankan inferensi lokalisasi & klasifikasi lesi patogen daun pisang,
standarisasi pra-pemrosesan CIE-LAB CLAHE (Task 1), telemetri latensi terurai (Task 2),
koreksi granularitas wilayah deteksi (Task 3), dan visualisasi komparasi citra (Task 8).
"""

import os
import cv2
import time
import base64
import numpy as np
from ultralytics import YOLO
from typing import Dict, Any, List, Optional, Tuple
from core.constants import CLASS_COLORS, DISEASE_INFO, CLASS_GRANULARITY
from core.config import get_system_device_name


def image_to_base64(img_bgr: np.ndarray) -> str:
    """Mengonversi citra BGR OpenCV ke format data URL Base64 JPEG."""
    if img_bgr is None or img_bgr.size == 0:
        return ""
    success, buffer = cv2.imencode('.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, 90])
    if not success:
        return ""
    b64_str = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{b64_str}"


def preprocess_lab_clahe(
    img_bgr: np.ndarray,
    target_size: Tuple[int, int] = (640, 640),
    use_clahe: bool = True,
    clip_limit: float = 2.0,
    tile_grid_size: Tuple[int, int] = (8, 8)
) -> Tuple[np.ndarray, str, str]:
    """
    TASK 1 & TASK 8: Standarisasi Pipeline Pra-Pemrosesan CIE-LAB CLAHE.
    1. Letterbox resize mempertahankan aspek rasio asli (padding ke 640x640 dengan warna netral 114).
       Hal ini krusial agar geometri bercak lesi lonjong/oval (Cordana & Pestalotiopsis) tidak terdistorsi pipih
       menyerupai garis bercak Black Sigatoka.
    2. Jika use_clahe is True:
       - Konversi BGR -> CIE-LAB.
       - Terapkan cv2.createCLAHE HANYA pada kanal Luminans (L) agar informasi
         kromatis warna kuning (b) dan merah-hijau (a) tidak bergeser (anti-color shift).
       - Gabungkan kembali (L_clahe, A, B) lalu konversi kembali ke BGR.
    3. Mengembalikan canvas 640x640 preprocessed_bgr, base64 raw_resized (tanpa CLAHE), dan base64 preprocessed_clahe.
    """
    if img_bgr is None or img_bgr.size == 0:
        return None, "", ""

    h, w = img_bgr.shape[:2]
    tw, th = target_size
    scale = min(tw / w, th / h)
    nw, nh = int(round(w * scale)), int(round(h * scale))
    resized = cv2.resize(img_bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)

    if use_clahe:
        lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        l_clahe = clahe.apply(l_ch)
        lab_enhanced = cv2.merge((l_clahe, a_ch, b_ch))
        enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
    else:
        enhanced = resized.copy()

    canvas_preprocessed = np.full((th, tw, 3), 114, dtype=np.uint8)
    canvas_raw = np.full((th, tw, 3), 114, dtype=np.uint8)

    top = (th - nh) // 2
    left = (tw - nw) // 2

    canvas_preprocessed[top:top + nh, left:left + nw] = enhanced
    canvas_raw[top:top + nh, left:left + nw] = resized

    raw_resized_b64 = image_to_base64(canvas_raw)
    preprocessed_clahe_b64 = image_to_base64(canvas_preprocessed)

    return canvas_preprocessed, raw_resized_b64, preprocessed_clahe_b64


def draw_styled_detections(
    img_bgr: np.ndarray,
    boxes,
    class_names: Dict[int, str],
    valid_indices: Optional[List[int]] = None
) -> np.ndarray:
    """
    Merender bounding box berpenampilan modern dengan header tag berlabel dan skor keyakinan.
    Hanya menggambar kotak valid yang telah lolos verifikasi jaringan foliar (tanpa kotak pot/lantai).
    """
    annotated = img_bgr.copy()
    h, w = annotated.shape[:2]

    for idx, box in enumerate(boxes):
        if valid_indices is not None and idx not in valid_indices:
            continue
        cls_id = int(box.cls[0])
        cls_name = class_names[cls_id]
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].cpu().numpy().astype(int)
        x1, y1, x2, y2 = xyxy

        # Ambil warna kelas patogen
        color_rgb = CLASS_COLORS.get(cls_name, (234, 179, 8))
        color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])

        # Gambar garis batas bounding box
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color_bgr, 2, cv2.LINE_AA)

        # Label tag teks
        label_text = f"{cls_name} {conf:.1%}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        thickness = 1
        (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)

        # Posisi kotak tag header
        tag_y1 = max(0, y1 - th - 10)
        tag_y2 = tag_y1 + th + 10
        tag_x2 = min(w, x1 + tw + 14)

        # Latar belakang tag solid
        cv2.rectangle(annotated, (x1, tag_y1), (tag_x2, tag_y2), color_bgr, -1)

        # Warna teks label
        if cls_name in ['Cordana', 'Yellow Sigatoka']:
            text_color = (15, 23, 42)  # Dark slate
        else:
            text_color = (255, 255, 255)

        cv2.putText(
            annotated,
            label_text,
            (x1 + 7, tag_y2 - baseline - 2),
            font,
            font_scale,
            text_color,
            thickness,
            cv2.LINE_AA
        )

    return annotated


def draw_warning_overlay(
    img_bgr: np.ndarray,
    tag_text: str = "",
    details: Optional[List[str]] = None,
    color_bgr: tuple = (30, 30, 225),
    subtitle: Optional[str] = None
) -> np.ndarray:
    """
    Mengembalikan citra bersih tanpa lapisan bingkai/banner/HUD yang menutupi visual citra,
    sesuai instruksi user agar tampilan preview tetap natural.
    """
    return img_bgr.copy()


class InferenceService:
    """
    Layanan inferensi model pembelajaran mendalam YOLO untuk deteksi penyakit daun pisang.
    """

    def __init__(self, model_path: str, fallback_path: Optional[str] = None):
        target_path = model_path
        if not os.path.exists(target_path):
            candidates = [
                fallback_path,
                os.path.join(os.getcwd(), 'best_yolo26n_clahe.pt'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'best_yolo26n_clahe.pt'),
                'best_yolo26n_clahe.pt'
            ]
            for c in candidates:
                if c and os.path.exists(c):
                    print(f"[InferenceService] Model utama tidak ditemukan, menggunakan model alternatif: {c}")
                    target_path = c
                    break

        print(f"[InferenceService] Memuat bobot model YOLO dari: {target_path}")
        self.model = YOLO(target_path)
        self.class_names = self.model.names
        print(f"[InferenceService] Model berhasil diinisialisasi. Daftar Kelas: {self.class_names}")

    @staticmethod
    def compute_disease_scores(diseases_only: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Perhitungan skor patologi terkalibrasi ilmiah:
        Memadukan kuadrat keyakinan puncak (C_max^2) dengan suku pendukung multi-lesi terverifikasi (0.20 * sum(conf^2)).
        Formula ini menahan dominasi kotak besar Black Sigatoka difus agar tidak mengalahkan
        lesi fokal spesifik berkeyakinan tinggi seperti Pestalotiopsis dan Cordana.
        """
        class_max_conf: Dict[str, float] = {}
        class_conf_sum: Dict[str, float] = {}
        for d in diseases_only:
            c = d['class_name']
            conf_val = float(d['confidence']) / 100.0
            if c not in class_max_conf or conf_val > class_max_conf[c]:
                class_max_conf[c] = conf_val
            class_conf_sum[c] = class_conf_sum.get(c, 0.0) + (conf_val ** 2)

        return {
            c: (class_max_conf[c] ** 2) + 0.20 * class_conf_sum[c]
            for c in class_max_conf
        }

    def predict(
        self,
        img_bgr: np.ndarray,
        conf_thresh: float = 0.25,
        iou_thresh: float = 0.45,
        imgsz: int = 640,
        use_clahe: bool = True
    ) -> Dict[str, Any]:
        """
        TASK 1, 2, 3: Menjalankan inferensi deteksi objek dengan telemetri latensi terurai,
        standarisasi LAB-CLAHE, dan koreksi granularitas wilayah deteksi.
        """
        t0 = time.perf_counter()

        # Deteksi tipe hardware kontekstual
        device_name = get_system_device_name()

        # Enforce valid inference threshold minimum (mencegah regim halusinasi noise di bawah 20%)
        conf_thresh = max(0.20, float(conf_thresh))

        # 1. Pra-pemrosesan (Resize + CIE-LAB CLAHE Kanal L)
        preprocessed_bgr, raw_resized_b64, preprocessed_clahe_b64 = preprocess_lab_clahe(
            img_bgr, target_size=(imgsz, imgsz), use_clahe=use_clahe
        )
        t1 = time.perf_counter()
        preprocess_ms = round((t1 - t0) * 1000, 2)

        # Ekstraksi Kanopi Daun Global (Foliar Canopy Mask) pada citra 640x640:
        # Menolak secara tegas bounding box artefak yang menempel pada latar belakang non-daun
        # (lantai, meja kayu coklat, dinding, pot keramik, atau tanah).
        hsv_full = cv2.cvtColor(preprocessed_bgr, cv2.COLOR_BGR2HSV)
        b_full = preprocessed_bgr[:, :, 0].astype(np.float32)
        g_full = preprocessed_bgr[:, :, 1].astype(np.float32)
        r_full = preprocessed_bgr[:, :, 2].astype(np.float32)

        # Jaringan lamina daun pisang mencakup:
        # 1. Klorofil daun hidup (hijau normal):
        mask_green = (
            (hsv_full[:, :, 0] >= 22) & (hsv_full[:, :, 0] <= 98)
            & (hsv_full[:, :, 1] >= 15) & (hsv_full[:, :, 2] >= 20)
            & (g_full > b_full + 5)
        )

        # 2. Klorosis kuning / halo patogen (Yellow Sigatoka & tepi Cordana):
        mask_halo = (
            (hsv_full[:, :, 0] >= 12) & (hsv_full[:, :, 0] <= 42)
            & (hsv_full[:, :, 1] >= 18) & (hsv_full[:, :, 2] >= 25)
            & (g_full > b_full + 8)
        )

        # 3. Jaringan nekrotik / bercak lesi patogen (Black Sigatoka, Cordana, Pestalotiopsis):
        mask_necrotic = (
            (hsv_full[:, :, 0] >= 5) & (hsv_full[:, :, 0] <= 32)
            & (hsv_full[:, :, 1] >= 12) & (hsv_full[:, :, 2] >= 15) & (hsv_full[:, :, 2] <= 215)
            & (r_full >= b_full + 3)
        )

        # 4. Daun tua / zaitun / lamina mengering alami:
        mask_olive = (
            (hsv_full[:, :, 0] >= 18) & (hsv_full[:, :, 0] <= 65)
            & (hsv_full[:, :, 1] >= 10) & (hsv_full[:, :, 2] >= 15)
            & (g_full >= b_full - 5)
        )

        mask_foliar_raw = (mask_green | mask_halo | mask_necrotic | mask_olive).astype(np.uint8) * 255

        # Bersihkan noise isolated speckle pada latar non-daun
        open_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_opened = cv2.morphologyEx(mask_foliar_raw, cv2.MORPH_OPEN, open_k)

        # Pertahankan hanya komponen foliar yang memiliki luas signifikan (area >= 150px)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_opened)
        clean_foliar_mask = np.zeros_like(mask_opened)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= 150:
                clean_foliar_mask[labels == i] = 255

        # Dilatasi untuk menaungi lesi nekrotik dan tepi helai daun
        dilate_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))
        canopy_mask = cv2.dilate(clean_foliar_mask, dilate_k) > 0
        total_leaf_pixels = np.count_nonzero(clean_foliar_mask)

        # 2. Inferensi Model YOLO26n + NMS
        results = self.model.predict(
            source=preprocessed_bgr,
            conf=conf_thresh,
            iou=iou_thresh,
            imgsz=imgsz,
            verbose=False
        )
        t2 = time.perf_counter()
        inference_nms_ms = round((t2 - t1) * 1000, 2)

        res = results[0]
        boxes = res.boxes

        detections: List[Dict[str, Any]] = []
        class_counter: Dict[str, int] = {}
        total_canvas_area = float(imgsz * imgsz)

        # 3. Post-processing, Supresi Penahanan Lesi (Containment), & Ekstraksi Granularitas
        candidates = []
        for idx, box in enumerate(boxes):
            cls_id = int(box.cls[0])
            cls_name = self.class_names[cls_id]
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].cpu().numpy().tolist()
            x1, y1, x2, y2 = [int(v) for v in xyxy]

            box_w = max(1, x2 - x1)
            box_h = max(1, y2 - y1)
            box_area = box_w * box_h

            box_canopy = canopy_mask[max(0, y1):min(imgsz, y2), max(0, x1):min(imgsz, x2)]
            canopy_overlap_ratio = np.count_nonzero(box_canopy) / float(box_area)
            if total_leaf_pixels > 500 and canopy_overlap_ratio < 0.10 and conf < 0.50:
                continue

            candidates.append({
                'idx': idx,
                'cls_name': cls_name,
                'conf': conf,
                'xyxy': xyxy,
                'box_area': box_area,
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2
            })

        # Supresi Penahanan Lesi Antar-Kelas (Intra-Lesion Containment Suppression):
        # Mencegah artefak internal semu tanpa menghapus lesi spesifik (Pestalotiopsis & Cordana).
        suppressed_indices = set()
        for i, c_large in enumerate(candidates):
            for j, c_small in enumerate(candidates):
                if i == j or c_small['idx'] in suppressed_indices:
                    continue
                if c_large['box_area'] < 1.8 * c_small['box_area']:
                    continue
                ix1 = max(c_large['x1'], c_small['x1'])
                iy1 = max(c_large['y1'], c_small['y1'])
                ix2 = min(c_large['x2'], c_small['x2'])
                iy2 = min(c_large['y2'], c_small['y2'])
                inter_w = max(0, ix2 - ix1)
                inter_h = max(0, iy2 - iy1)
                inter_area = inter_w * inter_h
                
                if inter_area >= 0.60 * c_small['box_area']:
                    # Aturan Patologi: Kotak besar Black Sigatoka DILARANG menekan lesi spesifik Pestalotiopsis / Cordana
                    if c_large['cls_name'] == 'Black Sigatoka' and c_small['cls_name'] in ['Pestalotiopsis', 'Cordana']:
                        continue
                    if c_large['cls_name'] != c_small['cls_name'] and c_large['conf'] >= (c_small['conf'] + 0.10):
                        suppressed_indices.add(c_small['idx'])

        valid_indices: List[int] = []
        for c in candidates:
            if c['idx'] in suppressed_indices:
                continue
            idx = c['idx']
            cls_name = c['cls_name']
            conf = c['conf']
            xyxy = c['xyxy']
            x1, y1, x2, y2 = c['x1'], c['y1'], c['x2'], c['y2']

            valid_indices.append(idx)
            class_counter[cls_name] = class_counter.get(cls_name, 0) + 1

            box_w = max(0.0, float(x2 - x1))
            box_h = max(0.0, float(y2 - y1))
            box_area_ratio_pct = round(((box_w * box_h) / total_canvas_area) * 100.0, 2)

            gran_info = CLASS_GRANULARITY.get(cls_name, {
                'granularity_type': 'Deteksi Bounding Box',
                'count_label': 'Wilayah Deteksi',
                'unit_interpretation': 'Wilayah Deteksi',
                'is_lesion_level': True
            })

            detections.append({
                'class_name': cls_name,
                'confidence': round(conf * 100, 1),
                'bbox': [round(x, 1) for x in xyxy],
                'box_area_ratio_pct': box_area_ratio_pct,
                'granularity_type': gran_info.get('granularity_type', ''),
                'count_label': gran_info.get('count_label', ''),
                'unit_interpretation': gran_info.get('unit_interpretation', ''),
                'is_lesion_level': gran_info.get('is_lesion_level', True),
                'color': CLASS_COLORS.get(cls_name, (234, 179, 8))
            })

        # Render citra dengan bounding box
        annotated_bgr = draw_styled_detections(preprocessed_bgr, boxes, self.class_names, valid_indices)
        annotated_b64 = image_to_base64(annotated_bgr)
        original_b64 = image_to_base64(img_bgr)

        t3 = time.perf_counter()
        postprocess_encode_ms = round((t3 - t2) * 1000, 2)
        server_total_ms = round((t3 - t0) * 1000, 2)

        # Pembagian Wilayah Deteksi: Level Lesi vs Level Daun Utuh (Task 3)
        lesion_level_count = sum(1 for d in detections if d.get('is_lesion_level', True))
        leaf_level_count = sum(1 for d in detections if not d.get('is_lesion_level', True))
        avg_box_area_ratio = (
            round(sum(d['box_area_ratio_pct'] for d in detections) / len(detections), 2)
            if detections else 0.0
        )

        # Paket Telemetri Latensi Terurai (Task 2)
        latency_breakdown = {
            "preprocess_ms": preprocess_ms,
            "inference_nms_ms": inference_nms_ms,
            "postprocess_encode_ms": postprocess_encode_ms,
            "server_total_ms": server_total_ms,
            "device_name": device_name,
            "input_resolution": f"{imgsz}x{imgsz}",
            "clahe_mode": (
                "CIE-LAB (Channel L, ClipLimit=2.0, Grid=8x8)"
                if use_clahe
                else "Non-CLAHE (Standard RGB/BGR)"
            ),
            "iou_threshold": iou_thresh,
            "conf_threshold": conf_thresh
        }

        # Penentuan diagnosis utama
        if len(detections) == 0:
            primary_class = 'Uncertain'
            summary_title = 'Tidak Terdeteksi Lesi Patologis'
            summary_description = (
                'Model tidak mendeteksi adanya lesi penyakit aktif pada spesimen daun ini pada ambang batas keyakinan standar (25%). '
                'Permukaan helai daun tampak sehat atau pastikan foto difokuskan tegak lurus pada permukaan daun.'
            )
            disease_detail = None
        else:
            diseases_only = [d for d in detections if d['class_name'] != 'Fresh']
            if diseases_only:
                # Perhitungan skor patologi terkalibrasi ilmiah via compute_disease_scores
                class_scores = self.compute_disease_scores(diseases_only)
                primary_class = max(class_scores, key=class_scores.get)
                primary_count = sum(1 for d in diseases_only if d['class_name'] == primary_class)
                p_gran = CLASS_GRANULARITY.get(primary_class, {})
                unit_label = p_gran.get('count_label', 'Wilayah Deteksi')
                summary_title = f"Terindikasi {primary_class} ({primary_count} {unit_label})"
                summary_description = (
                    f"Ditemukan {primary_count} {unit_label.lower()} yang bersesuaian dengan "
                    f"karakteristik patogen {primary_class}."
                )
            else:
                primary_class = 'Fresh'
                summary_title = "Daun Terkategori Sehat (Fresh)"
                summary_description = "Seluruh helai daun teridentifikasi normal tanpa lesi patologis aktif."

            disease_detail = DISEASE_INFO.get(primary_class, None)

        return {
            'success': True,
            'inference_time_ms': server_total_ms,
            'latency_breakdown': latency_breakdown,
            'total_detections': len(detections),
            'total_regions': len(detections),
            'lesion_level_count': lesion_level_count,
            'leaf_level_count': leaf_level_count,
            'avg_box_area_ratio': avg_box_area_ratio,
            'avg_box_area_ratio_pct': avg_box_area_ratio,
            'region_count': {
                'total_regions': len(detections),
                'lesion_level_count': lesion_level_count,
                'leaf_level_count': leaf_level_count
            },
            'primary_class': primary_class,
            'summary_title': summary_title,
            'summary_description': summary_description,
            'disease_info': disease_detail,
            'detections': detections,
            'class_counter': class_counter,
            'original_image': original_b64,
            'raw_resized_base64': raw_resized_b64,
            'preprocessed_clahe_base64': preprocessed_clahe_b64,
            'annotated_result_base64': annotated_b64,
            'annotated_image': annotated_b64
        }
