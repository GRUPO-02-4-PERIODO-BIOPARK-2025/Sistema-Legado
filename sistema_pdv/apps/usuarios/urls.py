from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastro/', views.cadastro_view, name='cadastro'),
    path('recuperar-senha/', views.recuperar_senha_view, name='recuperar_senha'),
]
