from django.db import models
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.db import models
import qrcode
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    categoria = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre}"

    def get_absolute_url(self):
        return reverse('productos-list')


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.estado}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    escaneado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad})"


class UbicacionProducto(models.Model):
    producto = models.OneToOneField('Producto', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='ubicaciones/')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Ubicación de {self.producto.nombre}"
    
@receiver(post_save, sender=Producto)
def generar_qr_producto(sender, instance, created, **kwargs):
    """Genera un QR automáticamente cuando se crea o actualiza un producto"""
    if created or not os.path.exists(os.path.join(settings.MEDIA_ROOT, f"qr/producto_{instance.id}.png")):
        qr_path = os.path.join(settings.MEDIA_ROOT, 'qr')
        os.makedirs(qr_path, exist_ok=True)

        data = str(instance.id)
        img = qrcode.make(data)

        img.save(os.path.join(qr_path, f"producto_{instance.id}.png"))
        print(f"✅ QR generado para {instance.nombre}")

# Create your models here.
