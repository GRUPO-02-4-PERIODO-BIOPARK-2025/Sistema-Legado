from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Max, Q
from django.http import HttpResponse
import csv

from apps.produtos.models import Produto
from .models import MovimentoEstoque
from .services import ajustar_estoque


def index(request):
    # Parâmetros de busca e filtro
    busca = request.GET.get('busca', '').strip()
    filtro_status = request.GET.get('status', '')

    produtos = Produto.objects.all()

    # Aplicar busca por nome
    if busca:
        produtos = produtos.filter(nome__icontains=busca)

    total_produtos = Produto.objects.count()
    estoque_baixo = 0
    sem_estoque = 0
    produtos_list = []

    for p in produtos:
        estoque_atual = getattr(p, 'estoque', 0)
        estoque_min = getattr(p, 'estoque_min', 10)
        status = 'normal'
        if estoque_atual == 0:
            status = 'sem_estoque'
        elif estoque_atual < estoque_min:
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

    # Aplicar filtro de status
    if filtro_status:
        produtos_list = [item for item in produtos_list if item['status'] == filtro_status]

    # Contar totais (sempre sobre todos os produtos, não filtrados)
    for p in Produto.objects.all():
        estoque_atual = getattr(p, 'estoque', 0)
        estoque_min = getattr(p, 'estoque_min', 10)
        if estoque_atual == 0:
            sem_estoque += 1
        elif estoque_atual < estoque_min:
            estoque_baixo += 1

    context = {
        'produtos': produtos_list,
        'total_produtos': total_produtos,
        'estoque_baixo': estoque_baixo,
        'sem_estoque': sem_estoque,
        'busca': busca,
        'filtro_status': filtro_status,
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


def relatorio(request):
    # Filtros
    busca = request.GET.get('busca', '').strip()
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    movimentos = MovimentoEstoque.objects.select_related('produto').order_by('-data')

    # Aplicar filtros
    if busca:
        movimentos = movimentos.filter(produto__nome__icontains=busca)

    if data_inicio:
        movimentos = movimentos.filter(data__date__gte=data_inicio)

    if data_fim:
        movimentos = movimentos.filter(data__date__lte=data_fim)

    context = {
        'movimentos': movimentos[:100],  # Limitar a 100 registros
        'busca': busca,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }

    return render(request, 'estoque/relatorio.html', context)


def exportar_relatorio(request):
    # Mesmos filtros do relatório
    busca = request.GET.get('busca', '').strip()
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    movimentos = MovimentoEstoque.objects.select_related('produto').order_by('-data')

    if busca:
        movimentos = movimentos.filter(produto__nome__icontains=busca)
    if data_inicio:
        movimentos = movimentos.filter(data__date__gte=data_inicio)
    if data_fim:
        movimentos = movimentos.filter(data__date__lte=data_fim)

    # Criar CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="relatorio_estoque.csv"'
    response.write('\ufeff')  # BOM para UTF-8

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Data/Hora', 'Produto', 'Quantidade', 'Tipo', 'Estoque Atual'])

    for mov in movimentos:
        tipo = 'Entrada' if mov.quantidade > 0 else 'Saída'
        writer.writerow([
            mov.data.strftime('%d/%m/%Y %H:%M:%S'),
            mov.produto.nome,
            abs(mov.quantidade),
            tipo,
            mov.produto.estoque,
        ])

    return response
