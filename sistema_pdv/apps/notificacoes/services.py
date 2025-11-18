"""Notificações business logic"""
from django.db import transaction
from django.utils import timezone
from apps.produtos.models import Produto
from .models import Notification, StockThreshold


def verificar_estoque_baixo(produto):
    """
    Verifica se o produto está com estoque baixo e cria notificação se necessário
    
    Args:
        produto: Instância do modelo Produto
    
    Returns:
        dict: {'created': bool, 'notification': Notification ou None}
    """
    try:
        # Buscar threshold do produto
        threshold = StockThreshold.objects.filter(
            produto=produto,
            ativo=True
        ).first()
        
        # Se não houver threshold configurado, usa padrão de 10
        quantidade_minima = threshold.quantidade_minima if threshold else 10
        
        # Verificar se já existe notificação não lida recente (últimas 24h)
        from datetime import timedelta
        uma_hora_atras = timezone.now() - timedelta(hours=1)
        notificacao_recente = Notification.objects.filter(
            produto=produto,
            lida=False,
            criado_em__gte=uma_hora_atras
        ).exists()
        
        if notificacao_recente:
            return {'created': False, 'notification': None}
        
        # Determinar tipo e prioridade baseado no estoque
        estoque_atual = produto.estoque
        
        if estoque_atual == 0:
            tipo = 'out_of_stock'
            prioridade = 'critical'
            titulo = f'SEM ESTOQUE: {produto.nome}'
            mensagem = f'O produto "{produto.nome}" está sem estoque!'
        elif estoque_atual <= quantidade_minima * 0.3:  # Menos de 30% do mínimo
            tipo = 'critical'
            prioridade = 'critical'
            titulo = f'CRÍTICO: {produto.nome}'
            mensagem = f'O produto "{produto.nome}" está com apenas {estoque_atual} unidades (mínimo: {quantidade_minima})'
        elif estoque_atual <= quantidade_minima:
            tipo = 'low_stock'
            prioridade = 'high'
            titulo = f'Estoque Baixo: {produto.nome}'
            mensagem = f'O produto "{produto.nome}" está com {estoque_atual} unidades (mínimo: {quantidade_minima})'
        else:
            # Estoque OK
            return {'created': False, 'notification': None}
        
        # Criar notificação
        notification = Notification.objects.create(
            produto=produto,
            tipo=tipo,
            prioridade=prioridade,
            titulo=titulo,
            mensagem=mensagem,
            quantidade_atual=estoque_atual,
            quantidade_minima=quantidade_minima
        )
        
        return {'created': True, 'notification': notification}
    
    except Exception as e:
        print(f"Erro ao verificar estoque baixo: {e}")
        return {'created': False, 'notification': None, 'error': str(e)}


def verificar_todos_produtos():
    """
    Verifica todos os produtos ativos e gera notificações para estoque baixo
    
    Returns:
        dict: Estatísticas da verificação
    """
    produtos = Produto.objects.all()
    total = produtos.count()
    criadas = 0
    
    for produto in produtos:
        resultado = verificar_estoque_baixo(produto)
        if resultado.get('created'):
            criadas += 1
    
    return {
        'total_verificados': total,
        'notificacoes_criadas': criadas
    }


def obter_notificacoes_nao_lidas():
    """
    Retorna todas as notificações não lidas ordenadas por prioridade
    
    Returns:
        QuerySet: Notificações não lidas
    """
    # Ordem de prioridade personalizada
    ordem_prioridade = {
        'critical': 1,
        'high': 2,
        'medium': 3,
        'low': 4
    }
    
    notificacoes = Notification.objects.filter(lida=False).select_related('produto')
    
    # Ordenar por prioridade e depois por data
    return sorted(
        notificacoes,
        key=lambda n: (ordem_prioridade.get(n.prioridade, 99), -n.criado_em.timestamp())
    )


def marcar_notificacao_lida(notification_id, usuario=None):
    """
    Marca uma notificação como lida
    
    Args:
        notification_id: ID da notificação
        usuario: Usuário que leu a notificação (opcional)
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        notification = Notification.objects.get(pk=notification_id)
        notification.marcar_como_lida(usuario)
        return {'success': True, 'message': 'Notificação marcada como lida'}
    except Notification.DoesNotExist:
        return {'success': False, 'message': 'Notificação não encontrada'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def marcar_todas_lidas(usuario=None):
    """
    Marca todas as notificações como lidas
    
    Args:
        usuario: Usuário que leu as notificações (opcional)
    
    Returns:
        dict: {'success': bool, 'count': int}
    """
    try:
        with transaction.atomic():
            notificacoes = Notification.objects.filter(lida=False)
            count = notificacoes.count()
            
            for notificacao in notificacoes:
                notificacao.marcar_como_lida(usuario)
            
            return {'success': True, 'count': count}
    except Exception as e:
        return {'success': False, 'message': str(e), 'count': 0}


def criar_ou_atualizar_threshold(produto_id, quantidade_minima, ativo=True):
    """
    Cria ou atualiza o threshold de estoque mínimo para um produto
    
    Args:
        produto_id: ID do produto
        quantidade_minima: Quantidade mínima de estoque
        ativo: Se o threshold está ativo
    
    Returns:
        dict: {'success': bool, 'threshold': StockThreshold}
    """
    try:
        produto = Produto.objects.get(pk=produto_id)
        threshold, created = StockThreshold.objects.update_or_create(
            produto=produto,
            defaults={
                'quantidade_minima': quantidade_minima,
                'ativo': ativo
            }
        )
        
        # Verificar se já precisa criar notificação
        if created or ativo:
            verificar_estoque_baixo(produto)
        
        return {
            'success': True,
            'threshold': threshold,
            'created': created
        }
    except Produto.DoesNotExist:
        return {'success': False, 'message': 'Produto não encontrado'}
    except Exception as e:
        return {'success': False, 'message': str(e)}


def obter_estatisticas():
    """
    Retorna estatísticas sobre notificações
    
    Returns:
        dict: Estatísticas de notificações
    """
    total = Notification.objects.count()
    nao_lidas = Notification.objects.filter(lida=False).count()
    criticas = Notification.objects.filter(
        lida=False,
        prioridade='critical'
    ).count()
    
    # Produtos com estoque crítico
    produtos_criticos = Produto.objects.filter(
        notifications__lida=False,
        notifications__prioridade='critical'
    ).distinct().count()
    
    return {
        'total_notificacoes': total,
        'nao_lidas': nao_lidas,
        'criticas': criticas,
        'produtos_criticos': produtos_criticos
    }
