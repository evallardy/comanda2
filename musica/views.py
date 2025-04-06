from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import time
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import get_object_or_404, render
from django.http import Http404

from django.views.generic import ListView
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
import qrcode
import base64
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from uuid import UUID

from pedido.models import DiaContable
from .models import Cancion
from .forms import CancionesForm

class SolicitarMusicaView(LoginRequiredMixin, View):
    def get(self, request, token):
        try:
            token_uuid = token.hex  # Convierte el string en UUID
            dia_contable = get_object_or_404(DiaContable, token=token, estatus=1)
            form = CancionesForm()
            canciones = Cancion.objects.filter(estatus='NO', dia_contable=dia_contable)
            return render(request, 'musica/solicitar_musica.html', {'form': form, 'canciones': canciones})
        except ValueError:
            raise Http404("Token inválido")

    def post(self, request, token):
        dia_contable = get_object_or_404(DiaContable, estatus=1)
        form = CancionesForm(request.POST)

        if form.is_valid():
            cancion = form.save(commit=False)
            cancion.dia_contable = dia_contable
            cancion.save()
            Registrada='Registrada'
            return redirect(f"{reverse('solicitar_musica', kwargs={'token': token})}?mensaje=Registrada")

        return render(request, 'musica/solicitar_musica.html', {'form': form, 'dia_contable': dia_contable})
    
class Solicitar1MusicaView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            dia_contable = get_object_or_404(DiaContable, estatus=1)
            form = CancionesForm()
            canciones = Cancion.objects.filter(estatus='NO', dia_contable=dia_contable)
            return render(request, 'musica/solicitar1_musica.html', {'form': form, 'canciones': canciones})
        except ValueError:
            raise Http404("Token inválido")

    def post(self, request, token):
        dia_contable = get_object_or_404(DiaContable, estatus=1)
        form = CancionesForm(request.POST)

        if form.is_valid():
            cancion = form.save(commit=False)
            cancion.dia_contable = dia_contable
            cancion.save()
            Registrada='Registrada'
            return redirect(f"{reverse('solicitar_musica', kwargs={'token': token})}?mensaje=Registrada")

        return render(request, 'musica/solicitar1_musica.html', {'form': form, 'dia_contable': dia_contable})

client_id = settings.CLIENT_ID
client_secret = settings.CLIENT_SECRET
redirect_uri = settings.REDIRECT_URI

scope = 'playlist-modify-public playlist-modify-private'

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
)
#     cache_path='.spotify_cache'

@login_required
def spotify_callback(request):
    code = request.GET.get('code')
    if code:
        token_info = sp_oauth.get_access_token(code)
        request.session['spotify_token'] = token_info['access_token']
        return redirect(reverse_lazy("musica"))
    else:
        pass
        return redirect(reverse_lazy("musica"))

@login_required
def cambiar_estatus_cancion(request, id):
    cancion = get_object_or_404(Cancion, id=id)

    if cancion.estatus == 'NO':

#        request.session.pop('spotify_token', None)

        token = request.session.get('spotify_token')

        if not token:
            return redirect(sp_oauth.get_authorize_url())

        # Intentar refrescar el token si es inválido
        token_info = sp_oauth.get_cached_token()
#        if not token_info or token_info['expires_at'] < time.time():
#            token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
#            request.session['spotify_token'] = token_info['access_token']
#            token = request.session.get('spotify_token')

        sp = spotipy.Spotify(auth=token)

        playlist_id = settings.PLAYLIST_ID
        
        try:
            # ✅ Pasar directamente el valor de la URI
            sp.playlist_add_items(playlist_id, [cancion.uri])

            cancion.estatus = 'SI'
            cancion.save(update_fields=['estatus'])

            dia_contable = get_object_or_404(DiaContable, estatus=1)
            canciones = Cancion.objects.filter(
                dia_contable=dia_contable,
                estatus='NO'
            ).order_by('fecha_solicitud')

            return render(request, 'musica/lista_canciones.html', {'canciones': canciones})
        
        except spotipy.exceptions.SpotifyException as e:
            return render(request, 'musica/lista_canciones.html', {'error': f"Error en Spotify: {e}"})
        except Exception as e:
            return render(request, 'musica/lista_canciones.html', {'error': f"Error inesperado: {e}"})
    else:
        dia_contable = get_object_or_404(DiaContable, estatus=1)
        canciones = Cancion.objects.filter(
            dia_contable=dia_contable,
            estatus='NO'
        ).order_by('fecha_solicitud')

        return render(request, 'musica/lista_canciones.html', {'canciones': canciones})

@login_required
def ponEnLista(request, uri, artistas, nombre, album):

    dia_contable = DiaContable.objects.filter(estatus=1).first()
    
    cancion = Cancion.objects.create (
        dia_contable = dia_contable,
        uri = uri,
        artista = artistas,
        titulo = nombre,
        album = album,
    )

    return JsonResponse({'respuesta': "OK"})

@login_required
def listaCancionesTodas(request, autor, cancion):

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

    encontro = False

    busqueda = str(autor) + " / " + str(cancion)

    result = sp.search(autor)

    canciones = []
    for i in range(0, len(result["tracks"]["items"])):
        musica = str(result["tracks"]["items"][i]["name"]).upper()
        musica1 = str(cancion).upper()
        if musica1 in musica:
            encontro = True
            canciones.append({
                "artista": result["tracks"]["items"][i]["artists"],
                "album": result["tracks"]["items"][i]["album"]["name"],
                "nombre": result["tracks"]["items"][i]["name"],
                'uri': result["tracks"]["items"][i]["uri"],
                })

    return JsonResponse({'canciones': canciones, 'encontro': encontro,})

@login_required
def listaCancionesAutor(request, autor):

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

    encontro = False
    result = sp.search(autor)
    canciones = []
    for i in range(0, len(result["tracks"]["items"])):
        encontro = True
        canciones.append({
            "artista": result["tracks"]["items"][i]["artists"],
            "album": result["tracks"]["items"][i]["album"]["name"],
            "nombre": result["tracks"]["items"][i]["name"],
            'uri': result["tracks"]["items"][i]["uri"],
        })

    return JsonResponse({'canciones': canciones, 'encontro': encontro,})

@login_required
def listaCanciones(request, cancion):

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))

    encontro = False
    result = sp.search(cancion)
    canciones = []
    for i in range(0, len(result["tracks"]["items"])):
        encontro = True
        canciones.append({
            "artista": result["tracks"]["items"][i]["artists"],
            "album": result["tracks"]["items"][i]["album"]["name"],
            "nombre": result["tracks"]["items"][i]["name"],
            'uri': result["tracks"]["items"][i]["uri"],
            })

    return JsonResponse({'canciones': canciones, 'encontro': encontro,})

class PresentaQRView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Obtener el curso por pk
        dia_contable = get_object_or_404(DiaContable, estatus=1)

        # Genera el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f'{settings.SITE_URL}/musica/solicitar/{dia_contable.token}/'  # URL del curso
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill='black', back_color='white')

        # Guarda la imagen en un objeto BytesIO
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Codifica la imagen a base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        img_url = f"data:image/png;base64,{img_base64}"

        return render(request, 'musica/mostrar_qr.html', {
            'qr_url': img_url
        })

    def post(self, request, *args, **kwargs):
        # Obtener el curso por pk
        curso = get_object_or_404(Curso, pk=kwargs['pk'])
        
        # Crear el formulario con los datos enviados
        form = CorreoForm(request.POST)

        if form.is_valid():
            # Obtener los datos del formulario
            destinatario = form.cleaned_data['destinatario']
            asunto = form.cleaned_data['asunto']
            contenido = form.cleaned_data['contenido']

            # Generar el código QR nuevamente
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f'https://descapa.iagmexico.com/core/asistentes/registrar/{curso.pk}/'  # URL del curso
#            qr_data = f'//localhost:8000/core/asistentes/registrar/{curso.pk}/'  # URL del curso
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill='black', back_color='white')

            # Guarda la imagen en un objeto BytesIO
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Codifica la imagen a base64
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
            img_url = f"data:image/png;base64,{img_base64}"

            # Preparar el correo
            # from_email = settings.EMAIL_HOST_USER
            from_email = 'soporte@iagmexico.com'
            recipient_list = [destinatario]  # Usar el correo proporcionado por el usuario

            # Crear el mensaje del correo
            email = EmailMessage(
                asunto,  # Asunto
                contenido,  # Contenido
                from_email,  # De quien lo envia
                recipient_list,  # Destinatarios
            )

            # Adjuntar la imagen del QR al correo
            email.attach(
                f"qr_curso_{curso.pk}.png",  # Nombre del archivo
                img_io.getvalue(),  # Imagen en formato binario
                "image/png"  # Tipo de contenido
            )

            # Enviar el correo
            try:
                email.send()
#                messages.success(request, "Correo enviado correctamente.")
                respuesta = 'Correo enviado correctamente'
            except Exception as e:
#                messages.error(request, f"Error al enviar el correo: {str(e)}")
                respuesta = f"Error al enviar el correo: {str(e)}"

            # Redirigir a la página de éxito o mostrar mensaje
            return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
                'form': form,
                'curso': curso,
                'qr_url': img_url,
                'respuesta': respuesta,
            })
        
        # Si el formulario no es válido, volver a mostrar el formulario con errores
        return render(request, 'core/asistentes/asistente_enviar_qr_form.html', {
            'form': form,
            'curso': curso,
            'qr_url': img_url
        })

class ListaCancionesView(LoginRequiredMixin, ListView):
    model = Cancion
    template_name = 'musica/lista_canciones.html'
    context_object_name = 'canciones'

    def get_queryset(self):
        token = self.kwargs.get("token")
        dia_contable = get_object_or_404(DiaContable, estatus=1)
        return Cancion.objects.filter(dia_contable=dia_contable, estatus='NO').order_by('fecha_solicitud')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = self.kwargs.get("token")
        return context

