from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def administrador_required(view_func):
    """
    Decorator que permite acesso apenas para administradores.
    Funcionários são redirecionados para o PDV.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        try:
            perfil = request.user.perfil
            if perfil.permissao == 'administrador':
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, 'Você não tem permissão para acessar esta página.')
                return redirect('vendas:index')
        except:
            messages.error(request, 'Perfil não encontrado.')
            return redirect('vendas:index')
    
    return _wrapped_view
