from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    path('', views.index, name='index'),
    path('adicionar-item/', views.adicionar_item, name='adicionar_item'),
    path('remover-item/<int:item_id>/', views.remover_item, name='remover_item'),
    path('atualizar-quantidade/<int:item_id>/', views.atualizar_quantidade, name='atualizar_quantidade'),
    path('aplicar-desconto/', views.aplicar_desconto, name='aplicar_desconto'),
    path('finalizar/', views.finalizar_venda, name='finalizar'),
    path('cancelar/', views.cancelar, name='cancelar'),
]
