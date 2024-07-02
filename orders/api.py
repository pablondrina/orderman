from ninja import NinjaAPI, Schema
from django.shortcuts import get_object_or_404
from .models import Order, Customer
from typing import List
from decimal import Decimal
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging


api = NinjaAPI()

# Schemas
class OrderIn(Schema):
    subscriber_id: str
    order_details: str
    priority: int = 2
    total_amount: Decimal

class OrderOut(Schema):
    id: int
    subscriber_id: str
    order_details: str
    status: str
    priority: int
    total_amount: Decimal
    created_at: str
    updated_at: str

logger = logging.getLogger(__name__)

# Endpoints
@api.post("/orders/")
def create_order(request, payload: OrderIn):
    try:
        customer = Customer.objects.get(subscriber_id=payload.subscriber_id)
    except Customer.DoesNotExist:
        return {"error": f"Customer with subscriber_id {payload.subscriber_id} not found"}, 404

    order = Order.objects.create(
        customer=customer,
        order_details=payload.order_details,
        priority=payload.priority,
        total_amount=payload.total_amount
    )

    logger.info(f'Novo pedido criado: {order.id}')
    
    # Enviar notificação via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "order_updates",
        {
            "type": "order_update",
            "message": "new_order"
        }
    )
    logger.info('Notificação WebSocket enviada')

    return {"id": order.id, "message": "Order created successfully"}


@api.get("/orders/", response=List[OrderOut])
def list_orders(request):
    return [
        OrderOut(
            id=order.id,
            subscriber_id=order.customer.subscriber_id,  # Usando 'customer' em vez de 'subscriber'
            order_details=order.order_details,
            status=order.status,
            priority=order.priority,
            total_amount=order.total_amount,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat()
        )
        for order in Order.objects.all()
    ]

@api.get("/orders/{order_id}/", response=OrderOut)
def get_order(request, order_id: int):
    order = get_object_or_404(Order, id=order_id)
    return OrderOut(
        id=order.id,
        subscriber_id=order.customer.subscriber_id,  # Usando 'customer' em vez de 'subscriber'
        order_details=order.order_details,
        status=order.status,
        priority=order.priority,
        total_amount=order.total_amount,
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat()
    )