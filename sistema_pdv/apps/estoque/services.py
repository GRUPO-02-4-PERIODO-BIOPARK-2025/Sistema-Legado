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
    
    # Verificar se precisa gerar notificação de estoque baixo
    try:
        from apps.notificacoes.services import verificar_estoque_baixo
        verificar_estoque_baixo(produto)
    except Exception as e:
        print(f"Erro ao verificar estoque baixo: {e}")
    
    return produto
