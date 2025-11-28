from django.urls import path, include
from .views import CustomLoginView, custom_logout_view, dashboard
from productos.views import dashboard_admin  # 👈 importamos la vista de admin


urlpatterns = [
    
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard_admin/', dashboard_admin, name='dashboard_admin'),  # ✅ esta es la del admin
    path('captcha/', include('captcha.urls')),

]
