"""Vendas models"""
from django.db import models
from django.contrib.auth.models import User
import uuid

class Venda(models.Model):
    codigo_barras = models.CharField(max_length=50, unique=True, editable=False)
    data = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.PROTECT, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
    finalizada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.codigo_barras:
            # Gera código de barras único
            self.codigo_barras = str(uuid.uuid4().int)[:10]
        super().save(*args, **kwargs)

    def calcular_total(self):
        self.subtotal = sum(item.subtotal for item in self.itemvenda_set.all())
        self.total = self.subtotal - self.desconto + self.frete
        self.save()
    
    def get_status_pagamento(self):
        """Retorna o status do pagamento baseado nas parcelas"""
        if not self.finalizada:
            return {'status': 'aberta', 'display': 'Em Aberto'}
        
        # Buscar todas as parcelas da venda
        total_parcelas = 0
        parcelas_pagas = 0
        
        for pagamento in self.pagamentos.all():
            parcelas = pagamento.parcelas_detalhes.all()
            total_parcelas += parcelas.count()
            parcelas_pagas += parcelas.filter(status='pago').count()
        
        # Se não tem parcelas registradas, considera como pago (vendas antigas)
        if total_parcelas == 0:
            return {'status': 'pago', 'display': 'Pago'}
        
        # Se todas as parcelas estão pagas
        if parcelas_pagas == total_parcelas:
            return {'status': 'pago', 'display': 'Pago'}
        
        # Se algumas parcelas estão pagas
        if parcelas_pagas > 0:
            return {'status': 'parcial', 'display': f'Parcial ({parcelas_pagas}/{total_parcelas})'}
        
        # Se nenhuma parcela foi paga
        return {'status': 'pendente', 'display': 'Pendente'}
    
    def get_valor_recebido(self):
        """Retorna o valor efetivamente recebido (apenas parcelas pagas)"""
        from decimal import Decimal
        total_recebido = Decimal('0.00')
        
        for pagamento in self.pagamentos.all():
            parcelas = pagamento.parcelas_detalhes.all()
            
            # Se não tem parcelas registradas, considera tudo pago (vendas antigas)
            if not parcelas.exists():
                total_recebido += pagamento.valor
            else:
                # Soma apenas as parcelas que foram pagas
                parcelas_pagas = parcelas.filter(status='pago')
                for parcela in parcelas_pagas:
                    total_recebido += parcela.valor
        
        return total_recebido

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
    parcelas = models.IntegerField(default=1, help_text="Número de parcelas (1 = à vista)")

    def __str__(self):
        if self.parcelas > 1:
            return f"{self.get_tipo_display()} - R$ {self.valor} ({self.parcelas}x)"
        return f"{self.get_tipo_display()} - R$ {self.valor}"


class Parcela(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
    ]
    
    pagamento = models.ForeignKey(Pagamento, on_delete=models.CASCADE, related_name='parcelas_detalhes')
    numero = models.IntegerField(help_text="Número da parcela")
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_vencimento = models.DateField(null=True, blank=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    usuario_baixa = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['numero']
        unique_together = ['pagamento', 'numero']
    
    def __str__(self):
        return f"Parcela {self.numero}/{self.pagamento.parcelas} - R$ {self.valor} ({self.status})"
