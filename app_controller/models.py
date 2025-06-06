from django.db import models
import secrets
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from validate_docbr import CPF, CNPJ

# Validações reutilizáveis
telefone_validator = RegexValidator(
    regex=r'^\(\d{2}\) \d{4,5}-\d{4}$',
    message="Formato: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX"
)

class Cliente(models.Model):
    nome = models.CharField(
        max_length=255,
        verbose_name=_("Nome Completo"),
        help_text=_("Razão Social ou Nome Completo")
    )
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name=_("CNPJ"),
        validators=[MinLengthValidator(14)],
        help_text=_("Formato: 00.000.000/0000-00")
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name=_("Telefone"),
        validators=[telefone_validator]
    )
    email = models.EmailField(
        verbose_name=_("E-mail"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cnpj']),
        ]

    def __str__(self):
        return self.nome

    def clean(self):
        cnpj = CNPJ()
        if not cnpj.validate(self.cnpj):
            raise ValidationError(_("CNPJ inválido"))


class Motorista(models.Model):
    nome = models.CharField(
        max_length=255,
        verbose_name=_("Nome Completo")
    )
    cpf = models.CharField(
        max_length=14,
        unique=True,
        verbose_name=_("CPF"),
        validators=[MinLengthValidator(11)],
        help_text=_("Formato: 000.000.000-00")
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name=_("Telefone"),
        validators=[telefone_validator]
    )
    email = models.EmailField(
        verbose_name=_("E-mail"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Motorista")
        verbose_name_plural = _("Motoristas")
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cpf']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.cpf})"

    def clean(self):
        cpf = CPF()
        if not cpf.validate(self.cpf):
            raise ValidationError(_("CPF inválido"))


class Transportadora(models.Model):
    nome = models.CharField(
        max_length=255,
        verbose_name=_("Nome da Transportadora")
    )
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name=_("CNPJ"),
        validators=[MinLengthValidator(14)],
        help_text=_("Formato: 00.000.000/0000-00")
    )
    telefone = models.CharField(
        max_length=20,
        verbose_name=_("Telefone"),
        validators=[telefone_validator]
    )
    email = models.EmailField(
        verbose_name=_("E-mail"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Transportadora")
        verbose_name_plural = _("Transportadoras")
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['cnpj']),
        ]

    def __str__(self):
        return self.nome

    def clean(self):
        cnpj = CNPJ()
        if not cnpj.validate(self.cnpj):
            raise ValidationError(_("CNPJ inválido"))

class ValePallet(models.Model):
    ESTADO_CHOICES = [
        ('EMITIDO', 'Emitido'),
        ('SAIDA', 'Saida'),
        ('RETORNO', 'Retorno'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    numero_vale = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT)
    transportadora = models.ForeignKey(Transportadora, on_delete=models.PROTECT)
    data_emissao = models.DateTimeField(auto_now_add=True)
    data_validade = models.DateTimeField()
    qtd_pbr = models.PositiveIntegerField(default=0)
    qtd_chepp = models.PositiveIntegerField(default=0)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='EMITIDO')
    observacoes = models.TextField(blank=True, null=True)
    hash_seguranca = models.CharField(max_length=32, unique=True, editable=False)
    criado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Criado por"
    )

    
    class Meta:
        ordering = ['-data_emissao']
        verbose_name = 'Vale Pallet'
        verbose_name_plural = 'Vales Pallets'
    
    def __str__(self):
        return f"Vale {self.numero_vale} - {self.cliente.nome}"
        
    
    @property
    def esta_vencido(self):
        hoje = timezone.now().date()  # Pega apenas a data (ignora horário)
        data_validade = self.data_validade.date()  # Converte data_validade para date (sem hora)
        return hoje > data_validade
    
    def gerar_hash(self):
        """Gera um hash seguro usando secrets"""
        self.hash_seguranca = secrets.token_hex(16)
    from django.utils import timezone

class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('EMITIDO', 'Emitido'),
        ('SAIDA', 'Saida'),
        ('RETORNO', 'Retorno'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    vale = models.ForeignKey(ValePallet, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    data_hora = models.DateTimeField(auto_now_add=True)  # Mantém para registro interno
    data_validade = models.DateTimeField(null=True)  # Obrigatório (ou use null=True se opcional)
    qtd_pbr = models.PositiveIntegerField(default=0)
    qtd_chepp = models.PositiveIntegerField(default=0)
    observacao = models.TextField(blank=True, null=True)
    responsavel = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    
    class Meta:
        ordering = ['-data_hora']
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - Vale {self.vale.numero_vale}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Apenas na criação
            if self.tipo == 'EMITIDO':
                self.vale.estado = 'EMITIDO'
            elif self.tipo == 'SAIDA':
                self.vale.estado = 'SAIDA'
            elif self.tipo == 'RETORNO':
                self.vale.estado = 'RETORNO'
            self.vale.save()
        super().save(*args, **kwargs)