/**
 * Organogram Printing - Interactive JavaScript
 * Professional printing and report generation functionality
 */

class OrganogramPrinting {
    constructor() {
        this.currentReportData = null;
        this.currentDownloadUrl = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadRecentReports();
    }
    
    setupEventListeners() {
        // Report type change
        const reportType = document.getElementById('report-type');
        if (reportType) {
            reportType.addEventListener('change', (e) => {
                this.handleReportTypeChange(e.target.value);
            });
        }
        
        // Preview button
        const previewBtn = document.getElementById('preview-btn');
        if (previewBtn) {
            previewBtn.addEventListener('click', () => {
                this.previewReport();
            });
        }
        
        // Generate button
        const generateBtn = document.getElementById('generate-btn');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateReport();
            });
        }
        
        // Print preview button
        const printPreviewBtn = document.getElementById('print-preview-btn');
        if (printPreviewBtn) {
            printPreviewBtn.addEventListener('click', () => {
                this.printPreview();
            });
        }
        
        // Download preview button
        const downloadPreviewBtn = document.getElementById('download-preview-btn');
        if (downloadPreviewBtn) {
            downloadPreviewBtn.addEventListener('click', () => {
                this.downloadPreview();
            });
        }
        
        // Download report button (in success modal)
        const downloadReportBtn = document.getElementById('download-report-btn');
        if (downloadReportBtn) {
            downloadReportBtn.addEventListener('click', () => {
                this.downloadGeneratedReport();
            });
        }
        
        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(button => {
            button.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.closeModal(modal.id);
            });
        });
        
        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }
    
    handleReportTypeChange(reportType) {
        const structureSelection = document.getElementById('structure-selection');
        const partySelection = document.getElementById('party-selection');
        
        if (reportType === 'party') {
            structureSelection.style.display = 'none';
            partySelection.style.display = 'block';
        } else {
            structureSelection.style.display = 'block';
            partySelection.style.display = 'none';
        }
        
        // Clear preview
        this.clearPreview();
    }
    
    async previewReport() {
        const reportType = document.getElementById('report-type').value;
        const structureId = document.getElementById('structure-select').value;
        const partyId = document.getElementById('party-select').value;
        const template = document.getElementById('template-select').value;
        
        // Validate selection
        if (reportType === 'structure' && !structureId) {
            this.showNotification('Please select a structure', 'warning');
            return;
        }
        
        if (reportType === 'party' && !partyId) {
            this.showNotification('Please select a party', 'warning');
            return;
        }
        
        try {
            this.showPreviewLoading();
            
            // Build preview URL
            let previewUrl = '/admin/corporate/preview-organogram/?';
            const params = new URLSearchParams();
            
            if (reportType === 'structure') {
                params.append('structure_id', structureId);
            } else {
                params.append('party_id', partyId);
            }
            params.append('template', template);
            
            previewUrl += params.toString();
            
            // Fetch preview
            const response = await fetch(previewUrl);
            
            if (response.ok) {
                const previewHtml = await response.text();
                this.showPreview(previewHtml);
            } else {
                throw new Error('Failed to generate preview');
            }
            
        } catch (error) {
            console.error('Preview error:', error);
            this.showPreviewError('Failed to generate preview');
        }
    }
    
    async generateReport() {
        const reportType = document.getElementById('report-type').value;
        const structureId = document.getElementById('structure-select').value;
        const partyId = document.getElementById('party-select').value;
        const template = document.getElementById('template-select').value;
        const format = document.getElementById('format-select').value;
        
        // Validate selection
        if (reportType === 'structure' && !structureId) {
            this.showNotification('Please select a structure', 'warning');
            return;
        }
        
        if (reportType === 'party' && !partyId) {
            this.showNotification('Please select a party', 'warning');
            return;
        }
        
        // Collect options
        const options = {
            include_statistics: document.getElementById('include-statistics').checked,
            include_hierarchy: document.getElementById('include-hierarchy').checked,
            include_ownership_details: document.getElementById('include-ownership-details').checked,
            include_jurisdictions: document.getElementById('include-jurisdictions').checked,
            include_compliance: document.getElementById('include-compliance').checked,
            include_recommendations: document.getElementById('include-recommendations').checked,
            page_size: document.getElementById('page-size').value,
            page_orientation: document.getElementById('page-orientation').value
        };
        
        const requestData = {
            report_type: reportType,
            template: template,
            format: format,
            options: options
        };
        
        if (reportType === 'structure') {
            requestData.structure_id = structureId;
        } else {
            requestData.party_id = partyId;
        }
        
        try {
            this.showLoadingModal();
            
            const response = await fetch('/admin/corporate/generate-organogram-report/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentDownloadUrl = result.download_url;
                this.showSuccessModal(result.message, result.filename);
                this.loadRecentReports(); // Refresh recent reports
            } else {
                throw new Error(result.error || 'Failed to generate report');
            }
            
        } catch (error) {
            console.error('Generation error:', error);
            this.showErrorModal(error.message);
        }
    }
    
    showPreviewLoading() {
        const previewContent = document.getElementById('preview-content');
        const previewActions = document.getElementById('preview-actions');
        
        previewContent.innerHTML = `
            <div class="preview-loading">
                <div class="loading-spinner"></div>
                <h3>Generating Preview...</h3>
                <p>Please wait while we prepare your report preview.</p>
            </div>
        `;
        
        previewActions.style.display = 'none';
    }
    
    showPreview(previewHtml) {
        const previewContent = document.getElementById('preview-content');
        const previewActions = document.getElementById('preview-actions');
        
        previewContent.innerHTML = previewHtml;
        previewActions.style.display = 'flex';
    }
    
    showPreviewError(message) {
        const previewContent = document.getElementById('preview-content');
        const previewActions = document.getElementById('preview-actions');
        
        previewContent.innerHTML = `
            <div class="preview-error">
                <div class="error-icon">❌</div>
                <h3>Preview Error</h3>
                <p>${message}</p>
                <button class="btn btn-primary" onclick="window.organogramPrinting.previewReport()">
                    Try Again
                </button>
            </div>
        `;
        
        previewActions.style.display = 'none';
    }
    
    clearPreview() {
        const previewContent = document.getElementById('preview-content');
        const previewActions = document.getElementById('preview-actions');
        
        previewContent.innerHTML = `
            <div class="preview-placeholder">
                <div class="placeholder-icon">📄</div>
                <h3>No Preview Available</h3>
                <p>Select a structure or party and click "Preview Report" to see a preview of your report.</p>
            </div>
        `;
        
        previewActions.style.display = 'none';
    }
    
    printPreview() {
        const previewContent = document.getElementById('preview-content');
        const printWindow = window.open('', '_blank');
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Organogram Report Preview</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .preview-loading, .preview-error { text-align: center; }
                    @media print {
                        body { margin: 0; }
                    }
                </style>
            </head>
            <body>
                ${previewContent.innerHTML}
            </body>
            </html>
        `);
        
        printWindow.document.close();
        printWindow.print();
    }
    
    downloadPreview() {
        const previewContent = document.getElementById('preview-content');
        
        // Create HTML content
        const htmlContent = `
            <!DOCTYPE html>
            <html>
            <head>
                <title>Organogram Report Preview</title>
                <meta charset="utf-8">
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        margin: 20px; 
                        line-height: 1.6;
                    }
                    .preview-loading, .preview-error { 
                        text-align: center; 
                    }
                    table { 
                        border-collapse: collapse; 
                        width: 100%; 
                        margin: 20px 0;
                    }
                    th, td { 
                        border: 1px solid #ddd; 
                        padding: 8px; 
                        text-align: left;
                    }
                    th { 
                        background-color: #f2f2f2; 
                    }
                </style>
            </head>
            <body>
                ${previewContent.innerHTML}
            </body>
            </html>
        `;
        
        // Create and download file
        const blob = new Blob([htmlContent], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `organogram_preview_${new Date().getTime()}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('Preview downloaded successfully', 'success');
    }
    
    downloadGeneratedReport() {
        if (this.currentDownloadUrl) {
            window.open(this.currentDownloadUrl, '_blank');
            this.closeModal('success-modal');
        }
    }
    
    showLoadingModal() {
        const modal = document.getElementById('loading-modal');
        const progressFill = document.getElementById('progress-fill');
        
        modal.classList.add('show');
        
        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressFill.style.width = progress + '%';
        }, 200);
        
        // Store interval for cleanup
        modal.dataset.progressInterval = interval;
    }
    
    showSuccessModal(message, filename) {
        this.closeModal('loading-modal');
        
        const modal = document.getElementById('success-modal');
        const messageElement = document.getElementById('success-message');
        
        messageElement.textContent = message + (filename ? ` (${filename})` : '');
        modal.classList.add('show');
    }
    
    showErrorModal(message) {
        this.closeModal('loading-modal');
        
        const modal = document.getElementById('error-modal');
        const messageElement = document.getElementById('error-message');
        
        messageElement.textContent = message;
        modal.classList.add('show');
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            
            // Clear progress interval if it exists
            if (modal.dataset.progressInterval) {
                clearInterval(modal.dataset.progressInterval);
                delete modal.dataset.progressInterval;
            }
        }
    }
    
    loadRecentReports() {
        // In a real implementation, this would fetch from the server
        // For now, we'll just update the display with sample data
        const reportsGrid = document.getElementById('recent-reports-grid');
        
        // Sample recent reports data
        const sampleReports = [
            {
                name: 'Structure Report - International Holding',
                time: '2 hours ago',
                format: 'PDF',
                size: '2.3 MB',
                icon: '📄'
            },
            {
                name: 'Party Report - John Smith',
                time: 'yesterday',
                format: 'Excel',
                size: '1.8 MB',
                icon: '📊'
            },
            {
                name: 'Compliance Report - Q4 2024',
                time: '3 days ago',
                format: 'PDF',
                size: '4.1 MB',
                icon: '📋'
            }
        ];
        
        reportsGrid.innerHTML = sampleReports.map(report => `
            <div class="report-item">
                <div class="report-icon">${report.icon}</div>
                <div class="report-info">
                    <h4>${report.name}</h4>
                    <p>Generated ${report.time} • ${report.format} • ${report.size}</p>
                </div>
                <div class="report-actions">
                    <button class="btn-icon-small" title="Download" onclick="window.organogramPrinting.downloadReport('${report.name}')">💾</button>
                    <button class="btn-icon-small" title="Share" onclick="window.organogramPrinting.shareReport('${report.name}')">📤</button>
                    <button class="btn-icon-small" title="Delete" onclick="window.organogramPrinting.deleteReport('${report.name}')">🗑️</button>
                </div>
            </div>
        `).join('');
    }
    
    downloadReport(reportName) {
        this.showNotification(`Downloading ${reportName}...`, 'info');
        // In real implementation, this would trigger actual download
    }
    
    shareReport(reportName) {
        this.showNotification(`Sharing ${reportName}...`, 'info');
        // In real implementation, this would open share dialog
    }
    
    deleteReport(reportName) {
        if (confirm(`Are you sure you want to delete "${reportName}"?`)) {
            this.showNotification(`${reportName} deleted`, 'success');
            this.loadRecentReports();
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '15px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '600',
            zIndex: '9999',
            opacity: '0',
            transform: 'translateX(100%)',
            transition: 'all 0.3s ease'
        });
        
        // Set background color based on type
        const colors = {
            success: '#48bb78',
            error: '#e53e3e',
            warning: '#ed8936',
            info: '#667eea'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after delay
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Quick action functions
function quickStructureReport() {
    const structureSelect = document.getElementById('structure-select');
    if (structureSelect.value) {
        document.getElementById('report-type').value = 'structure';
        document.getElementById('template-select').value = 'professional';
        document.getElementById('format-select').value = 'pdf';
        window.organogramPrinting.generateReport();
    } else {
        window.organogramPrinting.showNotification('Please select a structure first', 'warning');
    }
}

function quickPartyReport() {
    const partySelect = document.getElementById('party-select');
    if (partySelect.value) {
        document.getElementById('report-type').value = 'party';
        document.getElementById('template-select').value = 'professional';
        document.getElementById('format-select').value = 'pdf';
        window.organogramPrinting.generateReport();
    } else {
        window.organogramPrinting.showNotification('Please select a party first', 'warning');
    }
}

function quickComplianceReport() {
    const structureSelect = document.getElementById('structure-select');
    if (structureSelect.value) {
        document.getElementById('report-type').value = 'compliance';
        document.getElementById('template-select').value = 'compliance';
        document.getElementById('format-select').value = 'pdf';
        document.getElementById('include-compliance').checked = true;
        document.getElementById('include-recommendations').checked = true;
        window.organogramPrinting.generateReport();
    } else {
        window.organogramPrinting.showNotification('Please select a structure first', 'warning');
    }
}

function quickDetailedReport() {
    const structureSelect = document.getElementById('structure-select');
    if (structureSelect.value) {
        document.getElementById('report-type').value = 'comprehensive';
        document.getElementById('template-select').value = 'detailed';
        document.getElementById('format-select').value = 'pdf';
        // Check all options for detailed report
        document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(cb => {
            cb.checked = true;
        });
        window.organogramPrinting.generateReport();
    } else {
        window.organogramPrinting.showNotification('Please select a structure first', 'warning');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.organogramPrinting = new OrganogramPrinting();
});

