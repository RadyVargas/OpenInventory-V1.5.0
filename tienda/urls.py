# tienda/urls.py
from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    # Catálogo
    path('', views.catalogo, name='catalogo'),
    path('producto/<int:pk>/', views.producto_detalle, name='producto_detalle'),
    
    # Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('confirmar-compra/', views.confirmar_compra, name='confirmar_compra'),
    path('exito/<int:pedido_id>/', views.compra_exitosa, name='compra_exitosa'),
]
