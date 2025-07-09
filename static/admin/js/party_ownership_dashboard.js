/**
 * Party Ownership Dashboard - Interactive JavaScript
 * Provides comprehensive dashboard functionality for party ownership analysis
 */

class PartyOwnershipDashboard {
    constructor() {
        this.currentParty = null;
        this.currentView = 'overview';
        this.charts = {};
        this.data = {};
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.loadInitialData();
    }
    
    setupEventListeners() {
        // Party selection
        const partySelect = document.getElementById('party-select');
        if (partySelect) {
            partySelect.addEventListener('change', (e) => {
                this.selectParty(e.target.value);
            });
        }
        
        // View type selection
        const viewType = document.getElementById('view-type');
        if (viewType) {
            viewType.addEventListener('change', (e) => {
                this.changeView(e.target.value);
            });
        }
        
        // Date filter
        const dateFilter = document.getElementById('date-filter');
        if (dateFilter) {
            dateFilter.addEventListener('change', (e) => {
                this.applyDateFilter(e.target.value);
            });
        }
        
        // Tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Chart controls
        const chartType = document.getElementById('chart-type');
        if (chartType) {
            chartType.addEventListener('change', (e) => {
                this.updateOwnershipChart(e.target.value);
            });
        }
        
        const chartFilter = document.getElementById('chart-filter');
        if (chartFilter) {
            chartFilter.addEventListener('change', (e) => {
                this.applyChartFilter(e.target.value);
            });
        }
        
        // Timeline controls
        const timelineGranularity = document.getElementById('timeline-granularity');
        if (timelineGranularity) {
            timelineGranularity.addEventListener('change', (e) => {
                this.updateTimelineChart();
            });
        }
        
        const timelineMetric = document.getElementById('timeline-metric');
        if (timelineMetric) {
            timelineMetric.addEventListener('change', (e) => {
                this.updateTimelineChart();
            });
        }
        
        // Export and print buttons
        const exportBtn = document.getElementById('export-party-report-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.showExportModal();
            });
        }
        
        const printBtn = document.getElementById('print-party-dashboard-btn');
        if (printBtn) {
            printBtn.addEventListener('click', () => {
                this.printDashboard();
            });
        }
        
        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(button => {
            button.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.closeModal(modal.id);
            });
        });
        
        // Confirm export button
        const confirmExportBtn = document.getElementById('confirm-export-btn');
        if (confirmExportBtn) {
            confirmExportBtn.addEventListener('click', () => {
                this.exportReport();
            });
        }
        
        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
    }
    
    async selectParty(partyId) {
        if (!partyId) {
            this.currentParty = null;
            this.showEmptyState();
            return;
        }
        
        try {
            this.showLoading();
            
            // Fetch party data
            const response = await fetch(`/admin/corporate/party-dashboard-data/${partyId}/`);
            const data = await response.json();
            
            if (data.success) {
                this.currentParty = partyId;
                this.data = data.data;
                this.updateDashboard();
            } else {
                this.showError('Failed to load party data');
            }
        } catch (error) {
            console.error('Error loading party data:', error);
            this.showError('Error loading party data');
        }
    }
    
    updateDashboard() {
        this.updatePartyInfo();
        this.updateStatistics();
        this.updateCharts();
        this.updateStructures();
        this.updateAnalytics();
        this.updateRecentActivity();
        this.hideLoading();
    }
    
    updatePartyInfo() {
        const data = this.data;
        
        // Update statistics
        document.getElementById('total-structures').textContent = data.stats.total_structures;
        document.getElementById('total-ownership').textContent = data.stats.total_ownership + '%';
        document.getElementById('active-entities').textContent = data.stats.active_entities;
        document.getElementById('jurisdictions-count').textContent = data.stats.jurisdictions_count;
    }
    
    updateStatistics() {
        // Update various statistics displays
        const stats = this.data.stats;
        
        // Update metric values in analytics tab
        if (document.getElementById('avg-ownership')) {
            document.getElementById('avg-ownership').textContent = stats.avg_ownership + '%';
        }
        if (document.getElementById('max-ownership')) {
            document.getElementById('max-ownership').textContent = stats.max_ownership + '%';
        }
        if (document.getElementById('diversification-index')) {
            document.getElementById('diversification-index').textContent = stats.diversification_index;
        }
        if (document.getElementById('complexity-score')) {
            document.getElementById('complexity-score').textContent = stats.complexity_score;
        }
    }
    
    initializeCharts() {
        // Initialize Chart.js charts
        this.initOwnershipPieChart();
        this.initStructureTypesChart();
        this.initJurisdictionChart();
        this.initTimelineChart();
    }
    
    initOwnershipPieChart() {
        const ctx = document.getElementById('ownership-pie-chart');
        if (!ctx) return;
        
        this.charts.ownershipPie = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#667eea', '#764ba2', '#f093fb', '#f5576c',
                        '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    initStructureTypesChart() {
        const ctx = document.getElementById('structure-types-chart');
        if (!ctx) return;
        
        this.charts.structureTypes = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Number of Structures',
                    data: [],
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: '#667eea',
                    borderWidth: 1,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
    
    initJurisdictionChart() {
        const ctx = document.getElementById('jurisdiction-chart');
        if (!ctx) return;
        
        this.charts.jurisdiction = new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(240, 147, 251, 0.8)',
                        'rgba(245, 87, 108, 0.8)',
                        'rgba(79, 172, 254, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
    
    initTimelineChart() {
        const ctx = document.getElementById('timeline-chart');
        if (!ctx) return;
        
        this.charts.timeline = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Ownership Percentage',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    updateCharts() {
        if (!this.data || !this.data.charts) return;
        
        const chartData = this.data.charts;
        
        // Update ownership pie chart
        if (this.charts.ownershipPie && chartData.ownership) {
            this.charts.ownershipPie.data.labels = chartData.ownership.labels;
            this.charts.ownershipPie.data.datasets[0].data = chartData.ownership.data;
            this.charts.ownershipPie.update();
        }
        
        // Update structure types chart
        if (this.charts.structureTypes && chartData.structure_types) {
            this.charts.structureTypes.data.labels = chartData.structure_types.labels;
            this.charts.structureTypes.data.datasets[0].data = chartData.structure_types.data;
            this.charts.structureTypes.update();
        }
        
        // Update jurisdiction chart
        if (this.charts.jurisdiction && chartData.jurisdictions) {
            this.charts.jurisdiction.data.labels = chartData.jurisdictions.labels;
            this.charts.jurisdiction.data.datasets[0].data = chartData.jurisdictions.data;
            this.charts.jurisdiction.update();
        }
        
        // Update timeline chart
        if (this.charts.timeline && chartData.timeline) {
            this.charts.timeline.data.labels = chartData.timeline.labels;
            this.charts.timeline.data.datasets[0].data = chartData.timeline.data;
            this.charts.timeline.update();
        }
    }
    
    updateOwnershipChart(chartType) {
        // Update the ownership visualization based on selected type
        const container = document.getElementById('ownership-visualization');
        if (!container) return;
        
        container.innerHTML = '<div class="loading-spinner">Loading visualization...</div>';
        
        // Simulate loading and render based on chart type
        setTimeout(() => {
            switch (chartType) {
                case 'hierarchy':
                    this.renderHierarchyChart(container);
                    break;
                case 'network':
                    this.renderNetworkChart(container);
                    break;
                case 'sankey':
                    this.renderSankeyChart(container);
                    break;
                case 'sunburst':
                    this.renderSunburstChart(container);
                    break;
                default:
                    this.renderHierarchyChart(container);
            }
        }, 500);
    }
    
    renderHierarchyChart(container) {
        // D3.js hierarchy tree implementation
        container.innerHTML = '';
        
        const width = container.clientWidth;
        const height = 400;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Add placeholder hierarchy visualization
        const g = svg.append('g')
            .attr('transform', 'translate(50, 50)');
        
        // Sample hierarchy data
        const hierarchyData = {
            name: this.data?.party_name || 'Selected Party',
            children: this.data?.structures?.map(s => ({
                name: s.name,
                children: s.entities?.map(e => ({ name: e.name })) || []
            })) || []
        };
        
        const tree = d3.tree().size([width - 100, height - 100]);
        const root = d3.hierarchy(hierarchyData);
        tree(root);
        
        // Draw links
        g.selectAll('.link')
            .data(root.links())
            .enter().append('path')
            .attr('class', 'link')
            .attr('d', d3.linkVertical()
                .x(d => d.x)
                .y(d => d.y))
            .style('fill', 'none')
            .style('stroke', '#667eea')
            .style('stroke-width', 2);
        
        // Draw nodes
        const node = g.selectAll('.node')
            .data(root.descendants())
            .enter().append('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.x},${d.y})`);
        
        node.append('circle')
            .attr('r', 8)
            .style('fill', '#667eea')
            .style('stroke', 'white')
            .style('stroke-width', 2);
        
        node.append('text')
            .attr('dy', -15)
            .attr('text-anchor', 'middle')
            .style('font-size', '12px')
            .style('font-weight', 'bold')
            .text(d => d.data.name);
    }
    
    renderNetworkChart(container) {
        // D3.js force-directed network implementation
        container.innerHTML = '';
        
        const width = container.clientWidth;
        const height = 400;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        // Add network visualization placeholder
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('fill', '#667eea')
            .text('Network Graph Visualization');
    }
    
    renderSankeyChart(container) {
        // Sankey diagram implementation
        container.innerHTML = '';
        
        const width = container.clientWidth;
        const height = 400;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('fill', '#667eea')
            .text('Sankey Diagram Visualization');
    }
    
    renderSunburstChart(container) {
        // Sunburst chart implementation
        container.innerHTML = '';
        
        const width = container.clientWidth;
        const height = 400;
        
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        svg.append('text')
            .attr('x', width / 2)
            .attr('y', height / 2)
            .attr('text-anchor', 'middle')
            .style('font-size', '16px')
            .style('fill', '#667eea')
            .text('Sunburst Chart Visualization');
    }
    
    updateTimelineChart() {
        const granularity = document.getElementById('timeline-granularity')?.value || 'month';
        const metric = document.getElementById('timeline-metric')?.value || 'ownership';
        
        // Update timeline chart based on selected granularity and metric
        if (this.charts.timeline) {
            // Simulate data update
            const labels = this.generateTimelineLabels(granularity);
            const data = this.generateTimelineData(metric, labels.length);
            
            this.charts.timeline.data.labels = labels;
            this.charts.timeline.data.datasets[0].data = data;
            this.charts.timeline.data.datasets[0].label = this.getMetricLabel(metric);
            this.charts.timeline.update();
        }
    }
    
    generateTimelineLabels(granularity) {
        const labels = [];
        const now = new Date();
        const periods = granularity === 'month' ? 12 : granularity === 'quarter' ? 8 : 5;
        
        for (let i = periods - 1; i >= 0; i--) {
            const date = new Date(now);
            if (granularity === 'month') {
                date.setMonth(date.getMonth() - i);
                labels.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
            } else if (granularity === 'quarter') {
                date.setMonth(date.getMonth() - (i * 3));
                labels.push(`Q${Math.floor(date.getMonth() / 3) + 1} ${date.getFullYear()}`);
            } else {
                date.setFullYear(date.getFullYear() - i);
                labels.push(date.getFullYear().toString());
            }
        }
        
        return labels;
    }
    
    generateTimelineData(metric, length) {
        // Generate sample data based on metric type
        const data = [];
        for (let i = 0; i < length; i++) {
            switch (metric) {
                case 'ownership':
                    data.push(Math.random() * 100);
                    break;
                case 'entities':
                    data.push(Math.floor(Math.random() * 20) + 1);
                    break;
                case 'structures':
                    data.push(Math.floor(Math.random() * 10) + 1);
                    break;
                case 'value':
                    data.push(Math.random() * 1000000);
                    break;
                default:
                    data.push(Math.random() * 100);
            }
        }
        return data;
    }
    
    getMetricLabel(metric) {
        const labels = {
            ownership: 'Ownership Percentage',
            entities: 'Number of Entities',
            structures: 'Number of Structures',
            value: 'Portfolio Value'
        };
        return labels[metric] || 'Metric';
    }
    
    updateStructures() {
        // Update structures display if needed
        // This would typically involve updating the structures grid
    }
    
    updateAnalytics() {
        // Update analytics displays
        // Risk indicators, recommendations, compliance status
    }
    
    updateRecentActivity() {
        const activityContainer = document.getElementById('recent-activity');
        if (!activityContainer) return;
        
        // Sample recent activity data
        const activities = [
            { description: 'New entity added to Structure A', date: '2 hours ago' },
            { description: 'Ownership percentage updated', date: '1 day ago' },
            { description: 'Compliance report generated', date: '3 days ago' },
            { description: 'Structure validation completed', date: '1 week ago' }
        ];
        
        activityContainer.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <span class="activity-description">${activity.description}</span>
                <span class="activity-date">${activity.date}</span>
            </div>
        `).join('');
    }
    
    switchTab(tabName) {
        // Hide all tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Remove active class from all tab buttons
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.remove('active');
        });
        
        // Show selected tab pane
        const targetPane = document.getElementById(`${tabName}-tab`);
        if (targetPane) {
            targetPane.classList.add('active');
        }
        
        // Add active class to clicked button
        const targetButton = document.querySelector(`[data-tab="${tabName}"]`);
        if (targetButton) {
            targetButton.classList.add('active');
        }
        
        // Update charts if switching to chart tabs
        if (tabName === 'ownership-chart') {
            setTimeout(() => this.updateOwnershipChart('hierarchy'), 100);
        } else if (tabName === 'timeline') {
            setTimeout(() => this.updateTimelineChart(), 100);
        }
    }
    
    changeView(viewType) {
        this.currentView = viewType;
        // Implement view changes based on type
    }
    
    applyDateFilter(dateRange) {
        // Apply date filtering to data and update displays
        console.log('Applying date filter:', dateRange);
    }
    
    applyChartFilter(filterType) {
        // Apply filtering to ownership chart
        console.log('Applying chart filter:', filterType);
    }
    
    showExportModal() {
        const modal = document.getElementById('export-modal');
        if (modal) {
            modal.classList.add('show');
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
        }
    }
    
    exportReport() {
        const reportType = document.querySelector('input[name="report_type"]:checked')?.value;
        const format = document.querySelector('input[name="export_format"]:checked')?.value;
        const includeCharts = document.querySelector('input[name="include_charts"]')?.checked;
        const includeRawData = document.querySelector('input[name="include_raw_data"]')?.checked;
        const includeRecommendations = document.querySelector('input[name="include_recommendations"]')?.checked;
        const includeCompliance = document.querySelector('input[name="include_compliance"]')?.checked;
        
        const exportData = {
            party_id: this.currentParty,
            report_type: reportType,
            format: format,
            include_charts: includeCharts,
            include_raw_data: includeRawData,
            include_recommendations: includeRecommendations,
            include_compliance: includeCompliance
        };
        
        // Show loading state
        const confirmBtn = document.getElementById('confirm-export-btn');
        const originalText = confirmBtn.textContent;
        confirmBtn.textContent = 'Generating...';
        confirmBtn.disabled = true;
        
        // Simulate export process
        setTimeout(() => {
            this.showNotification('Report generated successfully!', 'success');
            this.closeModal('export-modal');
            
            // Reset button
            confirmBtn.textContent = originalText;
            confirmBtn.disabled = false;
        }, 2000);
    }
    
    printDashboard() {
        window.print();
    }
    
    showLoading() {
        const content = document.getElementById('dashboard-content');
        if (content) {
            content.innerHTML = '<div class="loading-state"><div class="loading-spinner"></div><p>Loading dashboard...</p></div>';
        }
    }
    
    hideLoading() {
        // Loading is hidden when content is updated
    }
    
    showEmptyState() {
        const content = document.getElementById('dashboard-content');
        if (content) {
            content.innerHTML = `
                <div class="empty-dashboard">
                    <div class="empty-content">
                        <div class="empty-icon">👤</div>
                        <h2>Select a Party to View Dashboard</h2>
                        <p>Choose a party from the dropdown above to view their ownership dashboard with detailed analytics and visualizations.</p>
                    </div>
                </div>
            `;
        }
    }
    
    showError(message) {
        this.showNotification(message, 'error');
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
    
    loadInitialData() {
        // Load initial data if party is pre-selected
        const partySelect = document.getElementById('party-select');
        if (partySelect && partySelect.value) {
            this.selectParty(partySelect.value);
        }
    }
}

// Global functions for template usage
function viewStructureDetails(structureId) {
    // Implementation for viewing structure details
    console.log('Viewing structure details for:', structureId);
}

function editStructure(structureId) {
    // Implementation for editing structure
    console.log('Editing structure:', structureId);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.partyDashboard = new PartyOwnershipDashboard();
});

// Add CSS for loading and notification styles
const style = document.createElement('style');
style.textContent = `
    .loading-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 400px;
        color: #718096;
    }
    
    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #e2e8f0;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 20px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .notification {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
`;
document.head.appendChild(style);

