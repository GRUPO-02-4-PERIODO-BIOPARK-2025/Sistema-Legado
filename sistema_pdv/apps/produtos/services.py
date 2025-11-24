from .models import Produto

def buscar_produtos():
    return Produto.objects.all().order_by('nome')
