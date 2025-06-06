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
from django.utils import timezone

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

                    Movimentacao.objects.create(
                        vale=vale,
                        tipo='EMITIDO',
                        qtd_pbr=vale.qtd_pbr,
                        qtd_chepp=vale.qtd_chepp,
                        data_validade=vale.data_validade,  # PEGA DIRETO DO VALE
                        responsavel=request.user if request.user.is_authenticated else None,
                        observacao=f'Vale criado - PBR: {vale.qtd_pbr}, CHEP: {vale.qtd_chepp}'
                    )


                    # Dados para o QR Code (formato JSON)
                    qr_data = {
                        "id": vale.id,
                        "hash": vale.hash_seguranca,
                        "numero_vale": vale.numero_vale,
                        "url": request.build_absolute_uri(f'/valepallet/processar/{vale.id}/{vale.hash_seguranca}/')
                    }
                    
                    qr_code = generate_qr_code(qr_data)
                    qr_filename = f'vale_{vale.numero_vale}.png'
                    vale.qr_code.save(qr_filename, qr_code, save=True)

                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        qr_code.seek(0)
                        qr_base64 = base64.b64encode(qr_code.read()).decode('utf-8')
                        return JsonResponse({
                            'success': True,
                            'qr_code_url': f"data:image/png;base64,{qr_base64}",
                            'vale_id': vale.id,
                            'qr_data': qr_data  # Para debug
                        })

                    messages.success(request, f'Vale {vale.numero_vale} criado com sucesso!')
                    return redirect('valepallet_detalhes', id=vale.id)

            except Exception as e:
                logger.error(f"Erro ao criar vale pallet: {str(e)}", exc_info=True)
                messages.error(request, 'Erro ao criar vale pallet')
                return JsonResponse({'success': False, 'error': str(e)}, status=500)
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
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
@transaction.atomic
def processar_scan(request, id, hash_seguranca):
    try:
        # 1. Busca o vale pallet ou retorna 404
        vale = get_object_or_404(ValePallet, id=id, hash_seguranca=hash_seguranca)
        
        # 2. Registra quem está fazendo a operação (se autenticado)
        usuario = request.user if request.user.is_authenticated else None
        
        # 3. Lógica de transição de estados
        if vale.estado == 'EMITIDO':
            # Primeira transição: EMITIDO → SAIDA
            vale.estado = 'SAIDA'
            vale.usuario_saida = usuario
            vale.data_saida = timezone.now()  # Registrar data/hora da saída
            vale.save()
            
            Movimentacao.objects.create(
                vale=vale,
                tipo='SCAN',
                responsavel=usuario,
                observacao=f"Vale escaneado - Registrada SAÍDA"
            )
            
            messages.success(request, f'Vale {vale.numero_vale} registrado como SAÍDA com sucesso!')
            logger.info(f"Vale {vale.id} saída registrada por {usuario}")
            
        elif vale.estado == 'SAIDA':
            # Segunda transição: SAIDA → RETORNO
            vale.estado = 'RETORNO'
            vale.usuario_retorno = usuario
            vale.data_retorno = timezone.now()  # Registrar data/hora do retorno
            vale.save()
            
            Movimentacao.objects.create(
                vale=vale,
                tipo='SCAN',
                responsavel=usuario,
                observacao=f"Vale escaneado - Registrado RETORNO"
            )
            
            messages.success(request, f'Vale {vale.numero_vale} registrado como RETORNO com sucesso!')
            logger.info(f"Vale {vale.id} retorno registrado por {usuario}")
            
        elif vale.estado == 'RETORNO':
            # Vale já completou o ciclo
            messages.warning(request, f'Vale {vale.numero_vale} já completou o ciclo (SAÍDA → RETORNO)!')
            
        else:
            # Estado inválido/inesperado
            messages.error(request, f'Estado atual do vale {vale.numero_vale} não permite esta operação!')
        
        # 4. Redireciona para a página de detalhes
        return redirect('valepallet_detalhes', id=vale.id)
        
    except Exception as e:
        logger.error(f"Erro ao processar vale {id}: {str(e)}", exc_info=True)
        messages.error(request, 'Erro ao processar o vale pallet!')
        return redirect('valepallet_listar')


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
    vale_id = request.GET.get('vale_id')  # Para receber o vale específico
    
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST)
        if form.is_valid():
            try:
                movimentacao = form.save(commit=False)
                if request.user.is_authenticated:
                    movimentacao.responsavel = request.user
                
                # Atualiza automaticamente o vale relacionado
                if movimentacao.tipo == 'EMITIDO':
                    movimentacao.vale.estado = 'EMITIDO'
                elif movimentacao.tipo == 'SAIDA':
                    movimentacao.vale.estado = 'SAIDA'
                elif movimentacao.tipo == 'RETORNO':
                    movimentacao.vale.estado = 'RETORNO'
                
                movimentacao.vale.save()
                movimentacao.save()
                
                messages.success(request, 'Movimentação registrada com sucesso!')
                return redirect('valepallet_detalhes', id=movimentacao.vale.id)
                
            except Exception as e:
                logger.error(f"Erro ao registrar movimentação: {str(e)}")
                messages.error(request, f'Erro ao registrar movimentação: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        initial = {}
        if vale_id:
            initial['vale'] = vale_id
        form = MovimentacaoForm(initial=initial)
    
    return render(request, 'cadastro/movimentacao/listar.html', {
        'form': form,
        'titulo': 'Registrar Movimentação',
        'url_retorno': 'valepallet_listar'
    })
