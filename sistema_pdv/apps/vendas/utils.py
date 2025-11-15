"""Auxiliary functions for vendas (PDV)"""

def calcular_total(itens):
    return sum((i.get('preco', 0) * i.get('quantidade', 0)) for i in itens)
