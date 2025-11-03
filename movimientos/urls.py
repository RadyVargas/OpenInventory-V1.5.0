from django.urls import path
from . import views
from .views import movimientos_list, movimientos_create

urlpatterns = [
    path('', views.movimientos_list, name='movimientos-list'),
    path('nuevo/', views.movimientos_create, name='movimientos-create'),
    path('', movimientos_list, name='movimientos-list'),
    path('nuevo/', movimientos_create, name='movimientos-create'),


]
