import uuid
from django.db import models

from pedido.models import DiaContable

PUESTA = (
    ('NO', 'NO'),
    ('SI', 'SI'),
)

class Cancion(models.Model):
    dia_contable = models.ForeignKey(DiaContable, on_delete=models.CASCADE, related_name="solicitudes")
    titulo = models.CharField("Título de la Canción", max_length=255, default='')
    artista = models.CharField("Artista", max_length=255, null=True, blank=True)
    estatus = models.CharField("Estatus", max_length=2, default='NO', choices=PUESTA)
    fecha_solicitud = models.DateTimeField("Fecha de Solicitud", auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} - {self.artista}"

    class Meta:
        verbose_name = 'Canción'
        verbose_name_plural = 'Canciones'
        ordering = ['fecha_solicitud',]
        db_table = 'Cancion'
