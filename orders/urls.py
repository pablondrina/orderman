from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('order/<int:order_id>/mark_confirmed/', views.mark_confirmed, name='mark_confirmed'),
    path('order/<int:order_id>/mark_concluded/', views.mark_concluded, name='mark_concluded'),
    path('order/<int:order_id>/mark_ready_to_pickup/', views.mark_ready_to_pickup, name='mark_ready_to_pickup'),
    path('order/<int:order_id>/advance_status/', views.advance_status, name='advance_status'),
    path('order/<int:order_id>/mark_cancelled/', views.mark_cancelled, name='mark_cancelled'),
]