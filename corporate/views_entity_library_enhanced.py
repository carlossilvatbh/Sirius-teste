"""
Enhanced Entity Library Views - Fase 2
Views aprimoradas com templates, quick add e busca avançada
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json

from .models import Entity, Structure, EntityOwnership
from parties.models import Party
from .entity_templates import EntityTemplate, QuickAddPreset, create_predefined_templates, create_quick_add_presets


def entity_library_enhanced_view(request):
    """View principal da entity library aprimorada"""
    
    # Initialize templates if needed
    if not EntityTemplate.objects.exists():
        create_predefined_templates()
        create_quick_add_presets()
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    jurisdiction_filter = request.GET.get('jurisdiction', '')
    entity_type_filter = request.GET.get('entity_type', '')
    
    # Base querysets
    entities = Entity.objects.all()
    parties = Party.objects.all()
    templates = EntityTemplate.objects.filter(is_active=True)
    quick_presets = QuickAddPreset.objects.all()
    
    # Apply search filters
    if search_query:
        entities = entities.filter(
            Q(name__icontains=search_query) |
            Q(entity_type__icontains=search_query) |
            Q(jurisdiction__icontains=search_query)
        )
        parties = parties.filter(
            Q(name__icontains=search_query) |
            Q(party_type__icontains=search_query)
        )
        templates = templates.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Apply category filter
    if category_filter:
        templates = templates.filter(category=category_filter)
    
    # Apply jurisdiction filter
    if jurisdiction_filter:
        entities = entities.filter(jurisdiction=jurisdiction_filter)
        templates = templates.filter(jurisdiction=jurisdiction_filter)
    
    # Apply entity type filter
    if entity_type_filter:
        entities = entities.filter(entity_type=entity_type_filter)
    
    # Pagination
    entities_paginator = Paginator(entities, 12)
    entities_page = entities_paginator.get_page(request.GET.get('entities_page', 1))
    
    parties_paginator = Paginator(parties, 12)
    parties_page = parties_paginator.get_page(request.GET.get('parties_page', 1))
    
    templates_paginator = Paginator(templates, 8)
    templates_page = templates_paginator.get_page(request.GET.get('templates_page', 1))
    
    # Get statistics
    stats = {
        'total_entities': Entity.objects.count(),
        'total_parties': Party.objects.count(),
        'total_templates': EntityTemplate.objects.filter(is_active=True).count(),
        'total_structures': Structure.objects.count(),
        'popular_jurisdictions': Entity.objects.values('jurisdiction').annotate(
            count=Count('jurisdiction')
        ).order_by('-count')[:5],
        'popular_entity_types': Entity.objects.values('entity_type').annotate(
            count=Count('entity_type')
        ).order_by('-count')[:5],
    }
    
    # Get filter options
    filter_options = {
        'categories': EntityTemplate.TEMPLATE_CATEGORIES,
        'jurisdictions': EntityTemplate.JURISDICTIONS,
        'entity_types': Entity.objects.values_list('entity_type', flat=True).distinct(),
    }
    
    context = {
        'entities_page': entities_page,
        'parties_page': parties_page,
        'templates_page': templates_page,
        'quick_presets': quick_presets,
        'stats': stats,
        'filter_options': filter_options,
        'current_filters': {
            'search': search_query,
            'category': category_filter,
            'jurisdiction': jurisdiction_filter,
            'entity_type': entity_type_filter,
        }
    }
    
    return render(request, 'admin/corporate/entity_library_enhanced.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def create_entity_from_template_api(request):
    """API para criar entity a partir de template"""
    try:
        data = json.loads(request.body)
        template_id = data.get('template_id')
        custom_name = data.get('custom_name')
        custom_attributes = data.get('custom_attributes', {})
        
        template = get_object_or_404(EntityTemplate, id=template_id)
        entity = template.create_entity_from_template(
            custom_name=custom_name,
            custom_attributes=custom_attributes
        )
        
        return JsonResponse({
            'success': True,
            'entity': {
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.jurisdiction,
            },
            'message': f'Entity "{entity.name}" created successfully from template'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def quick_add_entity_api(request):
    """API para quick add de entity usando preset"""
    try:
        data = json.loads(request.body)
        preset_id = data.get('preset_id')
        custom_suffix = data.get('custom_suffix')
        
        preset = get_object_or_404(QuickAddPreset, id=preset_id)
        entity = preset.create_quick_entity(custom_suffix=custom_suffix)
        
        return JsonResponse({
            'success': True,
            'entity': {
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.jurisdiction,
            },
            'message': f'Entity "{entity.name}" created successfully via quick add'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def template_details_api(request, template_id):
    """API para obter detalhes de um template"""
    try:
        template = get_object_or_404(EntityTemplate, id=template_id)
        
        return JsonResponse({
            'success': True,
            'template': {
                'id': template.id,
                'name': template.name,
                'category': template.category,
                'jurisdiction': template.jurisdiction,
                'entity_type': template.entity_type,
                'description': template.description,
                'default_name_pattern': template.default_name_pattern,
                'default_attributes': template.default_attributes,
                'required_documents': template.required_documents,
                'typical_uses': template.typical_uses,
                'usage_count': template.usage_count,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def entity_usage_stats_enhanced_api(request, entity_id):
    """API aprimorada para estatísticas de uso de entity"""
    try:
        entity = get_object_or_404(Entity, id=entity_id)
        
        # Get ownership relationships
        as_owner = EntityOwnership.objects.filter(owner_entity=entity)
        as_owned = EntityOwnership.objects.filter(owned_entity=entity)
        
        # Get structures where this entity is used
        structures_as_owner = Structure.objects.filter(
            entityownership__owner_entity=entity
        ).distinct()
        
        structures_as_owned = Structure.objects.filter(
            entityownership__owned_entity=entity
        ).distinct()
        
        # Calculate total ownership percentages
        total_ownership_given = sum(
            ownership.ownership_percentage or 0 
            for ownership in as_owner.all()
        )
        
        total_ownership_received = sum(
            ownership.ownership_percentage or 0 
            for ownership in as_owned.all()
        )
        
        stats = {
            'entity': {
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.jurisdiction,
            },
            'ownership_stats': {
                'owns_entities_count': as_owner.count(),
                'owned_by_entities_count': as_owned.count(),
                'total_ownership_given': total_ownership_given,
                'total_ownership_received': total_ownership_received,
            },
            'structure_usage': {
                'structures_as_owner_count': structures_as_owner.count(),
                'structures_as_owned_count': structures_as_owned.count(),
                'structures_as_owner': [
                    {'id': s.id, 'name': s.name} 
                    for s in structures_as_owner[:5]
                ],
                'structures_as_owned': [
                    {'id': s.id, 'name': s.name} 
                    for s in structures_as_owned[:5]
                ],
            },
            'relationships': {
                'as_owner': [
                    {
                        'owned_entity': ownership.owned_entity.name,
                        'percentage': ownership.ownership_percentage,
                        'structure': ownership.structure.name if ownership.structure else None,
                    }
                    for ownership in as_owner.all()[:10]
                ],
                'as_owned': [
                    {
                        'owner_entity': ownership.owner_entity.name,
                        'percentage': ownership.ownership_percentage,
                        'structure': ownership.structure.name if ownership.structure else None,
                    }
                    for ownership in as_owned.all()[:10]
                ],
            }
        }
        
        return JsonResponse({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def search_entities_api(request):
    """API avançada para busca de entities"""
    try:
        query = request.GET.get('q', '')
        entity_type = request.GET.get('entity_type', '')
        jurisdiction = request.GET.get('jurisdiction', '')
        limit = int(request.GET.get('limit', 20))
        
        entities = Entity.objects.all()
        
        if query:
            entities = entities.filter(
                Q(name__icontains=query) |
                Q(entity_type__icontains=query) |
                Q(jurisdiction__icontains=query)
            )
        
        if entity_type:
            entities = entities.filter(entity_type=entity_type)
        
        if jurisdiction:
            entities = entities.filter(jurisdiction=jurisdiction)
        
        entities = entities[:limit]
        
        results = [
            {
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.jurisdiction,
                'display_name': f"{entity.name} ({entity.entity_type}, {entity.jurisdiction})"
            }
            for entity in entities
        ]
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["GET"])
def search_parties_api(request):
    """API avançada para busca de parties"""
    try:
        query = request.GET.get('q', '')
        party_type = request.GET.get('party_type', '')
        limit = int(request.GET.get('limit', 20))
        
        parties = Party.objects.all()
        
        if query:
            parties = parties.filter(
                Q(name__icontains=query) |
                Q(party_type__icontains=query)
            )
        
        if party_type:
            parties = parties.filter(party_type=party_type)
        
        parties = parties[:limit]
        
        results = [
            {
                'id': party.id,
                'name': party.name,
                'party_type': party.party_type,
                'display_name': f"{party.name} ({party.party_type})"
            }
            for party in parties
        ]
        
        return JsonResponse({
            'success': True,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

