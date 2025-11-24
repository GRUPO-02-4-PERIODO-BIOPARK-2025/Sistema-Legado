from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from datetime import datetime
import matplotlib.pyplot as plt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from django.db.models.functions import TruncDay
from apps.vendas.models import Venda, Pagamento
from apps.clientes.models import Cliente
from django.contrib.auth.models import User

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
        total_faturamento = vendas.aggregate(Sum('total'))['total__sum'] or 0
        
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

        vendas_por_dia = vendas.annotate(dia=TruncDay('data')).values('dia').annotate(
            total_vendas=Count('id'),
            faturamento=Sum('total')
        ).order_by('dia')

        dias = [v['dia'].strftime('%d/%m') for v in vendas_por_dia]
        faturamento = [float(v['faturamento']) for v in vendas_por_dia]

        plt.switch_backend('Agg')
        fig, ax = plt.subplots(figsize=(10, 5))

        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

        ax.bar(dias, faturamento, color='#6f2bd6')
        ax.set_title('Faturamento Diário', fontsize=14, fontweight='bold')
        ax.set_xlabel('Dia', fontsize=12)
        ax.set_ylabel('Faturamento (R$)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        FigureCanvas(fig).print_png(buffer)
        plt.close(fig)

        response = HttpResponse(buffer.getvalue(), content_type='image/png')
        return response
