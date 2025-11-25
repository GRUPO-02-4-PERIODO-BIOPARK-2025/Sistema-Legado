from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    path('', views.index, name='index'),
    path('adicionar-item/', views.adicionar_item, name='adicionar_item'),
    path('remover-item/<int:item_id>/', views.remover_item, name='remover_item'),
    path('atualizar-quantidade/<int:item_id>/', views.atualizar_quantidade, name='atualizar_quantidade'),
    path('aplicar-desconto/', views.aplicar_desconto, name='aplicar_desconto'),
    path('aplicar-frete/', views.aplicar_frete, name='aplicar_frete'),
    path('associar-cliente/', views.associar_cliente, name='associar_cliente'),
    path('finalizar/', views.finalizar_venda, name='finalizar'),
    path('cancelar/', views.cancelar, name='cancelar'),
    path('atualizar-cliente/', views.atualizar_cliente, name='atualizar_cliente'),
    path('gerenciar/', views.gerenciar_vendas, name='gerenciar'),
    path('detalhes/<int:venda_id>/', views.detalhes_venda, name='detalhes'),
    path('cancelar-venda/<int:venda_id>/', views.cancelar_venda_finalizada, name='cancelar_venda'),
    path('baixar-parcela/<int:parcela_id>/', views.baixar_parcela, name='baixar_parcela'),
]
