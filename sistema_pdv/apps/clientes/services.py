from .models import Cliente

def buscar_clientes():
    return Cliente.objects.all().order_by('-created_at')

def obter_cliente(pk):
    try:
        return Cliente.objects.get(pk=pk)
    except Cliente.DoesNotExist:
        return None
