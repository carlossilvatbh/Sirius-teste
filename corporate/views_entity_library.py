from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
import json

from .models import Entity, Structure, EntityOwnership
from parties.models import Party


@staff_member_required
def entity_library_view(request):
    """
    Entity Library Panel - Manage entities available for organogram building
    """
    
    # Get filter parameters
    entity_type_filter = request.GET.get('entity_type', '')
    jurisdiction_filter = request.GET.get('jurisdiction', '')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    entities = Entity.objects.filter(active=True)
    
    # Apply filters
    if entity_type_filter:
        entities = entities.filter(entity_type=entity_type_filter)
    
    if jurisdiction_filter:
        entities = entities.filter(jurisdiction=jurisdiction_filter)
    
    if search_query:
        entities = entities.filter(
            Q(name__icontains=search_query) |
            Q(entity_type__icontains=search_query) |
            Q(jurisdiction__icontains=search_query)
        )
    
    # Annotate with usage statistics
    entities = entities.annotate(
        usage_count=Count('ownerships_as_owned__structure', distinct=True)
    ).order_by('name')
    
    # Get filter options
    entity_types = Entity.objects.values_list('entity_type', flat=True).distinct()
    jurisdictions = Entity.objects.values_list('jurisdiction', flat=True).distinct()
    
    # Get parties for the library
    parties = Party.objects.filter(active=True).order_by('name')
    
    context = {
        'title': 'Entity Library',
        'entities': entities,
        'parties': parties,
        'entity_types': entity_types,
        'jurisdictions': jurisdictions,
        'current_filters': {
            'entity_type': entity_type_filter,
            'jurisdiction': jurisdiction_filter,
            'search': search_query,
        },
        'opts': Entity._meta,
        'has_view_permission': True,
        'has_change_permission': True,
        'has_add_permission': True,
    }
    
    return render(request, 'admin/corporate/entity_library_panel.html', context)


@staff_member_required
@csrf_exempt
def create_entity_api(request):
    """
    API endpoint to create new entity from organogram builder
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'entity_type', 'jurisdiction']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Create entity
        entity = Entity.objects.create(
            name=data['name'],
            entity_type=data['entity_type'],
            jurisdiction=data['jurisdiction'],
            us_state=data.get('us_state'),
            br_state=data.get('br_state'),
            total_shares=data.get('total_shares'),
            tax_classification=data.get('tax_classification'),
            implementation_time=data.get('implementation_time', 30),
            complexity=data.get('complexity', 3),
            confidentiality_level=data.get('confidentiality_level', 3),
            asset_protection=data.get('asset_protection', 3),
            banking_facility=data.get('banking_facility', 3),
        )
        
        # Return entity data
        return JsonResponse({
            'success': True,
            'entity': {
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.get_full_jurisdiction_display(),
                'total_shares': entity.total_shares,
                'icon': get_entity_icon(entity.entity_type)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def entity_usage_stats_api(request, entity_id):
    """
    API endpoint to get entity usage statistics
    """
    try:
        entity = get_object_or_404(Entity, id=entity_id)
        
        # Get usage statistics
        ownerships = EntityOwnership.objects.filter(owned_entity=entity).select_related(
            'structure', 'owner_ubo', 'owner_entity'
        )
        
        structures_data = {}
        for ownership in ownerships:
            structure_id = ownership.structure.id
            if structure_id not in structures_data:
                structures_data[structure_id] = {
                    'structure': {
                        'id': ownership.structure.id,
                        'name': ownership.structure.name,
                        'status': ownership.structure.status,
                        'created_at': ownership.structure.created_at.isoformat(),
                    },
                    'ownerships': []
                }
            
            owner_info = {}
            if ownership.owner_ubo:
                owner_info = {
                    'type': 'party',
                    'id': ownership.owner_ubo.id,
                    'name': ownership.owner_ubo.name,
                    'icon': '👤'
                }
            elif ownership.owner_entity:
                owner_info = {
                    'type': 'entity',
                    'id': ownership.owner_entity.id,
                    'name': ownership.owner_entity.name,
                    'icon': get_entity_icon(ownership.owner_entity.entity_type)
                }
            
            structures_data[structure_id]['ownerships'].append({
                'id': ownership.id,
                'owner': owner_info,
                'percentage': float(ownership.ownership_percentage or 0),
                'shares': ownership.owned_shares,
                'corporate_name': ownership.corporate_name,
                'hash_number': ownership.hash_number,
            })
        
        return JsonResponse({
            'success': True,
            'entity': {
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.get_full_jurisdiction_display(),
                'total_shares': entity.total_shares,
            },
            'usage_statistics': {
                'total_structures': len(structures_data),
                'structures': list(structures_data.values())
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def party_usage_stats_api(request, party_id):
    """
    API endpoint to get party usage statistics
    """
    try:
        party = get_object_or_404(Party, id=party_id)
        
        # Get usage statistics
        ownerships = EntityOwnership.objects.filter(owner_ubo=party).select_related(
            'structure', 'owned_entity'
        )
        
        structures_data = {}
        for ownership in ownerships:
            structure_id = ownership.structure.id
            if structure_id not in structures_data:
                structures_data[structure_id] = {
                    'structure': {
                        'id': ownership.structure.id,
                        'name': ownership.structure.name,
                        'status': ownership.structure.status,
                        'created_at': ownership.structure.created_at.isoformat(),
                    },
                    'ownerships': []
                }
            
            structures_data[structure_id]['ownerships'].append({
                'id': ownership.id,
                'owned_entity': {
                    'id': ownership.owned_entity.id,
                    'name': ownership.owned_entity.name,
                    'entity_type': ownership.owned_entity.entity_type,
                    'icon': get_entity_icon(ownership.owned_entity.entity_type)
                },
                'percentage': float(ownership.ownership_percentage or 0),
                'shares': ownership.owned_shares,
                'corporate_name': ownership.corporate_name,
                'hash_number': ownership.hash_number,
            })
        
        return JsonResponse({
            'success': True,
            'party': {
                'id': party.id,
                'name': party.name,
                'nationality': getattr(party, 'nationality', ''),
            },
            'usage_statistics': {
                'total_structures': len(structures_data),
                'structures': list(structures_data.values())
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def duplicate_entity_api(request, entity_id):
    """
    API endpoint to duplicate an entity
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        original_entity = get_object_or_404(Entity, id=entity_id)
        
        # Create duplicate
        duplicate = Entity.objects.create(
            name=f"{original_entity.name} (Copy)",
            entity_type=original_entity.entity_type,
            jurisdiction=original_entity.jurisdiction,
            us_state=original_entity.us_state,
            br_state=original_entity.br_state,
            total_shares=original_entity.total_shares,
            tax_classification=original_entity.tax_classification,
            implementation_time=original_entity.implementation_time,
            complexity=original_entity.complexity,
            confidentiality_level=original_entity.confidentiality_level,
            asset_protection=original_entity.asset_protection,
            banking_facility=original_entity.banking_facility,
            tax_impact_usa=original_entity.tax_impact_usa,
            tax_impact_brazil=original_entity.tax_impact_brazil,
            tax_impact_others=original_entity.tax_impact_others,
            privacy_impact=original_entity.privacy_impact,
            privacy_score=original_entity.privacy_score,
            banking_relation_score=original_entity.banking_relation_score,
            compliance_score=original_entity.compliance_score,
            required_documentation=original_entity.required_documentation,
            documents_url=original_entity.documents_url,
            required_forms_usa=original_entity.required_forms_usa,
            required_forms_brazil=original_entity.required_forms_brazil,
            implementation_templates=original_entity.implementation_templates,
        )
        
        return JsonResponse({
            'success': True,
            'entity': {
                'id': duplicate.id,
                'name': duplicate.name,
                'entity_type': duplicate.entity_type,
                'jurisdiction': duplicate.get_full_jurisdiction_display(),
                'total_shares': duplicate.total_shares,
                'icon': get_entity_icon(duplicate.entity_type)
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def entity_templates_api(request):
    """
    API endpoint to get entity templates for quick creation
    """
    # Common entity templates
    templates = [
        {
            'name': 'Delaware Corporation',
            'entity_type': 'CORP',
            'jurisdiction': 'US',
            'us_state': 'DE',
            'total_shares': 1000,
            'description': 'Standard Delaware Corporation for US operations'
        },
        {
            'name': 'Wyoming LLC',
            'entity_type': 'LLC_DISREGARDED',
            'jurisdiction': 'US',
            'us_state': 'WY',
            'total_shares': None,
            'description': 'Wyoming LLC for privacy and asset protection'
        },
        {
            'name': 'Bahamas IBC',
            'entity_type': 'IBC',
            'jurisdiction': 'BS',
            'total_shares': 50000,
            'description': 'Bahamas International Business Company'
        },
        {
            'name': 'Cayman Islands Fund',
            'entity_type': 'FUND',
            'jurisdiction': 'KY',
            'total_shares': None,
            'description': 'Cayman Islands Investment Fund'
        },
        {
            'name': 'Nevada Trust',
            'entity_type': 'TRUST',
            'jurisdiction': 'US',
            'us_state': 'NV',
            'total_shares': None,
            'description': 'Nevada Asset Protection Trust'
        },
        {
            'name': 'BVI Company',
            'entity_type': 'IBC',
            'jurisdiction': 'VG',
            'total_shares': 50000,
            'description': 'British Virgin Islands Business Company'
        }
    ]
    
    return JsonResponse({
        'success': True,
        'templates': templates
    })


def get_entity_icon(entity_type):
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


def get_entity_type_display(entity_type):
    """Get display name for entity type"""
    types = dict(Entity.ENTITY_TYPES)
    return types.get(entity_type, entity_type)


def get_jurisdiction_display(jurisdiction):
    """Get display name for jurisdiction"""
    jurisdictions = dict(Entity.JURISDICTIONS)
    return jurisdictions.get(jurisdiction, jurisdiction)

