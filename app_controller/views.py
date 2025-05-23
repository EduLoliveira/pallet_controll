from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .models import Cliente, Motorista, Transportadora, ValePallet, Movimentacao
from .forms import ClienteForm, MotoristaForm, TransportadoraForm, ValePalletForm, MovimentacaoForm
from .utils import generate_qr_code
import base64

# ===== PÁGINA INICIAL =====
def home(request):
    return render(request, 'cadastro/home.html')

# ===== CLIENTES (Mantido igual - está correto) =====
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
    vales = ValePallet.objects.all().order_by('-id')  # Lista todos os vales (GET)
    return render(request, 'cadastro/valepallet/listar.html', {'vales': vales})

def valepallet_cadastrar(request):
    if request.method == 'POST':
        form = ValePalletForm(request.POST)
        if form.is_valid():
            try:
                vale = form.save(commit=False)
                vale.criado_por = request.user
                vale.hash_seguranca = get_random_string(length=32)
                vale.save()

                # Gera QR Code
                qr_data = f"vpallet:{vale.id}:{vale.hash_seguranca}"
                qr_code = generate_qr_code(qr_data)
                qr_filename = f'vale_{vale.numero_vale}.png'
                vale.qr_code.save(qr_filename, qr_code, save=True)

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    qr_code.seek(0)
                    qr_base64 = base64.b64encode(qr_code.read()).decode('utf-8')
                    return JsonResponse({
                        'success': True,
                        'qr_code_url': f"data:image/png;base64,{qr_base64}",
                        'vale_id': vale.id
                    })

                messages.success(request, f'Vale {vale.numero_vale} criado!')
                return redirect('valepallet_detalhes', id=vale.id)

            except Exception as e:
                messages.error(request, f'Erro ao criar vale: {str(e)}')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': str(e)}, status=400)

        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    form = ValePalletForm()
    return render(request, 'cadastro/valepallet/form.html', {'form': form, 'titulo': 'Novo Vale'})
def valepallet_detalhes(request, id):
    vale = get_object_or_404(ValePallet, pk=id)
    return render(request, 'cadastro/valepallet/detalhes.html', {'vale': vale})

def valepallet_editar(request, id):
    vale = get_object_or_404(ValePallet, pk=id)
    if request.method == 'POST':
        form = ValePalletForm(request.POST, instance=vale)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vale {vale.numero_vale} atualizado!')
            return redirect('valepallet_detalhes', id=vale.id)
    else:
        form = ValePalletForm(instance=vale)
    return render(request, 'cadastro/valepallet/form.html', {'form': form, 'titulo': 'Editar Vale'})

def valepallet_remover(request, id):
    vale = get_object_or_404(ValePallet, pk=id)
    vale.delete()
    messages.success(request, f'Vale {vale.numero_vale} removido!')
    return redirect('valepallet_listar')


# ========== Valida QR Code ============ #
def scan_qr_code(request):
    """Página para escanear QR code"""
    return render(request, 'cadastro/valepallet/scan_qr_code.html')

def validar_qr(request):
    if request.method == 'POST':
        qr_data = request.POST.get('qr_data', '').strip()
        if not qr_data:
            messages.error(request, "QR Code vazio!")
            return redirect('scan_qr_code')

        try:
            # Valida formato do QR Code
            if not qr_data.startswith('vpallet:'):
                raise ValueError("Formato inválido. Use 'vpallet:id:hash'.")

            _, vale_id, hash_recebido = qr_data.split(':')
            vale = get_object_or_404(ValePallet, id=vale_id)

            # Valida hash
            if vale.hash_seguranca != hash_recebido:
                raise ValueError("QR Code adulterado ou inválido.")

            # Valida vencimento
            if vale.esta_vencido:
                messages.warning(request, f"Vale {vale.numero_vale} vencido!")
                return redirect('valepallet_detalhes', id=vale.id)

            # Registra movimentação
            tipo_operacao = 'DEVOLUCAO' if vale.estado == 'UTILIZADO' else 'UTILIZACAO'
            Movimentacao.objects.create(
                vale=vale,
                tipo=tipo_operacao,
                qtd_pbr=vale.qtd_pbr,
                qtd_chepp=vale.qtd_chepp,
                responsavel=request.user.username
            )

            # Atualiza estado
            vale.estado = 'RETORNADO' if vale.estado == 'UTILIZADO' else 'UTILIZADO'
            vale.save()

            messages.success(request, f"Vale {vale.numero_vale} atualizado!")
            return redirect('valepallet_detalhes', id=vale.id)

        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Erro interno: {str(e)}")

    return redirect('scan_qr_code')


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