"""Usuarios models placeholder"""
from django.db import models

class Perfil(models.Model):
    usuario = models.CharField(max_length=150)
    email = models.EmailField()
    permissao = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.usuario
