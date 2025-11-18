from django.db import models


class Funcionario(models.Model):
    nome = models.CharField('Nome Completo', max_length=255)
    email = models.EmailField('E-mail', max_length=254, blank=True)
    telefone = models.CharField('Telefone', max_length=50, blank=True)
    cpf = models.CharField('CPF', max_length=14, blank=False)
    rg = models.CharField('RG', max_length=20, blank=True)
    cargo = models.CharField('Cargo', max_length=100, blank=True)
    departamento = models.CharField('Departamento', max_length=100, blank=True)
    salario = models.DecimalField('Salário', max_digits=10, decimal_places=2, blank=True, null=True)
    data_admissao = models.DateField('Data de Admissão', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.nome
