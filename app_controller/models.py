from django.db import models

# Create your models here.
from django.db import models

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
    numero_vale = models.CharField(max_length=50, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    motorista = models.ForeignKey(Motorista, on_delete=models.PROTECT)
    transportadora = models.ForeignKey(Transportadora, on_delete=models.PROTECT)
    data_emissao = models.DateField(auto_now_add=True)
    data_validade = models.DateField()
    qtd_pbr = models.PositiveIntegerField(default=0)
    qtd_chepp = models.PositiveIntegerField(default=0)
    codigo_barras = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    status = models.BooleanField(default=True)
    
    def _str_(self):
        return f"Vale {self.numero_vale} - {self.cliente.nome}"

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
    
    def _str_(self):
        return f"{self.get_tipo_display()} - Vale {self.vale.numero_vale}"