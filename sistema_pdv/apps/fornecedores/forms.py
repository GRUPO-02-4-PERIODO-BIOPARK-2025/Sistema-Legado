from django import forms

class FornecedorForm(forms.Form):
    nome = forms.CharField(max_length=255)
    telefone = forms.CharField(max_length=50, required=False)
