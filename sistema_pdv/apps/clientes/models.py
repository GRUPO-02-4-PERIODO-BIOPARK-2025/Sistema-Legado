from django.db import models

class Cliente(models.Model):

    TIPO_DOCUMENTO_CHOICES = (
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
    )

    nome = models.CharField('Nome Completo', max_length=255)
    email = models.EmailField('E-mail', max_length=254, blank=True)

    telefone = models.CharField('Telefone', max_length=50)

    tipo_documento = models.CharField(
        'Tipo de Documento',
        max_length=10,
        choices=TIPO_DOCUMENTO_CHOICES,
        blank=True,
        null=True
    )

    numero_documento = models.CharField(
        'Número do Documento',
        max_length=20
    )

    endereco = models.CharField('Endereço Completo', max_length=255, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    cep = models.CharField('CEP', max_length=12, blank=True)

    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        db_table = 'clientes_cliente' 
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']

    def __str__(self):
        return self.nome
