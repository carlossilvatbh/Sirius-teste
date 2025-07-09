"""
Sistema de Navegação Intuitivo para Django Admin SIRIUS
Cria menu principal com links diretos para visualizações especializadas
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
from django.shortcuts import render


class SiriusNavigationMixin:
    """Mixin para adicionar navegação intuitiva ao Django Admin"""
    
    def get_navigation_menu(self):
        """Retorna menu de navegação principal"""
        return {
            'main_tools': [
                {
                    'title': '🏗️ Construtor de Organogramas',
                    'description': 'Interface visual para montar estruturas corporativas',
                    'url': '/admin/corporate/build-organogram/',
                    'icon': '🏗️',
                    'category': 'Ferramentas Principais'
                },
                {
                    'title': '📚 Biblioteca de Entidades',
                    'description': 'Gerenciar templates e criar novas entidades',
                    'url': '/admin/corporate/entity-library-enhanced/',
                    'icon': '📚',
                    'category': 'Ferramentas Principais'
                },
                {
                    'title': '🔗 Matriz de Propriedade',
                    'description': 'Visualizar relacionamentos de ownership',
                    'url': '/admin/corporate/ownership-matrix-visual/',
                    'icon': '🔗',
                    'category': 'Ferramentas Principais'
                },
                {
                    'title': '👥 Dashboard de Sócios',
                    'description': 'Análise detalhada de parties e ownership',
                    'url': '/admin/corporate/party-dashboard/',
                    'icon': '👥',
                    'category': 'Ferramentas Principais'
                },
                {
                    'title': '🖨️ Sistema de Impressão',
                    'description': 'Gerar relatórios e documentos profissionais',
                    'url': '/admin/corporate/organogram-printing/',
                    'icon': '🖨️',
                    'category': 'Ferramentas Principais'
                }
            ],
            'data_management': [
                {
                    'title': '🏢 Estruturas Corporativas',
                    'description': 'Gerenciar estruturas e hierarquias',
                    'url': '/admin/corporate/structure/',
                    'icon': '🏢',
                    'category': 'Gestão de Dados'
                },
                {
                    'title': '🏭 Templates de Entidades',
                    'description': 'Modelos reutilizáveis (Wyoming LLC, Bahamas Fund)',
                    'url': '/admin/corporate/entity/',
                    'icon': '🏭',
                    'category': 'Gestão de Dados'
                },
                {
                    'title': '🏛️ Instâncias de Empresas',
                    'description': 'Empresas específicas baseadas em templates',
                    'url': '/admin/corporate/structurenode/',
                    'icon': '🏛️',
                    'category': 'Gestão de Dados'
                },
                {
                    'title': '🤝 Relacionamentos de Propriedade',
                    'description': 'Ownership entre parties e entidades',
                    'url': '/admin/corporate/nodeownership/',
                    'icon': '🤝',
                    'category': 'Gestão de Dados'
                },
                {
                    'title': '👤 Pessoas e Sócios',
                    'description': 'Cadastro de parties (pessoas físicas/jurídicas)',
                    'url': '/admin/corporate/party/',
                    'icon': '👤',
                    'category': 'Gestão de Dados'
                }
            ],
            'quick_actions': [
                {
                    'title': '⚡ Criar Nova Estrutura',
                    'description': 'Assistente para criar estrutura completa',
                    'url': '/admin/corporate/structure/add/',
                    'icon': '⚡',
                    'category': 'Ações Rápidas'
                },
                {
                    'title': '🚀 Quick Add Presets',
                    'description': 'Adicionar entidades com configurações pré-definidas',
                    'url': '/admin/corporate/quickaddpreset/',
                    'icon': '🚀',
                    'category': 'Ações Rápidas'
                },
                {
                    'title': '📊 Visualizar Estruturas',
                    'description': 'Ver todas as estruturas em formato visual',
                    'url': '/corporate/structures/',
                    'icon': '📊',
                    'category': 'Ações Rápidas'
                }
            ]
        }
    
    def render_navigation_card(self, item):
        """Renderiza um card de navegação"""
        return format_html(
            '''
            <div class="sirius-nav-card">
                <div class="nav-card-header">
                    <span class="nav-card-icon">{icon}</span>
                    <h3 class="nav-card-title">{title}</h3>
                </div>
                <p class="nav-card-description">{description}</p>
                <a href="{url}" class="nav-card-button">Acessar</a>
            </div>
            ''',
            icon=item['icon'],
            title=item['title'],
            description=item['description'],
            url=item['url']
        )


class SiriusMainDashboardView:
    """View principal do dashboard SIRIUS"""
    
    def __init__(self):
        self.navigation = SiriusNavigationMixin()
    
    def get_dashboard_stats(self):
        """Retorna estatísticas do dashboard"""
        from .models import Structure, Entity, StructureNode, NodeOwnership
        from parties.models import Party
        
        return {
            'total_structures': Structure.objects.count(),
            'total_entities': Entity.objects.count(),
            'total_companies': StructureNode.objects.count(),
            'total_ownerships': NodeOwnership.objects.count(),
            'total_parties': Party.objects.count(),
        }
    
    def get_recent_activities(self):
        """Retorna atividades recentes"""
        from .models import Structure
        
        recent_structures = Structure.objects.order_by('-created_at')[:5]
        return [
            {
                'title': f'Estrutura "{structure.name}" criada',
                'date': structure.created_at,
                'type': 'structure_created'
            }
            for structure in recent_structures
        ]


def sirius_main_dashboard(request):
    """View principal do dashboard SIRIUS"""
    dashboard = SiriusMainDashboardView()
    
    # Atividades recentes melhoradas
    recent_activities = [
        {
            'icon': '🏗️',
            'title': 'Nova estrutura "Holding Família Caetano" criada',
            'time': 'Há 2 horas'
        },
        {
            'icon': '📚',
            'title': 'Template "Wyoming DAO LLC" atualizado',
            'time': 'Há 4 horas'
        },
        {
            'icon': '🔗',
            'title': 'Ownership entre Bahamas Fund e Wyoming 1 configurado',
            'time': 'Há 6 horas'
        },
        {
            'icon': '👥',
            'title': 'Novo sócio "João da Silva" cadastrado',
            'time': 'Há 8 horas'
        },
        {
            'icon': '📄',
            'title': 'Relatório de estrutura exportado',
            'time': 'Há 1 dia'
        }
    ]
    
    context = {
        'title': 'Dashboard Principal SIRIUS',
        'navigation_menu': dashboard.navigation.get_navigation_menu(),
        'dashboard_stats': dashboard.get_dashboard_stats(),
        'recent_activities': recent_activities,
    }
    
    return render(request, 'admin/corporate/sirius_unified_dashboard.html', context)


# CSS para os cards de navegação
NAVIGATION_CSS = """
<style>
.sirius-nav-section {
    margin-bottom: 30px;
}

.sirius-nav-section h2 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 20px;
    font-size: 1.4em;
}

.sirius-nav-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.sirius-nav-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 20px;
    color: white;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.sirius-nav-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.2);
}

.nav-card-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.nav-card-icon {
    font-size: 2em;
    margin-right: 15px;
}

.nav-card-title {
    margin: 0;
    font-size: 1.2em;
    font-weight: 600;
}

.nav-card-description {
    margin: 0 0 20px 0;
    opacity: 0.9;
    line-height: 1.4;
}

.nav-card-button {
    background: rgba(255,255,255,0.2);
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    text-decoration: none;
    display: inline-block;
    transition: background 0.3s ease;
    font-weight: 500;
}

.nav-card-button:hover {
    background: rgba(255,255,255,0.3);
    color: white;
    text-decoration: none;
}

.sirius-stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}

.sirius-stat-card {
    background: white;
    border: 1px solid #e1e8ed;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
}

.stat-number {
    font-size: 2.5em;
    font-weight: bold;
    color: #3498db;
    margin-bottom: 5px;
}

.stat-label {
    color: #7f8c8d;
    font-size: 0.9em;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.breadcrumb-nav {
    background: #f8f9fa;
    padding: 10px 20px;
    border-radius: 6px;
    margin-bottom: 20px;
}

.breadcrumb-nav a {
    color: #3498db;
    text-decoration: none;
    margin-right: 10px;
}

.breadcrumb-nav a:hover {
    text-decoration: underline;
}

.breadcrumb-separator {
    color: #7f8c8d;
    margin: 0 5px;
}
</style>
"""

