from django.db import models
from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile
import os

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    
    def _str_(self):
        return self.nome

class Motorista(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    def _str_(self):
        return self.nome

class Transportadora(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    
    def _str_(self):
        return self.nome

class ValePallet(models.Model):
    ESTADO_CHOICES = [
        ('EMITIDO', 'Emitido'),
        ('UTILIZADO', 'Utilizado'),
        ('RETORNADO', 'Retornado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    numero_vale = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT)
    transportadora = models.ForeignKey(Transportadora, on_delete=models.PROTECT)
    data_emissao = models.DateTimeField(auto_now_add=True)  # Mudado para DateTimeField
    data_validade = models.DateTimeField()  # Mudado para DateTimeField
    qtd_pbr = models.PositiveIntegerField(default=0)
    qtd_chepp = models.PositiveIntegerField(default=0)
    saldo_pbr = models.PositiveIntegerField(default=0)  # Novo campo
    saldo_chepp = models.PositiveIntegerField(default=0)  # Novo campo
    codigo_barras = models.CharField(max_length=100, unique=True, blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='EMITIDO')  # Substitui o status
    observacoes = models.TextField(blank=True, null=True)
    hash_seguranca = models.CharField(max_length=32, unique=True, editable=False)
    
    def __str__(self):
        return f"Vale {self.numero_vale} - {self.cliente.nome}"
    
    @property
    def esta_vencido(self):
        from django.utils import timezone
        return timezone.now() > self.data_validade
    
    def gerar_hash(self):
        import hashlib
        unique_str = f"{self.numero_vale}{self.data_emissao.timestamp()}"
        self.hash_seguranca = hashlib.md5(unique_str.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        if not self.hash_seguranca:
            self.gerar_hash()
        if not self.qr_code:  # Gerar QR Code se não existir
            self.gerar_qr_code()
        super().save(*args, **kwargs)
    
    def gerar_qr_code(self):
        from .utils import generate_qr_code
        if not self.hash_seguranca:
            self.gerar_hash()
        qr_data = f"vpallet:{self.id}:{self.hash_seguranca}"
        self.qr_code.save(f'qr_{self.numero_vale}.png', generate_qr_code(qr_data), save=False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Novo vale
            self.saldo_pbr = self.qtd_pbr
            self.saldo_chepp = self.qtd_chepp
            if not self.hash_seguranca:
                self.gerar_hash()
        
        super().save(*args, **kwargs)  # Salva primeiro para gerar ID
        
        if not self.qr_code:  # Gera QR Code após salvar
            self.gerar_qr_code()
            super().save(*args, **kwargs)  # Salva novamente com o QR Code

class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('RETORNO', 'Retorno'),
    ]
    
    vale = models.ForeignKey(ValePallet, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    data_hora = models.DateTimeField(auto_now_add=True)
    qtd_pbr = models.PositiveIntegerField(default=0)
    qtd_chepp = models.PositiveIntegerField(default=0)
    observacao = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'movimentacoes'
        ordering = ['-data_hora']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - Vale {self.vale.numero_vale}"

    def save(self, *args, **kwargs):
        # Atualiza saldo automaticamente
        if not self.pk:  # Somente para novas movimentações
            if self.tipo == 'ENTRADA':
                self.vale.saldo_pbr += self.qtd_pbr
                self.vale.saldo_chepp += self.qtd_chepp
            elif self.tipo in ['SAIDA', 'RETORNO']:
                self.vale.saldo_pbr -= self.qtd_pbr
                self.vale.saldo_chepp -= self.qtd_chepp
            self.vale.save()
        super().save(*args, **kwargs)