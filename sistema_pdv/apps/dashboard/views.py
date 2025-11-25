from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
import json
from apps.vendas.models import Venda
from apps.produtos.models import Produto
from apps.clientes.models import Cliente

@login_required(login_url='usuarios:login')
def index(request):
    hoje = timezone.now().date()
    inicio_mes = hoje.replace(day=1)
    
    # Vendas de hoje
    vendas_hoje = Venda.objects.filter(finalizada=True, data__date=hoje)
    total_vendas_hoje = vendas_hoje.aggregate(total=Sum('total'))['total'] or 0
    
    # Vendas do mês
    vendas_mes = Venda.objects.filter(finalizada=True, data__date__gte=inicio_mes)
    total_vendas_mes = vendas_mes.aggregate(total=Sum('total'))['total'] or 0
    
    # Produtos em estoque
    produtos_em_estoque = Produto.objects.filter(estoque__gt=0).count()
    
    # Total de clientes cadastrados
    total_clientes = Cliente.objects.count()
    
    # Dados para o gráfico de vendas mensais (últimos 12 meses)
    meses_labels = []
    vendas_mensais_data = []
    
    for i in range(11, -1, -1):
        # Calcular o primeiro dia do mês
        mes_ref = hoje.replace(day=1) - timedelta(days=i*30)
        mes_ref = mes_ref.replace(day=1)
        
        # Calcular o último dia do mês
        if mes_ref.month == 12:
            proximo_mes = mes_ref.replace(year=mes_ref.year + 1, month=1)
        else:
            proximo_mes = mes_ref.replace(month=mes_ref.month + 1)
        
        fim_mes = proximo_mes - timedelta(days=1)
        
        # Buscar vendas do mês
        vendas_do_mes = Venda.objects.filter(
            finalizada=True,
            data__date__gte=mes_ref,
            data__date__lte=fim_mes
        )
        total_mes = vendas_do_mes.aggregate(total=Sum('total'))['total'] or 0
        
        # Nomes dos meses em português
        meses_nomes = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                       'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        
        meses_labels.append(meses_nomes[mes_ref.month - 1])
        vendas_mensais_data.append(float(total_mes))
    
    context = {
        'total_vendas_hoje': total_vendas_hoje,
        'total_vendas_mes': total_vendas_mes,
        'produtos_em_estoque': produtos_em_estoque,
        'clientes_ativos': total_clientes,
        'meses_labels': json.dumps(meses_labels),
        'vendas_mensais_data': json.dumps(vendas_mensais_data),
    }
    
    return render(request, 'dashboard/index.html', context)
