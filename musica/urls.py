from django.urls import path
from .views import SolicitarMusicaView, PresentaQRView, ListaCancionesView, cambiar_estatus_cancion

urlpatterns = [
    path('solicitar/<uuid:token>/', SolicitarMusicaView.as_view(), name='solicitar_musica'),
    path('presenta_qr/', PresentaQRView.as_view(), name='presenta'),
    
    path('lista/', ListaCancionesView.as_view(), name='musica'),
    path('cambiar_estatus/<int:id>/', cambiar_estatus_cancion, name='cambiar_estatus_cancion'),

]