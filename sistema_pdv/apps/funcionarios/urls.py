from django.urls import path
from . import views

app_name = 'funcionarios'

urlpatterns = [
    path('', views.index, name='index'),
]
