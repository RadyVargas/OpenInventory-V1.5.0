from django.urls import path
from .views import CustomLoginView, CustomLogoutView, dashboard, custom_logout_view


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),

]
