from django.urls import path
from app_controller import views
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required


urlpatterns = [
    # AUTENTICAÇÃO (públicas)
    path('', views.cadastrar_pessoa_juridica, name='cadastrar_pessoa_juridica'),
    path('login/', LoginView.as_view(template_name='cadastro/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # PÁGINAS PRIVADAS (protegidas por login_required)
    path('painel/', views.painel_usuario, name='painel_usuario'),

    # CLIENTES
    path('clientes/', views.cliente_listar, name='cliente_listar'),
    path('clientes/cadastrar/', views.cliente_cadastrar, name='cliente_cadastrar'),
    path('clientes/editar/<int:id>/', views.cliente_editar, name='cliente_editar'),
    path('clientes/remover/<int:id>/', views.cliente_remover, name='cliente_remover'),
    
    # MOTORISTAS
    path('motoristas/', views.motorista_listar, name='motorista_listar'),
    path('motoristas/cadastrar/', views.motorista_cadastrar, name='motorista_cadastrar'),
    path('motoristas/editar/<int:id>/', views.motorista_editar, name='motorista_editar'),
    path('motoristas/remover/<int:id>/', views.motorista_remover, name='motorista_remover'),
    
    # TRANSPORTADORAS
    path('transportadoras/', views.transportadora_listar, name='transportadora_listar'),
    path('transportadoras/cadastrar/', views.transportadora_cadastrar, name='transportadora_cadastrar'),
    path('transportadoras/editar/<int:id>/', views.transportadora_editar, name='transportadora_editar'),
    path('transportadoras/remover/<int:id>/', views.transportadora_remover, name='transportadora_remover'),
    
    # VALE PALLET
    path('vales/', views.valepallet_listar, name='valepallet_listar'),
    path('vales/cadastrar/', views.valepallet_cadastrar, name='valepallet_cadastrar'),
    path('vales/detalhes/<int:id>/', views.valepallet_detalhes, name='valepallet_detalhes'),
    path('vales/editar/<int:id>/', views.valepallet_editar, name='valepallet_editar'),
    path('vales/remover/<int:id>/', views.valepallet_remover, name='valepallet_remover'),

    # QR CODE (NOVA ROTA UNIFICADA)
    path('valepallet/processar/<int:id>/<str:hash_seguranca>/', views.processar_scan, name='valepallet_processar'),

    # MOVIMENTAÇÕES
    path('movimentacoes/', views.movimentacao_listar, name='movimentacao_listar'),
    path('movimentacoes/registrar/', views.movimentacao_registrar, name='movimentacao_registrar'),

    # APIs
    path('api/validarCNPJ/', views.validar_cnpj_api, name='validar_cnpj_api'),
    path('api/consultarCEP/', views.consultar_cep_api, name='consultar_cep_api'),
    path('api/estados/', views.listar_estados_api, name='listar_estados_api'),
    path('api/municipios/<str:uf>/', views.listar_municipios_api, name='listar_municipios_api'),
]
