from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class Customer(models.Model):
    subscriber_id = models.CharField(_('ID do Assinante'), max_length=64, primary_key=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    def __str__(self):
        return self.subscriber_id
    
    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')



class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', _('Novo pedido')),
        ('confirmed', _('Confirmado')),
        ('ready_to_pickup', _('Pronto para retirada')),
        ('concluded', _('Concluído')),
        ('cancelled', _('Cancelado')),
    ]

    PRIORITY_CHOICES = [
        (1, _('Baixa')),
        (2, _('Normal')),
        (3, _('Alta')),
        (4, _('Urgente')),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Dinheiro')),
        ('credit_card', _('Crédito')),
        ('debit_card', _('Dábito')),
        ('pix', _('Pix')),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('delivery', _('Entrega')),
        ('takeout', _('Retirada')),
    ]

    customer = models.ForeignKey(Customer, verbose_name=_('ID do Assinante'), on_delete=models.CASCADE)
    delivery_method = models.CharField(_('Modo de Entrega'), max_length=16, choices=DELIVERY_METHOD_CHOICES, default='takeout')
    payment_method = models.CharField(_('Forma de Pagamento'), max_length=16, choices=PAYMENT_METHOD_CHOICES, default='pix')
    priority = models.IntegerField(_('Prioridade'), choices=PRIORITY_CHOICES, default=2)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='placed')
    order_details = models.TextField(_('Detalhes do Pedido'), blank=True)
    total_amount = models.DecimalField(_('Valor Total'), max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')
        ordering = ['-priority', '-created_at', 'status']

    def __str__(self):
        return f"Pedido #{self.id} @{self.customer.subscriber_id} ({self.status})"

@receiver(post_save, sender=Order)
def order_status_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "orders",
        {
            "type": "order_update",
            "content": {
                "order_id": instance.id,
                "status": instance.status,
            },
        },
    )

class Comment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Pedido'))
    content = models.TextField(_('Conteúdo'))
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)

    class Meta:
        verbose_name = _('Comentário')
        verbose_name_plural = _('Comentários')
        ordering = ['-created_at']

    def __str__(self):
        return f"Comentário em {self.order}"