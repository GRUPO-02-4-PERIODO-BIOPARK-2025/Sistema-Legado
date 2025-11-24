from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return redirect('usuarios:login')

urlpatterns = [
    path('usuarios/', include('apps.usuarios.urls')),
    path('admin/', admin.site.urls),
    path('', root_redirect, name='root'),
    path('dashboard/', include('apps.dashboard.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('funcionarios/', include('apps.funcionarios.urls')),
    path('fornecedores/', include('apps.fornecedores.urls')),
    path('produtos/', include('apps.produtos.urls')),
    path('estoque/', include('apps.estoque.urls')),
    path('vendas/', include('apps.vendas.urls')),
    path('', include('apps.notificacoes.urls')),
    path('relatorios/', include('apps.relatorios.urls')),
    ]