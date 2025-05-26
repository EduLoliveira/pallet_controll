from django import forms
from django.core.validators import RegexValidator
from django.utils import timezone
from .models import Cliente, Motorista, Transportadora, ValePallet, Movimentacao

# ===== CONSTANTES DE VALIDAÇÃO =====
CNPJ_REGEX = r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'
CPF_REGEX = r'^\d{3}\.\d{3}\.\d{3}-\d{2}$'
TELEFONE_REGEX = r'^\(\d{2}\) \d{5}-\d{4}$'

# ===== FORMULÁRIOS PRINCIPAIS =====
class ClienteForm(forms.ModelForm):
    cnpj = forms.CharField(
        validators=[RegexValidator(
            regex=CNPJ_REGEX,
            message='CNPJ inválido (padrão: 00.000.000/0000-00)'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00.000.000/0000-00'
        })
    )
    
    telefone = forms.CharField(
        validators=[RegexValidator(
            regex=TELEFONE_REGEX,
            message='Telefone inválido (padrão: (00) 00000-0000)'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000'
        })
    )

    class Meta:
        model = Cliente
        fields = ['nome', 'cnpj', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail',
        }

class MotoristaForm(forms.ModelForm):
    cpf = forms.CharField(
        validators=[RegexValidator(
            regex=CPF_REGEX,
            message='CPF inválido (padrão: 000.000.000-00)'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00'
        })
    )
    
    telefone = forms.CharField(
        validators=[RegexValidator(
            regex=TELEFONE_REGEX,
            message='Telefone inválido (padrão: (00) 00000-0000)'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000'
        })
    )

    class Meta:
        model = Motorista
        fields = ['nome', 'cpf', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail (opcional)',
        }

class TransportadoraForm(forms.ModelForm):
    cnpj = forms.CharField(
        validators=[RegexValidator(
            regex=CNPJ_REGEX,
            message='CNPJ inválido (padrão: 00.000.000/0000-00)'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00.000.000/0000-00'
        })
    )
    
    telefone = forms.CharField(
        validators=[RegexValidator(
            regex=TELEFONE_REGEX,
            message='Telefone inválido (padrão: (00) 00000-0000)'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(00) 00000-0000'
        })
    )

    class Meta:
        model = Transportadora
        fields = ['nome', 'cnpj', 'telefone', 'email']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome da Transportadora',
            'email': 'E-mail',
        }

# ===== FORMULÁRIOS DE OPERAÇÕES =====
class ValePalletForm(forms.ModelForm):
    data_validade = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().strftime('%Y-%m-%d')
        }),
        initial=timezone.now().date()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nome')
        self.fields['motorista'].queryset = Motorista.objects.all().order_by('nome')
        self.fields['transportadora'].queryset = Transportadora.objects.all().order_by('nome')
        
        # Melhoria para selects
        for field in ['cliente', 'motorista', 'transportadora']:
            self.fields[field].widget.attrs.update({'class': 'form-select'})

    class Meta:
        model = ValePallet
        fields = ['numero_vale', 'cliente', 'motorista', 'transportadora', 
                 'data_validade', 'qtd_pbr', 'qtd_chepp']
        widgets = {
            'numero_vale': forms.TextInput(attrs={'class': 'form-control'}),
            'qtd_pbr': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1
            }),
            'qtd_chepp': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1
            }),
        }
        labels = {
            'numero_vale': 'Número do Vale',
            'data_validade': 'Data de Validade',
            'qtd_pbr': 'Quantidade PBR',
            'qtd_chepp': 'Quantidade CHEP',
        }

class MovimentacaoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vale'].queryset = ValePallet.objects.filter(
            status=True
        ).order_by('-id')
        
        # Atualiza classes para Bootstrap 5
        self.fields['tipo'].widget.attrs.update({'class': 'form-select'})
        self.fields['observacao'].widget.attrs.update({'rows': 3})

    class Meta:
        model = Movimentacao
        fields = ['vale', 'tipo', 'qtd_pbr', 'qtd_chepp', 'observacao']
        widgets = {
            'qtd_pbr': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1
            }),
            'qtd_chepp': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 1
            }),
        }
        labels = {
            'vale': 'Vale de Pallet',
            'tipo': 'Tipo de Movimentação',
            'observacao': 'Observações',
        }