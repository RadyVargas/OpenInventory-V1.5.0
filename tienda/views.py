# tienda/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from productos.models import Producto, Pedido, DetallePedido
from decimal import Decimal
import json

# ============================================
# UTILIDADES PARA MANEJO DE CARRITO EN SESIÓN
# ============================================

"""
las vistas de la de la tienda estan configuradas
con bootstrap y heredan de su propio base.html,
contienen su propio css y js.
completr un pedido este se almacena en la bd
con los datos del cliente para despues mostrarse 
en OpenInventory

"""

def obtener_carrito(request):
    """Obtiene el carrito de la sesión o crea uno nuevo"""
    carrito = request.session.get('carrito', {})
    return carrito

def guardar_carrito(request, carrito):
    """Guarda el carrito en la sesión"""
    request.session['carrito'] = carrito
    request.session.modified = True

def calcular_total_carrito(carrito):
    """Calcula el total del carrito"""
    total = Decimal('0.00')
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            total += producto.precio * cantidad
        except Producto.DoesNotExist:
            continue
    return total

def obtener_items_carrito(carrito):
    """Obtiene los items del carrito con información completa"""
    items = []
    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id)
            subtotal = producto.precio * cantidad
            items.append({
                'producto': producto,
                'cantidad': cantidad,
                'subtotal': subtotal
            })
        except Producto.DoesNotExist:
            continue
    return items

# ============================================
# VISTAS DE CATÁLOGO
# ============================================

def catalogo(request):
    """Vista principal del catálogo de productos"""
    productos = Producto.objects.filter(stock__gt=0).order_by('-id')
    carrito = obtener_carrito(request)
    cantidad_items = sum(carrito.values())
    
    context = {
        'productos': productos,
        'cantidad_items': cantidad_items,
    }
    return render(request, 'tienda/catalogo.html', context)

def producto_detalle(request, pk):
    """Vista de detalle de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    carrito = obtener_carrito(request)
    cantidad_items = sum(carrito.values())
    
    context = {
        'producto': producto,
        'cantidad_items': cantidad_items,
    }
    return render(request, 'tienda/producto_detalle.html', context)

# ============================================
# VISTAS DE CARRITO
# ============================================

def ver_carrito(request):
    """Vista del carrito de compras"""
    carrito = obtener_carrito(request)
    items = obtener_items_carrito(carrito)
    total = calcular_total_carrito(carrito)
    cantidad_items = sum(carrito.values())
    
    context = {
        'items': items,
        'total': total,
        'cantidad_items': cantidad_items,
    }
    return render(request, 'tienda/carrito.html', context)

def agregar_al_carrito(request, producto_id):
    """Agrega un producto al carrito (AJAX)"""
    if request.method == 'POST':
        try:
            producto = get_object_or_404(Producto, id=producto_id)
            cantidad = int(request.POST.get('cantidad', 1))
            
            # Validar stock
            if cantidad > producto.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Solo hay {producto.stock} unidades disponibles'
                })
            
            carrito = obtener_carrito(request)
            
            # Agregar o actualizar cantidad
            if str(producto_id) in carrito:
                nueva_cantidad = carrito[str(producto_id)] + cantidad
                if nueva_cantidad > producto.stock:
                    return JsonResponse({
                        'success': False,
                        'message': f'Solo hay {producto.stock} unidades disponibles'
                    })
                carrito[str(producto_id)] = nueva_cantidad
            else:
                carrito[str(producto_id)] = cantidad
            
            guardar_carrito(request, carrito)
            cantidad_items = sum(carrito.values())
            
            return JsonResponse({
                'success': True,
                'message': f'{producto.nombre} agregado al carrito',
                'cantidad_items': cantidad_items
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def actualizar_carrito(request, producto_id):
    """Actualiza la cantidad de un producto en el carrito (AJAX)"""
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            producto = get_object_or_404(Producto, id=producto_id)
            
            if cantidad > producto.stock:
                return JsonResponse({
                    'success': False,
                    'message': f'Solo hay {producto.stock} unidades disponibles'
                })
            
            carrito = obtener_carrito(request)
            
            if cantidad > 0:
                carrito[str(producto_id)] = cantidad
            else:
                carrito.pop(str(producto_id), None)
            
            guardar_carrito(request, carrito)
            total = calcular_total_carrito(carrito)
            cantidad_items = sum(carrito.values())
            
            return JsonResponse({
                'success': True,
                'total': str(total),
                'cantidad_items': cantidad_items
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def eliminar_del_carrito(request, producto_id):
    """Elimina un producto del carrito (AJAX)"""
    if request.method == 'POST':
        try:
            carrito = obtener_carrito(request)
            carrito.pop(str(producto_id), None)
            guardar_carrito(request, carrito)
            
            total = calcular_total_carrito(carrito)
            cantidad_items = sum(carrito.values())
            
            return JsonResponse({
                'success': True,
                'total': str(total),
                'cantidad_items': cantidad_items
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

# ============================================
# VISTAS DE CHECKOUT CON REGISTRO DE CLIENTE
# ============================================

def checkout(request):
    """Vista de checkout con formulario de datos del cliente"""
    carrito = obtener_carrito(request)
    
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío')
        return redirect('tienda:catalogo')
    
    if request.method == 'POST':
        try:
            # Obtener datos del cliente
            nombre_completo = request.POST.get('nombre_completo', '').strip()
            email = request.POST.get('email', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            direccion = request.POST.get('direccion', '').strip()
            
            # Validar datos
            if not all([nombre_completo, email, telefono, direccion]):
                messages.error(request, 'Por favor completa todos los campos')
                return redirect('tienda:checkout')
            
            # Validar stock antes de crear el pedido
            for producto_id, cantidad in carrito.items():
                producto = Producto.objects.get(id=producto_id)
                if producto.stock < cantidad:
                    messages.error(request, f'No hay suficiente stock de {producto.nombre}')
                    return redirect('tienda:ver_carrito')
            
            # Crear pedido con transacción atómica
            with transaction.atomic():
                # Importar Usuario
                from usuarios.models import Usuario
                
                # Crear o obtener usuario cliente
                # Usamos el email como username único
                username = f"cliente_{email.split('@')[0]}_{hash(email) % 10000}"
                
                # Buscar si ya existe un cliente con este email
                try:
                    usuario_cliente = Usuario.objects.get(email=email, rol='cliente')
                except Usuario.DoesNotExist:
                    # Crear nuevo usuario cliente
                    usuario_cliente = Usuario.objects.create_user(
                        username=username,
                        email=email,
                        first_name=nombre_completo.split()[0] if nombre_completo.split() else nombre_completo,
                        last_name=' '.join(nombre_completo.split()[1:]) if len(nombre_completo.split()) > 1 else '',
                        rol='cliente',
                        is_active=True
                    )
                    # No necesita password ya que no hará login
                    usuario_cliente.set_unusable_password()
                    usuario_cliente.save()
                
                # Crear pedido asociado al cliente
                pedido = Pedido.objects.create(
                    usuario=usuario_cliente,
                    estado='pendiente',
                    nombre_cliente=nombre_completo,
                    email_cliente=email,
                    telefono_cliente=telefono,
                    direccion_envio=direccion
                )
                
                # Crear detalles del pedido
                for producto_id, cantidad in carrito.items():
                    producto = Producto.objects.get(id=producto_id)
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio
                    )
                
                # Guardar datos del cliente en sesión para mostrar en confirmación
                request.session['ultimo_pedido'] = {
                    'id': pedido.id,
                    'nombre': nombre_completo,
                    'email': email,
                    'telefono': telefono,
                    'direccion': direccion
                }
                
                # Limpiar carrito
                request.session['carrito'] = {}
                request.session.modified = True
                
                messages.success(request, f'¡Pedido #{pedido.id} creado exitosamente! Será procesado por el equipo de bodega.')
                return redirect('tienda:compra_exitosa', pedido_id=pedido.id)
                
        except Exception as e:
            messages.error(request, f'Error al procesar el pedido: {str(e)}')
            return redirect('tienda:checkout')
    
    # GET request - mostrar formulario
    items = obtener_items_carrito(carrito)
    total = calcular_total_carrito(carrito)
    cantidad_items = sum(carrito.values())
    
    context = {
        'items': items,
        'total': total,
        'cantidad_items': cantidad_items,
    }
    return render(request, 'tienda/checkout.html', context)

def confirmar_compra(request):
    """Redirige a checkout (ya no se usa)"""
    return redirect('tienda:checkout')

def compra_exitosa(request, pedido_id):
    """Vista de confirmación de compra"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()
    datos_cliente = request.session.get('ultimo_pedido', {})
    
    # Calcular total
    total = sum(detalle.cantidad * detalle.precio_unitario for detalle in detalles)
    
    context = {
        'pedido': pedido,
        'detalles': detalles,
        'total': total,
        'datos_cliente': datos_cliente,
        'cantidad_items': 0,  # Carrito vacío después de compra
    }
    return render(request, 'tienda/compra_exitosa.html', context)
