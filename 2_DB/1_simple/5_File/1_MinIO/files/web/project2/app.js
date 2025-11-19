// MinIO File Manager SPA
class MinIOFileManager {
    constructor() {
        this.currentView = 'dashboard';
        this.files = [];
        this.settings = this.loadSettings();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.applyTheme();
        this.navigate('dashboard');
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.dataset.view;
                this.navigate(view);
            });
        });
    }

    navigate(view) {
        this.currentView = view;
        
        // Update active nav button
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === view);
        });

        // Load view
        this.loadView(view);
    }

    loadView(view) {
        const content = document.getElementById('content');
        const template = document.getElementById(`${view}-template`);
        
        if (template) {
            content.innerHTML = template.innerHTML;
            this.initializeView(view);
        }
    }

    initializeView(view) {
        switch(view) {
            case 'dashboard':
                this.initDashboard();
                break;
            case 'upload':
                this.initUpload();
                break;
            case 'files':
                this.initFiles();
                break;
            case 'settings':
                this.initSettings();
                break;
        }
    }

    // Dashboard View
    initDashboard() {
        this.updateStats();
        this.loadRecentFiles();
    }

    updateStats() {
        const totalFiles = document.getElementById('total-files');
        const storageUsed = document.getElementById('storage-used');
        const lastUpload = document.getElementById('last-upload');

        if (totalFiles) totalFiles.textContent = this.files.length;
        if (storageUsed) storageUsed.textContent = this.calculateStorageUsed();
        if (lastUpload) lastUpload.textContent = this.getLastUploadTime();
    }

    calculateStorageUsed() {
        const bytes = this.files.reduce((total, file) => total + (file.size || 0), 0);
        return this.formatBytes(bytes);
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 MB';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getLastUploadTime() {
        const lastUpload = localStorage.getItem('lastUpload');
        if (!lastUpload) return 'Never';
        
        const date = new Date(lastUpload);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    loadRecentFiles() {
        const list = document.getElementById('recent-files-list');
        if (!list) return;

        const recentFiles = this.files.slice(-5).reverse();
        list.innerHTML = recentFiles.map(file => `
            <li>${file.name} - ${this.formatBytes(file.size)}</li>
        `).join('') || '<li>No files uploaded yet</li>';
    }

    // Upload View
    initUpload() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');
        const browseBtn = document.getElementById('browse-btn');

        if (browseBtn) {
            browseBtn.addEventListener('click', () => fileInput.click());
        }

        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFiles(e.target.files);
            });
        }

        if (dropZone) {
            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('dragging');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('dragging');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('dragging');
                this.handleFiles(e.dataTransfer.files);
            });
        }
    }

    handleFiles(files) {
        const queueContainer = document.getElementById('upload-queue');
        const queueList = document.getElementById('queue-list');
        
        if (!files.length) return;

        queueContainer.classList.remove('hidden');
        queueList.innerHTML = '';

        Array.from(files).forEach(file => {
            const item = this.createUploadItem(file);
            queueList.appendChild(item);
            this.simulateUpload(file, item);
        });
    }

    createUploadItem(file) {
        const li = document.createElement('li');
        li.className = 'upload-item';
        li.innerHTML = `
            <span>${file.name}</span>
            <div class="upload-progress">
                <div class="progress-bar" style="width: 0%"></div>
            </div>
        `;
        return li;
    }

    simulateUpload(file, element) {
        const progressBar = element.querySelector('.progress-bar');
        let progress = 0;

        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress > 100) progress = 100;
            
            progressBar.style.width = progress + '%';

            if (progress === 100) {
                clearInterval(interval);
                this.onFileUploaded(file);
                setTimeout(() => {
                    element.innerHTML = `<span>${file.name}</span><span>✓ Uploaded</span>`;
                }, 500);
            }
        }, 200);
    }

    onFileUploaded(file) {
        this.files.push({
            name: file.name,
            size: file.size,
            type: file.type,
            uploadDate: new Date().toISOString()
        });
        
        localStorage.setItem('files', JSON.stringify(this.files));
        localStorage.setItem('lastUpload', new Date().toISOString());
        
        this.showNotification('File uploaded successfully', 'success');
    }

    // Files View
    initFiles() {
        this.loadFiles();
        this.setupFileSearch();
        this.setupFileSort();
    }

    loadFiles() {
        const grid = document.getElementById('file-grid');
        if (!grid) return;

        const savedFiles = localStorage.getItem('files');
        if (savedFiles) {
            this.files = JSON.parse(savedFiles);
        }

        grid.innerHTML = this.files.map(file => `
            <div class="file-card">
                <div class="file-icon">${this.getFileIcon(file.type)}</div>
                <div class="file-name">${file.name}</div>
                <div class="file-info">${this.formatBytes(file.size)}</div>
            </div>
        `).join('') || '<p>No files uploaded yet</p>';
    }

    getFileIcon(type) {
        if (type.startsWith('image/')) return '🖼️';
        if (type.startsWith('video/')) return '🎥';
        if (type.startsWith('audio/')) return '🎵';
        if (type.includes('pdf')) return '📄';
        if (type.includes('zip') || type.includes('rar')) return '📦';
        if (type.includes('html') || type.includes('css') || type.includes('javascript')) return '💻';
        return '📎';
    }

    setupFileSearch() {
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterFiles(e.target.value);
            });
        }
    }

    filterFiles(query) {
        const filtered = this.files.filter(file => 
            file.name.toLowerCase().includes(query.toLowerCase())
        );
        
        const grid = document.getElementById('file-grid');
        grid.innerHTML = filtered.map(file => `
            <div class="file-card">
                <div class="file-icon">${this.getFileIcon(file.type)}</div>
                <div class="file-name">${file.name}</div>
                <div class="file-info">${this.formatBytes(file.size)}</div>
            </div>
        `).join('') || '<p>No files found</p>';
    }

    setupFileSort() {
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortFiles(e.target.value);
            });
        }
    }

    sortFiles(sortBy) {
        switch(sortBy) {
            case 'name':
                this.files.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case 'size':
                this.files.sort((a, b) => b.size - a.size);
                break;
            case 'date':
                this.files.sort((a, b) => new Date(b.uploadDate) - new Date(a.uploadDate));
                break;
        }
        this.loadFiles();
    }

    // Settings View
    initSettings() {
        const form = document.getElementById('settings-form');
        if (form) {
            // Load current settings
            document.getElementById('endpoint').value = this.settings.endpoint;
            document.getElementById('bucket').value = this.settings.bucket;
            document.getElementById('theme').value = this.settings.theme;

            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveSettings();
            });
        }
    }

    loadSettings() {
        const saved = localStorage.getItem('settings');
        return saved ? JSON.parse(saved) : {
            endpoint: 'localhost:9000',
            bucket: 'demo-bucket',
            theme: 'light'
        };
    }

    saveSettings() {
        this.settings = {
            endpoint: document.getElementById('endpoint').value,
            bucket: document.getElementById('bucket').value,
            theme: document.getElementById('theme').value
        };

        localStorage.setItem('settings', JSON.stringify(this.settings));
        this.applyTheme();
        this.showNotification('Settings saved successfully', 'success');
    }

    applyTheme() {
        document.body.classList.toggle('dark-theme', this.settings.theme === 'dark');
    }

    // Notifications
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type}`;
        
        setTimeout(() => {
            notification.classList.add('hidden');
        }, 3000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MinIOFileManager();
});