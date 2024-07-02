from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Order)
def order_post_save(sender, instance, created, **kwargs):
    if created:
        # Notificar sobre novo pedido
        notify_new_order(instance)
    else:
        # Notificar sobre atualização de pedido
        notify_order_update(instance)

def notify_new_order(order):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "order_notifications",
        {
            "type": "order.notification",
            "message": f"Novo pedido recebido: #{order.id}",
            "order_id": order.id,
        },
    )

def notify_order_update(order):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "order_notifications",
        {
            "type": "order.notification",
            "message": f"Pedido #{order.id} atualizado. Novo status: {order.get_status_display()}",
            "order_id": order.id,
        },
    )