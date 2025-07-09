from django.contrib import admin
from django.utils.html import format_html
from django.urls import path, reverse
from django.http import HttpResponseRedirect
from .models import Entity, Structure, EntityOwnership, StructureNode, NodeOwnership
from parties.models import Party

# Import the new organogram admin
from .admin_organogram import StructureOrganogramAdmin, EntityLibraryAdmin
from .entity_templates import EntityTemplate, QuickAddPreset
from .admin_navigation import sirius_main_dashboard


class SiriusAdminSite(admin.AdminSite):
    """Admin site customizado para SIRIUS com navegação intuitiva"""
    site_header = '🏢 SIRIUS Corporate Management'
    site_title = 'SIRIUS Admin'
    index_title = 'Dashboard Principal'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('sirius-dashboard/', self.admin_view(sirius_main_dashboard), name='sirius_dashboard'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        """Redireciona para o dashboard principal customizado"""
        return HttpResponseRedirect(reverse('admin:sirius_dashboard'))


# Usar o admin site customizado
admin_site = SiriusAdminSite(name='sirius_admin')

# Register the enhanced admin classes with better names
admin.site.register(Structure, StructureOrganogramAdmin)
admin.site.register(Entity, EntityLibraryAdmin)

# Register template models with improved names
@admin.register(EntityTemplate)
class EntityTemplateAdmin(admin.ModelAdmin):
    """Admin para Templates de Entidades Reutilizáveis"""
    list_display = ['name', 'category', 'jurisdiction', 'entity_type', 'usage_count', 'is_active']
    list_filter = ['category', 'jurisdiction', 'is_active']
    search_fields = ['name', 'description', 'entity_type']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('🏭 Informações do Template', {
            'fields': ('name', 'category', 'jurisdiction', 'entity_type', 'description')
        }),
        ('⚙️ Configuração do Template', {
            'fields': ('default_name_pattern', 'default_attributes', 'required_documents', 'typical_uses')
        }),
        ('📊 Status', {
            'fields': ('is_active', 'usage_count')
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(QuickAddPreset)
class QuickAddPresetAdmin(admin.ModelAdmin):
    """Admin para Presets de Adição Rápida"""
    list_display = ['name', 'template', 'quick_name_prefix', 'usage_count', 'is_favorite']
    list_filter = ['template__category', 'template__jurisdiction', 'is_favorite']
    search_fields = ['name', 'template__name', 'quick_name_prefix']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('⚡ Informações do Preset', {
            'fields': ('name', 'template')
        }),
        ('🚀 Configuração Quick Add', {
            'fields': ('quick_name_prefix', 'auto_number', 'preset_attributes')
        }),
        ('⭐ Configurações', {
            'fields': ('is_favorite', 'usage_count')
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Register models with improved names and descriptions
@admin.register(StructureNode)
class CompanyInstanceAdmin(admin.ModelAdmin):
    """Admin para Instâncias de Empresas (baseadas em templates)"""
    list_display = ['custom_name', 'entity_template', 'structure', 'level', 'total_shares', 'get_ownership_percentage']
    list_filter = ['structure', 'level', 'entity_template__entity_type', 'entity_template__jurisdiction']
    search_fields = ['custom_name', 'corporate_name', 'entity_template__name', 'structure__name']
    readonly_fields = ['created_at', 'updated_at', 'get_ownership_percentage']
    
    fieldsets = (
        ('🏛️ Informações da Empresa', {
            'fields': ('entity_template', 'structure', 'custom_name')
        }),
        ('⚙️ Configuração da Instância', {
            'fields': ('total_shares', 'corporate_name', 'hash_number')
        }),
        ('🏗️ Hierarquia', {
            'fields': ('level', 'parent_node')
        }),
        ('📊 Status', {
            'fields': ('get_ownership_percentage', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_ownership_percentage(self, obj):
        """Show total ownership percentage"""
        percentage = obj.get_ownership_percentage()
        if percentage == 100:
            return f"✅ {percentage}%"
        elif percentage > 0:
            return f"⚠️ {percentage}%"
        else:
            return f"❌ {percentage}%"
    get_ownership_percentage.short_description = 'Propriedade Total'

@admin.register(NodeOwnership)
class OwnershipRelationshipAdmin(admin.ModelAdmin):
    """Admin para Relacionamentos de Propriedade"""
    list_display = ['get_owner_name', 'get_owner_type', 'owned_node', 'ownership_percentage', 'owned_shares', 'get_total_value_usd']
    list_filter = ['owned_node__structure', 'owned_node__level', 'ownership_percentage']
    search_fields = ['owner_party__name', 'owner_node__custom_name', 'owned_node__custom_name']
    readonly_fields = ['created_at', 'updated_at', 'get_total_value_usd']
    
    fieldsets = (
        ('🤝 Relacionamento de Propriedade', {
            'fields': ('owner_party', 'owner_node', 'owned_node')
        }),
        ('💰 Detalhes da Propriedade', {
            'fields': ('ownership_percentage', 'owned_shares', 'share_value_usd', 'get_total_value_usd')
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_owner_name(self, obj):
        return obj.get_owner_name()
    get_owner_name.short_description = 'Proprietário'
    
    def get_owner_type(self, obj):
        owner_type = obj.get_owner_type()
        if owner_type == "Party":
            return "👤 Pessoa/Sócio"
        elif owner_type == "Entity":
            return "🏢 Empresa"
        return owner_type
    get_owner_type.short_description = 'Tipo'
    
    def get_total_value_usd(self, obj):
        total = obj.get_total_value_usd()
        return f"${total:,.2f}"
    get_total_value_usd.short_description = 'Valor Total (USD)'

# Register legacy models with improved names
admin.site.register(EntityOwnership)

