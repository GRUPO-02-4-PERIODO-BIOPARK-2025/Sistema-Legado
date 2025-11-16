from django import forms
from django.core.exceptions import ValidationError
from .models import Fornecedor
import re
import urllib.request
import json


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'nome', 'nome_fantasia', 'cnpj', 'inscricao_estadual',
            'categoria', 'endereco', 'cidade', 'estado', 'cep',
            'telefone', 'celular', 'email'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome da empresa'}),
            'nome_fantasia': forms.TextInput(attrs={'placeholder': 'Nome fantasia'}),
            'cnpj': forms.TextInput(attrs={'placeholder': 'CNPJ ou CPF - ex: 00.000.000/0001-00 ou 000.000.000-00'}),
            'inscricao_estadual': forms.TextInput(attrs={'placeholder': 'Inscrição estadual'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Rua, número, bairro'}),
            'cidade': forms.TextInput(attrs={'placeholder': 'Nome da cidade'}),
            'estado': forms.TextInput(attrs={'placeholder': 'UF'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(99) 99999-9999'}),
            'celular': forms.TextInput(attrs={'placeholder': '(99) 99999-9999'}),
            'email': forms.EmailInput(attrs={'placeholder': 'nome@provedor.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields required on the form level as requested
        for f in ('cnpj', 'cidade', 'estado', 'cep'):
            if f in self.fields:
                self.fields[f].required = True

    def clean_cnpj(self):
        value = self.cleaned_data.get('cnpj', '')
        # remove non-digits
        digits = re.sub(r"\D", "", value or "")
        if not digits:
            raise ValidationError('CNPJ/CPF é obrigatório.')
        if len(digits) not in (11, 14):
            raise ValidationError('CNPJ deve ter 14 dígitos ou CPF 11 dígitos (somente números).')
        # keep formatted as entered but you may store digits only if preferred
        return value

    def clean_cep(self):
        cep = self.cleaned_data.get('cep', '')
        digits = re.sub(r"\D", "", cep or "")
        if not digits:
            raise ValidationError('CEP é obrigatório.')
        if len(digits) != 8:
            raise ValidationError('CEP inválido. Deve conter 8 dígitos.')

        # Lookup via ViaCEP to populate address fields when possible
        try:
            url = f"https://viacep.com.br/ws/{digits}/json/"
            with urllib.request.urlopen(url, timeout=5) as resp:
                body = resp.read()
                data = json.loads(body.decode('utf-8'))
                if data.get('erro'):
                    raise Exception('CEP não encontrado')
                # Compose endereco if available
                logradouro = data.get('logradouro') or ''
                bairro = data.get('bairro') or ''
                localidade = data.get('localidade') or ''
                uf = data.get('uf') or ''
                endereco = ', '.join(p for p in (logradouro, bairro) if p).strip()
                # Populate cleaned_data so form will show these values
                if endereco:
                    self.cleaned_data['endereco'] = endereco
                if localidade and not self.cleaned_data.get('cidade'):
                    self.cleaned_data['cidade'] = localidade
                if uf and not self.cleaned_data.get('estado'):
                    self.cleaned_data['estado'] = uf
        except Exception:
            # If lookup fails, allow manual input but do not silently overwrite
            raise ValidationError('Não foi possível buscar endereço para esse CEP. Verifique o CEP ou preencha manualmente.')

        return cep

