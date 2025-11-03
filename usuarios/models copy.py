from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('bodeguero', 'Empleado de almacén'),
        ('gerente', 'Gerente de compras'),
        ('propietario', 'Propietario/Cliente final'),
    )

    rol = models.CharField(max_length=30, choices=ROLES, default='bodeguero')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

# Create your models here.
