"""Notificações URL Configuration"""
from django.urls import path
from . import views

app_name = 'notificacoes'

urlpatterns = [
    # API endpoints
    path('api/notificacoes/', views.listar_notificacoes, name='api_listar'),
    path('api/notificacoes/estatisticas/', views.obter_estatisticas, name='api_estatisticas'),
    path('api/notificacoes/marcar-todas-lidas/', views.marcar_todas_lidas, name='api_marcar_todas_lidas'),
    path('api/notificacoes/<int:notification_id>/marcar-lida/', views.marcar_lida, name='api_marcar_lida'),
    path('api/notificacoes/verificar-produto/<int:produto_id>/', views.verificar_produto, name='api_verificar_produto'),
    path('api/notificacoes/verificar-todos/', views.verificar_todos, name='api_verificar_todos'),
    path('api/notificacoes/thresholds/', views.gerenciar_threshold, name='api_thresholds_list'),
    path('api/notificacoes/thresholds/<int:produto_id>/', views.gerenciar_threshold, name='api_thresholds_detail'),
    path('api/notificacoes/health/', views.health_check, name='api_health'),
]
