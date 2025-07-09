"""
Views para o Organogram Builder - Interface visual para montagem de estruturas
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db import transaction
import json

from .models import Structure, Entity, StructureNode, NodeOwnership
from parties.models import Party


@staff_member_required
def organogram_builder_view(request):
    """View principal do Organogram Builder"""
    
    # Buscar dados para o builder
    structures = Structure.objects.all().order_by('-created_at')
    entities = Entity.objects.all().order_by('name')
    parties = Party.objects.all().order_by('name')
    
    # Estatísticas
    stats = {
        'total_structures': structures.count(),
        'total_entities': entities.count(),
        'total_parties': parties.count(),
        'total_nodes': StructureNode.objects.count(),
        'total_ownerships': NodeOwnership.objects.count(),
    }
    
    context = {
        'title': 'Construtor de Organogramas',
        'structures': structures,
        'entities': entities,
        'parties': parties,
        'stats': stats,
    }
    
    return render(request, 'admin/corporate/organogram_builder.html', context)


@staff_member_required
def organogram_builder_structure(request, structure_id):
    """View para editar estrutura específica no builder"""
    
    structure = get_object_or_404(Structure, id=structure_id)
    
    # Buscar nodes da estrutura
    nodes = StructureNode.objects.filter(structure=structure).select_related(
        'entity_template'
    ).order_by('level', 'custom_name')
    
    # Buscar ownerships
    ownerships = NodeOwnership.objects.filter(
        owned_node__structure=structure
    ).select_related('owner_party', 'owner_node', 'owned_node')
    
    # Preparar dados para o frontend
    nodes_data = []
    for node in nodes:
        nodes_data.append({
            'id': node.id,
            'custom_name': node.custom_name,
            'entity_template': {
                'id': node.entity_template.id,
                'name': node.entity_template.name,
                'entity_type': node.entity_template.entity_type,
                'jurisdiction': node.entity_template.jurisdiction,
            },
            'level': node.level,
            'total_shares': node.total_shares,
            'corporate_name': node.corporate_name,
            'parent_node_id': node.parent_node.id if node.parent_node else None,
        })
    
    ownerships_data = []
    for ownership in ownerships:
        ownerships_data.append({
            'id': ownership.id,
            'owner_type': 'party' if ownership.owner_party else 'node',
            'owner_id': ownership.owner_party.id if ownership.owner_party else ownership.owner_node.id,
            'owner_name': ownership.get_owner_name(),
            'owned_node_id': ownership.owned_node.id,
            'ownership_percentage': float(ownership.ownership_percentage),
            'owned_shares': ownership.owned_shares,
            'share_value_usd': float(ownership.share_value_usd),
        })
    
    # Buscar entidades e parties disponíveis
    available_entities = Entity.objects.all().order_by('name')
    available_parties = Party.objects.all().order_by('name')
    
    context = {
        'title': f'Editar Estrutura: {structure.name}',
        'structure': structure,
        'nodes_data': json.dumps(nodes_data),
        'ownerships_data': json.dumps(ownerships_data),
        'available_entities': available_entities,
        'available_parties': available_parties,
    }
    
    return render(request, 'admin/corporate/organogram_builder_structure.html', context)


@csrf_exempt
@staff_member_required
def organogram_builder_api(request):
    """API para operações do organogram builder"""
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'create_structure':
                return create_structure_api(data)
            elif action == 'add_node':
                return add_node_api(data)
            elif action == 'update_node':
                return update_node_api(data)
            elif action == 'delete_node':
                return delete_node_api(data)
            elif action == 'add_ownership':
                return add_ownership_api(data)
            elif action == 'update_ownership':
                return update_ownership_api(data)
            elif action == 'delete_ownership':
                return delete_ownership_api(data)
            else:
                return JsonResponse({'success': False, 'error': 'Ação não reconhecida'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método não permitido'})


def create_structure_api(data):
    """Criar nova estrutura"""
    try:
        with transaction.atomic():
            structure = Structure.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                structure_type=data.get('structure_type', 'HOLDING'),
                status='ACTIVE'
            )
            
            return JsonResponse({
                'success': True,
                'structure_id': structure.id,
                'message': f'Estrutura "{structure.name}" criada com sucesso'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def add_node_api(data):
    """Adicionar node à estrutura"""
    try:
        with transaction.atomic():
            structure = Structure.objects.get(id=data['structure_id'])
            entity_template = Entity.objects.get(id=data['entity_template_id'])
            
            # Determinar nível
            level = 1
            if data.get('parent_node_id'):
                parent_node = StructureNode.objects.get(id=data['parent_node_id'])
                level = parent_node.level + 1
            
            node = StructureNode.objects.create(
                entity_template=entity_template,
                structure=structure,
                custom_name=data['custom_name'],
                total_shares=data.get('total_shares', 1000),
                corporate_name=data.get('corporate_name', ''),
                level=level,
                parent_node_id=data.get('parent_node_id')
            )
            
            return JsonResponse({
                'success': True,
                'node_id': node.id,
                'message': f'Node "{node.custom_name}" adicionado com sucesso'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def add_ownership_api(data):
    """Adicionar relacionamento de ownership"""
    try:
        with transaction.atomic():
            owned_node = StructureNode.objects.get(id=data['owned_node_id'])
            
            ownership_data = {
                'owned_node': owned_node,
                'ownership_percentage': data['ownership_percentage'],
                'owned_shares': data.get('owned_shares', 0),
                'share_value_usd': data.get('share_value_usd', 0),
            }
            
            # Determinar tipo de owner
            if data.get('owner_party_id'):
                ownership_data['owner_party'] = Party.objects.get(id=data['owner_party_id'])
            elif data.get('owner_node_id'):
                ownership_data['owner_node'] = StructureNode.objects.get(id=data['owner_node_id'])
            else:
                return JsonResponse({'success': False, 'error': 'Owner não especificado'})
            
            ownership = NodeOwnership.objects.create(**ownership_data)
            
            return JsonResponse({
                'success': True,
                'ownership_id': ownership.id,
                'message': 'Relacionamento de ownership criado com sucesso'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def update_node_api(data):
    """Atualizar node existente"""
    try:
        with transaction.atomic():
            node = StructureNode.objects.get(id=data['node_id'])
            
            # Atualizar campos
            if 'custom_name' in data:
                node.custom_name = data['custom_name']
            if 'total_shares' in data:
                node.total_shares = data['total_shares']
            if 'corporate_name' in data:
                node.corporate_name = data['corporate_name']
            
            node.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Node "{node.custom_name}" atualizado com sucesso'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def update_ownership_api(data):
    """Atualizar ownership existente"""
    try:
        with transaction.atomic():
            ownership = NodeOwnership.objects.get(id=data['ownership_id'])
            
            # Atualizar campos
            if 'ownership_percentage' in data:
                ownership.ownership_percentage = data['ownership_percentage']
            if 'owned_shares' in data:
                ownership.owned_shares = data['owned_shares']
            if 'share_value_usd' in data:
                ownership.share_value_usd = data['share_value_usd']
            
            ownership.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Ownership atualizado com sucesso'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def delete_node_api(data):
    """Deletar node"""
    try:
        with transaction.atomic():
            node = StructureNode.objects.get(id=data['node_id'])
            node_name = node.custom_name
            node.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Node "{node_name}" removido com sucesso'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def delete_ownership_api(data):
    """Deletar ownership"""
    try:
        with transaction.atomic():
            ownership = NodeOwnership.objects.get(id=data['ownership_id'])
            ownership.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Ownership removido com sucesso'
            })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
def get_structure_data_api(request, structure_id):
    """API para buscar dados de uma estrutura específica"""
    try:
        structure = get_object_or_404(Structure, id=structure_id)
        
        # Buscar nodes
        nodes = StructureNode.objects.filter(structure=structure).select_related('entity_template')
        nodes_data = []
        for node in nodes:
            nodes_data.append({
                'id': node.id,
                'custom_name': node.custom_name,
                'entity_template_name': node.entity_template.name,
                'level': node.level,
                'total_shares': node.total_shares,
                'parent_node_id': node.parent_node.id if node.parent_node else None,
            })
        
        # Buscar ownerships
        ownerships = NodeOwnership.objects.filter(owned_node__structure=structure)
        ownerships_data = []
        for ownership in ownerships:
            ownerships_data.append({
                'id': ownership.id,
                'owner_name': ownership.get_owner_name(),
                'owned_node_id': ownership.owned_node.id,
                'ownership_percentage': float(ownership.ownership_percentage),
                'owned_shares': ownership.owned_shares,
            })
        
        return JsonResponse({
            'success': True,
            'structure': {
                'id': structure.id,
                'name': structure.name,
                'description': structure.description,
            },
            'nodes': nodes_data,
            'ownerships': ownerships_data,
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

