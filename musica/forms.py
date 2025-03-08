from django import forms
from .models import Cancion

class CancionesForm(forms.ModelForm):
    class Meta:
        model = Cancion
        fields = ['titulo', 'artista']
