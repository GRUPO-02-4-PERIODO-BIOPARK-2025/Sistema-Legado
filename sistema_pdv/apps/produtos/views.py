from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import ProdutoForm
from .models import Produto
from . import services


def index(request):
    produtos = services.buscar_produtos()
    form = ProdutoForm()

    return render(request, 'produtos/index.html', {
        'produtos': produtos,
        'form': form,
    })


def create(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save()
            # Verificar se precisa gerar notificação de estoque baixo
            try:
                from apps.notificacoes.services import verificar_estoque_baixo
                verificar_estoque_baixo(produto)
            except Exception as e:
                print(f"Erro ao verificar estoque baixo: {e}")
            return redirect(reverse('produtos:index'))

    return redirect(reverse('produtos:index'))


def edit(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            produto = form.save()
            # Verificar se precisa gerar notificação de estoque baixo
            try:
                from apps.notificacoes.services import verificar_estoque_baixo
                verificar_estoque_baixo(produto)
            except Exception as e:
                print(f"Erro ao verificar estoque baixo: {e}")
            return redirect(reverse('produtos:index'))
    else:
        form = ProdutoForm(instance=produto)

    produtos = services.buscar_produtos()

    return render(request, 'produtos/index.html', {
        'produtos': produtos,
        'form': form,
        'edit_id': produto.pk,
    })


def delete(request, pk):
    produto = get_object_or_404(Produto, pk=pk)

    if request.method == 'POST':
        produto.delete()

    return redirect(reverse('produtos:index'))
