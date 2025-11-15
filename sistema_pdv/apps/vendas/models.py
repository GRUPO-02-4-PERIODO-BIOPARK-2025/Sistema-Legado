"""Vendas models placeholder"""
from django.db import models

class Venda(models.Model):
    data = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT)
    quantidade = models.IntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)

class Pagamento(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
