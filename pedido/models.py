import uuid
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import models
from django.utils import timezone

from producto.models import Producto
from usuario.models import Usuario
from producto.models import TIPO_PRODUCTO

ACTIVO_CAJA = (
    (0, 'Cancelado'),
    (1, 'Por pagar'),
    (2, 'Pagado'),
)
ACTIVA_COMANDA = (
    (0, 'Cancelado'),
    (1, 'Activa'),
    (2, 'Pre-pagada'),
    (3, 'Cerrada'),
    (4, 'Cerrada sin pagar'),
)
ACTIVO_DETALLE = (
    (0, 'Cancelado'),
    (1, 'Solicitado'),
    (2, 'Elaborado'),
    (3, 'Entregado'),
    (4, 'Cancelado elaborado'),
    (5, 'Cancelado difinitivo'),
)
ACTIVO_PAGO = (
    (0, 'Cancelado'),
    (1, 'Pagado'),
)
ACTIVO_PROMOCION = (
    (0, 'No presentar'),
    (1, 'Presentar'),
)
ESTADO_DIA = (
    (0, 'Cancelado'),
    (1, 'Activo'),
    (2, 'Cerrado'),
)

class DiaContable(models.Model):
    estatus = models.IntegerField("Estatus", choices=ESTADO_DIA, default=1)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        verbose_name = 'Día contable'
        verbose_name_plural = 'Días contable'
        ordering = ['-fecha_alta',]
        db_table = 'DiaContable'

class Comanda(models.Model):
    mesa = models.CharField("Mesa", max_length=255, null=True, blank=True)
    observacion = models.CharField("Observación", max_length=255, null=True, blank=True)
    dia_contable = models.ForeignKey(DiaContable, on_delete=models.CASCADE, related_name="DiaContable")
    estatus = models.IntegerField("Estatus", choices=ACTIVA_COMANDA, default=1)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    class Meta:
        verbose_name = 'Comanda'
        verbose_name_plural = 'Comandas'
        ordering = ['-dia_contable', '-fecha_alta',]
        db_table = 'Comanda'

    def __str__(self):
        return ' %s / %s' % (self.mesa, self.observacion)

class Servicio(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, related_name="ComandaServicio")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="UsuarioServicio", null=True, blank=True)
    actividad = models.CharField("Actividad", max_length=255)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        ordering = ['comanda', '-fecha_alta',]
        db_table = 'Servicio'

    def __str__(self):
        return ' %s, %s, %s' % (self.comanda, self.usuario)

class Caja(models.Model, PermissionRequiredMixin):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, verbose_name="Comanda")
    caja_grupo = models.ForeignKey('Pago', on_delete=models.CASCADE, verbose_name="Pago_grupo", null=True, blank=True)
    descripcion = models.CharField("Tipo", max_length=255) # Producto, Paquete o Insumo
    especifico = models.CharField("Descripción", max_length=255, null=True, blank=True) # Nombre del anterior campo
    cantidad = models.IntegerField("Cantidad", default=1)
    precio_unitario = models.DecimalField("Precio unitario", max_digits=10, decimal_places=2, default=0)
    importe = models.DecimalField("Importe", max_digits=10, decimal_places=2, default=0)
    estatus = models.IntegerField("Estatus", choices=ACTIVO_CAJA, default=1)
    descripcion_cancela = models.CharField("Cancelación por", max_length=255, null=True, blank=True)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    class Meta:
        verbose_name = 'Operación'
        verbose_name_plural = 'Operaciones'
        ordering = ['comanda','-fecha_alta',]
        db_table = 'Caja'

    def __str__(self):
        return ' %s, %s, %s, %s' % (self.comanda, self.descripcion, self.importe, dict(ACTIVO_CAJA).get(self.estatus))

class Pago(models.Model, PermissionRequiredMixin):
    importe_efectivo = models.DecimalField("Importe", max_digits=10, decimal_places=2, default=0)
    importe_tarjeta = models.DecimalField("Importe", max_digits=10, decimal_places=2, default=0)
    importe_transferencia = models.DecimalField("Importe", max_digits=10, decimal_places=2, default=0)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="UsuarioPago", null=True, blank=True)
    estatus = models.IntegerField("Estatus", choices=ACTIVO_PAGO, default=1)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_alta',]
        db_table = 'Pago'

    def __str__(self):
        return ' %s, %s, %s, %s' % (self.fecha_modificacion, dict(ACTIVO_PAGO).get(self.estatus))

class Detalle(models.Model, PermissionRequiredMixin):
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE, verbose_name="Caja")
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE, verbose_name="ComandaDetalle")
    tipo = models.IntegerField("Tipo", choices=TIPO_PRODUCTO, default=1)
    producto = models.CharField("Producto", max_length=255, null=True, blank=True)
    especificacion = models.CharField("Detalle", max_length=255, null=True, blank=True)
    nota = models.CharField("Observación", max_length=255)
    cantidad = models.IntegerField("Cantidad", default=1)
    estatus = models.IntegerField("Estatus", choices=ACTIVO_DETALLE, default=1)
    fecha_modificacion = models.DateTimeField("Fecha modificación", auto_now=True)
    fecha_alta = models.DateTimeField("Fecha alta", auto_now_add=True)

    class Meta:
        verbose_name = 'Detalle'
        verbose_name_plural = 'Detalles'
        ordering = ['-fecha_alta',]
        db_table = 'Detalle'

    def __str__(self):
        return ' %s, %s, %s, %s' % (self.comanda, self.fecha_alta, dict(ACTIVO_DETALLE).get(self.estatus))
