# usuarios/views.py
import json
from decimal import Decimal
from django.db.models import F, Sum, Count, ExpressionWrapper, DecimalField
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from movimientos.models import Movimiento  
from productos.models import Producto, Pedido, DetallePedido
from .forms import CustomAuthenticationForm
from django.urls import reverse
from django.contrib import messages




#LOGIN / LOGOUT

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = CustomAuthenticationForm

    def form_invalid(self, form):
        messages.error(self.request, "Usuario o contraseña incorrectos.")
        return super().form_invalid(form)

    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.rol == 'bodeguero':
            return reverse('dashboard_admin')
        else:
            return reverse('dashboard')


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

@login_required
def custom_logout_view(request):
    logout(request)
    return render(request, 'usuarios/logout.html')


# DASHBOARD

from django.db.models import F, Sum, Count, ExpressionWrapper, DecimalField
from decimal import Decimal
import json

@login_required
def dashboard(request):
    #bodeguero es staff

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

    productos_bajos_qs = Producto.objects.filter(stock__lt=10)
    total_pedidos = Pedido.objects.count()

    pedidos_por_estado_qs = Pedido.objects.values('estado').annotate(total=Count('id'))
    if pedidos_por_estado_qs.exists():
        labels = [p['estado'].capitalize() for p in pedidos_por_estado_qs]
        data = [p['total'] for p in pedidos_por_estado_qs]
    else:
        labels = ['Pendiente', 'En_proceso', 'Completado']
        data = [0, 0, 0]

    #3 productos con más stock
    productos_top_stock = Producto.objects.values('nombre', 'stock').order_by('-stock')[:3]
    productos_labels = [p['nombre'] for p in productos_top_stock]
    productos_stock = [p['stock'] for p in productos_top_stock]

    #5 productos más vendidos desde DetallePedido
    productos_mas_vendidos = (
        DetallePedido.objects
        .values('producto__nombre')
        .annotate(total_vendidos=Sum('cantidad'))
        .order_by('-total_vendidos')[:5]
    )
    mas_vendidos_labels = [p['producto__nombre'] for p in productos_mas_vendidos]
    mas_vendidos_data = [p['total_vendidos'] for p in productos_mas_vendidos]

    context = {
        'total_stock': total_stock,
        'valor_inventario': valor_inventario,
        'productos_bajos': productos_bajos_qs,
        'total_pedidos': total_pedidos,
        'labels_json': json.dumps(labels),
        'data_json': json.dumps(data),
        'productos_labels_json': json.dumps(productos_labels),
        'productos_stock_json': json.dumps(productos_stock),
        'mas_vendidos_labels_json': json.dumps(mas_vendidos_labels),
        'mas_vendidos_data_json': json.dumps(mas_vendidos_data),
    }

    return render(request, 'productos/dashboard_admin.html', context)
