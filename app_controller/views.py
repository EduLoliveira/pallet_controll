from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.db import transaction
from django.views.decorators.http import require_http_methods, require_GET
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import login
from .models import Cliente, Motorista, Transportadora, ValePallet, Movimentacao
from .forms import ClienteForm, MotoristaForm, TransportadoraForm, ValePalletForm, MovimentacaoForm, UsuarioPJForm, PessoaJuridicaForm
from .utils import generate_qr_code
import logging
import requests

logger = logging.getLogger(__name__)

# ==============================================
# PÁGINA INICIAL E AUTENTICAÇÃO
# ==============================================
def home(request):
    """Página inicial. Redireciona para o painel se o usuário estiver logado."""
    if request.user.is_authenticated:
        return redirect('painel_usuario')
    return render(request, 'cadastro/home.html')

@transaction.atomic
def cadastrar_pessoa_juridica(request):
    """Cadastro de Pessoa Jurídica (com usuário associado)."""
    if request.method == 'POST':
        usuario_form = UsuarioPJForm(request.POST)
        pj_form = PessoaJuridicaForm(request.POST)
        
        if usuario_form.is_valid() and pj_form.is_valid():
            try:
                # Salva o usuário primeiro
                usuario = usuario_form.save(commit=False)
                usuario.set_password(usuario_form.cleaned_data['password1'])
                usuario.save()
                
                # Depois salva a Pessoa Jurídica
                pessoa_juridica = pj_form.save(commit=False)
                pessoa_juridica.usuario = usuario
                pessoa_juridica.save()
                
                # Faz login do usuário
                login(request, usuario)
                messages.success(request, 'Cadastro realizado com sucesso!')
                return redirect('painel_usuario')
                
            except Exception as e:
                logger.error(f"Erro ao cadastrar Pessoa Jurídica: {str(e)}")
                messages.error(request, 'Ocorreu um erro durante o cadastro. Por favor, tente novamente.')
        else:
            # Adicione esta linha para ver os erros de validação no console
            print("Erros no formulário de usuário:", usuario_form.errors)
            print("Erros no formulário PJ:", pj_form.errors)
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        usuario_form = UsuarioPJForm()
        pj_form = PessoaJuridicaForm()
    
    return render(request, 'cadastro/login.html', {
        'usuario_form': usuario_form,
        'pj_form': pj_form,
    })

@login_required
def painel_usuario(request):
    """Painel principal após login."""
    return render(request, 'cadastro/painel_usuario.html')

# ==============================================
# CRUD CLIENTES
# ==============================================
@login_required
@require_http_methods(["GET"])
def cliente_listar(request):
    """Lista clientes vinculados à PJ do usuário."""
    clientes = Cliente.objects.filter(criado_por=request.user.pessoajuridica).order_by('nome')
    return render(request, 'cadastro/cliente/listar.html', {
        'clientes': clientes,
        'titulo': 'Clientes',
        'url_cadastro': 'cliente_cadastrar',
        'url_edicao': 'cliente_editar'
    })

@login_required
@require_http_methods(["GET", "POST"])
def cliente_cadastrar(request):
    """Cadastra novo cliente."""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                cliente = form.save(commit=False)
                cliente.criado_por = request.user.pessoajuridica
                cliente.save()
                messages.success(request, 'Cliente cadastrado com sucesso!')
                return redirect('cliente_listar')
            except Exception as e:
                logger.error(f"Erro ao cadastrar cliente: {str(e)}")
                messages.error(request, 'Erro ao cadastrar cliente')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ClienteForm()
    
    return render(request, 'cadastro/cliente/form.html', {
        'form': form,
        'titulo': 'Cadastrar Cliente',
        'url_retorno': 'cliente_listar'
    })

@login_required
@require_http_methods(["GET", "POST"])
def cliente_editar(request, id):
    """Edita cliente existente."""
    cliente = get_object_or_404(Cliente, pk=id, criado_por=request.user.pessoajuridica)
    
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
    
    return render(request, 'cadastro/cliente/form.html', {
        'form': form,
        'titulo': 'Editar Cliente',
        'url_retorno': 'cliente_listar'
    })

@login_required
@require_http_methods(["POST"])
def cliente_remover(request, id):
    """Remove cliente (apenas POST)."""
    cliente = get_object_or_404(Cliente, pk=id, criado_por=request.user.pessoajuridica)
    try:
        cliente.delete()
        messages.success(request, 'Cliente removido com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover cliente: {str(e)}")
        messages.error(request, 'Erro ao remover cliente')
    return redirect('cliente_listar')

# ==============================================
# CRUD MOTORISTAS
# ==============================================
@login_required
@require_http_methods(["GET"])
def motorista_listar(request):
    """Lista motoristas vinculados à PJ do usuário."""
    motoristas = Motorista.objects.filter(criado_por=request.user.pessoajuridica).order_by('nome')
    return render(request, 'cadastro/motorista/listar.html', {
        'motoristas': motoristas,
        'titulo': 'Motoristas',
        'url_cadastro': 'motorista_cadastrar',
        'url_edicao': 'motorista_editar'
    })

@login_required
@require_http_methods(["GET", "POST"])
def motorista_cadastrar(request):
    """Cadastra novo motorista."""
    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            try:
                motorista = form.save(commit=False)
                motorista.criado_por = request.user.pessoajuridica
                motorista.save()
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

@login_required
@require_http_methods(["GET", "POST"])
def motorista_editar(request, id):
    """Edita motorista existente."""
    motorista = get_object_or_404(Motorista, pk=id, criado_por=request.user.pessoajuridica)
    
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

@login_required
@require_http_methods(["POST"])
def motorista_remover(request, id):
    """Remove motorista (apenas POST)."""
    motorista = get_object_or_404(Motorista, pk=id, criado_por=request.user.pessoajuridica)
    try:
        motorista.delete()
        messages.success(request, 'Motorista removido com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover motorista: {str(e)}")
        messages.error(request, 'Erro ao remover motorista')
    return redirect('motorista_listar')

# ==============================================
# CRUD TRANSPORTADORAS
# ==============================================
@login_required
@require_http_methods(["GET"])
def transportadora_listar(request):
    """Lista transportadoras vinculadas à PJ do usuário."""
    transportadoras = Transportadora.objects.filter(criado_por=request.user.pessoajuridica).order_by('nome')
    return render(request, 'cadastro/transportadora/listar.html', {
        'transportadoras': transportadoras,
        'titulo': 'Transportadoras',
        'url_cadastro': 'transportadora_cadastrar',
        'url_edicao': 'transportadora_editar'
    })

@login_required
@require_http_methods(["GET", "POST"])
def transportadora_cadastrar(request):
    """Cadastra nova transportadora."""
    if request.method == 'POST':
        form = TransportadoraForm(request.POST)
        if form.is_valid():
            try:
                transportadora = form.save(commit=False)
                transportadora.criado_por = request.user.pessoajuridica
                transportadora.save()
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

@login_required
@require_http_methods(["GET", "POST"])
def transportadora_editar(request, id):
    """Edita transportadora existente."""
    transportadora = get_object_or_404(Transportadora, pk=id, criado_por=request.user.pessoajuridica)
    
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

@login_required
@require_http_methods(["POST"])
def transportadora_remover(request, id):
    """Remove transportadora (apenas POST)."""
    transportadora = get_object_or_404(Transportadora, pk=id, criado_por=request.user.pessoajuridica)
    try:
        transportadora.delete()
        messages.success(request, 'Transportadora removida com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover transportadora: {str(e)}")
        messages.error(request, 'Erro ao remover transportadora')
    return redirect('transportadora_listar')

# ==============================================
# GESTÃO DE VALES PALLETS
# ==============================================
@login_required
@require_http_methods(["GET"])
def valepallet_listar(request):
    """Lista vales pallets vinculados à PJ do usuário."""
    vales = ValePallet.objects.filter(
        criado_por_pj=request.user.pessoajuridica
    ).select_related('cliente', 'motorista', 'transportadora').order_by('-data_emissao')
    return render(request, 'cadastro/valepallet/listar.html', {
        'vales': vales,
        'titulo': 'Vales Pallets',
        'url_cadastro': 'valepallet_cadastrar',
        'url_edicao': 'valepallet_editar'
    })

@login_required
@transaction.atomic
@require_http_methods(["GET", "POST"])
def valepallet_cadastrar(request):
    """Cadastra novo vale pallet."""
    if request.method == 'POST':
        form = ValePalletForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                vale = form.save(commit=False)
                vale.criado_por_pj = request.user.pessoajuridica
                vale.hash_seguranca = get_random_string(32)
                vale.save()

                # Cria movimentação inicial
                Movimentacao.objects.create(
                    vale=vale,
                    tipo='EMITIDO',
                    qtd_pbr=vale.qtd_pbr,
                    qtd_chepp=vale.qtd_chepp,
                    responsavel=request.user
                )

                # Gera QR Code
                qr_data = {
                    "id": vale.id,
                    "hash": vale.hash_seguranca,
                    "numero_vale": vale.numero_vale,
                    "url": request.build_absolute_uri(
                        reverse('processar_scan', args=[vale.id, vale.hash_seguranca])
                    )
                }
                qr_code = generate_qr_code(qr_data)
                vale.qr_code.save(f'vale_{vale.numero_vale}.png', qr_code, save=True)

                messages.success(request, f'Vale {vale.numero_vale} criado com sucesso!')
                return redirect('valepallet_detalhes', id=vale.id)

            except Exception as e:
                logger.error(f"Erro ao criar vale pallet: {str(e)}")
                messages.error(request, 'Erro ao criar vale pallet')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ValePalletForm(user=request.user)
    
    return render(request, 'cadastro/valepallet/form.html', {
        'form': form,
        'titulo': 'Novo Vale Pallet',
        'url_retorno': 'valepallet_listar'
    })

@login_required
@require_http_methods(["GET"])
def valepallet_detalhes(request, id):
    """Exibe detalhes de um vale pallet específico."""
    vale = get_object_or_404(
        ValePallet, 
        pk=id, 
        criado_por_pj=request.user.pessoajuridica
    )
    movimentacoes = Movimentacao.objects.filter(vale=vale).order_by('-data_hora')
    return render(request, 'cadastro/valepallet/detalhes.html', {
        'vale': vale,
        'movimentacoes': movimentacoes,
        'titulo': f'Detalhes do Vale {vale.numero_vale}'
    })

@login_required
@require_http_methods(["GET", "POST"])
def valepallet_editar(request, id):
    """Edita vale pallet existente."""
    vale = get_object_or_404(
        ValePallet, 
        pk=id, 
        criado_por_pj=request.user.pessoajuridica
    )
    
    if request.method == 'POST':
        form = ValePalletForm(request.POST, instance=vale, user=request.user)
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
        form = ValePalletForm(instance=vale, user=request.user)
    
    return render(request, 'cadastro/valepallet/form.html', {
        'form': form,
        'titulo': f'Editar Vale {vale.numero_vale}',
        'url_retorno': 'valepallet_listar'
    })

@login_required
@require_http_methods(["POST"])
def valepallet_remover(request, id):
    """Remove vale pallet (apenas POST)."""
    vale = get_object_or_404(
        ValePallet, 
        pk=id, 
        criado_por_pj=request.user.pessoajuridica
    )
    try:
        vale.delete()
        messages.success(request, f'Vale {vale.numero_vale} removido com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover vale pallet: {str(e)}")
        messages.error(request, 'Erro ao remover vale pallet')
    return redirect('valepallet_listar')

@login_required
@transaction.atomic
@require_http_methods(["GET"])
def processar_scan(request, id, hash_seguranca):
    """Processa o scan do QR Code (muda estado do vale)."""
    vale = get_object_or_404(
        ValePallet, 
        pk=id, 
        hash_seguranca=hash_seguranca,
        criado_por_pj=request.user.pessoajuridica
    )
    
    try:
        if vale.estado == 'EMITIDO':
            vale.estado = 'SAIDA'
            vale.usuario_saida = request.user
            vale.data_saida = timezone.now()
            vale.save()
            Movimentacao.objects.create(
                vale=vale,
                tipo='SAIDA',
                responsavel=request.user,
                observacao='Saída registrada via QR Code'
            )
            messages.success(request, 'Saída registrada com sucesso!')

        elif vale.estado == 'SAIDA':
            vale.estado = 'RETORNO'
            vale.usuario_retorno = request.user
            vale.data_retorno = timezone.now()
            vale.save()
            Movimentacao.objects.create(
                vale=vale,
                tipo='RETORNO',
                responsavel=request.user,
                observacao='Retorno registrado via QR Code'
            )
            messages.success(request, 'Retorno registrado com sucesso!')

        return redirect('valepallet_detalhes', id=vale.id)

    except Exception as e:
        logger.error(f"Erro ao processar QR Code: {str(e)}")
        messages.error(request, 'Erro no processamento do QR Code')
        return redirect('valepallet_listar')

# ==============================================
# GESTÃO DE MOVIMENTAÇÕES
# ==============================================
@login_required
@require_http_methods(["GET"])
def movimentacao_listar(request):
    """Lista todas as movimentações."""
    movimentacoes = Movimentacao.objects.filter(
        vale__criado_por_pj=request.user.pessoajuridica
    ).select_related('vale', 'responsavel').order_by('-data_hora')
    return render(request, 'cadastro/movimentacao/listar.html', {
        'movimentacoes': movimentacoes,
        'titulo': 'Movimentações'
    })

@login_required
@transaction.atomic
@require_http_methods(["GET", "POST"])
def movimentacao_registrar(request):
    """Registra nova movimentação manualmente."""
    vale_id = request.GET.get('vale_id')
    
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                movimentacao = form.save(commit=False)
                movimentacao.responsavel = request.user
                
                # Atualiza estado do vale se necessário
                if movimentacao.tipo in ['SAIDA', 'RETORNO']:
                    movimentacao.vale.estado = movimentacao.tipo
                    movimentacao.vale.save()
                
                movimentacao.save()
                messages.success(request, 'Movimentação registrada com sucesso!')
                return redirect('valepallet_detalhes', id=movimentacao.vale.id)
            except Exception as e:
                logger.error(f"Erro ao registrar movimentação: {str(e)}")
                messages.error(request, 'Erro ao registrar movimentação')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        initial = {}
        if vale_id:
            initial['vale'] = vale_id
        form = MovimentacaoForm(initial=initial, user=request.user)
    
    return render(request, 'cadastro/movimentacao/form.html', {
        'form': form,
        'titulo': 'Registrar Movimentação',
        'url_retorno': 'valepallet_listar'
    })

# ==============================================
# APIs DE CONSULTA (CNPJ, CEP, etc.)
# ==============================================
@require_GET
def validar_cnpj_api(request):
    cnpj = request.GET.get('cnpj', '').replace('.', '').replace('/', '').replace('-', '')
    if not cnpj.isdigit() or len(cnpj) != 14:
        return JsonResponse({'valido': False, 'erro': 'CNPJ inválido'}, status=400)
    
    try:
        response = requests.get(f'https://receitaws.com.br/v1/cnpj/{cnpj}', timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'ERROR':
            return JsonResponse({'valido': False, 'erro': data.get('message', 'CNPJ inválido')})
        
        return JsonResponse({
            'valido': True,
            'DsRazaoSocial': data.get('nome', ''),
            'DsNomeFantasia': data.get('fantasia', ''),
            'DsSituacaoCadastral': data.get('situacao', ''),
            'DsEnderecoLogradouro': data.get('logradouro', ''),
            'NrEnderecoNumero': data.get('numero', ''),
            'DsEnderecoBairro': data.get('bairro', ''),
            'NrEnderecoCep': data.get('cep', '').replace('.', '').replace('-', ''),
            'DsEnderecoCidade': data.get('municipio', ''),
            'DsEnderecoEstado': data.get('uf', ''),
            'DsEmail': data.get('email', '')
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar CNPJ: {str(e)}")
        return JsonResponse({'valido': False, 'erro': 'Serviço indisponível'}, status=503)
    except Exception as e:
        logger.error(f"Erro inesperado ao validar CNPJ: {str(e)}")
        return JsonResponse({'valido': False, 'erro': 'Erro interno'}, status=500)


@require_GET
def consultar_cep_api(request):
    cep = request.GET.get('cep', '').replace('-', '')
    
    if not cep.isdigit() or len(cep) != 8:
        return JsonResponse({'erro': 'CEP deve conter 8 dígitos numéricos.'}, status=400)
    
    # Primeiro tentamos ViaCEP
    try:
        viacep_response = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=3)
        viacep_response.raise_for_status()
        viacep_data = viacep_response.json()
        
        if not viacep_data.get('erro'):
            return JsonResponse({
                'success': True,
                'DsEnderecoLogradouro': viacep_data.get('logradouro', ''),
                'DsEnderecoBairro': viacep_data.get('bairro', ''),
                'DsEnderecoCidade': viacep_data.get('localidade', ''),
                'DsEnderecoEstado': viacep_data.get('uf', ''),
                'DsEnderecoComplemento': viacep_data.get('complemento', ''),
                'api_utilizada': 'ViaCEP'
            })
    except requests.exceptions.RequestException as viacep_error:
        logger.warning(f"Falha na consulta ViaCEP: {str(viacep_error)}")
    
    # Se ViaCEP falhar, tentamos BrasilAPI
    try:
        brasilapi_response = requests.get(f'https://brasilapi.com.br/api/cep/v2/{cep}', timeout=3)
        brasilapi_response.raise_for_status()
        brasilapi_data = brasilapi_response.json()
        
        return JsonResponse({
            'success': True,
            'DsEnderecoLogradouro': brasilapi_data.get('street', ''),
            'DsEnderecoBairro': brasilapi_data.get('neighborhood', ''),
            'DsEnderecoCidade': brasilapi_data.get('city', ''),
            'DsEnderecoEstado': brasilapi_data.get('state', ''),
            'DsEnderecoComplemento': brasilapi_data.get('complement', ''),
            'api_utilizada': 'BrasilAPI'
        })
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return JsonResponse({'erro': 'CEP não encontrado em nenhuma base.'}, status=404)
        logger.error(f"Erro BrasilAPI: {str(e)}")
        return JsonResponse({'erro': 'Serviço de consulta retornou erro.'}, status=502)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão BrasilAPI: {str(e)}")
        return JsonResponse({'erro': 'Não foi possível conectar aos serviços de consulta.'}, status=503)
    
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return JsonResponse({'erro': 'Erro interno ao processar CEP.'}, status=500)
    
@require_GET
def listar_estados_api(request):
    """
    API para listar estados brasileiros usando IBGE
    """
    try:
        response = requests.get(
            'https://servicodados.ibge.gov.br/api/v1/localidades/estados',
            timeout=10
        )
        response.raise_for_status()
        
        estados = [{
            'sigla': est['sigla'],
            'nome': est['nome']
        } for est in response.json()]
        
        return JsonResponse({
            'estados': sorted(estados, key=lambda x: x['nome'])
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao listar estados: {str(e)}")
        return JsonResponse(
            {'error': 'Serviço indisponível'},
            status=503
        )
    except Exception as e:
        logger.error(f"Erro inesperado na API de estados: {str(e)}")
        return JsonResponse(
            {'error': 'Erro interno no servidor'},
            status=500
        )

@require_GET
def listar_municipios_api(request, uf):
    """
    API para listar municípios por UF usando IBGE
    """
    if not uf or len(uf) != 2:
        return JsonResponse(
            {'error': 'UF inválida'},
            status=400
        )

    try:
        response = requests.get(
            f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios',
            timeout=10
        )
        response.raise_for_status()
        
        municipios = [{
            'id': mun['id'],
            'nome': mun['nome']
        } for mun in response.json()]
        
        return JsonResponse({
            'municipios': sorted(municipios, key=lambda x: x['nome'])
        })

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao listar municípios: {str(e)}")
        return JsonResponse(
            {'error': 'Serviço indisponível'},
            status=503
        )
    except Exception as e:
        logger.error(f"Erro inesperado na API de municípios: {str(e)}")
        return JsonResponse(
            {'error': 'Erro interno no servidor'},
            status=500
        )