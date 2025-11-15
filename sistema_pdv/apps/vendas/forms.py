from django import forms

class VendaForm(forms.Form):
    cliente_id = forms.IntegerField(required=False)
    total = forms.DecimalField(max_digits=10, decimal_places=2)
