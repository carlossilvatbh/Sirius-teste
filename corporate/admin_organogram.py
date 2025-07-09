from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from django.forms import TextInput, Textarea
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .models import Entity, Structure, EntityOwnership
from parties.models import Party
from .views_entity_library_enhanced import entity_library_enhanced_view


class OrganogramBuilderInline(admin.StackedInline):
    """Organogram Builder Interface for EntityOwnership"""
    model = EntityOwnership
    extra = 0
    min_num = 0
    
    template = 'admin/corporate/organogram_builder_inline.html'
    
    fields = []  # We'll handle fields in the template
    
    def get_formset(self, request, obj=None, **kwargs):
        """Customize formset for organogram builder"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Add custom attributes to formset
        formset.organogram_data = self.get_organogram_data(obj) if obj else {}
        formset.available_entities = self.get_available_entities()
        formset.available_parties = self.get_available_parties()
        
        return formset
    
    def get_organogram_data(self, structure):
        """Get organogram data for visualization"""
        if not structure:
            return {}
        
        ownerships = EntityOwnership.objects.filter(structure=structure).select_related(
            'owned_entity', 'owner_ubo', 'owner_entity'
        )
        
        # Build hierarchical data
        nodes = {}
        edges = []
        
        # Create nodes for all entities and parties
        for ownership in ownerships:
            # Owned entity node
            entity_id = f"entity_{ownership.owned_entity.id}"
            if entity_id not in nodes:
                nodes[entity_id] = {
                    'id': entity_id,
                    'type': 'entity',
                    'name': ownership.owned_entity.name,
                    'entity_type': ownership.owned_entity.entity_type,
                    'jurisdiction': ownership.owned_entity.get_full_jurisdiction_display(),
                    'total_shares': ownership.owned_entity.total_shares,
                    'level': 0  # Will be calculated
                }
            
            # Owner node
            if ownership.owner_ubo:
                owner_id = f"party_{ownership.owner_ubo.id}"
                if owner_id not in nodes:
                    nodes[owner_id] = {
                        'id': owner_id,
                        'type': 'party',
                        'name': ownership.owner_ubo.name,
                        'nationality': getattr(ownership.owner_ubo, 'nationality', ''),
                        'level': 0  # Will be calculated
                    }
            elif ownership.owner_entity:
                owner_id = f"entity_{ownership.owner_entity.id}"
                if owner_id not in nodes:
                    nodes[owner_id] = {
                        'id': owner_id,
                        'type': 'entity',
                        'name': ownership.owner_entity.name,
                        'entity_type': ownership.owner_entity.entity_type,
                        'jurisdiction': ownership.owner_entity.get_full_jurisdiction_display(),
                        'total_shares': ownership.owner_entity.total_shares,
                        'level': 0  # Will be calculated
                    }
            
            # Create edge
            owner_id = f"party_{ownership.owner_ubo.id}" if ownership.owner_ubo else f"entity_{ownership.owner_entity.id}"
            edges.append({
                'id': f"edge_{ownership.id}",
                'source': owner_id,
                'target': entity_id,
                'percentage': float(ownership.ownership_percentage or 0),
                'shares': ownership.owned_shares,
                'corporate_name': ownership.corporate_name,
                'hash_number': ownership.hash_number,
                'share_value_usd': float(ownership.share_value_usd or 0),
                'share_value_eur': float(ownership.share_value_eur or 0),
                'ownership_id': ownership.id
            })
        
        # Calculate levels (hierarchy depth)
        self.calculate_node_levels(nodes, edges)
        
        return {
            'nodes': list(nodes.values()),
            'edges': edges,
            'structure_id': structure.id,
            'structure_name': structure.name
        }
    
    def calculate_node_levels(self, nodes, edges):
        """Calculate hierarchical levels for nodes"""
        # Find root nodes (parties that don't have incoming edges)
        incoming_targets = {edge['target'] for edge in edges}
        root_nodes = [node_id for node_id in nodes.keys() if node_id not in incoming_targets]
        
        # BFS to assign levels
        queue = [(node_id, 0) for node_id in root_nodes]
        visited = set()
        
        while queue:
            node_id, level = queue.pop(0)
            if node_id in visited:
                continue
            
            visited.add(node_id)
            nodes[node_id]['level'] = level
            
            # Add children to queue
            for edge in edges:
                if edge['source'] == node_id and edge['target'] not in visited:
                    queue.append((edge['target'], level + 1))
    
    def get_available_entities(self):
        """Get all available entities for the library"""
        entities = Entity.objects.filter(active=True).order_by('name')
        return [
            {
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.get_full_jurisdiction_display(),
                'total_shares': entity.total_shares,
                'icon': self.get_entity_icon(entity.entity_type)
            }
            for entity in entities
        ]
    
    def get_available_parties(self):
        """Get all available parties for the library"""
        from parties.models import Party
        parties = Party.objects.filter(active=True).order_by('name')
        return [
            {
                'id': party.id,
                'name': party.name,
                'nationality': getattr(party, 'nationality', ''),
                'icon': '👤'
            }
            for party in parties
        ]
    
    def get_entity_icon(self, entity_type):
        """Get icon for entity type"""
        icons = {
            'TRUST': '🛡️',
            'FOREIGN_TRUST': '🛡️',
            'FUND': '💰',
            'IBC': '🏢',
            'LLC_DISREGARDED': '🏛️',
            'LLC_PARTNERSHIP': '🤝',
            'LLC_AS_CORP': '🏢',
            'CORP': '🏢',
            'WYOMING_FOUNDATION': '🏛️',
        }
        return icons.get(entity_type, '🏢')
    
    class Media:
        css = {
            'all': ('admin/css/organogram_builder.css',)
        }
        js = ('admin/js/organogram_builder.js',)


@admin.register(Structure)
class StructureOrganogramAdmin(admin.ModelAdmin):
    """Enhanced Structure admin with Organogram Builder"""
    
    list_display = [
        'name_with_icon', 'status_badge', 'entities_count', 
        'completion_percentage', 'hierarchy_depth', 'created_at', 'action_buttons'
    ]
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('name', 'description', 'status'),
            'classes': ('wide',)
        }),
        ('🌳 Organogram Builder', {
            'fields': ('organogram_builder',),
            'classes': ('wide',),
            'description': 'Build your corporate structure visually using drag & drop'
        }),
        ('📊 Ownership Matrix', {
            'fields': ('ownership_matrix',),
            'classes': ('wide', 'collapse'),
            'description': 'Detailed ownership matrix with validation'
        }),
        ('📈 Validation & Metrics', {
            'fields': ('validation_summary', 'tax_impacts_summary'),
            'classes': ('wide', 'collapse'),
            'description': 'Validation results and calculated metrics'
        }),
    )
    
    readonly_fields = ['organogram_builder', 'ownership_matrix', 'validation_summary', 'tax_impacts_summary']
    
    inlines = []  # We'll use custom organogram builder instead
    
    # actions = []  # Will be added in future phases
    
    def get_urls(self):
        """Add custom URLs for organogram builder and API endpoints"""
        urls = super().get_urls()
        custom_urls = [
            path(
                'organogram-builder/',
                self.admin_site.admin_view(self.organogram_builder_view),
                name='corporate_structure_organogram_builder'
            ),
            path(
                'api/save-organogram/',
                self.admin_site.admin_view(self.save_organogram_api),
                name='corporate_structure_save_organogram'
            ),
            path(
                'api/validate-structure/<int:structure_id>/',
                self.admin_site.admin_view(self.validate_structure_api),
                name='corporate_structure_validate'
            ),
            path(
                'entity-library/',
                self.admin_site.admin_view(entity_library_enhanced_view),
                name='entity_library_enhanced'
            ),
        ]
        return custom_urls + urls
    
    def organogram_builder_view(self, request):
        """Custom view for organogram builder"""
        structure_id = request.GET.get('structure_id')
        structure = None
        
        if structure_id:
            try:
                structure = Structure.objects.get(id=structure_id)
            except Structure.DoesNotExist:
                messages.error(request, 'Structure not found')
                return redirect('admin:corporate_structure_changelist')
        
        context = {
            'title': 'Organogram Builder',
            'structure': structure,
            'available_entities': self.get_available_entities(),
            'available_parties': self.get_available_parties(),
            'organogram_data': self.get_organogram_data(structure) if structure else {},
            'opts': self.model._meta,
            'has_view_permission': True,
            'has_change_permission': True,
        }
        
        return render(request, 'admin/corporate/build_organogram.html', context)
    
    @method_decorator(csrf_exempt)
    def save_organogram_api(self, request):
        """API endpoint to save organogram data"""
        if request.method != 'POST':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
        
        try:
            data = json.loads(request.body)
            structure_id = data.get('structure_id')
            nodes = data.get('nodes', [])
            edges = data.get('edges', [])
            
            if not structure_id:
                return JsonResponse({'error': 'Structure ID required'}, status=400)
            
            structure = Structure.objects.get(id=structure_id)
            
            # Clear existing ownerships
            EntityOwnership.objects.filter(structure=structure).delete()
            
            # Create new ownerships from edges
            for edge in edges:
                source_id = edge['source']
                target_id = edge['target']
                
                # Parse IDs
                if source_id.startswith('party_'):
                    owner_party_id = int(source_id.replace('party_', ''))
                    owner_entity_id = None
                elif source_id.startswith('entity_'):
                    owner_party_id = None
                    owner_entity_id = int(source_id.replace('entity_', ''))
                else:
                    continue
                
                if target_id.startswith('entity_'):
                    owned_entity_id = int(target_id.replace('entity_', ''))
                else:
                    continue
                
                # Get objects
                from parties.models import Party
                owner_ubo = Party.objects.get(id=owner_party_id) if owner_party_id else None
                owner_entity = Entity.objects.get(id=owner_entity_id) if owner_entity_id else None
                owned_entity = Entity.objects.get(id=owned_entity_id)
                
                # Create ownership
                EntityOwnership.objects.create(
                    structure=structure,
                    owner_ubo=owner_ubo,
                    owner_entity=owner_entity,
                    owned_entity=owned_entity,
                    ownership_percentage=edge.get('percentage', 0),
                    owned_shares=edge.get('shares'),
                    corporate_name=edge.get('corporate_name', ''),
                    hash_number=edge.get('hash_number', ''),
                    share_value_usd=edge.get('share_value_usd'),
                    share_value_eur=edge.get('share_value_eur'),
                )
            
            return JsonResponse({'success': True, 'message': 'Organogram saved successfully'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def validate_structure_api(self, request, structure_id):
        """API endpoint to validate structure"""
        try:
            structure = Structure.objects.get(id=structure_id)
            
            # Perform validation
            validation_results = self.perform_structure_validation(structure)
            
            return JsonResponse({
                'success': True,
                'validation_results': validation_results
            })
            
        except Structure.DoesNotExist:
            return JsonResponse({'error': 'Structure not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    def perform_structure_validation(self, structure):
        """Perform comprehensive structure validation"""
        results = {
            'overall_status': 'valid',
            'issues': [],
            'warnings': [],
            'entity_validations': {},
            'ownership_totals': {},
            'hierarchy_analysis': {}
        }
        
        ownerships = EntityOwnership.objects.filter(structure=structure).select_related(
            'owned_entity', 'owner_ubo', 'owner_entity'
        )
        
        if not ownerships.exists():
            results['overall_status'] = 'invalid'
            results['issues'].append('No ownership relationships defined')
            return results
        
        # Validate ownership percentages
        entity_totals = {}
        for ownership in ownerships:
            entity_id = ownership.owned_entity.id
            if entity_id not in entity_totals:
                entity_totals[entity_id] = {
                    'entity': ownership.owned_entity,
                    'total_percentage': 0,
                    'ownerships': []
                }
            entity_totals[entity_id]['total_percentage'] += ownership.ownership_percentage or 0
            entity_totals[entity_id]['ownerships'].append(ownership)
        
        # Check each entity
        for entity_id, data in entity_totals.items():
            entity = data['entity']
            total = data['total_percentage']
            
            results['ownership_totals'][entity_id] = {
                'entity_name': entity.name,
                'total_percentage': total,
                'status': 'valid' if total == 100 else 'invalid'
            }
            
            if total != 100:
                if total > 100:
                    results['issues'].append(f'{entity.name} is over-owned ({total}%)')
                    results['overall_status'] = 'invalid'
                elif total < 100:
                    results['warnings'].append(f'{entity.name} is under-owned ({total}%)')
                    if results['overall_status'] == 'valid':
                        results['overall_status'] = 'warning'
        
        # Analyze hierarchy
        results['hierarchy_analysis'] = self.analyze_hierarchy(ownerships)
        
        return results
    
    def analyze_hierarchy(self, ownerships):
        """Analyze the hierarchy structure"""
        analysis = {
            'max_depth': 0,
            'root_entities': [],
            'leaf_entities': [],
            'circular_references': []
        }
        
        # Build graph
        graph = {}
        all_entities = set()
        
        for ownership in ownerships:
            source = ownership.owner_entity.id if ownership.owner_entity else f"party_{ownership.owner_ubo.id}"
            target = ownership.owned_entity.id
            
            all_entities.add(target)
            if ownership.owner_entity:
                all_entities.add(source)
            
            if source not in graph:
                graph[source] = []
            graph[source].append(target)
        
        # Find roots (entities not owned by other entities)
        owned_entities = {ownership.owned_entity.id for ownership in ownerships}
        owning_entities = {ownership.owner_entity.id for ownership in ownerships if ownership.owner_entity}
        
        analysis['root_entities'] = list(owning_entities - owned_entities)
        analysis['leaf_entities'] = list(owned_entities - owning_entities)
        
        # Calculate max depth using DFS
        def dfs_depth(node, visited, depth):
            if node in visited:
                return depth  # Circular reference
            
            visited.add(node)
            max_child_depth = depth
            
            if node in graph:
                for child in graph[node]:
                    child_depth = dfs_depth(child, visited.copy(), depth + 1)
                    max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        for root in analysis['root_entities']:
            depth = dfs_depth(root, set(), 0)
            analysis['max_depth'] = max(analysis['max_depth'], depth)
        
        return analysis
    
    def name_with_icon(self, obj):
        """Display name with appropriate icon"""
        status_icons = {
            'DRAFTING': '📝',
            'SENT_FOR_APPROVAL': '📤',
            'APPROVED': '✅',
        }
        icon = status_icons.get(obj.status, '📋')
        return format_html('{} {}', icon, obj.name)
    name_with_icon.short_description = 'Structure Name'
    name_with_icon.admin_order_field = 'name'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'DRAFTING': '#6c757d',
            'SENT_FOR_APPROVAL': '#ffc107',
            'APPROVED': '#28a745',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def entities_count(self, obj):
        """Count of entities in this structure"""
        count = EntityOwnership.objects.filter(structure=obj).values('owned_entity').distinct().count()
        return format_html('🏢 {}', count)
    entities_count.short_description = 'Entities'
    
    def hierarchy_depth(self, obj):
        """Calculate and display hierarchy depth"""
        ownerships = EntityOwnership.objects.filter(structure=obj)
        if not ownerships.exists():
            return format_html('<span style="color: #6c757d;">➖</span>')
        
        analysis = self.analyze_hierarchy(ownerships)
        depth = analysis['max_depth']
        
        return format_html('🌳 {} levels', depth)
    hierarchy_depth.short_description = 'Depth'
    
    def completion_percentage(self, obj):
        """Show completion percentage with progress bar"""
        ownerships = EntityOwnership.objects.filter(structure=obj)
        if not ownerships.exists():
            return format_html('<span style="color: #dc3545;">0%</span>')
        
        # Calculate completion
        entity_totals = {}
        for ownership in ownerships:
            entity_id = ownership.owned_entity_id
            if entity_id not in entity_totals:
                entity_totals[entity_id] = 0
            entity_totals[entity_id] += ownership.ownership_percentage or 0
        
        complete_entities = sum(1 for total in entity_totals.values() if total == 100)
        total_entities = len(entity_totals)
        
        if total_entities == 0:
            percentage = 0
        else:
            percentage = (complete_entities / total_entities) * 100
        
        color = '#28a745' if percentage == 100 else '#ffc107' if percentage > 0 else '#dc3545'
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 60px; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; transition: width 0.3s ease;"></div>'
            '</div>'
            '<span style="color: {}; font-weight: bold;">{}%</span>'
            '</div>',
            percentage, color, color, int(percentage)
        )
    completion_percentage.short_description = 'Completion'
    
    def action_buttons(self, obj):
        """Action buttons for quick operations"""
        buttons = []
        
        # Organogram Builder button
        builder_url = reverse('admin:corporate_structure_organogram_builder')
        buttons.append(
            f'<a href="{builder_url}?structure_id={obj.id}" '
            f'style="background: #667eea; color: white; padding: 4px 8px; '
            f'border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 4px;">'
            f'🌳 Builder</a>'
        )
        
        # Validate button
        buttons.append(
            f'<a href="#" onclick="validateStructure({obj.id})" '
            f'style="background: #28a745; color: white; padding: 4px 8px; '
            f'border-radius: 4px; text-decoration: none; font-size: 11px; margin-right: 4px;">'
            f'✅ Validate</a>'
        )
        
        # Print button
        buttons.append(
            f'<a href="#" onclick="printOrganogram({obj.id})" '
            f'style="background: #6f42c1; color: white; padding: 4px 8px; '
            f'border-radius: 4px; text-decoration: none; font-size: 11px;">'
            f'🖨️ Print</a>'
        )
        
        return format_html(''.join(buttons))
    action_buttons.short_description = 'Actions'
    
    def organogram_builder(self, obj):
        """Organogram builder interface"""
        if not obj or not obj.pk:
            return format_html(
                '<div style="text-align: center; padding: 40px; color: #666; border: 2px dashed #ddd; border-radius: 8px;">'
                '<h3>🌳 Organogram Builder</h3>'
                '<p>Save the structure first to access the organogram builder</p>'
                '</div>'
            )
        
        builder_url = reverse('admin:corporate_structure_organogram_builder')
        
        return format_html(
            '<div style="text-align: center; padding: 20px; border: 1px solid #e9ecef; border-radius: 8px; background: #f8f9fa;">'
            '<h3 style="margin-bottom: 15px;">🌳 Interactive Organogram Builder</h3>'
            '<p style="margin-bottom: 20px; color: #666;">Build your corporate structure visually using drag & drop</p>'
            '<a href="{}?structure_id={}" '
            'style="display: inline-block; background: #667eea; color: white; padding: 12px 24px; '
            'border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 14px;">'
            '🚀 Open Organogram Builder</a>'
            '</div>',
            builder_url, obj.id
        )
    organogram_builder.short_description = 'Organogram Builder'
    
    def ownership_matrix(self, obj):
        """Visual ownership matrix"""
        if not obj:
            return format_html('<div style="color: #666;">No structure selected</div>')
        
        ownerships = EntityOwnership.objects.filter(structure=obj).select_related(
            'owned_entity', 'owner_ubo', 'owner_entity'
        )
        
        if not ownerships.exists():
            return format_html(
                '<div style="text-align: center; padding: 20px; color: #666;">'
                '📋 No ownership relationships defined<br>'
                '<small>Use the organogram builder to create ownership structure</small>'
                '</div>'
            )
        
        # Group by entity
        entity_groups = {}
        for ownership in ownerships:
            entity_id = ownership.owned_entity_id
            if entity_id not in entity_groups:
                entity_groups[entity_id] = {
                    'entity': ownership.owned_entity,
                    'ownerships': [],
                    'total_percentage': 0
                }
            entity_groups[entity_id]['ownerships'].append(ownership)
            entity_groups[entity_id]['total_percentage'] += ownership.ownership_percentage or 0
        
        html_parts = ['<div class="ownership-matrix">']
        
        for group in entity_groups.values():
            entity = group['entity']
            total = group['total_percentage']
            
            # Entity header
            status_color = '#28a745' if total == 100 else '#ffc107' if total < 100 else '#dc3545'
            html_parts.append(
                f'<div class="entity-group">'
                f'<div class="entity-header">'
                f'<div class="entity-info">'
                f'<span class="entity-icon">🏢</span>'
                f'<span class="entity-name">{entity.name}</span>'
                f'<span class="entity-type">({entity.get_entity_type_display()})</span>'
                f'</div>'
                f'<div class="entity-total" style="background: {status_color};">{total:.1f}%</div>'
                f'</div>'
            )
            
            # Ownership rows
            html_parts.append('<div class="ownership-rows">')
            for ownership in group['ownerships']:
                owner_name = ownership.owner_ubo.name if ownership.owner_ubo else (
                    ownership.owner_entity.name if ownership.owner_entity else 'Unknown'
                )
                owner_icon = '👤' if ownership.owner_ubo else '🏢'
                percentage = ownership.ownership_percentage or 0
                
                html_parts.append(
                    f'<div class="ownership-row">'
                    f'<div class="owner-info">'
                    f'<span class="owner-icon">{owner_icon}</span>'
                    f'<span class="owner-name">{owner_name}</span>'
                    f'</div>'
                    f'<div class="ownership-bar">'
                    f'<div class="bar-fill" style="width: {min(percentage, 100)}%; background: {status_color};"></div>'
                    f'<span class="bar-text">{percentage:.1f}%</span>'
                    f'</div>'
                    f'<div class="ownership-details">'
                    f'<div>Shares: {ownership.owned_shares or "N/A"}</div>'
                    f'<div>Corporate: {ownership.corporate_name or "N/A"}</div>'
                    f'</div>'
                    f'</div>'
                )
            
            html_parts.append('</div></div>')
        
        html_parts.append('</div>')
        
        return format_html(''.join(html_parts))
    ownership_matrix.short_description = 'Ownership Matrix'
    
    def validation_summary(self, obj):
        """Validation summary with metrics"""
        if not obj:
            return format_html('<div style="color: #666;">No structure selected</div>')
        
        validation_results = self.perform_structure_validation(obj)
        
        status_colors = {
            'valid': '#28a745',
            'warning': '#ffc107',
            'invalid': '#dc3545'
        }
        
        status_color = status_colors.get(validation_results['overall_status'], '#6c757d')
        
        html_parts = [
            f'<div style="margin-bottom: 15px; padding: 10px; background: {status_color}; '
            f'color: white; border-radius: 6px; text-align: center; font-weight: bold;">'
            f'Overall Status: {validation_results["overall_status"].title()}'
            f'</div>'
        ]
        
        if validation_results['issues']:
            html_parts.append('<div style="margin-bottom: 10px;"><strong style="color: #dc3545;">Issues:</strong>')
            for issue in validation_results['issues']:
                html_parts.append(f'<div style="color: #dc3545; margin-left: 10px;">❌ {issue}</div>')
            html_parts.append('</div>')
        
        if validation_results['warnings']:
            html_parts.append('<div style="margin-bottom: 10px;"><strong style="color: #ffc107;">Warnings:</strong>')
            for warning in validation_results['warnings']:
                html_parts.append(f'<div style="color: #ffc107; margin-left: 10px;">⚠️ {warning}</div>')
            html_parts.append('</div>')
        
        return format_html(''.join(html_parts))
    validation_summary.short_description = 'Validation Summary'
    
    def tax_impacts_summary(self, obj):
        """Tax impacts summary"""
        # This would calculate tax impacts based on the structure
        return format_html(
            '<div style="color: #666; font-style: italic;">Tax impact calculation will be implemented in Phase 5</div>'
        )
    tax_impacts_summary.short_description = 'Tax Impacts'
    
    def get_organogram_data(self, structure):
        """Get organogram data for the structure"""
        inline = OrganogramBuilderInline(self.model, self.admin_site)
        return inline.get_organogram_data(structure)
    
    def get_available_entities(self):
        """Get available entities"""
        inline = OrganogramBuilderInline(self.model, self.admin_site)
        return inline.get_available_entities()
    
    def get_available_parties(self):
        """Get available parties"""
        inline = OrganogramBuilderInline(self.model, self.admin_site)
        return inline.get_available_parties()
    
    class Media:
        css = {
            'all': (
                'admin/css/organogram_builder.css',
                'admin/css/ownership_matrix.css',
            )
        }
        js = (
            'admin/js/organogram_builder.js',
        )


# Keep existing Entity and EntityOwnership admins but enhance them
@admin.register(Entity)
class EntityLibraryAdmin(admin.ModelAdmin):
    """Enhanced Entity admin for library functionality"""
    
    list_display = [
        'name_with_icon', 'entity_type', 'jurisdiction', 
        'usage_count', 'total_shares', 'created_at'
    ]
    list_filter = ['entity_type', 'jurisdiction', 'active', 'created_at']
    search_fields = ['name', 'entity_type', 'jurisdiction']
    ordering = ['name']
    
    fieldsets = (
        ('🏢 Entity Information', {
            'fields': ('name', 'entity_type', 'jurisdiction', 'us_state', 'br_state'),
            'classes': ('wide',)
        }),
        ('📊 Share Information', {
            'fields': ('total_shares',),
            'classes': ('wide',)
        }),
        ('📈 Usage Statistics', {
            'fields': ('usage_statistics',),
            'classes': ('wide', 'collapse'),
            'description': 'How this entity is being used across structures'
        }),
    )
    
    readonly_fields = ['usage_statistics']
    
    def name_with_icon(self, obj):
        """Display name with entity type icon"""
        inline = OrganogramBuilderInline(Structure, self.admin_site)
        icon = inline.get_entity_icon(obj.entity_type)
        return format_html('{} {}', icon, obj.name)
    name_with_icon.short_description = 'Entity Name'
    name_with_icon.admin_order_field = 'name'
    
    def usage_count(self, obj):
        """Count of structures using this entity"""
        count = EntityOwnership.objects.filter(owned_entity=obj).values('structure').distinct().count()
        return format_html('🏗️ {}', count)
    usage_count.short_description = 'Used In'
    
    def usage_statistics(self, obj):
        """Detailed usage statistics"""
        ownerships = EntityOwnership.objects.filter(owned_entity=obj).select_related('structure')
        
        if not ownerships.exists():
            return format_html(
                '<div style="text-align: center; padding: 20px; color: #666;">'
                '📋 Entity not used in any structures yet<br>'
                '<small>This entity is available in the library for use</small>'
                '</div>'
            )
        
        structures = {}
        for ownership in ownerships:
            structure_id = ownership.structure.id
            if structure_id not in structures:
                structures[structure_id] = {
                    'structure': ownership.structure,
                    'ownerships': []
                }
            structures[structure_id]['ownerships'].append(ownership)
        
        html_parts = ['<div class="usage-statistics">']
        
        for data in structures.values():
            structure = data['structure']
            ownerships_list = data['ownerships']
            
            html_parts.append(
                f'<div style="border: 1px solid #e9ecef; border-radius: 6px; '
                f'margin-bottom: 10px; padding: 10px; background: #f8f9fa;">'
                f'<div style="font-weight: bold; margin-bottom: 5px;">🏗️ {structure.name}</div>'
            )
            
            for ownership in ownerships_list:
                owner_name = ownership.owner_ubo.name if ownership.owner_ubo else (
                    ownership.owner_entity.name if ownership.owner_entity else 'Unknown'
                )
                owner_icon = '👤' if ownership.owner_ubo else '🏢'
                percentage = ownership.ownership_percentage or 0
                
                html_parts.append(
                    f'<div style="margin-left: 15px; font-size: 12px; color: #666;">'
                    f'{owner_icon} {owner_name} owns {percentage:.1f}%</div>'
                )
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        return format_html(''.join(html_parts))
    usage_statistics.short_description = 'Usage Statistics'


# Unregister the old admin if it exists
try:
    admin.site.unregister(Structure)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Entity)
except admin.sites.NotRegistered:
    pass

