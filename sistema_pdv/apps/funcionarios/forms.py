from django import forms

class FuncionarioForm(forms.Form):
    nome = forms.CharField(max_length=255)
    cargo = forms.CharField(max_length=100, required=False)
