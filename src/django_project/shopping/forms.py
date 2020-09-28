from django import forms

class ShoppingListForm(forms.Form):
    shopping_list = forms.CharField(label='Shopping list', max_length=1000)