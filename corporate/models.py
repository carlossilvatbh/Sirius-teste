from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Entity(models.Model):
    """
    Template de Entidade Legal (Entity Template)
    Representa templates reutilizáveis como Wyoming LLC, Bahamas Fund
    Removed: description field (no longer needed)
    Modified: costs management moved to FINANCIAL_DEPARTMENT app
    Enhanced: template management in Implementation subsection
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
        ("US", "United States"),
        ("BS", "Bahamas"),
        ("BR", "Brazil"),
        ("BZ", "Belize"),
        ("VG", "British Virgin Islands"),
        ("KY", "Cayman Islands"),
        ("PA", "Panama"),
    ]

    US_STATES = [
        ("AL", "Alabama"),
        ("AK", "Alaska"),
        ("AZ", "Arizona"),
        ("AR", "Arkansas"),
        ("CA", "California"),
        ("CO", "Colorado"),
        ("CT", "Connecticut"),
        ("DE", "Delaware"),
        ("FL", "Florida"),
        ("GA", "Georgia"),
        ("HI", "Hawaii"),
        ("ID", "Idaho"),
        ("IL", "Illinois"),
        ("IN", "Indiana"),
        ("IA", "Iowa"),
        ("KS", "Kansas"),
        ("KY", "Kentucky"),
        ("LA", "Louisiana"),
        ("ME", "Maine"),
        ("MD", "Maryland"),
        ("MA", "Massachusetts"),
        ("MI", "Michigan"),
        ("MN", "Minnesota"),
        ("MS", "Mississippi"),
        ("MO", "Missouri"),
        ("MT", "Montana"),
        ("NE", "Nebraska"),
        ("NV", "Nevada"),
        ("NH", "New Hampshire"),
        ("NJ", "New Jersey"),
        ("NM", "New Mexico"),
        ("NY", "New York"),
        ("NC", "North Carolina"),
        ("ND", "North Dakota"),
        ("OH", "Ohio"),
        ("OK", "Oklahoma"),
        ("OR", "Oregon"),
        ("PA", "Pennsylvania"),
        ("RI", "Rhode Island"),
        ("SC", "South Carolina"),
        ("SD", "South Dakota"),
        ("TN", "Tennessee"),
        ("TX", "Texas"),
        ("UT", "Utah"),
        ("VT", "Vermont"),
        ("VA", "Virginia"),
        ("WA", "Washington"),
        ("WV", "West Virginia"),
        ("WI", "Wisconsin"),
        ("WY", "Wyoming"),
        ("DC", "District of Columbia"),
    ]

    BR_STATES = [
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Amazonas"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    ]

    # Basic Information
    name = models.CharField(max_length=100, help_text="Entity name")
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_TYPES,
        help_text="Type of legal entity",
        default="CORP",
    )

    # Tax classification
    tax_classification = models.CharField(
        max_length=50,
        choices=TAX_CLASSIFICATION_CHOICES,
        blank=True,
        help_text="Tax classification for this entity",
    )

    # Template Management (moved to Implementation subsection)
    implementation_templates = models.TextField(
        blank=True,
        help_text="Implementation templates (text format, not JSON)"
    )

    # Shares Information
    total_shares = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total number of shares for this entity"
    )

    # Jurisdiction Information
    jurisdiction = models.CharField(
        max_length=10,
        choices=JURISDICTIONS,
        default="US",
        help_text="Primary jurisdiction",
    )
    us_state = models.CharField(
        max_length=10,
        choices=US_STATES,
        blank=True,
        null=True,
        help_text="US State (only if jurisdiction is United States)",
    )
    br_state = models.CharField(
        max_length=10,
        choices=BR_STATES,
        blank=True,
        null=True,
        help_text="Brazilian State (only if jurisdiction is Brazil)",
    )

    # Implementation Details
    implementation_time = models.IntegerField(
        help_text="Implementation time in days",
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        default=30,
    )
    complexity = models.IntegerField(
        choices=[(i, f"Level {i}") for i in range(1, 6)],
        help_text="Complexity level from 1 (simple) to 5 (very complex)",
        default=3,
    )

    # Tax Impact Information
    tax_impact_usa = models.TextField(
        help_text="Detailed tax implications in the United States",
        default="To be determined",
    )
    tax_impact_brazil = models.TextField(
        help_text="Detailed tax implications in Brazil",
        default="To be determined",
    )
    tax_impact_others = models.TextField(
        blank=True, help_text="Tax implications in other jurisdictions"
    )

    # Privacy and Asset Protection
    confidentiality_level = models.IntegerField(
        choices=[(i, f"Level {i}") for i in range(1, 6)],
        help_text="Confidentiality level from 1 (low) to 5 (very high)",
        default=3,
    )
    asset_protection = models.IntegerField(
        choices=[(i, f"Level {i}") for i in range(1, 6)],
        help_text="Asset protection level from 1 (low) to 5 (very high)",
        default=3,
    )
    privacy_impact = models.TextField(
        help_text="Detailed privacy implications and protections",
        default="Standard privacy protections apply",
    )

    # Privacy Score (0-3) replaces privacy_score (0-100)
    privacy_score = models.IntegerField(
        choices=[(i, f"Level {i}") for i in range(0, 4)],
        help_text="Privacy score from 0 (lowest) to 3 (highest)",
        default=1,
    )

    # Banking Relation Score (1-3)
    banking_relation_score = models.IntegerField(
        choices=[(i, f"Level {i}") for i in range(1, 4)],
        help_text="Banking relationship difficulty from 1 (easy) to 3 (difficult)",
        default=2,
    )
    compliance_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Compliance score from 0 to 100",
        blank=True,
        null=True,
    )

    # Operational Information
    banking_facility = models.IntegerField(
        choices=[(i, f"Level {i}") for i in range(1, 6)],
        help_text="Banking facility level from 1 (difficult) to 5 (very easy)",
        default=3,
    )
    required_documentation = models.TextField(
        help_text="Required documentation for setup",
        default="Standard documentation required",
    )

    # Document URLs
    documents_url = models.URLField(
        blank=True, help_text="URL for entity documents and templates"
    )

    # Compliance and Reporting
    required_forms_usa = models.TextField(
        blank=True, help_text="Required US forms and reporting obligations"
    )
    required_forms_brazil = models.TextField(
        blank=True,
        help_text="Required Brazilian forms and reporting obligations",
    )

    # Status and Metadata
    active = models.BooleanField(
        default=True, help_text="Whether entity is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["jurisdiction"]),
            models.Index(fields=["active"]),
            models.Index(fields=["entity_type"]),
            models.Index(fields=["complexity"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"

    def save(self, *args, **kwargs):
        """Auto-calculate privacy score from confidentiality_level if not set"""
        if self.confidentiality_level and not self.privacy_score:
            self.privacy_score = min(3, (self.confidentiality_level - 1))
        super().save(*args, **kwargs)

    def clean(self):
        """Validate jurisdiction and state combinations"""
        super().clean()

        # Validate US state is only set when jurisdiction is US
        if self.us_state and self.jurisdiction != "US":
            raise ValidationError(
                {"us_state": "US State can only be set when jurisdiction is US"}
            )

        # Validate BR state is only set when jurisdiction is BR
        if self.br_state and self.jurisdiction != "BR":
            raise ValidationError(
                {"br_state": "Brazilian State can only be set when jurisdiction is Brazil"}
            )

    def get_complexity_display_text(self):
        """Get human-readable complexity description"""
        complexity_map = {
            1: "Very Simple",
            2: "Simple",
            3: "Moderate",
            4: "Complex",
            5: "Very Complex",
        }
        return complexity_map.get(self.complexity, "Unknown")

    def get_full_jurisdiction_display(self):
        """Get full jurisdiction including state if applicable"""
        jurisdiction = self.get_jurisdiction_display()

        if self.jurisdiction == "US" and self.us_state:
            state = dict(self.US_STATES).get(self.us_state, self.us_state)
            return f"{state}, {jurisdiction}"
        elif self.jurisdiction == "BR" and self.br_state:
            state = dict(self.BR_STATES).get(self.br_state, self.br_state)
            return f"{state}, {jurisdiction}"

        return jurisdiction

    def get_tax_classification_display(self):
        """Return tax classification display name"""
        if self.tax_classification:
            return dict(self.TAX_CLASSIFICATION_CHOICES).get(
                self.tax_classification, self.tax_classification
            )
        return "Not set"

    def get_templates_list(self):
        """Return formatted list of templates"""
        if not self.implementation_templates:
            return []
        return [
            f"{template.get('name', 'Unknown')} ({template.get('url', 'No URL')})"
            for template in self.implementation_templates
        ]

    def get_privacy_score_display(self):
        """Get privacy score display"""
        score_map = {
            0: "Lowest Privacy",
            1: "Low Privacy",
            2: "Medium Privacy",
            3: "High Privacy",
        }
        return score_map.get(self.privacy_score, "Unknown")

    def get_banking_relation_display(self):
        """Get banking relation difficulty display"""
        score_map = {
            1: "Easy Banking",
            2: "Moderate Banking",
            3: "Difficult Banking",
        }
        return score_map.get(self.banking_relation_score, "Unknown")

    def get_compliance_level_display(self):
        """Get compliance level as percentage"""
        if self.compliance_score:
            return f"{self.compliance_score}%"
        return "Not set"

    class Meta:
        verbose_name = "Template de Entidade"
        verbose_name_plural = "Templates de Entidades"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_entity_type_display()})"


class Structure(models.Model):
    """
    Estrutura Corporativa
    Representa hierarquias de propriedade (árvore corporativa) entre Entidades e UBOs
    Purpose: Model complex corporate ownership structures
    """

    STATUS_CHOICES = [
        ('DRAFTING', 'Drafting'),
        ('SENT_FOR_APPROVAL', 'Sent for Approval'),
        ('APPROVED', 'Approved'),
    ]

    name = models.CharField(max_length=200, help_text="Structure name")
    description = models.TextField(help_text="Structure description")

    # Status Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFTING')

    # Validation aggregated fields
    tax_impacts = models.TextField(
        blank=True,
        help_text="Aggregated tax impacts from validation rules"
    )
    severity_levels = models.TextField(
        blank=True,
        help_text="Aggregated severity levels from validation rules"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estrutura Corporativa"
        verbose_name_plural = "Estruturas Corporativas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Save first to get primary key
        super().save(*args, **kwargs)
        
        # Update calculated fields after saving (when pk exists)
        if self.pk:
            self.update_calculated_fields()
            # Save again only if calculated fields changed
            if self.tax_impacts or self.severity_levels:
                super().save(update_fields=['tax_impacts', 'severity_levels'])
        
        if self.status == 'SENT_FOR_APPROVAL':
            # Trigger notification to approvers
            self.notify_approvers()

    def notify_approvers(self):
        """Implement notification system for approvers"""
        # TODO: Implement notification logic
        pass

    def update_calculated_fields(self):
        """Update tax_impacts and severity_levels from validation rules (FASE 5)"""
        self.tax_impacts = self.combined_tax_impacts
        self.severity_levels = ", ".join(self.combined_severities)

    @property
    def combined_tax_impacts(self):
        """Return all tax impacts from validation rules based on entities in structure"""
        impacts = []
        entities = self.get_all_entities_in_structure()
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                rules = ValidationRule.objects.filter(
                    models.Q(parent_entity=entity1, related_entity=entity2) |
                    models.Q(parent_entity=entity2, related_entity=entity1)
                )
                for rule in rules:
                    if rule.tax_impacts:
                        impacts.append(rule.tax_impacts)
        
        return "; ".join(set(impacts)) if impacts else "No tax impacts identified"

    @property
    def combined_severities(self):
        """Return all severities from validation rules"""
        severities = []
        entities = self.get_all_entities_in_structure()
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                rules = ValidationRule.objects.filter(
                    models.Q(parent_entity=entity1, related_entity=entity2) |
                    models.Q(parent_entity=entity2, related_entity=entity1)
                )
                severities.extend([rule.severity for rule in rules if rule.severity])
        
        return list(set(severities))

    def get_all_entities_in_structure(self):
        """Get all entities involved in this structure"""
        entities = []
        for ownership in self.entity_ownerships.all():
            if ownership.owned_entity not in entities:
                entities.append(ownership.owned_entity)
            if ownership.owner_entity and ownership.owner_entity not in entities:
                entities.append(ownership.owner_entity)
        return entities

    def validate_entity_combinations(self):
        """Validate that no prohibited combinations exist in structure (FASE 6)"""
        entities = self.get_all_entities_in_structure()
        
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                prohibited_rules = ValidationRule.objects.filter(
                    models.Q(parent_entity=entity1, related_entity=entity2) |
                    models.Q(parent_entity=entity2, related_entity=entity1),
                    relationship_type='PROHIBITED'
                )
                
                if prohibited_rules.exists():
                    rule = prohibited_rules.first()
                    raise ValidationError(
                        f"Prohibited combination: {entity1.name} and {entity2.name}. "
                        f"Reason: {rule.description}"
                    )

    def clean(self):
        super().clean()
        if self.pk:  # Only validate if structure already exists
            self.validate_entity_combinations()


class EntityOwnership(models.Model):
    """
    Manages ownership relationships within a Structure
    Handles both UBO → Entity and Entity → Entity ownership
    Enhanced with Corporate Name, Hash Number, and Share Values
    """

    structure = models.ForeignKey(Structure, on_delete=models.CASCADE, related_name='entity_ownerships')

    # Owner can be either UBO or Entity
    owner_ubo = models.ForeignKey(
        'parties.Party', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        help_text="UBO owner"
    )
    owner_entity = models.ForeignKey(
        Entity, 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE, 
        related_name='ownerships_as_owner',
        help_text="Entity owner"
    )

    # Owned entity
    owned_entity = models.ForeignKey(
        Entity, 
        on_delete=models.CASCADE, 
        related_name='ownerships_as_owned'
    )

    # Corporate identification (FASE 2)
    corporate_name = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Corporate name when entity is used in structure"
    )
    hash_number = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Hash number when entity is used in structure"
    )

    # Share management
    owned_shares = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of shares owned by this owner"
    )
    ownership_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ownership percentage"
    )

    # Share valuation (FASE 3)
    share_value_usd = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01)],
        help_text="Value per share in USD"
    )
    share_value_eur = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.01)],
        help_text="Value per share in EUR"
    )

    # Total values (calculated fields)
    total_value_usd = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Total value of owned shares in USD"
    )
    total_value_eur = models.DecimalField(
        max_digits=20, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Total value of owned shares in EUR"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Registro Legado de Propriedade"
        verbose_name_plural = "Registros Legados de Propriedade"
        unique_together = ['structure', 'owner_ubo', 'owner_entity', 'owned_entity']
        indexes = [
            models.Index(fields=["structure"]),
            models.Index(fields=["owned_entity"]),
            models.Index(fields=["owner_ubo"]),
            models.Index(fields=["owner_entity"]),
        ]

    def __str__(self):
        owner_name = ""
        if self.owner_ubo:
            owner_name = str(self.owner_ubo)
        elif self.owner_entity:
            owner_name = str(self.owner_entity)
        
        percentage = self.ownership_percentage or 0
        return f"{owner_name} owns {percentage}% of {self.owned_entity.name}"

    def clean(self):
        super().clean()
        # Validate that exactly one owner type is specified
        owner_count = sum([bool(self.owner_ubo), bool(self.owner_entity)])
        if owner_count != 1:
            raise ValidationError("Must specify exactly one owner (UBO or Entity)")

        # Validate Corporate Name or Hash Number when entity is used in structure
        if not self.corporate_name and not self.hash_number:
            raise ValidationError(
                "Entity in structure must have Corporate Name, Hash Number, or both"
            )

        # Validate share distribution
        if self.owned_entity.total_shares:
            self.validate_shares_distribution()

    def save(self, *args, **kwargs):
        # Auto-calculate percentage from shares (FASE 4)
        if self.owned_shares and self.owned_entity.total_shares:
            calculated_percentage = (self.owned_shares / self.owned_entity.total_shares) * 100
            if not self.ownership_percentage:
                self.ownership_percentage = calculated_percentage

        # Auto-calculate shares from percentage (FASE 4)
        elif self.ownership_percentage and self.owned_entity.total_shares:
            calculated_shares = int((self.ownership_percentage / 100) * self.owned_entity.total_shares)
            if not self.owned_shares:
                self.owned_shares = calculated_shares

        # Calculate total values (FASE 3)
        self.calculate_total_values()

        super().save(*args, **kwargs)

    def calculate_total_values(self):
        """Calculate total values based on shares and share values"""
        if self.share_value_usd and self.owned_shares:
            self.total_value_usd = self.owned_shares * self.share_value_usd
        if self.share_value_eur and self.owned_shares:
            self.total_value_eur = self.owned_shares * self.share_value_eur

    def validate_shares_distribution(self):
        """Validate that all shares have owners (FASE 4)"""
        total_owned = EntityOwnership.objects.filter(
            structure=self.structure,
            owned_entity=self.owned_entity
        ).exclude(pk=self.pk).aggregate(
            total=models.Sum('owned_shares')
        )['total'] or 0

        if self.owned_shares:
            total_owned += self.owned_shares

        if total_owned > self.owned_entity.total_shares:
            raise ValidationError(
                f"Total owned shares ({total_owned}) cannot exceed "
                f"entity total shares ({self.owned_entity.total_shares})"
            )

class MasterEntity(models.Model):
    """
    Designates Master Entities (roots) of a Structure
    Only UBOs can own Master Entities
    """

    structure = models.ForeignKey(Structure, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Master Entity"
        verbose_name_plural = "Master Entities"
        unique_together = ['structure', 'entity']
        indexes = [
            models.Index(fields=["structure"]),
            models.Index(fields=["entity"]),
        ]

    def __str__(self):
        return f"{self.entity.name} (Master in {self.structure.name})"


class ValidationRule(models.Model):
    """
    Enhanced validation rules for entity combinations
    Removed: conditions field
    Renamed: structure_a → parent_entity, structure_b → related_entity
    Added: tax_impacts field
    """

    RELATIONSHIP_TYPES = [
        ("REQUIRED", "Required Combination"),
        ("RECOMMENDED", "Recommended Combination"),
        ("INCOMPATIBLE", "Incompatible Combination"),
        ("CONDITIONAL", "Conditional Combination"),
        ("SYNERGISTIC", "Synergistic Combination"),
    ]

    SEVERITY_CHOICES = [
        ("ERROR", "Error - Blocks configuration"),
        ("WARNING", "Warning - Potential issue"),
        ("INFO", "Information - Suggestion"),
    ]

    parent_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='parent_validation_rules'
    )
    related_entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name='related_validation_rules'
    )

    relationship_type = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    description = models.TextField()

    # New field for tax impact explanations
    tax_impacts = models.TextField(
        help_text="Detailed tax implications of this entity combination"
    )

    jurisdiction = models.CharField(max_length=100, blank=True)
    active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Validation Rule"
        verbose_name_plural = "Validation Rules"
        unique_together = ["parent_entity", "related_entity", "relationship_type"]
        indexes = [
            models.Index(fields=["parent_entity"]),
            models.Index(fields=["related_entity"]),
            models.Index(fields=["active"]),
        ]

    def __str__(self):
        return f"{self.parent_entity.name} -> {self.related_entity.name} ({self.get_relationship_type_display()})"


# Keep existing models that don't need changes for now
# We'll update references in later phases

class UBO(models.Model):
    """
    Ultimate Beneficial Owner - represents the ultimate beneficial owners of structures
    This model will be migrated to parties.Party in Phase 3
    """

    TIPO_PESSOA = [
        ("FISICA", "Pessoa Física"),
        ("JURIDICA", "Pessoa Jurídica"),
    ]

    NACIONALIDADES = [
        ("BR", "Brasil"),
        ("US", "Estados Unidos"),
        ("BS", "Bahamas"),
        ("KN", "São Cristóvão e Nevis"),
        ("VG", "Ilhas Virgens Britânicas"),
        ("PA", "Panamá"),
        ("CH", "Suíça"),
        ("SG", "Singapura"),
        ("HK", "Hong Kong"),
        ("OTHER", "Outro"),
    ]

    # Basic Information (merged from both models)
    nome = models.CharField(max_length=200, help_text="Full name")
    nome_completo = models.CharField(
        max_length=200,
        blank=True,
        help_text="Nome completo do Ultimate Beneficial Owner",
    )
    tipo_pessoa = models.CharField(
        max_length=20,
        choices=TIPO_PESSOA,
        default="FISICA",
        help_text="Type of entity (individual or corporate)",
    )

    # Contact Information
    email = models.EmailField(blank=True, help_text="Email address")
    telefone = models.CharField(
        max_length=20, blank=True, help_text="Phone number"
    )

    # Address Information
    endereco = models.TextField(blank=True, help_text="Complete address")
    endereco_residencia_fiscal = models.TextField(
        blank=True, help_text="Endereço completo de residência fiscal"
    )
    cidade = models.CharField(max_length=100, blank=True, help_text="City")
    estado = models.CharField(
        max_length=100, blank=True, help_text="State/Province"
    )
    pais = models.CharField(max_length=100, blank=True, help_text="Country")
    cep = models.CharField(
        max_length=20, blank=True, help_text="ZIP/Postal Code"
    )

    # Identification
    documento_identidade = models.CharField(
        max_length=50, blank=True, help_text="Identity document number"
    )
    tipo_documento = models.CharField(
        max_length=50, blank=True, help_text="Type of identity document"
    )
    tin = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tax Identification Number - número emitido pelo país de residência fiscal",
    )

    # Additional Information
    nacionalidade = models.CharField(
        max_length=10,
        choices=NACIONALIDADES,
        blank=True,
        help_text="Nationality",
    )
    data_nascimento = models.DateField(
        null=True, blank=True, help_text="Date of birth (for individuals)"
    )
    observacoes = models.TextField(
        blank=True, help_text="Observações adicionais sobre o UBO"
    )

    # Metadata
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "UBO (Ultimate Beneficial Owner)"
        verbose_name_plural = "UBOs (Ultimate Beneficial Owners)"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["tipo_pessoa"]),
            models.Index(fields=["tin"]),
            models.Index(fields=["nacionalidade"]),
            models.Index(fields=["ativo"]),
        ]

    def __str__(self):
        if self.tin:
            return f"{self.nome or self.nome_completo} ({self.tin})"
        return f"{self.nome or self.nome_completo} ({self.get_tipo_pessoa_display()})"

    def clean(self):
        """Validações customizadas"""
        super().clean()

        # Ensure at least one name field is filled
        if not self.nome and not self.nome_completo:
            raise ValidationError("At least one name field must be filled")

        # Sync nome and nome_completo if only one is filled
        if self.nome and not self.nome_completo:
            self.nome_completo = self.nome
        elif self.nome_completo and not self.nome:
            self.nome = self.nome_completo

        # Validação básica de TIN (pode ser expandida por país)
        if self.tin:
            import re

            if not re.match(r"^[A-Z0-9\-]{5,20}$", self.tin.upper()):
                raise ValidationError(
                    {
                        "tin": "TIN deve conter apenas letras, números e hífens (5-20 caracteres)"
                    }
                )

    def get_endereco_completo(self):
        """Retorna endereço completo formatado"""
        endereco_base = self.endereco or self.endereco_residencia_fiscal
        partes = [endereco_base, self.cidade, self.estado, self.pais, self.cep]
        return ", ".join([parte for parte in partes if parte])


class JurisdictionAlert(models.Model):
    """
    Model for jurisdiction-specific alerts and compliance requirements.
    Enhanced with deadline management, recurrence patterns, and service connections.
    """

    JURISDICOES = [
        ("US", "United States"),
        ("BR", "Brazil"),
        ("BS", "Bahamas"),
        ("WY", "Wyoming"),
        ("GLOBAL", "Global/Multiple"),
    ]

    TIPOS_ALERTA = [
        ("TAX", "Tax Obligation"),
        ("COMPLIANCE", "Compliance Requirement"),
        ("REPORTING", "Reporting Obligation"),
        ("DEADLINE", "Important Deadline"),
        ("REGULATORY", "Regulatory Change"),
        ("RENEWAL", "License/Registration Renewal"),
        ("FILING", "Required Filing"),
    ]

    DEADLINE_TYPES = [
        ("SINGLE", "Single Deadline"),
        ("RECURRING", "Recurring Deadline"),
    ]

    RECURRENCE_PATTERNS = [
        ("MONTHLY", "Monthly"),
        ("QUARTERLY", "Quarterly"),
        ("SEMIANUAL", "Semiannual"),
        ("ANNUAL", "Annual"),
        ("BIENNIAL", "Biennial"),
        ("CUSTOM", "Custom Pattern"),
    ]

    # Basic Information
    jurisdicao = models.CharField(
        max_length=10, choices=JURISDICOES, help_text="Applicable jurisdiction"
    )
    tipo_alerta = models.CharField(
        max_length=20, choices=TIPOS_ALERTA, help_text="Type of alert"
    )
    titulo = models.CharField(max_length=200, help_text="Alert title")
    descricao = models.TextField(help_text="Detailed alert description")

    # Applicability - Updated to use Entity instead of Structure
    estruturas_aplicaveis = models.ManyToManyField(
        Entity,
        blank=True,
        help_text="Entities to which this alert applies",
    )

    # Deadline Management
    deadline_type = models.CharField(
        max_length=20,
        choices=DEADLINE_TYPES,
        default="SINGLE",
        help_text="Type of deadline (single or recurring)",
    )
    single_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Single deadline date (for non-recurring alerts)",
    )
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=RECURRENCE_PATTERNS,
        null=True,
        blank=True,
        help_text="Pattern for recurring deadlines",
    )
    next_deadline = models.DateField(
        null=True, blank=True, help_text="Next calculated deadline date"
    )
    last_completed = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this alert was last completed",
    )

    # Templates and Links
    template_url = models.URLField(
        blank=True, help_text="URL to template or form for this alert"
    )
    compliance_url = models.URLField(
        blank=True, help_text="URL to compliance information or portal"
    )

    # Service Connection
    service_connection = models.ForeignKey(
        "corporate_relationship.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associated service for this alert",
    )

    # Advanced Configuration
    advance_notice_days = models.PositiveIntegerField(
        default=30, help_text="Days before deadline to trigger advance notice"
    )
    auto_calculate_next = models.BooleanField(
        default=True,
        help_text="Automatically calculate next deadline after completion",
    )
    custom_recurrence_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Custom configuration for complex recurrence patterns",
    )

    # Priority and Status
    prioridade = models.IntegerField(
        choices=[(i, f"Priority {i}") for i in range(1, 6)],
        default=3,
        help_text="Alert priority from 1 (low) to 5 (critical)",
    )
    ativo = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Jurisdiction Alert"
        verbose_name_plural = "Jurisdiction Alerts"
        ordering = ["-prioridade", "next_deadline", "jurisdicao"]
        indexes = [
            models.Index(fields=["jurisdicao", "tipo_alerta"]),
            models.Index(fields=["next_deadline"]),
            models.Index(fields=["deadline_type"]),
            models.Index(fields=["prioridade"]),
            models.Index(fields=["ativo"]),
        ]

    def __str__(self):
        return f"{self.get_jurisdicao_display()}: {self.titulo}"

    def clean(self):
        """Validate deadline configuration"""
        if self.deadline_type == "SINGLE":
            if not self.single_deadline:
                raise ValidationError(
                    "Single deadline date is required for single deadline type"
                )
            if self.recurrence_pattern:
                raise ValidationError(
                    "Recurrence pattern should not be set for single deadline type"
                )
        elif self.deadline_type == "RECURRING":
            if not self.recurrence_pattern:
                raise ValidationError(
                    "Recurrence pattern is required for recurring deadline type"
                )
            if self.single_deadline:
                raise ValidationError(
                    "Single deadline should not be set for recurring deadline type"
                )

    def calculate_next_deadline(self):
        """Calculate the next deadline based on recurrence pattern"""
        if self.deadline_type != "RECURRING" or not self.recurrence_pattern:
            return None

        from dateutil.relativedelta import relativedelta

        # Use last_completed as base, or current date if never completed
        base_date = self.last_completed or timezone.now().date()

        if self.recurrence_pattern == "MONTHLY":
            return base_date + relativedelta(months=1)
        elif self.recurrence_pattern == "QUARTERLY":
            return base_date + relativedelta(months=3)
        elif self.recurrence_pattern == "SEMIANUAL":
            return base_date + relativedelta(months=6)
        elif self.recurrence_pattern == "ANNUAL":
            return base_date + relativedelta(years=1)
        elif self.recurrence_pattern == "BIENNIAL":
            return base_date + relativedelta(years=2)
        elif self.recurrence_pattern == "CUSTOM":
            # Handle custom patterns from custom_recurrence_config
            config = self.custom_recurrence_config
            if "months" in config:
                return base_date + relativedelta(months=config["months"])
            elif "days" in config:
                return base_date + relativedelta(days=config["days"])

        return None

    def update_next_deadline(self):
        """Update the next_deadline field based on calculation"""
        if self.deadline_type == "SINGLE":
            self.next_deadline = self.single_deadline
        elif self.deadline_type == "RECURRING" and self.auto_calculate_next:
            self.next_deadline = self.calculate_next_deadline()

        self.save(update_fields=["next_deadline"])

    def mark_completed(self, completion_date=None):
        """Mark alert as completed and update next deadline"""
        completion_date = completion_date or timezone.now().date()
        self.last_completed = completion_date

        if self.deadline_type == "RECURRING" and self.auto_calculate_next:
            self.next_deadline = self.calculate_next_deadline()

        self.save(update_fields=["last_completed", "next_deadline"])

    def is_overdue(self):
        """Check if alert is overdue"""
        if not self.next_deadline:
            return False
        return timezone.now().date() > self.next_deadline

    def days_until_deadline(self):
        """Calculate days until next deadline"""
        if not self.next_deadline:
            return None
        delta = self.next_deadline - timezone.now().date()
        return delta.days

    def needs_advance_notice(self):
        """Check if advance notice should be triggered"""
        days_until = self.days_until_deadline()
        if days_until is None:
            return False
        return 0 <= days_until <= self.advance_notice_days

    def get_status_display(self):
        """Get human-readable status"""
        if self.is_overdue():
            return "Overdue"
        elif self.needs_advance_notice():
            return "Due Soon"
        elif self.next_deadline:
            return "Scheduled"
        else:
            return "No Deadline"

    def get_status_color(self):
        """Get color code for status display"""
        if self.is_overdue():
            return "#dc3545"  # Red
        elif self.needs_advance_notice():
            return "#ffc107"  # Yellow
        elif self.next_deadline:
            return "#28a745"  # Green
        else:
            return "#6c757d"  # Gray


class Successor(models.Model):
    """
    Modelo para gestão de sucessão entre UBOs
    This model will be migrated to parties.BeneficiaryRelation in Phase 3
    """

    # Relacionamentos
    ubo_proprietario = models.ForeignKey(
        UBO,
        on_delete=models.CASCADE,
        related_name="sucessores_definidos",
        help_text="UBO que está definindo a sucessão",
    )
    ubo_sucessor = models.ForeignKey(
        UBO,
        on_delete=models.CASCADE,
        related_name="sucessoes_recebidas",
        help_text="UBO que receberá a sucessão",
    )

    # Campos de sucessão
    percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)],
        help_text="Percentual que o sucessor receberá (0.01 a 100.00)",
    )
    data_definicao = models.DateTimeField(
        auto_now_add=True, help_text="Data em que a sucessão foi definida"
    )
    data_efetivacao = models.DateField(
        null=True,
        blank=True,
        help_text="Data em que a sucessão deve ser efetivada (opcional)",
    )
    condicoes = models.TextField(
        blank=True, help_text="Condições específicas para a sucessão"
    )

    # Status
    ativo = models.BooleanField(default=True)
    efetivado = models.BooleanField(default=False)
    data_efetivacao_real = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Data real em que a sucessão foi efetivada",
    )

    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Successor"
        verbose_name_plural = "Successors"
        ordering = ["-data_definicao"]
        unique_together = ["ubo_proprietario", "ubo_sucessor"]
        indexes = [
            models.Index(fields=["ubo_proprietario", "ativo"]),
            models.Index(fields=["data_efetivacao"]),
        ]

    def __str__(self):
        return (
            f"{self.ubo_proprietario.nome} → {self.ubo_sucessor.nome} "
            f"({self.percentual}%)"
        )

    def clean(self):
        """Validações customizadas"""
        super().clean()

        # Validar que sucessor não é o mesmo que proprietário
        if self.ubo_proprietario == self.ubo_sucessor:
            raise ValidationError("UBO não pode ser sucessor de si mesmo")

        # Validar soma de percentuais para o mesmo proprietário
        if self.pk:
            outros_sucessores = Successor.objects.filter(
                ubo_proprietario=self.ubo_proprietario, ativo=True
            ).exclude(pk=self.pk)
        else:
            outros_sucessores = Successor.objects.filter(
                ubo_proprietario=self.ubo_proprietario, ativo=True
            )

        total_outros = sum(s.percentual for s in outros_sucessores)
        if total_outros + self.percentual > 100:
            raise ValidationError(
                {
                    "percentual": (
                        f"Soma dos percentuais excede 100%. "
                        f"Disponível: {100 - total_outros}%"
                    )
                }
            )


class StructureOwnership(models.Model):
    """
    Tabela de propriedade entre estruturas (N↔N não-simétrica).
    Mapeia participação societária de uma estrutura em outra.
    This model will be updated to use Entity instead of Structure in later phases
    """

    parent = models.ForeignKey(
        Entity,  # Updated to use Entity
        on_delete=models.CASCADE,
        related_name="owned_entities_legacy",
        help_text="Entity proprietária (parent)",
    )
    child = models.ForeignKey(
        Entity,  # Updated to use Entity
        on_delete=models.CASCADE,
        related_name="ownership_by_legacy",
        help_text="Entity possuída (child)",
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)],
        help_text="Percentual de propriedade (0.01 a 100.00)",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Structure Ownership (Legacy)"
        verbose_name_plural = "Structure Ownerships (Legacy)"
        unique_together = ["parent", "child"]
        ordering = ["-percentage"]

    def __str__(self):
        return (
            f"{self.parent.name} owns {self.percentage}% of "
            f"{self.child.name}"
        )

    def clean(self):
        """Validações customizadas"""
        super().clean()

        # Validar que parent não é o mesmo que child
        if self.parent == self.child:
            raise ValidationError("Entity cannot own itself")




class StructureNode(models.Model):
    """
    Represents a specific instance of an Entity within a Structure.
    This allows Entity templates to be reused across multiple structures.
    """
    
    # Reference to the Entity template
    entity_template = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="structure_instances",
        help_text="Entity template this node is based on"
    )
    
    # Structure this node belongs to
    structure = models.ForeignKey(
        Structure,
        on_delete=models.CASCADE,
        related_name="nodes",
        help_text="Structure this node belongs to"
    )
    
    # Instance-specific customizations
    custom_name = models.CharField(
        max_length=200,
        help_text="Custom name for this specific instance"
    )
    
    total_shares = models.PositiveIntegerField(
        help_text="Total number of shares for this instance"
    )
    
    corporate_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Official corporate name for this instance"
    )
    
    hash_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Registration or hash number"
    )
    
    # Hierarchy information
    level = models.PositiveIntegerField(
        help_text="Level in the structure hierarchy (1 = top level)"
    )
    
    parent_node = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="child_nodes",
        help_text="Parent node in the hierarchy"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Instância de Empresa"
        verbose_name_plural = "Instâncias de Empresas"
        unique_together = ["structure", "custom_name"]
        ordering = ["level", "custom_name"]
    
    def __str__(self):
        return f"{self.custom_name} (Level {self.level}) - {self.structure.name}"
    
    def get_entity_type_display(self):
        """Get the entity type from the template"""
        return self.entity_template.get_entity_type_display()
    
    def get_jurisdiction_display(self):
        """Get the jurisdiction from the template"""
        return self.entity_template.get_jurisdiction_display()
    
    def get_children(self):
        """Get all child nodes"""
        return self.child_nodes.all()
    
    def get_ownership_percentage(self):
        """Calculate total ownership percentage from all owners"""
        total = self.owned_by.aggregate(
            total=models.Sum('ownership_percentage')
        )['total'] or 0
        return total


class NodeOwnership(models.Model):
    """
    Represents ownership relationships in the new structure system.
    Supports both Party→Node and Node→Node ownership.
    """
    
    # Owner can be either a Party (UBO) or another StructureNode (Entity→Entity)
    owner_party = models.ForeignKey(
        'parties.Party',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owned_nodes",
        help_text="Party that owns this node (UBO)"
    )
    
    owner_node = models.ForeignKey(
        StructureNode,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="owned_nodes",
        help_text="Node that owns this node (Entity→Entity)"
    )
    
    # The node being owned
    owned_node = models.ForeignKey(
        StructureNode,
        on_delete=models.CASCADE,
        related_name="owned_by",
        help_text="Node being owned"
    )
    
    # Ownership details
    ownership_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0.01), MaxValueValidator(100.00)],
        help_text="Ownership percentage (0.01 to 100.00)"
    )
    
    owned_shares = models.PositiveIntegerField(
        help_text="Number of shares owned"
    )
    
    share_value_usd = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Value per share in USD"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Relacionamento de Propriedade"
        verbose_name_plural = "Relacionamentos de Propriedade"
        ordering = ["-ownership_percentage"]
    
    def __str__(self):
        owner_name = self.owner_party.name if self.owner_party else self.owner_node.custom_name
        return f"{owner_name} owns {self.ownership_percentage}% of {self.owned_node.custom_name}"
    
    def clean(self):
        """Custom validations"""
        super().clean()
        
        # Must have either owner_party or owner_node, but not both
        if not self.owner_party and not self.owner_node:
            raise ValidationError("Must specify either owner_party or owner_node")
        
        if self.owner_party and self.owner_node:
            raise ValidationError("Cannot specify both owner_party and owner_node")
        
        # Prevent self-ownership for nodes
        if self.owner_node and self.owner_node == self.owned_node:
            raise ValidationError("Node cannot own itself")
        
        # Validate shares don't exceed total shares
        if self.owned_shares > self.owned_node.total_shares:
            raise ValidationError("Owned shares cannot exceed total shares")
    
    def get_owner_name(self):
        """Get the name of the owner (party or node)"""
        if self.owner_party:
            return self.owner_party.name
        elif self.owner_node:
            return self.owner_node.custom_name
        return "Unknown Owner"
    
    def get_owner_type(self):
        """Get the type of owner"""
        if self.owner_party:
            return "Party"
        elif self.owner_node:
            return "Entity"
        return "Unknown"
    
    def get_total_value_usd(self):
        """Calculate total value of this ownership"""
        return self.owned_shares * self.share_value_usd

