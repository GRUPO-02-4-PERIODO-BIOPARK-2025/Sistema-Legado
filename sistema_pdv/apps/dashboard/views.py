from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
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
    
    context = {
        'total_vendas_hoje': total_vendas_hoje,
        'total_vendas_mes': total_vendas_mes,
        'produtos_em_estoque': produtos_em_estoque,
        'clientes_ativos': total_clientes,
    }
    
    return render(request, 'dashboard/index.html', context)
