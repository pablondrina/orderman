import logging
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import Order
import json


logger = logging.getLogger(__name__)


def advance_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    current_status = order.status
    status_order = ['placed', 'confirmed', 'ready_to_pickup', 'concluded']
    
    if current_status == 'cancelled':
        messages.error(request, f"O pedido #{order.id} está cancelado e não pode ser avançado.")
    elif current_status == 'concluded':
        messages.error(request, f"O pedido #{order.id} já está concluído e não pode ser avançado.")
    else:
        try:
            current_index = status_order.index(current_status)
            if current_index < len(status_order) - 1:
                order.status = status_order[current_index + 1]
                order.save()
                messages.success(request, f"Status do pedido #{order.id} atualizado para {order.get_status_display()}.")
            else:
                messages.error(request, f"O pedido #{order.id} já está no status final.")
        except ValueError:
            messages.error(request, f"Status do pedido #{order.id} inválido.")
    
    return redirect('admin:orders_order_changelist')



def mark_confirmed(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = 'confirmed'
    order.save()
    messages.success(request, f'Order {order.id} marked as confirmed.')
    return redirect('admin:orders_order_changelist')



def mark_ready_to_pickup(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = 'ready_to_pickup'
    order.save()
    messages.success(request, f'Order {order.id} marked as ready to pickup.')
    return redirect('admin:orders_order_changelist')


def mark_concluded(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = 'concluded'
    order.save()
    messages.success(request, f'Order {order.id} marked as concluded.')
    return redirect('admin:orders_order_changelist')


@csrf_exempt  # Temporariamente, para fins de depuração
@require_POST
def mark_cancelled(request, order_id):
    logger.debug(f"Request received to cancel order ID: {order_id}")
    try:
        order = get_object_or_404(Order, id=order_id)
        logger.debug(f"Order found: {order}")
        
        if order.status == 'cancelled':
            logger.error(f"O pedido #{order.id} já está cancelado.")
            response = JsonResponse({'success': False, 'error': 'O pedido já está cancelado.'}, status=200)
            logger.debug(f"Response: {response.content}")
            return response
        elif order.status == 'concluded':
            logger.error(f"Não é possível cancelar o pedido #{order.id}, pois ele já foi concluído.")
            response = JsonResponse({'success': False, 'error': 'Não é possível cancelar o pedido, pois ele já foi concluído.'}, status=200)
            logger.debug(f"Response: {response.content}")
            return response
        else:
            order.status = 'cancelled'
            order.save()
            logger.info(f"Pedido #{order.id} foi cancelado com sucesso.")
            response = JsonResponse({'success': True}, status=200)
            logger.debug(f"Response: {response.content}")
            return response
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        response = JsonResponse({'success': False, 'error': str(e)}, status=400)
        logger.debug(f"Response: {response.content}")
        return response
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        response = JsonResponse({'success': False, 'error': str(e)}, status=500)
        logger.debug(f"Response: {response.content}")
        return response