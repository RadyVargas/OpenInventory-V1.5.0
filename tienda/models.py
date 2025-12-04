# tienda/models.py
from django.db import models
from productos.models import Producto

# No necesitamos modelos de base de datos para el carrito
# El carrito se manejará en la sesión de Django
# Los pedidos se crearán usando el modelo Pedido existente de la app productos
