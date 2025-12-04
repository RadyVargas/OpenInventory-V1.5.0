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
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError


class Producto(models.Model):
    nombre = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\-\_]+$',
                message='El nombre solo puede contener letras, números, espacios y guiones.'
            )
        ]
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0.01, message='El precio debe ser mayor que cero.')
        ]
    )
    stock = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message='El stock debe ser al menos 1.')
        ]
    )
    categoria = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$',
                message='La categoría solo puede contener letras y espacios.'
            )
        ]
    )
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name='Imagen del Producto')
    descripcion = models.TextField(blank=True, null=True, verbose_name='Descripción del Producto')

    def __str__(self):
        return f"{self.nombre}"

    def get_absolute_url(self):
        return reverse('productos-list')
    @property
    def precio_formateado(self):
        return f"{int(self.precio):,}".replace(",", ".")


    def clean(self):
        super().clean()
        if self.precio is not None and self.precio > 9999999999:
            raise ValidationError('El precio es demasiado alto.')


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
    ]
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bodeguero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_asignados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    nombre_cliente = models.CharField(max_length=200, blank=True, null=True)
    email_cliente = models.EmailField(blank=True, null=True)
    telefono_cliente = models.CharField(max_length=20, blank=True, null=True)
    direccion_envio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.estado}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    escaneado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.producto.nombre} (x{self.cantidad})"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario


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
