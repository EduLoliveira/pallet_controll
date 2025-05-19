from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cliente, Motorista, Transportadora, ValePallet, Movimentacao
from .forms import ClienteForm, MotoristaForm, TransportadoraForm, ValePalletForm, MovimentacaoForm

# ===== PÁGINA INICIAL =====
def home(request):
    return render(request, 'cadastro/home.html')

# ===== CLIENTES =====
def cliente_listar(request):
    clientes = Cliente.objects.all()
    return render(request, 'cadastro/listar.html', {'clientes': clientes})

def cliente_cadastrar(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('cliente_listar')
    else:
        form = ClienteForm()
    return render(request, 'cadastro/form.html', {'form': form, 'titulo': 'Cadastrar Cliente'})

def cliente_editar(request, id):
    cliente = get_object_or_404(Cliente, pk=id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado!')
            return redirect('cliente_listar')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'cadastro/form.html', {'form': form, 'titulo': 'Editar Cliente'})

def cliente_remover(request, id):
    cliente = get_object_or_404(Cliente, pk=id)
    cliente.delete()
    messages.success(request, 'Cliente removido!')
    return redirect('cliente_listar')

# ===== MOTORISTAS ===== (mesma estrutura dos clientes)
def motorista_listar(request):
    motoristas = Motorista.objects.all()
    return render(request, 'cadastro/motorista/listar.html', {'motoristas': motoristas})

def motorista_cadastrar(request):
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Motorista cadastrado!')
            return redirect('motorista_listar')
    else:
        form = MotoristaForm()
    return render(request, 'cadastro/motorista/form.html', {'form': form, 'titulo': 'Cadastrar Motorista'})

def motorista_editar(request, id):
    motorista = get_object_or_404(Motorista, pk=id)
    if request.method == 'POST':
        form = MotoristaForm(request.POST, instance=motorista)
        if form.is_valid():
            form.save()
            messages.success(request, 'Motorista atualizado!')
            return redirect('motorista_listar')
    else:
        form = MotoristaForm(instance=motorista)
    return render(request, 'cadastro/motorista/form.html', {'form': form, 'titulo': 'Editar Motorista'})

def motorista_remover(request, id):
    motorista = get_object_or_404(Motorista, pk=id)
    motorista.delete()
    messages.success(request, 'Motorista removido!')
    return redirect('motorista_listar')

# ===== TRANSPORTADORAS =====
def transportadora_listar(request):
    transportadoras = Transportadora.objects.all()
    return render(request, 'cadastro/transportadora/listar.html', {'transportadoras': transportadoras})

def transportadora_cadastrar(request):
    if request.method == 'POST':
        form = TransportadoraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transportadora cadastrada com sucesso!')
            return redirect('transportadora_listar')
    else:
        form = TransportadoraForm()
    return render(request, 'cadastro/transportadora/form.html', {'form': form, 'titulo': 'Cadastrar Transportadora'})

def transportadora_editar(request, id):
    transportadora = get_object_or_404(Transportadora, pk=id)
    if request.method == 'POST':
        form = TransportadoraForm(request.POST, instance=transportadora)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transportadora atualizada!')
            return redirect('transportadora_listar')
    else:
        form = TransportadoraForm(instance=transportadora)
    return render(request, 'cadastro/transportadora/form.html', {'form': form, 'titulo': 'Editar Transportadora'})

def transportadora_remover(request, id):
    transportadora = get_object_or_404(Transportadora, pk=id)
    transportadora.delete()
    messages.success(request, 'Transportadora removida!')
    return redirect('transportadora_listar')

# ===== VALE PALLET =====
def valepallet_listar(request):
    vales = ValePallet.objects.all()
    return render(request, 'cadastro/valepallet/listar.html', {'vales': vales})

def valepallet_cadastrar(request):
    if request.method == 'POST':
        form = ValePalletForm(request.POST)
        if form.is_valid():
            vale = form.save()
            messages.success(request, f'Vale {vale.numero_vale} criado!')
            return redirect('valepallet_listar')
    else:
        form = ValePalletForm()
    return render(request, 'cadastro/valepallet/form.html', {'form': form, 'titulo': 'Novo Vale'})

def valepallet_editar(request, id):
    vale = get_object_or_404(ValePallet, pk=id)
    if request.method == 'POST':
        form = ValePalletForm(request.POST, instance=vale)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vale {vale.numero_vale} atualizado!')
            return redirect('valepallet_listar')
    else:
        form = ValePalletForm(instance=vale)
    return render(request, 'cadastro/valepallet/form.html', {'form': form, 'titulo': 'Editar Vale'})

def valepallet_remover(request, id):
    vale = get_object_or_404(ValePallet, pk=id)
    vale.delete()
    messages.success(request, f'Vale {vale.numero_vale} removido!')
    return redirect('valepallet_listar')


# ===== MOVIMENTAÇÕES =====
def movimentacao_registrar(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            movimentacao = form.save()
            messages.success(request, f'Movimentação {movimentacao.get_tipo_display()} registrada!')
            return redirect('movimentacao_listar')
    else:
        form = MovimentacaoForm()
    return render(request, 'cadastro/movimentacao/form.html', {'form': form})

def movimentacao_listar(request):
    movimentacoes = Movimentacao.objects.all().order_by('-data_hora')
    return render(request, 'cadastro/movimentacao/listar.html', {'movimentacoes': movimentacoes})