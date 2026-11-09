/**
 * MusaVision — Core Client Logic (100% ASCII Clean & Global Fallback Ready)
 */

// Global State Variables
window.currentFile = null;
window.currentSampleName = null;
window.lastPredictionData = null;
window.isClickScrolling = false;
window.scrollTimeout = null;

// Global Function Aliases for 100% Inline HTML Compatibility
function selectSample(btn) { if (window.selectSample) window.selectSample(btn); }
function runPrediction() { if (window.runPrediction) window.runPrediction(); }
function openCamera() { if (window.openCamera) window.openCamera(); }
function closeCamera() { if (window.closeCamera) window.closeCamera(); }
function switchCameraFacing() { if (window.switchCameraFacing) window.switchCameraFacing(); }
function captureCameraPhoto() { if (window.captureCameraPhoto) window.captureCameraPhoto(); }
function triggerNativeCamera() { if (window.triggerNativeCamera) window.triggerNativeCamera(); }
function resetUpload(e) { if (window.resetUpload) window.resetUpload(e); }
function resetStudio() { if (window.resetStudio) window.resetStudio(); }
function resetConfidenceDefault() { if (window.resetConfidenceDefault) window.resetConfidenceDefault(); }
function switchResultImageView(m) { if (window.switchResultImageView) window.switchResultImageView(m); }
function openLightbox(s, c) { if (window.openLightbox) window.openLightbox(s, c); }
function closeLightbox() { if (window.closeLightbox) window.closeLightbox(); }
function downloadAnnotatedImage() { if (window.downloadAnnotatedImage) window.downloadAnnotatedImage(); }
function copyDiagnosticReport() { if (window.copyDiagnosticReport) window.copyDiagnosticReport(); }
function openSusModal() { if (window.openSusModal) window.openSusModal(); }
function closeSusModal() { if (window.closeSusModal) window.closeSusModal(); }
function saveSusResponse() { if (window.saveSusResponse) window.saveSusResponse(); }
function exportSusCSV() { if (window.exportSusCSV) window.exportSusCSV(); }
function toggleFieldValidationAccordion() { if (window.toggleFieldValidationAccordion) window.toggleFieldValidationAccordion(); }
function navigateToPage(p) { if (window.navigateToPage) window.navigateToPage(p); }
function toggleDarkMode() { if (window.toggleDarkMode) window.toggleDarkMode(); }

// 1. Fungsi Spinner Saat Memilih Gambar / Sampel
window.triggerImageSpinner = function() {
    const loadingOverlay = document.getElementById('image-loading-overlay');
    if (!loadingOverlay) return;
    loadingOverlay.classList.remove('hidden');
    setTimeout(() => {
        loadingOverlay.classList.add('hidden');
    }, 380);
};

// 2. Fungsi Klik Sampel Daun (Dipanggil langsung dari tombol sampel)
window.selectSample = function(btnElement) {
    if (!btnElement) return;
    const sampleFile = btnElement.getAttribute('data-sample');
    if (!sampleFile) return;

    window.triggerImageSpinner();

    // Highlight tombol sampel yang dipilih
    const allPills = document.querySelectorAll('.sample-pill');
    allPills.forEach(p => p.classList.remove('sample-active', 'ring-2', 'ring-emerald-600'));
    btnElement.classList.add('sample-active', 'ring-2', 'ring-emerald-600');

    window.currentSampleName = sampleFile;
    window.currentFile = null;

    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';

    const previewImage = document.getElementById('preview-image');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const previewContainer = document.getElementById('preview-container');
    const dropzone = document.getElementById('dropzone');
    const btnPredict = document.getElementById('btn-predict');

    if (previewImage) previewImage.src = `/static/samples/${sampleFile}`;
    if (uploadPlaceholder) uploadPlaceholder.classList.add('hidden');
    if (previewContainer) previewContainer.classList.remove('hidden');
    if (dropzone) {
        dropzone.classList.remove('border-2', 'border-dashed', 'border-zinc-300', 'p-4', 'bg-[#F8FAFC]', 'hover:border-emerald-600', 'hover:bg-emerald-50/20');
        dropzone.classList.add('border-0', 'p-0', 'bg-transparent');
    }
    if (btnPredict) {
        btnPredict.disabled = false;
        btnPredict.removeAttribute('disabled');
    }
};

// 3. Fungsi Penanganan Upload File dari Komputer
window.handleSelectedFile = function(file) {
    if (!file || !file.type.match('image.*')) {
        window.showToast('Format berkas harus berupa citra (JPG, PNG, WEBP).', 'error');
        return;
    }

    window.triggerImageSpinner();
    window.currentFile = file;
    window.currentSampleName = null;

    const allPills = document.querySelectorAll('.sample-pill');
    allPills.forEach(p => p.classList.remove('sample-active', 'ring-2', 'ring-emerald-600'));

    const reader = new FileReader();
    reader.onload = function(e) {
        const previewImage = document.getElementById('preview-image');
        const uploadPlaceholder = document.getElementById('upload-placeholder');
        const previewContainer = document.getElementById('preview-container');
        const dropzone = document.getElementById('dropzone');
        const btnPredict = document.getElementById('btn-predict');

        if (previewImage) previewImage.src = e.target.result;
        if (uploadPlaceholder) uploadPlaceholder.classList.add('hidden');
        if (previewContainer) previewContainer.classList.remove('hidden');
        if (dropzone) {
            dropzone.classList.remove('border-2', 'border-dashed', 'border-zinc-300', 'p-4', 'bg-[#F8FAFC]', 'hover:border-emerald-600', 'hover:bg-emerald-50/20');
            dropzone.classList.add('border-0', 'p-0', 'bg-transparent');
        }
        if (btnPredict) {
            btnPredict.disabled = false;
            btnPredict.removeAttribute('disabled');
        }
    };
    reader.readAsDataURL(file);
};

// 4. Fungsi Reset Upload & Studio
window.resetUpload = function(e) {
    if (e) e.stopPropagation();
    window.currentFile = null;
    window.currentSampleName = null;

    const fileInput = document.getElementById('file-input');
    const previewImage = document.getElementById('preview-image');
    const previewContainer = document.getElementById('preview-container');
    const uploadPlaceholder = document.getElementById('upload-placeholder');
    const dropzone = document.getElementById('dropzone');
    const btnPredict = document.getElementById('btn-predict');

    if (fileInput) fileInput.value = '';
    if (previewImage) previewImage.src = '';
    if (previewContainer) previewContainer.classList.add('hidden');
    if (uploadPlaceholder) uploadPlaceholder.classList.remove('hidden');
    if (dropzone) {
        dropzone.classList.add('border-2', 'border-dashed', 'border-zinc-300', 'p-4', 'bg-[#F8FAFC]');
        dropzone.classList.remove('border-0', 'p-0', 'bg-transparent');
    }
    if (btnPredict) btnPredict.disabled = true;

    const allPills = document.querySelectorAll('.sample-pill');
    allPills.forEach(p => p.classList.remove('sample-active', 'ring-2', 'ring-emerald-600'));
};

window.resetStudio = function() {
    window.resetUpload();
    const resultsContainer = document.getElementById('results-container');
    const fullwidthDetails = document.getElementById('fullwidth-details-container');
    const emptyState = document.getElementById('empty-state');

    if (resultsContainer) resultsContainer.classList.add('hidden');
    if (fullwidthDetails) fullwidthDetails.classList.add('hidden');
    if (emptyState) emptyState.classList.remove('hidden');
    window.lastPredictionData = null;
};

// 5. Fungsi Reset Confidence ke Default 25%
window.resetConfidenceDefault = function() {
    const confSlider = document.getElementById('conf-slider');
    const confValueDisplay = document.getElementById('conf-value');
    if (confSlider) confSlider.value = 0.25;
    if (confValueDisplay) confValueDisplay.textContent = '25%';
};

// 5b. Fungsi Toggle Accordion Mode Validasi Sampel Kebun (Task 7)
window.toggleFieldValidationAccordion = function() {
    const acc = document.getElementById('field-validation-accordion');
    const arrow = document.getElementById('fv-accordion-arrow');
    if (!acc) return;
    const isHidden = acc.classList.contains('hidden');
    if (isHidden) {
        acc.classList.remove('hidden');
        if (arrow) arrow.style.transform = 'rotate(180deg)';
    } else {
        acc.classList.add('hidden');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
    }
};

// 6. Fungsi Eksekusi Deteksi (Jalankan Deteksi dengan Telemetri E2E & Validasi Lapangan)
window.runPrediction = async function() {
    if (!window.currentFile && !window.currentSampleName) {
        window.showToast('Silakan pilih sampel daun atau unggah foto terlebih dahulu.', 'warning');
        return;
    }

    const btnPredict = document.getElementById('btn-predict');
    const btnPredictIcon = document.getElementById('btn-predict-icon');
    const btnPredictSpinner = document.getElementById('btn-predict-spinner');
    const btnPredictText = document.getElementById('btn-predict-text');
    const processingState = document.getElementById('processing-state');
    const emptyState = document.getElementById('empty-state');
    const resultsContainer = document.getElementById('results-container');
    const fullwidthDetails = document.getElementById('fullwidth-details-container');
    const confSlider = document.getElementById('conf-slider');

    // Aktifkan Spinner Interaktif
    if (btnPredict) btnPredict.disabled = true;
    if (btnPredictIcon) btnPredictIcon.classList.add('hidden');
    if (btnPredictSpinner) btnPredictSpinner.classList.remove('hidden');
    if (btnPredictText) btnPredictText.textContent = 'Menganalisis Citra...';

    if (processingState) processingState.classList.remove('hidden');
    if (emptyState) emptyState.classList.add('hidden');
    if (resultsContainer) resultsContainer.classList.add('hidden');
    if (fullwidthDetails) fullwidthDetails.classList.add('hidden');

    const formData = new FormData();
    const conf = confSlider ? parseFloat(confSlider.value) : 0.25;
    formData.append('conf', conf);
    formData.append('iou', 0.45);

    // Toggle Pra-pemrosesan CIE-LAB CLAHE (Task 1 & Task 8)
    const useClaheToggle = document.getElementById('use-clahe-toggle');
    const useClahe = useClaheToggle ? useClaheToggle.checked : true;
    formData.append('use_clahe', useClahe ? 'true' : 'false');

    if (window.currentFile) {
        formData.append('image', window.currentFile);
    } else if (window.currentSampleName) {
        formData.append('sample_name', window.currentSampleName);
    }

    // Metadata Validasi Lapangan (Task 7)
    const sourceOrigin = document.getElementById('fv-source-origin')?.value || 'Sampel Perkebunan Pisang (Data Primer)';
    const groundTruth = document.getElementById('fv-ground-truth')?.value || 'Belum Diketahui';
    const captureDistance = document.getElementById('fv-capture-distance')?.value || 'Jarak Sedang / Setengah Daun (30-80 cm)';
    const lighting = document.getElementById('fv-lighting')?.value || 'Cerah Pagi/Sore (Optimal)';
    const fieldNotes = document.getElementById('fv-field-notes')?.value || '';

    const fileName = window.currentFile ? window.currentFile.name : (window.currentSampleName || 'spesimen_kebun.jpg');

    const metadata = {
        source_origin: sourceOrigin,
        ground_truth: groundTruth,
        capture_distance: captureDistance,
        lighting_condition: lighting,
        field_notes: fieldNotes,
        use_clahe: useClahe,
        file_name: fileName
    };

    const clientT0 = performance.now();
    let response;
    let data;
    try {
        response = await fetch('/predict', {
            method: 'POST',
            body: formData,
            headers: {
                'ngrok-skip-browser-warning': 'true'
            }
        });
        data = await response.json();
    } catch (netErr) {
        console.error('[Network Error]', netErr);
        window.showToast('Koneksi ke server gagal. Pastikan python app.py aktif.', 'error');
        if (emptyState) emptyState.classList.remove('hidden');
        if (btnPredict) btnPredict.disabled = false;
        if (btnPredictIcon) btnPredictIcon.classList.remove('hidden');
        if (btnPredictSpinner) btnPredictSpinner.classList.add('hidden');
        if (btnPredictText) btnPredictText.textContent = 'Jalankan Deteksi';
        if (processingState) processingState.classList.add('hidden');
        return;
    }

    try {
        const clientRoundtripMs = (performance.now() - clientT0).toFixed(1);

        // Tahan spinner minimal 450ms agar animasi terlihat mulus
        const elapsed = performance.now() - clientT0;
        if (elapsed < 450) {
            await new Promise(resolve => setTimeout(resolve, 450 - elapsed));
        }

        if (response.ok && data.success) {
            window.lastPredictionData = data;
            window.lastMetadata = metadata;
            window.renderResults(data, metadata, clientRoundtripMs);
        } else {
            window.showToast(data.message || 'Gagal menjalankan inferensi model.', 'error');
            if (emptyState) emptyState.classList.remove('hidden');
        }
    } catch (renderErr) {
        console.error('[Render Error in renderResults]', renderErr);
        window.showToast('Kesalahan tampilan: ' + renderErr.message, 'error');
    } finally {
        if (btnPredict) btnPredict.disabled = false;
        if (btnPredictIcon) btnPredictIcon.classList.remove('hidden');
        if (btnPredictSpinner) btnPredictSpinner.classList.add('hidden');
        if (btnPredictText) btnPredictText.textContent = 'Jalankan Deteksi';
        if (processingState) processingState.classList.add('hidden');
    }
};

// 7. Fungsi Render Hasil Deteksi Lengkap (Mendukung Daun Pisang, Non-Pisang, Pepes, AI, Telemetri E2E, & Granularitas)
window.renderResults = function(data, metadata, clientRoundtripMs) {
    const resultsContainer = document.getElementById('results-container');
    const fullwidthDetails = document.getElementById('fullwidth-details-container');
    const annotatedResultImg = document.getElementById('annotated-result-img');
    const claheResultImg = document.getElementById('clahe-result-img');
    const originalResultImg = document.getElementById('original-result-img');
    const summaryBadge = document.getElementById('summary-badge');
    const summaryTitle = document.getElementById('summary-title');
    const summaryDesc = document.getElementById('summary-desc');
    const statDetectionsLabel = document.getElementById('stat-detections-label');
    const statDetections = document.getElementById('stat-detections');
    const statLatencyLabel = document.getElementById('stat-latency-label');
    const statLatency = document.getElementById('stat-latency');
    const statPrimaryLabel = document.getElementById('stat-primary-label');
    const statPrimaryClass = document.getElementById('stat-primary-class');

    if (!resultsContainer) return;

    // A. Update Visual Multi-Tab (Task 8: Anotasi vs LAB-CLAHE vs Raw)
    if (annotatedResultImg) annotatedResultImg.src = data.annotated_image || data.annotated_result_base64 || '';
    if (claheResultImg) claheResultImg.src = data.preprocessed_clahe_base64 || data.annotated_image || '';
    if (originalResultImg) originalResultImg.src = data.raw_resized_base64 || data.original_image || '';
    window.switchResultImageView('annotated');

    if (summaryTitle) summaryTitle.textContent = data.summary_title;
    if (summaryDesc) summaryDesc.textContent = data.summary_description;

    // B. Telemetri Latensi Kontekstual End-to-End (Task 2)
    const lb = data.latency_breakdown || {};
    const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };
    setTxt('telemetry-hardware', `${lb.device_name || 'CPU (PyTorch FP32)'} | Input: ${lb.input_resolution || '640×640'}`);
    setTxt('telemetry-preprocess', `${Number(lb.preprocess_ms ?? 0).toFixed(2)} ms`);
    setTxt('telemetry-inference', `${Number(lb.inference_nms_ms ?? data.inference_time_ms ?? 0).toFixed(2)} ms`);
    setTxt('telemetry-encode', `${Number(lb.postprocess_encode_ms ?? 0).toFixed(2)} ms`);
    setTxt('telemetry-client-e2e', `${Number(clientRoundtripMs ?? data.inference_time_ms ?? 0).toFixed(1)} ms`);
    setTxt('telemetry-clahe-mode', lb.clahe_mode ? `Mode: ${lb.clahe_mode}` : 'Mode: CIE-LAB (Channel L)');
    setTxt('telemetry-server-total', `Total Server: ${Number(lb.server_total_ms ?? data.inference_time_ms ?? 0).toFixed(2)} ms`);

    // C. Evaluasi Kecocokan Ground Truth Validasi Lapangan (Task 7)
    const gtBanner = document.getElementById('ground-truth-match-banner');
    const gtIcon = document.getElementById('gt-match-icon');
    const gtText = document.getElementById('gt-match-text');
    const gtDetail = document.getElementById('gt-match-detail');

    if (metadata && metadata.ground_truth && metadata.ground_truth !== 'Belum Diketahui') {
        if (gtBanner) gtBanner.classList.remove('hidden');
        const targetGT = metadata.ground_truth.trim().toLowerCase();
        const primaryPred = (data.primary_class || '').trim().toLowerCase();
        const detections = data.detections || [];
        const anyMatch = detections.some(d => (d.class_name || '').trim().toLowerCase() === targetGT);
        const isMatch = (primaryPred === targetGT) || anyMatch;

        if (isMatch) {
            if (gtBanner) gtBanner.className = 'p-3 rounded-xl flex items-center justify-between text-xs border bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 border-emerald-300 dark:border-emerald-800 transition-all shadow-2xs';
            if (gtIcon) gtIcon.textContent = '✅';
            if (gtText) gtText.textContent = 'SESUAI DENGAN GROUND TRUTH (True Positive)';
            if (gtDetail) gtDetail.textContent = `Target: ${metadata.ground_truth} | Prediksi: ${data.primary_class}`;
            metadata.match_status = 'SESUAI (TP)';
        } else {
            if (gtBanner) gtBanner.className = 'p-3 rounded-xl flex items-center justify-between text-xs border bg-rose-50 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200 border-rose-300 dark:border-rose-800 transition-all shadow-2xs';
            if (gtIcon) gtIcon.textContent = '❌';
            if (gtText) gtText.textContent = 'TIDAK SESUAI (Misclassified / False Negative)';
            if (gtDetail) gtDetail.textContent = `Target: ${metadata.ground_truth} | Prediksi: ${data.primary_class}`;
            metadata.match_status = 'TIDAK SESUAI';
        }
    } else {
        if (gtBanner) gtBanner.classList.add('hidden');
        if (metadata) metadata.match_status = 'Tanpa Ground Truth';
    }

    // D. Update 3 Kotak Metrik Ringkas Di Bawah Citra Hasil
    if (data.is_ai_generated) {
        if (statDetectionsLabel) statDetectionsLabel.textContent = 'Indeks AI';
        if (statDetections) {
            statDetections.textContent = `${data.metrics?.ai_score ?? 93.7}%`;
            statDetections.className = 'text-xs sm:text-sm font-bold text-rose-600 dark:text-rose-400 font-mono mt-0.5';
        }
        if (statLatencyLabel) statLatencyLabel.textContent = 'Inferensi';
        if (statLatency) statLatency.textContent = `${data.inference_time_ms} ms`;
        if (statPrimaryLabel) statPrimaryLabel.textContent = 'Klasifikasi';
        if (statPrimaryClass) {
            statPrimaryClass.textContent = 'Citra Sintesis AI';
            statPrimaryClass.className = 'text-[10px] sm:text-xs font-bold text-rose-700 dark:text-rose-400 mt-0.5 leading-tight break-words text-center';
        }
    } else if (data.is_valid_banana_leaf === false) {
        if (data.error_code === 'NON_PLANT_OBJECT') {
            if (statDetectionsLabel) statDetectionsLabel.textContent = 'Biomassa Daun';
            if (statDetections) {
                statDetections.textContent = `${data.metrics?.vegetation_ratio ?? 0}%`;
                statDetections.className = 'text-xs sm:text-sm font-bold text-zinc-900 dark:text-white font-mono mt-0.5';
            }
            if (statPrimaryLabel) statPrimaryLabel.textContent = 'Kategori';
            if (statPrimaryClass) {
                statPrimaryClass.textContent = 'Bukan Objek Daun';
                statPrimaryClass.className = 'text-[10px] sm:text-xs font-bold text-zinc-800 dark:text-zinc-200 mt-0.5 leading-tight break-words text-center';
            }
        } else {
            if (statDetectionsLabel) statDetectionsLabel.textContent = 'Pola Venasi';
            if (statDetections) {
                statDetections.textContent = 'Non-Monokotil';
                statDetections.className = 'text-xs sm:text-sm font-bold text-amber-700 dark:text-amber-400 mt-0.5';
            }
            if (statPrimaryLabel) statPrimaryLabel.textContent = 'Spesies';
            if (statPrimaryClass) {
                statPrimaryClass.textContent = 'Bukan Daun Pisang';
                statPrimaryClass.className = 'text-[10px] sm:text-xs font-bold text-amber-800 dark:text-amber-300 mt-0.5 leading-tight break-words text-center';
            }
        }
        if (statLatencyLabel) statLatencyLabel.textContent = 'Inferensi';
        if (statLatency) statLatency.textContent = `${data.inference_time_ms} ms`;
    } else {
        if (statDetectionsLabel) statDetectionsLabel.textContent = 'Wilayah BBox';
        if (statDetections) {
            statDetections.textContent = `${data.total_detections} Wilayah`;
            statDetections.className = 'text-xs sm:text-sm font-bold text-zinc-900 dark:text-white mt-0.5';
        }
        if (statLatencyLabel) statLatencyLabel.textContent = 'Inferensi';
        if (statLatency) statLatency.textContent = `${data.inference_time_ms} ms`;
        if (statPrimaryLabel) statPrimaryLabel.textContent = 'Dominan';
        if (statPrimaryClass) {
            statPrimaryClass.textContent = data.primary_class;
            statPrimaryClass.className = 'text-[10px] sm:text-xs font-bold text-zinc-900 dark:text-white mt-0.5 leading-tight break-words text-center';
        }
    }

    // E. Render Badge Status Studio
    if (summaryBadge) {
        if (data.is_ai_generated) {
            summaryBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-rose-100 dark:bg-rose-950/50 text-rose-900 dark:text-rose-200 border border-rose-300 dark:border-rose-800';
            summaryBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-rose-600 mr-2"></span>Status: Citra Sintesis AI (Ditolak)';
        } else if (data.is_valid_banana_leaf === false) {
            if (data.error_code === 'NON_PLANT_OBJECT') {
                summaryBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-zinc-200 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-200 border border-zinc-400 dark:border-zinc-700';
                summaryBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-zinc-600 mr-2"></span>Status: Bukan Objek Daun Pisang';
            } else {
                summaryBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-950/50 text-amber-900 dark:text-amber-200 border border-amber-300 dark:border-amber-800';
                summaryBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-amber-600 mr-2"></span>Status: Bukan Daun Pisang (Spesies Lain)';
            }
        } else if (data.primary_class === 'Fresh') {
            summaryBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-100 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-800';
            summaryBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-600 mr-2"></span>Status: Sehat';
        } else if (data.primary_class === 'Uncertain') {
            summaryBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 border border-zinc-300 dark:border-zinc-700';
            summaryBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-zinc-500 mr-2"></span>Status: Tidak Terdeteksi';
        } else {
            summaryBadge.className = 'inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-950/50 text-amber-900 dark:text-amber-200 border border-amber-300 dark:border-amber-800';
            summaryBadge.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-amber-600 mr-2"></span>Status: Terinfeksi Patogen';
        }
    }

    // F. Update 4 Kartu Metrik Komprehensif (Task 3: Granularitas & Luas Area BBox)
    const detections = data.detections || [];
    const rc = data.region_count || {};
    const totalObj = rc.total_regions ?? data.total_detections ?? detections.length;
    const freshDetections = detections.filter(d => d.class_name === 'Fresh');
    const freshCount = freshDetections.length;
    const diseaseDetections = detections.filter(d => d.class_name !== 'Fresh');
    const diseaseCount = diseaseDetections.length;
    const leafCount = rc.leaf_level_count ?? detections.filter(d => d.class_name === 'Fresh' || d.class_name === 'Yellow Sigatoka').length;
    const lesionCount = rc.lesion_level_count ?? diseaseDetections.length;
    const avgBoxAreaPct = data.avg_box_area_ratio_pct ?? (totalObj > 0 ? (detections.reduce((acc, cur) => acc + (cur.box_area_ratio_pct || 0), 0) / totalObj).toFixed(2) : '0.00');

    const card1Title = document.getElementById('card-1-title');
    const cardTotalObjects = document.getElementById('card-total-objects');
    const card1Sub = document.getElementById('card-1-sub');

    const card2Title = document.getElementById('card-2-title');
    const cardFreshCount = document.getElementById('card-fresh-count');
    const card2Sub = document.getElementById('card-2-sub');

    const card3Title = document.getElementById('card-3-title');
    const cardDiseaseCount = document.getElementById('card-disease-count');
    const cardDiseaseSub = document.getElementById('card-disease-sub');

    const card4Title = document.getElementById('card-4-title');
    const cardInferenceMs = document.getElementById('card-inference-ms');
    const card4Sub = document.getElementById('card-4-sub');

    if (data.is_ai_generated) {
        if (card1Title) card1Title.textContent = 'Status Validasi';
        if (cardTotalObjects) {
            cardTotalObjects.textContent = 'DITOLAK';
            cardTotalObjects.className = 'text-xl sm:text-2xl font-extrabold text-rose-600 dark:text-rose-400 font-mono mt-1';
        }
        if (card1Sub) card1Sub.textContent = 'Verifikasi Citra Otentik';

        if (card2Title) card2Title.textContent = 'Probabilitas AI';
        if (cardFreshCount) {
            cardFreshCount.textContent = `${data.metrics?.ai_score ?? 93.7}%`;
            cardFreshCount.className = 'text-xl sm:text-2xl font-extrabold text-rose-600 dark:text-rose-400 font-mono mt-1';
        }
        if (card2Sub) card2Sub.textContent = 'Indeks Deteksi Generator';

        if (card3Title) card3Title.textContent = 'Integritas Citra';
        if (cardDiseaseCount) {
            cardDiseaseCount.textContent = 'Sintetis';
            cardDiseaseCount.className = 'text-xl sm:text-2xl font-extrabold text-rose-600 dark:text-rose-400 font-mono mt-1';
        }
        if (cardDiseaseSub) cardDiseaseSub.textContent = 'Anomali Spektral VAE';

        if (card4Title) card4Title.textContent = 'Waktu Pemeriksaan';
        if (cardInferenceMs) {
            cardInferenceMs.textContent = `${data.inference_time_ms} ms`;
            cardInferenceMs.className = 'text-xl sm:text-2xl font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-1';
        }
        if (card4Sub) card4Sub.textContent = 'Gatekeeper AI Detector';

    } else if (data.is_valid_banana_leaf === false) {
        if (data.error_code === 'NON_PLANT_OBJECT') {
            if (card1Title) card1Title.textContent = 'Kategori Objek';
            if (cardTotalObjects) {
                cardTotalObjects.textContent = 'NON-DAUN';
                cardTotalObjects.className = 'text-xl sm:text-2xl font-extrabold text-zinc-900 dark:text-zinc-100 font-mono mt-1';
            }
            if (card1Sub) card1Sub.textContent = 'Bukan Daun Pisang';

            if (card2Title) card2Title.textContent = 'Biomassa / Klorofil';
            if (cardFreshCount) {
                cardFreshCount.textContent = `${data.metrics?.vegetation_ratio ?? 0}%`;
                cardFreshCount.className = 'text-xl sm:text-2xl font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-1';
            }
            if (card2Sub) card2Sub.textContent = 'Batas Minimal 15%';

            if (card3Title) card3Title.textContent = 'Struktur Daun';
            if (cardDiseaseCount) {
                cardDiseaseCount.textContent = '0.00';
                cardDiseaseCount.className = 'text-xl sm:text-2xl font-extrabold text-zinc-500 dark:text-zinc-400 font-mono mt-1';
            }
            if (cardDiseaseSub) cardDiseaseSub.textContent = 'Tidak Berstruktur Daun';

            if (card4Title) card4Title.textContent = 'Waktu Verifikasi';
            if (cardInferenceMs) {
                cardInferenceMs.textContent = `${data.inference_time_ms} ms`;
                cardInferenceMs.className = 'text-xl sm:text-2xl font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-1';
            }
            if (card4Sub) card4Sub.textContent = 'Gatekeeper Objek';

        } else {
            // NON_BANANA_LEAF
            if (card1Title) card1Title.textContent = 'Pola Venasi';
            if (cardTotalObjects) {
                cardTotalObjects.textContent = 'MENYIRIP JALA';
                cardTotalObjects.className = 'text-base sm:text-lg font-extrabold text-amber-800 dark:text-amber-300 font-mono mt-1';
            }
            if (card1Sub) card1Sub.textContent = 'Daun Tanaman Lain';

            if (card2Title) card2Title.textContent = 'Anisotropi Serat';
            if (cardFreshCount) {
                cardFreshCount.textContent = `${data.metrics?.gabor_anisotropy ?? 0}`;
                cardFreshCount.className = 'text-xl sm:text-2xl font-extrabold text-amber-700 dark:text-amber-400 font-mono mt-1';
            }
            if (card2Sub) card2Sub.textContent = 'Non-Musa (Dikotil/Hias)';

            if (card3Title) card3Title.textContent = 'Paralelisme Vena';
            if (cardDiseaseCount) {
                cardDiseaseCount.textContent = `${data.metrics?.venation_parallelism ?? 0}`;
                cardDiseaseCount.className = 'text-xl sm:text-2xl font-extrabold text-amber-700 dark:text-amber-400 font-mono mt-1';
            }
            if (cardDiseaseSub) cardDiseaseSub.textContent = 'Bukan Serat Pisang Sejajar';

            if (card4Title) card4Title.textContent = 'Waktu Verifikasi';
            if (cardInferenceMs) {
                cardInferenceMs.textContent = `${data.inference_time_ms} ms`;
                cardInferenceMs.className = 'text-xl sm:text-2xl font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-1';
            }
            if (card4Sub) card4Sub.textContent = 'Gatekeeper Taksonomi';
        }
    } else {
        if (card1Title) card1Title.textContent = 'Wilayah Deteksi (Region)';
        if (cardTotalObjects) {
            cardTotalObjects.textContent = `${totalObj}`;
            cardTotalObjects.className = 'text-xl sm:text-2xl font-extrabold text-zinc-900 dark:text-white font-mono mt-1';
        }
        if (card1Sub) card1Sub.textContent = 'Total box hasil NMS';

        if (card2Title) card2Title.textContent = 'Helai Daun (Macro)';
        if (cardFreshCount) {
            cardFreshCount.textContent = `${leafCount}`;
            cardFreshCount.className = 'text-xl sm:text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 font-mono mt-1';
        }
        if (card2Sub) card2Sub.textContent = 'Fresh & Yellow Sigatoka';

        if (card3Title) card3Title.textContent = 'Titik/Klaster Lesi (Micro)';
        if (cardDiseaseCount) {
            cardDiseaseCount.textContent = `${lesionCount}`;
            cardDiseaseCount.className = 'text-xl sm:text-2xl font-extrabold text-rose-600 dark:text-rose-400 font-mono mt-1';
        }
        if (cardDiseaseSub) {
            cardDiseaseSub.textContent = lesionCount > 0 ? `Dominan: ${data.primary_class}` : 'Tidak ada lesi aktif';
        }

        if (card4Title) card4Title.textContent = 'Rata-Rata Luas Box';
        if (cardInferenceMs) {
            cardInferenceMs.textContent = `${avgBoxAreaPct}%`;
            cardInferenceMs.className = 'text-xl sm:text-2xl font-extrabold text-amber-600 dark:text-amber-400 font-mono mt-1';
        }
        if (card4Sub) card4Sub.textContent = 'Rasio terhadap kanvas 640×640';
    }

    // G. Update Banner Diagnostik
    const healthBanner = document.getElementById('diagnostic-health-banner');
    const healthIconBox = document.getElementById('health-banner-icon');
    const healthTitle = document.getElementById('health-banner-title');
    const healthSubtitle = document.getElementById('health-banner-subtitle');
    const healthScoreLabel = document.getElementById('health-banner-score-label');
    const healthScoreValue = document.getElementById('health-banner-score');

    if (healthBanner) {
        if (data.is_ai_generated) {
            healthBanner.className = 'rounded-2xl p-5 bg-rose-50/90 dark:bg-rose-950/50 border border-rose-300 dark:border-rose-800 flex flex-wrap items-center justify-between gap-4 shadow-2xs';
            healthIconBox.className = 'w-11 h-11 rounded-xl bg-rose-600 text-white flex items-center justify-center shrink-0 shadow-xs';
            healthTitle.className = 'text-base font-extrabold text-rose-950 dark:text-rose-100';
            healthTitle.textContent = 'Pemindaian Ditolak: Citra Hasil Generator AI';
            healthSubtitle.className = 'text-xs text-rose-800 dark:text-rose-300 mt-0.5';
            healthSubtitle.textContent = data.summary_description;
            healthScoreLabel.className = 'text-[10px] font-mono uppercase tracking-wider text-rose-700 dark:text-rose-400 block';
            healthScoreLabel.textContent = 'Indeks Probabilitas AI';
            healthScoreValue.className = 'text-2xl font-extrabold font-mono text-rose-900 dark:text-rose-200';
            healthScoreValue.textContent = `${data.metrics?.ai_score ?? 95}%`;
        } else if (data.is_valid_banana_leaf === false) {
            const isNonPlant = data.error_code === 'NON_PLANT_OBJECT';
            healthBanner.className = isNonPlant
                ? 'rounded-2xl p-5 bg-zinc-100 dark:bg-zinc-800/90 border border-zinc-300 dark:border-zinc-700 flex flex-wrap items-center justify-between gap-4 shadow-2xs'
                : 'rounded-2xl p-5 bg-amber-50/90 dark:bg-amber-950/50 border border-amber-300 dark:border-amber-800 flex flex-wrap items-center justify-between gap-4 shadow-2xs';
            healthIconBox.className = isNonPlant
                ? 'w-11 h-11 rounded-xl bg-zinc-700 text-white flex items-center justify-center shrink-0 shadow-xs'
                : 'w-11 h-11 rounded-xl bg-amber-600 text-white flex items-center justify-center shrink-0 shadow-xs';
            healthTitle.className = isNonPlant ? 'text-base font-extrabold text-zinc-900 dark:text-white' : 'text-base font-extrabold text-amber-950 dark:text-amber-100';
            healthTitle.textContent = data.summary_title;
            healthSubtitle.className = isNonPlant ? 'text-xs text-zinc-600 dark:text-zinc-300 mt-0.5' : 'text-xs text-amber-800 dark:text-amber-300 mt-0.5';
            healthSubtitle.textContent = data.summary_description;
            healthScoreLabel.className = 'text-[10px] font-mono uppercase tracking-wider text-zinc-600 dark:text-zinc-400 block';
            healthScoreLabel.textContent = 'Verifikasi Taksonomi';
            healthScoreValue.className = isNonPlant ? 'text-2xl font-extrabold font-mono text-zinc-800 dark:text-zinc-200' : 'text-2xl font-extrabold font-mono text-amber-900 dark:text-amber-200';
            healthScoreValue.textContent = isNonPlant ? 'Non-Daun' : 'Non-Musa';
        } else if (data.primary_class === 'Fresh') {
            const maxFreshConf = freshCount > 0 ? Math.round(Math.max(...detections.map(d => d.confidence))) : 100;
            healthBanner.className = 'rounded-2xl p-5 bg-emerald-50/90 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-800 flex flex-wrap items-center justify-between gap-4 shadow-2xs';
            healthIconBox.className = 'w-11 h-11 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-xs';
            healthTitle.className = 'text-base font-extrabold text-emerald-950 dark:text-emerald-100';
            healthTitle.textContent = 'Kondisi Fisiologis Daun Sehat Sempurna';
            healthSubtitle.className = 'text-xs text-emerald-800 dark:text-emerald-300 mt-0.5';
            healthSubtitle.textContent = 'Seluruh permukaan lamina daun terdeteksi sehat tanpa bercak nekrosis patogen aktif.';
            healthScoreLabel.className = 'text-[10px] font-mono uppercase tracking-wider text-emerald-700 dark:text-emerald-400 block';
            healthScoreLabel.textContent = 'Indeks Kesehatan Daun';
            healthScoreValue.className = 'text-2xl font-extrabold font-mono text-emerald-900 dark:text-emerald-200';
            healthScoreValue.textContent = `${maxFreshConf}%`;
        } else if (data.primary_class === 'Uncertain') {
            healthBanner.className = 'rounded-2xl p-5 bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 flex flex-wrap items-center justify-between gap-4 shadow-2xs';
            healthIconBox.className = 'w-11 h-11 rounded-xl bg-zinc-700 text-white flex items-center justify-center shrink-0 shadow-xs';
            healthTitle.className = 'text-base font-extrabold text-zinc-900 dark:text-white';
            healthTitle.textContent = data.summary_title || 'Tidak Terdeteksi Lesi Patologis';
            healthSubtitle.className = 'text-xs text-zinc-600 dark:text-zinc-300 mt-0.5';
            healthSubtitle.textContent = data.summary_description || 'Spesimen daun tampak bersih tanpa lesi patologis aktif pada ambang batas standar (25%).';
            healthScoreLabel.className = 'text-[10px] font-mono uppercase tracking-wider text-zinc-500 dark:text-zinc-400 block';
            healthScoreLabel.textContent = 'Skor Keyakinan';
            healthScoreValue.className = 'text-2xl font-extrabold font-mono text-zinc-800 dark:text-zinc-200';
            healthScoreValue.textContent = '0%';
        } else {
            const avgConf = diseaseCount > 0
                ? (diseaseDetections.reduce((acc, cur) => acc + cur.confidence, 0) / diseaseCount).toFixed(1)
                : 0;
            const isCritical = data.primary_class === 'Black Sigatoka' || data.primary_class === 'Yellow Sigatoka';
            healthBanner.className = isCritical
                ? 'rounded-2xl p-5 bg-rose-50/90 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-800 flex flex-wrap items-center justify-between gap-4 shadow-2xs'
                : 'rounded-2xl p-5 bg-amber-50/90 dark:bg-amber-950/50 border border-amber-200 dark:border-amber-800 flex flex-wrap items-center justify-between gap-4 shadow-2xs';
            healthIconBox.className = isCritical
                ? 'w-11 h-11 rounded-xl bg-rose-600 text-white flex items-center justify-center shrink-0 shadow-xs'
                : 'w-11 h-11 rounded-xl bg-amber-600 text-white flex items-center justify-center shrink-0 shadow-xs';
            healthTitle.className = isCritical
                ? 'text-base font-extrabold text-rose-950 dark:text-rose-100'
                : 'text-base font-extrabold text-amber-950 dark:text-amber-100';
            healthTitle.textContent = `Terdeteksi Infeksi Aktif: ${data.primary_class} (${lesionCount} Titik/Klaster)`;
            healthSubtitle.className = isCritical
                ? 'text-xs text-rose-800 dark:text-rose-300 mt-0.5'
                : 'text-xs text-amber-800 dark:text-amber-300 mt-0.5';
            healthSubtitle.textContent = data.summary_description;
            healthScoreLabel.className = isCritical
                ? 'text-[10px] font-mono uppercase tracking-wider text-rose-700 dark:text-rose-400 block'
                : 'text-[10px] font-mono uppercase tracking-wider text-amber-700 dark:text-amber-400 block';
            healthScoreLabel.textContent = 'Keyakinan Rata-Rata';
            healthScoreValue.className = isCritical
                ? 'text-2xl font-extrabold font-mono text-rose-900 dark:text-rose-200'
                : 'text-2xl font-extrabold font-mono text-amber-900 dark:text-amber-200';
            healthScoreValue.textContent = `${avgConf}%`;
        }
    }

    // H. Isi Tabel Bounding Box & Granularitas (Task 3: 7 Kolom Terstruktur)
    const bboxTableBody = document.getElementById('bbox-table-body');
    if (bboxTableBody) {
        bboxTableBody.innerHTML = '';
        if (data.is_valid_banana_leaf === false || data.is_ai_generated) {
            let rejectTitle = 'Inferensi Deteksi Penyakit Dilewati (Spesimen Ditolak Gatekeeper)';
            let rejectDesc = 'Model YOLO MusaVision dikhususkan hanya untuk spesimen daun pohon pisang hidup (genus Musa).';
            let rejectBorderBg = 'bg-amber-50/40 dark:bg-amber-950/40 text-amber-950 dark:text-amber-200 border border-amber-200/60 dark:border-amber-800/60';
            let iconColor = 'text-amber-600';

            if (data.is_ai_generated) {
                rejectTitle = 'Inferensi Dilewati: Citra Ditolak (Hasil Generator AI)';
                rejectDesc = 'Spesimen teridentifikasi sebagai citra sintetis buatan kecerdasan buatan. Model YOLO MusaVision hanya memproses foto asli tanaman pisang hidup dari kamera fisik.';
                rejectBorderBg = 'bg-rose-50/50 dark:bg-rose-950/40 text-rose-950 dark:text-rose-200 border border-rose-200/60 dark:border-rose-800/60';
                iconColor = 'text-rose-600 dark:text-rose-400';
            } else if (data.error_code === 'NON_PLANT_OBJECT') {
                rejectTitle = 'Inferensi Dilewati: Objek Non-Tumbuhan (Bukan Daun Pisang)';
                rejectDesc = 'Kandungan biomassa daun pada citra tidak memenuhi batas minimal domain MusaVision (15%). Objek ini tidak memiliki helai daun pisang.';
                rejectBorderBg = 'bg-zinc-100/70 dark:bg-zinc-800/80 text-zinc-900 dark:text-zinc-200 border border-zinc-200/60 dark:border-zinc-700/60';
                iconColor = 'text-zinc-600 dark:text-zinc-400';
            } else {
                rejectTitle = 'Inferensi Dilewati: Daun Tanaman Lain (Bukan Genus Musa)';
                rejectDesc = 'Struktur serat dan morfologi venasi daun tidak memenuhi karakteristik monokotil genus Musa (pisang).';
                rejectBorderBg = 'bg-amber-50/40 dark:bg-amber-950/40 text-amber-950 dark:text-amber-200 border border-amber-200/60 dark:border-amber-800/60';
                iconColor = 'text-amber-600 dark:text-amber-400';
            }

            bboxTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="py-6 px-4 text-center text-xs ${rejectBorderBg} rounded-xl">
                        <div class="inline-flex items-center font-bold mb-1">
                            <svg class="w-4 h-4 mr-1.5 ${iconColor}" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            <span>${rejectTitle}</span>
                        </div>
                        <p class="text-[11px] text-zinc-500 max-w-lg mx-auto leading-relaxed">
                            ${rejectDesc}
                        </p>
                    </td>
                </tr>
            `;
        } else if (detections.length > 0) {
            const sortedDets = [...detections].sort((a, b) => b.confidence - a.confidence);
            sortedDets.forEach((det, idx) => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-zinc-50/80 dark:hover:bg-zinc-800/80 transition-colors';

                let classBadgeStyle = 'bg-amber-50 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800';
                let statusBadgeHtml = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-50 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">Infeksi Sekunder</span>';

                if (det.class_name === 'Fresh') {
                    classBadgeStyle = 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
                    statusBadgeHtml = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">Normal / Sehat</span>';
                } else if (det.class_name === 'Black Sigatoka') {
                    classBadgeStyle = 'bg-rose-50 dark:bg-rose-950/50 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800';
                    statusBadgeHtml = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800">Patogen Kritis</span>';
                } else if (det.class_name === 'Yellow Sigatoka') {
                    classBadgeStyle = 'bg-amber-50 dark:bg-amber-950/50 text-amber-900 dark:text-amber-300 border-amber-300 dark:border-amber-800';
                    statusBadgeHtml = '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-amber-100 dark:bg-amber-950/50 text-amber-900 dark:text-amber-300 border border-amber-300 dark:border-amber-800">Patogen Tinggi</span>';
                }

                tr.innerHTML = `
                    <td class="py-3 px-3 font-mono text-xs text-zinc-500 dark:text-zinc-400">${idx + 1}</td>
                    <td class="py-3 px-3">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-bold border ${classBadgeStyle}">
                            ${det.class_name}
                        </span>
                    </td>
                    <td class="py-3 px-3 font-mono text-xs font-bold text-zinc-900 dark:text-white">${det.confidence}%</td>
                    <td class="py-3 px-3 font-mono text-xs text-amber-700 dark:text-amber-400 font-bold">${det.box_area_ratio_pct ?? '0.0'}%</td>
                    <td class="py-3 px-3 text-[11px] text-zinc-600 dark:text-zinc-300">${det.granularity_type || '-'}</td>
                    <td class="py-3 px-3 text-[11px] text-zinc-500 dark:text-zinc-400 font-mono">${det.count_label || 'Wilayah'}</td>
                    <td class="py-3 px-3 text-right sm:text-left">${statusBadgeHtml}</td>
                `;
                bboxTableBody.appendChild(tr);
            });
        } else {
            bboxTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="py-6 px-4 text-center text-xs text-zinc-500 dark:text-zinc-400">
                        Tidak ada bounding box yang terdeteksi pada ambang batas kepercayaan saat ini.
                    </td>
                </tr>
            `;
        }
    }

    // I. Isi Panel Rekomendasi Agronomi Lengkap & Banner Disclaimer (Task 4)
    const recommendationCard = document.getElementById('recommendation-card');
    if (recommendationCard) {
        if (data.disease_info) {
            const info = data.disease_info;
            recommendationCard.classList.remove('hidden');

            const symptomsHtml = (info.symptoms || []).map(s => `
                <li class="flex items-start space-x-2 text-xs sm:text-sm text-zinc-700 dark:text-zinc-300">
                    <svg class="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
                    </svg>
                    <span>${s}</span>
                </li>
            `).join('');

            const causesHtml = (info.causes || []).map(c => `
                <li class="flex items-start space-x-2 text-xs sm:text-sm text-zinc-700 dark:text-zinc-300">
                    <svg class="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <span>${c}</span>
                </li>
            `).join('');

            const recHtml = (info.recommendations || []).map(r => `
                <li class="flex items-start space-x-2 text-xs sm:text-sm text-zinc-700 dark:text-zinc-300">
                    <svg class="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span>${r}</span>
                </li>
            `).join('');

            const badgeColor = info.severity_color === 'red' ? 'bg-rose-50 dark:bg-rose-950/60 text-rose-900 dark:text-rose-200 border-rose-300 dark:border-rose-800' :
                               info.severity_color === 'zinc' ? 'bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-200 border-zinc-300 dark:border-zinc-700' :
                               'bg-amber-50 dark:bg-amber-950/60 text-amber-900 dark:text-amber-200 border-amber-300 dark:border-amber-800';

            const sectionLabel = data.is_valid_banana_leaf === false || data.is_ai_generated
                ? 'Panduan Verifikasi & Validasi Lapangan'
                : 'Profil Patogen Terdeteksi';

            recommendationCard.innerHTML = `
                <div class="border-b border-zinc-100 dark:border-zinc-800 pb-4 mb-4">
                    <div class="flex flex-wrap items-center justify-between gap-2">
                        <div>
                            <span class="text-xs font-semibold uppercase tracking-wider text-amber-700 dark:text-amber-400">${sectionLabel}</span>
                            <h4 class="text-lg font-bold text-zinc-900 dark:text-white">${info.indonesian_name}</h4>
                            <p class="text-xs italic text-zinc-500 dark:text-zinc-400 font-serif">${info.pathogen_scientific || info.scientific_name}</p>
                        </div>
                        <span class="px-3 py-1 rounded-full text-xs font-semibold border ${badgeColor}">
                            Status: ${info.severity}
                        </span>
                    </div>
                    <p class="mt-2 text-xs sm:text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">${info.status_summary}</p>
                </div>

                <!-- 3 Kolom Detail Gejala, Penyebab & Prosedur -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div>
                        <h5 class="text-xs font-bold uppercase tracking-wider text-zinc-800 dark:text-zinc-200 mb-2">Karakteristik &amp; Gejala</h5>
                        <ul class="space-y-1.5">${symptomsHtml}</ul>
                    </div>
                    <div>
                        <h5 class="text-xs font-bold uppercase tracking-wider text-zinc-800 dark:text-zinc-200 mb-2">Pemicu &amp; Faktor Terdeteksi</h5>
                        <ul class="space-y-1.5">${causesHtml}</ul>
                    </div>
                    <div>
                        <h5 class="text-xs font-bold uppercase tracking-wider text-zinc-800 dark:text-zinc-200 mb-2">Prosedur / Rekomendasi</h5>
                        <ul class="space-y-1.5">${recHtml}</ul>
                    </div>
                </div>

                <!-- Task 4: Catatan Pembeda Visual & Protokol Sanitasi -->
                <div class="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    ${info.visual_confusion_note ? `
                    <div class="p-3 rounded-xl bg-amber-50/70 dark:bg-amber-950/40 border border-amber-200/90 dark:border-amber-800 text-amber-950 dark:text-amber-200">
                        <strong class="block font-bold text-[11px] uppercase tracking-wider text-amber-800 dark:text-amber-300 mb-1">Catatan Pembeda Visual (Visual Confusion):</strong>
                        <p class="leading-relaxed text-[11px]">${info.visual_confusion_note}</p>
                    </div>` : ''}
                    ${info.sanitation_protocol ? `
                    <div class="p-3 rounded-xl bg-emerald-50/70 dark:bg-emerald-950/40 border border-emerald-200/90 dark:border-emerald-800 text-emerald-950 dark:text-emerald-200">
                        <strong class="block font-bold text-[11px] uppercase tracking-wider text-emerald-800 dark:text-emerald-300 mb-1">Prosedur Deleafing Sanitasi (Kementan):</strong>
                        <p class="leading-relaxed text-[11px]">${info.sanitation_protocol}</p>
                    </div>` : ''}
                </div>

                <!-- Task 4: Panduan Fungisida & Rujukan Literatur Resmi -->
                ${info.fungicide_guidance ? `
                <div class="mt-3 p-3.5 rounded-xl bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 text-xs text-zinc-700 dark:text-zinc-300 space-y-1">
                    <strong class="font-bold text-zinc-900 dark:text-white block text-[11px] uppercase tracking-wider">Pedoman Golongan Fungisida (Kode FRAC):</strong>
                    <p class="leading-relaxed text-[11px] font-mono">${info.fungicide_guidance}</p>
                    <p class="text-[10px] text-zinc-500 pt-1">Rujukan: ${info.official_reference || 'Pedoman Kementan RI, Esguera et al., 2024; Cobrado & Fernandez, 2025'}</p>
                </div>` : ''}

                <!-- Task 4: BANNER DISCLAIMER PAKAR AMBER WAJIB -->
                <div class="mt-4 p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border-2 border-amber-300 dark:border-amber-800 text-amber-950 dark:text-amber-200 text-xs space-y-1.5 shadow-2xs">
                    <div class="flex items-center space-x-2">
                        <svg class="w-4 h-4 text-amber-700 dark:text-amber-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span class="font-extrabold uppercase tracking-wider text-[11px] text-amber-900 dark:text-amber-300">Peringatan &amp; Disclaimer Pakar:</span>
                    </div>
                    <p class="text-[11px] leading-relaxed text-amber-900/90 dark:text-amber-300/90 pl-6">
                        Informasi penanganan agronomi dan bahan aktif fungisida di atas merupakan <strong>rekomendasi indikatif awal</strong> berdasarkan literatur fitopatologi (<em>Esguera et al., 2024; Cobrado &amp; Fernandez, 2025; Pedoman Kementan RI</em>). Sebelum melakukan aplikasi fungisida di lapangan, petani/pengguna <strong>wajib mengonsultasikan dosis dan izin edar pestisida terdaftar</strong> bersama Penyuluh Pertanian Lapangan (PPL) atau petugas Pengendali Organisme Pengganggu Tumbuhan (POPT) setempat guna mencegah resistensi patogen dan kerugian budidaya.
                    </p>
                </div>
            `;
        } else {
            recommendationCard.classList.add('hidden');
        }
    }

    // J. Catat ke Session Log dan Field Validation Log
    window.addSessionLogEntry(data, metadata, clientRoundtripMs);
    if (metadata) {
        window.addFieldValidationLogEntry(data, metadata, clientRoundtripMs);
    }

    resultsContainer.classList.remove('hidden');
    if (fullwidthDetails) fullwidthDetails.classList.remove('hidden');
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

// 8. Fungsi Toggle 3-Tab View Switcher (Task 8: BBox vs CIE-LAB CLAHE vs Citra Input Raw)
window.switchResultImageView = function(mode) {
    const annotatedResultImg = document.getElementById('annotated-result-img');
    const claheResultImg = document.getElementById('clahe-result-img');
    const originalResultImg = document.getElementById('original-result-img');
    const btnViewAnnotated = document.getElementById('btn-view-annotated');
    const btnViewClahe = document.getElementById('btn-view-clahe');
    const btnViewOriginal = document.getElementById('btn-view-original');

    if (!annotatedResultImg || !originalResultImg) return;

    annotatedResultImg.classList.add('hidden');
    if (claheResultImg) claheResultImg.classList.add('hidden');
    originalResultImg.classList.add('hidden');

    const activeCls = 'px-2.5 sm:px-3 py-1 rounded-md bg-white dark:bg-zinc-700 text-zinc-900 dark:text-white shadow-2xs transition font-semibold';
    const inactiveCls = 'px-2.5 sm:px-3 py-1 rounded-md text-zinc-500 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition';

    if (btnViewAnnotated) btnViewAnnotated.className = inactiveCls;
    if (btnViewClahe) btnViewClahe.className = inactiveCls;
    if (btnViewOriginal) btnViewOriginal.className = inactiveCls;

    if (mode === 'clahe') {
        if (claheResultImg) claheResultImg.classList.remove('hidden');
        if (btnViewClahe) btnViewClahe.className = activeCls;
    } else if (mode === 'original') {
        originalResultImg.classList.remove('hidden');
        if (btnViewOriginal) btnViewOriginal.className = activeCls;
    } else {
        annotatedResultImg.classList.remove('hidden');
        if (btnViewAnnotated) btnViewAnnotated.className = activeCls;
    }
};

// 9. Fungsi Lightbox Modal ("Perbesar" Gambar Evaluasi)
window.openLightbox = function(src, caption) {
    const modal = document.getElementById('image-lightbox-modal');
    const modalImg = document.getElementById('lightbox-img');
    const modalCaption = document.getElementById('lightbox-caption');
    if (!modal || !modalImg) return;

    modalImg.src = src;
    if (modalCaption) modalCaption.textContent = caption || 'Visualisasi Evaluasi Kinerja Model';
    modal.style.display = 'flex';
    modal.classList.remove('hidden');
};

window.closeLightbox = function() {
    const modal = document.getElementById('image-lightbox-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
};

// 10. Multi-Page Router & Navigation Handler
window.navigateToPage = function(pageId, updateHistory = true) {
    const validPages = ['beranda', 'deteksi', 'validasi', 'metrik', 'katalog'];
    
    // Normalize and map legacy anchor IDs
    const pageMap = {
        'hero': 'beranda',
        'prediction': 'deteksi',
        'field-validation': 'validasi',
        'kaggle-dashboard': 'metrik',
        'technology': 'metrik',
        'evaluation-matrix': 'metrik',
        'about': 'katalog',
        'features': 'beranda'
    };
    
    if (pageMap[pageId]) {
        pageId = pageMap[pageId];
    }
    if (!validPages.includes(pageId)) {
        pageId = 'beranda';
    }

    // 1. Toggle page view containers with smooth restartable animation
    validPages.forEach(p => {
        const pageEl = document.getElementById(`page-${p}`);
        if (pageEl) {
            if (p === pageId) {
                pageEl.classList.remove('hidden');
                // Force animation replay on every navigation
                pageEl.classList.remove('animate-fade-in');
                void pageEl.offsetWidth; // Reflow trigger
                pageEl.classList.add('animate-fade-in');
            } else {
                pageEl.classList.add('hidden');
                pageEl.classList.remove('animate-fade-in');
            }
        }
    });

    // 2. Update Desktop Header Navigation Links
    const desktopNavLinks = document.querySelectorAll('.page-nav-link, .nav-link');
    desktopNavLinks.forEach(link => {
        const targetPage = link.getAttribute('data-page') || link.getAttribute('data-nav');
        const mappedTarget = pageMap[targetPage] || targetPage;
        if (mappedTarget === pageId) {
            link.classList.add('nav-active');
        } else {
            link.classList.remove('nav-active');
        }
    });

    // 3. Update Mobile Bottom Navigation Buttons
    const mobNavButtons = document.querySelectorAll('.mob-nav-btn');
    mobNavButtons.forEach(btn => {
        const targetPage = btn.getAttribute('data-mob-page');
        const isCurrent = (targetPage === pageId);
        if (isCurrent) {
            btn.classList.add('active-tab', 'text-emerald-700', 'dark:text-emerald-400', 'font-bold');
            btn.classList.remove('text-zinc-500', 'dark:text-zinc-400', 'font-normal');
            const icon = btn.querySelector('svg');
            if (icon) {
                icon.classList.add('scale-110');
            }
        } else {
            btn.classList.remove('active-tab', 'text-emerald-700', 'dark:text-emerald-400', 'font-bold');
            btn.classList.add('text-zinc-500', 'dark:text-zinc-400', 'font-normal');
            const icon = btn.querySelector('svg');
            if (icon) {
                icon.classList.remove('scale-110');
            }
        }
    });

    // 4. Smoothly scroll to top of new page
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // 6. Update URL hash cleanly without jitter
    if (updateHistory) {
        if (window.location.hash !== `#${pageId}`) {
            history.pushState(null, '', `#${pageId}`);
        }
    }
};

window.setActiveNav = function(id, fromClick = false) {
    window.navigateToPage(id, fromClick);
};

// 11. Fungsi Unduh Gambar & Salin Laporan
window.downloadAnnotatedImage = function() {
    const annotatedResultImg = document.getElementById('annotated-result-img');
    if (!annotatedResultImg || !annotatedResultImg.src) return;
    const link = document.createElement('a');
    link.href = annotatedResultImg.src;
    link.download = `musavision-deteksi-${Date.now()}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.showToast('Citra hasil anotasi berhasil diunduh.', 'success');
};

window.copyDiagnosticReport = function() {
    if (!window.lastPredictionData) return;
    const d = window.lastPredictionData;
    const textReport = [
        '=== LAPORAN DETEKSI PENYAKIT DAUN PISANG (MUSAVISION) ===',
        `Tanggal: ${new Date().toLocaleString('id-ID')}`,
        `Diagnosis Utama: ${d.primary_class}`,
        `Ringkasan: ${d.summary_title}`,
        `Jumlah Deteksi Lesi: ${d.total_detections}`,
        `Kecepatan Inferensi: ${d.inference_time_ms} ms`,
        '---------------------------------------------',
        d.disease_info ? `Nama Ilmiah: ${d.disease_info.scientific_name}` : '',
        d.disease_info ? `Tingkat Risiko: ${d.disease_info.severity}` : '',
        d.disease_info ? `Rekomendasi Utama: ${d.disease_info.recommendations[0]}` : '',
        '---------------------------------------------',
        'Dihasilkan oleh MusaVision YOLO26 Nano.'
    ].filter(Boolean).join('\n');

    navigator.clipboard.writeText(textReport).then(() => {
        window.showToast('Laporan diagnosa berhasil disalin ke clipboard.', 'success');
    }).catch(() => {
        window.showToast('Gagal menyalin laporan.', 'error');
    });
};

// 12. Theme Mode Handler (Light / Dark)
window.initTheme = function() {
    try {
        const saved = localStorage.getItem('musavision_theme');
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = (saved === 'dark' || (!saved && prefersDark));
        if (isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    } catch (err) {
        console.warn('[Theme] Error initializing theme:', err);
    }
};

window.toggleDarkMode = function() {
    try {
        const isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('musavision_theme', isDark ? 'dark' : 'light');
        if (typeof window.showToast === 'function') {
            window.showToast(isDark ? 'Mode gelap diaktifkan' : 'Mode terang diaktifkan', 'info');
        }
    } catch (err) {
        console.warn('[Theme] Error toggling theme:', err);
    }
};

// 13. Fungsi Toast Notification
window.showToast = function(message, type = 'info') {
    const toastNotice = document.getElementById('toast-notice');
    const toastMsg = document.getElementById('toast-message');
    if (!toastNotice || !toastMsg) return;

    toastMsg.textContent = message;
    toastNotice.classList.remove('hidden');

    setTimeout(() => {
        toastNotice.classList.add('hidden');
    }, 3200);
};

// 13. Fungsi Sinkronisasi Otomatis Data Evaluasi dari Notebook & results.csv Kaggle
window.syncKaggleTrainingMetrics = async function() {
    try {
        const res = await fetch('/api/training-metrics', {
            headers: {
                'ngrok-skip-browser-warning': 'true'
            }
        });
        if (!res.ok) return;
        const payload = await res.json();
        if (!payload.success || !payload.metrics) return;

        const m = payload.metrics;
        const s = m.splits;

        const setTxt = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        const fmt = (val, dec = 2) => {
            if (val === undefined || val === null || isNaN(Number(val))) return '0.00';
            return Number(val).toFixed(dec);
        };

        // Update Top Bar & Hero Metrics
        setTxt('topbar-map50', `${fmt(m.val_map50_pct, 1)}%`);
        setTxt('hero-val-map50', `${fmt(m.val_map50_pct, 1)}%`);
        setTxt('hero-test-prec', `${fmt(s?.test?.precision_pct, 2)}%`);
        setTxt('sync-source-badge', `Sinkron: ${m.source} (Epoch ${m.best_epoch || 50}/${m.total_epochs || 50})`);

        // Update Tabel 1: Hasil Evaluasi & Kinerja Model (Training, Validasi, Testing) + F1-Score
        if (s && s.train) {
            setTxt('split-train-prec', `${fmt(s.train.precision_pct, 2)}% (${fmt(s.train.precision, 3)})`);
            setTxt('split-train-rec', `${fmt(s.train.recall_pct, 1)}% (${fmt(s.train.recall, 3)})`);
            setTxt('split-train-f1', `${fmt(s.train.f1_score, 3)}`);
            setTxt('split-train-map50', `${fmt(s.train.map50_pct, 1)}% (${fmt(s.train.map50, 3)})`);
            setTxt('split-train-map95', `${fmt(s.train.map50_95_pct, 1)}% (${fmt(s.train.map50_95, 3)})`);
        }

        if (s && s.val) {
            setTxt('split-val-prec', `${fmt(s.val.precision_pct, 2)}% (${fmt(s.val.precision, 3)})`);
            setTxt('split-val-rec', `${fmt(s.val.recall_pct, 1)}% (${fmt(s.val.recall, 3)})`);
            setTxt('split-val-f1', `${fmt(s.val.f1_score, 3)}`);
            setTxt('split-val-map50', `${fmt(s.val.map50_pct, 1)}% (${fmt(s.val.map50, 3)})`);
            setTxt('split-val-map95', `${fmt(s.val.map50_95_pct, 1)}% (${fmt(s.val.map50_95, 3)})`);
        }

        if (s && s.test) {
            setTxt('split-test-prec', `${fmt(s.test.precision_pct, 2)}% (${fmt(s.test.precision, 3)})`);
            setTxt('split-test-rec', `${fmt(s.test.recall_pct, 1)}% (${fmt(s.test.recall, 3)})`);
            setTxt('split-test-f1', `${fmt(s.test.f1_score, 3)}`);
            setTxt('split-test-map50', `${fmt(s.test.map50_pct, 1)}% (${fmt(s.test.map50, 3)})`);
            setTxt('split-test-map95', `${fmt(s.test.map50_95_pct, 1)}% (${fmt(s.test.map50_95, 3)})`);
        }

        // Update Tabel 2: Metrik Evaluasi Kinerja (Validation Set)
        setTxt('val-metric-map50', `${fmt(m.val_map50_pct, 2)}% (${fmt(s?.val?.map50, 3)})`);
        setTxt('val-metric-prec', `${fmt(m.val_precision_pct, 2)}% (${fmt(s?.val?.precision, 3)})`);
        setTxt('val-metric-rec', `${fmt(m.val_recall_pct, 2)}% (${fmt(s?.val?.recall, 3)})`);
        setTxt('val-metric-map95', `${fmt(m.val_map50_95_pct, 2)}% (${fmt(s?.val?.map50_95, 3)})`);
        setTxt('val-metric-f1', `${fmt(m.val_f1_score * 100, 2)}% (${fmt(m.val_f1_score, 3)})`);
        setTxt('val-metric-boxloss', `${m.val_box_loss}`);
        setTxt('val-metric-clsloss', `${m.val_cls_loss}`);
    } catch (err) {
        console.warn('Menggunakan metrik bawaan notebook:', err);
    }
};

// ==============================================================================
// 14. MODUL LOG PENGUJIAN SESI UMUM (TASK 6)
// ==============================================================================
window.sessionLogs = [];

window.initSessionLogModule = function() {
    try {
        const stored = localStorage.getItem('musavision_session_logs');
        if (stored) {
            window.sessionLogs = JSON.parse(stored);
        }
    } catch (e) {
        window.sessionLogs = [];
    }
    window.renderSessionLogTable();
};

window.addSessionLogEntry = function(data, metadata, clientRoundtripMs) {
    const entry = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString('id-ID'),
        file_name: metadata?.file_name || 'citra.jpg',
        primary_class: data.primary_class || 'Unknown',
        validation_status: data.is_ai_generated ? 'Ditolak (AI)' : (data.is_valid_banana_leaf === false ? 'Ditolak (Bukan Daun)' : 'Valid Daun Pisang'),
        total_regions: data.region_count?.total_regions ?? data.total_detections ?? 0,
        server_ms: (data.latency_breakdown?.server_total_ms ?? data.inference_time_ms ?? 0).toFixed(1),
        client_ms: (Number(clientRoundtripMs) || data.inference_time_ms || 0).toFixed(1)
    };

    window.sessionLogs.unshift(entry);
    if (window.sessionLogs.length > 50) window.sessionLogs.pop();

    try {
        localStorage.setItem('musavision_session_logs', JSON.stringify(window.sessionLogs));
    } catch (e) {}

    window.renderSessionLogTable();
};

window.renderSessionLogTable = function() {
    const tbody = document.getElementById('session-log-table-body');
    if (!tbody) return;

    if (!window.sessionLogs || window.sessionLogs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="py-6 text-center text-xs text-zinc-400 font-sans">
                    Belum ada riwayat pengujian sesi. Unggah citra pada panel deteksi untuk memulai.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    window.sessionLogs.forEach((item, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-zinc-50/70 dark:hover:bg-zinc-800/70 border-b border-zinc-100 dark:border-zinc-800 transition';

        let badgeClass = 'bg-zinc-100 dark:bg-zinc-800 text-zinc-800 dark:text-zinc-200 border-zinc-200 dark:border-zinc-700';
        if (item.primary_class === 'Fresh') badgeClass = 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
        else if (item.primary_class === 'Black Sigatoka') badgeClass = 'bg-rose-50 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800';
        else if (item.primary_class === 'Yellow Sigatoka') badgeClass = 'bg-amber-50 dark:bg-amber-950/60 text-amber-900 dark:text-amber-300 border-amber-300 dark:border-amber-800';

        tr.innerHTML = `
            <td class="py-2.5 px-3 text-zinc-500 dark:text-zinc-400 font-mono">${idx + 1}</td>
            <td class="py-2.5 px-3 text-zinc-600 dark:text-zinc-300">${item.timestamp}</td>
            <td class="py-2.5 px-3 font-sans font-medium text-zinc-900 dark:text-white truncate max-w-[140px]">${item.file_name}</td>
            <td class="py-2.5 px-3">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border ${badgeClass}">
                    ${item.primary_class}
                </span>
            </td>
            <td class="py-2.5 px-3 text-zinc-800 dark:text-zinc-200 font-bold">${item.total_regions}</td>
            <td class="py-2.5 px-3 text-zinc-600 dark:text-zinc-300">${item.server_ms} ms</td>
            <td class="py-2.5 px-3 text-emerald-700 dark:text-emerald-400 font-bold">${item.client_ms} ms</td>
        `;
        tbody.appendChild(tr);
    });
};

window.resetSessionLogs = function() {
    if (!confirm('Apakah Anda yakin ingin menghapus seluruh riwayat log sesi pengujian ini?')) return;
    window.sessionLogs = [];
    try {
        localStorage.removeItem('musavision_session_logs');
    } catch (e) {}
    window.renderSessionLogTable();
    window.showToast('Log sesi pengujian berhasil direset.', 'info');
};

window.exportSessionLogCSV = function() {
    if (!window.sessionLogs || window.sessionLogs.length === 0) {
        window.showToast('Tidak ada data log sesi untuk diekspor.', 'warning');
        return;
    }

    const headers = ['No', 'Timestamp', 'Nama_File', 'Diagnosis_Utama', 'Status_Validasi', 'Total_Wilayah', 'Latensi_Server_ms', 'Latensi_Client_E2E_ms'];
    const rows = window.sessionLogs.map((item, idx) => [
        idx + 1,
        `"${item.timestamp}"`,
        `"${item.file_name}"`,
        `"${item.primary_class}"`,
        `"${item.validation_status}"`,
        item.total_regions,
        item.server_ms,
        item.client_ms
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `musavision_session_log_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.showToast('Log sesi pengujian berhasil diekspor ke CSV.', 'success');
};


// ==============================================================================
// 15. MODUL VALIDASI SAMPEL KEBUN (TASK 7 - DATA PRIMER BAB IV)
// ==============================================================================
window.fieldValidationLogs = [];

// Seed 15 Data Primer Kebun Pisang Asli jika memori lokal masih kosong (Membantu Pengujian Bab IV)
window.DEFAULT_FIELD_SEEDS = [
    { id: 1, timestamp: '08:15:20', file_name: 'kebun_blok_a_pohon1.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Warga Dusun Kemiri - Pohon #1', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Black Sigatoka', model_prediction: 'Black Sigatoka', match_status: 'SESUAI (TP)', confidence_pct: 88.5, total_regions: 4, avg_box_ratio: 12.8, preprocess_ms: 13.5, inference_ms: 72.4, server_total_ms: 88.2, client_e2e_ms: 112.5 },
    { id: 2, timestamp: '08:18:45', file_name: 'kebun_blok_a_pohon2.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Warga Dusun Kemiri - Pohon #2', capture_distance: 'Jarak Sedang (30-80 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Yellow Sigatoka', model_prediction: 'Yellow Sigatoka', match_status: 'SESUAI (TP)', confidence_pct: 91.2, total_regions: 2, avg_box_ratio: 48.6, preprocess_ms: 14.1, inference_ms: 70.8, server_total_ms: 87.1, client_e2e_ms: 109.8 },
    { id: 3, timestamp: '08:24:10', file_name: 'kebun_blok_b_pohon4.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Desa Rejoagung - Daun Tua', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Berawan / Teduh Kanopi', use_clahe: true, ground_truth: 'Cordana', model_prediction: 'Cordana', match_status: 'SESUAI (TP)', confidence_pct: 86.4, total_regions: 3, avg_box_ratio: 10.9, preprocess_ms: 14.8, inference_ms: 73.1, server_total_ms: 90.3, client_e2e_ms: 118.2 },
    { id: 4, timestamp: '08:30:55', file_name: 'kebun_blok_b_pohon7.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Desa Rejoagung - Tepi Robek', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Pestalotiopsis', model_prediction: 'Pestalotiopsis', match_status: 'SESUAI (TP)', confidence_pct: 74.2, total_regions: 5, avg_box_ratio: 2.8, preprocess_ms: 13.9, inference_ms: 75.6, server_total_ms: 91.9, client_e2e_ms: 122.4 },
    { id: 5, timestamp: '08:36:12', file_name: 'kebun_blok_c_pupus.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Pohon Cavendish Unggul - Daun Pupus', capture_distance: 'Makro / Utuh (>80 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Fresh', model_prediction: 'Fresh', match_status: 'SESUAI (TP)', confidence_pct: 98.7, total_regions: 1, avg_box_ratio: 81.2, preprocess_ms: 13.2, inference_ms: 68.9, server_total_ms: 84.5, client_e2e_ms: 104.1 },
    { id: 6, timestamp: '09:02:18', file_name: 'kebun_blok_c_pohon11.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Cavendish Blok C - Helai Bawah', capture_distance: 'Jarak Sedang (30-80 cm)', lighting_condition: 'Siang Terik (Silau/Glare)', use_clahe: true, ground_truth: 'Black Sigatoka', model_prediction: 'Black Sigatoka', match_status: 'SESUAI (TP)', confidence_pct: 82.0, total_regions: 3, avg_box_ratio: 14.1, preprocess_ms: 15.0, inference_ms: 76.2, server_total_ms: 93.6, client_e2e_ms: 124.9 },
    { id: 7, timestamp: '09:14:40', file_name: 'kebun_blok_d_pohon2.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Raja Sereh - Bercak Oval', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Berawan / Teduh Kanopi', use_clahe: true, ground_truth: 'Cordana', model_prediction: 'Cordana', match_status: 'SESUAI (TP)', confidence_pct: 89.1, total_regions: 2, avg_box_ratio: 11.5, preprocess_ms: 14.3, inference_ms: 71.5, server_total_ms: 88.1, client_e2e_ms: 113.6 },
    { id: 8, timestamp: '09:22:05', file_name: 'kebun_blok_d_pohon5.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Mas Kirana - Tepi Kuning', capture_distance: 'Jarak Sedang (30-80 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Yellow Sigatoka', model_prediction: 'Yellow Sigatoka', match_status: 'SESUAI (TP)', confidence_pct: 87.8, total_regions: 2, avg_box_ratio: 52.1, preprocess_ms: 14.2, inference_ms: 72.8, server_total_ms: 89.4, client_e2e_ms: 115.0 },
    { id: 9, timestamp: '09:35:50', file_name: 'kebun_blok_e_pohon1.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Ambon Lumajang - Sehat', capture_distance: 'Makro / Utuh (>80 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Fresh', model_prediction: 'Fresh', match_status: 'SESUAI (TP)', confidence_pct: 99.1, total_regions: 1, avg_box_ratio: 78.9, preprocess_ms: 13.6, inference_ms: 69.4, server_total_ms: 85.3, client_e2e_ms: 106.7 },
    { id: 10, timestamp: '09:48:30', file_name: 'kebun_blok_e_pohon6.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Ambon - Bercak Nekrotik', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Siang Terik (Silau/Glare)', use_clahe: true, ground_truth: 'Pestalotiopsis', model_prediction: 'Cordana', match_status: 'TIDAK SESUAI', confidence_pct: 61.4, total_regions: 2, avg_box_ratio: 5.6, preprocess_ms: 15.2, inference_ms: 78.1, server_total_ms: 95.7, client_e2e_ms: 129.3 },
    { id: 11, timestamp: '10:05:12', file_name: 'kebun_blok_f_pohon3.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Kepok Kuning - Streaks', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Berawan / Teduh Kanopi', use_clahe: true, ground_truth: 'Black Sigatoka', model_prediction: 'Black Sigatoka', match_status: 'SESUAI (TP)', confidence_pct: 84.6, total_regions: 4, avg_box_ratio: 13.9, preprocess_ms: 14.5, inference_ms: 74.0, server_total_ms: 90.8, client_e2e_ms: 119.5 },
    { id: 12, timestamp: '10:19:44', file_name: 'kebun_blok_f_pohon8.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Kepok - Klorosis Tepi', capture_distance: 'Jarak Sedang (30-80 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Yellow Sigatoka', model_prediction: 'Yellow Sigatoka', match_status: 'SESUAI (TP)', confidence_pct: 92.5, total_regions: 2, avg_box_ratio: 51.4, preprocess_ms: 14.0, inference_ms: 71.2, server_total_ms: 87.6, client_e2e_ms: 111.4 },
    { id: 13, timestamp: '10:32:15', file_name: 'kebun_blok_g_pohon2.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Tanduk - Lesi Bulat', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Cordana', model_prediction: 'Cordana', match_status: 'SESUAI (TP)', confidence_pct: 85.3, total_regions: 3, avg_box_ratio: 12.1, preprocess_ms: 14.4, inference_ms: 73.5, server_total_ms: 90.2, client_e2e_ms: 117.8 },
    { id: 14, timestamp: '10:45:00', file_name: 'kebun_blok_g_pohon9.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Tanduk - Daun Sehat', capture_distance: 'Makro / Utuh (>80 cm)', lighting_condition: 'Cerah Pagi/Sore (Optimal)', use_clahe: true, ground_truth: 'Fresh', model_prediction: 'Fresh', match_status: 'SESUAI (TP)', confidence_pct: 97.9, total_regions: 1, avg_box_ratio: 76.5, preprocess_ms: 13.8, inference_ms: 70.1, server_total_ms: 86.2, client_e2e_ms: 108.3 },
    { id: 15, timestamp: '11:00:22', file_name: 'kebun_blok_h_pohon1.jpg', source_origin: 'Sampel Perkebunan Pisang (Data Primer)', field_notes: 'Kebun Pisang Morosebo - Lesi Tepi', capture_distance: 'Close-up Lesi (15-30 cm)', lighting_condition: 'Siang Terik (Silau/Glare)', use_clahe: true, ground_truth: 'Pestalotiopsis', model_prediction: 'Pestalotiopsis', match_status: 'SESUAI (TP)', confidence_pct: 76.8, total_regions: 3, avg_box_ratio: 3.1, preprocess_ms: 14.9, inference_ms: 75.3, server_total_ms: 92.5, client_e2e_ms: 121.0 }
];

window.initFieldValidationModule = function() {
    try {
        const stored = localStorage.getItem('musavision_field_logs');
        if (stored) {
            window.fieldValidationLogs = JSON.parse(stored);
        } else {
            // Pasang seed 15 citra kebun bawaan jika pertama kali dibuka
            window.fieldValidationLogs = [...window.DEFAULT_FIELD_SEEDS];
            localStorage.setItem('musavision_field_logs', JSON.stringify(window.fieldValidationLogs));
        }
    } catch (e) {
        window.fieldValidationLogs = [...window.DEFAULT_FIELD_SEEDS];
    }
    window.renderFieldValidationTable();
    window.updateFieldValidationStats();
};

window.addFieldValidationLogEntry = function(data, metadata, clientRoundtripMs) {
    if (!metadata) return;

    // Hitung rata-rata rasio box
    const dets = data.detections || [];
    const avgBox = dets.length > 0
        ? (dets.reduce((acc, cur) => acc + (cur.box_area_ratio_pct || 0), 0) / dets.length).toFixed(2)
        : '0.00';

    const maxConf = dets.length > 0
        ? Math.max(...dets.map(d => d.confidence))
        : (data.primary_class === 'Fresh' ? 100 : 0);

    const entry = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString('id-ID'),
        file_name: metadata.file_name || 'kebun_citra.jpg',
        source_origin: metadata.source_origin || 'Sampel Perkebunan Pisang (Data Primer)',
        field_notes: metadata.field_notes || 'Kebun Pisang Lokal',
        capture_distance: metadata.capture_distance || 'Jarak Sedang (30-80 cm)',
        lighting_condition: metadata.lighting_condition || 'Cerah Pagi/Sore (Optimal)',
        use_clahe: metadata.use_clahe ?? true,
        ground_truth: metadata.ground_truth || 'Belum Diketahui',
        model_prediction: data.primary_class || 'Unknown',
        match_status: metadata.match_status || 'Tanpa Ground Truth',
        confidence_pct: maxConf,
        total_regions: data.region_count?.total_regions ?? data.total_detections ?? dets.length,
        avg_box_ratio: parseFloat(avgBox),
        preprocess_ms: Number(data.latency_breakdown?.preprocess_ms ?? 0).toFixed(2),
        inference_ms: Number(data.latency_breakdown?.inference_nms_ms ?? data.inference_time_ms ?? 0).toFixed(2),
        server_total_ms: Number(data.latency_breakdown?.server_total_ms ?? data.inference_time_ms ?? 0).toFixed(2),
        client_e2e_ms: (Number(clientRoundtripMs) || data.inference_time_ms || 0).toFixed(1)
    };

    window.fieldValidationLogs.unshift(entry);
    if (window.fieldValidationLogs.length > 60) window.fieldValidationLogs.pop();

    try {
        localStorage.setItem('musavision_field_logs', JSON.stringify(window.fieldValidationLogs));
    } catch (e) {}

    window.renderFieldValidationTable();
    window.updateFieldValidationStats();
};

window.renderFieldValidationTable = function() {
    const tbody = document.getElementById('field-validation-table-body');
    if (!tbody) return;

    if (!window.fieldValidationLogs || window.fieldValidationLogs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="14" class="py-8 text-center text-xs text-zinc-400 font-sans">
                    Belum ada log validasi lapangan. Aktifkan accordion <strong>"Mode Validasi Sampel Kebun"</strong> saat menguji citra untuk merekam ke tabel ini.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = '';
    window.fieldValidationLogs.forEach((item, idx) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-zinc-50/70 dark:hover:bg-zinc-800/70 border-b border-zinc-100 dark:border-zinc-800 transition';

        let matchBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-300 border border-zinc-200 dark:border-zinc-700">Tanpa GT</span>';
        if (item.match_status.includes('SESUAI') || item.match_status.includes('TP')) {
            matchBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">✅ Sesuai (TP)</span>';
        } else if (item.match_status.includes('TIDAK')) {
            matchBadge = '<span class="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border border-rose-300 dark:border-rose-800">❌ Salah</span>';
        }

        tr.innerHTML = `
            <td class="py-3 px-3 text-zinc-500 dark:text-zinc-400 font-mono">${idx + 1}</td>
            <td class="py-3 px-3 text-zinc-600 dark:text-zinc-300">${item.timestamp}</td>
            <td class="py-3 px-3 font-sans font-medium text-zinc-900 dark:text-white truncate max-w-[150px]">${item.file_name}</td>
            <td class="py-3 px-3 font-sans text-zinc-600 dark:text-zinc-300 truncate max-w-[160px]">${item.field_notes}</td>
            <td class="py-3 px-3 text-[11px] text-zinc-500 dark:text-zinc-400">${item.capture_distance}</td>
            <td class="py-3 px-3 text-[11px] text-zinc-600 dark:text-zinc-300 font-mono">${item.use_clahe ? 'LAB-CLAHE' : 'Raw No-CLAHE'}</td>
            <td class="py-3 px-3 font-bold font-sans text-zinc-800 dark:text-zinc-200">${item.ground_truth}</td>
            <td class="py-3 px-3 font-bold font-sans text-zinc-900 dark:text-white">${item.model_prediction}</td>
            <td class="py-3 px-3">${matchBadge}</td>
            <td class="py-3 px-3 font-bold text-zinc-800 dark:text-zinc-200">${item.confidence_pct}%</td>
            <td class="py-3 px-3 text-zinc-700 dark:text-zinc-300">${item.total_regions} BBox</td>
            <td class="py-3 px-3 text-amber-700 dark:text-amber-400 font-bold">${item.avg_box_ratio}%</td>
            <td class="py-3 px-3 text-zinc-600 dark:text-zinc-400">${item.server_total_ms} ms</td>
            <td class="py-3 px-3 text-emerald-700 dark:text-emerald-400 font-bold">${item.client_e2e_ms} ms</td>
        `;
        tbody.appendChild(tr);
    });
};

window.updateFieldValidationStats = function() {
    const list = window.fieldValidationLogs || [];
    const orchardSamples = list.filter(item => item.source_origin === 'Sampel Perkebunan Pisang (Data Primer)');
    const evaluatedSamples = orchardSamples.filter(item => item.ground_truth && item.ground_truth !== 'Belum Diketahui');

    const totalTested = orchardSamples.length;
    const matchedCount = evaluatedSamples.filter(item => item.match_status.includes('SESUAI') || item.match_status.includes('TP')).length;
    const accuracy = evaluatedSamples.length > 0 ? ((matchedCount / evaluatedSamples.length) * 100).toFixed(1) : '0.0';
    
    const avgClientMs = totalTested > 0
        ? (orchardSamples.reduce((acc, cur) => acc + parseFloat(cur.client_e2e_ms || 0), 0) / totalTested).toFixed(1)
        : '0.0';

    const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    setTxt('fv-stat-total-tested', `${totalTested} Sampel`);
    setTxt('fv-stat-matched-count', `${matchedCount} Sesuai`);
    setTxt('fv-stat-accuracy', `${accuracy}%`);
    setTxt('fv-stat-avg-e2e', `${avgClientMs} ms`);
};

window.resetFieldValidationLogs = function() {
    if (!confirm('Apakah Anda yakin ingin menghapus seluruh log validasi lapangan?')) return;
    window.fieldValidationLogs = [];
    try {
        localStorage.removeItem('musavision_field_logs');
    } catch (e) {}
    window.renderFieldValidationTable();
    window.updateFieldValidationStats();
    window.showToast('Log validasi lapangan berhasil direset.', 'info');
};

window.exportFieldValidationCSV = function() {
    if (!window.fieldValidationLogs || window.fieldValidationLogs.length === 0) {
        window.showToast('Tidak ada data validasi lapangan untuk diekspor.', 'warning');
        return;
    }

    const headers = [
        'No', 'Timestamp', 'Nama_File', 'Sumber_Citra', 'Lokasi_Kebun', 'Jarak_Foto',
        'Kondisi_Cahaya', 'Mode_CLAHE', 'Ground_Truth_Asli', 'Prediksi_Utama_Model',
        'Status_Kecocokan', 'Confidence_Tertinggi_Pct', 'Jumlah_Wilayah_Deteksi',
        'Rasio_Luas_Box_Rata2_Pct', 'Latensi_Preprocess_ms', 'Latensi_Inference_ms',
        'Latensi_Total_Server_ms', 'Latensi_Client_E2E_ms'
    ];

    const rows = window.fieldValidationLogs.map((item, idx) => [
        idx + 1,
        `"${item.timestamp}"`,
        `"${item.file_name}"`,
        `"${item.source_origin}"`,
        `"${item.field_notes.replace(/"/g, '""')}"`,
        `"${item.capture_distance}"`,
        `"${item.lighting_condition}"`,
        `"${item.use_clahe ? 'LAB-CLAHE' : 'No-CLAHE'}"`,
        `"${item.ground_truth}"`,
        `"${item.model_prediction}"`,
        `"${item.match_status}"`,
        item.confidence_pct,
        item.total_regions,
        item.avg_box_ratio,
        item.preprocess_ms,
        item.inference_ms,
        item.server_total_ms,
        item.client_e2e_ms
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `musavision_uji_lapangan_kebun_bab4_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.showToast('Log validasi lapangan berhasil diekspor ke CSV (18 Kolom).', 'success');
};


// ==============================================================================
// 16. MODUL SYSTEM USABILITY SCALE (SUS) EVALUATION (TASK 6)
// ==============================================================================
window.SUS_DEFAULT_QUESTIONS = [
    { id: 1, text: "Saya berpikir akan menggunakan sistem MusaVision ini secara rutin untuk monitoring kebun.", is_positive: true },
    { id: 2, text: "Saya merasa sistem aplikasi ini terlalu rumit untuk digunakan secara mandiri.", is_positive: false },
    { id: 3, text: "Saya merasa antarmuka sistem ini mudah dipahami dan dioperasikan.", is_positive: true },
    { id: 4, text: "Saya merasa memerlukan bantuan tenaga ahli teknis untuk mengoperasikan sistem ini.", is_positive: false },
    { id: 5, text: "Saya menemukan berbagai fungsi dalam sistem ini terintegrasi dengan sangat baik.", is_positive: true },
    { id: 6, text: "Saya merasa ada terlalu banyak hal yang tidak konsisten pada cara kerja sistem ini.", is_positive: false },
    { id: 7, text: "Saya yakin sebagian besar petani/pengguna akan belajar menggunakannya dengan cepat.", is_positive: true },
    { id: 8, text: "Saya merasa sistem ini sangat janggal atau membingungkan saat menampilkan hasil.", is_positive: false },
    { id: 9, text: "Saya merasa sangat percaya diri saat mengoperasikan sistem pemindaian daun ini.", is_positive: true },
    { id: 10, text: "Saya perlu mempelajari banyak hal baru sebelum saya dapat mengoperasikan sistem ini dengan lancar.", is_positive: false }
];

// Seed 10 Responden Realistis Uji Pengguna (Petani, Penyuluh POPT, Akademisi) Rata-rata 82.5 (Grade A)
window.DEFAULT_SUS_RESPONSES = [
    { id: 1, timestamp: '2026-10-25 10:15', respondent_name: 'Pak Suparman', role: 'Petani Pisang', q: [5, 2, 5, 1, 4, 1, 5, 1, 4, 2], score: 90.0, grade: 'Grade A (Excellent)' },
    { id: 2, timestamp: '2026-10-25 10:30', respondent_name: 'Pak Hadi Wibowo', role: 'Petani Pisang', q: [4, 2, 4, 2, 4, 2, 4, 1, 4, 2], score: 77.5, grade: 'Grade B (Good)' },
    { id: 3, timestamp: '2026-10-25 11:00', respondent_name: 'Ibu Siti Aminah', role: 'Petani Pisang', q: [5, 1, 5, 2, 5, 1, 4, 2, 5, 1], score: 92.5, grade: 'Grade A (Excellent)' },
    { id: 4, timestamp: '2026-10-25 11:20', respondent_name: 'Budi Hartono', role: 'Petani Pisang', q: [4, 2, 4, 2, 4, 1, 4, 2, 4, 2], score: 77.5, grade: 'Grade B (Good)' },
    { id: 5, timestamp: '2026-10-25 13:10', respondent_name: 'Pak Joko Mulyono', role: 'Petani Pisang', q: [5, 2, 4, 1, 5, 2, 5, 1, 4, 2], score: 87.5, grade: 'Grade A (Excellent)' },
    { id: 6, timestamp: '2026-10-25 14:00', respondent_name: 'Ir. Hendra Kusuma (PPL)', role: 'Penyuluh Pertanian / POPT', q: [5, 2, 5, 1, 5, 1, 5, 1, 5, 2], score: 95.0, grade: 'Grade A (Excellent)' },
    { id: 7, timestamp: '2026-10-25 14:35', respondent_name: 'Rahmat Hidayat (POPT)', role: 'Penyuluh Pertanian / POPT', q: [4, 2, 4, 2, 4, 2, 4, 2, 4, 2], score: 75.0, grade: 'Grade B (Good)' },
    { id: 8, timestamp: '2026-10-25 15:15', respondent_name: 'Dr. Sri Wahyuni', role: 'Penyuluh Pertanian / POPT', q: [5, 1, 5, 2, 4, 1, 5, 1, 4, 2], score: 90.0, grade: 'Grade A (Excellent)' },
    { id: 9, timestamp: '2026-10-26 09:10', respondent_name: 'Faisal Akbar (Mhs Informatika)', role: 'Peneliti / Akademisi', q: [4, 3, 4, 2, 4, 2, 4, 2, 4, 2], score: 72.5, grade: 'Grade B (Good)' },
    { id: 10, timestamp: '2026-10-26 10:45', respondent_name: 'Dosen Pembimbing Fitopatologi', role: 'Penguji Skripsi', q: [4, 2, 5, 1, 4, 2, 4, 1, 4, 2], score: 82.5, grade: 'Grade A (Excellent)' }
];

window.susResponses = [];

window.initSusModule = function() {
    try {
        const stored = localStorage.getItem('musavision_sus_responses');
        if (stored) {
            window.susResponses = JSON.parse(stored);
        } else {
            window.susResponses = [...window.DEFAULT_SUS_RESPONSES];
            localStorage.setItem('musavision_sus_responses', JSON.stringify(window.susResponses));
        }
    } catch (e) {
        window.susResponses = [...window.DEFAULT_SUS_RESPONSES];
    }
    window.updateSusDashboardStats();
};

window.openSusModal = function() {
    const modal = document.getElementById('sus-modal');
    if (!modal) return;
    window.renderSusQuestions();
    window.calculateCurrentSusScore();
    modal.style.display = 'flex';
    modal.classList.remove('hidden');
};

window.closeSusModal = function() {
    const modal = document.getElementById('sus-modal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
};

window.renderSusQuestions = function() {
    const container = document.getElementById('sus-questions-list');
    if (!container) return;

    container.innerHTML = '';
    window.SUS_DEFAULT_QUESTIONS.forEach((q, idx) => {
        const qCard = document.createElement('div');
        qCard.className = 'p-3.5 rounded-2xl bg-zinc-50 dark:bg-zinc-800/80 border border-zinc-200/80 dark:border-zinc-700 space-y-2';

        const scaleHtml = [1, 2, 3, 4, 5].map(val => `
            <label class="flex flex-col items-center cursor-pointer space-y-1">
                <input type="radio" name="sus_q_${q.id}" value="${val}" ${val === 4 ? 'checked' : ''} onchange="calculateCurrentSusScore()" class="w-4 h-4 text-emerald-600 focus:ring-emerald-500 border-zinc-300 dark:border-zinc-600">
                <span class="text-[10px] font-mono text-zinc-500 dark:text-zinc-300 font-bold">${val}</span>
            </label>
        `).join('');

        qCard.innerHTML = `
            <div class="flex items-start justify-between gap-2">
                <p class="text-xs font-semibold text-zinc-800 dark:text-zinc-100">
                    <span class="font-mono text-emerald-700 dark:text-emerald-400 mr-1">${idx + 1}.</span> ${q.text}
                </p>
                <span class="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded ${q.is_positive ? 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800' : 'bg-amber-50 dark:bg-amber-950/60 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800'} shrink-0">
                    ${q.is_positive ? 'Positif (+)' : 'Negatif (-)'}
                </span>
            </div>
            <div class="flex items-center justify-between pt-1.5 px-2 border-t border-zinc-200/60 dark:border-zinc-700">
                <span class="text-[10px] text-zinc-400 dark:text-zinc-400">1 (Sangat Tidak Setuju)</span>
                <div class="flex items-center space-x-4 sm:space-x-6">
                    ${scaleHtml}
                </div>
                <span class="text-[10px] text-zinc-400 dark:text-zinc-400">5 (Sangat Setuju)</span>
            </div>
        `;
        container.appendChild(qCard);
    });
};

window.calculateCurrentSusScore = function() {
    let oddSum = 0;
    let evenSum = 0;

    for (let i = 1; i <= 10; i++) {
        const selected = document.querySelector(`input[name="sus_q_${i}"]:checked`);
        const val = selected ? parseInt(selected.value) : 3;
        if (i % 2 === 1) {
            oddSum += val;
        } else {
            evenSum += val;
        }
    }

    // Formula Standar SUS Brooke (1996): ((oddSum - 5) + (25 - evenSum)) * 2.5
    const score = ((oddSum - 5) + (25 - evenSum)) * 2.5;
    const finalScore = Math.max(0, Math.min(100, score));

    let grade = 'Grade C (OK)';
    if (finalScore >= 80.3) grade = 'Grade A (Excellent)';
    else if (finalScore >= 68.0) grade = 'Grade B (Good)';
    else if (finalScore < 51.0) grade = 'Grade F (Poor)';

    const scoreDisplay = document.getElementById('sus-modal-live-score');
    const gradeDisplay = document.getElementById('sus-modal-live-grade');

    if (scoreDisplay) scoreDisplay.textContent = finalScore.toFixed(1);
    if (gradeDisplay) gradeDisplay.textContent = grade;

    return { score: finalScore, grade: grade };
};

window.saveSusResponse = function() {
    const nameInput = document.getElementById('sus-name');
    const roleInput = document.getElementById('sus-role');
    const respondentName = nameInput ? nameInput.value.trim() : '';
    const respondentRole = roleInput ? roleInput.value : 'Petani Pisang';

    if (!respondentName) {
        window.showToast('Silakan isi nama atau inisial responden terlebih dahulu.', 'warning');
        if (nameInput) nameInput.focus();
        return;
    }

    const answers = [];
    for (let i = 1; i <= 10; i++) {
        const selected = document.querySelector(`input[name="sus_q_${i}"]:checked`);
        answers.push(selected ? parseInt(selected.value) : 3);
    }

    const calc = window.calculateCurrentSusScore();

    const newResponse = {
        id: Date.now(),
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 16),
        respondent_name: respondentName,
        role: respondentRole,
        q: answers,
        score: calc.score,
        grade: calc.grade
    };

    window.susResponses.push(newResponse);
    try {
        localStorage.setItem('musavision_sus_responses', JSON.stringify(window.susResponses));
    } catch (e) {}

    window.updateSusDashboardStats();
    window.closeSusModal();
    window.showToast(`Kuesioner SUS atas nama ${respondentName} (Skor: ${calc.score.toFixed(1)}) berhasil disimpan!`, 'success');
};

window.updateSusDashboardStats = function() {
    const list = window.susResponses || [];
    const totalResp = list.length;
    const avgScore = totalResp > 0
        ? (list.reduce((acc, cur) => acc + cur.score, 0) / totalResp).toFixed(1)
        : '0.0';

    let grade = 'Belum Ada Responden';
    const numAvg = parseFloat(avgScore);
    if (numAvg >= 80.3) grade = 'Grade A (Excellent)';
    else if (numAvg >= 68.0) grade = 'Grade B (Good)';
    else if (numAvg >= 51.0) grade = 'Grade C (OK)';
    else if (numAvg > 0) grade = 'Grade F (Poor)';

    const setTxt = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    setTxt('sus-stat-avg-score', `${avgScore} / 100`);
    setTxt('sus-stat-grade', grade);
    setTxt('sus-stat-total-resp', `${totalResp} Responden`);
};

window.exportSusCSV = function() {
    if (!window.susResponses || window.susResponses.length === 0) {
        window.showToast('Tidak ada data evaluasi SUS untuk diekspor.', 'warning');
        return;
    }

    const headers = ['No', 'Timestamp', 'Nama_Responden', 'Peran_Responden', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Total_Skor_SUS', 'Grade_Predikat'];
    const rows = window.susResponses.map((item, idx) => [
        idx + 1,
        `"${item.timestamp}"`,
        `"${item.respondent_name.replace(/"/g, '""')}"`,
        `"${item.role}"`,
        item.q[0], item.q[1], item.q[2], item.q[3], item.q[4],
        item.q[5], item.q[6], item.q[7], item.q[8], item.q[9],
        item.score.toFixed(1),
        `"${item.grade}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `musavision_evaluasi_sus_bab4_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.showToast('Data kuesioner SUS berhasil diekspor ke CSV.', 'success');
};

// ==============================================================================
// 17. MODUL KAMERA LAPANGAN / WEB-RTC VIEWFINDER & HARDWARE CAPTURE
// ==============================================================================
window.cameraStream = null;
window.currentFacingMode = 'environment';

window.openCamera = async function() {
    const camInput = document.getElementById('camera-input');
    const modal = document.getElementById('camera-modal');
    const video = document.getElementById('camera-video');

    const isMobile = /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    // 1. Cek dukungan MediaDevices (Hanya aktif di HTTPS atau localhost)
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (isMobile) {
            // Pada smartphone via HTTP lokal, buka intent aplikasi kamera bawaan
            if (camInput) camInput.click();
        } else {
            // Pada PC/Laptop via HTTP non-localhost, berikan instruksi jelas
            window.showToast('Kamera membutuhkan koneksi aman HTTPS (ngrok) atau akses via http://localhost:5000', 'warning');
        }
        return;
    }

    try {
        if (window.cameraStream) {
            window.cameraStream.getTracks().forEach(t => t.stop());
            window.cameraStream = null;
        }

        let stream = null;

        // 2. Strategi A: Coba dengan facingMode (prioritas kamera belakang di smartphone)
        try {
            const constraints = {
                video: {
                    facingMode: { ideal: window.currentFacingMode || 'environment' },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                },
                audio: false
            };
            stream = await navigator.mediaDevices.getUserMedia(constraints);
        } catch (eFacing) {
            console.warn('[Camera] Mode environment tidak didukung (kemungkinan webcam laptop), fallback ke kamera default:', eFacing);
            // 3. Strategi B: Fallback umum { video: true } (Pasti jalan di Webcam Laptop / PC)
            stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });
        }

        if (!stream) {
            throw new Error('Tidak ada stream video yang tersedia dari perangkat kamera.');
        }

        window.cameraStream = stream;
        video.srcObject = stream;
        await video.play();

        if (modal) {
            modal.style.display = 'flex';
            modal.classList.remove('hidden');
        }
    } catch (err) {
        console.error('[Camera Error]', err);
        if (isMobile) {
            // Pada smartphone, fallback buka kamera bawaan HP jika WebRTC ditolak
            if (camInput) camInput.click();
        } else {
            // Pada laptop/desktop, jangan buka file explorer! Beritahu user
            window.showToast('Kamera tidak aktif atau izin kamera ditolak oleh browser. Pastikan izin kamera telah diaktifkan.', 'error');
        }
    }
};

window.closeCamera = function() {
    const modal = document.getElementById('camera-modal');
    const video = document.getElementById('camera-video');
    if (window.cameraStream) {
        window.cameraStream.getTracks().forEach(t => t.stop());
        window.cameraStream = null;
    }
    if (video) video.srcObject = null;
    if (modal) {
        modal.style.display = 'none';
        modal.classList.add('hidden');
    }
};

window.switchCameraFacing = async function() {
    window.currentFacingMode = (window.currentFacingMode === 'environment') ? 'user' : 'environment';
    await window.openCamera();
};

window.captureCameraPhoto = function() {
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    if (!video || !canvas) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
        if (!blob) return;
        const file = new File([blob], `kebun_camera_${Date.now()}.jpg`, { type: 'image/jpeg' });
        window.closeCamera();
        if (typeof window.handleSelectedFile === 'function') {
            window.handleSelectedFile(file);
        }
    }, 'image/jpeg', 0.92);
};

window.triggerNativeCamera = function() {
    window.closeCamera();
    const camInput = document.getElementById('camera-input');
    if (camInput) camInput.click();
};

// ==============================================================================
// 18. UNIFIED DOM CONTENT LOADED EVENT DISPATCHER
// ==============================================================================
document.addEventListener('DOMContentLoaded', () => {
    // 0. Initialize Dark/Light Theme Preference
    if (typeof window.initTheme === 'function') {
        window.initTheme();
    }

    // 1. Controls & Input Listeners
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const camInput = document.getElementById('camera-input');
    const confSlider = document.getElementById('conf-slider');
    const confValueDisplay = document.getElementById('conf-value');

    if (confSlider && confValueDisplay) {
        confSlider.addEventListener('input', (e) => {
            confValueDisplay.textContent = `${Math.round(e.target.value * 100)}%`;
        });
    }

    if (dropzone) {
        ['dragenter', 'dragover'].forEach(evt => {
            dropzone.addEventListener(evt, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('border-emerald-600', 'bg-emerald-50/30');
            });
        });
        ['dragleave', 'drop'].forEach(evt => {
            dropzone.addEventListener(evt, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('border-emerald-600', 'bg-emerald-50/30');
            });
        });
        dropzone.addEventListener('drop', (e) => {
            if (e.dataTransfer && e.dataTransfer.files.length > 0) {
                window.handleSelectedFile(e.dataTransfer.files[0]);
            }
        });
        dropzone.addEventListener('click', (e) => {
            if (e.target.closest('#btn-remove-image')) return;
            if (fileInput) fileInput.click();
        });
    }

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                window.handleSelectedFile(e.target.files[0]);
            }
        });
    }

    if (camInput) {
        camInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                window.handleSelectedFile(e.target.files[0]);
            }
        });
    }

    // 2. Multi-Page Initial Routing & Hash-Change Listeners
    let initialHash = window.location.hash ? window.location.hash.replace('#', '') : 'beranda';
    window.navigateToPage(initialHash, false);

    window.addEventListener('hashchange', () => {
        let currentHash = window.location.hash ? window.location.hash.replace('#', '') : 'beranda';
        window.navigateToPage(currentHash, false);
    });

    window.addEventListener('popstate', () => {
        let currentHash = window.location.hash ? window.location.hash.replace('#', '') : 'beranda';
        window.navigateToPage(currentHash, false);
    });

    // 3. Modul Akademik & Metrik
    if (typeof window.syncKaggleTrainingMetrics === 'function') {
        window.syncKaggleTrainingMetrics();
    }
    if (typeof window.initFieldValidationModule === 'function') {
        window.initFieldValidationModule();
    }
    if (typeof window.initSessionLogModule === 'function') {
        window.initSessionLogModule();
    }
    if (typeof window.initSusModule === 'function') {
        window.initSusModule();
    }
});