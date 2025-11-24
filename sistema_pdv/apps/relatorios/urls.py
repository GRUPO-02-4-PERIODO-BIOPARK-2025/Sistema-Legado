from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    path('', views.RelatoriosView.as_view(), name='index'),
    path('gerar/', views.GerarRelatorioView.as_view(), name='gerar_relatorio'),
    path('grafico/', views.GerarGraficoView.as_view(), name='gerar_grafico'), # ← NOVA LINHA ADICIONADA
]
