# feira_app/forms.py
from django import forms

class AddToListForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'style': 'width: 70px; display: inline-block; margin-right: 10px;'}))
    # produto_id será passado pela URL ou como um campo oculto se necessário

class UpdateListItemForm(forms.Form):
    quantidade = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'style': 'width: 70px;'}))
