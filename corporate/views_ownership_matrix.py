"""
Ownership Matrix Visual Views
Provides comprehensive ownership visualization and management
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count
from django.core.serializers import serialize
import json
import csv
import io
from collections import defaultdict

from .models import Entity, Structure, EntityOwnership
from parties.models import Party


@staff_member_required
def ownership_matrix_visual_view(request):
    """
    Main view for the ownership matrix visual interface
    """
    # Get all data for the interface
    structures = Structure.objects.all().order_by('name')
    entities = Entity.objects.all().order_by('name')
    parties = Party.objects.all().order_by('name')
    ownerships = EntityOwnership.objects.select_related(
        'owner_entity', 'owner_ubo', 'owned_entity', 'structure'
    ).all()
    
    # Calculate statistics
    total_ownerships = ownerships.count()
    entities_count = entities.count()
    parties_count = parties.count()
    
    context = {
        'structures': structures,
        'entities': entities,
        'parties': parties,
        'ownerships': ownerships,
        'total_ownerships': total_ownerships,
        'entities_count': entities_count,
        'parties_count': parties_count,
    }
    
    return render(request, 'admin/corporate/ownership_matrix_visual.html', context)


@staff_member_required
@require_http_methods(["GET"])
def ownership_matrix_data_api(request):
    """
    API endpoint to get ownership matrix data
    """
    try:
        # Get filter parameters
        structure_id = request.GET.get('structure_id')
        min_percentage = float(request.GET.get('min_percentage', 0))
        include_parties = request.GET.get('include_parties', 'true').lower() == 'true'
        
        # Build queryset
        ownerships_qs = EntityOwnership.objects.select_related(
            'owner_entity', 'owner_ubo', 'owned_entity', 'structure'
        )
        
        if structure_id:
            ownerships_qs = ownerships_qs.filter(structure_id=structure_id)
        
        if min_percentage > 0:
            ownerships_qs = ownerships_qs.filter(ownership_percentage__gte=min_percentage)
        
        if not include_parties:
            ownerships_qs = ownerships_qs.filter(owner_ubo__isnull=True)
        
        # Serialize data
        ownerships_data = []
        for ownership in ownerships_qs:
            ownerships_data.append({
                'id': ownership.id,
                'owner_entity_id': ownership.owner_entity.id if ownership.owner_entity else None,
                'owner_entity_name': ownership.owner_entity.name if ownership.owner_entity else None,
                'owner_ubo_id': ownership.owner_ubo.id if ownership.owner_ubo else None,
                'owner_ubo_name': ownership.owner_ubo.name if ownership.owner_ubo else None,
                'owned_entity_id': ownership.owned_entity.id,
                'owned_entity_name': ownership.owned_entity.name,
                'ownership_percentage': float(ownership.ownership_percentage),
                'structure_id': ownership.structure.id if ownership.structure else None,
                'structure_name': ownership.structure.name if ownership.structure else None,
                'notes': ownership.notes or '',
                'created_at': ownership.created_at.isoformat() if hasattr(ownership, 'created_at') else None,
            })
        
        # Get entities and parties data
        entities_data = []
        for entity in Entity.objects.all():
            entities_data.append({
                'id': entity.id,
                'name': entity.name,
                'entity_type': entity.entity_type,
                'jurisdiction': entity.jurisdiction,
            })
        
        parties_data = []
        if include_parties:
            for party in Party.objects.all():
                parties_data.append({
                    'id': party.id,
                    'name': party.name,
                    'party_type': party.party_type if hasattr(party, 'party_type') else 'Individual',
                })
        
        return JsonResponse({
            'ownerships': ownerships_data,
            'entities': entities_data,
            'parties': parties_data,
            'total_count': len(ownerships_data),
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def create_ownership_api(request):
    """
    API endpoint to create a new ownership relationship
    """
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        # Validate required fields
        owner_type = data.get('owner_type')
        owner_id = data.get('owner_id')
        owned_entity_id = data.get('owned_entity_id')
        ownership_percentage = float(data.get('ownership_percentage', 0))
        
        if not all([owner_type, owner_id, owned_entity_id]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        if ownership_percentage < 0 or ownership_percentage > 100:
            return JsonResponse({'error': 'Ownership percentage must be between 0 and 100'}, status=400)
        
        # Get owned entity
        owned_entity = get_object_or_404(Entity, id=owned_entity_id)
        
        # Create ownership object
        ownership_data = {
            'owned_entity': owned_entity,
            'ownership_percentage': ownership_percentage,
            'notes': data.get('notes', ''),
        }
        
        # Set owner based on type
        if owner_type == 'entity':
            owner_entity = get_object_or_404(Entity, id=owner_id)
            ownership_data['owner_entity'] = owner_entity
        elif owner_type == 'party':
            owner_ubo = get_object_or_404(Party, id=owner_id)
            ownership_data['owner_ubo'] = owner_ubo
        else:
            return JsonResponse({'error': 'Invalid owner type'}, status=400)
        
        # Set structure if provided
        structure_id = data.get('structure_id')
        if structure_id:
            structure = get_object_or_404(Structure, id=structure_id)
            ownership_data['structure'] = structure
        
        # Check for duplicate ownership
        existing_ownership = EntityOwnership.objects.filter(
            **{k: v for k, v in ownership_data.items() if k != 'ownership_percentage' and k != 'notes'}
        ).first()
        
        if existing_ownership:
            return JsonResponse({'error': 'Ownership relationship already exists'}, status=400)
        
        # Create the ownership
        ownership = EntityOwnership.objects.create(**ownership_data)
        
        return JsonResponse({
            'id': ownership.id,
            'message': 'Ownership created successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@require_http_methods(["GET"])
def get_ownership_api(request, ownership_id):
    """
    API endpoint to get a specific ownership relationship
    """
    try:
        ownership = get_object_or_404(EntityOwnership, id=ownership_id)
        
        data = {
            'id': ownership.id,
            'owner_entity_id': ownership.owner_entity.id if ownership.owner_entity else None,
            'owner_ubo_id': ownership.owner_ubo.id if ownership.owner_ubo else None,
            'owned_entity_id': ownership.owned_entity.id,
            'ownership_percentage': float(ownership.ownership_percentage),
            'structure_id': ownership.structure.id if ownership.structure else None,
            'notes': ownership.notes or '',
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["PUT"])
def update_ownership_api(request, ownership_id):
    """
    API endpoint to update an ownership relationship
    """
    try:
        ownership = get_object_or_404(EntityOwnership, id=ownership_id)
        data = json.loads(request.body)
        
        # Update fields
        if 'ownership_percentage' in data:
            percentage = float(data['ownership_percentage'])
            if percentage < 0 or percentage > 100:
                return JsonResponse({'error': 'Ownership percentage must be between 0 and 100'}, status=400)
            ownership.ownership_percentage = percentage
        
        if 'notes' in data:
            ownership.notes = data['notes']
        
        if 'structure_id' in data:
            if data['structure_id']:
                structure = get_object_or_404(Structure, id=data['structure_id'])
                ownership.structure = structure
            else:
                ownership.structure = None
        
        ownership.save()
        
        return JsonResponse({'message': 'Ownership updated successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_ownership_api(request, ownership_id):
    """
    API endpoint to delete an ownership relationship
    """
    try:
        ownership = get_object_or_404(EntityOwnership, id=ownership_id)
        ownership.delete()
        
        return JsonResponse({'message': 'Ownership deleted successfully'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def validate_ownership_matrix_api(request):
    """
    API endpoint to validate the ownership matrix
    """
    try:
        data = json.loads(request.body) if request.body else {}
        structure_id = data.get('structure_id')
        
        # Build queryset
        ownerships_qs = EntityOwnership.objects.all()
        if structure_id:
            ownerships_qs = ownerships_qs.filter(structure_id=structure_id)
        
        validation_results = []
        
        # Check 1: Total ownership per entity should not exceed 100%
        entity_ownerships = defaultdict(float)
        for ownership in ownerships_qs:
            entity_ownerships[ownership.owned_entity.id] += ownership.ownership_percentage
        
        for entity_id, total_percentage in entity_ownerships.items():
            entity = Entity.objects.get(id=entity_id)
            if total_percentage > 100:
                validation_results.append({
                    'type': 'error',
                    'title': f'Over-ownership detected: {entity.name}',
                    'message': f'Total ownership is {total_percentage:.2f}%, which exceeds 100%'
                })
            elif total_percentage == 100:
                validation_results.append({
                    'type': 'success',
                    'title': f'Complete ownership: {entity.name}',
                    'message': f'Total ownership is exactly 100%'
                })
            elif total_percentage < 100 and total_percentage > 0:
                validation_results.append({
                    'type': 'warning',
                    'title': f'Partial ownership: {entity.name}',
                    'message': f'Total ownership is {total_percentage:.2f}%, {100 - total_percentage:.2f}% unaccounted'
                })
        
        # Check 2: Circular ownership detection
        def has_circular_ownership(entity_id, visited=None, path=None):
            if visited is None:
                visited = set()
            if path is None:
                path = []
            
            if entity_id in path:
                return True, path + [entity_id]
            
            if entity_id in visited:
                return False, []
            
            visited.add(entity_id)
            path.append(entity_id)
            
            # Check all entities that this entity owns
            owned_entities = ownerships_qs.filter(
                Q(owner_entity_id=entity_id)
            ).values_list('owned_entity_id', flat=True)
            
            for owned_entity_id in owned_entities:
                has_circular, circular_path = has_circular_ownership(owned_entity_id, visited.copy(), path.copy())
                if has_circular:
                    return True, circular_path
            
            return False, []
        
        checked_entities = set()
        for entity in Entity.objects.all():
            if entity.id not in checked_entities:
                has_circular, circular_path = has_circular_ownership(entity.id)
                if has_circular:
                    entity_names = [Entity.objects.get(id=eid).name for eid in circular_path]
                    validation_results.append({
                        'type': 'error',
                        'title': 'Circular ownership detected',
                        'message': f'Circular ownership path: {" → ".join(entity_names)}'
                    })
                    checked_entities.update(circular_path)
                else:
                    checked_entities.add(entity.id)
        
        # Check 3: Orphaned entities (no ownership)
        owned_entity_ids = set(ownerships_qs.values_list('owned_entity_id', flat=True))
        all_entity_ids = set(Entity.objects.values_list('id', flat=True))
        orphaned_entity_ids = all_entity_ids - owned_entity_ids
        
        for entity_id in orphaned_entity_ids:
            entity = Entity.objects.get(id=entity_id)
            validation_results.append({
                'type': 'warning',
                'title': f'Orphaned entity: {entity.name}',
                'message': 'This entity has no ownership relationships'
            })
        
        # Summary
        error_count = len([r for r in validation_results if r['type'] == 'error'])
        warning_count = len([r for r in validation_results if r['type'] == 'warning'])
        
        if error_count == 0 and warning_count == 0:
            validation_results.insert(0, {
                'type': 'success',
                'title': 'Matrix validation passed',
                'message': 'No issues found in the ownership matrix'
            })
        else:
            validation_results.insert(0, {
                'type': 'info',
                'title': 'Validation summary',
                'message': f'Found {error_count} errors and {warning_count} warnings'
            })
        
        return JsonResponse(validation_results, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def export_ownership_matrix_api(request):
    """
    API endpoint to export the ownership matrix in various formats
    """
    try:
        data = json.loads(request.body)
        format_type = data.get('format', 'csv')
        structure_id = data.get('structure_id')
        include_parties = data.get('include_parties', True)
        include_zero_ownership = data.get('include_zero_ownership', False)
        include_metadata = data.get('include_metadata', True)
        
        # Build queryset
        ownerships_qs = EntityOwnership.objects.select_related(
            'owner_entity', 'owner_ubo', 'owned_entity', 'structure'
        )
        
        if structure_id:
            ownerships_qs = ownerships_qs.filter(structure_id=structure_id)
        
        if not include_parties:
            ownerships_qs = ownerships_qs.filter(owner_ubo__isnull=True)
        
        if not include_zero_ownership:
            ownerships_qs = ownerships_qs.filter(ownership_percentage__gt=0)
        
        if format_type == 'csv':
            return export_csv(ownerships_qs, include_metadata)
        elif format_type == 'json':
            return export_json(ownerships_qs, include_metadata)
        elif format_type == 'excel':
            return export_excel(ownerships_qs, include_metadata)
        elif format_type == 'pdf':
            return export_pdf(ownerships_qs, include_metadata)
        else:
            return JsonResponse({'error': 'Unsupported format'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def export_csv(ownerships_qs, include_metadata):
    """Export ownership matrix as CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    headers = ['Owner', 'Owner Type', 'Owned Entity', 'Ownership %', 'Structure']
    if include_metadata:
        headers.extend(['Notes', 'Created At'])
    writer.writerow(headers)
    
    # Write data
    for ownership in ownerships_qs:
        owner_name = ownership.owner_entity.name if ownership.owner_entity else ownership.owner_ubo.name
        owner_type = 'Entity' if ownership.owner_entity else 'Party'
        
        row = [
            owner_name,
            owner_type,
            ownership.owned_entity.name,
            ownership.ownership_percentage,
            ownership.structure.name if ownership.structure else ''
        ]
        
        if include_metadata:
            row.extend([
                ownership.notes or '',
                ownership.created_at.isoformat() if hasattr(ownership, 'created_at') else ''
            ])
        
        writer.writerow(row)
    
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ownership_matrix.csv"'
    return response


def export_json(ownerships_qs, include_metadata):
    """Export ownership matrix as JSON"""
    data = []
    
    for ownership in ownerships_qs:
        item = {
            'owner': {
                'name': ownership.owner_entity.name if ownership.owner_entity else ownership.owner_ubo.name,
                'type': 'entity' if ownership.owner_entity else 'party',
                'id': ownership.owner_entity.id if ownership.owner_entity else ownership.owner_ubo.id
            },
            'owned_entity': {
                'name': ownership.owned_entity.name,
                'id': ownership.owned_entity.id,
                'type': ownership.owned_entity.entity_type
            },
            'ownership_percentage': float(ownership.ownership_percentage),
            'structure': {
                'name': ownership.structure.name if ownership.structure else None,
                'id': ownership.structure.id if ownership.structure else None
            }
        }
        
        if include_metadata:
            item['metadata'] = {
                'notes': ownership.notes or '',
                'created_at': ownership.created_at.isoformat() if hasattr(ownership, 'created_at') else None
            }
        
        data.append(item)
    
    response = JsonResponse(data, safe=False)
    response['Content-Disposition'] = 'attachment; filename="ownership_matrix.json"'
    return response


def export_excel(ownerships_qs, include_metadata):
    """Export ownership matrix as Excel (placeholder - would need openpyxl)"""
    # For now, return CSV with Excel content type
    return export_csv(ownerships_qs, include_metadata)


def export_pdf(ownerships_qs, include_metadata):
    """Export ownership matrix as PDF (placeholder - would need reportlab)"""
    # For now, return JSON
    return export_json(ownerships_qs, include_metadata)

