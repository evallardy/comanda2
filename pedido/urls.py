from django.urls import path

from .views import *

urlpatterns = [

    path('lista/<int:opcion>/', DetalleListView.as_view(), name='accion'),
    path('atender/<int:pk>/<int:opcion>/', DetalleAtenderView.as_view(), name='detalle_atender'),
    path('cancelar/<int:pk>/<int:opcion>/', DetalleCancelarView.as_view(), name='detalle_cancelar'),


    path('pedido/comanda/', ComandaView.as_view(), name='comanda'),
    path('pedido/productos_paquete/<int:paquete_id>/', obtener_productos_paquete, name='productos_paquete'),
    path('pedido/agregar_carrito/', agregar_al_carrito, name='agregar_carrito'),
    path("guardar/", guardar_datos, name="guardar_datos"),
    path("api/comandas/", obtener_comandas, name="obtener_comandas"),
    path("actualizar_sesion/", actualizar_sesion, name="actualizar_sesion"),

    path('pedido/comanda/', ComandaView.as_view(), name='comanda'),
    path('servicios/', ServicioListView.as_view(), name='servicios'),

    path('caja/', CajaListView.as_view(), name='caja'),
    path('caja/pagar/', pagar_caja, name='pagar_caja'),
    path('guardar_pago/', guardar_pago, name='guardar_pago'),
    path('caja/global/', CajaReporteView.as_view(), name='global'),
    path('caja/cerrar_comanda/<int:id>/', cerrar_comanda, name='cerrarComanda'),

    path('comandas/', ComandasView.as_view(), name='comandas'),

    path('cierre/', CierreView.as_view(), name='cierre'),

]
