from django import template

register = template.Library()

@register.filter
def get_item(caja_estatus, caja_id):
    return caja_estatus.get(caja_id, 'Sin definición')

