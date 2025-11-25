from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.db.models.functions import TruncDay
from apps.vendas.models import Venda, Pagamento
from apps.clientes.models import Cliente
from django.contrib.auth.models import User
from collections import defaultdict

class RelatoriosView(LoginRequiredMixin, TemplateView ):
    template_name = 'relatorios/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clientes'] = Cliente.objects.all()
        context['funcionarios'] = User.objects.all()
        context['formas_pagamento'] = Pagamento.TIPO_CHOICES
        context['filtros'] = {}
        return context

class GerarRelatorioView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data_inicio_str = request.GET.get('data_inicio')
        data_fim_str = request.GET.get('data_fim')
        cliente_id = request.GET.get('cliente')
        funcionario_id = request.GET.get('funcionario')
        forma_pagamento = request.GET.get('forma_pagamento')

        vendas = Venda.objects.filter(finalizada=True)

        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
                vendas = vendas.filter(data__gte=data_inicio)
            except ValueError:
                pass 

        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
                data_fim = data_fim.replace(hour=23, minute=59, second=59)
                vendas = vendas.filter(data__lte=data_fim)
            except ValueError:
                pass 

        if cliente_id:
            vendas = vendas.filter(cliente_id=cliente_id)

        if funcionario_id:
            vendas = vendas.filter(usuario_id=funcionario_id)

        if forma_pagamento:
            vendas = vendas.filter(pagamentos__tipo=forma_pagamento).distinct()

        total_vendas = vendas.count()
        
        # Calcular faturamento baseado no valor efetivamente recebido
        total_faturamento = 0
        for venda in vendas:
            total_faturamento += float(venda.get_valor_recebido())
        
        vendas_detalhes = vendas.order_by('-data').select_related('usuario', 'cliente').prefetch_related('pagamentos')

        context = {
            'total_vendas': total_vendas,
            'total_faturamento': total_faturamento,
            'vendas_detalhes': vendas_detalhes,
            'filtros': request.GET,
        }

        return render(request, 'relatorios/index.html', context)

class GerarGraficoView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        data_inicio_str = request.GET.get('data_inicio')
        data_fim_str = request.GET.get('data_fim')
        cliente_id = request.GET.get('cliente')
        funcionario_id = request.GET.get('funcionario')
        forma_pagamento = request.GET.get('forma_pagamento')

        vendas = Venda.objects.filter(finalizada=True)

        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
                vendas = vendas.filter(data__gte=data_inicio)
            except ValueError:
                pass

        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
                data_fim = data_fim.replace(hour=23, minute=59, second=59)
                vendas = vendas.filter(data__lte=data_fim)
            except ValueError:
                pass

        if cliente_id:
            vendas = vendas.filter(cliente_id=cliente_id)

        if funcionario_id:
            vendas = vendas.filter(usuario_id=funcionario_id)

        if forma_pagamento:
            vendas = vendas.filter(pagamentos__tipo=forma_pagamento).distinct()

        # Agrupar vendas por dia da semana - SEMPRE mostrar todos os 7 dias
        dias_semana_labels = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        vendas_por_dia_semana = [0, 0, 0, 0, 0, 0, 0]  # Inicializar com zeros
        
        for venda in vendas:
            # Obter o dia da semana (0 = segunda, 6 = domingo)
            dia_semana = venda.data.weekday()
            # Usar valor recebido ao invés do total
            vendas_por_dia_semana[dia_semana] += float(venda.get_valor_recebido())
        
        # SEMPRE usar todos os dias da semana
        dias = dias_semana_labels
        faturamento = vendas_por_dia_semana

        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=(12, 6))

        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

        # Criar as barras com cor roxa e largura de 0.7 para ficarem próximas
        bars = ax.bar(range(len(dias)), faturamento, color='#6f2bd6', width=0.7, edgecolor='none')
        
        ax.set_title('Faturamento por Dia da Semana', fontsize=16, fontweight='bold', pad=20, color='#1d1d1f')
        ax.set_xlabel('Dia da Semana', fontsize=13, fontweight='600', color='#333')
        ax.set_ylabel('Faturamento (R$)', fontsize=13, fontweight='600', color='#333')
        ax.set_xticks(range(len(dias)))
        ax.set_xticklabels(dias, rotation=0, ha='center', fontsize=12, color='#333')
        
        # Adicionar grade horizontal leve
        ax.grid(axis='y', alpha=0.2, linestyle='-', linewidth=0.5, color='#e0e0e0')
        ax.set_axisbelow(True)
        
        # Estilizar o gráfico - estilo minimalista
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['bottom'].set_color('#cccccc')
        
        # Configurar ticks do eixo Y
        ax.tick_params(axis='y', colors='#666', labelsize=11)
        ax.tick_params(axis='x', colors='#333', labelsize=12)
        
        # Adicionar valores no topo das barras
        for i, (bar, valor) in enumerate(zip(bars, faturamento)):
            height = bar.get_height()
            if valor > 0:  # Só mostrar valor se for maior que zero
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'R$ {valor:.2f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold', color='#1d1d1f')
        
        plt.tight_layout()

        buffer = io.BytesIO()
        FigureCanvas(fig).print_png(buffer)
        plt.close(fig)

        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        return response
