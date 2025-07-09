/**
 * Organogram Builder - Interactive Corporate Structure Builder
 * Implements drag & drop, hierarchical visualization, and real-time validation
 */

class OrganogramBuilder {
    constructor() {
        this.svg = null;
        this.mainGroup = null;
        this.nodesLayer = null;
        this.connectionsLayer = null;
        
        this.nodes = new Map();
        this.connections = new Map();
        this.selectedNode = null;
        this.selectedConnection = null;
        
        this.zoom = null;
        this.simulation = null;
        
        this.isDragging = false;
        this.isPanning = false;
        
        // Configuration
        this.config = {
            nodeWidth: 160,
            nodeHeight: 80,
            levelHeight: 150,
            nodeSpacing: 200,
            colors: {
                entity: '#667eea',
                party: '#f093fb',
                selected: '#28a745',
                connection: '#666'
            }
        };
        
        // Bind methods
        this.handleDragStart = this.handleDragStart.bind(this);
        this.handleDragOver = this.handleDragOver.bind(this);
        this.handleDrop = this.handleDrop.bind(this);
        this.handleNodeClick = this.handleNodeClick.bind(this);
        this.handleConnectionClick = this.handleConnectionClick.bind(this);
    }
    
    init() {
        this.initializeSVG();
        this.initializeLibrary();
        this.initializeEventListeners();
        this.loadOrganogramData();
        this.updateStatusBar();
    }
    
    initializeSVG() {
        this.svg = d3.select('#organogram-svg');
        this.mainGroup = this.svg.select('#main-group');
        this.nodesLayer = this.svg.select('#nodes-layer');
        this.connectionsLayer = this.svg.select('#connections-layer');
        
        // Initialize zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on('zoom', (event) => {
                this.mainGroup.attr('transform', event.transform);
            })
            .on('start', () => {
                this.isPanning = true;
                this.svg.classed('panning', true);
            })
            .on('end', () => {
                this.isPanning = false;
                this.svg.classed('panning', false);
            });
        
        this.svg.call(this.zoom);
        
        // Prevent default drag behavior on SVG
        this.svg.on('dragover', (event) => {
            event.preventDefault();
        });
        
        this.svg.on('drop', (event) => {
            event.preventDefault();
            this.handleCanvasDrop(event);
        });
    }
    
    initializeLibrary() {
        // Initialize drag and drop for library items
        const libraryItems = document.querySelectorAll('.library-item');
        libraryItems.forEach(item => {
            item.draggable = true;
            item.addEventListener('dragstart', this.handleDragStart);
        });
        
        // Initialize library tabs
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchLibraryTab(btn.dataset.tab);
            });
        });
        
        // Initialize search
        const searchInput = document.getElementById('library-search');
        searchInput.addEventListener('input', (e) => {
            this.filterLibraryItems(e.target.value);
        });
        
        // Initialize add to organogram buttons
        const addButtons = document.querySelectorAll('.add-to-organogram');
        addButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const item = e.target.closest('.library-item');
                this.addItemToOrganogram(item);
            });
        });
    }
    
    initializeEventListeners() {
        // Header buttons
        document.getElementById('save-btn').addEventListener('click', () => {
            this.saveOrganogram();
        });
        
        document.getElementById('validate-btn').addEventListener('click', () => {
            this.validateStructure();
        });
        
        document.getElementById('print-btn').addEventListener('click', () => {
            this.printOrganogram();
        });
        
        // Canvas tools
        document.getElementById('zoom-in-btn').addEventListener('click', () => {
            this.zoomIn();
        });
        
        document.getElementById('zoom-out-btn').addEventListener('click', () => {
            this.zoomOut();
        });
        
        document.getElementById('fit-to-screen-btn').addEventListener('click', () => {
            this.fitToScreen();
        });
        
        document.getElementById('auto-layout-btn').addEventListener('click', () => {
            this.autoLayout();
        });
        
        document.getElementById('clear-canvas-btn').addEventListener('click', () => {
            this.clearCanvas();
        });
        
        // Modal handlers
        this.initializeModals();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    }
    
    initializeModals() {
        // Modal close buttons
        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                this.closeModal(modal.id);
            });
        });
        
        // Click outside to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
        
        // Add entity form
        document.getElementById('add-entity-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createNewEntity();
        });
        
        // Connection form
        document.getElementById('connection-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveConnectionProperties();
        });
    }
    
    loadOrganogramData() {
        if (window.organogramData && window.organogramData.nodes) {
            const data = window.organogramData;
            
            // Load nodes
            data.nodes.forEach(nodeData => {
                this.createNode(nodeData);
            });
            
            // Load connections
            data.edges.forEach(edgeData => {
                this.createConnection(edgeData);
            });
            
            // Auto layout if nodes exist
            if (data.nodes.length > 0) {
                setTimeout(() => {
                    this.autoLayout();
                }, 100);
            }
        }
    }
    
    handleDragStart(event) {
        const item = event.target.closest('.library-item');
        if (!item) return;
        
        const data = {
            type: item.dataset.type,
            id: item.dataset.id,
            name: item.dataset.name,
            entityType: item.dataset.entityType,
            jurisdiction: item.dataset.jurisdiction,
            nationality: item.dataset.nationality,
            totalShares: item.dataset.totalShares
        };
        
        event.dataTransfer.setData('application/json', JSON.stringify(data));
        event.dataTransfer.effectAllowed = 'copy';
        
        item.classList.add('dragging');
        
        // Show drop zone
        document.getElementById('drop-zone').style.display = 'flex';
    }
    
    handleDragOver(event) {
        event.preventDefault();
        event.dataTransfer.dropEffect = 'copy';
    }
    
    handleDrop(event) {
        event.preventDefault();
        this.handleCanvasDrop(event);
    }
    
    handleCanvasDrop(event) {
        // Hide drop zone
        document.getElementById('drop-zone').style.display = 'none';
        
        // Remove dragging class from all items
        document.querySelectorAll('.library-item.dragging').forEach(item => {
            item.classList.remove('dragging');
        });
        
        try {
            const data = JSON.parse(event.dataTransfer.getData('application/json'));
            if (data) {
                this.addItemToCanvas(data, event);
            }
        } catch (e) {
            console.error('Error parsing drop data:', e);
        }
    }
    
    addItemToCanvas(data, event) {
        // Get drop position relative to SVG
        const svgRect = this.svg.node().getBoundingClientRect();
        const transform = d3.zoomTransform(this.svg.node());
        
        const x = (event.clientX - svgRect.left - transform.x) / transform.k;
        const y = (event.clientY - svgRect.top - transform.y) / transform.k;
        
        // Create node data
        const nodeData = {
            id: `${data.type}_${data.id}`,
            type: data.type,
            name: data.name,
            x: x,
            y: y,
            level: 0
        };
        
        if (data.type === 'entity') {
            nodeData.entity_type = data.entityType;
            nodeData.jurisdiction = data.jurisdiction;
            nodeData.total_shares = data.totalShares;
        } else if (data.type === 'party') {
            nodeData.nationality = data.nationality;
        }
        
        this.createNode(nodeData);
        this.updateStatusBar();
        this.setStatus('Node added to organogram');
    }
    
    addItemToOrganogram(item) {
        const data = {
            type: item.dataset.type,
            id: item.dataset.id,
            name: item.dataset.name,
            entityType: item.dataset.entityType,
            jurisdiction: item.dataset.jurisdiction,
            nationality: item.dataset.nationality,
            totalShares: item.dataset.totalShares
        };
        
        // Add to center of canvas
        const svgRect = this.svg.node().getBoundingClientRect();
        const centerX = svgRect.width / 2;
        const centerY = svgRect.height / 2;
        
        const event = {
            clientX: svgRect.left + centerX,
            clientY: svgRect.top + centerY
        };
        
        this.addItemToCanvas(data, event);
    }
    
    createNode(nodeData) {
        if (this.nodes.has(nodeData.id)) {
            console.warn('Node already exists:', nodeData.id);
            return;
        }
        
        const node = this.nodesLayer.append('g')
            .attr('class', 'node')
            .attr('transform', `translate(${nodeData.x || 0}, ${nodeData.y || 0})`)
            .style('cursor', 'pointer')
            .on('click', (event) => {
                event.stopPropagation();
                this.handleNodeClick(nodeData.id);
            });
        
        // Node background
        const rect = node.append('rect')
            .attr('width', this.config.nodeWidth)
            .attr('height', this.config.nodeHeight)
            .attr('rx', 12)
            .attr('ry', 12)
            .attr('class', `node-${nodeData.type}`)
            .style('filter', 'drop-shadow(0 2px 8px rgba(0,0,0,0.15))');
        
        // Node icon
        node.append('text')
            .attr('class', 'node-icon')
            .attr('x', this.config.nodeWidth / 2)
            .attr('y', 25)
            .text(this.getNodeIcon(nodeData));
        
        // Node name
        node.append('text')
            .attr('class', 'node-text')
            .attr('x', this.config.nodeWidth / 2)
            .attr('y', 45)
            .style('font-size', '12px')
            .text(this.truncateText(nodeData.name, 18));
        
        // Node details
        const details = this.getNodeDetails(nodeData);
        if (details) {
            node.append('text')
                .attr('class', 'node-details')
                .attr('x', this.config.nodeWidth / 2)
                .attr('y', 60)
                .text(details);
        }
        
        // Make node draggable
        this.makeDraggable(node, nodeData.id);
        
        // Store node data
        this.nodes.set(nodeData.id, {
            ...nodeData,
            element: node
        });
    }
    
    createConnection(edgeData) {
        const connectionId = edgeData.id || `${edgeData.source}_${edgeData.target}`;
        
        if (this.connections.has(connectionId)) {
            console.warn('Connection already exists:', connectionId);
            return;
        }
        
        const sourceNode = this.nodes.get(edgeData.source);
        const targetNode = this.nodes.get(edgeData.target);
        
        if (!sourceNode || !targetNode) {
            console.warn('Source or target node not found for connection:', edgeData);
            return;
        }
        
        const connection = this.connectionsLayer.append('g')
            .attr('class', 'connection-group')
            .style('cursor', 'pointer')
            .on('click', (event) => {
                event.stopPropagation();
                this.handleConnectionClick(connectionId);
            });
        
        // Connection path
        const path = connection.append('path')
            .attr('class', 'connection')
            .attr('d', this.calculateConnectionPath(sourceNode, targetNode));
        
        // Connection label background
        const labelBg = connection.append('rect')
            .attr('class', 'connection-background')
            .attr('width', 50)
            .attr('height', 20)
            .attr('x', -25)
            .attr('y', -10);
        
        // Connection label
        const label = connection.append('text')
            .attr('class', 'connection-label')
            .text(`${edgeData.percentage || 0}%`);
        
        // Position label at midpoint
        this.updateConnectionLabel(connection, sourceNode, targetNode);
        
        // Store connection data
        this.connections.set(connectionId, {
            ...edgeData,
            element: connection,
            source: edgeData.source,
            target: edgeData.target
        });
    }
    
    calculateConnectionPath(sourceNode, targetNode) {
        const sourceX = sourceNode.x + this.config.nodeWidth / 2;
        const sourceY = sourceNode.y + this.config.nodeHeight;
        const targetX = targetNode.x + this.config.nodeWidth / 2;
        const targetY = targetNode.y;
        
        const midY = (sourceY + targetY) / 2;
        
        return `M ${sourceX} ${sourceY} 
                C ${sourceX} ${midY}, ${targetX} ${midY}, ${targetX} ${targetY}`;
    }
    
    updateConnectionLabel(connection, sourceNode, targetNode) {
        const sourceX = sourceNode.x + this.config.nodeWidth / 2;
        const sourceY = sourceNode.y + this.config.nodeHeight;
        const targetX = targetNode.x + this.config.nodeWidth / 2;
        const targetY = targetNode.y;
        
        const midX = (sourceX + targetX) / 2;
        const midY = (sourceY + targetY) / 2;
        
        connection.select('.connection-background')
            .attr('transform', `translate(${midX}, ${midY})`);
        
        connection.select('.connection-label')
            .attr('transform', `translate(${midX}, ${midY})`);
    }
    
    makeDraggable(nodeElement, nodeId) {
        const drag = d3.drag()
            .on('start', (event) => {
                this.isDragging = true;
                nodeElement.classed('dragging', true);
                this.selectNode(nodeId);
            })
            .on('drag', (event) => {
                const nodeData = this.nodes.get(nodeId);
                nodeData.x = event.x;
                nodeData.y = event.y;
                
                nodeElement.attr('transform', `translate(${event.x}, ${event.y})`);
                
                // Update connections
                this.updateNodeConnections(nodeId);
            })
            .on('end', (event) => {
                this.isDragging = false;
                nodeElement.classed('dragging', false);
            });
        
        nodeElement.call(drag);
    }
    
    updateNodeConnections(nodeId) {
        this.connections.forEach((connection, connectionId) => {
            if (connection.source === nodeId || connection.target === nodeId) {
                const sourceNode = this.nodes.get(connection.source);
                const targetNode = this.nodes.get(connection.target);
                
                if (sourceNode && targetNode) {
                    const path = this.calculateConnectionPath(sourceNode, targetNode);
                    connection.element.select('.connection').attr('d', path);
                    this.updateConnectionLabel(connection.element, sourceNode, targetNode);
                }
            }
        });
    }
    
    handleNodeClick(nodeId) {
        if (this.isDragging) return;
        
        this.selectNode(nodeId);
        this.showNodeProperties(nodeId);
    }
    
    handleConnectionClick(connectionId) {
        if (this.isDragging) return;
        
        this.selectConnection(connectionId);
        this.showConnectionProperties(connectionId);
    }
    
    selectNode(nodeId) {
        // Clear previous selections
        this.clearSelections();
        
        this.selectedNode = nodeId;
        const nodeData = this.nodes.get(nodeId);
        if (nodeData) {
            nodeData.element.classed('selected', true);
        }
    }
    
    selectConnection(connectionId) {
        // Clear previous selections
        this.clearSelections();
        
        this.selectedConnection = connectionId;
        const connectionData = this.connections.get(connectionId);
        if (connectionData) {
            connectionData.element.select('.connection').classed('selected', true);
        }
    }
    
    clearSelections() {
        this.selectedNode = null;
        this.selectedConnection = null;
        
        this.nodesLayer.selectAll('.node').classed('selected', false);
        this.connectionsLayer.selectAll('.connection').classed('selected', false);
        
        this.hideProperties();
    }
    
    showNodeProperties(nodeId) {
        const nodeData = this.nodes.get(nodeId);
        if (!nodeData) return;
        
        const propertiesContent = document.getElementById('properties-content');
        
        let html = `
            <div class="property-section">
                <h4>${this.getNodeIcon(nodeData)} ${nodeData.name}</h4>
                <div class="property-item">
                    <label>Type:</label>
                    <span>${nodeData.type === 'entity' ? 'Entity' : 'Party'}</span>
                </div>
        `;
        
        if (nodeData.type === 'entity') {
            html += `
                <div class="property-item">
                    <label>Entity Type:</label>
                    <span>${nodeData.entity_type || 'N/A'}</span>
                </div>
                <div class="property-item">
                    <label>Jurisdiction:</label>
                    <span>${nodeData.jurisdiction || 'N/A'}</span>
                </div>
                <div class="property-item">
                    <label>Total Shares:</label>
                    <span>${nodeData.total_shares || 'N/A'}</span>
                </div>
            `;
        } else {
            html += `
                <div class="property-item">
                    <label>Nationality:</label>
                    <span>${nodeData.nationality || 'N/A'}</span>
                </div>
            `;
        }
        
        html += `
                <div class="property-actions">
                    <button class="btn btn-sm btn-danger" onclick="organogramBuilder.deleteNode('${nodeId}')">
                        🗑️ Delete
                    </button>
                </div>
            </div>
        `;
        
        propertiesContent.innerHTML = html;
    }
    
    showConnectionProperties(connectionId) {
        const connectionData = this.connections.get(connectionId);
        if (!connectionData) return;
        
        // Show connection modal for editing
        this.openModal('connection-modal');
        
        // Populate form
        document.getElementById('ownership-percentage').value = connectionData.percentage || '';
        document.getElementById('ownership-shares').value = connectionData.shares || '';
        document.getElementById('corporate-name').value = connectionData.corporate_name || '';
        document.getElementById('hash-number').value = connectionData.hash_number || '';
        document.getElementById('share-value-usd').value = connectionData.share_value_usd || '';
        document.getElementById('share-value-eur').value = connectionData.share_value_eur || '';
        
        // Store current connection ID for saving
        document.getElementById('connection-form').dataset.connectionId = connectionId;
    }
    
    saveConnectionProperties() {
        const form = document.getElementById('connection-form');
        const connectionId = form.dataset.connectionId;
        
        if (!connectionId) return;
        
        const connectionData = this.connections.get(connectionId);
        if (!connectionData) return;
        
        // Update connection data
        connectionData.percentage = parseFloat(document.getElementById('ownership-percentage').value) || 0;
        connectionData.shares = parseInt(document.getElementById('ownership-shares').value) || null;
        connectionData.corporate_name = document.getElementById('corporate-name').value;
        connectionData.hash_number = document.getElementById('hash-number').value;
        connectionData.share_value_usd = parseFloat(document.getElementById('share-value-usd').value) || null;
        connectionData.share_value_eur = parseFloat(document.getElementById('share-value-eur').value) || null;
        
        // Update visual
        connectionData.element.select('.connection-label')
            .text(`${connectionData.percentage}%`);
        
        this.closeModal('connection-modal');
        this.setStatus('Connection properties updated');
    }
    
    hideProperties() {
        const propertiesContent = document.getElementById('properties-content');
        propertiesContent.innerHTML = `
            <div class="no-selection">
                <div class="no-selection-icon">👆</div>
                <div class="no-selection-text">Select a node or connection to edit properties</div>
            </div>
        `;
    }
    
    deleteNode(nodeId) {
        if (!confirm('Are you sure you want to delete this node?')) return;
        
        // Delete connections involving this node
        const connectionsToDelete = [];
        this.connections.forEach((connection, connectionId) => {
            if (connection.source === nodeId || connection.target === nodeId) {
                connectionsToDelete.push(connectionId);
            }
        });
        
        connectionsToDelete.forEach(connectionId => {
            this.deleteConnection(connectionId);
        });
        
        // Delete node
        const nodeData = this.nodes.get(nodeId);
        if (nodeData) {
            nodeData.element.remove();
            this.nodes.delete(nodeId);
        }
        
        this.clearSelections();
        this.updateStatusBar();
        this.setStatus('Node deleted');
    }
    
    deleteConnection(connectionId) {
        const connectionData = this.connections.get(connectionId);
        if (connectionData) {
            connectionData.element.remove();
            this.connections.delete(connectionId);
        }
    }
    
    switchLibraryTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        
        // Update tab content
        document.querySelectorAll('.library-content').forEach(content => {
            content.style.display = content.id === `${tabName}-tab` ? 'block' : 'none';
        });
    }
    
    filterLibraryItems(searchTerm) {
        const term = searchTerm.toLowerCase();
        
        document.querySelectorAll('.library-item').forEach(item => {
            const name = item.dataset.name.toLowerCase();
            const type = (item.dataset.entityType || item.dataset.nationality || '').toLowerCase();
            const jurisdiction = (item.dataset.jurisdiction || '').toLowerCase();
            
            const matches = name.includes(term) || type.includes(term) || jurisdiction.includes(term);
            item.style.display = matches ? 'flex' : 'none';
        });
    }
    
    autoLayout() {
        if (this.nodes.size === 0) return;
        
        this.setStatus('Applying auto layout...');
        
        // Calculate hierarchy levels
        const levels = this.calculateHierarchyLevels();
        
        // Position nodes by level
        levels.forEach((nodeIds, level) => {
            const y = 100 + level * this.config.levelHeight;
            const totalWidth = nodeIds.length * this.config.nodeSpacing;
            const startX = -totalWidth / 2;
            
            nodeIds.forEach((nodeId, index) => {
                const nodeData = this.nodes.get(nodeId);
                if (nodeData) {
                    nodeData.x = startX + index * this.config.nodeSpacing;
                    nodeData.y = y;
                    nodeData.level = level;
                    
                    // Animate to new position
                    nodeData.element
                        .transition()
                        .duration(500)
                        .attr('transform', `translate(${nodeData.x}, ${nodeData.y})`);
                }
            });
        });
        
        // Update connections after layout
        setTimeout(() => {
            this.connections.forEach((connection, connectionId) => {
                this.updateNodeConnections(connection.source);
            });
            this.fitToScreen();
            this.setStatus('Auto layout applied');
        }, 600);
    }
    
    calculateHierarchyLevels() {
        const levels = new Map();
        const visited = new Set();
        
        // Find root nodes (nodes with no incoming connections)
        const hasIncoming = new Set();
        this.connections.forEach(connection => {
            hasIncoming.add(connection.target);
        });
        
        const rootNodes = Array.from(this.nodes.keys()).filter(nodeId => !hasIncoming.has(nodeId));
        
        // BFS to assign levels
        const queue = rootNodes.map(nodeId => ({ nodeId, level: 0 }));
        
        while (queue.length > 0) {
            const { nodeId, level } = queue.shift();
            
            if (visited.has(nodeId)) continue;
            visited.add(nodeId);
            
            if (!levels.has(level)) {
                levels.set(level, []);
            }
            levels.get(level).push(nodeId);
            
            // Add children to queue
            this.connections.forEach(connection => {
                if (connection.source === nodeId && !visited.has(connection.target)) {
                    queue.push({ nodeId: connection.target, level: level + 1 });
                }
            });
        }
        
        // Add orphaned nodes to level 0
        this.nodes.forEach((nodeData, nodeId) => {
            if (!visited.has(nodeId)) {
                if (!levels.has(0)) {
                    levels.set(0, []);
                }
                levels.get(0).push(nodeId);
            }
        });
        
        return levels;
    }
    
    fitToScreen() {
        if (this.nodes.size === 0) return;
        
        // Calculate bounds
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
        
        this.nodes.forEach(nodeData => {
            minX = Math.min(minX, nodeData.x);
            minY = Math.min(minY, nodeData.y);
            maxX = Math.max(maxX, nodeData.x + this.config.nodeWidth);
            maxY = Math.max(maxY, nodeData.y + this.config.nodeHeight);
        });
        
        const width = maxX - minX;
        const height = maxY - minY;
        const centerX = minX + width / 2;
        const centerY = minY + height / 2;
        
        // Calculate scale to fit
        const svgRect = this.svg.node().getBoundingClientRect();
        const scaleX = (svgRect.width * 0.8) / width;
        const scaleY = (svgRect.height * 0.8) / height;
        const scale = Math.min(scaleX, scaleY, 1);
        
        // Apply transform
        const transform = d3.zoomIdentity
            .translate(svgRect.width / 2, svgRect.height / 2)
            .scale(scale)
            .translate(-centerX, -centerY);
        
        this.svg.transition()
            .duration(500)
            .call(this.zoom.transform, transform);
    }
    
    zoomIn() {
        this.svg.transition()
            .duration(200)
            .call(this.zoom.scaleBy, 1.5);
    }
    
    zoomOut() {
        this.svg.transition()
            .duration(200)
            .call(this.zoom.scaleBy, 1 / 1.5);
    }
    
    clearCanvas() {
        if (!confirm('Are you sure you want to clear the entire organogram?')) return;
        
        this.nodes.clear();
        this.connections.clear();
        this.nodesLayer.selectAll('*').remove();
        this.connectionsLayer.selectAll('*').remove();
        
        this.clearSelections();
        this.updateStatusBar();
        this.setStatus('Canvas cleared');
    }
    
    saveOrganogram() {
        if (!window.structureId) {
            alert('No structure ID found. Please save the structure first.');
            return;
        }
        
        this.setStatus('Saving organogram...');
        document.getElementById('loading-indicator').style.display = 'flex';
        
        const data = {
            structure_id: window.structureId,
            nodes: Array.from(this.nodes.values()).map(node => ({
                id: node.id,
                type: node.type,
                name: node.name,
                x: node.x,
                y: node.y,
                level: node.level,
                entity_type: node.entity_type,
                jurisdiction: node.jurisdiction,
                total_shares: node.total_shares,
                nationality: node.nationality
            })),
            edges: Array.from(this.connections.values()).map(connection => ({
                id: connection.id,
                source: connection.source,
                target: connection.target,
                percentage: connection.percentage,
                shares: connection.shares,
                corporate_name: connection.corporate_name,
                hash_number: connection.hash_number,
                share_value_usd: connection.share_value_usd,
                share_value_eur: connection.share_value_eur
            }))
        };
        
        fetch('/admin/corporate/structure/api/save-organogram/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            document.getElementById('loading-indicator').style.display = 'none';
            
            if (result.success) {
                this.setStatus('Organogram saved successfully');
                // Show success message
                alert('Organogram saved successfully!');
            } else {
                this.setStatus('Error saving organogram');
                alert('Error saving organogram: ' + result.error);
            }
        })
        .catch(error => {
            document.getElementById('loading-indicator').style.display = 'none';
            this.setStatus('Error saving organogram');
            console.error('Error:', error);
            alert('Error saving organogram: ' + error.message);
        });
    }
    
    validateStructure() {
        if (!window.structureId) {
            alert('No structure ID found.');
            return;
        }
        
        this.setStatus('Validating structure...');
        
        fetch(`/admin/corporate/structure/api/validate-structure/${window.structureId}/`)
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.showValidationResults(result.validation_results);
                this.setStatus('Validation completed');
            } else {
                alert('Error validating structure: ' + result.error);
                this.setStatus('Validation failed');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error validating structure: ' + error.message);
            this.setStatus('Validation failed');
        });
    }
    
    showValidationResults(results) {
        const modal = document.getElementById('validation-modal');
        const resultsDiv = document.getElementById('validation-results');
        
        let html = `
            <div class="validation-status ${results.overall_status}">
                Overall Status: ${results.overall_status.toUpperCase()}
            </div>
        `;
        
        if (results.issues && results.issues.length > 0) {
            html += `
                <div class="validation-section">
                    <h4>❌ Issues</h4>
                    ${results.issues.map(issue => `
                        <div class="validation-item error">${issue}</div>
                    `).join('')}
                </div>
            `;
        }
        
        if (results.warnings && results.warnings.length > 0) {
            html += `
                <div class="validation-section">
                    <h4>⚠️ Warnings</h4>
                    ${results.warnings.map(warning => `
                        <div class="validation-item warning">${warning}</div>
                    `).join('')}
                </div>
            `;
        }
        
        if (results.ownership_totals) {
            html += `
                <div class="validation-section">
                    <h4>📊 Ownership Totals</h4>
                    ${Object.values(results.ownership_totals).map(entity => `
                        <div class="validation-item ${entity.status === 'valid' ? 'info' : 'error'}">
                            ${entity.entity_name}: ${entity.total_percentage}%
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        resultsDiv.innerHTML = html;
        this.openModal('validation-modal');
    }
    
    printOrganogram() {
        window.print();
    }
    
    createNewEntity() {
        const form = document.getElementById('add-entity-form');
        const formData = new FormData(form);
        
        // Here you would typically send the data to the server
        // For now, we'll just add it to the library
        
        const entityData = {
            id: Date.now(), // Temporary ID
            name: formData.get('name'),
            entity_type: formData.get('entity_type'),
            jurisdiction: formData.get('jurisdiction'),
            total_shares: formData.get('total_shares')
        };
        
        // Add to library (this would typically be done on the server)
        this.addEntityToLibrary(entityData);
        
        this.closeModal('add-entity-modal');
        form.reset();
        this.setStatus('New entity created');
    }
    
    addEntityToLibrary(entityData) {
        const entitiesList = document.getElementById('entities-list');
        
        const itemHtml = `
            <div class="library-item entity-item" 
                 data-type="entity" 
                 data-id="${entityData.id}"
                 data-name="${entityData.name}"
                 data-entity-type="${entityData.entity_type}"
                 data-jurisdiction="${entityData.jurisdiction}"
                 data-total-shares="${entityData.total_shares || ''}">
                <div class="item-icon">${this.getEntityIcon(entityData.entity_type)}</div>
                <div class="item-info">
                    <div class="item-name">${entityData.name}</div>
                    <div class="item-details">
                        <span class="item-type">${entityData.entity_type}</span>
                        <span class="item-jurisdiction">${entityData.jurisdiction}</span>
                    </div>
                    ${entityData.total_shares ? `<div class="item-shares">📊 ${entityData.total_shares} shares</div>` : ''}
                </div>
                <div class="item-actions">
                    <button class="btn btn-xs btn-primary add-to-organogram" title="Add to Organogram">
                        <span class="icon">➕</span>
                    </button>
                </div>
            </div>
        `;
        
        entitiesList.insertAdjacentHTML('afterbegin', itemHtml);
        
        // Re-initialize drag and drop for new item
        const newItem = entitiesList.firstElementChild;
        newItem.draggable = true;
        newItem.addEventListener('dragstart', this.handleDragStart);
        
        const addBtn = newItem.querySelector('.add-to-organogram');
        addBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.addItemToOrganogram(newItem);
        });
    }
    
    openModal(modalId) {
        document.getElementById(modalId).style.display = 'flex';
    }
    
    closeModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }
    
    handleKeyboard(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 's':
                    event.preventDefault();
                    this.saveOrganogram();
                    break;
                case 'z':
                    event.preventDefault();
                    // Undo functionality could be implemented here
                    break;
                case 'a':
                    event.preventDefault();
                    this.autoLayout();
                    break;
            }
        }
        
        if (event.key === 'Delete' && (this.selectedNode || this.selectedConnection)) {
            if (this.selectedNode) {
                this.deleteNode(this.selectedNode);
            } else if (this.selectedConnection) {
                this.deleteConnection(this.selectedConnection);
                this.clearSelections();
                this.updateStatusBar();
            }
        }
        
        if (event.key === 'Escape') {
            this.clearSelections();
        }
    }
    
    updateStatusBar() {
        document.getElementById('nodes-count').textContent = `Nodes: ${this.nodes.size}`;
        document.getElementById('connections-count').textContent = `Connections: ${this.connections.size}`;
    }
    
    setStatus(message) {
        document.getElementById('status-message').textContent = message;
        
        // Clear status after 3 seconds
        setTimeout(() => {
            document.getElementById('status-message').textContent = 'Ready';
        }, 3000);
    }
    
    getNodeIcon(nodeData) {
        if (nodeData.type === 'party') {
            return '👤';
        } else {
            return this.getEntityIcon(nodeData.entity_type);
        }
    }
    
    getEntityIcon(entityType) {
        const icons = {
            'TRUST': '🛡️',
            'FOREIGN_TRUST': '🛡️',
            'FUND': '💰',
            'IBC': '🏢',
            'LLC_DISREGARDED': '🏛️',
            'LLC_PARTNERSHIP': '🤝',
            'LLC_AS_CORP': '🏢',
            'CORP': '🏢',
            'WYOMING_FOUNDATION': '🏛️',
        };
        return icons[entityType] || '🏢';
    }
    
    getNodeDetails(nodeData) {
        if (nodeData.type === 'entity') {
            return nodeData.jurisdiction || '';
        } else {
            return nodeData.nationality || '';
        }
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
}

// Global functions for button handlers
window.closeModal = function(modalId) {
    document.getElementById(modalId).style.display = 'none';
};

window.validateStructure = function(structureId) {
    if (window.organogramBuilder) {
        window.organogramBuilder.validateStructure();
    }
};

window.printOrganogram = function(structureId) {
    if (window.organogramBuilder) {
        window.organogramBuilder.printOrganogram();
    }
};

// Export for global access
window.OrganogramBuilder = OrganogramBuilder;

