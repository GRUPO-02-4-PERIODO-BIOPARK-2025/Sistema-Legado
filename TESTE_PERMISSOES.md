# 🔐 Sistema de Permissões - Documentação

## Visão Geral
O sistema agora possui dois tipos de usuários com diferentes níveis de acesso:
- **Administrador**: Acesso total ao sistema
- **Funcionário**: Acesso restrito apenas ao PDV e Cadastro de Clientes

## Funcionalidades Implementadas

### 1. Campo de Tipo de Usuário no Cadastro
- Adicionado campo "Tipo de Usuário" no formulário de cadastro
- Opções disponíveis:
  - Administrador
  - Funcionário

### 2. Middleware de Permissões
- Controla automaticamente o acesso às URLs baseado no tipo de usuário
- Redireciona funcionários que tentam acessar páginas não autorizadas
- Exibe mensagem de alerta quando acesso é negado

### 3. Menu Lateral Dinâmico
- O menu (navbar) agora mostra apenas as opções permitidas para cada tipo de usuário
- **Administrador** vê todas as opções
- **Funcionário** vê apenas:
  - Dashboard
  - PDV - Vendas
  - Clientes

## Permissões por Tipo de Usuário

### 👨‍💼 Administrador
**Acesso Total:**
- ✅ Dashboard
- ✅ PDV - Vendas
- ✅ Produtos
- ✅ Estoque
- ✅ Clientes
- ✅ Funcionários
- ✅ Fornecedores
- ✅ Relatórios
- ✅ Financeiro
- ✅ Gerenciar Vendas

### 👤 Funcionário
**Acesso Restrito:**
- ✅ Dashboard (visualização)
- ✅ PDV - Vendas (realizar vendas)
- ✅ Clientes (cadastrar/editar clientes)
- ❌ Produtos
- ❌ Estoque
- ❌ Funcionários
- ❌ Fornecedores
- ❌ Relatórios
- ❌ Financeiro

## Como Testar

### Teste 1: Criar Usuário Funcionário
1. Acesse: http://127.0.0.1:8000/usuarios/cadastro/
2. Preencha os dados
3. Selecione "Funcionário" no campo "Tipo de Usuário"
4. Clique em "Cadastrar"
5. Faça login com as credenciais criadas

**Resultado esperado:**
- Menu lateral mostra apenas: Dashboard, PDV - Vendas, Clientes
- Tentativa de acessar outras URLs redireciona para dashboard com mensagem de alerta

### Teste 2: Criar Usuário Administrador
1. Acesse: http://127.0.0.1:8000/usuarios/cadastro/
2. Preencha os dados
3. Selecione "Administrador" no campo "Tipo de Usuário"
4. Clique em "Cadastrar"
5. Faça login com as credenciais criadas

**Resultado esperado:**
- Menu lateral mostra todas as opções
- Acesso liberado para todas as URLs do sistema

### Teste 3: Tentar Burlar Permissões (Funcionário)
1. Faça login como funcionário
2. Tente acessar diretamente: http://127.0.0.1:8000/produtos/
3. Ou: http://127.0.0.1:8000/funcionarios/
4. Ou: http://127.0.0.1:8000/fornecedores/

**Resultado esperado:**
- Redirecionamento automático para dashboard
- Mensagem: "Você não tem permissão para acessar esta página."

## Arquivos Modificados

### Novos Arquivos:
- `apps/usuarios/decorators.py` - Decorator para views administrativas
- `apps/usuarios/middleware.py` - Middleware de controle de permissões
- `atualizar_perfis.py` - Script para atualizar perfis existentes

### Arquivos Alterados:
- `apps/usuarios/forms.py` - Adicionado campo tipo_usuario
- `apps/usuarios/models.py` - Campo permissao no modelo Perfil
- `apps/usuarios/templates/usuarios/cadastro.html` - Campo tipo_usuario no form
- `sistema_pdv/settings.py` - Middleware adicionado
- `templates/navbar.html` - Menu condicional baseado em permissão

## Perfis Existentes

Todos os perfis existentes foram automaticamente atualizados para **Administrador**:
- ✓ alessandrav
- ✓ andressa
- ✓ marcela
- ✓ alessandr

## Segurança

### Camadas de Proteção:
1. **Middleware**: Intercepta todas as requisições e valida permissões
2. **Template**: Menu mostra apenas opções permitidas
3. **Decorator**: Pode ser usado em views específicas (disponível para uso futuro)

### Validações:
- Usuário precisa estar autenticado
- Sistema verifica o perfil e permissão antes de cada acesso
- Mensagens claras de erro quando acesso é negado

## URLs Públicas (Sem Restrição)

- `/usuarios/login/`
- `/usuarios/cadastro/`
- `/usuarios/logout/`
- `/usuarios/recuperar-senha/`
- `/dashboard/` (visualização apenas)

## Próximos Passos (Opcional)

1. **Permissões Granulares**: Criar mais níveis de permissão (ex: supervisor, gerente)
2. **Logs de Acesso**: Registrar tentativas de acesso negado
3. **Perfil de Usuário**: Página para visualizar/editar perfil
4. **Alterar Senha**: Funcionalidade para usuário alterar própria senha
5. **Permissões por Módulo**: Controle mais fino por funcionalidade

## Comandos Úteis

```bash
# Verificar sistema
python sistema_pdv/manage.py check

# Criar migrações
python sistema_pdv/manage.py makemigrations

# Aplicar migrações
python sistema_pdv/manage.py migrate

# Atualizar perfis existentes
Get-Content atualizar_perfis.py | python sistema_pdv/manage.py shell

# Iniciar servidor
python sistema_pdv/manage.py runserver
```

## Observações Importantes

⚠️ **Atenção:**
- O primeiro usuário cadastrado deve ser um Administrador
- Funcionários NÃO podem criar outros usuários
- Apenas Administradores podem acessar a gestão de Funcionários
- A permissão é verificada em tempo real a cada requisição

✅ **Recomendações:**
- Sempre testar com ambos os tipos de usuário
- Verificar logs do Django para debug
- Manter backup do banco de dados antes de mudanças em produção
