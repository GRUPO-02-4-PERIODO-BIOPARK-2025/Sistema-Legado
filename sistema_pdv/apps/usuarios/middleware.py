from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages

class PermissaoMiddleware:
    """
    Middleware que controla o acesso às URLs baseado no tipo de usuário.
    Funcionários só podem acessar: PDV (vendas) e Clientes.
    Administradores têm acesso total.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs permitidas para funcionários (além de vendas e clientes)
        self.urls_publicas = [
            'usuarios:login',
            'usuarios:logout',
            'usuarios:cadastro',
            'usuarios:recuperar_senha',
            'dashboard:index',
        ]
        
        # Namespaces permitidos para funcionários
        self.namespaces_funcionario = ['vendas', 'clientes', 'usuarios']

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                perfil = request.user.perfil
                
                # Se for administrador, libera tudo
                if perfil.permissao == 'administrador':
                    return self.get_response(request)
                
                # Se for funcionário, verifica permissões
                if perfil.permissao == 'funcionario':
                    current_url = resolve(request.path_info)
                    url_name = f"{current_url.namespace}:{current_url.url_name}" if current_url.namespace else current_url.url_name
                    
                    # Permite URLs públicas
                    if url_name in self.urls_publicas:
                        return self.get_response(request)
                    
                    # Permite namespaces específicos para funcionário
                    if current_url.namespace in self.namespaces_funcionario:
                        return self.get_response(request)
                    
                    # Bloqueia acesso a outras URLs
                    messages.warning(request, 'Você não tem permissão para acessar esta página.')
                    return redirect('vendas:index')
                    
            except Exception as e:
                pass
        
        return self.get_response(request)
