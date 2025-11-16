"""Fornecedores business logic helpers"""
from .models import Fornecedor


def buscar_fornecedores():
    return Fornecedor.objects.all()


def obter_fornecedor(pk):
    try:
        return Fornecedor.objects.get(pk=pk)
    except Fornecedor.DoesNotExist:
        return None
