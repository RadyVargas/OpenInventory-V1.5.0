from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Movimiento
from .forms import MovimientoForm

@login_required
def movimientos_list(request):
    movimientos = Movimiento.objects.all().order_by('-fecha')
    return render(request, 'movimientos/movimientos_list.html', {'movimientos': movimientos})

@login_required
def movimientos_create(request):
    if request.user.rol not in ['admin', 'bodeguero']:
        return redirect('movimientos-list')

    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()  # Guardamos el movimiento

            # Actualizar stock del producto
            producto = movimiento.producto
            if movimiento.tipo == 'entrada':
                producto.stock += movimiento.cantidad
            else:
                producto.stock -= movimiento.cantidad
            producto.save()

            return redirect('movimientos-list')
        else:
            print(form.errors)  # Para ver errores en consola
    else:
        form = MovimientoForm()

    return render(request, 'movimientos/movimiento_form.html', {'form': form})
