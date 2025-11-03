from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

# Models & forms
from .models import Producto, Pedido, DetallePedido, UbicacionProducto
from .forms import ProductoForm
from movimientos.models import Movimiento
from django.http import JsonResponse
from .models import Producto, DetallePedido, Pedido

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

# Placeholders temporales para dashboard
@login_required
def movimientos_list(request):
    return render(request, 'movimientos/movimientos_list.html')

######################################################################MOVIMIENTO#################################
@login_required
def reportes(request):
    if request.user.rol not in ['admin', 'gerente', 'propietario']:
        return redirect('dashboard')
    
    # Total productos
    total_productos = Producto.objects.count()

    # Stock total
    stock_total = sum([p.stock for p in Producto.objects.all()])

    # Movimientos recientes
    ultimos_movimientos = Movimiento.objects.all().order_by('-fecha')[:10]

    context = {
        'total_productos': total_productos,
        'stock_total': stock_total,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'productos/reportes.html', context)

@login_required
def lista_pedidos(request):
    # Solo el bodeguero ve pedidos pendientes
    pedidos = Pedido.objects.filter(estado='pendiente')
    return render(request, 'productos/lista_pedidos.html', {'pedidos': pedidos})

@login_required
def tomar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    pedido.estado = 'en_proceso'
    pedido.save()
    return redirect('detalle_pedido', pedido_id=pedido.id)

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()  # productos asociados
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

from django.shortcuts import render
from .models import Pedido

def movimientos_list(request):
    # Traemos solo pedidos completados
    pedidos = Pedido.objects.filter(estado='completado').order_by('-fecha_creacion')
    return render(request, 'productos/movimientos.html', {'pedidos': pedidos})
