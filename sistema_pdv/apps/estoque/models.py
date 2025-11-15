"""Estoque models placeholder"""
from django.db import models

class MovimentoEstoque(models.Model):
    produto = models.ForeignKey('produtos.Produto', on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.produto} ({self.quantidade})"
