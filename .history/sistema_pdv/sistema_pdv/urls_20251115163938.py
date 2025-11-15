from django.contrib import admin
from django.urls import path, include
from apps.usuarios import views as usuarios_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Make the site root go to the user registration (cadastro) page
    path('', usuarios_views.cadastro_view, name='root'),
    path('dashboard/', include('apps.dashboard.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('funcionarios/', include('apps.funcionarios.urls')),
    path('fornecedores/', include('apps.fornecedores.urls')),
    path('produtos/', include('apps.produtos.urls')),
    path('estoque/', include('apps.estoque.urls')),
    path('vendas/', include('apps.vendas.urls')),
    path('usuarios/', include('apps.usuarios.urls')),
]
