from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.db.models import Sum, Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from datetime import datetime

from apps.vendas.models import Venda, Pagamento
from apps.clientes.models import Cliente
from django.contrib.auth.models import User # Para funcionários/usuários

class RelatoriosView(LoginRequiredMixin, TemplateView ):
    template_name = 'relatorios/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passar dados para os filtros
        context['clientes'] = Cliente.objects.all()
        context['funcionarios'] = User.objects.all()
        context['formas_pagamento'] = Pagamento.TIPO_CHOICES
        context['filtros'] = {}
        return context

class GerarRelatorioView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # 1. Coletar e validar filtros
        data_inicio_str = request.GET.get('data_inicio')
        data_fim_str = request.GET.get('data_fim')
        cliente_id = request.GET.get('cliente')
        funcionario_id = request.GET.get('funcionario')
        forma_pagamento = request.GET.get('forma_pagamento')

        vendas = Venda.objects.filter(finalizada=True)

        # 2. Aplicar filtros
        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
                vendas = vendas.filter(data__gte=data_inicio)
            except ValueError:
                pass # Ignorar filtro inválido

        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
                # Adicionar 1 dia para incluir o dia final inteiro
                data_fim = data_fim.replace(hour=23, minute=59, second=59)
                vendas = vendas.filter(data__lte=data_fim)
            except ValueError:
                pass # Ignorar filtro inválido

        if cliente_id:
            vendas = vendas.filter(cliente_id=cliente_id)

        if funcionario_id:
            vendas = vendas.filter(usuario_id=funcionario_id)

        if forma_pagamento:
            # Filtrar vendas que possuem pelo menos um pagamento com a forma selecionada
            vendas = vendas.filter(pagamentos__tipo=forma_pagamento).distinct()

        # 3. Coletar dados para o relatório
        total_vendas = vendas.count()
        total_faturamento = vendas.aggregate(Sum('total'))['total__sum'] or 0
        
        # Detalhes das vendas
        vendas_detalhes = vendas.order_by('-data').select_related('usuario', 'cliente').prefetch_related('pagamentos')

        # 4. Preparar o contexto
        context = {
            'total_vendas': total_vendas,
            'total_faturamento': total_faturamento,
            'vendas_detalhes': vendas_detalhes,
            'filtros': request.GET,
        }

        # 5. Renderizar o relatório (usaremos um template HTML simples por enquanto)
        return render(request, 'relatorios/index.html', context)
