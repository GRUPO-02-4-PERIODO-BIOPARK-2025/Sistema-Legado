"""Modelo para Notificações"""
from django.db import models
from django.contrib.auth.models import User


class StockThreshold(models.Model): # TODO: deve ser definido na tela de cadastro do produto qnd implementada
    """Limites de estoque mínimo para produtos"""
    produto = models.OneToOneField(
        'produtos.Produto',
        on_delete=models.CASCADE,
        related_name='threshold'
    )
    quantidade_minima = models.IntegerField(
        default=10,
        help_text='Quantidade mínima antes de gerar alerta'
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock_thresholds'
        verbose_name = 'Limite de Estoque'
        verbose_name_plural = 'Limites de Estoque'

    def __str__(self):
        return f"{self.produto.nome} - Min: {self.quantidade_minima}"


class Notification(models.Model):
    """Notificações de estoque baixo"""
    TIPO_CHOICES = [
        ('low_stock', 'Estoque Baixo'),
        ('out_of_stock', 'Sem Estoque'),
        ('critical', 'Crítico'),
    ]

    PRIORIDADE_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]

    produto = models.ForeignKey(
        'produtos.Produto',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='low_stock')
    prioridade = models.CharField(max_length=10, choices=PRIORIDADE_CHOICES, default='medium')
    titulo = models.CharField(max_length=255)
    mensagem = models.TextField()
    quantidade_atual = models.IntegerField()
    quantidade_minima = models.IntegerField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    lida_em = models.DateTimeField(null=True, blank=True)
    lida_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_read'
    )

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['lida', '-criado_em']),
            models.Index(fields=['produto', '-criado_em']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.produto.nome}"

    def marcar_como_lida(self, usuario=None):
        """Marca a notificação como lida"""
        from django.utils import timezone
        self.lida = True
        self.lida_em = timezone.now()
        if usuario:
            self.lida_por = usuario
        self.save()
