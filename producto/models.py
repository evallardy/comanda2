from django.db.models.functions import Coalesce
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import models
from django.db.models import Case, When, Value, CharField, F, OuterRef, Subquery, IntegerField
from django.conf import settings
import os

ACTIVO_PRODUCTO = (
    (0, 'Baja'),
    (1, 'Activo'),
)
ACTIVO_PROMOCION = (
    (0, 'No presentar'),
    (1, 'Presentar'),
)
TIPO_PAQUETE = (
    (1, 'Combo'),
    (2, 'Promoción'),
)
TIPO_PRODUCTO = (
    (1, 'Cocina'),
    (2, 'Bar'),
)
TIPO_SOLICITUD = (
    (1, 'Forzoso'),
    (2, 'Solo Uno'),
    (3, 'Opcional'),
)
SINO = (
    (0, 'NO'),
    (1, 'SI'),
)
class Grupo(models.Model, PermissionRequiredMixin):
    nombre = models.CharField("Nombre", max_length=255)
    estatus = models.IntegerField("Estatus", choices=ACTIVO_PRODUCTO, default=1)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        ordering = ['nombre']
        unique_together = ['nombre']
        db_table = 'Grupo'

    def get_estatus_text(self):
        """Devuelve el texto correspondiente al valor del estatus."""
        ESTATUS_CHOICES = dict(ACTIVO_PRODUCTO)  # Convertir las opciones de estatus a un diccionario
        return ESTATUS_CHOICES.get(self.estatus, 'Desconocido')  # Retorna el texto del estatus

    def __str__(self):
        return '%s' % (self.nombre)

class Insumo(models.Model):
    grupo = models.ForeignKey("Grupo", on_delete=models.CASCADE, related_name="insumo_grupo")
    nombre = models.CharField("Nombre", max_length=255)
    venta = models.IntegerField("Vender", choices=SINO, default=0) 
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2, default=0)
    estatus = models.IntegerField("Estatus", choices=ACTIVO_PRODUCTO, default=1)
    imagen = models.ImageField("Imagen del insumo", upload_to="insumo/", null=True, blank=True)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    def imagen_url(self):
        if self.imagen:
            return os.path.join(settings.MEDIA_URL, str(self.imagen))
        return os.path.join(settings.STATIC_URL, "img/default.png")  # Imagen por defecto

    def get_estatus_text(self):
        """Devuelve el texto correspondiente al valor del estatus."""
        ESTATUS_CHOICES = dict(ACTIVO_PRODUCTO)  # Convertir las opciones de estatus a un diccionario
        return ESTATUS_CHOICES.get(self.estatus, 'Desconocido')  # Retorna el texto del estatus
    
    class Meta:
        verbose_name = 'Insumo'
        verbose_name_plural = 'Insumos'
        ordering = ['grupo', 'nombre']
        unique_together = ['grupo', 'nombre']
        db_table = 'Insumo'

    def __str__(self):
        return f"{self.grupo.nombre} - {self.nombre}"

class Producto(models.Model, PermissionRequiredMixin):
    nombre = models.CharField("Nombre", max_length=255)
    breve = models.CharField("Breve descripción", max_length=255, null=True, blank=True)
    tipo = models.IntegerField("Tipo", choices=TIPO_PRODUCTO, default=1)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2, default=0)
    imagen = models.ImageField("Imagen prod.", upload_to="productos/", null=True, blank=True)
    estatus = models.IntegerField("Estatus", choices=ACTIVO_PRODUCTO, default=1)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['tipo','nombre',]
        unique_together = ['nombre']
        db_table = 'Producto'

    def __str__(self):
        return ' %s, %s, $ %s' % (dict(TIPO_PRODUCTO).get(self.tipo), self.nombre, self.precio)

class ProductoInsumo(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    aplica = models.IntegerField("Aplica", choices=TIPO_SOLICITUD, default=1)
    cantidad = models.IntegerField("Cantidad de insumo por producto", default=1)
    precio_unitario = models.DecimalField("Precio Unitario", max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Insumo del producto'
        verbose_name_plural = 'Insumos del producto'
        ordering = ['producto', 'insumo']
        unique_together = ('producto', 'insumo')  # Evitar duplicados de insumo-producto
        db_table = 'ProductoInsumo'

    def __str__(self):
        return f"{self.grupo.producto} - {self.insumo}"

class Paquete(models.Model, PermissionRequiredMixin): 
    nombre = models.CharField("Promoción", max_length=255)
    descripcion = models.CharField("Descripción", max_length=255, null=True, blank=True)
    tipo_paquete = models.IntegerField("Tipo", choices=TIPO_PAQUETE, default=1)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2, default=0)
    imagen = models.IntegerField("Imagen paq.", null=True, blank=True)
    estatus = models.IntegerField("Estatus", choices=ACTIVO_PRODUCTO, default=1)
    fecha_inicio = models.DateTimeField("Inicio de promocion", null=True, blank=True)
    fecha_fin = models.DateTimeField("Fin de promoción", null=True, blank=True)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    # Relación Many-to-Many con una tabla intermedia
    productos = models.ManyToManyField(Producto, through='PaqueteProducto', related_name='paquetes')

    class Meta:
        verbose_name = 'Paquete'
        verbose_name_plural = 'Paquetes'
        ordering = ['tipo_paquete', 'nombre',]
        db_table = 'Paquete'

    def __str__(self):
        return ' %s, $ %s, %s' % (self.nombre, self.precio, dict(ACTIVO_PRODUCTO).get(self.estatus))

class PaqueteProducto(models.Model):
    paquete = models.ForeignKey(Paquete, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField("Cantidad de productos en el paquete", default=1)

    class Meta:
        verbose_name = 'Producto del paquete'
        verbose_name_plural = 'Productos del Paquete'
        ordering = ['paquete', 'producto',]
        unique_together = ('paquete', 'producto')  # Evitar duplicados de producto-paquete
        db_table = 'PaqueteProducto'
