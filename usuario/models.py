from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

ES_CLIENTE = (
    (False, 'No'),
    (True, 'Si'),
)

class Usuario(AbstractUser):
    celular = models.CharField(max_length=20, blank=True, null=True)
    cliente = models.BooleanField('Cliente', choices=ES_CLIENTE, default=False)
    
    class Meta:
        db_table = 'Usuario'
        permissions = (
            ('cocina', 'Consulta cocina'),
            ('bar', 'Consulta bar'),
            ('servicio', 'Solicitudes comanda'),
            ('entregas', 'Consulta entregas'),
            ('consultas_seguimiento', 'Consulta de seguimiento'),
            ('consulta_comandas', 'Consulta comandas'),
            ('consulta_servicios', 'Consulta de servicios'),
            ('catalogo', 'Consulta catálogo'),
            ('accesos', 'Consulta accesos'),
            ('abrir', 'Día abre'),
            ('cerrar', 'Día cierra'), 
            ('usuarios', 'Consulta usuarios'),
            ('caja', 'Pago de comandas'),
            ('presenta', 'Muestra QR para música'),
            ('musica', 'Lista de complacencias'),
        )

