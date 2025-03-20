from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from core.views import *
from musica.views import spotify_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('', index, name='principal'),
    path('core/', include('core.urls')),
    path('musica/', include('musica.urls')),
    path('producto/', include('producto.urls')),
    path('pedido/', include('pedido.urls')),
    path('usuario/', include('usuario.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('callback/', spotify_callback, name='spotify_callback'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
