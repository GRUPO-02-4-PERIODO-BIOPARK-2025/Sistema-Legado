from django.contrib import admin
from .models import Notification, StockThreshold


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'produto', 'lida', 'criado_em']
    list_filter = ['tipo', 'lida', 'criado_em']
    search_fields = ['titulo', 'mensagem', 'produto__nome']
    readonly_fields = ['criado_em']
    date_hierarchy = 'criado_em'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('produto')


@admin.register(StockThreshold)
class StockThresholdAdmin(admin.ModelAdmin):
    list_display = ['produto', 'quantidade_minima', 'ativo', 'atualizado_em']
    list_filter = ['ativo', 'atualizado_em']
    search_fields = ['produto__nome']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('produto')
