from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import json
import re
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django.http.response import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, View
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.db.models import Q, F, Value, DecimalField, Count

from producto.models import Producto, Paquete, PaqueteProducto, ProductoInsumo
from .models import DiaContable, Caja, Detalle, Comanda, Servicio, Pago
from musica.models import Cancion

# Create your views here.

class ComandaView(LoginRequiredMixin, View):
    template_name = 'pedido/comanda.html'

    def get(self, request):
        datos = {}

        productos = Producto.objects.filter(estatus=1).order_by('-tipo', 'nombre')
        datos['productos'] = productos

        paquetes = Paquete.objects.filter(estatus=1).order_by('tipo_paquete', 'nombre')
        datos['paquetes'] = paquetes

        return render(request, self.template_name, {'datos': datos})

    def post(self, request):
        product_id = request.POST.get('product_id')
#        quantity = int(request.POST.get('quantity', 1))

        # Gestionar el carrito en la sesión
#        cart = request.session.get('cart', {})
#        if product_id in cart:
#            cart[product_id] += quantity
#        else:
#            cart[product_id] = quantity

#        request.session['cart'] = cart
        return JsonResponse({'success': True})

@login_required
def obtener_productos_paquete(request, paquete_id):
    paquete = get_object_or_404(Paquete, id=paquete_id)
    productos = PaqueteProducto.objects.filter(paquete=paquete).select_related('producto')

    productos_lista = [
        {
            "id": p.producto.id,
            "nombre": p.producto.nombre,
            "cantidad": p.cantidad,
        }
        for p in productos
    ]

    return JsonResponse({"productos": productos_lista})

@login_required
def agregar_al_carrito(request):
    if request.method == "POST":
        producto_id = int(request.POST.get("producto_id", 0))
        cantidad = int(request.POST.get("cantidad", 0))
        tipo = request.POST.get("tipo", 0)
        nombre_producto = request.POST.get("nombre_producto", "")
        precio = float(request.POST.get("precio", 0.00))
        area = int(request.POST.get("area", 0))

        # Obtener `adicionales` y asegurarse de que sea un diccionario
        try:
            adicionales = json.loads(request.POST.get("adicionales", "{}"))
        except json.JSONDecodeError:
            adicionales = {}  # En caso de error, se usa un diccionario vacío

        if tipo == 'producto':
            ingredientes = []
            insumos = ProductoInsumo.objects.filter(producto_id=producto_id, aplica__in=(2,3)).order_by("insumo__grupo", "aplica")

            for linsumo in insumos:
                grupo = linsumo.insumo.grupo.nombre
                nombre = linsumo.insumo.nombre
                id = linsumo.insumo.id
                id_grupo = linsumo.insumo.grupo.id

                if linsumo.aplica == 2:
                    opcion = 'rb'
                elif linsumo.aplica == 3:
                    opcion = 'cb'
                else:
                    opcion = None  # Para manejar valores inesperados

                ingrediente = {
                    "grupo": grupo,
                    "opcion": opcion,
                    "nombre": nombre,
                    "valor": 0,
                    "id": id,
                    "id_grupo": id_grupo,
                }

                ingredientes.append(ingrediente)

            # Si 'insumos' no está en 'adicionales', lo creamos
            if "insumos" not in adicionales:
                adicionales["insumos"] = []

            # Agregar los ingredientes para cada cantidad
            for _ in range(int(cantidad)):
                adicionales["insumos"].append(ingredientes)  # Agregar una copia independiente

        else:
            productos = []
            contenido = PaqueteProducto.objects.filter(paquete_id=producto_id).order_by("producto__nombre")

            for pieza in contenido:
                id = pieza.producto.id
                paquete_area = pieza.producto.tipo
                nombre = pieza.producto.nombre
                cantidad = pieza.cantidad

                producto = {
                    "id": id,
                    "nombre": nombre,
                    "cantidad": cantidad,
                    "area": paquete_area,
                }

                productos.append(producto)
            
            for producto in productos:
                ingredientes = []
                insumos = ProductoInsumo.objects.filter(producto_id=producto['id'], aplica__in=(2,3)).order_by("insumo__grupo", "aplica")

                for linsumo in insumos:
                    grupo = linsumo.insumo.grupo.nombre
                    nombre = linsumo.insumo.nombre
                    id = linsumo.insumo.id
                    id_grupo = linsumo.insumo.grupo.id

                    if linsumo.aplica == 2:
                        opcion = 'rb'
                    elif linsumo.aplica == 3:
                        opcion = 'cb'
                    else:
                        opcion = None  # Para manejar valores inesperados

                    ingrediente = {
                        "grupo": grupo,
                        "opcion": opcion,
                        "nombre": nombre,
                        "valor": 0,
                        "id": id,
                        "id_grupo": id_grupo,
                    }

                    ingredientes.append(ingrediente)

                # Si 'insumos' no está en 'adicionales', lo creamos
                if "insumos" not in producto:
                    producto["insumos"] = []

                producto["insumos"].append(ingredientes)  # Agregar una copia independiente

                # Si 'insumos' no está en 'adicionales', lo creamos
                if "producto" not in adicionales:
                    adicionales["producto"] = []

                adicionales["producto"].append(producto)  # Agregar una copia independiente


        # Obtener el carrito de la sesión
        carrito = request.session.get("carrito", {})

        # Agregar o actualizar producto en el carrito
        carrito[producto_id] = {
            "tipo": tipo,
            "producto_id": producto_id,
            "nombre_producto": nombre_producto,
            "cantidad": int(cantidad),
            "precio": precio,
            "area": area,
            "adicionales": adicionales,
        }

        request.session["carrito"] = carrito  # Guardar en sesión
        return JsonResponse({"mensaje": "Producto agregado correctamente.", "adicionales": adicionales, "precio": precio, "area": area})

    return JsonResponse({"error": "Método no permitido."}, status=405)    

@login_required
def guardar_datos(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                datos = json.loads(request.body)  # Convertir JSON en diccionario Python
                productos = datos.get("productos", [])
                datos_producto = productos[0]
                accion = datos_producto.get("comanda")
                mesa_numero = datos_producto.get("mesa_numero")
                mesa_observacion = datos_producto.get("mesa_observacion")

                dia_contable = DiaContable.objects.filter(estatus=1).first()

                if accion == 'Nueva':
                    comanda = Comanda.objects.create (
                        mesa = mesa_numero,
                        observacion = mesa_observacion,
                        dia_contable = dia_contable,
                    )
                else:
                    comanda = Comanda.objects.filter(id=mesa_numero).first()

                # Procesar cada producto
                for producto in productos:

                    total = float(producto["cantidad"]) * float(producto["precio"])

                    titulo = producto["titulo"],

                    caja = Caja.objects.create (
                        comanda = comanda,
                        descripcion = titulo[0],
                        cantidad = producto["cantidad"],
                        precio_unitario = producto["precio"],
                        importe = total,
                    )

                    if titulo[0].startswith("Combo") or titulo[0].startswith("Promoción"):
                        adicionales = json.loads(producto["adicionales"])
                        for adicional in adicionales:
                            nombre_producto = adicional['nombre']
                            area = adicional['area']
                            articulos = adicional['producto']
                            for insumos in articulos:
                                complementos = insumos['insumos'][0]
                                coma = ''
                                Ingredientes = 'Ingredientes : '
                                for complemento in complementos:
                                    if complemento['valor'] == 1:
                                        Ingredientes += coma + complemento['nombre']
                                        coma = ', '
                                detalle = Detalle.objects.create (
                                    caja = caja,
                                    comanda = comanda,
                                    producto = nombre_producto,
                                    tipo = int(area),
                                    especificacion = Ingredientes,
                                )
                    else:
                        adicionales = json.loads(producto["adicionales"])
                        area = producto['area']
                        for adicional in adicionales:
                            nombre_producto = adicional['nombre']
                            Ingredientes = 'Ingredientes : '
                            coma = ''
                            for insumo in adicional['producto'][0]['insumos']:
                                if insumo['valor'] == 1:
                                    Ingredientes += coma + insumo['nombre']
                                    coma = ', '
                            detalle = Detalle.objects.create (
                                caja = caja,
                                comanda = comanda,
                                producto = nombre_producto,
                                tipo = area,
                                especificacion = Ingredientes,
                            )


            return HttpResponseRedirect(reverse('index'))
#            return JsonResponse({"mensaje": "Datos guardados correctamente"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en formato JSON"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=400)

@login_required
def obtener_comandas(request):
    comandas = Comanda.objects.filter(dia_contable__estatus=1,estatus__in=(1,2)).values("id", "mesa", "observacion")
    return JsonResponse(list(comandas), safe=False)

# Vista para listar los detalles
class DetalleListView(LoginRequiredMixin, ListView):
    model = Detalle
    template_name = 'pedido/detalle_list.html'
    context_object_name = 'detalles'

    def get_queryset(self):
        opcion = self.kwargs.get('opcion', 1)  # Obtiene el valor de la opción desde la URL
        if opcion == 1 or opcion == 2:
            estatus = 1
            detalle = Detalle.objects.filter(estatus=estatus, tipo=opcion).order_by('fecha_alta')
        elif opcion == 3:
            estatus = 2
            detalle = Detalle.objects.filter(estatus=estatus).order_by('fecha_alta')
        elif opcion == 4:
            detalle = Detalle.objects.filter(estatus__in=(0,1,2,3,4,5)).order_by('fecha_alta')
        else:
            estatus = 100
            detalle = Detalle.objects.filter(estatus>estatus).order_by('fecha_alta')
        return detalle

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        opcion = self.kwargs['opcion']  # Enviamos "opcion" al template
        area = ''
        if opcion == 2:
            area = 'Bar'
        elif opcion == 1:
            area = 'Cocina'
        elif opcion == 3:
            area = 'Entregas'
        context['area'] = area
        context['opcion'] = opcion
        return context

# Vista para marcar como atendido
class DetalleAtenderView(UpdateView):
    model = Detalle
    fields = []  # No usamos formulario, solo actualizamos el estatus
    template_name = 'pedido/detalle_atender.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['opcion'] = self.kwargs['opcion']  # Enviamos "opcion" al template
        return context

    def post(self, request, *args, **kwargs):
        opcion = self.kwargs.get('opcion', 1)  # Obtiene el valor de la opción desde la URL
        if opcion == 1 or opcion == 2:
            estatus = 2
        elif opcion == 3:
            estatus = 3
        if opcion == 1 or estatus == 2 or opcion == 3:
            detalle = self.get_object()
            detalle.estatus = estatus  # Cambia el estatus a 'Atendido'
            detalle.save()

        return redirect('accion', opcion)  # Corrige la sintaxis de `redirect`
    
# Vista para marcar como atendido
class DetalleCancelarView(LoginRequiredMixin, UpdateView):
    model = Detalle
    fields = []  # No usamos formulario, solo actualizamos el estatus
    template_name = 'pedido/detalle_cancelar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk', 1)  
        opcion = self.kwargs.get('opcion', 1)
        detalle = get_object_or_404(Detalle, id=pk)
        caja = get_object_or_404(Caja, id=detalle.caja_id)
        context['pedido'] = caja
        context['opcion'] = self.kwargs['opcion']  # Enviamos "opcion" al template
        return context

    def post(self, request, *args, **kwargs):
        opcion = self.kwargs.get('opcion', 1)  # Obtiene el valor de la opción desde la URL
        pk = self.kwargs.get('pk', 1)  
        opcion = self.kwargs.get('opcion', 1)
        detalle = get_object_or_404(Detalle, id=pk)
        caja = get_object_or_404(Caja, id=detalle.caja_id)

        cantidad = 0

        with transaction.atomic():
            detalle = self.get_object()
            detalle.estatus = 0  # Cambia el estatus a 'Atendido'
            detalle.save()

            if caja.cantidad > 1:
                cantidad = caja.cantidad - 1
                total = caja.precio_unitario * cantidad
                caja.cantidad = cantidad
                caja.importe = total
            else:
                caja.estatus = 0

            caja.save()

        return redirect('accion', opcion)  # Corrige la sintaxis de `redirect`

class CajaListView(LoginRequiredMixin, ListView):
    model = Caja
    template_name = 'pedido/caja_list.html'
    context_object_name = 'cajas'

    def get_queryset(self):
        return Caja.objects.filter(estatus=1,comanda__dia_contable__estatus=1).order_by('comanda__mesa','comanda__observacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        caja_estatus = {}
        comandas = Comanda.objects.filter(dia_contable__estatus=1,estatus__in=(1,2)).order_by('mesa','observacion')

        # obtener las mesas que estan sin productos para poder cerrar
        mesas_para_cerrar = Comanda.objects.filter(dia_contable__estatus=1, estatus=1).annotate(
            total_cajas=Count('caja', distinct=True),
            cajas_validas=Count('caja', filter=Q(caja__estatus__in=[0, 2]), distinct=True)
        ).filter(total_cajas=F('cajas_validas')).values('id', 'mesa', 'observacion')

        for caja in Caja.objects.filter(estatus__in=(1,2),comanda__dia_contable__estatus=1):
            detalles = Detalle.objects.filter(caja=caja,estatus__in=(1,2,3))

            if detalles.exists():
                estatus_detalles = list(detalles.values_list('estatus', flat=True))

                if all(est == 3 for est in estatus_detalles):
                    estado = 'Completado'
                else:
                    estado = 'En proceso'
            else:
                estado = 'Sin detalles'

            caja_estatus[caja.id] = estado  # 📌 Se almacena en el diccionario

        context['comandas'] = comandas
        context['caja_estatus'] = caja_estatus
        context['mesas_para_cerrar'] = mesas_para_cerrar
        return context

@login_required
def pagar_caja(request):
    if request.method == "POST":
        caja_ids = request.POST.getlist("cajas")  # Obtiene los IDs seleccionados
        cajas = Caja.objects.filter(id__in=caja_ids)
        
        # Aquí puedes realizar la lógica de pago, actualizar estatus, etc.
        for caja in cajas:
            caja.estatus = 2  # Por ejemplo, cambiar el estatus a "Pagado"
            caja.save()

        return JsonResponse({"message": "Pago procesado correctamente"})
    return redirect("caja_list")        

@login_required
def cerrar_comanda(request, id):

    if request.method == "GET":
        comanda = Comanda.objects.filter(id=id).update(estatus=3)

    return redirect(reverse_lazy("caja"))     

@login_required
def guardar_pago(request):
    if request.method == 'POST':
        importe_efectivo = request.POST.get('importe_efectivo')
        importe_tarjeta = request.POST.get('importe_tarjeta')
        importe_transferencia = request.POST.get('importe_transferencia')
        importe_comision = request.POST.get('importe_comision')
        importe_descuento = request.POST.get('importe_descuento')
        pagos_seleccionados = request.POST.get("pagos_seleccionados", "[]") 

        # Crear el registro de pago
        with transaction.atomic():
            pago = Pago.objects.create(
                importe_efectivo=importe_efectivo,
                importe_tarjeta=importe_tarjeta,
                importe_transferencia=importe_transferencia,
                importe_comision=importe_comision,
                importe_descuento=importe_descuento,
            )
            
            try:
                pagos_ids = [int(id.strip()) for id in pagos_seleccionados.split(",") if id.strip().isdigit()]
#                pagos_ids = json.loads(pagos_seleccionados)  # Convertir de JSON a lista
                if not isinstance(pagos_ids, list):
                    raise ValueError("El formato de pagosSeleccionados no es una lista válida.")
                
                # Convertimos los IDs a enteros (por seguridad)
                pagos_ids = [int(id) for id in pagos_ids if str(id).isdigit()]

                if pagos_ids:  # Verificar que haya IDs antes de actualizar
                    actualizados = Caja.objects.filter(id__in=pagos_ids).update(estatus=2,caja_grupo=pago)
                    return redirect(reverse_lazy("caja"))
#                    return JsonResponse({"mensaje": f"{actualizados} pagos actualizados correctamente"}, status=200)
                else:
                    return redirect(reverse_lazy("caja"))
#                    return JsonResponse({"error": "No se encontraron pagos válidos para actualizar"}, status=400)

            except (json.JSONDecodeError, ValueError, ValidationError) as e:
                return redirect(reverse_lazy("caja"))
#                return JsonResponse({"error": f"Error en el formato de datos: {str(e)}"}, status=400)

    return redirect(reverse_lazy("caja"))
#    return JsonResponse({"error": "Método no permitido"}, status=405)

class ServicioListView(LoginRequiredMixin, ListView):
    model = Servicio
    template_name = 'servicio_list.html'
    context_object_name = 'servicios'
    paginate_by = 10  # Paginación de 10 elementos por página

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.GET.get('orderby', 'fecha_alta')
        direction = self.request.GET.get('dir', 'asc')
        fecha_alta_filter = int(self.request.GET.get('fecha_alta', '0'))

        # Aplicar filtro por fecha si se selecciona una opción
        if fecha_alta_filter:
            queryset = queryset.filter(comanda__dia_contable__id=fecha_alta_filter)

        # Determinar el ordenamiento correcto
        if direction == 'desc':
            ordering = f'-{ordering}'
        
        return queryset.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_ordering'] = self.request.GET.get('orderby', 'fecha_alta')
        context['current_direction'] = self.request.GET.get('dir', 'asc')
        context['selected_fecha_alta'] = int(self.request.GET.get('fecha_alta', '0'))
        context['fechas_alta'] = DiaContable.objects.order_by('-fecha_alta')
        return context

class ComandasView(LoginRequiredMixin, ListView):
    model = Caja
    template_name = 'pedido/comandas.html'
    context_object_name = 'cajas'

    def get_queryset(self):
        return Caja.objects.filter(comanda__dia_contable__estatus=1).order_by('comanda__mesa','comanda__observacion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        caja_estatus = {}
        comandas = Comanda.objects.filter(dia_contable__estatus=1).order_by('mesa','observacion')

        for caja in Caja.objects.filter(comanda__dia_contable__estatus=1):
            detalles = Detalle.objects.filter(caja=caja)

            if caja.estatus == 2:
                estado = 'Pagado'
            elif detalles.exists():
                estatus_detalles = list(detalles.values_list('estatus', flat=True))

                if all(est == 3 for est in estatus_detalles):
                    estado = 'Por pagar'
                else:
                    if all(est == 0 for est in estatus_detalles):
                        estado = 'Cancelada' 
                    else:
                        estado = 'En proceso de entrega' 
            else:
                estado = 'Cancelado'

            caja_estatus[caja.id] = estado  # 📌 Se almacena en el diccionario

        context['comandas'] = comandas
        context['caja_estatus'] = caja_estatus
        return context

class CierreView(LoginRequiredMixin, View):
    template_name = 'pedido/cierre.html'

    def get(self, request):
        datos = {}

        if DiaContable.objects.filter(estatus=1).first():
            datos['accion'] = 'Cerrar día contable'
        else:
            datos['accion'] = 'Aperturar día contable'
        
        return render(request, self.template_name, {'datos': datos})

    def post(self, request):

        if DiaContable.objects.filter(estatus=1).first():
            dias_contables = DiaContable.objects.filter(estatus=1)

            if dias_contables:
                ids_dias_contables = list(dias_contables.values_list('id', flat=True))

                for dia in dias_contables:
                    dia.estatus = 0
                    dia.save()

                canciones_eliminadas = Cancion.objects.filter(dia_contable__in=ids_dias_contables).delete()
        else:
            nuevo_dia = DiaContable.objects.create()

        return redirect('index')
    
class CajaReporteView(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'pedido/caja_reporte.html'
    context_object_name = 'pagos'

    def get_queryset(self):
        dia_contable_id = self.request.GET.get('dia_contable')
        if not dia_contable_id:
            dia_contable = DiaContable.objects.filter(estatus=1).first()
            dia_contable_id = dia_contable.id
        queryset = Caja.objects.filter(comanda__dia_contable__id=dia_contable_id).values(
            'comanda__mesa',
            'comanda__observacion',
            'caja_grupo__id',
            'caja_grupo__importe_efectivo',
            'caja_grupo__importe_tarjeta',
            'caja_grupo__importe_transferencia',
            'caja_grupo__importe_comision',
            'caja_grupo__importe_descuento'
        ).annotate(
            total_importe=Coalesce(F("caja_grupo__importe_efectivo"), Value(0, output_field=DecimalField())) +
                        Coalesce(F("caja_grupo__importe_tarjeta"), Value(0, output_field=DecimalField())) +
                        Coalesce(F("caja_grupo__importe_transferencia"), Value(0, output_field=DecimalField()))
        ).distinct().order_by('comanda__mesa')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dia_contable_id = self.request.GET.get('dia_contable')
        if not dia_contable_id:
            dia_contable = DiaContable.objects.filter(estatus=1).first()
            dia_contable_id = dia_contable.id
        cajas = Caja.objects.filter(comanda__dia_contable__id=dia_contable_id).values(
            'comanda__mesa',
            'comanda__observacion',
            'caja_grupo__id',
            'caja_grupo__importe_efectivo',
            'caja_grupo__importe_tarjeta',
            'caja_grupo__importe_transferencia',
            'caja_grupo__importe_comision',
            'caja_grupo__importe_descuento',
            ).distinct().order_by('comanda')
        total_efectivo = cajas.aggregate(total=Sum('caja_grupo__importe_efectivo'))['total'] or 0
        total_tarjeta = cajas.aggregate(total=Sum('caja_grupo__importe_tarjeta'))['total'] or 0
        total_transferencia = cajas.aggregate(total=Sum('caja_grupo__importe_transferencia'))['total'] or 0
        total_comision = cajas.aggregate(total=Sum('caja_grupo__importe_comision'))['total'] or 0
        total_descuento = cajas.aggregate(total=Sum('caja_grupo__importe_descuento'))['total'] or 0
        total_importe = total_efectivo + total_tarjeta + total_transferencia
        total_global = total_comision + total_importe - total_descuento
        context['total_efectivo'] = total_efectivo
        context['total_tarjeta'] = total_tarjeta
        context['total_transferencia'] = total_transferencia
        context['total_comision'] = total_comision
        context['total_descuento'] = total_descuento
        context['total_importe'] = total_importe
        context['total_global'] = total_global
        context['dias_contables'] = DiaContable.objects.all()
        context['dia_contable_seleccionado'] = str(dia_contable_id)
        return context    