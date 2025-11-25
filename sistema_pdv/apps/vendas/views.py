from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q

from apps.produtos.models import Produto
from apps.clientes.models import Cliente
from .models import Venda, ItemVenda, Pagamento
from .services import processar_venda, cancelar_venda


@login_required(login_url='usuarios:login')
def index(request):
    from apps.clientes.models import Cliente
    
    # Buscar ou criar venda em aberto para o usuário
    venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
    
    if not venda:
        venda = Venda.objects.create(usuario=request.user)
    
    itens = venda.itemvenda_set.select_related('produto').all()
    produtos = Produto.objects.filter(estoque__gt=0).order_by('nome')
    clientes = Cliente.objects.all().order_by('nome')
    
    context = {
        'venda': venda,
        'itens': itens,
        'produtos': produtos,
        'clientes': clientes,
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
    from decimal import Decimal
    try:
        desconto = Decimal(str(request.POST.get('desconto', 0)))
        venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
        
        if not venda:
            return JsonResponse({'success': False, 'message': 'Nenhuma venda em aberto'})
        
        if desconto < 0 or desconto > venda.subtotal:
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
def aplicar_frete(request):
    from decimal import Decimal
    try:
        frete = Decimal(str(request.POST.get('frete', 0)))
        venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
        
        if not venda:
            return JsonResponse({'success': False, 'message': 'Nenhuma venda em aberto'})
        
        if frete < 0:
            return JsonResponse({'success': False, 'message': 'Frete inválido'})
        
        venda.frete = frete
        venda.calcular_total()
        
        return JsonResponse({
            'success': True,
            'total': float(venda.total),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def associar_cliente(request):
    try:
        cliente_id = request.POST.get('cliente_id')
        venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
        
        if not venda:
            return JsonResponse({'success': False, 'message': 'Nenhuma venda em aberto'})
        
        if cliente_id and cliente_id != '':
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            venda.cliente = cliente
            cliente_nome = cliente.nome
        else:
            venda.cliente = None
            cliente_nome = 'Cliente não informado'
        
        venda.save()
        
        return JsonResponse({
            'success': True,
            'cliente_nome': cliente_nome,
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
            
            # Capturar número de parcelas do cartão (aceita ambos os nomes)
            parcelas_cartao = int(request.POST.get('cartao_parcelas', request.POST.get('parcelas_cartao', 1)))
            
            total_pago = sum(pagamentos_data.values())
            
            if total_pago < float(venda.total):
                return JsonResponse({
                    'success': False,
                    'message': f'Valor insuficiente. Falta: R$ {float(venda.total) - total_pago:.2f}'
                })
            
            # Criar registros de pagamento
            from apps.vendas.models import Parcela
            from datetime import timedelta
            
            for tipo, valor in pagamentos_data.items():
                if valor > 0:
                    # Se for cartão, usar o número de parcelas informado
                    parcelas = parcelas_cartao if tipo == 'cartao' else 1
                    
                    pagamento = Pagamento.objects.create(
                        venda=venda,
                        tipo=tipo,
                        valor=valor,
                        parcelas=parcelas
                    )
                    
                    # Criar as parcelas individuais
                    if parcelas == 1:
                        # À vista - criar parcela única já paga
                        Parcela.objects.create(
                            pagamento=pagamento,
                            numero=1,
                            valor=valor,
                            status='pago',
                            data_vencimento=venda.data.date(),
                            data_pagamento=venda.data,
                            usuario_baixa=request.user
                        )
                    else:
                        # Parcelado - criar parcelas pendentes
                        valor_parcela = valor / parcelas
                        for i in range(1, parcelas + 1):
                            # Vencimento: 30 dias para cada parcela
                            dias_vencimento = 30 * i
                            data_vencimento = venda.data.date() + timedelta(days=dias_vencimento)
                            
                            Parcela.objects.create(
                                pagamento=pagamento,
                                numero=i,
                                valor=valor_parcela,
                                status='pendente',
                                data_vencimento=data_vencimento
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


@require_POST
def atualizar_cliente(request):
    """Atualiza o cliente da venda em aberto"""
    try:
        from apps.clientes.models import Cliente
        
        cliente_id = request.POST.get('cliente_id')
        venda = Venda.objects.filter(finalizada=False, usuario=request.user).first()
        
        if not venda:
            return JsonResponse({'success': False, 'message': 'Nenhuma venda em aberto'})
        
        if cliente_id and cliente_id != '':
            cliente = get_object_or_404(Cliente, pk=cliente_id)
            venda.cliente = cliente
        else:
            venda.cliente = None
        
        venda.save()
        
        return JsonResponse({
            'success': True,
            'cliente_nome': venda.cliente.nome if venda.cliente else 'Sem cliente'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def gerenciar_vendas(request):
    """View para gerenciar vendas finalizadas"""
    vendas = Venda.objects.filter(finalizada=True).select_related('cliente', 'usuario').prefetch_related('pagamentos__parcelas_detalhes').order_by('-data')
    
    # Filtros
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    cliente = request.GET.get('cliente')
    status_filtro = request.GET.get('status')
    
    if data_inicio:
        vendas = vendas.filter(data__date__gte=data_inicio)
    if data_fim:
        vendas = vendas.filter(data__date__lte=data_fim)
    if cliente:
        vendas = vendas.filter(Q(cliente__nome__icontains=cliente) | Q(codigo_barras__icontains=cliente))
    
    # Filtrar por status de pagamento
    if status_filtro:
        vendas_filtradas = []
        for venda in vendas:
            status_venda = venda.get_status_pagamento()
            if status_venda['status'] == status_filtro:
                vendas_filtradas.append(venda.id)
        vendas = vendas.filter(id__in=vendas_filtradas)
    
    context = {
        'vendas': vendas,
        'data_inicio': data_inicio or '',
        'data_fim': data_fim or '',
        'cliente': cliente or '',
        'status': status_filtro or '',
    }
    return render(request, 'vendas/gerenciar.html', context)


def detalhes_venda(request, venda_id):
    """Retorna os detalhes de uma venda em JSON"""
    try:
        venda = get_object_or_404(Venda, pk=venda_id, finalizada=True)
        itens = venda.itemvenda_set.select_related('produto').all()
        pagamentos = venda.pagamentos.all()
        
        itens_data = [{
            'produto': item.produto.nome,
            'quantidade': item.quantidade,
            'preco_unitario': float(item.preco_unitario),
            'subtotal': float(item.subtotal),
        } for item in itens]
        
        pagamentos_data = []
        for p in pagamentos:
            parcelas_info = []
            
            # Buscar parcelas do banco de dados
            parcelas_db = p.parcelas_detalhes.all()
            
            for parcela in parcelas_db:
                parcelas_info.append({
                    'id': parcela.id,
                    'numero': parcela.numero,
                    'valor': float(parcela.valor),
                    'status': parcela.status,
                    'status_display': parcela.get_status_display(),
                    'data_vencimento': parcela.data_vencimento.strftime('%d/%m/%Y') if parcela.data_vencimento else None,
                    'data_pagamento': parcela.data_pagamento.strftime('%d/%m/%Y %H:%M') if parcela.data_pagamento else None,
                })
            
            pagamentos_data.append({
                'tipo': p.get_tipo_display(),
                'valor': float(p.valor),
                'parcelas': p.parcelas,
                'parcelas_detalhes': parcelas_info
            })
        
        return JsonResponse({
            'success': True,
            'venda': {
                'id': venda.id,
                'codigo_barras': venda.codigo_barras,
                'data': venda.data.strftime('%d/%m/%Y %H:%M'),
                'cliente': venda.cliente.nome if venda.cliente else 'Cliente não informado',
                'usuario': venda.usuario.username if venda.usuario else 'N/A',
                'subtotal': float(venda.subtotal),
                'desconto': float(venda.desconto),
                'total': float(venda.total),
                'itens': itens_data,
                'pagamentos': pagamentos_data,
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def cancelar_venda_finalizada(request, venda_id):
    """Cancela uma venda já finalizada"""
    try:
        venda = get_object_or_404(Venda, pk=venda_id, finalizada=True)
        
        with transaction.atomic():
            # Devolver itens ao estoque
            for item in venda.itemvenda_set.all():
                item.produto.estoque += item.quantidade
                item.produto.save()
            
            # Marcar venda como cancelada (podemos adicionar um campo status depois)
            # Por enquanto, apenas deletamos
            venda.delete()
        
        return JsonResponse({'success': True, 'message': 'Venda cancelada com sucesso'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_POST
def baixar_parcela(request, parcela_id):
    """Dá baixa em uma parcela específica"""
    try:
        from apps.vendas.models import Parcela
        from django.utils import timezone
        
        parcela = get_object_or_404(Parcela, pk=parcela_id)
        
        if parcela.status == 'pago':
            return JsonResponse({'success': False, 'message': 'Esta parcela já foi paga'})
        
        with transaction.atomic():
            parcela.status = 'pago'
            parcela.data_pagamento = timezone.now()
            parcela.usuario_baixa = request.user
            parcela.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Parcela {parcela.numero}/{parcela.pagamento.parcelas} baixada com sucesso!',
            'data_pagamento': parcela.data_pagamento.strftime('%d/%m/%Y %H:%M')
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
