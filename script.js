class ArchitecturalAnimator {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000/api';
        this.currentJobId = null;
        this.pollingInterval = null;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const uploadZone = document.getElementById('uploadZone');
        const fileInput = document.getElementById('fileInput');
        const browseBtn = document.getElementById('browseBtn');
        const removeBtn = document.getElementById('removeBtn');
        const generateBtn = document.getElementById('generateBtn');
        const retryBtn = document.getElementById('retryBtn');
        const newAnimationBtn = document.getElementById('newAnimationBtn');

        // File upload handlers
        uploadZone.addEventListener('click', () => fileInput.click());
        uploadZone.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadZone.addEventListener('dragleave', this.handleDragLeave.bind(this));
        uploadZone.addEventListener('drop', this.handleFileDrop.bind(this));
        
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        removeBtn.addEventListener('click', this.removeSelectedFile.bind(this));
        generateBtn.addEventListener('click', this.generateAnimation.bind(this));
        retryBtn.addEventListener('click', this.resetToUpload.bind(this));
        newAnimationBtn.addEventListener('click', this.resetToUpload.bind(this));
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('uploadZone').classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('uploadZone').classList.remove('drag-over');
    }

    handleFileDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('uploadZone').classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    processFile(file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        if (!validTypes.includes(file.type)) {
            this.showError('Please select a valid image file (JPG, JPEG, PNG, or WEBP)');
            return;
        }

        // Validate file size (max 16MB)
        if (file.size > 16 * 1024 * 1024) {
            this.showError('File size must be less than 16MB');
            return;
        }

        // Display preview
        this.displayImagePreview(file);
        
        // Enable generate button
        document.getElementById('generateBtn').disabled = false;
    }

    displayImagePreview(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const previewSection = document.getElementById('previewSection');
            const previewImage = document.getElementById('previewImage');
            
            previewImage.src = e.target.result;
            previewSection.style.display = 'block';
        };
        
        reader.readAsDataURL(file);
    }

    removeSelectedFile() {
        const fileInput = document.getElementById('fileInput');
        const previewSection = document.getElementById('previewSection');
        const generateBtn = document.getElementById('generateBtn');
        
        fileInput.value = '';
        previewSection.style.display = 'none';
        generateBtn.disabled = true;
        
        this.hideError();
    }

    async generateAnimation() {
        const fileInput = document.getElementById('fileInput');
        const focusType = document.getElementById('focusType').value;
        
        if (!fileInput.files.length) {
            this.showError('Please select an image file first');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('focus_type', focusType);

        try {
            this.showProgress();
            this.disableGenerateButton();

            const response = await fetch(`${this.apiBaseUrl}/upload`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const data = await response.json();
            this.currentJobId = data.job_id;
            
            // Start polling for progress
            this.startProgressPolling();

        } catch (error) {
            console.error('Error generating animation:', error);
            this.showError(`Failed to start animation generation: ${error.message}`);
            this.hideProgress();
            this.enableGenerateButton();
        }
    }

    async startProgressPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        this.pollingInterval = setInterval(async () => {
            try {
                const response = await fetch(`${this.apiBaseUrl}/status/${this.currentJobId}`);
                
                if (!response.ok) {
                    throw new Error('Failed to fetch job status');
                }

                const data = await response.json();
                this.updateProgress(data);

                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(this.pollingInterval);
                    
                    if (data.status === 'completed') {
                        this.showResult(data.download_url);
                    } else {
                        this.showError(data.error || 'Animation generation failed');
                    }
                }

            } catch (error) {
                console.error('Error polling status:', error);
                clearInterval(this.pollingInterval);
                this.showError('Failed to check animation progress');
            }
        }, 2000); // Poll every 2 seconds
    }

    updateProgress(data) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const progressDetails = document.getElementById('progressDetails');

        const progress = data.progress || 0;
        progressFill.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;

        // Update progress details based on progress percentage
        let details = 'Initializing...';
        if (progress < 20) {
            details = 'Analyzing image structure...';
        } else if (progress < 40) {
            details = 'Processing architectural features...';
        } else if (progress < 60) {
            details = 'Generating 3D model...';
        } else if (progress < 80) {
            details = 'Creating animation sequence...';
        } else if (progress < 100) {
            details = 'Rendering final video...';
        } else {
            details = 'Complete!';
        }

        progressDetails.textContent = details;
    }

    showProgress() {
        this.hideError();
        this.hideResult();
        document.getElementById('progressSection').style.display = 'block';
    }

    hideProgress() {
        document.getElementById('progressSection').style.display = 'none';
    }

    async showResult(downloadUrl) {
        const resultSection = document.getElementById('resultSection');
        const videoElement = document.getElementById('resultVideo');
        const downloadLink = document.getElementById('downloadLink');

        // Set download link
        const fullDownloadUrl = `${this.apiBaseUrl}${downloadUrl}`;
        downloadLink.href = fullDownloadUrl;

        // Load and display video
        videoElement.src = fullDownloadUrl;
        videoElement.load();

        this.hideProgress();
        resultSection.style.display = 'block';

        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideResult() {
        document.getElementById('resultSection').style.display = 'none';
    }

    showError(message) {
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');

        errorMessage.textContent = message;
        errorSection.style.display = 'block';

        // Scroll to error
        errorSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideError() {
        document.getElementById('errorSection').style.display = 'none';
    }

    disableGenerateButton() {
        const generateBtn = document.getElementById('generateBtn');
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
    }

    enableGenerateButton() {
        const generateBtn = document.getElementById('generateBtn');
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Animation';
    }

    resetToUpload() {
        // Clear current state
        this.currentJobId = null;
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }

        // Reset UI
        this.removeSelectedFile();
        this.hideProgress();
        this.hideResult();
        this.hideError();
        this.enableGenerateButton();

        // Reset form
        document.getElementById('focusType').value = 'auto';
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ArchitecturalAnimator();
});

// Add some utility functions for better user experience
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Add global error handler
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
});
