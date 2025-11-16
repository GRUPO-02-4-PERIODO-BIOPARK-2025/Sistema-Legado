"""Fornecedores models"""
from django.db import models


class Fornecedor(models.Model):
    nome = models.CharField('Razão Social', max_length=255)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=255, blank=True)
    cnpj = models.CharField('CNPJ/CPF', max_length=20, blank=False)
    inscricao_estadual = models.CharField('Inscrição Estadual', max_length=50, blank=True)
    categoria = models.CharField('Categoria', max_length=100, blank=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=False)
    estado = models.CharField('Estado', max_length=2, blank=False)
    cep = models.CharField('CEP', max_length=12, blank=False)
    telefone = models.CharField('Telefone', max_length=50, blank=True)
    celular = models.CharField('Celular', max_length=50, blank=True)
    email = models.EmailField('E-mail', max_length=254, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.nome
