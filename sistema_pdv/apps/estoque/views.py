from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Max

from apps.produtos.models import Produto
from .models import MovimentoEstoque
from .services import ajustar_estoque


def index(request):
    produtos = Produto.objects.all()
    default_min = 10

    total_produtos = produtos.count()
    estoque_baixo = 0
    sem_estoque = 0
    produtos_list = []

    for p in produtos:
        estoque_atual = getattr(p, 'estoque', 0)
        estoque_min = getattr(p, 'estoque_min', default_min)
        status = 'normal'
        if estoque_atual == 0:
            sem_estoque += 1
            status = 'sem_estoque'
        elif estoque_atual < estoque_min:
            estoque_baixo += 1
            status = 'estoque_baixo'

        # Buscar última movimentação
        ultimo_movimento = MovimentoEstoque.objects.filter(produto=p).order_by('-data').first()
        ultima_atualizacao = ultimo_movimento.data if ultimo_movimento else None

        produtos_list.append({
            'obj': p,
            'estoque_min': estoque_min,
            'status': status,
            'ultima_atualizacao': ultima_atualizacao,
        })

    context = {
        'produtos': produtos_list,
        'total_produtos': total_produtos,
        'estoque_baixo': estoque_baixo,
        'sem_estoque': sem_estoque,
    }

    return render(request, 'estoque/index.html', context)


@require_POST
def ajustar(request, produto_id):
    action = request.POST.get('action')
    if action not in ('inc', 'dec'):
        messages.error(request, 'Ação inválida')
        return redirect('estoque:index')

    delta = 1 if action == 'inc' else -1
    try:
        ajustar_estoque(produto_id, delta)
        messages.success(request, 'Estoque atualizado com sucesso')
    except Exception as e:
        messages.error(request, f'Erro ao atualizar estoque: {e}')

    return redirect('estoque:index')
