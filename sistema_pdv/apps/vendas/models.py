"""Vendas models"""
from django.db import models
from django.contrib.auth.models import User
import uuid

class Venda(models.Model):
    codigo_barras = models.CharField(max_length=50, unique=True, editable=False)
    data = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    finalizada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.codigo_barras:
            # Gera código de barras único
            self.codigo_barras = str(uuid.uuid4().int)[:10]
        super().save(*args, **kwargs)

    def calcular_total(self):
        self.subtotal = sum(item.subtotal for item in self.itemvenda_set.all())
        self.total = self.subtotal - self.desconto
        self.save()

    def __str__(self):
        return f"Venda #{self.codigo_barras}"

class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE)
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
        self.venda.calcular_total()

    def __str__(self):
        return f"{self.produto.nome} x {self.quantidade}"

class Pagamento(models.Model):
    TIPO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('cartao', 'Cartão'),
        ('pix', 'PIX'),
        ('outros', 'Outros'),
    ]
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='pagamentos')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor}"
