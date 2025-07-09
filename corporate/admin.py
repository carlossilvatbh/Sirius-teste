from django.contrib import admin
from .models import Entity, Structure, EntityOwnership

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