# Sistema de Notificações - Low Stock Alerts

## Visão Geral

Sistema de notificações em tempo real que monitora o estoque de produtos e envia alertas via web push quando os níveis caem abaixo do limite configurado.

## Funcionalidades

### 1. **Monitoramento Automático de Estoque**
- Verifica automaticamente quando produtos atingem níveis baixos
- Três níveis de alerta:
  - **Estoque Baixo**: Quando atinge o limite mínimo
  - **Estoque Crítico**: Quando cai abaixo do limite
  - **Produto Esgotado**: Quando estoque = 0

### 2. **Notificações Web Push**
- Badge de notificação no canto superior direito
- Contador de notificações não lidas
- Dropdown com lista de notificações
- Auto-refresh a cada 30 segundos
- Marcação individual ou em massa como "lida"

### 3. **REST API**
Endpoints disponíveis:
- `GET /api/notificacoes/` - Lista todas as notificações
- `POST /api/notificacoes/<id>/marcar-lida/` - Marca como lida
- `POST /api/notificacoes/marcar-todas-lidas/` - Marca todas como lidas
- `GET /api/notificacoes/limites/` - Lista limites de estoque
- `POST /api/notificacoes/limites/` - Define limite para produto

## Estrutura do Código

```
apps/notificacoes/
├── models.py           # Notification e StockThreshold
├── services.py         # Lógica de verificação de estoque
├── views.py            # REST API endpoints
├── urls.py             # Rotas da API
└── admin.py            # Interface admin Django

static/
├── css/notifications.css   # Estilos do sino de notificação
└── js/notifications.js     # JavaScript para interação

templates/
└── base.html              # Sino de notificação no navbar
```

## Integração com Outros Apps

### Vendas (`apps/vendas/services.py`)
Após finalizar uma venda, verifica estoque de todos os itens:
```python
from apps.notificacoes.services import verificar_estoque_baixo

def processar_venda(venda):
    with transaction.atomic():
        for item in venda.itemvenda_set.all():
            produto.estoque -= item.quantidade
            produto.save()
            verificar_estoque_baixo(produto)  # ← Trigger notificação
```

### Estoque (`apps/estoque/services.py`)
Após qualquer movimentação de estoque:
```python
from apps.notificacoes.services import verificar_estoque_baixo

def registrar_movimento(produto, quantidade, tipo):
    # Atualiza estoque...
    produto.save()
    verificar_estoque_baixo(produto)  # ← Trigger notificação
```

## Configuração

### 1. Instalar App
Já adicionado em `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'apps.notificacoes',
]
```

### 2. Executar Migrations
```powershell
python manage.py makemigrations notificacoes
python manage.py migrate
```

### 3. Definir Limites de Estoque
Via Django Admin ou API:
```python
from apps.notificacoes.models import StockThreshold

StockThreshold.objects.create(
    produto=produto,
    limite_minimo=10,
    ativo=True
)
```

## Como Usar

### 1. **Definir Limites via API**
```bash
# TODO fazer a definição pela tela de estoque
POST /api/notificacoes/limites/
Content-Type: application/json

{
    "produto_id": 1,
    "limite_minimo": 10
}
```

### 2. **Visualizar Notificações**
- Clique no sino no canto superior direito
- Badge mostra número de notificações não lidas
- Click em uma notificação marca como lida

### 3. **Marcar Todas como Lidas**
- Clique em "Marcar todas como lidas" no dropdown

## Testes

### Testes Manuais
1. Criar produto com estoque = 15
2. Definir limite = 10
3. Fazer vendas até estoque < 10
4. Verificar notificação no sino
5. Marcar como lida
6. Reduzir estoque novamente
7. Verificar nova notificação

## API Responses

### GET /api/notificacoes/
```json
{
    "success": true,
    "notificacoes": [
        {
            "id": 1,
            "tipo": "estoque_baixo",
            "titulo": "Estoque Baixo",
            "mensagem": "Produto: Teste - Estoque: 8 unidades",
            "lida": false,
            "criado_em": "2025-11-18T10:30:00Z"
        }
    ],
    "nao_lidas": 1
}
```

### POST /api/notificacoes/limites/
```json
{
    "success": true,
    "message": "Limite de estoque definido com sucesso",
    "limite": {
        "id": 1,
        "produto_id": 1,
        "limite_minimo": 10,
        "ativo": true
    }
}
```

## Lógica de Notificação

### Quando Notificar?
- Estoque <= limite_minimo
- Não existe notificação não lida para o mesmo produto
- Threshold está ativo

### Tipos de Notificação
1. **estoque_baixo**: `0 < estoque <= limite_minimo`
2. **estoque_critico**: `estoque < limite_minimo` 
3. **produto_esgotado**: `estoque = 0`

### Prevenção de Duplicatas
- Apenas uma notificação não lida por produto
- Novas notificações só após marcar anterior como lida
- Garante que usuário não seja sobrecarregado

## Personalização

### Alterar Intervalo de Refresh
Em `static/js/notifications.js`:
```javascript
setInterval(function() {
    // ...
}, 30000); // ← Alterar de 30000ms (30s) para outro valor
```

### Adicionar Novos Tipos de Notificação
1. Adicionar em `models.py`:
```python
TIPOS_NOTIFICACAO = [
    # ...
    ('novo_tipo', 'Novo Tipo'),
]
```

2. Adicionar badge em `notifications.css`
3. Adicionar formatação em `notifications.js`

