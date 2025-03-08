from django.views.generic import ListView
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
import qrcode
import base64
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from uuid import UUID
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from pedido.models import DiaContable
from .models import Cancion
from .forms import CancionesForm

class SolicitarMusicaView(View):
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

class PresentaQRView(LoginRequiredMixin,View):
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

class ListaCancionesView(ListView):
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

def cambiar_estatus_cancion(request, id):
    cancion = get_object_or_404(Cancion, id=id)
    cancion.estatus = 'SI'
    cancion.save()
    dia_contable = get_object_or_404(DiaContable, estatus=1)
    canciones = Cancion.objects.filter(dia_contable=dia_contable, estatus='NO').order_by('fecha_solicitud')
    return render(request, 'musica/lista_canciones.html', {'canciones': canciones})