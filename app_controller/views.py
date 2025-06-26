from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils.crypto import get_random_string
from django.db import transaction
from django.views.decorators.http import require_http_methods, require_GET
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout
from .models import Cliente, Motorista, Transportadora, ValePallet, Movimentacao, PessoaJuridica, Usuario
from .forms import ClienteForm, MotoristaForm, TransportadoraForm, ValePalletForm, MovimentacaoForm, UsuarioPJForm, PessoaJuridicaForm
from .utils import generate_qr_code
import logging
import requests
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test, login_required
from django.db.models import Q, Count, Sum
from datetime import timedelta


logger = logging.getLogger(__name__)


def staff_required(view_func=None, redirect_url='painel_usuario'):
    """
    Decorator que verifica se o usuário é staff
    """
    def check_staff(user):
        return user.is_authenticated and user.is_staff
    
    if view_func:
        return user_passes_test(check_staff, login_url=redirect_url)(view_func)
    return user_passes_test(check_staff, login_url=redirect_url)

# ==============================================
# PÁGINA INICIAL E AUTENTICAÇÃO
# ==============================================
@csrf_exempt
def login(request):
    """
    View de login com logging profissional
    """
    if request.user.is_authenticated:
        return redirect('painel_usuario')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        logger.debug(f"Tentativa de login recebida - Usuário: {username}")

        if not username or not password:
            logger.warning("Tentativa de login com campos vazios")
            messages.error(request, 'Por favor, preencha todos os campos.')
            return render(request, 'cadastro/login_form.html')

        user = authenticate(request, username=username, password=password)
        
        if user is None:
            logger.warning(f"Falha na autenticação para o usuário: {username}")
            messages.error(request, 'Credenciais inválidas. Por favor, tente novamente.')
            return render(request, 'cadastro/login_form.html')

        auth_login(request, user)
        
        try:
            if not hasattr(user, 'pessoa_juridica'):
                logger.info(f"Usuário {username} sem PessoaJuridica associada")
                messages.warning(request, 'Conta não vinculada a uma empresa. Algumas funcionalidades podem ser limitadas.')
        except Exception as e:
            logger.error(f"Erro ao verificar PessoaJuridica: {str(e)}")
        
        logger.info(f"Login bem-sucedido para o usuário: {username}")
        return redirect('painel_usuario')

    return render(request, 'cadastro/login_form.html')


def custom_logout(request):
    """View personalizada para logout com redirecionamento para login"""
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def cadastrar_pessoa_juridica(request):
    if request.user.is_authenticated:
        return redirect('painel_usuario')

    if request.method == 'POST':
        usuario_form = UsuarioPJForm(request.POST)
        pj_form = PessoaJuridicaForm(request.POST)
        
        if usuario_form.is_valid() and pj_form.is_valid():
            with transaction.atomic():
                try:
                    usuario = usuario_form.save(commit=False)
                    password = usuario_form.cleaned_data.get('password1')
                    usuario.is_active = True
                    usuario.set_password(password)
                    usuario.save()
                    
                    pessoa_juridica = pj_form.save(commit=False)
                    pessoa_juridica.usuario = usuario
                    pessoa_juridica.save()

                    messages.success(request, 'Cadastro realizado com sucesso! Faça login para continuar.')
                    return redirect('login')

                except IntegrityError:
                    messages.error(request, 'Este nome de usuário ou e-mail já está cadastrado.')
                except Exception as e:
                    logger.error(f"Erro no cadastro: {str(e)}", exc_info=True)
                    messages.error(request, 'Erro durante o cadastro. Tente novamente.')
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
    context = {
        'is_staff': request.user.is_staff,
        'has_pj': hasattr(request.user, 'pessoa_juridica')
    }
    return render(request, 'cadastro/painel_usuario.html', context)

# ==============================================
# CRUD CLIENTES
# ==============================================

@login_required
@require_http_methods(["GET"])
def cliente_listar(request):
    """Lista clientes - todos veem, mas staff veem mais"""
    if request.user.is_staff:
        clientes = Cliente.objects.all().order_by('nome')
    elif hasattr(request.user, 'pessoa_juridica'):
        clientes = Cliente.objects.filter(criado_por=request.user.pessoa_juridica).order_by('nome')
    else:
        messages.error(request, 'Acesso não autorizado')
        return redirect('painel_usuario')
    
    return render(request, 'cadastro/cliente/listar.html', {
        'clientes': clientes,
        'is_staff': request.user.is_staff,
        'titulo': 'Clientes',
        'url_cadastro': 'cliente_cadastrar',
        'url_edicao': 'cliente_editar'
    })

@login_required
@require_http_methods(["GET", "POST"])
def cliente_cadastrar(request):
    """Cadastra novo cliente."""
    if not request.user.is_staff and not hasattr(request.user, 'pessoa_juridica'):
        messages.error(request, 'Usuário não autorizado.')
        return redirect('painel_usuario')

    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                cliente = form.save(commit=False)
                if not request.user.is_staff:
                    cliente.criado_por = request.user.pessoa_juridica
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
    cliente = get_object_or_404(Cliente, pk=id)
    
    # Verifica permissão
    if not request.user.is_staff and (not hasattr(request.user, 'pessoa_juridica') or 
                                     cliente.criado_por != request.user.pessoa_juridica):
        messages.error(request, 'Você não tem permissão para editar este cliente.')
        return redirect('cliente_listar')
    
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

@staff_required
@require_http_methods(["POST"])
def cliente_remover(request, id):
    """Remove cliente (apenas POST)."""
    cliente = get_object_or_404(Cliente, pk=id)
    
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
    """Lista motoristas vinculados à PJ do usuário ou todos se staff"""
    if request.user.is_staff:
        motoristas = Motorista.objects.all().order_by('nome')
    elif hasattr(request.user, 'pessoa_juridica'):
        motoristas = Motorista.objects.filter(criado_por=request.user.pessoa_juridica).order_by('nome')
    else:
        messages.error(request, 'Acesso não autorizado')
        return redirect('painel_usuario')
        
    return render(request, 'cadastro/motorista/listar.html', {
        'motoristas': motoristas,
        'is_staff': request.user.is_staff,
        'titulo': 'Motoristas',
        'url_cadastro': 'motorista_cadastrar',
        'url_edicao': 'motorista_editar'
    })

@login_required
@require_http_methods(["GET", "POST"])
def motorista_cadastrar(request):
    """Cadastra novo motorista."""
    if not request.user.is_staff and not hasattr(request.user, 'pessoa_juridica'):
        messages.error(request, 'Usuário não autorizado.')
        return redirect('painel_usuario')

    if request.method == 'POST':
        form = MotoristaForm(request.POST)
        if form.is_valid():
            try:
                motorista = form.save(commit=False)
                if not request.user.is_staff:
                    motorista.criado_por = request.user.pessoa_juridica
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
    motorista = get_object_or_404(Motorista, pk=id)
    
    # Verifica permissão
    if not request.user.is_staff and (not hasattr(request.user, 'pessoa_juridica') or 
                                    motorista.criado_por != request.user.pessoa_juridica):
        messages.error(request, 'Você não tem permissão para editar este motorista.')
        return redirect('motorista_listar')
    
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

@staff_required
@require_http_methods(["POST"])
def motorista_remover(request, id):
    """Remove motorista (apenas POST)."""
    motorista = get_object_or_404(Motorista, pk=id)
    
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
    """Lista transportadoras vinculadas à PJ do usuário ou todas se staff"""
    if request.user.is_staff:
        transportadoras = Transportadora.objects.all().order_by('nome')
    elif hasattr(request.user, 'pessoa_juridica'):
        transportadoras = Transportadora.objects.filter(criado_por=request.user.pessoa_juridica).order_by('nome')
    else:
        messages.error(request, 'Acesso não autorizado')
        return redirect('painel_usuario')
        
    return render(request, 'cadastro/transportadora/listar.html', {
        'transportadoras': transportadoras,
        'is_staff': request.user.is_staff,
        'titulo': 'Transportadoras',
        'url_cadastro': 'transportadora_cadastrar',
        'url_edicao': 'transportadora_editar'
    })

@login_required
@require_http_methods(["GET", "POST"])
def transportadora_cadastrar(request):
    """Cadastra nova transportadora."""
    if not request.user.is_staff and not hasattr(request.user, 'pessoa_juridica'):
        messages.error(request, 'Usuário não autorizado.')
        return redirect('painel_usuario')

    if request.method == 'POST':
        form = TransportadoraForm(request.POST)
        if form.is_valid():
            try:
                transportadora = form.save(commit=False)
                if not request.user.is_staff:
                    transportadora.criado_por = request.user.pessoa_juridica
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
    transportadora = get_object_or_404(Transportadora, pk=id)
    
    # Verifica permissão
    if not request.user.is_staff and (not hasattr(request.user, 'pessoa_juridica') or 
                                     transportadora.criado_por != request.user.pessoa_juridica):
        messages.error(request, 'Você não tem permissão para editar esta transportadora.')
        return redirect('transportadora_listar')
    
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

@staff_required
@require_http_methods(["POST"])
def transportadora_remover(request, id):
    """Remove transportadora (apenas POST)."""
    transportadora = get_object_or_404(Transportadora, pk=id)
    
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
    """Lista vales - todos veem, mas staff veem mais"""
    if request.user.is_staff:
        vales = ValePallet.objects.all().select_related(
            'cliente', 'motorista', 'transportadora', 'criado_por'
        )
    elif hasattr(request.user, 'pessoa_juridica'):
        vales = ValePallet.objects.filter(
            criado_por=request.user.pessoa_juridica
        ).select_related('cliente', 'motorista', 'transportadora')
    else:
        messages.error(request, 'Acesso não autorizado')
        return redirect('painel_usuario')
    
    return render(request, 'cadastro/valepallet/listar.html', {
        'vales': vales,
        'is_staff': request.user.is_staff,
        'titulo': 'Vales Pallets',
        'url_cadastro': 'valepallet_cadastrar',
        'url_edicao': 'valepallet_editar'
    })

@transaction.atomic
@login_required
@require_http_methods(["GET", "POST"])
def valepallet_cadastrar(request):
    """Cadastra novo vale pallet com tratamento robusto de erros."""
    if not request.user.is_staff and not hasattr(request.user, 'pessoa_juridica'):
        messages.error(request, 'Usuário não autorizado.')
        return redirect('painel_usuario')

    if request.method == 'POST':
        form = ValePalletForm(request.POST, user=request.user)
        
        # Configura os querysets para o staff
        if request.user.is_staff:
            form.fields['cliente'].queryset = Cliente.objects.all().order_by('nome')
            form.fields['motorista'].queryset = Motorista.objects.all().order_by('nome')
            form.fields['transportadora'].queryset = Transportadora.objects.all().order_by('nome')
            form.fields['criado_por'].queryset = PessoaJuridica.objects.all().order_by('razao_social')
            form.fields['criado_por'].required = False

        if not form.is_valid():
            messages.error(request, 'Por favor, corrija os erros no formulário.')
            return render(request, 'cadastro/valepallet/form.html', {
                'form': form,
                'titulo': 'Novo Vale Pallet',
                'url_retorno': 'valepallet_listar'
            })

        try:
            with transaction.atomic():
                vale = form.save(commit=False)
                
                # Gera um hash único
                hash_gerado = get_random_string(32)
                while ValePallet.objects.filter(hash_seguranca=hash_gerado).exists():
                    hash_gerado = get_random_string(32)
                
                vale.hash_seguranca = hash_gerado
                
                if not request.user.is_staff:
                    vale.criado_por = request.user.pessoa_juridica
                    vale.estado = 'EMITIDO'
                else:
                    # Para staff, criado_por pode ser None ou o valor selecionado
                    if not form.cleaned_data.get('criado_por'):
                        vale.criado_por = request.user.pessoa_juridica
                
                vale.save()

                Movimentacao.objects.create(
                    vale=vale,
                    tipo='EMITIDO',
                    qtd_pbr=vale.qtd_pbr,
                    qtd_chepp=vale.qtd_chepp,
                    responsavel=request.user,
                    observacao=f'Vale {vale.numero_vale} criado'
                )

                # Gerar QR Code
                try:
                    scan_url = request.build_absolute_uri(
                        reverse('valepallet_processar', args=[vale.id, vale.hash_seguranca])
                    )
                    qr_data = {
                        "id": vale.id,
                        "hash": vale.hash_seguranca,
                        "numero_vale": vale.numero_vale,
                        "url": scan_url
                    }
                    qr_code = generate_qr_code(qr_data)
                    
                    if qr_code:
                        from django.core.files.base import ContentFile
                        from io import BytesIO
                        
                        filename = f'vale_{vale.id}_{vale.numero_vale}.png'
                        file_content = ContentFile(qr_code.getvalue())
                        vale.qr_code.save(filename, file_content, save=True)
                except Exception as e:
                    logger.error(f"Erro ao gerar QR code: {str(e)}")
                    messages.warning(request, 'Erro ao gerar QR code. O vale foi criado, mas sem QR code.')

                messages.success(request, 'Vale pallet criado com sucesso!')
                return redirect('valepallet_detalhes', id=vale.id)

        except IntegrityError as e:
            logger.error(f"Erro de integridade: {str(e)}")
            messages.error(request, 'Erro ao criar o vale. Por favor, tente novamente.')
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            messages.error(request, 'Erro ao criar o vale pallet.')
    else:
        form = ValePalletForm(user=request.user)
        
        # Configura os querysets baseado no tipo de usuário
        if request.user.is_staff:
            form.fields['cliente'].queryset = Cliente.objects.all().order_by('nome')
            form.fields['motorista'].queryset = Motorista.objects.all().order_by('nome')
            form.fields['transportadora'].queryset = Transportadora.objects.all().order_by('nome')
            form.fields['criado_por'].queryset = PessoaJuridica.objects.all().order_by('razao_social')
            form.fields['criado_por'].required = False
        elif hasattr(request.user, 'pessoa_juridica'):
            pj = request.user.pessoa_juridica
            form.fields['cliente'].queryset = Cliente.objects.filter(criado_por=pj).order_by('nome')
            form.fields['motorista'].queryset = Motorista.objects.filter(criado_por=pj).order_by('nome')
            form.fields['transportadora'].queryset = Transportadora.objects.filter(criado_por=pj).order_by('nome')

    return render(request, 'cadastro/valepallet/form.html', {
        'form': form,
        'titulo': 'Novo Vale Pallet',
        'url_retorno': 'valepallet_listar'
    })


@login_required
@require_http_methods(["GET"])
def valepallet_detalhes(request, id):
    """Exibe detalhes de um vale pallet específico."""
    try:
        vale = get_object_or_404(
            ValePallet.objects.select_related(
                'cliente', 
                'motorista', 
                'transportadora',
                'criado_por'
            ),
            pk=id
        )

        # Verificação de permissão
        if not request.user.is_staff and (not hasattr(request.user, 'pessoa_juridica') or 
                                        vale.criado_por != request.user.pessoa_juridica):
            messages.error(request, 'Você não tem permissão para acessar este vale.')
            return redirect('valepallet_listar')

        movimentacoes = Movimentacao.objects.filter(vale=vale).order_by('-data_hora')

        # Tratamento simplificado do QR Code
        qr_code_url = vale.qr_code.url if vale.qr_code else None

        context = {
            'vale': vale,
            'movimentacoes': movimentacoes,
            'qr_code_url': qr_code_url,
            'titulo': f'Detalhes do Vale {vale.numero_vale}',
            'pode_editar': request.user.is_staff or (hasattr(request.user, 'pessoa_juridica') and 
                                                    vale.criado_por == request.user.pessoa_juridica)
        }

        return render(request, 'cadastro/valepallet/detalhes.html', context)

    except Exception as e:
        logger.error(f"Erro ao acessar detalhes do vale {id}: {str(e)}", exc_info=True)
        messages.error(request, 'Erro ao carregar detalhes do vale')
        return redirect('valepallet_listar')


@transaction.atomic
@login_required
@require_http_methods(["GET", "POST"])
def valepallet_editar(request, id):
    """Edita vale pallet existente."""
    vale = get_object_or_404(ValePallet, pk=id)
    
    # Verifica permissão
    if not request.user.is_staff and (not hasattr(request.user, 'pessoa_juridica') or 
                                     vale.criado_por != request.user.pessoa_juridica):
        messages.error(request, 'Você não tem permissão para editar este vale.')
        return redirect('valepallet_listar')
    
    if request.method == 'POST':
        form = ValePalletForm(request.POST, instance=vale, user=request.user)
        
        # Configura os querysets para o staff
        if request.user.is_staff:
            form.fields['cliente'].queryset = Cliente.objects.all().order_by('nome')
            form.fields['motorista'].queryset = Motorista.objects.all().order_by('nome')
            form.fields['transportadora'].queryset = Transportadora.objects.all().order_by('nome')
            form.fields['criado_por'].queryset = PessoaJuridica.objects.all().order_by('razao_social')
            form.fields['criado_por'].required = False

        if form.is_valid():
            try:
                with transaction.atomic():
                    if request.user.is_staff:
                        # Para staff, criado_por pode ser None ou o valor selecionado
                        if not form.cleaned_data.get('criado_por'):
                            vale.criado_por = None
                    
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
        
        # Configura os querysets baseado no tipo de usuário
        if request.user.is_staff:
            form.fields['cliente'].queryset = Cliente.objects.all().order_by('nome')
            form.fields['motorista'].queryset = Motorista.objects.all().order_by('nome')
            form.fields['transportadora'].queryset = Transportadora.objects.all().order_by('nome')
            form.fields['criado_por'].queryset = PessoaJuridica.objects.all().order_by('razao_social')
            form.fields['criado_por'].required = False
        elif hasattr(request.user, 'pessoa_juridica'):
            pj = request.user.pessoa_juridica
            form.fields['cliente'].queryset = Cliente.objects.filter(criado_por=pj).order_by('nome')
            form.fields['motorista'].queryset = Motorista.objects.filter(criado_por=pj).order_by('nome')
            form.fields['transportadora'].queryset = Transportadora.objects.filter(criado_por=pj).order_by('nome')
    
    return render(request, 'cadastro/valepallet/form.html', {
        'form': form,
        'titulo': f'Editar Vale {vale.numero_vale}',
        'url_retorno': 'valepallet_listar'
    })


@transaction.atomic
@staff_required
@require_http_methods(["POST"])
def valepallet_remover(request, id):
    """Remove vale pallet (apenas POST)."""
    vale = get_object_or_404(ValePallet, pk=id)
    
    try:
        vale.delete()
        messages.success(request, f'Vale {vale.numero_vale} removido com sucesso!')
    except Exception as e:
        logger.error(f"Erro ao remover vale pallet: {str(e)}")
        messages.error(request, 'Erro ao remover vale pallet')
    return redirect('valepallet_listar')

@transaction.atomic
@login_required
@require_http_methods(["GET"])
def processar_scan(request, id, hash_seguranca):
    """Processa o scan do QR Code (muda estado do vale)."""
    if not hasattr(request.user, 'pessoa_juridica'):
        messages.error(request, 'Usuário não vinculado a uma empresa.')
        return redirect('painel_usuario')

    try:
        with transaction.atomic():
            vale = get_object_or_404(
                ValePallet, 
                pk=id, 
                hash_seguranca=hash_seguranca
            )
            
            # Verifica se o usuário tem permissão
            if not request.user.is_staff and vale.criado_por != request.user.pessoa_juridica:
                messages.error(request, 'Você não tem permissão para processar este vale.')
                return redirect('valepallet_listar')
            
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
        logger.error(f"Erro ao processar QR Code: {str(e)}", exc_info=True)
        messages.error(request, 'Erro no processamento do QR Code')
        return redirect('valepallet_listar')
    
# ==============================================
# GESTÃO DE MOVIMENTAÇÕES
# ==============================================
@login_required
@require_http_methods(["GET"])
def movimentacao_listar(request):
    """Lista todas as movimentações e exibe o dashboard de pallets."""
    # Consulta básica de movimentações
    if request.user.is_staff:
        movimentacoes = Movimentacao.objects.all().select_related('vale', 'responsavel').order_by('-data_hora')
        vales = ValePallet.objects.all()
    elif hasattr(request.user, 'pessoa_juridica'):
        movimentacoes = Movimentacao.objects.filter(
            vale__criado_por=request.user.pessoa_juridica
        ).select_related('vale', 'responsavel').order_by('-data_hora')
        vales = ValePallet.objects.filter(criado_por=request.user.pessoa_juridica)
    else:
        messages.error(request, 'Acesso não autorizado')
        return redirect('painel_usuario')

    # Data atual para cálculos
    hoje = timezone.now().date()
    data_limite_vencer = hoje + timedelta(days=30)

    # Métricas de status
    # A vencer: vales com saída e que vencem em até 30 dias
    a_vencer = vales.filter(
        data_saida__isnull=False,
        data_retorno__isnull=True,
        data_validade__range=[hoje, data_limite_vencer]
    ).count()
    
    # Coletado: vales com saída e retorno registrados
    coletado = vales.filter(
        data_saida__isnull=False,
        data_retorno__isnull=False
    ).count()
    
    # Pendente: vales emitidos mas sem saída
    pendente = vales.filter(
        data_saida__isnull=True
    ).count()
    
    # Vencido: vales com saída mas sem retorno e data de validade passada
    vencido = vales.filter(
        data_saida__isnull=False,
        data_retorno__isnull=True,
        data_validade__lt=hoje
    ).count()

    # Métricas de pallets
    # Pallets em movimentação (com saída mas sem retorno)
    pallets_movimentacao = vales.filter(
        data_saida__isnull=False,
        data_retorno__isnull=True
    ).aggregate(
        total=Sum('qtd_pbr')
    )['total'] or 0
    
    # Pallets no prazo (pendentes ou dentro da validade)
    pallets_prazo = vales.filter(
        Q(data_saida__isnull=True) |  # Pendentes
        (Q(data_saida__isnull=False) & Q(data_retorno__isnull=True) & Q(data_validade__gte=hoje))  # Em movimento mas dentro do prazo
    ).aggregate(
        total=Sum('qtd_pbr')
    )['total'] or 0
    
    # Pallets vencidos (com saída, sem retorno e data vencida)
    pallets_vencidos = vales.filter(
        data_saida__isnull=False,
        data_retorno__isnull=True,
        data_validade__lt=hoje
    ).aggregate(
        total=Sum('qtd_pbr')
    )['total'] or 0
    
    # Total de pallets
    total_pallets = vales.aggregate(
        total=Sum('qtd_pbr')
    )['total'] or 0

    # Dias em aberto
    menos_30_dias = vales.filter(
        data_emissao__gte=hoje - timedelta(days=30)
    ).count()
    
    mais_30_dias = vales.filter(
        data_emissao__lt=hoje - timedelta(days=30),
        data_emissao__gte=hoje - timedelta(days=90)
    ).count()
    
    mais_90_dias = vales.filter(
        data_emissao__lt=hoje - timedelta(days=90),
        data_emissao__gte=hoje - timedelta(days=180)
    ).count()
    
    mais_180_dias = vales.filter(
        data_emissao__lt=hoje - timedelta(days=180)
    ).count()

    # Agregação por fornecedor (usuário responsável)
    fornecedores_data = movimentacoes.values(
        'responsavel__username'
    ).annotate(
        total_vales=Count('vale', distinct=True),
        total_pallets=Sum('vale__qtd_pbr')
    ).order_by('responsavel__username')

    total_fornecedores = {
        'vales': sum(item['total_vales'] for item in fornecedores_data),
        'pallets': sum(item['total_pallets'] for item in fornecedores_data)
    }

    return render(request, 'cadastro/movimentacao/listar.html', {
        'movimentacoes': movimentacoes,
        'titulo': 'Movimentações',
        'is_staff': request.user.is_staff,
        
        # Métricas para o dashboard
        'a_vencer': a_vencer,
        'coletado': coletado,
        'pendente': pendente,
        'vencido': vencido,
        
        'pallets_movimentacao': pallets_movimentacao,
        'pallets_prazo': pallets_prazo,
        'pallets_vencidos': pallets_vencidos,
        'total_pallets': total_pallets,
        
        'menos_30_dias': menos_30_dias,
        'mais_30_dias': mais_30_dias,
        'mais_90_dias': mais_90_dias,
        'mais_180_dias': mais_180_dias,
        
        'fornecedores_data': fornecedores_data,
        'total_fornecedores': total_fornecedores
    })

@transaction.atomic
@login_required
@require_http_methods(["GET", "POST"])
def movimentacao_registrar(request):
    """Registra nova movimentação manualmente."""
    if not request.user.is_staff and not hasattr(request.user, 'pessoa_juridica'):
        messages.error(request, 'Usuário não autorizado.')
        return redirect('painel_usuario')

    vale_id = request.GET.get('vale_id')
    
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                movimentacao = form.save(commit=False)
                movimentacao.responsavel = request.user
                
                # Verifica permissão para o vale associado
                if not request.user.is_staff and (not hasattr(request.user, 'pessoa_juridica') or 
                                               movimentacao.vale.criado_por != request.user.pessoa_juridica):
                    messages.error(request, 'Você não tem permissão para registrar movimentação neste vale.')
                    return redirect('movimentacao_listar')
                
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


# ===== APIs EXTERNAS =====
@require_GET
def validar_cnpj_api(request):
    cnpj = request.GET.get('cnpj', '').replace('.', '').replace('/', '').replace('-', '')
    if not cnpj.isdigit() or len(cnpj) != 14:
        return JsonResponse({'valido': False, 'erro': 'CNPJ deve ter 14 dígitos numéricos.'}, status=400)
    
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
            'DsSituacaoCadastral': data.get('situacao', 'ATIVO'),
            'DsEnderecoLogradouro': data.get('logradouro', ''),
            'NrEnderecoNumero': data.get('numero', ''),
            'DsEnderecoBairro': data.get('bairro', ''),
            'NrEnderecoCep': data.get('cep', '').replace('.', '').replace('-', ''),
            'DsEnderecoCidade': data.get('municipio', ''),
            'DsEnderecoEstado': data.get('uf', ''),
            'DsEmail': data.get('email', ''),
            'DsInscricaoEstadual': data.get('inscricao_estadual', ''),
            'DsTelefone': data.get('telefone', ''),
            'DsSite': data.get('site', '')
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar CNPJ: {str(e)}")
        return JsonResponse({'valido': False, 'erro': 'Serviço de consulta indisponível'}, status=503)
    except Exception as e:
        logger.error(f"Erro inesperado ao validar CNPJ: {str(e)}")
        return JsonResponse({'valido': False, 'erro': 'Erro interno ao processar CNPJ'}, status=500)

@require_GET
def consultar_cep_api(request):
    cep = request.GET.get('cep', '').replace('-', '')
    if not cep.isdigit() or len(cep) != 8:
        return JsonResponse({'erro': 'CEP deve conter 8 dígitos numéricos.'}, status=400)
    
    try:
        response = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'erro' in data:
            return JsonResponse({'erro': 'CEP não encontrado'}, status=404)
            
        return JsonResponse({
            'DsEnderecoLogradouro': data.get('logradouro', ''),
            'DsEnderecoBairro': data.get('bairro', ''),
            'DsEnderecoCidade': data.get('localidade', ''),
            'DsEnderecoEstado': data.get('uf', ''),
            'DsEnderecoComplemento': data.get('complemento', '')
        })
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar CEP: {str(e)}")
        return JsonResponse({'erro': 'Serviço de consulta indisponível'}, status=503)
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar CEP: {str(e)}")
        return JsonResponse({'erro': 'Erro interno ao processar CEP'}, status=500)

@require_GET
def listar_estados_api(request):
    try:
        response = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome', timeout=10)
        response.raise_for_status()
        estados = [{'sigla': est['sigla'], 'nome': est['nome']} for est in response.json()]
        return JsonResponse({'estados': estados})
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao listar estados: {str(e)}")
        return JsonResponse({'erro': 'Serviço indisponível'}, status=503)
    except Exception as e:
        logger.error(f"Erro inesperado ao listar estados: {str(e)}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)

@require_GET
def listar_municipios_api(request, uf):
    if not uf or len(uf) != 2:
        return JsonResponse({'erro': 'UF inválida'}, status=400)
    
    try:
        response = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios', timeout=10)
        response.raise_for_status()
        municipios = [{'id': mun['id'], 'nome': mun['nome']} for mun in response.json()]
        return JsonResponse({'municipios': municipios})
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao listar municípios: {str(e)}")
        return JsonResponse({'erro': 'Serviço indisponível'}, status=503)
    except Exception as e:
        logger.error(f"Erro inesperado ao listar municípios: {str(e)}")
        return JsonResponse({'erro': 'Erro interno'}, status=500)