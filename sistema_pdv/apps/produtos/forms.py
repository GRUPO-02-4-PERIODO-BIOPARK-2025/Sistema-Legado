from django import forms

class ProdutoForm(forms.Form):
    nome = forms.CharField(max_length=255)
    preco = forms.DecimalField(max_digits=10, decimal_places=2)
    estoque = forms.IntegerField(min_value=0)
