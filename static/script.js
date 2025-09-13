let currentFileId = null;

// DOM elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');

// Event listeners
browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
downloadBtn.addEventListener('click', downloadFile);
resetBtn.addEventListener('click', resetApp);

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
});

dropZone.addEventListener('click', () => fileInput.click());

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processFile(file);
    }
}

function processFile(file) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/tiff', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        showError('Please select a valid image file (JPG, PNG, TIFF, BMP)');
        return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
        showError('File size must be less than 50MB');
        return;
    }

    // Show progress
    showProgress();
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);

    // Upload and process
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showResult(data);
        } else {
            showError(data.error || 'Processing failed');
        }
    })
    .catch(error => {
        showError('Upload failed: ' + error.message);
    });
}

function showProgress() {
    hideAllSections();
    progressSection.style.display = 'block';
    
    // Animate progress
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
    }, 200);
    
    // Store interval to clear it later
    progressSection.dataset.interval = interval;
}

function showResult(data) {
    // Clear progress interval
    if (progressSection.dataset.interval) {
        clearInterval(progressSection.dataset.interval);
    }
    
    hideAllSections();
    currentFileId = data.file_id;
    
    // Update result info
    document.getElementById('originalName').textContent = data.original_filename;
    document.getElementById('originalSize').textContent = formatFileSize(data.original_size);
    document.getElementById('processedSize').textContent = formatFileSize(data.processed_size);
    
    // Show EXIF data
    const exifList = document.getElementById('exifList');
    const exifInfo = document.getElementById('exifInfo');
    
    if (Object.keys(data.exif_data).length > 0) {
        exifList.innerHTML = '';
        Object.entries(data.exif_data).forEach(([key, value]) => {
            const item = document.createElement('div');
            item.className = 'exif-item';
            item.innerHTML = `
                <span class="exif-key">${key}:</span>
                <span class="exif-value">${value}</span>
            `;
            exifList.appendChild(item);
        });
        exifInfo.style.display = 'block';
    } else {
        exifInfo.style.display = 'none';
    }
    
    resultSection.style.display = 'block';
}

function showError(message) {
    // Clear progress interval
    if (progressSection.dataset.interval) {
        clearInterval(progressSection.dataset.interval);
    }
    
    hideAllSections();
    document.getElementById('errorMessage').textContent = message;
    errorSection.style.display = 'block';
}

function hideAllSections() {
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function downloadFile() {
    if (currentFileId) {
        const link = document.createElement('a');
        link.href = `/download/${currentFileId}`;
        link.download = `exif_removed_${currentFileId}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function resetApp() {
    hideAllSections();
    currentFileId = null;
    fileInput.value = '';
    progressFill.style.width = '0%';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    resetApp();
});
