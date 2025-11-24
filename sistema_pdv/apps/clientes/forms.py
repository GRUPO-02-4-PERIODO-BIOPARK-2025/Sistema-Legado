from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente
import re
import urllib.request
import json


class ClienteForm(forms.ModelForm):

    class Meta:
        model = Cliente
        fields = [
            'nome',
            'email',
            'telefone',
            'tipo_documento',
            'numero_documento',
            'endereco',
            'cidade',
            'estado',
            'cep'
        ]

        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Digite o nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'email@exemplo.com'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(11) 99999-9999'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_documento': forms.TextInput(attrs={
                'placeholder': '000.000.000-00 ou 00.000.000/0001-00'
            }),
            'endereco': forms.TextInput(attrs={
                'placeholder': 'Rua, número, bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'placeholder': 'Nome da cidade'
            }),
            'estado': forms.TextInput(attrs={
                'placeholder': 'UF'
            }),
            'cep': forms.TextInput(attrs={
                'placeholder': '00000-000'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        campos_obrigatorios = ['nome', 'telefone', 'numero_documento']

        for campo in campos_obrigatorios:
            self.fields[campo].required = True

    def clean_numero_documento(self):
        value = self.cleaned_data.get('numero_documento', '')
        tipo = self.cleaned_data.get('tipo_documento')

        digits = re.sub(r"\D", "", value)

        if not digits:
            raise ValidationError("Número do documento é obrigatório.")

        if tipo == 'CPF' and len(digits) != 11:
            raise ValidationError("CPF deve conter 11 dígitos.")

        if tipo == 'CNPJ' and len(digits) != 14:
            raise ValidationError("CNPJ deve conter 14 dígitos.")

        if tipo not in ['CPF', 'CNPJ']:
            if len(digits) not in [11, 14]:
                raise ValidationError("Documento inválido. Informe CPF ou CNPJ.")

        return value

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '')

        if not cep:
            return cep

        digits = re.sub(r"\D", "", cep)

        if len(digits) != 8:
            raise ValidationError("CEP inválido. Deve conter 8 dígitos.")

        try:
            url = f"https://viacep.com.br/ws/{digits}/json/"
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read().decode())

                if data.get('erro'):
                    raise Exception()

                logradouro = data.get('logradouro', '')
                bairro = data.get('bairro', '')
                cidade = data.get('localidade', '')
                uf = data.get('uf', '')

                endereco = ', '.join(filter(None, [logradouro, bairro]))

                if endereco:
                    self.cleaned_data['endereco'] = endereco
                if cidade:
                    self.cleaned_data['cidade'] = cidade
                if uf:
                    self.cleaned_data['estado'] = uf

        except Exception:
            raise ValidationError("Erro ao buscar CEP. Preencha manualmente.")

        return cep
