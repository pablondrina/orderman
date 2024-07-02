# orderman/routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from orders.consumers import OrderConsumer  # Substitua 'myapp' pelo nome do seu aplicativo

websocket_urlpatterns = [
    path('ws/orders/', OrderConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': URLRouter(websocket_urlpatterns),
})
