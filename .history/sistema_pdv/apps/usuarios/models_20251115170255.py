"""Usuarios models"""
from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    permissao = models.CharField(max_length=50, blank=True, default='usuario')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.usuario.username

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'
