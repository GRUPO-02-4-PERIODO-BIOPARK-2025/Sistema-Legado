"""Vendas business logic"""
from django.db import transaction
from apps.produtos.models import Produto
from apps.estoque.models import MovimentoEstoque


def processar_venda(venda):
    """Finaliza a venda e atualiza o estoque"""
    try:
        with transaction.atomic():
            # Atualizar estoque para cada item
            for item in venda.itemvenda_set.all():
                produto = item.produto
                
                if produto.estoque < item.quantidade:
                    return {
                        'success': False,
                        'message': f'Estoque insuficiente para {produto.nome}'
                    }
                
                # Reduzir estoque
                produto.estoque -= item.quantidade
                produto.save()
                
                # Registrar movimento de estoque
                MovimentoEstoque.objects.create(
                    produto=produto,
                    quantidade=-item.quantidade
                )
            
            # Marcar venda como finalizada
            venda.finalizada = True
            venda.save()
            
            return {'success': True}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}


def cancelar_venda(venda):
    """Cancela uma venda em aberto"""
    if not venda.finalizada:
        venda.itemvenda_set.all().delete()
        venda.delete()
        return True
    return False
