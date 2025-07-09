from django.contrib import admin
from .models import Entity, Structure, EntityOwnership, StructureNode, NodeOwnership

# Import the new organogram admin
from .admin_organogram import StructureOrganogramAdmin, EntityLibraryAdmin
from .entity_templates import EntityTemplate, QuickAddPreset

# Register the enhanced admin classes
admin.site.register(Structure, StructureOrganogramAdmin)
admin.site.register(Entity, EntityLibraryAdmin)

# Register template models
@admin.register(EntityTemplate)
class EntityTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'jurisdiction', 'entity_type', 'usage_count', 'is_active']
    list_filter = ['category', 'jurisdiction', 'is_active']
    search_fields = ['name', 'description', 'entity_type']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'jurisdiction', 'entity_type', 'description')
        }),
        ('Template Configuration', {
            'fields': ('default_name_pattern', 'default_attributes', 'required_documents', 'typical_uses')
        }),
        ('Status', {
            'fields': ('is_active', 'usage_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(QuickAddPreset)
class QuickAddPresetAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'quick_name_prefix', 'usage_count', 'is_favorite']
    list_filter = ['template__category', 'template__jurisdiction', 'is_favorite']
    search_fields = ['name', 'template__name', 'quick_name_prefix']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'template')
        }),
        ('Quick Add Configuration', {
            'fields': ('quick_name_prefix', 'auto_number', 'preset_attributes')
        }),
        ('Settings', {
            'fields': ('is_favorite', 'usage_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Register other models
admin.site.register(EntityOwnership)

@admin.register(StructureNode)
class StructureNodeAdmin(admin.ModelAdmin):
    list_display = ['custom_name', 'entity_template', 'structure', 'level', 'total_shares', 'get_ownership_percentage']
    list_filter = ['structure', 'level', 'entity_template__entity_type', 'entity_template__jurisdiction']
    search_fields = ['custom_name', 'corporate_name', 'entity_template__name', 'structure__name']
    readonly_fields = ['created_at', 'updated_at', 'get_ownership_percentage']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('entity_template', 'structure', 'custom_name')
        }),
        ('Instance Configuration', {
            'fields': ('total_shares', 'corporate_name', 'hash_number')
        }),
        ('Hierarchy', {
            'fields': ('level', 'parent_node')
        }),
        ('Status', {
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
    get_ownership_percentage.short_description = 'Total Ownership'

@admin.register(NodeOwnership)
class NodeOwnershipAdmin(admin.ModelAdmin):
    list_display = ['get_owner_name', 'get_owner_type', 'owned_node', 'ownership_percentage', 'owned_shares', 'get_total_value_usd']
    list_filter = ['owned_node__structure', 'owned_node__level', 'ownership_percentage']
    search_fields = ['owner_party__name', 'owner_node__custom_name', 'owned_node__custom_name']
    readonly_fields = ['created_at', 'updated_at', 'get_total_value_usd']
    
    fieldsets = (
        ('Ownership Relationship', {
            'fields': ('owner_party', 'owner_node', 'owned_node')
        }),
        ('Ownership Details', {
            'fields': ('ownership_percentage', 'owned_shares', 'share_value_usd', 'get_total_value_usd')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_owner_name(self, obj):
        return obj.get_owner_name()
    get_owner_name.short_description = 'Owner'
    
    def get_owner_type(self, obj):
        owner_type = obj.get_owner_type()
        if owner_type == "Party":
            return "👤 Party"
        elif owner_type == "Entity":
            return "🏢 Entity"
        return owner_type
    get_owner_type.short_description = 'Type'
    
    def get_total_value_usd(self, obj):
        total = obj.get_total_value_usd()
        return f"${total:,.2f}"
    get_total_value_usd.short_description = 'Total Value (USD)'

