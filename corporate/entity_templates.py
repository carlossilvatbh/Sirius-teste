"""
Entity Templates System - Fase 2
Sistema de templates pré-definidos para criação rápida de entities
"""

from django.db import models
from .models import Entity
import json

class EntityTemplate(models.Model):
    """Templates pré-definidos para criação rápida de entities"""
    
    TEMPLATE_CATEGORIES = [
        ('corporate', 'Corporate Structures'),
        ('holding', 'Holding Companies'),
        ('trust', 'Trust Structures'),
        ('partnership', 'Partnership Entities'),
        ('foundation', 'Foundation Structures'),
        ('llc', 'LLC Structures'),
    ]
    
    JURISDICTIONS = [
        ('bahamas', 'Bahamas'),
        ('bvi', 'British Virgin Islands'),
        ('cayman', 'Cayman Islands'),
        ('nevis', 'Nevis'),
        ('delaware', 'Delaware, USA'),
        ('nevada', 'Nevada, USA'),
        ('wyoming', 'Wyoming, USA'),
        ('singapore', 'Singapore'),
        ('hong_kong', 'Hong Kong'),
        ('switzerland', 'Switzerland'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Template Name")
    category = models.CharField(max_length=50, choices=TEMPLATE_CATEGORIES, verbose_name="Category")
    jurisdiction = models.CharField(max_length=50, choices=JURISDICTIONS, verbose_name="Jurisdiction")
    description = models.TextField(verbose_name="Description")
    
    # Template data structure
    entity_type = models.CharField(max_length=100, verbose_name="Entity Type")
    default_name_pattern = models.CharField(max_length=200, verbose_name="Default Name Pattern")
    
    # JSON fields for template configuration
    default_attributes = models.JSONField(default=dict, verbose_name="Default Attributes")
    required_documents = models.JSONField(default=list, verbose_name="Required Documents")
    typical_uses = models.JSONField(default=list, verbose_name="Typical Uses")
    
    # Metadata
    usage_count = models.IntegerField(default=0, verbose_name="Usage Count")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "🏭 Entity Template"
        verbose_name_plural = "🏭 Entity Templates"
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_jurisdiction_display()})"
    
    def increment_usage(self):
        """Incrementa contador de uso do template"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def create_entity_from_template(self, custom_name=None, custom_attributes=None):
        """Cria uma nova entity baseada neste template"""
        entity_name = custom_name or self.generate_default_name()
        
        # Merge default attributes with custom ones
        attributes = self.default_attributes.copy()
        if custom_attributes:
            attributes.update(custom_attributes)
        
        entity = Entity.objects.create(
            name=entity_name,
            entity_type=self.entity_type,
            jurisdiction=self.jurisdiction,
            **attributes
        )
        
        # Increment usage counter
        self.increment_usage()
        
        return entity
    
    def generate_default_name(self):
        """Gera nome padrão baseado no pattern"""
        import random
        import string
        
        # Replace placeholders in pattern
        name = self.default_name_pattern
        
        # Replace {random} with random string
        if '{random}' in name:
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            name = name.replace('{random}', random_str)
        
        # Replace {jurisdiction} with jurisdiction name
        if '{jurisdiction}' in name:
            name = name.replace('{jurisdiction}', self.get_jurisdiction_display())
        
        # Replace {type} with entity type
        if '{type}' in name:
            name = name.replace('{type}', self.entity_type)
        
        return name


class QuickAddPreset(models.Model):
    """Presets para quick add de entities comuns"""
    
    name = models.CharField(max_length=200, verbose_name="Preset Name")
    template = models.ForeignKey(EntityTemplate, on_delete=models.CASCADE, verbose_name="Base Template")
    
    # Quick add specific fields
    quick_name_prefix = models.CharField(max_length=100, blank=True, verbose_name="Quick Name Prefix")
    auto_number = models.BooleanField(default=True, verbose_name="Auto Number")
    
    # Preset attributes
    preset_attributes = models.JSONField(default=dict, verbose_name="Preset Attributes")
    
    # Usage tracking
    usage_count = models.IntegerField(default=0, verbose_name="Usage Count")
    is_favorite = models.BooleanField(default=False, verbose_name="Is Favorite")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "⚡ Quick Add Preset"
        verbose_name_plural = "⚡ Quick Add Presets"
        ordering = ['-is_favorite', '-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} (Quick Add)"
    
    def create_quick_entity(self, custom_suffix=None):
        """Cria entity rapidamente usando este preset"""
        # Generate name
        if self.auto_number:
            count = Entity.objects.filter(
                name__startswith=self.quick_name_prefix
            ).count() + 1
            entity_name = f"{self.quick_name_prefix} {count:03d}"
        else:
            entity_name = self.quick_name_prefix
        
        if custom_suffix:
            entity_name += f" {custom_suffix}"
        
        # Create entity using template
        entity = self.template.create_entity_from_template(
            custom_name=entity_name,
            custom_attributes=self.preset_attributes
        )
        
        # Increment usage
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
        
        return entity


# Predefined templates data
PREDEFINED_TEMPLATES = [
    {
        'name': 'Bahamas IBC Standard',
        'category': 'corporate',
        'jurisdiction': 'bahamas',
        'entity_type': 'International Business Company',
        'default_name_pattern': '{jurisdiction} Holdings {random} Ltd.',
        'description': 'Standard Bahamas International Business Company for holding purposes',
        'default_attributes': {
            'authorized_shares': 50000,
            'share_class': 'Ordinary',
            'par_value': 'No Par Value',
            'registered_office_required': True,
            'minimum_directors': 1,
            'minimum_shareholders': 1,
        },
        'required_documents': [
            'Certificate of Incorporation',
            'Memorandum and Articles of Association',
            'Register of Directors',
            'Register of Shareholders',
        ],
        'typical_uses': [
            'International holding company',
            'Investment vehicle',
            'Asset protection',
            'Tax planning structure',
        ]
    },
    {
        'name': 'Delaware LLC Standard',
        'category': 'llc',
        'jurisdiction': 'delaware',
        'entity_type': 'Limited Liability Company',
        'default_name_pattern': '{random} {jurisdiction} LLC',
        'description': 'Standard Delaware LLC for business operations',
        'default_attributes': {
            'management_type': 'Member-managed',
            'duration': 'Perpetual',
            'registered_agent_required': True,
            'minimum_members': 1,
        },
        'required_documents': [
            'Certificate of Formation',
            'Operating Agreement',
            'Registered Agent Appointment',
        ],
        'typical_uses': [
            'Business operations',
            'Real estate holding',
            'Investment activities',
            'Joint ventures',
        ]
    },
    {
        'name': 'Nevis LLC Privacy',
        'category': 'llc',
        'jurisdiction': 'nevis',
        'entity_type': 'Limited Liability Company',
        'default_name_pattern': 'Nevis {random} LLC',
        'description': 'Nevis LLC with enhanced privacy features',
        'default_attributes': {
            'privacy_enhanced': True,
            'asset_protection': True,
            'charging_order_protection': True,
            'minimum_members': 1,
        },
        'required_documents': [
            'Articles of Organization',
            'Operating Agreement',
            'Registered Agent Appointment',
        ],
        'typical_uses': [
            'Asset protection',
            'Privacy planning',
            'International business',
            'Investment holding',
        ]
    },
    {
        'name': 'BVI Company Standard',
        'category': 'corporate',
        'jurisdiction': 'bvi',
        'entity_type': 'Business Company',
        'default_name_pattern': '{random} {jurisdiction} Ltd.',
        'description': 'Standard BVI Business Company',
        'default_attributes': {
            'authorized_shares': 50000,
            'share_class': 'Ordinary',
            'par_value': 'USD 1.00',
            'minimum_directors': 1,
            'minimum_shareholders': 1,
        },
        'required_documents': [
            'Certificate of Incorporation',
            'Memorandum and Articles of Association',
            'Register of Directors',
            'Register of Members',
        ],
        'typical_uses': [
            'International trading',
            'Holding company',
            'Investment vehicle',
            'Joint ventures',
        ]
    },
]


def create_predefined_templates():
    """Cria templates pré-definidos no banco de dados"""
    for template_data in PREDEFINED_TEMPLATES:
        template, created = EntityTemplate.objects.get_or_create(
            name=template_data['name'],
            jurisdiction=template_data['jurisdiction'],
            defaults=template_data
        )
        if created:
            print(f"Created template: {template.name}")
        else:
            print(f"Template already exists: {template.name}")


def create_quick_add_presets():
    """Cria presets de quick add baseados nos templates"""
    presets_data = [
        {
            'name': 'Quick Bahamas Holding',
            'template_name': 'Bahamas IBC Standard',
            'quick_name_prefix': 'Bahamas Holdings',
            'preset_attributes': {'purpose': 'Holding Company'}
        },
        {
            'name': 'Quick Delaware LLC',
            'template_name': 'Delaware LLC Standard', 
            'quick_name_prefix': 'Delaware',
            'preset_attributes': {'purpose': 'Business Operations'}
        },
        {
            'name': 'Quick Nevis Privacy LLC',
            'template_name': 'Nevis LLC Privacy',
            'quick_name_prefix': 'Nevis Privacy',
            'preset_attributes': {'purpose': 'Asset Protection'}
        },
    ]
    
    for preset_data in presets_data:
        try:
            template = EntityTemplate.objects.get(name=preset_data['template_name'])
            preset, created = QuickAddPreset.objects.get_or_create(
                name=preset_data['name'],
                defaults={
                    'template': template,
                    'quick_name_prefix': preset_data['quick_name_prefix'],
                    'preset_attributes': preset_data['preset_attributes'],
                    'is_favorite': True,
                }
            )
            if created:
                print(f"Created preset: {preset.name}")
        except EntityTemplate.DoesNotExist:
            print(f"Template not found: {preset_data['template_name']}")

