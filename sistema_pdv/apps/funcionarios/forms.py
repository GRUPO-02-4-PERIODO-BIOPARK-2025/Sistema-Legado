from django import forms
from django.core.exceptions import ValidationError
from .models import Funcionario
import re


class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            'nome', 'email', 'telefone', 'cpf', 'rg',
            'cargo', 'departamento', 'salario', 'data_admissao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Nome completo do funcionário'}),
            'email': forms.EmailInput(attrs={'placeholder': 'nome@provedor.com'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(99) 99999-9999'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'placeholder': 'Número do RG'}),
            'cargo': forms.TextInput(attrs={'placeholder': 'Ex: Vendedor, Gerente, etc.'}),
            'departamento': forms.TextInput(attrs={'placeholder': 'Ex: Vendas, Administrativo, etc.'}),
            'salario': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'data_admissao': forms.DateInput(attrs={'placeholder': 'dd/mm/aaaa', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cpf'].required = True

    def clean_cpf(self):
        value = self.cleaned_data.get('cpf', '')
        digits = re.sub(r"\D", "", value or "")
        if not digits:
            raise ValidationError('CPF é obrigatório.')
        if len(digits) != 11:
            raise ValidationError('CPF deve ter 11 dígitos.')
        return value

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email:
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, email):
                raise ValidationError('E-mail inválido. Verifique o formato.')
        return email
