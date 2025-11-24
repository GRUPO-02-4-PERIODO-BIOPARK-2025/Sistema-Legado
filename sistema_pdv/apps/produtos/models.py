from django.db import models

class Produto(models.Model):

    nome = models.CharField('Nome do Produto', max_length=255)
    sku = models.CharField('SKU', max_length=100, blank=True, null=True)
    categoria = models.CharField('Categoria', max_length=255, blank=True, null=True)

    preco = models.DecimalField('Preço (R$)', max_digits=10, decimal_places=2)
    estoque = models.IntegerField('Quantidade em Estoque')
    estoque_min = models.IntegerField('Estoque Mínimo', default=10, help_text='Quantidade mínima antes de gerar alerta')
    peso = models.DecimalField('Peso (kg)', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'produtos_produto'  # 👈 tabela do banco legado
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome
