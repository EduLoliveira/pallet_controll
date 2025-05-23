
from app_controller import views
from django.urls import path

urlpatterns = [
    # PÁGINA INICIAL
    path('', views.home, name='home'),

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
    path('vales/editar/<int:id>/', views.valepallet_editar, name='valepallet_editar'),
    path('vales/remover/<int:id>/', views.valepallet_remover, name='valepallet_remover'),

    # MOVIMENTAÇÕES
    path('movimentacoes/', views.movimentacao_listar, name='movimentacao_listar'),
]