from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from movimientos.models import Movimiento  
from .forms import CustomAuthenticationForm

class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    authentication_form = CustomAuthenticationForm


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')

@login_required
def dashboard(request):
    # Traemos los últimos 5 movimientos
    movimientos = Movimiento.objects.all().order_by('-fecha')[:5]
    return render(request, 'usuarios/dashboard.html', {'movimientos': movimientos})

@login_required
def custom_logout_view(request):
    logout(request)
    return render(request, 'usuarios/logout.html')
