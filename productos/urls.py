from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.productos_list, name='productos-list'),
    path('productos/nuevo/', views.productos_create, name='productos-create'),
    path('productos/<int:pk>/editar/', views.productos_update, name='productos-update'),
    path('productos/<int:pk>/eliminar/', views.productos_delete, name='productos-delete'),

    path('reportes/', views.reportes, name='reportes'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/tomar/<int:pedido_id>/', views.tomar_pedido, name='tomar_pedido'),
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('escanear_producto/', views.escanear_producto, name='escanear_producto'),
    path('detalle_pedido/escanear/', views.escanear_producto, name='escanear_producto'),
    path('movimientos/', views.movimientos_list, name='movimientos-list'),


]
