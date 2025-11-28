from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Producto, Pedido, DetallePedido, UbicacionProducto
from .forms import ProductoForm, DetallePedidoFormSet
from movimientos.models import Movimiento
from django.http import JsonResponse
from .models import Producto, DetallePedido, Pedido
from django.db.models import Sum, Count
from django.db.models import F, Sum, Count, ExpressionWrapper, DecimalField
from django.contrib.admin.views.decorators import staff_member_required
from .models import Producto, Pedido, DetallePedido
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from decimal import Decimal
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import pandas as pd
import io



# CRUD Productos
#esta funcion hace las alertas de stock
@login_required
def productos_list(request):
    productos = Producto.objects.all()
    umbral_stock_bajo = 5

    productos_bajo_stock = Producto.objects.filter(stock__lt=umbral_stock_bajo)

    alerta_stock_bajo = productos_bajo_stock.exists()

    return render(request, 'productos/productos_list.html', {
        'productos': productos,
        'alerta_stock_bajo': alerta_stock_bajo,
        'productos_bajo_stock': productos_bajo_stock
    })
    

@login_required
def productos_create(request):
    if request.user.rol != 'admin':
        return redirect('productos-list')
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('productos-list')
    else:
        form = ProductoForm()
    return render(request, 'productos/producto_form.html', {'form': form})

@login_required
def productos_update(request, pk):
    if request.user.rol not in ['admin', 'bodeguero']:
        return redirect('productos-list')
    producto = Producto.objects.get(pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('productos-list')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/producto_form.html', {'form': form})

@login_required
def productos_delete(request, pk):
    if request.user.rol != 'admin':
        return redirect('productos-list')
    producto = Producto.objects.get(pk=pk)
    if request.method == 'POST':
        producto.delete()
        return redirect('productos-list')
    return render(request, 'productos/producto_confirm_delete.html', {'producto': producto})


#Funcion auxiliar para obtener datos de reportes
def _get_report_context():

    #KPIs Principales
    total_stock_unidades = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    valor_inventario_agg = Producto.objects.aggregate(
        valor=Sum(ExpressionWrapper(F('precio') * F('stock'), output_field=DecimalField()))
    )['valor'] or Decimal('0.00')

    #Formateo de valores
    valor_inventario_formateado = f"${valor_inventario_agg:,.0f}".replace(",", ".")
    total_stock_unidades_formateado = f"{total_stock_unidades:,}".replace(",", ".")

    #analisis de Productos
    productos_bajo_stock = Producto.objects.filter(stock__lt=10).order_by('stock')
    
    productos_vendidos = DetallePedido.objects.values('producto__nombre').annotate(
        total_vendido=Sum('cantidad')
    ).order_by('-total_vendido')

    top_5_mas_vendidos = productos_vendidos[:5]
    top_5_menos_vendidos = productos_vendidos.reverse()[:5]

    #Analisis Pedidos
    now = timezone.now()
    pedidos_completados_mes = Pedido.objects.filter(
        estado='completado',
        fecha_creacion__month=now.month,
        fecha_creacion__year=now.year
    ).count()

    rendimiento_bodegueros = Pedido.objects.filter(estado='completado', bodeguero__isnull=False).values('bodeguero__username').annotate(
        total_completado=Count('id')
    ).order_by('-total_completado')

    context = {
        'valor_inventario_raw': valor_inventario_agg,
        'valor_inventario': valor_inventario_formateado,
        'total_stock_unidades': total_stock_unidades_formateado,
        'productos_bajo_stock': productos_bajo_stock,
        'pedidos_completados_mes': pedidos_completados_mes,
        'top_5_mas_vendidos': top_5_mas_vendidos,
        'top_5_menos_vendidos': top_5_menos_vendidos,
        'rendimiento_bodegueros': rendimiento_bodegueros,
    }
    return context

@staff_member_required
def reportes(request):
    """
    Vista para mostrar la página de reportes con KPIs y análisis.
    """
    context = _get_report_context()
    return render(request, 'productos/reportes.html', context)

@staff_member_required
def descargar_reporte_pdf(request):
    """
    Genera y descarga un reporte en PDF con los datos principales.
    """
    context = _get_report_context()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(inch, height - inch, "Reporte de Inventario")

    p.setFont("Helvetica", 12)
    y = height - 1.5 * inch
    p.drawString(inch, y, f"Valor Total del Inventario: {context['valor_inventario']}")
    y -= 0.5 * inch
    p.drawString(inch, y, f"Total de Unidades en Stock: {context['total_stock_unidades']}")
    y -= 0.5 * inch
    p.drawString(inch, y, f"Pedidos Completados este Mes: {context['pedidos_completados_mes']}")

    y -= 1 * inch
    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, y, "Productos con Bajo Stock (<10):")
    p.setFont("Helvetica", 10)
    y -= 0.3 * inch
    for producto in context['productos_bajo_stock']:
        p.drawString(1.2 * inch, y, f"- {producto.nombre} (Stock: {producto.stock})")
        y -= 0.25 * inch
        if y < inch: #salto de pagina
            p.showPage()
            p.setFont("Helvetica", 10)
            y = height - inch



    #rendimiento de bodegueros
    y -= 1 * inch
    if y < 2 * inch:
        p.showPage()
        y = height - inch

    p.setFont("Helvetica-Bold", 12)
    p.drawString(inch, y, "Rendimiento de Bodegueros")
    p.setFont("Helvetica", 10)
    y -= 0.3 * inch

    for item in context['rendimiento_bodegueros']:
        p.drawString(1.2 * inch, y, f"- {item['bodeguero__username']}: {item['total_completado']} pedidos")
        y -= 0.25 * inch

    p.showPage()
    p.save()
    return response

@staff_member_required
def descargar_reporte_excel(request):
    """
    Genera y descarga un reporte en Excel con el listado de productos y rendimiento de bodegueros.
    """
    context = _get_report_context()
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        
        productos_qs = Producto.objects.all().values('nombre', 'precio', 'stock', 'categoria')
        df_productos = pd.DataFrame(list(productos_qs))
        df_productos.to_excel(writer, index=False, sheet_name='Productos')

        rendimiento_data = list(context['rendimiento_bodegueros'])
        if rendimiento_data:
            df_rendimiento = pd.DataFrame(rendimiento_data)
           
            df_rendimiento.rename(columns={'bodeguero__username': 'Bodeguero', 'total_completado': 'Pedidos Completados'}, inplace=True)
            df_rendimiento.to_excel(writer, index=False, sheet_name='Rendimiento Bodegueros')

    output.seek(0)

    productos = Producto.objects.all().values('nombre', 'precio', 'stock', 'categoria')
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_productos.xlsx"'
    return response

@login_required
def crear_pedido(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('dashboard')

    if request.method == 'POST':
        pedido = Pedido(usuario=request.user)
        formset = DetallePedidoFormSet(request.POST, instance=pedido)
        if formset.is_valid():
            with transaction.atomic():
                pedido.save()
                formset.save()
            messages.success(request, "Pedido creado exitosamente.")
            return redirect('lista_pedidos')
    else:
        formset = DetallePedidoFormSet(instance=Pedido())

    return render(request, 'productos/crear_pedido.html', {'formset': formset})
@login_required
def lista_pedidos(request):
    pedidos = Pedido.objects.filter(estado='pendiente')
    return render(request, 'productos/lista_pedidos.html', {'pedidos': pedidos})

@login_required
def tomar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'en_proceso'
    pedido.bodeguero = request.user  
    pedido.save()
    return redirect('detalle_pedido', pedido_id=pedido.id)

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()  
    return render(request, 'productos/detalle_pedido.html', {
        'pedido': pedido,
        'detalles': detalles
    })
    
from django.http import JsonResponse
from .models import DetallePedido

from django.http import JsonResponse
from .models import DetallePedido

def escanear_producto(request):
    """
    Recibe POST con 'producto_id' y 'pedido_id',
    marca como escaneado y actualiza stock solo una vez.
    """
    if request.method == "POST":
        producto_id = request.POST.get("producto_id")
        pedido_id = request.POST.get("pedido_id")

        try:
            detalle = DetallePedido.objects.get(
                pedido_id=pedido_id, producto_id=producto_id
            )

            # Solo descontar si no estaba escaneado
            if not detalle.escaneado:
                detalle.escaneado = True
                detalle.save()

                # Actualizar stock
                producto = detalle.producto
                producto.stock -= detalle.cantidad
                if producto.stock < 0:
                    producto.stock = 0
                producto.save()

            # Revisar si todos los detalles están escaneados
            pedido = detalle.pedido
            if all(d.escaneado for d in pedido.detalles.all()):
                pedido.estado = "completado"
                pedido.save()
                status = "Pedido completado"
            else:
                status = "Producto escaneado"

            return JsonResponse({"success": True, "status": status})

        except DetallePedido.DoesNotExist:
            return JsonResponse({"success": False, "status": "Producto no encontrado en el pedido"})

    return JsonResponse({"success": False, "status": "Método no permitido"})







import json
from django.shortcuts import render
from .models import Pedido, Producto

def movimientos_list(request):
    pedidos = Pedido.objects.filter(estado='completado').select_related('usuario', 'bodeguero').order_by('-fecha_creacion')
    return render(request, 'productos/movimientos.html', {'pedidos': pedidos})
from decimal import Decimal
from django.db.models import F, Sum, Count, ExpressionWrapper, DecimalField
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .models import Producto, Pedido, DetallePedido

@staff_member_required
def dashboard_admin(request):
    total_stock = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0

    valor_agg = Producto.objects.aggregate(
        valor=Sum(
            ExpressionWrapper(
                F('precio') * F('stock'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )
    )['valor']
    valor_inventario = valor_agg if valor_agg is not None else Decimal('0.00')
    valor_inventario_formateado = f"{valor_inventario:,.0f}".replace(",", ".")
    valor_stock_formateado = f"{total_stock:,.0f}".replace(",", ".")
    productos_bajos_qs = Producto.objects.filter(stock__lt=10)
    total_pedidos = Pedido.objects.count()

    productos_top_stock = Producto.objects.values('nombre', 'stock').order_by('-stock')[:3]
    labels = [p['nombre'] for p in productos_top_stock]
    data = [p['stock'] for p in productos_top_stock]

    productos_labels_json = json.dumps(labels)
    productos_stock_json = json.dumps(data)

    context = {
    'total_stock': valor_stock_formateado,
    'valor_inventario': valor_inventario_formateado,
    'productos_bajos': productos_bajos_qs,
    'total_pedidos': total_pedidos,
    'productos_labels_json': productos_labels_json,
    'productos_stock_json': productos_stock_json,
    }
    from movimientos.models import Movimiento

    
    productos_vendidos_qs = (
        DetallePedido.objects
        .values('producto__nombre')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5]
    )

    mas_vendidos_labels = [p['producto__nombre'] for p in productos_vendidos_qs]
    mas_vendidos_data = [p['total_vendido'] for p in productos_vendidos_qs]

    mas_vendidos_labels_json = json.dumps(mas_vendidos_labels)
    mas_vendidos_data_json = json.dumps(mas_vendidos_data)

    context.update({
        'mas_vendidos_labels_json': mas_vendidos_labels_json,
        'mas_vendidos_data_json': mas_vendidos_data_json,
    })

    return render(request, 'productos/dashboard_admin.html', context)
