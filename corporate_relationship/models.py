from django.conf import settings
from django.db import models
from djmoney.models.fields import MoneyField
import uuid


class File(models.Model):
    """
    Represents approved structures
    Created when structure status becomes 'APPROVED'
    """

    structure = models.OneToOneField(
        'corporate.Structure',
        on_delete=models.CASCADE,
        help_text="Reference to approved structure"
    )

    approved_by = models.ForeignKey(
        'parties.Party',
        on_delete=models.SET_NULL,
        null=True,
        help_text="Party who approved the structure"
    )
    approval_date = models.DateTimeField(help_text="When the structure was approved")

    # File metadata
    file_number = models.CharField(max_length=50, unique=True, help_text="Unique file identifier")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
        ordering = ["-approval_date"]
        indexes = [
            models.Index(fields=["file_number"]),
            models.Index(fields=["approval_date"]),
        ]

    def __str__(self):
        return f"File {self.file_number} - {self.structure.name}"

    def save(self, *args, **kwargs):
        if not self.file_number:
            # Auto-generate file number
            self.file_number = self.generate_file_number()
        super().save(*args, **kwargs)

    def generate_file_number(self):
        """Generate unique file number"""
        return f"FILE-{uuid.uuid4().hex[:8].upper()}"


# Keep existing models but update references where needed

class RelationshipStructure(models.Model):
    """
    Relacionamento entre uma Structure e um Client.
    Criado automaticamente quando um PersonalizedProduct é aprovado.
    Updated to work with new structure
    """

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("ARCHIVED", "Archived"),
    ]

    structure = models.ForeignKey(
        "corporate.Structure",  # This now refers to the new Structure model
        on_delete=models.CASCADE,
        help_text="Estrutura legal relacionada",
    )
    client = models.ForeignKey(
        "sales.Partner",  # Updated to use Partner instead of Client
        on_delete=models.CASCADE,
        help_text="Partner proprietário da estrutura",
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default="ACTIVE",
        help_text="Status do relacionamento",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Data de criação do relacionamento"
    )

    class Meta:
        verbose_name = "Relationship Structure"
        verbose_name_plural = "Relationship Structures"
        unique_together = ["structure", "client"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["structure"]),
            models.Index(fields=["client"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.structure.name} - {self.client.company_name}"


class Service(models.Model):
    """
    Serviço que pode ser executado para um cliente.
    Migrado de corporate.Service com suporte multi-moeda.
    Updated to work with new structure
    """

    name = models.CharField(max_length=120, help_text="Nome do serviço")
    description = models.TextField(
        blank=True, help_text="Descrição detalhada do serviço"
    )

    # Preços multi-moeda (USD, BRL, EUR)
    service_price = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        help_text="Preço do serviço",
    )
    regulator_fee = MoneyField(
        max_digits=12,
        decimal_places=2,
        default_currency="USD",
        help_text="Taxa regulatória/governamental",
    )

    # Cargos e responsabilidades
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        help_text="Usuário responsável pela execução",
    )
    counterparty_name = models.CharField(
        max_length=120, help_text="Nome do órgão/entidade receptora"
    )
    informed = models.ManyToManyField(
        "sales.Contact",  # Updated to use Contact from sales app
        blank=True,
        help_text="Contatos do cliente a serem notificados",
    )

    # Relacionamentos
    relationship_structure = models.ForeignKey(
        RelationshipStructure,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="Estrutura relacionada (opcional)",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["executor"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.counterparty_name}"

    def get_total_cost(self):
        """Calcula custo total (serviço + taxa regulatória)"""
        return self.service_price + self.regulator_fee


class ServiceActivity(models.Model):
    """
    Atividade específica dentro de um serviço.
    Permite rastreamento detalhado da execução.
    Enhanced with more detailed tracking
    """

    STATUS_CHOICES = [
        ("PLANNED", "Planned"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="activities",
        help_text="Serviço ao qual esta atividade pertence",
    )

    # Activity details
    activity_title = models.CharField(max_length=200, help_text="Título da atividade")
    activity_description = models.TextField(blank=True, help_text="Descrição detalhada da atividade")
    
    # Scheduling
    start_date = models.DateField(help_text="Data de início planejada")
    due_date = models.DateField(null=True, blank=True, help_text="Data de vencimento")
    completed_date = models.DateField(null=True, blank=True, help_text="Data de conclusão real")

    # Status and priority
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default="PLANNED",
        help_text="Status da atividade",
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="MEDIUM",
        help_text="Prioridade da atividade",
    )

    # Responsibility
    responsible_person = models.CharField(
        max_length=200,
        blank=True,
        help_text="Pessoa responsável pela atividade"
    )

    # Notes and comments
    notes = models.TextField(blank=True, help_text="Notas e comentários")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Service Activity"
        verbose_name_plural = "Service Activities"
        ordering = ["due_date", "priority", "start_date"]
        indexes = [
            models.Index(fields=["service"]),
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["priority"]),
        ]

    def __str__(self):
        return f"{self.service.name} - {self.activity_title}"

    def is_overdue(self):
        """Check if activity is overdue"""
        if not self.due_date or self.status == "COMPLETED":
            return False
        from django.utils import timezone
        return timezone.now().date() > self.due_date

    def days_until_due(self):
        """Calculate days until due date"""
        if not self.due_date:
            return None
        from django.utils import timezone
        delta = self.due_date - timezone.now().date()
        return delta.days


class WebhookLog(models.Model):
    """
    Log de tentativas de webhook para auditoria e retentativas.
    """

    STATUS_CHOICES = [
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("PENDING", "Pending"),
    ]

    event_type = models.CharField(
        max_length=50,
        help_text="Tipo do evento (ex: personalized_product_approved)",
    )
    payload = models.JSONField(help_text="Payload enviado no webhook")
    url = models.URLField(help_text="URL de destino do webhook")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
        help_text="Status da tentativa",
    )
    response_status_code = models.PositiveIntegerField(
        null=True, blank=True, help_text="Código de status HTTP da resposta"
    )
    response_body = models.TextField(
        blank=True, help_text="Corpo da resposta HTTP"
    )
    error_message = models.TextField(
        blank=True, help_text="Mensagem de erro se houver falha"
    )
    attempt_count = models.PositiveIntegerField(
        default=1, help_text="Número de tentativas realizadas"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Data da primeira tentativa"
    )
    last_attempt_at = models.DateTimeField(
        auto_now=True, help_text="Data da última tentativa"
    )

    class Meta:
        verbose_name = "Webhook Log"
        verbose_name_plural = "Webhook Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.status} ({self.attempt_count} attempts)"

