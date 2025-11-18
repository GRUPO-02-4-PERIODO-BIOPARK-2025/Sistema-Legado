from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction

from apps.produtos.models import Produto
from .models import Venda, ItemVenda, Pagamento
from .services import processar_venda, cancelar_venda


def index(request):
    # Buscar ou criar venda em aberto para o usuário
    venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
    
    if not venda:
        venda = Venda.objects.create(usuario=request.user)
    
    itens = venda.itemvenda_set.select_related('produto').all()
    produtos = Produto.objects.filter(estoque__gt=0).order_by('nome')
    
    context = {
        'venda': venda,
        'itens': itens,
        'produtos': produtos,
    }
    return render(request, 'vendas/index.html', context)


@require_POST
def adicionar_item(request):
    try:
        produto_id = request.POST.get('produto_id')
        quantidade = int(request.POST.get('quantidade', 1))
        
        produto = get_object_or_404(Produto, pk=produto_id)
        
        # Verificar estoque
        if produto.estoque < quantidade:
            return JsonResponse({
                'success': False,
                'message': f'Estoque insuficiente. Disponível: {produto.estoque}'
            })
        
        # Buscar venda em aberto
        venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
        if not venda:
            venda = Venda.objects.create(usuario=request.user)
        
        # Verificar se já existe o item
        item = ItemVenda.objects.filter(venda=venda, produto=produto).first()
        
        if item:
            # Atualizar quantidade
            nova_quantidade = item.quantidade + quantidade
            if produto.estoque < nova_quantidade:
                return JsonResponse({
                    'success': False,
                    'message': f'Estoque insuficiente. Disponível: {produto.estoque}'
                })
            item.quantidade = nova_quantidade
            item.save()
        else:
            # Criar novo item
            ItemVenda.objects.create(
                venda=venda,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=produto.preco,
                subtotal=produto.preco * quantidade
            )
        
        venda.calcular_total()
        
        return JsonResponse({
            'success': True,
            'subtotal': float(venda.subtotal),
            'total': float(venda.total),
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def remover_item(request, item_id):
    try:
        item = get_object_or_404(ItemVenda, pk=item_id)
        venda = item.venda
        item.delete()
        venda.calcular_total()
        
        return JsonResponse({
            'success': True,
            'subtotal': float(venda.subtotal),
            'total': float(venda.total),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def atualizar_quantidade(request, item_id):
    try:
        item = get_object_or_404(ItemVenda, pk=item_id)
        acao = request.POST.get('acao')  # 'incrementar' ou 'decrementar'
        
        if acao == 'incrementar':
            if item.produto.estoque < item.quantidade + 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Estoque insuficiente'
                })
            item.quantidade += 1
        elif acao == 'decrementar':
            if item.quantidade > 1:
                item.quantidade -= 1
            else:
                # Se quantidade for 1, remove o item
                venda = item.venda
                item.delete()
                venda.calcular_total()
                return JsonResponse({
                    'success': True,
                    'removed': True,
                    'subtotal': float(venda.subtotal),
                    'total': float(venda.total),
                })
        
        item.save()
        
        return JsonResponse({
            'success': True,
            'quantidade': item.quantidade,
            'subtotal_item': float(item.subtotal),
            'subtotal': float(item.venda.subtotal),
            'total': float(item.venda.total),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def aplicar_desconto(request):
    try:
        desconto = float(request.POST.get('desconto', 0))
        venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
        
        if not venda:
            return JsonResponse({'success': False, 'message': 'Nenhuma venda em aberto'})
        
        if desconto < 0 or desconto > float(venda.subtotal):
            return JsonResponse({'success': False, 'message': 'Desconto inválido'})
        
        venda.desconto = desconto
        venda.calcular_total()
        
        return JsonResponse({
            'success': True,
            'total': float(venda.total),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def finalizar_venda(request):
    try:
        with transaction.atomic():
            venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
            
            if not venda or not venda.itemvenda_set.exists():
                return JsonResponse({'success': False, 'message': 'Carrinho vazio'})
            
            # Processar pagamentos
            pagamentos_data = {
                'dinheiro': float(request.POST.get('pagamento_dinheiro', 0)),
                'cartao': float(request.POST.get('pagamento_cartao', 0)),
                'pix': float(request.POST.get('pagamento_pix', 0)),
                'outros': float(request.POST.get('pagamento_outros', 0)),
            }
            
            total_pago = sum(pagamentos_data.values())
            
            if total_pago < float(venda.total):
                return JsonResponse({
                    'success': False,
                    'message': f'Valor insuficiente. Falta: R$ {float(venda.total) - total_pago:.2f}'
                })
            
            # Criar registros de pagamento
            for tipo, valor in pagamentos_data.items():
                if valor > 0:
                    Pagamento.objects.create(
                        venda=venda,
                        tipo=tipo,
                        valor=valor
                    )
            
            # Processar venda (atualizar estoque)
            resultado = processar_venda(venda)
            
            if resultado['success']:
                troco = total_pago - float(venda.total)
                return JsonResponse({
                    'success': True,
                    'troco': troco,
                    'codigo_barras': venda.codigo_barras,
                })
            else:
                return JsonResponse({'success': False, 'message': resultado['message']})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def cancelar(request):
    try:
        venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
        if venda:
            cancelar_venda(venda)
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
