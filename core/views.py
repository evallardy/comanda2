from django.shortcuts import render
from django.shortcuts import get_object_or_404
import unicodedata

from pedido.models import DiaContable

# Create your views here.

def minus(text):
    # Eliminar acentos y convertir a minúsculas
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join([c for c in normalized_text if unicodedata.category(c) != 'Mn']).lower()

def index(request):
    template_name = 'core/index.html'

    if DiaContable.objects.filter(estatus=1).first():
        activo = True
    else:
        activo = False

    opciones_menus = ['Comanda', 'Bar',  'Cocina', 'Caja', 'Entregas', 'Consulta', 'Comandas', 'Servicios', 'Catálogo', 
        'Usuarios', 'Accesos', 'Cierre', 'Presenta', 'Musica']  # Lista en lugar de set

    # Crear la estructura JSON correcta
    menus_json = [{"opcion": p,
                    "liga": minus(p)
                    }
                    for p in opciones_menus]

    return render(request, template_name, {'menus': menus_json, "activo": activo,})  # Pasar como diccionario

