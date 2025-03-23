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
        'Usuarios', 'Accesos', 'Cierre', 'Complace','Presenta', 'Musica']  # Lista en lugar de set

    # Crear la estructura JSON correcta
    menus_json = [{"opcion": p,
                    "liga": minus(p)
                    }
                    for p in opciones_menus]
    context = {}                    
    context['servicio_perm'] = request.user.has_perm('usuario.servicio')
    context['bar_perm'] = request.user.has_perm('usuario.bar')
    context['cocina_perm'] = request.user.has_perm('usuario.cocina')
    context['caja_perm'] = request.user.has_perm('usuario.caja')
    context['entregas_perm'] = request.user.has_perm('usuario.entregas')
    context['consultas_seguimiento_perm'] = request.user.has_perm('usuario.consultas_seguimiento')
    context['consulta_comandas_perm'] = request.user.has_perm('usuario.consulta_comandas')
    context['consulta_servicios_perm'] = request.user.has_perm('usuario.consulta_servicios')
    context['catalogo_perm'] = request.user.has_perm('usuario.catalogo')
    context['usuarios_perm'] = request.user.has_perm('usuario.usuarios')
    context['accesos_perm'] = request.user.has_perm('usuario.accesos')
    context['cierre_perm'] = request.user.has_perm('usuario.cerrar')
    context['abre_perm'] = request.user.has_perm('usuario.abrir')
    
    context['presenta_perm'] = request.user.has_perm('usuario.presenta')
    context['musica_perm'] = request.user.has_perm('usuario.musica')
    
    
    context['servicio_cierra_perm'] = request.user.has_perm('usuario.servicio_cierra')


    return render(request, template_name, {'menus': menus_json, "activo": activo, "context": context})  # Pasar como diccionario

