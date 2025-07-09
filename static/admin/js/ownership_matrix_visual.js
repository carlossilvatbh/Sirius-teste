/**
 * Ownership Matrix Visual - Interactive JavaScript
 * Provides comprehensive ownership visualization and management
 */

class OwnershipMatrixVisual {
    constructor() {
        this.currentData = null;
        this.filteredData = null;
        this.networkSimulation = null;
        this.matrixGrid = null;
        this.currentView = 'visual';
        this.selectedStructure = null;
        this.ownershipThreshold = 0;
        this.showParties = true;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadData();
        this.initializeVisualization();
    }
    
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.matrix-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
        
        // Control panel events
        document.getElementById('structure-select').addEventListener('change', (e) => {
            this.selectedStructure = e.target.value;
            this.filterAndUpdateData();
        });
        
        document.getElementById('view-mode').addEventListener('change', (e) => {
            this.currentView = e.target.value;
            this.updateVisualization();
        });
        
        document.getElementById('filter-threshold').addEventListener('input', (e) => {
            this.ownershipThreshold = parseFloat(e.target.value);
            document.getElementById('threshold-value').textContent = `${this.ownershipThreshold}%`;
            this.filterAndUpdateData();
        });
        
        document.getElementById('show-parties').addEventListener('change', (e) => {
            this.showParties = e.target.checked;
            this.filterAndUpdateData();
        });
        
        // Header action buttons
        document.getElementById('create-ownership-btn').addEventListener('click', () => {
            this.openOwnershipModal();
        });
        
        document.getElementById('validate-matrix-btn').addEventListener('click', () => {
            this.validateMatrix();
        });
        
        document.getElementById('export-matrix-btn').addEventListener('click', () => {
            this.openExportModal();
        });
        
        // Modal events
        document.getElementById('save-ownership-btn').addEventListener('click', () => {
            this.saveOwnership();
        });
        
        document.getElementById('confirm-export-btn').addEventListener('click', () => {
            this.exportMatrix();
        });
        
        // Owner type change
        document.getElementById('owner-type').addEventListener('change', (e) => {
            this.updateOwnerSelect(e.target.value);
        });
        
        // Network controls
        document.getElementById('center-network')?.addEventListener('click', () => {
            this.centerNetwork();
        });
        
        document.getElementById('zoom-in')?.addEventListener('click', () => {
            this.zoomNetwork(1.2);
        });
        
        document.getElementById('zoom-out')?.addEventListener('click', () => {
            this.zoomNetwork(0.8);
        });
        
        document.getElementById('reset-positions')?.addEventListener('click', () => {
            this.resetNetworkPositions();
        });
        
        // Modal close events
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
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
    
    async loadData() {
        try {
            const response = await fetch('/admin/corporate/api/ownership-matrix-data/');
            this.currentData = await response.json();
            this.filteredData = { ...this.currentData };
            this.updateStatistics();
            this.updateVisualization();
        } catch (error) {
            console.error('Error loading ownership data:', error);
            this.showNotification('Error loading ownership data', 'error');
        }
    }
    
    filterAndUpdateData() {
        if (!this.currentData) return;
        
        let filtered = { ...this.currentData };
        
        // Filter by structure
        if (this.selectedStructure) {
            filtered.ownerships = filtered.ownerships.filter(o => 
                o.structure_id == this.selectedStructure
            );
        }
        
        // Filter by ownership threshold
        if (this.ownershipThreshold > 0) {
            filtered.ownerships = filtered.ownerships.filter(o => 
                o.ownership_percentage >= this.ownershipThreshold
            );
        }
        
        // Filter parties
        if (!this.showParties) {
            filtered.ownerships = filtered.ownerships.filter(o => 
                !o.owner_ubo_id
            );
        }
        
        this.filteredData = filtered;
        this.updateStatistics();
        this.updateVisualization();
    }
    
    updateStatistics() {
        if (!this.filteredData) return;
        
        const stats = this.calculateStatistics(this.filteredData);
        
        document.getElementById('total-ownerships').textContent = stats.totalOwnerships;
        document.getElementById('entities-count').textContent = stats.entitiesCount;
        document.getElementById('parties-count').textContent = stats.partiesCount;
        
        // Update validation status
        this.updateValidationStatus(stats.validationStatus);
    }
    
    calculateStatistics(data) {
        const ownerships = data.ownerships || [];
        const entities = new Set();
        const parties = new Set();
        
        ownerships.forEach(o => {
            entities.add(o.owned_entity_id);
            if (o.owner_entity_id) entities.add(o.owner_entity_id);
            if (o.owner_ubo_id) parties.add(o.owner_ubo_id);
        });
        
        return {
            totalOwnerships: ownerships.length,
            entitiesCount: entities.size,
            partiesCount: parties.size,
            validationStatus: this.getValidationStatus(ownerships)
        };
    }
    
    getValidationStatus(ownerships) {
        // Simple validation: check if any entity has >100% ownership
        const entityOwnerships = {};
        
        ownerships.forEach(o => {
            if (!entityOwnerships[o.owned_entity_id]) {
                entityOwnerships[o.owned_entity_id] = 0;
            }
            entityOwnerships[o.owned_entity_id] += o.ownership_percentage;
        });
        
        const hasInvalidOwnership = Object.values(entityOwnerships).some(total => total > 100);
        return hasInvalidOwnership ? 'invalid' : 'valid';
    }
    
    updateValidationStatus(status) {
        const statusElement = document.getElementById('validation-status');
        const indicator = statusElement.querySelector('.status-indicator');
        
        indicator.className = `status-indicator ${status}`;
        indicator.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.matrix-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update content
        document.querySelectorAll('.matrix-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        this.currentView = tabName;
        this.updateVisualization();
    }
    
    initializeVisualization() {
        this.initializeMatrixGrid();
        this.initializeNetworkGraph();
    }
    
    updateVisualization() {
        if (!this.filteredData) return;
        
        switch (this.currentView) {
            case 'visual':
                this.updateMatrixGrid();
                break;
            case 'table':
                this.updateTable();
                break;
            case 'network':
                this.updateNetworkGraph();
                break;
        }
    }
    
    initializeMatrixGrid() {
        const container = document.getElementById('ownership-matrix-grid');
        if (!container) return;
        
        // Initialize D3 matrix visualization
        this.matrixGrid = d3.select(container);
    }
    
    updateMatrixGrid() {
        if (!this.matrixGrid || !this.filteredData) return;
        
        const data = this.prepareMatrixData(this.filteredData);
        
        // Clear previous content
        this.matrixGrid.selectAll('*').remove();
        
        // Create matrix visualization
        this.createMatrixVisualization(data);
    }
    
    prepareMatrixData(data) {
        const entities = data.entities || [];
        const parties = data.parties || [];
        const ownerships = data.ownerships || [];
        
        // Create matrix structure
        const allNodes = [...entities, ...parties];
        const matrix = [];
        
        allNodes.forEach((source, i) => {
            allNodes.forEach((target, j) => {
                const ownership = ownerships.find(o => 
                    (o.owner_entity_id == source.id || o.owner_ubo_id == source.id) &&
                    o.owned_entity_id == target.id
                );
                
                matrix.push({
                    source: i,
                    target: j,
                    value: ownership ? ownership.ownership_percentage : 0,
                    ownership: ownership
                });
            });
        });
        
        return { nodes: allNodes, matrix };
    }
    
    createMatrixVisualization(data) {
        const { nodes, matrix } = data;
        const cellSize = 40;
        const margin = { top: 100, right: 50, bottom: 50, left: 100 };
        
        const width = nodes.length * cellSize + margin.left + margin.right;
        const height = nodes.length * cellSize + margin.top + margin.bottom;
        
        const svg = this.matrixGrid
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // Color scale
        const colorScale = d3.scaleSequential(d3.interpolateBlues)
            .domain([0, 100]);
        
        // Create cells
        const cells = g.selectAll('.cell')
            .data(matrix)
            .enter()
            .append('rect')
            .attr('class', 'cell')
            .attr('x', d => (d.target % nodes.length) * cellSize)
            .attr('y', d => Math.floor(d.source) * cellSize)
            .attr('width', cellSize - 1)
            .attr('height', cellSize - 1)
            .attr('fill', d => d.value > 0 ? colorScale(d.value) : '#f8f9fa')
            .attr('stroke', '#e2e8f0')
            .attr('stroke-width', 1)
            .style('cursor', 'pointer')
            .on('mouseover', (event, d) => {
                this.showMatrixTooltip(event, d, nodes);
            })
            .on('mouseout', () => {
                this.hideMatrixTooltip();
            })
            .on('click', (event, d) => {
                if (d.ownership) {
                    this.editOwnership(d.ownership.id);
                }
            });
        
        // Add percentage text for non-zero values
        g.selectAll('.cell-text')
            .data(matrix.filter(d => d.value > 0))
            .enter()
            .append('text')
            .attr('class', 'cell-text')
            .attr('x', d => (d.target % nodes.length) * cellSize + cellSize / 2)
            .attr('y', d => Math.floor(d.source) * cellSize + cellSize / 2)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('font-size', '10px')
            .attr('font-weight', 'bold')
            .attr('fill', d => d.value > 50 ? 'white' : 'black')
            .text(d => `${d.value.toFixed(1)}%`);
        
        // Add row labels
        g.selectAll('.row-label')
            .data(nodes)
            .enter()
            .append('text')
            .attr('class', 'row-label')
            .attr('x', -10)
            .attr('y', (d, i) => i * cellSize + cellSize / 2)
            .attr('text-anchor', 'end')
            .attr('dominant-baseline', 'middle')
            .attr('font-size', '12px')
            .attr('font-weight', '600')
            .text(d => d.name);
        
        // Add column labels
        g.selectAll('.col-label')
            .data(nodes)
            .enter()
            .append('text')
            .attr('class', 'col-label')
            .attr('x', (d, i) => i * cellSize + cellSize / 2)
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('font-size', '12px')
            .attr('font-weight', '600')
            .attr('transform', (d, i) => `rotate(-45, ${i * cellSize + cellSize / 2}, -10)`)
            .text(d => d.name);
    }
    
    showMatrixTooltip(event, d, nodes) {
        if (d.value === 0) return;
        
        const sourceNode = nodes[Math.floor(d.source)];
        const targetNode = nodes[d.target % nodes.length];
        
        const tooltip = d3.select('body')
            .append('div')
            .attr('class', 'matrix-tooltip')
            .style('position', 'absolute')
            .style('background', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('padding', '10px')
            .style('border-radius', '5px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('z-index', '1000');
        
        tooltip.html(`
            <strong>${sourceNode.name}</strong><br>
            owns <strong>${d.value.toFixed(2)}%</strong><br>
            of <strong>${targetNode.name}</strong>
        `);
        
        tooltip
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px');
    }
    
    hideMatrixTooltip() {
        d3.selectAll('.matrix-tooltip').remove();
    }
    
    updateTable() {
        const tbody = document.getElementById('ownership-table-body');
        if (!tbody || !this.filteredData) return;
        
        tbody.innerHTML = '';
        
        this.filteredData.ownerships.forEach(ownership => {
            const row = this.createTableRow(ownership);
            tbody.appendChild(row);
        });
    }
    
    createTableRow(ownership) {
        const row = document.createElement('tr');
        row.dataset.ownershipId = ownership.id;
        
        const ownerName = ownership.owner_entity_name || ownership.owner_ubo_name;
        const ownerType = ownership.owner_entity_id ? 'entity' : 'party';
        
        row.innerHTML = `
            <td class="owner-cell">
                <span class="${ownerType}-badge">${ownerName}</span>
            </td>
            <td class="owned-cell">
                <span class="entity-badge">${ownership.owned_entity_name}</span>
            </td>
            <td class="percentage-cell">
                <span class="percentage-value">${ownership.ownership_percentage.toFixed(2)}%</span>
            </td>
            <td class="structure-cell">
                ${ownership.structure_name ? 
                    `<span class="structure-badge">${ownership.structure_name}</span>` : 
                    '<span class="no-structure">-</span>'
                }
            </td>
            <td class="type-cell">
                <span class="type-badge ${ownerType}">${ownerType.charAt(0).toUpperCase() + ownerType.slice(1)}</span>
            </td>
            <td class="actions-cell">
                <button class="btn-small edit-ownership" data-ownership-id="${ownership.id}">
                    Edit
                </button>
                <button class="btn-small delete-ownership" data-ownership-id="${ownership.id}">
                    Delete
                </button>
            </td>
        `;
        
        // Add event listeners
        row.querySelector('.edit-ownership').addEventListener('click', () => {
            this.editOwnership(ownership.id);
        });
        
        row.querySelector('.delete-ownership').addEventListener('click', () => {
            this.deleteOwnership(ownership.id);
        });
        
        return row;
    }
    
    initializeNetworkGraph() {
        const container = document.getElementById('network-graph');
        if (!container) return;
        
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.networkSvg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        this.networkG = this.networkSvg.append('g');
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on('zoom', (event) => {
                this.networkG.attr('transform', event.transform);
            });
        
        this.networkSvg.call(zoom);
        
        // Initialize simulation
        this.networkSimulation = d3.forceSimulation()
            .force('link', d3.forceLink().id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2));
    }
    
    updateNetworkGraph() {
        if (!this.networkG || !this.filteredData) return;
        
        const data = this.prepareNetworkData(this.filteredData);
        
        // Clear previous content
        this.networkG.selectAll('*').remove();
        
        // Create links
        const links = this.networkG.selectAll('.link')
            .data(data.links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => Math.sqrt(d.value / 10));
        
        // Create nodes
        const nodes = this.networkG.selectAll('.node')
            .data(data.nodes)
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr('r', d => d.type === 'party' ? 8 : 12)
            .attr('fill', d => d.type === 'party' ? '#48bb78' : '#4299e1')
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .call(d3.drag()
                .on('start', (event, d) => this.dragStarted(event, d))
                .on('drag', (event, d) => this.dragged(event, d))
                .on('end', (event, d) => this.dragEnded(event, d))
            );
        
        // Add labels
        const labels = this.networkG.selectAll('.label')
            .data(data.nodes)
            .enter()
            .append('text')
            .attr('class', 'label')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('font-size', '10px')
            .attr('font-weight', '600')
            .attr('fill', '#2d3748')
            .text(d => d.name);
        
        // Update simulation
        this.networkSimulation
            .nodes(data.nodes)
            .on('tick', () => {
                links
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                nodes
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                labels
                    .attr('x', d => d.x)
                    .attr('y', d => d.y + 20);
            });
        
        this.networkSimulation.force('link').links(data.links);
        this.networkSimulation.alpha(1).restart();
    }
    
    prepareNetworkData(data) {
        const entities = data.entities || [];
        const parties = data.parties || [];
        const ownerships = data.ownerships || [];
        
        const nodes = [
            ...entities.map(e => ({ ...e, type: 'entity' })),
            ...parties.map(p => ({ ...p, type: 'party' }))
        ];
        
        const links = ownerships.map(o => ({
            source: o.owner_entity_id || o.owner_ubo_id,
            target: o.owned_entity_id,
            value: o.ownership_percentage,
            ownership: o
        }));
        
        return { nodes, links };
    }
    
    dragStarted(event, d) {
        if (!event.active) this.networkSimulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    dragEnded(event, d) {
        if (!event.active) this.networkSimulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    centerNetwork() {
        if (!this.networkSvg) return;
        
        const width = this.networkSvg.attr('width');
        const height = this.networkSvg.attr('height');
        
        this.networkSvg.transition()
            .duration(750)
            .call(
                d3.zoom().transform,
                d3.zoomIdentity.translate(0, 0).scale(1)
            );
    }
    
    zoomNetwork(scale) {
        if (!this.networkSvg) return;
        
        this.networkSvg.transition()
            .duration(300)
            .call(
                d3.zoom().scaleBy,
                scale
            );
    }
    
    resetNetworkPositions() {
        if (!this.networkSimulation) return;
        
        this.networkSimulation.alpha(1).restart();
    }
    
    openOwnershipModal(ownershipId = null) {
        const modal = document.getElementById('ownership-modal');
        const title = document.getElementById('ownership-modal-title');
        const form = document.getElementById('ownership-form');
        
        if (ownershipId) {
            title.textContent = 'Edit Ownership Relationship';
            this.loadOwnershipData(ownershipId);
        } else {
            title.textContent = 'Create Ownership Relationship';
            form.reset();
        }
        
        modal.style.display = 'block';
    }
    
    async loadOwnershipData(ownershipId) {
        try {
            const response = await fetch(`/admin/corporate/api/ownership/${ownershipId}/`);
            const ownership = await response.json();
            
            // Populate form with ownership data
            document.getElementById('owner-type').value = ownership.owner_entity_id ? 'entity' : 'party';
            this.updateOwnerSelect(ownership.owner_entity_id ? 'entity' : 'party');
            document.getElementById('owner-select').value = ownership.owner_entity_id || ownership.owner_ubo_id;
            document.getElementById('owned-entity').value = ownership.owned_entity_id;
            document.getElementById('ownership-percentage').value = ownership.ownership_percentage;
            document.getElementById('structure-select-modal').value = ownership.structure_id || '';
            document.getElementById('ownership-notes').value = ownership.notes || '';
            
        } catch (error) {
            console.error('Error loading ownership data:', error);
            this.showNotification('Error loading ownership data', 'error');
        }
    }
    
    updateOwnerSelect(ownerType) {
        const ownerSelect = document.getElementById('owner-select');
        ownerSelect.innerHTML = '<option value="">Select Owner</option>';
        
        if (!this.currentData) return;
        
        const options = ownerType === 'entity' ? this.currentData.entities : this.currentData.parties;
        
        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option.id;
            optionElement.textContent = `${option.name} ${ownerType === 'entity' ? `(${option.entity_type})` : ''}`;
            ownerSelect.appendChild(optionElement);
        });
    }
    
    async saveOwnership() {
        const form = document.getElementById('ownership-form');
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/admin/corporate/api/ownership/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                this.closeModal('ownership-modal');
                this.loadData(); // Reload data
                this.showNotification('Ownership saved successfully', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.message || 'Error saving ownership', 'error');
            }
        } catch (error) {
            console.error('Error saving ownership:', error);
            this.showNotification('Error saving ownership', 'error');
        }
    }
    
    editOwnership(ownershipId) {
        this.openOwnershipModal(ownershipId);
    }
    
    async deleteOwnership(ownershipId) {
        if (!confirm('Are you sure you want to delete this ownership relationship?')) {
            return;
        }
        
        try {
            const response = await fetch(`/admin/corporate/api/ownership/${ownershipId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                this.loadData(); // Reload data
                this.showNotification('Ownership deleted successfully', 'success');
            } else {
                this.showNotification('Error deleting ownership', 'error');
            }
        } catch (error) {
            console.error('Error deleting ownership:', error);
            this.showNotification('Error deleting ownership', 'error');
        }
    }
    
    async validateMatrix() {
        try {
            const response = await fetch('/admin/corporate/api/validate-ownership-matrix/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    structure_id: this.selectedStructure
                })
            });
            
            const results = await response.json();
            this.showValidationResults(results);
            
        } catch (error) {
            console.error('Error validating matrix:', error);
            this.showNotification('Error validating matrix', 'error');
        }
    }
    
    showValidationResults(results) {
        const modal = document.getElementById('validation-modal');
        const resultsContainer = document.getElementById('validation-results');
        
        resultsContainer.innerHTML = '';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = `validation-item ${result.type}`;
            item.innerHTML = `
                <h4>${result.title}</h4>
                <p>${result.message}</p>
            `;
            resultsContainer.appendChild(item);
        });
        
        modal.style.display = 'block';
    }
    
    openExportModal() {
        const modal = document.getElementById('export-modal');
        modal.style.display = 'block';
    }
    
    async exportMatrix() {
        const format = document.querySelector('input[name="export_format"]:checked').value;
        const includeParties = document.getElementById('include-parties').checked;
        const includeZeroOwnership = document.getElementById('include-zero-ownership').checked;
        const includeMetadata = document.getElementById('include-metadata').checked;
        
        try {
            const response = await fetch('/admin/corporate/api/export-ownership-matrix/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    format,
                    structure_id: this.selectedStructure,
                    include_parties: includeParties,
                    include_zero_ownership: includeZeroOwnership,
                    include_metadata: includeMetadata
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `ownership_matrix.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.closeModal('export-modal');
                this.showNotification('Matrix exported successfully', 'success');
            } else {
                this.showNotification('Error exporting matrix', 'error');
            }
        } catch (error) {
            console.error('Error exporting matrix:', error);
            this.showNotification('Error exporting matrix', 'error');
        }
    }
    
    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.style.display = 'none';
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
            zIndex: '10000',
            opacity: '0',
            transform: 'translateX(100%)',
            transition: 'all 0.3s ease'
        });
        
        // Set background color based on type
        const colors = {
            success: '#48bb78',
            error: '#f56565',
            warning: '#ed8936',
            info: '#4299e1'
        };
        notification.style.background = colors[type] || colors.info;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new OwnershipMatrixVisual();
});

// Global functions for modal management
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

