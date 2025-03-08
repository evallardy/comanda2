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

    path('pedido/comanda/', ComandaView.as_view(), name='comanda'),
    path('servicios/', ServicioListView.as_view(), name='servicios'),

    path('caja/', CajaListView.as_view(), name='caja'),
    path('caja/pagar/', pagar_caja, name='pagar_caja'),
    path('guardar_pago/', guardar_pago, name='guardar_pago'),
    path('comandas/', ComandasView.as_view(), name='comandas'),

    path('usuario/', DetalleListView.as_view(), name='usuario'),
    path('accesos/', DetalleListView.as_view(), name='accesos'),
    path('cierre/', CierreView.as_view(), name='cierre'),
    path('apertura/', DetalleListView.as_view(), name='apertura'),

]
