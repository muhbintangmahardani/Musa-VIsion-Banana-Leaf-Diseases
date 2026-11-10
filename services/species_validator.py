"""
MusaVision — Banana Leaf Species & Genus Musa Validator Service
Mengevaluasi secara ketat apakah citra masukan benar merupakan daun tanaman pisang hidup
(Genus Musa spp. in-vivo foliar) berdasarkan:
  1. Rasio biomassa vegetasi & klorofil hidup (menolak objek non-tumbuhan).
  2. Pendeteksian degradasi termal / hangus arang (menolak daun pisang olahan kuliner / pepes).
  3. Analisis anisotropi filter Gabor multi-sudut (menolak daun tanaman spesies lain / dikotil).
  4. Koherensi pertulangan menyirip sejajar monokotil (parallel-pinnate venation).
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional
from core.constants import ErrorCode


@dataclass
class SpeciesValidationResult:
    """Hasil validasi taksonomi dan kelayakan fisiologis daun pisang."""
    is_banana_leaf: bool
    error_code: str                 # ErrorCode string (None jika valid)
    detected_category: str          # "Daun Pisang Hidup (Musa spp.)", "Daun Olahan / Pepes", "Daun Tanaman Lain", "Objek Non-Tumbuhan"
    banana_confidence: float        # Rentang 0.0 - 100.0%
    vegetation_ratio: float         # 0.0 - 100.0% (proporsi kanopi daun)
    living_chlorophyll_ratio: float # 0.0 - 100.0% (proporsi klorofil aktif tanaman hidup)
    charred_soot_ratio: float       # 0.0 - 100.0% (proporsi hangus / arang / gosong pembakaran)
    gabor_anisotropy: float         # 0.0 - 1.0 (tingkat keseragaman arah serat monokotil sejajar)
    venation_parallelism: float     # 0.0 - 1.0 (konsentrasi sudut serat utama)
    reason: str
    guidance: str


class SpeciesValidatorService:
    """
    Layanan validasi taksonomi eksklusif untuk genus Musa (Pohon Pisang) dan filtrasi daun olahan.
    """

    def __init__(
        self,
        min_vegetation_ratio: float = 0.10,
        min_living_chlorophyll: float = 0.05,
        max_charred_soot: float = 0.12,
        min_gabor_anisotropy: float = 0.80,
        min_parallelism: float = 0.16
    ):
        self.min_vegetation_ratio = min_vegetation_ratio
        self.min_living_chlorophyll = min_living_chlorophyll
        self.max_charred_soot = max_charred_soot
        self.min_gabor_anisotropy = min_gabor_anisotropy
        self.min_parallelism = min_parallelism

    def _extract_biomass_metrics(self, img_bgr: np.ndarray) -> Dict[str, Any]:
        """
        Menganalisis klorofil daun hidup sejati (True Living Foliar Chlorophyll),
        deteksi kulit manusia/ruangan, daun kusam bungkus pepes, dan arang gosong.
        """
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        total_pixels = img_bgr.shape[0] * img_bgr.shape[1] + 1e-6

        b_ch = img_bgr[:, :, 0].astype(np.float32)
        g_ch = img_bgr[:, :, 1].astype(np.float32)
        r_ch = img_bgr[:, :, 2].astype(np.float32)

        # 1. Klorofil Hijau Daun Hidup (Green Foliar Chlorophyll):
        # Karakteristik daun tumbuhan hidup: H: 24-95, G >= R - 5 dan G > B + 12
        mask_green = (
            (hsv[:, :, 0] >= 24) & (hsv[:, :, 0] <= 95)
            & (hsv[:, :, 1] >= 25) & (hsv[:, :, 2] >= 25)
            & (g_ch >= r_ch - 5) & (g_ch > b_ch + 12)
        )

        # 2. Lingkaran Halo Klorosis & Daun Menguning (Yellow Chlorosis / Senescence):
        # Khas pada lesi Yellow Sigatoka, tepi Cordana, dan daun menguning aktif
        # Memiliki warna kuning sejati (absorpsi biru kuat B < 130 dan komponen hijau tinggi G > B + 18)
        mask_halo = (
            (hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 32)
            & (hsv[:, :, 1] >= 35) & (hsv[:, :, 2] >= 35)
            & (g_ch > b_ch + 18) & (b_ch < 130)
            & (r_ch <= g_ch + 30)
        )

        # Klorofil & Jaringan Hidup Tanaman (True Living Foliar Chlorophyll):
        mask_living = mask_green | mask_halo
        living_pixels = np.count_nonzero(mask_living)
        living_foliar_ratio = float(living_pixels / total_pixels)

        # 3. Deteksi Warna Kulit Manusia (Human Skin Detector):
        # Kulit manusia memiliki R > G + 15, R > B + 20, Hue <= 25, Saturation >= 20, Value >= 40
        mask_skin = (
            (r_ch > g_ch + 15) & (r_ch > b_ch + 20)
            & (hsv[:, :, 0] <= 25) & (hsv[:, :, 1] >= 20) & (hsv[:, :, 2] >= 40)
        )
        skin_ratio = float(np.count_nonzero(mask_skin) / total_pixels)

        # 4. Jaringan Nekrotik / Bercak Lesi Cokelat / Karat Patogen Daun:
        # PENTING: Lesi nekrotik daun pisang selalu menempel atau berada di sekitar lamina daun hidup
        leaf_vicinity = cv2.dilate(mask_living.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35))) > 0
        mask_necrotic = (
            (hsv[:, :, 0] >= 5) & (hsv[:, :, 0] <= 32)
            & (hsv[:, :, 1] >= 15) & (hsv[:, :, 2] >= 15) & (hsv[:, :, 2] <= 215)
            & (r_ch >= b_ch + 3)
            & leaf_vicinity
        )

        # Total Biomassa Jaringan Daun (Foliar Lamina Biomass) = Jaringan Hidup + Lesi Nekrotik di atas daun
        mask_foliar = mask_living | mask_necrotic
        foliar_pixels = np.count_nonzero(mask_foliar)
        total_foliar_ratio = float(foliar_pixels / total_pixels)

        # 5. Daun Pisang Olahan / Matang Kusam (Bungkus Pepes Pasca-Panen)
        mask_dull_cooked = (
            (hsv[:, :, 0] >= 15) & (hsv[:, :, 0] <= 55)
            & (hsv[:, :, 1] >= 20)
            & (hsv[:, :, 2] >= 20) & (hsv[:, :, 2] <= 180)
            & (g_ch >= b_ch - 5) & (r_ch <= g_ch + 35)
        )
        dull_leaf_ratio = float(np.count_nonzero(mask_dull_cooked) / total_pixels)

        # 6. Arang / Hangus Gosong Pembakaran (V <= 28)
        mask_charred = (hsv[:, :, 2] <= 28)
        dull_dilated = cv2.dilate(mask_dull_cooked.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15)))
        mask_leaf_charred = mask_charred & (dull_dilated > 0)
        leaf_charred_ratio = float(np.count_nonzero(mask_leaf_charred) / total_pixels)
        charred_ratio = float(np.count_nonzero(mask_charred) / total_pixels)

        green_pixels = np.count_nonzero(mask_green)
        halo_pixels = np.count_nonzero(mask_halo)

        green_ratio = float(green_pixels / total_pixels)
        halo_ratio = float(halo_pixels / total_pixels)

        # Mask daun untuk penentuan bounding box ROI dan analisis tekstur internal lamina
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cleaned_foliar = cv2.morphologyEx((mask_foliar.astype(np.uint8)) * 255, cv2.MORPH_CLOSE, kernel)

        # Analisis bentuk kontur: Deteksi daun berlekuk/menjari (lobed/palmate dicot seperti pepaya/jarak/maple)
        is_lobed_leaf = False
        contours, _ = cv2.findContours(cleaned_foliar, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 10000:
                hull = cv2.convexHull(cnt)
                hull_area = cv2.contourArea(hull)
                solidity = area / (hull_area + 1e-6)
                # Daun pisang selalu utuh (entire margin) dengan solidity >= 0.75. Daun menjari memiliki lekukan dalam (< 0.70)
                if solidity < 0.70:
                    is_lobed_leaf = True
                    break

        # Analisis tekstur internal lamina: Erosi untuk membuang batas/kontur luar daun
        erode_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        eroded_mask = cv2.erode(cleaned_foliar, erode_kernel, iterations=2)
        gray_img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        gx = cv2.Sobel(gray_img, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_img, cv2.CV_32F, 0, 1, ksize=3)
        mag = np.sqrt(gx**2 + gy**2)
        
        valid_lamina = eroded_mask > 0
        if np.count_nonzero(valid_lamina) > 300:
            internal_mag_mean = float(np.mean(mag[valid_lamina]))
        else:
            internal_mag_mean = 0.0

        return {
            'mask_leaf': cleaned_foliar,
            'eroded_mask': eroded_mask,
            'veg_ratio': total_foliar_ratio,
            'living_foliar_ratio': living_foliar_ratio,
            'living_ratio': green_ratio,
            'green_ratio': green_ratio,
            'halo_ratio': halo_ratio,
            'charred_ratio': charred_ratio,
            'leaf_charred_ratio': leaf_charred_ratio,
            'dull_leaf_ratio': dull_leaf_ratio,
            'skin_ratio': skin_ratio,
            'is_lobed_leaf': is_lobed_leaf,
            'internal_mag_mean': internal_mag_mean
        }

    def _compute_gabor_anisotropy(self, gray_img: np.ndarray, mask_leaf: Optional[np.ndarray] = None) -> float:
        """
        Menghitung anisotropi orientasi menggunakan bank Gabor filter pada 8 arah sudut.
        Dihitung pada wilayah lamina daun utama dan patch tengah agar tekstur pohon/latar
        kebun tidak mengacaukan pola serat menyirip sejajar khas genus Musa.
        """
        h, w = gray_img.shape
        cy, cx = h // 2, w // 2
        r_h = min(120, max(40, h // 3))
        r_w = min(120, max(40, w // 3))
        center_patch = gray_img[cy - r_h : cy + r_h, cx - r_w : cx + r_w]

        def _calc_aniso(img_patch: np.ndarray) -> float:
            if img_patch is None or img_patch.size < 100:
                return 0.0
            if float(np.std(img_patch)) < 4.0:
                return 0.0
            resized = cv2.resize(img_patch, (128, 128), interpolation=cv2.INTER_AREA)
            energies = []
            for theta in np.linspace(0, np.pi, 8, endpoint=False):
                kernel = cv2.getGaborKernel((15, 15), 3.0, theta, 6.0, 0.5, 0, ktype=cv2.CV_32F)
                filtered = cv2.filter2D(resized.astype(np.float32), cv2.CV_32F, kernel)
                energies.append(float(np.mean(filtered**2)))
            max_e = max(energies)
            min_e = min(energies)
            return float((max_e - min_e) / (max_e + min_e + 1e-6))

        # PENTING: Patch tengah HANYA boleh dihitung jika patch tengah didominasi lamina daun (mask_leaf >= 30%)
        # Mencegah wajah manusia (mata/alis/bibir horizontal) terhitung sebagai serat daun pisang (anisotropi semu)!
        aniso_center = 0.0
        if mask_leaf is not None:
            center_mask = mask_leaf[cy - r_h : cy + r_h, cx - r_w : cx + r_w]
            if np.count_nonzero(center_mask) >= (0.30 * center_patch.size):
                aniso_center = _calc_aniso(center_patch)

        # Jika ada mask_leaf dengan komponen besar, hitung juga pada komponen terbesar
        aniso_roi = 0.0
        if mask_leaf is not None and np.count_nonzero(mask_leaf) > 500:
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_leaf)
            if num_labels > 1:
                largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
                x, y, w_box, h_box, area_box = stats[largest_label]
                if area_box >= (0.05 * h * w) and w_box > 30 and h_box > 30:
                    roi = gray_img[y:y+h_box, x:x+w_box]
                    aniso_roi = _calc_aniso(roi)

        return float(max(aniso_center, aniso_roi))

    def _compute_venation_coherence(self, gray_img: np.ndarray, mask: np.ndarray) -> float:
        """
        Menghitung konsistensi orientasi gradien serat daun.
        """
        h, w = gray_img.shape
        scale = 320.0 / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)

        gray_small = cv2.resize(gray_img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        mask_small = cv2.resize(mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)

        gx = cv2.Sobel(gray_small, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray_small, cv2.CV_32F, 0, 1, ksize=3)

        mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)

        valid_pixels = (mask_small > 0) & (mag > 12.0)
        valid_angles = angle[valid_pixels]

        if len(valid_angles) < 200:
            return 0.10

        angles_180 = np.mod(valid_angles, 180.0)
        hist, _ = np.histogram(angles_180, bins=18, range=(0.0, 180.0))
        hist_prob = hist.astype(np.float32) / (float(np.sum(hist)) + 1e-6)

        top_bins = np.sort(hist_prob)[-3:]
        return float(np.sum(top_bins))

    def validate(
        self,
        img_bgr: np.ndarray,
        yolo_has_detections: bool = False,
        max_yolo_conf: float = 0.0,
        yolo_disease_detected: bool = False,
        max_disease_conf: float = 0.0
    ) -> SpeciesValidationResult:
        """
        Menjalankan validasi taksonomi genus Musa terkalibrasi cerdas.
        Evaluasi ketat morfologi foliar: HANYA daun tanaman pisang hidup yang lolos.
        Menolak secara tegas objek non-tanaman (wajah, selfie, hewan, ruangan, benda mati),
        daun pepes olahan matang/bakar, dan daun tanaman hias/dikotil spesies lain.
        """
        if img_bgr is None or img_bgr.size == 0:
            return SpeciesValidationResult(
                is_banana_leaf=False,
                error_code=ErrorCode.INVALID_IMAGE.value,
                detected_category="Citra Tidak Valid",
                banana_confidence=0.0,
                vegetation_ratio=0.0,
                living_chlorophyll_ratio=0.0,
                charred_soot_ratio=0.0,
                gabor_anisotropy=0.0,
                venation_parallelism=0.0,
                reason="Citra kosong atau format berkas tidak didukung.",
                guidance="Harap unggah berkas foto daun berformat JPG, PNG, atau WEBP."
            )

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        b_metrics = self._extract_biomass_metrics(img_bgr)

        green_ratio = b_metrics['green_ratio']
        halo_ratio = b_metrics['halo_ratio']
        veg_ratio = b_metrics['veg_ratio']
        living_foliar_ratio = b_metrics['living_foliar_ratio']
        charred_ratio = b_metrics['charred_ratio']
        leaf_charred_ratio = b_metrics['leaf_charred_ratio']
        dull_leaf_ratio = b_metrics['dull_leaf_ratio']
        skin_ratio = b_metrics['skin_ratio']
        leaf_mask = b_metrics['mask_leaf']
        is_lobed = b_metrics.get('is_lobed_leaf', False)

        gabor_anisotropy = self._compute_gabor_anisotropy(gray, leaf_mask)
        parallelism = self._compute_venation_coherence(gray, leaf_mask)

        # -----------------------------------------------------------------
        # JALUR 1: BUKAN OBJEK TUMBUHAN (living_foliar_ratio < 0.12 ATAU dominasi kulit manusia)
        # Objek manusia, wajah/selfie, ruangan, laptop, meja, pakaian,
        # makanan, barang sehari-hari, lantai, atau benda mati lainnya.
        # -----------------------------------------------------------------
        if living_foliar_ratio < 0.12 or (skin_ratio > 0.20 and living_foliar_ratio < 0.20):
            return SpeciesValidationResult(
                is_banana_leaf=False,
                error_code=ErrorCode.NON_PLANT_OBJECT.value,
                detected_category="Bukan Objek Daun Pisang",
                banana_confidence=round(living_foliar_ratio * 20.0, 1),
                vegetation_ratio=round(veg_ratio * 100, 1),
                living_chlorophyll_ratio=round(living_foliar_ratio * 100, 1),
                charred_soot_ratio=round(charred_ratio * 100, 1),
                gabor_anisotropy=round(gabor_anisotropy, 3),
                venation_parallelism=round(parallelism, 3),
                reason=(
                    f"Rasio klorofil daun hidup pada citra hanya {living_foliar_ratio*100:.1f}% (minimal {self.min_vegetation_ratio*100:.0f}%). "
                    "Citra tidak menampilkan permukaan helai daun tanaman hidup atau terhalang oleh objek non-daun (wajah, manusia, atau ruangan)."
                ),
                guidance="Arahkan kamera secara fokus ke permukaan helai daun pohon pisang hidup dan singkirkan objek selain daun."
            )

        # -----------------------------------------------------------------
        # JALUR 2: DAUN BAKAR / OLAHAN PEPES (Arang gosong pembakaran)
        # Menolak daun pepes olahan matang yang dibakar arang
        # -----------------------------------------------------------------
        if charred_ratio > self.max_charred_soot or (charred_ratio > 0.04 and dull_leaf_ratio > 0.15):
            return SpeciesValidationResult(
                is_banana_leaf=False,
                error_code=ErrorCode.NON_PLANT_OBJECT.value,
                detected_category="Bukan Objek Daun Pisang",
                banana_confidence=10.0,
                vegetation_ratio=round(veg_ratio * 100, 1),
                living_chlorophyll_ratio=round(living_foliar_ratio * 100, 1),
                charred_soot_ratio=round(charred_ratio * 100, 1),
                gabor_anisotropy=round(gabor_anisotropy, 3),
                venation_parallelism=round(parallelism, 3),
                reason="Citra teridentifikasi sebagai daun olahan / terbakar arang (bukan daun tanaman hidup di pohon).",
                guidance="Arahkan kamera ke helai daun pohon pisang hidup di kebun."
            )

        # -----------------------------------------------------------------
        # JALUR 3: DAUN BERLEKUK / MENJARI DIKOTIL (PEPAYA, SINGKONG, JARAK, TANAMAN HIAS)
        # Daun pisang selalu bertulang menyirip sejajar dengan helai utuh (entire margin)
        # -----------------------------------------------------------------
        if is_lobed:
            return SpeciesValidationResult(
                is_banana_leaf=False,
                error_code=ErrorCode.NON_BANANA_LEAF.value,
                detected_category="Daun Tanaman Lain (Bukan Genus Musa)",
                banana_confidence=round(gabor_anisotropy * 50.0, 1),
                vegetation_ratio=round(veg_ratio * 100, 1),
                living_chlorophyll_ratio=round(living_foliar_ratio * 100, 1),
                charred_soot_ratio=round(charred_ratio * 100, 1),
                gabor_anisotropy=round(gabor_anisotropy, 3),
                venation_parallelism=round(parallelism, 3),
                reason=(
                    "Morfologi helai daun memiliki lekukan menjari (palmate/lobed) khas tanaman dikotil. "
                    "Daun pisang (Musa spp.) secara biologis selalu memiliki helai utuh (entire margin) bertulang menyirip sejajar."
                ),
                guidance=(
                    "Sistem MusaVision dikhususkan secara eksklusif untuk tanaman pisang (Musa spp.). "
                    "Pastikan daun yang difoto berasal dari pohon pisang dan bukan daun pepaya, singkong, jarak, atau tanaman hias."
                )
            )

        # -----------------------------------------------------------------
        # JALUR 4: DAUN TANAMAN SPESIES LAIN (NON-BANANA LEAF / SERAT BUKAN MONOKOTIL SEJAJAR)
        # Menolak tanaman hias pot / dikotil yang tidak memiliki pertulangan serat monokotil sejajar
        # -----------------------------------------------------------------
        if gabor_anisotropy < self.min_gabor_anisotropy or parallelism < self.min_parallelism:
            return SpeciesValidationResult(
                is_banana_leaf=False,
                error_code=ErrorCode.NON_BANANA_LEAF.value,
                detected_category="Daun Tanaman Lain (Bukan Genus Musa)",
                banana_confidence=round(gabor_anisotropy * 50.0, 1),
                vegetation_ratio=round(veg_ratio * 100, 1),
                living_chlorophyll_ratio=round(living_foliar_ratio * 100, 1),
                charred_soot_ratio=round(charred_ratio * 100, 1),
                gabor_anisotropy=round(gabor_anisotropy, 3),
                venation_parallelism=round(parallelism, 3),
                reason=(
                    f"Pola pertulangan dan struktur venasi daun (anisotropi: {gabor_anisotropy:.2f}, koherensi: {parallelism:.2f}) "
                    "tidak menunjukkan karakteristik serat menyirip sejajar khas tanaman monokotil genus Musa (pisang). "
                    "Struktur daun teridentifikasi dari spesies tanaman lain (dikotil/tanaman hias non-pisang)."
                ),
                guidance=(
                    "Sistem MusaVision dikhususkan secara eksklusif untuk tanaman pisang (Musa spp.). "
                    "Pastikan daun yang difoto berasal dari pohon pisang dan bukan daun mangga, sirih, pepaya, singkong, atau tanaman hias."
                )
            )

        # -----------------------------------------------------------------
        # JALUR 5: DAUN PISANG HIDUP SEHAT / GENUS MUSA TERVERIFIKASI
        # -----------------------------------------------------------------
        norm_aniso = min(1.0, gabor_anisotropy / 0.95)
        banana_confidence = round(min(98.5, max(75.0, norm_aniso * 98.0)), 1)
        return SpeciesValidationResult(
            is_banana_leaf=True,
            error_code="",
            detected_category="Daun Pisang Hidup (Musa spp.)",
            banana_confidence=banana_confidence,
            vegetation_ratio=round(veg_ratio * 100, 1),
            living_chlorophyll_ratio=round(living_foliar_ratio * 100, 1),
            charred_soot_ratio=round(charred_ratio * 100, 1),
            gabor_anisotropy=round(gabor_anisotropy, 3),
            venation_parallelism=round(parallelism, 3),
            reason=(
                f"Karakteristik venasi sejajar monokotil (anisotropi: {gabor_anisotropy:.2f}) dan proporsi biomassa lamina "
                f"({veg_ratio*100:.1f}%) sesuai dengan spesimen in-vivo genus Musa (pohon pisang)."
            ),
            guidance="Citra valid daun pisang genus Musa. Siap dianalisis oleh model patologi YOLO."
        )

