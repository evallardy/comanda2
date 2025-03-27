from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import json
from django.db.models.functions import Coalesce
from django.db.models import Case, When, Value, CharField, F, OuterRef, Subquery, IntegerField, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View

from core.views import minus
from .models import Grupo, Insumo, Producto, ProductoInsumo, Paquete, PaqueteProducto
from .forms import GrupoForm, InsumoForm, ProductoForm, PaqueteForm

# Create your views here.

@login_required
def catalogo(request):
    template_name = 'producto/catalogo.html'

    opciones_menus = ['Grupos', 'Insumos',  'Productos', 'Paquetes', 'Principal']  # Lista en lugar de set

    # Crear la estructura JSON correcta
    # Crear la estructura JSON correcta
    menus_json = [{"opcion": p,
                    "liga": minus(p)
                    }
                    for p in opciones_menus]

    return render(request, template_name, {'menus': menus_json})  # Pasar como diccionario

class GrupoListView(LoginRequiredMixin, ListView):
    model = Grupo
    template_name = 'producto/grupo/grupo_list.html'
    context_object_name = 'grupos'
    ordering = ['nombre']  # Orden predeterminado

    def get_queryset(self):
        # Obtener el valor de 'ordenar' de la URL
        ordenar = self.request.GET.get('ordenar', 'nombre')  # Por defecto ordenar por nombre

        if ordenar == 'estatus_text':  # Si el orden es por la descripción de 'estatus'
            # Obtener dinámicamente los valores de estatus y sus correspondientes textos
            ESTATUS_CHOICES = dict(Grupo._meta.get_field('estatus').choices)

            # Crear el 'Case' dinámico
            case_conditions = [When(estatus=key, then=Value(value)) for key, value in ESTATUS_CHOICES.items()]
            case_conditions.append(When(estatus=None, then=Value('Desconocido')))  # Opcional, si hay valores nulos

            return Grupo.objects.all().annotate(
                estatus_text=Case(*case_conditions, default=Value('Desconocido'), output_field=CharField())
            ).order_by('estatus_text')  # Ordenar por el campo 'estatus_text'

        return Grupo.objects.order_by(ordenar)  # Si no es 'estatus_text', ordenar por 'nombre' u otro campo

class GrupoCreateView(LoginRequiredMixin, CreateView):
    model = Grupo
    form_class = GrupoForm
    template_name = 'producto/grupo/grupo_form.html'
    success_url = reverse_lazy('grupos')

class GrupoUpdateView(LoginRequiredMixin, UpdateView):
    model = Grupo
    form_class = GrupoForm
    template_name = 'producto/grupo/grupo_form.html'
    success_url = reverse_lazy('grupos')

class GrupoDeleteView(LoginRequiredMixin, DeleteView):
    model = Grupo
    template_name = 'producto/grupo/grupo_confirm_delete.html'
    success_url = reverse_lazy('grupos')

class InsumoListView(LoginRequiredMixin, ListView):
    model = Insumo
    template_name = "producto/insumo/insumo_list.html"
    context_object_name = "insumos"

    def get_queryset(self):
        # Obtener el valor de 'ordenar' de la URL
        ordenar = self.request.GET.get('ordenar', 'nombre')  # Por defecto ordenar por nombre

        if ordenar == 'estatus_text':  # Si el orden es por la descripción de 'estatus'
            # Obtener dinámicamente los valores de estatus y sus correspondientes textos
            ESTATUS_CHOICES = dict(Insumo._meta.get_field('estatus').choices)

            # Crear el 'Case' dinámico
            case_conditions = [When(estatus=key, then=Value(value)) for key, value in ESTATUS_CHOICES.items()]
            case_conditions.append(When(estatus=None, then=Value('Desconocido')))  # Opcional, si hay valores nulos

            return Insumo.objects.all().annotate(
                estatus_text=Case(*case_conditions, default=Value('Desconocido'), output_field=CharField())
            ).order_by('estatus_text')  # Ordenar por el campo 'estatus_text'

        elif ordenar == 'venta_text':  # Si el orden es por la descripción de 'estatus'
            # Obtener dinámicamente los valores de estatus y sus correspondientes textos
            ESTATUS_CHOICES = dict(Insumo._meta.get_field('venta').choices)

            # Crear el 'Case' dinámico
            case_conditions = [When(venta=key, then=Value(value)) for key, value in ESTATUS_CHOICES.items()]
            case_conditions.append(When(venta=None, then=Value('Desconocido')))  # Opcional, si hay valores nulos

            return Insumo.objects.all().annotate(
                venta_text=Case(*case_conditions, default=Value('Desconocido'), output_field=CharField())
            ).order_by('-venta_text')  # Ordenar por el campo 'estatus_text'

        return Insumo.objects.order_by(ordenar)  # Si no es 'estatus_text', ordenar por 'nombre' u otro campo

class InsumoCreateView(LoginRequiredMixin, CreateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "producto/insumo/insumo_form.html"
    success_url = reverse_lazy("insumos")

class InsumoUpdateView(LoginRequiredMixin, UpdateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "producto/insumo/insumo_form.html"
    success_url = reverse_lazy("insumos")

class InsumoDeleteView(LoginRequiredMixin, DeleteView):
    model = Insumo
    template_name = "producto/insumo/insumo_confirm_delete.html"
    success_url = reverse_lazy("insumos")

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'producto/producto/producto_list.html'
    context_object_name = 'productos'
    ordering = ['nombre']  # Orden predeterminado

    def get_queryset(self):
        # Obtener el valor de 'ordenar' de la URL
        ordenar = self.request.GET.get('ordenar', 'nombre')  # Por defecto ordenar por nombre

        # Verificar si el orden es por 'estatus', 'nombre' o 'precio'
        if ordenar == 'estatus_text':  # Si el orden es por la descripción de 'estatus'
            # Obtener dinámicamente los valores de estatus y sus correspondientes textos
            ESTATUS_CHOICES = dict(Producto._meta.get_field('estatus').choices)

            # Crear el 'Case' dinámico
            case_conditions = [When(estatus=key, then=Value(value)) for key, value in ESTATUS_CHOICES.items()]
            case_conditions.append(When(estatus=None, then=Value('Desconocido')))  # Opcional, si hay valores nulos

            return Producto.objects.all().annotate(
                estatus_text=Case(*case_conditions, default=Value('Desconocido'), output_field=CharField())
            ).order_by('estatus_text')  # Ordenar por el campo 'estatus_text'

        elif ordenar == 'tipo_text':  # Si el orden es por la descripción de 'tipo'
            # Obtener dinámicamente los valores de tipo y sus correspondientes textos
            ESTATUS_CHOICES = dict(Producto._meta.get_field('tipo').choices)

            # Crear el 'Case' dinámico
            case_conditions = [When(tipo=key, then=Value(value)) for key, value in ESTATUS_CHOICES.items()]
            case_conditions.append(When(tipo=None, then=Value('Desconocido')))  # Opcional, si hay valores nulos

            return Producto.objects.all().annotate(
                tipo_text=Case(*case_conditions, default=Value('Desconocido'), output_field=CharField())
            ).order_by('tipo_text')  # Ordenar por el campo 'estatus_text'

        elif ordenar == 'precio':
            return Producto.objects.all().order_by(F('precio'))  # Ordenar por el campo 'precio'

        # Orden por nombre por defecto
        return Producto.objects.all().order_by(F('nombre'))

class GuardarInsumosSesionView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        insumos_seleccionados = data.get('insumos', [])
        request.session['insumos_seleccionados'] = insumos_seleccionados
        return JsonResponse({'status': 'success', 'insumos': insumos_seleccionados})

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    template_name = 'producto/producto/producto_form.html'
    form_class = ProductoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['insumos'] = Insumo.objects.annotate(
            seleccionado=Coalesce(Value(0, output_field=IntegerField()), Value(0, output_field=IntegerField())),  # ✅ 0 como valor numérico
            aplica=Coalesce(Value(None, output_field=IntegerField()), Value(0, output_field=IntegerField()))  # ✅ 0 como valor numérico
        ).values("id", "nombre", "grupo__nombre", "seleccionado", "aplica")
        
        return context

    def get_success_url(self):
        return reverse_lazy('productos')

    def form_valid(self, form):
        # Guardar el producto
        response = super().form_valid(form)
        
        # Obtener los insumos seleccionados de la sesión
        insumos_seleccionados = self.request.session.get('insumos_seleccionados', [])
        producto = form.instance  # El producto guardado
        
      # Asociar insumos seleccionados al producto
        for insumo_data in insumos_seleccionados:
            insumo_id = insumo_data['id']
            opcional = insumo_data['opcional']

            insumo = get_object_or_404(Insumo, pk=insumo_id)

            ProductoInsumo.objects.create(
                producto=producto,
                insumo=insumo,
                aplica=opcional,  # Puedes personalizar este valor
                cantidad=1,  # Personalizar si el usuario ingresa una cantidad
            )

        # Limpiar la sesión después de guardar
        self.request.session.pop('insumos_seleccionados', None)
       
        return response

class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    template_name = 'producto/producto/producto_form.html'
    form_class = ProductoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")  # El producto guardado

        producto = get_object_or_404(Producto, pk=pk)

        # Subquery para obtener el campo "aplica" de ProductoInsumo si el insumo está en la relación
        subquery_aplica = ProductoInsumo.objects.filter(
            producto=producto,  
            insumo=OuterRef("pk")
        ).values("aplica")[:1]

        # Subquery para verificar si el insumo está en la selección (1 si está, 0 si no)
        subquery_seleccionado = ProductoInsumo.objects.filter(
            producto=producto,
            insumo=OuterRef("pk")
        ).values("id")[:1]

        # Consulta principal con JOIN y Coalesce para incluir todos los insumos
        insumos = Insumo.objects.annotate(
            aplica=Coalesce(Subquery(subquery_aplica, output_field=IntegerField()), Value(None)),
            seleccionado=Coalesce(Subquery(subquery_seleccionado, output_field=IntegerField()), Value(0))
        ).values("id", "nombre", "grupo__nombre", "seleccionado", "aplica")

        context['insumos'] = insumos

        return context

    def get_success_url(self):
        return reverse_lazy('productos')

    def form_valid(self, form):
        # Guardar el producto
        response = super().form_valid(form)
        
        # Obtener los insumos seleccionados de la sesión
        insumos_seleccionados = self.request.session.get('insumos_seleccionados', [])
        producto = form.instance  # El producto guardado
        
        ProductoInsumo.objects.filter(producto=producto).delete()

      # Asociar insumos seleccionados al producto
        for insumo_data in insumos_seleccionados:
            insumo_id = insumo_data['id']
            opcional = insumo_data['opcional']

            insumo = get_object_or_404(Insumo, pk=insumo_id)

            ProductoInsumo.objects.create(
                producto=producto,
                insumo=insumo,
                aplica=opcional,  # Puedes personalizar este valor
                cantidad=1,  # Personalizar si el usuario ingresa una cantidad
            )

        # Limpiar la sesión después de guardar
        self.request.session.pop('insumos_seleccionados', None)
       
        return response

class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'producto/producto/producto_confirm_delete.html'
    success_url = reverse_lazy('productos')

class PaqueteListView(LoginRequiredMixin, ListView):
    model = Paquete
    template_name = 'producto/paquete/paquete_list.html'
    context_object_name = 'paquetes'
    ordering = ['nombre']  # Orden predeterminado

    def get_queryset(self):
        # Obtener el valor de 'ordenar' de la URL
        ordenar = self.request.GET.get('ordenar', 'nombre')  # Por defecto ordenar por nombre

        # Verificar si el orden es por 'estatus', 'nombre' o 'precio'
        if ordenar == 'estatus_text':  # Si el orden es por la descripción de 'estatus'
            # Obtener dinámicamente los valores de estatus y sus correspondientes textos
            ESTATUS_CHOICES = dict(Paquete._meta.get_field('estatus').choices)

            # Crear el 'Case' dinámico
            case_conditions = [When(estatus=key, then=Value(value)) for key, value in ESTATUS_CHOICES.items()]
            case_conditions.append(When(estatus=None, then=Value('Desconocido')))  # Opcional, si hay valores nulos

            return Paquete.objects.all().annotate(
                estatus_text=Case(*case_conditions, default=Value('Desconocido'), output_field=CharField())
            ).order_by('estatus_text')  # Ordenar por el campo 'estatus_text'

        elif ordenar == 'tipo_text':  # Si el orden es por la descripción de 'tipo'
            # Obtener dinámicamente los valores de tipo y sus correspondientes textos
            ESTATUS_CHOICES = dict(Paquete._meta.get_field('tipo_paquete').choices)

            # Crear el 'Case' dinámico
            case_conditions = [When(tipo_paquete=key, then=Value(value)) for key, value in ESTATUS_CHOICES.items()]
            case_conditions.append(When(tipo_paquete=None, then=Value('Desconocido')))  # Opcional, si hay valores nulos

            return Paquete.objects.all().annotate(
                tipo_text=Case(*case_conditions, default=Value('Desconocido'), output_field=CharField())
            ).order_by('tipo_text')  # Ordenar por el campo 'estatus_text'

        elif ordenar == 'precio':
            return Paquete.objects.all().order_by(F('precio'))  # Ordenar por el campo 'precio'

        # Orden por nombre por defecto
        return Paquete.objects.all().order_by(F('nombre'))

class GuardarProdutosSesionView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        productos_seleccionados = data.get('productos', [])
        request.session['productos_seleccionados'] = productos_seleccionados
        return JsonResponse({'status': 'success', 'productos': productos_seleccionados})

class PaqueteCreateView(LoginRequiredMixin, CreateView):
    model = Paquete
    template_name = 'producto/paquete/paquete_form.html'
    form_class = PaqueteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productos'] = Producto.objects.annotate(
            seleccionado=Coalesce(Value(0, output_field=IntegerField()), Value(0, output_field=IntegerField())),  # ✅ 0 como valor numérico
            cantidad=Coalesce(Value(0, output_field=IntegerField()), Value(0, output_field=IntegerField()))  # ✅ 0 como valor numérico
        ).values("id", "nombre", "tipo", "seleccionado", "cantidad")
        
        return context

    def get_success_url(self):
        return reverse_lazy('paquetes')

    def form_valid(self, form):
        # Guardar el producto
        response = super().form_valid(form)
        
        # Obtener los insumos seleccionados de la sesión
        productos_seleccionados = self.request.session.get('productos_seleccionados', [])
        paquete = form.instance  # El producto guardado
        
      # Asociar insumos seleccionados al producto
        for producto_data in productos_seleccionados:
            producto_id = producto_data['id']
            cantidad = producto_data['cantidad']

            producto = get_object_or_404(Producto, pk=producto_id)

            PaqueteProducto.objects.create(
                paquete=paquete,
                producto=producto,
                cantidad=cantidad,
            )

        # Limpiar la sesión después de guardar
        self.request.session.pop('productos_seleccionados', None)
       
        return response

class PaqueteUpdateView(LoginRequiredMixin, UpdateView):
    model = Paquete
    template_name = 'producto/paquete/paquete_form.html'
    form_class = PaqueteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")  # El producto guardado

        paquete = get_object_or_404(Paquete, pk=pk)

        # Subquery para obtener el campo "cantidad" de PaqueteProducto si el producto está en la relación
        subquery_aplica = PaqueteProducto.objects.filter(paquete=paquete,producto=OuterRef("pk")).values("cantidad")[:1]

        # Subquery para verificar si el producto está en la selección (1 si está, 0 si no)
        subquery_seleccionado = PaqueteProducto.objects.filter(paquete=paquete,producto=OuterRef("pk")).values("id")[:1]

        # Consulta principal con JOIN y Coalesce para incluir todos los insumos
        productos = Producto.objects.annotate(
            seleccionado=Coalesce(Subquery(subquery_seleccionado, output_field=IntegerField()), Value(0)),
            cantidad=Coalesce(Subquery(subquery_aplica, output_field=IntegerField()), Value(0))
        ).values("id", "nombre", "tipo", "seleccionado", "cantidad")

        context['productos'] = productos

        # Añadir las fechas de inicio y fin al contexto
        if paquete.fecha_inicio:
            context['fecha_inicio'] = paquete.fecha_inicio.strftime('%Y-%m-%dT%H:%M')  # Formatear la fecha para datetime-local
            context['fecha_fin'] = paquete.fecha_fin.strftime('%Y-%m-%dT%H:%M')  # Formatear la fecha para datetime-local

        return context

    def get_success_url(self):
        return reverse_lazy('paquetes')

    def form_valid(self, form):
        # Guardar el producto
        response = super().form_valid(form)
        
        # Obtener los insumos seleccionados de la sesión
        productos_seleccionados = self.request.session.get('productos_seleccionados', [])
        paquete = form.instance  # El paquete guardado
        
        PaqueteProducto.objects.filter(paquete=paquete).delete()

      # Asociar insumos seleccionados al producto
        for producto_data in productos_seleccionados:
            producto_id = producto_data['id']
            cantidad = producto_data['cantidad']

            producto = get_object_or_404(Producto, pk=producto_id)

            PaqueteProducto.objects.create(
                paquete=paquete,
                producto=producto,
                cantidad=cantidad,  # Personalizar si el usuario ingresa una cantidad
            )

        # Limpiar la sesión después de guardar
        self.request.session.pop('productos_seleccionados', None)
       
        return response

class PaqueteDeleteView(LoginRequiredMixin, DeleteView):
    model = Paquete
    template_name = 'producto/paquete/paquete_confirm_delete.html'
    success_url = reverse_lazy('paquetes')
