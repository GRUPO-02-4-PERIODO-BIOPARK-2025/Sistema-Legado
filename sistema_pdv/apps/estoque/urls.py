from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('', views.index, name='index'),
    path('ajustar/<int:produto_id>/', views.ajustar, name='ajustar'),
]
