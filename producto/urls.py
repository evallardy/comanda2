from django.urls import path

from .views import *

urlpatterns = [
    
    # Productos
    path('catalogo/', catalogo, name='catalogo'),

    # Modelo grupo
    path('grupos/', GrupoListView.as_view(), name='grupos'),
    path('grupos/nuevo/', GrupoCreateView.as_view(), name='grupo_create'),
    path('grupos/editar/<int:pk>/', GrupoUpdateView.as_view(), name='grupo_update'),
    path('grupos/eliminar/<int:pk>/', GrupoDeleteView.as_view(), name='grupo_delete'),

    # Insumos
    path('insumos/', InsumoListView.as_view(), name='insumos'),
    path('insumos/nuevo/', InsumoCreateView.as_view(), name='insumo_create'),
    path('insumos/editar/<int:pk>/', InsumoUpdateView.as_view(), name='insumo_update'),
    path('insumos/eliminar/<int:pk>/', InsumoDeleteView.as_view(), name='insumo_delete'),
    
    # Productos
    path('productos/', ProductoListView.as_view(), name='productos'),
    path('producto/nuevo/', ProductoCreateView.as_view(), name='producto_create'),
    path('producto/editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto_update'),
    path('producto/eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='producto_delete'),
    path('producto/guardar_insumos_en_sesion/', GuardarInsumosSesionView.as_view(), name='guardar_insumos_en_sesion'),

    # Paquetes
    path('paquetes/', PaqueteListView.as_view(), name='paquetes'),
    path('paquete/nuevo/', PaqueteCreateView.as_view(), name='paquete_create'),
    path('paquete/editar/<int:pk>/', PaqueteUpdateView.as_view(), name='paquete_update'),
    path('paquete/eliminar/<int:pk>/', PaqueteDeleteView.as_view(), name='paquete_delete'),
    path('paquete/guardar_productos_en_sesion/', GuardarProdutosSesionView.as_view(), name='guardar_productos_en_sesion'),

]
