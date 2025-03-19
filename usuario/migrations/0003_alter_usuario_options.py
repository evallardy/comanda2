# Generated by Django 4.0.4 on 2025-03-18 21:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuario', '0002_alter_usuario_cliente'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='usuario',
            options={'permissions': (('cocina', 'Cocina consulta'), ('cocina_termina', 'Cocina termina'), ('cocina_cancela', 'Cocina cancela'), ('bar', 'Bar consulta'), ('bar_termina', 'Bar termina'), ('bar_cancela', 'Bar cancela'), ('servicio', 'Comandas consulta'), ('servicio_nueva', 'Comanda nueva'), ('servicio_solicitar', 'Comanda solicita'), ('servicio_cancelar', 'Comanda cancela'), ('servicio_ver', 'Comanda detalle'), ('servicio_mod', 'Comanda detalle mod.'), ('servicio_cierra', 'Comanda cierra'), ('entregas', 'Entregas consulta'), ('entregas_ok', 'Entrega OK'), ('entregas_cancela', 'Entrega cancelada'), ('consultas_seguimiento', 'Consulta de seguimiento'), ('consultas_reporte_dia', 'Consulta de reporte del día'), ('catalogo', 'Catálogo consulta'), ('catalogo_agregar', 'Catálogo Agrega'), ('catalogo_modificar', 'Catáogo Modifica'), ('accesos', 'Accesos consulta'), ('accesos_modificar', 'Accesos modifica'), ('abrir', 'Día abre'), ('cerrar', 'Día cierra'), ('usuarios', 'Usuarios consulta'), ('crea_usuario', 'Usuario nuevo'), ('modifica_usuario', 'Usuario modifica'), ('caja', 'Pago de comandas'))},
        ),
    ]
