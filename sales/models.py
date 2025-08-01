from django.core.exceptions import ValidationError
from django.db import models


class Partner(models.Model):
    """
    Business partners (formerly Client)
    Links to Party in parties app
    """

    party = models.OneToOneField('parties.Party', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=120)
    address = models.TextField()

    # Additional partner-specific fields
    partnership_start_date = models.DateField(auto_now_add=True)
    partnership_status = models.CharField(
        max_length=20,
        choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')],
        default='ACTIVE'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"
        ordering = ["company_name"]
        indexes = [
            models.Index(fields=["partnership_status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.company_name


class Contact(models.Model):
    """
    Contacts within partners (moved from corporate_relationship)
    """

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=80)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["partner"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.partner.company_name}"


class StructureRequest(models.Model):
    """
    Requests for Corporate team to build structures
    """

    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('IN_REVIEW', 'In Review'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    ]

    description = models.TextField(help_text="Detailed description of requested structure")

    # At least one party required
    requesting_parties = models.ManyToManyField(
        'parties.Party', 
        help_text="Parties requesting the structure"
    )

    # Point of contact
    point_of_contact_party = models.ForeignKey(
        'parties.Party',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='poc_requests'
    )
    point_of_contact_partner = models.ForeignKey(
        Partner,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='poc_requests'
    )
    point_of_contact_contact = models.ForeignKey(
        Contact,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Specific contact within partner"
    )

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Structure Request"
        verbose_name_plural = "Structure Requests"
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self):
        return f"Structure Request #{self.pk} - {self.get_status_display()}"

    def clean(self):
        # Validate point of contact selection
        poc_count = sum([
            bool(self.point_of_contact_party),
            bool(self.point_of_contact_partner),
            bool(self.point_of_contact_contact)
        ])
        if poc_count != 1:
            raise ValidationError("Must specify exactly one point of contact")


class StructureApproval(models.Model):
    """
    Approval workflow for structures
    Read-only view of structure details with approval actions
    """

    APPROVAL_ACTIONS = [
        ('APPROVED', 'Approved'),
        ('APPROVED_WITH_PRICE_CHANGE', 'Approved with Price Change'),
        ('NEED_CORRECTION', 'Need Correction'),
        ('REJECTED', 'Rejected'),
    ]

    structure = models.OneToOneField('corporate.Structure', on_delete=models.CASCADE)
    action = models.CharField(max_length=30, choices=APPROVAL_ACTIONS)

    # Action-specific fields
    approver = models.ForeignKey(
        'parties.Party',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Who approved (for APPROVED actions)"
    )
    final_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final price (for APPROVED_WITH_PRICE_CHANGE)"
    )
    correction_comment = models.TextField(
        blank=True,
        help_text="Comment for corrections needed (for NEED_CORRECTION)"
    )
    rejector = models.ForeignKey(
        'parties.Party',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rejected_structures',
        help_text="Who rejected (for REJECTED)"
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (for REJECTED)"
    )

    # Metadata
    action_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        help_text="System user who processed the approval"
    )

    class Meta:
        verbose_name = "Structure Approval"
        verbose_name_plural = "Structure Approvals"
        ordering = ["-action_date"]
        indexes = [
            models.Index(fields=["structure"]),
            models.Index(fields=["action"]),
            models.Index(fields=["action_date"]),
        ]

    def __str__(self):
        return f"{self.structure.name} - {self.get_action_display()}"


# Keep existing models that are still needed but will be migrated later

class Product(models.Model):
    """
    Produto comercial que conecta duas ou mais Legal Structures
    This model will be migrated to corporate.Structure in later phases
    """

    COMPLEXIDADE_PRODUCT = [
        ("BASIC", "Basic Configuration"),
        ("INTERMEDIATE", "Intermediate Configuration"),
        ("ADVANCED", "Advanced Configuration"),
        ("EXPERT", "Expert Configuration"),
    ]

    # Campos básicos
    nome = models.CharField(max_length=100, help_text="Nome do produto")
    complexidade_template = models.CharField(
        max_length=20,
        choices=COMPLEXIDADE_PRODUCT,
        default="BASIC",
        help_text="Nível de complexidade",
    )
    descricao = models.TextField(help_text="Descrição detalhada do produto")

    # Novos campos comerciais
    commercial_name = models.CharField(
        max_length=200, help_text="Nome comercial do produto (texto livre)"
    )
    master_agreement_url = models.URLField(
        help_text="URL para documento de Master Agreement"
    )

    # Hierarquia de Legal Structures
    legal_structures = models.ManyToManyField(
        "corporate.Entity",  # Updated to use Entity instead of Structure
        through="ProductHierarchy",
        through_fields=("product", "structure"),
        help_text="Legal entities included in this product",
    )

    # Configuração e custos
    custo_automatico = models.BooleanField(
        default=True,
        help_text="Se True, custo é calculado automaticamente das estruturas",
    )
    custo_manual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custo manual (usado quando custo_automatico=False)",
    )

    # Campos de implementação
    tempo_total_implementacao = models.IntegerField(
        help_text="Tempo total de implementação em dias"
    )
    uso_count = models.IntegerField(
        default=0, help_text="Número de vezes que este produto foi usado"
    )
    publico_alvo = models.TextField(
        blank=True, help_text="Público-alvo do produto"
    )
    casos_uso = models.TextField(blank=True, help_text="Casos de uso comuns")

    # Metadados
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product (Legacy)"
        verbose_name_plural = "Products (Legacy)"
        ordering = ["-uso_count", "commercial_name"]
        indexes = [
            models.Index(fields=["commercial_name"]),
            models.Index(fields=["ativo"]),
        ]

    def __str__(self):
        return f"{self.commercial_name} ({self.nome})"

    def get_custo_total(self):
        """Calcula custo total do produto"""
        if not self.custo_automatico and self.custo_manual:
            return self.custo_manual

        # Calcular automaticamente baseado nas estruturas
        total = 0
        for hierarchy in self.producthierarchy_set.all():
            # Note: This will need to be updated when Entity pricing is implemented
            total += 0  # Placeholder - will be calculated from financial_department

        return total


class ProductHierarchy(models.Model):
    """
    Hierarquia de Legal Structures dentro de um Product
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        help_text="Product that contains this structure",
    )
    structure = models.ForeignKey(
        "corporate.Entity",  # Updated to use Entity instead of Structure
        on_delete=models.CASCADE,
        help_text="Legal entity included in the product",
    )
    order = models.PositiveIntegerField(
        help_text="Order of this structure in the product hierarchy"
    )

    # Configuração específica da estrutura no produto
    custom_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custom cost for this structure in this product",
    )
    notes = models.TextField(
        blank=True,
        help_text="Specific notes for this structure in this product",
    )

    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product Hierarchy (Legacy)"
        verbose_name_plural = "Product Hierarchies (Legacy)"
        ordering = ["product", "order"]
        unique_together = [["product", "structure"], ["product", "order"]]
        indexes = [
            models.Index(fields=["product", "order"]),
        ]

    def __str__(self):
        return (
            f"{self.product.commercial_name} - "
            f"{self.structure.name} (#{self.order})"
        )

    def get_effective_cost(self):
        """Retorna o custo efetivo da estrutura no produto"""
        if self.custom_cost:
            return self.custom_cost
        # Note: This will need to be updated when Entity pricing is implemented
        return 0  # Placeholder


class PersonalizedProduct(models.Model):
    """
    Produto personalizado que representa Products ou Legal Structures
    """

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("ACTIVE", "Active"),
        ("INACTIVE", "Inactive"),
        ("ARCHIVED", "Archived"),
        ("APPROVED", "Approved"),  # Novo status conforme especificação
    ]

    # Informações básicas
    nome = models.CharField(
        max_length=200, help_text="Nome do produto personalizado"
    )
    descricao = models.TextField(
        blank=True, help_text="Descrição detalhada do produto personalizado"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
        help_text="Status atual do produto personalizado",
    )

    # Relacionamentos base (um dos dois deve ser preenchido)
    base_product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Product base para este produto personalizado",
    )
    base_structure = models.ForeignKey(
        "corporate.Entity",  # Updated to use Entity instead of Structure
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Legal Entity base para este produto personalizado",
    )

    # Versionamento
    version_number = models.PositiveIntegerField(
        default=1, help_text="Número da versão (incrementado automaticamente)"
    )
    parent_version = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_versions",
        help_text="Versão anterior deste produto personalizado",
    )

    # Configuração personalizada (agora opcional)
    configuracao_personalizada = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configurações específicas deste produto personalizado",
    )

    # Novo campo: custom_configuration (substitui configuracao_personalizada)
    custom_configuration = models.JSONField(
        blank=True,
        null=True,
        help_text="Custom configuration for this personalized product",
    )

    # Custos personalizados
    custo_personalizado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Custo personalizado (sobrescreve cálculo automático)",
    )

    # Observações e notas
    observacoes = models.TextField(
        blank=True, help_text="Observações e notas específicas"
    )

    # Metadados
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personalized Product"
        verbose_name_plural = "Personalized Products"
        ordering = ["-version_number", "-created_at"]
        indexes = [
            models.Index(fields=["base_product"]),
            models.Index(fields=["base_structure"]),
            models.Index(fields=["status"]),
            models.Index(fields=["version_number"]),
            models.Index(fields=["ativo"]),
        ]

    def __str__(self):
        base_name = ""
        if self.base_product:
            base_name = self.base_product.commercial_name
        elif self.base_structure:
            base_name = self.base_structure.name

        return f"{self.nome} (v{self.version_number}) - {base_name}"

    def clean(self):
        """Validações customizadas"""
        super().clean()

        # Validar que apenas um dos campos base está preenchido
        if self.base_product and self.base_structure:
            raise ValidationError(
                "Produto personalizado deve ter apenas um base "
                "(Product ou Structure)"
            )

        if not self.base_product and not self.base_structure:
            raise ValidationError(
                "Produto personalizado deve ter um base (Product ou Structure)"
            )

    def get_base_object(self):
        """Retorna o objeto base (Product ou Structure)"""
        return self.base_product or self.base_structure

    def get_base_type(self):
        """Retorna o tipo do objeto base"""
        if self.base_product:
            return "Product"
        elif self.base_structure:
            return "Structure"
        return None

    def get_custo_total(self):
        """Calcula custo total considerando personalização"""
        if self.custo_personalizado:
            return self.custo_personalizado

        # Usar custo do objeto base
        base_obj = self.get_base_object()
        if base_obj:
            if hasattr(base_obj, "get_custo_total"):
                return base_obj.get_custo_total()
            # Note: This will need to be updated when Entity pricing is implemented

        return 0

    def save(self, *args, **kwargs):
        """Override save to track status changes for signals"""
        # Store previous status for signal handling
        if self.pk:
            try:
                old_instance = PersonalizedProduct.objects.get(pk=self.pk)
                self._previous_status = old_instance.status
            except PersonalizedProduct.DoesNotExist:
                self._previous_status = None
        else:
            self._previous_status = None

        super().save(*args, **kwargs)

