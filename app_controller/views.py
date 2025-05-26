from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.db import transaction
from django.views.decorators.http import require_http_methods
from .models import Cliente, Motorista, Transportadora, ValePallet, Movimentacao
from .forms import ClienteForm, MotoristaForm, TransportadoraForm, ValePalletForm, MovimentacaoForm
from .utils import generate_qr_code
import base64
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# ===== PÁGINA INICIAL =====
def home(request):
    return render(request, 'cadastro/home.html')

# ===== CLIENTES =====
@require_http_methods(["GET"])
def cliente_listar(request):
    clientes = Cliente.objects.all().order_by('nome')
    return render(request, 'cadastro/listar.html', {
        'clientes': clientes,
        'titulo': 'Clientes',
        'url_cadastro': 'cliente_cadastrar',
        'url_edicao': 'cliente_editar'
    })

def cliente_cadastrar(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cliente cadastrado com sucesso!')
                return redirect('cliente_listar')
            except Exception as e:
                logger.error(f"Erro ao cadastrar cliente: {str(e)}")
                messages.error(request, 'Erro ao cadastrar cliente')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ClienteForm()
    
    return render(request, 'cadastro/form.html', {
        'form': form,
        'titulo': 'Cadastrar Cliente',
        'url_retorno': 'cliente_listar'
    })

def cliente_editar(request, id):
    cliente = get_object_or_404(Cliente, pk=id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cliente atualizado com sucesso!')
                return redirect('cliente_listar')
            except Exception as e:
                logger.error(f"Erro ao atualizar cliente: {str(e)}")
                messages.error(request, 'Erro ao atualizar cliente')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'cadastro/form.html', {
        'form': form,
        'titulo': 'Editar Cliente',
        'url_retorno': 'cliente_listar'
    })

@require_http_methods(["POST"])
def cliente_remover(request, id):
    cliente = get_object_or_404(Cliente, pk=id)
    try:
        cliente.delete()
        messages.success(request, 'Cliente removido com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover cliente: {str(e)}")
        messages.error(request, 'Erro ao remover cliente')
    return redirect('cliente_listar')

# ===== MOTORISTAS ===== 
@require_http_methods(["GET"])
def motorista_listar(request):
    motoristas = Motorista.objects.all().order_by('nome')
    return render(request, 'cadastro/motorista/listar.html', {
        'motoristas': motoristas,
        'titulo': 'Motoristas',
        'url_cadastro': 'motorista_cadastrar',
        'url_edicao': 'motorista_editar'
    })

def motorista_cadastrar(request):
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Motorista cadastrado com sucesso!')
                return redirect('motorista_listar')
            except Exception as e:
                logger.error(f"Erro ao cadastrar motorista: {str(e)}")
                messages.error(request, 'Erro ao cadastrar motorista')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = MotoristaForm()
    
    return render(request, 'cadastro/motorista/form.html', {
        'form': form,
        'titulo': 'Cadastrar Motorista',
        'url_retorno': 'motorista_listar'
    })

def motorista_editar(request, id):
    motorista = get_object_or_404(Motorista, pk=id)
    
    if request.method == 'POST':
        form = MotoristaForm(request.POST, instance=motorista)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Motorista atualizado com sucesso!')
                return redirect('motorista_listar')
            except Exception as e:
                logger.error(f"Erro ao atualizar motorista: {str(e)}")
                messages.error(request, 'Erro ao atualizar motorista')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = MotoristaForm(instance=motorista)
    
    return render(request, 'cadastro/motorista/form.html', {
        'form': form,
        'titulo': 'Editar Motorista',
        'url_retorno': 'motorista_listar'
    })

@require_http_methods(["POST"])
def motorista_remover(request, id):
    motorista = get_object_or_404(Motorista, pk=id)
    try:
        motorista.delete()
        messages.success(request, 'Motorista removido com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover motorista: {str(e)}")
        messages.error(request, 'Erro ao remover motorista')
    return redirect('motorista_listar')

# ===== TRANSPORTADORAS =====
@require_http_methods(["GET"])
def transportadora_listar(request):
    transportadoras = Transportadora.objects.all().order_by('nome')
    return render(request, 'cadastro/transportadora/listar.html', {
        'transportadoras': transportadoras,
        'titulo': 'Transportadoras',
        'url_cadastro': 'transportadora_cadastrar',
        'url_edicao': 'transportadora_editar'
    })

def transportadora_cadastrar(request):
    if request.method == 'POST':
        form = TransportadoraForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Transportadora cadastrada com sucesso!')
                return redirect('transportadora_listar')
            except Exception as e:
                logger.error(f"Erro ao cadastrar transportadora: {str(e)}")
                messages.error(request, 'Erro ao cadastrar transportadora')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = TransportadoraForm()
    
    return render(request, 'cadastro/transportadora/form.html', {
        'form': form,
        'titulo': 'Cadastrar Transportadora',
        'url_retorno': 'transportadora_listar'
    })

def transportadora_editar(request, id):
    transportadora = get_object_or_404(Transportadora, pk=id)
    
    if request.method == 'POST':
        form = TransportadoraForm(request.POST, instance=transportadora)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Transportadora atualizada com sucesso!')
                return redirect('transportadora_listar')
            except Exception as e:
                logger.error(f"Erro ao atualizar transportadora: {str(e)}")
                messages.error(request, 'Erro ao atualizar transportadora')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = TransportadoraForm(instance=transportadora)
    
    return render(request, 'cadastro/transportadora/form.html', {
        'form': form,
        'titulo': 'Editar Transportadora',
        'url_retorno': 'transportadora_listar'
    })

@require_http_methods(["POST"])
def transportadora_remover(request, id):
    transportadora = get_object_or_404(Transportadora, pk=id)
    try:
        transportadora.delete()
        messages.success(request, 'Transportadora removida com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover transportadora: {str(e)}")
        messages.error(request, 'Erro ao remover transportadora')
    return redirect('transportadora_listar')

# ===== VALE PALLET =====
@require_http_methods(["GET"])
def valepallet_listar(request):
    vales = ValePallet.objects.all().select_related(
        'cliente', 'motorista', 'transportadora'
    ).order_by('-data_emissao')
    
    return render(request, 'cadastro/valepallet/listar.html', {
        'vales': vales,
        'titulo': 'Vales Pallets',
        'url_cadastro': 'valepallet_cadastrar',
        'url_edicao': 'valepallet_editar'
    })

@transaction.atomic
def valepallet_cadastrar(request):
    # Carrega todos os dados para os selects (independente do método)
    clientes = Cliente.objects.all()
    motoristas = Motorista.objects.all()
    transportadoras = Transportadora.objects.all()
    
    if request.method == 'POST':
        form = ValePalletForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    vale = form.save(commit=False)
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

                    messages.success(request, f'Vale {vale.numero_vale} criado com sucesso!')
                    return redirect('valepallet_detalhes', id=vale.id)

            except Exception as e:
                logger.error(f"Erro ao criar vale pallet: {str(e)}", exc_info=True)
                messages.error(request, 'Erro ao criar vale pallet')
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': str(e)
                    }, status=500)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                }, status=400)
    else:
        form = ValePalletForm()

    context = {
        'form': form,
        'titulo': 'Novo Vale Pallet',
        'url_retorno': 'valepallet_listar',
        'clientes': clientes,
        'motoristas': motoristas,
        'transportadoras': transportadoras
    }
    return render(request, 'cadastro/valepallet/form.html', context)

@require_http_methods(["GET"])
def valepallet_detalhes(request, id):
    vale = get_object_or_404(ValePallet.objects.select_related(
        'cliente', 'motorista', 'transportadora', 'criado_por'
    ), pk=id)
    
    movimentacoes = Movimentacao.objects.filter(vale=vale).order_by('-data_hora')
    
    return render(request, 'cadastro/valepallet/detalhes.html', {
        'vale': vale,
        'movimentacoes': movimentacoes
    })

def valepallet_editar(request, id):
    vale = get_object_or_404(ValePallet, pk=id)
    
    if request.method == 'POST':
        form = ValePalletForm(request.POST, instance=vale)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Vale {vale.numero_vale} atualizado com sucesso!')
                return redirect('valepallet_detalhes', id=vale.id)
            except Exception as e:
                logger.error(f"Erro ao atualizar vale pallet: {str(e)}")
                messages.error(request, 'Erro ao atualizar vale pallet')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ValePalletForm(instance=vale)
    
    return render(request, 'cadastro/valepallet/form.html', {
        'form': form,
        'titulo': 'Editar Vale Pallet',
        'url_retorno': 'valepallet_listar'
    })

@require_http_methods(["POST"])
def valepallet_remover(request, id):
    vale = get_object_or_404(ValePallet, pk=id)
    try:
        vale.delete()
        messages.success(request, f'Vale {vale.numero_vale} removido com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover vale pallet: {str(e)}")
        messages.error(request, 'Erro ao remover vale pallet')
    return redirect('valepallet_listar')

# ===== VALIDAÇÃO QR CODE =====
@require_http_methods(["GET"])
def scan_qr_code(request):
    return render(request, 'cadastro/valepallet/scan_qr_code.html')

@transaction.atomic
def validar_qr(request):
    if request.method != 'POST':
        return redirect('scan_qr_code')
    
    qr_data = request.POST.get('qr_data', '').strip()
    if not qr_data:
        messages.error(request, "QR Code vazio!")
        return redirect('scan_qr_code')

    try:
        if not qr_data.startswith('vpallet:'):
            raise ValueError("Formato inválido. Use 'vpallet:id:hash'.")

        _, vale_id, hash_recebido = qr_data.split(':')
        vale = get_object_or_404(ValePallet, id=vale_id)

        if vale.hash_seguranca != hash_recebido:
            raise ValueError("QR Code adulterado ou inválido.")

        if vale.esta_vencido:
            messages.warning(request, f"Vale {vale.numero_vale} vencido!")
            return redirect('valepallet_detalhes', id=vale.id)

        # Determina o tipo de operação
        if vale.estado == 'UTILIZADO':
            tipo_operacao = 'DEVOLUCAO'
            novo_estado = 'RETORNADO'
            qtd_pbr = vale.saldo_pbr
            qtd_chepp = vale.saldo_chepp
        else:
            tipo_operacao = 'UTILIZACAO'
            novo_estado = 'UTILIZADO'
            qtd_pbr = vale.qtd_pbr
            qtd_chepp = vale.qtd_chepp

        # Cria movimentação
        Movimentacao.objects.create(
            vale=vale,
            tipo=tipo_operacao,
            qtd_pbr=qtd_pbr,
            qtd_chepp=qtd_chepp,
            responsavel=request.user.username
        )

        # Atualiza estado do vale
        vale.estado = novo_estado
        vale.save()

        messages.success(request, f"Vale {vale.numero_vale} atualizado com sucesso!")
        return redirect('valepallet_detalhes', id=vale.id)

    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        logger.error(f"Erro ao validar QR Code: {str(e)}")
        messages.error(request, "Erro ao processar QR Code")
    
    return redirect('scan_qr_code')

# ===== MOVIMENTAÇÕES =====
@require_http_methods(["GET"])
def movimentacao_listar(request):
    movimentacoes = Movimentacao.objects.select_related('vale').order_by('-data_hora')
    return render(request, 'cadastro/movimentacao/listar.html', {
        'movimentacoes': movimentacoes,
        'titulo': 'Movimentações'
    })

@transaction.atomic
def movimentacao_registrar(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            try:
                movimentacao = form.save()
                messages.success(request, 'Movimentação registrada com sucesso!')
                return redirect('movimentacao_listar')
            except Exception as e:
                logger.error(f"Erro ao registrar movimentação: {str(e)}")
                messages.error(request, 'Erro ao registrar movimentação')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = MovimentacaoForm()
    
    return render(request, 'cadastro/movimentacao/form.html', {
        'form': form,
        'titulo': 'Registrar Movimentação',
        'url_retorno': 'movimentacao_listar'
    })