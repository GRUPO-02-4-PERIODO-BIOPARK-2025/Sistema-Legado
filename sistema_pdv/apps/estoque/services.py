"""Estoque business logic"""
from django.utils import timezone

from apps.produtos.models import Produto
from .models import MovimentoEstoque


def ajustar_estoque(produto_id, delta):
    produto = Produto.objects.get(pk=produto_id)
    novo = produto.estoque + delta
    if novo < 0:
        novo = 0
    produto.estoque = novo
    produto.save()

    MovimentoEstoque.objects.create(produto=produto, quantidade=delta, data=timezone.now())
    return produto
