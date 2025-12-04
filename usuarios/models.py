from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('bodeguero', 'bodeguero'),
        ('propietario', 'Supervisor'),
        ('gerente', 'gerente'),
        ('cliente', 'Cliente'),  # Para clientes de TechStore
    )

    rol = models.CharField(max_length=30, choices=ROLES, default='bodeguero')

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

# Create your models here.
