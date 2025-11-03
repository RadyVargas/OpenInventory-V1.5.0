# core/middleware.py
import time
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout

class SessionIdleTimeoutMiddleware:
    """
    Middleware que cierra la sesión si el usuario está inactivo más tiempo
    que el valor definido en settings.SESSION_IDLE_TIMEOUT (segundos).
    Registrar DESPUÉS de AuthenticationMiddleware en settings.MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Timeout en segundos (si no está definido en settings, None => desactivado)
        self.timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', None)

    def __call__(self, request):
        # Si no hay timeout configurado o usuario no autenticado, no hacemos nada
        if not self.timeout or not request.user.is_authenticated:
            return self.get_response(request)

        current_ts = int(time.time())
        last_activity = request.session.get('last_activity', current_ts)

        # Si la diferencia supera el timeout, cerrar sesión y redirigir a login
        if current_ts - last_activity > self.timeout:
            # cerrar sesión
            logout(request)
            # agregar mensaje para que el usuario sepa por qué fue desconectado
            try:
                messages.warning(request, "Su sesión expiró por inactividad. Por favor inicie sesión nuevamente.")
            except Exception:
                pass
            return redirect('login')  # ajusta el nombre si tu URL de login es diferente

        # actualizar última actividad (timestamp)
        request.session['last_activity'] = current_ts

        response = self.get_response(request)
        return response
