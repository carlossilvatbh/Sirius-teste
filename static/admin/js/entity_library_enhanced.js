/**
 * Entity Library Enhanced JavaScript - Fase 2
 * Funcionalidades interativas para templates, quick add e busca avançada
 */

class EntityLibraryEnhanced {
    constructor() {
        this.currentTemplateId = null;
        this.init();
    }

    init() {
        this.setupTabs();
        this.setupSearch();
        this.setupFilters();
        this.setupQuickAdd();
        this.setupTemplates();
        this.setupEntities();
        this.setupParties();
        this.setupModals();
        this.setupDragAndDrop();
    }

    // Tab Management
    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.getAttribute('data-tab');
                
                // Remove active class from all tabs and contents
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                button.classList.add('active');
                document.getElementById(`${targetTab}-tab`).classList.add('active');
            });
        });
    }

    // Search Functionality
    setupSearch() {
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-btn');

        const performSearch = () => {
            const searchTerm = searchInput.value.trim();
            this.updateURL({ search: searchTerm });
            window.location.reload();
        };

        searchButton.addEventListener('click', performSearch);
        
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
            }
        });

        // Real-time search suggestions (debounced)
        let searchTimeout;
        searchInput.addEventListener('input', () => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.showSearchSuggestions(searchInput.value);
            }, 300);
        });
    }

    // Filter Management
    setupFilters() {
        const categoryFilter = document.getElementById('category-filter');
        const jurisdictionFilter = document.getElementById('jurisdiction-filter');
        const entityTypeFilter = document.getElementById('entity-type-filter');
        const clearFiltersBtn = document.getElementById('clear-filters-btn');

        [categoryFilter, jurisdictionFilter, entityTypeFilter].forEach(filter => {
            filter.addEventListener('change', () => {
                this.applyFilters();
            });
        });

        clearFiltersBtn.addEventListener('click', () => {
            this.clearFilters();
        });
    }

    applyFilters() {
        const filters = {
            category: document.getElementById('category-filter').value,
            jurisdiction: document.getElementById('jurisdiction-filter').value,
            entity_type: document.getElementById('entity-type-filter').value,
        };

        this.updateURL(filters);
        window.location.reload();
    }

    clearFilters() {
        document.getElementById('category-filter').value = '';
        document.getElementById('jurisdiction-filter').value = '';
        document.getElementById('entity-type-filter').value = '';
        document.getElementById('search-input').value = '';
        
        this.updateURL({
            search: '',
            category: '',
            jurisdiction: '',
            entity_type: ''
        });
        window.location.reload();
    }

    // Quick Add Functionality
    setupQuickAdd() {
        const quickAddButtons = document.querySelectorAll('.quick-add-btn');
        
        quickAddButtons.forEach(button => {
            button.addEventListener('click', async (e) => {
                const presetId = button.getAttribute('data-preset-id');
                const card = button.closest('.quick-preset-card');
                const customSuffix = card.querySelector('.custom-suffix-input').value.trim();
                
                button.disabled = true;
                button.textContent = 'Creating...';
                
                try {
                    const response = await this.quickAddEntity(presetId, customSuffix);
                    if (response.success) {
                        this.showNotification('success', response.message);
                        this.refreshEntityList();
                    } else {
                        this.showNotification('error', response.error);
                    }
                } catch (error) {
                    this.showNotification('error', 'Failed to create entity');
                } finally {
                    button.disabled = false;
                    button.textContent = 'Quick Add';
                }
            });
        });
    }

    async quickAddEntity(presetId, customSuffix) {
        const response = await fetch('/admin/corporate/api/quick-add-entity/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                preset_id: presetId,
                custom_suffix: customSuffix
            })
        });
        
        return await response.json();
    }

    // Template Management
    setupTemplates() {
        const templateDetailsButtons = document.querySelectorAll('.template-details-btn');
        const createFromTemplateButtons = document.querySelectorAll('.create-from-template-btn');

        templateDetailsButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const templateId = button.getAttribute('data-template-id');
                await this.showTemplateDetails(templateId);
            });
        });

        createFromTemplateButtons.forEach(button => {
            button.addEventListener('click', () => {
                const templateId = button.getAttribute('data-template-id');
                this.showCreateEntityModal(templateId);
            });
        });
    }

    async showTemplateDetails(templateId) {
        try {
            const response = await fetch(`/admin/corporate/api/template-details/${templateId}/`);
            const data = await response.json();
            
            if (data.success) {
                this.populateTemplateDetailsModal(data.template);
                this.currentTemplateId = templateId;
                this.openModal('template-details-modal');
            } else {
                this.showNotification('error', 'Failed to load template details');
            }
        } catch (error) {
            this.showNotification('error', 'Failed to load template details');
        }
    }

    populateTemplateDetailsModal(template) {
        const content = document.getElementById('template-details-content');
        content.innerHTML = `
            <div class="template-details-full">
                <div class="detail-section">
                    <h3>Basic Information</h3>
                    <p><strong>Name:</strong> ${template.name}</p>
                    <p><strong>Category:</strong> ${template.category}</p>
                    <p><strong>Jurisdiction:</strong> ${template.jurisdiction}</p>
                    <p><strong>Entity Type:</strong> ${template.entity_type}</p>
                    <p><strong>Usage Count:</strong> ${template.usage_count}</p>
                </div>
                
                <div class="detail-section">
                    <h3>Description</h3>
                    <p>${template.description}</p>
                </div>
                
                <div class="detail-section">
                    <h3>Default Name Pattern</h3>
                    <p><code>${template.default_name_pattern}</code></p>
                </div>
                
                <div class="detail-section">
                    <h3>Default Attributes</h3>
                    <pre>${JSON.stringify(template.default_attributes, null, 2)}</pre>
                </div>
                
                <div class="detail-section">
                    <h3>Required Documents</h3>
                    <ul>
                        ${template.required_documents.map(doc => `<li>${doc}</li>`).join('')}
                    </ul>
                </div>
                
                <div class="detail-section">
                    <h3>Typical Uses</h3>
                    <ul>
                        ${template.typical_uses.map(use => `<li>${use}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    showCreateEntityModal(templateId) {
        this.currentTemplateId = templateId;
        this.openModal('create-entity-modal');
        
        // Setup create entity form
        const confirmButton = document.getElementById('confirm-create-entity-btn');
        confirmButton.onclick = () => this.createEntityFromTemplate();
    }

    async createEntityFromTemplate() {
        const entityName = document.getElementById('entity-name').value.trim();
        const customAttributesText = document.getElementById('custom-attributes').value.trim();
        
        if (!entityName) {
            this.showNotification('error', 'Entity name is required');
            return;
        }
        
        let customAttributes = {};
        if (customAttributesText) {
            try {
                customAttributes = JSON.parse(customAttributesText);
            } catch (error) {
                this.showNotification('error', 'Invalid JSON in custom attributes');
                return;
            }
        }
        
        const confirmButton = document.getElementById('confirm-create-entity-btn');
        confirmButton.disabled = true;
        confirmButton.textContent = 'Creating...';
        
        try {
            const response = await this.createEntityFromTemplateAPI(
                this.currentTemplateId, 
                entityName, 
                customAttributes
            );
            
            if (response.success) {
                this.showNotification('success', response.message);
                this.closeModal('create-entity-modal');
                this.refreshEntityList();
            } else {
                this.showNotification('error', response.error);
            }
        } catch (error) {
            this.showNotification('error', 'Failed to create entity');
        } finally {
            confirmButton.disabled = false;
            confirmButton.textContent = 'Create Entity';
        }
    }

    async createEntityFromTemplateAPI(templateId, entityName, customAttributes) {
        const response = await fetch('/admin/corporate/api/create-entity-from-template/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template_id: templateId,
                custom_name: entityName,
                custom_attributes: customAttributes
            })
        });
        
        return await response.json();
    }

    // Entity Management
    setupEntities() {
        const entityStatsButtons = document.querySelectorAll('.entity-stats-btn');
        
        entityStatsButtons.forEach(button => {
            button.addEventListener('click', async () => {
                const entityId = button.getAttribute('data-entity-id');
                await this.showEntityStats(entityId);
            });
        });
    }

    async showEntityStats(entityId) {
        try {
            const response = await fetch(`/admin/corporate/api/entity-usage-stats-enhanced/${entityId}/`);
            const data = await response.json();
            
            if (data.success) {
                this.populateEntityStatsModal(data.stats);
                this.openModal('entity-stats-modal');
            } else {
                this.showNotification('error', 'Failed to load entity statistics');
            }
        } catch (error) {
            this.showNotification('error', 'Failed to load entity statistics');
        }
    }

    populateEntityStatsModal(stats) {
        const content = document.getElementById('entity-stats-content');
        content.innerHTML = `
            <div class="entity-stats-full">
                <div class="stats-header">
                    <h3>${stats.entity.name}</h3>
                    <p>${stats.entity.entity_type} - ${stats.entity.jurisdiction}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h4>Ownership Statistics</h4>
                        <p>Owns ${stats.ownership_stats.owns_entities_count} entities</p>
                        <p>Owned by ${stats.ownership_stats.owned_by_entities_count} entities</p>
                        <p>Total ownership given: ${stats.ownership_stats.total_ownership_given}%</p>
                        <p>Total ownership received: ${stats.ownership_stats.total_ownership_received}%</p>
                    </div>
                    
                    <div class="stat-card">
                        <h4>Structure Usage</h4>
                        <p>Used as owner in ${stats.structure_usage.structures_as_owner_count} structures</p>
                        <p>Used as owned in ${stats.structure_usage.structures_as_owned_count} structures</p>
                    </div>
                </div>
                
                <div class="relationships-section">
                    <div class="relationship-column">
                        <h4>As Owner</h4>
                        <ul>
                            ${stats.relationships.as_owner.map(rel => 
                                `<li>${rel.owned_entity} (${rel.percentage}%)</li>`
                            ).join('')}
                        </ul>
                    </div>
                    
                    <div class="relationship-column">
                        <h4>As Owned</h4>
                        <ul>
                            ${stats.relationships.as_owned.map(rel => 
                                `<li>${rel.owner_entity} (${rel.percentage}%)</li>`
                            ).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    // Party Management
    setupParties() {
        const partyStatsButtons = document.querySelectorAll('.party-stats-btn');
        
        partyStatsButtons.forEach(button => {
            button.addEventListener('click', () => {
                const partyId = button.getAttribute('data-party-id');
                this.showNotification('info', `Party stats for ID ${partyId} - Feature coming soon!`);
            });
        });
    }

    // Drag and Drop
    setupDragAndDrop() {
        const entityCards = document.querySelectorAll('.entity-card');
        const partyCards = document.querySelectorAll('.party-card');
        
        [...entityCards, ...partyCards].forEach(card => {
            card.addEventListener('dragstart', (e) => {
                card.classList.add('dragging');
                e.dataTransfer.setData('text/plain', card.dataset.entityId || card.dataset.partyId);
                e.dataTransfer.setData('type', card.classList.contains('entity-card') ? 'entity' : 'party');
            });
            
            card.addEventListener('dragend', () => {
                card.classList.remove('dragging');
            });
        });
    }

    // Modal Management
    setupModals() {
        const modals = document.querySelectorAll('.modal');
        const closeButtons = document.querySelectorAll('.modal-close');
        
        // Close modal when clicking close button
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                const modal = button.closest('.modal');
                this.closeModal(modal.id);
            });
        });
        
        // Close modal when clicking outside
        modals.forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });
        
        // Setup create from modal button
        const createFromModalBtn = document.getElementById('create-from-modal-btn');
        if (createFromModalBtn) {
            createFromModalBtn.addEventListener('click', () => {
                this.closeModal('template-details-modal');
                this.showCreateEntityModal(this.currentTemplateId);
            });
        }
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    // Search Suggestions
    async showSearchSuggestions(query) {
        if (query.length < 2) return;
        
        try {
            const [entitiesResponse, partiesResponse] = await Promise.all([
                fetch(`/admin/corporate/api/search-entities/?q=${encodeURIComponent(query)}&limit=5`),
                fetch(`/admin/corporate/api/search-parties/?q=${encodeURIComponent(query)}&limit=5`)
            ]);
            
            const entitiesData = await entitiesResponse.json();
            const partiesData = await partiesResponse.json();
            
            this.displaySearchSuggestions(entitiesData.results, partiesData.results);
        } catch (error) {
            console.error('Failed to fetch search suggestions:', error);
        }
    }

    displaySearchSuggestions(entities, parties) {
        // Remove existing suggestions
        const existingSuggestions = document.querySelector('.search-suggestions');
        if (existingSuggestions) {
            existingSuggestions.remove();
        }
        
        if (entities.length === 0 && parties.length === 0) return;
        
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        
        let suggestionsHTML = '<div class="suggestions-content">';
        
        if (entities.length > 0) {
            suggestionsHTML += '<div class="suggestion-group"><h4>Entities</h4>';
            entities.forEach(entity => {
                suggestionsHTML += `
                    <div class="suggestion-item" data-type="entity" data-id="${entity.id}">
                        ${entity.display_name}
                    </div>
                `;
            });
            suggestionsHTML += '</div>';
        }
        
        if (parties.length > 0) {
            suggestionsHTML += '<div class="suggestion-group"><h4>Parties</h4>';
            parties.forEach(party => {
                suggestionsHTML += `
                    <div class="suggestion-item" data-type="party" data-id="${party.id}">
                        ${party.display_name}
                    </div>
                `;
            });
            suggestionsHTML += '</div>';
        }
        
        suggestionsHTML += '</div>';
        suggestionsContainer.innerHTML = suggestionsHTML;
        
        // Position suggestions below search box
        const searchBox = document.querySelector('.search-box');
        searchBox.appendChild(suggestionsContainer);
        
        // Add click handlers for suggestions
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                const searchInput = document.getElementById('search-input');
                searchInput.value = item.textContent.trim();
                suggestionsContainer.remove();
            });
        });
    }

    // Utility Functions
    updateURL(params) {
        const url = new URL(window.location);
        Object.keys(params).forEach(key => {
            if (params[key]) {
                url.searchParams.set(key, params[key]);
            } else {
                url.searchParams.delete(key);
            }
        });
        window.history.replaceState({}, '', url);
    }

    refreshEntityList() {
        // Refresh the current tab content
        setTimeout(() => {
            window.location.reload();
        }, 1000);
    }

    showNotification(type, message) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">
                    ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
                </span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Add close button functionality
        notification.querySelector('.notification-close').addEventListener('click', () => {
            notification.remove();
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EntityLibraryEnhanced();
});

// Global function to close modals (for inline onclick handlers)
window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
};

