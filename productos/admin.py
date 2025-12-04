from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
import os
from .models import Producto, Pedido, DetallePedido, UbicacionProducto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'categoria', 'imagen', 'mostrar_qr')

    def mostrar_qr(self, obj):
        qr_path = f"qr/producto_{obj.id}.png"
        full_path = os.path.join(settings.MEDIA_ROOT, qr_path)
        if os.path.exists(full_path):
            return format_html('<img src="/media/{}" width="100" height="100"/>', qr_path)
        return "(QR no generado aún)"

    mostrar_qr.short_description = "Código QR"



class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = [DetallePedidoInline]
    list_display = ('id', 'usuario', 'fecha_creacion', 'estado')


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'escaneado')


@admin.register(UbicacionProducto)
class UbicacionProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'descripcion')
