from django import forms

class MovimentoEstoqueForm(forms.Form):
    produto_id = forms.IntegerField()
    quantidade = forms.IntegerField()
