"""Funcionarios models placeholder"""
from django.db import models

class Funcionario(models.Model):
    nome = models.CharField(max_length=255)
    cargo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nome
