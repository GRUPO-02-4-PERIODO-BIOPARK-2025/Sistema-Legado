"""Fornecedores models placeholder"""
from django.db import models

class Fornecedor(models.Model):
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.nome
