from django.db import models
from productos.models import Producto
from usuarios.models import Usuario

TIPO_MOVIMIENTO = [
    ('entrada', 'Entrada'),
    ('salida', 'Salida'),
]

class Movimiento(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"
