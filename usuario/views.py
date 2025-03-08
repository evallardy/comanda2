from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from usuario.models import Usuario
from .forms import UsuarioForm, UsuarioFormEdit, CambiaContrasenaForm


class usuarios(LoginRequiredMixin, ListView):
    model = Usuario
    template_name = 'usuario/usuarios.html'
    context_object_name = 'usuarios'
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = Usuario.objects.exclude(username='iagevm').exclude(username='jcamarillo')
        # Puedes realizar filtros o manipulaciones adicionales en el queryset si es necesario
        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuarios_perm'] = self.request.user.has_perm('core.usuarios')
        context['crea_usuario_perm'] = self.request.user.has_perm('core.crea_usuario')
        context['modifica_usuario_perm'] = self.request.user.has_perm('core.modifica_usuario')
        return context

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = Usuario
    form_class = UsuarioFormEdit
    template_name = 'usuario/usuario.html'
    success_url = reverse_lazy('usuarios')  # URL de éxito después de guardar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', '0')
        usuario_sel = Usuario.objects.filter(id=pk).first()
        usuario = usuario_sel.username
        context['modifica_usuario_perm'] = self.request.user.has_perm('core.modifica_usuario')
        context['usuario'] = usuario
        return context

    def post(self, request, *args, **kwargs):
        # Intentar obtener el usuario a actualizar
        user = self.get_object()  # Obtén el usuario a actualizar

        # Obtener los datos del formulario manualmente
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        celular = request.POST.get('celular')
        email = request.POST.get('email')
        cliente = request.POST.get('cliente') == 'on'  # Checkbox devuelve 'on' o None
        is_active = request.POST.get('is_active') == 'on'  # Checkbox devuelve 'on' o None
        password = request.POST.get('password')

        # Actualizar los campos del usuario en la base de datos
        Usuario.objects.filter(id=user.id).update(
            first_name=first_name,
            last_name=last_name,
            celular=celular,
            email=email,
            cliente=cliente,
            is_active=is_active,
        )

        # Actualizar la contraseña solo si se proporciona un nuevo valor
        if password:
            user.set_password(password)  # Establece la nueva contraseña
            update_session_auth_hash(request, user)  # Mantiene la sesión activa

        user.save()  # Guarda el usuario para que se aplique la nueva contraseña

        return HttpResponseRedirect(reverse('usuarios'))

@login_required
def registro(request):
    data = {
        'form': UsuarioForm
    }
    if request.method == 'POST':
        formulario = UsuarioForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            return redirect(to="usuarios")
        data["form"] = formulario
    return render(request, 'registration/registro.html', data)

class cambiar_contrasena(LoginRequiredMixin, View):
    template_name = 'usuario/cambiar_contrasena.html'
    form_class = CambiaContrasenaForm
    success_url = reverse_lazy("index")

    def get(self, request, *args, **kwargs ):
        return render(request, self.template_name, {'form': self.form_class})
    
    def post(self, request, *args, **kwargs ):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = Usuario.objects.filter(id=request.user.id)
            if user.exists(): 
                user = user.first()
                user.set_password(form.cleaned_data.get('password1'))
                user.save()
                return redirect(self.success_url)
            return redirect(self.success_url)
        else:
            form = self.form_class(request.POST)
            return render(request, self.template_name, {'form': form})
