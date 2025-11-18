"""Notificações via REST API"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from . import services
from .models import Notification, StockThreshold
from apps.produtos.models import Produto


@require_GET
@login_required(login_url='usuarios:login')
def listar_notificacoes(request):
    """
    Endpoint para listar notificações
    GET /api/notificacoes/
    Query params:
        - nao_lidas: true/false (filtrar apenas não lidas)
        - limit: int (limitar quantidade)
    """
    try:
        nao_lidas_apenas = request.GET.get('nao_lidas', 'false').lower() == 'true'
        limit = request.GET.get('limit')
        
        if nao_lidas_apenas:
            notificacoes = services.obter_notificacoes_nao_lidas()
        else:
            notificacoes = Notification.objects.all().select_related('produto')
        
        if limit:
            notificacoes = list(notificacoes)[:int(limit)]
        
        # Serializar notificações
        data = [{
            'id': n.id, # type: ignore
            'tipo': n.tipo,
            'prioridade': n.prioridade,
            'titulo': n.titulo,
            'mensagem': n.mensagem,
            'produto': {
                'id': n.produto.id,
                'nome': n.produto.nome,
                'estoque_atual': n.produto.estoque
            },
            'quantidade_atual': n.quantidade_atual,
            'quantidade_minima': n.quantidade_minima,
            'lida': n.lida,
            'criado_em': n.criado_em.isoformat(),
            'lida_em': n.lida_em.isoformat() if n.lida_em else None
        } for n in notificacoes]
        
        return JsonResponse({
            'success': True,
            'count': len(data),
            'notificacoes': data
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_POST
@login_required(login_url='usuarios:login')
def marcar_lida(request, notification_id):
    """
    API endpoint para marcar notificação como lida
    POST /api/notificacoes/<id>/marcar-lida/
    """
    try:
        resultado = services.marcar_notificacao_lida(
            notification_id,
            usuario=request.user
        )
        
        if resultado['success']:
            return JsonResponse(resultado)
        else:
            return JsonResponse(resultado, status=404)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_POST
@login_required(login_url='usuarios:login')
def marcar_todas_lidas(request):
    """
    API endpoint para marcar todas as notificações como lidas
    POST /api/notificacoes/marcar-todas-lidas/
    """
    try:
        resultado = services.marcar_todas_lidas(usuario=request.user)
        return JsonResponse(resultado)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_GET
@login_required(login_url='usuarios:login')
def obter_estatisticas(request):
    """
    API endpoint para obter estatísticas de notificações
    GET /api/notificacoes/estatisticas/
    """
    try:
        stats = services.obter_estatisticas()
        return JsonResponse({
            'success': True,
            'estatisticas': stats
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_POST
@login_required(login_url='usuarios:login')
def verificar_produto(request, produto_id):
    """
    API endpoint para verificar estoque de um produto específico
    POST /api/notificacoes/verificar-produto/<produto_id>/
    """
    try:
        produto = Produto.objects.get(pk=produto_id)
        resultado = services.verificar_estoque_baixo(produto)
        
        return JsonResponse({
            'success': True,
            'notificacao_criada': resultado.get('created', False),
            'produto': {
                'id': produto.id, # type: ignore
                'nome': produto.nome,
                'estoque': produto.estoque
            }
        })
    
    except Produto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Produto não encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_POST
@login_required(login_url='usuarios:login')
def verificar_todos(request):
    """
    API endpoint para verificar estoque de todos os produtos
    POST /api/notificacoes/verificar-todos/
    """
    try:
        resultado = services.verificar_todos_produtos()
        return JsonResponse({
            'success': True,
            'resultado': resultado
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["GET", "POST", "PUT"])
@login_required(login_url='usuarios:login')
def gerenciar_threshold(request, produto_id=None):
    """
    API endpoint para gerenciar thresholds de estoque
    GET /api/notificacoes/thresholds/ - Listar todos
    GET /api/notificacoes/thresholds/<produto_id>/ - Obter específico
    POST /api/notificacoes/thresholds/ - Criar/atualizar
    """
    try:
        if request.method == 'GET':
            if produto_id:
                # Buscar threshold específico
                try:
                    threshold = StockThreshold.objects.select_related('produto').get(
                        produto_id=produto_id
                    )
                    return JsonResponse({
                        'success': True,
                        'threshold': {
                            'id': threshold.id, # type: ignore
                            'produto_id': threshold.produto.id,
                            'produto_nome': threshold.produto.nome,
                            'quantidade_minima': threshold.quantidade_minima,
                            'ativo': threshold.ativo,
                            'criado_em': threshold.criado_em.isoformat(),
                            'atualizado_em': threshold.atualizado_em.isoformat()
                        }
                    })
                except StockThreshold.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'message': 'Threshold não encontrado'
                    }, status=404)
            else:
                # Listar todos os thresholds
                thresholds = StockThreshold.objects.select_related('produto').all()
                data = [{
                    'id': t.id, # type: ignore
                    'produto_id': t.produto.id,
                    'produto_nome': t.produto.nome,
                    'quantidade_minima': t.quantidade_minima,
                    'ativo': t.ativo,
                    'estoque_atual': t.produto.estoque
                } for t in thresholds]
                
                return JsonResponse({
                    'success': True,
                    'count': len(data),
                    'thresholds': data
                })
        
        elif request.method in ['POST', 'PUT']:
            # Criar ou atualizar threshold
            data = json.loads(request.body)
            produto_id = data.get('produto_id') or produto_id
            quantidade_minima = data.get('quantidade_minima')
            ativo = data.get('ativo', True)
            
            if not produto_id or quantidade_minima is None:
                return JsonResponse({
                    'success': False,
                    'message': 'produto_id e quantidade_minima são obrigatórios'
                }, status=400)
            
            resultado = services.criar_ou_atualizar_threshold(
                produto_id,
                quantidade_minima,
                ativo
            )
            
            if resultado['success']:
                threshold = resultado['threshold']
                return JsonResponse({
                    'success': True,
                    'created': resultado['created'],
                    'threshold': {
                        'id': threshold.id,
                        'produto_id': threshold.produto.id,
                        'quantidade_minima': threshold.quantidade_minima,
                        'ativo': threshold.ativo
                    }
                })
            else:
                return JsonResponse(resultado, status=400)
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_GET
@login_required(login_url='usuarios:login')
def health_check(request):
    """
    API endpoint para verificar saúde do serviço de notificações
    GET /api/notificacoes/health/
    """
    return JsonResponse({
        'success': True,
        'status': 'healthy',
        'service': 'notifications'
    })
