from django.contrib import admin
from django.urls import path, include
from orders.api import api
# from orders.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),
    path('orders/', include('orders.urls', namespace='orders')),
    # path('admin/dashboard/', DashboardView.as_view(), name='admin_dashboard'),
]
