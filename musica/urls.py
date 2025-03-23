from django.urls import path
from .views import (
    SolicitarMusicaView, PresentaQRView, ListaCancionesView, cambiar_estatus_cancion, listaCancionesTodas,
    listaCancionesAutor, listaCanciones, ponEnLista, spotify_callback, Solicitar1MusicaView
    )

urlpatterns = [
    path('solicitar/<uuid:token>/', SolicitarMusicaView.as_view(), name='solicitar_musica'),
    path('solicitar/', Solicitar1MusicaView.as_view(), name='complace'),
    path('presenta_qr/', PresentaQRView.as_view(), name='presenta'),
    
    path('lista/', ListaCancionesView.as_view(), name='musica'),
    path('cambiar_estatus/<int:id>/', cambiar_estatus_cancion, name='cambiar_estatus_cancion'),
    path('listaCancionesTodas/<str:autor>/<str:cancion>/', listaCancionesTodas, name='listaCanciones'),
    path('listaCancionesAutor/<str:autor>/', listaCancionesAutor, name='listaCanciones'),
    path('listaCanciones/<str:cancion>/', listaCanciones, name='listaCanciones'),
    path('ponEnLista/<str:uri>/<str:artistas>/<str:nombre>/<str:album>/', ponEnLista, name='ponEnLista'),

]