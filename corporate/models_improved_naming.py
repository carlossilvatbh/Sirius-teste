"""
Models com nomenclatura otimizada para melhor UX
Implementação da Fase 1: Meta Classes sem risco
"""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Entity(models.Model):
    """
    Template de Entidade Legal (Entity Template)
    Representa templates reutilizáveis como Wyoming LLC, Bahamas Fund
    """

    ENTITY_TYPES = [
        ("TRUST", "Trust"),
        ("FOREIGN_TRUST", "Foreign Trust"),
        ("FUND", "Fund"),
        ("IBC", "International Business Company"),
        ("LLC_DISREGARDED", "LLC Disregarded Entity"),
        ("LLC_PARTNERSHIP", "LLC Partnership"),
        ("LLC_AS_CORP", "LLC as a Corp"),
        ("CORP", "Corp"),
        ("WYOMING_FOUNDATION", "Wyoming Statutory Foundation"),
    ]

    TAX_CLASSIFICATION_CHOICES = [
        ("TRUST", "Trust"),
        ("FOREIGN_TRUST", "Foreign Trust"),
        ("FUND", "Fund"),
        ("US_CORP", "US Corp"),
        ("OFFSHORE_CORP", "Offshore Corp"),
        ("LLC_DISREGARDED_ENTITY", "LLC Disregarded Entity"),
        ("LLC_PARTNERSHIP", "LLC Partnership"),
        ("VIRTUAL_ASSET", "Virtual Asset"),
    ]

    JURISDICTIONS = [
        ("US", "Estados Unidos"),
        ("BS", "Bahamas"),
        ("BR", "Brasil"),
        ("BZ", "Belize"),
        ("VG", "Ilhas Virgens Britânicas"),
        ("KY", "Ilhas Cayman"),
        ("PA", "Panamá"),
    ]

    # Basic Information
    name = models.CharField(
        max_length=100, 
        help_text="Nome do template de entidade (ex: Wyoming DAO LLC)",
        verbose_name="Nome do Template"
    )
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPES,
        help_text="Tipo de entidade legal",
        default="CORP",
        verbose_name="Tipo de Entidade"
    )

    # Tax classification
    tax_classification = models.CharField(
        max_length=50,
        choices=TAX_CLASSIFICATION_CHOICES,
        blank=True,
        help_text="Classificação fiscal desta entidade",
        verbose_name="Classificação Fiscal"
    )

    # Template Management
    implementation_templates = models.TextField(
        blank=True,
        help_text="Templates de implementação (formato texto)",
        verbose_name="Templates de Implementação"
    )

    # Shares Information
    total_shares = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Número total de shares padrão para esta entidade",
        verbose_name="Total de Shares Padrão"
    )

    # Jurisdiction Information
    jurisdiction = models.CharField(
        max_length=10,
        choices=JURISDICTIONS,
        default="US",
        help_text="Jurisdição principal",
        verbose_name="Jurisdição"
    )

    # Implementation Details
    implementation_time = models.IntegerField(
        help_text="Tempo de implementação em dias",
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        default=30,
        verbose_name="Tempo de Implementação (dias)"
    )
    complexity = models.IntegerField(
        choices=[(i, f"Nível {i}") for i in range(1, 6)],
        help_text="Nível de complexidade de 1 (simples) a 5 (muito complexo)",
        default=3,
        verbose_name="Nível de Complexidade"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Template de Entidade"
        verbose_name_plural = "Templates de Entidades"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

    def get_jurisdiction_display_pt(self):
        """Retorna jurisdição em português"""
        jurisdiction_map = {
            "US": "Estados Unidos",
            "BS": "Bahamas", 
            "BR": "Brasil",
            "BZ": "Belize",
            "VG": "Ilhas Virgens Britânicas",
            "KY": "Ilhas Cayman",
            "PA": "Panamá"
        }
        return jurisdiction_map.get(self.jurisdiction, self.jurisdiction)


class Structure(models.Model):
    """
    Estrutura Corporativa
    Representa uma estrutura corporativa completa
    """

    STRUCTURE_TYPES = [
        ("HOLDING", "Holding"),
        ("TRUST", "Trust"),
        ("FUND", "Fund"),
        ("MIXED", "Mista"),
        ("FAMILY_OFFICE", "Family Office"),
    ]

    STATUS_CHOICES = [
        ("DRAFTING", "Em Elaboração"),
        ("ACTIVE", "Ativa"),
        ("INACTIVE", "Inativa"),
        ("ARCHIVED", "Arquivada"),
    ]

    name = models.CharField(
        max_length=200,
        help_text="Nome da estrutura corporativa",
        verbose_name="Nome da Estrutura"
    )
    description = models.TextField(
        blank=True,
        help_text="Descrição detalhada da estrutura",
        verbose_name="Descrição"
    )
    structure_type = models.CharField(
        max_length=50,
        choices=STRUCTURE_TYPES,
        default="HOLDING",
        help_text="Tipo de estrutura corporativa",
        verbose_name="Tipo de Estrutura"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFTING",
        help_text="Status atual da estrutura",
        verbose_name="Status"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Estrutura Corporativa"
        verbose_name_plural = "Estruturas Corporativas"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_structure_type_display()})"

    def get_total_nodes(self):
        """Retorna total de nodes na estrutura"""
        return self.structurenode_set.count()

    def get_total_ownerships(self):
        """Retorna total de relacionamentos de ownership"""
        return NodeOwnership.objects.filter(owned_node__structure=self).count()

    def get_max_level(self):
        """Retorna o nível máximo da estrutura"""
        max_level = self.structurenode_set.aggregate(
            max_level=models.Max('level')
        )['max_level']
        return max_level or 0


class StructureNode(models.Model):
    """
    Instância de Empresa
    Representa uma instância específica de um template de entidade dentro de uma estrutura
    """

    entity_template = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        help_text="Template de entidade utilizado",
        verbose_name="Template de Entidade"
    )
    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        help_text="Estrutura à qual esta instância pertence",
        verbose_name="Estrutura"
    )
    custom_name = models.CharField(
        max_length=200,
        help_text="Nome customizado para esta instância (ex: Holding Principal)",
        verbose_name="Nome Customizado"
    )
    corporate_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nome corporativo oficial (ex: ABC Holdings LLC)",
        verbose_name="Nome Corporativo"
    )
    total_shares = models.PositiveIntegerField(
        default=1000,
        help_text="Total de shares desta instância",
        verbose_name="Total de Shares"
    )
    level = models.PositiveIntegerField(
        default=1,
        help_text="Nível hierárquico na estrutura (1 = topo)",
        verbose_name="Nível Hierárquico"
    )
    parent_node = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Node pai na hierarquia",
        verbose_name="Node Pai"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Instância de Empresa"
        verbose_name_plural = "Instâncias de Empresas"
        ordering = ['structure', 'level', 'custom_name']
        unique_together = ['structure', 'custom_name']

    def __str__(self):
        return f"{self.custom_name} ({self.entity_template.name})"

    def get_ownership_percentage_owned(self):
        """Retorna percentual total de ownership que esta instância possui"""
        total = self.nodeownership_set.aggregate(
            total=models.Sum('ownership_percentage')
        )['total']
        return total or 0

    def get_children_nodes(self):
        """Retorna nodes filhos"""
        return StructureNode.objects.filter(parent_node=self)

    def get_total_value_usd(self):
        """Retorna valor total em USD baseado nos ownerships"""
        ownerships = NodeOwnership.objects.filter(owned_node=self)
        total = sum(o.owned_shares * o.share_value_usd for o in ownerships)
        return total


class NodeOwnership(models.Model):
    """
    Relacionamento de Propriedade
    Representa relacionamentos de ownership entre parties e instâncias de empresas
    """

    # Owner pode ser Party ou outro StructureNode
    owner_party = models.ForeignKey(
        'parties.Party',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Sócio pessoa física/jurídica proprietário",
        verbose_name="Sócio Proprietário"
    )
    owner_node = models.ForeignKey(
        StructureNode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='owned_nodes',
        help_text="Empresa proprietária (para ownership entre empresas)",
        verbose_name="Empresa Proprietária"
    )

    # Owned node
    owned_node = models.ForeignKey(
        StructureNode,
        on_delete=models.CASCADE,
        related_name='ownership_received',
        help_text="Empresa que é propriedade",
        verbose_name="Empresa Propriedade"
    )

    # Ownership details
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentual de propriedade (0-100%)",
        verbose_name="Percentual de Propriedade (%)"
    )
    owned_shares = models.PositiveIntegerField(
        default=0,
        help_text="Número de shares possuídas",
        verbose_name="Shares Possuídas"
    )
    share_value_usd = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Valor por share em USD",
        verbose_name="Valor por Share (USD)"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Relacionamento de Propriedade"
        verbose_name_plural = "Relacionamentos de Propriedade"
        ordering = ['-ownership_percentage']

    def __str__(self):
        owner_name = self.get_owner_name()
        return f"{owner_name} → {self.owned_node.custom_name} ({self.ownership_percentage}%)"

    def clean(self):
        """Validação customizada"""
        # Deve ter exatamente um owner (party ou node)
        if not self.owner_party and not self.owner_node:
            raise ValidationError("Deve especificar um proprietário (sócio ou empresa)")
        
        if self.owner_party and self.owner_node:
            raise ValidationError("Não pode ter tanto sócio quanto empresa como proprietário")

        # Validar que ownership não excede 100% para o node
        total_ownership = NodeOwnership.objects.filter(
            owned_node=self.owned_node
        ).exclude(id=self.id).aggregate(
            total=models.Sum('ownership_percentage')
        )['total'] or 0
        
        if total_ownership + self.ownership_percentage > 100:
            raise ValidationError(
                f"Ownership total excederia 100%. Atual: {total_ownership}%, "
                f"Tentando adicionar: {self.ownership_percentage}%"
            )

    def get_owner_name(self):
        """Retorna nome do proprietário"""
        if self.owner_party:
            return self.owner_party.name
        elif self.owner_node:
            return self.owner_node.custom_name
        return "Proprietário não definido"

    def get_total_value_usd(self):
        """Retorna valor total deste ownership em USD"""
        return self.owned_shares * self.share_value_usd


class EntityOwnership(models.Model):
    """
    Registro Legado de Propriedade
    Sistema antigo de ownership - mantido para compatibilidade
    """

    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        help_text="Estrutura relacionada",
        verbose_name="Estrutura"
    )
    owned_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='ownership_received_legacy',
        help_text="Entidade que é propriedade",
        verbose_name="Entidade Propriedade"
    )
    owner_ubo = models.ForeignKey(
        'parties.Party',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="UBO proprietário",
        verbose_name="UBO Proprietário"
    )
    owner_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='ownership_given_legacy',
        help_text="Entidade proprietária",
        verbose_name="Entidade Proprietária"
    )
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentual de propriedade",
        verbose_name="Percentual de Propriedade (%)"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Registro Legado de Propriedade"
        verbose_name_plural = "Registros Legados de Propriedade"
        ordering = ['-created_at']

    def __str__(self):
        owner_name = self.owner_ubo.name if self.owner_ubo else self.owner_entity.name
        return f"{owner_name} → {self.owned_entity.name} ({self.ownership_percentage}%)"

