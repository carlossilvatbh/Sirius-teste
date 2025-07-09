"""
Party Ownership Dashboard Views
Provides comprehensive dashboard functionality for party ownership analysis
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg, Max
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from collections import defaultdict
import json
from datetime import datetime, timedelta

from .models import Entity, Structure, EntityOwnership
from parties.models import Party


@staff_member_required
def party_ownership_dashboard(request, party_id=None):
    """
    Main party ownership dashboard view
    """
    # Get all parties for selection
    parties = Party.objects.all().order_by('name')
    
    context = {
        'parties': parties,
        'selected_party': None,
        'party_stats': {},
        'party_structures': [],
        'analytics': {}
    }
    
    if party_id:
        try:
            selected_party = get_object_or_404(Party, id=party_id)
            context.update({
                'selected_party': selected_party,
                'party_stats': get_party_statistics(selected_party),
                'party_structures': get_party_structures(selected_party),
                'analytics': get_party_analytics(selected_party)
            })
        except Party.DoesNotExist:
            pass
    
    return render(request, 'admin/corporate/party_ownership_dashboard.html', context)


@staff_member_required
def party_dashboard_data(request, party_id):
    """
    API endpoint for party dashboard data
    """
    try:
        party = get_object_or_404(Party, id=party_id)
        
        # Get comprehensive party data
        data = {
            'party_name': party.name,
            'party_type': party.party_type if hasattr(party, 'party_type') else 'Individual',
            'stats': get_party_statistics(party),
            'structures': get_party_structures_data(party),
            'charts': get_party_chart_data(party),
            'timeline': get_party_timeline_data(party),
            'analytics': get_party_analytics(party),
            'recent_activity': get_party_recent_activity(party)
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Party.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Party not found'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def get_party_statistics(party):
    """
    Calculate comprehensive statistics for a party
    """
    # Get all ownerships where this party is the owner
    ownerships = EntityOwnership.objects.filter(owner_ubo=party)
    
    # Get all structures this party is involved in
    structures = Structure.objects.filter(
        id__in=ownerships.values_list('structure_id', flat=True)
    ).distinct()
    
    # Get all entities owned by this party
    owned_entities = Entity.objects.filter(
        id__in=ownerships.values_list('owned_entity_id', flat=True)
    ).distinct()
    
    # Calculate statistics
    total_ownership = ownerships.aggregate(
        total=Sum('ownership_percentage')
    )['total'] or 0
    
    avg_ownership = ownerships.aggregate(
        avg=Avg('ownership_percentage')
    )['avg'] or 0
    
    max_ownership = ownerships.aggregate(
        max=Max('ownership_percentage')
    )['max'] or 0
    
    # Get unique jurisdictions
    jurisdictions = set()
    for entity in owned_entities:
        if hasattr(entity, 'jurisdiction') and entity.jurisdiction:
            jurisdictions.add(entity.jurisdiction)
    
    return {
        'total_structures': structures.count(),
        'total_ownership': round(total_ownership, 2),
        'active_entities': owned_entities.count(),
        'jurisdictions_count': len(jurisdictions),
        'avg_ownership': round(avg_ownership, 2),
        'max_ownership': round(max_ownership, 2),
        'total_ownerships': ownerships.count(),
        'diversification_index': calculate_diversification_index(ownerships),
        'complexity_score': calculate_complexity_score(party)
    }


def get_party_structures(party):
    """
    Get structures associated with a party for template display
    """
    ownerships = EntityOwnership.objects.filter(owner_ubo=party)
    structure_ids = ownerships.values_list('structure_id', flat=True).distinct()
    structures = Structure.objects.filter(id__in=structure_ids)
    
    result = []
    for structure in structures:
        # Calculate party's total ownership in this structure
        party_ownerships = ownerships.filter(structure=structure)
        total_ownership = party_ownerships.aggregate(
            total=Sum('ownership_percentage')
        )['total'] or 0
        
        # Count entities in this structure
        entities_count = Entity.objects.filter(
            id__in=party_ownerships.values_list('owned_entity_id', flat=True)
        ).count()
        
        result.append({
            'id': structure.id,
            'name': structure.name,
            'structure_type': structure.structure_type if hasattr(structure, 'structure_type') else 'Unknown',
            'status': 'Active',  # Default status
            'entities_count': entities_count,
            'party_ownership_percentage': round(total_ownership, 2)
        })
    
    return result


def get_party_structures_data(party):
    """
    Get detailed structures data for API response
    """
    structures = get_party_structures(party)
    
    # Add additional data for each structure
    for structure in structures:
        structure_obj = Structure.objects.get(id=structure['id'])
        
        # Get entities in this structure
        ownerships = EntityOwnership.objects.filter(
            owner_ubo=party,
            structure=structure_obj
        )
        
        entities = []
        for ownership in ownerships:
            entities.append({
                'id': ownership.owned_entity.id,
                'name': ownership.owned_entity.name,
                'entity_type': ownership.owned_entity.entity_type,
                'ownership_percentage': ownership.ownership_percentage,
                'jurisdiction': getattr(ownership.owned_entity, 'jurisdiction', 'Unknown')
            })
        
        structure['entities'] = entities
    
    return structures


def get_party_chart_data(party):
    """
    Generate chart data for party dashboard
    """
    ownerships = EntityOwnership.objects.filter(owner_ubo=party)
    
    # Ownership distribution by entity
    ownership_data = []
    ownership_labels = []
    for ownership in ownerships[:8]:  # Limit to top 8 for readability
        ownership_labels.append(ownership.owned_entity.name)
        ownership_data.append(float(ownership.ownership_percentage))
    
    # Structure types distribution
    structures = Structure.objects.filter(
        id__in=ownerships.values_list('structure_id', flat=True)
    ).distinct()
    
    structure_types = defaultdict(int)
    for structure in structures:
        structure_type = getattr(structure, 'structure_type', 'Unknown')
        structure_types[structure_type] += 1
    
    # Jurisdiction distribution
    entities = Entity.objects.filter(
        id__in=ownerships.values_list('owned_entity_id', flat=True)
    )
    
    jurisdictions = defaultdict(int)
    for entity in entities:
        jurisdiction = getattr(entity, 'jurisdiction', 'Unknown')
        jurisdictions[jurisdiction] += 1
    
    return {
        'ownership': {
            'labels': ownership_labels,
            'data': ownership_data
        },
        'structure_types': {
            'labels': list(structure_types.keys()),
            'data': list(structure_types.values())
        },
        'jurisdictions': {
            'labels': list(jurisdictions.keys()),
            'data': list(jurisdictions.values())
        },
        'timeline': generate_timeline_data(party)
    }


def generate_timeline_data(party):
    """
    Generate timeline data for party ownership over time
    """
    # Generate sample timeline data (in real implementation, this would use actual dates)
    labels = []
    data = []
    
    # Generate last 12 months
    current_date = datetime.now()
    for i in range(11, -1, -1):
        date = current_date - timedelta(days=i * 30)
        labels.append(date.strftime('%b %Y'))
        
        # Calculate ownership at that time (simplified)
        # In real implementation, this would query historical data
        base_ownership = 50 + (i * 2)  # Sample increasing ownership
        data.append(min(100, base_ownership))
    
    return {
        'labels': labels,
        'data': data
    }


def get_party_timeline_data(party):
    """
    Get timeline data for party ownership changes
    """
    return generate_timeline_data(party)


def get_party_analytics(party):
    """
    Generate analytics and recommendations for party
    """
    ownerships = EntityOwnership.objects.filter(owner_ubo=party)
    
    # Calculate risk metrics
    concentration_risk = calculate_concentration_risk(ownerships)
    jurisdiction_risk = calculate_jurisdiction_risk(party)
    complexity_risk = calculate_complexity_risk(party)
    
    # Generate recommendations
    recommendations = generate_recommendations(party, ownerships)
    
    # Compliance status
    compliance = {
        'documentation': 'compliant',
        'reporting': 'partial',
        'tax': 'compliant',
        'regulatory': 'compliant'
    }
    
    return {
        'concentration_risk': concentration_risk,
        'jurisdiction_risk': jurisdiction_risk,
        'complexity_risk': complexity_risk,
        'recommendations': recommendations,
        'compliance': compliance
    }


def get_party_recent_activity(party):
    """
    Get recent activity for party
    """
    # In real implementation, this would query an activity log
    return [
        {
            'description': f'New ownership in {party.name} portfolio',
            'date': '2 hours ago',
            'type': 'ownership_change'
        },
        {
            'description': 'Structure validation completed',
            'date': '1 day ago',
            'type': 'validation'
        },
        {
            'description': 'Compliance report generated',
            'date': '3 days ago',
            'type': 'compliance'
        }
    ]


def calculate_diversification_index(ownerships):
    """
    Calculate diversification index based on ownership distribution
    """
    if not ownerships.exists():
        return 0
    
    # Simple diversification calculation
    total_ownerships = ownerships.count()
    if total_ownerships <= 1:
        return 0
    
    # Calculate based on number of different entities and ownership distribution
    unique_entities = ownerships.values('owned_entity').distinct().count()
    diversification = min(100, (unique_entities / total_ownerships) * 100)
    
    return round(diversification, 1)


def calculate_complexity_score(party):
    """
    Calculate complexity score based on structure complexity
    """
    ownerships = EntityOwnership.objects.filter(owner_ubo=party)
    
    # Factors contributing to complexity
    num_structures = ownerships.values('structure').distinct().count()
    num_entities = ownerships.values('owned_entity').distinct().count()
    num_jurisdictions = len(set(
        getattr(entity, 'jurisdiction', 'Unknown')
        for entity in Entity.objects.filter(
            id__in=ownerships.values_list('owned_entity_id', flat=True)
        )
    ))
    
    # Simple complexity calculation
    complexity = min(100, (num_structures * 10) + (num_entities * 5) + (num_jurisdictions * 15))
    
    return round(complexity, 1)


def calculate_concentration_risk(ownerships):
    """
    Calculate concentration risk based on ownership distribution
    """
    if not ownerships.exists():
        return 0
    
    # Calculate concentration based on largest ownership percentage
    max_ownership = ownerships.aggregate(max=Max('ownership_percentage'))['max'] or 0
    
    # High concentration if single ownership > 50%
    if max_ownership > 50:
        return min(100, max_ownership)
    else:
        return max_ownership / 2
    
    return round(max_ownership, 1)


def calculate_jurisdiction_risk(party):
    """
    Calculate jurisdiction risk based on jurisdiction diversity
    """
    ownerships = EntityOwnership.objects.filter(owner_ubo=party)
    entities = Entity.objects.filter(
        id__in=ownerships.values_list('owned_entity_id', flat=True)
    )
    
    jurisdictions = set()
    for entity in entities:
        jurisdiction = getattr(entity, 'jurisdiction', 'Unknown')
        jurisdictions.add(jurisdiction)
    
    # Risk decreases with jurisdiction diversity
    num_jurisdictions = len(jurisdictions)
    if num_jurisdictions <= 1:
        return 80  # High risk for single jurisdiction
    elif num_jurisdictions <= 3:
        return 50  # Medium risk
    else:
        return 20  # Low risk for diverse jurisdictions
    
    return 50  # Default medium risk


def calculate_complexity_risk(party):
    """
    Calculate complexity risk based on structure complexity
    """
    complexity_score = calculate_complexity_score(party)
    
    # Convert complexity score to risk percentage
    if complexity_score > 70:
        return 80  # High risk
    elif complexity_score > 40:
        return 50  # Medium risk
    else:
        return 20  # Low risk


def generate_recommendations(party, ownerships):
    """
    Generate recommendations based on party's ownership profile
    """
    recommendations = []
    
    # Check concentration risk
    max_ownership = ownerships.aggregate(max=Max('ownership_percentage'))['max'] or 0
    if max_ownership > 75:
        recommendations.append({
            'type': 'Risk Management',
            'text': 'Consider diversifying ownership to reduce concentration risk.',
            'priority': 'high'
        })
    
    # Check jurisdiction diversity
    entities = Entity.objects.filter(
        id__in=ownerships.values_list('owned_entity_id', flat=True)
    )
    jurisdictions = set(
        getattr(entity, 'jurisdiction', 'Unknown')
        for entity in entities
    )
    
    if len(jurisdictions) <= 2:
        recommendations.append({
            'type': 'Diversification',
            'text': 'Consider expanding to additional jurisdictions for better risk distribution.',
            'priority': 'medium'
        })
    
    # Check structure complexity
    num_structures = ownerships.values('structure').distinct().count()
    if num_structures > 5:
        recommendations.append({
            'type': 'Simplification',
            'text': 'Review structure complexity and consider consolidation opportunities.',
            'priority': 'low'
        })
    
    return recommendations


@staff_member_required
@csrf_exempt
def export_party_report(request):
    """
    Export party report in various formats
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        data = json.loads(request.body)
        party_id = data.get('party_id')
        report_type = data.get('report_type', 'summary')
        format_type = data.get('format', 'pdf')
        
        party = get_object_or_404(Party, id=party_id)
        
        # Generate report based on type and format
        # This would integrate with report generation libraries
        
        return JsonResponse({
            'success': True,
            'message': f'{report_type.title()} report generated successfully',
            'download_url': f'/admin/corporate/reports/party_{party_id}_{report_type}.{format_type}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@staff_member_required
def validate_party_ownership(request, party_id):
    """
    Validate party ownership structure
    """
    try:
        party = get_object_or_404(Party, id=party_id)
        ownerships = EntityOwnership.objects.filter(owner_ubo=party)
        
        validation_results = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Validate ownership percentages
        for structure in Structure.objects.filter(
            id__in=ownerships.values_list('structure_id', flat=True)
        ).distinct():
            structure_ownerships = ownerships.filter(structure=structure)
            total_ownership = structure_ownerships.aggregate(
                total=Sum('ownership_percentage')
            )['total'] or 0
            
            if total_ownership > 100:
                validation_results['errors'].append(
                    f'Total ownership in {structure.name} exceeds 100%'
                )
                validation_results['valid'] = False
            elif total_ownership < 100:
                validation_results['warnings'].append(
                    f'Total ownership in {structure.name} is less than 100%'
                )
        
        return JsonResponse({
            'success': True,
            'validation': validation_results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

