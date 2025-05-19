from django import forms
from .models import Cliente, Motorista, Transportadora, ValePallet, Movimentacao
from django.utils import timezone

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'cnpj', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome Completo',
            'cnpj': 'CNPJ',
            'telefone': 'Telefone',
            'email': 'E-mail',
        }

class MotoristaForm(forms.ModelForm):
    class Meta:
        model = Motorista
        fields = ['nome', 'cpf', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome Completo',
            'cpf': 'CPF',
            'telefone': 'Telefone',
            'email': 'E-mail (opcional)',
        }

class TransportadoraForm(forms.ModelForm):
    class Meta:
        model = Transportadora
        fields = ['nome', 'cnpj', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome da Transportadora',
            'cnpj': 'CNPJ',
            'telefone': 'Telefone',
            'email': 'E-mail',
        }

class ValePalletForm(forms.ModelForm):
    data_validade = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now().date()
    )
    
    class Meta:
        model = ValePallet
        fields = ['numero_vale', 'cliente', 'motorista', 'transportadora', 
                 'data_validade', 'qtd_pbr', 'qtd_chepp', 'codigo_barras']
        widgets = {
            'numero_vale': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'motorista': forms.Select(attrs={'class': 'form-control'}),
            'transportadora': forms.Select(attrs={'class': 'form-control'}),
            'qtd_pbr': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'qtd_chepp': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero_vale': 'Número do Vale',
            'cliente': 'Cliente',
            'motorista': 'Motorista',
            'transportadora': 'Transportadora',
            'data_validade': 'Data de Validade',
            'qtd_pbr': 'Quantidade PBR',
            'qtd_chepp': 'Quantidade CHEP',
            'codigo_barras': 'Código de Barras',
        }

class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = ['vale', 'tipo', 'qtd_pbr', 'qtd_chepp', 'observacao']
        widgets = {
            'vale': forms.Select(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'qtd_pbr': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'qtd_chepp': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'vale': 'Vale de Pallet',
            'tipo': 'Tipo de Movimentação',
            'qtd_pbr': 'Quantidade PBR',
            'qtd_chepp': 'Quantidade CHEP',
            'observacao': 'Observações',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra os vales apenas para os que estão ativos (status=True)
        self.fields['vale'].queryset = ValePallet.objects.filter(status=True)