from django import forms
from django.core.exceptions import ValidationError
from .models import Grupo, Insumo, Producto, Paquete

class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nombre', 'estatus']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del grupo'}),
            'estatus': forms.Select(attrs={'class': 'form-control'}),
        }

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['grupo', 'nombre', 'venta', 'precio', 'estatus', 'imagen',]
        widgets = {
            'grupo': forms.Select(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'venta': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'estatus': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'breve', 'tipo', 'precio', 'imagen', 'estatus']  # Excluir 'imagen' si no es necesario
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'breve': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'estatus': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PaqueteForm(forms.ModelForm):
    class Meta:
        model = Paquete
        fields = ['nombre', 'descripcion', 'tipo_paquete', 'precio', 'imagen', 'fecha_inicio', 'fecha_fin', 'estatus']  # Excluir 'imagen' si no es necesario
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_paquete': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'estatus': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_paquete = cleaned_data.get("tipo_paquete")
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        # Validar que las fechas sean requeridas solo si tipo_paquete es 2
        if tipo_paquete == 2:  # Ajusta el valor según cómo se almacena 'tipo_paquete' (puede ser un número)
            if not fecha_inicio or not fecha_fin:
                raise ValidationError("Las fechas de inicio y fin son obligatorias cuando el tipo de paquete es Promoción.")
            if fecha_inicio >= fecha_fin:
                raise ValidationError("La fecha de inicio debe ser menor que la fecha de fin.")
        
        return cleaned_data